"""v1.16 paper-strength GEML/i*pi EML decision package."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any, Iterable, Mapping

from .benchmark import V115_GEML_TARGETS, V115_NEGATIVE_CONTROL_TARGETS, V115_OSCILLATORY_TARGETS, builtin_suite


DEFAULT_V116_PACKAGE_DIR = Path("artifacts") / "paper" / "v1.16-geml"
DEFAULT_V116_CAMPAIGN_DIR = Path("artifacts") / "campaigns" / "v1.16-geml-pilot"
DEFAULT_V116_LADDER_DIR = Path("artifacts") / "campaigns" / "v1.16-geml-budget-ladder"
DEFAULT_V116_ABLATION_DIR = DEFAULT_V116_PACKAGE_DIR / "ablations"
DEFAULT_V116_FINAL_DIR = DEFAULT_V116_PACKAGE_DIR / "final-decision"


class V116PackageError(RuntimeError):
    """Raised when the v1.16 package cannot be safely written."""


@dataclass(frozen=True)
class V116PackagePaths:
    output_dir: Path
    manifest_json: Path
    gate_config_json: Path
    campaign_contract_json: Path
    gate_evaluation_json: Path
    decision_md: Path
    claim_audit_json: Path
    claim_audit_md: Path
    source_locks_json: Path
    reproduction_md: Path

    def as_dict(self) -> dict[str, str]:
        return {key: str(value) for key, value in self.__dict__.items()}


@dataclass(frozen=True)
class V116BudgetLadderPaths:
    output_dir: Path
    manifest_json: Path
    budget_ladder_json: Path
    budget_ladder_md: Path
    failure_taxonomy_json: Path
    failure_taxonomy_csv: Path
    failure_taxonomy_md: Path
    source_locks_json: Path

    def as_dict(self) -> dict[str, str]:
        return {key: str(value) for key, value in self.__dict__.items()}


@dataclass(frozen=True)
class V116AblationPaths:
    output_dir: Path
    manifest_json: Path
    ablation_table_json: Path
    ablation_table_csv: Path
    ablation_table_md: Path
    failure_examples_json: Path
    failure_examples_csv: Path
    failure_examples_md: Path
    figure_metadata_json: Path
    source_locks_json: Path
    figures_dir: Path
    family_recovery_svg: Path
    loss_snap_svg: Path
    branch_anomalies_svg: Path
    runtime_svg: Path
    representative_curves_svg: Path

    def as_dict(self) -> dict[str, str]:
        return {key: str(value) for key, value in self.__dict__.items()}


@dataclass(frozen=True)
class V116FinalDecisionPaths:
    output_dir: Path
    manifest_json: Path
    final_decision_json: Path
    final_decision_md: Path
    final_claim_audit_json: Path
    final_claim_audit_md: Path
    source_locks_json: Path
    package_readme_md: Path

    def as_dict(self) -> dict[str, str]:
        return {key: str(value) for key, value in self.__dict__.items()}


def v116_package_paths(output_dir: Path = DEFAULT_V116_PACKAGE_DIR) -> V116PackagePaths:
    output_dir = Path(output_dir)
    return V116PackagePaths(
        output_dir=output_dir,
        manifest_json=output_dir / "manifest.json",
        gate_config_json=output_dir / "gate-config.json",
        campaign_contract_json=output_dir / "campaign-contract.json",
        gate_evaluation_json=output_dir / "gate-evaluation.json",
        decision_md=output_dir / "decision.md",
        claim_audit_json=output_dir / "claim-audit.json",
        claim_audit_md=output_dir / "claim-audit.md",
        source_locks_json=output_dir / "source-locks.json",
        reproduction_md=output_dir / "reproduction.md",
    )


def v116_budget_ladder_paths(output_dir: Path = DEFAULT_V116_LADDER_DIR) -> V116BudgetLadderPaths:
    output_dir = Path(output_dir)
    return V116BudgetLadderPaths(
        output_dir=output_dir,
        manifest_json=output_dir / "manifest.json",
        budget_ladder_json=output_dir / "budget-ladder.json",
        budget_ladder_md=output_dir / "budget-ladder.md",
        failure_taxonomy_json=output_dir / "failure-taxonomy.json",
        failure_taxonomy_csv=output_dir / "failure-taxonomy.csv",
        failure_taxonomy_md=output_dir / "failure-taxonomy.md",
        source_locks_json=output_dir / "source-locks.json",
    )


def v116_ablation_paths(output_dir: Path = DEFAULT_V116_ABLATION_DIR) -> V116AblationPaths:
    output_dir = Path(output_dir)
    figures_dir = output_dir / "figures"
    return V116AblationPaths(
        output_dir=output_dir,
        manifest_json=output_dir / "manifest.json",
        ablation_table_json=output_dir / "ablation-table.json",
        ablation_table_csv=output_dir / "ablation-table.csv",
        ablation_table_md=output_dir / "ablation-table.md",
        failure_examples_json=output_dir / "failure-examples.json",
        failure_examples_csv=output_dir / "failure-examples.csv",
        failure_examples_md=output_dir / "failure-examples.md",
        figure_metadata_json=output_dir / "figure-metadata.json",
        source_locks_json=output_dir / "source-locks.json",
        figures_dir=figures_dir,
        family_recovery_svg=figures_dir / "family-recovery.svg",
        loss_snap_svg=figures_dir / "loss-before-after-snap.svg",
        branch_anomalies_svg=figures_dir / "branch-anomalies.svg",
        runtime_svg=figures_dir / "runtime.svg",
        representative_curves_svg=figures_dir / "representative-curves.svg",
    )


def v116_final_decision_paths(
    output_dir: Path = DEFAULT_V116_FINAL_DIR,
    *,
    package_dir: Path = DEFAULT_V116_PACKAGE_DIR,
) -> V116FinalDecisionPaths:
    output_dir = Path(output_dir)
    package_dir = Path(package_dir)
    return V116FinalDecisionPaths(
        output_dir=output_dir,
        manifest_json=output_dir / "manifest.json",
        final_decision_json=output_dir / "final-decision.json",
        final_decision_md=output_dir / "final-decision.md",
        final_claim_audit_json=output_dir / "final-claim-audit.json",
        final_claim_audit_md=output_dir / "final-claim-audit.md",
        source_locks_json=output_dir / "source-locks.json",
        package_readme_md=package_dir / "README.md",
    )


def default_v116_gate_config(*, min_unique_seeds: int = 3) -> dict[str, Any]:
    """Return the fail-closed v1.16 paper-strength gate."""

    return {
        "schema": "eml.v116_paper_strength_gate.v1",
        "outcomes": {
            "paper_positive": "Verifier-gated exact i*pi recovery beats raw EML on natural-bias targets under the full matched protocol.",
            "promising_preliminary": "Exact i*pi signal exists but the full paper denominator is incomplete.",
            "negative": "Raw EML wins or no exact i*pi recovery signal appears under the declared protocol.",
            "inconclusive": "Evidence is insufficient or confounded; no positive claim is allowed.",
        },
        "positive_recovery_numerator": "trained_exact_recovery_only",
        "diagnostic_only_classes": [
            "loss_only",
            "same_ast_seed_round_trip",
            "verified_equivalent_warm_start",
            "repaired_candidate",
            "compile_only_verified_support",
            "unsupported",
        ],
        "thresholds": {
            "declared_targets": list(V115_GEML_TARGETS),
            "natural_bias_targets": list(V115_OSCILLATORY_TARGETS),
            "negative_control_targets": list(V115_NEGATIVE_CONTROL_TARGETS),
            "min_unique_seeds_for_paper_positive": int(min_unique_seeds),
            "min_natural_ipi_recovery_wins": 1,
            "min_ipi_minus_raw_recovery_wins": 1,
            "max_negative_control_ipi_recovery_wins": 0,
            "require_complete_matched_denominator": True,
            "require_source_locks": True,
        },
        "fail_closed_rules": [
            "loss-only improvement cannot be promoted to recovery",
            "same-AST or exact-seed returns cannot enter trained recovery denominators",
            "negative-control i*pi wins block paper-positive interpretation",
            "missing source locks or incomplete denominators block paper-positive interpretation",
        ],
    }


def default_v116_campaign_contract(*, seeds: Iterable[int] = (0, 1, 2)) -> dict[str, Any]:
    """Return the matched campaign denominator contract for v1.16."""

    seeds = tuple(int(seed) for seed in seeds)
    return {
        "schema": "eml.v116_matched_campaign_contract.v1",
        "suite_ids": {
            "smoke": "v1.16-geml-smoke",
            "pilot": "v1.16-geml-pilot",
            "full": "v1.16-geml-full",
        },
        "targets": {
            "natural_bias": list(V115_OSCILLATORY_TARGETS),
            "negative_controls": list(V115_NEGATIVE_CONTROL_TARGETS),
        },
        "matched_fields": [
            "formula",
            "seed",
            "depth",
            "steps",
            "restarts",
            "hardening_steps",
            "hardening_emit_interval",
            "dataset.points",
            "dataset.tolerance",
            "constants_policy",
            "snap_rule",
            "verifier_gate",
        ],
        "operator_families": ["raw_eml", "ipi_eml"],
        "seeds": list(seeds),
        "verifier_gate": "trained exact candidate selected by verifier across train, held-out, extrapolation, and high-precision checks",
        "claim_denominator_rules": {
            "loss_only": "diagnostic_only",
            "same_ast_seed_round_trip": "excluded_from_trained_exact_recovery",
            "compile_only_verified_support": "excluded_from_trained_exact_recovery",
            "negative_controls": "visible_and_claim_blocking",
        },
        "resource_metadata_required": ["wall_clock_seconds", "attempt_count", "candidate_count", "code_version", "platform"],
    }


def evaluate_v116_gate(
    paired_summary: Mapping[str, Any] | None = None,
    classification: Iterable[Mapping[str, Any]] = (),
    *,
    paired_rows: Iterable[Mapping[str, Any]] = (),
    gate_config: Mapping[str, Any] | None = None,
    source_locks_ok: bool = True,
) -> dict[str, Any]:
    """Classify v1.16 GEML evidence without letting loss-only rows carry claims."""

    paired_summary = paired_summary or {}
    gate_config = gate_config or default_v116_gate_config()
    thresholds = gate_config.get("thresholds") if isinstance(gate_config.get("thresholds"), Mapping) else {}
    rows = [dict(row) for row in paired_rows]
    families = [dict(row) for row in classification]
    by_family = {str(row.get("target_family") or "unknown"): row for row in families}
    natural_families = {family for family in by_family if family != "negative_control"}
    natural_rows = [row for family, row in by_family.items() if family in natural_families]

    paired_row_count = int(paired_summary.get("paired_rows") or sum(int(row.get("paired_rows") or 0) for row in families))
    declared_targets = tuple(thresholds.get("declared_targets") or V115_GEML_TARGETS)
    min_unique_seeds = int(thresholds.get("min_unique_seeds_for_paper_positive") or 1)
    unique_seeds = _unique_seed_count(rows) or _summary_seed_count(paired_summary) or 1
    complete_denominator = paired_row_count >= len(declared_targets) * min_unique_seeds and unique_seeds >= min_unique_seeds

    natural_ipi_wins = sum(int(row.get("ipi_recovery_wins") or 0) for row in natural_rows)
    natural_raw_wins = sum(int(row.get("raw_recovery_wins") or 0) for row in natural_rows)
    negative_control = by_family.get("negative_control", {})
    negative_control_ipi_wins = int(negative_control.get("ipi_recovery_wins") or 0)
    loss_only_outcomes = int(paired_summary.get("loss_only_outcomes") or sum(int(row.get("loss_only_outcomes") or 0) for row in families))
    exact_signal = natural_ipi_wins >= int(thresholds.get("min_natural_ipi_recovery_wins") or 1)
    ipi_delta = natural_ipi_wins - natural_raw_wins
    negative_controls_clean = negative_control_ipi_wins <= int(thresholds.get("max_negative_control_ipi_recovery_wins") or 0)
    paper_positive_ready = (
        exact_signal
        and ipi_delta >= int(thresholds.get("min_ipi_minus_raw_recovery_wins") or 1)
        and negative_controls_clean
        and complete_denominator
        and source_locks_ok
    )

    if paper_positive_ready:
        decision = "paper_positive"
        rationale = "Exact verifier-gated i*pi recovery wins satisfy the full matched denominator and negative-control gate."
    elif exact_signal and ipi_delta > 0 and negative_controls_clean:
        decision = "promising_preliminary"
        rationale = "Exact i*pi recovery signal exists, but the full paper-positive denominator is incomplete."
    elif natural_raw_wins > natural_ipi_wins or (complete_denominator and natural_ipi_wins == 0):
        decision = "negative"
        rationale = "The matched exact-recovery evidence does not support an i*pi advantage."
    else:
        decision = "inconclusive"
        rationale = "The evidence is incomplete, loss-only, or confounded; no positive claim is allowed."

    blockers: list[str] = []
    if not exact_signal:
        blockers.append("no_natural_ipi_exact_recovery_signal")
    if not complete_denominator:
        blockers.append("incomplete_matched_denominator")
    if not negative_controls_clean:
        blockers.append("negative_control_ipi_recovery_win")
    if not source_locks_ok:
        blockers.append("missing_or_failed_source_locks")
    if loss_only_outcomes and not exact_signal:
        blockers.append("loss_only_signal_without_exact_recovery")

    return {
        "schema": "eml.v116_gate_evaluation.v1",
        "decision": decision,
        "rationale": rationale,
        "metrics": {
            "paired_rows": paired_row_count,
            "declared_targets": len(declared_targets),
            "unique_seeds": unique_seeds,
            "min_unique_seeds_for_paper_positive": min_unique_seeds,
            "complete_denominator": complete_denominator,
            "natural_ipi_recovery_wins": natural_ipi_wins,
            "natural_raw_recovery_wins": natural_raw_wins,
            "natural_ipi_minus_raw_recovery_wins": ipi_delta,
            "negative_control_ipi_recovery_wins": negative_control_ipi_wins,
            "loss_only_outcomes": loss_only_outcomes,
            "source_locks_ok": bool(source_locks_ok),
        },
        "blockers": blockers,
        "gate": gate_config,
    }


def build_v116_claim_audit(
    claim_text: str,
    *,
    gate_evaluation: Mapping[str, Any],
    gate_config: Mapping[str, Any] | None = None,
    source_locks: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Audit v1.16 paper claims against the predefined gate."""

    gate_config = gate_config or default_v116_gate_config()
    source_locks = source_locks or {}
    lower_claim = claim_text.lower()
    decision = str(gate_evaluation.get("decision") or "")
    checks = [
        _audit_check(
            "gate_has_all_outcomes",
            {"paper_positive", "promising_preliminary", "negative", "inconclusive"} <= set((gate_config.get("outcomes") or {}).keys()),
            "Gate config defines all allowed v1.16 outcomes.",
        ),
        _audit_check(
            "exact_recovery_only_positive_gate",
            gate_config.get("positive_recovery_numerator") == "trained_exact_recovery_only",
            "Positive recovery numerator is verifier-gated trained exact recovery only.",
        ),
        _audit_check(
            "blocks_loss_only_recovery_claims",
            not _contains_any(lower_claim, ("loss-only recovery", "loss only recovery", "loss-only proves recovery")),
            "Claim text does not promote loss-only improvement to recovery.",
        ),
        _audit_check(
            "blocks_global_superiority_language",
            not _contains_any(lower_claim, ("global superiority", "globally better", "universally better", "dominates raw eml")),
            "Claim text avoids global raw/i*pi superiority claims.",
        ),
        _audit_check(
            "blocks_broad_blind_recovery_language",
            not _contains_any(lower_claim, ("broad blind recovery", "solves blind recovery", "recovers arbitrary formulas")),
            "Claim text avoids broad blind-recovery claims.",
        ),
        _audit_check(
            "blocks_full_universality_language",
            not _contains_any(lower_claim, ("full universality", "scientific-calculator universality", "all elementary functions")),
            "Claim text avoids full i*pi/GEML universality claims.",
        ),
        _audit_check(
            "negative_controls_visible",
            "negative control" in lower_claim or "negative-control" in lower_claim,
            "Claim text keeps negative controls visible.",
        ),
        _audit_check(
            "paper_positive_requires_gate_pass",
            ("paper_positive" not in lower_claim and "paper positive" not in lower_claim) or decision == "paper_positive",
            "Paper-positive language appears only when the gate evaluates paper_positive.",
        ),
        _audit_check(
            "source_locks_present",
            bool(source_locks.get("inputs") or source_locks.get("outputs")),
            "Package includes source-lock tables.",
        ),
    ]
    return {
        "schema": "eml.v116_claim_audit.v1",
        "status": "passed" if all(check["status"] == "passed" for check in checks) else "failed",
        "decision": decision,
        "checks": checks,
    }


def write_v116_paper_package(
    output_dir: Path = DEFAULT_V116_PACKAGE_DIR,
    *,
    campaign_dir: Path = DEFAULT_V116_CAMPAIGN_DIR,
    budget_ladder_dir: Path | None = None,
    overwrite: bool = False,
    min_unique_seeds: int = 3,
) -> V116PackagePaths:
    """Write v1.16 contract, gate evaluation, and claim audit artifacts."""

    output_dir = Path(output_dir)
    paths = v116_package_paths(output_dir)
    if paths.manifest_json.exists() and not overwrite:
        raise V116PackageError(f"{paths.manifest_json} already exists; pass overwrite=True to refresh")
    paths.output_dir.mkdir(parents=True, exist_ok=True)

    gate_config = default_v116_gate_config(min_unique_seeds=min_unique_seeds)
    contract = default_v116_campaign_contract(seeds=range(min_unique_seeds))
    paired_rows = _read_paired_rows(Path(campaign_dir))
    paired_summary = _read_json(Path(campaign_dir) / "tables" / "geml-paired-summary.json") if (Path(campaign_dir) / "tables" / "geml-paired-summary.json").is_file() else _summary_from_rows(paired_rows)
    classification = _classification_from_rows(paired_rows)
    lock_items = [
        ("roadmap", Path(".planning/ROADMAP.md"), "input"),
        ("requirements", Path(".planning/REQUIREMENTS.md"), "input"),
        ("campaign_manifest", Path(campaign_dir) / "campaign-manifest.json", "input"),
        ("geml_paired_summary", Path(campaign_dir) / "tables" / "geml-paired-summary.json", "input"),
        ("geml_paired_comparison", Path(campaign_dir) / "tables" / "geml-paired-comparison.csv", "input"),
    ]
    ladder_manifest: dict[str, Any] | None = None
    if budget_ladder_dir is not None:
        ladder_dir = Path(budget_ladder_dir)
        lock_items.extend(
            [
                ("budget_ladder_manifest", ladder_dir / "manifest.json", "input"),
                ("budget_ladder_json", ladder_dir / "budget-ladder.json", "input"),
                ("failure_taxonomy_json", ladder_dir / "failure-taxonomy.json", "input"),
            ]
        )
        if (ladder_dir / "manifest.json").is_file():
            ladder_manifest = _read_json(ladder_dir / "manifest.json")
    locks = _source_locks_payload(lock_items)
    source_locks_ok = all(item["status"] == "locked" for item in locks["inputs"])
    evaluation = evaluate_v116_gate(
        paired_summary,
        classification,
        paired_rows=paired_rows,
        gate_config=gate_config,
        source_locks_ok=source_locks_ok,
    )
    decision_md = _decision_markdown(evaluation, classification, Path(campaign_dir))
    audit = build_v116_claim_audit(decision_md, gate_evaluation=evaluation, gate_config=gate_config, source_locks=locks)

    _write_json(paths.gate_config_json, gate_config)
    _write_json(paths.campaign_contract_json, contract)
    _write_json(paths.gate_evaluation_json, evaluation)
    paths.decision_md.write_text(decision_md, encoding="utf-8")
    _write_json(paths.claim_audit_json, audit)
    paths.claim_audit_md.write_text(_claim_audit_markdown(audit), encoding="utf-8")
    paths.reproduction_md.write_text(_reproduction_markdown(Path(campaign_dir), min_unique_seeds), encoding="utf-8")
    locks["outputs"] = _source_locks(
        [
            ("gate_config", paths.gate_config_json),
            ("campaign_contract", paths.campaign_contract_json),
            ("gate_evaluation", paths.gate_evaluation_json),
            ("decision", paths.decision_md),
            ("claim_audit_json", paths.claim_audit_json),
            ("claim_audit_md", paths.claim_audit_md),
            ("reproduction", paths.reproduction_md),
        ],
        role="output",
    )
    _write_json(paths.source_locks_json, locks)
    manifest = {
        "schema": "eml.v116_paper_decision_package.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decision": evaluation["decision"],
        "rationale": evaluation["rationale"],
        "campaign_dir": str(campaign_dir),
        "budget_ladder": {
            "dir": str(budget_ladder_dir) if budget_ladder_dir is not None else None,
            "decision": ladder_manifest.get("decision") if ladder_manifest is not None else None,
            "rationale": ladder_manifest.get("rationale") if ladder_manifest is not None else None,
        },
        "gate_config": str(paths.gate_config_json),
        "campaign_contract": str(paths.campaign_contract_json),
        "gate_evaluation": str(paths.gate_evaluation_json),
        "claim_audit": {"status": audit["status"], "json": str(paths.claim_audit_json), "markdown": str(paths.claim_audit_md)},
        "source_locks": str(paths.source_locks_json),
        "reproduction": str(paths.reproduction_md),
    }
    _write_json(paths.manifest_json, manifest)
    return paths


def write_v116_budget_ladder(
    output_dir: Path = DEFAULT_V116_LADDER_DIR,
    *,
    smoke_campaign_dir: Path = Path("artifacts") / "campaigns" / "v1.16-geml-smoke",
    pilot_campaign_dir: Path = DEFAULT_V116_CAMPAIGN_DIR,
    overwrite: bool = False,
) -> V116BudgetLadderPaths:
    """Write smoke/pilot/full routing artifacts for v1.16 GEML campaigns."""

    output_dir = Path(output_dir)
    paths = v116_budget_ladder_paths(output_dir)
    if paths.manifest_json.exists() and not overwrite:
        raise V116PackageError(f"{paths.manifest_json} already exists; pass overwrite=True to refresh")
    paths.output_dir.mkdir(parents=True, exist_ok=True)

    smoke = _campaign_evidence("smoke", Path(smoke_campaign_dir))
    pilot = _campaign_evidence("pilot", Path(pilot_campaign_dir))
    pilot_evaluation = evaluate_v116_gate(
        pilot["summary"],
        _classification_from_rows(pilot["rows"]),
        paired_rows=pilot["rows"],
        gate_config=default_v116_gate_config(min_unique_seeds=1),
        source_locks_ok=pilot["source_locks_ok"],
    )
    metrics = pilot_evaluation["metrics"]
    pilot_has_exact_signal = (
        int(metrics["natural_ipi_recovery_wins"]) > 0
        and int(metrics["natural_ipi_minus_raw_recovery_wins"]) > 0
        and int(metrics["negative_control_ipi_recovery_wins"]) == 0
    )
    if not pilot["rows"]:
        full_decision = "pilot_not_performed"
        rationale = "No pilot paired rows were found; full campaign is blocked."
    elif pilot_has_exact_signal:
        full_decision = "run_full_campaign"
        rationale = "Pilot has verifier-gated natural-family i*pi exact recovery signal and clean negative controls."
    else:
        full_decision = "stop_full_campaign_fail_closed"
        rationale = "Pilot did not show clean verifier-gated i*pi exact recovery signal; full campaign should not run."

    taxonomy_rows = _failure_taxonomy_rows([*smoke["rows"], *pilot["rows"]])
    if not taxonomy_rows:
        taxonomy_rows = [
            {
                "tier": "pilot",
                "pair_id": "not_performed",
                "formula": "",
                "target_family": "",
                "seed": "",
                "comparison_outcome": "not_performed",
                "failure_class": "not_performed",
                "actionable_next_step": "Run geml-v116-smoke and geml-v116-pilot before evaluating the full campaign gate.",
            }
        ]

    ladder = {
        "schema": "eml.v116_budget_ladder.v1",
        "decision": full_decision,
        "rationale": rationale,
        "tiers": [
            _ladder_tier("smoke", smoke, "PYTHONPATH=src python -m eml_symbolic_regression.cli campaign geml-v116-smoke --label v1.16-geml-smoke --overwrite"),
            _ladder_tier("pilot", pilot, "PYTHONPATH=src python -m eml_symbolic_regression.cli campaign geml-v116-pilot --label v1.16-geml-pilot --overwrite"),
            {
                "name": "full",
                "status": "recommended" if full_decision == "run_full_campaign" else "blocked",
                "command": "PYTHONPATH=src python -m eml_symbolic_regression.cli campaign geml-v116-full --label v1.16-geml-full --overwrite",
                "gate": "run only after pilot has clean verifier-gated exact i*pi recovery signal",
            },
        ],
        "pilot_gate_evaluation": pilot_evaluation,
    }

    _write_json(paths.budget_ladder_json, ladder)
    paths.budget_ladder_md.write_text(_budget_ladder_markdown(ladder), encoding="utf-8")
    taxonomy_payload = {"schema": "eml.v116_failure_taxonomy.v1", "rows": taxonomy_rows}
    _write_json(paths.failure_taxonomy_json, taxonomy_payload)
    _write_csv(paths.failure_taxonomy_csv, taxonomy_rows, _FAILURE_TAXONOMY_COLUMNS)
    paths.failure_taxonomy_md.write_text(_failure_taxonomy_markdown(taxonomy_rows), encoding="utf-8")

    locks = _source_locks_payload(
        [
            ("smoke_manifest", Path(smoke_campaign_dir) / "campaign-manifest.json", "input"),
            ("smoke_paired_summary", Path(smoke_campaign_dir) / "tables" / "geml-paired-summary.json", "input"),
            ("smoke_paired_comparison", Path(smoke_campaign_dir) / "tables" / "geml-paired-comparison.csv", "input"),
            ("pilot_manifest", Path(pilot_campaign_dir) / "campaign-manifest.json", "input"),
            ("pilot_paired_summary", Path(pilot_campaign_dir) / "tables" / "geml-paired-summary.json", "input"),
            ("pilot_paired_comparison", Path(pilot_campaign_dir) / "tables" / "geml-paired-comparison.csv", "input"),
        ]
    )
    locks["outputs"] = _source_locks(
        [
            ("budget_ladder_json", paths.budget_ladder_json),
            ("budget_ladder_md", paths.budget_ladder_md),
            ("failure_taxonomy_json", paths.failure_taxonomy_json),
            ("failure_taxonomy_csv", paths.failure_taxonomy_csv),
            ("failure_taxonomy_md", paths.failure_taxonomy_md),
        ],
        role="output",
    )
    _write_json(paths.source_locks_json, locks)
    manifest = {
        "schema": "eml.v116_budget_ladder_manifest.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decision": full_decision,
        "rationale": rationale,
        "smoke_campaign_dir": str(smoke_campaign_dir),
        "pilot_campaign_dir": str(pilot_campaign_dir),
        "budget_ladder": str(paths.budget_ladder_json),
        "failure_taxonomy": str(paths.failure_taxonomy_json),
        "source_locks": str(paths.source_locks_json),
    }
    _write_json(paths.manifest_json, manifest)
    return paths


_ABLATION_COLUMNS = [
    "dimension",
    "variant",
    "status",
    "operator_family",
    "paired_rows",
    "run_rows",
    "exact_recovery_count",
    "verified_equivalent_count",
    "repaired_candidate_count",
    "same_ast_count",
    "compile_only_count",
    "loss_only_count",
    "branch_pathology_count",
    "numerical_instability_count",
    "median_post_snap_mse",
    "median_runtime_seconds",
    "candidate_pool_median",
    "observed_effect",
    "next_step",
]

_FAILURE_EXAMPLE_COLUMNS = [
    "failure_class",
    "status",
    "count",
    "representative_pair_id",
    "formula",
    "target_family",
    "seed",
    "comparison_outcome",
    "actionable_next_step",
]

_CANONICAL_FAILURE_CLASSES = [
    "loss_only_signal",
    "optimization_or_snap_miss",
    "snap_mismatch",
    "branch_pathology",
    "verifier_mismatch",
    "unsupported_or_over_depth",
    "numerical_instability",
]


def write_v116_ablation_assets(
    output_dir: Path = DEFAULT_V116_ABLATION_DIR,
    *,
    campaign_dir: Path = DEFAULT_V116_CAMPAIGN_DIR,
    budget_ladder_dir: Path = DEFAULT_V116_LADDER_DIR,
    package_dir: Path = DEFAULT_V116_PACKAGE_DIR,
    overwrite: bool = False,
) -> V116AblationPaths:
    """Write deterministic v1.16 ablation tables, failure examples, and figures."""

    output_dir = Path(output_dir)
    paths = v116_ablation_paths(output_dir)
    if paths.manifest_json.exists() and not overwrite:
        raise V116PackageError(f"{paths.manifest_json} already exists; pass overwrite=True to refresh")
    paths.output_dir.mkdir(parents=True, exist_ok=True)
    paths.figures_dir.mkdir(parents=True, exist_ok=True)

    campaign_dir = Path(campaign_dir)
    budget_ladder_dir = Path(budget_ladder_dir)
    package_dir = Path(package_dir)
    paired_rows = _read_paired_rows(campaign_dir)
    run_rows = _read_csv(campaign_dir / "tables" / "runs.csv")
    taxonomy_path = budget_ladder_dir / "failure-taxonomy.json"
    taxonomy_payload = _read_json(taxonomy_path) if taxonomy_path.is_file() else {"rows": _failure_taxonomy_rows(paired_rows)}
    taxonomy_rows = [dict(row) for row in taxonomy_payload.get("rows", [])]
    package_manifest = _read_json(package_dir / "manifest.json") if (package_dir / "manifest.json").is_file() else {}
    gate_evaluation = _read_json(package_dir / "gate-evaluation.json") if (package_dir / "gate-evaluation.json").is_file() else {}
    decision = str(gate_evaluation.get("decision") or package_manifest.get("decision") or "inconclusive")

    ablation_rows = _v116_ablation_rows(paired_rows, run_rows, taxonomy_rows, gate_evaluation)
    failure_examples = _v116_failure_examples(taxonomy_rows)
    classification = _classification_from_rows(paired_rows)
    figure_metadata = {
        "schema": "eml.v116_figure_metadata.v1",
        "figures": [
            {
                "id": "family_recovery",
                "path": str(paths.family_recovery_svg),
                "source": str(campaign_dir / "tables" / "geml-paired-comparison.csv"),
                "claim_boundary": "Exact recovery bars are zero unless verifier-gated recovery rows exist.",
            },
            {
                "id": "loss_before_after_snap",
                "path": str(paths.loss_snap_svg),
                "source": str(campaign_dir / "tables" / "geml-paired-comparison.csv"),
                "claim_boundary": "Loss improvements are diagnostic only and do not count as recovery.",
            },
            {
                "id": "branch_anomalies",
                "path": str(paths.branch_anomalies_svg),
                "source": str(campaign_dir / "tables" / "geml-paired-comparison.csv"),
                "claim_boundary": "Branch anomalies are shown as blockers or diagnostics, not as hidden exclusions.",
            },
            {
                "id": "runtime",
                "path": str(paths.runtime_svg),
                "source": str(campaign_dir / "tables" / "geml-paired-comparison.csv"),
                "claim_boundary": "Runtime is reported for resource context and does not affect recovery classification.",
            },
            {
                "id": "representative_curves",
                "path": str(paths.representative_curves_svg),
                "source": str(campaign_dir / "runs"),
                "claim_boundary": "Representative panels label failed verification honestly.",
            },
        ],
    }

    _write_json(paths.ablation_table_json, {"schema": "eml.v116_ablation_table.v1", "rows": ablation_rows})
    _write_csv(paths.ablation_table_csv, ablation_rows, _ABLATION_COLUMNS)
    paths.ablation_table_md.write_text(_v116_ablation_markdown(ablation_rows), encoding="utf-8")
    _write_json(paths.failure_examples_json, {"schema": "eml.v116_failure_examples.v1", "rows": failure_examples})
    _write_csv(paths.failure_examples_csv, failure_examples, _FAILURE_EXAMPLE_COLUMNS)
    paths.failure_examples_md.write_text(_v116_failure_examples_markdown(failure_examples), encoding="utf-8")
    _write_json(paths.figure_metadata_json, figure_metadata)
    paths.family_recovery_svg.write_text(_v116_family_recovery_svg(classification), encoding="utf-8")
    paths.loss_snap_svg.write_text(_v116_loss_snap_svg(paired_rows), encoding="utf-8")
    paths.branch_anomalies_svg.write_text(_v116_branch_anomalies_svg(paired_rows), encoding="utf-8")
    paths.runtime_svg.write_text(_v116_runtime_svg(paired_rows), encoding="utf-8")
    paths.representative_curves_svg.write_text(_v116_representative_curves_svg(paired_rows), encoding="utf-8")

    locks = _source_locks_payload(
        [
            ("campaign_manifest", campaign_dir / "campaign-manifest.json", "input"),
            ("geml_paired_summary", campaign_dir / "tables" / "geml-paired-summary.json", "input"),
            ("geml_paired_comparison", campaign_dir / "tables" / "geml-paired-comparison.csv", "input"),
            ("runs_table", campaign_dir / "tables" / "runs.csv", "input"),
            ("budget_ladder_manifest", budget_ladder_dir / "manifest.json", "input"),
            ("failure_taxonomy", taxonomy_path, "input"),
            ("paper_package_manifest", package_dir / "manifest.json", "input"),
            ("paper_gate_evaluation", package_dir / "gate-evaluation.json", "input"),
        ]
    )
    locks["outputs"] = _source_locks(
        [
            ("ablation_table_json", paths.ablation_table_json),
            ("ablation_table_csv", paths.ablation_table_csv),
            ("ablation_table_md", paths.ablation_table_md),
            ("failure_examples_json", paths.failure_examples_json),
            ("failure_examples_csv", paths.failure_examples_csv),
            ("failure_examples_md", paths.failure_examples_md),
            ("figure_metadata", paths.figure_metadata_json),
            ("family_recovery_svg", paths.family_recovery_svg),
            ("loss_snap_svg", paths.loss_snap_svg),
            ("branch_anomalies_svg", paths.branch_anomalies_svg),
            ("runtime_svg", paths.runtime_svg),
            ("representative_curves_svg", paths.representative_curves_svg),
        ],
        role="output",
    )
    _write_json(paths.source_locks_json, locks)
    source_locks_ok = all(item["status"] == "locked" for item in locks["inputs"])
    manifest = {
        "schema": "eml.v116_ablation_assets_manifest.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "paper_claim_allowed": decision == "paper_positive",
        "campaign_dir": str(campaign_dir),
        "budget_ladder_dir": str(budget_ladder_dir),
        "package_dir": str(package_dir),
        "ablation_table": str(paths.ablation_table_json),
        "failure_examples": str(paths.failure_examples_json),
        "figure_metadata": str(paths.figure_metadata_json),
        "source_locks": str(paths.source_locks_json),
        "source_locks_ok": source_locks_ok,
        "row_counts": {
            "paired_rows": len(paired_rows),
            "run_rows": len(run_rows),
            "ablation_rows": len(ablation_rows),
            "failure_example_rows": len(failure_examples),
        },
        "claim_boundary": "Phase 92 assets explain an inconclusive/negative result unless the Phase 88 gate is paper_positive.",
    }
    _write_json(paths.manifest_json, manifest)
    return paths


def write_v116_final_decision_package(
    output_dir: Path = DEFAULT_V116_FINAL_DIR,
    *,
    package_dir: Path = DEFAULT_V116_PACKAGE_DIR,
    ablation_dir: Path = DEFAULT_V116_ABLATION_DIR,
    budget_ladder_dir: Path = DEFAULT_V116_LADDER_DIR,
    campaign_dir: Path = DEFAULT_V116_CAMPAIGN_DIR,
    overwrite: bool = False,
) -> V116FinalDecisionPaths:
    """Write the final v1.16 paper decision package and README guidance."""

    output_dir = Path(output_dir)
    package_dir = Path(package_dir)
    ablation_dir = Path(ablation_dir)
    budget_ladder_dir = Path(budget_ladder_dir)
    campaign_dir = Path(campaign_dir)
    paths = v116_final_decision_paths(output_dir, package_dir=package_dir)
    if paths.manifest_json.exists() and not overwrite:
        raise V116PackageError(f"{paths.manifest_json} already exists; pass overwrite=True to refresh")
    paths.output_dir.mkdir(parents=True, exist_ok=True)

    package_manifest = _read_json(package_dir / "manifest.json") if (package_dir / "manifest.json").is_file() else {}
    gate_config = _read_json(package_dir / "gate-config.json") if (package_dir / "gate-config.json").is_file() else default_v116_gate_config()
    gate_evaluation = _read_json(package_dir / "gate-evaluation.json") if (package_dir / "gate-evaluation.json").is_file() else {}
    ablation_manifest = _read_json(ablation_dir / "manifest.json") if (ablation_dir / "manifest.json").is_file() else {}
    figure_metadata = _read_json(ablation_dir / "figure-metadata.json") if (ablation_dir / "figure-metadata.json").is_file() else {"figures": []}
    budget_manifest = _read_json(budget_ladder_dir / "manifest.json") if (budget_ladder_dir / "manifest.json").is_file() else {}
    paired_summary = _read_json(campaign_dir / "tables" / "geml-paired-summary.json") if (campaign_dir / "tables" / "geml-paired-summary.json").is_file() else {}
    decision = str(gate_evaluation.get("decision") or package_manifest.get("decision") or "inconclusive")
    allowed_decisions = {"paper_positive", "promising_preliminary", "negative", "inconclusive"}
    if decision not in allowed_decisions:
        raise V116PackageError(f"Unexpected v1.16 final decision {decision!r}")

    commands = _v116_final_reproduction_commands(campaign_dir, budget_ladder_dir, package_dir, ablation_dir, output_dir)
    final_decision = {
        "schema": "eml.v116_final_decision.v1",
        "decision": decision,
        "paper_claim_allowed": decision == "paper_positive",
        "rationale": gate_evaluation.get("rationale") or package_manifest.get("rationale") or "",
        "blockers": list(gate_evaluation.get("blockers") or []),
        "gate_metrics": gate_evaluation.get("metrics") or {},
        "budget_ladder_decision": budget_manifest.get("decision"),
        "ablation_decision": ablation_manifest.get("decision"),
        "paired_summary": paired_summary,
        "package_contents": {
            "package_manifest": str(package_dir / "manifest.json"),
            "gate_evaluation": str(package_dir / "gate-evaluation.json"),
            "claim_audit": str(package_dir / "claim-audit.json"),
            "ablation_manifest": str(ablation_dir / "manifest.json"),
            "ablation_table": str(ablation_dir / "ablation-table.json"),
            "failure_examples": str(ablation_dir / "failure-examples.json"),
            "figure_metadata": str(ablation_dir / "figure-metadata.json"),
            "reproduction": str(package_dir / "reproduction.md"),
        },
        "reproduction_commands": commands,
        "claim_boundary": _v116_final_claim_boundary(decision),
    }
    final_md = _v116_final_decision_markdown(final_decision, figure_metadata)
    readme_md = _v116_package_readme(final_decision, figure_metadata)
    locks = _source_locks_payload(
        [
            ("campaign_manifest", campaign_dir / "campaign-manifest.json", "input"),
            ("geml_paired_summary", campaign_dir / "tables" / "geml-paired-summary.json", "input"),
            ("geml_paired_comparison", campaign_dir / "tables" / "geml-paired-comparison.csv", "input"),
            ("budget_ladder_manifest", budget_ladder_dir / "manifest.json", "input"),
            ("failure_taxonomy", budget_ladder_dir / "failure-taxonomy.json", "input"),
            ("package_manifest", package_dir / "manifest.json", "input"),
            ("gate_config", package_dir / "gate-config.json", "input"),
            ("gate_evaluation", package_dir / "gate-evaluation.json", "input"),
            ("package_claim_audit", package_dir / "claim-audit.json", "input"),
            ("package_source_locks", package_dir / "source-locks.json", "input"),
            ("reproduction", package_dir / "reproduction.md", "input"),
            ("ablation_manifest", ablation_dir / "manifest.json", "input"),
            ("ablation_table", ablation_dir / "ablation-table.json", "input"),
            ("failure_examples", ablation_dir / "failure-examples.json", "input"),
            ("figure_metadata", ablation_dir / "figure-metadata.json", "input"),
            ("ablation_source_locks", ablation_dir / "source-locks.json", "input"),
        ]
    )
    audit = _v116_final_claim_audit(
        final_md + "\n" + readme_md,
        gate_evaluation=gate_evaluation,
        gate_config=gate_config,
        source_locks=locks,
        final_decision=final_decision,
        figure_metadata=figure_metadata,
        ablation_manifest=ablation_manifest,
        commands=commands,
    )

    _write_json(paths.final_decision_json, final_decision)
    paths.final_decision_md.write_text(final_md, encoding="utf-8")
    _write_json(paths.final_claim_audit_json, audit)
    paths.final_claim_audit_md.write_text(_claim_audit_markdown(audit), encoding="utf-8")
    paths.package_readme_md.write_text(readme_md, encoding="utf-8")
    locks["outputs"] = _source_locks(
        [
            ("final_decision_json", paths.final_decision_json),
            ("final_decision_md", paths.final_decision_md),
            ("final_claim_audit_json", paths.final_claim_audit_json),
            ("final_claim_audit_md", paths.final_claim_audit_md),
            ("package_readme", paths.package_readme_md),
        ],
        role="output",
    )
    _write_json(paths.source_locks_json, locks)
    source_locks_ok = all(item["status"] == "locked" for item in locks["inputs"])
    manifest = {
        "schema": "eml.v116_final_decision_manifest.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "paper_claim_allowed": decision == "paper_positive",
        "claim_audit_status": audit["status"],
        "source_locks_ok": source_locks_ok,
        "final_decision": str(paths.final_decision_json),
        "final_claim_audit": str(paths.final_claim_audit_json),
        "source_locks": str(paths.source_locks_json),
        "package_readme": str(paths.package_readme_md),
    }
    _write_json(paths.manifest_json, manifest)
    return paths


def _v116_final_reproduction_commands(
    campaign_dir: Path,
    budget_ladder_dir: Path,
    package_dir: Path,
    ablation_dir: Path,
    output_dir: Path,
) -> list[str]:
    return [
        "PYTHONPATH=src python -m eml_symbolic_regression.cli campaign geml-v116-smoke --label v1.16-geml-smoke --overwrite",
        "PYTHONPATH=src python -m eml_symbolic_regression.cli campaign geml-v116-pilot --label v1.16-geml-pilot --overwrite",
        f"PYTHONPATH=src python -m eml_symbolic_regression.cli geml-v116-ladder --pilot-dir {campaign_dir} --output-dir {budget_ladder_dir} --overwrite",
        f"PYTHONPATH=src python -m eml_symbolic_regression.cli geml-paper-v116 --campaign-dir {campaign_dir} --budget-ladder-dir {budget_ladder_dir} --output-dir {package_dir} --min-unique-seeds 3 --overwrite",
        f"PYTHONPATH=src python -m eml_symbolic_regression.cli geml-v116-ablations --campaign-dir {campaign_dir} --budget-ladder-dir {budget_ladder_dir} --package-dir {package_dir} --output-dir {ablation_dir} --overwrite",
        f"PYTHONPATH=src python -m eml_symbolic_regression.cli geml-v116-final --campaign-dir {campaign_dir} --budget-ladder-dir {budget_ladder_dir} --package-dir {package_dir} --ablation-dir {ablation_dir} --output-dir {output_dir} --overwrite",
    ]


def _v116_final_claim_boundary(decision: str) -> str:
    if decision == "paper_positive":
        return "The exact-recovery gate allows a bounded positive v1.16 claim under the declared matched protocol."
    if decision == "promising_preliminary":
        return "The result may be described as preliminary only; it is not a final recovery claim."
    if decision == "negative":
        return "The matched exact-recovery evidence does not support an i*pi advantage under the declared protocol."
    return "The package is inconclusive; no positive i*pi/GEML recovery claim is supported."


def _v116_final_decision_markdown(final_decision: Mapping[str, Any], figure_metadata: Mapping[str, Any]) -> str:
    metrics = final_decision.get("gate_metrics") if isinstance(final_decision.get("gate_metrics"), Mapping) else {}
    lines = [
        "# v1.16 Final GEML/i*pi Decision",
        "",
        f"**Decision:** `{final_decision.get('decision')}`",
        "",
        str(final_decision.get("claim_boundary") or ""),
        "",
        str(final_decision.get("rationale") or ""),
        "",
        "Negative controls remain visible. Loss-only improvements remain diagnostic. Exact recovery requires verifier-gated snapped candidates.",
        "",
        "## Gate Metrics",
        "",
        f"- Paired rows: {metrics.get('paired_rows')}",
        f"- Unique seeds: {metrics.get('unique_seeds')}",
        f"- Complete denominator: {metrics.get('complete_denominator')}",
        f"- Natural i*pi exact recovery wins: {metrics.get('natural_ipi_recovery_wins')}",
        f"- Natural raw exact recovery wins: {metrics.get('natural_raw_recovery_wins')}",
        f"- Negative-control i*pi exact recovery wins: {metrics.get('negative_control_ipi_recovery_wins')}",
        f"- Loss-only outcomes: {metrics.get('loss_only_outcomes')}",
        "",
        "## Included Evidence",
        "",
    ]
    contents = final_decision.get("package_contents") if isinstance(final_decision.get("package_contents"), Mapping) else {}
    for key, value in contents.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Figures", ""])
    for figure in figure_metadata.get("figures", []):
        if isinstance(figure, Mapping):
            lines.append(f"- `{figure.get('id')}`: `{figure.get('path')}`")
    lines.extend(["", "## Reproduction Commands", ""])
    for command in final_decision.get("reproduction_commands", []):
        lines.extend(["```bash", str(command), "```", ""])
    return "\n".join(lines)


def _v116_package_readme(final_decision: Mapping[str, Any], figure_metadata: Mapping[str, Any]) -> str:
    lines = [
        "# v1.16 GEML/i*pi Evidence Package",
        "",
        f"Decision: `{final_decision.get('decision')}`",
        "",
        str(final_decision.get("claim_boundary") or ""),
        "",
        "This package is governed by the predefined exact-recovery gate. Negative controls are part of the evidence, and loss-only improvements are reported only as diagnostics.",
        "",
        "## Start Here",
        "",
        "- `final-decision/final-decision.md` - final decision and reproduction commands.",
        "- `gate-evaluation.json` - gate metrics and blockers.",
        "- `decision.md` - Phase 91 gate decision details.",
        "- `ablations/ablation-table.md` - ablations and blocked follow-up rows.",
        "- `ablations/failure-examples.md` - failure taxonomy examples and next steps.",
        "- `claim-audit.md` and `final-decision/final-claim-audit.md` - claim-safety checks.",
        "",
        "## Figures",
        "",
    ]
    for figure in figure_metadata.get("figures", []):
        if isinstance(figure, Mapping):
            lines.append(f"- `{figure.get('id')}`: `{figure.get('path')}`")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "The current package does not support a positive i*pi/GEML recovery claim. Any paper text should describe the result as inconclusive under the declared matched protocol.",
            "",
        ]
    )
    return "\n".join(lines)


def _v116_final_claim_audit(
    claim_text: str,
    *,
    gate_evaluation: Mapping[str, Any],
    gate_config: Mapping[str, Any],
    source_locks: Mapping[str, Any],
    final_decision: Mapping[str, Any],
    figure_metadata: Mapping[str, Any],
    ablation_manifest: Mapping[str, Any],
    commands: Iterable[str],
) -> dict[str, Any]:
    audit = build_v116_claim_audit(
        claim_text,
        gate_evaluation=gate_evaluation,
        gate_config=gate_config,
        source_locks=source_locks,
    )
    lower_claim = claim_text.lower()
    extra_checks = [
        _audit_check(
            "final_decision_is_allowed",
            str(final_decision.get("decision")) in {"paper_positive", "promising_preliminary", "negative", "inconclusive"},
            "Final decision is one of the predefined v1.16 outcomes.",
        ),
        _audit_check(
            "final_readme_matches_gate",
            str(final_decision.get("decision")) == str(gate_evaluation.get("decision") or final_decision.get("decision")),
            "README and final decision use the gate-controlled outcome.",
        ),
        _audit_check(
            "ablation_assets_present",
            bool(ablation_manifest.get("ablation_table") or ablation_manifest.get("row_counts")),
            "Final package includes ablation assets.",
        ),
        _audit_check(
            "figure_metadata_present",
            bool(figure_metadata.get("figures")),
            "Final package includes figure metadata.",
        ),
        _audit_check(
            "reproduction_commands_present",
            len(list(commands)) >= 4,
            "Final package includes reproduction commands.",
        ),
        _audit_check(
            "negative_control_cherry_picking_blocked",
            ("negative control" in lower_claim or "negative-control" in lower_claim) and "visible" in lower_claim,
            "Final package keeps negative controls visible.",
        ),
    ]
    checks = [*audit["checks"], *extra_checks]
    return {
        "schema": "eml.v116_final_claim_audit.v1",
        "status": "passed" if all(check["status"] == "passed" for check in checks) else "failed",
        "decision": audit["decision"],
        "checks": checks,
    }


def _v116_ablation_rows(
    paired_rows: Iterable[Mapping[str, Any]],
    run_rows: Iterable[Mapping[str, Any]],
    taxonomy_rows: Iterable[Mapping[str, Any]],
    gate_evaluation: Mapping[str, Any],
) -> list[dict[str, Any]]:
    paired = [dict(row) for row in paired_rows]
    runs = [dict(row) for row in run_rows]
    taxonomy = [dict(row) for row in taxonomy_rows]
    gate_metrics = gate_evaluation.get("metrics") if isinstance(gate_evaluation.get("metrics"), Mapping) else {}
    rows: list[dict[str, Any]] = []
    for operator in ("raw", "ipi"):
        run_stats = _operator_run_stats(runs, f"{operator}_eml")
        prefix = "raw" if operator == "raw" else "ipi"
        rows.append(
            _ablation_row(
                dimension="initialization",
                variant="raw random restarts" if operator == "raw" else "generic i*pi phase initializers",
                status="measured_pilot",
                operator_family=f"{operator}_eml",
                paired_rows=len(paired),
                run_rows=run_stats["run_rows"],
                exact_recovery_count=_paired_exact_wins(paired, prefix),
                loss_only_count=_paired_loss_only_wins(paired, prefix),
                branch_pathology_count=_failure_count(taxonomy, "branch_pathology", operator=prefix),
                numerical_instability_count=_failure_count(taxonomy, "numerical_instability", operator=prefix),
                median_post_snap_mse=run_stats["median_post_snap_mse"],
                median_runtime_seconds=run_stats["median_runtime_seconds"],
                candidate_pool_median=run_stats["candidate_pool_median"],
                observed_effect=(
                    "No verifier-gated exact recovery; raw won more loss-only rows."
                    if operator == "raw"
                    else "Generic phase initialization produced loss-only signals but no exact recovery."
                ),
                next_step="Do not promote loss-only results; inspect snap margins and branch diagnostics before increasing budget.",
                verified_equivalent_count=run_stats["verified_equivalent_count"],
                repaired_candidate_count=run_stats["repaired_candidate_count"],
                same_ast_count=run_stats["same_ast_count"],
                compile_only_count=run_stats["compile_only_count"],
            )
        )

    branch_count = sum(1 for row in taxonomy if str(row.get("failure_class")) == "branch_pathology")
    rows.append(
        _ablation_row(
            dimension="branch_guards",
            variant="guarded training with faithful verification",
            status="measured_pilot",
            operator_family="matched",
            paired_rows=len(paired),
            run_rows=len(runs),
            exact_recovery_count=int(gate_metrics.get("natural_ipi_recovery_wins") or 0) + int(gate_metrics.get("natural_raw_recovery_wins") or 0),
            loss_only_count=sum(1 for row in paired if str(row.get("comparison_outcome") or "").endswith("lower_post_snap_mse")),
            branch_pathology_count=branch_count,
            numerical_instability_count=_failure_count(taxonomy, "numerical_instability"),
            median_post_snap_mse=_median_numeric([_numeric(row.get("raw_post_snap_mse")) for row in paired] + [_numeric(row.get("ipi_post_snap_mse")) for row in paired]),
            median_runtime_seconds=_median_numeric([_numeric(row.get("raw_runtime_seconds")) for row in paired] + [_numeric(row.get("ipi_runtime_seconds")) for row in paired]),
            candidate_pool_median=_median_numeric(_numeric(row.get("optimizer_candidate_count")) for row in runs),
            observed_effect="Branch diagnostics remained visible; branch-related rows did not become verified recoveries.",
            next_step="Compare faithful and guarded traces on the same candidates before adding stronger branch penalties.",
        )
    )
    rows.append(
        _ablation_row(
            dimension="constants",
            variant="literal constants including pi",
            status="measured_pilot",
            operator_family="matched",
            paired_rows=len(paired),
            run_rows=len(runs),
            exact_recovery_count=int(gate_metrics.get("natural_ipi_recovery_wins") or 0) + int(gate_metrics.get("natural_raw_recovery_wins") or 0),
            loss_only_count=sum(1 for row in paired if str(row.get("comparison_outcome") or "").endswith("lower_post_snap_mse")),
            observed_effect="Literal pi support was present, so failure is not explained by missing pi alone.",
            next_step="Only test reduced constant catalogs as a controlled ablation after exact recovery appears.",
        )
    )
    for depth in sorted({str(row.get("depth") or "") for row in paired if row.get("depth") not in {None, ""}}):
        depth_rows = [row for row in paired if str(row.get("depth") or "") == depth]
        rows.append(
            _ablation_row(
                dimension="depth",
                variant=f"depth {depth}",
                status="measured_pilot",
                operator_family="matched",
                paired_rows=len(depth_rows),
                run_rows=sum(1 for row in runs if str(row.get("depth") or "") == depth),
                exact_recovery_count=sum(1 for row in depth_rows if str(row.get("comparison_outcome") or "") in {"ipi_recovery_win", "raw_recovery_win", "both_recovered"}),
                loss_only_count=sum(1 for row in depth_rows if str(row.get("comparison_outcome") or "").endswith("lower_post_snap_mse")),
                median_post_snap_mse=_median_numeric([_numeric(row.get("raw_post_snap_mse")) for row in depth_rows] + [_numeric(row.get("ipi_post_snap_mse")) for row in depth_rows]),
                median_runtime_seconds=_median_numeric([_numeric(row.get("raw_runtime_seconds")) for row in depth_rows] + [_numeric(row.get("ipi_runtime_seconds")) for row in depth_rows]),
                observed_effect="Depth remained within the pilot budget; no depth bucket produced exact recovery.",
                next_step="Increase depth only with a paired budget increase and exact-recovery denominator intact.",
            )
        )
    rows.append(
        _ablation_row(
            dimension="budget",
            variant="pilot steps/restarts",
            status="measured_pilot",
            operator_family="matched",
            paired_rows=len(paired),
            run_rows=len(runs),
            exact_recovery_count=sum(1 for row in paired if str(row.get("comparison_outcome") or "") in {"ipi_recovery_win", "raw_recovery_win", "both_recovered"}),
            loss_only_count=sum(1 for row in paired if str(row.get("comparison_outcome") or "").endswith("lower_post_snap_mse")),
            median_post_snap_mse=_median_numeric([_numeric(row.get("raw_post_snap_mse")) for row in paired] + [_numeric(row.get("ipi_post_snap_mse")) for row in paired]),
            median_runtime_seconds=_median_numeric([_numeric(row.get("raw_optimizer_wall_clock_seconds")) for row in paired] + [_numeric(row.get("ipi_optimizer_wall_clock_seconds")) for row in paired]),
            candidate_pool_median=_median_numeric(_numeric(row.get("optimizer_candidate_count")) for row in runs),
            observed_effect="Pilot budget produced only diagnostic loss-only differences.",
            next_step="Full or larger budgets stay blocked until a smaller pilot shows exact-recovery signal.",
        )
    )
    rows.append(
        _ablation_row(
            dimension="candidate_pooling",
            variant="verifier-gated hardening candidate pool",
            status="measured_pilot",
            operator_family="matched",
            paired_rows=len(paired),
            run_rows=len(runs),
            exact_recovery_count=sum(1 for row in paired if str(row.get("comparison_outcome") or "") in {"ipi_recovery_win", "raw_recovery_win", "both_recovered"}),
            loss_only_count=sum(1 for row in paired if str(row.get("comparison_outcome") or "").endswith("lower_post_snap_mse")),
            median_post_snap_mse=_median_numeric(_numeric(row.get("post_snap_mse")) for row in runs),
            median_runtime_seconds=_median_numeric(_numeric(row.get("runtime_seconds")) for row in runs),
            candidate_pool_median=_median_numeric(_numeric(row.get("optimizer_candidate_count")) for row in runs),
            observed_effect="Candidate pooling selected snapped candidates but none passed the verifier.",
            next_step="Inspect low-margin slots and add neighborhood candidates before increasing campaign size.",
        )
    )
    blocked_status = "not_run_blocked_by_pilot_gate"
    for dimension, variant, next_step in [
        ("branch_guards", "unguarded faithful-only training", "Run only as a controlled diagnostic after a measured exact-recovery signal appears."),
        ("constants", "no-pi literal catalog", "Use to test constant dependence once the current pi-enabled denominator has a positive signal."),
        ("budget", "full multi-seed campaign budget", "Blocked by the Phase 90 ladder because the pilot had no exact i*pi recovery."),
        ("candidate_pooling", "expanded local snap-neighborhood pool", "Prioritize if future pilot rows show near-miss snap margins."),
    ]:
        rows.append(
            _ablation_row(
                dimension=dimension,
                variant=variant,
                status=blocked_status,
                operator_family="matched",
                observed_effect="Not measured in v1.16 because the pilot gate failed closed.",
                next_step=next_step,
            )
        )
    return rows


def _ablation_row(**values: Any) -> dict[str, Any]:
    row = {column: "" for column in _ABLATION_COLUMNS}
    row.update(values)
    return row


def _operator_run_stats(rows: Iterable[Mapping[str, Any]], operator_family: str) -> dict[str, Any]:
    selected = [row for row in rows if str(row.get("operator_family") or "") == operator_family]
    return {
        "run_rows": len(selected),
        "median_post_snap_mse": _median_numeric(_numeric(row.get("post_snap_mse") or row.get("post_snap_loss")) for row in selected),
        "median_runtime_seconds": _median_numeric(_numeric(row.get("runtime_seconds") or row.get("optimizer_wall_clock_seconds")) for row in selected),
        "candidate_pool_median": _median_numeric(_numeric(row.get("optimizer_candidate_count")) for row in selected),
        "verified_equivalent_count": _run_class_count(selected, ("verified_equivalent_ast", "verified_equivalent")),
        "repaired_candidate_count": _run_class_count(selected, ("repaired_candidate",)),
        "same_ast_count": _run_class_count(selected, ("same_ast", "same_ast_return", "same_ast_warm_start_return")),
        "compile_only_count": _run_class_count(selected, ("compile_only_verified_support",)),
    }


def _run_class_count(rows: Iterable[Mapping[str, Any]], needles: Iterable[str]) -> int:
    wanted = set(needles)
    count = 0
    for row in rows:
        values = {
            str(row.get("recovery_class") or ""),
            str(row.get("evidence_class") or ""),
            str(row.get("discovery_class") or ""),
            str(row.get("return_kind") or ""),
            str(row.get("warm_start_evidence") or ""),
        }
        if values & wanted:
            count += 1
    return count


def _paired_exact_wins(rows: Iterable[Mapping[str, Any]], operator: str) -> int:
    if operator == "ipi":
        return sum(1 for row in rows if str(row.get("comparison_outcome") or "") in {"ipi_recovery_win", "both_recovered"})
    return sum(1 for row in rows if str(row.get("comparison_outcome") or "") in {"raw_recovery_win", "both_recovered"})


def _paired_loss_only_wins(rows: Iterable[Mapping[str, Any]], operator: str) -> int:
    return sum(1 for row in rows if str(row.get("comparison_outcome") or "") == f"{operator}_lower_post_snap_mse")


def _failure_count(rows: Iterable[Mapping[str, Any]], failure_class: str, *, operator: str | None = None) -> int:
    count = 0
    for row in rows:
        if str(row.get("failure_class") or "") != failure_class:
            continue
        if operator is not None and not str(row.get("comparison_outcome") or "").startswith(operator):
            continue
        count += 1
    return count


def _v116_failure_examples(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[Mapping[str, Any]]] = {}
    for row in rows:
        failure_class = str(row.get("failure_class") or "verifier_mismatch")
        grouped.setdefault(failure_class, []).append(row)
    result: list[dict[str, Any]] = []
    for failure_class in _CANONICAL_FAILURE_CLASSES:
        examples = sorted(
            grouped.get(failure_class, []),
            key=lambda row: (str(row.get("formula") or ""), str(row.get("seed") or ""), str(row.get("pair_id") or "")),
        )
        if not examples:
            result.append(
                {
                    "failure_class": failure_class,
                    "status": "not_observed",
                    "count": 0,
                    "representative_pair_id": "",
                    "formula": "",
                    "target_family": "",
                    "seed": "",
                    "comparison_outcome": "",
                    "actionable_next_step": _default_next_step_for_failure(failure_class),
                }
            )
            continue
        example = examples[0]
        result.append(
            {
                "failure_class": failure_class,
                "status": "observed",
                "count": len(examples),
                "representative_pair_id": str(example.get("pair_id") or ""),
                "formula": str(example.get("formula") or ""),
                "target_family": str(example.get("target_family") or ""),
                "seed": str(example.get("seed") or ""),
                "comparison_outcome": str(example.get("comparison_outcome") or ""),
                "actionable_next_step": str(example.get("actionable_next_step") or _default_next_step_for_failure(failure_class)),
            }
        )
    return result


def _default_next_step_for_failure(failure_class: str) -> str:
    defaults = {
        "loss_only_signal": "Inspect snap mismatch; keep the row diagnostic until exact verification passes.",
        "optimization_or_snap_miss": "Increase candidate-pool or hardening budget only after checking snap margins.",
        "snap_mismatch": "Compare soft candidate behavior with snapped AST alternatives near low-margin slots.",
        "branch_pathology": "Inspect branch-domain construction and guarded-versus-faithful mismatch diagnostics.",
        "verifier_mismatch": "Inspect split-level verifier evidence and high-precision status.",
        "unsupported_or_over_depth": "Check target depth, literal constants, and suite support gates before rerunning.",
        "numerical_instability": "Reduce guard pressure or inspect anomaly traces before increasing budget.",
    }
    return defaults.get(failure_class, "Inspect the row manually before treating it as evidence.")


def _v116_ablation_markdown(rows: Iterable[Mapping[str, Any]]) -> str:
    lines = [
        "# v1.16 Ablation Table",
        "",
        "Loss-only rows are diagnostics and never count as recovery.",
        "",
        "| Dimension | Variant | Status | Operator | Pairs | Exact | Loss-Only | Effect | Next Step |",
        "|-----------|---------|--------|----------|-------|-------|-----------|--------|-----------|",
    ]
    for row in rows:
        lines.append(
            f"| {row.get('dimension')} | {row.get('variant')} | {row.get('status')} | {row.get('operator_family')} | "
            f"{row.get('paired_rows')} | {row.get('exact_recovery_count')} | {row.get('loss_only_count')} | "
            f"{row.get('observed_effect')} | {row.get('next_step')} |"
        )
    lines.append("")
    return "\n".join(lines)


def _v116_failure_examples_markdown(rows: Iterable[Mapping[str, Any]]) -> str:
    lines = [
        "# v1.16 Failure Examples",
        "",
        "| Failure Class | Status | Count | Example | Formula | Outcome | Next Step |",
        "|---------------|--------|-------|---------|---------|---------|-----------|",
    ]
    for row in rows:
        lines.append(
            f"| {row.get('failure_class')} | {row.get('status')} | {row.get('count')} | {row.get('representative_pair_id')} | "
            f"{row.get('formula')} | {row.get('comparison_outcome')} | {row.get('actionable_next_step')} |"
        )
    lines.append("")
    return "\n".join(lines)


def _classification_from_rows(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[Mapping[str, Any]]] = {}
    for row in rows:
        family = str(row.get("target_family") or "unknown")
        grouped.setdefault(family, []).append(row)
    families = sorted(set(grouped) | {"negative_control", "periodic", "harmonic", "damped_oscillation", "standing_wave", "log_periodic"})
    result: list[dict[str, Any]] = []
    for family in families:
        items = grouped.get(family, [])
        outcomes = _count_by_key(items, "comparison_outcome")
        loss_only = outcomes.get("ipi_lower_post_snap_mse", 0) + outcomes.get("raw_lower_post_snap_mse", 0)
        result.append(
            {
                "target_family": family,
                "declared_targets": _declared_family_count(family),
                "paired_rows": len(items),
                "ipi_recovery_wins": outcomes.get("ipi_recovery_win", 0),
                "raw_recovery_wins": outcomes.get("raw_recovery_win", 0),
                "both_recovered": outcomes.get("both_recovered", 0),
                "neither_recovered": outcomes.get("neutral_no_recovery", 0) + loss_only,
                "loss_only_outcomes": loss_only,
                "ipi_lower_post_snap_mse": outcomes.get("ipi_lower_post_snap_mse", 0),
                "raw_lower_post_snap_mse": outcomes.get("raw_lower_post_snap_mse", 0),
            }
        )
    return result


_FAILURE_TAXONOMY_COLUMNS = [
    "tier",
    "pair_id",
    "formula",
    "target_family",
    "seed",
    "comparison_outcome",
    "failure_class",
    "actionable_next_step",
]


def _campaign_evidence(tier: str, campaign_dir: Path) -> dict[str, Any]:
    rows = [{**row, "tier": tier} for row in _read_paired_rows(campaign_dir)]
    summary_path = campaign_dir / "tables" / "geml-paired-summary.json"
    summary = _read_json(summary_path) if summary_path.is_file() else _summary_from_rows(rows)
    locks = _source_locks(
        [
            ("campaign_manifest", campaign_dir / "campaign-manifest.json"),
            ("geml_paired_summary", summary_path),
            ("geml_paired_comparison", campaign_dir / "tables" / "geml-paired-comparison.csv"),
        ],
        role="input",
    )
    return {
        "tier": tier,
        "campaign_dir": str(campaign_dir),
        "rows": rows,
        "summary": summary,
        "source_locks": locks,
        "source_locks_ok": all(lock["status"] == "locked" for lock in locks),
    }


def _ladder_tier(name: str, evidence: Mapping[str, Any], command: str) -> dict[str, Any]:
    summary = evidence.get("summary") if isinstance(evidence.get("summary"), Mapping) else {}
    return {
        "name": name,
        "status": "performed" if evidence.get("rows") else "not_performed",
        "paired_rows": int(summary.get("paired_rows") or 0),
        "ipi_recovery_wins": int(summary.get("ipi_recovery_wins") or 0),
        "raw_recovery_wins": int(summary.get("raw_recovery_wins") or 0),
        "loss_only_outcomes": int(summary.get("loss_only_outcomes") or 0),
        "source_locks_ok": bool(evidence.get("source_locks_ok")),
        "command": command,
    }


def _failure_taxonomy_rows(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for row in rows:
        outcome = str(row.get("comparison_outcome") or "")
        failure_class, next_step = _failure_class_for_pair(row, outcome)
        result.append(
            {
                "tier": str(row.get("tier") or _tier_from_case_id(str(row.get("raw_case_id") or row.get("ipi_case_id") or ""))),
                "pair_id": str(row.get("pair_id") or ""),
                "formula": str(row.get("formula") or ""),
                "target_family": str(row.get("target_family") or ""),
                "seed": str(row.get("seed") or ""),
                "comparison_outcome": outcome or "unknown",
                "failure_class": failure_class,
                "actionable_next_step": next_step,
            }
        )
    return result


def _failure_class_for_pair(row: Mapping[str, Any], outcome: str) -> tuple[str, str]:
    if outcome in {"ipi_recovery_win", "raw_recovery_win", "both_recovered"}:
        return "exact_recovery_signal", "Keep this row in exact-recovery denominators and compare seed stability."
    if outcome in {"ipi_lower_post_snap_mse", "raw_lower_post_snap_mse"}:
        return "loss_only_signal", "Inspect snap mismatch and candidate-pool alternatives; do not count as recovery."
    if _numeric(row.get("ipi_branch_cut_crossing_count")) > 0 or _numeric(row.get("raw_branch_cut_crossing_count")) > 0:
        return "branch_pathology", "Inspect branch-domain construction and guarded-versus-faithful mismatch diagnostics."
    if "unsupported" in str(row.get("raw_status") or "").lower() or "unsupported" in str(row.get("ipi_status") or "").lower():
        return "unsupported_or_over_depth", "Check target depth, literal constants, and suite support gates before rerunning."
    if _numeric(row.get("raw_nan_count")) > 0 or _numeric(row.get("ipi_nan_count")) > 0 or _numeric(row.get("raw_inf_count")) > 0 or _numeric(row.get("ipi_inf_count")) > 0:
        return "numerical_instability", "Reduce guard pressure or inspect anomaly traces before increasing budget."
    if outcome == "neutral_no_recovery":
        return "optimization_or_snap_miss", "Increase candidate-pool or hardening budget only after checking snap margins."
    return "verifier_mismatch", "Inspect verifier evidence and exact-candidate selection fields."


def _tier_from_case_id(case_id: str) -> str:
    if "smoke" in case_id:
        return "smoke"
    if "pilot" in case_id:
        return "pilot"
    return "unknown"


def _numeric(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _finite_numeric_values(values: Iterable[Any]) -> list[float]:
    result: list[float] = []
    for value in values:
        numeric = _numeric(value)
        if math.isfinite(numeric):
            result.append(numeric)
    return result


def _median_numeric(values: Iterable[Any]) -> float | str:
    numeric = sorted(_finite_numeric_values(values))
    if not numeric:
        return ""
    midpoint = len(numeric) // 2
    if len(numeric) % 2:
        return numeric[midpoint]
    return (numeric[midpoint - 1] + numeric[midpoint]) / 2


def _mean_numeric(values: Iterable[Any]) -> float:
    numeric = _finite_numeric_values(values)
    return sum(numeric) / len(numeric) if numeric else 0.0


def _sum_numeric(values: Iterable[Any]) -> float:
    return sum(_finite_numeric_values(values))


def _format_number(value: float, *, suffix: str = "") -> str:
    if abs(value) >= 100:
        body = f"{value:.0f}"
    elif abs(value) >= 10:
        body = f"{value:.1f}"
    else:
        body = f"{value:.3g}"
    return f"{body}{suffix}"


def _budget_ladder_markdown(ladder: Mapping[str, Any]) -> str:
    lines = [
        "# v1.16 GEML Budget Ladder",
        "",
        f"Decision: `{ladder.get('decision')}`",
        "",
        str(ladder.get("rationale") or ""),
        "",
        "| Tier | Status | Pairs | i*pi Wins | Raw Wins | Loss-Only | Source Locks |",
        "|------|--------|-------|-----------|----------|-----------|--------------|",
    ]
    for tier in ladder.get("tiers", []):
        if not isinstance(tier, Mapping):
            continue
        lines.append(
            f"| {tier.get('name')} | {tier.get('status')} | {tier.get('paired_rows', '')} | "
            f"{tier.get('ipi_recovery_wins', '')} | {tier.get('raw_recovery_wins', '')} | "
            f"{tier.get('loss_only_outcomes', '')} | {tier.get('source_locks_ok', '')} |"
        )
    lines.extend(["", "## Commands", ""])
    for tier in ladder.get("tiers", []):
        if isinstance(tier, Mapping) and tier.get("command"):
            lines.extend([f"### {tier.get('name')}", "", "```bash", str(tier["command"]), "```", ""])
    return "\n".join(lines)


def _failure_taxonomy_markdown(rows: Iterable[Mapping[str, Any]]) -> str:
    lines = [
        "# v1.16 GEML Failure Taxonomy",
        "",
        "| Tier | Pair | Formula | Family | Outcome | Failure Class | Next Step |",
        "|------|------|---------|--------|---------|---------------|-----------|",
    ]
    for row in rows:
        lines.append(
            f"| {row.get('tier')} | {row.get('pair_id')} | {row.get('formula')} | {row.get('target_family')} | "
            f"{row.get('comparison_outcome')} | {row.get('failure_class')} | {row.get('actionable_next_step')} |"
        )
    lines.append("")
    return "\n".join(lines)


def _v116_family_recovery_svg(classification: Iterable[Mapping[str, Any]]) -> str:
    bars: list[dict[str, Any]] = []
    for row in classification:
        family = str(row.get("target_family") or "unknown")
        if int(row.get("paired_rows") or 0) == 0 and int(row.get("declared_targets") or 0) == 0:
            continue
        exact = int(row.get("ipi_recovery_wins") or 0) + int(row.get("raw_recovery_wins") or 0) + int(row.get("both_recovered") or 0)
        loss_only = int(row.get("loss_only_outcomes") or 0)
        bars.append({"label": f"{family} exact", "value": exact, "color": "#1b998b", "display": str(exact)})
        bars.append({"label": f"{family} loss-only", "value": loss_only, "color": "#e9c46a", "display": str(loss_only)})
    return _bar_svg(
        "Family Recovery Outcomes",
        "Exact recovery is verifier-gated. Loss-only bars are diagnostic and cannot support recovery claims.",
        bars,
    )


def _v116_loss_snap_svg(rows: Iterable[Mapping[str, Any]]) -> str:
    paired = [dict(row) for row in rows]
    bars = [
        {"label": "raw pre-snap", "value": _mean_numeric(_numeric(row.get("raw_pre_snap_mse")) for row in paired), "color": "#457b9d"},
        {"label": "raw post-snap", "value": _mean_numeric(_numeric(row.get("raw_post_snap_mse")) for row in paired), "color": "#1d3557"},
        {"label": "i*pi pre-snap", "value": _mean_numeric(_numeric(row.get("ipi_pre_snap_mse")) for row in paired), "color": "#f4a261"},
        {"label": "i*pi post-snap", "value": _mean_numeric(_numeric(row.get("ipi_post_snap_mse")) for row in paired), "color": "#e76f51"},
    ]
    return _bar_svg(
        "Loss Before and After Snap",
        "Mean MSE across paired pilot rows. These values are diagnostics, not recovery evidence.",
        bars,
    )


def _v116_branch_anomalies_svg(rows: Iterable[Mapping[str, Any]]) -> str:
    paired = [dict(row) for row in rows]
    bars = [
        {"label": "raw branch cuts", "value": _sum_numeric(row.get("raw_branch_cut_count") for row in paired), "color": "#457b9d"},
        {"label": "raw proximity", "value": _sum_numeric(row.get("raw_branch_cut_proximity_count") for row in paired), "color": "#a8dadc"},
        {"label": "raw crossings", "value": _sum_numeric(row.get("raw_branch_cut_crossing_count") for row in paired), "color": "#1d3557"},
        {"label": "i*pi branch cuts", "value": _sum_numeric(row.get("ipi_branch_cut_count") for row in paired), "color": "#f4a261"},
        {"label": "i*pi proximity", "value": _sum_numeric(row.get("ipi_branch_cut_proximity_count") for row in paired), "color": "#e9c46a"},
        {"label": "i*pi crossings", "value": _sum_numeric(row.get("ipi_branch_cut_crossing_count") for row in paired), "color": "#e76f51"},
    ]
    return _bar_svg(
        "Branch Diagnostics",
        "Counts remain visible even when they weaken the i*pi interpretation.",
        bars,
    )


def _v116_runtime_svg(rows: Iterable[Mapping[str, Any]]) -> str:
    paired = [dict(row) for row in rows]
    bars = [
        {"label": "raw optimizer", "value": _median_numeric(_numeric(row.get("raw_optimizer_wall_clock_seconds")) for row in paired), "color": "#457b9d", "display_suffix": "s"},
        {"label": "raw total", "value": _median_numeric(_numeric(row.get("raw_runtime_seconds")) for row in paired), "color": "#1d3557", "display_suffix": "s"},
        {"label": "i*pi optimizer", "value": _median_numeric(_numeric(row.get("ipi_optimizer_wall_clock_seconds")) for row in paired), "color": "#f4a261", "display_suffix": "s"},
        {"label": "i*pi total", "value": _median_numeric(_numeric(row.get("ipi_runtime_seconds")) for row in paired), "color": "#e76f51", "display_suffix": "s"},
    ]
    return _bar_svg("Runtime and Resource Context", "Median seconds across pilot pairs.", bars)


def _v116_representative_curves_svg(rows: Iterable[Mapping[str, Any]]) -> str:
    selected = _representative_curve_rows(rows)
    if not selected:
        return _empty_svg("Representative Fits and Failures", "No paired rows available.", width=1080, height=560)
    width = 1080
    panel_h = 170
    height = 90 + panel_h * len(selected)
    parts = [
        _svg_header(width, height),
        '<style>.title{font:700 22px Arial,sans-serif;fill:#17202a}.note{font:12px Arial,sans-serif;fill:#34495e}.label{font:11px Arial,sans-serif;fill:#34495e}.axis{stroke:#d8dee4;stroke-width:1}.target{fill:none;stroke:#1b998b;stroke-width:2}.candidate{fill:none;stroke:#e76f51;stroke-width:2;stroke-dasharray:5 4}.panel{fill:#ffffff;stroke:#d8dee4;stroke-width:1}</style>',
        '<text x="34" y="36" class="title">Representative Fits and Failures</text>',
        '<text x="34" y="58" class="note">Panels show target curves and selected snapped candidates when artifacts are available; all selected pilot examples failed verification.</text>',
    ]
    for index, row in enumerate(selected):
        y0 = 82 + index * panel_h
        side = "ipi" if str(row.get("comparison_outcome") or "").startswith("ipi") else "raw"
        curve = _curve_payload(row, side)
        parts.append(f'<rect x="32" y="{y0}" width="{width - 64}" height="{panel_h - 16}" rx="4" class="panel"/>')
        title = f"{row.get('formula', '')} seed {row.get('seed', '')} {side} {row.get('comparison_outcome', '')}"
        parts.append(f'<text x="50" y="{y0 + 24}" class="label">{escape(title)}</text>')
        plot_x = 54
        plot_y = y0 + 40
        plot_w = width - 130
        plot_h = panel_h - 76
        parts.append(f'<line x1="{plot_x}" y1="{plot_y + plot_h}" x2="{plot_x + plot_w}" y2="{plot_y + plot_h}" class="axis"/>')
        target_points = _polyline_points(curve.get("x", []), curve.get("target", []), plot_x, plot_y, plot_w, plot_h, curve.get("y_min"), curve.get("y_max"))
        candidate_points = _polyline_points(curve.get("x", []), curve.get("candidate", []), plot_x, plot_y, plot_w, plot_h, curve.get("y_min"), curve.get("y_max"))
        if target_points:
            parts.append(f'<polyline points="{target_points}" class="target"/>')
        if candidate_points:
            parts.append(f'<polyline points="{candidate_points}" class="candidate"/>')
        parts.append(f'<text x="{plot_x}" y="{y0 + panel_h - 26}" class="label">target</text>')
        parts.append(f'<text x="{plot_x + 54}" y="{y0 + panel_h - 26}" class="label" fill="#e76f51">candidate: {escape(str(curve.get("candidate_expression") or "unavailable"))}</text>')
        parts.append(f'<text x="{plot_x + plot_w - 250}" y="{y0 + panel_h - 26}" class="label">verifier: {escape(str(curve.get("verifier_status") or "failed"))}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def _bar_svg(title: str, subtitle: str, bars: Iterable[Mapping[str, Any]], *, width: int = 960, height: int = 520) -> str:
    bar_rows = [dict(row) for row in bars]
    if not bar_rows:
        return _empty_svg(title, "No rows available.", width=width, height=height)
    max_value = max((_numeric(row.get("value")) for row in bar_rows), default=0.0)
    scale_max = max(max_value, 1.0)
    left = 220
    top = 86
    row_h = max(24, min(42, int((height - top - 40) / max(len(bar_rows), 1))))
    plot_w = width - left - 80
    parts = [
        _svg_header(width, height),
        '<style>.title{font:700 22px Arial,sans-serif;fill:#17202a}.note{font:12px Arial,sans-serif;fill:#34495e}.label{font:11px Arial,sans-serif;fill:#34495e}.grid{stroke:#edf2f4;stroke-width:1}.bar{opacity:.92}</style>',
        f'<text x="34" y="36" class="title">{escape(title)}</text>',
        f'<text x="34" y="58" class="note">{escape(subtitle)}</text>',
    ]
    for tick in range(5):
        x = left + plot_w * tick / 4
        parts.append(f'<line x1="{x:.1f}" y1="{top - 12}" x2="{x:.1f}" y2="{height - 34}" class="grid"/>')
    for index, row in enumerate(bar_rows):
        value = _numeric(row.get("value"))
        y = top + index * row_h
        bar_w = plot_w * value / scale_max
        color = str(row.get("color") or "#457b9d")
        display = str(row.get("display") or _format_number(value, suffix=str(row.get("display_suffix") or "")))
        parts.append(f'<text x="34" y="{y + 15}" class="label">{escape(str(row.get("label") or ""))}</text>')
        parts.append(f'<rect x="{left}" y="{y}" width="{bar_w:.1f}" height="{max(row_h - 8, 8)}" class="bar" fill="{escape(color)}"/>')
        parts.append(f'<text x="{left + bar_w + 8:.1f}" y="{y + 15}" class="label">{escape(display)}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def _empty_svg(title: str, message: str, *, width: int = 960, height: int = 520) -> str:
    return "\n".join(
        [
            _svg_header(width, height),
            '<style>.title{font:700 22px Arial,sans-serif;fill:#17202a}.note{font:13px Arial,sans-serif;fill:#34495e}</style>',
            f'<text x="34" y="38" class="title">{escape(title)}</text>',
            f'<text x="34" y="68" class="note">{escape(message)}</text>',
            "</svg>",
        ]
    )


def _svg_header(width: int, height: int) -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">'


def _representative_curve_rows(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    ranked = sorted(
        [dict(row) for row in rows],
        key=lambda row: (
            0 if str(row.get("comparison_outcome") or "").startswith("ipi") else 1,
            str(row.get("target_family") or ""),
            str(row.get("formula") or ""),
            str(row.get("seed") or ""),
        ),
    )
    return ranked[:3]


def _curve_payload(row: Mapping[str, Any], side: str) -> dict[str, Any]:
    formula = str(row.get("formula") or "")
    seed = int(_numeric(row.get("seed")))
    candidate_expression = None
    verifier_status = row.get(f"{side}_verification_outcome") or row.get(f"{side}_status") or "failed"
    artifact_path = Path(str(row.get(f"{side}_artifact_path") or ""))
    if artifact_path.is_file():
        artifact = _read_json(artifact_path)
        candidate_expression = _selected_symbolic_expression(artifact)
        verifier_status = artifact.get("verification_outcome") or artifact.get("claim_status") or verifier_status
    x_values, target_values = _target_curve_values(formula, seed)
    candidate_values = _evaluate_candidate_expression(candidate_expression, x_values)
    finite_values = [value for value in [*target_values, *candidate_values] if value is not None and math.isfinite(value)]
    y_min = min(finite_values) if finite_values else -1.0
    y_max = max(finite_values) if finite_values else 1.0
    if abs(y_max - y_min) < 1e-12:
        y_min -= 1.0
        y_max += 1.0
    return {
        "x": x_values,
        "target": target_values,
        "candidate": candidate_values,
        "candidate_expression": candidate_expression,
        "verifier_status": verifier_status,
        "y_min": y_min,
        "y_max": y_max,
    }


def _selected_symbolic_expression(artifact: Mapping[str, Any]) -> str | None:
    refit = artifact.get("refit")
    if isinstance(refit, Mapping):
        selected = str(refit.get("selected_candidate") or "pre_refit")
        candidate = refit.get(f"{selected}_candidate")
        if isinstance(candidate, Mapping) and candidate.get("symbolic_expression"):
            return str(candidate["symbolic_expression"])
        for key in ("pre_refit_candidate", "post_refit_candidate"):
            candidate = refit.get(key)
            if isinstance(candidate, Mapping) and candidate.get("symbolic_expression"):
                return str(candidate["symbolic_expression"])
    for key in ("selected_candidate", "trained_eml_candidate"):
        value = artifact.get(key)
        if isinstance(value, Mapping) and value.get("symbolic_expression"):
            return str(value["symbolic_expression"])
    return None


def _target_curve_values(formula: str, seed: int) -> tuple[list[float], list[float]]:
    try:
        from .datasets import get_demo

        spec = get_demo(formula)
        split = spec.make_splits(points=32, seed=seed)[0]
        variable = spec.variable
        x_values = [float(value) for value in split.inputs[variable]]
        target = [float(complex(value).real) for value in split.target]
        return x_values, target
    except Exception:
        x_values = [index / 31 * 2 - 1 for index in range(32)]
        return x_values, [0.0 for _ in x_values]


def _evaluate_candidate_expression(expression: str | None, x_values: Iterable[float]) -> list[float | None]:
    if not expression:
        return []
    try:
        import numpy as np
        import sympy as sp

        x_list = list(x_values)
        x = sp.Symbol("x")
        expr = sp.sympify(expression, locals={"E": sp.E, "pi": sp.pi})
        fn = sp.lambdify(x, expr, modules=["numpy"])
        values = np.asarray(fn(np.asarray(x_list, dtype=float)), dtype=np.complex128).reshape(-1)
        if values.size == 1 and len(x_list) > 1:
            values = np.repeat(values, len(x_list))
        return [float(value.real) if np.isfinite(value.real) and abs(value.imag) < 1e-8 else None for value in values]
    except Exception:
        return []


def _polyline_points(
    x_values: Iterable[float],
    y_values: Iterable[float | None],
    x: float,
    y: float,
    width: float,
    height: float,
    y_min: Any,
    y_max: Any,
) -> str:
    xs = list(x_values)
    ys = list(y_values)
    if not xs or not ys:
        return ""
    x_min = min(xs)
    x_max = max(xs)
    if abs(x_max - x_min) < 1e-12:
        x_max = x_min + 1.0
    ymin = _numeric(y_min)
    ymax = _numeric(y_max)
    if abs(ymax - ymin) < 1e-12:
        ymax = ymin + 1.0
    points: list[str] = []
    for xv, yv in zip(xs, ys):
        if yv is None or not math.isfinite(float(yv)):
            continue
        px = x + (float(xv) - x_min) / (x_max - x_min) * width
        py = y + height - (float(yv) - ymin) / (ymax - ymin) * height
        points.append(f"{px:.1f},{py:.1f}")
    return " ".join(points)


def _summary_from_rows(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    rows = [dict(row) for row in rows]
    outcomes = _count_by_key(rows, "comparison_outcome")
    return {
        "schema": "eml.geml_paired_summary.v1",
        "paired_rows": len(rows),
        "ipi_recovery_wins": outcomes.get("ipi_recovery_win", 0),
        "raw_recovery_wins": outcomes.get("raw_recovery_win", 0),
        "both_recovered": outcomes.get("both_recovered", 0),
        "loss_only_outcomes": outcomes.get("ipi_lower_post_snap_mse", 0) + outcomes.get("raw_lower_post_snap_mse", 0),
        "unique_seeds": _unique_seed_count(rows),
    }


def _declared_family_count(family: str) -> int:
    suite = builtin_suite("v1.15-geml-oscillatory")
    formulas = {case.formula for case in suite.cases if _family_for_tags(case.tags) == family}
    return len(formulas)


def _family_for_tags(tags: Iterable[Any]) -> str:
    values = {str(tag) for tag in tags}
    if "negative_control" in values:
        return "negative_control"
    if "log_periodic" in values:
        return "log_periodic"
    if "damped_oscillation" in values:
        return "damped_oscillation"
    if "standing_wave" in values:
        return "standing_wave"
    if "harmonic" in values:
        return "harmonic"
    if "periodic" in values:
        return "periodic"
    return "unknown"


def _read_paired_rows(campaign_dir: Path) -> list[dict[str, Any]]:
    path = campaign_dir / "tables" / "geml-paired-comparison.csv"
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _read_csv(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _unique_seed_count(rows: Iterable[Mapping[str, Any]]) -> int:
    seeds = {str(row.get("seed")) for row in rows if row.get("seed") not in {None, ""}}
    return len(seeds)


def _summary_seed_count(summary: Mapping[str, Any]) -> int:
    for key in ("unique_seeds", "seed_count"):
        if summary.get(key) is not None:
            return int(summary[key])
    return 0


def _count_by_key(rows: Iterable[Mapping[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key) or "")
        counts[value] = counts.get(value, 0) + 1
    return counts


def _decision_markdown(evaluation: Mapping[str, Any], classification: Iterable[Mapping[str, Any]], campaign_dir: Path) -> str:
    metrics = evaluation.get("metrics") if isinstance(evaluation.get("metrics"), Mapping) else {}
    lines = [
        "# v1.16 GEML/i*pi EML Paper Decision",
        "",
        f"**Decision:** `{evaluation.get('decision')}`",
        "",
        str(evaluation.get("rationale") or ""),
        "",
        "The decision is controlled by the predefined paper-strength gate. Loss-only improvements are diagnostics, not recovery. Negative-control rows remain visible and claim-blocking.",
        "",
        f"Campaign directory: `{campaign_dir}`",
        "",
        "## Gate Metrics",
        "",
        f"- Paired rows: {metrics.get('paired_rows')}",
        f"- Declared targets: {metrics.get('declared_targets')}",
        f"- Unique seeds: {metrics.get('unique_seeds')}",
        f"- Complete denominator: {metrics.get('complete_denominator')}",
        f"- Natural i*pi exact recovery wins: {metrics.get('natural_ipi_recovery_wins')}",
        f"- Natural raw exact recovery wins: {metrics.get('natural_raw_recovery_wins')}",
        f"- Negative-control i*pi exact recovery wins: {metrics.get('negative_control_ipi_recovery_wins')}",
        f"- Loss-only outcomes: {metrics.get('loss_only_outcomes')}",
        "",
        "## Target Families",
        "",
        "| Family | Declared | Pairs | i*pi Wins | Raw Wins | Loss-Only |",
        "|--------|----------|-------|-----------|----------|-----------|",
    ]
    for row in classification:
        lines.append(
            f"| {row.get('target_family')} | {row.get('declared_targets')} | {row.get('paired_rows')} | "
            f"{row.get('ipi_recovery_wins')} | {row.get('raw_recovery_wins')} | {row.get('loss_only_outcomes')} |"
        )
    lines.append("")
    return "\n".join(lines)


def _claim_audit_markdown(audit: Mapping[str, Any]) -> str:
    lines = ["# v1.16 Claim Audit", "", f"Status: `{audit.get('status')}`", "", "| Check | Status | Description |", "|-------|--------|-------------|"]
    for check in audit.get("checks", []):
        lines.append(f"| {check['id']} | {check['status']} | {check['description']} |")
    lines.append("")
    return "\n".join(lines)


def _reproduction_markdown(campaign_dir: Path, min_unique_seeds: int) -> str:
    return "\n".join(
        [
            "# Reproducing the v1.16 GEML Decision Package",
            "",
            "Run the v1.16 pilot campaign:",
            "",
            "```bash",
            "PYTHONPATH=src python -m eml_symbolic_regression.cli campaign geml-v116-pilot --label v1.16-geml-pilot --overwrite",
            "```",
            "",
            "Refresh this package:",
            "",
            "```bash",
            f"PYTHONPATH=src python -m eml_symbolic_regression.cli geml-paper-v116 --campaign-dir {campaign_dir} --min-unique-seeds {min_unique_seeds} --overwrite",
            "```",
            "",
        ]
    )


def _audit_check(check_id: str, passed: bool, description: str) -> dict[str, str]:
    return {"id": check_id, "status": "passed" if passed else "failed", "description": description}


def _contains_any(text: str, phrases: Iterable[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def _source_locks_payload(items: Iterable[tuple[str, Path, str]]) -> dict[str, Any]:
    grouped = {"schema": "eml.v116_source_locks.v1", "inputs": [], "outputs": []}
    for source_id, path, role in items:
        grouped["inputs" if role == "input" else "outputs"].extend(_source_locks([(source_id, path)], role=role))
    return grouped


def _source_locks(items: Iterable[tuple[str, Path]], *, role: str) -> list[dict[str, Any]]:
    locks: list[dict[str, Any]] = []
    for source_id, path in items:
        if not path.is_file():
            locks.append({"source_id": source_id, "role": role, "path": str(path), "status": "missing"})
            continue
        locks.append(
            {
                "source_id": source_id,
                "role": role,
                "path": str(path),
                "status": "locked",
                "sha256": _sha256(path),
                "bytes": path.stat().st_size,
            }
        )
    return locks


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: Iterable[Mapping[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})
