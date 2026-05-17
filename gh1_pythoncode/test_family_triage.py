import json

from eml_symbolic_regression.family_triage import write_family_evidence_manifest, write_family_triage


def _aggregate(*runs):
    return {
        "schema": "eml.benchmark_aggregate.v1",
        "suite": {"id": "v1.8-family-smoke"},
        "counts": {"total": len(runs), "verifier_recovered": 1, "unsupported": 1, "failed": 1, "verifier_recovery_rate": 1 / 3},
        "runs": list(runs),
    }


def _run(case_id, operator, *, status, claim_status=None, reason="verified", start_mode="blind"):
    return {
        "run_id": case_id,
        "case_id": case_id,
        "formula": "exp",
        "start_mode": start_mode,
        "training_mode": "blind_training",
        "status": status,
        "claim_status": claim_status or status,
        "classification": status,
        "reason": reason,
        "artifact_path": f"artifacts/{case_id}.json",
        "optimizer": {"operator_family": {"label": operator}, "operator_schedule": []},
        "metrics": {"operator_family": operator, "operator_schedule": ""},
    }


def test_family_triage_classifies_centered_smoke_failures(tmp_path):
    smoke_path = tmp_path / "smoke-aggregate.json"
    calibration_path = tmp_path / "calibration-aggregate.json"
    smoke_path.write_text(
        json.dumps(
            _aggregate(
                _run("exp-blind-raw", "raw_eml", status="recovered", claim_status="recovered"),
                _run("exp-blind-ceml2", "CEML_2", status="snapped_but_failed", claim_status="failed", reason="train_failed"),
                _run(
                    "beer-warm-ceml2",
                    "CEML_2",
                    status="unsupported",
                    claim_status="unsupported",
                    reason="centered_family_same_family_seed_missing",
                    start_mode="warm_start",
                ),
            )
        ),
        encoding="utf-8",
    )
    calibration_path.write_text(json.dumps(_aggregate(_run("cal-exp-ceml2", "CEML_2", status="snapped_but_failed"))), encoding="utf-8")

    paths = write_family_triage(smoke_aggregate=smoke_path, calibration_aggregate=calibration_path, output_dir=tmp_path / "triage")
    payload = json.loads(paths.json_path.read_text())
    categories = {item["case_id"]: item["category"] for item in payload["classifications"]}

    assert payload["go_no_go"]["verdict"] == "conditional_go_scoped"
    assert categories["exp-blind-ceml2"] == "budget_or_operator_behavior"
    assert categories["beer-warm-ceml2"] == "missing_integration"
    assert "centered_family_same_family_seed_missing" in paths.markdown_path.read_text(encoding="utf-8")
    assert "conditional_go_scoped" in paths.go_no_go_path.read_text(encoding="utf-8")


def test_family_evidence_manifest_separates_completed_and_scoped_campaigns(tmp_path):
    paths = write_family_evidence_manifest(
        completed_campaigns=[
            {
                "name": "family-standard",
                "aggregate_json": "artifacts/campaigns/v1.8-family-standard-scoped/aggregate.json",
                "operator_family_locks_json": "artifacts/campaigns/v1.8-family-standard-scoped/tables/operator-family-locks.json",
                "reproduction_command": "PYTHONPATH=src python -m eml_symbolic_regression.cli campaign family-standard",
            }
        ],
        scoped_campaigns=[
            {"name": "family-showcase", "scope_reason": "no centered-family positive signal in calibration"},
        ],
        output_dir=tmp_path / "evidence",
    )

    payload = json.loads(paths.json_path.read_text())
    assert payload["counts"] == {"completed": 1, "scoped": 1, "with_regression_locks": 1}
    assert "family-showcase" in paths.markdown_path.read_text(encoding="utf-8")
