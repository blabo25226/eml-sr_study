import pytest
import numpy as np

from eml_symbolic_regression.datasets import demo_specs, get_demo, proof_dataset_manifest


FORBIDDEN_RAW_KEYS = {"inputs", "target", "train_x", "heldout_x", "extrap_x"}


def _walk_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


def _without_signatures(manifest):
    payload = dict(manifest)
    payload.pop("manifest_sha256", None)
    payload["splits"] = [
        {key: value for key, value in split.items() if key not in {"input_sha256", "target_sha256"}}
        for split in manifest["splits"]
    ]
    return payload


def test_proof_dataset_manifest_is_deterministic_for_same_seed():
    first = proof_dataset_manifest("exp", points=12, seed=7, tolerance=1e-8)
    second = proof_dataset_manifest("exp", points=12, seed=7, tolerance=1e-8)

    assert first == second
    assert first["schema"] == "eml.proof_dataset_manifest.v1"
    assert first["formula_id"] == "exp"
    assert first["variable"] == "x"
    assert first["seed"] == 7
    assert first["tolerance"] == 1e-8
    assert first["sample_policy"] == "linspace_with_seeded_0.2_percent_jitter"
    assert len(first["manifest_sha256"]) == 64

    split_counts = {split["name"]: split["count"] for split in first["splits"]}
    assert split_counts == {"train": 12, "heldout": 16, "extrapolation": 16}
    assert {split["name"] for split in first["splits"]} == {"train", "heldout", "extrapolation"}
    assert all(len(split["input_sha256"]) == 64 and len(split["target_sha256"]) == 64 for split in first["splits"])


def test_seed_changes_signatures_but_not_dataset_contract():
    seed_seven = proof_dataset_manifest("exp", points=12, seed=7, tolerance=1e-8)
    seed_eight = proof_dataset_manifest("exp", points=12, seed=8, tolerance=1e-8)

    assert seed_seven["formula_id"] == seed_eight["formula_id"] == "exp"
    assert seed_seven["variable"] == seed_eight["variable"] == "x"
    assert seed_seven["provenance"] == seed_eight["provenance"]
    assert _without_signatures(seed_seven) | {"seed": 8} == _without_signatures(seed_eight)
    assert seed_seven["manifest_sha256"] != seed_eight["manifest_sha256"]
    assert any(
        left["input_sha256"] != right["input_sha256"] or left["target_sha256"] != right["target_sha256"]
        for left, right in zip(seed_seven["splits"], seed_eight["splits"])
    )


def test_manifest_contains_split_domains_and_no_raw_arrays():
    manifest = proof_dataset_manifest("exp", points=12, seed=7, tolerance=1e-8)

    domains = {split["name"]: split["domain"] for split in manifest["splits"]}
    assert domains == {
        "train": [-1.0, 1.0],
        "heldout": [-0.8, 0.8],
        "extrapolation": [1.05, 1.5],
    }
    assert not (FORBIDDEN_RAW_KEYS & set(_walk_keys(manifest)))


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"points": 0}, "points must be positive"),
        ({"points": -1}, "points must be positive"),
        ({"tolerance": 0.0}, "tolerance must be positive"),
        ({"tolerance": -1e-8}, "tolerance must be positive"),
    ],
)
def test_proof_dataset_manifest_rejects_invalid_sampling_contracts(kwargs, message):
    with pytest.raises(ValueError, match=message):
        proof_dataset_manifest("exp", **kwargs)


def test_formula_provenance_is_explicit_for_all_demo_specs():
    for formula_id, spec in demo_specs().items():
        provenance = spec.formula_provenance()

        assert provenance["formula_id"] == formula_id
        assert provenance["variable"] == spec.variable
        assert provenance["description"] == spec.description
        assert provenance["symbolic_expression"]
        assert provenance["candidate_name"]
        assert provenance["source_document"]
        assert provenance["source_linkage"]
        assert isinstance(provenance["normalized_dimensionless"], bool)


def test_for_demo_and_paper_provenance_are_distinct():
    exp_provenance = get_demo("exp").formula_provenance()
    planck_provenance = get_demo("planck").formula_provenance()

    assert "sources/paper.pdf" in exp_provenance["source_document"]
    assert "sources/NORTH_STAR.md" in exp_provenance["source_linkage"]
    assert planck_provenance["source_document"] == "sources/FOR_DEMO.md"
    assert planck_provenance["normalized_dimensionless"] is True
    assert "Planck" in planck_provenance["source_linkage"]
    assert "exp" in exp_provenance["symbolic_expression"]


def test_arrhenius_demo_uses_positive_dimensionless_domains():
    # v1.9-arrhenius-evidence / arrhenius-warm must remain same_ast evidence:
    # direct_division_template -> same_ast_return -> recovered.
    spec = get_demo("arrhenius")

    assert spec.variable == "x"
    assert spec.train_domain == (0.5, 3.0)
    assert spec.heldout_domain == (0.6, 2.7)
    assert spec.extrap_domain == (3.1, 4.2)
    assert spec.normalized_dimensionless is True
    assert spec.source_document == "sources/FOR_DEMO.md"
    assert "Arrhenius" in spec.source_linkage

    splits = spec.make_splits(points=24, seed=0)
    for split in splits:
        values = split.inputs["x"]
        assert values.min() > 0.0
        assert np.issubdtype(split.target.dtype, np.complexfloating)
        assert np.all(np.isfinite(split.target))

    manifest = proof_dataset_manifest("arrhenius", points=24, seed=0, tolerance=1e-8)
    domains = {split["name"]: split["domain"] for split in manifest["splits"]}
    assert domains == {
        "train": [0.5, 3.0],
        "heldout": [0.6, 2.7],
        "extrapolation": [3.1, 4.2],
    }
    assert manifest["formula_id"] == "arrhenius"
    assert manifest["provenance"]["formula_id"] == "arrhenius"
    assert manifest["provenance"]["symbolic_expression"] == "exp(-0.8/x)"
    assert manifest["provenance"]["source_document"] == "sources/FOR_DEMO.md"
    assert manifest["provenance"]["normalized_dimensionless"] is True
    assert not (FORBIDDEN_RAW_KEYS & set(_walk_keys(manifest)))
