"""Matched baseline harness for EML and conventional symbolic regressors."""

from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import importlib.util
import json
import platform
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import sympy as sp

from .datasets import expanded_dataset_manifest, get_expanded_dataset, make_expanded_dataset_splits
from .expression import Candidate, SympyCandidate
from .verify import DataSplit, VerificationReport, verify_candidate

DEFAULT_BASELINE_OUTPUT_DIR = Path("artifacts") / "baselines" / "v1.13"
DEFAULT_BASELINE_DATASETS = (
    "noisy_beer_lambert_sweep",
    "michaelis_parameter_identifiability",
    "multivariable_arrhenius_surface",
    "unit_aware_ohm_law",
    "real_hubble_1929",
)
BASELINE_ADAPTERS = ("eml_reference", "polynomial_least_squares", "pysr", "gplearn", "pyoperon", "karoo_gp")
EXTERNAL_BASELINE_MODULES = {
    "pysr": "pysr",
    "gplearn": "gplearn",
    "pyoperon": "pyoperon",
    "karoo_gp": "karoo_gp",
}
CONSTANT_POLICIES = ("basis_only", "literal_constants")
START_CONDITIONS = ("blind", "warm_start")
DENOMINATOR_POLICY = "excluded_from_eml_recovery_denominators"
CLAIM_SURFACE_POLICY = "quarantined_appendix_or_future_work_only"
LOCAL_BASELINE_ADAPTERS = ("eml_reference", "polynomial_least_squares")
CSV_COLUMNS = (
    "row_id",
    "dataset_id",
    "adapter",
    "baseline_family",
    "status",
    "reason",
    "claim_status",
    "seed",
    "constants_policy",
    "start_condition",
    "dataset_manifest_sha256",
    "dataset_classification",
    "dataset_category",
    "time_seconds",
    "max_evaluations",
    "final_confirmation_status",
    "final_confirmation_max_abs_error",
    "max_abs_error",
    "mse",
    "dependency_status",
    "adapter_launch_status",
    "fixed_budget_launched",
    "main_surface_eligible",
    "denominator_policy",
    "model_expression",
)


@dataclass(frozen=True)
class BaselineHarnessPaths:
    output_dir: Path
    manifest_json: Path
    rows_json: Path
    rows_csv: Path
    report_md: Path
    dependency_locks_json: Path

    def as_dict(self) -> dict[str, str]:
        return {
            "output_dir": str(self.output_dir),
            "manifest_json": str(self.manifest_json),
            "rows_json": str(self.rows_json),
            "rows_csv": str(self.rows_csv),
            "report_md": str(self.report_md),
            "dependency_locks_json": str(self.dependency_locks_json),
        }


def write_baseline_harness(
    *,
    output_dir: Path = DEFAULT_BASELINE_OUTPUT_DIR,
    datasets: Sequence[str] = DEFAULT_BASELINE_DATASETS,
    adapters: Sequence[str] = ("eml_reference", "polynomial_least_squares", "pysr", "gplearn"),
    seeds: Sequence[int] = (0,),
    constants_policies: Sequence[str] = CONSTANT_POLICIES,
    start_conditions: Sequence[str] = START_CONDITIONS,
    points: int = 32,
    tolerance: float = 1e-8,
    time_seconds: float = 5.0,
    max_evaluations: int = 1000,
    overwrite: bool = False,
    command: str | None = None,
) -> BaselineHarnessPaths:
    """Write a matched baseline artifact bundle."""

    _validate_sequence("datasets", datasets)
    _validate_sequence("adapters", adapters)
    _validate_sequence("seeds", seeds)
    _validate_choices("adapters", adapters, BASELINE_ADAPTERS)
    _validate_choices("constants_policies", constants_policies, CONSTANT_POLICIES)
    _validate_choices("start_conditions", start_conditions, START_CONDITIONS)
    points = int(points)
    max_evaluations = int(max_evaluations)
    tolerance = float(tolerance)
    time_seconds = float(time_seconds)
    if points <= 0:
        raise ValueError("points must be positive")
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")
    if time_seconds <= 0:
        raise ValueError("time_seconds must be positive")
    if max_evaluations <= 0:
        raise ValueError("max_evaluations must be positive")
    for seed in seeds:
        int(seed)

    if output_dir.exists() and any(output_dir.iterdir()) and not overwrite:
        raise FileExistsError(f"baseline output directory already exists and is non-empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = BaselineHarnessPaths(
        output_dir=output_dir,
        manifest_json=output_dir / "manifest.json",
        rows_json=output_dir / "baseline-runs.json",
        rows_csv=output_dir / "baseline-runs.csv",
        report_md=output_dir / "baseline-report.md",
        dependency_locks_json=output_dir / "dependency-locks.json",
    )

    rows = run_baseline_rows(
        datasets=datasets,
        adapters=adapters,
        seeds=tuple(int(seed) for seed in seeds),
        constants_policies=constants_policies,
        start_conditions=start_conditions,
        points=points,
        tolerance=tolerance,
        time_seconds=time_seconds,
        max_evaluations=max_evaluations,
    )
    dependency_locks = build_dependency_locks(adapters)
    manifest = build_baseline_manifest(
        rows,
        paths=paths,
        datasets=datasets,
        adapters=adapters,
        seeds=tuple(int(seed) for seed in seeds),
        constants_policies=constants_policies,
        start_conditions=start_conditions,
        points=points,
        tolerance=tolerance,
        time_seconds=time_seconds,
        max_evaluations=max_evaluations,
        command=command,
    )

    _write_json(paths.rows_json, {"schema": "eml.baseline_rows.v1", "rows": rows})
    _write_csv(paths.rows_csv, rows)
    _write_json(paths.dependency_locks_json, dependency_locks)
    _write_json(paths.manifest_json, manifest)
    paths.report_md.write_text(render_baseline_report(manifest, rows, dependency_locks), encoding="utf-8")
    return paths


def run_baseline_rows(
    *,
    datasets: Sequence[str],
    adapters: Sequence[str],
    seeds: Sequence[int],
    constants_policies: Sequence[str],
    start_conditions: Sequence[str],
    points: int,
    tolerance: float,
    time_seconds: float,
    max_evaluations: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    dataset_cache: dict[tuple[str, int], tuple[dict[str, Any], list[DataSplit]]] = {}
    for dataset_id in datasets:
        spec = get_expanded_dataset(str(dataset_id))
        for seed in seeds:
            cache_key = (spec.id, int(seed))
            if cache_key not in dataset_cache:
                dataset_cache[cache_key] = (
                    expanded_dataset_manifest(spec.id, points=points, seed=int(seed), tolerance=tolerance),
                    make_expanded_dataset_splits(spec.id, points=points, seed=int(seed)),
                )
            dataset_manifest, splits = dataset_cache[cache_key]
            for constants_policy in constants_policies:
                for start_condition in start_conditions:
                    for adapter in adapters:
                        rows.append(
                            _run_baseline_row(
                                adapter=str(adapter),
                                spec=spec,
                                dataset_manifest=dataset_manifest,
                                splits=splits,
                                seed=int(seed),
                                constants_policy=str(constants_policy),
                                start_condition=str(start_condition),
                                points=points,
                                tolerance=tolerance,
                                time_seconds=time_seconds,
                                max_evaluations=max_evaluations,
                            )
                        )
    return rows


def build_dependency_locks(adapters: Sequence[str]) -> dict[str, Any]:
    adapter_rows = [_dependency_status(str(adapter)) for adapter in adapters]
    source_paths = [
        Path("src") / "eml_symbolic_regression" / "baselines.py",
        Path("src") / "eml_symbolic_regression" / "datasets.py",
        Path("data") / "real" / "hubble_1929_velocity_distance.csv",
    ]
    source_locks = [
        {
            "source_id": path.as_posix().replace("/", "_").replace(".", "_"),
            "path": path.as_posix(),
            "present": path.exists(),
            "sha256": _sha256(path) if path.exists() else None,
        }
        for path in source_paths
    ]
    return {
        "schema": "eml.baseline_dependency_locks.v1",
        "generated_at": _now_iso(),
        "adapters": adapter_rows,
        "source_locks": source_locks,
        "denominator_policy": DENOMINATOR_POLICY,
    }


def build_baseline_manifest(
    rows: Sequence[Mapping[str, Any]],
    *,
    paths: BaselineHarnessPaths,
    datasets: Sequence[str],
    adapters: Sequence[str],
    seeds: Sequence[int],
    constants_policies: Sequence[str],
    start_conditions: Sequence[str],
    points: int,
    tolerance: float,
    time_seconds: float,
    max_evaluations: int,
    command: str | None,
) -> dict[str, Any]:
    status_counts = Counter(str(row.get("status")) for row in rows)
    adapter_counts = Counter(str(row.get("adapter")) for row in rows)
    launch_counts = Counter(str(row.get("adapter_launch_status") or "unknown") for row in rows)
    main_surface_eligible = [
        row for row in rows if bool(row.get("main_surface_eligible")) and str(row.get("denominator_policy") or "") != DENOMINATOR_POLICY
    ]
    completed_external = [row for row in rows if _is_completed_external_fixed_budget_row(row)]
    return {
        "schema": "eml.baseline_harness_manifest.v1",
        "generated_at": _now_iso(),
        "command": command,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "config": {
            "datasets": list(datasets),
            "adapters": list(adapters),
            "seeds": [int(seed) for seed in seeds],
            "constants_policies": list(constants_policies),
            "start_conditions": list(start_conditions),
            "points": int(points),
            "tolerance": float(tolerance),
            "time_seconds": float(time_seconds),
            "max_evaluations": int(max_evaluations),
        },
        "counts": {
            "total": len(rows),
            "by_status": dict(sorted(status_counts.items())),
            "by_adapter": dict(sorted(adapter_counts.items())),
            "by_adapter_launch_status": dict(sorted(launch_counts.items())),
        },
        "denominator_policy": DENOMINATOR_POLICY,
        "claim_surface": {
            "policy": CLAIM_SURFACE_POLICY,
            "main_surface_comparison_claim": False,
            "main_surface_eligible_rows": len(main_surface_eligible),
            "completed_external_fixed_budget_rows": len(completed_external),
            "required_for_main_surface_comparison": (
                "completed fixed-budget external baseline rows on the same target set and split contract"
            ),
        },
        "outputs": paths.as_dict(),
    }


def render_baseline_report(
    manifest: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    dependency_locks: Mapping[str, Any],
) -> str:
    lines = [
        "# Matched Baseline Harness Report",
        "",
        f"- Generated: {manifest['generated_at']}",
        f"- Rows: {manifest['counts']['total']}",
        f"- Denominator policy: `{DENOMINATOR_POLICY}`",
        f"- Claim-surface policy: `{CLAIM_SURFACE_POLICY}`",
        "",
        "These rows are diagnostic scaffolding and future-work context. Unavailable, unsupported, local-reference, and denominator-excluded rows are not public comparator evidence.",
        "",
        "## Status Counts",
        "",
        "| Status | Count |",
        "|--------|-------|",
    ]
    for status, count in manifest["counts"]["by_status"].items():
        lines.append(f"| {status} | {count} |")

    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| Dataset | Adapter | Start | Constants | Status | Dependency | Launch | Claim | Final confirmation |",
            "|---------|---------|-------|-----------|--------|------------|--------|-------|--------------------|",
        ]
    )
    for row in rows:
        final = row.get("final_confirmation") if isinstance(row.get("final_confirmation"), Mapping) else {}
        dependency = row.get("dependency") if isinstance(row.get("dependency"), Mapping) else {}
        lines.append(
            f"| {row['dataset_id']} | {row['adapter']} | {row['start_condition']} | "
            f"{row['constants_policy']} | {row['status']} | {dependency.get('import_status') or ''} | "
            f"{row.get('adapter_launch_status') or ''} | {row.get('claim_status') or ''} | "
            f"{final.get('status') or ''} |"
        )

    lines.extend(["", "## Dependency Locks", "", "| Adapter | Module | Import status | Version |", "|---------|--------|---------------|---------|"])
    for adapter in dependency_locks.get("adapters", []):
        lines.append(
            f"| {adapter['adapter']} | {adapter.get('module') or ''} | "
            f"{adapter['import_status']} | {adapter.get('version') or ''} |"
        )
    return "\n".join(lines) + "\n"


def _run_baseline_row(
    *,
    adapter: str,
    spec: Any,
    dataset_manifest: Mapping[str, Any],
    splits: list[DataSplit],
    seed: int,
    constants_policy: str,
    start_condition: str,
    points: int,
    tolerance: float,
    time_seconds: float,
    max_evaluations: int,
) -> dict[str, Any]:
    base = _base_row(
        adapter=adapter,
        spec=spec,
        dataset_manifest=dataset_manifest,
        seed=seed,
        constants_policy=constants_policy,
        start_condition=start_condition,
        points=points,
        tolerance=tolerance,
        time_seconds=time_seconds,
        max_evaluations=max_evaluations,
    )
    try:
        if adapter == "eml_reference":
            return _run_eml_reference(base, spec.candidate, splits, constants_policy=constants_policy, start_condition=start_condition, tolerance=tolerance)
        if adapter == "polynomial_least_squares":
            return _run_polynomial_baseline(base, spec.variables, splits, constants_policy=constants_policy, start_condition=start_condition, tolerance=tolerance)
        if adapter in EXTERNAL_BASELINE_MODULES:
            return _run_external_adapter_probe(base, adapter)
        return _unsupported_row(base, "unknown_adapter", f"unknown adapter {adapter!r}")
    except Exception as exc:  # noqa: BLE001 - baseline rows must fail closed.
        row = dict(base)
        row.update(
            {
                "status": "execution_error",
                "reason": "adapter_execution_error",
                "adapter_launch_status": "fixed_budget_execution_error",
                "fixed_budget_launched": True,
                "main_surface_eligible": False,
                "error": {"type": type(exc).__name__, "message": str(exc)},
            }
        )
        return row


def _base_row(
    *,
    adapter: str,
    spec: Any,
    dataset_manifest: Mapping[str, Any],
    seed: int,
    constants_policy: str,
    start_condition: str,
    points: int,
    tolerance: float,
    time_seconds: float,
    max_evaluations: int,
) -> dict[str, Any]:
    dependency = _dependency_status(adapter)
    return {
        "schema": "eml.baseline_row.v1",
        "row_id": "::".join((spec.id, adapter, f"seed{seed}", constants_policy, start_condition)),
        "dataset_id": spec.id,
        "formula_id": spec.formula_id,
        "dataset_classification": spec.classification,
        "dataset_category": spec.category,
        "dataset_manifest_sha256": dataset_manifest["manifest_sha256"],
        "dataset_manifest": dataset_manifest,
        "adapter": adapter,
        "baseline_family": "eml" if adapter == "eml_reference" else "conventional_symbolic_regression",
        "seed": int(seed),
        "constants_policy": constants_policy,
        "start_condition": start_condition,
        "budget": {
            "points": int(points),
            "tolerance": float(tolerance),
            "time_seconds": float(time_seconds),
            "max_evaluations": int(max_evaluations),
        },
        "dependency": dependency,
        "denominator_policy": DENOMINATOR_POLICY,
        "claim_surface_policy": CLAIM_SURFACE_POLICY,
        "adapter_launch_status": "pending",
        "fixed_budget_launched": False,
        "main_surface_eligible": False,
        "status": "pending",
        "reason": None,
        "claim_status": None,
        "verification": None,
        "metrics": {},
        "final_confirmation": {},
        "model": {},
    }


def _run_eml_reference(
    base: Mapping[str, Any],
    candidate: Candidate | None,
    splits: list[DataSplit],
    *,
    constants_policy: str,
    start_condition: str,
    tolerance: float,
) -> dict[str, Any]:
    if start_condition != "warm_start":
        return _unsupported_row(base, "eml_reference_is_not_blind_search", "reference candidate is not blind EML search evidence")
    if candidate is None:
        return _unsupported_row(base, "no_clean_reference_candidate", "dataset has no exact symbolic target candidate")
    expression = candidate.to_sympy()
    if constants_policy == "basis_only" and _uses_non_basis_literal_constants(expression):
        return _unsupported_row(base, "constants_policy_requires_literal_constants", "reference expression uses non-basis literal constants")

    report = verify_candidate(candidate, splits, tolerance=tolerance)
    return _completed_row(
        base,
        report,
        model={
            "source": "clean_reference_candidate",
            "candidate_kind": getattr(candidate, "candidate_kind", type(candidate).__name__),
            "expression": sp.sstr(expression),
        },
    )


def _run_polynomial_baseline(
    base: Mapping[str, Any],
    variables: Sequence[str],
    splits: list[DataSplit],
    *,
    constants_policy: str,
    start_condition: str,
    tolerance: float,
) -> dict[str, Any]:
    if start_condition != "blind":
        return _unsupported_row(base, "adapter_has_no_warm_start_mode", "polynomial least-squares baseline is blind only")
    if constants_policy != "literal_constants":
        return _unsupported_row(base, "polynomial_fit_requires_literal_coefficients", "least-squares coefficients require literal constants")

    train = next((split for split in splits if split.name == "train"), splits[0])
    design, expressions = _polynomial_design(train.inputs, tuple(variables))
    target = np.asarray(train.target.real, dtype=np.float64)
    coeffs, *_ = np.linalg.lstsq(design, target, rcond=None)
    expression = _expression_from_coefficients(coeffs, expressions)
    candidate = SympyCandidate(expression, tuple(variables), name="polynomial_least_squares")
    report = verify_candidate(candidate, splits, tolerance=tolerance)
    return _completed_row(
        base,
        report,
        model={
            "source": "fixed_polynomial_feature_lstsq",
            "candidate_kind": candidate.candidate_kind,
            "expression": sp.sstr(expression),
            "feature_count": len(expressions),
            "fit_split": train.name,
        },
    )


def _run_external_adapter_probe(base: Mapping[str, Any], adapter: str) -> dict[str, Any]:
    dependency = _dependency_status(adapter)
    if dependency["import_status"] == "missing":
        row = dict(base)
        row.update(
            {
                "status": "unavailable",
                "reason": "missing_optional_dependency",
                "dependency": dependency,
                "adapter_launch_status": "not_launched_missing_dependency",
                "fixed_budget_launched": False,
                "main_surface_eligible": False,
                "model": {"source": "not_run"},
            }
        )
        return row
    return _unsupported_row(base, "external_adapter_execution_not_enabled", "dependency is importable but Phase 75 does not launch external SR runtimes")


def _completed_row(base: Mapping[str, Any], report: VerificationReport, *, model: Mapping[str, Any]) -> dict[str, Any]:
    row = dict(base)
    row.update(
        {
            "status": "completed",
            "reason": None,
            "claim_status": report.status,
            "adapter_launch_status": "fixed_budget_completed",
            "fixed_budget_launched": True,
            "main_surface_eligible": False,
            "verification": report.as_dict(),
            "metrics": _metrics_from_report(report),
            "final_confirmation": _final_confirmation_from_report(report),
            "model": dict(model),
        }
    )
    return row


def _unsupported_row(base: Mapping[str, Any], reason: str, detail: str) -> dict[str, Any]:
    row = dict(base)
    launch_status = "not_launched_adapter_disabled" if reason == "external_adapter_execution_not_enabled" else "not_launched_unsupported_contract"
    row.update(
        {
            "status": "unsupported",
            "reason": reason,
            "detail": detail,
            "adapter_launch_status": launch_status,
            "fixed_budget_launched": False,
            "main_surface_eligible": False,
        }
    )
    return row


def _is_completed_external_fixed_budget_row(row: Mapping[str, Any]) -> bool:
    return (
        str(row.get("status") or "") == "completed"
        and str(row.get("adapter") or "") not in LOCAL_BASELINE_ADAPTERS
        and bool(row.get("fixed_budget_launched"))
    )


def _metrics_from_report(report: VerificationReport) -> dict[str, Any]:
    if not report.split_results:
        return {}
    return {
        "max_abs_error": max(float(result.max_abs_error) for result in report.split_results),
        "mse": max(float(result.mse) for result in report.split_results),
        "high_precision_max_error": float(report.high_precision_max_error),
        "metric_roles": dict(report.metric_roles or {}),
    }


def _final_confirmation_from_report(report: VerificationReport) -> dict[str, Any]:
    finals = [result for result in report.split_results if result.role == "final_confirmation"]
    if not finals:
        return {"status": "missing", "max_abs_error": None, "mse": None}
    return {
        "status": "passed" if all(result.passed for result in finals) else "failed",
        "max_abs_error": max(float(result.max_abs_error) for result in finals),
        "mse": max(float(result.mse) for result in finals),
        "split_count": len(finals),
    }


def _polynomial_design(inputs: Mapping[str, np.ndarray], variables: tuple[str, ...]) -> tuple[np.ndarray, list[sp.Expr]]:
    count = len(next(iter(inputs.values())))
    columns = [np.ones(count, dtype=np.float64)]
    expressions: list[sp.Expr] = [sp.Integer(1)]
    symbols = {name: sp.Symbol(name) for name in variables}
    for name in variables:
        values = np.asarray(inputs[name], dtype=np.float64)
        columns.append(values)
        expressions.append(symbols[name])
    for name in variables:
        values = np.asarray(inputs[name], dtype=np.float64)
        columns.append(values**2)
        expressions.append(symbols[name] ** 2)
    for left_index, left in enumerate(variables):
        for right in variables[left_index + 1 :]:
            columns.append(np.asarray(inputs[left], dtype=np.float64) * np.asarray(inputs[right], dtype=np.float64))
            expressions.append(symbols[left] * symbols[right])
    return np.column_stack(columns), expressions


def _expression_from_coefficients(coeffs: np.ndarray, expressions: Sequence[sp.Expr]) -> sp.Expr:
    expr = sp.Integer(0)
    for coeff, term in zip(coeffs, expressions):
        value = float(coeff)
        if abs(value) <= 1e-12:
            continue
        expr += sp.Float(repr(value)) * term
    return sp.expand(expr)


def _uses_non_basis_literal_constants(expression: sp.Expr) -> bool:
    allowed = (0.0, 1.0, -1.0)
    for atom in expression.atoms(sp.Number):
        if atom in {sp.E, sp.pi, sp.I}:
            return True
        try:
            value = complex(atom.evalf())
        except TypeError:
            return True
        if abs(value.imag) > 1e-12:
            return True
        if not any(abs(value.real - allowed_value) <= 1e-12 for allowed_value in allowed):
            return True
    return False


def _dependency_status(adapter: str) -> dict[str, Any]:
    if adapter == "eml_reference":
        return {"adapter": adapter, "module": "eml_symbolic_regression", "import_status": "local", "version": None}
    if adapter == "polynomial_least_squares":
        return {"adapter": adapter, "module": "numpy+sympy", "import_status": "local", "version": None}
    module = EXTERNAL_BASELINE_MODULES.get(adapter)
    if module is None:
        return {"adapter": adapter, "module": None, "import_status": "unknown_adapter", "version": None}
    spec = importlib.util.find_spec(module)
    if spec is None:
        return {"adapter": adapter, "module": module, "import_status": "missing", "version": None}
    try:
        version = importlib.metadata.version(module)
    except importlib.metadata.PackageNotFoundError:
        version = None
    return {
        "adapter": adapter,
        "module": module,
        "import_status": "available",
        "version": version,
        "origin": spec.origin,
    }


def _validate_sequence(name: str, values: Sequence[Any]) -> None:
    if not values:
        raise ValueError(f"{name} must not be empty")


def _validate_choices(name: str, values: Sequence[str], allowed: Sequence[str]) -> None:
    invalid = sorted(set(str(value) for value in values) - set(allowed))
    if invalid:
        raise ValueError(f"{name} contains unsupported values: {', '.join(invalid)}")


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(CSV_COLUMNS), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            metrics = row.get("metrics") if isinstance(row.get("metrics"), Mapping) else {}
            final = row.get("final_confirmation") if isinstance(row.get("final_confirmation"), Mapping) else {}
            dependency = row.get("dependency") if isinstance(row.get("dependency"), Mapping) else {}
            model = row.get("model") if isinstance(row.get("model"), Mapping) else {}
            writer.writerow(
                {
                    **row,
                    "time_seconds": row.get("budget", {}).get("time_seconds") if isinstance(row.get("budget"), Mapping) else None,
                    "max_evaluations": row.get("budget", {}).get("max_evaluations") if isinstance(row.get("budget"), Mapping) else None,
                    "final_confirmation_status": final.get("status"),
                    "final_confirmation_max_abs_error": final.get("max_abs_error"),
                    "max_abs_error": metrics.get("max_abs_error"),
                    "mse": metrics.get("mse"),
                    "dependency_status": dependency.get("import_status"),
                    "model_expression": model.get("expression"),
                }
            )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
