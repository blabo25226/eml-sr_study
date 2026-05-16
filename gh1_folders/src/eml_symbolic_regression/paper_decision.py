"""Paper-facing decision memo generation for centered-family evidence."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping


DEFAULT_PAPER_OUTPUT_ROOT = Path("artifacts") / "paper" / "v1.8"

SAFE_CLAIMS = (
    "cEML_{s,t} is an affine-normalized transport of raw EML that preserves the exp-log inverse-pair structure.",
    "At the neutral point (0,t), cEML_{s,t} has output 0 and local Jacobian (+1,-1).",
    "The scale s is a curvature knob: local second derivatives shrink as s grows.",
    "The inverse-branch singularity is shifted to y=t-s, so singularity distance is a measurable diagnostic.",
    "On bounded boxes away from the shifted singularity, the large-s limit approaches subtraction.",
)

UNSAFE_CLAIMS = (
    "Do not claim CEML_s is complete for all s>0 without constructive witnesses or proof.",
    "Do not claim ZEML_s is a terminal-1 completeness replacement; closed zero-terminal trees collapse to zero.",
    "Do not claim centered families universally solve blind symbolic regression.",
    "Do not claim the centered family is a drop-in pocket-calculator basis until interdefinability is proved.",
    "Do not merge pure blind, scaffolded, compile-only, warm-start, repaired, and perturbed-basin evidence into one recovery metric.",
)

FIGURE_TABLE_INVENTORY = (
    "Headline figure: exact recovery versus depth, raw EML versus fixed CEML_s/ZEML_s and continuation schedules.",
    "Recovery table: exact recovery rate by formula, start mode, training mode, operator family, schedule, and depth.",
    "Diagnostics table: anomaly rates, shifted-singularity proximity, post-snap verifier pass rate, and unsupported rate.",
    "Repair/refit table: repair attempt rate, repair acceptance, refit attempt rate, and refit acceptance.",
    "Overhead table: active node count and candidate complexity by operator family and formula.",
)


@dataclass(frozen=True)
class PaperDecisionPaths:
    output_dir: Path
    decision_json: Path
    decision_markdown: Path
    safe_claims: Path
    unsafe_claims: Path
    figure_inventory: Path
    completeness_boundary: Path

    def as_dict(self) -> dict[str, str]:
        return {
            "output_dir": str(self.output_dir),
            "decision_json": str(self.decision_json),
            "decision_markdown": str(self.decision_markdown),
            "safe_claims": str(self.safe_claims),
            "unsafe_claims": str(self.unsafe_claims),
            "figure_inventory": str(self.figure_inventory),
            "completeness_boundary": str(self.completeness_boundary),
        }


def write_paper_decision_package(
    aggregate_paths: Iterable[Path] = (),
    *,
    output_dir: Path = DEFAULT_PAPER_OUTPUT_ROOT,
) -> PaperDecisionPaths:
    """Write the current paper decision package and return generated paths."""

    aggregates = [_load_aggregate(path) for path in aggregate_paths]
    summary = _summarize_aggregates(aggregates)
    decision = _decision_payload(summary)

    paths = PaperDecisionPaths(
        output_dir=output_dir,
        decision_json=output_dir / "decision-memo.json",
        decision_markdown=output_dir / "decision-memo.md",
        safe_claims=output_dir / "safe-claims.md",
        unsafe_claims=output_dir / "unsafe-claims.md",
        figure_inventory=output_dir / "figure-table-inventory.md",
        completeness_boundary=output_dir / "completeness-boundary.md",
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(paths.decision_json, decision)
    paths.decision_markdown.write_text(_decision_markdown(decision), encoding="utf-8")
    paths.safe_claims.write_text(_claims_doc("Safe Claims", SAFE_CLAIMS, summary), encoding="utf-8")
    paths.unsafe_claims.write_text(_claims_doc("Unsafe Claims", UNSAFE_CLAIMS, summary), encoding="utf-8")
    paths.figure_inventory.write_text(_bulleted_doc("Figure and Table Inventory", FIGURE_TABLE_INVENTORY), encoding="utf-8")
    paths.completeness_boundary.write_text(_completeness_boundary_markdown(summary), encoding="utf-8")
    return paths


def _load_aggregate(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["_source_path"] = str(path)
    return payload


def _summarize_aggregates(aggregates: list[Mapping[str, Any]]) -> dict[str, Any]:
    runs = [run for aggregate in aggregates for run in aggregate.get("runs", ())]
    groups: dict[str, dict[str, Any]] = {}
    for run in runs:
        operator = _operator_family_label(run)
        item = groups.setdefault(operator, {"total": 0, "recovered": 0, "unsupported": 0, "families": set(), "schedules": set()})
        item["total"] += 1
        if run.get("claim_status") == "recovered":
            item["recovered"] += 1
        if str(run.get("classification") or run.get("evidence_class")) == "unsupported":
            item["unsupported"] += 1
        item["families"].add(operator)
        schedule = _operator_schedule_label(run)
        if schedule:
            item["schedules"].add(schedule)

    serial_groups = {
        operator: {
            "total": values["total"],
            "recovered": values["recovered"],
            "unsupported": values["unsupported"],
            "recovery_rate": _rate(values["recovered"], values["total"]),
            "unsupported_rate": _rate(values["unsupported"], values["total"]),
            "schedules": sorted(values["schedules"]),
        }
        for operator, values in sorted(groups.items())
    }
    centered = {key: value for key, value in serial_groups.items() if key != "raw_eml"}
    return {
        "aggregate_paths": [aggregate.get("_source_path") for aggregate in aggregates],
        "run_count": len(runs),
        "operator_groups": serial_groups,
        "has_centered_evidence": bool(centered),
        "raw_recovery_rate": serial_groups.get("raw_eml", {}).get("recovery_rate"),
        "best_centered_recovery_rate": max((value["recovery_rate"] for value in centered.values()), default=None),
    }


def _decision_payload(summary: Mapping[str, Any]) -> dict[str, Any]:
    raw_rate = summary.get("raw_recovery_rate")
    centered_rate = summary.get("best_centered_recovery_rate")
    if not summary.get("has_centered_evidence"):
        decision = "wait_for_centered_family_evidence"
        recommendation = (
            "Do not submit the centered-family empirical paper yet. Run the current family campaigns first; "
            "a raw-EML searchability/geometry note remains publishable from the archived proof evidence."
        )
    elif centered_rate is not None and raw_rate is not None and float(centered_rate) > float(raw_rate):
        decision = "publish_robustness_geometry_paper_now"
        recommendation = (
            "Publish a robustness/geometry paper centered on the operator-family comparison. Keep completeness claims out "
            "unless constructive witnesses are added."
        )
    elif raw_rate is not None and float(raw_rate) > 0.0:
        decision = "publish_raw_eml_searchability_note"
        recommendation = (
            "Do not position the centered family as an empirical improvement. The v1.8 aggregates support a raw-EML "
            "searchability/geometry note with centered variants reported as negative or diagnostic evidence."
        )
    else:
        decision = "abandon_or_pivot_centered_family_work"
        recommendation = (
            "The supplied aggregates do not support a centered-family improvement or a positive raw-EML paper claim. "
            "Use the results as a pivot signal before spending more full-campaign budget."
        )
    return {
        "schema": "eml.paper_decision.v1",
        "decision": decision,
        "recommendation": recommendation,
        "evidence_summary": dict(summary),
        "safe_claims": list(SAFE_CLAIMS),
        "unsafe_claims": list(UNSAFE_CLAIMS),
        "figure_table_inventory": list(FIGURE_TABLE_INVENTORY),
        "completeness_boundary": {
            "status": "incomplete",
            "ceml_s_successor_claim": "not_established",
            "zeml_s_terminal_zero_limitation": "closed zero-terminal ZEML_s trees do not generate new constants",
        },
    }


def _decision_markdown(payload: Mapping[str, Any]) -> str:
    summary = payload["evidence_summary"]
    lines = [
        "# v1.8 Paper Decision Memo",
        "",
        f"**Decision:** `{payload['decision']}`",
        "",
        str(payload["recommendation"]),
        "",
        "## Evidence Summary",
        "",
        f"- Aggregate files: {len(summary.get('aggregate_paths', []))}",
        f"- Runs summarized: {summary.get('run_count', 0)}",
        f"- Centered-family evidence present: {summary.get('has_centered_evidence')}",
        f"- Raw recovery rate: {_format_rate(summary.get('raw_recovery_rate'))}",
        f"- Best centered recovery rate: {_format_rate(summary.get('best_centered_recovery_rate'))}",
        "",
        "## Operator Groups",
        "",
        "| Operator | Runs | Recovered | Recovery Rate | Unsupported Rate | Schedules |",
        "|----------|------|-----------|---------------|------------------|-----------|",
    ]
    for operator, row in summary.get("operator_groups", {}).items():
        lines.append(
            f"| {operator} | {row['total']} | {row['recovered']} | {_format_rate(row['recovery_rate'])} | "
            f"{_format_rate(row['unsupported_rate'])} | {', '.join(row['schedules']) or 'fixed'} |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "Centered-family mathematical claims are safe only at the operator/geometry level until constructive completeness is supplied.",
            "Empirical recovery claims require v1.8 family campaign aggregates and must keep regimes separate.",
            "",
        ]
    )
    return "\n".join(lines)


def _completeness_boundary_markdown(summary: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Completeness Boundary",
            "",
            "**Status:** incomplete",
            "",
            "- `CEML_s` successor/completeness is not established by this milestone.",
            "- `ZEML_s` is a training-centered form, not a terminal-1 completeness replacement.",
            "- Constructive interdefinability search outputs are not present in the supplied aggregates.",
            "- Any future witness search must record `s`, terminal convention, exact AST, verification backend, and failure cases.",
            f"- Centered empirical evidence present in supplied aggregates: {summary.get('has_centered_evidence')}",
            "",
        ]
    )


def _claims_doc(title: str, items: Iterable[str], summary: Mapping[str, Any]) -> str:
    lines = [f"# {title}", ""]
    lines.extend(
        [
            "## Evidence Inputs",
            "",
            "These claims are scoped to the supplied aggregate files:",
            "",
        ]
    )
    aggregate_paths = [path for path in summary.get("aggregate_paths", ()) if path]
    if aggregate_paths:
        lines.extend(f"- `{path}`" for path in aggregate_paths)
    else:
        lines.append("- No aggregate paths supplied")
    lines.extend(["", "## Claims", ""])
    lines.extend(f"- {item}" for item in items)
    lines.append("")
    return "\n".join(lines)


def _bulleted_doc(title: str, items: Iterable[str]) -> str:
    lines = [f"# {title}", ""]
    lines.extend(f"- {item}" for item in items)
    lines.append("")
    return "\n".join(lines)


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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


def _rate(count: int, total: int) -> float:
    return count / total if total else 0.0


def _format_rate(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.1%}"
