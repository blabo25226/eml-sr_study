import csv
import json
import shlex

import pytest

from eml_symbolic_regression.benchmark import RunFilter, load_suite
from eml_symbolic_regression.campaign import (
    CampaignOutputExistsError,
    _limitations_section,
    _reproduction_command,
    _strengths_paragraph,
    campaign_preset,
    list_campaign_presets,
    run_campaign,
    write_campaign_report,
    write_campaign_tables,
)


def _proof_basin_run(
    *,
    run_id: str = "basin-beer-lambert-bound-seed0-noise5",
    suite_id: str = "proof-perturbed-basin",
    case_id: str = "basin-beer-lambert-bound",
    evidence_class: str = "perturbed_true_tree_recovered",
    classification: str = "same_ast_return",
    status: str = "recovered",
    claim_status: str = "recovered",
    return_kind: str = "same_ast_return",
    raw_status: str = "recovered",
    repair_status: str = "not_attempted",
    perturbation_noise: float = 5.0,
) -> dict:
    return {
        "run_id": run_id,
        "artifact_path": f"artifacts/benchmarks/{suite_id}/{run_id}.json",
        "suite_id": suite_id,
        "case_id": case_id,
        "formula": "beer_lambert",
        "start_mode": "perturbed_tree",
        "seed": 0,
        "perturbation_noise": perturbation_noise,
        "optimizer": {"depth": 9, "steps": 20, "warm_depth": 9, "warm_steps": 40, "restarts": 1, "warm_restarts": 1},
        "dataset": {"points": 12},
        "claim_id": "paper-perturbed-true-tree-basin" if suite_id == "proof-perturbed-basin" else None,
        "claim_class": "bounded_training_proof" if suite_id == "proof-perturbed-basin" else None,
        "training_mode": "perturbed_true_tree_training",
        "threshold_policy_id": "bounded_100_percent" if suite_id == "proof-perturbed-basin" else None,
        "threshold": {"id": "bounded_100_percent"} if suite_id == "proof-perturbed-basin" else None,
        "status": status,
        "claim_status": claim_status,
        "classification": classification,
        "evidence_class": evidence_class,
        "return_kind": return_kind,
        "raw_status": raw_status,
        "repair_status": repair_status,
        "reason": "verified" if claim_status == "recovered" else "verifier_mismatch",
        "metrics": {
            "best_loss": 0.01,
            "post_snap_loss": 0.02,
            "snap_min_margin": 0.7,
            "verifier_status": "recovered" if claim_status == "recovered" else "failed",
            "changed_slot_count": 2,
            "repair_status": repair_status,
            "repair_verifier_status": "recovered" if repair_status == "repaired" else None,
            "repair_accepted_move_count": 1 if repair_status == "repaired" else 0,
            "repair_candidate_root_count": 2 if repair_status == "repaired" else None,
            "repair_deduped_variant_count": 7 if repair_status == "repaired" else None,
            "repair_accepted_candidate_root_source": "fallback" if repair_status == "repaired" else None,
        },
        "stage_statuses": {"perturbed_true_tree_attempt": raw_status},
    }


def _geml_pair_run(
    *,
    operator_family: str,
    formula: str = "sin_pi",
    recovered: bool = False,
    post_snap_mse: float = 0.1,
) -> dict:
    discovery_class = "trained_exact_recovery" if recovered else "failed_training_attempt"
    return {
        "run_id": f"{formula}-{operator_family}-seed0",
        "artifact_path": "",
        "suite_id": "v1.15-geml-oscillatory",
        "case_id": f"{formula}-{operator_family}-blind",
        "formula": formula,
        "start_mode": "blind",
        "seed": 0,
        "perturbation_noise": 0.0,
        "optimizer": {"depth": 3, "steps": 24, "warm_depth": 0, "warm_steps": 8, "restarts": 1, "warm_restarts": 1},
        "dataset": {"points": 24},
        "training_mode": "blind_training",
        "status": "recovered" if recovered else "snapped_but_failed",
        "claim_status": "recovered" if recovered else "failed",
        "classification": "verified_exact" if recovered else "snapped_but_failed",
        "verification_outcome": "recovered" if recovered else "failed",
        "evidence_regime": "trained",
        "discovery_class": discovery_class,
        "warm_start_evidence": "not_warm_start",
        "ast_return_status": "not_warm_start",
        "evidence_class": "trained_exact" if recovered else "failed",
        "constants_policy": "literal_constants",
        "tags": ["v1.15", "geml_oscillatory", "periodic", "branch_safe_by_construction"],
        "metrics": {
            "operator_family": "raw_eml" if operator_family == "raw" else "ipi_eml",
            "best_loss": post_snap_mse / 2,
            "pre_snap_mse": post_snap_mse / 3,
            "post_snap_loss": post_snap_mse,
            "post_snap_mse": post_snap_mse,
            "post_snap_minus_soft_best": post_snap_mse / 2,
            "post_snap_minus_pre_snap": post_snap_mse / 3,
            "gradient_l2_norm_max": 1.0,
            "gradient_max_abs_max": 0.5,
            "snap_min_margin": 0.04,
            "snap_active_node_count": 3,
            "snap_low_margin_slot_count": 1,
            "snap_lowest_margin_slots": [{"slot": "root.left", "choice": "var:x", "probability": 0.52, "margin": 0.04}],
            "snap_low_confidence_alternatives": [
                {
                    "slot": "root.left",
                    "current_choice": "var:x",
                    "current_probability": 0.52,
                    "current_margin": 0.04,
                    "alternatives": [{"choice": "child", "probability": 0.48, "probability_gap": 0.04, "rank": 1}],
                }
            ],
            "selected_candidate_id": f"{formula}-{operator_family}-selected",
            "fallback_candidate_id": f"{formula}-{operator_family}-fallback",
            "selection_mode": "verifier_gated_exact_candidate_pool",
            "candidate_pool_size": 2,
            "fallback_snap_min_margin": 0.03,
            "fallback_low_margin_slot_count": 1,
            "anomaly_exp_overflow_count": 2,
            "anomaly_nan_count": 0,
            "anomaly_inf_count": 0,
            "anomaly_branch_input_count": 8,
            "anomaly_log_branch_cut_count": 0,
            "anomaly_log_branch_cut_proximity_count": 1,
            "anomaly_log_branch_cut_crossing_count": 0,
            "optimizer_wall_clock_seconds": 0.25,
            "verifier_status": "recovered" if recovered else "failed",
        },
        "stage_statuses": {},
    }


def test_campaign_presets_map_to_budgeted_suites():
    assert list_campaign_presets() == (
        "smoke",
        "standard",
        "showcase",
        "proof-shallow",
        "proof-shallow-pure-blind",
        "proof-basin",
        "proof-basin-probes",
        "proof-depth-curve",
        "family-smoke",
        "family-calibration",
        "family-shallow-pure-blind",
        "family-shallow",
        "family-basin",
        "family-depth-curve",
        "family-standard",
        "family-showcase",
        "paper-training",
        "paper-probes",
        "paper-tracks",
        "geml-oscillatory-smoke",
        "geml-oscillatory",
        "geml-v116-smoke",
        "geml-v116-pilot",
        "geml-v116-full",
    )

    standard = campaign_preset("standard")
    suite = load_suite(standard.suite)
    runs = suite.expanded_runs()

    assert standard.tier == "showcase-default"
    assert {run.start_mode for run in runs} >= {"blind", "warm_start", "compile"}
    assert any(run.case_id == "beer-perturbation-sweep" for run in runs)
    assert any(run.case_id == "shockley-warm" and run.start_mode == "warm_start" for run in runs)
    assert any(run.formula == "michaelis_menten" for run in runs)
    assert any(run.formula == "planck" for run in runs)
    assert {"radioactive_decay", "logistic", "shockley"} <= {run.formula for run in runs}

    proof = campaign_preset("proof-shallow")
    assert proof.suite == "v1.5-shallow-proof"
    assert any(run.claim_id == "paper-shallow-scaffolded-recovery" for run in load_suite(proof.suite).expanded_runs())

    pure_blind = campaign_preset("proof-shallow-pure-blind")
    assert pure_blind.suite == "v1.5-shallow-pure-blind"
    assert any(run.claim_id == "paper-shallow-blind-recovery" for run in load_suite(pure_blind.suite).expanded_runs())

    proof_basin = campaign_preset("proof-basin")
    assert proof_basin.benchmark_suite == "proof-perturbed-basin"
    assert proof_basin.budget_guardrail == "CI-scale perturbed basin proof suite; high-noise probes are reported separately"
    assert any(run.case_id == "basin-beer-lambert-bound" for run in load_suite(proof_basin.suite).expanded_runs())

    proof_basin_probes = campaign_preset("proof-basin-probes")
    assert proof_basin_probes.suite == "proof-perturbed-basin-beer-probes"
    assert any(run.case_id == "basin-beer-lambert-bound-probes" for run in load_suite(proof_basin_probes.suite).expanded_runs())

    depth_curve = campaign_preset("proof-depth-curve")
    assert depth_curve.suite == "proof-depth-curve"
    assert any(run.case_id == "depth-6-perturbed" for run in load_suite(depth_curve.suite).expanded_runs())

    family_smoke = campaign_preset("family-smoke")
    family_runs = load_suite(family_smoke.suite).expanded_runs()
    assert family_smoke.suite == "v1.8-family-smoke"
    assert any(run.case_id == "exp-blind-ceml2" for run in family_runs)
    assert any(run.case_id == "exp-blind-ceml8" for run in family_runs)
    assert any([operator.label for operator in run.optimizer.operator_schedule] == ["ZEML_8", "ZEML_4"] for run in family_runs)

    family_calibration = campaign_preset("family-calibration")
    assert family_calibration.suite == "v1.8-family-calibration"
    assert len(load_suite(family_calibration.suite).expanded_runs()) == 22

    family_standard = campaign_preset("family-standard")
    assert family_standard.suite == "v1.8-family-standard"
    assert family_standard.tier == "v1.8-family-matrix"

    paper_training = campaign_preset("paper-training")
    paper_training_runs = load_suite(paper_training.suite).expanded_runs()
    assert paper_training.suite == "v1.11-paper-training"
    assert paper_training.tier == "v1.11-paper"
    assert {run.start_mode for run in paper_training_runs} == {"blind", "warm_start", "perturbed_tree"}

    paper_probes = campaign_preset("paper-probes")
    paper_probe_runs = load_suite(paper_probes.suite).expanded_runs()
    assert paper_probes.suite == "v1.11-logistic-planck-probes"
    assert {run.formula for run in paper_probe_runs} == {"logistic", "planck"}
    assert {run.start_mode for run in paper_probe_runs} == {"compile", "blind"}

    paper_tracks = campaign_preset("paper-tracks")
    paper_track_runs = load_suite(paper_tracks.suite).expanded_runs()
    assert paper_tracks.suite == "v1.13-paper-tracks"
    assert paper_tracks.tier == "v1.13-paper"
    assert {run.track for run in paper_track_runs} == {"basis_only", "literal_constants"}
    assert len(paper_track_runs) == 24

    geml_smoke = campaign_preset("geml-oscillatory-smoke")
    assert geml_smoke.suite == "v1.15-geml-oscillatory-smoke"
    assert len(load_suite(geml_smoke.suite).expanded_runs()) == 4

    geml_full = campaign_preset("geml-oscillatory")
    geml_runs = load_suite(geml_full.suite).expanded_runs()
    assert geml_full.suite == "v1.15-geml-oscillatory"
    assert geml_full.tier == "v1.15-geml"
    assert len(geml_runs) == 20
    assert {run.optimizer.operator_family.label for run in geml_runs} == {"raw_eml", "ipi_eml"}

    geml_v116_pilot = campaign_preset("geml-v116-pilot")
    geml_v116_runs = load_suite(geml_v116_pilot.suite).expanded_runs()
    assert geml_v116_pilot.suite == "v1.16-geml-pilot"
    assert geml_v116_pilot.tier == "v1.16-geml"
    assert len(geml_v116_runs) == 24
    assert any(run.optimizer.phase_initializers for run in geml_v116_runs if run.optimizer.operator_family.label == "ipi_eml")
    assert {"geml-v116-smoke", "geml-v116-pilot", "geml-v116-full"} <= set(list_campaign_presets())


def test_campaign_writes_manifest_suite_result_and_aggregate(tmp_path):
    result = run_campaign(
        "smoke",
        output_root=tmp_path,
        label="ci-smoke",
        run_filter=RunFilter(case_ids=("planck-diagnostic",)),
    )

    assert result.campaign_dir == tmp_path / "ci-smoke"
    assert result.manifest_path.exists()
    assert result.suite_result_path.exists()
    assert result.aggregate_paths["json"].exists()
    assert result.aggregate_paths["markdown"].exists()

    manifest = json.loads(result.manifest_path.read_text())
    assert manifest["schema"] == "eml.campaign_manifest.v1"
    assert manifest["preset"]["name"] == "smoke"
    assert manifest["suite"]["id"] == "smoke"
    assert manifest["counts"]["total"] == 1
    assert manifest["run_filter"]["case_ids"] == ["planck-diagnostic"]
    assert "campaign smoke" in manifest["reproducibility"]["command"]


def test_family_smoke_campaign_writes_family_manifest(tmp_path):
    result = run_campaign(
        "family-smoke",
        output_root=tmp_path,
        label="family-ci",
        run_filter=RunFilter(case_ids=("exp-blind-raw", "exp-blind-ceml2")),
    )

    manifest = json.loads(result.manifest_path.read_text())
    aggregate = json.loads(result.aggregate_paths["json"].read_text())
    recovery_rows = list(csv.DictReader(result.table_paths["operator_family_recovery_csv"].open(encoding="utf-8")))
    diagnostic_rows = list(csv.DictReader(result.table_paths["operator_family_diagnostics_csv"].open(encoding="utf-8")))
    locks = json.loads(result.table_paths["operator_family_locks_json"].read_text())
    comparison = result.table_paths["operator_family_comparison_md"].read_text(encoding="utf-8")

    assert manifest["preset"]["name"] == "family-smoke"
    assert manifest["suite"]["id"] == "v1.8-family-smoke"
    assert manifest["counts"]["total"] == 2
    assert manifest["run_filter"]["case_ids"] == ["exp-blind-raw", "exp-blind-ceml2"]
    assert {"raw_eml", "CEML_2"} <= {row["operator_family"] for row in recovery_rows}
    assert {"raw_eml", "CEML_2"} <= {row["operator_family"] for row in diagnostic_rows}
    assert locks["schema"] == "eml.operator_family_locks.v1"
    assert {row["operator_family"] for row in locks["groups"]} >= {"raw_eml", "CEML_2"}
    assert "Operator-Family Comparison" in comparison
    assert "operator_family_comparison_md" in result.table_paths
    assert {run["metrics"]["operator_family"] for run in aggregate["runs"]} <= {"raw_eml", "CEML_2"}
    assert "## Operator-Family Comparison" in result.report_path.read_text(encoding="utf-8")


def test_reproduction_command_quotes_shell_sensitive_values(tmp_path):
    output_root = tmp_path / "campaign root"
    command = _reproduction_command(
        "smoke",
        output_root,
        "ok; echo injected",
        True,
        {
            "formulas": ["exp", "log; rm -rf /"],
            "start_modes": ["blind"],
            "case_ids": ["case with space"],
            "seeds": [0],
            "perturbation_noises": [0.0],
        },
    )

    assert command == shlex.join(shlex.split(command))
    assert shlex.split(command) == [
        "PYTHONPATH=src",
        "python",
        "-m",
        "eml_symbolic_regression.cli",
        "campaign",
        "smoke",
        "--output-root",
        str(output_root),
        "--label",
        "ok; echo injected",
        "--overwrite",
        "--formula",
        "exp",
        "--formula",
        "log; rm -rf /",
        "--start-mode",
        "blind",
        "--case",
        "case with space",
        "--seed",
        "0",
        "--perturbation-noise",
        "0.0",
    ]


def test_campaign_refuses_silent_overwrite(tmp_path):
    run_campaign(
        "smoke",
        output_root=tmp_path,
        label="existing",
        run_filter=RunFilter(case_ids=("planck-diagnostic",)),
    )

    with pytest.raises(CampaignOutputExistsError):
        run_campaign(
            "smoke",
            output_root=tmp_path,
            label="existing",
            run_filter=RunFilter(case_ids=("planck-diagnostic",)),
        )

    stale_artifact = tmp_path / "existing" / "runs" / "stale-suite" / "stale.json"
    stale_artifact.parent.mkdir(parents=True)
    stale_artifact.write_text("{}", encoding="utf-8")

    replacement = run_campaign(
        "smoke",
        output_root=tmp_path,
        label="existing",
        overwrite=True,
        run_filter=RunFilter(case_ids=("planck-diagnostic",)),
    )

    assert replacement.manifest_path.exists()
    assert not stale_artifact.exists()


def test_campaign_writes_tidy_csvs_and_headline_metrics(tmp_path):
    result = run_campaign(
        "smoke",
        output_root=tmp_path,
        label="csv-smoke",
        run_filter=RunFilter(case_ids=("beer-warm", "planck-diagnostic")),
    )

    assert result.table_paths["runs_csv"].exists()
    assert result.table_paths["group_formula_csv"].exists()
    assert result.table_paths["group_start_mode_csv"].exists()
    assert result.table_paths["group_perturbation_noise_csv"].exists()
    assert result.table_paths["group_depth_csv"].exists()
    assert result.table_paths["group_failure_class_csv"].exists()
    assert result.table_paths["headline_json"].exists()
    assert result.table_paths["headline_csv"].exists()
    assert result.table_paths["failures_csv"].exists()
    assert result.table_paths["geml_paired_comparison_csv"].exists()
    assert result.table_paths["geml_paired_summary_json"].exists()
    assert result.table_paths["geml_paired_comparison_md"].exists()

    run_rows = list(csv.DictReader(result.table_paths["runs_csv"].open(encoding="utf-8")))
    assert len(run_rows) == 2
    assert {
        "formula",
        "start_mode",
        "seed",
        "depth",
        "steps",
        "perturbation_noise",
        "best_loss",
        "pre_snap_mse",
        "post_snap_loss",
        "post_snap_mse",
        "gradient_l2_norm_max",
        "gradient_max_abs_max",
        "verifier_status",
        "recovery_class",
        "runtime_seconds",
        "optimizer_wall_clock_seconds",
        "anomaly_log_branch_cut_proximity_count",
        "anomaly_log_branch_cut_crossing_count",
        "branch_diagnostics_status",
        "changed_slot_count",
        "warm_start_mechanism",
        "warm_start_evidence",
        "ast_return_status",
        "total_restarts",
        "artifact_path",
    } <= set(run_rows[0])
    assert {
        "claim_id",
        "claim_class",
        "training_mode",
        "evidence_class",
        "threshold_policy",
        "dataset_manifest_sha256",
        "provenance_source",
        "provenance_expression",
    } <= set(run_rows[0])
    assert "threshold_status" not in set(run_rows[0])
    assert run_rows[0]["training_mode"]
    assert run_rows[0]["claim_id"] == ""
    warm_row = next(row for row in run_rows if row["start_mode"] == "warm_start")
    assert warm_row["warm_start_evidence"] == "exact_seed_round_trip"
    assert warm_row["ast_return_status"] == "same_ast"
    assert warm_row["total_restarts"] == warm_row["warm_restarts"] == "1"

    report = result.report_path.read_text(encoding="utf-8")
    assert "## Warm-Start Evidence" in report
    assert "exact_seed_round_trip" in report
    assert "exact seed round-trips" in report
    assert "robustness" not in report.lower()
    assert "warm-start basin" not in report.lower()

    headline = json.loads(result.table_paths["headline_json"].read_text())
    assert headline["total_runs"] == 2
    assert headline["verifier_recovered"] == 1
    assert headline["unsupported"] == 1
    assert headline["same_ast_return"] == 1

    failures = list(csv.DictReader(result.table_paths["failures_csv"].open(encoding="utf-8")))
    assert len(failures) == 1
    assert failures[0]["classification"] == "unsupported"
    assert failures[0]["reason"]


def test_campaign_tables_preserve_perturbed_repair_status_columns(tmp_path):
    aggregate = {
        "runs": [
            _proof_basin_run(),
            _proof_basin_run(
                run_id="basin-beer-lambert-bound-probe-repaired",
                suite_id="proof-perturbed-basin-beer-probes",
                case_id="basin-beer-lambert-bound-probes",
                evidence_class="repaired_candidate",
                classification="repaired_candidate",
                status="repaired_candidate",
                return_kind="snapped_but_failed",
                raw_status="snapped_but_failed",
                repair_status="repaired",
                perturbation_noise=15.0,
            ),
        ],
        "counts": {"total": 2, "verifier_recovered": 1, "evidence_classes": {}},
        "thresholds": [],
    }

    paths = write_campaign_tables(aggregate, tmp_path / "tables")

    run_rows = list(csv.DictReader(paths["runs_csv"].open(encoding="utf-8")))
    assert {
        "return_kind",
        "raw_status",
        "repair_status",
        "repair_verifier_status",
        "repair_accepted_move_count",
        "repair_candidate_root_count",
        "repair_deduped_variant_count",
        "repair_accepted_candidate_root_source",
    } <= set(run_rows[0])
    repaired = next(row for row in run_rows if row["evidence_class"] == "repaired_candidate")
    assert repaired["return_kind"] == "snapped_but_failed"
    assert repaired["raw_status"] == "snapped_but_failed"
    assert repaired["repair_status"] == "repaired"
    assert repaired["repair_verifier_status"] == "recovered"
    assert repaired["repair_accepted_move_count"] == "1"
    assert repaired["repair_candidate_root_count"] == "2"
    assert repaired["repair_deduped_variant_count"] == "7"
    assert repaired["repair_accepted_candidate_root_source"] == "fallback"

    failures = list(csv.DictReader(paths["failures_csv"].open(encoding="utf-8")))
    assert len(failures) == 1
    assert failures[0]["classification"] == "repaired_candidate"
    assert failures[0]["raw_status"] == "snapped_but_failed"
    assert failures[0]["repair_status"] == "repaired"
    assert failures[0]["repair_candidate_root_count"] == "2"
    assert failures[0]["repair_deduped_variant_count"] == "7"
    assert failures[0]["repair_accepted_candidate_root_source"] == "fallback"


def test_campaign_tables_emit_geml_paired_comparison(tmp_path):
    aggregate = {
        "runs": [
            _geml_pair_run(operator_family="raw", recovered=False, post_snap_mse=0.2),
            _geml_pair_run(operator_family="ipi", recovered=True, post_snap_mse=0.01),
        ],
        "counts": {"total": 2, "verifier_recovered": 1, "evidence_classes": {}},
        "thresholds": [],
    }

    paths = write_campaign_tables(aggregate, tmp_path / "tables")

    rows = list(csv.DictReader(paths["geml_paired_comparison_csv"].open(encoding="utf-8")))
    summary = json.loads(paths["geml_paired_summary_json"].read_text(encoding="utf-8"))
    markdown = paths["geml_paired_comparison_md"].read_text(encoding="utf-8")

    assert len(rows) == 1
    row = rows[0]
    assert row["formula"] == "sin_pi"
    assert row["raw_discovery_class"] == "failed_training_attempt"
    assert row["ipi_discovery_class"] == "trained_exact_recovery"
    assert row["comparison_outcome"] == "ipi_recovery_win"
    assert row["raw_post_snap_mse"] == "0.2"
    assert row["ipi_post_snap_mse"] == "0.01"
    assert row["raw_snap_min_margin"] == "0.04"
    assert row["ipi_low_margin_slot_count"] == "1.0"
    assert row["raw_selected_candidate_id"] == "sin_pi-raw-selected"
    assert row["ipi_selection_mode"] == "verifier_gated_exact_candidate_pool"
    assert "root.left" in row["raw_lowest_margin_slots_json"]
    assert "child" in row["ipi_low_confidence_alternatives_json"]
    assert row["ipi_branch_cut_proximity_count"] == "1.0"
    assert row["ipi_optimizer_wall_clock_seconds"] == "0.25"
    assert summary["schema"] == "eml.geml_paired_summary.v1"
    assert summary["paired_rows"] == 1
    assert summary["ipi_recovery_wins"] == 1
    assert summary["ipi_trained_exact_recovery_rate"] == 1.0
    assert "GEML Paired Comparison" in markdown
    assert "ipi_recovery_win" in markdown


def test_campaign_tables_classify_geml_pairs_by_formula_without_tags(tmp_path):
    runs = [
        _geml_pair_run(operator_family="raw", formula="exp", recovered=False, post_snap_mse=0.2),
        _geml_pair_run(operator_family="ipi", formula="exp", recovered=False, post_snap_mse=0.3),
    ]
    for run in runs:
        run.pop("tags")
    aggregate = {"runs": runs, "counts": {"total": 2, "verifier_recovered": 0, "evidence_classes": {}}, "thresholds": []}

    paths = write_campaign_tables(aggregate, tmp_path / "tables")

    rows = list(csv.DictReader(paths["geml_paired_comparison_csv"].open(encoding="utf-8")))
    summary = json.loads(paths["geml_paired_summary_json"].read_text(encoding="utf-8"))
    assert rows[0]["target_family"] == "negative_control"
    assert summary["negative_control_pairs"] == 1
    assert summary["neither_recovered"] == 1
    assert summary["loss_only_outcomes"] == 1
    assert summary["raw_lower_post_snap_mse"] == 1
    assert summary["target_families"] == {"negative_control": 1}


def test_proof_campaign_tables_and_manifest_preserve_claim_metadata(tmp_path):
    result = run_campaign(
        "proof-shallow",
        output_root=tmp_path,
        label="proof-exp",
        run_filter=RunFilter(case_ids=("shallow-exp-blind",), seeds=(0,)),
    )

    assert result.table_paths["group_evidence_class_csv"].exists()
    assert result.table_paths["group_claim_csv"].exists()
    assert result.table_paths["group_threshold_policy_csv"].exists()

    run_rows = list(csv.DictReader(result.table_paths["runs_csv"].open(encoding="utf-8")))
    assert len(run_rows) == 1
    row = run_rows[0]
    assert row["claim_id"] == "paper-shallow-scaffolded-recovery"
    assert row["claim_class"] == "scaffolded_training_proof"
    assert row["training_mode"] == "blind_training"
    assert row["evidence_class"]
    assert row["threshold_policy"] == "scaffolded_bounded_100_percent"
    assert row["dataset_manifest_sha256"]
    assert row["provenance_source"] == "sources/paper.pdf"
    assert row["provenance_expression"] == "exp(x)"
    assert "threshold_status" not in row

    claim_groups = list(csv.DictReader(result.table_paths["group_claim_csv"].open(encoding="utf-8")))
    assert claim_groups[0]["group"] == "paper-shallow-scaffolded-recovery"

    manifest = json.loads(result.manifest_path.read_text())
    assert manifest["counts"]["evidence_classes"]
    assert manifest["thresholds"]
    threshold = manifest["thresholds"][0]
    assert threshold["claim_id"] == "paper-shallow-scaffolded-recovery"
    assert threshold["threshold_policy_id"] == "scaffolded_bounded_100_percent"
    assert threshold["status"] in {"passed", "failed"}
    assert {"claim_id", "threshold_policy_id", "status", "passed", "eligible", "rate"} <= set(threshold)
    assert manifest["output"]["tables"]["group_evidence_class_csv"].endswith("group-evidence-class.csv")
    assert manifest["output"]["tables"]["group_claim_csv"].endswith("group-claim.csv")
    assert manifest["output"]["tables"]["group_threshold_policy_csv"].endswith("group-threshold-policy.csv")


def test_proof_basin_report_names_probe_suite_and_status_taxonomy(tmp_path):
    campaign_dir = tmp_path / "proof-basin-report"
    (campaign_dir / "tables").mkdir(parents=True)
    aggregate = {
        "runs": [
            _proof_basin_run(),
            _proof_basin_run(
                run_id="basin-beer-lambert-bound-probes-seed0-noise35",
                suite_id="proof-perturbed-basin-beer-probes",
                case_id="basin-beer-lambert-bound-probes",
                evidence_class="snapped_but_failed",
                classification="snapped_but_failed",
                status="snapped_but_failed",
                claim_status="failed",
                return_kind="snapped_but_failed",
                raw_status="snapped_but_failed",
                repair_status="not_repaired",
                perturbation_noise=35.0,
            ),
        ],
        "counts": {"total": 2, "verifier_recovered": 1, "same_ast_return": 1, "verified_equivalent_ast": 0, "evidence_classes": {}},
        "thresholds": [
            {
                "claim_id": "paper-perturbed-true-tree-basin",
                "threshold_policy_id": "bounded_100_percent",
                "status": "passed",
                "passed": 1,
                "eligible": 1,
                "rate": 1.0,
            }
        ],
    }
    manifest = {
        "preset": campaign_preset("proof-basin").as_dict(),
        "suite": {"id": "proof-perturbed-basin"},
        "output": {"raw_run_root": str(campaign_dir / "runs")},
        "reproducibility": {"command": "PYTHONPATH=src python -m eml_symbolic_regression.cli campaign proof-basin"},
    }
    table_paths = {"runs_csv": campaign_dir / "tables" / "runs.csv"}

    report_path = write_campaign_report(campaign_dir, manifest, aggregate, table_paths, {})
    report = report_path.read_text(encoding="utf-8")
    proof_section = report.split("## Proof Contract", 1)[1].split("## Figures", 1)[0]

    assert "proof-perturbed-basin-beer-probes" in report
    assert "| Field | Meaning |" in report
    assert "`return_kind`" in report
    assert "`raw_status`" in report
    assert "`repair_status`" in report
    assert "| Same-AST exact returns | 1 (50.0%) |" in report
    assert "| perturbed_tree | 2 | 1 | 1 | 0 | 1 | 0 | 0 | 1 |" in report
    assert "paper-perturbed-true-tree-basin" in proof_section
    assert "basin-beer-lambert-bound-probes" not in proof_section


def test_depth_curve_campaign_writes_depth_curve_tables_and_report(tmp_path):
    result = run_campaign(
        "proof-depth-curve",
        output_root=tmp_path,
        label="depth-curve",
        run_filter=RunFilter(case_ids=("depth-2-blind", "depth-2-perturbed"), seeds=(0,)),
    )

    assert result.table_paths["depth_curve_csv"].exists()
    rows = list(csv.DictReader(result.table_paths["depth_curve_csv"].open(encoding="utf-8")))
    assert {row["start_mode"] for row in rows} == {"blind", "perturbed_tree"}
    assert {row["depth"] for row in rows} == {"2"}

    report = result.report_path.read_text(encoding="utf-8")
    assert "## Depth Curve" in report
    assert "paper reports that blind recovery falls sharply with depth" in report
    assert "depth-curve-recovery.svg" in report


def test_campaign_writes_stable_svg_figures(tmp_path):
    result = run_campaign("smoke", output_root=tmp_path, label="figures-smoke")

    assert {
        "recovery_by_formula",
        "recovery_by_start_mode",
        "loss_before_after_snap",
        "beer_perturbation",
        "runtime_depth_budget",
        "failure_taxonomy",
    } <= set(result.figure_paths)

    for path in result.figure_paths.values():
        assert path.exists()
        text = path.read_text(encoding="utf-8")
        assert text.startswith("<svg ")
        assert "</svg>" in text

    assert result.figure_paths["recovery_by_formula"].name == "recovery-by-formula.svg"
    assert "-log10(loss)" in result.figure_paths["loss_before_after_snap"].read_text(encoding="utf-8")

    manifest = json.loads(result.manifest_path.read_text())
    assert "figures" in manifest["output"]
    assert manifest["output"]["figures"]["failure_taxonomy"].endswith("failure-taxonomy.svg")


def test_campaign_writes_self_contained_report(tmp_path):
    result = run_campaign(
        "smoke",
        output_root=tmp_path,
        label="report-smoke",
        run_filter=RunFilter(case_ids=("beer-warm", "planck-diagnostic")),
    )

    assert result.report_path is not None
    assert result.report_path.exists()
    report = result.report_path.read_text(encoding="utf-8")

    assert "# EML Benchmark Campaign Report: smoke" in report
    assert "## Headline Metrics" in report
    assert "## Regime Summary" in report
    assert "## What EML Demonstrates Well" in report
    assert "## Limitations" in report
    assert "## Next Experiments" in report
    assert "campaign smoke --output-root" in report
    assert "figures/recovery-by-formula.svg" in report
    assert "tables/runs.csv" in report
    assert "unsupported" in report
    assert "## Proof Contract" not in report
    assert "universal blind recovery" not in report
    assert "all elementary functions recovered" not in report

    manifest = json.loads(result.manifest_path.read_text())
    assert manifest["output"]["report_markdown"].endswith("report.md")


def test_limitations_section_counts_scaffolded_blind_recovery_honestly():
    text = _limitations_section(
        [
            {
                "start_mode": "blind",
                "claim_status": "recovered",
                "classification": "recovered",
                "evidence_class": "scaffolded_blind_training_recovered",
            },
            {
                "start_mode": "blind",
                "claim_status": "failed",
                "classification": "snapped_but_failed",
                "evidence_class": "snapped_but_failed",
            },
        ]
    )

    assert "Blind training recovery: 1/2 blind runs recovered." in text
    assert "1 scaffolded blind recoveries and 0 pure random-initialized blind recoveries" in text


def test_strengths_paragraph_stays_blind_for_blind_only_suite():
    runs = [
        {
            "start_mode": "blind",
            "claim_status": "recovered",
            "classification": "recovered",
            "evidence_class": "scaffolded_blind_training_recovered",
        }
    ]

    text = _strengths_paragraph(
        runs,
        {
            "verifier_recovered": 1,
            "same_ast_return": 0,
            "verified_equivalent_ast": 0,
            "total": 1,
        },
    )

    assert "bounded blind-training behavior" in text
    assert "scaffolded blind recoveries" in text
    assert "Warm-start runs are especially useful evidence" not in text


def test_strengths_paragraph_distinguishes_pure_blind_from_repaired_recovery():
    runs = [
        {
            "start_mode": "blind",
            "claim_status": "recovered",
            "classification": "recovered",
            "evidence_class": "blind_training_recovered",
        },
        {
            "start_mode": "blind",
            "claim_status": "recovered",
            "classification": "repaired_candidate",
            "evidence_class": "repaired_candidate",
        },
    ]

    text = _strengths_paragraph(
        runs,
        {
            "verifier_recovered": 2,
            "same_ast_return": 0,
            "verified_equivalent_ast": 0,
            "total": 2,
        },
    )

    assert "threshold-eligible pure blind recovery" in text
    assert "including 1 threshold-eligible pure blind recovery" in text
    assert "plus 1 repaired candidate" in text


def test_strengths_paragraph_pluralizes_pure_blind_recoveries():
    runs = [
        {
            "start_mode": "blind",
            "claim_status": "recovered",
            "classification": "recovered",
            "evidence_class": "blind_training_recovered",
        },
        {
            "start_mode": "blind",
            "claim_status": "recovered",
            "classification": "recovered",
            "evidence_class": "blind_training_recovered",
        },
    ]

    text = _strengths_paragraph(
        runs,
        {
            "verifier_recovered": 2,
            "same_ast_return": 0,
            "verified_equivalent_ast": 0,
            "total": 2,
        },
    )

    assert "including 2 threshold-eligible pure blind recoveries" in text
    assert "recoverys" not in text


def test_strengths_paragraph_describes_perturbed_tree_basin_without_warm_start_language():
    runs = [
        {
            "start_mode": "perturbed_tree",
            "claim_status": "recovered",
            "classification": "same_ast_return",
            "evidence_class": "perturbed_true_tree_recovered",
        },
        {
            "start_mode": "perturbed_tree",
            "claim_status": "recovered",
            "classification": "repaired_candidate",
            "evidence_class": "repaired_candidate",
        },
    ]

    text = _strengths_paragraph(
        runs,
        {
            "verifier_recovered": 2,
            "same_ast_return": 1,
            "verified_equivalent_ast": 0,
            "total": 2,
        },
    )

    assert "perturbed true-tree basin" in text
    assert "repaired candidates" in text
    assert "Warm-start runs are especially useful evidence" not in text


def test_limitations_section_counts_perturbed_tree_same_ast_and_repaired_rows():
    text = _limitations_section(
        [
            {
                "start_mode": "perturbed_tree",
                "classification": "same_ast_return",
                "return_kind": "same_ast_return",
                "claim_status": "recovered",
                "evidence_class": "perturbed_true_tree_recovered",
            },
            {
                "start_mode": "perturbed_tree",
                "classification": "repaired_candidate",
                "return_kind": "verified_equivalent_ast",
                "claim_status": "recovered",
                "evidence_class": "repaired_candidate",
            },
        ]
    )

    assert "Same-AST exact return: 1 runs" in text
    assert "Verified-equivalent exact return: 1 runs" in text


def test_proof_campaign_report_separates_threshold_status(tmp_path):
    result = run_campaign(
        "proof-shallow",
        output_root=tmp_path,
        label="proof-report",
        run_filter=RunFilter(case_ids=("shallow-exp-blind",), seeds=(0,)),
    )

    report = result.report_path.read_text(encoding="utf-8")
    manifest = json.loads(result.manifest_path.read_text())
    threshold = manifest["thresholds"][0]

    assert "## Regime Summary" in report
    assert "## Proof Contract" in report
    assert "| Claim | Threshold | Status | Passed | Eligible | Rate |" in report
    assert (
        f"| {threshold['claim_id']} | {threshold['threshold_policy_id']} | {threshold['status']} | "
        f"{threshold['passed']} | {threshold['eligible']} | {threshold['rate']:.3f} |"
    ) in report
    assert (
        "Bounded proof thresholds count only allowed verifier-owned training evidence classes; "
        "catalog and compile-only verification remain separate evidence classes."
    ) in report
    assert "universal blind recovery" not in report
    assert "all elementary functions recovered" not in report
