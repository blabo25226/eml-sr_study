import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import sympy as sp
import torch

import eml_symbolic_regression.benchmark as benchmark_module
from eml_symbolic_regression.basin import BasinTrainingResult
from eml_symbolic_regression.benchmark import (
    BenchmarkCase,
    BenchmarkRepairConfig,
    BenchmarkRun,
    BenchmarkSuite,
    DatasetConfig,
    OptimizerBudget,
    RunFilter,
    builtin_suite,
    evidence_class_for_payload,
    execute_benchmark_run,
    run_benchmark_suite,
)
from eml_symbolic_regression.compiler import CompilerConfig, compile_and_validate
from eml_symbolic_regression.datasets import get_demo
from eml_symbolic_regression.expression import Const, Eml, Var
from eml_symbolic_regression.master_tree import SoftEMLTree
from eml_symbolic_regression.optimize import ExactCandidate, FitResult, TrainingConfig
from eml_symbolic_regression.repair import RepairConfig, RepairMove, RepairReport
from eml_symbolic_regression.verify import SplitResult, VerificationReport, verify_candidate
from eml_symbolic_regression.warm_start import WarmStartResult


ROOT = Path(__file__).resolve().parents[1]
CLI_ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src")}


def _verification_report(status: str) -> VerificationReport:
    return VerificationReport(
        status=status,
        candidate_kind="exact_eml",
        reason="verified" if status == "recovered" else "heldout_failed",
        split_results=[SplitResult("heldout", 0.0 if status == "recovered" else 1.0, 0.0, 0.0, status == "recovered")],
        high_precision_max_error=0.0 if status == "recovered" else 1.0,
        tolerance=1e-8,
    )


def _fit_from_slots(slots: dict[str, str], *, depth: int = 2) -> FitResult:
    tree = SoftEMLTree(depth, ("x",), (1.0,))
    for slot, choice in slots.items():
        node_path, side = slot.rsplit(".", 1)
        tree.set_slot(node_path, side, choice, strength=40.0)
    snap = tree.snap()
    return FitResult(
        status="snapped_candidate",
        best_loss=1.0,
        post_snap_loss=1.0,
        snap=snap,
        manifest={"schema": "eml.run_manifest.v1", "status": "snapped_candidate", "snap": snap.as_dict()},
    )


def _repairable_fit_for_exp() -> FitResult:
    tree = SoftEMLTree(1, ("x",), (1.0,))
    tree.set_slot("root", "right", "const:1", strength=40.0)
    with torch.no_grad():
        tree.root.left_logits.copy_(torch.tensor([2.0, 1.85], dtype=torch.float64))

    snap = tree.snap()
    selected = ExactCandidate(
        candidate_id="selected",
        attempt_index=0,
        random_restart=0,
        seed=0,
        attempt_kind="random",
        source="legacy_final_snap",
        checkpoint_index=None,
        hardening_step=None,
        global_step=0,
        temperature=0.25,
        best_fit_loss=1.0,
        pre_snap_loss=1.0,
        post_snap_loss=1.0,
        snap=snap,
        verification=_verification_report("failed"),
        slot_alternatives=tree.active_slot_alternatives(top_k=1),
    )
    manifest = {
        "schema": "eml.run_manifest.v1",
        "status": "snapped_candidate",
        "snap": snap.as_dict(),
        "candidates": [selected.as_dict()],
        "selection": {
            "mode": "verifier_gated_exact_candidate_pool",
            "candidate_count": 1,
            "selected_candidate_id": "selected",
            "fallback_candidate_id": "selected",
        },
        "selected_candidate": selected.as_dict(),
        "fallback_candidate": selected.as_dict(),
    }
    return FitResult(
        status="snapped_candidate",
        best_loss=1.0,
        post_snap_loss=1.0,
        snap=snap,
        manifest=manifest,
        verification=_verification_report("failed"),
        selected_candidate=selected,
        fallback_candidate=selected,
        candidates=(selected,),
    )


def _candidate_from_tree(
    tree: SoftEMLTree,
    *,
    candidate_id: str,
    source: str,
    slot_alternatives_top_k: int = 1,
) -> ExactCandidate:
    snap = tree.snap()
    return ExactCandidate(
        candidate_id=candidate_id,
        attempt_index=0,
        random_restart=0,
        seed=0,
        attempt_kind="random",
        source=source,
        checkpoint_index=None,
        hardening_step=None,
        global_step=0,
        temperature=0.25,
        best_fit_loss=1.0,
        pre_snap_loss=1.0,
        post_snap_loss=1.0,
        snap=snap,
        verification=_verification_report("failed"),
        slot_alternatives=() if slot_alternatives_top_k <= 0 else tree.active_slot_alternatives(top_k=slot_alternatives_top_k),
    )


def _candidate_pool_repairable_fit_for_exp() -> FitResult:
    selected_tree = SoftEMLTree(1, ("x",), (1.0,))
    selected_tree.set_slot("root", "left", "const:1", strength=40.0)
    selected_tree.set_slot("root", "right", "var:x", strength=40.0)
    selected = _candidate_from_tree(
        selected_tree,
        candidate_id="selected",
        source="legacy_final_snap",
        slot_alternatives_top_k=0,
    )

    fallback_tree = SoftEMLTree(1, ("x",), (1.0,))
    fallback_tree.set_slot("root", "right", "const:1", strength=40.0)
    with torch.no_grad():
        fallback_tree.root.left_logits.copy_(torch.tensor([2.0, 1.85], dtype=torch.float64))
    fallback = _candidate_from_tree(
        fallback_tree,
        candidate_id="fallback",
        source="hardening_checkpoint",
        slot_alternatives_top_k=1,
    )
    manifest = {
        "schema": "eml.run_manifest.v1",
        "status": "snapped_candidate",
        "snap": selected.snap.as_dict(),
        "candidates": [selected.as_dict(), fallback.as_dict()],
        "selection": {
            "mode": "verifier_gated_exact_candidate_pool",
            "candidate_count": 2,
            "selected_candidate_id": "selected",
            "fallback_candidate_id": "fallback",
        },
        "selected_candidate": selected.as_dict(),
        "fallback_candidate": fallback.as_dict(),
    }
    return FitResult(
        status="snapped_candidate",
        best_loss=1.0,
        post_snap_loss=1.0,
        snap=selected.snap,
        manifest=manifest,
        verification=_verification_report("failed"),
        selected_candidate=selected,
        fallback_candidate=fallback,
        candidates=(selected, fallback),
    )


def _not_repaired_report(*, original_status: str = "snapped_but_failed", return_kind: str = "snapped_but_failed") -> RepairReport:
    return RepairReport(
        status="not_repaired",
        original_status=original_status,
        return_kind=return_kind,
        moves_attempted=(),
        accepted_moves=(),
        repaired_expression=None,
        verification=None,
        reason="no_verified_slot_neighborhood",
        variant_count=1,
    )


def _repaired_report(
    expression,
    *,
    original_status: str = "snapped_but_failed",
    return_kind: str = "snapped_but_failed",
    source: str = "slot_alternative",
) -> RepairReport:
    move = RepairMove(
        kind="leaf_replacement",
        slot="root.left",
        before="const:1",
        after="var:x",
        source=source,
        accepted=True,
        verifier_status="recovered",
    )
    return RepairReport(
        status="repaired_candidate",
        original_status=original_status,
        return_kind=return_kind,
        moves_attempted=(move,),
        accepted_moves=(move,),
        repaired_expression=expression,
        verification=_verification_report("recovered"),
        reason="verified_slot_neighborhood",
        variant_count=1,
    )


def test_runner_executes_catalog_compile_blind_and_warm_start(tmp_path):
    suite = type(builtin_suite("smoke"))(
        "smoke",
        "test smoke",
        builtin_suite("smoke").cases,
        tmp_path / "artifacts",
    )

    result = run_benchmark_suite(suite)
    payload = result.as_dict()

    assert payload["counts"]["total"] == 3
    assert all(item.artifact_path.exists() for item in result.results)
    statuses = {item.run.case_id: item.status for item in result.results}
    assert statuses["exp-blind"] in {"recovered", "snapped_but_failed", "failed"}
    assert statuses["beer-warm"] in {"same_ast_return", "verified_equivalent_ast", "snapped_but_failed"}
    assert statuses["planck-diagnostic"] == "unsupported"
    for item in result.results:
        artifact = json.loads(item.artifact_path.read_text(encoding="utf-8"))
        assert artifact["claim_id"] is None
        assert artifact["claim_class"] is None
        assert artifact["threshold"] is None
        assert artifact["training_mode"] == item.run.training_mode
        assert artifact["evidence_class"] == evidence_class_for_payload(artifact)
        assert artifact["dataset"] == item.run.dataset.as_dict()
        assert artifact["dataset_manifest"]["schema"] == "eml.proof_dataset_manifest.v1"
        assert artifact["budget"] == item.run.optimizer.as_dict()
        assert artifact["provenance"]["symbolic_expression"]
        assert artifact["provenance"]["source_document"].startswith("sources/")


def test_runner_executes_operator_family_smoke_matrix(tmp_path):
    base = builtin_suite("v1.7-family-smoke")
    suite = type(base)(base.id, base.description, base.cases, tmp_path / "artifacts")

    result = run_benchmark_suite(
        suite,
        run_filter=RunFilter(case_ids=("exp-blind-ceml2", "exp-blind-zeml8-4"), seeds=(0,)),
    )
    aggregate = benchmark_module.aggregate_evidence(result)
    aggregate_runs = {item["run_id"]: item for item in aggregate["runs"]}
    expected_exclusions = [
        "exp:centered_family_same_family_witness_missing",
        "log:centered_family_same_family_witness_missing",
        "scaled_exp:centered_family_same_family_witness_missing",
    ]

    assert len(result.results) == 2
    for item in result.results:
        artifact = json.loads(item.artifact_path.read_text(encoding="utf-8"))
        assert artifact["budget"] == item.run.optimizer.as_dict()
        assert artifact["budget"]["operator_family"]["label"] in {"CEML_2", "ZEML_8"}
        assert artifact["budget"]["scaffold_initializers"] == []
        assert artifact["budget"]["scaffold_exclusions"] == expected_exclusions
        assert artifact["trained_eml_candidate"]["config"]["operator_family"]["label"] in {"CEML_2", "ZEML_8"}
        assert artifact["trained_eml_candidate"]["config"]["scaffold_initializers"] == []
        assert artifact["trained_eml_candidate"]["scaffold_exclusions"] == expected_exclusions
        assert all(
            not restart["attempt_kind"].startswith("scaffold_")
            for restart in artifact["trained_eml_candidate"]["restarts"]
        )
        assert artifact["metrics"]["operator_family"] in {"CEML_2", "ZEML_8"}
        assert artifact["metrics"]["scaffold_exclusions"] == expected_exclusions
        assert aggregate_runs[item.run.run_id]["metrics"]["scaffold_exclusions"] == expected_exclusions
        if item.run.case_id == "exp-blind-zeml8-4":
            assert artifact["metrics"]["operator_schedule"] == "ZEML_8 -> ZEML_4"


def test_centered_warm_start_fails_closed_with_operator_metadata(tmp_path):
    base = builtin_suite("v1.8-family-smoke")
    suite = type(base)(base.id, base.description, base.cases, tmp_path / "artifacts")

    result = run_benchmark_suite(
        suite,
        run_filter=RunFilter(case_ids=("beer-warm-ceml2",), seeds=(0,)),
    )
    artifact = json.loads(result.results[0].artifact_path.read_text(encoding="utf-8"))

    assert result.results[0].status == "unsupported"
    assert artifact["warm_start_eml"]["reason"] == "centered_family_same_family_seed_missing"
    assert artifact["warm_start_eml"]["unsupported_class"] == "missing_same_family_exact_seed"
    assert artifact["warm_start_eml"]["counts_in_denominator"] is True
    assert artifact["warm_start_eml"]["operator_family"]["label"] == "CEML_2"
    assert artifact["metrics"]["operator_family"] == "CEML_2"
    assert artifact["metrics"]["unsupported_reason"] == "centered_family_same_family_seed_missing"


def test_centered_perturbed_tree_unsupported_reason_survives_aggregate(tmp_path):
    base = builtin_suite("v1.8-family-basin")
    suite = type(base)(base.id, base.description, base.cases, tmp_path / "artifacts")

    result = run_benchmark_suite(
        suite,
        run_filter=RunFilter(case_ids=("basin-depth1-perturbed-ceml2",), seeds=(0,)),
    )
    artifact = json.loads(result.results[0].artifact_path.read_text(encoding="utf-8"))
    aggregate = benchmark_module.aggregate_evidence(result)

    assert result.results[0].status == "unsupported"
    assert artifact["perturbed_true_tree"]["reason"] == "centered_family_same_family_seed_missing"
    assert artifact["perturbed_true_tree"]["unsupported_class"] == "missing_same_family_exact_seed"
    assert artifact["perturbed_true_tree"]["operator_family"]["label"] == "CEML_2"
    assert artifact["metrics"]["unsupported_reason"] == "centered_family_same_family_seed_missing"
    assert aggregate["runs"][0]["reason"] == "centered_family_same_family_seed_missing"


def test_runner_filter_executes_subset(tmp_path):
    base = builtin_suite("v1.2-evidence")
    suite = type(base)(base.id, base.description, base.cases, tmp_path / "artifacts")

    result = run_benchmark_suite(suite, run_filter=RunFilter(case_ids=("beer-perturbation-sweep",), seeds=(0,)))

    assert len(result.results) == 3
    assert {item.run.perturbation_noise for item in result.results} == {0.0, 5.0, 35.0}


def test_proof_aware_run_artifact_includes_threshold_dataset_and_provenance(tmp_path):
    case = BenchmarkCase.from_mapping(
        {
            "id": "shallow-exp-blind",
            "formula": "exp",
            "start_mode": "blind",
            "seeds": [0],
            "dataset": {"points": 12},
            "optimizer": {"depth": 1, "steps": 6, "restarts": 1},
            "claim_id": "paper-shallow-scaffolded-recovery",
            "threshold_policy_id": "scaffolded_bounded_100_percent",
            "training_mode": "blind_training",
        },
        path="cases[0]",
    )
    suite = BenchmarkSuite("v1.5-shallow-proof", "cheap proof-aware runner smoke", (case,), tmp_path / "artifacts")

    result = run_benchmark_suite(suite)
    artifact = json.loads(result.results[0].artifact_path.read_text(encoding="utf-8"))

    assert artifact["claim_id"] == "paper-shallow-scaffolded-recovery"
    assert artifact["claim_class"] == "scaffolded_training_proof"
    assert artifact["training_mode"] == "blind_training"
    assert artifact["threshold"]["id"] == "scaffolded_bounded_100_percent"
    assert artifact["dataset_manifest"]["schema"] == "eml.proof_dataset_manifest.v1"
    assert artifact["dataset_manifest"]["formula_id"] == "exp"
    assert artifact["dataset_manifest"]["points"] == 12
    assert artifact["budget"]["depth"] == 1
    assert artifact["provenance"]["symbolic_expression"] == "exp(x)"
    assert artifact["provenance"]["source_document"] == "sources/paper.pdf"
    assert artifact["evidence_class"] == evidence_class_for_payload(artifact)


def test_shallow_beer_lambert_blind_run_artifact_exposes_scaled_scaffold_diagnostics(tmp_path):
    base = builtin_suite("v1.5-shallow-proof")
    suite = type(base)(base.id, base.description, base.cases, tmp_path / "artifacts")

    result = run_benchmark_suite(
        suite,
        run_filter=RunFilter(case_ids=("shallow-beer-lambert-blind",), seeds=(0,)),
    )
    artifact = json.loads(result.results[0].artifact_path.read_text(encoding="utf-8"))
    candidate = artifact["trained_eml_candidate"]
    initialization = candidate["best_restart"]["initialization"]
    metrics = artifact["metrics"]

    assert result.results[0].status == "recovered"
    assert artifact["status"] == "recovered"
    assert artifact["budget"]["constants"] == ["-0.8"]
    assert artifact["evidence_class"] == "scaffolded_blind_training_recovered"
    assert candidate["scaffold_exclusions"] == []
    assert initialization["kind"] == "scaffold_scaled_exp"
    assert initialization["strategy"] == "paper_scaled_exponential_family"
    assert initialization["coefficient"] == "-0.8"
    assert initialization["constant_label"] == "const:-0.8"
    assert metrics["scaffold_source"] == "scaffold_scaled_exp"
    assert metrics["scaffold_strategy"] == "paper_scaled_exponential_family"
    assert metrics["scaffold_coefficient"] == "-0.8"
    assert metrics["best_loss"] is not None
    assert metrics["post_snap_loss"] <= 1e-20
    assert metrics["snap_min_margin"] > 0.99
    assert metrics["snap_active_node_count"] == 19
    assert metrics["verifier_status"] == "recovered"
    assert candidate["selection"]["mode"] == "verifier_gated_exact_candidate_pool"
    assert candidate["selected_candidate"]["candidate_id"] == candidate["selection"]["selected_candidate_id"]
    assert candidate["fallback_candidate"]["candidate_id"] == candidate["selection"]["fallback_candidate_id"]
    assert candidate["fallback_candidate"]["source"] == "legacy_final_snap"
    assert metrics["selected_candidate_id"] == candidate["selection"]["selected_candidate_id"]
    assert metrics["fallback_candidate_id"] == candidate["selection"]["fallback_candidate_id"]
    assert metrics["selection_mode"] == "verifier_gated_exact_candidate_pool"
    assert metrics["candidate_pool_size"] == candidate["selection"]["candidate_count"]


def test_runner_writes_execution_error_if_payload_construction_fails(tmp_path):
    run = BenchmarkRun(
        suite_id="direct",
        case_id="orphan-threshold",
        formula="exp",
        start_mode="blind",
        seed=0,
        perturbation_noise=0.0,
        dataset=DatasetConfig(points=12),
        optimizer=OptimizerBudget(depth=1, steps=1, restarts=1),
        artifact_path=tmp_path / "orphan-threshold.json",
        threshold_policy_id="missing-policy",
        training_mode="blind_training",
    )

    result = execute_benchmark_run(run)
    artifact = json.loads(result.artifact_path.read_text(encoding="utf-8"))

    assert result.status == "execution_error"
    assert artifact["status"] == "execution_error"
    assert artifact["error"]["type"] == "ProofContractError"
    assert artifact["threshold"] is None
    assert artifact["evidence_class"] == "execution_failure"


def test_evidence_class_for_payload_is_derived_and_covers_reserved_repair():
    assert evidence_class_for_payload({"evidence_class": "blind_training_recovered", "status": "unsupported"}) == "unsupported"
    assert evidence_class_for_payload({"status": "repaired_candidate"}) == "repaired_candidate"
    assert evidence_class_for_payload({"status": "failed", "repair_status": "repaired"}) == "repaired_candidate"
    assert evidence_class_for_payload({"status": "recovered", "claim_status": "recovered", "run": {"start_mode": "catalog"}}) == "catalog_verified"
    assert evidence_class_for_payload({"status": "recovered", "claim_status": "recovered", "run": {"start_mode": "compile"}}) == "compile_only_verified"
    assert (
        evidence_class_for_payload(
            {
                "status": "recovered",
                "claim_status": "recovered",
                "training_mode": "blind_training",
                "run": {"start_mode": "blind"},
            }
        )
        == "blind_training_recovered"
    )
    assert (
        evidence_class_for_payload(
            {
                "status": "recovered",
                "claim_status": "recovered",
                "training_mode": "blind_training",
                "run": {"start_mode": "blind"},
                "trained_eml_candidate": {"best_restart": {"attempt_kind": "scaffold_scaled_exp"}},
            }
        )
        == "scaffolded_blind_training_recovered"
    )
    assert (
        evidence_class_for_payload(
            {
                "status": "same_ast_return",
                "claim_status": "same_ast_return",
                "training_mode": "compiler_warm_start_training",
                "run": {"start_mode": "warm_start"},
            }
        )
        == "same_ast"
    )
    assert (
        evidence_class_for_payload(
            {
                "status": "recovered",
                "claim_status": "recovered",
                "return_kind": "same_ast_return",
                "raw_status": "recovered",
                "training_mode": "perturbed_true_tree_training",
                "run": {"start_mode": "perturbed_tree", "perturbation_noise": 0.05},
            }
        )
        == "perturbed_true_tree_recovered"
    )
    assert (
        evidence_class_for_payload(
            {
                "status": "recovered",
                "claim_status": "recovered",
                "return_kind": "same_ast_return",
                "training_mode": "perturbed_true_tree_training",
                "run": {"start_mode": "warm_start", "perturbation_noise": 0.05},
            }
        )
        != "perturbed_true_tree_recovered"
    )


def test_perturbed_tree_runner_records_return_kind_and_raw_status(tmp_path):
    case = BenchmarkCase.from_mapping(
        {
            "id": "basin-depth1-perturbed",
            "formula": "basin_depth1_exp",
            "start_mode": "perturbed_tree",
            "seeds": [0],
            "perturbation_noise": [0.05],
            "dataset": {"points": 12},
            "optimizer": {"depth": 1, "warm_steps": 1, "warm_restarts": 1},
            "training_mode": "perturbed_true_tree_training",
        },
        path="cases[0]",
    )
    suite = BenchmarkSuite("proof-perturbed-basin", "cheap perturbed-tree smoke", (case,), tmp_path / "artifacts")

    result = run_benchmark_suite(suite)
    artifact = json.loads(result.results[0].artifact_path.read_text(encoding="utf-8"))

    assert result.results[0].status == "recovered"
    assert artifact["status"] == "recovered"
    assert artifact["run"]["start_mode"] == "perturbed_tree"
    assert artifact["training_mode"] == "perturbed_true_tree_training"
    assert artifact["return_kind"] == "same_ast_return"
    assert artifact["raw_status"] == "recovered"
    assert artifact["claim_status"] == "recovered"
    assert artifact["evidence_class"] == "perturbed_true_tree_recovered"
    assert artifact["stage_statuses"]["perturbed_true_tree_attempt"] == "recovered"
    assert artifact["perturbed_true_tree"]["schema"] == "eml.perturbed_true_tree_manifest.v1"
    assert artifact["perturbed_true_tree"]["optimizer"]["best_restart"]["initialization"]["kind"] == "perturbed_true_tree"
    assert artifact["metrics"]["verifier_status"] == "recovered"


def test_perturbed_tree_repair_promotes_artifact_without_overwriting_raw(monkeypatch, tmp_path):
    target_expr = Eml(Eml(Var("x"), Const(1.0)), Const(1.0))
    raw_fit = _fit_from_slots({"root.left": "var:x", "root.right": "const:1"})
    embedding = SoftEMLTree(2, ("x",), (1.0,)).embed_expr(target_expr)
    raw_verification = _verification_report("failed")

    def fake_fit_perturbed_true_tree(*args, **kwargs):
        return BasinTrainingResult(
            status="snapped_but_failed",
            return_kind="snapped_but_failed",
            fit=raw_fit,
            embedding=embedding,
            verification=raw_verification,
            manifest={
                "schema": "eml.perturbed_true_tree_manifest.v1",
                "status": "snapped_but_failed",
                "raw_status": "snapped_but_failed",
                "return_kind": "snapped_but_failed",
                "optimizer": raw_fit.manifest,
                "verification": raw_verification.as_dict(),
            },
        )

    monkeypatch.setattr(benchmark_module, "fit_perturbed_true_tree", fake_fit_perturbed_true_tree)
    run = BenchmarkRun(
        suite_id="proof-perturbed-basin",
        case_id="basin-depth2-perturbed",
        formula="basin_depth2_exp_exp",
        start_mode="perturbed_tree",
        seed=0,
        perturbation_noise=0.05,
        dataset=DatasetConfig(points=12),
        optimizer=OptimizerBudget(depth=2, warm_steps=1, warm_restarts=1),
        artifact_path=tmp_path / "repaired-perturbed.json",
        claim_id="paper-perturbed-true-tree-basin",
        threshold_policy_id="bounded_100_percent",
        training_mode="perturbed_true_tree_training",
    )

    result = execute_benchmark_run(run)
    artifact = json.loads(result.artifact_path.read_text(encoding="utf-8"))

    assert result.status == "repaired_candidate"
    assert artifact["status"] == "repaired_candidate"
    assert artifact["claim_status"] == "recovered"
    assert artifact["return_kind"] == "snapped_but_failed"
    assert artifact["raw_status"] == "snapped_but_failed"
    assert artifact["repair_status"] == "repaired"
    assert artifact["evidence_class"] == "repaired_candidate"
    assert artifact["perturbed_true_tree"]["status"] == "snapped_but_failed"
    assert artifact["stage_statuses"]["perturbed_true_tree_attempt"] == "snapped_but_failed"
    assert artifact["stage_statuses"]["local_repair"] == "repaired_candidate"
    assert artifact["repair"]["status"] == "repaired_candidate"
    assert artifact["repair"]["verification"]["status"] == "recovered"
    assert artifact["repair"]["accepted_moves"][0]["source"] == "embedded_target_slot"
    assert artifact["metrics"]["repair_status"] == "repaired"
    assert artifact["metrics"]["repair_move_count"] >= 1
    assert artifact["metrics"]["repair_accepted_move_count"] >= 1
    assert artifact["metrics"]["repair_verifier_status"] == "recovered"


@pytest.mark.parametrize("start_mode", ["blind", "warm_start", "perturbed_tree"])
def test_expanded_repair_config_routes_to_target_free_cleanup(monkeypatch, tmp_path, start_mode):
    captured_configs = []

    def fake_cleanup_failed_candidate(*args, **kwargs):
        captured_configs.append(kwargs.get("config"))
        return _not_repaired_report(original_status=kwargs["original_status"], return_kind=kwargs["return_kind"])

    monkeypatch.setattr(benchmark_module, "cleanup_failed_candidate", fake_cleanup_failed_candidate)
    monkeypatch.setattr(
        benchmark_module,
        "repair_perturbed_candidate",
        lambda *args, **kwargs: _not_repaired_report(original_status=kwargs["original_status"], return_kind=kwargs["return_kind"]),
    )

    if start_mode == "blind":
        monkeypatch.setattr(benchmark_module, "fit_eml_tree", lambda *args, **kwargs: _repairable_fit_for_exp())
        run = BenchmarkRun(
            suite_id="phase52",
            case_id="blind-expanded-repair",
            formula="exp",
            start_mode="blind",
            seed=0,
            perturbation_noise=0.0,
            dataset=DatasetConfig(points=12),
            optimizer=OptimizerBudget(depth=1, steps=1, restarts=1, refit_steps=0),
            artifact_path=tmp_path / "blind-expanded-repair.json",
            training_mode="blind_training",
            repair=BenchmarkRepairConfig(preset="expanded_candidate_pool"),
        )
    elif start_mode == "warm_start":
        fit = _repairable_fit_for_exp()
        warm_tree = SoftEMLTree(1, ("x",), (1.0,))
        embedding = warm_tree.embed_expr(Eml(Var("x"), Const(1.0)))

        def fake_warm_start(*args, **kwargs):
            return WarmStartResult(
                status="snapped_but_failed",
                fit=fit,
                embedding=embedding,
                verification=_verification_report("failed"),
                manifest={
                    "schema": "eml.warm_start_manifest.v1",
                    "status": "snapped_but_failed",
                    "optimizer": fit.manifest,
                    "verification": _verification_report("failed").as_dict(),
                    "diagnosis": {"status": "snapped_but_failed", "mechanism": "snap_instability"},
                },
            )

        monkeypatch.setattr(benchmark_module, "fit_warm_started_eml_tree", fake_warm_start)
        run = BenchmarkRun(
            suite_id="phase52",
            case_id="warm-expanded-repair",
            formula="exp",
            start_mode="warm_start",
            seed=0,
            perturbation_noise=0.0,
            dataset=DatasetConfig(points=12),
            optimizer=OptimizerBudget(depth=1, steps=1, restarts=1, warm_steps=1, warm_restarts=1, refit_steps=0),
            artifact_path=tmp_path / "warm-expanded-repair.json",
            training_mode="compiler_warm_start_training",
            repair=BenchmarkRepairConfig(preset="expanded_candidate_pool"),
        )
    else:
        target_expr = Eml(Eml(Var("x"), Const(1.0)), Const(1.0))
        raw_fit = _fit_from_slots({"root.left": "var:x", "root.right": "const:1"})
        embedding = SoftEMLTree(2, ("x",), (1.0,)).embed_expr(target_expr)
        raw_verification = _verification_report("failed")

        def fake_fit_perturbed_true_tree(*args, **kwargs):
            return BasinTrainingResult(
                status="snapped_but_failed",
                return_kind="snapped_but_failed",
                fit=raw_fit,
                embedding=embedding,
                verification=raw_verification,
                manifest={
                    "schema": "eml.perturbed_true_tree_manifest.v1",
                    "status": "snapped_but_failed",
                    "raw_status": "snapped_but_failed",
                    "return_kind": "snapped_but_failed",
                    "optimizer": raw_fit.manifest,
                    "verification": raw_verification.as_dict(),
                },
            )

        monkeypatch.setattr(benchmark_module, "fit_perturbed_true_tree", fake_fit_perturbed_true_tree)
        run = BenchmarkRun(
            suite_id="phase52",
            case_id="perturbed-expanded-repair",
            formula="basin_depth2_exp_exp",
            start_mode="perturbed_tree",
            seed=0,
            perturbation_noise=0.05,
            dataset=DatasetConfig(points=12),
            optimizer=OptimizerBudget(depth=2, warm_steps=1, warm_restarts=1, refit_steps=0),
            artifact_path=tmp_path / "perturbed-expanded-repair.json",
            training_mode="perturbed_true_tree_training",
            repair=BenchmarkRepairConfig(preset="expanded_candidate_pool"),
        )

    execute_benchmark_run(run)

    assert captured_configs == [RepairConfig.expanded_candidate_pool()]


def test_candidate_pool_cleanup_promotes_artifact_without_mutating_selected_or_fallback(monkeypatch, tmp_path):
    fit = _candidate_pool_repairable_fit_for_exp()
    monkeypatch.setattr(benchmark_module, "fit_eml_tree", lambda *args, **kwargs: fit)
    run = BenchmarkRun(
        suite_id="phase52",
        case_id="candidate-pool-cleanup",
        formula="exp",
        start_mode="blind",
        seed=0,
        perturbation_noise=0.0,
        dataset=DatasetConfig(points=12),
        optimizer=OptimizerBudget(depth=1, steps=1, restarts=1, refit_steps=0),
        artifact_path=tmp_path / "candidate-pool-cleanup.json",
        training_mode="blind_training",
        repair=BenchmarkRepairConfig(preset="expanded_candidate_pool"),
    )

    result = execute_benchmark_run(run)
    artifact = json.loads(result.artifact_path.read_text(encoding="utf-8"))
    candidate = artifact["trained_eml_candidate"]

    assert result.status == "repaired_candidate"
    assert artifact["status"] == "repaired_candidate"
    assert artifact["repair_status"] == "repaired"
    assert artifact["claim_status"] == "recovered"
    assert artifact["evidence_class"] == "repaired_candidate"
    assert candidate["selected_candidate"]["candidate_id"] == "selected"
    assert candidate["fallback_candidate"]["candidate_id"] == "fallback"
    assert candidate["selection"]["selected_candidate_id"] == "selected"
    assert candidate["selection"]["fallback_candidate_id"] == "fallback"
    assert artifact["repair"]["accepted_candidate_id"] == "fallback"
    assert artifact["repair"]["accepted_candidate_source"] == "hardening_checkpoint"
    assert artifact["repair"]["accepted_candidate_root_source"] == "fallback"
    assert artifact["repair"]["accepted_moves"][0]["candidate_id"] == "fallback"
    assert artifact["repair"]["accepted_moves"][0]["candidate_root_source"] == "fallback"
    assert artifact["metrics"]["repair_candidate_root_count"] == 2
    assert artifact["metrics"]["repair_deduped_variant_count"] >= 1
    assert artifact["metrics"]["repair_accepted_candidate_id"] == "fallback"
    assert artifact["metrics"]["repair_accepted_candidate_source"] == "hardening_checkpoint"
    assert artifact["metrics"]["repair_accepted_candidate_root_source"] == "fallback"


def test_perturbed_target_aware_repair_still_runs_after_expanded_target_free_miss(monkeypatch, tmp_path):
    calls = []
    target_expr = Eml(Eml(Var("x"), Const(1.0)), Const(1.0))
    raw_fit = _fit_from_slots({"root.left": "var:x", "root.right": "const:1"})
    embedding = SoftEMLTree(2, ("x",), (1.0,)).embed_expr(target_expr)
    raw_verification = _verification_report("failed")

    def fake_fit_perturbed_true_tree(*args, **kwargs):
        return BasinTrainingResult(
            status="snapped_but_failed",
            return_kind="snapped_but_failed",
            fit=raw_fit,
            embedding=embedding,
            verification=raw_verification,
            manifest={
                "schema": "eml.perturbed_true_tree_manifest.v1",
                "status": "snapped_but_failed",
                "raw_status": "snapped_but_failed",
                "return_kind": "snapped_but_failed",
                "optimizer": raw_fit.manifest,
                "verification": raw_verification.as_dict(),
            },
        )

    def fake_cleanup_failed_candidate(*args, **kwargs):
        calls.append(("target_free", kwargs.get("config")))
        return _not_repaired_report(original_status=kwargs["original_status"], return_kind=kwargs["return_kind"])

    def fake_repair_perturbed_candidate(*args, **kwargs):
        calls.append(("target_aware", kwargs.get("config")))
        return _repaired_report(
            target_expr,
            original_status=kwargs["original_status"],
            return_kind=kwargs["return_kind"],
            source="embedded_target_slot",
        )

    monkeypatch.setattr(benchmark_module, "fit_perturbed_true_tree", fake_fit_perturbed_true_tree)
    monkeypatch.setattr(benchmark_module, "cleanup_failed_candidate", fake_cleanup_failed_candidate)
    monkeypatch.setattr(benchmark_module, "repair_perturbed_candidate", fake_repair_perturbed_candidate)
    run = BenchmarkRun(
        suite_id="phase52",
        case_id="perturbed-expanded-repair-fallback",
        formula="basin_depth2_exp_exp",
        start_mode="perturbed_tree",
        seed=0,
        perturbation_noise=0.05,
        dataset=DatasetConfig(points=12),
        optimizer=OptimizerBudget(depth=2, warm_steps=1, warm_restarts=1, refit_steps=0),
        artifact_path=tmp_path / "perturbed-expanded-repair-fallback.json",
        training_mode="perturbed_true_tree_training",
        repair=BenchmarkRepairConfig(preset="expanded_candidate_pool"),
    )

    result = execute_benchmark_run(run)
    artifact = json.loads(result.artifact_path.read_text(encoding="utf-8"))

    assert result.status == "repaired_candidate"
    assert artifact["repair_status"] == "repaired"
    assert artifact["repair"]["accepted_moves"][0]["source"] == "embedded_target_slot"
    assert calls == [
        ("target_free", RepairConfig.expanded_candidate_pool()),
        ("target_aware", None),
    ]


@pytest.mark.parametrize("start_mode", ["blind", "warm_start"])
def test_target_free_cleanup_promotes_blind_and_warm_start_artifacts(monkeypatch, tmp_path, start_mode):
    fit = _repairable_fit_for_exp()
    run = BenchmarkRun(
        suite_id="phase35",
        case_id=f"{start_mode}-cleanup",
        formula="exp",
        start_mode=start_mode,
        seed=0,
        perturbation_noise=0.0,
        dataset=DatasetConfig(points=12),
        optimizer=OptimizerBudget(depth=1, steps=1, restarts=1, warm_steps=1, warm_restarts=1),
        artifact_path=tmp_path / f"{start_mode}-cleanup.json",
        training_mode="blind_training" if start_mode == "blind" else "compiler_warm_start_training",
    )

    if start_mode == "blind":
        monkeypatch.setattr(benchmark_module, "fit_eml_tree", lambda *args, **kwargs: fit)
    else:
        warm_tree = SoftEMLTree(1, ("x",), (1.0,))
        embedding = warm_tree.embed_expr(Eml(Var("x"), Const(1.0)))

        def fake_warm_start(*args, **kwargs):
            return WarmStartResult(
                status="snapped_but_failed",
                fit=fit,
                embedding=embedding,
                verification=_verification_report("failed"),
                manifest={
                    "schema": "eml.warm_start_manifest.v1",
                    "status": "snapped_but_failed",
                    "optimizer": fit.manifest,
                    "verification": _verification_report("failed").as_dict(),
                    "diagnosis": {"status": "snapped_but_failed", "mechanism": "snap_instability"},
                },
            )

        monkeypatch.setattr(benchmark_module, "fit_warm_started_eml_tree", fake_warm_start)

    result = execute_benchmark_run(run)
    artifact = json.loads(result.artifact_path.read_text(encoding="utf-8"))
    candidate = artifact["trained_eml_candidate"] if start_mode == "blind" else artifact["warm_start_eml"]["optimizer"]

    assert result.status == "repaired_candidate"
    assert artifact["status"] == "repaired_candidate"
    assert artifact["claim_status"] == "recovered"
    assert artifact["repair_status"] == "repaired"
    assert artifact["repair"]["status"] == "repaired_candidate"
    assert artifact["repair"]["accepted_moves"][0]["source"] == "slot_alternative"
    assert candidate["selected_candidate"]["candidate_id"] == "selected"
    assert candidate["fallback_candidate"]["candidate_id"] == "selected"
    assert artifact["metrics"]["repair_status"] == "repaired"
    assert artifact["metrics"]["repair_accepted_move_count"] >= 1


def test_post_snap_refit_accepts_improved_literal_constant_candidate():
    spec = get_demo("beer_lambert")
    splits = spec.make_splits(points=24, seed=0)
    x = sp.Symbol(spec.variable)
    compiled = compile_and_validate(
        sp.exp(sp.Float("-0.7") * x),
        CompilerConfig(variables=(spec.variable,), max_depth=16, max_nodes=256),
        {spec.variable: splits[0].inputs[spec.variable]},
    )
    verification = verify_candidate(compiled.expression, splits, tolerance=1e-8)
    config = TrainingConfig(
        depth=compiled.metadata.depth,
        variables=(spec.variable,),
        constants=compiled.metadata.constants,
        steps=1,
        restarts=1,
        seed=0,
        refit_steps=60,
        refit_lr=0.05,
    )

    refit = benchmark_module._run_post_snap_refit(
        compiled.expression,
        verification=verification,
        source="test_candidate",
        training_split=splits[0],
        verification_splits=splits,
        config=config,
        tolerance=1e-8,
    )

    assert verification.status == "failed"
    assert refit.status == "accepted"
    assert refit.accepted is True
    assert refit.verification is not None
    assert refit.verification.status == "failed"
    assert refit.payload["selected_candidate"] == "post_refit"
    assert refit.payload["pre_refit_candidate"]["metrics"]["verifier_status"] == "failed"
    assert refit.payload["post_refit_candidate"]["metrics"]["verifier_status"] == "failed"
    assert refit.payload["post_refit_candidate"]["post_snap_loss"] < refit.payload["pre_refit_candidate"]["post_snap_loss"]
    assert any(item["changed"] for item in refit.payload["refittable_constants"])


def test_exact_candidate_payload_keeps_inline_symbolic_expression_for_small_ast(monkeypatch):
    expression = Eml(Var("x"), Const(1.0))
    monkeypatch.setattr(benchmark_module, "SYMBOLIC_INLINE_NODE_BUDGET", 255)

    payload = benchmark_module._exact_candidate_payload(
        expression,
        verification=None,
        source="test_candidate",
        post_snap_loss=0.0,
    )

    assert payload["symbolic_expression"] == "exp(x)"
    assert payload["symbolic_expression_render"]["status"] == "rendered"
    assert payload["symbolic_expression_render"]["mode"] == "inline"


def test_exact_candidate_payload_omits_symbolic_expression_when_guard_times_out(monkeypatch):
    expression: Eml | Var | Const = Eml(Var("x"), Const(1.0))
    for _ in range(130):
        expression = Eml(expression, Const(1.0))

    monkeypatch.setattr(
        benchmark_module,
        "_render_symbolic_expression_subprocess",
        lambda document, *, timeout_seconds: {
            "status": "omitted_timeout",
            "mode": "subprocess",
            "timeout_seconds": timeout_seconds,
            "detail": "timed out in test",
        },
    )

    payload = benchmark_module._exact_candidate_payload(
        expression,
        verification=None,
        source="test_candidate",
        post_snap_loss=0.0,
    )

    assert payload["symbolic_expression"] is None
    assert payload["symbolic_expression_render"]["status"] == "omitted_timeout"
    assert payload["symbolic_expression_render"]["mode"] == "subprocess"
    assert payload["ast"]["metadata"]["node_count"] == expression.node_count()


def test_depth_curve_runner_records_blind_failure_and_perturbed_recovery(tmp_path):
    base = builtin_suite("proof-depth-curve")
    suite = type(base)(base.id, base.description, base.cases, tmp_path / "artifacts")

    result = run_benchmark_suite(
        suite,
        run_filter=RunFilter(case_ids=("depth-4-blind", "depth-4-perturbed"), seeds=(0,)),
    )
    artifacts = {
        item.run.case_id: json.loads(item.artifact_path.read_text(encoding="utf-8"))
        for item in result.results
    }

    blind = artifacts["depth-4-blind"]
    perturbed = artifacts["depth-4-perturbed"]

    assert blind["run"]["start_mode"] == "blind"
    assert blind["training_mode"] == "blind_training"
    assert blind["claim_id"] == "paper-blind-depth-degradation"
    assert blind["threshold"]["id"] == "measured_depth_curve"
    assert blind["status"] in {"snapped_but_failed", "failed"}
    assert blind["claim_status"] == "failed"
    assert blind["evidence_class"] in {"snapped_but_failed", "failed", "soft_fit_only"}

    assert perturbed["run"]["start_mode"] == "perturbed_tree"
    assert perturbed["training_mode"] == "perturbed_true_tree_training"
    assert perturbed["claim_id"] == "paper-blind-depth-degradation"
    assert perturbed["threshold"]["id"] == "measured_depth_curve"
    assert perturbed["status"] == "recovered"
    assert perturbed["claim_status"] == "recovered"
    assert perturbed["return_kind"] == "same_ast_return"
    assert perturbed["raw_status"] == "recovered"
    assert perturbed["evidence_class"] == "perturbed_true_tree_recovered"


def test_cli_benchmark_writes_suite_result(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "eml_symbolic_regression.cli",
            "benchmark",
            "smoke",
            "--case",
            "planck-diagnostic",
            "--output-dir",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        env=CLI_ENV,
        text=True,
    )

    assert "smoke: 1 runs" in result.stdout
    suite_result = tmp_path / "smoke" / "suite-result.json"
    payload = json.loads(suite_result.read_text())
    assert payload["counts"]["total"] == 1
    assert payload["results"][0]["status"] == "unsupported"


def test_cli_list_claims_prints_claim_matrix():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "eml_symbolic_regression.cli",
            "list-claims",
        ],
        check=True,
        capture_output=True,
        env=CLI_ENV,
        text=True,
    )

    lines = result.stdout.strip().splitlines()
    assert lines == sorted(lines)
    assert any(
        line.startswith("paper-shallow-blind-recovery: measured_training_boundary threshold=measured_pure_blind_recovery suites=")
        for line in lines
    )
    assert any(
        line.startswith(
            "paper-shallow-scaffolded-recovery: scaffolded_training_proof threshold=scaffolded_bounded_100_percent suites="
        )
        for line in lines
    )
    assert any(line.endswith("suites=proof-depth-curve") for line in lines)


def test_cli_proof_dataset_writes_manifest_without_raw_arrays(tmp_path):
    output = tmp_path / "exp-proof-manifest.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "eml_symbolic_regression.cli",
            "proof-dataset",
            "exp",
            "--points",
            "12",
            "--seed",
            "7",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        env=CLI_ENV,
        text=True,
    )

    assert f"exp: dataset manifest -> {output}" in result.stdout
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["schema"] == "eml.proof_dataset_manifest.v1"
    assert payload["formula_id"] == "exp"
    assert payload["seed"] == 7
    assert payload["splits"][0]["name"] == "train"
    assert payload["splits"][0]["count"] == 12
    assert payload["provenance"]["symbolic_expression"] == "exp(x)"
    assert payload["manifest_sha256"]
    encoded = json.dumps(payload)
    assert '"inputs"' not in encoded
    assert '"target"' not in encoded
    assert '"values"' not in encoded


@pytest.mark.parametrize(
    ("extra_args", "message"),
    [
        (["--points", "0"], "points must be positive"),
        (["--tolerance=-1e-8"], "tolerance must be positive"),
    ],
)
def test_cli_proof_dataset_rejects_invalid_sampling_contracts(tmp_path, extra_args, message):
    output = tmp_path / "bad-proof-manifest.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "eml_symbolic_regression.cli",
            "proof-dataset",
            "exp",
            "--output",
            str(output),
            *extra_args,
        ],
        check=False,
        capture_output=True,
        env=CLI_ENV,
        text=True,
    )

    assert result.returncode != 0
    assert message in result.stderr
    assert not output.exists()


def test_cli_campaign_writes_report(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "eml_symbolic_regression.cli",
            "campaign",
            "smoke",
            "--case",
            "planck-diagnostic",
            "--output-root",
            str(tmp_path),
            "--label",
            "cli-smoke",
        ],
        check=True,
        capture_output=True,
        env=CLI_ENV,
        text=True,
    )

    assert "report ->" in result.stdout
    report = tmp_path / "cli-smoke" / "report.md"
    manifest = tmp_path / "cli-smoke" / "campaign-manifest.json"
    assert report.exists()
    assert manifest.exists()
    assert "## Headline Metrics" in report.read_text(encoding="utf-8")


def test_for_demo_diagnostic_subset_preserves_unsupported_formula(tmp_path):
    base = builtin_suite("for-demo-diagnostics")
    suite = type(base)(base.id, base.description, base.cases, tmp_path / "artifacts")

    result = run_benchmark_suite(suite, run_filter=RunFilter(case_ids=("damped-oscillator-compile",)))

    assert len(result.results) == 1
    assert result.results[0].status == "unsupported"
    assert result.results[0].payload["compiled_eml"]["reason"] == "unsupported_operator"
    assert result.results[0].payload["compiled_eml"]["diagnostic"]["strict"]["reason"] == "unsupported_operator"


def test_shockley_warm_start_moves_to_verified_recovered_artifact(tmp_path):
    base = builtin_suite("v1.3-standard")
    suite = type(base)(base.id, base.description, base.cases, tmp_path / "artifacts")

    result = run_benchmark_suite(suite, run_filter=RunFilter(case_ids=("shockley-warm",)))

    assert len(result.results) == 1
    assert result.results[0].status == "same_ast_return"
    assert result.results[0].payload["claim_status"] == "recovered"
    assert result.results[0].payload["evidence_class"] == "same_ast"
    compiled = result.results[0].payload["compiled_eml"]
    assert compiled["metadata"]["depth"] <= 13
    assert compiled["metadata"]["macro_diagnostics"]["hits"] == ["scaled_exp_minus_one_template"]
    assert result.results[0].payload["stage_statuses"]["compiled_seed"] == "recovered"
    assert result.results[0].payload["stage_statuses"]["warm_start_attempt"] == "same_ast_return"
    assert result.results[0].payload["stage_statuses"]["trained_exact_recovery"] == "recovered"


def test_arrhenius_warm_benchmark_records_same_ast_evidence(tmp_path):
    base = builtin_suite("v1.9-arrhenius-evidence")
    suite = type(base)(base.id, base.description, base.cases, tmp_path / "artifacts")

    result = run_benchmark_suite(
        suite,
        run_filter=RunFilter(case_ids=("arrhenius-warm",), seeds=(0,), perturbation_noises=(0.0,)),
    )

    assert len(result.results) == 1
    assert result.results[0].status == "same_ast_return"
    assert result.results[0].artifact_path.exists()
    assert suite.id in result.results[0].artifact_path.parts

    artifact = json.loads(result.results[0].artifact_path.read_text(encoding="utf-8"))
    domains = {split["name"]: tuple(split["domain"]) for split in artifact["dataset_manifest"]["splits"]}

    assert artifact["run"]["suite_id"] == "v1.9-arrhenius-evidence"
    assert artifact["run"]["case_id"] == "arrhenius-warm"
    assert artifact["run"]["formula"] == "arrhenius"
    assert artifact["run"]["start_mode"] == "warm_start"
    assert artifact["training_mode"] == "compiler_warm_start_training"
    assert artifact["status"] == "same_ast_return"
    assert artifact["claim_status"] == "recovered"
    assert artifact["evidence_class"] == "same_ast"
    assert artifact["stage_statuses"]["compiled_seed"] == "recovered"
    assert artifact["stage_statuses"]["warm_start_attempt"] == "same_ast_return"
    assert artifact["stage_statuses"]["trained_exact_recovery"] == "recovered"
    assert artifact["compiled_eml"]["metadata"]["macro_diagnostics"]["hits"] == ["direct_division_template"]
    assert artifact["compiled_eml"]["metadata"]["depth"] == 7
    assert artifact["warm_start_eml"]["status"] == "same_ast_return"
    assert artifact["warm_start_eml"]["verification"]["status"] == "recovered"
    assert artifact["warm_start_eml"]["diagnosis"]["changed_slot_count"] == 0
    assert artifact["dataset_manifest"]["formula_id"] == "arrhenius"
    assert artifact["provenance"]["symbolic_expression"] == "exp(-0.8/x)"
    assert domains == {
        "train": (0.5, 3.0),
        "heldout": (0.6, 2.7),
        "extrapolation": (3.1, 4.2),
    }

    aggregate = benchmark_module.aggregate_evidence(result)
    aggregate_run = aggregate["runs"][0]

    assert aggregate_run["evidence_class"] == "same_ast"
    assert aggregate_run["classification"] == "same_ast_warm_start_return"


def test_michaelis_warm_benchmark_records_same_ast_evidence(tmp_path):
    base = builtin_suite("v1.9-michaelis-evidence")
    suite = type(base)(base.id, base.description, base.cases, tmp_path / "artifacts")

    result = run_benchmark_suite(
        suite,
        run_filter=RunFilter(case_ids=("michaelis-warm",), seeds=(0,), perturbation_noises=(0.0,)),
    )

    assert len(result.results) == 1
    assert result.results[0].status == "same_ast_return"
    assert result.results[0].artifact_path.exists()
    assert suite.id in result.results[0].artifact_path.parts

    artifact = json.loads(result.results[0].artifact_path.read_text(encoding="utf-8"))
    domains = {split["name"]: tuple(split["domain"]) for split in artifact["dataset_manifest"]["splits"]}

    assert artifact["run"]["suite_id"] == "v1.9-michaelis-evidence"
    assert artifact["run"]["case_id"] == "michaelis-warm"
    assert artifact["run"]["formula"] == "michaelis_menten"
    assert artifact["run"]["start_mode"] == "warm_start"
    assert artifact["training_mode"] == "compiler_warm_start_training"
    assert artifact["status"] == "same_ast_return"
    assert artifact["claim_status"] == "recovered"
    assert artifact["evidence_class"] == "same_ast"
    assert artifact["stage_statuses"]["compiled_seed"] == "recovered"
    assert artifact["stage_statuses"]["warm_start_attempt"] == "same_ast_return"
    assert artifact["stage_statuses"]["trained_exact_recovery"] == "recovered"
    assert artifact["compiled_eml"]["metadata"]["macro_diagnostics"]["hits"] == ["saturation_ratio_template"]
    assert artifact["compiled_eml"]["metadata"]["depth"] == 12
    assert artifact["compiled_eml"]["metadata"]["node_count"] == 41
    assert artifact["warm_start_eml"]["status"] == "same_ast_return"
    assert artifact["warm_start_eml"]["verification"]["status"] == "recovered"
    assert artifact["warm_start_eml"]["diagnosis"]["changed_slot_count"] == 0
    assert artifact["dataset_manifest"]["formula_id"] == "michaelis_menten"
    assert artifact["provenance"]["symbolic_expression"] == "2*x/(x + 0.5)"
    assert domains == {
        "train": (0.05, 5.0),
        "heldout": (0.08, 4.5),
        "extrapolation": (5.1, 7.0),
    }

    aggregate = benchmark_module.aggregate_evidence(result)
    aggregate_run = aggregate["runs"][0]

    assert aggregate_run["evidence_class"] == "same_ast"
    assert aggregate_run["classification"] == "same_ast_warm_start_return"
    assert aggregate_run["classification"] != "blind_recovery"
    assert aggregate_run["start_mode"] == "warm_start"


def test_logistic_v110_compile_benchmark_records_improved_unsupported_diagnostic(tmp_path):
    base = builtin_suite("v1.10-logistic-evidence")
    suite = type(base)(base.id, base.description, base.cases, tmp_path / "artifacts")

    result = run_benchmark_suite(suite, run_filter=RunFilter(case_ids=("logistic-compile",), seeds=(0,)))

    assert len(result.results) == 1
    assert result.results[0].status == "unsupported"
    assert result.results[0].artifact_path.exists()
    assert suite.id in result.results[0].artifact_path.parts

    artifact = json.loads(result.results[0].artifact_path.read_text(encoding="utf-8"))
    compiled = artifact["compiled_eml"]
    relaxed = compiled["diagnostic"]["relaxed"]
    macro_diagnostics = relaxed["metadata"]["macro_diagnostics"]

    assert artifact["run"]["suite_id"] == "v1.10-logistic-evidence"
    assert artifact["run"]["case_id"] == "logistic-compile"
    assert artifact["run"]["formula"] == "logistic"
    assert artifact["run"]["start_mode"] == "compile"
    assert artifact["status"] == "unsupported"
    assert artifact["claim_status"] == "unsupported"
    assert artifact["stage_statuses"]["compiled_seed"] == "unsupported"
    assert "warm_start_eml" not in artifact
    assert compiled["reason"] == "depth_exceeded"
    assert compiled["diagnostic"]["strict"]["reason"] == "depth_exceeded"
    assert relaxed["metadata"]["depth"] == 15
    assert relaxed["metadata"]["node_count"] == 49
    assert relaxed["validation"]["passed"] is True
    assert macro_diagnostics["hits"] == ["exponential_saturation_template"]
    assert macro_diagnostics["depth_delta"] == 12
    assert macro_diagnostics["node_delta"] == 28
    assert macro_diagnostics["validation_status"] == "validated"
    assert macro_diagnostics["validation_passed"] is True

    aggregate = benchmark_module.aggregate_evidence(result)
    aggregate_run = aggregate["runs"][0]

    assert aggregate["counts"]["unsupported"] == 1
    assert aggregate_run["classification"] == "unsupported"
    assert aggregate_run["evidence_class"] == "unsupported"
    assert aggregate_run["reason"] == "depth_exceeded"
    assert aggregate_run["metrics"]["unsupported_reason"] == "depth_exceeded"


def test_v113_basis_only_compile_fails_closed_on_literal_coefficients(tmp_path):
    base = builtin_suite("v1.13-paper-basis-only")
    suite = type(base)(base.id, base.description, base.cases, tmp_path / "artifacts")

    result = run_benchmark_suite(suite, run_filter=RunFilter(case_ids=("beer-lambert-basis-only-compile",), seeds=(0,)))

    assert len(result.results) == 1
    assert result.results[0].status == "unsupported"
    artifact = json.loads(result.results[0].artifact_path.read_text(encoding="utf-8"))

    assert artifact["run"]["track"] == "basis_only"
    assert artifact["run"]["constants_policy"] == "basis_only"
    assert artifact["benchmark_track"]["literal_catalog"] == []
    assert artifact["status"] == "unsupported"
    assert artifact["compiled_eml"]["reason"] == "constant_policy"

    aggregate = benchmark_module.aggregate_evidence(result)
    assert aggregate["tracks"] == [
        {
            "track": "basis_only",
            "total": 1,
            "verifier_recovered": 0,
            "verification_passed": 0,
            "trained_exact_recovery": 0,
            "compile_only_verified_support": 0,
            "unsupported": 1,
            "failed": 0,
            "verifier_recovery_rate": 0.0,
            "trained_exact_recovery_rate": 0.0,
            "constants_policies": ["basis_only"],
            "formulas": ["beer_lambert"],
            "evidence_classes": {"unsupported": 1},
            "evidence_regimes": {"unsupported": 1},
            "discovery_classes": {"unsupported": 1},
        }
    ]


def test_planck_v110_compile_benchmark_records_improved_unsupported_diagnostic(tmp_path):
    base = builtin_suite("v1.10-planck-diagnostics")
    suite = type(base)(base.id, base.description, base.cases, tmp_path / "artifacts")

    result = run_benchmark_suite(suite, run_filter=RunFilter(case_ids=("planck-compile",), seeds=(0,)))

    assert len(result.results) == 1
    assert result.results[0].status == "unsupported"
    assert result.results[0].artifact_path.exists()
    assert suite.id in result.results[0].artifact_path.parts

    artifact = json.loads(result.results[0].artifact_path.read_text(encoding="utf-8"))
    compiled = artifact["compiled_eml"]
    relaxed = compiled["diagnostic"]["relaxed"]
    macro_diagnostics = relaxed["metadata"]["macro_diagnostics"]

    assert artifact["run"]["suite_id"] == "v1.10-planck-diagnostics"
    assert artifact["run"]["case_id"] == "planck-compile"
    assert artifact["run"]["formula"] == "planck"
    assert artifact["run"]["start_mode"] == "compile"
    assert artifact["status"] == "unsupported"
    assert artifact["claim_status"] == "unsupported"
    assert artifact["stage_statuses"]["compiled_seed"] == "unsupported"
    assert "warm_start_eml" not in artifact
    assert compiled["reason"] == "depth_exceeded"
    assert compiled["diagnostic"]["strict"]["reason"] == "depth_exceeded"
    assert relaxed["metadata"]["depth"] == 14
    assert relaxed["metadata"]["depth"] < 20
    assert relaxed["metadata"]["node_count"] == 59
    assert relaxed["validation"]["passed"] is True
    assert macro_diagnostics["hits"] == [
        "low_degree_power_template",
        "scaled_exp_minus_one_template",
        "direct_division_template",
    ]
    assert macro_diagnostics["depth_delta"] == 10
    assert macro_diagnostics["node_delta"] == 34
    assert macro_diagnostics["validation_status"] == "validated"
    assert macro_diagnostics["validation_passed"] is True

    aggregate = benchmark_module.aggregate_evidence(result)
    aggregate_run = aggregate["runs"][0]

    assert aggregate["counts"]["unsupported"] == 1
    assert aggregate_run["classification"] == "unsupported"
    assert aggregate_run["evidence_class"] == "unsupported"
    assert aggregate_run["reason"] == "depth_exceeded"
    assert aggregate_run["metrics"]["unsupported_reason"] == "depth_exceeded"


def test_v111_paper_training_runs_real_pure_blind_training(tmp_path):
    base = builtin_suite("v1.11-paper-training")
    suite = type(base)(base.id, base.description, base.cases, tmp_path / "artifacts")

    result = run_benchmark_suite(suite, run_filter=RunFilter(case_ids=("exp-pure-blind",), seeds=(0,)))

    assert len(result.results) == 1
    assert result.results[0].artifact_path.exists()

    artifact = json.loads(result.results[0].artifact_path.read_text(encoding="utf-8"))
    aggregate = benchmark_module.aggregate_evidence(result)
    aggregate_run = aggregate["runs"][0]

    assert artifact["run"]["suite_id"] == "v1.11-paper-training"
    assert artifact["run"]["case_id"] == "exp-pure-blind"
    assert artifact["run"]["start_mode"] == "blind"
    assert artifact["run"]["optimizer"]["scaffold_initializers"] == []
    assert artifact["training_mode"] == "blind_training"
    assert artifact["status"] == "recovered"
    assert artifact["claim_status"] == "recovered"
    assert aggregate_run["evidence_class"] == "blind_training_recovered"
    assert aggregate_run["classification"] == "blind_recovery"
    assert aggregate["counts"]["verifier_recovered"] == 1


def test_v111_logistic_planck_probe_compile_rows_remain_unsupported(tmp_path):
    base = builtin_suite("v1.11-logistic-planck-probes")
    suite = type(base)(base.id, base.description, base.cases, tmp_path / "artifacts")

    result = run_benchmark_suite(
        suite,
        run_filter=RunFilter(case_ids=("logistic-compile", "planck-compile"), seeds=(0,)),
    )

    assert len(result.results) == 2
    assert {item.status for item in result.results} == {"unsupported"}

    aggregate = benchmark_module.aggregate_evidence(result)
    by_formula = {run["formula"]: run for run in aggregate["runs"]}

    assert aggregate["counts"]["unsupported"] == 2
    assert aggregate["counts"]["verifier_recovered"] == 0
    assert by_formula["logistic"]["evidence_class"] == "unsupported"
    assert by_formula["planck"]["evidence_class"] == "unsupported"
    assert by_formula["logistic"]["reason"] == "depth_exceeded"
    assert by_formula["planck"]["reason"] == "depth_exceeded"
