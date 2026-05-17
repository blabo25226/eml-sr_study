import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from eml_symbolic_regression.cli import build_parser, dataset_manifest_command
from eml_symbolic_regression.datasets import (
    expanded_dataset_manifest,
    expanded_dataset_specs,
    get_expanded_dataset,
    list_expanded_datasets,
    make_expanded_dataset_splits,
)
from eml_symbolic_regression.verify import metric_role_counts, verify_candidate


ROOT = Path(__file__).resolve().parents[1]
CLI_ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src")}


FORBIDDEN_RAW_KEYS = {"inputs", "target_values", "train_x", "heldout_x", "extrap_x"}
REQUIRED_CATEGORIES = {
    "noisy_synthetic_sweep",
    "parameter_identifiability_stress",
    "multivariable_case",
    "unit_aware_formulation",
    "real_dataset_path",
}


def _walk_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


def test_expanded_dataset_registry_covers_required_categories():
    specs = expanded_dataset_specs()

    assert set(list_expanded_datasets()) == set(specs)
    assert {spec.category for spec in specs.values()} == REQUIRED_CATEGORIES
    assert {spec.classification for spec in specs.values()} == {"synthetic", "semi_synthetic", "real"}
    assert specs["real_hubble_1929"].data_path is not None
    assert specs["real_hubble_1929"].data_path.exists()

    for spec in specs.values():
        assert spec.compatible_contracts == ("verifier", "benchmark_track", "baseline_harness")
        assert spec.generator
        assert spec.noise_policy["type"]
        assert spec.split_policy["roles"]["final_confirmation"] == "final_confirmation"
        assert spec.domain_constraints


def test_noisy_synthetic_manifest_records_required_contract_fields():
    manifest = expanded_dataset_manifest("noisy_beer_lambert_sweep", points=20, seed=3, tolerance=1e-8)

    assert manifest == expanded_dataset_manifest("noisy_beer_lambert_sweep", points=20, seed=3, tolerance=1e-8)
    assert manifest["schema"] == "eml.expanded_dataset_manifest.v1"
    assert manifest["dataset_id"] == "noisy_beer_lambert_sweep"
    assert manifest["formula_id"] == "beer_lambert"
    assert manifest["classification"] == "synthetic"
    assert manifest["category"] == "noisy_synthetic_sweep"
    assert manifest["noise_policy"] == {
        "type": "gaussian_relative",
        "relative_sigma": 0.01,
        "applies_to": ["train", "selection", "heldout"],
    }
    assert manifest["units"] == {"x": "dimensionless_absorbance_path", "target": "relative_intensity"}
    assert manifest["domain_constraints"]["x"]["max"] == 4.5
    assert "baseline_harness" in manifest["compatible_contracts"]
    assert len(manifest["manifest_sha256"]) == 64

    splits = {split["name"]: split for split in manifest["splits"]}
    assert set(splits) == {"train", "selection", "heldout", "extrapolation", "final_confirmation"}
    assert splits["train"]["role"] == "training"
    assert splits["selection"]["role"] == "selection"
    assert splits["heldout"]["role"] == "diagnostic"
    assert splits["extrapolation"]["role"] == "diagnostic"
    assert splits["final_confirmation"]["role"] == "final_confirmation"
    assert splits["train"]["count"] == 20
    assert splits["selection"]["count"] == 12
    assert splits["final_confirmation"]["count"] == 16
    assert all(len(split["target_sha256"]) == 64 for split in splits.values())
    assert all(len(digest) == 64 for split in splits.values() for digest in split["input_sha256"].values())
    assert not (FORBIDDEN_RAW_KEYS & set(_walk_keys(manifest)))


def test_manifest_seed_changes_signatures_without_changing_contract():
    seed_three = expanded_dataset_manifest("noisy_beer_lambert_sweep", points=20, seed=3)
    seed_four = expanded_dataset_manifest("noisy_beer_lambert_sweep", points=20, seed=4)

    assert seed_three["dataset_id"] == seed_four["dataset_id"]
    assert seed_three["variables"] == seed_four["variables"]
    assert seed_three["noise_policy"] == seed_four["noise_policy"]
    assert seed_three["split_policy"] == seed_four["split_policy"]
    assert seed_three["manifest_sha256"] != seed_four["manifest_sha256"]
    assert any(
        left["target_sha256"] != right["target_sha256"]
        or left["input_sha256"] != right["input_sha256"]
        for left, right in zip(seed_three["splits"], seed_four["splits"])
    )


def test_multivariable_dataset_splits_verify_against_clean_candidate():
    spec = get_expanded_dataset("multivariable_arrhenius_surface")
    splits = make_expanded_dataset_splits(spec.id, points=18, seed=1)

    assert spec.candidate is not None
    assert {split.name for split in splits} == {"train", "selection", "heldout", "extrapolation", "final_confirmation"}
    assert all(set(split.inputs) == {"a", "t"} for split in splits)
    assert metric_role_counts(splits) == {
        "training": 1,
        "selection": 1,
        "diagnostic": 2,
        "verifier": 0,
        "final_confirmation": 1,
    }

    report = verify_candidate(spec.candidate, splits, tolerance=1e-8)
    assert report.status == "verified_showcase"
    assert report.reason == "verified_non_eml_candidate"
    assert report.symbolic_status == "passed"
    assert report.dense_random_status == "passed"
    assert report.adversarial_status == "passed"


def test_unit_aware_dataset_manifest_records_units_and_domains():
    manifest = expanded_dataset_manifest("unit_aware_ohm_law", points=16, seed=2)

    assert manifest["classification"] == "semi_synthetic"
    assert manifest["category"] == "unit_aware_formulation"
    assert manifest["units"] == {
        "current_amp": "ampere",
        "resistance_ohm": "ohm",
        "target": "volt",
    }
    assert manifest["domain_constraints"]["current_amp"]["unit"] == "ampere"
    assert manifest["domain_constraints"]["resistance_ohm"]["unit"] == "ohm"
    assert all(split["target_unit"] == "volt" for split in manifest["splits"])


def test_real_hubble_manifest_uses_committed_observations_and_fixed_splits():
    manifest = expanded_dataset_manifest("real_hubble_1929", points=40, seed=9)

    assert manifest["classification"] == "real"
    assert manifest["category"] == "real_dataset_path"
    assert manifest["source_url"] == "https://www2.stat.duke.edu/courses/Fall03/sta113/Hubble.html"
    assert manifest["target_expression"] is None
    assert manifest["noise_policy"] == {"type": "observational", "known_noise_model": False}
    assert Path(manifest["data_path"]).exists()

    splits = {split["name"]: split for split in manifest["splits"]}
    assert set(splits) == {"train", "heldout", "final_confirmation"}
    assert splits["train"]["role"] == "training"
    assert splits["heldout"]["role"] == "diagnostic"
    assert splits["final_confirmation"]["role"] == "final_confirmation"
    assert {name: split["count"] for name, split in splits.items()} == {
        "train": 15,
        "heldout": 5,
        "final_confirmation": 4,
    }
    assert splits["train"]["domain"]["distance_mpc"] == [0.032, 2.0]

    loaded_splits = make_expanded_dataset_splits("real_hubble_1929", points=12, seed=0)
    assert [split.name for split in loaded_splits] == ["train", "heldout", "final_confirmation"]
    assert np.iscomplexobj(loaded_splits[0].target)
    assert len(loaded_splits[0].inputs["distance_mpc"]) == 15


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"points": 0}, "points must be positive"),
        ({"points": -1}, "points must be positive"),
        ({"tolerance": 0.0}, "tolerance must be positive"),
        ({"tolerance": -1e-8}, "tolerance must be positive"),
    ],
)
def test_expanded_dataset_manifest_rejects_invalid_sampling_contracts(kwargs, message):
    with pytest.raises(ValueError, match=message):
        expanded_dataset_manifest("noisy_beer_lambert_sweep", **kwargs)


def test_cli_dataset_manifest_writes_manifest(tmp_path):
    output = tmp_path / "manifest.json"
    args = build_parser().parse_args(
        [
            "dataset-manifest",
            "unit_aware_ohm_law",
            "--output",
            str(output),
            "--points",
            "16",
            "--seed",
            "2",
        ]
    )

    assert dataset_manifest_command(args) == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["schema"] == "eml.expanded_dataset_manifest.v1"
    assert payload["dataset_id"] == "unit_aware_ohm_law"
    assert payload["units"]["target"] == "volt"


def test_cli_list_datasets_exposes_expanded_registry():
    result = subprocess.run(
        [sys.executable, "-m", "eml_symbolic_regression.cli", "list-datasets"],
        check=True,
        capture_output=True,
        env=CLI_ENV,
        text=True,
    )

    assert "noisy_beer_lambert_sweep:" in result.stdout
    assert "[synthetic/noisy_synthetic_sweep]" in result.stdout
    assert "real_hubble_1929:" in result.stdout
    assert "[real/real_dataset_path]" in result.stdout
