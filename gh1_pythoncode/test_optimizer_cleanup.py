import numpy as np

import eml_symbolic_regression.optimize as optimize
from eml_symbolic_regression.cleanup import cleanup_candidate
from eml_symbolic_regression.datasets import get_demo
from eml_symbolic_regression.expression import Const, Var, ipi_eml_expr
from eml_symbolic_regression.optimize import TrainingConfig, fit_eml_tree
from eml_symbolic_regression.semantics import ceml_s_operator, ipi_eml_operator, zeml_s_operator
from eml_symbolic_regression.verify import DataSplit, verify_candidate


EXPECTED_CENTERED_SCAFFOLD_EXCLUSIONS = [
    "exp:centered_family_same_family_witness_missing",
    "log:centered_family_same_family_witness_missing",
    "scaled_exp:centered_family_same_family_witness_missing",
]


def test_optimizer_returns_snapped_candidate_manifest():
    spec = get_demo("exp")
    train = spec.make_splits(points=16)[0]
    result = fit_eml_tree(
        train.inputs,
        train.target,
        TrainingConfig(depth=1, variables=("x",), steps=2, restarts=1, seed=123),
    )
    assert result.status in {"snapped_candidate", "failed"}
    assert "restarts" in result.manifest
    assert result.manifest["config"]["semantics_mode"] == "guarded"
    assert result.manifest["semantics_alignment"]["training_semantics_mode"] == "guarded"
    assert result.manifest["semantics_alignment"]["objective_matches_verifier_semantics"] is False
    assert result.manifest["semantics_alignment"]["fallback_reason"] is not None
    assert result.snap.expression.node_count() >= 3


def test_optimizer_manifest_records_faithful_semantics_alignment_and_certificates():
    spec = get_demo("exp")
    splits = spec.make_splits(points=16)
    result = fit_eml_tree(
        splits[0].inputs,
        splits[0].target,
        TrainingConfig(depth=1, variables=("x",), steps=2, restarts=1, seed=0, semantics_mode="faithful"),
        verification_splits=splits,
    )

    alignment = result.manifest["semantics_alignment"]

    assert alignment["training_semantics_mode"] == "faithful"
    assert alignment["objective_matches_verifier_semantics"] is True
    assert alignment["fallback_reason"] is None
    assert "trace_totals" in alignment["anomaly_summary"]
    assert alignment["post_snap_mismatch"]["selected_candidate_id"] == result.manifest["selected_candidate"]["candidate_id"]
    assert alignment["verifier_evidence"]["certificate_status"] == result.verification.certificate_status
    assert alignment["verifier_evidence"]["evidence_level"] == result.verification.evidence_level


def test_optimizer_scaffold_recovers_exp_with_manifest_provenance():
    spec = get_demo("exp")
    splits = spec.make_splits(points=16)
    result = fit_eml_tree(
        splits[0].inputs,
        splits[0].target,
        TrainingConfig(depth=1, variables=("x",), steps=2, restarts=1, seed=0),
    )
    report = verify_candidate(result.snap.expression, splits)
    kinds = [(attempt.get("initialization") or {}).get("kind") for attempt in result.manifest["restarts"]]

    assert report.status == "recovered"
    assert result.manifest["config"]["scaffold_initializers"] == ["exp", "log", "scaled_exp"]
    assert "scaffold_exp" in kinds


def test_optimizer_runs_fixed_centered_family_with_manifest_metadata():
    x = np.linspace(-1.0, 1.0, 16)
    target = 2.0 * np.expm1(x / 2.0)
    result = fit_eml_tree(
        {"x": x},
        target,
        TrainingConfig(
            depth=1,
            variables=("x",),
            steps=2,
            restarts=1,
            seed=0,
            operator_family=ceml_s_operator(2.0),
        ),
    )

    assert result.snap.expression.to_node()["operator"]["label"] == "CEML_2"
    assert result.manifest["config"]["operator_family"]["label"] == "CEML_2"
    assert result.manifest["config"]["scaffold_initializers"] == []
    assert result.manifest["scaffold_exclusions"] == EXPECTED_CENTERED_SCAFFOLD_EXCLUSIONS
    assert result.manifest["scaffold_witness_operator"]["label"] == "CEML_2"
    assert all(not item["attempt_kind"].startswith("scaffold_") for item in result.manifest["restarts"])


def test_optimizer_preserves_centered_schedule_metadata():
    x = np.linspace(-1.0, 1.0, 16)
    target = np.expm1(x)
    result = fit_eml_tree(
        {"x": x},
        target,
        TrainingConfig(
            depth=1,
            variables=("x",),
            steps=4,
            restarts=1,
            seed=0,
            operator_schedule=(zeml_s_operator(8.0), zeml_s_operator(4.0)),
        ),
    )

    assert result.manifest["config"]["operator_schedule"][0]["label"] == "ZEML_8"
    assert result.manifest["config"]["operator_schedule"][1]["label"] == "ZEML_4"
    assert result.manifest["config"]["scaffold_initializers"] == []
    assert result.manifest["scaffold_exclusions"] == EXPECTED_CENTERED_SCAFFOLD_EXCLUSIONS
    assert result.manifest["scaffold_witness_operator"]["label"] == "ZEML_8"
    assert all(not item["attempt_kind"].startswith("scaffold_") for item in result.manifest["restarts"])
    assert [item["operator"]["label"] for item in result.manifest["operator_trace"][:2]] == ["ZEML_8", "ZEML_4"]
    assert result.manifest["operator_trace"][-1]["phase"] == "hardening"
    assert result.manifest["operator_trace"][-1]["operator"]["label"] == "ZEML_4"
    assert result.snap.expression.to_node()["operator"]["label"] == "ZEML_4"


def test_optimizer_runs_ipi_eml_with_branch_and_snap_metadata():
    x = np.linspace(-0.5, 0.5, 16)
    target = np.exp(1j * np.pi * x)
    split = DataSplit(
        name="heldout",
        inputs={"x": x},
        target=target,
        target_mpmath=lambda context: np.exp(1j * np.pi * context["x"]),
    )

    def initializer(model, restart, seed):
        embedding = model.embed_expr(ipi_eml_expr(Var("x"), Const(1.0)))
        return {"kind": "ipi_exact_seed", "restart": restart, "seed": seed, "embedding": embedding.as_dict()}

    result = fit_eml_tree(
        {"x": x},
        target,
        TrainingConfig(
            depth=1,
            variables=("x",),
            steps=1,
            restarts=1,
            lr=0.0,
            seed=0,
            operator_family=ipi_eml_operator(),
        ),
        initializer=initializer,
        verification_splits=[split],
    )

    selected = result.manifest["selected_candidate"]
    trace_row = result.manifest["restarts"][0]["trace"][0]
    trace_totals = result.manifest["semantics_alignment"]["anomaly_summary"]["trace_totals"]

    assert result.snap.expression.to_node()["operator"]["label"] == "ipi_eml"
    assert result.manifest["config"]["operator_family"]["label"] == "ipi_eml"
    assert result.manifest["config"]["scaffold_initializers"] == []
    assert result.manifest["scaffold_exclusions"] == EXPECTED_CENTERED_SCAFFOLD_EXCLUSIONS
    assert selected["best_fit_loss"] >= 0.0
    assert selected["pre_snap_mse"] >= 0.0
    assert selected["post_snap_mse"] == selected["post_snap_loss"]
    assert selected["verification"]["branch_diagnostics"]["status"] == "performed"
    assert result.manifest["semantics_alignment"]["verifier_evidence"]["branch_diagnostics"]["status"] == "performed"
    assert trace_row["gradient_l2_norm"] >= 0.0
    assert trace_row["gradient_max_abs"] >= 0.0
    assert "log_branch_cut_proximity_count" in trace_row
    assert "log_branch_cut_crossing_count" in trace_totals
    assert result.manifest["timing"]["wall_clock_seconds"] >= 0.0
    assert result.verification is not None
    assert result.verification.status == "recovered"


def test_optimizer_uses_generic_ipi_phase_initializer_without_formula_leakage():
    x = np.linspace(-0.5, 0.5, 16)
    target = np.exp(1j * np.pi * x)
    split = DataSplit(
        name="heldout",
        inputs={"x": x},
        target=target,
        target_mpmath=lambda context: np.exp(1j * np.pi * context["x"]),
    )

    result = fit_eml_tree(
        {"x": x},
        target,
        TrainingConfig(
            depth=1,
            variables=("x",),
            steps=1,
            restarts=0,
            lr=0.0,
            seed=0,
            operator_family=ipi_eml_operator(),
            phase_initializers=("ipi_phase_unit",),
        ),
        verification_splits=[split],
    )

    initialization = result.manifest["restarts"][0]["initialization"]
    assert result.verification is not None
    assert result.verification.status == "recovered"
    assert result.manifest["config"]["phase_initializers"] == ["ipi_phase_unit"]
    assert initialization["strategy"] == "generic_ipi_operator_primitive"
    assert initialization["formula_leakage"] is False
    assert initialization["embedding"]["round_trip_equal"] is True


def test_optimizer_empty_loss_summary_keeps_gradient_keys():
    summary = optimize._loss_summary([])

    assert summary["gradient_l2_norm_max"] == 0.0
    assert summary["gradient_max_abs_max"] == 0.0


def test_optimizer_custom_initializer_does_not_add_scaffold_provenance():
    spec = get_demo("exp")
    train = spec.make_splits(points=16)[0]

    def initializer(model, restart, seed):
        model.force_exp("x")
        return {"kind": "custom_initializer", "restart": restart, "seed": seed}

    result = fit_eml_tree(
        train.inputs,
        train.target,
        TrainingConfig(depth=1, variables=("x",), steps=2, restarts=1, seed=0),
        initializer=initializer,
    )
    kinds = [(attempt.get("initialization") or {}).get("kind") for attempt in result.manifest["restarts"]]

    assert kinds == ["custom_initializer"]


def test_optimizer_records_candidate_pool_selection_and_legacy_fallback():
    spec = get_demo("exp")
    splits = spec.make_splits(points=16)
    result = fit_eml_tree(
        splits[0].inputs,
        splits[0].target,
        TrainingConfig(
            depth=1,
            variables=("x",),
            steps=2,
            restarts=1,
            seed=0,
            hardening_steps=2,
            hardening_emit_interval=1,
        ),
        verification_splits=splits,
    )

    selection = result.manifest["selection"]
    selected = result.manifest["selected_candidate"]
    fallback = result.manifest["fallback_candidate"]
    candidates = result.manifest["candidates"]

    assert selection["mode"] == "verifier_gated_exact_candidate_pool"
    assert selection["candidate_count"] == len(candidates)
    assert len(candidates) >= 2
    assert selection["selected_candidate_id"] == selected["candidate_id"]
    assert selection["fallback_candidate_id"] == fallback["candidate_id"]
    assert fallback["source"] == "legacy_final_snap"
    assert any(candidate["source"] == "hardening_checkpoint" for candidate in candidates)
    assert selected["verification"]["status"] == "recovered"
    assert result.verification is not None
    assert result.verification.status == "recovered"


def test_optimizer_scaled_exp_scaffold_recovers_radioactive_decay_with_manifest():
    spec = get_demo("radioactive_decay")
    splits = spec.make_splits(points=12, seed=0)

    result = fit_eml_tree(
        splits[0].inputs,
        splits[0].target,
        TrainingConfig(
            depth=9,
            variables=("t",),
            constants=(-0.4,),
            steps=2,
            restarts=1,
            seed=0,
            scaffold_initializers=("scaled_exp",),
        ),
    )
    report = verify_candidate(result.snap.expression, splits)
    best_restart = result.manifest["best_restart"]
    initialization = best_restart["initialization"]

    assert report.status == "recovered"
    assert best_restart["attempt_kind"] == "scaffold_scaled_exp"
    assert initialization["kind"] == "scaffold_scaled_exp"
    assert initialization["variable"] == "t"
    assert initialization["coefficient"] == "-0.4"
    assert initialization["constant_label"] == "const:-0.4"
    assert initialization["strategy"] == "paper_scaled_exponential_family"
    assert initialization["seed"] == 0
    assert initialization["embedding"]["success"] is True
    assert initialization["embedding"]["snap"]["active_node_count"] == 19


def test_optimizer_scaled_exp_scaffold_recovers_beer_lambert_and_positive_growth():
    cases = (
        ("beer_lambert", "x", -0.8),
        ("scaled_exp_growth", "x", 0.4),
    )

    for formula, variable, coefficient in cases:
        spec = get_demo(formula)
        splits = spec.make_splits(points=12, seed=0)
        result = fit_eml_tree(
            splits[0].inputs,
            splits[0].target,
            TrainingConfig(
                depth=9,
                variables=(variable,),
                constants=(coefficient,),
                steps=2,
                restarts=1,
                seed=0,
                scaffold_initializers=("scaled_exp",),
            ),
        )
        report = verify_candidate(result.snap.expression, splits)

        assert report.status == "recovered"
        assert result.manifest["best_restart"]["attempt_kind"] == "scaffold_scaled_exp"


def test_cleanup_report_verifies_candidate():
    spec = get_demo("log")
    splits = spec.make_splits(points=24)
    report = cleanup_candidate(spec.candidate, splits)
    assert "log" in report.cleaned or "exp" in report.cleaned
    assert report.verification is not None
    assert report.verification.status == "recovered"
