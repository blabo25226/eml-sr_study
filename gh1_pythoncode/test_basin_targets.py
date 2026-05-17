import pytest

from eml_symbolic_regression.basin import basin_target_spec, basin_target_specs
from eml_symbolic_regression.basin import fit_perturbed_true_tree
from eml_symbolic_regression.datasets import get_demo, proof_dataset_manifest
from eml_symbolic_regression.expression import Eml, Expr
from eml_symbolic_regression.optimize import TrainingConfig
from eml_symbolic_regression.verify import verify_candidate
from eml_symbolic_regression.warm_start import PerturbationConfig


EXPECTED_SYNTHETIC_TARGETS = {
    "basin_depth1_exp": {
        "depth": 1,
        "nodes": 3,
        "train": (-1.0, 1.0),
        "heldout": (-0.8, 0.8),
        "extrap": (1.1, 1.5),
    },
    "basin_depth2_exp_exp": {
        "depth": 2,
        "nodes": 5,
        "train": (-0.8, 0.2),
        "heldout": (-0.7, 0.1),
        "extrap": (0.3, 0.5),
    },
    "basin_depth3_exp_exp_exp": {
        "depth": 3,
        "nodes": 7,
        "train": (-1.0, -0.2),
        "heldout": (-0.9, -0.35),
        "extrap": (-1.4, -1.1),
    },
}

EXPECTED_PHASE31_DOMAINS = {
    **{
        target_id: (metadata["train"], metadata["heldout"], metadata["extrap"])
        for target_id, metadata in EXPECTED_SYNTHETIC_TARGETS.items()
    },
    "beer_lambert": ((0.0, 3.0), (0.15, 2.7), (3.1, 4.5)),
}


def _heldout_inside_train(train: tuple[float, float], heldout: tuple[float, float]) -> bool:
    return train[0] <= heldout[0] < heldout[1] <= train[1]


def _extrap_disjoint_from_train(train: tuple[float, float], extrap: tuple[float, float]) -> bool:
    return extrap[1] < train[0] or train[1] < extrap[0]


def test_basin_target_inventory_is_deterministic_and_exact() -> None:
    specs = basin_target_specs()
    assert tuple(spec.id for spec in specs) == tuple(EXPECTED_SYNTHETIC_TARGETS)
    assert basin_target_specs() == specs

    for target_id, expected in EXPECTED_SYNTHETIC_TARGETS.items():
        spec = basin_target_spec(target_id)

        assert spec.variable == "x"
        assert isinstance(spec.expression, Eml)
        assert spec.expression.depth() == expected["depth"]
        assert spec.expression.node_count() == expected["nodes"]
        assert spec.expression.constants() == {complex(1.0)}
        assert spec.train_domain == expected["train"]
        assert spec.heldout_domain == expected["heldout"]
        assert spec.extrap_domain == expected["extrap"]
        assert spec.source_document == "sources/NORTH_STAR.md"
        assert "Phase 31" in spec.source_linkage


@pytest.mark.parametrize("target_id", EXPECTED_SYNTHETIC_TARGETS)
def test_synthetic_basin_targets_are_demo_specs_and_verify(target_id: str) -> None:
    basin_spec = basin_target_spec(target_id)
    demo = get_demo(target_id)

    assert demo.name == target_id
    assert demo.variable == basin_spec.variable
    assert demo.candidate == basin_spec.expression
    assert demo.normalized_dimensionless is True
    assert demo.train_domain == basin_spec.train_domain
    assert demo.heldout_domain == basin_spec.heldout_domain
    assert demo.extrap_domain == basin_spec.extrap_domain

    report = verify_candidate(demo.candidate, demo.make_splits(points=24, seed=0), tolerance=1e-8)
    assert report.status == "recovered"


def test_phase31_basin_domains_are_explicit_and_well_separated() -> None:
    for target_id, expected_domains in EXPECTED_PHASE31_DOMAINS.items():
        demo = get_demo(target_id)
        train, heldout, extrap = expected_domains

        assert demo.train_domain == train
        assert demo.heldout_domain == heldout
        assert demo.extrap_domain == extrap
        assert _heldout_inside_train(train, heldout)
        assert _extrap_disjoint_from_train(train, extrap)


def test_basin_target_lookup_fails_closed() -> None:
    with pytest.raises(KeyError, match="Unknown basin target"):
        basin_target_spec("not_a_basin_target")


def test_basin_dataset_manifest_is_deterministic_and_formula_owned() -> None:
    manifest = proof_dataset_manifest("basin_depth2_exp_exp", points=18, seed=5)

    assert manifest == proof_dataset_manifest("basin_depth2_exp_exp", points=18, seed=5)
    assert manifest["schema"] == "eml.proof_dataset_manifest.v1"
    assert manifest["formula_id"] == "basin_depth2_exp_exp"
    assert manifest["variable"] == "x"
    assert manifest["provenance"]["normalized_dimensionless"] is True
    assert manifest["provenance"]["source_document"] == "sources/NORTH_STAR.md"
    assert "Phase 31" in manifest["provenance"]["source_linkage"]
    assert [split["domain"] for split in manifest["splits"]] == [
        [-0.8, 0.2],
        [-0.7, 0.1],
        [0.3, 0.5],
    ]
    assert proof_dataset_manifest("basin_depth2_exp_exp", points=18, seed=6)["manifest_sha256"] != manifest["manifest_sha256"]


def test_basin_module_does_not_depend_on_demo_spec() -> None:
    # A circular import here would make target inventory unusable before datasets are loaded.
    assert all(isinstance(spec.expression, Expr) for spec in basin_target_specs())


def test_fit_perturbed_true_tree_records_same_ast_return_as_raw_recovery() -> None:
    spec = basin_target_spec("basin_depth1_exp")
    demo = get_demo(spec.id)
    splits = demo.make_splits(points=12, seed=0)

    result = fit_perturbed_true_tree(
        splits[0].inputs,
        splits[0].target,
        TrainingConfig(depth=spec.expression.depth(), variables=(spec.variable,), steps=1, restarts=1, seed=0),
        spec.expression,
        perturbation_config=PerturbationConfig(seed=0, noise_scale=0.05),
        verification_splits=splits,
        tolerance=1e-8,
        target_metadata={"formula_id": spec.id},
    )

    assert result.status == "recovered"
    assert result.return_kind == "same_ast_return"
    assert result.verification is not None
    assert result.verification.status == "recovered"
    assert result.manifest["schema"] == "eml.perturbed_true_tree_manifest.v1"
    assert result.manifest["status"] == "recovered"
    assert result.manifest["raw_status"] == "recovered"
    assert result.manifest["return_kind"] == "same_ast_return"
    assert result.manifest["target_metadata"]["formula_id"] == spec.id
    assert result.manifest["optimizer"]["best_restart"]["initialization"]["kind"] == "perturbed_true_tree"
    assert result.manifest["perturbation_config"] == {"seed": 0, "noise_scale": 0.05}
