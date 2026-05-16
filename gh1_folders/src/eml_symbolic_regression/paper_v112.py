"""v1.12 paper draft and supplement artifacts."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from .benchmark import (
    BenchmarkCase,
    BenchmarkSuite,
    DatasetConfig,
    OptimizerBudget,
    aggregate_evidence,
    load_suite,
    run_benchmark_suite,
    write_aggregate_reports,
)
from .compiler import CompilerConfig, UnsupportedExpression, compile_and_validate, diagnose_compile_expression
from .datasets import get_demo
from .verify import verify_candidate


DEFAULT_V112_DRAFT_DIR = Path("artifacts") / "paper" / "v1.11" / "draft"
DEFAULT_V112_REFRESH_DIR = Path("artifacts") / "campaigns" / "v1.12-evidence-refresh"
DEFAULT_V111_PAPER_ROOT = Path("artifacts") / "paper" / "v1.11"
DEFAULT_V112_SUPPLEMENT_DIR = DEFAULT_V111_PAPER_ROOT / "v1.12-supplement"
DEFAULT_V112_TRAINING_DETAIL_DIR = DEFAULT_V112_DRAFT_DIR / "training-detail"
DEFAULT_V111_RAW_HYBRID_DIR = DEFAULT_V111_PAPER_ROOT / "raw-hybrid"
DEFAULT_V111_MOTIF_DIAGNOSTICS = Path("artifacts") / "diagnostics" / "v1.11-paper-ablations" / "motif-depth-deltas.json"
DEFAULT_V111_PROBE_AGGREGATE = Path("artifacts") / "campaigns" / "v1.11-logistic-planck-probes" / "aggregate.json"


@dataclass(frozen=True)
class PaperDraftPaths:
    output_dir: Path
    manifest_json: Path
    abstract_md: Path
    methods_md: Path
    results_md: Path
    limitations_md: Path
    claim_taxonomy_json: Path
    claim_taxonomy_csv: Path
    claim_taxonomy_md: Path

    def as_dict(self) -> dict[str, str]:
        return {key: str(value) for key, value in self.__dict__.items()}


@dataclass(frozen=True)
class PaperRefreshPaths:
    output_dir: Path
    manifest_json: Path
    shallow_suite_json: Path
    shallow_suite_result_json: Path
    shallow_aggregate_json: Path
    shallow_aggregate_md: Path
    shallow_runs_json: Path
    shallow_runs_csv: Path
    shallow_runs_md: Path
    depth_suite_json: Path
    depth_suite_result_json: Path
    depth_aggregate_json: Path
    depth_aggregate_md: Path
    depth_runs_json: Path
    depth_runs_csv: Path
    depth_runs_md: Path
    depth_summary_json: Path
    depth_summary_csv: Path
    depth_summary_md: Path

    def as_dict(self) -> dict[str, str]:
        return {key: str(value) for key, value in self.__dict__.items()}


@dataclass(frozen=True)
class PaperFacingPaths:
    output_dir: Path
    manifest_json: Path
    figure_captions_md: Path
    table_captions_md: Path
    motif_evolution_json: Path
    motif_evolution_csv: Path
    motif_evolution_md: Path
    negative_results_json: Path
    negative_results_csv: Path
    negative_results_md: Path
    pipeline_svg: Path
    pipeline_metadata_json: Path

    def as_dict(self) -> dict[str, str]:
        return {key: str(value) for key, value in self.__dict__.items()}


@dataclass(frozen=True)
class PaperProbePaths:
    output_dir: Path
    manifest_json: Path
    baseline_probe_json: Path
    baseline_probe_csv: Path
    baseline_probe_md: Path
    logistic_probe_json: Path
    logistic_probe_csv: Path
    logistic_probe_md: Path
    logistic_diagnostic_json: Path

    def as_dict(self) -> dict[str, str]:
        return {key: str(value) for key, value in self.__dict__.items()}


@dataclass(frozen=True)
class PaperSupplementPaths:
    output_dir: Path
    manifest_json: Path
    source_locks_json: Path
    claim_audit_json: Path
    claim_audit_md: Path
    reproduction_md: Path

    def as_dict(self) -> dict[str, str]:
        return {key: str(value) for key, value in self.__dict__.items()}


@dataclass(frozen=True)
class PaperTrainingDetailPaths:
    output_dir: Path
    manifest_json: Path
    readme_md: Path
    step_trace_json: Path
    step_trace_csv: Path
    step_trace_md: Path
    run_summary_json: Path
    run_summary_csv: Path
    run_summary_md: Path
    candidate_lifecycle_json: Path
    candidate_lifecycle_csv: Path
    candidate_lifecycle_md: Path
    shallow_loss_svg: Path
    depth_loss_svg: Path

    def as_dict(self) -> dict[str, str]:
        return {key: str(value) for key, value in self.__dict__.items()}


def write_v112_draft(
    *,
    output_dir: Path = DEFAULT_V112_DRAFT_DIR,
    paper_root: Path = DEFAULT_V111_PAPER_ROOT,
    raw_hybrid_dir: Path = DEFAULT_V111_RAW_HYBRID_DIR,
) -> PaperDraftPaths:
    """Write the first paper-shaped draft scaffold from the v1.11 package."""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paper_root = Path(paper_root)
    raw_hybrid_dir = Path(raw_hybrid_dir)
    paths = PaperDraftPaths(
        output_dir=output_dir,
        manifest_json=output_dir / "manifest.json",
        abstract_md=output_dir / "abstract.md",
        methods_md=output_dir / "methods.md",
        results_md=output_dir / "results.md",
        limitations_md=output_dir / "limitations.md",
        claim_taxonomy_json=output_dir / "claim-taxonomy.json",
        claim_taxonomy_csv=output_dir / "claim-taxonomy.csv",
        claim_taxonomy_md=output_dir / "claim-taxonomy.md",
    )

    readiness_path = paper_root / "paper-readiness.md"
    audit_path = paper_root / "claim-audit.json"
    asset_manifest_path = paper_root / "assets" / "manifest.json"
    source_locks_path = paper_root / "source-locks.json"
    claim_ledger_path = raw_hybrid_dir / "claim-ledger.json"
    scientific_table_path = raw_hybrid_dir / "scientific-law-table.json"

    readiness = readiness_path.read_text(encoding="utf-8")
    audit = _read_json(audit_path)
    assets = _read_json(asset_manifest_path)
    claim_ledger = _read_json(claim_ledger_path)
    scientific = _read_json(scientific_table_path)

    taxonomy_rows = claim_taxonomy_rows(claim_ledger)
    _write_json(
        paths.claim_taxonomy_json,
        {"schema": "eml.v112_claim_taxonomy.v1", "generated_at": _now_iso(), "rows": taxonomy_rows},
    )
    _write_csv(paths.claim_taxonomy_csv, taxonomy_rows)
    paths.claim_taxonomy_md.write_text(_claim_taxonomy_markdown(taxonomy_rows), encoding="utf-8")

    paths.abstract_md.write_text(_abstract_markdown(readiness, scientific), encoding="utf-8")
    paths.methods_md.write_text(_methods_markdown(), encoding="utf-8")
    paths.results_md.write_text(_results_markdown(scientific, assets, audit), encoding="utf-8")
    paths.limitations_md.write_text(_limitations_markdown(), encoding="utf-8")

    source_paths = (
        readiness_path,
        audit_path,
        asset_manifest_path,
        source_locks_path,
        claim_ledger_path,
        scientific_table_path,
    )
    manifest = {
        "schema": "eml.v112_paper_draft.v1",
        "generated_at": _now_iso(),
        "output_dir": str(output_dir),
        "outputs": paths.as_dict(),
        "sources": [_source_lock(path.stem.replace("-", "_"), path) for path in source_paths],
        "claim_boundary": "draft scaffold preserves v1.11 regime separation and unsupported logistic/Planck status",
        "reproduction": {
            "command": f"PYTHONPATH=src python -m eml_symbolic_regression.cli paper-draft --output-dir {output_dir}",
        },
    }
    _write_json(paths.manifest_json, manifest)
    return paths


def write_v112_supplement(
    *,
    output_dir: Path = DEFAULT_V112_SUPPLEMENT_DIR,
    draft_dir: Path = DEFAULT_V112_DRAFT_DIR,
    refresh_dir: Path = DEFAULT_V112_REFRESH_DIR,
    overwrite: bool = False,
) -> PaperSupplementPaths:
    """Assemble a source-locked v1.12 supplement for the v1.11 paper package."""

    output_dir = Path(output_dir)
    draft_dir = Path(draft_dir)
    refresh_dir = Path(refresh_dir)
    paths = PaperSupplementPaths(
        output_dir=output_dir,
        manifest_json=output_dir / "manifest.json",
        source_locks_json=output_dir / "source-locks.json",
        claim_audit_json=output_dir / "claim-audit.json",
        claim_audit_md=output_dir / "claim-audit.md",
        reproduction_md=output_dir / "reproduction.md",
    )
    if output_dir.exists() and overwrite:
        shutil.rmtree(output_dir)
    if paths.manifest_json.exists() and not overwrite:
        raise FileExistsError(f"{paths.manifest_json} already exists; pass overwrite=True to refresh")
    output_dir.mkdir(parents=True, exist_ok=True)

    locks = _v112_source_locks(draft_dir=draft_dir, refresh_dir=refresh_dir, output_dir=output_dir)
    audit = audit_v112_supplement(draft_dir=draft_dir, refresh_dir=refresh_dir, source_locks=locks)
    _write_json(paths.claim_audit_json, audit)
    paths.claim_audit_md.write_text(_v112_claim_audit_markdown(audit), encoding="utf-8")
    paths.reproduction_md.write_text(_v112_reproduction_markdown(output_dir), encoding="utf-8")

    source_lock_payload = {
        "schema": "eml.v112_supplement_source_locks.v1",
        "generated_at": _now_iso(),
        "output_dir": str(output_dir),
        "sources": locks,
        "source_count": len(locks),
    }
    _write_json(paths.source_locks_json, source_lock_payload)
    manifest = {
        "schema": "eml.v112_supplement.v1",
        "generated_at": _now_iso(),
        "output_dir": str(output_dir),
        "outputs": paths.as_dict(),
        "source_locks": str(paths.source_locks_json),
        "source_lock_count": len(locks),
        "audit_status": audit["status"],
        "claim_audit": str(paths.claim_audit_json),
        "parent_package": str(DEFAULT_V111_PAPER_ROOT),
        "draft_dir": str(draft_dir),
        "refresh_dir": str(refresh_dir),
        "claim_boundary": "v1.12 supplement source-locks paper additions without changing v1.11 claim denominators",
        "reproduction": {
            "commands_markdown": str(paths.reproduction_md),
            "supplement_command": f"PYTHONPATH=src python -m eml_symbolic_regression.cli paper-supplement --output-dir {output_dir} --overwrite",
        },
    }
    _write_json(paths.manifest_json, manifest)
    return paths


def audit_v112_supplement(*, draft_dir: Path, refresh_dir: Path, source_locks: list[Mapping[str, Any]]) -> dict[str, Any]:
    draft_dir = Path(draft_dir)
    refresh_dir = Path(refresh_dir)
    checks: list[dict[str, Any]] = []

    draft_sections = [draft_dir / name for name in ("abstract.md", "methods.md", "results.md", "limitations.md")]
    _audit_check(
        checks,
        "draft_sections_present",
        all(path.is_file() for path in draft_sections),
        "Draft section skeletons are present.",
        {"paths": [str(path) for path in draft_sections]},
    )

    taxonomy = _read_json(draft_dir / "claim-taxonomy.json")
    taxonomy_classes = {str(row.get("evidence_class")) for row in taxonomy.get("rows", []) if isinstance(row, Mapping)}
    required_classes = {
        "pure_blind",
        "scaffolded",
        "warm_start",
        "same_ast",
        "perturbed_basin",
        "repair_refit",
        "compile_only",
        "unsupported",
        "failed",
    }
    _audit_check(
        checks,
        "claim_taxonomy_complete",
        required_classes <= taxonomy_classes,
        "Claim taxonomy covers all evidence regimes.",
        {"missing": sorted(required_classes - taxonomy_classes), "classes": sorted(taxonomy_classes)},
    )

    facing_manifest = _read_json(draft_dir / "paper-facing-manifest.json")
    facing_counts = facing_manifest.get("counts") if isinstance(facing_manifest.get("counts"), Mapping) else {}
    _audit_check(
        checks,
        "paper_facing_assets_present",
        facing_counts.get("motif_rows", 0) >= 5
        and facing_counts.get("negative_result_rows") == 2
        and (draft_dir / "figures" / "pipeline.svg").is_file()
        and (draft_dir / "figure-captions.md").is_file()
        and (draft_dir / "table-captions.md").is_file(),
        "Paper-facing motif, negative-result, pipeline, and caption artifacts are present.",
        {"counts": facing_counts},
    )

    shallow_rows = _read_json(refresh_dir / "tables" / "shallow-refresh-runs.json").get("rows", [])
    shallow_case_counts: dict[str, int] = {}
    for row in shallow_rows:
        if isinstance(row, Mapping):
            shallow_case_counts[str(row.get("case_id"))] = shallow_case_counts.get(str(row.get("case_id")), 0) + 1
    _audit_check(
        checks,
        "shallow_refresh_counts",
        len(shallow_rows) == 10
        and shallow_case_counts.get("exp-pure-blind-seed-refresh") == 5
        and shallow_case_counts.get("exp-scaffolded-seed-refresh") == 5,
        "Shallow refresh keeps pure-blind and scaffolded seed denominators separate.",
        {"row_count": len(shallow_rows), "case_counts": shallow_case_counts},
    )

    depth_rows = _read_json(refresh_dir / "tables" / "depth-refresh-runs.json").get("rows", [])
    depth_summary_rows = _read_json(refresh_dir / "tables" / "depth-refresh-summary.json").get("rows", [])
    depth_counts: dict[int, int] = {}
    for row in depth_rows:
        if isinstance(row, Mapping) and isinstance(row.get("depth"), int):
            depth_counts[int(row["depth"])] = depth_counts.get(int(row["depth"]), 0) + 1
    _audit_check(
        checks,
        "depth_refresh_counts",
        set(depth_counts) == {2, 3, 4, 5} and all(count >= 2 for count in depth_counts.values()) and len(depth_summary_rows) == 4,
        "Depth refresh covers depths 2 through 5 with at least two rows each.",
        {"depth_counts": depth_counts, "summary_rows": len(depth_summary_rows)},
    )

    negative_rows = _read_json(draft_dir / "tables" / "logistic-planck-negative-results.json").get("rows", [])
    negative_by_formula = {str(row.get("formula_id")): row for row in negative_rows if isinstance(row, Mapping)}
    _audit_check(
        checks,
        "logistic_planck_negative_rows_not_promoted",
        all(
            negative_by_formula.get(formula, {}).get("promotion") == "no"
            and negative_by_formula.get(formula, {}).get("compile_support") == "unsupported"
            for formula in ("logistic", "planck")
        ),
        "Logistic and Planck negative rows remain unsupported and unpromoted.",
        {"rows": negative_by_formula},
    )

    baseline_rows = _read_json(draft_dir / "tables" / "conventional-symbolic-baseline-probe.json").get("rows", [])
    logistic_probe_rows = _read_json(draft_dir / "tables" / "logistic-strict-support-probe.json").get("rows", [])
    baseline = baseline_rows[0] if baseline_rows and isinstance(baseline_rows[0], Mapping) else {}
    logistic_probe = logistic_probe_rows[0] if logistic_probe_rows and isinstance(logistic_probe_rows[0], Mapping) else {}
    _audit_check(
        checks,
        "bounded_probe_status_visible",
        baseline.get("status") in {"completed", "deferred", "unavailable"}
        and baseline.get("diagnostic_only") is True
        and logistic_probe.get("strict_gate") == 13
        and logistic_probe.get("promotion") == "no",
        "Bounded baseline and logistic strict-support probe outcomes are visible and non-promotional.",
        {"baseline": baseline, "logistic_probe": logistic_probe},
    )

    training_detail_manifest = draft_dir / "training-detail" / "manifest.json"
    training_detail = _read_json(training_detail_manifest) if training_detail_manifest.is_file() else {}
    training_counts = training_detail.get("counts") if isinstance(training_detail.get("counts"), Mapping) else {}
    _audit_check(
        checks,
        "training_detail_artifacts_present",
        training_counts.get("step_trace_rows", 0) > 0
        and training_counts.get("run_summary_rows", 0) > 0
        and training_counts.get("candidate_lifecycle_rows", 0) > 0
        and (draft_dir / "training-detail" / "figures" / "shallow-loss-curves.svg").is_file()
        and (draft_dir / "training-detail" / "figures" / "depth-loss-curves.svg").is_file(),
        "Training-detail artifacts expose per-step losses, run summaries, candidate lifecycle rows, and loss-curve figures.",
        {"counts": training_counts},
    )

    roles = {str(row.get("role")) for row in source_locks if isinstance(row, Mapping)}
    required_roles = {"v112_draft", "v112_paper_facing", "v112_evidence_refresh", "v112_bounded_probe"}
    _audit_check(
        checks,
        "source_locks_cover_v112_artifact_families",
        required_roles <= roles and all(row.get("sha256") and row.get("source_path") for row in source_locks),
        "Source locks cover draft, paper-facing, evidence-refresh, and bounded-probe artifact families.",
        {"missing_roles": sorted(required_roles - roles), "source_lock_count": len(source_locks)},
    )

    status = "passed" if all(check["status"] == "passed" for check in checks) else "failed"
    return {
        "schema": "eml.v112_claim_audit.v1",
        "generated_at": _now_iso(),
        "status": status,
        "checks": checks,
        "summary": {
            "passed": sum(1 for check in checks if check["status"] == "passed"),
            "failed": sum(1 for check in checks if check["status"] != "passed"),
        },
    }


def write_v112_training_detail_assets(
    *,
    output_dir: Path = DEFAULT_V112_TRAINING_DETAIL_DIR,
    refresh_dir: Path = DEFAULT_V112_REFRESH_DIR,
) -> PaperTrainingDetailPaths:
    """Write paper-facing per-step training traces, lifecycle tables, and loss-curve figures."""

    output_dir = Path(output_dir)
    refresh_dir = Path(refresh_dir)
    tables_dir = output_dir / "tables"
    figures_dir = output_dir / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    paths = PaperTrainingDetailPaths(
        output_dir=output_dir,
        manifest_json=output_dir / "manifest.json",
        readme_md=output_dir / "README.md",
        step_trace_json=tables_dir / "training-step-traces.json",
        step_trace_csv=tables_dir / "training-step-traces.csv",
        step_trace_md=tables_dir / "training-step-traces.md",
        run_summary_json=tables_dir / "training-run-summaries.json",
        run_summary_csv=tables_dir / "training-run-summaries.csv",
        run_summary_md=tables_dir / "training-run-summaries.md",
        candidate_lifecycle_json=tables_dir / "candidate-lifecycle.json",
        candidate_lifecycle_csv=tables_dir / "candidate-lifecycle.csv",
        candidate_lifecycle_md=tables_dir / "candidate-lifecycle.md",
        shallow_loss_svg=figures_dir / "shallow-loss-curves.svg",
        depth_loss_svg=figures_dir / "depth-loss-curves.svg",
    )

    run_payloads = _v112_refresh_run_payloads(refresh_dir)
    step_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    candidate_rows: list[dict[str, Any]] = []
    for source, artifact_path, payload in run_payloads:
        rows, summaries, candidates = training_detail_rows_from_payload(payload, source=source, artifact_path=artifact_path)
        step_rows.extend(rows)
        summary_rows.extend(summaries)
        candidate_rows.extend(candidates)

    _write_table(paths.step_trace_json, paths.step_trace_csv, paths.step_trace_md, "Training Step Traces", step_rows)
    _write_table(paths.run_summary_json, paths.run_summary_csv, paths.run_summary_md, "Training Run Summaries", summary_rows)
    _write_table(paths.candidate_lifecycle_json, paths.candidate_lifecycle_csv, paths.candidate_lifecycle_md, "Candidate Lifecycle", candidate_rows)
    paths.shallow_loss_svg.write_text(
        _training_loss_svg([row for row in step_rows if row.get("source") == "shallow"], "v1.12 shallow refresh loss traces"),
        encoding="utf-8",
    )
    paths.depth_loss_svg.write_text(
        _training_loss_svg([row for row in step_rows if row.get("source") == "depth"], "v1.12 depth refresh loss traces"),
        encoding="utf-8",
    )
    paths.readme_md.write_text(_training_detail_readme(paths, len(run_payloads), step_rows, summary_rows, candidate_rows), encoding="utf-8")

    source_paths = [Path(path) for _, path, _ in run_payloads]
    for name in ("manifest.json", "shallow-aggregate.json", "depth-aggregate.json"):
        path = refresh_dir / name
        if path.is_file():
            source_paths.append(path)
    manifest = {
        "schema": "eml.v112_training_detail_assets.v1",
        "generated_at": _now_iso(),
        "output_dir": str(output_dir),
        "outputs": paths.as_dict(),
        "counts": {
            "run_payloads": len(run_payloads),
            "step_trace_rows": len(step_rows),
            "run_summary_rows": len(summary_rows),
            "candidate_lifecycle_rows": len(candidate_rows),
            "traced_runs": len({row.get("run_id") for row in step_rows}),
        },
        "sources": [_source_lock(f"run_{index:03d}", path) for index, path in enumerate(dict.fromkeys(source_paths))],
        "claim_boundary": "training-detail figures show optimizer dynamics and candidate lifecycle; verifier status still owns recovery claims",
        "reproduction": {
            "command": (
                "PYTHONPATH=src python -m eml_symbolic_regression.cli paper-training-detail "
                f"--output-dir {output_dir} --refresh-dir {refresh_dir}"
            ),
        },
    }
    _write_json(paths.manifest_json, manifest)
    return paths


def training_detail_rows_from_payload(
    payload: Mapping[str, Any],
    *,
    source: str,
    artifact_path: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    run = payload.get("run") if isinstance(payload.get("run"), Mapping) else {}
    budget = payload.get("budget") if isinstance(payload.get("budget"), Mapping) else {}
    metrics = payload.get("metrics") if isinstance(payload.get("metrics"), Mapping) else {}
    manifest = _training_manifest_from_payload(payload)
    if not manifest:
        return [], [], []

    run_context = {
        "source": source,
        "run_id": run.get("run_id"),
        "suite_id": run.get("suite_id"),
        "case_id": run.get("case_id"),
        "formula": run.get("formula"),
        "start_mode": run.get("start_mode"),
        "seed": run.get("seed"),
        "depth": budget.get("depth"),
        "steps": budget.get("steps"),
        "hardening_steps": budget.get("hardening_steps"),
        "training_mode": payload.get("training_mode"),
        "status": payload.get("status"),
        "claim_status": payload.get("claim_status"),
        "evidence_class": payload.get("evidence_class"),
        "verifier_status": metrics.get("verifier_status"),
        "artifact_path": str(artifact_path),
    }

    best_restart = manifest.get("best_restart") if isinstance(manifest.get("best_restart"), Mapping) else {}
    best_attempt_index = best_restart.get("restart")
    step_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    for restart in manifest.get("restarts", []):
        if not isinstance(restart, Mapping):
            continue
        attempt_index = restart.get("restart")
        is_best = attempt_index == best_attempt_index
        summary = restart.get("loss_summary") if isinstance(restart.get("loss_summary"), Mapping) else {}
        summary_rows.append(
            {
                **run_context,
                "attempt_index": attempt_index,
                "attempt_kind": restart.get("attempt_kind"),
                "random_restart": restart.get("random_restart"),
                "attempt_seed": restart.get("seed"),
                "is_best_restart": is_best,
                "steps_recorded": summary.get("steps_recorded"),
                "fit_steps_recorded": summary.get("fit_steps_recorded"),
                "hardening_steps_recorded": summary.get("hardening_steps_recorded"),
                "first_fit_loss": summary.get("first_fit_loss"),
                "last_fit_loss": summary.get("last_fit_loss"),
                "best_fit_loss": summary.get("best_fit_loss"),
                "best_global_step": summary.get("best_global_step"),
                "loss_reduction": summary.get("loss_reduction"),
                "loss_reduction_ratio": summary.get("loss_reduction_ratio"),
                "final_nan_count": _nested_mapping(restart, ("final_anomalies", "nan_count")),
                "final_inf_count": _nested_mapping(restart, ("final_anomalies", "inf_count")),
                "final_clamp_count": _nested_mapping(restart, ("final_anomalies", "clamp_count")),
                "candidate_ids": restart.get("candidate_ids"),
            }
        )
        for trace in restart.get("trace", []):
            if not isinstance(trace, Mapping):
                continue
            step_rows.append(
                {
                    **run_context,
                    "attempt_index": attempt_index,
                    "attempt_kind": restart.get("attempt_kind"),
                    "random_restart": restart.get("random_restart"),
                    "attempt_seed": restart.get("seed"),
                    "is_best_restart": is_best,
                    "phase": trace.get("phase"),
                    "step": trace.get("step"),
                    "global_step": trace.get("global_step"),
                    "temperature": trace.get("temperature"),
                    "operator_family": trace.get("operator_family"),
                    "fit_loss": trace.get("fit_loss"),
                    "objective_loss": trace.get("objective_loss"),
                    "entropy": trace.get("entropy"),
                    "entropy_loss": trace.get("entropy_loss"),
                    "expected_child_use": trace.get("expected_child_use"),
                    "size_loss": trace.get("size_loss"),
                    "anomaly_penalty": trace.get("anomaly_penalty"),
                    "nan_count": trace.get("nan_count"),
                    "inf_count": trace.get("inf_count"),
                    "clamp_count": trace.get("clamp_count"),
                    "max_abs": trace.get("max_abs"),
                    "max_exp_real": trace.get("max_exp_real"),
                    "exp_overflow_count": trace.get("exp_overflow_count"),
                    "log_branch_cut_count": trace.get("log_branch_cut_count"),
                    "log_non_finite_input_count": trace.get("log_non_finite_input_count"),
                    "by_node": trace.get("by_node"),
                }
            )

    selection = manifest.get("selection") if isinstance(manifest.get("selection"), Mapping) else {}
    candidates: list[dict[str, Any]] = []
    for candidate in manifest.get("candidates", []):
        if not isinstance(candidate, Mapping):
            continue
        candidate_metrics = candidate.get("selection_metrics") if isinstance(candidate.get("selection_metrics"), Mapping) else {}
        candidates.append(
            {
                **run_context,
                "candidate_id": candidate.get("candidate_id"),
                "candidate_source": candidate.get("source"),
                "attempt_index": candidate.get("attempt_index"),
                "checkpoint_index": candidate.get("checkpoint_index"),
                "hardening_step": candidate.get("hardening_step"),
                "global_step": candidate.get("global_step"),
                "temperature": candidate.get("temperature"),
                "best_fit_loss": candidate.get("best_fit_loss"),
                "post_snap_loss": candidate.get("post_snap_loss"),
                "active_slot_count": candidate.get("active_slot_count"),
                "low_margin_slot_count": candidate.get("low_margin_slot_count"),
                "snap_min_margin": _nested_mapping(candidate, ("snap", "min_margin")),
                "snap_active_node_count": _nested_mapping(candidate, ("snap", "active_node_count")),
                "verifier_status": candidate_metrics.get("verifier_status"),
                "heldout_max_abs_error": candidate_metrics.get("heldout_max_abs_error"),
                "extrapolation_max_abs_error": candidate_metrics.get("extrapolation_max_abs_error"),
                "high_precision_max_error": candidate_metrics.get("high_precision_max_error"),
                "is_selected": candidate.get("candidate_id") == selection.get("selected_candidate_id"),
                "is_fallback": candidate.get("candidate_id") == selection.get("fallback_candidate_id"),
            }
        )
    return step_rows, summary_rows, candidates


def _training_manifest_from_payload(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    trained = payload.get("trained_eml_candidate")
    if isinstance(trained, Mapping):
        return trained
    warm = payload.get("warm_start_eml")
    if isinstance(warm, Mapping) and isinstance(warm.get("optimizer"), Mapping):
        return warm["optimizer"]
    perturbed = payload.get("perturbed_true_tree")
    if isinstance(perturbed, Mapping) and isinstance(perturbed.get("optimizer"), Mapping):
        return perturbed["optimizer"]
    return {}


def _v112_refresh_run_payloads(refresh_dir: Path) -> list[tuple[str, Path, Mapping[str, Any]]]:
    payloads: list[tuple[str, Path, Mapping[str, Any]]] = []
    seen: set[Path] = set()
    for source, aggregate_name in (("shallow", "shallow-aggregate.json"), ("depth", "depth-aggregate.json")):
        aggregate_path = refresh_dir / aggregate_name
        if not aggregate_path.is_file():
            continue
        aggregate = _read_json(aggregate_path)
        for run in aggregate.get("runs", []):
            if not isinstance(run, Mapping) or not run.get("artifact_path"):
                continue
            artifact_path = Path(str(run["artifact_path"]))
            if artifact_path in seen or not artifact_path.is_file():
                continue
            seen.add(artifact_path)
            payloads.append((source, artifact_path, _read_json(artifact_path)))
    return payloads


def _training_detail_readme(
    paths: PaperTrainingDetailPaths,
    run_count: int,
    step_rows: list[Mapping[str, Any]],
    summary_rows: list[Mapping[str, Any]],
    candidate_rows: list[Mapping[str, Any]],
) -> str:
    return "\n".join(
        [
            "# v1.12 Training Detail Artifacts",
            "",
            f"Runs inspected: {run_count}.",
            f"Step-trace rows: {len(step_rows)}.",
            f"Run-summary rows: {len(summary_rows)}.",
            f"Candidate-lifecycle rows: {len(candidate_rows)}.",
            "",
            "## Tables",
            "",
            f"- `{paths.step_trace_csv}`: per-step fit loss, objective loss, entropy, size penalty, temperature, operator family, and anomaly counters.",
            f"- `{paths.run_summary_csv}`: per-restart loss summaries and final anomaly totals.",
            f"- `{paths.candidate_lifecycle_csv}`: exact candidate pool lifecycle, snap margins, post-snap loss, verifier status, and selected/fallback flags.",
            "",
            "## Figures",
            "",
            f"- `{paths.shallow_loss_svg}`: shallow refresh loss curves.",
            f"- `{paths.depth_loss_svg}`: depth-refresh loss curves.",
            "",
            "## Claim Boundary",
            "",
            "These artifacts illustrate optimizer dynamics and candidate selection. Recovery claims still come only from verifier status, not from loss curves alone.",
            "",
        ]
    )


def _training_loss_svg(rows: list[Mapping[str, Any]], title: str) -> str:
    plot_rows = [
        row
        for row in rows
        if row.get("is_best_restart") is True and row.get("phase") == "fit" and _number_or_none(row.get("fit_loss")) is not None
    ]
    width, height = 1080, 520
    left, top, right, bottom = 70, 70, 30, 70
    plot_w = width - left - right
    plot_h = height - top - bottom
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>.title{font:700 22px Arial,sans-serif;fill:#17202a}.axis{font:12px Arial,sans-serif;fill:#34495e}.label{font:11px Arial,sans-serif;fill:#34495e}.grid{stroke:#d8dee4;stroke-width:1}.curve{fill:none;stroke-width:2;opacity:.88}.note{font:12px Arial,sans-serif;fill:#5d6d7e}</style>",
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff"/>',
        f'<text x="{left}" y="36" class="title">{_svg_text(title)}</text>',
        f'<text x="{left}" y="56" class="note">Best restart per run; y-axis is log10(fit loss). Loss curves illustrate optimizer dynamics only.</text>',
    ]
    if not plot_rows:
        parts.append(f'<text x="{left}" y="{top + 40}" class="axis">No traced fit steps available.</text></svg>')
        return "\n".join(parts)

    max_step = max(int(row.get("global_step") or 0) for row in plot_rows) or 1
    losses = [_number_or_none(row.get("fit_loss")) for row in plot_rows]
    log_losses = [math.log10(max(float(value), 1e-300)) for value in losses if value is not None and np.isfinite(float(value))]
    min_y = min(log_losses)
    max_y = max(log_losses)
    if min_y == max_y:
        min_y -= 1.0
        max_y += 1.0

    for index in range(6):
        y = top + plot_h * index / 5
        x = left + plot_w * index / 5
        parts.append(f'<line x1="{left}" y1="{y:.2f}" x2="{left + plot_w}" y2="{y:.2f}" class="grid"/>')
        parts.append(f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{top + plot_h}" class="grid"/>')
    parts.append(f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" stroke="#34495e" stroke-width="1.5"/>')
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" stroke="#34495e" stroke-width="1.5"/>')
    parts.append(f'<text x="{left + plot_w / 2 - 25:.2f}" y="{height - 24}" class="axis">step</text>')
    parts.append(f'<text x="16" y="{top + plot_h / 2:.2f}" transform="rotate(-90 16 {top + plot_h / 2:.2f})" class="axis">log10 loss</text>')

    colors = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#8c564b", "#17becf", "#bcbd22", "#ff7f0e", "#7f7f7f", "#e377c2"]
    grouped: dict[str, list[Mapping[str, Any]]] = {}
    for row in plot_rows:
        grouped.setdefault(str(row.get("run_id")), []).append(row)
    for index, (run_id, items) in enumerate(sorted(grouped.items())):
        points = []
        for row in sorted(items, key=lambda item: int(item.get("global_step") or 0)):
            loss = _number_or_none(row.get("fit_loss"))
            if loss is None:
                continue
            x = left + (int(row.get("global_step") or 0) / max_step) * plot_w
            log_loss = math.log10(max(float(loss), 1e-300))
            y = top + ((max_y - log_loss) / (max_y - min_y)) * plot_h
            points.append(f"{x:.2f},{y:.2f}")
        if len(points) >= 2:
            color = colors[index % len(colors)]
            parts.append(f'<polyline points="{" ".join(points)}" class="curve" stroke="{color}"/>')
    parts.append(f'<text x="{left}" y="{height - 45}" class="note">Traced runs: {len(grouped)}. Full data: training-step-traces.csv/json.</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def _number_or_none(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if np.isfinite(number) else None


def _svg_text(value: Any) -> str:
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def write_v112_bounded_probes(
    *,
    output_dir: Path = DEFAULT_V112_DRAFT_DIR,
    baseline_modules: tuple[str, ...] = ("pysr", "gplearn", "pyoperon", "karoo_gp"),
    logistic_points: int = 24,
    logistic_seed: int = 0,
) -> PaperProbePaths:
    """Write bounded baseline status and logistic strict-support probe artifacts."""

    output_dir = Path(output_dir)
    tables_dir = output_dir / "tables"
    output_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)
    paths = PaperProbePaths(
        output_dir=output_dir,
        manifest_json=output_dir / "bounded-probes-manifest.json",
        baseline_probe_json=tables_dir / "conventional-symbolic-baseline-probe.json",
        baseline_probe_csv=tables_dir / "conventional-symbolic-baseline-probe.csv",
        baseline_probe_md=tables_dir / "conventional-symbolic-baseline-probe.md",
        logistic_probe_json=tables_dir / "logistic-strict-support-probe.json",
        logistic_probe_csv=tables_dir / "logistic-strict-support-probe.csv",
        logistic_probe_md=tables_dir / "logistic-strict-support-probe.md",
        logistic_diagnostic_json=tables_dir / "logistic-strict-support-diagnostic.json",
    )

    baseline_rows = conventional_symbolic_baseline_probe_rows(baseline_modules)
    logistic_rows, logistic_diagnostic = logistic_strict_support_probe_rows(points=logistic_points, seed=logistic_seed)
    _write_table(
        paths.baseline_probe_json,
        paths.baseline_probe_csv,
        paths.baseline_probe_md,
        "Conventional Symbolic Baseline Probe",
        baseline_rows,
    )
    _write_table(
        paths.logistic_probe_json,
        paths.logistic_probe_csv,
        paths.logistic_probe_md,
        "Logistic Strict-Support Probe",
        logistic_rows,
    )
    _write_json(paths.logistic_diagnostic_json, logistic_diagnostic)

    manifest = {
        "schema": "eml.v112_bounded_probes.v1",
        "generated_at": _now_iso(),
        "output_dir": str(output_dir),
        "outputs": paths.as_dict(),
        "counts": {
            "baseline_rows": len(baseline_rows),
            "logistic_probe_rows": len(logistic_rows),
        },
        "statuses": {
            "baseline": baseline_rows[0].get("status") if baseline_rows else "missing",
            "logistic_promotion": logistic_rows[0].get("promotion") if logistic_rows else "missing",
            "logistic_strict_status": logistic_rows[0].get("strict_status") if logistic_rows else "missing",
        },
        "source_locks": [
            _source_lock("baseline_probe", paths.baseline_probe_json),
            _source_lock("logistic_probe", paths.logistic_probe_json),
            _source_lock("logistic_diagnostic", paths.logistic_diagnostic_json),
        ],
        "claim_boundary": "bounded probes are diagnostic-only unless strict support and verifier recovery both pass",
        "reproduction": {
            "command": f"PYTHONPATH=src python -m eml_symbolic_regression.cli paper-probes --output-dir {output_dir}",
        },
    }
    _write_json(paths.manifest_json, manifest)
    return paths


def conventional_symbolic_baseline_probe_rows(baseline_modules: tuple[str, ...] = ("pysr", "gplearn", "pyoperon", "karoo_gp")) -> list[dict[str, Any]]:
    detected = [module for module in baseline_modules if importlib.util.find_spec(module) is not None]
    if not detected:
        return [
            {
                "baseline_id": "conventional_symbolic_regression",
                "checked_modules": list(baseline_modules),
                "detected_modules": [],
                "status": "unavailable",
                "formula": "not_run",
                "reason": "no_local_symbolic_regression_package",
                "limitation": "PySR, gplearn, PyOperon, and karoo-gp were not importable locally; no dependency installation was attempted in this bounded phase.",
                "diagnostic_only": True,
                "denominator_policy": "excluded from EML recovery denominators",
                "claim_boundary": "absence of a conventional SR comparator is reported as a limitation, not hidden",
            }
        ]

    return [
        {
            "baseline_id": "conventional_symbolic_regression",
            "checked_modules": list(baseline_modules),
            "detected_modules": detected,
            "status": "deferred",
            "formula": "not_run",
            "reason": "local_package_detected_but_bounded_phase_did_not_launch_external_sr_runtime",
            "limitation": "A symbolic-regression package is importable, but this phase avoids unbounded tuning or Julia/runtime setup; run a separate matched-budget baseline phase before making comparator claims.",
            "diagnostic_only": True,
            "denominator_policy": "excluded from EML recovery denominators",
            "claim_boundary": "available baseline tooling does not enter EML recovery counts without a source-locked matched-budget run",
        }
    ]


def logistic_strict_support_probe_rows(
    *,
    points: int = 24,
    seed: int = 0,
    strict_gate: int = 13,
    max_nodes: int = 256,
    tolerance: float = 1e-8,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    spec = get_demo("logistic")
    splits = spec.make_splits(points=points, seed=seed)
    validation_inputs = {spec.variable: np.concatenate([split.inputs[spec.variable] for split in splits]).astype(np.complex128)}
    expression = spec.candidate.to_sympy()
    config = CompilerConfig(variables=(spec.variable,), max_depth=strict_gate, max_nodes=max_nodes, validation_tolerance=tolerance)
    diagnostic = diagnose_compile_expression(expression, config, validation_inputs)

    verifier_status = "not_run_strict_compile_failed"
    verifier_reason = "strict compile did not produce an exact EML candidate"
    promotion = "no"
    promotion_reason = "strict support and verifier recovery did not both pass"
    strict_metadata: Mapping[str, Any] = {}
    strict_validation: Mapping[str, Any] = {}
    if diagnostic.get("status") == "compiled":
        strict_payload = diagnostic.get("strict") if isinstance(diagnostic.get("strict"), Mapping) else {}
        strict_metadata = strict_payload.get("metadata") if isinstance(strict_payload.get("metadata"), Mapping) else {}
        strict_validation = strict_payload.get("validation") if isinstance(strict_payload.get("validation"), Mapping) else {}
        try:
            compiled = compile_and_validate(expression, config, validation_inputs)
            report = verify_candidate(compiled.expression, splits, tolerance=tolerance)
            verifier_status = report.status
            verifier_reason = report.reason
            if verifier_status == "recovered":
                promotion = "yes"
                promotion_reason = "strict compile and verifier recovery both passed"
        except UnsupportedExpression as exc:
            verifier_status = "not_run_strict_compile_failed"
            verifier_reason = f"{exc.reason}: {exc.detail}"

    strict_failure = diagnostic.get("strict") if isinstance(diagnostic.get("strict"), Mapping) else {}
    relaxed = diagnostic.get("relaxed") if isinstance(diagnostic.get("relaxed"), Mapping) else {}
    relaxed_metadata = relaxed.get("metadata") if isinstance(relaxed.get("metadata"), Mapping) else {}
    relaxed_validation = relaxed.get("validation") if isinstance(relaxed.get("validation"), Mapping) else {}
    macro = relaxed_metadata.get("macro_diagnostics") if isinstance(relaxed_metadata.get("macro_diagnostics"), Mapping) else {}
    relaxed_depth = relaxed_metadata.get("depth")
    depth_gap = relaxed_depth - strict_gate if isinstance(relaxed_depth, int) else None
    row = {
        "source": "v1.12-logistic-strict-support-probe",
        "formula_id": spec.name,
        "symbolic_expression": str(expression),
        "strict_gate": strict_gate,
        "max_nodes": max_nodes,
        "points": points,
        "seed": seed,
        "strict_status": diagnostic.get("status"),
        "strict_reason": strict_failure.get("reason") if strict_failure else "compiled",
        "strict_detail": strict_failure.get("detail") if strict_failure else "",
        "strict_depth": strict_metadata.get("depth"),
        "strict_node_count": strict_metadata.get("node_count"),
        "strict_validation_status": strict_validation.get("reason"),
        "relaxed_depth": relaxed_depth,
        "relaxed_node_count": relaxed_metadata.get("node_count"),
        "relaxed_macro_hits": macro.get("hits", []),
        "relaxed_baseline_depth": macro.get("baseline_depth"),
        "relaxed_depth_delta": macro.get("depth_delta"),
        "depth_gap_to_strict_gate": depth_gap,
        "relaxed_validation_status": relaxed_validation.get("reason"),
        "relaxed_validation_passed": relaxed_validation.get("passed"),
        "verifier_status": verifier_status,
        "verifier_reason": verifier_reason,
        "promotion": promotion,
        "promotion_reason": promotion_reason,
        "claim_boundary": "strict gate remains 13; relaxed depth improvement is diagnostic and not recovery promotion",
    }
    diagnostic_payload = {
        "schema": "eml.v112_logistic_strict_support_diagnostic.v1",
        "generated_at": _now_iso(),
        "config": {
            "strict_gate": strict_gate,
            "max_nodes": max_nodes,
            "points": points,
            "seed": seed,
            "tolerance": tolerance,
        },
        "formula": spec.formula_provenance(),
        "diagnostic": diagnostic,
        "row": row,
    }
    return [row], diagnostic_payload


def write_v112_paper_facing_assets(
    *,
    output_dir: Path = DEFAULT_V112_DRAFT_DIR,
    motif_diagnostics: Path = DEFAULT_V111_MOTIF_DIAGNOSTICS,
    scientific_law_table: Path = DEFAULT_V111_RAW_HYBRID_DIR / "scientific-law-table.json",
    probe_aggregate: Path = DEFAULT_V111_PROBE_AGGREGATE,
    refresh_manifest: Path = DEFAULT_V112_REFRESH_DIR / "manifest.json",
) -> PaperFacingPaths:
    """Write v1.12 paper-facing captions, tables, and pipeline figure."""

    output_dir = Path(output_dir)
    tables_dir = output_dir / "tables"
    figures_dir = output_dir / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    paths = PaperFacingPaths(
        output_dir=output_dir,
        manifest_json=output_dir / "paper-facing-manifest.json",
        figure_captions_md=output_dir / "figure-captions.md",
        table_captions_md=output_dir / "table-captions.md",
        motif_evolution_json=tables_dir / "motif-library-evolution.json",
        motif_evolution_csv=tables_dir / "motif-library-evolution.csv",
        motif_evolution_md=tables_dir / "motif-library-evolution.md",
        negative_results_json=tables_dir / "logistic-planck-negative-results.json",
        negative_results_csv=tables_dir / "logistic-planck-negative-results.csv",
        negative_results_md=tables_dir / "logistic-planck-negative-results.md",
        pipeline_svg=figures_dir / "pipeline.svg",
        pipeline_metadata_json=figures_dir / "pipeline.metadata.json",
    )

    motif_payload = _read_json(Path(motif_diagnostics))
    scientific_payload = _read_json(Path(scientific_law_table))
    probe_payload = _read_json(Path(probe_aggregate))

    motif_rows = motif_library_evolution_rows(motif_payload)
    negative_rows = logistic_planck_negative_result_rows(scientific_payload, motif_payload, probe_payload)
    _write_table(paths.motif_evolution_json, paths.motif_evolution_csv, paths.motif_evolution_md, "Motif Library Evolution", motif_rows)
    _write_table(
        paths.negative_results_json,
        paths.negative_results_csv,
        paths.negative_results_md,
        "Logistic and Planck Negative Results",
        negative_rows,
    )

    paths.pipeline_svg.write_text(_pipeline_svg(), encoding="utf-8")
    _write_json(
        paths.pipeline_metadata_json,
        {
            "schema": "eml.v112_pipeline_figure_metadata.v1",
            "figure_id": "pipeline",
            "title": "Verifier-Gated Hybrid EML Pipeline",
            "source_tables": {
                "claim_taxonomy": str(output_dir / "claim-taxonomy.json"),
                "shallow_refresh": str(DEFAULT_V112_REFRESH_DIR / "tables" / "shallow-refresh-runs.json"),
                "depth_refresh": str(DEFAULT_V112_REFRESH_DIR / "tables" / "depth-refresh-summary.json"),
            },
            "claim_boundary": "pipeline diagram shows stages, not a single pure-blind recovery denominator",
        },
    )
    paths.figure_captions_md.write_text(_figure_captions_markdown(paths), encoding="utf-8")
    paths.table_captions_md.write_text(_table_captions_markdown(paths), encoding="utf-8")

    source_paths = [Path(motif_diagnostics), Path(scientific_law_table), Path(probe_aggregate)]
    if Path(refresh_manifest).is_file():
        source_paths.append(Path(refresh_manifest))
    manifest = {
        "schema": "eml.v112_paper_facing_assets.v1",
        "generated_at": _now_iso(),
        "output_dir": str(output_dir),
        "outputs": paths.as_dict(),
        "counts": {
            "motif_rows": len(motif_rows),
            "negative_result_rows": len(negative_rows),
            "figures": 1,
            "caption_files": 2,
        },
        "sources": [_source_lock(path.stem.replace("-", "_"), path) for path in source_paths],
        "claim_boundary": "paper-facing assets preserve unsupported diagnostic rows and regime separation",
        "reproduction": {
            "command": f"PYTHONPATH=src python -m eml_symbolic_regression.cli paper-figures --output-dir {output_dir}",
        },
    }
    _write_json(paths.manifest_json, manifest)
    return paths


def motif_library_evolution_rows(motif_payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    wanted = {"Logistic diagnostic", "Planck diagnostic", "Shockley", "Arrhenius", "Michaelis-Menten"}
    rows: list[dict[str, Any]] = []
    for row in motif_payload.get("rows", []):
        if not isinstance(row, Mapping) or row.get("law") not in wanted:
            continue
        law = str(row.get("law"))
        depth_note = ""
        if law == "Planck diagnostic":
            depth_note = "v1.11 diagnostic framing reports 24 -> 14; older relaxed package text also referenced improvement below relaxed depth 20."
        rows.append(
            {
                "law": law,
                "source_expression": row.get("source_expression"),
                "baseline_depth": row.get("baseline_depth"),
                "motif_depth": row.get("motif_depth"),
                "depth_delta": row.get("depth_delta"),
                "baseline_nodes": row.get("baseline_nodes"),
                "motif_nodes": row.get("motif_nodes"),
                "node_delta": row.get("node_delta"),
                "macro_hits": row.get("macro_hits"),
                "strict_support": row.get("strict_support"),
                "compile_support": row.get("compile_support"),
                "validation_status": row.get("validation_status"),
                "validation_passed": row.get("validation_passed"),
                "artifact_path": row.get("artifact_path"),
                "depth_convention_note": depth_note,
                "paper_claim": _motif_paper_claim(row),
            }
        )
    return sorted(rows, key=lambda item: str(item["law"]))


def logistic_planck_negative_result_rows(
    scientific_payload: Mapping[str, Any],
    motif_payload: Mapping[str, Any],
    probe_payload: Mapping[str, Any],
) -> list[dict[str, Any]]:
    motif_by_law = {str(row.get("law")): row for row in motif_payload.get("rows", []) if isinstance(row, Mapping)}
    scientific_by_law = {str(row.get("law")): row for row in scientific_payload.get("rows", []) if isinstance(row, Mapping)}
    runs_by_formula_mode: dict[tuple[str, str], Mapping[str, Any]] = {}
    for run in probe_payload.get("runs", []):
        if isinstance(run, Mapping):
            runs_by_formula_mode[(str(run.get("formula")), str(run.get("start_mode")))] = run

    rows: list[dict[str, Any]] = []
    for formula, law in (("logistic", "Logistic diagnostic"), ("planck", "Planck diagnostic")):
        scientific = scientific_by_law.get(law, {})
        motif = motif_by_law.get(law, {})
        compile_run = runs_by_formula_mode.get((formula, "compile"), {})
        blind_run = runs_by_formula_mode.get((formula, "blind"), {})
        rows.append(
            {
                "law": law,
                "formula_id": formula,
                "compile_support": scientific.get("compile_support"),
                "strict_gate": 13,
                "baseline_depth": motif.get("baseline_depth"),
                "relaxed_motif_depth": motif.get("motif_depth") or scientific.get("compile_depth"),
                "relaxed_depth_improved": bool(motif.get("depth_delta")),
                "macro_hits": scientific.get("macro_hits"),
                "compile_probe_status": compile_run.get("classification") or compile_run.get("status"),
                "blind_probe_status": blind_run.get("classification") or blind_run.get("status"),
                "blind_probe_verifier_status": _nested_mapping(blind_run, ("metrics", "verifier_status")),
                "promotion": "no",
                "promotion_reason": "strict support and verifier recovery did not both pass",
                "evidence_regime": scientific.get("evidence_regime"),
                "scientific_artifact_path": scientific.get("artifact_path"),
                "blind_probe_artifact_path": blind_run.get("artifact_path"),
                "claim_boundary": "negative result remains visible; relaxed depth improvement is not recovery",
            }
        )
    return rows


def v112_shallow_refresh_suite(output_dir: Path = DEFAULT_V112_REFRESH_DIR) -> BenchmarkSuite:
    """Build the v1.12 shallow refresh suite without executing it."""

    artifact_root = Path(output_dir) / "runs"
    dataset = DatasetConfig(points=24)
    seeds = (2, 3, 4, 5, 6)
    pure = BenchmarkCase(
        id="exp-pure-blind-seed-refresh",
        formula="exp",
        start_mode="blind",
        seeds=seeds,
        dataset=dataset,
        optimizer=OptimizerBudget(depth=1, steps=80, restarts=2, scaffold_initializers=()),
        tags=("v1.12", "paper_refresh", "pure_blind", "shallow"),
        expect_recovery=False,
        training_mode="blind_training",
    )
    scaffolded = BenchmarkCase(
        id="exp-scaffolded-seed-refresh",
        formula="exp",
        start_mode="blind",
        seeds=seeds,
        dataset=dataset,
        optimizer=OptimizerBudget(depth=1, steps=40, restarts=1),
        tags=("v1.12", "paper_refresh", "scaffolded", "shallow"),
        expect_recovery=True,
        training_mode="blind_training",
    )
    return BenchmarkSuite(
        id="v1.12-shallow-refresh",
        description="v1.12 current-code shallow exp seed refresh with separate pure-blind and scaffolded denominators.",
        cases=(pure, scaffolded),
        artifact_root=artifact_root,
    )


def v112_depth_refresh_suite(output_dir: Path = DEFAULT_V112_REFRESH_DIR) -> BenchmarkSuite:
    """Build the current-code depth 2-5 refresh suite without executing it."""

    base = load_suite("proof-depth-curve")
    selected = {"depth-2-blind", "depth-3-blind", "depth-4-blind", "depth-5-blind"}
    return BenchmarkSuite(
        id=base.id,
        description="v1.12 current-code subset of proof-depth-curve, blind depths 2 through 5 with two seeds each.",
        cases=tuple(case for case in base.cases if case.id in selected),
        artifact_root=Path(output_dir) / "runs",
        schema=base.schema,
    )


def write_v112_evidence_refresh(
    *,
    output_dir: Path = DEFAULT_V112_REFRESH_DIR,
    overwrite: bool = False,
) -> PaperRefreshPaths:
    """Run the v1.12 shallow/depth evidence refresh and write compact paper tables."""

    output_dir = Path(output_dir)
    if output_dir.exists() and overwrite:
        shutil.rmtree(output_dir)
    if (output_dir / "manifest.json").exists() and not overwrite:
        raise FileExistsError(f"{output_dir / 'manifest.json'} already exists; pass overwrite=True to refresh")
    output_dir.mkdir(parents=True, exist_ok=True)
    tables_dir = output_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    paths = PaperRefreshPaths(
        output_dir=output_dir,
        manifest_json=output_dir / "manifest.json",
        shallow_suite_json=output_dir / "shallow-suite.json",
        shallow_suite_result_json=output_dir / "shallow-suite-result.json",
        shallow_aggregate_json=output_dir / "shallow-aggregate.json",
        shallow_aggregate_md=output_dir / "shallow-aggregate.md",
        shallow_runs_json=tables_dir / "shallow-refresh-runs.json",
        shallow_runs_csv=tables_dir / "shallow-refresh-runs.csv",
        shallow_runs_md=tables_dir / "shallow-refresh-runs.md",
        depth_suite_json=output_dir / "depth-suite.json",
        depth_suite_result_json=output_dir / "depth-suite-result.json",
        depth_aggregate_json=output_dir / "depth-aggregate.json",
        depth_aggregate_md=output_dir / "depth-aggregate.md",
        depth_runs_json=tables_dir / "depth-refresh-runs.json",
        depth_runs_csv=tables_dir / "depth-refresh-runs.csv",
        depth_runs_md=tables_dir / "depth-refresh-runs.md",
        depth_summary_json=tables_dir / "depth-refresh-summary.json",
        depth_summary_csv=tables_dir / "depth-refresh-summary.csv",
        depth_summary_md=tables_dir / "depth-refresh-summary.md",
    )

    shallow_suite = v112_shallow_refresh_suite(output_dir)
    depth_suite = v112_depth_refresh_suite(output_dir)
    _write_json(paths.shallow_suite_json, shallow_suite.as_dict())
    _write_json(paths.depth_suite_json, depth_suite.as_dict())

    shallow_result = run_benchmark_suite(shallow_suite)
    _write_json(paths.shallow_suite_result_json, shallow_result.as_dict())
    shallow_aggregate_paths = write_aggregate_reports(shallow_result, output_dir / "shallow")
    shutil.copy2(shallow_aggregate_paths["json"], paths.shallow_aggregate_json)
    shutil.copy2(shallow_aggregate_paths["markdown"], paths.shallow_aggregate_md)
    shallow_aggregate = aggregate_evidence(shallow_result)

    depth_result = run_benchmark_suite(depth_suite)
    _write_json(paths.depth_suite_result_json, depth_result.as_dict())
    depth_aggregate_paths = write_aggregate_reports(depth_result, output_dir / "depth")
    shutil.copy2(depth_aggregate_paths["json"], paths.depth_aggregate_json)
    shutil.copy2(depth_aggregate_paths["markdown"], paths.depth_aggregate_md)
    depth_aggregate = aggregate_evidence(depth_result)

    shallow_rows = refresh_run_rows(shallow_aggregate, source="v1.12-current-code-shallow-refresh")
    depth_rows = refresh_run_rows(depth_aggregate, source="v1.12-current-code-depth-refresh")
    depth_summary_rows = [
        {
            "source": "v1.12-current-code-depth-refresh",
            "depth": row.get("depth"),
            "start_mode": row.get("start_mode"),
            "training_mode": row.get("training_mode"),
            "seed_count": row.get("seed_count"),
            "recovered": row.get("recovered"),
            "total": row.get("total"),
            "recovery_rate": row.get("recovery_rate"),
            "best_loss_median": row.get("best_loss_median"),
            "post_snap_loss_median": row.get("post_snap_loss_median"),
            "runtime_seconds_median": row.get("runtime_seconds_median"),
            "claim_boundary": "current-code v1.12 depth refresh; not archived v1.6 evidence",
        }
        for row in depth_aggregate.get("depth_curve", [])
    ]
    _write_table(paths.shallow_runs_json, paths.shallow_runs_csv, paths.shallow_runs_md, "Shallow Refresh Runs", shallow_rows)
    _write_table(paths.depth_runs_json, paths.depth_runs_csv, paths.depth_runs_md, "Depth Refresh Runs", depth_rows)
    _write_table(
        paths.depth_summary_json,
        paths.depth_summary_csv,
        paths.depth_summary_md,
        "Depth Refresh Summary",
        depth_summary_rows,
    )

    manifest = {
        "schema": "eml.v112_evidence_refresh.v1",
        "generated_at": _now_iso(),
        "output_dir": str(output_dir),
        "outputs": paths.as_dict(),
        "counts": {
            "shallow_runs": len(shallow_rows),
            "depth_runs": len(depth_rows),
            "depth_summary_rows": len(depth_summary_rows),
            "shallow_verifier_recovered": shallow_aggregate.get("counts", {}).get("verifier_recovered"),
            "depth_verifier_recovered": depth_aggregate.get("counts", {}).get("verifier_recovered"),
        },
        "source_locks": [
            _source_lock("shallow_suite", paths.shallow_suite_json),
            _source_lock("shallow_aggregate", paths.shallow_aggregate_json),
            _source_lock("depth_suite", paths.depth_suite_json),
            _source_lock("depth_aggregate", paths.depth_aggregate_json),
        ],
        "claim_boundary": "current-code refresh rows preserve pure-blind, scaffolded, and depth denominators separately",
        "reproduction": {
            "command": f"PYTHONPATH=src python -m eml_symbolic_regression.cli paper-refresh --output-dir {output_dir} --overwrite",
        },
    }
    _write_json(paths.manifest_json, manifest)
    return paths


def refresh_run_rows(aggregate: Mapping[str, Any], *, source: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for run in aggregate.get("runs", []):
        if not isinstance(run, Mapping):
            continue
        optimizer = run.get("optimizer") if isinstance(run.get("optimizer"), Mapping) else {}
        metrics = run.get("metrics") if isinstance(run.get("metrics"), Mapping) else {}
        rows.append(
            {
                "source": source,
                "suite_id": run.get("suite_id"),
                "case_id": run.get("case_id"),
                "formula": run.get("formula"),
                "start_mode": run.get("start_mode"),
                "seed": run.get("seed"),
                "depth": optimizer.get("depth"),
                "steps": optimizer.get("steps"),
                "restarts": optimizer.get("restarts"),
                "scaffold_initializers": ";".join(str(item) for item in optimizer.get("scaffold_initializers", [])),
                "evidence_class": run.get("evidence_class"),
                "classification": run.get("classification"),
                "status": run.get("status"),
                "claim_status": run.get("claim_status"),
                "verifier_status": metrics.get("verifier_status"),
                "best_loss": metrics.get("best_loss"),
                "post_snap_loss": metrics.get("post_snap_loss"),
                "snap_min_margin": metrics.get("snap_min_margin"),
                "reason": run.get("reason"),
                "artifact_path": run.get("artifact_path"),
                "claim_boundary": "row belongs only to its source suite/start-mode denominator",
            }
        )
    return rows


def _motif_paper_claim(row: Mapping[str, Any]) -> str:
    if row.get("strict_support") is True:
        return "Reusable motif lowers compile depth while preserving strict support and verifier-backed same-AST evidence."
    return "Reusable motif lowers relaxed compile depth, but strict support remains false and no recovery promotion is claimed."


def _nested_mapping(payload: Mapping[str, Any], path: tuple[str, ...]) -> Any:
    current: Any = payload
    for key in path:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current


def _pipeline_svg() -> str:
    boxes = [
        ("Data", "train / held-out / extrapolation", 40),
        ("Soft complete EML tree", "complex128 logits and guards", 245),
        ("Snap", "exact categorical EML AST", 500),
        ("Candidate pool", "repair / refit with fallback", 675),
        ("Verifier", "held-out + mpmath checks", 910),
    ]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1140" height="320" viewBox="0 0 1140 320">',
        "<style>",
        ".title{font:700 24px Arial,sans-serif;fill:#17202a}.label{font:700 17px Arial,sans-serif;fill:#17202a}.small{font:13px Arial,sans-serif;fill:#34495e}.box{fill:#f7f9fb;stroke:#34495e;stroke-width:1.5}.arrow{stroke:#146c94;stroke-width:3;fill:none;marker-end:url(#arrow)}.band{fill:#e8f1f5}",
        "</style>",
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#146c94"/></marker></defs>',
        '<rect x="0" y="0" width="1140" height="320" fill="#ffffff"/>',
        '<text x="40" y="42" class="title">Verifier-Gated Hybrid EML Pipeline</text>',
        '<text x="40" y="68" class="small">Stages are regime-aware; verifier status, not soft loss alone, owns recovery claims.</text>',
        '<rect x="40" y="236" width="1060" height="42" class="band"/>',
        '<text x="58" y="262" class="small">Claim boundary: pure blind, scaffolded, warm-start, same-AST, repair/refit, compile-only, unsupported, and failed rows keep separate denominators.</text>',
    ]
    for title, subtitle, x in boxes:
        width = 165 if title != "Soft complete EML tree" else 210
        parts.append(f'<rect x="{x}" y="116" width="{width}" height="82" rx="6" class="box"/>')
        parts.append(f'<text x="{x + 14}" y="148" class="label">{title}</text>')
        parts.append(f'<text x="{x + 14}" y="174" class="small">{subtitle}</text>')
        end_x = x + width
        if title != "Verifier":
            next_x = boxes[boxes.index((title, subtitle, x)) + 1][2]
            parts.append(f'<path d="M{end_x + 10} 157 L{next_x - 15} 157" class="arrow"/>')
    parts.append("</svg>")
    return "\n".join(parts)


def _figure_captions_markdown(paths: PaperFacingPaths) -> str:
    return "\n".join(
        [
            "# Figure Captions",
            "",
            "## Figure 1. Verifier-gated hybrid EML pipeline",
            "",
            f"Source: `{paths.pipeline_svg}` and `{paths.pipeline_metadata_json}`. The diagram summarizes data preparation, soft complete-tree search, exact snapping, candidate-pool repair/refit, and verifier-owned recovery checks. It is a workflow figure, not a recovery-rate denominator.",
            "",
            "## Existing v1.11 figures",
            "",
            "- `artifacts/paper/v1.11/figures/regime_recovery.svg`: recovery by evidence regime with separated denominators.",
            "- `artifacts/paper/v1.11/figures/depth_degradation.svg`: archived v1.6 depth-boundary evidence; supplement with Phase 65 current-code depth rows.",
            "- `artifacts/paper/v1.11/figures/scientific_law_support.svg`: supported and unsupported scientific-law rows.",
            "- `artifacts/paper/v1.11/figures/motif_depth_deltas.svg`: reusable motif depth reductions, not recovery promotion for unsupported rows.",
            "- `artifacts/paper/v1.11/figures/training_lifecycle.svg`: soft loss and snap-loss diagnostics before verifier selection.",
            "- `artifacts/paper/v1.11/figures/failure_taxonomy.svg`: visible unsupported and failed cases.",
            "- `artifacts/paper/v1.11/figures/baseline_diagnostics.svg`: prediction-only baseline diagnostics, outside EML symbolic recovery denominators.",
            "",
        ]
    )


def _table_captions_markdown(paths: PaperFacingPaths) -> str:
    return "\n".join(
        [
            "# Table Captions",
            "",
            "## Table 1. Claim taxonomy",
            "",
            "`artifacts/paper/v1.11/draft/claim-taxonomy.md` defines evidence classes and denominator eligibility. This table is the guardrail for all reported recovery rates.",
            "",
            "## Table 2. Motif library evolution",
            "",
            f"`{paths.motif_evolution_md}` records before/after depth and node counts for reusable compiler motifs. Planck uses the v1.11 diagnostic convention 24 -> 14; older relaxed-depth references are noted separately.",
            "",
            "## Table 3. Logistic and Planck negative results",
            "",
            f"`{paths.negative_results_md}` makes the unsupported status visible: compile support is unsupported, relaxed depth improved, blind probes did not recover, and promotion remains `no`.",
            "",
            "## Table 4. Shallow and depth refresh",
            "",
            "`artifacts/campaigns/v1.12-evidence-refresh/tables/shallow-refresh-runs.md` and `artifacts/campaigns/v1.12-evidence-refresh/tables/depth-refresh-summary.md` provide current-code refresh rows for Phase 65.",
            "",
            "## Table 5. Training dynamics and candidate lifecycle",
            "",
            "`artifacts/paper/v1.11/draft/training-detail/tables/training-step-traces.md`, `training-run-summaries.md`, and `candidate-lifecycle.md` expose per-step losses, objective components, anomaly counters, snap metrics, and verifier-owned candidate selection for the v1.12 refresh runs.",
            "",
        ]
    )


def _v112_source_locks(*, draft_dir: Path, refresh_dir: Path, output_dir: Path) -> list[dict[str, Any]]:
    locks: list[dict[str, Any]] = []
    for src in sorted(Path(draft_dir).rglob("*")):
        if not src.is_file():
            continue
        role = _v112_draft_role(src)
        rel = src.relative_to(draft_dir)
        locks.append(_copy_and_lock_v112(f"v112-draft-{_path_id(rel)}", role, src, output_dir / "sources" / "draft" / rel))

    for src in sorted(Path(refresh_dir).rglob("*")):
        if not src.is_file() or "runs" in src.relative_to(refresh_dir).parts:
            continue
        rel = src.relative_to(refresh_dir)
        locks.append(
            _copy_and_lock_v112(
                f"v112-refresh-{_path_id(rel)}",
                "v112_evidence_refresh",
                src,
                output_dir / "sources" / "evidence-refresh" / rel,
            )
        )
    return locks


def _v112_draft_role(path: Path) -> str:
    name = path.name
    if name in {"abstract.md", "methods.md", "results.md", "limitations.md", "manifest.json"} or name.startswith("claim-taxonomy"):
        return "v112_draft"
    if name.startswith("conventional-symbolic-baseline-probe") or name.startswith("logistic-strict-support"):
        return "v112_bounded_probe"
    return "v112_paper_facing"


def _copy_and_lock_v112(source_id: str, role: str, src: Path, dst: Path) -> dict[str, Any]:
    if not src.is_file():
        raise FileNotFoundError(f"required source missing: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.resolve() != dst.resolve():
        shutil.copy2(src, dst)
    return {
        "source_id": source_id,
        "role": role,
        "source_path": str(src),
        "supplement_path": str(dst),
        "sha256": _sha256(src),
        "bytes": src.stat().st_size,
    }


def _v112_claim_audit_markdown(audit: Mapping[str, Any]) -> str:
    lines = [
        "# v1.12 Claim Audit",
        "",
        f"Status: **{audit.get('status')}**",
        "",
        "| Check | Status | Detail |",
        "|-------|--------|--------|",
    ]
    for check in audit.get("checks", []):
        if isinstance(check, Mapping):
            lines.append(f"| {check.get('id')} | {check.get('status')} | {check.get('message')} |")
    lines.append("")
    return "\n".join(lines)


def _v112_reproduction_markdown(output_dir: Path) -> str:
    output_text = str(output_dir)
    return "\n".join(
        [
            "# v1.12 Supplement Reproduction Commands",
            "",
            "Run from the repository root.",
            "",
            "```bash",
            "PYTHONPATH=src python -m eml_symbolic_regression.cli paper-draft --output-dir artifacts/paper/v1.11/draft",
            "PYTHONPATH=src python -m eml_symbolic_regression.cli paper-refresh --output-dir artifacts/campaigns/v1.12-evidence-refresh --overwrite",
            "PYTHONPATH=src python -m eml_symbolic_regression.cli paper-figures --output-dir artifacts/paper/v1.11/draft",
            "PYTHONPATH=src python -m eml_symbolic_regression.cli paper-probes --output-dir artifacts/paper/v1.11/draft",
            f"PYTHONPATH=src python -m eml_symbolic_regression.cli paper-supplement --output-dir {output_text} --overwrite",
            "```",
            "",
            "The baseline probe is optional and fail-closed: if no conventional symbolic-regression package is importable locally, the supplement records `unavailable` rather than installing dependencies.",
            "",
        ]
    )


def _audit_check(
    checks: list[dict[str, Any]],
    check_id: str,
    condition: bool,
    message: str,
    details: Mapping[str, Any],
) -> None:
    checks.append(
        {
            "id": check_id,
            "status": "passed" if condition else "failed",
            "message": message,
            "details": details,
        }
    )


def _path_id(path: Path) -> str:
    return "-".join(path.parts).replace(".", "-").replace("_", "-")


def claim_taxonomy_rows(claim_ledger: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return paper-facing evidence-regime definitions with denominator rules."""

    ledger_rows = claim_ledger.get("rows") if isinstance(claim_ledger.get("rows"), list) else []
    by_regime: dict[str, list[Mapping[str, Any]]] = {}
    for row in ledger_rows:
        if not isinstance(row, Mapping):
            continue
        claim_id = str(row.get("claim_id") or "")
        if not claim_id.startswith("v111-regime-"):
            continue
        by_regime.setdefault(str(row.get("eligible_denominator") or ""), []).append(row)

    definitions = [
        (
            "pure_blind",
            "Pure blind",
            "Random-initialized blind training with scaffold initializers disabled.",
            "Only verifier-recovered rows in this class may support pure blind recovery rates.",
            True,
        ),
        (
            "scaffolded",
            "Scaffolded blind",
            "Blind training with declared structural scaffold initializers.",
            "Useful optimizer evidence, but not pure blind discovery.",
            False,
        ),
        (
            "warm_start",
            "Compiler warm start",
            "Training initialized from a compiled EML expression.",
            "Basin or compiler-assisted evidence, not random-initialized discovery.",
            False,
        ),
        (
            "same_ast",
            "Same-AST return",
            "Runs that return the exact compiled or known target AST.",
            "Strong representational and basin evidence, not discovery from scratch.",
            False,
        ),
        (
            "perturbed_basin",
            "Perturbed basin",
            "Known true-tree starts perturbed before optimization.",
            "Measures local basin stability, not blind search.",
            False,
        ),
        (
            "repair_refit",
            "Repair/refit",
            "Verifier-gated local repair or frozen-structure constant refit after snapping.",
            "Post-snap improvement evidence, not the original optimizer discovery event.",
            False,
        ),
        (
            "compile_only",
            "Compile-only",
            "Exact compiler diagnostics without training.",
            "Representation support or unsupported diagnostics, not training recovery.",
            False,
        ),
        (
            "unsupported",
            "Unsupported",
            "Rows blocked by support gates, compile depth, missing witnesses, or explicit unsupported status.",
            "Must remain visible in denominators where eligible and never count as recovered.",
            False,
        ),
        (
            "failed",
            "Failed",
            "Rows that ran but failed verifier recovery, snapping, or acceptable numerical criteria.",
            "Must remain visible and never count as recovered.",
            False,
        ),
    ]

    rows: list[dict[str, Any]] = []
    for evidence_class, label, definition, safe_claim, pure_blind in definitions:
        source_rows = _source_rows_for_taxonomy(evidence_class, by_regime)
        total = sum(int(row.get("total") or 0) for row in source_rows)
        verifier_recovered = sum(int(row.get("verifier_recovered") or 0) for row in source_rows)
        unsupported = sum(int(row.get("unsupported") or 0) for row in source_rows)
        failed = sum(int(row.get("failed") or 0) for row in source_rows)
        rows.append(
            {
                "evidence_class": evidence_class,
                "paper_label": label,
                "definition": definition,
                "denominator_rule": _denominator_rule(evidence_class),
                "eligible_for_pure_blind_rate": pure_blind,
                "eligible_for_verifier_recovery_rate": evidence_class not in {"unsupported", "failed"},
                "rate_source": "verifier-owned counts only",
                "safe_public_claim": safe_claim,
                "source_claim_ids": ";".join(str(row.get("claim_id")) for row in source_rows),
                "source_total": total,
                "source_verifier_recovered": verifier_recovered,
                "source_unsupported": unsupported,
                "source_failed": failed,
                "claim_boundary": "do not merge this class into pure blind discovery unless explicitly eligible",
            }
        )
    return rows


def _source_rows_for_taxonomy(evidence_class: str, by_regime: Mapping[str, list[Mapping[str, Any]]]) -> list[Mapping[str, Any]]:
    if evidence_class == "same_ast":
        return by_regime.get("same_ast_return", [])
    if evidence_class == "repair_refit":
        return [*by_regime.get("repaired", []), *by_regime.get("refit", [])]
    return by_regime.get(evidence_class, [])


def _denominator_rule(evidence_class: str) -> str:
    if evidence_class == "pure_blind":
        return "pure-blind suite rows only; scaffolds, warm starts, repairs, and perturbed starts excluded"
    if evidence_class in {"unsupported", "failed"}:
        return "visible negative rows inside their original regime denominator"
    return f"{evidence_class} rows are denominated separately from pure blind rows"


def _abstract_markdown(readiness: str, scientific: Mapping[str, Any]) -> str:
    supported = [
        str(row.get("law"))
        for row in scientific.get("rows", [])
        if isinstance(row, Mapping) and row.get("compile_support") == "supported" and row.get("verifier_status") == "recovered"
    ]
    supported_text = ", ".join(supported) if supported else "none"
    return "\n".join(
        [
            "# Abstract Draft Skeleton",
            "",
            "## Working Title",
            "",
            "Verifier-gated hybrid symbolic regression over complete EML trees",
            "",
            "## Abstract",
            "",
            "We study symbolic regression in the elementary-function basis generated by the single binary EML operator. The method searches a complete depth-bounded soft EML tree, snaps the optimized categorical choices into an exact tree, applies local repair or refit only under verifier ownership, and reports formulas only after held-out, extrapolation, and high-precision checks.",
            "",
            "The current evidence supports a bounded claim: shallow and scaffolded regimes can recover verified formulas, compiler and same-AST warm starts provide useful basin evidence, and blind recovery degrades quickly with depth. The paper should present this as a verifier-gated hybrid EML methods and evidence study, not as broad superiority over symbolic-regression systems.",
            "",
            f"Supported scientific-law rows in the v1.11 source package: {supported_text}. Logistic and Planck remain unsupported diagnostics unless a later strict support and verifier artifact passes.",
            "",
            "## Evidence Hooks",
            "",
            "- Primary evidence package: `artifacts/paper/v1.11/`.",
            "- Claim audit: `artifacts/paper/v1.11/claim-audit.json`.",
            "- Claim taxonomy: `artifacts/paper/v1.11/draft/claim-taxonomy.md`.",
            "- Evidence refresh placeholders: Phase 65 will add current-code shallow and depth-refresh rows.",
            "",
            "## Framing Guardrail",
            "",
            readiness.split("## Paper Framing", 1)[-1].strip() if "## Paper Framing" in readiness else readiness.strip(),
            "",
        ]
    )


def _methods_markdown() -> str:
    return "\n".join(
        [
            "# Methods Draft Skeleton",
            "",
            "## EML Representation",
            "",
            "Define the EML operator and the complete depth-bounded binary tree grammar. State that exact candidate formulas are represented as EML ASTs, with literal constants reported as explicit provenance when used.",
            "",
            "## Differentiable Search",
            "",
            "Describe the PyTorch `complex128` soft master tree, categorical logits, restart budgets, hardening, and training-mode numerical guards. Make clear that soft loss is a candidate-generation signal, not the recovery criterion.",
            "",
            "## Snapping and Candidate Pooling",
            "",
            "Describe argmax snapping, late-hardening candidate pools, fallback preservation, local cleanup, and post-snap refit as verifier-ranked stages.",
            "",
            "## Compiler and Motif Library",
            "",
            "Describe the SymPy-to-EML compiler as a structural, validation-gated source of exact seeds and diagnostics. Motifs are reusable transformations; formula-name recognizers and silent gate relaxation are excluded.",
            "",
            "## Verification Contract",
            "",
            "State the verifier-owned recovery contract: training split, held-out split, extrapolation split, exact candidate checks, and high-precision checks. A row is recovered only when the verifier status passes.",
            "",
            "## Evidence Regimes",
            "",
            "Use `claim-taxonomy.md` as the methods table for regime separation: pure blind, scaffolded, warm-start, same-AST, perturbed-basin, repair/refit, compile-only, unsupported, and failed.",
            "",
        ]
    )


def _results_markdown(scientific: Mapping[str, Any], assets: Mapping[str, Any], audit: Mapping[str, Any]) -> str:
    rows = [row for row in scientific.get("rows", []) if isinstance(row, Mapping)]
    supported = [str(row.get("law")) for row in rows if row.get("compile_support") == "supported" and row.get("verifier_status") == "recovered"]
    unsupported = [str(row.get("law")) for row in rows if row.get("compile_support") == "unsupported" or row.get("verifier_status") == "unsupported"]
    figure_count = assets.get("counts", {}).get("figures") if isinstance(assets.get("counts"), Mapping) else "unknown"
    table_count = assets.get("counts", {}).get("tables") if isinstance(assets.get("counts"), Mapping) else "unknown"
    return "\n".join(
        [
            "# Results Draft Skeleton",
            "",
            "## Representation and Verification",
            "",
            "Report exact EML AST support, source-locked package generation, and the v1.11 claim audit. The current audit status is "
            f"`{audit.get('status')}`.",
            "",
            "## Regime-Separated Recovery",
            "",
            "Use the regime recovery table and taxonomy table to report pure blind, scaffolded, warm-start, same-AST, perturbed-basin, repair/refit, compile-only, unsupported, and failed rows separately.",
            "",
            "## Depth-Limit Story",
            "",
            "Use archived v1.6 depth-degradation evidence as historical boundary evidence, then replace or supplement with Phase 65 current-code depth-refresh rows.",
            "",
            "## Scientific-Law Rows",
            "",
            f"Supported rows: {', '.join(supported) if supported else 'none'}.",
            "",
            f"Unsupported or diagnostic rows: {', '.join(unsupported) if unsupported else 'none'}. Logistic and Planck remain unsupported unless strict support and verifier recovery both pass.",
            "",
            "## Figures and Tables",
            "",
            f"The v1.11 package already contains {figure_count} figures and {table_count} source tables. Phase 66 will add paper-facing captions, motif evolution, pipeline, negative-results, and taxonomy presentation artifacts.",
            "",
        ]
    )


def _limitations_markdown() -> str:
    return "\n".join(
        [
            "# Limitations Draft Skeleton",
            "",
            "## Blind Search Depth",
            "",
            "Blind gradient search degrades sharply as exact EML depth increases. The paper should report this as a central limitation, not as a minor caveat.",
            "",
            "## Evidence Regime Separation",
            "",
            "Scaffolded, warm-start, same-AST, perturbed true-tree, repair/refit, and compile-only evidence are useful but do not establish pure blind discovery.",
            "",
            "## Logistic and Planck",
            "",
            "Logistic and Planck have improved relaxed-depth diagnostics, but remain unsupported under strict support gates unless a later phase produces strict compiler support and verifier-owned recovery.",
            "",
            "## Baselines",
            "",
            "Current prediction-only baselines are diagnostic, not matched-budget symbolic-regression comparators. A conventional SR baseline is useful only if it is locally feasible without changing the paper's recovery denominators.",
            "",
            "## Scope",
            "",
            "The paper should claim a reproducible verifier-gated hybrid EML pipeline with honest boundaries, not universal deep recovery or broad symbolic-regression superiority.",
            "",
        ]
    )


def _claim_taxonomy_markdown(rows: list[Mapping[str, Any]]) -> str:
    columns = [
        "evidence_class",
        "paper_label",
        "denominator_rule",
        "eligible_for_pure_blind_rate",
        "eligible_for_verifier_recovery_rate",
        "safe_public_claim",
    ]
    return "\n".join(["# Claim Taxonomy", "", *_markdown_table_lines(rows, columns)])


def _write_table(json_path: Path, csv_path: Path, md_path: Path, title: str, rows: list[Mapping[str, Any]]) -> None:
    columns = _columns(rows)
    _write_json(json_path, {"schema": "eml.v112_source_table.v1", "columns": columns, "rows": rows})
    _write_csv(csv_path, rows)
    md_path.write_text("\n".join([f"# {title}", "", *_markdown_table_lines(rows, columns)]), encoding="utf-8")


def _markdown_table_lines(rows: list[Mapping[str, Any]], columns: list[str]) -> list[str]:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(_format_markdown(row.get(column)) for column in columns) + " |")
    lines.append("")
    return lines


def _format_markdown(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value if value is not None else "").replace("|", "\\|")


def _write_csv(path: Path, rows: list[Mapping[str, Any]]) -> None:
    columns = _columns(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: _csv_value(row.get(column)) for column in columns})


def _columns(rows: list[Mapping[str, Any]]) -> list[str]:
    columns: list[str] = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(str(key))
    return columns


def _csv_value(value: Any) -> Any:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True)
    if value is None:
        return ""
    return value


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _source_lock(source_id: str, path: Path) -> dict[str, Any]:
    return {"source_id": source_id, "path": str(path), "sha256": _sha256(path)}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
