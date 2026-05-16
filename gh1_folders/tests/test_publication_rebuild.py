import json
from pathlib import Path

import pytest

from eml_symbolic_regression.cli import build_parser, publication_rebuild_command
from eml_symbolic_regression.publication import (
    DEFAULT_PUBLICATION_DIR,
    PublicationRebuildError,
    _campaign_label_for_output,
    _linked_artifact_root,
    _validate_synthetic_public_snapshot,
    build_publication_claim_audit,
    validate_publication_package,
    write_publication_rebuild,
)


def _json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_publication_rebuild_smoke_writes_manifest_locks_and_validation(tmp_path):
    paths = write_publication_rebuild(
        output_dir=tmp_path / "paper",
        smoke=True,
        overwrite=True,
        allow_dirty=True,
        command="PYTHONPATH=src python -m eml_symbolic_regression.cli publication-rebuild --smoke",
    )

    manifest = _json(paths.manifest_json)
    source_locks = _json(paths.source_locks_json)
    validation = _json(paths.validation_json)

    assert manifest["schema"] == "eml.v113_publication_rebuild.v1"
    assert manifest["mode"] == "smoke"
    assert manifest["git"]["revision"]
    assert manifest["environment"]["python"]
    assert manifest["environment"]["lockfile"]["path"] == "requirements-lock.txt"
    assert source_locks["schema"] == "eml.v113_publication_source_locks.v1"
    assert source_locks["input_count"] >= 3
    assert validation["status"] == "passed"
    assert manifest["validation"]["status"] == "passed"
    assert all(row["sha256"] and row["bytes"] > 0 for row in manifest["inputs"])
    assert all(row["sha256"] and row["bytes"] > 0 for row in manifest["outputs"])
    assert any(row["path"].endswith("validation.json") for row in manifest["outputs"])


def test_publication_rebuild_cli_writes_package(tmp_path, capsys):
    output_dir = tmp_path / "paper"
    args = build_parser().parse_args(
        [
            "publication-rebuild",
            "--output-dir",
            str(output_dir),
            "--smoke",
            "--overwrite",
            "--allow-dirty",
        ]
    )

    assert args.func is publication_rebuild_command
    assert args.func(args) == 0

    captured = capsys.readouterr().out
    assert "publication rebuild: manifest ->" in captured
    assert "(passed)" in captured
    assert (output_dir / "manifest.json").exists()
    assert (output_dir / "validation.json").exists()


def test_publication_rebuild_defaults_to_v114_without_overwriting_historical_v113():
    args = build_parser().parse_args(["publication-rebuild", "--smoke"])

    assert args.output_dir == str(DEFAULT_PUBLICATION_DIR)
    assert args.output_dir.endswith("artifacts/paper/v1.14")
    assert _linked_artifact_root(Path("artifacts/paper/v1.14")) == Path("artifacts/paper/v1.14/linked-artifacts")
    assert _campaign_label_for_output(Path("artifacts/paper/v1.14")) == "v1.14-corrected-paper-tracks"
    assert _linked_artifact_root(Path("artifacts/paper/v1.13")) == Path("artifacts")


def test_publication_rebuild_public_snapshot_contract_omits_private_workflows():
    assert _validate_synthetic_public_snapshot()["status"] == "passed"


def test_publication_rebuild_smoke_writes_audit_and_release_gate(tmp_path):
    paths = write_publication_rebuild(output_dir=tmp_path / "paper", smoke=True, overwrite=True, allow_dirty=True)
    manifest = _json(paths.manifest_json)
    audit = _json(paths.claim_audit_json)
    gate = _json(paths.release_gate_json)

    assert audit["status"] == "skipped"
    assert gate["status"] == "skipped"
    assert manifest["claim_audit"]["json"].endswith("claim-audit.json")
    assert manifest["release_gate"]["json"].endswith("release-gate.json")
    assert any(row["path"].endswith("claim-audit.json") for row in manifest["outputs"])
    assert any(row["path"].endswith("release-gate.json") for row in manifest["outputs"])


def test_publication_claim_audit_passes_recovered_rows_with_verifier_and_baseline_context(tmp_path):
    artifact = tmp_path / "run.json"
    artifact.write_text(
        json.dumps(
            {
                "compiled_eml_verification": {
                    "status": "recovered",
                    "metric_roles": {"training": 1, "diagnostic": 2, "final_confirmation": 0},
                    "dense_random_status": "passed",
                    "adversarial_status": "passed",
                    "high_precision_status": "performed",
                    "high_precision_max_error": 0.0,
                    "tolerance": 1e-8,
                }
            }
        ),
        encoding="utf-8",
    )
    aggregate = tmp_path / "aggregate.json"
    aggregate.write_text(
        json.dumps(
            {
                "counts": {"failed": 0, "execution_error": 0, "unsupported": 1},
                "tracks": [{"track": "basis_only"}, {"track": "literal_constants"}],
                "runs": [
                    {
                        "run_id": "exp-basis",
                        "case_id": "exp-basis",
                        "formula": "exp",
                        "claim_status": "recovered",
                        "benchmark_track": "basis_only",
                        "constants_policy": "basis_only",
                        "artifact_path": str(artifact),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    baseline_manifest = tmp_path / "baseline-manifest.json"
    baseline_manifest.write_text(json.dumps({"denominator_policy": "excluded_from_eml_recovery_denominators"}), encoding="utf-8")

    audit = build_publication_claim_audit(
        {
            "paper_tracks": {"aggregate_json": str(aggregate)},
            "baseline_harness": {"manifest_json": str(baseline_manifest)},
        }
    )

    assert audit["status"] == "passed"
    assert audit["recovered_claims"][0]["final_confirmation_status"] == "dense_adversarial_verifier_substitute"
    assert audit["counts"]["trained_exact_recovery_rows"] == 1
    assert audit["counts"]["compile_only_verified_support_rows"] == 0


def test_publication_claim_audit_fails_missing_track_labels(tmp_path):
    artifact = tmp_path / "run.json"
    artifact.write_text(
        json.dumps(
            {
                "verification": {
                    "status": "recovered",
                    "metric_roles": {"final_confirmation": 1},
                    "dense_random_status": "passed",
                    "adversarial_status": "passed",
                }
            }
        ),
        encoding="utf-8",
    )
    aggregate = tmp_path / "aggregate.json"
    aggregate.write_text(
        json.dumps(
            {
                "counts": {"failed": 0, "execution_error": 0, "unsupported": 0},
                "tracks": [{"track": "basis_only"}, {"track": "literal_constants"}],
                "runs": [{"run_id": "bad", "claim_status": "recovered", "artifact_path": str(artifact)}],
            }
        ),
        encoding="utf-8",
    )
    baseline_manifest = tmp_path / "baseline-manifest.json"
    baseline_manifest.write_text(json.dumps({"denominator_policy": "excluded_from_eml_recovery_denominators"}), encoding="utf-8")

    audit = build_publication_claim_audit(
        {
            "paper_tracks": {"aggregate_json": str(aggregate)},
            "baseline_harness": {"manifest_json": str(baseline_manifest)},
        }
    )

    assert audit["status"] == "failed"
    checks = {check["id"]: check for check in audit["checks"]}
    assert checks["recovered_rows_have_track_labels"]["status"] == "failed"


def test_publication_claim_audit_rejects_compile_only_trained_recovery_promotion(tmp_path):
    artifact = tmp_path / "compile.json"
    artifact.write_text(
        json.dumps(
            {
                "compiled_eml_verification": {
                    "status": "recovered",
                    "metric_roles": {"final_confirmation": 1},
                    "dense_random_status": "passed",
                    "adversarial_status": "passed",
                }
            }
        ),
        encoding="utf-8",
    )
    aggregate = tmp_path / "aggregate.json"
    aggregate.write_text(
        json.dumps(
            {
                "counts": {"failed": 0, "execution_error": 0, "unsupported": 0},
                "tracks": [{"track": "basis_only"}, {"track": "literal_constants"}],
                "runs": [
                    {
                        "run_id": "compile-promoted",
                        "formula": "exp",
                        "start_mode": "compile",
                        "claim_status": "recovered",
                        "verification_outcome": "recovered",
                        "discovery_class": "trained_exact_recovery",
                        "evidence_class": "compile_only_verified",
                        "benchmark_track": "basis_only",
                        "constants_policy": "basis_only",
                        "artifact_path": str(artifact),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    baseline_manifest = tmp_path / "baseline-manifest.json"
    baseline_manifest.write_text(json.dumps({"denominator_policy": "excluded_from_eml_recovery_denominators"}), encoding="utf-8")

    audit = build_publication_claim_audit(
        {
            "paper_tracks": {"aggregate_json": str(aggregate)},
            "baseline_harness": {"manifest_json": str(baseline_manifest)},
        }
    )

    checks = {check["id"]: check for check in audit["checks"]}
    assert audit["status"] == "failed"
    assert checks["compile_only_excluded_from_trained_recovery"]["status"] == "failed"
    assert checks["compile_only_excluded_from_trained_recovery"]["details"]["compile_rows_in_trained"] == ["compile-promoted"]


def test_publication_claim_audit_rejects_baseline_main_surface_claim_without_eligible_rows(tmp_path):
    aggregate = tmp_path / "aggregate.json"
    aggregate.write_text(
        json.dumps(
            {
                "counts": {"failed": 0, "execution_error": 0, "unsupported": 0},
                "tracks": [{"track": "basis_only"}, {"track": "literal_constants"}],
                "runs": [],
            }
        ),
        encoding="utf-8",
    )
    baseline_rows = tmp_path / "baseline-runs.json"
    baseline_rows.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "row_id": "pysr-missing",
                        "adapter": "pysr",
                        "status": "unavailable",
                        "reason": "missing_optional_dependency",
                        "dependency": {"import_status": "missing"},
                        "denominator_policy": "excluded_from_eml_recovery_denominators",
                        "adapter_launch_status": "not_launched_missing_dependency",
                        "fixed_budget_launched": False,
                        "main_surface_eligible": False,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    baseline_manifest = tmp_path / "baseline-manifest.json"
    baseline_manifest.write_text(
        json.dumps(
            {
                "denominator_policy": "excluded_from_eml_recovery_denominators",
                "claim_surface": {
                    "policy": "quarantined_appendix_or_future_work_only",
                    "main_surface_comparison_claim": True,
                },
                "outputs": {"rows_json": str(baseline_rows)},
            }
        ),
        encoding="utf-8",
    )

    audit = build_publication_claim_audit(
        {
            "paper_tracks": {"aggregate_json": str(aggregate)},
            "baseline_harness": {"manifest_json": str(baseline_manifest)},
        }
    )

    checks = {check["id"]: check for check in audit["checks"]}
    assert audit["status"] == "failed"
    assert checks["baseline_rows_expose_quarantine_fields"]["status"] == "passed"
    assert checks["baseline_main_surface_claims_quarantined"]["status"] == "failed"
    assert checks["baseline_main_surface_claims_quarantined"]["details"]["eligible_external_row_count"] == 0
    assert audit["baseline_claim_surface"]["main_surface_comparison_claim"] is True


def test_publication_validation_rejects_placeholder_metadata(tmp_path):
    paths = write_publication_rebuild(output_dir=tmp_path / "paper", smoke=True, overwrite=True, allow_dirty=True)
    bad_artifact = paths.output_dir / "bad.json"
    bad_artifact.write_text('{"generated_at": "1970-01-01T00:00:00+00:00", "code_version": "snapshot"}\n', encoding="utf-8")

    validation = validate_publication_package(paths.output_dir)

    assert validation["status"] == "failed"
    checks = {check["id"]: check for check in validation["checks"]}
    violations = checks["placeholder_metadata_rejected"]["details"]["violations"]
    assert {"path": "bad.json", "token": "1970-01-01T00:00:00+00:00"} in violations
    assert {"path": "bad.json", "token": '"snapshot"'} in violations


def test_publication_validation_allows_explicit_deterministic_fixture(tmp_path):
    paths = write_publication_rebuild(output_dir=tmp_path / "paper", smoke=True, overwrite=True, allow_dirty=True)
    fixture = paths.output_dir / "fixtures" / "stable.json"
    fixture.parent.mkdir()
    fixture.write_text('{"generated_at": "1970-01-01T00:00:00+00:00", "code_version": "snapshot"}\n', encoding="utf-8")

    validation = validate_publication_package(paths.output_dir, allowed_placeholder_paths=("fixtures/stable.json",))

    assert validation["status"] == "passed"


def test_publication_rebuild_refuses_unsafe_overwrite_target():
    with pytest.raises(PublicationRebuildError):
        write_publication_rebuild(output_dir=Path.cwd(), smoke=True, overwrite=True, allow_dirty=True)
