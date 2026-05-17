import json

from eml_symbolic_regression.datasets import get_demo
from eml_symbolic_regression.optimize import TrainingConfig, fit_eml_tree


def test_minimal_train_snap_verify_artifact_regression(tmp_path):
    spec = get_demo("exp")
    splits = spec.make_splits(points=12, seed=0)

    fit = fit_eml_tree(
        splits[0].inputs,
        splits[0].target,
        TrainingConfig(depth=1, variables=("x",), steps=2, restarts=1, seed=0),
        verification_splits=splits,
        tolerance=1e-8,
    )
    assert fit.verification is not None

    artifact = {
        "schema": "eml.evidence_regression.v1",
        "formula": spec.name,
        "optimizer": fit.manifest,
        "verification": fit.verification.as_dict(),
    }
    artifact_path = tmp_path / "evidence-regression.json"
    artifact_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    payload = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert payload["schema"] == "eml.evidence_regression.v1"
    assert payload["optimizer"]["selection"]["mode"] == "verifier_gated_exact_candidate_pool"
    assert payload["optimizer"]["selected_candidate"]["verification"]["status"] == "recovered"
    assert payload["optimizer"]["semantics_alignment"]["training_semantics_mode"] == "guarded"
    assert payload["optimizer"]["semantics_alignment"]["post_snap_mismatch"]["verifier_status"] == "recovered"
    assert payload["verification"]["status"] == "recovered"
    assert payload["verification"]["metric_roles"]["diagnostic"] >= 1
