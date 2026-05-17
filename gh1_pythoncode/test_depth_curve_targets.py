import pytest

from eml_symbolic_regression.datasets import get_demo, proof_dataset_manifest
from eml_symbolic_regression.depth_curve import depth_curve_target_spec, depth_curve_target_specs
from eml_symbolic_regression.expression import Expr
from eml_symbolic_regression.verify import verify_candidate


EXPECTED_DEPTH_CURVE_TARGETS = {
    "depth_curve_depth2": {"depth": 2, "nodes": 5},
    "depth_curve_depth3": {"depth": 3, "nodes": 7},
    "depth_curve_depth4": {"depth": 4, "nodes": 11},
    "depth_curve_depth5": {"depth": 5, "nodes": 11},
    "depth_curve_depth6": {"depth": 6, "nodes": 13},
}

EXPECTED_DOMAINS = ((1.2, 2.0), (1.25, 1.9), (2.05, 2.4))


def _heldout_inside_train(train: tuple[float, float], heldout: tuple[float, float]) -> bool:
    return train[0] <= heldout[0] < heldout[1] <= train[1]


def _extrap_disjoint_from_train(train: tuple[float, float], extrap: tuple[float, float]) -> bool:
    return train[1] < extrap[0]


def test_depth_curve_target_inventory_is_deterministic_and_exact() -> None:
    specs = depth_curve_target_specs()

    assert tuple(spec.id for spec in specs) == tuple(EXPECTED_DEPTH_CURVE_TARGETS)
    assert depth_curve_target_specs() == specs

    for target_id, expected in EXPECTED_DEPTH_CURVE_TARGETS.items():
        spec = depth_curve_target_spec(target_id)

        assert spec.variable == "x"
        assert spec.expression.depth() == expected["depth"]
        assert spec.expression.node_count() == expected["nodes"]
        assert spec.expression.constants() == {complex(1.0)}
        assert spec.source_document == "sources/NORTH_STAR.md"
        assert "Phase 32" in spec.source_linkage
        assert spec.train_domain == EXPECTED_DOMAINS[0]
        assert spec.heldout_domain == EXPECTED_DOMAINS[1]
        assert spec.extrap_domain == EXPECTED_DOMAINS[2]


@pytest.mark.parametrize("target_id", EXPECTED_DEPTH_CURVE_TARGETS)
def test_depth_curve_targets_are_demo_specs_and_verify(target_id: str) -> None:
    spec = depth_curve_target_spec(target_id)
    demo = get_demo(target_id)

    assert demo.name == target_id
    assert demo.variable == spec.variable
    assert demo.candidate == spec.expression
    assert demo.description == spec.description
    assert demo.normalized_dimensionless is True
    assert demo.train_domain == spec.train_domain
    assert demo.heldout_domain == spec.heldout_domain
    assert demo.extrap_domain == spec.extrap_domain

    report = verify_candidate(demo.candidate, demo.make_splits(points=24, seed=0), tolerance=1e-8)
    assert report.status == "recovered"


def test_depth_curve_domains_are_explicit_and_well_separated() -> None:
    for target_id in EXPECTED_DEPTH_CURVE_TARGETS:
        demo = get_demo(target_id)

        assert _heldout_inside_train(demo.train_domain, demo.heldout_domain)
        assert _extrap_disjoint_from_train(demo.train_domain, demo.extrap_domain)


def test_depth_curve_target_lookup_fails_closed() -> None:
    with pytest.raises(KeyError, match="Unknown depth-curve target"):
        depth_curve_target_spec("missing-depth-target")


def test_depth_curve_dataset_manifest_is_deterministic_and_formula_owned() -> None:
    manifest = proof_dataset_manifest("depth_curve_depth4", points=18, seed=5)

    assert manifest == proof_dataset_manifest("depth_curve_depth4", points=18, seed=5)
    assert manifest["schema"] == "eml.proof_dataset_manifest.v1"
    assert manifest["formula_id"] == "depth_curve_depth4"
    assert manifest["provenance"]["normalized_dimensionless"] is True
    assert manifest["provenance"]["source_document"] == "sources/NORTH_STAR.md"
    assert "Phase 32" in manifest["provenance"]["source_linkage"]
    assert tuple(tuple(split["domain"]) for split in manifest["splits"]) == EXPECTED_DOMAINS
    assert proof_dataset_manifest("depth_curve_depth4", points=18, seed=6)["manifest_sha256"] != manifest["manifest_sha256"]


def test_depth_curve_module_does_not_depend_on_demo_spec() -> None:
    assert all(isinstance(spec.expression, Expr) for spec in depth_curve_target_specs())
