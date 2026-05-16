"""PyTorch optimization loop for soft EML trees."""

from __future__ import annotations

import time
from dataclasses import dataclass, field, replace
from typing import Any, Callable, Mapping

import numpy as np
import torch

from .expression import Const, Var, format_constant_value, ipi_eml_expr
from .master_tree import ActiveSlotAlternatives, SnapDecision, SnapResult, SoftEMLTree, constant_label
from .semantics import AnomalyStats, EmlOperator, TrainingSemanticsConfig, as_complex_tensor, mse_complex_numpy, raw_eml_operator
from .verify import DataSplit, VerificationReport, selection_candidate_splits, verify_candidate
from .witnesses import (
    CENTERED_FAMILY_SAME_FAMILY_WITNESS_MISSING,
    known_scaffold_kinds,
    resolve_scaffold_plan,
    scaffold_witness_for,
)


@dataclass(frozen=True)
class TrainingConfig:
    depth: int = 2
    variables: tuple[str, ...] = ("x",)
    constants: tuple[complex, ...] = (1.0,)
    steps: int = 300
    restarts: int = 3
    lr: float = 0.05
    temperature_start: float = 2.0
    temperature_end: float = 0.25
    hardening_steps: int = 4
    hardening_temperature_end: float = 0.02
    hardening_emit_interval: int = 2
    entropy_weight: float = 1e-3
    size_weight: float = 1e-4
    clamp_exp_real: float = 40.0
    log_domain_epsilon: float = 1e-9
    log_safety_weight: float = 0.0
    log_safety_margin: float = 1e-6
    log_safety_imag_tolerance: float = 1e-6
    semantics_mode: str = "guarded"
    refit_steps: int = 80
    refit_lr: float = 0.02
    seed: int = 0
    scaffold_initializers: tuple[str, ...] = ("exp", "log", "scaled_exp")
    phase_initializers: tuple[str, ...] = ()
    operator_family: EmlOperator = field(default_factory=raw_eml_operator)
    operator_schedule: tuple[EmlOperator, ...] = ()

    def __post_init__(self) -> None:
        mode = str(self.semantics_mode)
        if mode not in {"guarded", "faithful"}:
            raise ValueError("semantics_mode must be 'guarded' or 'faithful'")
        object.__setattr__(self, "semantics_mode", mode)
        unknown = sorted(set(self.phase_initializers) - set(_PHASE_INITIALIZERS))
        if unknown:
            raise ValueError(f"unknown phase initializers: {', '.join(unknown)}")

    def semantics_config(self) -> TrainingSemanticsConfig:
        return TrainingSemanticsConfig(
            mode=self.semantics_mode,
            clamp_exp_real=self.clamp_exp_real,
            log_domain_epsilon=self.log_domain_epsilon,
            log_safety_weight=self.log_safety_weight,
            log_safety_margin=self.log_safety_margin,
            log_safety_imag_tolerance=self.log_safety_imag_tolerance,
        )

    def operator_payload(self) -> dict[str, Any]:
        return {
            "operator_family": self.operator_family.as_dict(),
            "operator_schedule": [operator.as_dict() for operator in self.operator_schedule],
        }


@dataclass(frozen=True)
class ExactCandidate:
    candidate_id: str
    attempt_index: int
    random_restart: int | None
    seed: int
    attempt_kind: str
    source: str
    checkpoint_index: int | None
    hardening_step: int | None
    global_step: int
    temperature: float
    best_fit_loss: float
    pre_snap_loss: float
    post_snap_loss: float
    snap: SnapResult
    slot_alternatives: tuple[ActiveSlotAlternatives, ...] = ()
    verification: VerificationReport | None = None
    selection_metrics: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        low_margin = sorted(self.snap.decisions, key=lambda item: item.margin)[:5]
        return {
            "candidate_id": self.candidate_id,
            "attempt_index": self.attempt_index,
            "random_restart": self.random_restart,
            "seed": self.seed,
            "attempt_kind": self.attempt_kind,
            "source": self.source,
            "checkpoint_index": self.checkpoint_index,
            "hardening_step": self.hardening_step,
            "global_step": self.global_step,
            "temperature": self.temperature,
            "best_fit_loss": self.best_fit_loss,
            "pre_snap_mse": self.pre_snap_loss,
            "post_snap_loss": self.post_snap_loss,
            "post_snap_mse": self.post_snap_loss,
            "active_slot_count": len(self.snap.decisions),
            "low_margin_slot_count": sum(1 for item in self.snap.decisions if item.margin < 0.1),
            "lowest_margin_slots": [_decision_payload(item) for item in low_margin],
            "snap": self.snap.as_dict(),
            "slot_alternatives": [item.as_dict() for item in self.slot_alternatives],
            "verification": self.verification.as_dict() if self.verification is not None else None,
            "branch_diagnostics": self.verification.branch_diagnostics if self.verification is not None else None,
            "selection_metrics": dict(self.selection_metrics or {}),
        }


@dataclass(frozen=True)
class FitResult:
    status: str
    best_loss: float
    post_snap_loss: float
    snap: SnapResult
    manifest: dict[str, Any]
    verification: VerificationReport | None = None
    selected_candidate: ExactCandidate | None = None
    fallback_candidate: ExactCandidate | None = None
    candidates: tuple[ExactCandidate, ...] = ()


def _temperature(config: TrainingConfig, step: int) -> float:
    if config.steps <= 1:
        return config.temperature_end
    frac = step / (config.steps - 1)
    return config.temperature_start + frac * (config.temperature_end - config.temperature_start)


def _hardening_temperature(config: TrainingConfig, step: int) -> float:
    if config.hardening_steps <= 1:
        return config.hardening_temperature_end
    frac = step / (config.hardening_steps - 1)
    return config.temperature_end + frac * (config.hardening_temperature_end - config.temperature_end)


def _should_emit_hardening_candidate(config: TrainingConfig, step: int) -> bool:
    if config.hardening_steps <= 0:
        return False
    if step == config.hardening_steps - 1:
        return True
    interval = max(int(config.hardening_emit_interval), 1)
    return step % interval == 0


def _decision_payload(decision: SnapDecision) -> dict[str, Any]:
    return {
        "slot": f"{decision.path}.{decision.side}",
        "choice": decision.choice,
        "probability": decision.probability,
        "margin": decision.margin,
    }


def _train_step(
    model: SoftEMLTree,
    optimizer: torch.optim.Optimizer,
    tensor_inputs: Mapping[str, torch.Tensor],
    target_tensor: torch.Tensor,
    *,
    temperature: float,
    config: TrainingConfig,
    operator_family: EmlOperator,
) -> tuple[dict[str, float] | None, AnomalyStats]:
    optimizer.zero_grad()
    model.set_operator(operator_family)
    stats = AnomalyStats()
    pred = model(
        tensor_inputs,
        temperature=temperature,
        training_semantics=True,
        stats=stats,
        semantics=config.semantics_config(),
    )
    fit_loss = torch.mean(torch.abs(pred - target_tensor) ** 2)
    entropy = model.gate_entropy(temperature)
    size = model.expected_child_use(temperature)
    anomaly_penalty = stats.training_penalty(device=fit_loss.device)
    entropy_loss = config.entropy_weight * entropy
    size_loss = config.size_weight * size
    loss = fit_loss + entropy_loss + size_loss + anomaly_penalty
    if not torch.isfinite(loss):
        return None, stats
    loss.backward()
    gradient_l2_norm, gradient_max_abs = _gradient_metrics(model)
    optimizer.step()
    return {
        "fit_loss": float(fit_loss.detach().item()),
        "pre_snap_mse": float(fit_loss.detach().item()),
        "objective_loss": float(loss.detach().item()),
        "entropy": float(entropy.detach().item()),
        "entropy_loss": float(entropy_loss.detach().item()),
        "expected_child_use": float(size.detach().item()),
        "size_loss": float(size_loss.detach().item()),
        "anomaly_penalty": float(anomaly_penalty.detach().item()),
        "gradient_l2_norm": gradient_l2_norm,
        "gradient_max_abs": gradient_max_abs,
    }, stats


def _gradient_metrics(model: SoftEMLTree) -> tuple[float, float]:
    squared = 0.0
    max_abs = 0.0
    for parameter in model.parameters():
        if parameter.grad is None:
            continue
        grad = parameter.grad.detach()
        squared += float(torch.sum(torch.abs(grad) ** 2).item())
        max_abs = max(max_abs, float(torch.max(torch.abs(grad)).item()) if grad.numel() else 0.0)
    return float(np.sqrt(squared)), max_abs


def _trace_entry(
    *,
    phase: str,
    step: int,
    global_step: int,
    temperature: float,
    metrics: Mapping[str, float],
    stats: AnomalyStats,
    operator_family: EmlOperator,
) -> dict[str, Any]:
    anomaly = stats.as_dict()
    return {
        "phase": phase,
        "step": step,
        "global_step": global_step,
        "temperature": temperature,
        "operator_family": operator_family.label,
        "fit_loss": metrics["fit_loss"],
        "pre_snap_mse": metrics["pre_snap_mse"],
        "objective_loss": metrics["objective_loss"],
        "gradient_l2_norm": metrics["gradient_l2_norm"],
        "gradient_max_abs": metrics["gradient_max_abs"],
        "entropy": metrics["entropy"],
        "entropy_loss": metrics["entropy_loss"],
        "expected_child_use": metrics["expected_child_use"],
        "size_loss": metrics["size_loss"],
        "anomaly_penalty": metrics["anomaly_penalty"],
        "nan_count": anomaly["nan_count"],
        "inf_count": anomaly["inf_count"],
        "clamp_count": anomaly["clamp_count"],
        "max_abs": anomaly["max_abs"],
        "max_exp_real": anomaly["max_exp_real"],
        "exp_overflow_count": anomaly["exp_overflow_count"],
        "log_small_magnitude_count": anomaly["log_small_magnitude_count"],
        "log_non_positive_real_count": anomaly["log_non_positive_real_count"],
        "log_branch_cut_count": anomaly["log_branch_cut_count"],
        "branch_input_count": anomaly["branch_input_count"],
        "log_branch_cut_proximity_count": anomaly["log_branch_cut_proximity_count"],
        "log_branch_cut_crossing_count": anomaly["log_branch_cut_crossing_count"],
        "log_branch_cut_min_distance": anomaly["log_branch_cut_min_distance"],
        "log_non_finite_input_count": anomaly["log_non_finite_input_count"],
        "invalid_domain_skip_count": anomaly["invalid_domain_skip_count"],
        "expm1_overflow_count": anomaly["expm1_overflow_count"],
        "log1p_branch_cut_count": anomaly["log1p_branch_cut_count"],
        "shifted_singularity_near_count": anomaly["shifted_singularity_near_count"],
        "shifted_singularity_min_distance": anomaly["shifted_singularity_min_distance"],
        "log_safety_penalty": anomaly["log_safety_penalty"],
        "by_node": anomaly["by_node"],
    }


def _loss_summary(trace: list[Mapping[str, Any]]) -> dict[str, Any]:
    if not trace:
        return {
            "steps_recorded": 0,
            "fit_steps_recorded": 0,
            "hardening_steps_recorded": 0,
            "first_fit_loss": None,
            "last_fit_loss": None,
            "best_fit_loss": None,
            "best_global_step": None,
            "loss_reduction": None,
            "loss_reduction_ratio": None,
            "gradient_l2_norm_max": 0.0,
            "gradient_max_abs_max": 0.0,
        }
    fit_values = [float(row["fit_loss"]) for row in trace if row.get("phase") == "fit" and np.isfinite(float(row["fit_loss"]))]
    all_values = [float(row["fit_loss"]) for row in trace if np.isfinite(float(row["fit_loss"]))]
    first = fit_values[0] if fit_values else (all_values[0] if all_values else None)
    last = all_values[-1] if all_values else None
    best_row = min(
        (row for row in trace if np.isfinite(float(row.get("fit_loss", float("inf"))))),
        key=lambda row: float(row["fit_loss"]),
        default=None,
    )
    best = float(best_row["fit_loss"]) if best_row is not None else None
    reduction = (first - last) if first is not None and last is not None else None
    ratio = (last / first) if first not in {None, 0.0} and last is not None else None
    return {
        "steps_recorded": len(trace),
        "fit_steps_recorded": sum(1 for row in trace if row.get("phase") == "fit"),
        "hardening_steps_recorded": sum(1 for row in trace if row.get("phase") == "hardening"),
        "first_fit_loss": first,
        "last_fit_loss": last,
        "best_fit_loss": best,
        "best_global_step": best_row.get("global_step") if best_row is not None else None,
        "loss_reduction": reduction,
        "loss_reduction_ratio": ratio,
        "gradient_l2_norm_max": max((_numeric(row.get("gradient_l2_norm")) for row in trace), default=0.0),
        "gradient_max_abs_max": max((_numeric(row.get("gradient_max_abs")) for row in trace), default=0.0),
    }


def _manifest_trace_summary(restart_logs: list[Mapping[str, Any]]) -> dict[str, Any]:
    summaries = [log.get("loss_summary") for log in restart_logs if isinstance(log.get("loss_summary"), Mapping)]
    total_steps = sum(int(summary.get("steps_recorded") or 0) for summary in summaries)
    best_values = [float(summary["best_fit_loss"]) for summary in summaries if summary.get("best_fit_loss") is not None]
    return {
        "restart_count": len(restart_logs),
        "total_steps_recorded": total_steps,
        "best_fit_loss_min": min(best_values) if best_values else None,
        "best_fit_loss_max": max(best_values) if best_values else None,
        "trace_available": total_steps > 0,
    }


_ANOMALY_COUNT_FIELDS = (
    "nan_count",
    "inf_count",
    "clamp_count",
    "exp_overflow_count",
    "log_small_magnitude_count",
    "log_non_positive_real_count",
    "log_branch_cut_count",
    "branch_input_count",
    "log_branch_cut_proximity_count",
    "log_branch_cut_crossing_count",
    "log_non_finite_input_count",
    "invalid_domain_skip_count",
    "expm1_overflow_count",
    "log1p_branch_cut_count",
    "shifted_singularity_near_count",
)


def _numeric(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number


def _anomaly_summary(restart_logs: list[Mapping[str, Any]]) -> dict[str, Any]:
    final_rows = [row.get("final_anomalies") for row in restart_logs if isinstance(row.get("final_anomalies"), Mapping)]
    trace_rows: list[Mapping[str, Any]] = []
    for row in restart_logs:
        trace = row.get("trace")
        if isinstance(trace, list):
            trace_rows.extend(item for item in trace if isinstance(item, Mapping))

    def summarize(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
        max_abs_values = [_numeric(row.get("max_abs")) for row in rows]
        max_exp_values = [_numeric(row.get("max_exp_real")) for row in rows]
        singularity_values = [
            _numeric(row.get("shifted_singularity_min_distance"), default=float("inf"))
            for row in rows
            if row.get("shifted_singularity_min_distance") is not None
        ]
        branch_distance_values = [
            _numeric(row.get("log_branch_cut_min_distance"), default=float("inf"))
            for row in rows
            if row.get("log_branch_cut_min_distance") is not None
        ]
        payload = {field: int(sum(_numeric(row.get(field)) for row in rows)) for field in _ANOMALY_COUNT_FIELDS}
        payload.update(
            {
                "log_safety_penalty": float(sum(_numeric(row.get("log_safety_penalty")) for row in rows)),
                "max_abs": max(max_abs_values) if max_abs_values else 0.0,
                "max_exp_real": max(max_exp_values) if max_exp_values else 0.0,
                "log_branch_cut_min_distance": min(branch_distance_values) if branch_distance_values else None,
                "shifted_singularity_min_distance": min(singularity_values) if singularity_values else None,
            }
        )
        return payload

    return {
        "final_by_restart": summarize(final_rows),
        "trace_totals": summarize(trace_rows),
    }


def _semantics_alignment_payload(
    config: TrainingConfig,
    restart_logs: list[Mapping[str, Any]],
    selected_candidate: ExactCandidate,
) -> dict[str, Any]:
    verification = selected_candidate.verification
    split_errors = [result.max_abs_error for result in verification.split_results] if verification is not None else []
    post_snap_delta = (
        selected_candidate.post_snap_loss - selected_candidate.best_fit_loss
        if np.isfinite(selected_candidate.post_snap_loss) and np.isfinite(selected_candidate.best_fit_loss)
        else None
    )
    post_snap_pre_delta = (
        selected_candidate.post_snap_loss - selected_candidate.pre_snap_loss
        if np.isfinite(selected_candidate.post_snap_loss) and np.isfinite(selected_candidate.pre_snap_loss)
        else None
    )
    return {
        "training_semantics_mode": config.semantics_mode,
        "objective_matches_verifier_semantics": config.semantics_mode == "faithful",
        "fallback_reason": None
        if config.semantics_mode == "faithful"
        else "guarded_training_uses_exp_clamp_and_optional_log_safety_penalty",
        "guard_parameters": {
            "clamp_exp_real": config.clamp_exp_real,
            "log_domain_epsilon": config.log_domain_epsilon,
            "log_safety_weight": config.log_safety_weight,
            "log_safety_margin": config.log_safety_margin,
            "log_safety_imag_tolerance": config.log_safety_imag_tolerance,
        },
        "ablation_contract": {
            "control_mode": "faithful",
            "treatment_mode": "guarded",
            "suite_override": "benchmark --semantics-mode {guarded,faithful}",
            "comparison_keys": [
                "verifier_status",
                "post_snap_loss",
                "high_precision_max_error",
                "anomaly_clamp_count",
                "anomaly_log_safety_penalty",
            ],
        },
        "anomaly_summary": _anomaly_summary(restart_logs),
        "post_snap_mismatch": {
            "selected_candidate_id": selected_candidate.candidate_id,
            "soft_best_fit_loss": selected_candidate.best_fit_loss,
            "pre_snap_mse": selected_candidate.pre_snap_loss,
            "post_snap_loss": selected_candidate.post_snap_loss,
            "post_snap_mse": selected_candidate.post_snap_loss,
            "post_snap_minus_soft_best": post_snap_delta,
            "post_snap_minus_pre_snap": post_snap_pre_delta,
            "verifier_status": verification.status if verification is not None else None,
            "high_precision_max_error": verification.high_precision_max_error if verification is not None else None,
            "split_max_abs_error": max(split_errors) if split_errors else None,
        },
        "verifier_evidence": {
            "symbolic_status": verification.symbolic_status if verification is not None else None,
            "dense_random_status": verification.dense_random_status if verification is not None else None,
            "adversarial_status": verification.adversarial_status if verification is not None else None,
            "certificate_status": verification.certificate_status if verification is not None else None,
            "evidence_level": verification.evidence_level if verification is not None else None,
            "metric_roles": verification.metric_roles if verification is not None else None,
            "branch_diagnostics": verification.branch_diagnostics if verification is not None else None,
        },
    }


def _emit_candidate(
    model: SoftEMLTree,
    inputs: Mapping[str, Any],
    target: Any,
    *,
    candidate_id: str,
    attempt_index: int,
    random_restart: int | None,
    seed: int,
    attempt_kind: str,
    source: str,
    checkpoint_index: int | None,
    hardening_step: int | None,
    global_step: int,
    temperature: float,
    best_fit_loss: float,
    config: TrainingConfig,
) -> ExactCandidate:
    snap = model.snap()
    slot_alternatives = model.active_slot_alternatives(top_k=2)
    pre_snap_loss = _soft_checkpoint_loss(model, inputs, target, temperature=temperature, config=config)
    snapped_pred = snap.expression.evaluate_numpy({name: np.asarray(value) for name, value in inputs.items()})
    post_snap_loss = mse_complex_numpy(snapped_pred, target)
    return ExactCandidate(
        candidate_id=candidate_id,
        attempt_index=attempt_index,
        random_restart=random_restart,
        seed=seed,
        attempt_kind=attempt_kind,
        source=source,
        checkpoint_index=checkpoint_index,
        hardening_step=hardening_step,
        global_step=global_step,
        temperature=temperature,
        best_fit_loss=best_fit_loss,
        pre_snap_loss=pre_snap_loss,
        post_snap_loss=post_snap_loss,
        snap=snap,
        slot_alternatives=slot_alternatives,
    )


def _soft_checkpoint_loss(
    model: SoftEMLTree,
    inputs: Mapping[str, Any],
    target: Any,
    *,
    temperature: float,
    config: TrainingConfig,
) -> float:
    with torch.no_grad():
        tensor_inputs = {name: as_complex_tensor(value) for name, value in inputs.items()}
        target_tensor = as_complex_tensor(target)
        pred = model(
            tensor_inputs,
            temperature=temperature,
            training_semantics=True,
            semantics=config.semantics_config(),
        )
        return float(torch.mean(torch.abs(pred - target_tensor) ** 2).item())


def _report_group_error(report: VerificationReport | None, predicate: Callable[[str], bool]) -> float:
    if report is None:
        return float("inf")
    values = [result.max_abs_error for result in report.split_results if predicate(result.name.lower())]
    if not values:
        return 0.0
    return float(max(values))


def _selection_metrics(candidate: ExactCandidate, report: VerificationReport | None) -> dict[str, Any]:
    verifier_status = report.status if report is not None else None
    extrap_error = _report_group_error(report, lambda name: "extra" in name)
    heldout_error = _report_group_error(report, lambda name: "hold" in name or "valid" in name)
    return {
        "verifier_status": verifier_status,
        "status_rank": _status_rank(verifier_status),
        "extrapolation_max_abs_error": extrap_error,
        "high_precision_max_error": report.high_precision_max_error if report is not None else float("inf"),
        "heldout_max_abs_error": heldout_error,
        "post_snap_loss": candidate.post_snap_loss,
        "complexity": candidate.snap.active_node_count,
        "soft_fit_loss": candidate.best_fit_loss,
    }


def _status_rank(status: str | None) -> int:
    return {
        "recovered": 0,
        "verified_showcase": 1,
        "failed": 2,
        None: 3,
    }.get(status, 3)


def _finite_or_inf(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return float("inf")
    return number if np.isfinite(number) else float("inf")


def _candidate_ranking_key(candidate: ExactCandidate) -> tuple[Any, ...]:
    metrics = candidate.selection_metrics or {}
    return (
        int(metrics.get("status_rank", 3)),
        _finite_or_inf(metrics.get("extrapolation_max_abs_error")),
        _finite_or_inf(metrics.get("high_precision_max_error")),
        _finite_or_inf(metrics.get("heldout_max_abs_error")),
        _finite_or_inf(metrics.get("post_snap_loss")),
        int(metrics.get("complexity", candidate.snap.active_node_count)),
        _finite_or_inf(metrics.get("soft_fit_loss")),
        candidate.candidate_id,
    )


def _select_exact_candidate(
    candidates: list[ExactCandidate],
    *,
    verification_splits: list[DataSplit] | None,
    tolerance: float,
) -> tuple[list[ExactCandidate], str]:
    selection_mode = "verifier_gated_exact_candidate_pool" if verification_splits is not None else "train_post_snap_exact_candidate_pool"
    ranked: list[ExactCandidate] = []
    ranking_splits = selection_candidate_splits(verification_splits) if verification_splits is not None else None
    has_final_confirmation = verification_splits is not None and len(ranking_splits or ()) != len(verification_splits)
    for candidate in candidates:
        selection_report = verify_candidate(candidate.snap.expression, ranking_splits, tolerance=tolerance) if ranking_splits is not None else None
        report = (
            verify_candidate(candidate.snap.expression, verification_splits, tolerance=tolerance)
            if has_final_confirmation and verification_splits is not None
            else selection_report
        )
        ranked.append(replace(candidate, verification=report, selection_metrics=_selection_metrics(candidate, selection_report)))
    ranked.sort(key=_candidate_ranking_key)
    return ranked, selection_mode


def fit_eml_tree(
    inputs: Mapping[str, Any],
    target: Any,
    config: TrainingConfig,
    initializer: Callable[[SoftEMLTree, int, int], dict[str, Any]] | None = None,
    *,
    verification_splits: list[DataSplit] | None = None,
    tolerance: float = 1e-8,
) -> FitResult:
    """Fit a soft EML tree and retain a verifier-rankable exact-candidate pool."""

    target_tensor = as_complex_tensor(target)
    wall_start = time.perf_counter()
    tensor_inputs = {name: as_complex_tensor(value) for name, value in inputs.items()}

    best: tuple[float, dict[str, Any]] | None = None
    restart_logs: list[dict[str, Any]] = []
    candidates: list[ExactCandidate] = []

    initial_operator = _operator_for_step(config, 0, max(config.steps, 1))
    scaffold_plan = resolve_scaffold_plan(config.scaffold_initializers, initial_operator)
    effective_config = replace(config, scaffold_initializers=scaffold_plan.enabled)
    attempts = _training_attempts(effective_config, initializer is not None)

    for attempt_index, attempt in enumerate(attempts):
        restart = int(attempt["restart"])
        seed = int(attempt["seed"])
        torch.manual_seed(seed)
        model = SoftEMLTree(
            effective_config.depth,
            effective_config.variables,
            effective_config.constants,
            operator_family=_operator_for_step(effective_config, 0, max(effective_config.steps, 1)),
        )
        model.reset_parameters(seed=seed, scale=0.25)
        if initializer is not None:
            initialization_log = initializer(model, restart, seed)
        elif str(attempt["kind"]).startswith("phase_initializer_"):
            initialization_log = _apply_phase_initializer(model, attempt)
        elif attempt["kind"].startswith("scaffold_"):
            initialization_log = _apply_scaffold(model, attempt)
        else:
            initialization_log = None
        optimizer = torch.optim.Adam(model.parameters(), lr=effective_config.lr)
        losses: list[float] = []
        trace: list[dict[str, Any]] = []
        final_stats = AnomalyStats()

        for step in range(effective_config.steps):
            temp = _temperature(effective_config, step)
            operator_family = _operator_for_step(effective_config, step, max(effective_config.steps, 1))
            step_metrics, stats = _train_step(
                model,
                optimizer,
                tensor_inputs,
                target_tensor,
                temperature=temp,
                config=effective_config,
                operator_family=operator_family,
            )
            if step_metrics is None:
                break
            fit_loss = step_metrics["fit_loss"]
            losses.append(fit_loss)
            trace.append(
                _trace_entry(
                    phase="fit",
                    step=step,
                    global_step=step,
                    temperature=temp,
                    metrics=step_metrics,
                    stats=stats,
                    operator_family=operator_family,
                )
            )
            final_stats = stats

        attempt_best_loss = min(losses) if losses else float("inf")
        log = {
            "restart": attempt_index,
            "random_restart": restart if attempt["kind"] == "random" else None,
            "seed": seed,
            "attempt_kind": attempt["kind"],
            "steps_completed": len(losses),
            "hardening_steps_completed": 0,
            "best_fit_loss": attempt_best_loss,
            "trace_schema": "eml.training_step_trace.v1",
            "trace": trace,
            "loss_summary": _loss_summary(trace),
            "final_anomalies": final_stats.as_dict(),
            "initialization": initialization_log,
            "candidate_ids": [],
        }

        legacy_candidate = _emit_candidate(
            model,
            inputs,
            target,
            candidate_id=f"attempt-{attempt_index:03d}-legacy-final-snap",
            attempt_index=attempt_index,
            random_restart=log["random_restart"],
            seed=seed,
            attempt_kind=str(attempt["kind"]),
            source="legacy_final_snap",
            checkpoint_index=None,
            hardening_step=None,
            global_step=max(len(losses) - 1, 0),
            temperature=_temperature(effective_config, max(len(losses) - 1, 0)),
            best_fit_loss=attempt_best_loss,
            config=effective_config,
        )
        candidates.append(legacy_candidate)
        log["candidate_ids"].append(legacy_candidate.candidate_id)

        hardening_completed = 0
        checkpoint_index = 0
        model.set_operator(_final_operator(effective_config))
        for hardening_step in range(effective_config.hardening_steps):
            temp = _hardening_temperature(effective_config, hardening_step)
            step_metrics, stats = _train_step(
                model,
                optimizer,
                tensor_inputs,
                target_tensor,
                temperature=temp,
                config=effective_config,
                operator_family=_final_operator(effective_config),
            )
            if step_metrics is None:
                break
            hardening_completed = hardening_step + 1
            trace.append(
                _trace_entry(
                    phase="hardening",
                    step=hardening_step,
                    global_step=effective_config.steps + hardening_step,
                    temperature=temp,
                    metrics=step_metrics,
                    stats=stats,
                    operator_family=_final_operator(effective_config),
                )
            )
            final_stats = stats
            if _should_emit_hardening_candidate(effective_config, hardening_step):
                candidate = _emit_candidate(
                    model,
                    inputs,
                    target,
                    candidate_id=f"attempt-{attempt_index:03d}-hardening-{checkpoint_index:02d}",
                    attempt_index=attempt_index,
                    random_restart=log["random_restart"],
                    seed=seed,
                    attempt_kind=str(attempt["kind"]),
                    source="hardening_checkpoint",
                    checkpoint_index=checkpoint_index,
                    hardening_step=hardening_step,
                    global_step=effective_config.steps + hardening_step,
                    temperature=temp,
                    best_fit_loss=attempt_best_loss,
                    config=effective_config,
                )
                candidates.append(candidate)
                log["candidate_ids"].append(candidate.candidate_id)
                checkpoint_index += 1

        log["hardening_steps_completed"] = hardening_completed
        log["loss_summary"] = _loss_summary(trace)
        log["final_anomalies"] = final_stats.as_dict()
        log["legacy_candidate_id"] = legacy_candidate.candidate_id
        restart_logs.append(log)

        if best is None or attempt_best_loss < best[0]:
            best = (attempt_best_loss, log)

    if best is None or not candidates:
        raise RuntimeError("No optimization restart completed")

    legacy_best_loss, best_log = best
    ranked_candidates, selection_mode = _select_exact_candidate(
        candidates,
        verification_splits=verification_splits,
        tolerance=tolerance,
    )
    selected_candidate = ranked_candidates[0]
    fallback_candidate = next(
        candidate
        for candidate in ranked_candidates
        if candidate.candidate_id == str(best_log["legacy_candidate_id"])
    )
    status = "snapped_candidate" if np.isfinite(selected_candidate.post_snap_loss) else "failed"
    manifest = {
        "schema": "eml.run_manifest.v1",
        "training_trace_schema": "eml.training_step_trace.v1",
        "config": _training_config_payload(effective_config),
        "operator_trace": _operator_trace(effective_config),
        "scaffold_exclusions": list(scaffold_plan.exclusions),
        "scaffold_witness_operator": initial_operator.as_dict(),
        "best_restart": best_log,
        "restarts": restart_logs,
        "trace_summary": _manifest_trace_summary(restart_logs),
        "semantics_alignment": _semantics_alignment_payload(effective_config, restart_logs, selected_candidate),
        "candidates": [candidate.as_dict() for candidate in ranked_candidates],
        "selection": {
            "mode": selection_mode,
            "candidate_count": len(candidates),
            "selected_candidate_id": selected_candidate.candidate_id,
            "fallback_candidate_id": fallback_candidate.candidate_id,
            "selected_attempt_index": selected_candidate.attempt_index,
            "selected_source": selected_candidate.source,
            "fallback_attempt_index": fallback_candidate.attempt_index,
            "fallback_source": fallback_candidate.source,
        },
        "selected_candidate": selected_candidate.as_dict(),
        "fallback_candidate": fallback_candidate.as_dict(),
        "snap": selected_candidate.snap.as_dict(),
        "best_loss": selected_candidate.best_fit_loss,
        "legacy_best_loss": legacy_best_loss,
        "post_snap_loss": selected_candidate.post_snap_loss,
        "timing": {
            "wall_clock_seconds": time.perf_counter() - wall_start,
            "attempt_count": len(restart_logs),
            "candidate_count": len(candidates),
        },
        "status": status,
    }
    return FitResult(
        status=status,
        best_loss=selected_candidate.best_fit_loss,
        post_snap_loss=selected_candidate.post_snap_loss,
        snap=selected_candidate.snap,
        manifest=manifest,
        verification=selected_candidate.verification,
        selected_candidate=selected_candidate,
        fallback_candidate=fallback_candidate,
        candidates=tuple(ranked_candidates),
    )


def _training_attempts(config: TrainingConfig, has_external_initializer: bool) -> list[dict[str, Any]]:
    attempts: list[dict[str, Any]] = []
    if not has_external_initializer:
        for phase_initializer in config.phase_initializers:
            if not _phase_initializer_supported(phase_initializer, config.operator_family):
                continue
            for variable in config.variables:
                attempts.append(
                    {
                        "kind": f"phase_initializer_{phase_initializer}",
                        "phase_initializer": phase_initializer,
                        "variable": variable,
                        "restart": -1,
                        "seed": config.seed,
                    }
                )
        known_scaffolds = set(known_scaffold_kinds())
        for scaffold in config.scaffold_initializers:
            if scaffold not in known_scaffolds:
                continue
            if scaffold == "log" and config.depth < 3:
                continue
            if scaffold == "scaled_exp" and config.depth < 9:
                continue
            for variable in config.variables:
                if scaffold == "scaled_exp":
                    for coefficient in _scaled_exp_constants(config.constants):
                        attempts.append(
                            {
                                "kind": "scaffold_scaled_exp",
                                "variable": variable,
                                "coefficient": coefficient,
                                "restart": -1,
                                "seed": config.seed,
                            }
                        )
                else:
                    attempts.append(
                        {
                            "kind": f"scaffold_{scaffold}",
                            "variable": variable,
                            "restart": -1,
                            "seed": config.seed,
                        }
                    )
    for restart in range(config.restarts):
        attempts.append(
            {
                "kind": "random",
                "variable": None,
                "restart": restart,
                "seed": config.seed + restart,
            }
        )
    return attempts


def _operator_for_step(config: TrainingConfig, step: int, total_steps: int) -> EmlOperator:
    if not config.operator_schedule:
        return config.operator_family
    if total_steps <= 1:
        return config.operator_schedule[-1]
    bucket = int((max(step, 0) * len(config.operator_schedule)) / total_steps)
    return config.operator_schedule[min(bucket, len(config.operator_schedule) - 1)]


def _final_operator(config: TrainingConfig) -> EmlOperator:
    return config.operator_schedule[-1] if config.operator_schedule else config.operator_family


def _training_config_payload(config: TrainingConfig) -> dict[str, Any]:
    payload = {
        key: value
        for key, value in config.__dict__.items()
        if key not in {"operator_family", "operator_schedule", "constants"}
    }
    payload["scaffold_initializers"] = list(config.scaffold_initializers)
    payload["phase_initializers"] = list(config.phase_initializers)
    payload["constants"] = [format_constant_value(value) for value in config.constants]
    payload.update(config.operator_payload())
    return payload


_PHASE_INITIALIZERS = ("ipi_phase_unit", "ipi_log_unit")


def known_phase_initializers() -> tuple[str, ...]:
    """Return generic, non-target-specific initializer names."""

    return _PHASE_INITIALIZERS


def _phase_initializer_supported(initializer: str, operator_family: EmlOperator) -> bool:
    if initializer.startswith("ipi_"):
        return operator_family.specialization == "ipi_eml"
    return False


def _apply_phase_initializer(model: SoftEMLTree, attempt: Mapping[str, Any]) -> dict[str, Any]:
    initializer = str(attempt["phase_initializer"])
    variable = str(attempt["variable"])
    if initializer == "ipi_phase_unit":
        expression = ipi_eml_expr(Var(variable), Const(1.0))
    elif initializer == "ipi_log_unit":
        expression = ipi_eml_expr(Const(1.0), Var(variable))
    else:
        raise ValueError(f"unknown phase initializer {initializer!r}")
    embedding = model.embed_expr(expression)
    return {
        "kind": f"phase_initializer_{initializer}",
        "phase_initializer": initializer,
        "variable": variable,
        "seed": attempt["seed"],
        "strategy": "generic_ipi_operator_primitive",
        "formula_leakage": False,
        "operator_family": model.operator_family.as_dict(),
        "embedding": embedding.as_dict(),
    }


def _operator_trace(config: TrainingConfig) -> list[dict[str, Any]]:
    if not config.operator_schedule:
        trace = [
            {
                "phase": "training",
                "start_step": 0,
                "end_step": max(config.steps - 1, 0),
                "operator": config.operator_family.as_dict(),
            }
        ]
    else:
        trace = []
        schedule = list(config.operator_schedule)
        total_steps = max(config.steps, 1)
        for index, operator in enumerate(schedule):
            start = int((index * total_steps) / len(schedule))
            end = int(((index + 1) * total_steps) / len(schedule)) - 1
            trace.append(
                {
                    "phase": "training",
                    "schedule_index": index,
                    "start_step": start,
                    "end_step": max(start, end),
                    "operator": operator.as_dict(),
                }
            )
    if config.hardening_steps > 0:
        trace.append(
            {
                "phase": "hardening",
                "start_step": config.steps,
                "end_step": config.steps + config.hardening_steps - 1,
                "operator": _final_operator(config).as_dict(),
            }
        )
    return trace


def _scaled_exp_constants(constants: tuple[complex, ...]) -> tuple[complex, ...]:
    result: list[complex] = []
    for value in constants:
        coefficient = complex(value)
        if not (np.isfinite(coefficient.real) and np.isfinite(coefficient.imag)):
            continue
        if abs(coefficient - 1.0) <= 1e-12:
            continue
        result.append(coefficient)
    return tuple(result)


def _apply_scaffold(model: SoftEMLTree, attempt: Mapping[str, Any]) -> dict[str, Any]:
    kind = str(attempt["kind"])
    variable = str(attempt["variable"])
    scaffold_kind = kind.removeprefix("scaffold_")
    if scaffold_witness_for(scaffold_kind, model.operator_family) is None:
        raise ValueError(f"{scaffold_kind}:{CENTERED_FAMILY_SAME_FAMILY_WITNESS_MISSING}")
    if kind == "scaffold_exp":
        model.force_exp(variable)
    elif kind == "scaffold_log":
        model.force_log(variable)
    elif kind == "scaffold_scaled_exp":
        coefficient = complex(attempt["coefficient"])
        embedding = model.force_scaled_exp(variable, coefficient)
        return {
            "kind": kind,
            "variable": variable,
            "coefficient": format_constant_value(coefficient),
            "constant_label": constant_label(coefficient),
            "seed": attempt["seed"],
            "strategy": "paper_scaled_exponential_family",
            "embedding": embedding.as_dict(),
        }
    else:
        raise ValueError(f"unknown scaffold initializer {kind!r}")
    return {
        "kind": kind,
        "variable": variable,
        "seed": attempt["seed"],
        "strategy": "generic_paper_primitive",
    }
