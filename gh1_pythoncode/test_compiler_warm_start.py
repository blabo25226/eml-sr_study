import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
import sympy as sp

from eml_symbolic_regression.compiler import (
    CompilerConfig,
    CompileReason,
    UnsupportedExpression,
    compile_and_validate,
    compile_sympy_expression,
    diagnose_compile_expression,
    multiply_expr,
)
from eml_symbolic_regression.datasets import get_demo
from eml_symbolic_regression.expression import Const, Var, exp_of, log_of
from eml_symbolic_regression.master_tree import EmbeddingConfig, EmbeddingError, SoftEMLTree
from eml_symbolic_regression.motif_search import validate_motif_candidate
from eml_symbolic_regression.optimize import TrainingConfig
from eml_symbolic_regression.warm_start import PerturbationConfig, fit_warm_started_eml_tree
from eml_symbolic_regression.warm_start import perturb_tree_logits


ROOT = Path(__file__).resolve().parents[1]
CLI_ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src")}


def test_compile_exp_log_and_beer_lambert_validate_against_sympy():
    x = sp.Symbol("x")
    inputs = {"x": np.linspace(0.25, 2.5, 12).astype(np.complex128)}
    config = CompilerConfig(variables=("x",), max_depth=12, max_nodes=128)

    for expr in (sp.exp(x), sp.log(x), sp.exp(sp.Float("-0.8") * x)):
        result = compile_and_validate(expr, config, inputs)
        assert result.validation is not None
        assert result.validation.passed
        assert result.metadata.unsupported_reason is None


def test_compile_shockley_uses_lower_depth_template():
    spec = get_demo("shockley")
    splits = spec.make_splits(points=24, seed=0)
    result = compile_and_validate(
        spec.candidate.to_sympy(),
        CompilerConfig(variables=(spec.variable,), max_depth=13, max_nodes=128),
        {spec.variable: splits[0].inputs[spec.variable]},
    )

    assert result.validation is not None
    assert result.validation.passed
    assert result.metadata.depth <= 13
    assert any(entry.rule == "scaled_exp_minus_one_template" for entry in result.metadata.trace)
    assert result.metadata.macro_diagnostics is not None
    assert result.metadata.macro_diagnostics["hits"] == ["scaled_exp_minus_one_template"]
    assert result.metadata.macro_diagnostics["depth_delta"] > 0
    assert result.metadata.macro_diagnostics["node_delta"] > 0


def test_compile_reciprocal_shift_uses_template():
    assert CompilerConfig().max_depth == 13
    assert CompilerConfig().max_nodes == 256

    x = sp.Symbol("x")
    inputs = {"x": np.linspace(0.25, 2.5, 12).astype(np.complex128)}
    result = compile_and_validate(
        1 / (x + sp.Float("0.5")),
        CompilerConfig(variables=("x",), max_depth=13, max_nodes=256),
        inputs,
    )

    assert result.validation is not None
    assert result.validation.passed
    assert result.metadata.unsupported_reason is None
    assert result.metadata.depth == 10
    assert result.metadata.node_count == 25
    assert result.metadata.macro_diagnostics is not None
    assert result.metadata.macro_diagnostics["hits"] == ["reciprocal_shift_template"]
    assert result.metadata.macro_diagnostics["baseline_depth"] == 14
    assert result.metadata.macro_diagnostics["baseline_node_count"] == 43
    assert result.metadata.macro_diagnostics["depth_delta"] == 4
    assert result.metadata.macro_diagnostics["node_delta"] == 18
    assert [entry.rule for entry in result.metadata.trace].count("reciprocal_shift_template") == 1
    assert "saturation_ratio_template" not in result.metadata.macro_diagnostics["hits"]


def test_compile_michaelis_uses_saturation_ratio_template():
    spec = get_demo("michaelis_menten")
    splits = spec.make_splits(points=24, seed=0)
    result = compile_and_validate(
        spec.candidate.to_sympy(),
        CompilerConfig(variables=(spec.variable,), max_depth=13, max_nodes=256),
        {spec.variable: splits[0].inputs[spec.variable]},
    )

    assert result.validation is not None
    assert result.validation.passed
    assert result.metadata.unsupported_reason is None
    assert result.metadata.depth == 12
    assert result.metadata.node_count == 41
    assert result.metadata.macro_diagnostics is not None
    macro = result.metadata.macro_diagnostics
    assert macro["hits"] == ["saturation_ratio_template"]
    assert macro["baseline_depth"] == 18
    assert macro["baseline_node_count"] == 75
    assert macro["depth_delta"] == 6
    assert macro["node_delta"] == 34
    assert [entry.rule for entry in result.metadata.trace].count("saturation_ratio_template") == 1
    assert "reciprocal_shift_template" not in macro["hits"]
    assert "direct_division_template" not in macro["hits"]


def test_unit_shift_macros_do_not_smuggle_basis_only_constants():
    x = sp.Symbol("x")
    config = CompilerConfig(variables=("x",), constant_policy="basis_only", max_depth=13, max_nodes=256)

    for expr in (1 / (x + 1), x / (x + 1)):
        with pytest.raises(UnsupportedExpression) as error:
            compile_sympy_expression(expr, config)
        assert error.value.reason == CompileReason.DEPTH_EXCEEDED


def test_unit_shift_macro_rejects_nonfinite_derived_constant():
    x = sp.Symbol("x")
    expr = 1 / (x + sp.Float("-1000"))

    with pytest.raises(UnsupportedExpression) as error:
        compile_sympy_expression(expr, CompilerConfig(variables=("x",), max_depth=13, max_nodes=256))
    assert error.value.reason == CompileReason.DEPTH_EXCEEDED

    relaxed = compile_sympy_expression(expr, CompilerConfig(variables=("x",), max_depth=64, max_nodes=512))

    assert relaxed.metadata.macro_diagnostics is not None
    assert relaxed.metadata.macro_diagnostics["hits"] == []
    assert all(np.isfinite(value.real) and np.isfinite(value.imag) for value in relaxed.metadata.constants)


def test_explicit_unit_coefficient_reciprocal_shift_uses_template():
    x = sp.Symbol("x")
    inputs = {"x": np.linspace(0.25, 2.5, 12).astype(np.complex128)}
    result = compile_and_validate(
        1 / (sp.Float("1.0") * x + sp.Float("0.5")),
        CompilerConfig(variables=("x",), max_depth=13, max_nodes=256),
        inputs,
    )

    assert result.validation is not None
    assert result.validation.passed
    assert result.metadata.depth == 10
    assert result.metadata.node_count == 25
    assert result.metadata.macro_diagnostics is not None
    assert result.metadata.macro_diagnostics["hits"] == ["reciprocal_shift_template"]


def test_explicit_unit_coefficient_saturation_ratio_uses_template():
    x = sp.Symbol("x")
    inputs = {"x": np.linspace(0.25, 2.5, 12).astype(np.complex128)}
    result = compile_and_validate(
        sp.Float("2.0") * x / (sp.Float("1.0") * x + sp.Float("0.5")),
        CompilerConfig(variables=("x",), max_depth=13, max_nodes=256),
        inputs,
    )

    assert result.validation is not None
    assert result.validation.passed
    assert result.metadata.depth == 12
    assert result.metadata.node_count == 41
    assert result.metadata.macro_diagnostics is not None
    assert result.metadata.macro_diagnostics["hits"] == ["saturation_ratio_template"]


def test_reciprocal_shift_accepts_compilable_subexpression():
    x = sp.Symbol("x")
    inputs = {"x": np.linspace(0.25, 2.5, 12).astype(np.complex128)}
    result = compile_and_validate(
        1 / (sp.exp(x) + sp.Float("0.5")),
        CompilerConfig(variables=("x",), max_depth=13, max_nodes=256),
        inputs,
    )

    assert result.validation is not None
    assert result.validation.passed
    assert result.metadata.macro_diagnostics is not None
    macro = result.metadata.macro_diagnostics
    assert macro["hits"] == ["reciprocal_shift_template"]
    assert macro["validation_status"] == "validated"
    assert macro["validation_passed"] is True


def test_saturation_ratio_accepts_compilable_subexpression():
    x = sp.Symbol("x")
    inputs = {"x": np.linspace(0.25, 2.5, 12).astype(np.complex128)}
    result = compile_and_validate(
        sp.Float("2.0") * sp.exp(x) / (sp.exp(x) + sp.Float("0.5")),
        CompilerConfig(variables=("x",), max_depth=13, max_nodes=256),
        inputs,
    )

    assert result.validation is not None
    assert result.validation.passed
    assert result.metadata.macro_diagnostics is not None
    macro = result.metadata.macro_diagnostics
    assert macro["hits"] == ["saturation_ratio_template"]
    assert macro["validation_status"] == "validated"
    assert macro["validation_passed"] is True


def test_generalized_shift_templates_fail_closed_on_non_unit_base_coefficient():
    x = sp.Symbol("x")

    for expr, forbidden in (
        (1 / (sp.Float("2.0") * sp.exp(x) + sp.Float("0.5")), "reciprocal_shift_template"),
        (
            sp.Float("2.0") * sp.exp(x) / (sp.Float("2.0") * sp.exp(x) + sp.Float("0.5")),
            "saturation_ratio_template",
        ),
    ):
        relaxed = compile_sympy_expression(expr, CompilerConfig(variables=("x",), max_depth=64, max_nodes=512))
        assert relaxed.metadata.macro_diagnostics is not None
        assert forbidden not in relaxed.metadata.macro_diagnostics["hits"]


def test_plain_compile_macro_diagnostics_mark_validation_not_run():
    x = sp.Symbol("x")
    result = compile_sympy_expression(
        1 / (sp.exp(x) + sp.Float("0.5")),
        CompilerConfig(variables=("x",), max_depth=13, max_nodes=256),
    )

    assert result.metadata.macro_diagnostics is not None
    assert result.metadata.macro_diagnostics["hits"] == ["reciprocal_shift_template"]
    assert result.metadata.macro_diagnostics["validation_status"] == "not_run"
    assert result.metadata.macro_diagnostics["validation_passed"] is None


def test_non_unit_coefficient_shift_does_not_use_unit_shift_templates():
    x = sp.Symbol("x")

    for expr in (1 / (2 * x + sp.Float("0.5")), sp.Float("2.0") * x / (2 * x + sp.Float("0.5"))):
        with pytest.raises(UnsupportedExpression) as error:
            compile_sympy_expression(expr, CompilerConfig(variables=("x",), max_depth=13, max_nodes=256))
        assert error.value.reason == CompileReason.DEPTH_EXCEEDED

        relaxed = compile_sympy_expression(expr, CompilerConfig(variables=("x",), max_depth=64, max_nodes=512))

        assert relaxed.metadata.macro_diagnostics is not None
        assert "reciprocal_shift_template" not in relaxed.metadata.macro_diagnostics["hits"]
        assert "saturation_ratio_template" not in relaxed.metadata.macro_diagnostics["hits"]


def test_compile_arrhenius_uses_direct_division_template():
    spec = get_demo("arrhenius")
    splits = spec.make_splits(points=24, seed=0)
    result = compile_and_validate(
        spec.candidate.to_sympy(),
        CompilerConfig(variables=(spec.variable,), max_depth=13, max_nodes=256),
        {spec.variable: splits[0].inputs[spec.variable]},
    )

    assert result.validation is not None
    assert result.validation.passed
    assert result.metadata.unsupported_reason is None
    assert result.metadata.depth == 7
    assert result.metadata.node_count <= 256
    assert result.metadata.macro_diagnostics is not None
    assert result.metadata.macro_diagnostics["hits"] == ["direct_division_template"]
    assert [entry.rule for entry in result.metadata.trace].count("direct_division_template") == 1


def test_compiler_fail_closed_negative_cases():
    x = sp.Symbol("x")

    with pytest.raises(UnsupportedExpression) as sin_error:
        compile_sympy_expression(sp.sin(x), CompilerConfig(variables=("x",)))
    assert sin_error.value.reason == CompileReason.UNSUPPORTED_OPERATOR

    with pytest.raises(UnsupportedExpression) as variable_error:
        compile_sympy_expression(x + sp.Symbol("y"), CompilerConfig(variables=("x",)))
    assert variable_error.value.reason == CompileReason.UNKNOWN_VARIABLE

    with pytest.raises(UnsupportedExpression) as constant_error:
        compile_sympy_expression(sp.Float("0.5"), CompilerConfig(constant_policy="basis_only"))
    assert constant_error.value.reason == CompileReason.CONSTANT_POLICY

    with pytest.raises(UnsupportedExpression) as depth_error:
        compile_sympy_expression(sp.exp(sp.Float("-0.8") * x), CompilerConfig(variables=("x",), max_depth=3))
    assert depth_error.value.reason == CompileReason.DEPTH_EXCEEDED

    n = sp.Symbol("n", integer=True)
    with pytest.raises(UnsupportedExpression) as symbolic_power_error:
        compile_sympy_expression(x**n, CompilerConfig(variables=("x",)))
    assert symbolic_power_error.value.reason == CompileReason.UNSUPPORTED_POWER


def test_compile_logistic_uses_exponential_saturation_template():
    spec = get_demo("logistic")
    splits = spec.make_splits(points=12, seed=0)
    diagnostic = diagnose_compile_expression(
        spec.candidate.to_sympy(),
        CompilerConfig(variables=(spec.variable,), max_depth=13, max_nodes=256),
        {spec.variable: splits[0].inputs[spec.variable]},
    )

    assert diagnostic["status"] == "unsupported"
    assert diagnostic["strict"]["reason"] == CompileReason.DEPTH_EXCEEDED
    relaxed = diagnostic["relaxed"]["metadata"]
    assert relaxed["depth"] == 15
    assert relaxed["node_count"] == 49
    macro = relaxed["macro_diagnostics"]
    assert macro["hits"] == ["exponential_saturation_template"]
    assert macro["baseline_depth"] == 27
    assert macro["baseline_node_count"] == 77
    assert macro["depth_delta"] == 12
    assert macro["node_delta"] == 28
    assert macro["validation_status"] == "validated"
    assert macro["validation_passed"] is True


def test_exponential_saturation_template_supports_equivalent_ratio_shape():
    x = sp.Symbol("x")
    inputs = {"x": np.linspace(0.25, 2.5, 12).astype(np.complex128)}
    result = compile_and_validate(
        sp.exp(sp.Float("1.3") * x) / (sp.exp(sp.Float("1.3") * x) + sp.Float("2.0")),
        CompilerConfig(variables=("x",), max_depth=15, max_nodes=256),
        inputs,
    )

    assert result.validation is not None
    assert result.validation.passed
    assert result.metadata.depth == 15
    assert result.metadata.macro_diagnostics is not None
    assert result.metadata.macro_diagnostics["hits"] == ["exponential_saturation_template"]


def test_exponential_saturation_template_normalizes_equal_scale_ratio_shape():
    x = sp.Symbol("x")
    inputs = {"x": np.linspace(0.25, 2.5, 12).astype(np.complex128)}
    result = compile_and_validate(
        sp.Float("2.0") * sp.exp(sp.Float("1.3") * x)
        / (sp.Float("2.0") * sp.exp(sp.Float("1.3") * x) + sp.Float("3.0")),
        CompilerConfig(variables=("x",), max_depth=15, max_nodes=256),
        inputs,
    )

    assert result.validation is not None
    assert result.validation.passed
    assert result.metadata.depth == 15
    assert result.metadata.macro_diagnostics is not None
    assert result.metadata.macro_diagnostics["hits"] == ["exponential_saturation_template"]


def test_low_degree_power_template_shortens_cube_but_not_square():
    x = sp.Symbol("x")
    inputs = {"x": np.linspace(0.25, 2.5, 12).astype(np.complex128)}

    cube = compile_and_validate(
        x**3,
        CompilerConfig(variables=("x",), max_depth=13, max_nodes=256),
        inputs,
    )
    assert cube.validation is not None
    assert cube.validation.passed
    assert cube.metadata.depth == 9
    assert cube.metadata.node_count == 25
    assert cube.metadata.macro_diagnostics is not None
    cube_macro = cube.metadata.macro_diagnostics
    assert cube_macro["hits"] == ["low_degree_power_template"]
    assert cube_macro["baseline_depth"] == 16
    assert cube_macro["baseline_node_count"] == 33
    assert cube_macro["depth_delta"] == 7
    assert cube_macro["node_delta"] == 8
    assert cube_macro["validation_status"] == "validated"
    assert cube_macro["validation_passed"] is True

    record = validate_motif_candidate(
        motif_name="low_degree_power_template",
        target_family="positive_integer_power",
        target_expression=x**3,
        candidate=exp_of(multiply_expr(Const(3.0), log_of(Var("x")))),
        variables=("x",),
        inputs=inputs,
        candidate_construction="exp(3*log(g))",
        baseline_depth=16,
        baseline_node_count=33,
    )
    assert record.accepted
    assert record.sample_count == inputs["x"].size
    assert record.candidate_depth == 9
    assert record.candidate_node_count == 25
    assert record.as_dict()["target_family"] == "positive_integer_power"

    square = compile_and_validate(
        x**2,
        CompilerConfig(variables=("x",), max_depth=13, max_nodes=256),
        inputs,
    )
    assert square.validation is not None
    assert square.validation.passed
    assert square.metadata.depth == 8
    assert square.metadata.macro_diagnostics is not None
    assert "low_degree_power_template" not in square.metadata.macro_diagnostics["hits"]


def test_planck_compile_depth_drops_below_archived_relaxed_diagnostic():
    spec = get_demo("planck")
    splits = spec.make_splits(points=12, seed=0)
    diagnostic = diagnose_compile_expression(
        spec.candidate.to_sympy(),
        CompilerConfig(variables=(spec.variable,), max_depth=13, max_nodes=256),
        {spec.variable: splits[0].inputs[spec.variable]},
    )

    assert diagnostic["status"] == "unsupported"
    assert diagnostic["strict"]["reason"] == CompileReason.DEPTH_EXCEEDED
    metadata = diagnostic["relaxed"]["metadata"]
    assert metadata["depth"] == 14
    assert metadata["depth"] < 20
    assert metadata["node_count"] == 59
    macro = metadata["macro_diagnostics"]
    assert set(macro["hits"]) == {
        "low_degree_power_template",
        "scaled_exp_minus_one_template",
        "direct_division_template",
    }
    assert macro["depth_delta"] > 0
    assert macro["node_delta"] > 0


def test_existing_macro_supported_demos_do_not_regress():
    assert CompilerConfig().max_depth == 13
    assert CompilerConfig().max_nodes == 256

    cases = (
        ("shockley", "scaled_exp_minus_one_template", None, None),
        ("arrhenius", "direct_division_template", 7, None),
        ("michaelis_menten", "saturation_ratio_template", 12, 41),
    )
    for demo_name, expected_macro, expected_depth, expected_nodes in cases:
        spec = get_demo(demo_name)
        splits = spec.make_splits(points=24, seed=0)
        result = compile_and_validate(
            spec.candidate.to_sympy(),
            CompilerConfig(variables=(spec.variable,), max_depth=13, max_nodes=256),
            {spec.variable: splits[0].inputs[spec.variable]},
        )

        assert result.validation is not None
        assert result.validation.passed
        assert result.metadata.unsupported_reason is None
        assert result.metadata.macro_diagnostics is not None
        assert result.metadata.macro_diagnostics["hits"] == [expected_macro]
        if expected_depth is not None:
            assert result.metadata.depth == expected_depth
        if expected_nodes is not None:
            assert result.metadata.node_count == expected_nodes


def test_damped_oscillator_diagnostic_defers_unsupported_cos():
    spec = get_demo("damped_oscillator")
    diagnostic = diagnose_compile_expression(
        spec.candidate.to_sympy(),
        CompilerConfig(variables=(spec.variable,), max_depth=13, max_nodes=256),
    )

    assert diagnostic["status"] == "unsupported"
    assert diagnostic["strict"]["reason"] == CompileReason.UNSUPPORTED_OPERATOR
    assert diagnostic["relaxed_error"]["reason"] == CompileReason.UNSUPPORTED_OPERATOR


def test_constant_catalog_and_embedding_round_trip_for_beer_lambert():
    x = sp.Symbol("x")
    compiled = compile_and_validate(
        sp.exp(sp.Float("-0.8") * x),
        CompilerConfig(variables=("x",), max_depth=12, max_nodes=128),
    )
    tree = SoftEMLTree(compiled.metadata.depth, ("x",), compiled.metadata.constants)
    assert "const:-0.8" in tree.slot_catalog()["root.left"]

    embedding = tree.embed_expr(compiled.expression, EmbeddingConfig(strength=40.0))
    assert embedding.success
    assert embedding.round_trip_equal
    assert embedding.snap.min_margin > 0.99


def test_embedding_reports_missing_terminals():
    x = sp.Symbol("x")
    compiled = compile_and_validate(
        sp.exp(sp.Float("-0.8") * x),
        CompilerConfig(variables=("x",), max_depth=12, max_nodes=128),
    )
    tree = SoftEMLTree(compiled.metadata.depth, ("x",), (1.0,))

    with pytest.raises(EmbeddingError) as error:
        tree.embed_expr(compiled.expression)
    assert error.value.reason == "missing_constant"


def test_warm_start_manifest_returns_same_ast_and_verifies():
    spec = get_demo("beer_lambert")
    splits = spec.make_splits(points=24, seed=0)
    compiled = compile_and_validate(
        spec.candidate.to_sympy(),
        CompilerConfig(variables=(spec.variable,), max_depth=12, max_nodes=128),
        {spec.variable: splits[0].inputs[spec.variable]},
    )
    result = fit_warm_started_eml_tree(
        splits[0].inputs,
        splits[0].target,
        TrainingConfig(depth=compiled.metadata.depth, variables=(spec.variable,), steps=1, restarts=1, seed=0),
        compiled.expression,
        perturbation_config=PerturbationConfig(seed=0, noise_scale=0.0),
        verification_splits=splits,
        compiler_metadata=compiled.metadata.as_dict(),
    )

    assert result.status == "same_ast_return"
    assert result.verification is not None
    assert result.verification.status == "recovered"
    assert result.manifest["optimizer"]["status"] == "snapped_candidate"
    assert result.manifest["status"] == "same_ast_return"
    assert result.manifest["diagnosis"]["mechanism"] == "same_ast_return"
    assert result.manifest["diagnosis"]["changed_slot_count"] == 0


def test_arrhenius_warm_start_returns_same_ast_and_verifies():
    # v1.9-arrhenius-evidence / arrhenius-warm is same_ast evidence, not blind discovery.
    spec = get_demo("arrhenius")
    splits = spec.make_splits(points=24, seed=0)
    compiled = compile_and_validate(
        spec.candidate.to_sympy(),
        CompilerConfig(variables=(spec.variable,), max_depth=13, max_nodes=256),
        {spec.variable: splits[0].inputs[spec.variable]},
    )
    result = fit_warm_started_eml_tree(
        splits[0].inputs,
        splits[0].target,
        TrainingConfig(depth=compiled.metadata.depth, variables=(spec.variable,), steps=1, restarts=1, seed=0),
        compiled.expression,
        perturbation_config=PerturbationConfig(seed=0, noise_scale=0.0),
        verification_splits=splits,
        compiler_metadata=compiled.metadata.as_dict(),
    )

    assert result.status == "same_ast_return"
    assert result.verification is not None
    assert result.verification.status == "recovered"
    assert result.manifest["status"] == "same_ast_return"
    assert result.manifest["diagnosis"]["mechanism"] == "same_ast_return"
    assert result.manifest["diagnosis"]["changed_slot_count"] == 0
    assert result.manifest["compiler_metadata"]["macro_diagnostics"]["hits"] == ["direct_division_template"]


def test_michaelis_warm_start_returns_same_ast_and_verifies():
    spec = get_demo("michaelis_menten")
    splits = spec.make_splits(points=24, seed=0)
    compiled = compile_and_validate(
        spec.candidate.to_sympy(),
        CompilerConfig(variables=(spec.variable,), max_depth=13, max_nodes=256),
        {spec.variable: splits[0].inputs[spec.variable]},
    )
    result = fit_warm_started_eml_tree(
        splits[0].inputs,
        splits[0].target,
        TrainingConfig(depth=compiled.metadata.depth, variables=(spec.variable,), steps=1, restarts=1, seed=0),
        compiled.expression,
        perturbation_config=PerturbationConfig(seed=0, noise_scale=0.0),
        verification_splits=splits,
        compiler_metadata=compiled.metadata.as_dict(),
    )

    assert result.status == "same_ast_return"
    assert result.verification is not None
    assert result.verification.status == "recovered"
    assert result.manifest["status"] == "same_ast_return"
    assert result.manifest["diagnosis"]["mechanism"] == "same_ast_return"
    assert result.manifest["diagnosis"]["changed_slot_count"] == 0
    assert result.manifest["compiler_metadata"]["depth"] == 12
    assert result.manifest["compiler_metadata"]["node_count"] == 41
    assert result.manifest["compiler_metadata"]["macro_diagnostics"]["hits"] == ["saturation_ratio_template"]


def test_perturbation_is_seeded_and_reports_active_slots():
    spec = get_demo("beer_lambert")
    compiled = compile_and_validate(
        spec.candidate.to_sympy(),
        CompilerConfig(variables=(spec.variable,), max_depth=12, max_nodes=128),
    )
    reports = []
    for _ in range(2):
        tree = SoftEMLTree(compiled.metadata.depth, (spec.variable,), compiled.metadata.constants)
        embedding = tree.embed_expr(compiled.expression, EmbeddingConfig(strength=30.0))
        reports.append(perturb_tree_logits(tree, PerturbationConfig(seed=123, noise_scale=0.01), embedding))

    assert reports[0].as_dict() == reports[1].as_dict()
    assert reports[0].active_slot_changes
    assert {"slot", "embedded_choice", "pre_choice", "post_choice", "changed"} <= set(
        reports[0].active_slot_changes[0]
    )


def test_high_noise_warm_start_records_failure_mechanism():
    spec = get_demo("beer_lambert")
    splits = spec.make_splits(points=24, seed=0)
    compiled = compile_and_validate(
        spec.candidate.to_sympy(),
        CompilerConfig(variables=(spec.variable,), max_depth=12, max_nodes=128),
        {spec.variable: splits[0].inputs[spec.variable]},
    )
    result = fit_warm_started_eml_tree(
        splits[0].inputs,
        splits[0].target,
        TrainingConfig(depth=compiled.metadata.depth, variables=(spec.variable,), steps=1, restarts=1, seed=0),
        compiled.expression,
        perturbation_config=PerturbationConfig(seed=0, noise_scale=35.0),
        verification_splits=splits,
        compiler_metadata=compiled.metadata.as_dict(),
    )
    diagnosis = result.manifest["diagnosis"]

    assert diagnosis["active_slot_count"] > 0
    assert diagnosis["changed_slot_count"] > 0
    assert diagnosis["mechanism"] == "active_slot_perturbation"
    assert diagnosis["verifier_status"] in {"failed", "recovered"}


def test_cli_warm_start_promotes_beer_lambert_only_after_verification(tmp_path):
    output = tmp_path / "beer-warm.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "eml_symbolic_regression.cli",
            "demo",
            "beer_lambert",
            "--warm-start-eml",
            "--points",
            "24",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        env=CLI_ENV,
        text=True,
    )
    assert "trained_exact_recovery=recovered" in result.stdout
    payload = json.loads(output.read_text())
    assert payload["claim_status"] == "recovered"
    assert payload["stage_statuses"]["catalog_showcase"] == "verified_showcase"
    assert payload["stage_statuses"]["trained_exact_recovery"] == "recovered"


def test_cli_warm_start_promotes_shockley_after_macro_shortening(tmp_path):
    output = tmp_path / "shockley-warm.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "eml_symbolic_regression.cli",
            "demo",
            "shockley",
            "--warm-start-eml",
            "--points",
            "24",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        env=CLI_ENV,
        text=True,
    )

    assert "compiled_seed=recovered" in result.stdout
    payload = json.loads(output.read_text())
    assert payload["claim_status"] == "recovered"
    assert payload["stage_statuses"]["compiled_seed"] == "recovered"
    assert payload["stage_statuses"]["warm_start_attempt"] == "same_ast_return"
    assert payload["stage_statuses"]["trained_exact_recovery"] == "recovered"
    assert payload["compiled_eml"]["metadata"]["macro_diagnostics"]["hits"] == ["scaled_exp_minus_one_template"]


def test_cli_warm_start_promotes_arrhenius_same_ast_evidence(tmp_path):
    # Benchmark suite v1.9-arrhenius-evidence case arrhenius-warm must classify this as same_ast.
    spec = get_demo("arrhenius")
    assert spec.train_domain == (0.5, 3.0)
    assert spec.heldout_domain == (0.6, 2.7)
    assert spec.extrap_domain == (3.1, 4.2)

    output = tmp_path / "arrhenius-warm.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "eml_symbolic_regression.cli",
            "demo",
            "arrhenius",
            "--warm-start-eml",
            "--points",
            "24",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        env=CLI_ENV,
        text=True,
    )

    assert "compiled_seed=recovered" in result.stdout
    assert "trained_exact_recovery=recovered" in result.stdout
    payload = json.loads(output.read_text())
    assert payload["demo"] == "arrhenius"
    assert payload["candidate"]["sympy"] == "exp(-0.8/x)"
    assert payload["claim_status"] == "recovered"
    assert payload["stage_statuses"]["compiled_seed"] == "recovered"
    assert payload["stage_statuses"]["warm_start_attempt"] == "same_ast_return"
    assert payload["stage_statuses"]["trained_exact_recovery"] == "recovered"
    assert payload["compiled_eml"]["metadata"]["macro_diagnostics"]["hits"] == ["direct_division_template"]
    assert payload["compiled_eml"]["metadata"]["depth"] == 7
    assert payload["warm_start_eml"]["status"] == "same_ast_return"
    assert payload["warm_start_eml"]["verification"]["status"] == "recovered"
    assert payload["warm_start_eml"]["diagnosis"]["changed_slot_count"] == 0


def test_cli_warm_start_promotes_michaelis_same_ast_evidence(tmp_path):
    output = tmp_path / "mm-warm.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "eml_symbolic_regression.cli",
            "demo",
            "michaelis_menten",
            "--warm-start-eml",
            "--points",
            "24",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        env=CLI_ENV,
        text=True,
    )
    assert "compiled_seed=recovered" in result.stdout
    assert "warm_start_attempt=same_ast_return" in result.stdout
    assert "trained_exact_recovery=recovered" in result.stdout

    payload = json.loads(output.read_text())
    assert payload["demo"] == "michaelis_menten"
    assert payload["claim_status"] == "recovered"
    assert payload["stage_statuses"]["compiled_seed"] == "recovered"
    assert payload["stage_statuses"]["warm_start_attempt"] == "same_ast_return"
    assert payload["stage_statuses"]["trained_exact_recovery"] == "recovered"
    assert "blind_baseline" not in payload["stage_statuses"]
    assert payload["compiled_eml"]["metadata"]["depth"] == 12
    assert payload["compiled_eml"]["metadata"]["node_count"] == 41
    assert payload["compiled_eml"]["metadata"]["macro_diagnostics"]["hits"] == ["saturation_ratio_template"]
    assert payload["warm_start_eml"]["status"] == "same_ast_return"
    assert payload["warm_start_eml"]["verification"]["status"] == "recovered"
    assert payload["warm_start_eml"]["diagnosis"]["changed_slot_count"] == 0


def test_cli_reports_planck_as_stretch_without_promotion(tmp_path):
    output = tmp_path / "planck-warm.json"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "eml_symbolic_regression.cli",
            "demo",
            "planck",
            "--warm-start-eml",
            "--points",
            "24",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        env=CLI_ENV,
        text=True,
    )
    payload = json.loads(output.read_text())
    assert payload["claim_status"] == "verified_showcase"
    assert payload["stage_statuses"]["stretch"] == "reported"
    assert payload["stretch"]["guaranteed_trained_recovery"] is False
    assert payload["warm_start_eml"]["status"] == "unsupported"
    relaxed_macro = payload["compiled_eml"]["diagnostic"]["relaxed"]["metadata"]["macro_diagnostics"]
    assert set(relaxed_macro["hits"]) == {
        "low_degree_power_template",
        "scaled_exp_minus_one_template",
        "direct_division_template",
    }
    assert relaxed_macro["depth_delta"] > 0
