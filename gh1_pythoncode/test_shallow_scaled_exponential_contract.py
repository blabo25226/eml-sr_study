import numpy as np
import pytest

from eml_symbolic_regression.compiler import scaled_exponential_expr
from eml_symbolic_regression.datasets import get_demo, proof_dataset_manifest
from eml_symbolic_regression.verify import verify_candidate


@pytest.mark.parametrize(
    ("formula_id", "variable", "coefficient"),
    [
        ("beer_lambert", "x", -0.8),
        ("radioactive_decay", "t", -0.4),
        ("scaled_exp_growth", "x", 0.4),
        ("scaled_exp_fast_decay", "x", -1.2),
    ],
)
def test_scaled_exponential_expr_is_exact_shape_evidence(formula_id: str, variable: str, coefficient: float) -> None:
    expr = scaled_exponential_expr(variable, coefficient)
    points = np.linspace(0.0, 2.0, 9)

    np.testing.assert_allclose(
        expr.evaluate_numpy({variable: points}),
        np.exp(coefficient * points).astype(np.complex128),
        atol=1e-10,
        rtol=1e-10,
    )
    assert expr.depth() == 9
    assert expr.node_count() == 19
    assert expr.constants() == {complex(1.0), complex(coefficient)}

    demo = get_demo(formula_id)
    report = verify_candidate(expr, demo.make_splits(points=32, seed=0), tolerance=1e-8)
    assert report.status == "recovered"


@pytest.mark.parametrize(
    ("formula_id", "symbolic_expression"),
    [
        ("scaled_exp_growth", "exp(0.4*x)"),
        ("scaled_exp_fast_decay", "exp(-1.2*x)"),
    ],
)
def test_signed_scaled_exponential_proof_targets_have_provenance(formula_id: str, symbolic_expression: str) -> None:
    spec = get_demo(formula_id)
    provenance = spec.formula_provenance()
    manifest = proof_dataset_manifest(formula_id, points=24, seed=3)

    assert provenance["normalized_dimensionless"] is True
    assert provenance["source_document"] == "sources/NORTH_STAR.md"
    assert "Phase 30 signed/scaled exponential proof coverage" in provenance["source_linkage"]
    assert provenance["symbolic_expression"] == symbolic_expression
    assert manifest["formula_id"] == formula_id
    assert manifest["provenance"] == provenance
    assert proof_dataset_manifest(formula_id, points=24, seed=3)["manifest_sha256"] == manifest["manifest_sha256"]
    assert proof_dataset_manifest(formula_id, points=24, seed=4)["manifest_sha256"] != manifest["manifest_sha256"]
