import json

import pytest

from eml_symbolic_regression.benchmark import aggregate_evidence, load_suite, run_benchmark_suite


EXPECTED_SHALLOW_CASE_IDS = (
    "shallow-exp-blind",
    "shallow-log-blind",
    "shallow-radioactive-decay-blind",
    "shallow-beer-lambert-blind",
    "shallow-scaled-exp-growth-blind",
    "shallow-scaled-exp-fast-decay-blind",
)

FORBIDDEN_PROOF_EVIDENCE = {
    "catalog_verified",
    "compile_only_verified",
    "same_ast",
}


@pytest.fixture(scope="module")
def shallow_proof_result(tmp_path_factory):
    base = load_suite("v1.5-shallow-proof")
    suite = type(base)(base.id, base.description, base.cases, tmp_path_factory.mktemp("shallow-proof") / "artifacts")
    result = run_benchmark_suite(suite)
    return result, aggregate_evidence(result)


def test_v15_shallow_suite_recovers_but_uses_scaffolded_blind_training(shallow_proof_result):
    result, aggregate = shallow_proof_result

    assert [case.id for case in result.suite.cases] == list(EXPECTED_SHALLOW_CASE_IDS)
    assert len(result.results) == 18
    assert {run["case_id"] for run in aggregate["runs"]} == set(EXPECTED_SHALLOW_CASE_IDS)
    assert {"shallow-radioactive-decay-blind", "shallow-beer-lambert-blind"} <= {
        run["case_id"] for run in aggregate["runs"]
    }
    assert {
        "shallow-scaled-exp-growth-blind",
        "shallow-scaled-exp-fast-decay-blind",
    } <= {run["case_id"] for run in aggregate["runs"]}

    for item in result.results:
        artifact = json.loads(item.artifact_path.read_text(encoding="utf-8"))

        assert item.status == "recovered"
        assert artifact["status"] == "recovered"
        assert artifact["claim_status"] == "recovered"
        assert artifact["run"]["start_mode"] == "blind"
        assert artifact["training_mode"] == "blind_training"
        assert artifact["evidence_class"] == "scaffolded_blind_training_recovered"
        assert artifact["evidence_class"] not in FORBIDDEN_PROOF_EVIDENCE
        assert "compiled_eml" not in artifact
        assert "compiled_eml_verification" not in artifact
        assert "warm_start_eml" not in artifact
        assert "verification" not in artifact


def test_v15_shallow_scaffolded_threshold_accepts_scaffolded_recovery(shallow_proof_result):
    _, aggregate = shallow_proof_result
    threshold = aggregate["thresholds"][0]

    assert threshold["claim_id"] == "paper-shallow-scaffolded-recovery"
    assert threshold["threshold_policy_id"] == "scaffolded_bounded_100_percent"
    assert threshold["eligible"] == 18
    assert threshold["passed"] == 18
    assert threshold["failed"] == 0
    assert threshold["rate"] == 1.0
    assert threshold["status"] == "passed"
    assert threshold["evidence_classes"] == {"scaffolded_blind_training_recovered": 18}

    for run in aggregate["runs"]:
        metrics = run["metrics"]

        assert run["evidence_class"] == "scaffolded_blind_training_recovered"
        assert metrics["best_loss"] is not None
        assert metrics["post_snap_loss"] is not None
        assert metrics["snap_min_margin"] is not None
        assert metrics["snap_active_node_count"] is not None
        assert metrics["scaffold_source"] is not None
        assert metrics["verifier_status"] == "recovered"


def test_v15_shallow_pure_blind_suite_declares_measured_random_only_boundary():
    suite = load_suite("v1.5-shallow-pure-blind")
    runs = suite.expanded_runs()

    assert [case.id for case in suite.cases] == [
        "shallow-exp-pure-blind",
        "shallow-log-pure-blind",
        "shallow-radioactive-decay-pure-blind",
        "shallow-beer-lambert-pure-blind",
        "shallow-scaled-exp-growth-pure-blind",
        "shallow-scaled-exp-fast-decay-pure-blind",
    ]
    assert len(runs) == 18
    assert {run.claim_id for run in runs} == {"paper-shallow-blind-recovery"}
    assert {run.threshold_policy_id for run in runs} == {"measured_pure_blind_recovery"}
    assert all(run.optimizer.scaffold_initializers == () for run in runs)
