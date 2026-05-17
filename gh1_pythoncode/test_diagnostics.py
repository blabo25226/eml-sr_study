import json
from pathlib import Path

from eml_symbolic_regression.benchmark import RunFilter
from eml_symbolic_regression.diagnostics import (
    build_perturbed_basin_bound_report,
    classify_blind_failure,
    compare_blind_runs,
    filter_for_runs,
    select_diagnostic_runs,
    write_baseline_triage,
    write_campaign_comparison,
)


def test_diagnostics_exposes_perturbed_basin_bound_builder():
    report = build_perturbed_basin_bound_report({"runs": []})

    assert report["schema"] == "eml.perturbed_basin_bound_report.v1"
    assert report["rows"] == []


def _write_fake_campaign(path: Path) -> None:
    runs = [
        {
            "run_id": "blind-exp-0",
            "artifact_path": str(path / "runs" / "suite" / "blind-exp-0.json"),
            "suite_id": "suite",
            "case_id": "exp-blind",
            "formula": "exp",
            "start_mode": "blind",
            "seed": 0,
            "perturbation_noise": 0.0,
            "optimizer": {"depth": 1},
            "dataset": {"points": 24},
            "status": "snapped_but_failed",
            "claim_status": "failed",
            "classification": "snapped_but_failed",
            "reason": "mpmath_failed",
            "metrics": {
                "best_loss": 1.25,
                "post_snap_loss": 2.5,
                "snap_min_margin": 0.12,
                "changed_slot_count": None,
                "verifier_status": "failed",
            },
            "stage_statuses": {"blind_baseline": "failed"},
        },
        {
            "run_id": "beer-35",
            "artifact_path": str(path / "runs" / "suite" / "beer-35.json"),
            "suite_id": "suite",
            "case_id": "beer-perturbation-sweep",
            "formula": "beer_lambert",
            "start_mode": "warm_start",
            "seed": 1,
            "perturbation_noise": 35.0,
            "optimizer": {"depth": 2},
            "dataset": {"points": 24},
            "status": "snapped_but_failed",
            "claim_status": "failed",
            "classification": "snapped_but_failed",
            "reason": "verified",
            "metrics": {
                "best_loss": 0.2,
                "post_snap_loss": 0.21,
                "snap_min_margin": 0.99,
                "changed_slot_count": 3,
                "verifier_status": "failed",
            },
            "stage_statuses": {"warm_start_attempt": "snapped_but_failed"},
        },
        {
            "run_id": "planck-compile",
            "artifact_path": str(path / "runs" / "suite" / "planck-compile.json"),
            "suite_id": "suite",
            "case_id": "planck-diagnostic",
            "formula": "planck",
            "start_mode": "compile",
            "seed": 0,
            "perturbation_noise": 0.0,
            "optimizer": {"depth": 2},
            "dataset": {"points": 24},
            "status": "unsupported",
            "claim_status": "unsupported",
            "classification": "unsupported",
            "reason": "depth_exceeded",
            "metrics": {"verifier_status": None},
            "stage_statuses": {"compiled_seed": "unsupported"},
        },
    ]
    (path / "runs" / "suite").mkdir(parents=True)
    for run in runs:
        Path(run["artifact_path"]).write_text(json.dumps({"run": run}), encoding="utf-8")
    aggregate = {
        "schema": "eml.benchmark_aggregate.v1",
        "suite": {"id": "suite"},
        "counts": {"total": 3, "verifier_recovered": 0, "unsupported": 1, "failed": 2},
        "runs": runs,
    }
    path.mkdir(parents=True, exist_ok=True)
    (path / "aggregate.json").write_text(json.dumps(aggregate), encoding="utf-8")
    (path / "suite-result.json").write_text(json.dumps({"counts": aggregate["counts"]}), encoding="utf-8")
    (path / "campaign-manifest.json").write_text(json.dumps({"preset": {"name": "fake"}}), encoding="utf-8")
    (path / "tables").mkdir()
    (path / "tables" / "runs.csv").write_text("run_id\nblind-exp-0\n", encoding="utf-8")


def test_baseline_triage_writes_report_and_lock(tmp_path):
    campaign = tmp_path / "v1.3-standard"
    _write_fake_campaign(campaign)

    paths = write_baseline_triage((campaign,), tmp_path / "triage")

    triage = json.loads(paths["json"].read_text())
    report = paths["markdown"].read_text(encoding="utf-8")
    lock = json.loads(paths["lock_json"].read_text())

    assert triage["schema"] == "eml.baseline_diagnostics.v1"
    assert triage["failure_group_counts"]
    assert "blind-exp-0" in report
    assert "best=1.25" in report
    assert "Baseline Locks" in report
    assert lock["baselines"][0]["files"][0]["sha256"]


def test_diagnostic_rerun_uses_exact_perturbation_noise_filter(tmp_path):
    campaign = tmp_path / "v1.3-standard"
    _write_fake_campaign(campaign)

    rows = select_diagnostic_runs((campaign,), "beer-perturbation-failures")
    run_filter = filter_for_runs(rows)

    assert len(rows) == 1
    assert run_filter == RunFilter(
        formulas=("beer_lambert",),
        start_modes=("warm_start",),
        case_ids=("beer-perturbation-sweep",),
        seeds=(1,),
        perturbation_noises=(35.0,),
    )


def test_compiler_depth_gate_selection_includes_unsupported_runs(tmp_path):
    campaign = tmp_path / "v1.3-standard"
    _write_fake_campaign(campaign)

    rows = select_diagnostic_runs((campaign,), "compiler-depth-gates")

    assert [row["formula"] for row in rows] == ["planck"]


def test_blind_failure_classifier_separates_soft_loss_and_recovery():
    failed = {
        "start_mode": "blind",
        "claim_status": "failed",
        "classification": "snapped_but_failed",
        "optimizer": {"depth": 1},
        "metrics": {"best_loss": 4.0, "post_snap_loss": 6.0, "snap_min_margin": 0.4},
    }
    recovered = {
        "start_mode": "blind",
        "claim_status": "recovered",
        "classification": "blind_recovery",
        "optimizer": {"depth": 1},
        "metrics": {"best_loss": 0.0, "post_snap_loss": 0.0, "snap_min_margin": 0.9},
    }

    assert classify_blind_failure(failed) == "soft_loss"
    assert classify_blind_failure(recovered) == "recovered"


def test_compare_blind_runs_reports_loss_delta_and_improvement():
    baseline = [
        {
            "formula": "exp",
            "case_id": "exp-blind",
            "start_mode": "blind",
            "seed": 0,
            "claim_status": "failed",
            "classification": "snapped_but_failed",
            "optimizer": {"depth": 1},
            "metrics": {"best_loss": 4.0, "post_snap_loss": 6.0, "snap_min_margin": 0.4},
        }
    ]
    candidate = [
        {
            "formula": "exp",
            "case_id": "exp-blind",
            "start_mode": "blind",
            "seed": 0,
            "claim_status": "recovered",
            "classification": "blind_recovery",
            "optimizer": {"depth": 1},
            "metrics": {"best_loss": 0.0, "post_snap_loss": 0.0, "snap_min_margin": 0.9},
        }
    ]

    comparison = compare_blind_runs(baseline, candidate)

    assert comparison[0]["improved"] is True
    assert comparison[0]["best_loss_delta"] == -4.0
    assert comparison[0]["candidate_diagnostic"] == "recovered"


def test_campaign_comparison_writes_deltas_and_verdicts(tmp_path):
    baseline = tmp_path / "v1.3-standard"
    candidate = tmp_path / "v1.4-standard"
    _write_fake_campaign(baseline)
    _write_fake_campaign(candidate)
    candidate_aggregate_path = candidate / "aggregate.json"
    candidate_aggregate = json.loads(candidate_aggregate_path.read_text(encoding="utf-8"))
    candidate_aggregate["runs"][0]["claim_status"] = "recovered"
    candidate_aggregate["runs"][0]["classification"] = "blind_recovery"
    candidate_aggregate["runs"][0]["metrics"]["best_loss"] = 0.0
    candidate_aggregate["runs"][0]["metrics"]["post_snap_loss"] = 0.0
    candidate_aggregate["runs"][2]["claim_status"] = "recovered"
    candidate_aggregate["runs"][2]["classification"] = "verifier_recovered"
    candidate_aggregate["runs"][2]["status"] = "recovered"
    candidate_aggregate["counts"] = {"total": 3, "verifier_recovered": 2, "unsupported": 0, "failed": 1}
    candidate_aggregate_path.write_text(json.dumps(candidate_aggregate), encoding="utf-8")

    paths = write_campaign_comparison((baseline,), (candidate,), tmp_path / "comparison")
    comparison = json.loads(paths["json"].read_text(encoding="utf-8"))
    markdown = paths["markdown"].read_text(encoding="utf-8")
    lock = json.loads(paths["lock_json"].read_text(encoding="utf-8"))

    assert comparison["categories"]["overall"]["verdict"] == "improved"
    assert comparison["categories"]["blind_recovery"]["verdict"] == "improved"
    assert comparison["categories"]["compiler_coverage"]["verdict"] == "improved"
    assert comparison["categories"]["overall"]["delta"]["verifier_recovery_rate"] > 0
    assert comparison["baseline_locks"]
    assert comparison["candidate_locks"]
    assert lock["baseline_locks"][0]["files"][0]["sha256"]
    assert "# Campaign Comparison Report" in markdown
    assert "## Anchor Locks" in markdown
    assert "diagnostics compare" in markdown
