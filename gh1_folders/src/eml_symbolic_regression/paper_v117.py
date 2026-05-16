"""v1.17 snap-first exact-recovery diagnostics and package helpers."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import shlex
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from .expression import expr_from_document, parse_constant_value
from .master_tree import (
    ActiveSlotAlternatives,
    ReplayAssignment,
    SlotAlternative,
    SnapDecision,
    SnapResult,
    expand_snap_neighborhood,
)
from .semantics import eml_operator_from_spec, raw_eml_operator


DEFAULT_V117_PACKAGE_DIR = Path("artifacts") / "paper" / "v1.17-geml"
DEFAULT_V117_SNAP_DIAGNOSTICS_DIR = DEFAULT_V117_PACKAGE_DIR / "snap-diagnostics"
DEFAULT_V117_NEIGHBORHOOD_DIR = DEFAULT_V117_PACKAGE_DIR / "neighborhoods"
DEFAULT_V117_RANKING_DIR = DEFAULT_V117_PACKAGE_DIR / "ranking"
DEFAULT_V117_SANDBOX_DIR = DEFAULT_V117_PACKAGE_DIR / "sandbox"
DEFAULT_V116_CAMPAIGN_DIR = Path("artifacts") / "campaigns" / "v1.16-geml-pilot"
DEFAULT_V116_PACKAGE_DIR = Path("artifacts") / "paper" / "v1.16-geml"


class V117PackageError(RuntimeError):
    """Raised when a v1.17 package artifact cannot be safely written."""


@dataclass(frozen=True)
class V117SnapDiagnosticPaths:
    output_dir: Path
    manifest_json: Path
    snap_diagnostics_json: Path
    snap_diagnostics_csv: Path
    snap_diagnostics_md: Path
    snap_neighborhood_seeds_json: Path
    source_locks_json: Path

    def as_dict(self) -> dict[str, str]:
        return {key: str(value) for key, value in self.__dict__.items()}


@dataclass(frozen=True)
class V117NeighborhoodPaths:
    output_dir: Path
    manifest_json: Path
    neighborhood_candidates_json: Path
    neighborhood_candidates_csv: Path
    neighborhood_candidates_md: Path
    source_locks_json: Path

    def as_dict(self) -> dict[str, str]:
        return {key: str(value) for key, value in self.__dict__.items()}


@dataclass(frozen=True)
class V117RankingPaths:
    output_dir: Path
    manifest_json: Path
    ranked_candidates_json: Path
    ranked_candidates_csv: Path
    ranked_candidates_md: Path
    source_locks_json: Path

    def as_dict(self) -> dict[str, str]:
        return {key: str(value) for key, value in self.__dict__.items()}


@dataclass(frozen=True)
class V117SandboxPaths:
    output_dir: Path
    manifest_json: Path
    sandbox_results_json: Path
    sandbox_results_csv: Path
    sandbox_results_md: Path
    source_locks_json: Path

    def as_dict(self) -> dict[str, str]:
        return {key: str(value) for key, value in self.__dict__.items()}


@dataclass(frozen=True)
class V117EvidencePackagePaths:
    output_dir: Path
    manifest_json: Path
    final_decision_json: Path
    final_decision_md: Path
    claim_audit_json: Path
    claim_audit_md: Path
    source_locks_json: Path
    package_readme_md: Path
    reproduction_md: Path

    def as_dict(self) -> dict[str, str]:
        return {key: str(value) for key, value in self.__dict__.items()}


def v117_snap_diagnostic_paths(output_dir: Path = DEFAULT_V117_SNAP_DIAGNOSTICS_DIR) -> V117SnapDiagnosticPaths:
    output_dir = Path(output_dir)
    return V117SnapDiagnosticPaths(
        output_dir=output_dir,
        manifest_json=output_dir / "manifest.json",
        snap_diagnostics_json=output_dir / "snap-diagnostics.json",
        snap_diagnostics_csv=output_dir / "snap-diagnostics.csv",
        snap_diagnostics_md=output_dir / "snap-diagnostics.md",
        snap_neighborhood_seeds_json=output_dir / "snap-neighborhood-seeds.json",
        source_locks_json=output_dir / "source-locks.json",
    )


def v117_neighborhood_paths(output_dir: Path = DEFAULT_V117_NEIGHBORHOOD_DIR) -> V117NeighborhoodPaths:
    output_dir = Path(output_dir)
    return V117NeighborhoodPaths(
        output_dir=output_dir,
        manifest_json=output_dir / "manifest.json",
        neighborhood_candidates_json=output_dir / "neighborhood-candidates.json",
        neighborhood_candidates_csv=output_dir / "neighborhood-candidates.csv",
        neighborhood_candidates_md=output_dir / "neighborhood-candidates.md",
        source_locks_json=output_dir / "source-locks.json",
    )


def v117_ranking_paths(output_dir: Path = DEFAULT_V117_RANKING_DIR) -> V117RankingPaths:
    output_dir = Path(output_dir)
    return V117RankingPaths(
        output_dir=output_dir,
        manifest_json=output_dir / "manifest.json",
        ranked_candidates_json=output_dir / "ranked-candidates.json",
        ranked_candidates_csv=output_dir / "ranked-candidates.csv",
        ranked_candidates_md=output_dir / "ranked-candidates.md",
        source_locks_json=output_dir / "source-locks.json",
    )


def v117_sandbox_paths(output_dir: Path = DEFAULT_V117_SANDBOX_DIR) -> V117SandboxPaths:
    output_dir = Path(output_dir)
    return V117SandboxPaths(
        output_dir=output_dir,
        manifest_json=output_dir / "manifest.json",
        sandbox_results_json=output_dir / "sandbox-results.json",
        sandbox_results_csv=output_dir / "sandbox-results.csv",
        sandbox_results_md=output_dir / "sandbox-results.md",
        source_locks_json=output_dir / "source-locks.json",
    )


def v117_evidence_package_paths(output_dir: Path = DEFAULT_V117_PACKAGE_DIR) -> V117EvidencePackagePaths:
    output_dir = Path(output_dir)
    return V117EvidencePackagePaths(
        output_dir=output_dir,
        manifest_json=output_dir / "manifest.json",
        final_decision_json=output_dir / "final-decision.json",
        final_decision_md=output_dir / "final-decision.md",
        claim_audit_json=output_dir / "claim-audit.json",
        claim_audit_md=output_dir / "claim-audit.md",
        source_locks_json=output_dir / "source-locks.json",
        package_readme_md=output_dir / "README.md",
        reproduction_md=output_dir / "reproduction.md",
    )


SNAP_DIAGNOSTIC_COLUMNS = [
    "diagnostic_id",
    "pair_id",
    "formula",
    "target_family",
    "seed",
    "operator_family",
    "candidate_role",
    "candidate_id",
    "fallback_candidate_id",
    "comparison_outcome",
    "trained_exact_recovery",
    "verification_outcome",
    "status",
    "snap_min_margin",
    "snap_active_node_count",
    "low_margin_slot_count",
    "lowest_margin_slots_json",
    "low_confidence_alternatives_json",
    "pre_snap_mse",
    "post_snap_mse",
    "post_snap_minus_soft_best",
    "post_snap_minus_pre_snap",
    "branch_cut_crossing_count",
    "branch_cut_proximity_count",
    "branch_input_count",
    "artifact_path",
    "snap_mismatch_class",
    "neighborhood_seed",
]


NEIGHBORHOOD_COLUMNS = [
    "candidate_uid",
    "seed_id",
    "pair_id",
    "formula",
    "target_family",
    "seed",
    "operator_family",
    "candidate_role",
    "candidate_id",
    "source_candidate_id",
    "provenance",
    "move_count",
    "heuristic_gap",
    "moves_json",
    "ast_json",
    "target_formula_leakage",
    "generation_status",
    "verifier_status",
]


RANKING_COLUMNS = [
    "rank",
    "candidate_uid",
    "seed_id",
    "pair_id",
    "formula",
    "target_family",
    "seed",
    "operator_family",
    "candidate_id",
    "provenance",
    "verifier_status",
    "evidence_class",
    "post_snap_mse",
    "heldout_max_abs_error",
    "extrapolation_max_abs_error",
    "high_precision_max_error",
    "move_count",
    "heuristic_gap",
    "selected",
    "selection_reason",
    "rejection_reason",
]


SANDBOX_COLUMNS = [
    "group",
    "operator_family",
    "target_family",
    "ranked_rows",
    "exact_recovery",
    "verified_equivalence",
    "loss_only",
    "fallback",
    "original_snap",
    "negative_control_rows",
]


def write_v117_snap_diagnostics(
    output_dir: Path = DEFAULT_V117_SNAP_DIAGNOSTICS_DIR,
    *,
    campaign_dir: Path = DEFAULT_V116_CAMPAIGN_DIR,
    overwrite: bool = False,
    low_margin_threshold: float = 0.1,
) -> V117SnapDiagnosticPaths:
    """Write v1.17 snap diagnostics and deterministic neighborhood seed manifest."""

    output_dir = Path(output_dir)
    campaign_dir = Path(campaign_dir)
    paths = v117_snap_diagnostic_paths(output_dir)
    if paths.manifest_json.exists() and not overwrite:
        raise V117PackageError(f"{paths.manifest_json} already exists; pass overwrite=True to refresh")
    paths.output_dir.mkdir(parents=True, exist_ok=True)

    paired_rows = _read_csv(campaign_dir / "tables" / "geml-paired-comparison.csv")
    diagnostics = _snap_diagnostic_rows(paired_rows, low_margin_threshold=low_margin_threshold)
    seeds = _snap_neighborhood_seed_rows(diagnostics, low_margin_threshold=low_margin_threshold)
    locks = _source_locks_payload(
        [
            ("campaign_manifest", campaign_dir / "campaign-manifest.json", "input"),
            ("geml_paired_summary", campaign_dir / "tables" / "geml-paired-summary.json", "input"),
            ("geml_paired_comparison", campaign_dir / "tables" / "geml-paired-comparison.csv", "input"),
            ("runs_table", campaign_dir / "tables" / "runs.csv", "input"),
        ]
    )

    _write_json(paths.snap_diagnostics_json, {"schema": "eml.v117_snap_diagnostics.v1", "rows": diagnostics})
    _write_csv(paths.snap_diagnostics_csv, diagnostics, SNAP_DIAGNOSTIC_COLUMNS)
    paths.snap_diagnostics_md.write_text(_snap_diagnostics_markdown(diagnostics), encoding="utf-8")
    _write_json(
        paths.snap_neighborhood_seeds_json,
        {
            "schema": "eml.v117_snap_neighborhood_seeds.v1",
            "source": str(paths.snap_diagnostics_json),
            "low_margin_threshold": low_margin_threshold,
            "rows": seeds,
        },
    )
    locks["outputs"] = _source_locks(
        [
            ("snap_diagnostics_json", paths.snap_diagnostics_json, "output"),
            ("snap_diagnostics_csv", paths.snap_diagnostics_csv, "output"),
            ("snap_diagnostics_md", paths.snap_diagnostics_md, "output"),
            ("snap_neighborhood_seeds", paths.snap_neighborhood_seeds_json, "output"),
        ]
    )
    _write_json(paths.source_locks_json, locks)

    manifest = {
        "schema": "eml.v117_snap_diagnostics_manifest.v1",
        "generated_at": _now_iso(),
        "campaign_dir": str(campaign_dir),
        "outputs": paths.as_dict(),
        "counts": {
            "paired_rows": len(paired_rows),
            "diagnostic_rows": len(diagnostics),
            "neighborhood_seed_rows": len(seeds),
            "low_margin_rows": sum(1 for row in diagnostics if _as_float(row.get("snap_min_margin")) <= low_margin_threshold),
            "loss_only_rows": sum(1 for row in diagnostics if str(row.get("comparison_outcome") or "").endswith("lower_post_snap_mse")),
        },
        "source_locks": str(paths.source_locks_json),
        "source_locks_ok": all(row["status"] == "locked" for row in locks["inputs"]),
        "claim_boundary": "Snap diagnostics seed target-agnostic neighborhood search; they do not change verifier recovery definitions.",
    }
    _write_json(paths.manifest_json, manifest)
    return paths


def write_v117_neighborhood_candidates(
    output_dir: Path = DEFAULT_V117_NEIGHBORHOOD_DIR,
    *,
    snap_diagnostics_dir: Path = DEFAULT_V117_SNAP_DIAGNOSTICS_DIR,
    overwrite: bool = False,
    candidate_budget: int = 32,
    beam_width: int = 8,
    max_moves: int = 2,
    max_slots: int | None = 6,
) -> V117NeighborhoodPaths:
    """Write bounded exact-tree neighborhood candidates from Phase 94 seed rows."""

    output_dir = Path(output_dir)
    snap_diagnostics_dir = Path(snap_diagnostics_dir)
    paths = v117_neighborhood_paths(output_dir)
    if paths.manifest_json.exists() and not overwrite:
        raise V117PackageError(f"{paths.manifest_json} already exists; pass overwrite=True to refresh")
    paths.output_dir.mkdir(parents=True, exist_ok=True)

    seeds_path = snap_diagnostics_dir / "snap-neighborhood-seeds.json"
    seeds_payload = _read_json(seeds_path)
    seed_rows = [dict(row) for row in seeds_payload.get("rows", []) if isinstance(row, Mapping)]
    candidate_rows: list[dict[str, Any]] = []
    artifact_paths: set[Path] = set()
    for seed in sorted(seed_rows, key=_seed_sort_key):
        artifact_path = Path(str(seed.get("artifact_path") or ""))
        if artifact_path:
            artifact_paths.add(artifact_path)
        candidate_rows.extend(
            _candidate_rows_for_seed(
                seed,
                candidate_budget=candidate_budget,
                beam_width=beam_width,
                max_moves=max_moves,
                max_slots=max_slots,
            )
        )

    _write_json(
        paths.neighborhood_candidates_json,
        {
            "schema": "eml.v117_neighborhood_candidates.v1",
            "source": str(seeds_path),
            "budget": {
                "candidate_budget": candidate_budget,
                "beam_width": beam_width,
                "max_moves": max_moves,
                "max_slots": max_slots,
            },
            "rows": candidate_rows,
        },
    )
    _write_csv(paths.neighborhood_candidates_csv, candidate_rows, NEIGHBORHOOD_COLUMNS)
    paths.neighborhood_candidates_md.write_text(_neighborhood_markdown(candidate_rows), encoding="utf-8")

    lock_items = [("snap_neighborhood_seeds", seeds_path, "input")]
    lock_items.extend((f"candidate_artifact_{index:03d}", path, "input") for index, path in enumerate(sorted(artifact_paths, key=str)))
    locks = _source_locks_payload(lock_items)
    locks["outputs"] = _source_locks(
        [
            ("neighborhood_candidates_json", paths.neighborhood_candidates_json, "output"),
            ("neighborhood_candidates_csv", paths.neighborhood_candidates_csv, "output"),
            ("neighborhood_candidates_md", paths.neighborhood_candidates_md, "output"),
        ]
    )
    _write_json(paths.source_locks_json, locks)
    manifest = {
        "schema": "eml.v117_neighborhood_manifest.v1",
        "generated_at": _now_iso(),
        "snap_diagnostics_dir": str(snap_diagnostics_dir),
        "outputs": paths.as_dict(),
        "counts": {
            "seed_rows": len(seed_rows),
            "candidate_rows": len(candidate_rows),
            "original_rows": sum(1 for row in candidate_rows if row.get("provenance") == "original_snap"),
            "fallback_rows": sum(1 for row in candidate_rows if row.get("provenance") == "fallback_snap"),
            "generated_rows": sum(1 for row in candidate_rows if str(row.get("provenance") or "").startswith("snap_neighborhood")),
        },
        "source_locks": str(paths.source_locks_json),
        "source_locks_ok": all(row["status"] == "locked" for row in locks["inputs"]),
        "claim_boundary": "Neighborhood candidates are target-agnostic exact alternatives; Phase 96 owns verifier-first promotion.",
    }
    _write_json(paths.manifest_json, manifest)
    return paths


def write_v117_candidate_ranking(
    output_dir: Path = DEFAULT_V117_RANKING_DIR,
    *,
    neighborhoods_dir: Path = DEFAULT_V117_NEIGHBORHOOD_DIR,
    overwrite: bool = False,
) -> V117RankingPaths:
    """Rank v1.17 candidates with verifier status before loss."""

    output_dir = Path(output_dir)
    neighborhoods_dir = Path(neighborhoods_dir)
    paths = v117_ranking_paths(output_dir)
    if paths.manifest_json.exists() and not overwrite:
        raise V117PackageError(f"{paths.manifest_json} already exists; pass overwrite=True to refresh")
    paths.output_dir.mkdir(parents=True, exist_ok=True)

    candidates_path = neighborhoods_dir / "neighborhood-candidates.json"
    payload = _read_json(candidates_path)
    rows = [dict(row) for row in payload.get("rows", []) if isinstance(row, Mapping)]
    ranked = _rank_candidate_rows(rows)
    selected = next((row for row in ranked if row["selected"]), None)
    counts = _ranking_counts(ranked)

    _write_json(
        paths.ranked_candidates_json,
        {
            "schema": "eml.v117_candidate_ranking.v1",
            "source": str(candidates_path),
            "verifier_gate": "verifier_status_first_then_error_then_post_snap_loss",
            "selected_candidate": selected,
            "counts": counts,
            "rows": ranked,
        },
    )
    _write_csv(paths.ranked_candidates_csv, ranked, RANKING_COLUMNS)
    paths.ranked_candidates_md.write_text(_ranking_markdown(ranked, selected), encoding="utf-8")
    locks = _source_locks_payload([("neighborhood_candidates", candidates_path, "input")])
    locks["outputs"] = _source_locks(
        [
            ("ranked_candidates_json", paths.ranked_candidates_json, "output"),
            ("ranked_candidates_csv", paths.ranked_candidates_csv, "output"),
            ("ranked_candidates_md", paths.ranked_candidates_md, "output"),
        ]
    )
    _write_json(paths.source_locks_json, locks)
    manifest = {
        "schema": "eml.v117_candidate_ranking_manifest.v1",
        "generated_at": _now_iso(),
        "neighborhoods_dir": str(neighborhoods_dir),
        "outputs": paths.as_dict(),
        "counts": counts,
        "selected_candidate_id": selected.get("candidate_id") if selected else None,
        "selected_evidence_class": selected.get("evidence_class") if selected else "no_verified_candidate",
        "source_locks": str(paths.source_locks_json),
        "source_locks_ok": all(row["status"] == "locked" for row in locks["inputs"]),
        "claim_boundary": "Ranking promotes only verifier-passed candidates; loss-only rows remain diagnostic.",
    }
    _write_json(paths.manifest_json, manifest)
    return paths


def write_v117_recovery_sandbox(
    output_dir: Path = DEFAULT_V117_SANDBOX_DIR,
    *,
    ranking_dir: Path = DEFAULT_V117_RANKING_DIR,
    overwrite: bool = False,
) -> V117SandboxPaths:
    """Write the focused v1.17 exact-signal sandbox gate."""

    output_dir = Path(output_dir)
    ranking_dir = Path(ranking_dir)
    paths = v117_sandbox_paths(output_dir)
    if paths.manifest_json.exists() and not overwrite:
        raise V117PackageError(f"{paths.manifest_json} already exists; pass overwrite=True to refresh")
    paths.output_dir.mkdir(parents=True, exist_ok=True)

    ranked_path = ranking_dir / "ranked-candidates.json"
    payload = _read_json(ranked_path)
    rows = [dict(row) for row in payload.get("rows", []) if isinstance(row, Mapping)]
    summary_rows = _sandbox_summary_rows(rows)
    natural_exact = [row for row in rows if _is_natural(row) and row.get("evidence_class") == "exact_recovery"]
    negative_control_exact = [row for row in rows if not _is_natural(row) and row.get("evidence_class") == "exact_recovery"]
    exact_signal_found = bool(natural_exact)
    broader_campaign_gate = "allow_next_campaign_planning" if exact_signal_found and not negative_control_exact else "block_broader_campaigns"
    decision = "exact_signal_found" if exact_signal_found and not negative_control_exact else "no_exact_signal"
    rationale = (
        "At least one natural-family verifier-gated exact recovery appears in ranked candidates."
        if exact_signal_found and not negative_control_exact
        else "No clean natural-family verifier-gated exact recovery signal appears; broader campaigns remain blocked."
    )

    results = {
        "schema": "eml.v117_recovery_sandbox.v1",
        "source": str(ranked_path),
        "decision": decision,
        "exact_signal_found": exact_signal_found,
        "broader_campaign_gate": broader_campaign_gate,
        "rationale": rationale,
        "natural_exact_recovery_count": len(natural_exact),
        "negative_control_exact_recovery_count": len(negative_control_exact),
        "summary_rows": summary_rows,
        "selected_exact_candidates": [row for row in rows if row.get("selected") is True and row.get("evidence_class") == "exact_recovery"],
    }
    _write_json(paths.sandbox_results_json, results)
    _write_csv(paths.sandbox_results_csv, summary_rows, SANDBOX_COLUMNS)
    paths.sandbox_results_md.write_text(_sandbox_markdown(results), encoding="utf-8")
    locks = _source_locks_payload([("ranked_candidates", ranked_path, "input")])
    locks["outputs"] = _source_locks(
        [
            ("sandbox_results_json", paths.sandbox_results_json, "output"),
            ("sandbox_results_csv", paths.sandbox_results_csv, "output"),
            ("sandbox_results_md", paths.sandbox_results_md, "output"),
        ]
    )
    _write_json(paths.source_locks_json, locks)
    manifest = {
        "schema": "eml.v117_recovery_sandbox_manifest.v1",
        "generated_at": _now_iso(),
        "ranking_dir": str(ranking_dir),
        "outputs": paths.as_dict(),
        "decision": decision,
        "exact_signal_found": exact_signal_found,
        "broader_campaign_gate": broader_campaign_gate,
        "source_locks": str(paths.source_locks_json),
        "source_locks_ok": all(row["status"] == "locked" for row in locks["inputs"]),
        "claim_boundary": "Broader campaigns are blocked unless this sandbox finds clean verifier-gated natural exact signal.",
    }
    _write_json(paths.manifest_json, manifest)
    return paths


def write_v117_evidence_package(
    output_dir: Path = DEFAULT_V117_PACKAGE_DIR,
    *,
    snap_diagnostics_dir: Path = DEFAULT_V117_SNAP_DIAGNOSTICS_DIR,
    neighborhoods_dir: Path = DEFAULT_V117_NEIGHBORHOOD_DIR,
    ranking_dir: Path = DEFAULT_V117_RANKING_DIR,
    sandbox_dir: Path = DEFAULT_V117_SANDBOX_DIR,
    v116_package_dir: Path = DEFAULT_V116_PACKAGE_DIR,
    overwrite: bool = False,
) -> V117EvidencePackagePaths:
    """Assemble the source-locked v1.17 evidence package and final campaign gate."""

    output_dir = Path(output_dir)
    snap_diagnostics_dir = Path(snap_diagnostics_dir)
    neighborhoods_dir = Path(neighborhoods_dir)
    ranking_dir = Path(ranking_dir)
    sandbox_dir = Path(sandbox_dir)
    v116_package_dir = Path(v116_package_dir)
    paths = v117_evidence_package_paths(output_dir)
    if paths.manifest_json.exists() and not overwrite:
        raise V117PackageError(f"{paths.manifest_json} already exists; pass overwrite=True to refresh")
    paths.output_dir.mkdir(parents=True, exist_ok=True)

    snap_manifest = _read_json(snap_diagnostics_dir / "manifest.json")
    snap_diagnostics = _read_json(snap_diagnostics_dir / "snap-diagnostics.json")
    snap_seeds = _read_json(snap_diagnostics_dir / "snap-neighborhood-seeds.json")
    neighborhood_manifest = _read_json(neighborhoods_dir / "manifest.json")
    neighborhoods = _read_json(neighborhoods_dir / "neighborhood-candidates.json")
    ranking_manifest = _read_json(ranking_dir / "manifest.json")
    ranked_candidates = _read_json(ranking_dir / "ranked-candidates.json")
    sandbox_manifest = _read_json(sandbox_dir / "manifest.json")
    sandbox_results = _read_json(sandbox_dir / "sandbox-results.json")
    v116_manifest = _read_json(v116_package_dir / "manifest.json")

    required_inputs = [
        ("v116_package_manifest", v116_package_dir / "manifest.json", "input"),
        ("snap_diagnostics_manifest", snap_diagnostics_dir / "manifest.json", "input"),
        ("snap_diagnostics", snap_diagnostics_dir / "snap-diagnostics.json", "input"),
        ("snap_neighborhood_seeds", snap_diagnostics_dir / "snap-neighborhood-seeds.json", "input"),
        ("neighborhood_manifest", neighborhoods_dir / "manifest.json", "input"),
        ("neighborhood_candidates", neighborhoods_dir / "neighborhood-candidates.json", "input"),
        ("ranking_manifest", ranking_dir / "manifest.json", "input"),
        ("ranked_candidates", ranking_dir / "ranked-candidates.json", "input"),
        ("sandbox_manifest", sandbox_dir / "manifest.json", "input"),
        ("sandbox_results", sandbox_dir / "sandbox-results.json", "input"),
    ]
    optional_inputs = [
        ("v116_source_locks", v116_package_dir / "source-locks.json", "input"),
        ("v116_claim_audit", v116_package_dir / "claim-audit.json", "input"),
        ("v116_reproduction", v116_package_dir / "reproduction.md", "input"),
        ("v116_gate_evaluation", v116_package_dir / "gate-evaluation.json", "input"),
        ("v116_failure_taxonomy_reference", v116_package_dir / "ablations" / "failure-examples.json", "input"),
    ]
    locks = _source_locks_payload([*required_inputs, *optional_inputs])
    _mark_required_locks(locks, required_inputs)

    commands = _v117_reproduction_commands(
        snap_diagnostics_dir=snap_diagnostics_dir,
        neighborhoods_dir=neighborhoods_dir,
        ranking_dir=ranking_dir,
        sandbox_dir=sandbox_dir,
        output_dir=output_dir,
        v116_package_dir=v116_package_dir,
    )
    final_decision = _v117_final_decision_payload(
        snap_manifest=snap_manifest,
        snap_diagnostics=snap_diagnostics,
        snap_seeds=snap_seeds,
        snap_diagnostics_dir=snap_diagnostics_dir,
        neighborhood_manifest=neighborhood_manifest,
        neighborhoods=neighborhoods,
        neighborhoods_dir=neighborhoods_dir,
        ranking_manifest=ranking_manifest,
        ranked_candidates=ranked_candidates,
        ranking_dir=ranking_dir,
        sandbox_manifest=sandbox_manifest,
        sandbox_results=sandbox_results,
        sandbox_dir=sandbox_dir,
        v116_manifest=v116_manifest,
        v116_package_dir=v116_package_dir,
        source_locks=locks,
        commands=commands,
    )
    final_md = _v117_final_decision_markdown(final_decision)
    readme_md = _v117_package_readme(final_decision)
    reproduction_md = _v117_reproduction_markdown(commands)
    audit = build_v117_claim_audit(final_md + "\n" + readme_md, final_decision=final_decision, source_locks=locks)

    _write_json(paths.final_decision_json, final_decision)
    paths.final_decision_md.write_text(final_md, encoding="utf-8")
    _write_json(paths.claim_audit_json, audit)
    paths.claim_audit_md.write_text(_v117_claim_audit_markdown(audit), encoding="utf-8")
    paths.package_readme_md.write_text(readme_md, encoding="utf-8")
    paths.reproduction_md.write_text(reproduction_md, encoding="utf-8")
    locks["outputs"] = _source_locks(
        [
            ("final_decision_json", paths.final_decision_json, "output"),
            ("final_decision_md", paths.final_decision_md, "output"),
            ("claim_audit_json", paths.claim_audit_json, "output"),
            ("claim_audit_md", paths.claim_audit_md, "output"),
            ("package_readme", paths.package_readme_md, "output"),
            ("reproduction", paths.reproduction_md, "output"),
        ]
    )
    _write_json(paths.source_locks_json, locks)

    manifest = {
        "schema": "eml.v117_evidence_package.v1",
        "generated_at": _now_iso(),
        "decision": final_decision["decision"],
        "broader_campaign_gate": final_decision["broader_campaign_gate"],
        "next_campaign_allowed": final_decision["next_campaign_allowed"],
        "exact_signal_found": final_decision["exact_signal_found"],
        "source_locks_ok": _required_source_locks_ok(locks),
        "claim_audit_status": audit["status"],
        "outputs": paths.as_dict(),
        "final_decision": str(paths.final_decision_json),
        "claim_audit": {"status": audit["status"], "json": str(paths.claim_audit_json), "markdown": str(paths.claim_audit_md)},
        "source_locks": str(paths.source_locks_json),
        "reproduction": str(paths.reproduction_md),
        "package_readme": str(paths.package_readme_md),
        "input_dirs": {
            "v116_package_dir": str(v116_package_dir),
            "snap_diagnostics_dir": str(snap_diagnostics_dir),
            "neighborhoods_dir": str(neighborhoods_dir),
            "ranking_dir": str(ranking_dir),
            "sandbox_dir": str(sandbox_dir),
        },
        "claim_boundary": final_decision["claim_boundary"],
    }
    _write_json(paths.manifest_json, manifest)
    return paths


def build_v117_claim_audit(
    claim_text: str,
    *,
    final_decision: Mapping[str, Any],
    source_locks: Mapping[str, Any],
) -> dict[str, Any]:
    """Audit final v1.17 package language against the exact-signal gate."""

    lower_claim = claim_text.lower()
    decision = str(final_decision.get("decision") or "")
    gate = str(final_decision.get("broader_campaign_gate") or "")
    exact_signal_found = bool(final_decision.get("exact_signal_found"))
    next_campaign_allowed = bool(final_decision.get("next_campaign_allowed"))
    natural_exact = int(final_decision.get("natural_exact_recovery_count") or 0)
    negative_control_exact = int(final_decision.get("negative_control_exact_recovery_count") or 0)
    checks = [
        _audit_check(
            "final_decision_is_allowed",
            decision in {"exact_signal_found", "still_inconclusive", "negative"},
            "Final decision is one of the predefined v1.17 outcomes.",
        ),
        _audit_check(
            "gate_controls_next_campaign",
            (gate == "allow_next_campaign_planning" and decision == "exact_signal_found" and next_campaign_allowed)
            or (gate == "block_broader_campaigns" and decision in {"still_inconclusive", "negative"} and not next_campaign_allowed),
            "Broader campaign planning follows the sandbox gate.",
        ),
        _audit_check(
            "exact_signal_counts_match_decision",
            (decision != "exact_signal_found") or (exact_signal_found and natural_exact > 0 and negative_control_exact == 0),
            "Exact-signal decisions require natural exact recovery and no negative-control exact recovery.",
        ),
        _audit_check(
            "v116_package_locked",
            _source_lock_status(source_locks, "v116_package_manifest") == "locked",
            "v1.16 package manifest is source-locked as the before-state reference.",
        ),
        _audit_check(
            "required_sources_locked",
            _required_source_locks_ok(source_locks),
            "Required v1.16 and v1.17 source artifacts are locked.",
        ),
        _audit_check(
            "additive_boundary_stated",
            "additive" in lower_claim and "v1.16 package remains intact" in lower_claim,
            "Package states that v1.17 comparisons are additive and do not mutate v1.16.",
        ),
        _audit_check(
            "loss_only_not_promoted",
            not _contains_any(lower_claim, ("loss-only recovery", "loss only recovery", "lower-loss recovery", "loss-only rows are recovered")),
            "Package does not promote loss-only diagnostics into recovery claims.",
        ),
        _audit_check(
            "failure_taxonomy_referenced",
            "failure taxonomy" in lower_claim,
            "Package preserves failure taxonomy context for non-recovery rows.",
        ),
        _audit_check(
            "reproduction_commands_present",
            len(final_decision.get("reproduction_commands") or []) >= 5,
            "Package includes reproduction commands for all v1.17 stages.",
        ),
    ]
    return {
        "schema": "eml.v117_claim_audit.v1",
        "status": "passed" if all(check["status"] == "passed" for check in checks) else "failed",
        "decision": decision,
        "broader_campaign_gate": gate,
        "checks": checks,
    }


def _snap_diagnostic_rows(
    paired_rows: Iterable[Mapping[str, Any]],
    *,
    low_margin_threshold: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for pair in paired_rows:
        for prefix, operator_family in (("raw", "raw_eml"), ("ipi", "ipi_eml")):
            candidate_id = str(pair.get(f"{prefix}_selected_candidate_id") or "")
            role = "selected" if candidate_id else "selected_unavailable"
            outcome = str(pair.get("comparison_outcome") or "")
            row = {
                "diagnostic_id": f"{pair.get('pair_id', '')}:{operator_family}:{role}",
                "pair_id": str(pair.get("pair_id") or ""),
                "formula": str(pair.get("formula") or ""),
                "target_family": str(pair.get("target_family") or ""),
                "seed": str(pair.get("seed") or ""),
                "operator_family": operator_family,
                "candidate_role": role,
                "candidate_id": candidate_id,
                "fallback_candidate_id": str(pair.get(f"{prefix}_fallback_candidate_id") or ""),
                "comparison_outcome": outcome,
                "trained_exact_recovery": _bool_text(pair.get(f"{prefix}_trained_exact_recovery")),
                "verification_outcome": str(pair.get(f"{prefix}_verification_outcome") or ""),
                "status": str(pair.get(f"{prefix}_status") or ""),
                "snap_min_margin": pair.get(f"{prefix}_snap_min_margin"),
                "snap_active_node_count": pair.get(f"{prefix}_snap_active_node_count"),
                "low_margin_slot_count": pair.get(f"{prefix}_low_margin_slot_count"),
                "lowest_margin_slots_json": _canonical_json_cell(pair.get(f"{prefix}_lowest_margin_slots_json")),
                "low_confidence_alternatives_json": _canonical_json_cell(pair.get(f"{prefix}_low_confidence_alternatives_json")),
                "pre_snap_mse": pair.get(f"{prefix}_pre_snap_mse"),
                "post_snap_mse": pair.get(f"{prefix}_post_snap_mse"),
                "post_snap_minus_soft_best": pair.get(f"{prefix}_post_snap_minus_soft_best"),
                "post_snap_minus_pre_snap": pair.get(f"{prefix}_post_snap_minus_pre_snap"),
                "branch_cut_crossing_count": pair.get(f"{prefix}_branch_cut_crossing_count"),
                "branch_cut_proximity_count": pair.get(f"{prefix}_branch_cut_proximity_count"),
                "branch_input_count": pair.get(f"{prefix}_branch_input_count"),
                "artifact_path": str(pair.get(f"{prefix}_artifact_path") or ""),
            }
            row["snap_mismatch_class"] = _snap_mismatch_class(row, outcome, low_margin_threshold=low_margin_threshold)
            row["neighborhood_seed"] = _is_neighborhood_seed(row, low_margin_threshold=low_margin_threshold)
            rows.append(row)
    return sorted(rows, key=_diagnostic_sort_key)


def _snap_neighborhood_seed_rows(
    diagnostics: Iterable[Mapping[str, Any]],
    *,
    low_margin_threshold: float,
) -> list[dict[str, Any]]:
    seeds: list[dict[str, Any]] = []
    for row in diagnostics:
        if not _is_neighborhood_seed(row, low_margin_threshold=low_margin_threshold):
            continue
        seeds.append(
            {
                "seed_id": f"{row.get('pair_id')}:{row.get('operator_family')}:{row.get('candidate_role')}",
                "pair_id": row.get("pair_id"),
                "formula": row.get("formula"),
                "target_family": row.get("target_family"),
                "seed": row.get("seed"),
                "operator_family": row.get("operator_family"),
                "candidate_id": row.get("candidate_id"),
                "fallback_candidate_id": row.get("fallback_candidate_id"),
                "comparison_outcome": row.get("comparison_outcome"),
                "snap_min_margin": row.get("snap_min_margin"),
                "low_margin_slot_count": row.get("low_margin_slot_count"),
                "lowest_margin_slots_json": row.get("lowest_margin_slots_json"),
                "low_confidence_alternatives_json": row.get("low_confidence_alternatives_json"),
                "artifact_path": row.get("artifact_path"),
                "source": "v1.17_snap_diagnostics",
                "target_formula_leakage": False,
            }
        )
    return sorted(seeds, key=_seed_sort_key)


def _is_neighborhood_seed(row: Mapping[str, Any], *, low_margin_threshold: float) -> bool:
    outcome = str(row.get("comparison_outcome") or "")
    if outcome in {"ipi_recovery_win", "raw_recovery_win", "both_recovered"}:
        return False
    if outcome.endswith("lower_post_snap_mse") or outcome == "neutral_no_recovery":
        return True
    return _as_float(row.get("snap_min_margin"), default=math.inf) <= low_margin_threshold


def _snap_mismatch_class(row: Mapping[str, Any], outcome: str, *, low_margin_threshold: float) -> str:
    if outcome in {"ipi_recovery_win", "raw_recovery_win", "both_recovered"}:
        return "exact_recovery_signal"
    if _as_float(row.get("branch_cut_crossing_count")) > 0:
        return "branch_pathology"
    if _as_float(row.get("snap_min_margin"), default=math.inf) <= low_margin_threshold or _as_float(row.get("low_margin_slot_count")) > 0:
        return "low_margin_snap_mismatch"
    if _as_float(row.get("post_snap_minus_soft_best")) > 0 or _as_float(row.get("post_snap_minus_pre_snap")) > 0:
        return "hard_snap_degradation"
    if outcome.endswith("lower_post_snap_mse"):
        return "loss_only_snap_candidate"
    return "verifier_or_optimization_miss"


def _diagnostic_sort_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        0 if bool(row.get("neighborhood_seed")) else 1,
        _as_float(row.get("snap_min_margin"), default=math.inf),
        str(row.get("formula") or ""),
        str(row.get("seed") or ""),
        str(row.get("operator_family") or ""),
        str(row.get("candidate_id") or ""),
    )


def _seed_sort_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    outcome = str(row.get("comparison_outcome") or "")
    priority = 0 if outcome.endswith("lower_post_snap_mse") else 1
    return (
        priority,
        _as_float(row.get("snap_min_margin"), default=math.inf),
        str(row.get("formula") or ""),
        str(row.get("seed") or ""),
        str(row.get("operator_family") or ""),
        str(row.get("candidate_id") or ""),
    )


def _snap_diagnostics_markdown(rows: Iterable[Mapping[str, Any]]) -> str:
    lines = [
        "# v1.17 Snap Diagnostics",
        "",
        "Snap diagnostics are explanatory only. Exact recovery remains verifier-owned.",
        "",
        "| Pair | Operator | Outcome | Margin | Low Slots | Class | Seed |",
        "|------|----------|---------|--------|-----------|-------|------|",
    ]
    for row in rows:
        lines.append(
            f"| {row.get('pair_id')} | {row.get('operator_family')} | {row.get('comparison_outcome')} | "
            f"{row.get('snap_min_margin')} | {row.get('low_margin_slot_count')} | "
            f"{row.get('snap_mismatch_class')} | {row.get('neighborhood_seed')} |"
        )
    lines.append("")
    return "\n".join(lines)


def _candidate_rows_for_seed(
    seed: Mapping[str, Any],
    *,
    candidate_budget: int,
    beam_width: int,
    max_moves: int,
    max_slots: int | None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seed_id = str(seed.get("seed_id") or "")
    source_candidate_id = str(seed.get("candidate_id") or "")
    fallback_candidate_id = str(seed.get("fallback_candidate_id") or "")
    rows.append(_provenance_candidate_row(seed, candidate_id=source_candidate_id, role="original", provenance="original_snap"))
    if fallback_candidate_id and fallback_candidate_id != source_candidate_id:
        rows.append(_provenance_candidate_row(seed, candidate_id=fallback_candidate_id, role="fallback", provenance="fallback_snap"))

    candidate_payload, config = _load_candidate_payload(seed, source_candidate_id)
    if candidate_payload is None:
        rows[0]["generation_status"] = "source_candidate_payload_missing"
        return rows

    try:
        snap = _snap_from_payload(candidate_payload["snap"])
        alternatives = _slot_alternatives_from_payload(candidate_payload.get("slot_alternatives") or [])
        variables = tuple(str(item) for item in config.get("variables") or ["x"])
        constants = tuple(parse_constant_value(item) for item in config.get("constants") or ["1"])
        operator_family = eml_operator_from_spec(config.get("operator_family") or raw_eml_operator().as_dict())
        variants = expand_snap_neighborhood(
            snap,
            alternatives,
            depth=max(int(snap.expression.depth()), 1),
            variables=variables,
            constants=constants,
            operator_family=operator_family,
            beam_width=beam_width,
            max_moves=max_moves,
            max_slots=max_slots,
        )
    except Exception as exc:  # noqa: BLE001 - artifact manifests should explain malformed inputs.
        rows[0]["generation_status"] = f"generation_error:{type(exc).__name__}"
        return rows

    for index, variant in enumerate(variants[: max(candidate_budget - len(rows), 0)]):
        move_count = len(variant.moves)
        rows.append(
            {
                **_seed_identity(seed),
                "candidate_uid": f"{seed_id}:n{index:03d}",
                "candidate_role": "neighborhood",
                "candidate_id": f"{source_candidate_id}:n{index:03d}",
                "source_candidate_id": source_candidate_id,
                "provenance": f"snap_neighborhood_{move_count}_slot",
                "move_count": move_count,
                "heuristic_gap": variant.heuristic_gap,
                "moves_json": _canonical_json_cell([move.as_dict() for move in variant.moves]),
                "ast_json": _canonical_json_cell(variant.expression.to_document(source="snap_neighborhood_candidate")),
                "target_formula_leakage": False,
                "generation_status": "generated",
                "verifier_status": "pending",
            }
        )
    return sorted(rows[:candidate_budget], key=_candidate_sort_key)


def _provenance_candidate_row(seed: Mapping[str, Any], *, candidate_id: str, role: str, provenance: str) -> dict[str, Any]:
    return {
        **_seed_identity(seed),
        "candidate_uid": f"{seed.get('seed_id')}:{role}",
        "candidate_role": role,
        "candidate_id": candidate_id,
        "source_candidate_id": candidate_id,
        "provenance": provenance,
        "move_count": 0,
        "heuristic_gap": 0.0,
        "moves_json": "[]",
        "ast_json": "",
        "target_formula_leakage": False,
        "generation_status": "preserved",
        "verifier_status": "pending",
    }


def _seed_identity(seed: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "seed_id": seed.get("seed_id"),
        "pair_id": seed.get("pair_id"),
        "formula": seed.get("formula"),
        "target_family": seed.get("target_family"),
        "seed": seed.get("seed"),
        "operator_family": seed.get("operator_family"),
    }


def _load_candidate_payload(seed: Mapping[str, Any], candidate_id: str) -> tuple[Mapping[str, Any] | None, Mapping[str, Any]]:
    artifact_path = Path(str(seed.get("artifact_path") or ""))
    artifact = _read_json(artifact_path)
    manifest = artifact.get("trained_eml_candidate") if isinstance(artifact.get("trained_eml_candidate"), Mapping) else artifact
    if not isinstance(manifest, Mapping):
        return None, {}
    config = manifest.get("config") if isinstance(manifest.get("config"), Mapping) else {}
    candidates = manifest.get("candidates") if isinstance(manifest.get("candidates"), list) else []
    for candidate in candidates:
        if isinstance(candidate, Mapping) and str(candidate.get("candidate_id") or "") == candidate_id:
            return candidate, config
    for key in ("selected_candidate", "fallback_candidate"):
        candidate = manifest.get(key)
        if isinstance(candidate, Mapping) and str(candidate.get("candidate_id") or "") == candidate_id:
            return candidate, config
    return None, config


def _snap_from_payload(payload: Mapping[str, Any]) -> SnapResult:
    expression = expr_from_document(payload["ast"])
    decisions = [
        SnapDecision(
            path=str(item["path"]),
            side=str(item["side"]),
            choice=str(item["choice"]),
            probability=float(item["probability"]),
            margin=float(item["margin"]),
        )
        for item in payload.get("decisions", [])
        if isinstance(item, Mapping)
    ]
    return SnapResult(
        expression=expression,
        decisions=decisions,
        min_margin=float(payload.get("min_margin", 1.0)),
        active_node_count=int(payload.get("active_node_count", expression.node_count())),
    )


def _slot_alternatives_from_payload(payload: Iterable[Mapping[str, Any]]) -> tuple[ActiveSlotAlternatives, ...]:
    groups: list[ActiveSlotAlternatives] = []
    for item in payload:
        alternatives: list[SlotAlternative] = []
        for alt in item.get("alternatives", []):
            if not isinstance(alt, Mapping):
                continue
            alternatives.append(
                SlotAlternative(
                    choice=str(alt["choice"]),
                    probability=float(alt.get("probability", 0.0)),
                    probability_gap=float(alt.get("probability_gap", 0.0)),
                    rank=int(alt.get("rank", len(alternatives) + 1)),
                    descendant_assignments=tuple(
                        ReplayAssignment(str(assignment["slot"]), str(assignment["choice"]))
                        for assignment in alt.get("descendant_assignments", [])
                        if isinstance(assignment, Mapping)
                    ),
                    subtree_root=str(alt["subtree_root"]) if alt.get("subtree_root") is not None else None,
                )
            )
        if alternatives:
            groups.append(
                ActiveSlotAlternatives(
                    slot=str(item["slot"]),
                    current_choice=str(item["current_choice"]),
                    current_probability=float(item.get("current_probability", 0.0)),
                    current_margin=float(item.get("current_margin", 1.0)),
                    alternatives=tuple(alternatives),
                )
            )
    return tuple(groups)


def _candidate_sort_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    provenance_priority = {"original_snap": 0, "fallback_snap": 1}
    return (
        str(row.get("seed_id") or ""),
        provenance_priority.get(str(row.get("provenance") or ""), 2),
        int(row.get("move_count") or 0),
        _as_float(row.get("heuristic_gap"), default=math.inf),
        str(row.get("candidate_id") or ""),
    )


def _neighborhood_markdown(rows: Iterable[Mapping[str, Any]]) -> str:
    lines = [
        "# v1.17 Snap Neighborhood Candidates",
        "",
        "Candidate generation is target-agnostic. Verifier-first ranking is handled separately.",
        "",
        "| Seed | Candidate | Provenance | Moves | Gap | Status |",
        "|------|-----------|------------|-------|-----|--------|",
    ]
    for row in rows:
        lines.append(
            f"| {row.get('seed_id')} | {row.get('candidate_id')} | {row.get('provenance')} | "
            f"{row.get('move_count')} | {row.get('heuristic_gap')} | {row.get('generation_status')} |"
        )
    lines.append("")
    return "\n".join(lines)


def _rank_candidate_rows(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    classified = [_ranking_row(row) for row in rows]
    classified.sort(key=_ranking_sort_key)
    selected_index = next((index for index, row in enumerate(classified) if row["evidence_class"] in {"exact_recovery", "verified_equivalence"}), None)
    if selected_index is None:
        selected_index = 0 if classified else None
    for index, row in enumerate(classified, start=1):
        row["rank"] = index
        row["selected"] = selected_index is not None and index - 1 == selected_index
        row["selection_reason"] = _selection_reason(row) if row["selected"] else ""
        row["rejection_reason"] = "" if row["selected"] else _rejection_reason(row, classified[selected_index] if selected_index is not None else None)
    return classified


def _ranking_row(row: Mapping[str, Any]) -> dict[str, Any]:
    evidence_class = _evidence_class(row)
    return {
        "rank": 0,
        "candidate_uid": row.get("candidate_uid"),
        "seed_id": row.get("seed_id"),
        "pair_id": row.get("pair_id"),
        "formula": row.get("formula"),
        "target_family": row.get("target_family"),
        "seed": row.get("seed"),
        "operator_family": row.get("operator_family"),
        "candidate_id": row.get("candidate_id"),
        "provenance": row.get("provenance"),
        "verifier_status": str(row.get("verifier_status") or "pending"),
        "evidence_class": evidence_class,
        "post_snap_mse": row.get("post_snap_mse"),
        "heldout_max_abs_error": row.get("heldout_max_abs_error"),
        "extrapolation_max_abs_error": row.get("extrapolation_max_abs_error"),
        "high_precision_max_error": row.get("high_precision_max_error"),
        "move_count": row.get("move_count"),
        "heuristic_gap": row.get("heuristic_gap"),
        "selected": False,
        "selection_reason": "",
        "rejection_reason": "",
    }


def _evidence_class(row: Mapping[str, Any]) -> str:
    explicit = str(row.get("evidence_class") or "")
    if explicit:
        return explicit
    status = str(row.get("verifier_status") or "pending")
    provenance = str(row.get("provenance") or "")
    if status == "recovered":
        return "exact_recovery"
    if status in {"verified_equivalent", "verified_showcase"}:
        return "verified_equivalence"
    if str(row.get("repair_status") or "") in {"repaired", "repaired_candidate"}:
        return "repair_only"
    if str(row.get("same_ast") or "").lower() == "true" or provenance == "same_ast":
        return "same_ast"
    if provenance == "compile_only":
        return "compile_only"
    if provenance == "fallback_snap":
        return "fallback"
    if provenance == "original_snap":
        return "original_snap"
    if status == "failed" and row.get("post_snap_mse") not in (None, ""):
        return "loss_only"
    return "unverified_pending"


def _ranking_sort_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        {
            "exact_recovery": 0,
            "verified_equivalence": 1,
            "repair_only": 2,
            "loss_only": 3,
            "same_ast": 4,
            "compile_only": 5,
            "fallback": 6,
            "original_snap": 7,
            "unverified_pending": 8,
        }.get(str(row.get("evidence_class")), 9),
        _as_float(row.get("high_precision_max_error"), default=math.inf),
        _as_float(row.get("extrapolation_max_abs_error"), default=math.inf),
        _as_float(row.get("heldout_max_abs_error"), default=math.inf),
        _as_float(row.get("post_snap_mse"), default=math.inf),
        int(float(row.get("move_count") or 0)),
        _as_float(row.get("heuristic_gap"), default=math.inf),
        str(row.get("candidate_uid") or ""),
    )


def _selection_reason(row: Mapping[str, Any]) -> str:
    if row.get("evidence_class") == "exact_recovery":
        return "Selected because verifier_status=recovered outranks loss-only and pending candidates."
    if row.get("evidence_class") == "verified_equivalence":
        return "Selected because verified equivalence is the strongest available verifier-owned evidence."
    return "No verifier-passed candidate exists; top row is reported for diagnostics only."


def _rejection_reason(row: Mapping[str, Any], selected: Mapping[str, Any] | None) -> str:
    if selected is None:
        return "No selected row available."
    if row.get("evidence_class") == "loss_only":
        return "Rejected for promotion: lower post-snap loss is diagnostic without verifier recovery."
    if row.get("evidence_class") in {"fallback", "original_snap"}:
        return "Preserved for provenance but not promoted over verifier-passed candidates."
    if row.get("verifier_status") in {"failed", "pending"}:
        return f"Rejected for promotion: verifier_status={row.get('verifier_status')}."
    return f"Ranked below selected {selected.get('candidate_id')} by verifier-first ordering."


def _ranking_counts(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    total = 0
    for row in rows:
        total += 1
        key = str(row.get("evidence_class") or "unknown")
        counts[key] = counts.get(key, 0) + 1
    return {"total": total, "by_evidence_class": dict(sorted(counts.items()))}


def _ranking_markdown(rows: Iterable[Mapping[str, Any]], selected: Mapping[str, Any] | None) -> str:
    lines = [
        "# v1.17 Verifier-First Candidate Ranking",
        "",
        f"Selected candidate: `{selected.get('candidate_id') if selected else 'none'}`",
        "",
        "| Rank | Candidate | Class | Verifier | Post Snap MSE | Reason |",
        "|------|-----------|-------|----------|---------------|--------|",
    ]
    for row in rows:
        reason = row.get("selection_reason") or row.get("rejection_reason")
        lines.append(
            f"| {row.get('rank')} | {row.get('candidate_id')} | {row.get('evidence_class')} | "
            f"{row.get('verifier_status')} | {row.get('post_snap_mse')} | {reason} |"
        )
    lines.append("")
    return "\n".join(lines)


def _sandbox_summary_rows(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((str(row.get("operator_family") or "unknown"), str(row.get("target_family") or "unknown")), []).append(row)
    summary: list[dict[str, Any]] = []
    for (operator_family, target_family), items in sorted(grouped.items()):
        summary.append(
            {
                "group": f"{operator_family}:{target_family}",
                "operator_family": operator_family,
                "target_family": target_family,
                "ranked_rows": len(items),
                "exact_recovery": sum(1 for row in items if row.get("evidence_class") == "exact_recovery"),
                "verified_equivalence": sum(1 for row in items if row.get("evidence_class") == "verified_equivalence"),
                "loss_only": sum(1 for row in items if row.get("evidence_class") == "loss_only"),
                "fallback": sum(1 for row in items if row.get("evidence_class") == "fallback"),
                "original_snap": sum(1 for row in items if row.get("evidence_class") == "original_snap"),
                "negative_control_rows": sum(1 for row in items if not _is_natural(row)),
            }
        )
    return summary


def _is_natural(row: Mapping[str, Any]) -> bool:
    return str(row.get("target_family") or "") != "negative_control"


def _sandbox_markdown(results: Mapping[str, Any]) -> str:
    lines = [
        "# v1.17 Focused Recovery Sandbox",
        "",
        f"Decision: `{results.get('decision')}`",
        "",
        str(results.get("rationale") or ""),
        "",
        f"Broader campaign gate: `{results.get('broader_campaign_gate')}`",
        "",
        "| Group | Rows | Exact | Verified Eq | Loss-Only | Fallback | Original | Negative Controls |",
        "|-------|------|-------|-------------|-----------|----------|----------|-------------------|",
    ]
    for row in results.get("summary_rows", []):
        if not isinstance(row, Mapping):
            continue
        lines.append(
            f"| {row.get('group')} | {row.get('ranked_rows')} | {row.get('exact_recovery')} | "
            f"{row.get('verified_equivalence')} | {row.get('loss_only')} | {row.get('fallback')} | "
            f"{row.get('original_snap')} | {row.get('negative_control_rows')} |"
        )
    lines.append("")
    return "\n".join(lines)


def _mark_required_locks(locks: dict[str, Any], required_inputs: Iterable[tuple[str, Path, str]]) -> None:
    required_ids = {source_id for source_id, _, _ in required_inputs}
    for row in locks.get("inputs", []):
        if isinstance(row, dict):
            row["required"] = row.get("source_id") in required_ids


def _required_source_locks_ok(source_locks: Mapping[str, Any]) -> bool:
    required = [row for row in source_locks.get("inputs", []) if isinstance(row, Mapping) and row.get("required")]
    return bool(required) and all(row.get("status") == "locked" for row in required)


def _source_lock_status(source_locks: Mapping[str, Any], source_id: str) -> str:
    for row in source_locks.get("inputs", []):
        if isinstance(row, Mapping) and row.get("source_id") == source_id:
            return str(row.get("status") or "missing")
    return "missing"


def _audit_check(check_id: str, passed: bool, description: str, details: Mapping[str, Any] | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {"id": check_id, "status": "passed" if passed else "failed", "description": description}
    if details:
        row["details"] = dict(details)
    return row


def _contains_any(text: str, phrases: Iterable[str]) -> bool:
    lower = text.lower()
    return any(phrase.lower() in lower for phrase in phrases)


def _v117_reproduction_commands(
    *,
    snap_diagnostics_dir: Path,
    neighborhoods_dir: Path,
    ranking_dir: Path,
    sandbox_dir: Path,
    output_dir: Path,
    v116_package_dir: Path,
) -> list[str]:
    return [
        _v117_cli_command(
            "geml-v117-snap-diagnostics",
            "--output-dir",
            snap_diagnostics_dir,
            "--campaign-dir",
            DEFAULT_V116_CAMPAIGN_DIR,
            "--overwrite",
        ),
        _v117_cli_command(
            "geml-v117-neighborhoods",
            "--output-dir",
            neighborhoods_dir,
            "--snap-diagnostics-dir",
            snap_diagnostics_dir,
            "--overwrite",
        ),
        _v117_cli_command(
            "geml-v117-rank-candidates",
            "--output-dir",
            ranking_dir,
            "--neighborhoods-dir",
            neighborhoods_dir,
            "--overwrite",
        ),
        _v117_cli_command(
            "geml-v117-sandbox",
            "--output-dir",
            sandbox_dir,
            "--ranking-dir",
            ranking_dir,
            "--overwrite",
        ),
        _v117_cli_command(
            "geml-v117-package",
            "--output-dir",
            output_dir,
            "--snap-diagnostics-dir",
            snap_diagnostics_dir,
            "--neighborhoods-dir",
            neighborhoods_dir,
            "--ranking-dir",
            ranking_dir,
            "--sandbox-dir",
            sandbox_dir,
            "--v116-package-dir",
            v116_package_dir,
            "--overwrite",
        ),
    ]


def _v117_cli_command(command: str, *args: object) -> str:
    parts = ["PYTHONPATH=src", "python", "-m", "eml_symbolic_regression.cli", command, *(str(arg) for arg in args)]
    return shlex.join(parts)


def _v117_final_decision_payload(
    *,
    snap_manifest: Mapping[str, Any],
    snap_diagnostics: Mapping[str, Any],
    snap_seeds: Mapping[str, Any],
    snap_diagnostics_dir: Path,
    neighborhood_manifest: Mapping[str, Any],
    neighborhoods: Mapping[str, Any],
    neighborhoods_dir: Path,
    ranking_manifest: Mapping[str, Any],
    ranked_candidates: Mapping[str, Any],
    ranking_dir: Path,
    sandbox_manifest: Mapping[str, Any],
    sandbox_results: Mapping[str, Any],
    sandbox_dir: Path,
    v116_manifest: Mapping[str, Any],
    v116_package_dir: Path,
    source_locks: Mapping[str, Any],
    commands: list[str],
) -> dict[str, Any]:
    sandbox_gate = str(sandbox_manifest.get("broader_campaign_gate") or sandbox_results.get("broader_campaign_gate") or "block_broader_campaigns")
    sandbox_decision = str(sandbox_manifest.get("decision") or sandbox_results.get("decision") or "no_exact_signal")
    natural_exact = int(sandbox_results.get("natural_exact_recovery_count") or 0)
    negative_control_exact = int(sandbox_results.get("negative_control_exact_recovery_count") or 0)
    exact_signal_found = bool(sandbox_manifest.get("exact_signal_found") or sandbox_results.get("exact_signal_found"))
    if exact_signal_found and natural_exact > 0 and negative_control_exact == 0 and sandbox_gate == "allow_next_campaign_planning":
        decision = "exact_signal_found"
        broader_campaign_gate = "allow_next_campaign_planning"
        rationale = "The focused sandbox found a clean verifier-gated natural exact signal and no negative-control exact recovery."
    elif sandbox_decision == "negative":
        decision = "negative"
        broader_campaign_gate = "block_broader_campaigns"
        rationale = "The focused sandbox reports a negative result under the declared protocol; broader campaigns remain blocked."
    else:
        decision = "still_inconclusive"
        broader_campaign_gate = "block_broader_campaigns"
        rationale = "No clean verifier-gated natural exact signal was found; broader campaigns remain blocked."

    ranked_rows = [row for row in ranked_candidates.get("rows", []) if isinstance(row, Mapping)]
    candidate_counts = ranking_manifest.get("counts") or ranked_candidates.get("counts") or _ranking_counts(ranked_rows)
    next_campaign_allowed = decision == "exact_signal_found" and broader_campaign_gate == "allow_next_campaign_planning"
    return {
        "schema": "eml.v117_final_decision.v1",
        "decision": decision,
        "rationale": rationale,
        "exact_signal_found": exact_signal_found and decision == "exact_signal_found",
        "broader_campaign_gate": broader_campaign_gate,
        "sandbox_broader_campaign_gate": sandbox_gate,
        "sandbox_decision": sandbox_decision,
        "next_campaign_allowed": next_campaign_allowed,
        "natural_exact_recovery_count": natural_exact,
        "negative_control_exact_recovery_count": negative_control_exact,
        "source_locks_ok": _required_source_locks_ok(source_locks),
        "v116_comparison_mode": "additive_reference_only",
        "v116_package": {
            "manifest": str(v116_package_dir / "manifest.json"),
            "decision": v116_manifest.get("decision"),
            "schema": v116_manifest.get("schema"),
            "status": _source_lock_status(source_locks, "v116_package_manifest"),
        },
        "v117_counts": {
            "snap_diagnostic_rows": len(snap_diagnostics.get("rows", []) or []),
            "snap_neighborhood_seed_rows": len(snap_seeds.get("rows", []) or []),
            "neighborhood_candidate_rows": len(neighborhoods.get("rows", []) or []),
            "ranking": candidate_counts,
            "sandbox_summary_rows": len(sandbox_results.get("summary_rows", []) or []),
        },
        "package_contents": {
            "before_v116_package_manifest": str(v116_package_dir / "manifest.json"),
            "snap_diagnostics_manifest": _manifest_output_path(snap_manifest, "manifest_json", snap_diagnostics_dir / "manifest.json"),
            "neighborhood_manifest": _manifest_output_path(neighborhood_manifest, "manifest_json", neighborhoods_dir / "manifest.json"),
            "ranking_manifest": _manifest_output_path(ranking_manifest, "manifest_json", ranking_dir / "manifest.json"),
            "sandbox_manifest": _manifest_output_path(sandbox_manifest, "manifest_json", sandbox_dir / "manifest.json"),
            "failure_taxonomy_reference": {
                "path": str(v116_package_dir / "ablations" / "failure-examples.json"),
                "status": _source_lock_status(source_locks, "v116_failure_taxonomy_reference"),
            },
        },
        "selected_exact_candidates": list(sandbox_results.get("selected_exact_candidates") or []),
        "reproduction_commands": commands,
        "claim_boundary": (
            "v1.17 is an additive snap-first analysis over the intact v1.16 package. "
            "Exact-signal claims require verifier-gated natural exact recovery, loss-only rows remain diagnostic, "
            "and the v1.16 failure taxonomy remains the context for non-recovery rows."
        ),
    }


def _manifest_output_path(manifest: Mapping[str, Any], key: str, fallback: Path) -> str:
    outputs = manifest.get("outputs")
    if isinstance(outputs, Mapping) and outputs.get(key):
        return str(outputs[key])
    return str(fallback)


def _v117_final_decision_markdown(final_decision: Mapping[str, Any]) -> str:
    lines = [
        "# v1.17 Final Decision",
        "",
        f"Decision: `{final_decision.get('decision')}`",
        "",
        str(final_decision.get("rationale") or ""),
        "",
        f"Broader campaign gate: `{final_decision.get('broader_campaign_gate')}`",
        f"Next campaign allowed: `{final_decision.get('next_campaign_allowed')}`",
        "",
        "The v1.16 package remains intact. v1.17 artifacts are additive diagnostics, neighborhoods, rankings, and sandbox results.",
        "",
        "Loss-only rows remain diagnostic. They are not promoted into verifier-owned exact-signal claims.",
        "",
        "The v1.16 failure taxonomy remains the reference context for non-recovery and snap-mismatch rows.",
        "",
        "## Counts",
        "",
        f"- Natural exact recoveries: `{final_decision.get('natural_exact_recovery_count')}`",
        f"- Negative-control exact recoveries: `{final_decision.get('negative_control_exact_recovery_count')}`",
        "",
    ]
    return "\n".join(lines)


def _v117_package_readme(final_decision: Mapping[str, Any]) -> str:
    contents = final_decision.get("package_contents") if isinstance(final_decision.get("package_contents"), Mapping) else {}
    lines = [
        "# v1.17 GEML Evidence Package",
        "",
        "This package is additive: the v1.16 package remains intact and is source-locked as the before-state reference.",
        "",
        f"Final decision: `{final_decision.get('decision')}`",
        f"Broader campaign gate: `{final_decision.get('broader_campaign_gate')}`",
        "",
        "## Before And After",
        "",
        f"- Before: `{contents.get('before_v116_package_manifest')}`",
        f"- Snap diagnostics: `{contents.get('snap_diagnostics_manifest')}`",
        f"- Neighborhood candidates: `{contents.get('neighborhood_manifest')}`",
        f"- Verifier-first ranking: `{contents.get('ranking_manifest')}`",
        f"- Focused sandbox: `{contents.get('sandbox_manifest')}`",
        "",
        "## Claim Boundary",
        "",
        str(final_decision.get("claim_boundary") or ""),
        "",
        "The v1.16 failure taxonomy is preserved as the reference for failure and non-recovery interpretation.",
        "",
        "## Files",
        "",
        "- `final-decision.json` and `final-decision.md` - final gate-controlled decision.",
        "- `claim-audit.json` and `claim-audit.md` - claim language and source-lock audit.",
        "- `source-locks.json` - required and optional input locks plus output locks.",
        "- `reproduction.md` - commands to rebuild the staged v1.17 package.",
        "",
    ]
    return "\n".join(lines)


def _v117_reproduction_markdown(commands: Iterable[str]) -> str:
    lines = ["# v1.17 Reproduction", "", "Run the staged package rebuild in order:", ""]
    for index, command in enumerate(commands, start=1):
        lines.extend([f"{index}.", "", f"```bash\n{command}\n```", ""])
    return "\n".join(lines)


def _v117_claim_audit_markdown(audit: Mapping[str, Any]) -> str:
    lines = [
        "# v1.17 Claim Audit",
        "",
        f"Status: `{audit.get('status')}`",
        "",
        "| Check | Status | Description |",
        "|-------|--------|-------------|",
    ]
    for check in audit.get("checks", []):
        if not isinstance(check, Mapping):
            continue
        lines.append(f"| {check.get('id')} | {check.get('status')} | {check.get('description')} |")
    lines.append("")
    return "\n".join(lines)


def _canonical_json_cell(value: Any) -> str:
    if value in (None, ""):
        return ""
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return value
        return json.dumps(parsed, sort_keys=True, separators=(",", ":"))
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _bool_text(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).lower() in {"true", "1", "yes", "recovered"}


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if math.isfinite(number) else default


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_csv(path: Path, rows: Iterable[Mapping[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: "" if row.get(key) is None else row.get(key) for key in fieldnames})


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _source_locks_payload(items: Iterable[tuple[str, Path, str]]) -> dict[str, Any]:
    locks = _source_locks(items)
    return {
        "schema": "eml.v117_source_locks.v1",
        "generated_at": _now_iso(),
        "inputs": [row for row in locks if row["role"] == "input"],
        "outputs": [row for row in locks if row["role"] == "output"],
    }


def _source_locks(items: Iterable[tuple[str, Path, str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source_id, path, role in items:
        path = Path(path)
        if path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            status = "locked"
            size = path.stat().st_size
        else:
            digest = None
            status = "missing"
            size = 0
        rows.append({"source_id": source_id, "path": str(path), "role": role, "status": status, "sha256": digest, "bytes": size})
    return rows


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
