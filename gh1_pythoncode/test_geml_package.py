import csv
import json

import pytest

from eml_symbolic_regression.geml_package import (
    GemlPackageError,
    build_geml_claim_audit,
    write_geml_evidence_package,
)


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_theory_fixture(theory_dir):
    _write_json(
        theory_dir / "ipi-restricted-theory.json",
        {
            "schema": "eml.ipi_restricted_theory.v1",
            "status": "passed",
            "checks": [{"id": "THRY-01", "passed": True}],
            "non_claims": ["restricted theory fixture"],
        },
    )
    (theory_dir / "ipi-restricted-theory.md").write_text("# i*pi EML Restricted Theory\n", encoding="utf-8")


def _write_paired_campaign_fixture(campaign_dir):
    table_dir = campaign_dir / "tables"
    table_dir.mkdir(parents=True, exist_ok=True)
    rows = [
        {"target_family": "periodic", "comparison_outcome": "ipi_recovery_win"},
        {"target_family": "negative_control", "comparison_outcome": "raw_lower_post_snap_mse"},
    ]
    with (table_dir / "geml-paired-comparison.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["target_family", "comparison_outcome"])
        writer.writeheader()
        writer.writerows(rows)
    _write_json(
        table_dir / "geml-paired-summary.json",
        {
            "schema": "eml.geml_paired_summary.v1",
            "paired_rows": 2,
            "raw_trained_exact_recovery": 0,
            "ipi_trained_exact_recovery": 1,
            "raw_trained_exact_recovery_rate": 0.0,
            "ipi_trained_exact_recovery_rate": 0.5,
            "ipi_recovery_wins": 1,
            "raw_recovery_wins": 0,
            "both_recovered": 0,
            "neither_recovered": 0,
            "negative_control_pairs": 1,
            "target_families": {"negative_control": 1, "periodic": 1},
            "comparison_outcomes": {"ipi_recovery_win": 1, "raw_lower_post_snap_mse": 1},
        },
    )
    _write_json(campaign_dir / "campaign-manifest.json", {"schema": "fixture", "preset": {"name": "geml-fixture"}})


def test_write_geml_evidence_package_writes_claim_safe_artifacts(tmp_path):
    campaign_dir = tmp_path / "campaign"
    theory_dir = tmp_path / "theory"
    _write_paired_campaign_fixture(campaign_dir)
    _write_theory_fixture(theory_dir)

    paths = write_geml_evidence_package(tmp_path / "package", campaign_dir=campaign_dir, theory_dir=theory_dir)

    manifest = json.loads(paths.manifest_json.read_text(encoding="utf-8"))
    audit = json.loads(paths.claim_audit_json.read_text(encoding="utf-8"))
    classification = json.loads(paths.target_family_json.read_text(encoding="utf-8"))["rows"]
    by_family = {row["target_family"]: row for row in classification}

    assert manifest["schema"] == "eml.v115_geml_evidence_package.v1"
    assert manifest["decision"]["decision"] == "inconclusive_smoke_only"
    assert audit["status"] == "passed"
    assert {check["id"]: check["status"] for check in audit["checks"]}["restricted_theory_referenced"] == "passed"
    assert by_family["periodic"]["decision_class"] == "ipi_win"
    assert by_family["negative_control"]["decision_class"] == "raw_loss_only_signal"
    assert by_family["negative_control"]["loss_only_outcomes"] == 1
    assert by_family["negative_control"]["neither_recovered"] == 1
    assert "complete-function coverage" in paths.claim_boundary_md.read_text(encoding="utf-8")


def test_geml_claim_audit_blocks_overclaim_language():
    audit = build_geml_claim_audit(
        "Under the matched protocol the decision is promising, with global superiority, "
        "broad blind recovery, and full universality for all elementary functions.",
        paired_summary={"schema": "eml.geml_paired_summary.v1", "paired_rows": 10},
        benchmark_manifest={
            "suites": [
                {"id": "v1.15-geml-oscillatory-smoke"},
                {"id": "v1.15-geml-oscillatory"},
            ]
        },
        theory_payload={"status": "passed"},
    )

    failed = {check["id"] for check in audit["checks"] if check["status"] == "failed"}
    assert audit["status"] == "failed"
    assert {
        "blocks_global_superiority_language",
        "blocks_broad_blind_recovery_language",
        "blocks_full_universality_language",
        "restricted_theory_referenced",
    } <= failed


def test_geml_package_refuses_existing_manifest_without_overwrite(tmp_path):
    campaign_dir = tmp_path / "campaign"
    theory_dir = tmp_path / "theory"
    _write_paired_campaign_fixture(campaign_dir)
    _write_theory_fixture(theory_dir)
    output_dir = tmp_path / "package"

    write_geml_evidence_package(output_dir, campaign_dir=campaign_dir, theory_dir=theory_dir)

    with pytest.raises(GemlPackageError):
        write_geml_evidence_package(output_dir, campaign_dir=campaign_dir, theory_dir=theory_dir)
