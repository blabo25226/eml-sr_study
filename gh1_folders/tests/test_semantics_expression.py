import json

import mpmath as mp
import numpy as np
import torch

from eml_symbolic_regression.expression import Const, Eml, Geml, Var, ceml_s_expr, expr_from_document, exp_expr, geml_expr, ipi_eml_expr, log_expr, zeml_s_expr
from eml_symbolic_regression.semantics import (
    AnomalyStats,
    TrainingSemanticsConfig,
    ceml_s_operator,
    centered_eml_numpy,
    centered_eml_torch,
    eml_numpy,
    eml_operator_from_spec,
    eml_torch,
    geml_numpy,
    geml_operator,
    geml_torch,
    ipi_eml_operator,
    zeml_s_operator,
)


def test_eml_numpy_matches_definition():
    x = np.array([0.0, 0.5, 1.0], dtype=np.complex128)
    y = np.array([1.0, 2.0, 3.0], dtype=np.complex128)
    np.testing.assert_allclose(eml_numpy(x, y), np.exp(x) - np.log(y))


def test_paper_exp_identity():
    x = np.linspace(-1.0, 1.0, 20)
    expr = exp_expr("x")
    np.testing.assert_allclose(expr.evaluate_numpy({"x": x}), np.exp(x), atol=1e-12)


def test_paper_log_identity():
    x = np.linspace(0.25, 3.0, 20)
    expr = log_expr("x")
    np.testing.assert_allclose(expr.evaluate_numpy({"x": x}), np.log(x), atol=1e-12)


def test_ast_json_round_trip():
    expr = log_expr("x")
    document = expr.to_document(variables=["x"], source="test")
    encoded = json.dumps(document, sort_keys=True)
    decoded = json.loads(encoded)
    rebuilt = expr_from_document(decoded)
    x = np.linspace(0.5, 2.0, 8)
    np.testing.assert_allclose(rebuilt.evaluate_numpy({"x": x}), expr.evaluate_numpy({"x": x}))
    assert document["semantics"]["named_specialization"] == "eml"


def test_geml_numpy_and_torch_match_definition():
    x = np.array([0.0, 0.25, -0.5], dtype=np.complex128)
    y = np.array([1.0 + 0.2j, 1.5 + 0.4j, 2.0 + 0.1j], dtype=np.complex128)
    operator = geml_operator(2.0)

    np.testing.assert_allclose(geml_numpy(x, y, operator=operator), np.exp(2.0 * x) - np.log(y) / 2.0)

    torch_actual = geml_torch(torch.as_tensor(x), torch.as_tensor(y), operator=operator, training=False)
    torch.testing.assert_close(torch_actual, torch.as_tensor(np.exp(2.0 * x) - np.log(y) / 2.0))


def test_geml_operator_parses_named_specializations():
    raw = eml_operator_from_spec("eml")
    geml_one = eml_operator_from_spec("geml:1")
    ipi = eml_operator_from_spec("ipi_eml")
    generic = eml_operator_from_spec("geml:2")

    assert raw.is_raw
    assert geml_one.is_raw
    assert ipi.is_geml
    assert ipi.label == "ipi_eml"
    assert abs(ipi.a - 1j * np.pi) < 1e-12
    assert generic.is_geml
    assert generic.label == "GEML_2"


def test_geml_named_specializations_validate_parameter():
    try:
        geml_operator(2.0, specialization="ipi_eml")
    except ValueError as exc:
        assert "i*pi" in str(exc)
    else:
        raise AssertionError("i*pi specialization must require a = i*pi")


def test_geml_exact_ast_round_trip_backends_and_sympy():
    expr = ipi_eml_expr(Var("x"), Var("y"))
    document = expr.to_document(variables=["x", "y"], source="test")
    encoded = json.dumps(document, sort_keys=True)
    rebuilt = expr_from_document(json.loads(encoded))
    x = np.linspace(-0.5, 0.5, 8)
    y = np.linspace(1.1, 2.0, 8)

    assert isinstance(rebuilt, Geml)
    assert rebuilt.to_node()["operator"]["label"] == "ipi_eml"
    assert rebuilt.to_document()["semantics"]["operator_family"]["named_specialization"] == "ipi_eml"
    np.testing.assert_allclose(
        rebuilt.evaluate_numpy({"x": x, "y": y}),
        np.exp(1j * np.pi * x) - np.log(y) / (1j * np.pi),
        atol=1e-12,
    )
    assert abs(complex(rebuilt.evaluate_mpmath({"x": 0.25, "y": 1.75})) - complex(np.exp(1j * np.pi * 0.25) - np.log(1.75) / (1j * np.pi))) < 1e-12
    assert "pi" in str(rebuilt.to_sympy())


def test_ipi_eml_mpmath_uses_high_precision_pi():
    previous_dps = mp.mp.dps
    try:
        mp.mp.dps = 80
        expr = ipi_eml_expr(Var("x"), Var("y"))
        actual = expr.evaluate_mpmath({"x": mp.mpf("0.125"), "y": mp.mpf("1.75")})
        expected = mp.e ** (mp.j * mp.pi * mp.mpf("0.125")) - mp.log(mp.mpf("1.75")) / (mp.j * mp.pi)
        assert abs(actual - expected) < mp.mpf("1e-70")
    finally:
        mp.mp.dps = previous_dps


def test_geml_structural_identity():
    u = np.array([-0.4, 0.0, 0.5], dtype=np.complex128)
    v = np.array([1.2 + 0.1j, 1.7 + 0.2j, 2.2 + 0.3j], dtype=np.complex128)

    for operator in (geml_operator(1.0), geml_operator(2.0), ipi_eml_operator()):
        a = np.complex128(operator.a)
        node = geml_expr(Var("u"), Var("v"), a=a)
        actual = np.exp(a * node.evaluate_numpy({"u": u, "v": v}))
        expected = np.exp(a * np.exp(a * u)) / v
        np.testing.assert_allclose(actual, expected, atol=1e-12)


def test_centered_eml_numpy_matches_definition():
    x = np.array([-0.5, 0.0, 0.5], dtype=np.complex128)
    y = np.array([0.25, 1.0, 2.0], dtype=np.complex128)
    operator = ceml_s_operator(2.0)

    actual = centered_eml_numpy(x, y, operator=operator)
    expected = 2.0 * np.expm1(x / 2.0) - 2.0 * np.log1p((y - 1.0) / 2.0)

    np.testing.assert_allclose(actual, expected)


def test_centered_exact_ast_round_trip_and_backends():
    expr = ceml_s_expr(Var("x"), Const(1.0), s=4.0)
    document = expr.to_document(variables=["x"], source="test")
    encoded = json.dumps(document, sort_keys=True)
    rebuilt = expr_from_document(json.loads(encoded))
    x = np.linspace(-1.0, 1.0, 8)

    np.testing.assert_allclose(rebuilt.evaluate_numpy({"x": x}), 4.0 * np.expm1(x / 4.0), atol=1e-12)
    assert rebuilt.to_node()["operator"]["family"] == "ceml_s"
    assert rebuilt.to_document()["semantics"]["operator_family"]["label"] == "CEML_4"
    assert abs(complex(rebuilt.evaluate_mpmath({"x": 0.25})) - complex(4.0 * np.expm1(0.25 / 4.0))) < 1e-12
    assert "exp" in str(rebuilt.to_sympy())


def test_zeml_exact_ast_records_zero_terminal_family():
    expr = zeml_s_expr(Var("x"), Const(0.0), s=8.0)
    node = expr.to_node()

    assert node["operator"]["family"] == "zeml_s"
    assert node["operator"]["terminal"] == "zero"
    assert node["operator"]["t"] == 0.0


def test_constant_occurrences_and_updates_are_path_stable():
    expr = Eml(Const(-0.8), Eml(Var("x"), Const(1.0)))

    occurrences = expr.constant_occurrences()
    assert [(item.path, item.refittable) for item in occurrences] == [("root.L", True), ("root.R.R", False)]

    updated = expr.with_constant_updates({"root.L": -0.5})
    updated_occurrences = updated.constant_occurrences()

    assert [complex(item.value) for item in updated_occurrences] == [complex(-0.5), complex(1.0)]
    assert updated.to_node()["right"] == expr.to_node()["right"]


def test_eml_torch_reports_log_domain_anomalies_and_penalty():
    stats = AnomalyStats()
    semantics = TrainingSemanticsConfig(
        clamp_exp_real=1.0,
        log_domain_epsilon=0.05,
        log_safety_weight=2.0,
        log_safety_margin=0.4,
        log_safety_imag_tolerance=0.1,
    )
    x = torch.tensor([2.0 + 0.0j, 0.0 + 0.0j], dtype=torch.complex128)
    y = torch.tensor([0.01 + 0.0j, -0.2 + 0.0j], dtype=torch.complex128)

    out = eml_torch(x, y, training=True, semantics=semantics, stats=stats, node="root")

    assert out.shape == x.shape
    assert stats.clamp_count == 1
    assert stats.exp_overflow_count == 1
    assert stats.log_small_magnitude_count == 1
    assert stats.log_non_positive_real_count == 1
    assert stats.log_branch_cut_count == 1
    assert stats.branch_input_count == 2
    assert stats.log_branch_cut_proximity_count == 1
    assert stats.log_branch_cut_crossing_count == 0
    assert stats.invalid_domain_skip_count == 1
    assert stats.log_safety_penalty > 0.0
    assert float(stats.training_penalty().item()) > 0.0
    assert stats.by_node["root"]["log_branch_cut_count"] == 1
    assert stats.by_node["root"]["branch_input_count"] == 2


def test_eml_torch_faithful_training_bypasses_training_guards():
    stats = AnomalyStats()
    semantics = TrainingSemanticsConfig(
        mode="faithful",
        clamp_exp_real=1.0,
        log_domain_epsilon=0.05,
        log_safety_weight=2.0,
        log_safety_margin=0.4,
        log_safety_imag_tolerance=0.1,
    )
    x = torch.tensor([2.0 + 0.0j], dtype=torch.complex128)
    y = torch.tensor([0.01 + 0.0j], dtype=torch.complex128)

    out = eml_torch(x, y, training=True, semantics=semantics, stats=stats, node="root")

    torch.testing.assert_close(out, torch.exp(x) - torch.log(y))
    assert stats.clamp_count == 0
    assert stats.exp_overflow_count == 0
    assert stats.log_small_magnitude_count == 1
    assert stats.log_safety_penalty == 0.0
    assert float(stats.training_penalty().item()) == 0.0


def test_centered_eml_torch_reports_shifted_singularity_diagnostics():
    stats = AnomalyStats()
    semantics = TrainingSemanticsConfig(clamp_exp_real=1.0, log_domain_epsilon=0.05, log_safety_weight=1.0)
    x = torch.tensor([4.0 + 0.0j, 0.0 + 0.0j], dtype=torch.complex128)
    y = torch.tensor([-1.0 + 0.0j, 1.0 + 0.0j], dtype=torch.complex128)

    out = centered_eml_torch(x, y, operator=ceml_s_operator(2.0), training=True, semantics=semantics, stats=stats, node="root")

    assert out.shape == x.shape
    assert stats.clamp_count == 1
    assert stats.expm1_overflow_count == 1
    assert stats.log1p_branch_cut_count == 1
    assert stats.shifted_singularity_near_count == 1
    assert stats.shifted_singularity_min_distance == 0.0
    assert stats.by_node["root"]["shifted_singularity_near_count"] == 1
    assert float(stats.training_penalty().item()) > 0.0


def test_centered_eml_torch_faithful_training_bypasses_training_guards():
    stats = AnomalyStats()
    semantics = TrainingSemanticsConfig(mode="faithful", clamp_exp_real=1.0, log_domain_epsilon=0.05, log_safety_weight=1.0)
    x = torch.tensor([4.0 + 0.0j], dtype=torch.complex128)
    y = torch.tensor([1.0 + 0.0j], dtype=torch.complex128)

    out = centered_eml_torch(x, y, operator=ceml_s_operator(2.0), training=True, semantics=semantics, stats=stats, node="root")

    expected = 2.0 * torch.expm1(x / 2.0) - 2.0 * torch.log1p((y - 1.0) / 2.0)
    torch.testing.assert_close(out, expected)
    assert stats.clamp_count == 0
    assert stats.expm1_overflow_count == 0
    assert stats.log_safety_penalty == 0.0
    assert float(stats.training_penalty().item()) == 0.0


def test_training_semantics_config_rejects_unknown_mode():
    try:
        TrainingSemanticsConfig(mode="almost-faithful")
    except ValueError as exc:
        assert "guarded" in str(exc)
    else:
        raise AssertionError("unknown semantics mode should fail")
