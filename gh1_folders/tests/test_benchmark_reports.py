import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from eml_symbolic_regression.benchmark import (
    BenchmarkCase,
    BenchmarkRun,
    BenchmarkRunResult,
    BenchmarkSuite,
    DatasetConfig,
    OptimizerBudget,
    RunFilter,
    _extract_run_metrics,
    aggregate_evidence,
    builtin_suite,
    render_aggregate_markdown,
    run_benchmark_suite,
    write_aggregate_reports,
)


def _synthetic_result(
    *,
    case_id: str,
    start_mode: str,
    training_mode: str,
    evidence_class: str,
    status: str = "recovered",
    claim_status: str = "recovered",
    perturbation_noise: float = 0.0,
    depth: int = 1,
    return_kind: str | None = None,
    raw_status: str | None = None,
    repair_status: str | None = None,
    claim_id: str | None = "paper-shallow-blind-recovery",
    claim_class: str | None = "measured_training_boundary",
    threshold_policy_id: str | None = "measured_pure_blind_recovery",
    track: str = "literal_constants",
    constants_policy: str = "literal_constants",
) -> BenchmarkRunResult:
    run = BenchmarkRun(
        suite_id="synthetic-proof",
        case_id=case_id,
        formula="exp",
        start_mode=start_mode,
        seed=0,
        perturbation_noise=perturbation_noise,
        dataset=DatasetConfig(points=12),
        optimizer=OptimizerBudget(depth=depth, steps=1, restarts=1),
        artifact_path=Path(f"/tmp/{case_id}.json"),
        claim_id=claim_id,
        threshold_policy_id=threshold_policy_id,
        training_mode=training_mode,
        track=track,
        constants_policy=constants_policy,
    )
    payload = {
        "run": run.as_dict(),
        "status": status,
        "claim_status": claim_status,
        "claim_id": claim_id,
        "claim_class": claim_class,
        "training_mode": training_mode,
        "evidence_class": evidence_class,
        "return_kind": return_kind,
        "raw_status": raw_status,
        "repair_status": repair_status,
        "threshold": {"id": threshold_policy_id} if threshold_policy_id is not None else None,
        "benchmark_track": run.as_dict()["benchmark_track"],
        "dataset": run.dataset.as_dict(),
        "dataset_manifest": {"schema": "eml.proof_dataset_manifest.v1"},
        "provenance": {"symbolic_expression": "exp(x)"},
        "metrics": {
            "best_loss": 0.01,
            "post_snap_loss": 0.02,
            "snap_min_margin": 0.7,
        },
        "stage_statuses": {},
    }
    return BenchmarkRunResult(run, status, run.artifact_path, payload)


def test_run_metric_extraction_exposes_phase84_geml_fields():
    metrics = _extract_run_metrics(
        {
            "run": {"start_mode": "blind", "optimizer": {"restarts": 1}},
            "budget": {"operator_family": {"label": "ipi_eml"}, "semantics_mode": "guarded"},
            "trained_eml_candidate": {
                "config": {"operator_family": {"label": "ipi_eml"}, "semantics_mode": "guarded"},
                "best_restart": {
                    "loss_summary": {"gradient_l2_norm_max": 1.5, "gradient_max_abs_max": 0.75},
                    "final_anomalies": {
                        "nan_count": 1,
                        "inf_count": 2,
                        "exp_overflow_count": 3,
                        "log_branch_cut_count": 4,
                        "log_branch_cut_proximity_count": 5,
                        "log_branch_cut_crossing_count": 6,
                        "branch_input_count": 7,
                    },
                },
                "selected_candidate": {
                    "best_fit_loss": 0.2,
                    "pre_snap_mse": 0.3,
                    "post_snap_loss": 0.4,
                    "post_snap_mse": 0.4,
                    "branch_diagnostics": {"status": "performed", "candidate_failure_class": "not_failed"},
                },
                "timing": {"wall_clock_seconds": 1.25, "attempt_count": 1, "candidate_count": 2},
            },
            "trained_eml_verification": {"status": "recovered"},
        }
    )

    assert metrics["operator_family"] == "ipi_eml"
    assert metrics["pre_snap_mse"] == 0.3
    assert metrics["post_snap_mse"] == 0.4
    assert metrics["gradient_l2_norm_max"] == 1.5
    assert metrics["gradient_max_abs_max"] == 0.75
    assert metrics["optimizer_wall_clock_seconds"] == 1.25
    assert metrics["optimizer_candidate_count"] == 2
    assert metrics["anomaly_nan_count"] == 1
    assert metrics["anomaly_log_branch_cut_proximity_count"] == 5
    assert metrics["anomaly_log_branch_cut_crossing_count"] == 6
    assert metrics["anomaly_branch_input_count"] == 7
    assert metrics["branch_diagnostics_status"] == "performed"
    assert metrics["branch_failure_class"] == "not_failed"


def test_aggregate_evidence_separates_unsupported_and_same_ast(tmp_path):
    base = builtin_suite("smoke")
    suite = type(base)(base.id, base.description, base.cases, tmp_path / "artifacts")

    result = run_benchmark_suite(suite, run_filter=RunFilter(case_ids=("beer-warm", "planck-diagnostic")))
    aggregate = aggregate_evidence(result)

    assert aggregate["schema"] == "eml.benchmark_aggregate.v1"
    assert aggregate["counts"]["total"] == 2
    assert aggregate["counts"]["unsupported"] == 1
    assert aggregate["counts"]["same_ast_return"] == 1
    assert aggregate["counts"]["verifier_recovered"] == 1
    assert aggregate["counts"]["evidence_classes"]["same_ast"] == 1
    assert aggregate["counts"]["evidence_classes"]["unsupported"] == 1
    assert {group["key"] for group in aggregate["groups"]["evidence_class"]} == {"same_ast", "unsupported"}
    assert {run["classification"] for run in aggregate["runs"]} == {"same_ast_warm_start_return", "unsupported"}
    warm_run = next(run for run in aggregate["runs"] if run["start_mode"] == "warm_start")
    assert warm_run["warm_start_evidence"] == "exact_seed_round_trip"
    assert warm_run["ast_return_status"] == "same_ast"
    assert warm_run["total_restarts"] == 1


def test_aggregate_run_rows_preserve_hybrid_selection_and_refit_metrics():
    suite = BenchmarkSuite("synthetic-proof", "synthetic proof aggregate", ())
    result = _synthetic_result(
        case_id="hybrid-lock",
        start_mode="blind",
        training_mode="blind_training",
        evidence_class="blind_training_recovered",
    )
    result.payload["metrics"].update(
        {
            "selected_candidate_id": "selected-7",
            "fallback_candidate_id": "fallback-3",
            "selection_mode": "verifier_gated_exact_candidate_pool",
            "refit_status": "accepted",
            "refit_accepted": True,
            "refit_constant_count": 2,
        }
    )

    aggregate = aggregate_evidence(SimpleNamespace(suite=suite, results=(result,)))
    metrics = aggregate["runs"][0]["metrics"]

    assert metrics["selected_candidate_id"] == "selected-7"
    assert metrics["fallback_candidate_id"] == "fallback-3"
    assert metrics["selection_mode"] == "verifier_gated_exact_candidate_pool"
    assert metrics["refit_status"] == "accepted"
    assert metrics["refit_accepted"] is True
    assert metrics["refit_constant_count"] == 2


def test_aggregate_evidence_keeps_benchmark_track_denominators_separate():
    suite = BenchmarkSuite("synthetic-tracks", "synthetic track aggregate", ())
    result = SimpleNamespace(
        suite=suite,
        results=(
            _synthetic_result(
                case_id="exp-basis",
                start_mode="compile",
                training_mode="compile_only_verification",
                evidence_class="unsupported",
                status="unsupported",
                claim_status="unsupported",
                track="basis_only",
                constants_policy="basis_only",
                claim_id=None,
                claim_class=None,
                threshold_policy_id=None,
            ),
            _synthetic_result(
                case_id="exp-literal",
                start_mode="warm_start",
                training_mode="compiler_warm_start_training",
                evidence_class="same_ast",
                status="same_ast_return",
                claim_status="recovered",
                track="literal_constants",
                constants_policy="literal_constants",
                claim_id=None,
                claim_class=None,
                threshold_policy_id=None,
            ),
        ),
    )

    aggregate = aggregate_evidence(result)
    tracks = {row["track"]: row for row in aggregate["tracks"]}
    markdown = render_aggregate_markdown(aggregate)

    assert tracks["basis_only"]["total"] == 1
    assert tracks["basis_only"]["unsupported"] == 1
    assert tracks["basis_only"]["verifier_recovered"] == 0
    assert tracks["basis_only"]["constants_policies"] == ["basis_only"]
    assert tracks["literal_constants"]["total"] == 1
    assert tracks["literal_constants"]["verifier_recovered"] == 1
    assert tracks["literal_constants"]["constants_policies"] == ["literal_constants"]
    assert {group["key"] for group in aggregate["groups"]["benchmark_track"]} == {"basis_only", "literal_constants"}
    assert "## Track Denominators" in markdown
    assert "| basis_only | 1 | 0 | 0 | 0 | 1 | 0 | 0.000 | basis_only |" in markdown


def test_aggregate_evidence_separates_verification_passed_from_trained_recovery():
    suite = BenchmarkSuite("synthetic-two-axis", "synthetic two-axis aggregate", ())
    result = SimpleNamespace(
        suite=suite,
        results=(
            _synthetic_result(
                case_id="compile-support",
                start_mode="compile",
                training_mode="compile_only_verification",
                evidence_class="compile_only_verified",
                claim_id=None,
                claim_class=None,
                threshold_policy_id=None,
                track="basis_only",
                constants_policy="basis_only",
            ),
            _synthetic_result(
                case_id="warm-trained",
                start_mode="warm_start",
                training_mode="compiler_warm_start_training",
                evidence_class="same_ast",
                status="same_ast_return",
                claim_id=None,
                claim_class=None,
                threshold_policy_id=None,
            ),
            _synthetic_result(
                case_id="unsupported",
                start_mode="compile",
                training_mode="compile_only_verification",
                evidence_class="unsupported",
                status="unsupported",
                claim_status="unsupported",
                claim_id=None,
                claim_class=None,
                threshold_policy_id=None,
                track="basis_only",
                constants_policy="basis_only",
            ),
        ),
    )

    aggregate = aggregate_evidence(result)
    rows = {run["case_id"]: run for run in aggregate["runs"]}

    assert aggregate["counts"]["verification_passed"] == 2
    assert aggregate["counts"]["trained_exact_recovery"] == 1
    assert aggregate["counts"]["compile_only_verified_support"] == 1
    assert rows["compile-support"]["verification_outcome"] == "recovered"
    assert rows["compile-support"]["discovery_class"] == "compile_only_verified_support"
    assert rows["warm-trained"]["discovery_class"] == "trained_exact_recovery"
    assert rows["warm-trained"]["warm_start_evidence"] == "exact_seed_round_trip"
    assert rows["warm-trained"]["ast_return_status"] == "same_ast"
    assert rows["unsupported"]["verification_outcome"] == "unsupported"


def test_warm_start_depth_gate_overrides_compiled_seed_claim_status(tmp_path):
    case = BenchmarkCase.from_mapping(
        {
            "id": "beer-warm-depth-gated",
            "formula": "beer_lambert",
            "start_mode": "warm_start",
            "seeds": [0],
            "perturbation_noise": [0.0],
            "dataset": {"points": 12},
            "optimizer": {
                "warm_steps": 1,
                "warm_restarts": 1,
                "max_warm_depth": 1,
            },
        },
        path="cases[0]",
    )
    suite = BenchmarkSuite("warm-depth-gate", "depth-gated warm-start regression", (case,), tmp_path / "artifacts")

    result = run_benchmark_suite(suite)
    aggregate = aggregate_evidence(result)
    artifact = json.loads(result.results[0].artifact_path.read_text(encoding="utf-8"))

    assert result.results[0].status == "unsupported"
    assert artifact["claim_status"] == "unsupported"
    assert artifact["warm_start_eml"]["reason"] == "depth_too_large_for_warm_start"
    assert aggregate["counts"]["verifier_recovered"] == 0
    assert aggregate["counts"]["unsupported"] == 1
    assert aggregate["runs"][0]["claim_status"] == "unsupported"


def test_shallow_pure_blind_threshold_reports_only_random_initialized_recovery():
    suite = BenchmarkSuite("synthetic-proof", "synthetic proof aggregate", ())
    result = SimpleNamespace(
        suite=suite,
        results=(
            _synthetic_result(case_id="blind", start_mode="blind", training_mode="blind_training", evidence_class="blind_training_recovered"),
            _synthetic_result(
                case_id="scaffolded-blind",
                start_mode="blind",
                training_mode="blind_training",
                evidence_class="scaffolded_blind_training_recovered",
            ),
            _synthetic_result(case_id="compile", start_mode="compile", training_mode="compile_only_verification", evidence_class="compile_only_verified"),
            _synthetic_result(case_id="catalog", start_mode="catalog", training_mode="catalog_verification", evidence_class="catalog_verified"),
            _synthetic_result(
                case_id="warm",
                start_mode="warm_start",
                training_mode="compiler_warm_start_training",
                evidence_class="compiler_warm_start_recovered",
            ),
            _synthetic_result(
                case_id="repair",
                start_mode="blind",
                training_mode="blind_training",
                evidence_class="repaired_candidate",
                status="repaired_candidate",
                claim_status="failed",
            ),
            _synthetic_result(
                case_id="verified-equivalent",
                start_mode="warm_start",
                training_mode="compiler_warm_start_training",
                evidence_class="verified_equivalent",
                status="verified_equivalent_ast",
                claim_status="verified_equivalent_ast",
            ),
            _synthetic_result(
                case_id="same-ast",
                start_mode="warm_start",
                training_mode="compiler_warm_start_training",
                evidence_class="same_ast",
                status="same_ast_return",
                claim_status="same_ast_return",
            ),
            _synthetic_result(
                case_id="soft-fit",
                start_mode="blind",
                training_mode="blind_training",
                evidence_class="soft_fit_only",
                status="soft_fit_only",
                claim_status="failed",
            ),
        ),
    )

    aggregate = aggregate_evidence(result)
    threshold = aggregate["thresholds"][0]

    assert aggregate["counts"]["evidence_classes"] == {
        "blind_training_recovered": 1,
        "catalog_verified": 1,
        "compile_only_verified": 1,
        "compiler_warm_start_recovered": 1,
        "repaired_candidate": 1,
        "same_ast": 1,
        "scaffolded_blind_training_recovered": 1,
        "soft_fit_only": 1,
        "verified_equivalent": 1,
    }
    assert threshold["claim_id"] == "paper-shallow-blind-recovery"
    assert threshold["threshold_policy_id"] == "measured_pure_blind_recovery"
    assert threshold["eligible"] == 9
    assert threshold["passed"] == 1
    assert threshold["failed"] == 8
    assert threshold["rate"] == pytest.approx(1.0 / 9.0)
    assert threshold["required_rate"] is None
    assert threshold["status"] == "reported"
    assert threshold["evidence_classes"] == aggregate["counts"]["evidence_classes"]


def test_shallow_scaffolded_threshold_counts_only_scaffolded_training_recovery():
    suite = BenchmarkSuite("synthetic-proof", "synthetic scaffolded proof aggregate", ())
    result = SimpleNamespace(
        suite=suite,
        results=(
            _synthetic_result(
                case_id="scaffolded-blind",
                start_mode="blind",
                training_mode="blind_training",
                evidence_class="scaffolded_blind_training_recovered",
                claim_id="paper-shallow-scaffolded-recovery",
                claim_class="scaffolded_training_proof",
                threshold_policy_id="scaffolded_bounded_100_percent",
            ),
            _synthetic_result(
                case_id="random-blind",
                start_mode="blind",
                training_mode="blind_training",
                evidence_class="blind_training_recovered",
                claim_id="paper-shallow-scaffolded-recovery",
                claim_class="scaffolded_training_proof",
                threshold_policy_id="scaffolded_bounded_100_percent",
            ),
            _synthetic_result(
                case_id="compile",
                start_mode="compile",
                training_mode="compile_only_verification",
                evidence_class="compile_only_verified",
                claim_id="paper-shallow-scaffolded-recovery",
                claim_class="scaffolded_training_proof",
                threshold_policy_id="scaffolded_bounded_100_percent",
            ),
        ),
    )

    threshold = aggregate_evidence(result)["thresholds"][0]

    assert threshold["claim_id"] == "paper-shallow-scaffolded-recovery"
    assert threshold["threshold_policy_id"] == "scaffolded_bounded_100_percent"
    assert threshold["eligible"] == 3
    assert threshold["passed"] == 1
    assert threshold["failed"] == 2
    assert threshold["rate"] == pytest.approx(1.0 / 3.0)
    assert threshold["required_rate"] == 1.0
    assert threshold["status"] == "failed"
    assert threshold["evidence_classes"] == {
        "blind_training_recovered": 1,
        "compile_only_verified": 1,
        "scaffolded_blind_training_recovered": 1,
    }


def test_perturbed_bounded_threshold_counts_repaired_candidates():
    suite = BenchmarkSuite("synthetic-perturbed-proof", "synthetic perturbed proof aggregate", ())
    result = SimpleNamespace(
        suite=suite,
        results=(
            _synthetic_result(
                case_id="raw",
                start_mode="perturbed_tree",
                training_mode="perturbed_true_tree_training",
                evidence_class="perturbed_true_tree_recovered",
                perturbation_noise=0.05,
                return_kind="same_ast_return",
                raw_status="recovered",
                claim_id="paper-perturbed-true-tree-basin",
                threshold_policy_id="bounded_100_percent",
            ),
            _synthetic_result(
                case_id="repair",
                start_mode="perturbed_tree",
                training_mode="perturbed_true_tree_training",
                evidence_class="repaired_candidate",
                status="repaired_candidate",
                claim_status="recovered",
                perturbation_noise=0.05,
                return_kind="snapped_but_failed",
                raw_status="snapped_but_failed",
                repair_status="repaired",
                claim_id="paper-perturbed-true-tree-basin",
                threshold_policy_id="bounded_100_percent",
            ),
            _synthetic_result(
                case_id="failed",
                start_mode="perturbed_tree",
                training_mode="perturbed_true_tree_training",
                evidence_class="snapped_but_failed",
                status="snapped_but_failed",
                claim_status="failed",
                perturbation_noise=0.05,
                return_kind="snapped_but_failed",
                raw_status="snapped_but_failed",
                repair_status="not_repaired",
                claim_id="paper-perturbed-true-tree-basin",
                threshold_policy_id="bounded_100_percent",
            ),
        ),
    )

    threshold = aggregate_evidence(result)["thresholds"][0]

    assert threshold["claim_id"] == "paper-perturbed-true-tree-basin"
    assert threshold["eligible"] == 3
    assert threshold["passed"] == 2
    assert threshold["failed"] == 1
    assert threshold["status"] == "failed"
    assert threshold["evidence_classes"] == {
        "perturbed_true_tree_recovered": 1,
        "repaired_candidate": 1,
        "snapped_but_failed": 1,
    }


@pytest.mark.parametrize(
    "evidence_class",
    (
        "compiler_warm_start_recovered",
        "verified_equivalent",
        "same_ast",
        "scaffolded_blind_training_recovered",
    ),
)
def test_perturbed_bounded_threshold_rejects_non_perturbed_evidence_classes(evidence_class):
    suite = BenchmarkSuite("synthetic-perturbed-proof", "synthetic perturbed proof aggregate", ())
    result = SimpleNamespace(
        suite=suite,
        results=(
            _synthetic_result(
                case_id=evidence_class,
                start_mode="perturbed_tree",
                training_mode="perturbed_true_tree_training",
                evidence_class=evidence_class,
                perturbation_noise=0.05,
                claim_id="paper-perturbed-true-tree-basin",
                threshold_policy_id="bounded_100_percent",
            ),
        ),
    )

    threshold = aggregate_evidence(result)["thresholds"][0]

    assert threshold["claim_id"] == "paper-perturbed-true-tree-basin"
    assert threshold["eligible"] == 1
    assert threshold["passed"] == 0
    assert threshold["failed"] == 1
    assert threshold["status"] == "failed"
    assert threshold["evidence_classes"] == {evidence_class: 1}


def test_aggregate_evidence_keeps_perturbed_raw_and_repair_taxonomy_distinct():
    suite = BenchmarkSuite("synthetic-perturbed-taxonomy", "synthetic taxonomy aggregate", ())
    common = {
        "start_mode": "perturbed_tree",
        "training_mode": "perturbed_true_tree_training",
        "claim_id": None,
        "claim_class": None,
        "threshold_policy_id": None,
        "perturbation_noise": 0.05,
    }
    result = SimpleNamespace(
        suite=suite,
        results=(
            _synthetic_result(
                case_id="same-ast",
                evidence_class="perturbed_true_tree_recovered",
                return_kind="same_ast_return",
                raw_status="recovered",
                **common,
            ),
            _synthetic_result(
                case_id="verified-equivalent",
                evidence_class="perturbed_true_tree_recovered",
                return_kind="verified_equivalent_ast",
                raw_status="recovered",
                **common,
            ),
            _synthetic_result(
                case_id="repair",
                evidence_class="repaired_candidate",
                status="repaired_candidate",
                claim_status="recovered",
                return_kind="snapped_but_failed",
                raw_status="snapped_but_failed",
                repair_status="repaired",
                **common,
            ),
            _synthetic_result(
                case_id="snapped",
                evidence_class="perturbed_true_tree_recovered",
                status="snapped_but_failed",
                claim_status="failed",
                return_kind="snapped_but_failed",
                raw_status="snapped_but_failed",
                repair_status="not_repaired",
                **common,
            ),
            _synthetic_result(
                case_id="soft-fit",
                evidence_class="perturbed_true_tree_recovered",
                status="soft_fit_only",
                claim_status="failed",
                return_kind="soft_fit_only",
                raw_status="soft_fit_only",
                repair_status="not_repaired",
                **common,
            ),
            _synthetic_result(
                case_id="unsupported",
                evidence_class="unsupported",
                status="unsupported",
                claim_status="unsupported",
                raw_status="unsupported",
                **common,
            ),
            _synthetic_result(
                case_id="execution-error",
                evidence_class="execution_failure",
                status="execution_error",
                claim_status="execution_error",
                raw_status="execution_error",
                **common,
            ),
        ),
    )
    result.results[2].payload["metrics"].update(
        {
            "repair_candidate_root_count": 2,
            "repair_deduped_variant_count": 7,
            "repair_accepted_candidate_id": "fallback",
            "repair_accepted_candidate_source": "hardening_checkpoint",
            "repair_accepted_candidate_root_source": "fallback",
        }
    )

    aggregate = aggregate_evidence(result)
    markdown = render_aggregate_markdown(aggregate)
    classifications = {run["case_id"]: run["classification"] for run in aggregate["runs"]}
    repair_metrics = next(run["metrics"] for run in aggregate["runs"] if run["case_id"] == "repair")

    assert classifications == {
        "same-ast": "same_ast_return",
        "verified-equivalent": "verified_equivalent_ast",
        "repair": "repaired_candidate",
        "snapped": "snapped_but_failed",
        "soft-fit": "soft_fit_only",
        "unsupported": "unsupported",
        "execution-error": "execution_failure",
    }
    assert aggregate["counts"]["same_ast_return"] == 1
    assert aggregate["counts"]["verified_equivalent_ast"] == 1
    assert aggregate["counts"]["repaired_candidate"] == 1
    assert repair_metrics["repair_candidate_root_count"] == 2
    assert repair_metrics["repair_deduped_variant_count"] == 7
    assert repair_metrics["repair_accepted_candidate_id"] == "fallback"
    assert repair_metrics["repair_accepted_candidate_source"] == "hardening_checkpoint"
    assert repair_metrics["repair_accepted_candidate_root_source"] == "fallback"
    assert {group["key"] for group in aggregate["groups"]["return_kind"]} >= {
        "same_ast_return",
        "verified_equivalent_ast",
        "snapped_but_failed",
        "soft_fit_only",
    }
    assert {group["key"] for group in aggregate["groups"]["raw_status"]} >= {
        "recovered",
        "snapped_but_failed",
        "soft_fit_only",
        "unsupported",
        "execution_error",
    }
    assert {group["key"] for group in aggregate["groups"]["repair_status"]} >= {"repaired", "not_repaired", "none"}
    assert "## By Return Kind" in markdown
    assert "## By Raw Status" in markdown
    assert "## By Repair Status" in markdown


def test_measured_depth_curve_threshold_is_reported_not_failed():
    suite = BenchmarkSuite("synthetic-depth", "synthetic depth aggregate", ())
    result = SimpleNamespace(
        suite=suite,
        results=(
            _synthetic_result(
                case_id="depth-6-blind",
                start_mode="blind",
                training_mode="blind_training",
                evidence_class="failed",
                status="failed",
                claim_status="failed",
                claim_id="paper-blind-depth-degradation",
                claim_class="measured_depth_curve",
                threshold_policy_id="measured_depth_curve",
            ),
        ),
    )

    aggregate = aggregate_evidence(result)
    threshold = aggregate["thresholds"][0]

    assert threshold["claim_id"] == "paper-blind-depth-degradation"
    assert threshold["threshold_policy_id"] == "measured_depth_curve"
    assert threshold["eligible"] == 1
    assert threshold["passed"] == 1
    assert threshold["rate"] == 1.0
    assert threshold["required_rate"] is None
    assert threshold["status"] == "reported"


def test_depth_curve_summary_groups_by_depth_and_mode():
    suite = BenchmarkSuite("synthetic-depth-curve", "synthetic depth curve aggregate", ())
    result = SimpleNamespace(
        suite=suite,
        results=(
            _synthetic_result(
                case_id="depth-2-blind",
                start_mode="blind",
                training_mode="blind_training",
                evidence_class="blind_training_recovered",
                depth=2,
                claim_id="paper-blind-depth-degradation",
                claim_class="measured_depth_curve",
                threshold_policy_id="measured_depth_curve",
            ),
            _synthetic_result(
                case_id="depth-4-blind",
                start_mode="blind",
                training_mode="blind_training",
                evidence_class="failed",
                status="failed",
                claim_status="failed",
                depth=4,
                claim_id="paper-blind-depth-degradation",
                claim_class="measured_depth_curve",
                threshold_policy_id="measured_depth_curve",
            ),
            _synthetic_result(
                case_id="depth-4-perturbed",
                start_mode="perturbed_tree",
                training_mode="perturbed_true_tree_training",
                evidence_class="perturbed_true_tree_recovered",
                perturbation_noise=0.05,
                depth=4,
                claim_id="paper-blind-depth-degradation",
                claim_class="measured_depth_curve",
                threshold_policy_id="measured_depth_curve",
            ),
        ),
    )

    aggregate = aggregate_evidence(result)
    rows = aggregate["depth_curve"]
    markdown = render_aggregate_markdown(aggregate)

    assert {(row["depth"], row["start_mode"]) for row in rows} == {(2, "blind"), (4, "blind"), (4, "perturbed_tree")}
    depth4_blind = next(row for row in rows if row["depth"] == 4 and row["start_mode"] == "blind")
    depth4_perturbed = next(row for row in rows if row["depth"] == 4 and row["start_mode"] == "perturbed_tree")

    assert depth4_blind["recovered"] == 0
    assert depth4_blind["total"] == 1
    assert depth4_blind["recovery_rate"] == 0.0
    assert depth4_blind["seed_count"] == 1
    assert depth4_blind["best_loss_values"] == [0.01]
    assert depth4_perturbed["recovered"] == 1
    assert depth4_perturbed["recovery_rate"] == 1.0
    assert depth4_perturbed["evidence_classes"] == {"perturbed_true_tree_recovered": 1}
    assert "## Depth Curve" in markdown
    assert "| 4 | blind | 1 | 0 | 1 | 0.000 |" in markdown


def test_write_aggregate_reports_outputs_json_and_markdown(tmp_path):
    base = builtin_suite("smoke")
    suite = type(base)(base.id, base.description, base.cases, tmp_path / "artifacts")
    result = run_benchmark_suite(suite, run_filter=RunFilter(case_ids=("planck-diagnostic",)))

    paths = write_aggregate_reports(result)

    assert paths["json"].exists()
    assert paths["markdown"].exists()
    markdown = paths["markdown"].read_text()
    assert "# Benchmark Evidence: smoke" in markdown
    assert "## By Evidence Class" in markdown
    assert "## Thresholds" in markdown
    assert "| planck |" in markdown


def test_markdown_report_contains_run_artifact_paths(tmp_path):
    base = builtin_suite("smoke")
    suite = type(base)(base.id, base.description, base.cases, tmp_path / "artifacts")
    result = run_benchmark_suite(suite, run_filter=RunFilter(case_ids=("planck-diagnostic",)))

    markdown = render_aggregate_markdown(aggregate_evidence(result))

    assert "planck-diagnostic" in markdown
    assert ".json" in markdown


def test_smoke_benchmark_exercises_required_paths_and_aggregate(tmp_path):
    base = builtin_suite("smoke")
    suite = type(base)(base.id, base.description, base.cases, tmp_path / "artifacts")

    result = run_benchmark_suite(suite)
    paths = write_aggregate_reports(result)
    aggregate = aggregate_evidence(result)

    assert {run.start_mode for run in (item.run for item in result.results)} == {"blind", "warm_start", "compile"}
    assert {"recovered", "snapped_but_failed", "same_ast_return", "unsupported"} >= {item.status for item in result.results}
    assert aggregate["counts"]["total"] == 3
    assert aggregate["counts"]["verifier_recovered"] == 2
    assert aggregate["counts"]["unsupported"] == 1
    assert aggregate["counts"]["same_ast_return"] == 1
    assert aggregate["counts"]["failed"] == 0
    assert paths["json"].exists()
    assert paths["markdown"].exists()
