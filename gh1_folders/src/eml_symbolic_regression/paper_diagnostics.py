"""Paper-facing ablation and baseline diagnostics from locked evidence artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np

from .datasets import get_demo


DEFAULT_PAPER_DIAGNOSTICS_OUTPUT_DIR = Path("artifacts") / "diagnostics" / "v1.11-paper-ablations"
DEFAULT_SCIENTIFIC_LAW_TABLE = Path("artifacts") / "paper" / "v1.11" / "raw-hybrid" / "scientific-law-table.json"
DEFAULT_TRAINING_AGGREGATE = Path("artifacts") / "campaigns" / "v1.11-paper-training" / "aggregate.json"
DEFAULT_PROBE_AGGREGATE = Path("artifacts") / "campaigns" / "v1.11-logistic-planck-probes" / "aggregate.json"
DEFAULT_REPAIR_SUMMARY = Path("artifacts") / "campaigns" / "v1.9-repair-evidence" / "repair-evidence-summary.json"


@dataclass(frozen=True)
class PaperDiagnosticsPaths:
    output_dir: Path
    manifest_json: Path
    motif_depth_deltas_json: Path
    motif_depth_deltas_csv: Path
    motif_depth_deltas_md: Path
    regime_comparison_json: Path
    regime_comparison_csv: Path
    regime_comparison_md: Path
    repair_refit_json: Path
    repair_refit_csv: Path
    repair_refit_md: Path
    baseline_diagnostics_json: Path
    baseline_diagnostics_csv: Path
    baseline_diagnostics_md: Path

    def as_dict(self) -> dict[str, str]:
        return {key: str(value) for key, value in self.__dict__.items()}


def write_paper_diagnostics(
    *,
    output_dir: Path = DEFAULT_PAPER_DIAGNOSTICS_OUTPUT_DIR,
    scientific_law_table: Path = DEFAULT_SCIENTIFIC_LAW_TABLE,
    training_aggregate: Path = DEFAULT_TRAINING_AGGREGATE,
    probe_aggregate: Path = DEFAULT_PROBE_AGGREGATE,
    repair_summary: Path = DEFAULT_REPAIR_SUMMARY,
) -> PaperDiagnosticsPaths:
    """Write v1.11 paper ablation and baseline diagnostics from existing artifacts."""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = _paths(output_dir)

    scientific_payload = _read_json(scientific_law_table)
    training_payload = _read_json(training_aggregate)
    probe_payload = _read_json(probe_aggregate)
    repair_payload = _read_json(repair_summary)

    motif_rows = motif_depth_delta_rows(scientific_payload)
    regime_rows = regime_comparison_rows(
        (
            ("v1.11-paper-training", training_payload),
            ("v1.11-logistic-planck-probes", probe_payload),
        )
    )
    repair_rows = repair_refit_rows(
        repair_payload,
        (
            ("v1.11-paper-training", training_payload),
            ("v1.11-logistic-planck-probes", probe_payload),
        ),
    )
    baseline_rows = baseline_diagnostic_rows(("exp", "logistic", "planck", "michaelis_menten", "arrhenius"))

    _write_table(paths.motif_depth_deltas_json, paths.motif_depth_deltas_csv, paths.motif_depth_deltas_md, motif_rows, _motif_markdown)
    _write_table(paths.regime_comparison_json, paths.regime_comparison_csv, paths.regime_comparison_md, regime_rows, _regime_markdown)
    _write_table(paths.repair_refit_json, paths.repair_refit_csv, paths.repair_refit_md, repair_rows, _repair_markdown)
    _write_table(
        paths.baseline_diagnostics_json,
        paths.baseline_diagnostics_csv,
        paths.baseline_diagnostics_md,
        baseline_rows,
        _baseline_markdown,
    )

    manifest = {
        "schema": "eml.paper_diagnostics.v1",
        "generated_at": _now_iso(),
        "output_dir": str(output_dir),
        "sources": [
            _source_lock("scientific_law_table", scientific_law_table),
            _source_lock("training_aggregate", training_aggregate),
            _source_lock("probe_aggregate", probe_aggregate),
            _source_lock("repair_summary", repair_summary),
        ],
        "outputs": paths.as_dict(),
        "counts": {
            "motif_depth_deltas": len(motif_rows),
            "regime_comparison": len(regime_rows),
            "repair_refit": len(repair_rows),
            "baseline_diagnostics": len(baseline_rows),
        },
        "claim_boundary": "baseline diagnostics are prediction-only and do not enter EML recovery denominators",
    }
    _write_json(paths.manifest_json, manifest)
    return paths


def motif_depth_delta_rows(scientific_law_payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for law_row in scientific_law_payload.get("rows", ()):
        if not isinstance(law_row, Mapping):
            continue
        artifact_path = Path(str(law_row.get("artifact_path") or ""))
        if not artifact_path.is_file() or artifact_path.suffix != ".json":
            continue
        run_payload = _read_json(artifact_path)
        compiled = run_payload.get("compiled_eml") if isinstance(run_payload.get("compiled_eml"), Mapping) else {}
        metadata = _compiled_metadata(compiled)
        macro = metadata.get("macro_diagnostics") if isinstance(metadata.get("macro_diagnostics"), Mapping) else {}
        hits = [str(item) for item in macro.get("hits", ())] if isinstance(macro.get("hits"), list) else []
        if not hits:
            continue
        baseline_depth = _int_or_none(macro.get("baseline_depth"))
        motif_depth = _int_or_none(metadata.get("depth") or law_row.get("compile_depth"))
        baseline_nodes = _int_or_none(macro.get("baseline_node_count"))
        motif_nodes = _int_or_none(metadata.get("node_count"))
        validation = _compiled_validation(compiled)
        validation_passed = macro.get("validation_passed", validation.get("passed"))
        rows.append(
            {
                "law": law_row.get("law"),
                "source_expression": metadata.get("source_expression") or law_row.get("formula"),
                "strict_support": law_row.get("compile_support") == "supported",
                "compile_support": law_row.get("compile_support"),
                "baseline_depth": baseline_depth,
                "motif_depth": motif_depth,
                "depth_delta": _delta(baseline_depth, motif_depth, macro.get("depth_delta")),
                "baseline_nodes": baseline_nodes,
                "motif_nodes": motif_nodes,
                "node_delta": _delta(baseline_nodes, motif_nodes, macro.get("node_delta")),
                "macro_hits": ";".join(hits),
                "validation_status": macro.get("validation_status") or validation.get("reason") or "unknown",
                "validation_passed": validation_passed,
                "max_abs_error": validation.get("max_abs_error"),
                "artifact_path": str(artifact_path),
            }
        )
    return rows


def regime_comparison_rows(aggregates: Iterable[tuple[str, Mapping[str, Any]]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for suite_id, aggregate in aggregates:
        for group_name in ("start_mode", "evidence_class"):
            group_rows = aggregate.get("groups", {}).get(group_name, ()) if isinstance(aggregate.get("groups"), Mapping) else ()
            for row in group_rows:
                if not isinstance(row, Mapping):
                    continue
                rows.append(
                    {
                        "suite_id": suite_id,
                        "group": group_name,
                        "key": row.get("key"),
                        "runs": row.get("total", 0),
                        "verifier_recovered": row.get("verifier_recovered", 0),
                        "same_ast_return": row.get("same_ast_return", 0),
                        "repaired_candidate": row.get("repaired_candidate", 0),
                        "unsupported": row.get("unsupported", 0),
                        "failed": row.get("failed", 0),
                        "recovery_rate": row.get("verifier_recovery_rate", 0.0),
                        "evidence_classes": json.dumps(row.get("evidence_classes", {}), sort_keys=True),
                        "denominator_rule": "group-local verifier-owned runs",
                    }
                )
    return rows


def repair_refit_rows(
    repair_summary: Mapping[str, Any],
    aggregates: Iterable[tuple[str, Mapping[str, Any]]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for pair in repair_summary.get("pairs", ()):
        if not isinstance(pair, Mapping):
            continue
        default = pair.get("default") if isinstance(pair.get("default"), Mapping) else {}
        expanded = pair.get("expanded") if isinstance(pair.get("expanded"), Mapping) else {}
        rows.append(
            {
                "source": "v1.9-repair-evidence",
                "formula": pair.get("formula"),
                "start_mode": pair.get("start_mode"),
                "seed": pair.get("seed"),
                "perturbation_noise": pair.get("perturbation_noise"),
                "changed_variable": "candidate_pool",
                "control_status": default.get("status"),
                "treatment_status": expanded.get("status"),
                "control_repair_status": default.get("repair_status"),
                "treatment_repair_status": expanded.get("repair_status"),
                "control_variant_count": default.get("repair_variant_count"),
                "treatment_variant_count": expanded.get("repair_variant_count"),
                "fallback_preserved": bool(default.get("fallback_manifest_preserved"))
                and bool(expanded.get("fallback_manifest_preserved")),
                "treatment_improved": bool(pair.get("expanded_improved_repair_status")),
                "final_regressed": bool(pair.get("expanded_final_status_regressed")),
                "artifact_path": expanded.get("artifact_path") or default.get("artifact_path"),
                "claim_boundary": "repair/refit diagnostics are not pure blind discovery",
            }
        )
    for suite_id, aggregate in aggregates:
        for run in aggregate.get("runs", ()):
            if not isinstance(run, Mapping):
                continue
            metrics = run.get("metrics") if isinstance(run.get("metrics"), Mapping) else {}
            if not (metrics.get("refit_status") or metrics.get("repair_status")):
                continue
            rows.append(
                {
                    "source": suite_id,
                    "formula": run.get("formula"),
                    "start_mode": run.get("start_mode"),
                    "seed": run.get("seed"),
                    "perturbation_noise": run.get("perturbation_noise"),
                    "changed_variable": "post_snap_refit_or_repair",
                    "control_status": run.get("status"),
                    "treatment_status": run.get("status"),
                    "control_repair_status": None,
                    "treatment_repair_status": metrics.get("repair_status"),
                    "control_variant_count": None,
                    "treatment_variant_count": metrics.get("repair_variant_count"),
                    "fallback_preserved": metrics.get("fallback_candidate_id") is not None,
                    "treatment_improved": run.get("claim_status") == "recovered",
                    "final_regressed": False,
                    "artifact_path": run.get("artifact_path"),
                    "claim_boundary": "post-snap refit/repair diagnostics are not pure blind discovery",
                }
            )
    return rows


def baseline_diagnostic_rows(formulas: Iterable[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for formula in formulas:
        spec = get_demo(formula)
        splits = spec.make_splits(points=40, seed=0)
        variable = spec.variable
        train = splits[0]
        train_x = np.asarray(train.inputs[variable], dtype=float)
        train_y = np.asarray(train.target.real, dtype=float)
        baseline_specs = (
            ("mean", "mean_predictor", _fit_mean(train_y)),
            ("linear", "polynomial_degree_1", _fit_poly(train_x, train_y, 1)),
            ("cubic", "polynomial_degree_3", _fit_poly(train_x, train_y, 3)),
            ("log_linear_positive", "log_linear_positive", _fit_log_linear(train_x, train_y)),
        )
        for baseline_name, baseline_type, model in baseline_specs:
            status = "ok" if model["status"] == "ok" else "unavailable"
            row: dict[str, Any] = {
                "formula": formula,
                "baseline_name": baseline_name,
                "baseline_type": baseline_type,
                "status": status,
                "parameter_count": model.get("parameter_count", 0),
                "model_summary": model.get("summary", ""),
                "assistance_level": "prediction_only_curve_fit",
                "claim_boundary": "prediction-only diagnostic; not EML symbolic recovery",
                "failure_reason": model.get("reason", ""),
            }
            for split in splits:
                metrics = _baseline_metrics(model, split.inputs[variable], split.target.real)
                row[f"{split.name}_mse"] = metrics["mse"]
                row[f"{split.name}_mae"] = metrics["mae"]
                row[f"{split.name}_max_abs"] = metrics["max_abs"]
            rows.append(row)
    return rows


def _paths(output_dir: Path) -> PaperDiagnosticsPaths:
    return PaperDiagnosticsPaths(
        output_dir=output_dir,
        manifest_json=output_dir / "manifest.json",
        motif_depth_deltas_json=output_dir / "motif-depth-deltas.json",
        motif_depth_deltas_csv=output_dir / "motif-depth-deltas.csv",
        motif_depth_deltas_md=output_dir / "motif-depth-deltas.md",
        regime_comparison_json=output_dir / "regime-comparison.json",
        regime_comparison_csv=output_dir / "regime-comparison.csv",
        regime_comparison_md=output_dir / "regime-comparison.md",
        repair_refit_json=output_dir / "repair-refit-diagnostics.json",
        repair_refit_csv=output_dir / "repair-refit-diagnostics.csv",
        repair_refit_md=output_dir / "repair-refit-diagnostics.md",
        baseline_diagnostics_json=output_dir / "baseline-diagnostics.json",
        baseline_diagnostics_csv=output_dir / "baseline-diagnostics.csv",
        baseline_diagnostics_md=output_dir / "baseline-diagnostics.md",
    )


def _compiled_metadata(compiled: Mapping[str, Any]) -> Mapping[str, Any]:
    metadata = compiled.get("metadata")
    if isinstance(metadata, Mapping):
        return metadata
    relaxed = _nested(compiled, ("diagnostic", "relaxed", "metadata"))
    return relaxed if isinstance(relaxed, Mapping) else {}


def _compiled_validation(compiled: Mapping[str, Any]) -> Mapping[str, Any]:
    validation = compiled.get("validation")
    if isinstance(validation, Mapping):
        return validation
    relaxed = _nested(compiled, ("diagnostic", "relaxed", "validation"))
    return relaxed if isinstance(relaxed, Mapping) else {}


def _nested(payload: Mapping[str, Any], path: tuple[str, ...]) -> Any:
    current: Any = payload
    for key in path:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current


def _fit_mean(y: np.ndarray) -> dict[str, Any]:
    value = float(np.mean(y))
    return {
        "status": "ok",
        "parameter_count": 1,
        "summary": f"y={value:.8g}",
        "predict": lambda x: np.full_like(np.asarray(x, dtype=float), value, dtype=float),
    }


def _fit_poly(x: np.ndarray, y: np.ndarray, degree: int) -> dict[str, Any]:
    coeffs = np.polyfit(x, y, degree)
    return {
        "status": "ok",
        "parameter_count": degree + 1,
        "summary": "polyfit[" + ",".join(f"{value:.8g}" for value in coeffs) + "]",
        "predict": lambda values, coeffs=coeffs: np.polyval(coeffs, np.asarray(values, dtype=float)),
    }


def _fit_log_linear(x: np.ndarray, y: np.ndarray) -> dict[str, Any]:
    if np.any(y <= 0) or not np.all(np.isfinite(y)):
        return {"status": "unavailable", "reason": "non_positive_or_nonfinite_targets", "parameter_count": 0, "summary": ""}
    coeffs = np.polyfit(x, np.log(y), 1)
    return {
        "status": "ok",
        "parameter_count": 2,
        "summary": f"exp({coeffs[0]:.8g}*x+{coeffs[1]:.8g})",
        "predict": lambda values, coeffs=coeffs: np.exp(np.polyval(coeffs, np.asarray(values, dtype=float))),
    }


def _baseline_metrics(model: Mapping[str, Any], x: np.ndarray, y: np.ndarray) -> dict[str, float | None]:
    if model.get("status") != "ok" or not callable(model.get("predict")):
        return {"mse": None, "mae": None, "max_abs": None}
    prediction = model["predict"](x)
    residual = np.asarray(prediction, dtype=float) - np.asarray(y, dtype=float)
    if not np.all(np.isfinite(residual)):
        return {"mse": None, "mae": None, "max_abs": None}
    return {
        "mse": float(np.mean(residual**2)),
        "mae": float(np.mean(np.abs(residual))),
        "max_abs": float(np.max(np.abs(residual))),
    }


def _delta(baseline: int | None, motif: int | None, reported: Any) -> int | None:
    reported_int = _int_or_none(reported)
    if reported_int is not None:
        return reported_int
    if baseline is None or motif is None:
        return None
    return baseline - motif


def _int_or_none(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _write_table(json_path: Path, csv_path: Path, md_path: Path, rows: list[Mapping[str, Any]], markdown_fn: Any) -> None:
    columns = _columns(rows)
    _write_json(json_path, {"schema": "eml.paper_diagnostic_table.v1", "columns": columns, "rows": rows})
    _write_csv(csv_path, rows, columns)
    md_path.write_text(markdown_fn(rows, columns), encoding="utf-8")


def _write_csv(path: Path, rows: list[Mapping[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: _csv_value(row.get(column)) for column in columns})


def _columns(rows: list[Mapping[str, Any]]) -> list[str]:
    seen: list[str] = []
    for row in rows:
        for key in row:
            if key not in seen:
                seen.append(str(key))
    return seen


def _motif_markdown(rows: list[Mapping[str, Any]], columns: list[str]) -> str:
    return _markdown_table("Motif Depth Deltas", rows, columns)


def _regime_markdown(rows: list[Mapping[str, Any]], columns: list[str]) -> str:
    return _markdown_table("Regime Comparison", rows, columns)


def _repair_markdown(rows: list[Mapping[str, Any]], columns: list[str]) -> str:
    return _markdown_table("Repair and Refit Diagnostics", rows, columns)


def _baseline_markdown(rows: list[Mapping[str, Any]], columns: list[str]) -> str:
    lines = [
        "# Baseline Diagnostics",
        "",
        "These rows are prediction-only conventional diagnostics. They are not symbolic recovery and do not enter EML recovery denominators.",
        "",
    ]
    lines.extend(_markdown_table_lines(rows, columns))
    return "\n".join(lines)


def _markdown_table(title: str, rows: list[Mapping[str, Any]], columns: list[str]) -> str:
    return "\n".join([f"# {title}", "", *_markdown_table_lines(rows, columns)])


def _markdown_table_lines(rows: list[Mapping[str, Any]], columns: list[str]) -> list[str]:
    if not columns:
        return ["No rows.", ""]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_format_markdown(row.get(column)) for column in columns) + " |")
    lines.append("")
    return lines


def _format_markdown(value: Any) -> str:
    return str(_csv_value(value)).replace("|", "\\|")


def _csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        if np.isfinite(value):
            return f"{value:.12g}"
        return str(value)
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True)
    return value


def _read_json(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _source_lock(source_id: str, path: Path) -> dict[str, Any]:
    return {"source_id": source_id, "path": str(path), "sha256": _sha256(path)}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
