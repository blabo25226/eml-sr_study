"""Verifier-owned recovery status and numeric checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

import mpmath as mp
import numpy as np
import sympy as sp
import torch

from .branch import BRANCH_DIAGNOSTIC_SCHEMA, PRINCIPAL_LOG_BRANCH
from .expression import Candidate
from .semantics import AnomalyStats, TrainingSemanticsConfig


@dataclass(frozen=True)
class DataSplit:
    name: str
    inputs: dict[str, np.ndarray]
    target: np.ndarray
    target_mpmath: Callable[[Mapping[str, Any]], mp.mpc] | None = None
    target_sympy: sp.Expr | None = None
    role: str | None = None
    domain: dict[str, tuple[float, float]] | None = None

    def sample_mpmath_contexts(self, limit: int = 8) -> list[dict[str, Any]]:
        count = min(limit, len(next(iter(self.inputs.values()))))
        indices = np.linspace(0, len(next(iter(self.inputs.values()))) - 1, count, dtype=int)
        contexts: list[dict[str, Any]] = []
        for index in indices:
            contexts.append({name: values[index] for name, values in self.inputs.items()})
        return contexts


@dataclass(frozen=True)
class SplitResult:
    name: str
    max_abs_error: float
    mse: float
    max_imag_residue: float
    passed: bool
    role: str = "diagnostic"


@dataclass(frozen=True)
class VerificationReport:
    status: str
    candidate_kind: str
    reason: str
    split_results: list[SplitResult]
    high_precision_max_error: float
    tolerance: float
    high_precision_status: str = "performed"
    symbolic_status: str = "unsupported_no_target"
    dense_random_status: str = "unsupported_no_target_evaluator"
    adversarial_status: str = "unsupported_no_target_evaluator"
    certificate_status: str = "unsupported_interval_certificate"
    evidence_level: str = "split_numeric"
    metric_roles: dict[str, int] | None = None
    dense_random_max_error: float | None = None
    adversarial_max_error: float | None = None
    branch_diagnostics: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "candidate_kind": self.candidate_kind,
            "reason": self.reason,
            "tolerance": self.tolerance,
            "high_precision_max_error": self.high_precision_max_error,
            "high_precision_status": self.high_precision_status,
            "symbolic_status": self.symbolic_status,
            "dense_random_status": self.dense_random_status,
            "dense_random_max_error": self.dense_random_max_error,
            "adversarial_status": self.adversarial_status,
            "adversarial_max_error": self.adversarial_max_error,
            "branch_diagnostics": dict(self.branch_diagnostics or {}),
            "certificate_status": self.certificate_status,
            "evidence_level": self.evidence_level,
            "metric_roles": dict(self.metric_roles or {}),
            "split_results": [result.__dict__ for result in self.split_results],
        }


def split_role(split: DataSplit) -> str:
    """Return the metric role for a split, with compatibility inference from names."""

    if split.role:
        return split.role
    name = split.name.lower().replace("-", "_")
    if name in {"train", "training"} or name.startswith("train_"):
        return "training"
    if "final" in name or "confirmation" in name:
        return "final_confirmation"
    if "selection" in name or "rank" in name:
        return "selection"
    if "heldout" in name or "holdout" in name or "extrap" in name or "diagnostic" in name:
        return "diagnostic"
    return "verifier"


def metric_role_counts(splits: list[DataSplit]) -> dict[str, int]:
    counts = {"training": 0, "selection": 0, "diagnostic": 0, "verifier": 0, "final_confirmation": 0}
    for split in splits:
        role = split_role(split)
        counts[role] = counts.get(role, 0) + 1
    return counts


def selection_candidate_splits(splits: list[DataSplit]) -> list[DataSplit]:
    """Return splits allowed to influence candidate ranking."""

    return [split for split in splits if split_role(split) != "final_confirmation"]


def _target_scalar_from_split(split: DataSplit, context: Mapping[str, Any]) -> complex | mp.mpc:
    if split.target_mpmath is not None:
        return split.target_mpmath(context)
    matches = _matching_context_indices(split, context)
    target = np.asarray(split.target, dtype=np.complex128)
    target_values = target[matches]
    if not np.all(target_values == target_values[0]):
        raise ValueError("Context matches multiple target values in split")
    return complex(target_values[0])


def _matching_context_indices(split: DataSplit, context: Mapping[str, Any]) -> list[int]:
    matches: set[int] | None = None
    for name, values in split.inputs.items():
        if name not in context:
            raise ValueError(f"Context missing input {name!r}")
        current = {int(index) for index in np.where(np.asarray(values) == context[name])[0]}
        matches = current if matches is None else matches & current
    if not matches:
        raise ValueError("Could not find full context in split")
    return sorted(matches)


def _symbolic_status(candidate: Candidate, target_sympy: sp.Expr | None, splits: list[DataSplit]) -> str:
    symbolic_target = target_sympy if target_sympy is not None else next((split.target_sympy for split in splits if split.target_sympy is not None), None)
    if symbolic_target is None:
        return "unsupported_no_target"
    try:
        difference = sp.simplify(candidate.to_sympy() - symbolic_target)
    except Exception:  # noqa: BLE001 - verifier reports unsupported symbolic paths instead of failing the run.
        return "unsupported_symbolic_error"
    if difference == 0:
        return "passed"
    try:
        return "passed" if sp.simplify(difference) == 0 else "failed"
    except Exception:  # noqa: BLE001 - simplification can fail on branch-sensitive expressions.
        return "failed"


def _split_domain(split: DataSplit) -> dict[str, tuple[float, float]]:
    if split.domain is not None:
        return dict(split.domain)
    domain: dict[str, tuple[float, float]] = {}
    for name, values in split.inputs.items():
        real_values = np.asarray(values, dtype=np.float64)
        domain[name] = (float(np.min(real_values)), float(np.max(real_values)))
    return domain


def _probe_status(
    candidate: Candidate,
    splits: list[DataSplit],
    *,
    tolerance: float,
    mode: str,
    count: int,
    seed: int,
) -> tuple[str, float | None]:
    if count <= 0:
        return "skipped", None
    eligible = [split for split in splits if split.target_mpmath is not None]
    if not eligible:
        return "unsupported_no_target_evaluator", None
    max_error = 0.0
    any_context = False
    rng = np.random.default_rng(seed)
    for split in eligible:
        contexts = _random_probe_contexts(split, count=count, rng=rng) if mode == "dense_random" else _adversarial_contexts(split, count=count)
        for context in contexts:
            any_context = True
            try:
                mp.mp.dps = 80
                pred = candidate.evaluate_mpmath(context)
                target = mp.mpc(split.target_mpmath(context))
                max_error = max(max_error, float(abs(pred - target)))
            except Exception:  # noqa: BLE001 - probe failures are verifier failures for this layer.
                return "failed", float("inf")
    if not any_context:
        return "unsupported_no_domain", None
    return ("passed" if max_error <= tolerance else "failed"), max_error


def _random_probe_contexts(split: DataSplit, *, count: int, rng: np.random.Generator) -> list[dict[str, Any]]:
    domain = _split_domain(split)
    contexts: list[dict[str, Any]] = []
    for _ in range(count):
        contexts.append({name: float(rng.uniform(low, high)) for name, (low, high) in domain.items()})
    return contexts


def _adversarial_contexts(split: DataSplit, *, count: int) -> list[dict[str, Any]]:
    domain = _split_domain(split)
    if not domain:
        return []
    midpoint = {name: (low + high) / 2.0 for name, (low, high) in domain.items()}
    contexts: list[dict[str, Any]] = []
    for name, (low, high) in domain.items():
        width = max(abs(high - low), 1.0)
        epsilon = width * 1e-6
        for value in (low, low + epsilon, (low + high) / 2.0, high - epsilon, high):
            context = dict(midpoint)
            context[name] = float(value)
            contexts.append(context)
            if len(contexts) >= count:
                return contexts
        if low < 0.0 < high:
            for value in (-epsilon, epsilon):
                context = dict(midpoint)
                context[name] = float(value)
                contexts.append(context)
                if len(contexts) >= count:
                    return contexts
    return contexts[:count]


def _evidence_level(status: str, symbolic_status: str, dense_status: str, adversarial_status: str) -> str:
    if status not in {"recovered", "verified_showcase"}:
        return "failed"
    if symbolic_status == "passed":
        return "symbolic"
    if dense_status == "passed" and adversarial_status == "passed":
        return "dense_adversarial_numeric"
    return "split_numeric"


def verify_candidate(
    candidate: Candidate,
    splits: list[DataSplit],
    *,
    tolerance: float = 1e-8,
    high_precision_points: int = 8,
    high_precision_skip_factor: float = 1e6,
    recovered_requires_exact_eml: bool = True,
    target_sympy: sp.Expr | None = None,
    dense_random_points: int = 16,
    adversarial_points: int = 8,
    random_seed: int = 8675309,
) -> VerificationReport:
    """Verify a candidate over numeric splits and mpmath point checks."""

    split_results: list[SplitResult] = []
    all_passed = True
    hp_max = 0.0
    high_precision_status = "performed"

    for split in splits:
        pred = candidate.evaluate_numpy(split.inputs)
        target = np.asarray(split.target, dtype=np.complex128)
        residual = pred - target
        max_abs = float(np.max(np.abs(residual)))
        mse = float(np.mean(np.abs(residual) ** 2))
        max_imag = float(np.max(np.abs(np.imag(pred)))) if pred.size else 0.0
        passed = bool(max_abs <= tolerance)
        all_passed = all_passed and passed
        split_results.append(SplitResult(split.name, max_abs, mse, max_imag, passed, role=split_role(split)))
        numeric_failure_is_nonfinite = not np.isfinite(max_abs)
        numeric_failure_is_decisive = (not passed) and (numeric_failure_is_nonfinite or max_abs > tolerance * high_precision_skip_factor)
        if numeric_failure_is_decisive:
            high_precision_status = "skipped_numeric_failure"
            hp_max = float("inf") if numeric_failure_is_nonfinite else max(hp_max, max_abs)
            continue

        for context in split.sample_mpmath_contexts(high_precision_points):
            mp.mp.dps = 80
            pred_hp = candidate.evaluate_mpmath(context)
            target_hp = mp.mpc(_target_scalar_from_split(split, context))
            hp_max = max(hp_max, float(abs(pred_hp - target_hp)))

    hp_passed = hp_max <= tolerance
    all_passed = all_passed and hp_passed
    candidate_kind = getattr(candidate, "candidate_kind", "unknown")

    if all_passed and (candidate_kind == "exact_eml" or not recovered_requires_exact_eml):
        status = "recovered"
        reason = "verified"
    elif all_passed:
        status = "verified_showcase"
        reason = "verified_non_eml_candidate"
    elif not hp_passed and high_precision_status != "skipped_numeric_failure":
        status = "failed"
        reason = "mpmath_failed"
    else:
        failed = next((result.name for result in split_results if not result.passed), "unknown")
        status = "failed"
        reason = f"{failed}_failed"

    symbolic_status = _symbolic_status(candidate, target_sympy, splits)
    dense_random_status, dense_random_max_error = _probe_status(
        candidate,
        splits,
        tolerance=tolerance,
        mode="dense_random",
        count=dense_random_points,
        seed=random_seed,
    )
    adversarial_status, adversarial_max_error = _probe_status(
        candidate,
        splits,
        tolerance=tolerance,
        mode="adversarial",
        count=adversarial_points,
        seed=random_seed + 1,
    )
    certificate_status = "symbolic_equivalence" if symbolic_status == "passed" else "unsupported_interval_certificate"
    evidence_level = _evidence_level(status, symbolic_status, dense_random_status, adversarial_status)
    branch_diagnostics = _candidate_branch_diagnostics(candidate, splits, candidate_status=status)

    return VerificationReport(
        status=status,
        candidate_kind=candidate_kind,
        reason=reason,
        split_results=split_results,
        high_precision_max_error=hp_max,
        tolerance=tolerance,
        high_precision_status=high_precision_status,
        symbolic_status=symbolic_status,
        dense_random_status=dense_random_status,
        dense_random_max_error=dense_random_max_error,
        adversarial_status=adversarial_status,
        adversarial_max_error=adversarial_max_error,
        certificate_status=certificate_status,
        evidence_level=evidence_level,
        metric_roles=metric_role_counts(splits),
        branch_diagnostics=branch_diagnostics,
    )


def _candidate_branch_diagnostics(
    candidate: Candidate,
    splits: list[DataSplit],
    *,
    candidate_status: str,
) -> dict[str, Any]:
    if not hasattr(candidate, "evaluate_torch"):
        return {
            "schema": BRANCH_DIAGNOSTIC_SCHEMA,
            "status": "unsupported_candidate_no_torch_eval",
            "branch_convention": PRINCIPAL_LOG_BRANCH,
            "candidate_failure_class": "not_failed" if candidate_status != "failed" else "unknown_no_branch_probe",
            "branch_safety_guard": _branch_safety_guard_contract(),
        }

    stats = AnomalyStats()
    semantics = TrainingSemanticsConfig(mode="faithful")
    try:
        for split in splits:
            tensor_inputs = {name: torch.as_tensor(values, dtype=torch.complex128) for name, values in split.inputs.items()}
            candidate.evaluate_torch(tensor_inputs, training=False, stats=stats, semantics=semantics)  # type: ignore[attr-defined]
    except Exception as exc:  # noqa: BLE001 - branch probe must not mask verifier result.
        return {
            "schema": BRANCH_DIAGNOSTIC_SCHEMA,
            "status": "failed_during_branch_probe",
            "branch_convention": PRINCIPAL_LOG_BRANCH,
            "error": type(exc).__name__,
            "candidate_failure_class": "branch_probe_failed" if candidate_status == "failed" else "not_failed",
            "branch_safety_guard": _branch_safety_guard_contract(),
        }

    summary = stats.as_dict()
    branch_related = bool(
        summary["invalid_domain_skip_count"]
        or summary["log_branch_cut_count"]
        or summary["log_branch_cut_proximity_count"]
        or summary["log_branch_cut_crossing_count"]
    )
    return {
        "schema": BRANCH_DIAGNOSTIC_SCHEMA,
        "status": "performed",
        "branch_convention": PRINCIPAL_LOG_BRANCH,
        "input_count": summary["branch_input_count"],
        "non_finite_count": summary["log_non_finite_input_count"],
        "near_zero_count": summary["log_small_magnitude_count"],
        "branch_cut_hit_count": summary["log_branch_cut_count"],
        "branch_cut_proximity_count": summary["log_branch_cut_proximity_count"],
        "branch_cut_crossing_count": summary["log_branch_cut_crossing_count"],
        "min_branch_cut_distance": summary["log_branch_cut_min_distance"],
        "log_small_magnitude_count": summary["log_small_magnitude_count"],
        "log_non_positive_real_count": summary["log_non_positive_real_count"],
        "log_branch_cut_count": summary["log_branch_cut_count"],
        "log_branch_cut_proximity_count": summary["log_branch_cut_proximity_count"],
        "log_branch_cut_crossing_count": summary["log_branch_cut_crossing_count"],
        "log_branch_cut_min_distance": summary["log_branch_cut_min_distance"],
        "log_non_finite_input_count": summary["log_non_finite_input_count"],
        "invalid_domain_skip_count": summary["invalid_domain_skip_count"],
        "branch_related": branch_related,
        "candidate_failure_class": (
            "branch_related" if candidate_status == "failed" and branch_related else "not_branch_related" if candidate_status == "failed" else "not_failed"
        ),
        "branch_safety_guard": _branch_safety_guard_contract(),
    }


def _branch_safety_guard_contract() -> dict[str, Any]:
    return {
        "available": True,
        "training_only": True,
        "faithful_verification_unchanged": True,
        "config_fields": ["log_safety_weight", "log_safety_margin", "log_safety_imag_tolerance"],
    }
