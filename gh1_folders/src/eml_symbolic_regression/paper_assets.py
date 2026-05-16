"""Deterministic paper figure and source-table assets for locked evidence."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any, Mapping, Sequence

from .paper_diagnostics import (
    DEFAULT_PAPER_DIAGNOSTICS_OUTPUT_DIR,
    DEFAULT_PROBE_AGGREGATE,
    DEFAULT_SCIENTIFIC_LAW_TABLE,
    DEFAULT_TRAINING_AGGREGATE,
)


DEFAULT_PAPER_ASSETS_OUTPUT_DIR = Path("artifacts") / "paper" / "v1.11" / "assets"
DEFAULT_DEPTH_CURVE_AGGREGATE = Path("artifacts") / "proof" / "v1.6" / "campaigns" / "proof-depth-curve" / "aggregate.json"


@dataclass(frozen=True)
class PaperAssetPaths:
    output_dir: Path
    manifest_json: Path
    table_json: Mapping[str, Path]
    table_csv: Mapping[str, Path]
    table_md: Mapping[str, Path]
    figures: Mapping[str, Path]
    figure_metadata: Mapping[str, Path]

    def as_dict(self) -> dict[str, Any]:
        return {
            "output_dir": str(self.output_dir),
            "manifest_json": str(self.manifest_json),
            "table_json": {key: str(value) for key, value in self.table_json.items()},
            "table_csv": {key: str(value) for key, value in self.table_csv.items()},
            "table_md": {key: str(value) for key, value in self.table_md.items()},
            "figures": {key: str(value) for key, value in self.figures.items()},
            "figure_metadata": {key: str(value) for key, value in self.figure_metadata.items()},
        }


def write_paper_assets(
    *,
    output_dir: Path = DEFAULT_PAPER_ASSETS_OUTPUT_DIR,
    scientific_law_table: Path = DEFAULT_SCIENTIFIC_LAW_TABLE,
    training_aggregate: Path = DEFAULT_TRAINING_AGGREGATE,
    probe_aggregate: Path = DEFAULT_PROBE_AGGREGATE,
    depth_curve_aggregate: Path = DEFAULT_DEPTH_CURVE_AGGREGATE,
    diagnostics_dir: Path = DEFAULT_PAPER_DIAGNOSTICS_OUTPUT_DIR,
) -> PaperAssetPaths:
    """Write v1.11 paper source tables, SVG figures, and metadata."""

    output_dir = Path(output_dir)
    tables_dir = output_dir / "tables"
    figures_dir = output_dir / "figures"
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    diagnostics_dir = Path(diagnostics_dir)
    scientific_payload = _read_json(scientific_law_table)
    training_payload = _read_json(training_aggregate)
    probe_payload = _read_json(probe_aggregate)
    depth_payload = _read_json(depth_curve_aggregate)
    diagnostics_manifest = _read_json(diagnostics_dir / "manifest.json")
    motif_payload = _read_json(diagnostics_dir / "motif-depth-deltas.json")
    baseline_payload = _read_json(diagnostics_dir / "baseline-diagnostics.json")

    table_rows = {
        "regime_recovery": regime_recovery_rows(
            (
                ("v1.11-paper-training", training_payload),
                ("v1.11-logistic-planck-probes", probe_payload),
            )
        ),
        "depth_degradation": depth_degradation_rows(depth_payload),
        "scientific_law_support": scientific_law_support_rows(scientific_payload),
        "motif_depth_deltas": list(motif_payload.get("rows", ())),
        "training_lifecycle": training_lifecycle_rows(
            (
                ("v1.11-paper-training", training_payload),
                ("v1.11-logistic-planck-probes", probe_payload),
            )
        ),
        "failure_taxonomy": failure_taxonomy_rows(
            (
                ("v1.11-paper-training", training_payload),
                ("v1.11-logistic-planck-probes", probe_payload),
            )
        ),
        "baseline_diagnostics": list(baseline_payload.get("rows", ())),
    }
    paths = _asset_paths(output_dir, table_rows)
    table_manifest: dict[str, Any] = {}
    for table_id, rows in table_rows.items():
        columns = _columns(rows)
        _write_json(paths.table_json[table_id], {"schema": "eml.paper_asset_table.v1", "columns": columns, "rows": rows})
        _write_csv(paths.table_csv[table_id], rows, columns)
        paths.table_md[table_id].write_text(_markdown_table(table_id.replace("_", " ").title(), rows, columns), encoding="utf-8")
        table_manifest[table_id] = {
            "json": str(paths.table_json[table_id]),
            "csv": str(paths.table_csv[table_id]),
            "markdown": str(paths.table_md[table_id]),
            "rows": len(rows),
            "columns": columns,
        }

    figure_specs = {
        "regime_recovery": {
            "title": "Verifier Recovery by Evidence Regime",
            "svg": _regime_recovery_svg(table_rows["regime_recovery"]),
            "table": "regime_recovery",
            "denominator": "group-local runs within each suite and start mode",
            "included_statuses": ["recovered", "unsupported", "failed"],
            "claim_boundary": "regimes remain separated; this is not a single blind-discovery denominator",
        },
        "depth_degradation": {
            "title": "Recovery Degradation with Depth",
            "svg": _depth_degradation_svg(table_rows["depth_degradation"]),
            "table": "depth_degradation",
            "denominator": "v1.6 proof-depth-curve rows grouped by depth and start mode",
            "included_statuses": ["recovered", "snapped_but_failed"],
            "claim_boundary": "depth-curve rows are historical boundary evidence, not v1.11 paper-training claims",
        },
        "scientific_law_support": {
            "title": "Scientific-Law Support Matrix",
            "svg": _scientific_law_support_svg(table_rows["scientific_law_support"]),
            "table": "scientific_law_support",
            "denominator": "one row per paper-package scientific-law entry",
            "included_statuses": ["supported", "unsupported", "recovered"],
            "claim_boundary": "unsupported diagnostic laws stay unsupported unless strict compile and verifier support pass",
        },
        "motif_depth_deltas": {
            "title": "Reusable Motif Compile-Depth Reduction",
            "svg": _motif_depth_deltas_svg(table_rows["motif_depth_deltas"]),
            "table": "motif_depth_deltas",
            "denominator": "rows with macro diagnostics and validation metadata",
            "included_statuses": ["supported", "unsupported"],
            "claim_boundary": "depth reduction is not recovery when strict support remains false",
        },
        "training_lifecycle": {
            "title": "Training Loss Before and After Snap",
            "svg": _training_lifecycle_svg(table_rows["training_lifecycle"]),
            "table": "training_lifecycle",
            "denominator": "v1.11 training and probe runs with recorded soft or post-snap losses",
            "included_statuses": ["recovered", "unsupported", "failed"],
            "claim_boundary": "low loss alone is never counted as recovered without verifier success",
        },
        "failure_taxonomy": {
            "title": "Unsupported and Failure Taxonomy",
            "svg": _failure_taxonomy_svg(table_rows["failure_taxonomy"]),
            "table": "failure_taxonomy",
            "denominator": "grouped unsupported or failed v1.11 runs",
            "included_statuses": ["unsupported", "failed", "snapped_but_failed"],
            "claim_boundary": "unsupported rows remain visible in the figure source table",
        },
        "baseline_diagnostics": {
            "title": "Prediction-Only Baseline Diagnostics",
            "svg": _baseline_diagnostics_svg(table_rows["baseline_diagnostics"]),
            "table": "baseline_diagnostics",
            "denominator": "local prediction-only baselines fit on deterministic demo splits",
            "included_statuses": ["ok", "unavailable"],
            "claim_boundary": "prediction-only baseline diagnostics do not enter EML symbolic-recovery denominators",
        },
    }

    figure_manifest: dict[str, Any] = {}
    for figure_id, spec in figure_specs.items():
        svg_path = paths.figures[figure_id]
        metadata_path = paths.figure_metadata[figure_id]
        svg_path.write_text(str(spec["svg"]), encoding="utf-8")
        metadata = {
            "schema": "eml.paper_figure_metadata.v1",
            "figure_id": figure_id,
            "title": spec["title"],
            "source_table_json": str(paths.table_json[str(spec["table"])]),
            "source_table_csv": str(paths.table_csv[str(spec["table"])]),
            "denominator": spec["denominator"],
            "included_statuses": spec["included_statuses"],
            "claim_boundary": spec["claim_boundary"],
        }
        _write_json(metadata_path, metadata)
        figure_manifest[figure_id] = {"svg": str(svg_path), "metadata": str(metadata_path), **metadata}

    sources = [
        _source_lock("scientific_law_table", scientific_law_table),
        _source_lock("training_aggregate", training_aggregate),
        _source_lock("probe_aggregate", probe_aggregate),
        _source_lock("depth_curve_aggregate", depth_curve_aggregate),
        _source_lock("diagnostics_manifest", diagnostics_dir / "manifest.json"),
        _source_lock("motif_depth_deltas", diagnostics_dir / "motif-depth-deltas.json"),
        _source_lock("baseline_diagnostics", diagnostics_dir / "baseline-diagnostics.json"),
    ]
    manifest = {
        "schema": "eml.paper_assets.v1",
        "generated_at": _now_iso(),
        "output_dir": str(output_dir),
        "sources": sources,
        "tables": table_manifest,
        "figures": figure_manifest,
        "counts": {
            "tables": len(table_manifest),
            "figures": len(figure_manifest),
            "source_locks": len(sources),
        },
        "source_diagnostics_schema": diagnostics_manifest.get("schema"),
        "claim_boundary": "paper assets visualize locked evidence and do not promote unsupported runs",
    }
    _write_json(paths.manifest_json, manifest)
    return paths


def regime_recovery_rows(aggregates: Sequence[tuple[str, Mapping[str, Any]]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for suite_id, aggregate in aggregates:
        group_rows = aggregate.get("groups", {}).get("start_mode", ()) if isinstance(aggregate.get("groups"), Mapping) else ()
        for row in group_rows:
            if not isinstance(row, Mapping):
                continue
            total = int(row.get("total") or 0)
            recovered = int(row.get("verifier_recovered") or 0)
            unsupported = int(row.get("unsupported") or 0)
            failed = int(row.get("failed") or 0) + int(row.get("execution_error") or 0)
            rows.append(
                {
                    "suite_id": suite_id,
                    "regime": row.get("key"),
                    "runs": total,
                    "verifier_recovered": recovered,
                    "same_ast_return": row.get("same_ast_return", 0),
                    "unsupported": unsupported,
                    "failed": failed,
                    "recovery_rate": _rate(recovered, total),
                    "unsupported_rate": _rate(unsupported, total),
                    "failure_rate": _rate(failed, total),
                    "evidence_classes": json.dumps(row.get("evidence_classes", {}), sort_keys=True),
                    "denominator_rule": "suite/start-mode-local runs",
                    "claim_boundary": "do not combine regimes into a blind-discovery denominator",
                }
            )
    return rows


def depth_degradation_rows(aggregate: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in aggregate.get("depth_curve", ()):
        if not isinstance(row, Mapping):
            continue
        rows.append(
            {
                "source": "v1.6-proof-depth-curve",
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
                "snap_min_margin_median": row.get("snap_min_margin_median"),
                "claim_boundary": "historical depth-boundary evidence; regimes remain separated",
            }
        )
    return rows


def scientific_law_support_rows(scientific_law_payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in scientific_law_payload.get("rows", ()):
        if not isinstance(row, Mapping):
            continue
        macro_hits = row.get("macro_hits") if isinstance(row.get("macro_hits"), list) else []
        compile_support = str(row.get("compile_support") or "")
        verifier_status = str(row.get("verifier_status") or "")
        rows.append(
            {
                "law": row.get("law"),
                "formula": row.get("formula"),
                "compile_support": compile_support,
                "compile_depth": row.get("compile_depth"),
                "macro_hits": ";".join(str(item) for item in macro_hits),
                "warm_start_status": row.get("warm_start_status"),
                "verifier_status": verifier_status,
                "evidence_regime": row.get("evidence_regime"),
                "strict_supported_and_verified": compile_support == "supported" and verifier_status == "recovered",
                "artifact_path": row.get("artifact_path"),
                "claim_boundary": "unsupported diagnostic laws are shown but not promoted",
            }
        )
    return rows


def training_lifecycle_rows(aggregates: Sequence[tuple[str, Mapping[str, Any]]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for suite_id, aggregate in aggregates:
        for run in aggregate.get("runs", ()):
            if not isinstance(run, Mapping):
                continue
            optimizer = run.get("optimizer") if isinstance(run.get("optimizer"), Mapping) else {}
            metrics = run.get("metrics") if isinstance(run.get("metrics"), Mapping) else {}
            rows.append(
                {
                    "suite_id": suite_id,
                    "run_id": run.get("run_id"),
                    "case_id": run.get("case_id"),
                    "formula": run.get("formula"),
                    "start_mode": run.get("start_mode"),
                    "evidence_class": run.get("evidence_class"),
                    "classification": run.get("classification"),
                    "status": run.get("status"),
                    "claim_status": run.get("claim_status"),
                    "depth": optimizer.get("depth"),
                    "steps": optimizer.get("steps"),
                    "best_loss": metrics.get("best_loss"),
                    "post_snap_loss": metrics.get("post_snap_loss"),
                    "snap_min_margin": metrics.get("snap_min_margin"),
                    "verifier_status": metrics.get("verifier_status"),
                    "artifact_path": run.get("artifact_path"),
                    "claim_boundary": "soft loss and snap loss are diagnostic until verifier-owned recovery passes",
                }
            )
    return rows


def failure_taxonomy_rows(aggregates: Sequence[tuple[str, Mapping[str, Any]]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str], int] = {}
    for suite_id, aggregate in aggregates:
        for run in aggregate.get("runs", ()):
            if not isinstance(run, Mapping):
                continue
            classification = str(run.get("classification") or run.get("evidence_class") or "unknown")
            if classification not in {"unsupported", "failed", "snapped_but_failed", "soft_fit_only", "execution_failure"}:
                continue
            key = (suite_id, str(run.get("formula") or ""), str(run.get("start_mode") or ""), classification)
            grouped[key] = grouped.get(key, 0) + 1
    return [
        {
            "suite_id": suite_id,
            "formula": formula,
            "start_mode": start_mode,
            "classification": classification,
            "count": count,
            "claim_boundary": "failure and unsupported rows stay visible",
        }
        for (suite_id, formula, start_mode, classification), count in sorted(grouped.items())
    ]


def _asset_paths(output_dir: Path, table_rows: Mapping[str, list[Mapping[str, Any]]]) -> PaperAssetPaths:
    table_json = {key: output_dir / "tables" / f"{key}.json" for key in table_rows}
    table_csv = {key: output_dir / "tables" / f"{key}.csv" for key in table_rows}
    table_md = {key: output_dir / "tables" / f"{key}.md" for key in table_rows}
    figure_keys = (
        "regime_recovery",
        "depth_degradation",
        "scientific_law_support",
        "motif_depth_deltas",
        "training_lifecycle",
        "failure_taxonomy",
        "baseline_diagnostics",
    )
    return PaperAssetPaths(
        output_dir=output_dir,
        manifest_json=output_dir / "manifest.json",
        table_json=table_json,
        table_csv=table_csv,
        table_md=table_md,
        figures={key: output_dir / "figures" / f"{key}.svg" for key in figure_keys},
        figure_metadata={key: output_dir / "figures" / f"{key}.metadata.json" for key in figure_keys},
    )


def _regime_recovery_svg(rows: list[Mapping[str, Any]]) -> str:
    bars = []
    for row in rows:
        label = f"{_short_suite(row.get('suite_id'))} {row.get('regime')}"
        rate = float(row.get("recovery_rate") or 0.0)
        bars.append({"label": label, "value": rate, "display": f"{int(row.get('verifier_recovered') or 0)}/{int(row.get('runs') or 0)}"})
    return _bar_chart_svg("Verifier Recovery by Evidence Regime", bars, y_label="verified recovered / runs", max_value=1.0)


def _depth_degradation_svg(rows: list[Mapping[str, Any]]) -> str:
    if not rows:
        return _empty_svg("Recovery Degradation with Depth", "No depth-curve rows available.")
    grouped: dict[str, list[tuple[float, float]]] = {}
    for row in rows:
        depth = _float_or_none(row.get("depth"))
        rate = _float_or_none(row.get("recovery_rate"))
        if depth is None or rate is None:
            continue
        grouped.setdefault(str(row.get("start_mode")), []).append((depth, rate))
    series = {key: sorted(values) for key, values in sorted(grouped.items())}
    return _line_chart_svg("Recovery Degradation with Depth", series, x_label="EML depth", y_label="recovered / runs")


def _scientific_law_support_svg(rows: list[Mapping[str, Any]]) -> str:
    if not rows:
        return _empty_svg("Scientific-Law Support Matrix", "No scientific-law rows available.", width=1080, height=420)
    width = 1080
    row_height = 42
    height = 96 + row_height * len(rows)
    left = 260
    headers = [("Compile", 430), ("Warm", 610), ("Verify", 790), ("Depth", 950)]
    parts = [_svg_header(width, height), '<text x="44" y="42" class="title">Scientific-Law Support Matrix</text>']
    parts.append('<text x="44" y="66" class="subtitle">Rows are generated from the v1.11 scientific-law source table.</text>')
    for label, x in headers:
        parts.append(f'<text x="{x}" y="92" class="axis-label">{escape(label)}</text>')
    for index, row in enumerate(rows):
        y = 118 + index * row_height
        law = str(row.get("law") or "")
        parts.append(f'<text x="44" y="{y + 22}" class="label">{escape(law)}</text>')
        _status_cell(parts, 430, y, str(row.get("compile_support") or "unknown"), row.get("compile_support") == "supported")
        warm_status = str(row.get("warm_start_status") or "unknown")
        _status_cell(parts, 610, y, warm_status, warm_status in {"same_ast_return", "verified_equivalent_ast", "recovered"})
        verify_status = str(row.get("verifier_status") or "unknown")
        _status_cell(parts, 790, y, verify_status, verify_status == "recovered")
        parts.append(f'<text x="950" y="{y + 22}" class="value">{escape(str(row.get("compile_depth") or ""))}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def _motif_depth_deltas_svg(rows: list[Mapping[str, Any]]) -> str:
    bars = []
    for row in rows:
        delta = _float_or_none(row.get("depth_delta"))
        if delta is None:
            continue
        bars.append(
            {
                "label": str(row.get("law") or ""),
                "value": delta,
                "display": f"{int(row.get('baseline_depth') or 0)}->{int(row.get('motif_depth') or 0)}",
            }
        )
    return _bar_chart_svg("Reusable Motif Compile-Depth Reduction", bars, y_label="baseline depth minus motif depth")


def _training_lifecycle_svg(rows: list[Mapping[str, Any]]) -> str:
    bars = []
    for row in rows:
        label = f"{row.get('formula')} {row.get('start_mode')}"
        best = _float_or_none(row.get("best_loss"))
        snapped = _float_or_none(row.get("post_snap_loss"))
        if best is not None:
            bars.append({"label": f"{label} best", "value": _loss_score(best), "display": _sci(best)})
        if snapped is not None:
            bars.append({"label": f"{label} snap", "value": _loss_score(snapped), "display": _sci(snapped)})
    return _bar_chart_svg(
        "Training Loss Before and After Snap",
        bars,
        y_label="-log10(loss), higher is lower loss",
        max_value=max((float(bar["value"]) for bar in bars), default=1.0),
        width=1180,
    )


def _failure_taxonomy_svg(rows: list[Mapping[str, Any]]) -> str:
    bars = [
        {
            "label": f"{row.get('formula')} {row.get('classification')}",
            "value": float(row.get("count") or 0.0),
            "display": str(row.get("count") or 0),
        }
        for row in rows
    ]
    return _bar_chart_svg("Unsupported and Failure Taxonomy", bars, y_label="run count", max_value=max((bar["value"] for bar in bars), default=1.0))


def _baseline_diagnostics_svg(rows: list[Mapping[str, Any]]) -> str:
    best_by_formula: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        if row.get("status") != "ok":
            continue
        formula = str(row.get("formula") or "")
        current = _float_or_none(row.get("extrapolation_mse"))
        if current is None:
            continue
        previous = best_by_formula.get(formula)
        previous_value = _float_or_none(previous.get("extrapolation_mse")) if previous else None
        if previous is None or previous_value is None or current < previous_value:
            best_by_formula[formula] = row
    bars = []
    for formula, row in sorted(best_by_formula.items()):
        mse = float(row.get("extrapolation_mse") or 0.0)
        bars.append(
            {
                "label": formula,
                "value": _loss_score(mse),
                "display": f"{row.get('baseline_name')} {_sci(mse)}",
            }
        )
    return _bar_chart_svg(
        "Best Prediction-Only Baseline Extrapolation Error",
        bars,
        y_label="-log10(extrapolation MSE), higher is lower error",
        max_value=max((float(bar["value"]) for bar in bars), default=1.0),
    )


def _bar_chart_svg(
    title: str,
    bars: list[Mapping[str, Any]],
    *,
    y_label: str,
    max_value: float | None = None,
    width: int = 960,
    height: int = 520,
) -> str:
    if not bars:
        return _empty_svg(title, "No data available.", width=width, height=height)
    left = 92
    right = 34
    top = 84
    bottom = 140
    plot_width = width - left - right
    plot_height = height - top - bottom
    baseline = top + plot_height
    max_seen = max(float(bar.get("value") or 0.0) for bar in bars)
    scale_max = max(max_value or max_seen, max_seen, 1e-12)
    slot = plot_width / len(bars)
    bar_width = max(8, min(52, slot * 0.56))
    palette = ["#146c94", "#d1495b", "#2a9d8f", "#e9c46a", "#4d908e", "#8f5d5d", "#577590"]

    parts = [_svg_header(width, height), f'<text x="{left}" y="42" class="title">{escape(title)}</text>']
    parts.append(f'<text x="{left}" y="65" class="subtitle">{escape(y_label)}</text>')
    parts.append(f'<line x1="{left}" y1="{baseline}" x2="{width - right}" y2="{baseline}" class="axis" />')
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{baseline}" class="axis" />')
    for tick in range(5):
        value = scale_max * tick / 4
        y = baseline - (value / scale_max * plot_height)
        parts.append(f'<line x1="{left - 5}" y1="{y:.2f}" x2="{width - right}" y2="{y:.2f}" class="grid" />')
        parts.append(f'<text x="{left - 12}" y="{y + 4:.2f}" class="tick" text-anchor="end">{_tick(value)}</text>')
    for index, bar in enumerate(bars):
        value = float(bar.get("value") or 0.0)
        h = value / scale_max * plot_height if scale_max else 0.0
        x = left + index * slot + (slot - bar_width) / 2
        y = baseline - h
        color = palette[index % len(palette)]
        label = escape(str(bar.get("label", "")))
        display = escape(str(bar.get("display", f"{value:.3g}")))
        parts.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_width:.2f}" height="{h:.2f}" fill="{color}" rx="3" />')
        parts.append(f'<text x="{x + bar_width / 2:.2f}" y="{max(y - 8, top - 8):.2f}" class="value" text-anchor="middle">{display}</text>')
        parts.append(
            f'<text x="{x + bar_width / 2:.2f}" y="{baseline + 22}" class="label" text-anchor="end" '
            f'transform="rotate(-36 {x + bar_width / 2:.2f} {baseline + 22})">{label}</text>'
        )
    parts.append("</svg>")
    return "\n".join(parts)


def _line_chart_svg(
    title: str,
    series: Mapping[str, list[tuple[float, float]]],
    *,
    x_label: str,
    y_label: str,
    width: int = 960,
    height: int = 520,
) -> str:
    if not series:
        return _empty_svg(title, "No numeric rows available.", width=width, height=height)
    left = 92
    right = 44
    top = 84
    bottom = 92
    plot_width = width - left - right
    plot_height = height - top - bottom
    baseline = top + plot_height
    all_x = [point[0] for values in series.values() for point in values]
    min_x = min(all_x)
    max_x = max(all_x)
    if min_x == max_x:
        max_x = min_x + 1.0
    palette = ["#146c94", "#d1495b", "#2a9d8f", "#e9c46a"]
    parts = [_svg_header(width, height), f'<text x="{left}" y="42" class="title">{escape(title)}</text>']
    parts.append(f'<text x="{left}" y="65" class="subtitle">{escape(y_label)}</text>')
    parts.append(f'<line x1="{left}" y1="{baseline}" x2="{width - right}" y2="{baseline}" class="axis" />')
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{baseline}" class="axis" />')
    for tick in range(5):
        value = tick / 4
        y = baseline - value * plot_height
        parts.append(f'<line x1="{left - 5}" y1="{y:.2f}" x2="{width - right}" y2="{y:.2f}" class="grid" />')
        parts.append(f'<text x="{left - 12}" y="{y + 4:.2f}" class="tick" text-anchor="end">{value:.2g}</text>')
    parts.append(f'<text x="{width / 2:.2f}" y="{height - 24}" class="axis-label" text-anchor="middle">{escape(x_label)}</text>')
    for index, (name, points) in enumerate(series.items()):
        color = palette[index % len(palette)]
        coords = []
        for x_value, y_value in points:
            x = left + ((x_value - min_x) / (max_x - min_x)) * plot_width
            y = baseline - max(0.0, min(1.0, y_value)) * plot_height
            coords.append((x, y))
        point_str = " ".join(f"{x:.2f},{y:.2f}" for x, y in coords)
        parts.append(f'<polyline points="{point_str}" fill="none" stroke="{color}" stroke-width="3" />')
        for x, y in coords:
            parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="{color}" />')
        legend_y = 92 + index * 22
        parts.append(f'<rect x="{width - 190}" y="{legend_y - 11}" width="14" height="14" fill="{color}" rx="2" />')
        parts.append(f'<text x="{width - 168}" y="{legend_y}" class="label">{escape(name)}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def _status_cell(parts: list[str], x: int, y: int, label: str, ok: bool) -> None:
    fill = "#2a9d8f" if ok else ("#d1495b" if label in {"unsupported", "failed"} else "#e9c46a")
    parts.append(f'<rect x="{x}" y="{y}" width="138" height="28" fill="{fill}" rx="4" />')
    parts.append(f'<text x="{x + 69}" y="{y + 18}" class="cell" text-anchor="middle">{escape(label)}</text>')


def _empty_svg(title: str, message: str, *, width: int = 960, height: int = 520) -> str:
    return "\n".join(
        [
            _svg_header(width, height),
            f'<text x="64" y="52" class="title">{escape(title)}</text>',
            f'<text x="64" y="92" class="subtitle">{escape(message)}</text>',
            "</svg>",
        ]
    )


def _svg_header(width: int, height: int) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">
<style>
  .title {{ font: 700 24px sans-serif; fill: #1d252c; }}
  .subtitle {{ font: 400 14px sans-serif; fill: #4b5563; }}
  .axis {{ stroke: #28343d; stroke-width: 1.3; }}
  .axis-label {{ font: 700 13px sans-serif; fill: #1d252c; }}
  .grid {{ stroke: #d7dde3; stroke-width: 1; }}
  .tick {{ font: 12px sans-serif; fill: #51606d; }}
  .label {{ font: 12px sans-serif; fill: #1d252c; }}
  .value {{ font: 700 11px sans-serif; fill: #1d252c; }}
  .cell {{ font: 700 11px sans-serif; fill: #ffffff; }}
</style>'''


def _short_suite(value: Any) -> str:
    text = str(value or "")
    return text.replace("v1.11-", "").replace("-training", "").replace("-probes", "")


def _loss_score(loss: float) -> float:
    return max(0.0, -math.log10(max(float(loss), 1e-16)))


def _sci(value: float) -> str:
    return f"{float(value):.1e}"


def _tick(value: float) -> str:
    return f"{value:.2g}"


def _float_or_none(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _rate(count: int, total: int) -> float:
    return count / total if total else 0.0


def _columns(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    columns: list[str] = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(str(key))
    return columns


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]], columns: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: _csv_value(row.get(column)) for column in columns})


def _markdown_table(title: str, rows: Sequence[Mapping[str, Any]], columns: Sequence[str]) -> str:
    lines = [f"# {title}", ""]
    if not columns:
        lines.extend(["No rows.", ""])
        return "\n".join(lines)
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("| " + " | ".join("---" for _ in columns) + " |")
    for row in rows:
        lines.append("| " + " | ".join(str(_csv_value(row.get(column))).replace("|", "\\|") for column in columns) + " |")
    lines.append("")
    return "\n".join(lines)


def _csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return f"{value:.12g}" if math.isfinite(value) else str(value)
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True)
    return value


def _read_json(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _source_lock(source_id: str, path: Path) -> dict[str, str]:
    return {"source_id": source_id, "path": str(path), "sha256": _sha256(path)}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
