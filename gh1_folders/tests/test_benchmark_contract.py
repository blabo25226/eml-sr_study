import json
from pathlib import Path

import numpy as np
import pytest

from eml_symbolic_regression.benchmark import (
    BenchmarkRepairConfig,
    BenchmarkCase,
    BenchmarkRun,
    BenchmarkSuite,
    BenchmarkValidationError,
    DatasetConfig,
    OptimizerBudget,
    PUBLICATION_BENCHMARK_TARGETS,
    V115_GEML_TARGETS,
    V115_NEGATIVE_CONTROL_TARGETS,
    V115_OSCILLATORY_TARGETS,
    builtin_suite,
    list_builtin_suites,
    load_suite,
    suite_with_semantics_mode,
)
from eml_symbolic_regression.cli import build_parser
from eml_symbolic_regression.datasets import get_demo
from eml_symbolic_regression.proof import paper_claim
from eml_symbolic_regression.semantics import eml_operator_from_spec


EXPECTED_CENTERED_SCAFFOLD_EXCLUSIONS = (
    "exp:centered_family_same_family_witness_missing",
    "log:centered_family_same_family_witness_missing",
    "scaled_exp:centered_family_same_family_witness_missing",
)


def test_scaffold_witness_registry_declares_raw_only_current_witnesses():
    from eml_symbolic_regression import (
        CENTERED_FAMILY_SAME_FAMILY_WITNESS_MISSING,
        ceml_s_operator,
        known_scaffold_kinds,
        list_scaffold_witnesses,
        raw_eml_operator,
        resolve_scaffold_plan,
        scaffold_witness_for,
        zeml_s_operator,
    )

    witnesses = list_scaffold_witnesses()

    assert [witness["kind"] for witness in witnesses] == ["exp", "log", "scaled_exp"]
    assert {witness["operator_family"] for witness in witnesses} == {"raw_eml"}
    assert witnesses == [
        {
            "kind": "exp",
            "operator_family": "raw_eml",
            "attempt_kind": "scaffold_exp",
            "min_depth": 1,
            "strategy": "generic_paper_primitive",
        },
        {
            "kind": "log",
            "operator_family": "raw_eml",
            "attempt_kind": "scaffold_log",
            "min_depth": 3,
            "strategy": "generic_paper_primitive",
        },
        {
            "kind": "scaled_exp",
            "operator_family": "raw_eml",
            "attempt_kind": "scaffold_scaled_exp",
            "min_depth": 9,
            "strategy": "paper_scaled_exponential_family",
        },
    ]
    assert known_scaffold_kinds() == ("exp", "log", "scaled_exp")

    requested = ("exp", "log", "scaled_exp", "exp")
    raw_plan = resolve_scaffold_plan(requested, raw_eml_operator())
    assert raw_plan.as_dict() == {
        "enabled": ["exp", "log", "scaled_exp"],
        "exclusions": [],
    }
    assert scaffold_witness_for("exp", raw_eml_operator()).as_dict() == witnesses[0]

    expected_exclusions = [
        f"exp:{CENTERED_FAMILY_SAME_FAMILY_WITNESS_MISSING}",
        f"log:{CENTERED_FAMILY_SAME_FAMILY_WITNESS_MISSING}",
        f"scaled_exp:{CENTERED_FAMILY_SAME_FAMILY_WITNESS_MISSING}",
    ]
    for operator in (ceml_s_operator(2.0), zeml_s_operator(8.0)):
        centered_plan = resolve_scaffold_plan(requested, operator)
        assert centered_plan.as_dict() == {
            "enabled": [],
            "exclusions": expected_exclusions,
        }
        assert scaffold_witness_for("exp", operator) is None


def test_builtin_suite_registry_expands_stable_run_ids():
    assert {
        "smoke",
        "v1.2-evidence",
        "for-demo-diagnostics",
        "v1.5-shallow-pure-blind",
        "v1.5-shallow-proof",
        "proof-perturbed-basin",
        "proof-perturbed-basin-beer-probes",
        "proof-depth-curve",
        "v1.7-family-smoke",
        "v1.7-family-shallow-pure-blind",
        "v1.7-family-shallow",
        "v1.7-family-basin",
        "v1.7-family-depth-curve",
        "v1.7-family-standard",
        "v1.7-family-showcase",
        "v1.8-family-smoke",
        "v1.8-family-calibration",
        "v1.8-family-shallow-pure-blind",
        "v1.8-family-shallow",
        "v1.8-family-basin",
        "v1.8-family-depth-curve",
        "v1.8-family-standard",
        "v1.8-family-showcase",
        "v1.9-arrhenius-evidence",
        "v1.9-michaelis-evidence",
        "v1.9-repair-evidence",
        "v1.10-logistic-evidence",
        "v1.10-planck-diagnostics",
        "v1.11-paper-training",
        "v1.11-logistic-planck-probes",
        "v1.13-paper-basis-only",
        "v1.13-paper-literal-constants",
        "v1.13-paper-tracks",
        "v1.15-geml-oscillatory-smoke",
        "v1.15-geml-oscillatory",
    } <= set(list_builtin_suites())
    suite = builtin_suite("smoke")
    runs = suite.expanded_runs()

    assert [run.case_id for run in runs] == ["exp-blind", "beer-warm", "planck-diagnostic"]
    assert runs[0].run_id == suite.expanded_runs()[0].run_id
    assert str(runs[0].artifact_path).endswith(f"{runs[0].run_id}.json")
    assert runs[0].claim_id is None
    assert runs[0].threshold_policy_id is None
    assert runs[0].training_mode == "blind_training"
    assert "repair" not in runs[0].as_dict()


def test_arrhenius_evidence_suite_contains_exact_warm_start_case():
    suite = builtin_suite("v1.9-arrhenius-evidence")
    runs = suite.expanded_runs()

    assert suite.id == "v1.9-arrhenius-evidence"
    assert [case.id for case in suite.cases] == ["arrhenius-warm"]
    assert len(runs) == 1

    run = runs[0]
    demo = get_demo("arrhenius")
    provenance = demo.formula_provenance()

    assert run.case_id == "arrhenius-warm"
    assert run.formula == "arrhenius"
    assert provenance["symbolic_expression"] == "exp(-0.8/x)"
    assert run.start_mode == "warm_start"
    assert run.training_mode == "compiler_warm_start_training"
    assert run.seed == 0
    assert run.perturbation_noise == 0.0
    assert run.dataset.points == 24
    assert run.optimizer.warm_steps == 1
    assert run.optimizer.max_warm_depth == 14
    assert run.expect_recovery is True
    assert {"v1.9", "arrhenius", "warm_start", "same_ast"} <= set(run.tags)
    assert demo.train_domain == (0.5, 3.0)
    assert demo.heldout_domain == (0.6, 2.7)
    assert demo.extrap_domain == (3.1, 4.2)
    assert run.run_id == "v1-9-arrhenius-evidence-arrhenius-warm-8dd4270da159"
    assert run.run_id == suite.expanded_runs()[0].run_id


def test_michaelis_evidence_suite_contains_exact_warm_start_case():
    suite = builtin_suite("v1.9-michaelis-evidence")
    runs = suite.expanded_runs()

    assert suite.id == "v1.9-michaelis-evidence"
    assert [case.id for case in suite.cases] == ["michaelis-warm"]
    assert len(runs) == 1

    run = runs[0]
    demo = get_demo("michaelis_menten")
    provenance = demo.formula_provenance()

    assert run.case_id == "michaelis-warm"
    assert run.formula == "michaelis_menten"
    assert provenance["symbolic_expression"] == "2*x/(x + 0.5)"
    assert run.start_mode == "warm_start"
    assert run.training_mode == "compiler_warm_start_training"
    assert run.seed == 0
    assert run.perturbation_noise == 0.0
    assert run.dataset.points == 24
    assert run.optimizer.warm_steps == 1
    assert run.optimizer.max_compile_depth == 13
    assert run.optimizer.max_compile_nodes == 256
    assert run.optimizer.max_warm_depth == 14
    assert run.expect_recovery is True
    assert run.tags == ("v1.9", "michaelis", "warm_start", "same_ast")
    assert "repair" not in run.as_dict()
    assert demo.train_domain == (0.05, 5.0)
    assert demo.heldout_domain == (0.08, 4.5)
    assert demo.extrap_domain == (5.1, 7.0)
    assert run.run_id == "v1-9-michaelis-evidence-michaelis-warm-bd8c78778caf"


def test_logistic_v110_evidence_suite_contains_compile_diagnostic_only():
    suite = builtin_suite("v1.10-logistic-evidence")
    runs = suite.expanded_runs()

    assert suite.id == "v1.10-logistic-evidence"
    assert [case.id for case in suite.cases] == ["logistic-compile"]
    assert len(runs) == 1

    run = runs[0]
    demo = get_demo("logistic")
    provenance = demo.formula_provenance()

    assert run.case_id == "logistic-compile"
    assert run.formula == "logistic"
    assert provenance["symbolic_expression"] == "1/(1 + 2*exp(-1.3*x))"
    assert run.start_mode == "compile"
    assert run.training_mode == "compile_only_verification"
    assert run.seed == 0
    assert run.perturbation_noise == 0.0
    assert run.dataset.points == 24
    assert run.optimizer.max_compile_depth == 13
    assert run.optimizer.max_compile_nodes == 256
    assert run.expect_recovery is False
    assert run.tags == ("v1.10", "logistic", "compile", "diagnostic", "unsupported")
    assert "campaigns" in run.artifact_path.parts
    assert str(run.artifact_path).endswith(f"v1.10-logistic-evidence/{run.run_id}.json")


def test_planck_v110_diagnostics_suite_contains_compile_diagnostic_only():
    suite = builtin_suite("v1.10-planck-diagnostics")
    runs = suite.expanded_runs()

    assert suite.id == "v1.10-planck-diagnostics"
    assert [case.id for case in suite.cases] == ["planck-compile"]
    assert len(runs) == 1

    run = runs[0]
    demo = get_demo("planck")
    provenance = demo.formula_provenance()

    assert run.case_id == "planck-compile"
    assert run.formula == "planck"
    assert provenance["symbolic_expression"] == "x**3/(exp(x) - 1)"
    assert run.start_mode == "compile"
    assert run.training_mode == "compile_only_verification"
    assert run.seed == 0
    assert run.perturbation_noise == 0.0
    assert run.dataset.points == 24
    assert run.optimizer.max_compile_depth == 13
    assert run.optimizer.max_compile_nodes == 256
    assert run.expect_recovery is False
    assert run.tags == ("v1.10", "planck", "compile", "diagnostic", "stretch", "unsupported")
    assert "campaigns" in run.artifact_path.parts
    assert str(run.artifact_path).endswith(f"v1.10-planck-diagnostics/{run.run_id}.json")


def test_v111_paper_training_suite_separates_claim_safe_regimes():
    suite = builtin_suite("v1.11-paper-training")
    runs = suite.expanded_runs()

    assert suite.id == "v1.11-paper-training"
    assert len(runs) == 8
    assert {run.start_mode for run in runs} == {"blind", "warm_start", "perturbed_tree"}
    assert {run.case_id for run in runs} == {
        "exp-pure-blind",
        "exp-scaffolded",
        "shockley-warm",
        "arrhenius-warm",
        "michaelis-warm",
        "basin-depth2-perturbed",
    }
    pure_blind = [run for run in runs if run.case_id == "exp-pure-blind"]
    scaffolded = [run for run in runs if run.case_id == "exp-scaffolded"]
    warm = [run for run in runs if run.start_mode == "warm_start"]
    perturbed = [run for run in runs if run.start_mode == "perturbed_tree"]

    assert len(pure_blind) == 2
    assert all(run.optimizer.scaffold_initializers == () for run in pure_blind)
    assert all(run.training_mode == "blind_training" for run in pure_blind)
    assert len(scaffolded) == 2
    assert all(run.optimizer.scaffold_initializers for run in scaffolded)
    assert all(run.training_mode == "blind_training" for run in scaffolded)
    assert {run.formula for run in warm} == {"shockley", "arrhenius", "michaelis_menten"}
    assert all(run.training_mode == "compiler_warm_start_training" for run in warm)
    assert len(perturbed) == 1
    assert perturbed[0].formula == "basin_depth2_exp_exp"
    assert perturbed[0].perturbation_noise == 0.05
    assert perturbed[0].training_mode == "perturbed_true_tree_training"


def test_v111_logistic_planck_probe_suite_has_compile_and_training_rows():
    suite = builtin_suite("v1.11-logistic-planck-probes")
    runs = suite.expanded_runs()

    assert suite.id == "v1.11-logistic-planck-probes"
    assert len(runs) == 4
    by_case = {run.case_id: run for run in runs}
    assert by_case["logistic-compile"].start_mode == "compile"
    assert by_case["planck-compile"].start_mode == "compile"
    assert by_case["logistic-blind-probe"].start_mode == "blind"
    assert by_case["planck-blind-probe"].start_mode == "blind"
    assert by_case["logistic-blind-probe"].optimizer.scaffold_initializers == ()
    assert by_case["planck-blind-probe"].optimizer.scaffold_initializers == ()
    assert by_case["logistic-blind-probe"].optimizer.constants == (1.0, 2.0, -1.3)
    assert by_case["planck-blind-probe"].optimizer.constants[:2] == (1.0, 3.0)
    assert by_case["planck-blind-probe"].optimizer.constants[2] == pytest.approx(2.718281828459045)
    assert all(run.expect_recovery is False for run in runs)
    assert {"compile", "blind"} == {run.start_mode for run in runs}


def test_v113_publication_track_suites_cover_every_target_with_separate_policies():
    basis = builtin_suite("v1.13-paper-basis-only")
    literal = builtin_suite("v1.13-paper-literal-constants")
    combined = builtin_suite("v1.13-paper-tracks")

    basis_runs = basis.expanded_runs()
    literal_runs = literal.expanded_runs()
    combined_runs = combined.expanded_runs()

    assert tuple(run.formula for run in basis_runs) == PUBLICATION_BENCHMARK_TARGETS
    assert tuple(run.formula for run in literal_runs) == PUBLICATION_BENCHMARK_TARGETS
    assert len(combined_runs) == len(PUBLICATION_BENCHMARK_TARGETS) * 2

    assert {run.track for run in basis_runs} == {"basis_only"}
    assert {run.constants_policy for run in basis_runs} == {"basis_only"}
    assert {run.start_mode for run in basis_runs} == {"compile"}
    assert all(run.optimizer.constants == (1.0,) for run in basis_runs)
    assert all(run.as_dict()["benchmark_track"]["literal_catalog"] == [] for run in basis_runs)

    assert {run.track for run in literal_runs} == {"literal_constants"}
    assert {run.constants_policy for run in literal_runs} == {"literal_constants"}
    assert {run.start_mode for run in literal_runs} == {"warm_start"}
    assert all(run.as_dict()["benchmark_track"]["scaffold_status"] == "disabled" for run in literal_runs)

    by_formula = {run.formula: run for run in literal_runs}
    assert set(by_formula["logistic"].as_dict()["benchmark_track"]["literal_catalog"]) == {"2", "-1.3"}
    assert set(by_formula["michaelis_menten"].as_dict()["benchmark_track"]["literal_catalog"]) == {"0.5", "2"}
    assert set(by_formula["planck"].as_dict()["benchmark_track"]["literal_catalog"]) == {"2.718281828459045", "3"}


def test_v115_oscillatory_targets_have_safe_deterministic_splits():
    for formula in V115_GEML_TARGETS:
        spec = get_demo(formula)
        splits = spec.make_splits(points=12, seed=0)

        assert spec.normalized_dimensionless is True
        assert len(splits) == 3
        for split in splits:
            assert np.all(np.isfinite(np.asarray(split.target, dtype=np.complex128)))
            for values in split.inputs.values():
                assert np.all(np.isfinite(values))
                if formula in {"log", "log_periodic_oscillation"}:
                    assert float(np.min(values)) > 0.0


def test_v115_geml_oscillatory_suite_pairs_raw_and_ipi_budgets():
    suite = builtin_suite("v1.15-geml-oscillatory")
    runs = suite.expanded_runs()

    assert tuple(sorted({run.formula for run in runs})) == tuple(sorted(V115_GEML_TARGETS))
    assert len(runs) == len(V115_GEML_TARGETS) * 2
    assert V115_OSCILLATORY_TARGETS
    assert V115_NEGATIVE_CONTROL_TARGETS

    by_formula: dict[str, list] = {}
    for run in runs:
        by_formula.setdefault(run.formula, []).append(run)
        assert run.start_mode == "blind"
        assert run.optimizer.scaffold_initializers == ()
        assert run.training_mode == "blind_training"
        if run.optimizer.operator_family.specialization == "ipi_eml":
            assert set(run.tags).intersection({"branch_safe_domain", "branch_safe_by_construction", "negative_control_domain"})

    for formula, pair in by_formula.items():
        assert {run.optimizer.operator_family.label for run in pair} == {"raw_eml", "ipi_eml"}
        raw_run = next(run for run in pair if run.optimizer.operator_family.label == "raw_eml")
        ipi_run = next(run for run in pair if run.optimizer.operator_family.label == "ipi_eml")
        raw_budget = raw_run.optimizer.as_dict()
        ipi_budget = ipi_run.optimizer.as_dict()
        raw_budget.pop("operator_family")
        ipi_budget.pop("operator_family")
        assert raw_budget == ipi_budget
        assert raw_run.dataset.as_dict() == ipi_run.dataset.as_dict()


def test_v116_geml_suites_use_generic_ipi_initializers_and_match_raw_budgets():
    assert {"v1.16-geml-smoke", "v1.16-geml-pilot", "v1.16-geml-full"} <= set(list_builtin_suites())
    suite = builtin_suite("v1.16-geml-pilot")
    runs = suite.expanded_runs()

    assert len(runs) == 24
    assert {run.optimizer.operator_family.label for run in runs} == {"raw_eml", "ipi_eml"}
    by_formula_seed: dict[tuple[str, int], list] = {}
    for run in runs:
        by_formula_seed.setdefault((run.formula, run.seed), []).append(run)
        assert run.start_mode == "blind"
        assert run.optimizer.scaffold_initializers == ()
        if run.optimizer.operator_family.specialization == "ipi_eml":
            assert run.optimizer.phase_initializers == ("ipi_phase_unit", "ipi_log_unit")
            assert "branch_safe_search" in run.tags
            assert set(run.tags).intersection({"branch_safe_domain", "branch_safe_by_construction", "negative_control_domain"})
        else:
            assert run.optimizer.phase_initializers == ()

    for pair in by_formula_seed.values():
        assert {run.optimizer.operator_family.label for run in pair} == {"raw_eml", "ipi_eml"}
        raw_run = next(run for run in pair if run.optimizer.operator_family.label == "raw_eml")
        ipi_run = next(run for run in pair if run.optimizer.operator_family.label == "ipi_eml")
        raw_budget = raw_run.optimizer.as_dict()
        ipi_budget = ipi_run.optimizer.as_dict()
        raw_budget.pop("operator_family")
        ipi_budget.pop("operator_family")
        raw_budget.pop("phase_initializers")
        ipi_budget.pop("phase_initializers")
        assert raw_budget == ipi_budget
        assert raw_run.dataset.as_dict() == ipi_run.dataset.as_dict()


def test_v115_ipi_branch_domain_validation_fails_closed():
    bad_case = BenchmarkCase(
        id="bad-ipi-sin",
        formula="sin_pi",
        start_mode="blind",
        optimizer=OptimizerBudget(
            depth=3,
            steps=1,
            restarts=1,
            scaffold_initializers=(),
            operator_family=eml_operator_from_spec("ipi_eml"),
        ),
        tags=("v1.15", "geml_oscillatory"),
    )
    suite = BenchmarkSuite("bad-v115", "bad branch declaration", (bad_case,))

    with pytest.raises(BenchmarkValidationError, match="branch_safe_domain"):
        suite.validate()


def test_phase_initializers_fail_closed_for_raw_operator():
    with pytest.raises(BenchmarkValidationError, match="phase_initializers"):
        OptimizerBudget(phase_initializers=("ipi_phase_unit",)).validate("optimizer")


def test_basis_only_track_rejects_literal_terminal_constants():
    case = BenchmarkCase.from_mapping(
        {
            "id": "bad-basis",
            "formula": "beer_lambert",
            "start_mode": "compile",
            "track": "basis_only",
            "constants_policy": "basis_only",
            "optimizer": {"constants": [1.0, -0.8]},
        },
        path="cases[0]",
    )
    suite = BenchmarkSuite("bad-basis", "bad basis-only constants", (case,))

    with pytest.raises(BenchmarkValidationError) as exc:
        suite.validate()

    assert exc.value.reason == "invalid_track"
    assert exc.value.path == "cases[0].optimizer.constants"


def test_benchmark_case_and_run_serialize_optional_repair_config():
    payload = {
        "id": "repair-radioactive-blind-expanded",
        "formula": "radioactive_decay",
        "start_mode": "blind",
        "seeds": [1],
        "dataset": {"points": 24},
        "optimizer": {"depth": 4, "steps": 80, "restarts": 1},
        "repair": {"preset": "expanded_candidate_pool"},
    }

    case = BenchmarkCase.from_mapping(payload, path="cases[0]")
    default_case = BenchmarkCase.from_mapping({key: value for key, value in payload.items() if key != "repair"}, path="cases[0]")
    suite = BenchmarkSuite("repair-suite", "repair config suite", (case,))
    default_suite = BenchmarkSuite("repair-suite", "repair config suite", (default_case,))
    run = suite.expanded_runs()[0]
    default_run = default_suite.expanded_runs()[0]

    assert case.repair == BenchmarkRepairConfig(preset="expanded_candidate_pool")
    assert case.as_dict()["repair"] == {"preset": "expanded_candidate_pool"}
    assert run.repair == case.repair
    assert run.as_dict()["repair"] == {"preset": "expanded_candidate_pool"}
    assert "repair" not in default_case.as_dict()
    assert "repair" not in default_run.as_dict()
    assert run.optimizer.as_dict() == default_run.optimizer.as_dict()
    assert run.run_id != default_run.run_id


def test_benchmark_run_id_includes_repair_only_when_declared():
    base = BenchmarkRun(
        suite_id="repair-suite",
        case_id="radioactive",
        formula="radioactive_decay",
        start_mode="blind",
        seed=1,
        perturbation_noise=0.0,
        dataset=DatasetConfig(points=24),
        optimizer=OptimizerBudget(depth=4, steps=80, restarts=1),
        artifact_path=Path("unused.json"),
    )
    with_repair = BenchmarkRun(
        suite_id=base.suite_id,
        case_id=base.case_id,
        formula=base.formula,
        start_mode=base.start_mode,
        seed=base.seed,
        perturbation_noise=base.perturbation_noise,
        dataset=base.dataset,
        optimizer=base.optimizer,
        artifact_path=base.artifact_path,
        repair=BenchmarkRepairConfig(preset="expanded_candidate_pool"),
    )

    assert base.run_id != with_repair.run_id
    assert "repair" not in base.as_dict()
    assert with_repair.as_dict()["repair"] == {"preset": "expanded_candidate_pool"}


def test_repair_evidence_suite_contains_default_and_expanded_near_miss_pairs():
    suite = builtin_suite("v1.9-repair-evidence")
    runs = suite.expanded_runs()

    assert suite.id == "v1.9-repair-evidence"
    assert [case.id for case in suite.cases] == [
        "repair-radioactive-blind-default",
        "repair-radioactive-blind-expanded",
        "repair-beer-warm-default",
        "repair-beer-warm-expanded",
    ]
    assert [run.run_id for run in runs] == [run.run_id for run in suite.expanded_runs()]
    assert {run.claim_id for run in runs} == {None}
    assert {run.threshold_policy_id for run in runs} == {None}
    assert {run.expect_recovery for run in runs} == {False}

    by_case = {run.case_id: run for run in runs}
    radioactive_default = by_case["repair-radioactive-blind-default"]
    radioactive_expanded = by_case["repair-radioactive-blind-expanded"]
    beer_default = by_case["repair-beer-warm-default"]
    beer_expanded = by_case["repair-beer-warm-expanded"]

    assert radioactive_default.formula == "radioactive_decay"
    assert radioactive_default.start_mode == "blind"
    assert radioactive_default.training_mode == "blind_training"
    assert radioactive_default.seed == 1
    assert radioactive_default.perturbation_noise == 0.0
    assert radioactive_default.dataset.points == 24
    assert radioactive_default.optimizer.depth == 4
    assert radioactive_default.optimizer.steps == 80
    assert radioactive_default.optimizer.restarts == 1
    assert radioactive_default.repair is None
    assert "repair" not in radioactive_default.as_dict()
    assert {"v1.9", "repair", "near_miss", "default_cleanup"} <= set(radioactive_default.tags)

    assert radioactive_expanded.formula == radioactive_default.formula
    assert radioactive_expanded.start_mode == radioactive_default.start_mode
    assert radioactive_expanded.seed == radioactive_default.seed
    assert radioactive_expanded.optimizer.as_dict() == radioactive_default.optimizer.as_dict()
    assert radioactive_expanded.repair == BenchmarkRepairConfig(preset="expanded_candidate_pool")
    assert radioactive_expanded.as_dict()["repair"] == {"preset": "expanded_candidate_pool"}
    assert {"v1.9", "repair", "near_miss", "expanded_cleanup"} <= set(radioactive_expanded.tags)
    assert radioactive_expanded.run_id != radioactive_default.run_id

    assert beer_default.formula == "beer_lambert"
    assert beer_default.start_mode == "warm_start"
    assert beer_default.training_mode == "compiler_warm_start_training"
    assert beer_default.seed == 1
    assert beer_default.perturbation_noise == 35.0
    assert beer_default.dataset.points == 24
    assert beer_default.optimizer.depth == 2
    assert beer_default.optimizer.warm_steps == 60
    assert beer_default.optimizer.warm_restarts == 1
    assert beer_default.repair is None
    assert "repair" not in beer_default.as_dict()
    assert {"v1.9", "repair", "near_miss", "default_cleanup"} <= set(beer_default.tags)

    assert beer_expanded.formula == beer_default.formula
    assert beer_expanded.start_mode == beer_default.start_mode
    assert beer_expanded.seed == beer_default.seed
    assert beer_expanded.perturbation_noise == beer_default.perturbation_noise
    assert beer_expanded.optimizer.as_dict() == beer_default.optimizer.as_dict()
    assert beer_expanded.repair == BenchmarkRepairConfig(preset="expanded_candidate_pool")
    assert beer_expanded.as_dict()["repair"] == {"preset": "expanded_candidate_pool"}
    assert {"v1.9", "repair", "near_miss", "expanded_cleanup"} <= set(beer_expanded.tags)
    assert beer_expanded.run_id != beer_default.run_id


def test_family_matrix_suites_clone_regimes_with_operator_variants():
    suite = load_suite("v1.7-family-shallow-pure-blind")
    runs = suite.expanded_runs()

    assert len(runs) == 72
    assert {run.claim_id for run in runs} == {None}
    assert {run.threshold_policy_id for run in runs} == {None}
    assert {"shallow-exp-pure-blind-raw", "shallow-exp-pure-blind-ceml2", "shallow-exp-pure-blind-zeml8-4"} <= {
        run.case_id for run in runs
    }
    assert {"raw_eml", "CEML_2", "ZEML_2", "ZEML_8"} <= {
        run.optimizer.operator_family.label for run in runs
    }
    assert any([operator.label for operator in run.optimizer.operator_schedule] == ["ZEML_8", "ZEML_4"] for run in runs)
    assert all({"v1.7", "family_matrix"} <= set(run.tags) for run in runs)

    shallow = load_suite("v1.7-family-shallow")
    centered_scaffolded = [
        run for run in shallow.expanded_runs() if run.case_id == "shallow-beer-lambert-blind-ceml2"
    ]
    raw_scaffolded = [run for run in shallow.expanded_runs() if run.case_id == "shallow-beer-lambert-blind-raw"]
    assert centered_scaffolded
    assert raw_scaffolded
    assert raw_scaffolded[0].optimizer.scaffold_initializers == ("exp", "log", "scaled_exp")
    assert raw_scaffolded[0].optimizer.scaffold_exclusions == ()
    assert centered_scaffolded[0].optimizer.operator_family.label == "CEML_2"
    assert centered_scaffolded[0].optimizer.scaffold_initializers == ()
    assert centered_scaffolded[0].optimizer.scaffold_exclusions == EXPECTED_CENTERED_SCAFFOLD_EXCLUSIONS


def test_v18_family_matrix_expands_scales_and_schedules():
    suite = load_suite("v1.8-family-calibration")
    runs = suite.expanded_runs()

    assert len(runs) == 22
    assert {"cal-exp-blind-ceml1", "cal-log-blind-zeml8-4-2-1"} <= {run.case_id for run in runs}
    assert {"raw_eml", "CEML_1", "CEML_2", "CEML_4", "CEML_8", "ZEML_1", "ZEML_2", "ZEML_4", "ZEML_8"} <= {
        run.optimizer.operator_family.label for run in runs
    }
    assert any(
        [operator.label for operator in run.optimizer.operator_schedule] == ["ZEML_8", "ZEML_4", "ZEML_2", "ZEML_1"]
        for run in runs
    )
    v18_probe = next(run for run in runs if run.case_id == "cal-exp-blind-ceml1")
    assert "v1.8" in v18_probe.tags
    assert "v1.7" not in v18_probe.tags
    raw_probe = next(run for run in runs if run.case_id == "cal-log-blind-raw")
    continuation_probe = next(run for run in runs if run.case_id == "cal-log-blind-zeml8-4-2-1")
    assert raw_probe.optimizer.scaffold_initializers == ("exp", "log", "scaled_exp")
    assert raw_probe.optimizer.scaffold_exclusions == ()
    assert [operator.label for operator in continuation_probe.optimizer.operator_schedule] == [
        "ZEML_8",
        "ZEML_4",
        "ZEML_2",
        "ZEML_1",
    ]
    assert continuation_probe.optimizer.operator_family.label == "ZEML_8"
    assert continuation_probe.optimizer.scaffold_initializers == ()
    assert continuation_probe.optimizer.scaffold_exclusions == EXPECTED_CENTERED_SCAFFOLD_EXCLUSIONS


def test_family_basin_and_depth_curve_preserve_regime_shapes_without_thresholds():
    basin_runs = load_suite("v1.7-family-basin").expanded_runs()
    depth_runs = load_suite("v1.7-family-depth-curve").expanded_runs()

    assert len(basin_runs) == 36
    assert len(depth_runs) == 80
    assert {"perturbed_tree"} == {run.start_mode for run in basin_runs}
    assert {"blind", "perturbed_tree"} == {run.start_mode for run in depth_runs}
    assert {run.claim_id for run in basin_runs + depth_runs} == {None}
    assert any(run.case_id == "basin-depth1-perturbed-ceml2" for run in basin_runs)
    assert any(run.case_id == "depth-6-perturbed-zeml8-4" for run in depth_runs)


def test_v12_evidence_suite_contains_perturbation_matrix():
    suite = load_suite("v1.2-evidence")
    runs = suite.expanded_runs()
    beer_runs = [run for run in runs if run.case_id == "beer-perturbation-sweep"]

    assert len(beer_runs) == 9
    assert {run.perturbation_noise for run in beer_runs} == {0.0, 5.0, 35.0}
    assert {run.seed for run in beer_runs} == {0, 1, 2}
    blind_formulas = {run.formula for run in runs if run.start_mode == "blind"}
    assert {"exp", "log", "radioactive_decay"} <= blind_formulas
    assert any(run.case_id == "michaelis-warm-diagnostic" and run.start_mode == "warm_start" for run in runs)
    assert any(run.formula == "planck" and "stretch" in run.tags for run in runs)


def test_for_demo_diagnostics_cover_selected_showcase_formulas():
    suite = load_suite("for-demo-diagnostics")
    formulas = {run.formula for run in suite.expanded_runs()}

    assert {
        "beer_lambert",
        "radioactive_decay",
        "michaelis_menten",
        "logistic",
        "shockley",
        "damped_oscillator",
        "planck",
    } <= formulas


def test_unknown_formula_fails_closed():
    suite = BenchmarkSuite.from_mapping(
        {
            "schema": "eml.benchmark_suite.v1",
            "id": "bad",
            "cases": [{"id": "bad-case", "formula": "nope", "start_mode": "blind"}],
        }
    )

    with pytest.raises(BenchmarkValidationError) as exc:
        suite.validate()

    assert exc.value.reason == "unknown_formula"
    assert exc.value.path == "cases[0].formula"


@pytest.mark.parametrize("start_mode", ["catalog", "compile", "blind"])
def test_non_perturbable_start_modes_reject_perturbation_noise(start_mode):
    suite = BenchmarkSuite.from_mapping(
        {
            "schema": "eml.benchmark_suite.v1",
            "id": "bad",
            "cases": [
                {
                    "id": "bad-case",
                    "formula": "exp",
                    "start_mode": start_mode,
                    "perturbation_noise": [1.0],
                }
            ],
        }
    )

    with pytest.raises(BenchmarkValidationError) as exc:
        suite.validate()

    assert exc.value.reason == "invalid_perturbation"


def test_perturbed_tree_defaults_to_perturbed_true_tree_training_and_keeps_noise_grid():
    case = BenchmarkCase.from_mapping(
        {
            "id": "basin-depth1-perturbed",
            "formula": "basin_depth1_exp",
            "start_mode": "perturbed_tree",
            "perturbation_noise": [0.05, 0.25],
        },
        path="cases[0]",
    )
    suite = BenchmarkSuite("proof-perturbed-basin", "perturbed tree contract", (case,))

    runs = suite.expanded_runs()

    assert {run.start_mode for run in runs} == {"perturbed_tree"}
    assert {run.training_mode for run in runs} == {"perturbed_true_tree_training"}
    assert [run.perturbation_noise for run in runs] == [0.05, 0.25]


def test_custom_suite_loads_from_json(tmp_path):
    path = tmp_path / "suite.json"
    path.write_text(
        json.dumps(
            {
                "schema": "eml.benchmark_suite.v1",
                "id": "custom",
                "artifact_root": str(tmp_path / "artifacts"),
                "cases": [{"id": "compile-exp", "formula": "exp", "start_mode": "compile", "dataset": {"points": 12}}],
            }
        ),
        encoding="utf-8",
    )

    suite = load_suite(path)
    runs = suite.expanded_runs()

    assert suite.id == "custom"
    assert len(runs) == 1
    assert runs[0].dataset.points == 12
    assert runs[0].claim_id is None
    assert runs[0].threshold_policy_id is None
    assert runs[0].training_mode == "compile_only_verification"
    assert str(runs[0].artifact_path).startswith(str(tmp_path / "artifacts"))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("seeds", "10"),
        ("perturbation_noise", "0.0"),
        ("tags", "smoke"),
    ],
)
def test_custom_suite_rejects_string_sequence_fields(tmp_path, field, value):
    path = tmp_path / "suite.json"
    path.write_text(
        json.dumps(
            {
                "schema": "eml.benchmark_suite.v1",
                "id": "custom",
                "cases": [{"id": "compile-exp", "formula": "exp", "start_mode": "compile", field: value}],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(BenchmarkValidationError) as exc:
        load_suite(path)

    assert exc.value.reason == "malformed_case"
    assert exc.value.path == f"cases[0].{field}"


def test_case_accepts_and_serializes_proof_metadata():
    case = BenchmarkCase.from_mapping(
        {
            "id": "shallow-exp-blind",
            "formula": "exp",
            "start_mode": "blind",
            "claim_id": "paper-shallow-scaffolded-recovery",
            "threshold_policy_id": "scaffolded_bounded_100_percent",
            "training_mode": "blind_training",
        },
        path="cases[0]",
    )
    suite = BenchmarkSuite("v1.5-shallow-proof", "proof metadata custom suite", (case,))
    suite.validate()
    runs = suite.expanded_runs()

    assert case.as_dict()["claim_id"] == "paper-shallow-scaffolded-recovery"
    assert runs[0].claim_id == "paper-shallow-scaffolded-recovery"
    assert runs[0].threshold_policy_id == "scaffolded_bounded_100_percent"
    assert runs[0].training_mode == "blind_training"
    assert runs[0].as_dict()["threshold_policy_id"] == "scaffolded_bounded_100_percent"
    assert runs[0].run_id != type(runs[0])(
        suite_id=runs[0].suite_id,
        case_id=runs[0].case_id,
        formula=runs[0].formula,
        start_mode=runs[0].start_mode,
        seed=runs[0].seed,
        perturbation_noise=runs[0].perturbation_noise,
        dataset=runs[0].dataset,
        optimizer=runs[0].optimizer,
        artifact_path=runs[0].artifact_path,
        tags=runs[0].tags,
        expect_recovery=runs[0].expect_recovery,
        claim_id="paper-perturbed-true-tree-basin",
        threshold_policy_id="bounded_100_percent",
        training_mode="blind_training",
    ).run_id


def test_optimizer_budget_parses_and_serializes_constants():
    budget = OptimizerBudget.from_mapping(
        {"depth": 9, "constants": ["-0.8", {"real": "0.4", "imag": "0"}], "scaffold_initializers": ["scaled_exp"]}
    )

    assert budget.constants == (complex(-0.8), complex(0.4))
    assert budget.scaffold_initializers == ("scaled_exp",)
    assert budget.as_dict()["constants"] == ["-0.8", "0.4"]
    assert budget.as_dict()["scaffold_initializers"] == ["scaled_exp"]

    with pytest.raises(BenchmarkValidationError) as exc:
        OptimizerBudget.from_mapping({"constants": ["nan"]}).validate("optimizer")

    assert exc.value.reason == "invalid_budget"
    assert exc.value.path == "optimizer.constants[0]"

    with pytest.raises(BenchmarkValidationError) as exc:
        OptimizerBudget.from_mapping({"scaffold_initializers": "scaled_exp"}).validate("optimizer")

    assert exc.value.reason == "malformed_budget"
    assert exc.value.path == "optimizer.scaffold_initializers"

    with pytest.raises(BenchmarkValidationError) as exc:
        OptimizerBudget.from_mapping({"scaffold_initializers": ["bad"]}).validate("optimizer")

    assert exc.value.reason == "invalid_budget"
    assert exc.value.path == "optimizer.scaffold_initializers"


def test_optimizer_budget_parses_and_serializes_semantics_mode():
    budget = OptimizerBudget.from_mapping({"semantics_mode": "faithful"})

    budget.validate("optimizer")
    assert budget.semantics_mode == "faithful"
    assert budget.as_dict()["semantics_mode"] == "faithful"

    with pytest.raises(BenchmarkValidationError) as exc:
        OptimizerBudget.from_mapping({"semantics_mode": "almost-faithful"}).validate("optimizer")

    assert exc.value.reason == "invalid_budget"
    assert exc.value.path == "optimizer.semantics_mode"


def test_optimizer_budget_parses_operator_family_and_schedule():
    budget = OptimizerBudget.from_mapping(
        {
            "operator_family": {"family": "ceml_s", "s": 2},
            "operator_schedule": ["zeml_s:8", "zeml_s:4"],
        }
    )

    assert budget.operator_family.label == "CEML_2"
    assert [operator.label for operator in budget.operator_schedule] == ["ZEML_8", "ZEML_4"]
    assert budget.as_dict()["operator_family"]["label"] == "CEML_2"
    assert [item["label"] for item in budget.as_dict()["operator_schedule"]] == ["ZEML_8", "ZEML_4"]

    with pytest.raises(BenchmarkValidationError) as exc:
        OptimizerBudget.from_mapping({"operator_schedule": "zeml_s:8"}).validate("optimizer")

    assert exc.value.reason == "malformed_budget"
    assert exc.value.path == "optimizer.operator_schedule"

    with pytest.raises(BenchmarkValidationError) as exc:
        OptimizerBudget.from_mapping({"operator_family": "not-a-family"}).validate("optimizer")

    assert exc.value.reason == "invalid_budget"
    assert exc.value.path == "optimizer.operator_family"

    with pytest.raises(BenchmarkValidationError) as exc:
        OptimizerBudget.from_mapping({"operator_schedule": ["raw_eml"]}).validate("optimizer")

    assert exc.value.reason == "invalid_budget"
    assert exc.value.path == "optimizer.operator_schedule[0]"


def test_suite_with_semantics_mode_overrides_every_case_without_mutating_source():
    suite = builtin_suite("smoke")
    overridden = suite_with_semantics_mode(suite, "faithful")

    assert {case.optimizer.semantics_mode for case in suite.cases} == {"guarded"}
    assert {case.optimizer.semantics_mode for case in overridden.cases} == {"faithful"}
    assert overridden.id == suite.id


def test_cli_parses_semantics_mode_for_demo_and_benchmark():
    parser = build_parser()

    demo_args = parser.parse_args(["demo", "exp", "--train-eml", "--semantics-mode", "faithful"])
    benchmark_args = parser.parse_args(["benchmark", "smoke", "--semantics-mode", "faithful"])

    assert demo_args.semantics_mode == "faithful"
    assert benchmark_args.semantics_mode == "faithful"


def test_operator_family_participates_in_benchmark_run_id():
    raw_case = BenchmarkCase.from_mapping(
        {"id": "exp-blind", "formula": "exp", "start_mode": "blind", "optimizer": {"depth": 1}},
        path="cases[0]",
    )
    centered_case = BenchmarkCase.from_mapping(
        {
            "id": "exp-blind",
            "formula": "exp",
            "start_mode": "blind",
            "optimizer": {"depth": 1, "operator_family": {"family": "ceml_s", "s": 2}},
        },
        path="cases[0]",
    )
    raw_run = BenchmarkSuite("custom", "raw", (raw_case,)).expanded_runs()[0]
    centered_run = BenchmarkSuite("custom", "centered", (centered_case,)).expanded_runs()[0]

    assert raw_run.run_id != centered_run.run_id


@pytest.mark.parametrize(
    ("suite_id", "case_id", "path_suffix"),
    [
        ("proof-custom", "shallow-exp-blind", "claim_id"),
        ("v1.5-shallow-proof", "proof-exp", "id"),
    ],
)
def test_proof_contract_validation_enforces_claim_suite_and_case_scope(suite_id, case_id, path_suffix):
    case = BenchmarkCase.from_mapping(
        {
            "id": case_id,
            "formula": "exp",
            "start_mode": "blind",
            "claim_id": "paper-shallow-scaffolded-recovery",
            "threshold_policy_id": "scaffolded_bounded_100_percent",
            "training_mode": "blind_training",
        },
        path="cases[0]",
    )
    suite = BenchmarkSuite(suite_id, "bad proof metadata scope", (case,))

    with pytest.raises(BenchmarkValidationError) as exc:
        suite.validate()

    assert exc.value.reason == "invalid_proof_contract"
    assert exc.value.path == f"cases[0].{path_suffix}"


@pytest.mark.parametrize(
    ("override", "path_suffix"),
    [
        ({"threshold_policy_id": "missing-policy"}, "threshold_policy_id"),
        ({"claim_id": "missing-claim", "threshold_policy_id": "measured_pure_blind_recovery", "training_mode": "blind_training"}, "claim_id"),
        ({"claim_id": "paper-shallow-blind-recovery", "training_mode": "blind_training"}, "threshold_policy_id"),
        ({"claim_id": "paper-shallow-blind-recovery", "threshold_policy_id": "missing-policy", "training_mode": "blind_training"}, "threshold_policy_id"),
        ({"claim_id": "paper-shallow-blind-recovery", "threshold_policy_id": "measured_pure_blind_recovery", "training_mode": "catalog_verification"}, "training_mode"),
        (
            {
                "claim_id": "paper-shallow-blind-recovery",
                "threshold_policy_id": "measured_pure_blind_recovery",
                "training_mode": "perturbed_true_tree_training",
            },
            "training_mode",
        ),
        (
            {
                "claim_id": "paper-shallow-blind-recovery",
                "threshold_policy_id": "measured_pure_blind_recovery",
                "training_mode": "blind_training",
            },
            "optimizer.scaffold_initializers",
        ),
    ],
)
def test_proof_contract_validation_fails_closed(override, path_suffix):
    payload = {
        "id": "bad-proof-case",
        "formula": "exp",
        "start_mode": "blind",
        **override,
    }
    suite = BenchmarkSuite.from_mapping({"id": "bad-proof-suite", "cases": [payload]})

    with pytest.raises(BenchmarkValidationError) as exc:
        suite.validate()

    assert exc.value.reason == "invalid_proof_contract"
    assert exc.value.path == f"cases[0].{path_suffix}"


def test_shallow_blind_claim_declares_signed_scaled_case_inventory():
    claim = paper_claim("paper-shallow-blind-recovery")

    assert claim.case_ids == (
        "shallow-exp-pure-blind",
        "shallow-log-pure-blind",
        "shallow-radioactive-decay-pure-blind",
        "shallow-beer-lambert-pure-blind",
        "shallow-scaled-exp-growth-pure-blind",
        "shallow-scaled-exp-fast-decay-pure-blind",
    )


def test_shallow_scaffolded_claim_declares_signed_scaled_case_inventory():
    claim = paper_claim("paper-shallow-scaffolded-recovery")

    assert claim.case_ids == (
        "shallow-exp-blind",
        "shallow-log-blind",
        "shallow-radioactive-decay-blind",
        "shallow-beer-lambert-blind",
        "shallow-scaled-exp-growth-blind",
        "shallow-scaled-exp-fast-decay-blind",
    )


def test_v15_shallow_proof_suite_expands_fixed_proof_contract_runs():
    suite = load_suite("v1.5-shallow-proof")
    runs = suite.expanded_runs()
    cases_by_id = {case.id: case for case in suite.cases}

    assert [case.id for case in suite.cases] == [
        "shallow-exp-blind",
        "shallow-log-blind",
        "shallow-radioactive-decay-blind",
        "shallow-beer-lambert-blind",
        "shallow-scaled-exp-growth-blind",
        "shallow-scaled-exp-fast-decay-blind",
    ]
    assert len(runs) == 18
    assert {run.seed for run in runs} == {0, 1, 2}
    assert {run.claim_id for run in runs} == {"paper-shallow-scaffolded-recovery"}
    assert {run.threshold_policy_id for run in runs} == {"scaffolded_bounded_100_percent"}
    assert {run.training_mode for run in runs} == {"blind_training"}
    assert {run.start_mode for run in runs} == {"blind"}
    assert all({"v1.5", "proof", "bounded", "scaffolded_blind"} <= set(run.tags) for run in runs)
    assert all(run.optimizer.steps > 0 and run.optimizer.restarts > 0 for run in runs)
    assert all(run.optimizer.as_dict()["constants"] for run in runs)
    assert all(run.optimizer.scaffold_initializers for run in runs)
    assert all(run.threshold_policy_id == paper_claim(run.claim_id).threshold_policy_id for run in runs)
    assert cases_by_id["shallow-exp-blind"].optimizer.depth == 1
    assert cases_by_id["shallow-log-blind"].optimizer.depth == 3

    coefficient_cases = {
        "shallow-radioactive-decay-blind": -0.4,
        "shallow-beer-lambert-blind": -0.8,
        "shallow-scaled-exp-growth-blind": 0.4,
        "shallow-scaled-exp-fast-decay-blind": -1.2,
    }
    for case_id, coefficient in coefficient_cases.items():
        case = cases_by_id[case_id]
        assert case.optimizer.depth == 9
        assert case.optimizer.constants == (complex(coefficient),)
        assert case.optimizer.as_dict()["constants"] == [repr(float(coefficient))]


def test_v15_shallow_pure_blind_suite_expands_measured_random_only_runs():
    suite = load_suite("v1.5-shallow-pure-blind")
    runs = suite.expanded_runs()
    cases_by_id = {case.id: case for case in suite.cases}

    assert [case.id for case in suite.cases] == [
        "shallow-exp-pure-blind",
        "shallow-log-pure-blind",
        "shallow-radioactive-decay-pure-blind",
        "shallow-beer-lambert-pure-blind",
        "shallow-scaled-exp-growth-pure-blind",
        "shallow-scaled-exp-fast-decay-pure-blind",
    ]
    assert len(runs) == 18
    assert {run.seed for run in runs} == {0, 1, 2}
    assert {run.claim_id for run in runs} == {"paper-shallow-blind-recovery"}
    assert {run.threshold_policy_id for run in runs} == {"measured_pure_blind_recovery"}
    assert {run.training_mode for run in runs} == {"blind_training"}
    assert {run.start_mode for run in runs} == {"blind"}
    assert all({"v1.5", "proof", "measured", "pure_blind"} <= set(run.tags) for run in runs)
    assert all(run.optimizer.scaffold_initializers == () for run in runs)
    assert all(run.threshold_policy_id == paper_claim(run.claim_id).threshold_policy_id for run in runs)
    assert cases_by_id["shallow-exp-pure-blind"].optimizer.depth == 1
    assert cases_by_id["shallow-log-pure-blind"].optimizer.depth == 3

    coefficient_cases = {
        "shallow-radioactive-decay-pure-blind": -0.4,
        "shallow-beer-lambert-pure-blind": -0.8,
        "shallow-scaled-exp-growth-pure-blind": 0.4,
        "shallow-scaled-exp-fast-decay-pure-blind": -1.2,
    }
    for case_id, coefficient in coefficient_cases.items():
        case = cases_by_id[case_id]
        assert case.optimizer.depth == 9
        assert case.optimizer.constants == (complex(coefficient),)
        assert case.optimizer.as_dict()["constants"] == [repr(float(coefficient))]


def test_proof_perturbed_basin_suite_expands_bounded_nonzero_runs():
    suite = load_suite("proof-perturbed-basin")
    runs = suite.expanded_runs()
    cases_by_id = {case.id: case for case in suite.cases}

    assert [case.id for case in suite.cases] == [
        "basin-depth1-perturbed",
        "basin-depth2-perturbed",
        "basin-depth3-perturbed",
        "basin-beer-lambert-bound",
    ]
    assert len(runs) == 9
    assert {run.start_mode for run in runs} == {"perturbed_tree"}
    assert {run.training_mode for run in runs} == {"perturbed_true_tree_training"}
    assert {run.claim_id for run in runs} == {"paper-perturbed-true-tree-basin"}
    assert {run.threshold_policy_id for run in runs} == {"bounded_100_percent"}
    assert all(run.perturbation_noise > 0.0 for run in runs)
    assert all({"v1.5", "proof", "bounded", "perturbed_tree"} <= set(run.tags) for run in runs)
    assert all(run.threshold_policy_id == paper_claim(run.claim_id).threshold_policy_id for run in runs)
    assert cases_by_id["basin-depth1-perturbed"].optimizer.depth == 1
    assert cases_by_id["basin-depth1-perturbed"].optimizer.warm_steps == 12
    assert cases_by_id["basin-depth2-perturbed"].optimizer.depth == 2
    assert cases_by_id["basin-depth2-perturbed"].optimizer.warm_steps == 16
    assert cases_by_id["basin-depth3-perturbed"].optimizer.depth == 3
    assert cases_by_id["basin-depth3-perturbed"].optimizer.warm_steps == 20
    assert cases_by_id["basin-beer-lambert-bound"].optimizer.warm_steps == 40
    assert cases_by_id["basin-beer-lambert-bound"].optimizer.warm_restarts == 1
    assert cases_by_id["basin-beer-lambert-bound"].optimizer.max_warm_depth == 10


def test_perturbed_basin_probe_suite_keeps_high_noise_outside_thresholds():
    suite = load_suite("proof-perturbed-basin-beer-probes")
    runs = suite.expanded_runs()

    assert [case.id for case in suite.cases] == ["basin-beer-lambert-bound-probes"]
    assert len(runs) == 4
    assert {run.formula for run in runs} == {"beer_lambert"}
    assert {run.start_mode for run in runs} == {"perturbed_tree"}
    assert {run.training_mode for run in runs} == {"perturbed_true_tree_training"}
    assert {run.perturbation_noise for run in runs} == {15.0, 35.0}
    assert {run.seed for run in runs} == {0, 1}
    assert {run.claim_id for run in runs} == {None}
    assert {run.threshold_policy_id for run in runs} == {None}
    assert all({"bound_probe", "beer_lambert", "high_noise"} <= set(run.tags) for run in runs)


def test_proof_depth_curve_suite_expands_blind_and_perturbed_rows():
    suite = load_suite("proof-depth-curve")
    runs = suite.expanded_runs()
    cases_by_id = {case.id: case for case in suite.cases}

    assert [case.id for case in suite.cases] == [
        "depth-2-blind",
        "depth-3-blind",
        "depth-4-blind",
        "depth-5-blind",
        "depth-6-blind",
        "depth-2-perturbed",
        "depth-3-perturbed",
        "depth-4-perturbed",
        "depth-5-perturbed",
        "depth-6-perturbed",
    ]
    assert len(runs) == 20
    assert {run.seed for run in runs} == {0, 1}
    assert {run.claim_id for run in runs} == {"paper-blind-depth-degradation"}
    assert {run.threshold_policy_id for run in runs} == {"measured_depth_curve"}
    assert {run.start_mode for run in runs} == {"blind", "perturbed_tree"}
    assert {run.training_mode for run in runs} == {"blind_training", "perturbed_true_tree_training"}
    assert all({"v1.5", "proof", "measured", "depth_curve"} <= set(run.tags) for run in runs)
    assert all(run.threshold_policy_id == paper_claim(run.claim_id).threshold_policy_id for run in runs)
    assert {cases_by_id[f"depth-{depth}-blind"].optimizer.depth for depth in range(2, 7)} == {2, 3, 4, 5, 6}
    assert {cases_by_id[f"depth-{depth}-perturbed"].optimizer.depth for depth in range(2, 7)} == {2, 3, 4, 5, 6}
    assert all(run.perturbation_noise == 0.0 for run in runs if run.start_mode == "blind")
    assert all(run.perturbation_noise > 0.0 for run in runs if run.start_mode == "perturbed_tree")
    assert cases_by_id["depth-2-perturbed"].optimizer.warm_steps == 20
    assert cases_by_id["depth-6-perturbed"].optimizer.warm_steps == 30


def test_cli_start_mode_filter_accepts_perturbed_tree():
    args = build_parser().parse_args(["benchmark", "proof-perturbed-basin", "--start-mode", "perturbed_tree"])

    assert args.start_mode == ["perturbed_tree"]


@pytest.mark.parametrize(
    ("override", "path_suffix"),
    [
        ({"start_mode": "warm_start", "training_mode": "compiler_warm_start_training"}, "start_mode"),
        ({"start_mode": "blind", "training_mode": "blind_training"}, "start_mode"),
        ({"start_mode": "compile", "training_mode": "compile_only_verification"}, "start_mode"),
        ({"perturbation_noise": [0.0]}, "perturbation_noise"),
        ({"training_mode": None}, "training_mode"),
        ({"threshold_policy_id": "measured_depth_curve"}, "threshold_policy_id"),
    ],
)
def test_perturbed_basin_proof_cases_reject_invalid_metadata(override, path_suffix):
    payload = {
        "id": "basin-depth1-perturbed",
        "formula": "basin_depth1_exp",
        "start_mode": "perturbed_tree",
        "perturbation_noise": [0.05],
        "claim_id": "paper-perturbed-true-tree-basin",
        "threshold_policy_id": "bounded_100_percent",
        "training_mode": "perturbed_true_tree_training",
        **{key: value for key, value in override.items() if value is not None},
    }
    if "training_mode" in override and override["training_mode"] is None:
        payload.pop("training_mode")
    suite = BenchmarkSuite.from_mapping({"id": "proof-perturbed-basin", "cases": [payload]})

    with pytest.raises(BenchmarkValidationError) as exc:
        suite.validate()

    assert exc.value.reason == "invalid_proof_contract"
    assert exc.value.path == f"cases[0].{path_suffix}"


def test_perturbed_basin_proof_cases_reject_caller_supplied_evidence_class():
    with pytest.raises(BenchmarkValidationError) as exc:
        BenchmarkCase.from_mapping(
            {
                "id": "basin-depth1-perturbed",
                "formula": "basin_depth1_exp",
                "start_mode": "perturbed_tree",
                "perturbation_noise": [0.05],
                "claim_id": "paper-perturbed-true-tree-basin",
                "threshold_policy_id": "bounded_100_percent",
                "training_mode": "perturbed_true_tree_training",
                "evidence_class": "perturbed_true_tree_recovered",
            },
            path="cases[0]",
        )

    assert exc.value.reason == "invalid_proof_contract"
    assert exc.value.path == "cases[0].evidence_class"


@pytest.mark.parametrize(
    ("override", "reason", "path_suffix"),
    [
        ({"start_mode": "compile", "training_mode": "compile_only_verification"}, "invalid_perturbation", "perturbation_noise"),
        ({"start_mode": "warm_start", "training_mode": "compiler_warm_start_training"}, "invalid_proof_contract", "start_mode"),
        ({"threshold_policy_id": "bounded_100_percent"}, "invalid_proof_contract", "threshold_policy_id"),
        ({"training_mode": None}, "invalid_proof_contract", "training_mode"),
        ({"perturbation_noise": [0.0]}, "invalid_proof_contract", "perturbation_noise"),
    ],
)
def test_depth_curve_perturbed_rows_reject_invalid_metadata(override, reason, path_suffix):
    payload = {
        "id": "depth-4-perturbed",
        "formula": "depth_curve_depth4",
        "start_mode": "perturbed_tree",
        "perturbation_noise": [0.05],
        "claim_id": "paper-blind-depth-degradation",
        "threshold_policy_id": "measured_depth_curve",
        "training_mode": "perturbed_true_tree_training",
        **{key: value for key, value in override.items() if value is not None},
    }
    if "training_mode" in override and override["training_mode"] is None:
        payload.pop("training_mode")
    suite = BenchmarkSuite.from_mapping({"id": "proof-depth-curve", "cases": [payload]})

    with pytest.raises(BenchmarkValidationError) as exc:
        suite.validate()

    assert exc.value.reason == reason
    assert exc.value.path == f"cases[0].{path_suffix}"


@pytest.mark.parametrize(
    "override",
    [
        {"start_mode": "catalog", "training_mode": "catalog_verification"},
        {"start_mode": "compile", "training_mode": "compile_only_verification"},
        {"start_mode": "warm_start", "training_mode": "compiler_warm_start_training"},
        {"threshold_policy_id": "measured_depth_curve"},
        {"threshold_policy_id": "bounded_100_percent"},
    ],
)
def test_shallow_scaffolded_proof_suite_rejects_non_blind_or_wrong_threshold_metadata(override):
    payload = {
        "id": "shallow-exp-blind",
        "formula": "exp",
        "start_mode": "blind",
        "claim_id": "paper-shallow-scaffolded-recovery",
        "threshold_policy_id": "scaffolded_bounded_100_percent",
        "training_mode": "blind_training",
        **override,
    }
    suite = BenchmarkSuite.from_mapping({"id": "v1.5-shallow-proof", "cases": [payload]})

    with pytest.raises(BenchmarkValidationError) as exc:
        suite.validate()

    assert exc.value.reason == "invalid_proof_contract"
