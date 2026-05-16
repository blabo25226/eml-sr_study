"""Centered-family triage and v1.8 evidence-scope artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping


DEFAULT_TRIAGE_OUTPUT_DIR = Path("artifacts") / "diagnostics" / "v1.8-family-triage"
DEFAULT_EVIDENCE_OUTPUT_DIR = Path("artifacts") / "diagnostics" / "v1.8-family-evidence"


@dataclass(frozen=True)
class FamilyTriagePaths:
    output_dir: Path
    json_path: Path
    markdown_path: Path
    go_no_go_path: Path

    def as_dict(self) -> dict[str, str]:
        return {
            "output_dir": str(self.output_dir),
            "json_path": str(self.json_path),
            "markdown_path": str(self.markdown_path),
            "go_no_go_path": str(self.go_no_go_path),
        }


@dataclass(frozen=True)
class FamilyEvidenceManifestPaths:
    output_dir: Path
    json_path: Path
    markdown_path: Path

    def as_dict(self) -> dict[str, str]:
        return {
            "output_dir": str(self.output_dir),
            "json_path": str(self.json_path),
            "markdown_path": str(self.markdown_path),
        }


def write_family_triage(
    *,
    smoke_aggregate: Path,
    calibration_aggregate: Path | None = None,
    output_dir: Path = DEFAULT_TRIAGE_OUTPUT_DIR,
) -> FamilyTriagePaths:
    """Write centered-family smoke/calibration triage and go/no-go artifacts."""

    smoke = _load_aggregate(smoke_aggregate)
    calibration = _load_aggregate(calibration_aggregate) if calibration_aggregate is not None else None
    smoke_items = [_classification_for_run(run, source="smoke") for run in smoke.get("runs", ())]
    calibration_items = (
        [_classification_for_run(run, source="calibration") for run in calibration.get("runs", ())]
        if calibration is not None
        else []
    )
    payload = {
        "schema": "eml.family_triage.v1",
        "inputs": {
            "smoke_aggregate": str(smoke_aggregate),
            "calibration_aggregate": str(calibration_aggregate) if calibration_aggregate is not None else None,
        },
        "smoke": _aggregate_snapshot(smoke),
        "calibration": _aggregate_snapshot(calibration) if calibration is not None else None,
        "classifications": smoke_items + calibration_items,
        "go_no_go": _go_no_go(smoke_items, calibration_items),
    }

    paths = FamilyTriagePaths(
        output_dir=output_dir,
        json_path=output_dir / "family-triage.json",
        markdown_path=output_dir / "family-triage.md",
        go_no_go_path=output_dir / "go-no-go.md",
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(paths.json_path, payload)
    paths.markdown_path.write_text(_triage_markdown(payload), encoding="utf-8")
    paths.go_no_go_path.write_text(_go_no_go_markdown(payload), encoding="utf-8")
    return paths


def write_family_evidence_manifest(
    *,
    completed_campaigns: Iterable[Mapping[str, Any]],
    scoped_campaigns: Iterable[Mapping[str, Any]],
    output_dir: Path = DEFAULT_EVIDENCE_OUTPUT_DIR,
) -> FamilyEvidenceManifestPaths:
    """Write a manifest that distinguishes executed campaigns from deliberate scope decisions."""

    completed = [_campaign_entry(item, completed=True) for item in completed_campaigns]
    scoped = [_campaign_entry(item, completed=False) for item in scoped_campaigns]
    payload = {
        "schema": "eml.family_evidence_manifest.v1",
        "completed_campaigns": completed,
        "scoped_campaigns": scoped,
        "counts": {
            "completed": len(completed),
            "scoped": len(scoped),
            "with_regression_locks": sum(1 for item in completed if item.get("operator_family_locks_json")),
        },
    }

    paths = FamilyEvidenceManifestPaths(
        output_dir=output_dir,
        json_path=output_dir / "family-evidence-manifest.json",
        markdown_path=output_dir / "family-evidence-manifest.md",
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(paths.json_path, payload)
    paths.markdown_path.write_text(_evidence_manifest_markdown(payload), encoding="utf-8")
    return paths


def _load_aggregate(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["_source_path"] = str(path)
    return payload


def _aggregate_snapshot(aggregate: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if aggregate is None:
        return None
    counts = aggregate.get("counts") if isinstance(aggregate.get("counts"), Mapping) else {}
    return {
        "source_path": aggregate.get("_source_path"),
        "suite_id": (aggregate.get("suite") or {}).get("id") if isinstance(aggregate.get("suite"), Mapping) else None,
        "total": counts.get("total", 0),
        "verifier_recovered": counts.get("verifier_recovered", 0),
        "unsupported": counts.get("unsupported", 0),
        "failed": counts.get("failed", 0),
        "verifier_recovery_rate": counts.get("verifier_recovery_rate", 0.0),
    }


def _classification_for_run(run: Mapping[str, Any], *, source: str) -> dict[str, Any]:
    operator = _operator_family_label(run)
    schedule = _operator_schedule_label(run)
    reason = str(run.get("reason") or run.get("status") or "unknown")
    start_mode = str(run.get("start_mode") or "unknown")
    status = str(run.get("status") or "unknown")
    claim_status = str(run.get("claim_status") or status)
    centered = operator != "raw_eml"
    if status == "unsupported" and reason in {"centered_family_warm_start_rules_missing", "centered_family_same_family_seed_missing"}:
        category = "missing_integration"
        action = "accepted_fail_closed_until_same_family_seed_exists"
    elif status == "unsupported" and reason == "centered_family_target_seed_missing":
        category = "missing_integration"
        action = "accepted_fail_closed_until_same_family_target_exists"
    elif status == "unsupported" and reason == "depth_exceeded":
        category = "accepted_exclusion"
        action = "keep_stretch_depth_gate_in_denominator"
    elif centered and start_mode == "blind" and claim_status != "recovered":
        category = "budget_or_operator_behavior"
        action = "use_calibration_before_full_blind_campaign"
    elif claim_status == "recovered":
        category = "trusted_positive"
        action = "usable_as_recovery_evidence"
    else:
        category = "measured_failure"
        action = "keep_in_denominator_and_compare_by_regime"
    return {
        "source": source,
        "run_id": run.get("run_id"),
        "case_id": run.get("case_id"),
        "formula": run.get("formula"),
        "start_mode": start_mode,
        "training_mode": run.get("training_mode"),
        "operator_family": operator,
        "operator_schedule": schedule,
        "status": status,
        "claim_status": claim_status,
        "classification": run.get("classification"),
        "reason": reason,
        "category": category,
        "action": action,
        "artifact_path": run.get("artifact_path"),
    }


def _go_no_go(smoke_items: list[Mapping[str, Any]], calibration_items: list[Mapping[str, Any]]) -> dict[str, Any]:
    missing_integration = [item for item in smoke_items if item.get("category") == "missing_integration"]
    centered_calibration = [item for item in calibration_items if item.get("operator_family") != "raw_eml"]
    centered_calibration_recovered = [item for item in centered_calibration if item.get("claim_status") == "recovered"]
    accepted_exclusions = [item for item in smoke_items if item.get("category") == "accepted_exclusion"]
    if missing_integration:
        verdict = "conditional_go_scoped"
        recommendation = (
            "Proceed only with campaigns whose centered paths are explicitly supported or fail-closed; "
            "do not treat centered warm-start unsupported rows as recovery failures hidden from denominators."
        )
    elif centered_calibration and not centered_calibration_recovered:
        verdict = "go_with_negative_signal"
        recommendation = "Proceed with measured negative centered-family evidence and keep claims conservative."
    else:
        verdict = "go"
        recommendation = "Proceed with full family campaigns under the expanded v1.8 matrix."
    return {
        "verdict": verdict,
        "recommendation": recommendation,
        "missing_integration_count": len(missing_integration),
        "accepted_exclusion_count": len(accepted_exclusions),
        "centered_calibration_runs": len(centered_calibration),
        "centered_calibration_recovered": len(centered_calibration_recovered),
        "fixed_blockers": [],
        "accepted_exclusions": sorted({str(item.get("reason")) for item in accepted_exclusions}),
        "remaining_risks": [
            "centered warm-start needs same-family exact seeds before it can become supported evidence",
            "centered blind exp/log calibration may reflect search geometry rather than implementation support",
            "Planck compile depth remains a stretch-target exclusion across raw and centered families",
        ],
    }


def _campaign_entry(item: Mapping[str, Any], *, completed: bool) -> dict[str, Any]:
    entry = {
        "name": item.get("name"),
        "status": "completed" if completed else "scoped",
        "aggregate_json": item.get("aggregate_json"),
        "report_markdown": item.get("report_markdown"),
        "operator_family_locks_json": item.get("operator_family_locks_json"),
        "reproduction_command": item.get("reproduction_command"),
        "scope_reason": item.get("scope_reason"),
    }
    return {key: value for key, value in entry.items() if value not in (None, "")}


def _operator_family_label(run: Mapping[str, Any]) -> str:
    metrics = run.get("metrics") if isinstance(run.get("metrics"), Mapping) else {}
    if metrics.get("operator_family"):
        return str(metrics["operator_family"])
    optimizer = run.get("optimizer") if isinstance(run.get("optimizer"), Mapping) else {}
    operator = optimizer.get("operator_family") if isinstance(optimizer.get("operator_family"), Mapping) else {}
    return str(operator.get("label") or operator.get("family") or "raw_eml")


def _operator_schedule_label(run: Mapping[str, Any]) -> str:
    metrics = run.get("metrics") if isinstance(run.get("metrics"), Mapping) else {}
    if metrics.get("operator_schedule"):
        return str(metrics["operator_schedule"])
    optimizer = run.get("optimizer") if isinstance(run.get("optimizer"), Mapping) else {}
    schedule = optimizer.get("operator_schedule")
    if isinstance(schedule, list) and schedule:
        return " -> ".join(str(item.get("label") or item.get("family") or "") for item in schedule if isinstance(item, Mapping))
    return "fixed"


def _triage_markdown(payload: Mapping[str, Any]) -> str:
    lines = [
        "# v1.8 Centered-Family Triage",
        "",
        "## Inputs",
        "",
        f"- Smoke aggregate: `{payload['inputs']['smoke_aggregate']}`",
        f"- Calibration aggregate: `{payload['inputs'].get('calibration_aggregate') or 'not supplied'}`",
        "",
        "## Go/No-Go",
        "",
        f"- Verdict: `{payload['go_no_go']['verdict']}`",
        f"- Recommendation: {payload['go_no_go']['recommendation']}",
        f"- Missing integration rows: {payload['go_no_go']['missing_integration_count']}",
        f"- Accepted exclusions: {payload['go_no_go']['accepted_exclusion_count']}",
        f"- Centered calibration recovered: {payload['go_no_go']['centered_calibration_recovered']}/{payload['go_no_go']['centered_calibration_runs']}",
        "",
        "## Classifications",
        "",
        "| Source | Case | Operator | Schedule | Mode | Status | Category | Reason | Action |",
        "|--------|------|----------|----------|------|--------|----------|--------|--------|",
    ]
    for item in payload.get("classifications", ()):
        lines.append(
            f"| {item['source']} | {item.get('case_id')} | {item.get('operator_family')} | {item.get('operator_schedule')} | "
            f"{item.get('start_mode')} | {item.get('status')} | {item.get('category')} | {item.get('reason')} | {item.get('action')} |"
        )
    lines.append("")
    return "\n".join(lines)


def _go_no_go_markdown(payload: Mapping[str, Any]) -> str:
    gate = payload["go_no_go"]
    lines = [
        "# v1.8 Family Full-Run Gate",
        "",
        f"**Verdict:** `{gate['verdict']}`",
        "",
        gate["recommendation"],
        "",
        "## Accepted Exclusions",
        "",
    ]
    lines.extend(f"- {item}" for item in gate.get("accepted_exclusions", ()))
    if not gate.get("accepted_exclusions"):
        lines.append("- None")
    lines.extend(["", "## Remaining Risks", ""])
    lines.extend(f"- {item}" for item in gate.get("remaining_risks", ()))
    lines.append("")
    return "\n".join(lines)


def _evidence_manifest_markdown(payload: Mapping[str, Any]) -> str:
    lines = [
        "# v1.8 Family Evidence Manifest",
        "",
        f"- Completed campaigns: {payload['counts']['completed']}",
        f"- Scoped campaigns: {payload['counts']['scoped']}",
        f"- Completed campaigns with regression locks: {payload['counts']['with_regression_locks']}",
        "",
        "## Completed",
        "",
        "| Campaign | Aggregate | Locks | Command |",
        "|----------|-----------|-------|---------|",
    ]
    for item in payload.get("completed_campaigns", ()):
        lines.append(
            f"| {item.get('name')} | `{item.get('aggregate_json', '')}` | `{item.get('operator_family_locks_json', '')}` | "
            f"`{item.get('reproduction_command', '')}` |"
        )
    if not payload.get("completed_campaigns"):
        lines.append("| None |  |  |  |")
    lines.extend(["", "## Scoped", "", "| Campaign | Reason |", "|----------|--------|"])
    for item in payload.get("scoped_campaigns", ()):
        lines.append(f"| {item.get('name')} | {item.get('scope_reason', '')} |")
    if not payload.get("scoped_campaigns"):
        lines.append("| None |  |")
    lines.append("")
    return "\n".join(lines)


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
