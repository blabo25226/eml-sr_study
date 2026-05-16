"""Publication-grade rebuild and provenance helpers."""

from __future__ import annotations

import hashlib
import json
import platform
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from .baselines import CLAIM_SURFACE_POLICY, DEFAULT_BASELINE_DATASETS, DENOMINATOR_POLICY, write_baseline_harness
from .campaign import DEFAULT_CAMPAIGN_ROOT, run_campaign
from .datasets import expanded_dataset_manifest


DEFAULT_PUBLICATION_DIR = Path("artifacts") / "paper" / "v1.14"
DEFAULT_V113_PUBLICATION_DIR = DEFAULT_PUBLICATION_DIR
DEFAULT_LOCKFILE = Path("requirements-lock.txt")
DEFAULT_CONTAINER_FILE = Path("Dockerfile")
DEFAULT_V113_CAMPAIGN_LABEL = "v1.13-paper-tracks-final"
FORBIDDEN_PLACEHOLDER_TOKENS = (
    "1970-01-01T00:00:00+00:00",
    '"snapshot"',
)


class PublicationRebuildError(RuntimeError):
    """Raised when publication package generation fails."""


@dataclass(frozen=True)
class PublicationRebuildPaths:
    output_dir: Path
    manifest_json: Path
    source_locks_json: Path
    reproduction_md: Path
    claim_audit_json: Path
    claim_audit_md: Path
    release_gate_json: Path
    release_gate_md: Path
    validation_json: Path
    validation_md: Path

    def as_dict(self) -> dict[str, str]:
        return {key: str(value) for key, value in self.__dict__.items()}


def write_publication_rebuild(
    *,
    output_dir: Path = DEFAULT_PUBLICATION_DIR,
    smoke: bool = False,
    overwrite: bool = False,
    allow_dirty: bool = True,
    command: str | None = None,
    allowed_placeholder_paths: Iterable[str] = (),
) -> PublicationRebuildPaths:
    """Write a corrected publication rebuild package with source and output provenance."""

    output_dir = Path(output_dir)
    paths = PublicationRebuildPaths(
        output_dir=output_dir,
        manifest_json=output_dir / "manifest.json",
        source_locks_json=output_dir / "source-locks.json",
        reproduction_md=output_dir / "reproduction.md",
        claim_audit_json=output_dir / "claim-audit.json",
        claim_audit_md=output_dir / "claim-audit.md",
        release_gate_json=output_dir / "release-gate.json",
        release_gate_md=output_dir / "release-gate.md",
        validation_json=output_dir / "validation.json",
        validation_md=output_dir / "validation.md",
    )
    if output_dir.exists() and overwrite:
        _remove_existing_output_dir(output_dir)
    if paths.manifest_json.exists() and not overwrite:
        raise PublicationRebuildError(f"{paths.manifest_json} already exists; pass overwrite=True to refresh")
    output_dir.mkdir(parents=True, exist_ok=True)

    git = _git_metadata()
    if git["dirty"] and not allow_dirty:
        raise PublicationRebuildError("publication rebuild requires a clean git tree unless allow_dirty=True")

    run_command = command or _default_rebuild_command(output_dir=output_dir, smoke=smoke)
    inputs = _default_source_inputs()
    source_lock_payload = {
        "schema": "eml.v113_publication_source_locks.v1",
        "generated_at": _now_iso(),
        "inputs": inputs,
        "input_count": len(inputs),
    }
    _write_json(paths.source_locks_json, source_lock_payload)
    paths.reproduction_md.write_text(
        _reproduction_markdown(output_dir=output_dir, command=run_command, smoke=smoke),
        encoding="utf-8",
    )
    paths.validation_md.write_text(
        "# Publication Validation\n\nValidation details are written to `validation.json`.\n",
        encoding="utf-8",
    )
    linked_evidence = _write_publication_evidence(output_dir, smoke=smoke)
    claim_audit = build_publication_claim_audit(linked_evidence, smoke=smoke)
    _write_json(paths.claim_audit_json, claim_audit)
    paths.claim_audit_md.write_text(_claim_audit_markdown(claim_audit), encoding="utf-8")
    release_gate = build_publication_release_gate(linked_evidence, claim_audit, smoke=smoke)
    _write_json(paths.release_gate_json, release_gate)
    paths.release_gate_md.write_text(_release_gate_markdown(release_gate), encoding="utf-8")

    manifest = {
        "schema": "eml.v113_publication_rebuild.v1",
        "generated_at": _now_iso(),
        "mode": "smoke" if smoke else "full",
        "output_dir": str(output_dir),
        "command": run_command,
        "git": git,
        "environment": _environment_metadata(),
        "inputs": inputs,
        "outputs": _output_locks(
            (
                paths.source_locks_json,
                paths.reproduction_md,
                paths.claim_audit_json,
                paths.claim_audit_md,
                paths.release_gate_json,
                paths.release_gate_md,
                paths.validation_md,
                *_linked_evidence_paths(linked_evidence),
            )
        ),
        "linked_evidence": linked_evidence,
        "claim_audit": {
            "status": claim_audit["status"],
            "json": str(paths.claim_audit_json),
            "markdown": str(paths.claim_audit_md),
        },
        "release_gate": {
            "status": release_gate["status"],
            "json": str(paths.release_gate_json),
            "markdown": str(paths.release_gate_md),
        },
        "claim_boundary": _claim_boundary(smoke),
    }
    _write_json(paths.manifest_json, manifest)

    validation = validate_publication_package(output_dir, allowed_placeholder_paths=allowed_placeholder_paths)
    _write_json(paths.validation_json, validation)
    paths.validation_md.write_text(_validation_markdown(validation), encoding="utf-8")
    manifest["outputs"] = _output_locks(
        (
            paths.source_locks_json,
            paths.reproduction_md,
            paths.claim_audit_json,
            paths.claim_audit_md,
            paths.release_gate_json,
            paths.release_gate_md,
            paths.validation_json,
            paths.validation_md,
            *_linked_evidence_paths(linked_evidence),
        )
    )
    manifest["validation"] = {
        "status": validation["status"],
        "validation_json": str(paths.validation_json),
        "validation_markdown": str(paths.validation_md),
    }
    _write_json(paths.manifest_json, manifest)
    return paths


def build_publication_claim_audit(evidence: Mapping[str, Any], *, smoke: bool = False) -> dict[str, Any]:
    if smoke:
        return {
            "schema": "eml.v113_claim_audit.v1",
            "generated_at": _now_iso(),
            "status": "skipped",
            "reason": "smoke_mode",
            "checks": [],
            "recovered_claims": [],
        }

    checks: list[dict[str, Any]] = []
    paper_tracks = evidence.get("paper_tracks") if isinstance(evidence.get("paper_tracks"), Mapping) else {}
    aggregate_path = Path(str(paper_tracks.get("aggregate_json") or ""))
    aggregate = _read_json(aggregate_path) if aggregate_path.is_file() else {}
    runs = aggregate.get("runs") if isinstance(aggregate.get("runs"), list) else []
    counts = aggregate.get("counts") if isinstance(aggregate.get("counts"), Mapping) else {}

    _check(
        checks,
        "paper_track_aggregate_present",
        aggregate_path.is_file() and bool(runs),
        "Paper-track aggregate exists and contains run rows.",
        {"aggregate_json": str(aggregate_path), "run_count": len(runs)},
    )
    _check(
        checks,
        "paper_track_rows_have_no_execution_failures",
        int(counts.get("failed", 0) or 0) == 0 and int(counts.get("execution_error", 0) or 0) == 0,
        "No paper-track rows failed unexpectedly.",
        {"counts": dict(counts)},
    )
    track_names = {str(track.get("track")) for track in aggregate.get("tracks", []) if isinstance(track, Mapping)}
    _check(
        checks,
        "track_denominators_present",
        {"basis_only", "literal_constants"} <= track_names,
        "Basis-only and literal-constant denominators are present.",
        {"tracks": sorted(track_names)},
    )

    verification_passed = [run for run in runs if _run_verification_passed(run)]
    recovered = [run for run in runs if _run_trained_exact_recovery(run)]
    compile_only_support = [run for run in runs if _run_compile_only_verified_support(run)]
    compile_rows_in_trained = [
        str(run.get("run_id") or run.get("case_id") or "unknown")
        for run in recovered
        if str(run.get("start_mode") or "") == "compile" or str(run.get("evidence_class") or "") == "compile_only_verified"
    ]

    recovered_claims: list[dict[str, Any]] = []
    compile_only_support_claims: list[dict[str, Any]] = []
    missing_verifier: list[str] = []
    missing_track: list[str] = []
    missing_artifact: list[str] = []
    missing_final_or_substitute: list[str] = []
    for run in verification_passed:
        run_id = str(run.get("run_id") or run.get("case_id") or "unknown")
        artifact_path = Path(str(run.get("artifact_path") or ""))
        artifact = _read_json(artifact_path) if artifact_path.is_file() else {}
        verification = _verification_payload(artifact)
        final_status = _final_confirmation_or_substitute_status(verification)
        if not artifact_path.is_file():
            missing_artifact.append(run_id)
        if not verification or verification.get("status") not in {"recovered", "verified_showcase"}:
            missing_verifier.append(run_id)
        if not run.get("benchmark_track") or not run.get("constants_policy"):
            missing_track.append(run_id)
        if final_status["status"] == "missing":
            missing_final_or_substitute.append(run_id)
        row = {
            "run_id": run_id,
            "formula": run.get("formula"),
            "benchmark_track": run.get("benchmark_track"),
            "constants_policy": run.get("constants_policy"),
            "artifact_path": str(artifact_path),
            "artifact_sha256": _sha256(artifact_path) if artifact_path.is_file() else None,
            "verification_outcome": _run_verification_outcome(run),
            "evidence_regime": run.get("evidence_regime"),
            "discovery_class": _run_discovery_class(run),
            "verifier_status": verification.get("status") if verification else None,
            "final_confirmation_status": final_status["status"],
        }
        if _run_compile_only_verified_support(run):
            compile_only_support_claims.append(row)
        elif _run_trained_exact_recovery(run):
            recovered_claims.append(row)

    _check(
        checks,
        "recovered_rows_have_verifier_evidence",
        not missing_verifier,
        "Verification-passed rows have verifier evidence payloads.",
        {"missing": missing_verifier, "verification_passed_count": len(verification_passed)},
    )
    _check(
        checks,
        "recovered_rows_have_track_labels",
        not missing_track,
        "Verification-passed rows carry benchmark track and constants policy labels.",
        {"missing": missing_track},
    )
    _check(
        checks,
        "recovered_rows_have_source_artifacts",
        not missing_artifact,
        "Verification-passed rows link existing source artifacts.",
        {"missing": missing_artifact},
    )
    _check(
        checks,
        "recovered_rows_have_final_confirmation_or_substitute",
        not missing_final_or_substitute,
        "Verification-passed rows have final-confirmation status or stronger verifier-evidence substitute.",
        {"missing": missing_final_or_substitute},
    )
    _check(
        checks,
        "compile_only_excluded_from_trained_recovery",
        not compile_rows_in_trained,
        "Compile-only verified support rows are excluded from trained recovery claims.",
        {"compile_rows_in_trained": compile_rows_in_trained, "compile_only_support_count": len(compile_only_support)},
    )
    headline_actual = {
        "trained_exact_recovery_rows": len(recovered),
        "compile_only_verified_support_rows": len(compile_only_support),
        "unsupported_rows": int(counts.get("unsupported", 0) or 0),
        "failed_rows": int(counts.get("failed", 0) or 0) + int(counts.get("execution_error", 0) or 0),
    }
    headline_expected = {
        "trained_exact_recovery_rows": 8,
        "compile_only_verified_support_rows": 1,
        "unsupported_rows": 15,
        "failed_rows": 0,
    }
    headline_applies = _is_publication_track_aggregate(aggregate)
    _check(
        checks,
        "paper_track_corrected_headline_counts",
        (not headline_applies) or headline_actual == headline_expected,
        "Paper-track headline counts use trained recovery and compile-only support as separate axes.",
        {"applied": headline_applies, "actual": headline_actual, "expected": headline_expected},
    )

    baseline = evidence.get("baseline_harness") if isinstance(evidence.get("baseline_harness"), Mapping) else {}
    baseline_manifest_path = Path(str(baseline.get("manifest_json") or ""))
    baseline_manifest = _read_json(baseline_manifest_path) if baseline_manifest_path.is_file() else {}
    baseline_rows_path = _baseline_rows_path(baseline, baseline_manifest)
    baseline_rows = _baseline_rows(baseline_rows_path)
    baseline_claim_surface = _baseline_claim_surface(baseline_manifest, baseline_rows)
    _check(
        checks,
        "baseline_context_present",
        baseline_manifest_path.is_file() and baseline_manifest.get("denominator_policy") == DENOMINATOR_POLICY,
        "Matched baseline context exists and is excluded from EML recovery denominators.",
        {"baseline_manifest": str(baseline_manifest_path), "denominator_policy": baseline_manifest.get("denominator_policy")},
    )
    if baseline_rows_path is not None:
        required_fields = {"dependency", "denominator_policy", "reason", "adapter_launch_status", "fixed_budget_launched", "main_surface_eligible"}
        missing_fields = [
            str(row.get("row_id") or row.get("adapter") or index)
            for index, row in enumerate(baseline_rows)
            if not required_fields <= set(row)
        ]
        _check(
            checks,
            "baseline_rows_expose_quarantine_fields",
            not missing_fields,
            "Baseline rows expose dependency, launch, denominator, and claim-surface quarantine fields.",
            {"rows_json": str(baseline_rows_path), "missing_fields": missing_fields},
        )
    _check(
        checks,
        "baseline_main_surface_claims_quarantined",
        (not baseline_claim_surface["main_surface_comparison_claim"]) or bool(baseline_claim_surface["eligible_external_rows"]),
        "Main-surface baseline comparison claims require completed fixed-budget external rows on the same target and split contract.",
        baseline_claim_surface,
    )

    status = "passed" if all(check["status"] == "passed" for check in checks) else "failed"
    return {
        "schema": "eml.v113_claim_audit.v1",
        "generated_at": _now_iso(),
        "status": status,
        "checks": checks,
        "recovered_claims": recovered_claims,
        "compile_only_support_claims": compile_only_support_claims,
        "baseline_claim_surface": baseline_claim_surface,
        "counts": {
            "paper_track_rows": len(runs),
            "verification_passed_rows": len(verification_passed),
            "recovered_rows": len(recovered),
            "trained_exact_recovery_rows": len(recovered),
            "compile_only_verified_support_rows": len(compile_only_support),
            "unsupported_rows": int(counts.get("unsupported", 0) or 0),
            "failed_rows": int(counts.get("failed", 0) or 0) + int(counts.get("execution_error", 0) or 0),
        },
    }


def build_publication_release_gate(
    evidence: Mapping[str, Any],
    claim_audit: Mapping[str, Any],
    *,
    smoke: bool = False,
) -> dict[str, Any]:
    if smoke:
        return {
            "schema": "eml.v113_release_gate.v1",
            "generated_at": _now_iso(),
            "status": "skipped",
            "reason": "smoke_mode",
            "checks": [],
            "main_sync": {"status": "not_attempted_smoke_mode"},
        }

    dev_contract = _run_ci_contract("dev", Path.cwd())
    public_contract = _validate_synthetic_public_snapshot()
    checks = [
        {
            "id": "claim_audit_passed",
            "status": "passed" if claim_audit.get("status") == "passed" else "failed",
            "details": {"claim_audit_status": claim_audit.get("status")},
        },
        {
            "id": "dev_contract_valid",
            "status": dev_contract["status"],
            "details": dev_contract,
        },
        {
            "id": "public_snapshot_contract_valid",
            "status": public_contract["status"],
            "details": public_contract,
        },
    ]
    status = "passed" if all(check["status"] == "passed" for check in checks) else "failed"
    return {
        "schema": "eml.v113_release_gate.v1",
        "generated_at": _now_iso(),
        "status": status,
        "checks": checks,
        "evidence": {
            "paper_tracks": evidence.get("paper_tracks", {}),
            "baseline_harness": evidence.get("baseline_harness", {}),
        },
        "main_sync": {
            "status": "ready_for_publish_main_workflow" if status == "passed" else "blocked",
            "workflow": ".github/workflows/publish-main.yml",
            "local_force_push_performed": False,
            "reason": "The local release gate validates readiness; sanitized main publication is performed by the dev-only GitHub workflow after dev is pushed.",
        },
    }


def validate_publication_package(
    output_dir: Path,
    *,
    allowed_placeholder_paths: Iterable[str] = (),
) -> dict[str, Any]:
    """Validate provenance hashes and placeholder metadata policy for a publication package."""

    output_dir = Path(output_dir)
    manifest_path = output_dir / "manifest.json"
    checks: list[dict[str, Any]] = []
    if not manifest_path.is_file():
        _check(checks, "manifest_present", False, "manifest.json exists", {"path": str(manifest_path)})
        return _validation_payload(checks)

    manifest = _read_json(manifest_path)
    required_fields = ("schema", "generated_at", "mode", "command", "git", "environment", "inputs", "outputs")
    _check(
        checks,
        "manifest_required_fields",
        all(field in manifest for field in required_fields),
        "Manifest has required publication provenance fields.",
        {"missing": [field for field in required_fields if field not in manifest]},
    )
    _check(
        checks,
        "manifest_schema",
        manifest.get("schema") == "eml.v113_publication_rebuild.v1",
        "Manifest uses the v1.13 publication rebuild schema.",
        {"schema": manifest.get("schema")},
    )
    _validate_hash_rows(checks, manifest.get("inputs", []), row_kind="input")
    _validate_hash_rows(checks, manifest.get("outputs", []), row_kind="output")
    _validate_placeholders(checks, output_dir, allowed_placeholder_paths)
    return _validation_payload(checks)


def _default_source_inputs() -> list[dict[str, Any]]:
    paths = (
        Path("pyproject.toml"),
        Path("requirements-lock.txt"),
        Path("Dockerfile"),
        Path("src/eml_symbolic_regression/cli.py"),
        Path("src/eml_symbolic_regression/publication.py"),
        Path("src/eml_symbolic_regression/benchmark.py"),
        Path("src/eml_symbolic_regression/campaign.py"),
        Path("src/eml_symbolic_regression/datasets.py"),
        Path("src/eml_symbolic_regression/baselines.py"),
        Path("src/eml_symbolic_regression/verify.py"),
        Path("scripts/validate-ci-contract.py"),
        Path(".github/workflows/ci.yml"),
        Path(".github/workflows/publish-main.yml"),
        Path("data/real/hubble_1929_velocity_distance.csv"),
        Path("sources/NORTH_STAR.md"),
        Path("sources/FOR_DEMO.md"),
    )
    rows = []
    for path in paths:
        if path.is_file():
            rows.append(_lock_row("source_input", path))
    return rows


def _remove_existing_output_dir(output_dir: Path) -> None:
    resolved = output_dir.resolve()
    forbidden = {Path.cwd().resolve(), Path("/").resolve()}
    if Path.home().exists():
        forbidden.add(Path.home().resolve())
    if resolved in forbidden:
        raise PublicationRebuildError(f"refusing to overwrite unsafe output directory: {output_dir}")
    shutil.rmtree(output_dir)


def _output_locks(paths: Iterable[Path]) -> list[dict[str, Any]]:
    return [_lock_row("generated_output", path) for path in paths if path.is_file()]


def _lock_row(role: str, path: Path) -> dict[str, Any]:
    return {
        "role": role,
        "path": str(path),
        "sha256": _sha256(path),
        "bytes": path.stat().st_size,
    }


def _validate_hash_rows(checks: list[dict[str, Any]], rows: Any, *, row_kind: str) -> None:
    if not isinstance(rows, list) or not rows:
        _check(checks, f"{row_kind}_rows_present", False, f"{row_kind} rows are present.", {"rows": rows})
        return
    missing_hash: list[str] = []
    missing_file: list[str] = []
    mismatched: list[str] = []
    for row in rows:
        if not isinstance(row, Mapping):
            missing_hash.append(str(row))
            continue
        path = Path(str(row.get("path") or ""))
        if not path.is_file():
            missing_file.append(str(path))
            continue
        expected = str(row.get("sha256") or "")
        if not expected:
            missing_hash.append(str(path))
        elif _sha256(path) != expected:
            mismatched.append(str(path))
    _check(
        checks,
        f"{row_kind}_hashes_valid",
        not missing_hash and not missing_file and not mismatched,
        f"{row_kind} rows have existing files and valid SHA-256 hashes.",
        {"missing_hash": missing_hash, "missing_file": missing_file, "mismatched": mismatched},
    )


def _validate_placeholders(checks: list[dict[str, Any]], output_dir: Path, allowed_placeholder_paths: Iterable[str]) -> None:
    allowed = {Path(path).as_posix() for path in allowed_placeholder_paths}
    violations: list[dict[str, str]] = []
    for path in sorted(item for item in output_dir.rglob("*") if item.is_file()):
        relative = path.relative_to(output_dir).as_posix()
        if relative in allowed:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8", errors="ignore")
        for token in FORBIDDEN_PLACEHOLDER_TOKENS:
            if token in text:
                violations.append({"path": relative, "token": token})
    _check(
        checks,
        "placeholder_metadata_rejected",
        not violations,
        "No forbidden placeholder metadata appears outside explicit deterministic fixtures.",
        {"violations": violations},
    )


def _validation_payload(checks: list[dict[str, Any]]) -> dict[str, Any]:
    status = "passed" if all(check["status"] == "passed" for check in checks) else "failed"
    return {
        "schema": "eml.v113_publication_validation.v1",
        "generated_at": _now_iso(),
        "status": status,
        "checks": checks,
    }


def _check(checks: list[dict[str, Any]], check_id: str, passed: bool, message: str, details: Mapping[str, Any]) -> None:
    checks.append(
        {
            "id": check_id,
            "status": "passed" if passed else "failed",
            "message": message,
            "details": dict(details),
        }
    )


def _write_publication_evidence(output_dir: Path, *, smoke: bool) -> dict[str, Any]:
    if smoke:
        return {"mode": "smoke", "generated": False, "reason": "smoke mode skips full linked evidence generation"}

    artifact_root = _linked_artifact_root(output_dir)
    version_label = _publication_version_label(output_dir)
    campaign = run_campaign(
        "paper-tracks",
        output_root=artifact_root / "campaigns",
        label=_campaign_label_for_output(output_dir),
        overwrite=True,
        write_suite_result=False,
    )
    baseline_output_dir = artifact_root / "baselines" / version_label
    baseline_paths = write_baseline_harness(
        output_dir=baseline_output_dir,
        overwrite=True,
        command=f"PYTHONPATH=src python -m eml_symbolic_regression.cli baseline-harness --output-dir {baseline_output_dir} --overwrite",
    )
    dataset_manifest_dir = artifact_root / "datasets" / version_label
    dataset_manifest_dir.mkdir(parents=True, exist_ok=True)
    dataset_manifests: list[dict[str, Any]] = []
    for dataset_id in DEFAULT_BASELINE_DATASETS:
        path = dataset_manifest_dir / f"{dataset_id}-manifest.json"
        manifest = expanded_dataset_manifest(dataset_id, points=32, seed=0, tolerance=1e-8)
        _write_json(path, manifest)
        dataset_manifests.append({"dataset_id": dataset_id, "path": str(path), "manifest_sha256": manifest["manifest_sha256"]})

    return {
        "mode": "full",
        "generated": True,
        "paper_tracks": {
            "campaign_dir": str(campaign.campaign_dir),
            "manifest_json": str(campaign.manifest_path),
            "aggregate_json": str(campaign.aggregate_paths["json"]),
            "aggregate_markdown": str(campaign.aggregate_paths["markdown"]),
            "report_markdown": str(campaign.report_path) if campaign.report_path is not None else None,
            "runs_csv": str(campaign.table_paths.get("runs_csv")) if campaign.table_paths.get("runs_csv") else None,
        },
        "baseline_harness": baseline_paths.as_dict(),
        "expanded_datasets": {
            "manifest_dir": str(dataset_manifest_dir),
            "manifests": dataset_manifests,
        },
    }


def _linked_artifact_root(output_dir: Path) -> Path:
    output_dir = Path(output_dir)
    if output_dir.name == "v1.13" and output_dir.parent.name == "paper" and output_dir.parent.parent.name == "artifacts":
        return output_dir.parent.parent
    if output_dir.parent.name == "paper" and output_dir.parent.parent.name == "artifacts":
        return output_dir / "linked-artifacts"
    return output_dir.parent / "linked-artifacts"


def _publication_version_label(output_dir: Path) -> str:
    name = Path(output_dir).name
    return name if name.startswith("v") else "v1.14"


def _campaign_label_for_output(output_dir: Path) -> str:
    version_label = _publication_version_label(output_dir)
    if version_label == "v1.13":
        return DEFAULT_V113_CAMPAIGN_LABEL
    return f"{version_label}-corrected-paper-tracks"


def _linked_evidence_paths(evidence: Mapping[str, Any]) -> tuple[Path, ...]:
    paths: list[Path] = []
    skipped_keys = {"suite_result_json"}

    def visit(value: Any) -> None:
        if isinstance(value, Mapping):
            for key, child in value.items():
                if key in skipped_keys:
                    continue
                if key.endswith("_json") or key.endswith("_markdown") or key in {"path", "rows_csv", "report_md"}:
                    if child:
                        path = Path(str(child))
                        if "runs" not in path.parts:
                            paths.append(path)
                else:
                    visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(evidence)
    deduped = tuple(dict.fromkeys(path for path in paths if path.is_file()))
    return deduped


def _verification_payload(artifact: Mapping[str, Any]) -> Mapping[str, Any]:
    for key in ("compiled_eml_verification", "trained_eml_verification", "verification"):
        value = artifact.get(key)
        if isinstance(value, Mapping):
            return value
    warm_start = artifact.get("warm_start_eml")
    if isinstance(warm_start, Mapping) and isinstance(warm_start.get("verification"), Mapping):
        return warm_start["verification"]
    return {}


def _run_verification_outcome(run: Mapping[str, Any]) -> str:
    if run.get("verification_outcome") is not None:
        return str(run["verification_outcome"])
    if str(run.get("status") or "") == "unsupported" or str(run.get("claim_status") or "") == "unsupported":
        return "unsupported"
    if str(run.get("status") or "") == "execution_error":
        return "not_performed"
    if run.get("claim_status") is not None:
        return str(run["claim_status"])
    if run.get("status") is not None:
        return str(run["status"])
    return "unknown"


def _run_verification_passed(run: Mapping[str, Any]) -> bool:
    return _run_verification_outcome(run) in {"recovered", "verified_showcase"}


def _run_discovery_class(run: Mapping[str, Any]) -> str:
    if run.get("discovery_class") is not None:
        return str(run["discovery_class"])
    if not _run_verification_passed(run):
        if str(run.get("classification") or "") == "unsupported" or str(run.get("status") or "") == "unsupported":
            return "unsupported"
        return "failed" if str(run.get("status") or "") in {"failed", "snapped_but_failed", "soft_fit_only"} else "unknown"
    start_mode = str(run.get("start_mode") or "")
    if start_mode == "compile" or str(run.get("evidence_class") or "") == "compile_only_verified":
        return "compile_only_verified_support"
    if start_mode in {"blind", "warm_start", "perturbed_tree"} or not start_mode:
        return "trained_exact_recovery"
    if start_mode == "catalog":
        return "catalog_verified_support"
    return "unknown"


def _run_trained_exact_recovery(run: Mapping[str, Any]) -> bool:
    return _run_discovery_class(run) == "trained_exact_recovery"


def _run_compile_only_verified_support(run: Mapping[str, Any]) -> bool:
    return _run_discovery_class(run) == "compile_only_verified_support"


def _baseline_rows_path(baseline: Mapping[str, Any], manifest: Mapping[str, Any]) -> Path | None:
    candidates: list[Any] = [baseline.get("rows_json")]
    outputs = manifest.get("outputs") if isinstance(manifest.get("outputs"), Mapping) else {}
    candidates.append(outputs.get("rows_json"))
    for value in candidates:
        if value:
            return Path(str(value))
    return None


def _baseline_rows(path: Path | None) -> list[Mapping[str, Any]]:
    if path is None or not path.is_file():
        return []
    payload = _read_json(path)
    rows = payload.get("rows") if isinstance(payload.get("rows"), list) else []
    return [row for row in rows if isinstance(row, Mapping)]


def _baseline_claim_surface(manifest: Mapping[str, Any], rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    claim_surface = manifest.get("claim_surface") if isinstance(manifest.get("claim_surface"), Mapping) else {}
    main_surface_claim = bool(claim_surface.get("main_surface_comparison_claim") or manifest.get("main_surface_comparison_claim"))
    eligible = [
        str(row.get("row_id") or row.get("adapter") or "unknown")
        for row in rows
        if _baseline_row_is_main_surface_eligible(row)
    ]
    unavailable = sum(1 for row in rows if str(row.get("status") or "") == "unavailable")
    unsupported = sum(1 for row in rows if str(row.get("status") or "") == "unsupported")
    denominator_excluded = sum(1 for row in rows if str(row.get("denominator_policy") or "") == DENOMINATOR_POLICY)
    return {
        "policy": str(claim_surface.get("policy") or CLAIM_SURFACE_POLICY),
        "main_surface_comparison_claim": main_surface_claim,
        "eligible_external_rows": eligible,
        "eligible_external_row_count": len(eligible),
        "unavailable_rows": unavailable,
        "unsupported_rows": unsupported,
        "denominator_excluded_rows": denominator_excluded,
        "row_count": len(rows),
    }


def _baseline_row_is_main_surface_eligible(row: Mapping[str, Any]) -> bool:
    adapter = str(row.get("adapter") or "")
    return (
        adapter not in {"", "eml_reference", "polynomial_least_squares"}
        and str(row.get("status") or "") == "completed"
        and bool(row.get("fixed_budget_launched"))
        and bool(row.get("main_surface_eligible"))
        and str(row.get("denominator_policy") or "") != DENOMINATOR_POLICY
    )


def _is_publication_track_aggregate(aggregate: Mapping[str, Any]) -> bool:
    suite = aggregate.get("suite") if isinstance(aggregate.get("suite"), Mapping) else {}
    if suite.get("id") == "v1.13-paper-tracks":
        return True
    tracks = {str(track.get("track")) for track in aggregate.get("tracks", []) if isinstance(track, Mapping)}
    runs = aggregate.get("runs") if isinstance(aggregate.get("runs"), list) else []
    return len(runs) == 24 and {"basis_only", "literal_constants"} <= tracks


def _final_confirmation_or_substitute_status(verification: Mapping[str, Any]) -> dict[str, str]:
    roles = verification.get("metric_roles") if isinstance(verification.get("metric_roles"), Mapping) else {}
    if int(roles.get("final_confirmation", 0) or 0) > 0:
        return {"status": "explicit_final_confirmation"}
    if verification.get("symbolic_status") == "passed":
        return {"status": "symbolic_equivalence_substitute"}
    if verification.get("dense_random_status") == "passed" and verification.get("adversarial_status") == "passed":
        return {"status": "dense_adversarial_verifier_substitute"}
    if verification.get("high_precision_status") == "performed" and float(verification.get("high_precision_max_error", float("inf")) or float("inf")) <= float(
        verification.get("tolerance", 0.0) or 0.0
    ):
        return {"status": "high_precision_verifier_substitute"}
    return {"status": "missing"}


def _run_ci_contract(mode: str, root: Path) -> dict[str, Any]:
    result = subprocess.run(
        (sys.executable, "scripts/validate-ci-contract.py", "--mode", mode, "--root", str(root)),
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return {
        "status": "passed" if result.returncode == 0 else "failed",
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def _validate_synthetic_public_snapshot() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="eml-public-snapshot-") as tmp:
        root = Path(tmp)
        for relative in ("pyproject.toml", "README.md", "src", "tests"):
            _copy_public_path(Path(relative), root / relative)
        return _run_ci_contract("public-snapshot", root)


def _copy_public_path(source: Path, target: Path) -> None:
    if source.is_dir():
        shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"))
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def _claim_audit_markdown(audit: Mapping[str, Any]) -> str:
    counts = audit.get("counts") if isinstance(audit.get("counts"), Mapping) else {}
    lines = [
        "# v1.13 Claim Audit",
        "",
        f"Status: `{audit['status']}`",
        "",
        "## Corrected Headline Counts",
        "",
        f"- Verification-passed rows: `{counts.get('verification_passed_rows', 0)}`",
        f"- Trained exact recovery rows: `{counts.get('trained_exact_recovery_rows', 0)}`",
        f"- Compile-only verified support rows: `{counts.get('compile_only_verified_support_rows', 0)}`",
        f"- Unsupported rows: `{counts.get('unsupported_rows', 0)}`",
        f"- Failed rows: `{counts.get('failed_rows', 0)}`",
        "",
        "| Check | Status |",
        "|-------|--------|",
    ]
    for check in audit.get("checks", []):
        lines.append(f"| {check['id']} | {check['status']} |")
    lines.extend(["", "## Recovered Claims", ""])
    for claim in audit.get("recovered_claims", []):
        lines.append(
            f"- `{claim['run_id']}`: {claim.get('formula')} / {claim.get('benchmark_track')} / "
            f"{claim.get('constants_policy')} / {claim.get('final_confirmation_status')}"
        )
    if not audit.get("recovered_claims"):
        lines.append("- None in this mode.")
    lines.extend(["", "## Compile-only Verified Support", ""])
    for claim in audit.get("compile_only_support_claims", []):
        lines.append(
            f"- `{claim['run_id']}`: {claim.get('formula')} / {claim.get('benchmark_track')} / "
            f"{claim.get('constants_policy')} / {claim.get('final_confirmation_status')}"
        )
    if not audit.get("compile_only_support_claims"):
        lines.append("- None in this mode.")
    baseline = audit.get("baseline_claim_surface") if isinstance(audit.get("baseline_claim_surface"), Mapping) else {}
    lines.extend(
        [
            "",
            "## Baseline Quarantine",
            "",
            f"- Policy: `{baseline.get('policy', CLAIM_SURFACE_POLICY)}`",
            f"- Main-surface comparison claim: `{baseline.get('main_surface_comparison_claim', False)}`",
            f"- Eligible external rows: `{baseline.get('eligible_external_row_count', 0)}`",
            f"- Unavailable rows: `{baseline.get('unavailable_rows', 0)}`",
            f"- Unsupported rows: `{baseline.get('unsupported_rows', 0)}`",
        ]
    )
    return "\n".join(lines) + "\n"


def _release_gate_markdown(gate: Mapping[str, Any]) -> str:
    lines = [
        "# v1.13 Release Gate",
        "",
        f"Status: `{gate['status']}`",
        "",
        "| Check | Status |",
        "|-------|--------|",
    ]
    for check in gate.get("checks", []):
        lines.append(f"| {check['id']} | {check['status']} |")
    main_sync = gate.get("main_sync") if isinstance(gate.get("main_sync"), Mapping) else {}
    lines.extend(["", "## Main Sync", "", f"- Status: `{main_sync.get('status')}`", f"- Workflow: `{main_sync.get('workflow', '')}`"])
    return "\n".join(lines) + "\n"


def _claim_boundary(smoke: bool) -> str:
    if smoke:
        return "Smoke mode validates rebuild/provenance mechanics only; full v1.13 evidence and release gates are skipped."
    return (
        "Full mode regenerates bounded v1.13 paper-track evidence, matched baseline context, "
        "expanded dataset manifests, claim audit, and local public-snapshot readiness. Direct remote main publication is delegated to the dev-only publish workflow."
    )


def _environment_metadata() -> dict[str, Any]:
    lockfile = _optional_file_identity(DEFAULT_LOCKFILE)
    container = _optional_file_identity(DEFAULT_CONTAINER_FILE)
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "executable": sys.executable,
        "lockfile": lockfile,
        "container": container,
    }


def _optional_file_identity(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"path": str(path), "present": False, "sha256": None}
    return {"path": str(path), "present": True, "sha256": _sha256(path)}


def _git_metadata() -> dict[str, Any]:
    revision = _run_git("rev-parse", "HEAD")
    branch = _run_git("rev-parse", "--abbrev-ref", "HEAD")
    status = _run_git("status", "--short")
    return {
        "revision": revision or "unknown",
        "branch": branch or "unknown",
        "dirty": bool(status),
        "status_short": status.splitlines() if status else [],
    }


def _run_git(*args: str) -> str:
    try:
        result = subprocess.run(
            ("git", *args),
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def _default_rebuild_command(*, output_dir: Path, smoke: bool) -> str:
    parts = [
        "PYTHONPATH=src",
        "python",
        "-m",
        "eml_symbolic_regression.cli",
        "publication-rebuild",
        "--output-dir",
        str(output_dir),
    ]
    if smoke:
        parts.append("--smoke")
    parts.append("--overwrite")
    return " ".join(parts)


def _reproduction_markdown(*, output_dir: Path, command: str, smoke: bool) -> str:
    mode = "smoke" if smoke else "full"
    description = (
        "The smoke rebuild is a fast provenance and package-shape check."
        if smoke
        else "The full rebuild regenerates v1.13 paper-track evidence, matched baseline context, dataset manifests, claim audit, and release-gate artifacts."
    )
    return "\n".join(
        [
            "# Corrected Publication Rebuild",
            "",
            f"Mode: `{mode}`",
            "",
            "Run:",
            "",
            "```bash",
            command,
            "```",
            "",
            description,
            f"Output root: `{output_dir}`",
            "",
        ]
    )


def _validation_markdown(validation: Mapping[str, Any]) -> str:
    lines = [
        "# Publication Validation",
        "",
        f"Status: `{validation['status']}`",
        "",
        "| Check | Status |",
        "|-------|--------|",
    ]
    for check in validation.get("checks", []):
        lines.append(f"| {check['id']} | {check['status']} |")
    lines.append("")
    return "\n".join(lines)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
