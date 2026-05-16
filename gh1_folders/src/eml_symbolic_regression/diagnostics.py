"""Diagnostics over committed benchmark campaign evidence."""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from .benchmark import RunFilter
from .campaign import CampaignResult, run_campaign


DEFAULT_BASELINE_CAMPAIGNS = (
    Path("artifacts") / "campaigns" / "v1.3-standard",
    Path("artifacts") / "campaigns" / "v1.3-showcase",
)

FAILURE_CLASSES = frozenset({"failed", "snapped_but_failed", "soft_fit_only", "unsupported", "execution_failure"})
DIAGNOSTIC_TARGETS = frozenset({"blind-failures", "beer-perturbation-failures", "compiler-depth-gates"})


def write_baseline_triage(campaign_dirs: Iterable[Path], output_dir: Path) -> dict[str, Path]:
    """Write JSON, Markdown, and lock artifacts for baseline campaign triage."""

    output_dir.mkdir(parents=True, exist_ok=True)
    triage = build_baseline_triage(tuple(campaign_dirs))
    json_path = output_dir / "triage.json"
    markdown_path = output_dir / "triage.md"
    lock_path = output_dir / "baseline-lock.json"
    _write_json(json_path, triage)
    markdown_path.write_text(render_baseline_triage_markdown(triage), encoding="utf-8")
    _write_json(lock_path, {"schema": "eml.baseline_lock.v1", "baselines": triage["baseline_locks"]})
    return {"json": json_path, "markdown": markdown_path, "lock_json": lock_path}


def write_campaign_comparison(
    baseline_dirs: Iterable[Path],
    candidate_dirs: Iterable[Path],
    output_dir: Path,
) -> dict[str, Path]:
    """Write comparison artifacts plus immutable lock metadata for campaign directory pairs."""

    output_dir.mkdir(parents=True, exist_ok=True)
    comparison = build_campaign_comparison(tuple(baseline_dirs), tuple(candidate_dirs))
    json_path = output_dir / "comparison.json"
    markdown_path = output_dir / "comparison.md"
    lock_path = output_dir / "comparison-lock.json"
    _write_json(json_path, comparison)
    markdown_path.write_text(render_campaign_comparison_markdown(comparison), encoding="utf-8")
    _write_json(
        lock_path,
        {
            "schema": "eml.campaign_comparison_lock.v1",
            "baseline_locks": comparison["baseline_locks"],
            "candidate_locks": comparison["candidate_locks"],
        },
    )
    return {"json": json_path, "markdown": markdown_path, "lock_json": lock_path}


def build_perturbed_basin_bound_report(
    bounded_aggregate: Mapping[str, Any],
    probe_aggregate: Mapping[str, Any] | None = None,
    *,
    formula: str = "beer_lambert",
    declared_noise_grid: tuple[float, ...] = (5.0, 15.0, 35.0),
    declared_bound_noise_max: float = 5.0,
) -> dict[str, Any]:
    """Build a Beer-Lambert perturbed-basin bound report from aggregate rows."""

    bounded_rows = _bound_report_rows(bounded_aggregate, row_source="bounded", formula=formula)
    probe_rows = _bound_report_rows(probe_aggregate or {}, row_source="probe", formula=formula)
    rows = sorted(
        [*bounded_rows, *probe_rows],
        key=lambda row: (
            float(row["perturbation_noise"]),
            str(row["row_source"]),
            int(row["seed"]) if row.get("seed") is not None else -1,
            str(row.get("run_id") or ""),
        ),
    )
    grid = tuple(float(value) for value in declared_noise_grid)
    declared_bound = float(declared_bound_noise_max)
    expected_seed_noise_rows = _expected_seed_noise_rows(
        (("bounded", bounded_aggregate), ("probe", probe_aggregate or {})),
        formula=formula,
        grid=grid,
        rows=rows,
    )
    expected_seeds_by_noise = _expected_seeds_by_noise(expected_seed_noise_rows)
    missing_seed_noise_rows = _missing_seed_noise_rows(
        expected_seed_noise_rows,
        rows,
        formula=formula,
    )
    incomplete_noise_values = sorted({float(row["perturbation_noise"]) for row in missing_seed_noise_rows})
    grid_values = set(grid)
    artifact_incomplete_noise_values = sorted(
        {
            float(row["perturbation_noise"])
            for row in rows
            if float(row["perturbation_noise"]) in grid_values and not _has_durable_artifact(row)
        }
    )
    incomplete_noise_values = sorted(set(incomplete_noise_values) | set(artifact_incomplete_noise_values))
    raw_supported = _supported_noise_prefix(
        rows,
        grid,
        lambda row: _has_durable_artifact(row) and row.get("evidence_class") == "perturbed_true_tree_recovered",
        expected_seeds_by_noise=expected_seeds_by_noise,
    )
    repaired_supported = _supported_noise_prefix(
        rows,
        grid,
        lambda row: _has_durable_artifact(row)
        and row.get("evidence_class") in {"perturbed_true_tree_recovered", "repaired_candidate"},
        expected_seeds_by_noise=expected_seeds_by_noise,
    )
    unsupported_noise_values = sorted(
        {
            float(row["perturbation_noise"])
            for row in rows
            if float(row["perturbation_noise"]) in grid_values
            and row.get("evidence_class") not in {"perturbed_true_tree_recovered", "repaired_candidate"}
        }
        | set(incomplete_noise_values)
    )

    return {
        "schema": "eml.perturbed_basin_bound_report.v1",
        "formula": formula,
        "declared_noise_grid": list(grid),
        "bounded_noise_values": _noise_values(bounded_rows),
        "probe_noise_values": _noise_values(probe_rows),
        "declared_bound_noise_max": declared_bound,
        "raw_supported_noise_max": raw_supported,
        "repaired_supported_noise_max": repaired_supported,
        "expected_seed_noise_rows": expected_seed_noise_rows,
        "missing_seed_noise_rows": missing_seed_noise_rows,
        "invalid_artifact_noise_values": artifact_incomplete_noise_values,
        "incomplete_noise_values": incomplete_noise_values,
        "unsupported_noise_values": unsupported_noise_values,
        "claim_recommendation": _bound_claim_recommendation(
            repaired_supported,
            declared_bound_noise_max=declared_bound,
        ),
        "rows": rows,
    }


def write_perturbed_basin_bound_report(
    bounded_aggregate_path: Path,
    probe_aggregate_path: Path | None,
    output_dir: Path,
) -> dict[str, Path]:
    """Write JSON and Markdown Beer-Lambert perturbed-basin bound evidence."""

    bounded_aggregate = json.loads(Path(bounded_aggregate_path).read_text(encoding="utf-8"))
    probe_aggregate = None
    if probe_aggregate_path is not None:
        probe_aggregate = json.loads(Path(probe_aggregate_path).read_text(encoding="utf-8"))
    report = build_perturbed_basin_bound_report(bounded_aggregate, probe_aggregate)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "basin-bound.json"
    markdown_path = output_dir / "basin-bound.md"
    _write_json(json_path, report)
    markdown_path.write_text(render_perturbed_basin_bound_markdown(report), encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}


def render_perturbed_basin_bound_markdown(report: Mapping[str, Any]) -> str:
    declared_noise_grid = ", ".join(_fmt(value) for value in report.get("declared_noise_grid", ()))
    lines = [
        "# Perturbed Basin Bound Report",
        "",
        f"- Formula: `{report.get('formula')}`",
        f"- Declared noise grid: {declared_noise_grid}",
        f"- Declared bounded proof max: {_fmt(report.get('declared_bound_noise_max'))}",
        f"- Raw supported max: {_fmt(report.get('raw_supported_noise_max'))}",
        f"- Repaired supported max: {_fmt(report.get('repaired_supported_noise_max'))}",
        f"- Claim recommendation: `{report.get('claim_recommendation')}`",
        f"- Expected seed/noise rows: {len(report.get('expected_seed_noise_rows', ()))}",
        f"- Missing seed/noise rows: {len(report.get('missing_seed_noise_rows', ()))}",
        "",
        "High-noise probe rows remain separate from bounded proof thresholds. Probe evidence can support a follow-up bound only when it forms a continuous declared-grid prefix.",
        "",
    ]

    missing_rows = list(report.get("missing_seed_noise_rows", ()))
    if missing_rows:
        lines.extend(
            [
                "## Missing Seed/Noise Rows",
                "",
                "| Source | Suite | Case | Seed | Noise | Reason |",
                "|--------|-------|------|------|-------|--------|",
            ]
        )
        for row in missing_rows:
            lines.append(
                f"| {row.get('row_source')} | {row.get('suite_id')} | {row.get('case_id')} | "
                f"{row.get('seed')} | {_fmt(row.get('perturbation_noise'))} | {row.get('reason')} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Rows",
            "",
            "| Source | Suite | Case | Run | Seed | Noise | Status | Claim | Evidence | Return Kind | Raw Status | Repair Status | Changed Slots | Accepted Repair Moves | Reason | Artifact | Artifact SHA256 |",
            "|--------|-------|------|-----|------|-------|--------|-------|----------|-------------|------------|---------------|---------------|-----------------------|--------|----------|----------|",
        ]
    )
    for row in report.get("rows", ()):
        lines.append(
            f"| {row.get('row_source')} | {row.get('suite_id')} | {row.get('case_id')} | {row.get('run_id')} | "
            f"{row.get('seed')} | {_fmt(row.get('perturbation_noise'))} | {row.get('status')} | "
            f"{row.get('claim_status')} | {row.get('evidence_class')} | {row.get('return_kind')} | "
            f"{row.get('raw_status')} | {row.get('repair_status')} | {_fmt(row.get('changed_slot_count'))} | "
            f"{_fmt(row.get('repair_accepted_move_count'))} | {row.get('reason')} | {row.get('artifact_path')} | "
            f"{row.get('artifact_sha256') or ''} |"
        )
    lines.append("")
    return "\n".join(lines)


def build_campaign_comparison(baseline_dirs: tuple[Path, ...], candidate_dirs: tuple[Path, ...]) -> dict[str, Any]:
    if len(baseline_dirs) != len(candidate_dirs):
        raise ValueError("baseline and candidate campaign counts must match")
    baseline_campaigns = [_load_campaign_dir(path) for path in baseline_dirs]
    candidate_campaigns = [_load_campaign_dir(path) for path in candidate_dirs]
    baseline_runs = [run for campaign in baseline_campaigns for run in campaign["aggregate"].get("runs", ())]
    candidate_runs = [run for campaign in candidate_campaigns for run in campaign["aggregate"].get("runs", ())]
    categories = {
        name: _compare_category(_category_rows(baseline_runs, name), _category_rows(candidate_runs, name))
        for name in ("overall", "blind_recovery", "beer_perturbation", "compiler_coverage")
    }
    return {
        "schema": "eml.campaign_comparison.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "campaign_pairs": [
            {
                "baseline": _baseline_summary(baseline),
                "candidate": _baseline_summary(candidate),
            }
            for baseline, candidate in zip(baseline_campaigns, candidate_campaigns)
        ],
        "baseline_locks": [_baseline_lock(campaign) for campaign in baseline_campaigns],
        "candidate_locks": [_baseline_lock(campaign) for campaign in candidate_campaigns],
        "categories": categories,
        "reproduce_command": _comparison_command(baseline_dirs, candidate_dirs),
    }


def build_baseline_triage(campaign_dirs: tuple[Path, ...]) -> dict[str, Any]:
    campaigns = [_load_campaign_dir(path) for path in campaign_dirs]
    failure_rows = [row for campaign in campaigns for row in _failure_rows(campaign)]
    group_counts = _group_failure_rows(failure_rows)
    diagnostic_subsets = {
        target: {
            "target": target,
            "run_count": len(rows),
            "run_filter": _filter_payload(filter_for_runs(rows)),
            "runs": rows,
        }
        for target in sorted(DIAGNOSTIC_TARGETS)
        for rows in (select_diagnostic_runs_from_rows(failure_rows, target),)
    }
    return {
        "schema": "eml.baseline_diagnostics.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "baselines": [_baseline_summary(campaign) for campaign in campaigns],
        "baseline_locks": [_baseline_lock(campaign) for campaign in campaigns],
        "failure_group_counts": group_counts,
        "failure_runs": failure_rows,
        "diagnostic_subsets": diagnostic_subsets,
    }


def select_diagnostic_runs(campaign_dirs: Iterable[Path], target: str) -> list[dict[str, Any]]:
    if target not in DIAGNOSTIC_TARGETS:
        raise ValueError(f"unknown diagnostic target {target!r}")
    campaigns = [_load_campaign_dir(path) for path in campaign_dirs]
    failure_rows = [row for campaign in campaigns for row in _failure_rows(campaign)]
    return select_diagnostic_runs_from_rows(failure_rows, target)


def select_diagnostic_runs_from_rows(rows: Iterable[Mapping[str, Any]], target: str) -> list[dict[str, Any]]:
    if target not in DIAGNOSTIC_TARGETS:
        raise ValueError(f"unknown diagnostic target {target!r}")
    selected: list[dict[str, Any]] = []
    for row in rows:
        if target == "blind-failures" and row.get("start_mode") == "blind":
            selected.append(dict(row))
        elif (
            target == "beer-perturbation-failures"
            and row.get("formula") == "beer_lambert"
            and row.get("start_mode") == "warm_start"
            and float(row.get("perturbation_noise") or 0.0) > 0.0
        ):
            selected.append(dict(row))
        elif target == "compiler-depth-gates" and row.get("classification") == "unsupported":
            selected.append(dict(row))
    return selected


def filter_for_runs(rows: Iterable[Mapping[str, Any]]) -> RunFilter:
    row_list = list(rows)
    return RunFilter(
        formulas=_sorted_str(row.get("formula") for row in row_list),
        start_modes=_sorted_str(row.get("start_mode") for row in row_list),
        case_ids=_sorted_str(row.get("case_id") for row in row_list),
        seeds=tuple(sorted({int(row["seed"]) for row in row_list if row.get("seed") is not None})),
        perturbation_noises=tuple(
            sorted({float(row["perturbation_noise"]) for row in row_list if row.get("perturbation_noise") is not None})
        ),
    )


def run_diagnostic_subset(
    target: str,
    campaign_dirs: Iterable[Path],
    *,
    preset_name: str,
    output_root: Path,
    label: str | None = None,
    overwrite: bool = False,
) -> CampaignResult:
    rows = select_diagnostic_runs(campaign_dirs, target)
    if not rows:
        raise ValueError(f"no baseline rows matched diagnostic target {target!r}")
    run_filter = filter_for_runs(rows)
    return run_campaign(preset_name, output_root=output_root, label=label, overwrite=overwrite, run_filter=run_filter)


def classify_blind_failure(run: Mapping[str, Any]) -> str:
    """Classify a blind run's remaining failure mechanism without changing recovery semantics."""

    if run.get("claim_status") == "recovered" or run.get("classification") == "blind_recovery":
        return "recovered"

    metrics = run.get("metrics", {})
    optimizer = run.get("optimizer", {})
    depth = _number_or_none(optimizer.get("depth"))
    active_nodes = _number_or_none(metrics.get("snap_active_node_count"))
    best_loss = _number_or_none(metrics.get("best_loss"))
    post_snap_loss = _number_or_none(metrics.get("post_snap_loss"))
    margin = _number_or_none(metrics.get("snap_min_margin"))

    if (depth is not None and depth >= 4) or (active_nodes is not None and active_nodes >= 9):
        return "expression_depth"
    if post_snap_loss is None or not math.isfinite(post_snap_loss):
        return "non_finite_snap"
    if best_loss is None or not math.isfinite(best_loss) or best_loss > 1.0:
        return "soft_loss"
    if (margin is not None and margin < 0.1) or (best_loss > 0 and post_snap_loss > best_loss * 10.0):
        return "snap_instability"
    return "verifier_mismatch"


def compare_blind_runs(baseline: Mapping[str, Any] | Iterable[Mapping[str, Any]], candidate: Mapping[str, Any] | Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Compare blind aggregate rows by formula/case/seed using verifier-owned statuses."""

    baseline_rows = _blind_rows(_rows_from(baseline))
    candidate_rows = _blind_rows(_rows_from(candidate))
    candidate_by_key = {_blind_key(row): row for row in candidate_rows}
    comparisons = []
    for base in baseline_rows:
        key = _blind_key(base)
        cand = candidate_by_key.get(key)
        if cand is None:
            continue
        base_metrics = base.get("metrics", {})
        cand_metrics = cand.get("metrics", {})
        best_delta = _delta(cand_metrics.get("best_loss"), base_metrics.get("best_loss"))
        post_delta = _delta(cand_metrics.get("post_snap_loss"), base_metrics.get("post_snap_loss"))
        comparisons.append(
            {
                "formula": key[0],
                "case_id": key[1],
                "seed": key[2],
                "baseline_status": base.get("claim_status") or base.get("status"),
                "candidate_status": cand.get("claim_status") or cand.get("status"),
                "baseline_classification": base.get("classification"),
                "candidate_classification": cand.get("classification"),
                "baseline_diagnostic": classify_blind_failure(base),
                "candidate_diagnostic": classify_blind_failure(cand),
                "best_loss_delta": best_delta,
                "post_snap_loss_delta": post_delta,
                "improved": _blind_improved(base, cand, best_delta, post_delta),
                "baseline_metrics": base_metrics,
                "candidate_metrics": cand_metrics,
            }
        )
    return comparisons


def render_baseline_triage_markdown(triage: Mapping[str, Any]) -> str:
    lines = [
        "# Baseline Failure Triage",
        "",
        "Committed v1.3 campaign failures grouped for v1.4 improvement work.",
        "",
        "## Baselines",
        "",
        "| Campaign | Runs | Verifier recovered | Unsupported | Failed |",
        "|----------|------|--------------------|-------------|--------|",
    ]
    for baseline in triage["baselines"]:
        counts = baseline.get("counts", {})
        lines.append(
            f"| {baseline['label']} | {counts.get('total', 0)} | {counts.get('verifier_recovered', 0)} | "
            f"{counts.get('unsupported', 0)} | {counts.get('failed', 0)} |"
        )

    lines.extend(
        [
            "",
            "## Failure Groups",
            "",
            "| Formula | Mode | Perturbation | Class | Count |",
            "|---------|------|--------------|-------|-------|",
        ]
    )
    for row in triage["failure_group_counts"]:
        lines.append(
            f"| {row['formula']} | {row['start_mode']} | {row['perturbation_noise']} | "
            f"{row['classification']} | {row['count']} |"
        )

    lines.extend(
        [
            "",
            "## Focused Diagnostic Subsets",
            "",
            "| Target | Runs | Formula filter | Mode filter | Noise filter |",
            "|--------|------|----------------|-------------|--------------|",
        ]
    )
    for target, subset in triage["diagnostic_subsets"].items():
        run_filter = subset["run_filter"]
        lines.append(
            f"| {target} | {subset['run_count']} | {', '.join(run_filter['formulas'])} | "
            f"{', '.join(run_filter['start_modes'])} | {', '.join(str(value) for value in run_filter['perturbation_noises'])} |"
        )

    lines.extend(
        [
            "",
            "## Representative Failure Runs",
            "",
            "| Campaign | Formula | Mode | Seed | Noise | Class | Reason | Metrics | Artifact |",
            "|----------|---------|------|------|-------|-------|--------|---------|----------|",
        ]
    )
    for row in triage["failure_runs"]:
        metrics = row.get("metrics", {})
        metric_text = (
            f"best={_fmt(metrics.get('best_loss'))}; snap={_fmt(metrics.get('post_snap_loss'))}; "
            f"margin={_fmt(metrics.get('snap_min_margin'))}; changed={_fmt(metrics.get('changed_slot_count'))}; "
            f"verifier={metrics.get('verifier_status')}"
        )
        lines.append(
            f"| {row['campaign']} | {row['formula']} | {row['start_mode']} | {row['seed']} | "
            f"{row['perturbation_noise']} | {row['classification']} | {row['reason']} | "
            f"{metric_text} | [{row['run_id']}]({row['artifact_path']}) |"
        )

    lines.extend(
        [
            "",
            "## Baseline Locks",
            "",
            "| Campaign | File | SHA-256 |",
            "|----------|------|---------|",
        ]
    )
    for baseline in triage["baseline_locks"]:
        for file_info in baseline["files"]:
            lines.append(f"| {baseline['label']} | {file_info['path']} | `{file_info['sha256']}` |")
    lines.append("")
    return "\n".join(lines)


def render_campaign_comparison_markdown(comparison: Mapping[str, Any]) -> str:
    lines = [
        "# Campaign Comparison Report",
        "",
        "Compares candidate campaign outputs against archived baseline campaign outputs without merging their denominators.",
        "",
        "## Reproduce",
        "",
        "Run this command from a clean checkout after the baseline and candidate campaign folders exist:",
        "",
        "```bash",
        comparison["reproduce_command"],
        "```",
        "",
        "## Campaign Pairs",
        "",
        "| Baseline | Candidate |",
        "|----------|-----------|",
    ]
    for pair in comparison["campaign_pairs"]:
        lines.append(f"| {pair['baseline']['path']} | {pair['candidate']['path']} |")

    lines.extend(
        [
            "",
            "## Anchor Locks",
            "",
            "### Baselines",
            "",
            "| Campaign | File | SHA-256 |",
            "|----------|------|---------|",
        ]
    )
    for campaign in comparison.get("baseline_locks", []):
        for file_info in campaign.get("files", []):
            lines.append(f"| {campaign['label']} | {file_info['path']} | `{file_info['sha256']}` |")
    lines.extend(["", "### Candidates", "", "| Campaign | File | SHA-256 |", "|----------|------|---------|"])
    for campaign in comparison.get("candidate_locks", []):
        for file_info in campaign.get("files", []):
            lines.append(f"| {campaign['label']} | {file_info['path']} | `{file_info['sha256']}` |")

    lines.extend(
        [
            "",
            "## Category Deltas",
            "",
            "| Category | Verdict | Recovery Rate | Unsupported Rate | Failure Rate | Median Best Loss | Median Post-Snap Loss | Median Runtime |",
            "|----------|---------|---------------|------------------|--------------|------------------|-----------------------|----------------|",
        ]
    )
    for name, category in comparison["categories"].items():
        delta = category["delta"]
        lines.append(
            f"| {name} | {category['verdict']} | {_fmt_delta(delta['verifier_recovery_rate'])} | "
            f"{_fmt_delta(delta['unsupported_rate'])} | {_fmt_delta(delta['failure_rate'])} | "
            f"{_fmt_delta(delta['median_best_loss'])} | {_fmt_delta(delta['median_post_snap_loss'])} | "
            f"{_fmt_delta(delta['median_runtime_seconds'])} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `improved` means recovery increased, unsupported rate decreased, or failure rate decreased.",
            "- `regressed` means the opposite movement dominates.",
            "- Loss and runtime deltas are supporting diagnostics and do not redefine recovery.",
            "",
        ]
    )
    return "\n".join(lines)


def _bound_report_rows(aggregate: Mapping[str, Any], *, row_source: str, formula: str) -> list[dict[str, Any]]:
    suite_id = aggregate.get("suite", {}).get("id") if isinstance(aggregate.get("suite"), Mapping) else None
    rows: list[dict[str, Any]] = []
    for row in aggregate.get("runs", ()):
        if row.get("formula") != formula:
            continue
        metrics = row.get("metrics") if isinstance(row.get("metrics"), Mapping) else {}
        repair_status = row.get("repair_status") or metrics.get("repair_status")
        evidence_class = _bound_report_evidence_class(row, repair_status=repair_status)
        artifact_path = row.get("artifact_path")
        rows.append(
            {
                "row_source": row_source,
                "suite_id": row.get("suite_id") or suite_id,
                "case_id": row.get("case_id"),
                "run_id": row.get("run_id"),
                "artifact_path": artifact_path,
                "artifact_sha256": _artifact_sha256(artifact_path, row.get("artifact_sha256")),
                "seed": row.get("seed"),
                "perturbation_noise": float(row.get("perturbation_noise") or 0.0),
                "status": row.get("status"),
                "claim_status": row.get("claim_status"),
                "evidence_class": evidence_class,
                "return_kind": row.get("return_kind"),
                "raw_status": row.get("raw_status"),
                "repair_status": repair_status,
                "changed_slot_count": _row_or_metric(row, metrics, "changed_slot_count"),
                "repair_accepted_move_count": _row_or_metric(row, metrics, "repair_accepted_move_count"),
                "reason": row.get("reason"),
            }
        )
    return rows


def _bound_report_evidence_class(row: Mapping[str, Any], *, repair_status: Any) -> str:
    evidence_class = row.get("evidence_class") or row.get("classification") or row.get("status")
    if repair_status == "repaired" or row.get("status") == "repaired_candidate":
        return "repaired_candidate"
    return str(evidence_class or "unknown")


def _row_or_metric(row: Mapping[str, Any], metrics: Mapping[str, Any], key: str) -> Any:
    if key in row:
        return row.get(key)
    return metrics.get(key)


def _noise_values(rows: Iterable[Mapping[str, Any]]) -> list[float]:
    return sorted({float(row["perturbation_noise"]) for row in rows})


def _expected_seed_noise_rows(
    aggregates: Iterable[tuple[str, Mapping[str, Any]]],
    *,
    formula: str,
    grid: tuple[float, ...],
    rows: list[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    grid_values = {float(value) for value in grid}
    expected: dict[tuple[float, int], dict[str, Any]] = {}
    for row_source, aggregate in aggregates:
        suite = aggregate.get("suite") if isinstance(aggregate.get("suite"), Mapping) else {}
        suite_id = suite.get("id") if isinstance(suite, Mapping) else None
        cases = suite.get("cases", ()) if isinstance(suite, Mapping) else ()
        for case in cases:
            if not isinstance(case, Mapping) or case.get("formula") != formula:
                continue
            for noise in case.get("perturbation_noise", ()):
                noise_value = float(noise)
                if noise_value not in grid_values:
                    continue
                for seed in case.get("seeds", ()):
                    seed_value = int(seed)
                    expected.setdefault(
                        (noise_value, seed_value),
                        {
                            "row_source": row_source,
                            "suite_id": suite_id,
                            "case_id": case.get("id"),
                            "formula": formula,
                            "seed": seed_value,
                            "perturbation_noise": noise_value,
                        },
                    )

    if expected:
        return [expected[key] for key in sorted(expected)]

    for row in rows:
        if row.get("seed") is None:
            continue
        noise_value = float(row["perturbation_noise"])
        if noise_value not in grid_values:
            continue
        seed_value = int(row["seed"])
        expected.setdefault(
            (noise_value, seed_value),
            {
                "row_source": row.get("row_source"),
                "suite_id": row.get("suite_id"),
                "case_id": row.get("case_id"),
                "formula": formula,
                "seed": seed_value,
                "perturbation_noise": noise_value,
            },
        )
    return [expected[key] for key in sorted(expected)]


def _expected_seeds_by_noise(expected_seed_noise_rows: Iterable[Mapping[str, Any]]) -> dict[float, set[int]]:
    expected: dict[float, set[int]] = {}
    for row in expected_seed_noise_rows:
        expected.setdefault(float(row["perturbation_noise"]), set()).add(int(row["seed"]))
    return expected


def _missing_seed_noise_rows(
    expected_seed_noise_rows: Iterable[Mapping[str, Any]],
    rows: list[Mapping[str, Any]],
    *,
    formula: str,
) -> list[dict[str, Any]]:
    observed = {
        (float(row["perturbation_noise"]), int(row["seed"]))
        for row in rows
        if row.get("seed") is not None and row.get("formula", formula) == formula
    }
    missing = []
    for expected in expected_seed_noise_rows:
        key = (float(expected["perturbation_noise"]), int(expected["seed"]))
        if key in observed:
            continue
        missing.append({**dict(expected), "reason": "missing_expected_seed_noise_row"})
    return missing


def _supported_noise_prefix(
    rows: list[Mapping[str, Any]],
    grid: tuple[float, ...],
    predicate: Any,
    *,
    expected_seeds_by_noise: Mapping[float, set[int]],
) -> float | None:
    by_noise: dict[float, list[Mapping[str, Any]]] = {}
    for row in rows:
        noise = float(row["perturbation_noise"])
        by_noise.setdefault(noise, []).append(row)

    supported: float | None = None
    for noise in sorted(grid):
        expected_seeds = expected_seeds_by_noise.get(float(noise))
        if not expected_seeds:
            break
        noise_rows = by_noise.get(float(noise), [])
        observed_seeds = {int(row["seed"]) for row in noise_rows if row.get("seed") is not None}
        if observed_seeds != expected_seeds:
            break
        if not all(predicate(row) for row in noise_rows):
            break
        supported = float(noise)
    return supported


def _has_durable_artifact(row: Mapping[str, Any]) -> bool:
    artifact_path = row.get("artifact_path")
    artifact_sha256 = row.get("artifact_sha256")
    if not _is_durable_artifact_path(artifact_path) or not _is_sha256_hex(artifact_sha256):
        return False
    return _artifact_sha256(artifact_path) == str(artifact_sha256).lower()


def _bound_claim_recommendation(repaired_supported_noise_max: float | None, *, declared_bound_noise_max: float) -> str:
    if repaired_supported_noise_max is None or repaired_supported_noise_max < declared_bound_noise_max:
        return f"narrow_to_{_bound_label(repaired_supported_noise_max)}"
    if repaired_supported_noise_max > declared_bound_noise_max:
        return f"probe_supports_{_bound_label(repaired_supported_noise_max)}"
    return "support_declared_bound"


def _bound_label(value: float | None) -> str:
    if value is None:
        return "none"
    number = float(value)
    if number.is_integer():
        return str(int(number))
    return f"{number:.15g}"


def _load_campaign_dir(path: Path) -> dict[str, Any]:
    aggregate_path = path / "aggregate.json"
    if not aggregate_path.exists():
        raise FileNotFoundError(f"missing aggregate.json in {path}")
    aggregate = json.loads(aggregate_path.read_text(encoding="utf-8"))
    manifest_path = path / "campaign-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    return {"path": path, "label": path.name, "aggregate": aggregate, "manifest": manifest}


def _baseline_summary(campaign: Mapping[str, Any]) -> dict[str, Any]:
    aggregate = campaign["aggregate"]
    manifest = campaign.get("manifest") or {}
    return {
        "label": campaign["label"],
        "path": str(campaign["path"]),
        "suite_id": aggregate.get("suite", {}).get("id"),
        "preset": manifest.get("preset", {}).get("name"),
        "counts": aggregate.get("counts", {}),
    }


def _baseline_lock(campaign: Mapping[str, Any]) -> dict[str, Any]:
    path = Path(campaign["path"])
    files = []
    for relative in ("aggregate.json", "suite-result.json", "campaign-manifest.json", "tables/runs.csv", "tables/failures.csv"):
        file_path = path / relative
        if file_path.exists():
            files.append({"path": str(file_path), "sha256": _sha256(file_path)})
    return {"label": campaign["label"], "path": str(path), "files": files}


def _failure_rows(campaign: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for run in campaign["aggregate"].get("runs", ()):
        if run.get("classification") not in FAILURE_CLASSES:
            continue
        rows.append(
            {
                "campaign": campaign["label"],
                "run_id": run.get("run_id"),
                "suite_id": run.get("suite_id"),
                "case_id": run.get("case_id"),
                "formula": run.get("formula"),
                "start_mode": run.get("start_mode"),
                "seed": run.get("seed"),
                "perturbation_noise": run.get("perturbation_noise"),
                "classification": run.get("classification"),
                "status": run.get("status"),
                "claim_status": run.get("claim_status"),
                "reason": run.get("reason"),
                "artifact_path": run.get("artifact_path"),
                "metrics": run.get("metrics", {}),
                "stage_statuses": run.get("stage_statuses", {}),
            }
        )
    return rows


def _group_failure_rows(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    counts: Counter[tuple[str, str, str, str]] = Counter()
    for row in rows:
        key = (
            str(row.get("formula")),
            str(row.get("start_mode")),
            str(row.get("perturbation_noise")),
            str(row.get("classification")),
        )
        counts[key] += 1
    return [
        {
            "formula": formula,
            "start_mode": start_mode,
            "perturbation_noise": perturbation_noise,
            "classification": classification,
            "count": count,
        }
        for (formula, start_mode, perturbation_noise, classification), count in sorted(counts.items())
    ]


def _filter_payload(run_filter: RunFilter) -> dict[str, list[Any]]:
    return {
        "formulas": list(run_filter.formulas),
        "start_modes": list(run_filter.start_modes),
        "case_ids": list(run_filter.case_ids),
        "seeds": list(run_filter.seeds),
        "perturbation_noises": list(run_filter.perturbation_noises),
    }


def _sorted_str(values: Iterable[Any]) -> tuple[str, ...]:
    return tuple(sorted({str(value) for value in values if value is not None}))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_sha256(path: Any, declared_sha256: Any = None) -> str | None:
    if not _is_durable_artifact_path(path):
        return None
    artifact_path = Path(str(path))
    if not artifact_path.is_file():
        return None
    actual_sha256 = _sha256(artifact_path)
    if declared_sha256 is not None and (
        not _is_sha256_hex(declared_sha256) or str(declared_sha256).lower() != actual_sha256
    ):
        return None
    return actual_sha256


def _is_durable_artifact_path(path: Any) -> bool:
    if not isinstance(path, str) or not path:
        return False
    artifact_path = Path(path)
    return not artifact_path.is_absolute() and ".." not in artifact_path.parts


def _is_sha256_hex(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    try:
        return f"{float(value):.4g}"
    except (TypeError, ValueError):
        return str(value)


def _category_rows(rows: Iterable[Mapping[str, Any]], category: str) -> list[Mapping[str, Any]]:
    row_list = list(rows)
    if category == "overall":
        return row_list
    if category == "blind_recovery":
        return [row for row in row_list if row.get("start_mode") == "blind"]
    if category == "beer_perturbation":
        return [row for row in row_list if row.get("formula") == "beer_lambert" and row.get("start_mode") == "warm_start"]
    if category == "compiler_coverage":
        formulas = {"michaelis_menten", "logistic", "shockley", "damped_oscillator", "planck"}
        return [row for row in row_list if row.get("formula") in formulas and row.get("start_mode") in {"compile", "warm_start"}]
    raise ValueError(f"unknown comparison category {category!r}")


def _compare_category(baseline_rows: list[Mapping[str, Any]], candidate_rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    baseline = _category_metrics(baseline_rows)
    candidate = _category_metrics(candidate_rows)
    delta = {
        key: _delta(candidate.get(key), baseline.get(key))
        for key in (
            "verifier_recovery_rate",
            "unsupported_rate",
            "failure_rate",
            "median_best_loss",
            "median_post_snap_loss",
            "median_runtime_seconds",
        )
    }
    return {
        "baseline": baseline,
        "candidate": candidate,
        "delta": delta,
        "verdict": _comparison_verdict(delta),
    }


def _category_metrics(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    recovered = sum(1 for row in rows if row.get("claim_status") == "recovered")
    unsupported = sum(1 for row in rows if row.get("classification") == "unsupported")
    failed = sum(1 for row in rows if row.get("classification") in {"failed", "snapped_but_failed", "soft_fit_only", "execution_failure"})
    return {
        "total": total,
        "verifier_recovered": recovered,
        "unsupported": unsupported,
        "failed": failed,
        "verifier_recovery_rate": recovered / total if total else 0.0,
        "unsupported_rate": unsupported / total if total else 0.0,
        "failure_rate": failed / total if total else 0.0,
        "median_best_loss": _median(_number_or_none(row.get("metrics", {}).get("best_loss")) for row in rows),
        "median_post_snap_loss": _median(_number_or_none(row.get("metrics", {}).get("post_snap_loss")) for row in rows),
        "median_runtime_seconds": _median(_runtime_seconds(row) for row in rows),
    }


def _comparison_verdict(delta: Mapping[str, float | None]) -> str:
    score = 0
    if (delta.get("verifier_recovery_rate") or 0.0) > 1e-12:
        score += 1
    elif (delta.get("verifier_recovery_rate") or 0.0) < -1e-12:
        score -= 1
    for key in ("unsupported_rate", "failure_rate"):
        value = delta.get(key)
        if value is None:
            continue
        if value < -1e-12:
            score += 1
        elif value > 1e-12:
            score -= 1
    if score > 0:
        return "improved"
    if score < 0:
        return "regressed"
    return "unchanged"


def _runtime_seconds(row: Mapping[str, Any]) -> float | None:
    artifact_path = row.get("artifact_path")
    if not artifact_path:
        return None
    try:
        payload = json.loads(Path(str(artifact_path)).read_text(encoding="utf-8"))
    except OSError:
        return None
    return _number_or_none(payload.get("timing", {}).get("elapsed_seconds"))


def _median(values: Iterable[float | None]) -> float | None:
    numeric = sorted(value for value in values if value is not None and math.isfinite(value))
    if not numeric:
        return None
    midpoint = len(numeric) // 2
    if len(numeric) % 2:
        return numeric[midpoint]
    return (numeric[midpoint - 1] + numeric[midpoint]) / 2


def _fmt_delta(value: Any) -> str:
    number = _number_or_none(value)
    if number is None:
        return "n/a"
    sign = "+" if number > 0 else ""
    return f"{sign}{number:.4g}"


def _comparison_command(baseline_dirs: tuple[Path, ...], candidate_dirs: tuple[Path, ...]) -> str:
    parts = ["PYTHONPATH=src", "python", "-m", "eml_symbolic_regression.cli", "diagnostics", "compare"]
    for baseline, candidate in zip(baseline_dirs, candidate_dirs):
        parts.extend(["--baseline", str(baseline), "--candidate", str(candidate)])
    parts.extend(["--output-dir", "artifacts/campaigns/comparison"])
    return " ".join(parts)


def _rows_from(value: Mapping[str, Any] | Iterable[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        return list(value.get("runs", ()))
    return list(value)


def _blind_rows(rows: Iterable[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    return [row for row in rows if row.get("start_mode") == "blind"]


def _blind_key(row: Mapping[str, Any]) -> tuple[str, str, int]:
    return (str(row.get("formula")), str(row.get("case_id")), int(row.get("seed") or 0))


def _number_or_none(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _delta(candidate: Any, baseline: Any) -> float | None:
    candidate_number = _number_or_none(candidate)
    baseline_number = _number_or_none(baseline)
    if candidate_number is None or baseline_number is None:
        return None
    if not math.isfinite(candidate_number) or not math.isfinite(baseline_number):
        return None
    return candidate_number - baseline_number


def _blind_improved(base: Mapping[str, Any], cand: Mapping[str, Any], best_delta: float | None, post_delta: float | None) -> bool:
    if base.get("claim_status") != "recovered" and cand.get("claim_status") == "recovered":
        return True
    if base.get("claim_status") == "recovered" and cand.get("claim_status") != "recovered":
        return False
    return bool((post_delta is not None and post_delta < 0.0) or (best_delta is not None and best_delta < 0.0))
