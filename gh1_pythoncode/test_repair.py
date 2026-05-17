import numpy as np
import torch

from eml_symbolic_regression.expression import Const, Eml, Var
from eml_symbolic_regression.master_tree import EmbeddingResult, SoftEMLTree
from eml_symbolic_regression.optimize import ExactCandidate, FitResult
from eml_symbolic_regression.repair import (
    RepairConfig,
    RepairMove,
    RepairReport,
    cleanup_failed_candidate,
    repair_perturbed_candidate,
)
from eml_symbolic_regression.verify import DataSplit, SplitResult, VerificationReport


def _verification_report(status: str = "recovered") -> VerificationReport:
    return VerificationReport(
        status=status,
        candidate_kind="exact_eml",
        reason="verified" if status == "recovered" else "heldout_failed",
        split_results=[SplitResult("heldout", 0.0 if status == "recovered" else 1.0, 0.0, 0.0, status == "recovered")],
        high_precision_max_error=0.0 if status == "recovered" else 1.0,
        tolerance=1e-8,
    )


def _fit_from_slots(
    slots: dict[str, str],
    *,
    depth: int = 2,
    variables: tuple[str, ...] = ("x",),
    constants: tuple[complex, ...] = (1.0,),
) -> FitResult:
    tree = SoftEMLTree(depth, variables, constants)
    for slot, choice in slots.items():
        node_path, side = slot.rsplit(".", 1)
        tree.set_slot(node_path, side, choice, strength=40.0)
    snap = tree.snap()
    return FitResult(
        status="snapped_candidate",
        best_loss=1.0,
        post_snap_loss=1.0,
        snap=snap,
        manifest={"snap": snap.as_dict(), "status": "snapped_candidate"},
    )


def _embedding_for_target(target_expr: Eml, *, depth: int = 2) -> EmbeddingResult:
    tree = SoftEMLTree(depth, ("x",), (1.0,))
    return tree.embed_expr(target_expr)


def _verification_splits(target_expr: Eml) -> list[DataSplit]:
    x_values = np.linspace(-0.4, 0.4, 9).astype(np.complex128)
    inputs = {"x": x_values}
    target = target_expr.evaluate_numpy(inputs)
    return [
        DataSplit("heldout", inputs, target),
        DataSplit("extrap", {"x": (x_values + 0.8).astype(np.complex128)}, target_expr.evaluate_numpy({"x": x_values + 0.8})),
    ]


def _run_repair(fit: FitResult, target_expr: Eml, embedding: EmbeddingResult) -> RepairReport:
    return repair_perturbed_candidate(
        fit,
        target_expr=target_expr,
        embedding=embedding,
        depth=2,
        variables=("x",),
        constants=(1.0,),
        verification_splits=_verification_splits(target_expr),
        tolerance=1e-8,
        original_status="snapped_but_failed",
        return_kind="snapped_but_failed",
    )


def _fit_with_selected_candidate(tree: SoftEMLTree) -> FitResult:
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
        slot_alternatives=tree.active_slot_alternatives(top_k=2),
    )
    return FitResult(
        status="snapped_candidate",
        best_loss=1.0,
        post_snap_loss=1.0,
        snap=snap,
        manifest={"schema": "eml.run_manifest.v1", "status": "snapped_candidate", "snap": snap.as_dict()},
        selected_candidate=selected,
        fallback_candidate=selected,
        candidates=(selected,),
    )


def _candidate_from_tree(
    tree: SoftEMLTree,
    *,
    candidate_id: str,
    source: str,
    slot_alternatives: object = None,
) -> ExactCandidate:
    snap = tree.snap()
    alternatives = tree.active_slot_alternatives(top_k=3) if slot_alternatives is None else slot_alternatives
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
        slot_alternatives=alternatives,
    )


def _constant_root_tree() -> SoftEMLTree:
    tree = SoftEMLTree(2, ("x",), (1.0,))
    tree.set_slot("root", "left", "const:1", strength=40.0)
    tree.set_slot("root", "right", "const:1", strength=40.0)
    return tree


def _terminal_to_child_repairable_tree() -> SoftEMLTree:
    tree = SoftEMLTree(2, ("x",), (1.0,))
    tree.set_slot("root", "right", "const:1", strength=40.0)
    tree.set_slot("root.L", "left", "var:x", strength=40.0)
    tree.set_slot("root.L", "right", "const:1", strength=40.0)
    with torch.no_grad():
        tree.root.left_logits.copy_(torch.tensor([0.0, 2.0, 1.85], dtype=torch.float64))
    return tree


def _constant_to_child_repairable_tree() -> SoftEMLTree:
    tree = SoftEMLTree(2, ("x",), (1.0,))
    tree.set_slot("root", "right", "const:1", strength=40.0)
    tree.set_slot("root.L", "left", "var:x", strength=40.0)
    tree.set_slot("root.L", "right", "const:1", strength=40.0)
    with torch.no_grad():
        tree.root.left_logits.copy_(torch.tensor([2.0, 0.0, 1.99], dtype=torch.float64))
    return tree


def _fit_with_candidate_pool(
    *,
    selected: ExactCandidate,
    fallback: ExactCandidate | None = None,
    candidates: tuple[ExactCandidate, ...] = (),
) -> FitResult:
    retained = candidates or ((selected,) if fallback is None else (selected, fallback))
    return FitResult(
        status="snapped_candidate",
        best_loss=1.0,
        post_snap_loss=1.0,
        snap=selected.snap,
        manifest={"schema": "eml.run_manifest.v1", "status": "snapped_candidate", "snap": selected.snap.as_dict()},
        selected_candidate=selected,
        fallback_candidate=fallback,
        candidates=retained,
    )


def _run_candidate_pool_cleanup(
    fit: FitResult,
    target_expr: Eml,
    *,
    config: RepairConfig | None = None,
) -> RepairReport:
    return cleanup_failed_candidate(
        fit,
        depth=2,
        variables=("x",),
        constants=(1.0,),
        verification_splits=_verification_splits(target_expr),
        tolerance=1e-8,
        config=config,
        original_status="snapped_but_failed",
        return_kind="snapped_but_failed",
    )


def test_repair_config_defaults_to_bounded_target_neighborhood() -> None:
    config = RepairConfig()

    assert config.max_target_reverts == 8
    assert config.strength == 30.0
    assert config.allow_target_slot_reverts is True
    assert config.allow_catalog_alternatives is False
    assert config.cleanup_top_k == 2
    assert config.cleanup_max_slots == 4
    assert config.cleanup_beam_width == 8
    assert config.cleanup_max_moves == 2
    assert config.cleanup_candidate_sources == ("selected",)


def test_repair_config_expanded_candidate_pool_is_bounded() -> None:
    config = RepairConfig.expanded_candidate_pool()

    assert config.max_target_reverts == 8
    assert config.strength == 30.0
    assert config.allow_target_slot_reverts is True
    assert config.allow_catalog_alternatives is False
    assert config.cleanup_top_k == 3
    assert config.cleanup_max_slots == 8
    assert config.cleanup_beam_width == 32
    assert config.cleanup_max_moves == 3
    assert config.cleanup_candidate_sources == ("selected", "fallback", "retained")


def test_repair_move_serializes_slot_and_subtree_provenance() -> None:
    move = RepairMove(
        kind="terminal_to_child",
        slot="root.left",
        before="var:x",
        after="child",
        source="embedded_target_slot",
        accepted=False,
        verifier_status="failed",
        descendant_assignments=({"slot": "root.L.left", "choice": "var:x"}, {"slot": "root.L.right", "choice": "const:1"}),
        pruned_assignments=({"slot": "root.L.right", "choice": "const:1"},),
        subtree_root="root.L",
    )

    payload = move.as_dict()

    assert payload["kind"] == "terminal_to_child"
    assert payload["slot"] == "root.left"
    assert payload["before"] == "var:x"
    assert payload["after"] == "child"
    assert payload["source"] == "embedded_target_slot"
    assert payload["accepted"] is False
    assert payload["verifier_status"] == "failed"
    assert payload["descendant_assignments"] == [
        {"slot": "root.L.left", "choice": "var:x"},
        {"slot": "root.L.right", "choice": "const:1"},
    ]
    assert payload["pruned_assignments"] == [{"slot": "root.L.right", "choice": "const:1"}]
    assert payload["subtree_root"] == "root.L"

    candidate_move = RepairMove(
        kind="terminal_to_child",
        slot="root.left",
        before="var:x",
        after="child",
        source="slot_alternative",
        accepted=True,
        verifier_status="recovered",
        candidate_id="fallback-candidate",
        candidate_source="hardening_checkpoint",
        candidate_root_source="fallback",
    )

    candidate_payload = candidate_move.as_dict()

    assert candidate_payload["candidate_id"] == "fallback-candidate"
    assert candidate_payload["candidate_source"] == "hardening_checkpoint"
    assert candidate_payload["candidate_root_source"] == "fallback"


def test_unverified_repair_report_preserves_raw_status_without_repaired_ast() -> None:
    attempted = RepairMove(
        kind="slot_revert",
        slot="root.right",
        before="var:x",
        after="const:1",
        source="embedded_target_slot",
        accepted=False,
        verifier_status="failed",
    )
    report = RepairReport(
        status="not_repaired",
        original_status="snapped_but_failed",
        return_kind="snapped_but_failed",
        moves_attempted=(attempted,),
        accepted_moves=(),
        repaired_expression=Eml(Var("x"), Const(1.0)),
        verification=_verification_report("failed"),
        reason="no_verified_local_move",
    )

    payload = report.as_dict()

    assert payload["status"] == "not_repaired"
    assert payload["original_status"] == "snapped_but_failed"
    assert payload["return_kind"] == "snapped_but_failed"
    assert payload["moves_attempted"] == [attempted.as_dict()]
    assert payload["accepted_moves"] == []
    assert payload["repaired_ast"] is None
    assert payload["verification"]["status"] == "failed"
    assert payload["reason"] == "no_verified_local_move"


def test_verified_repair_report_serializes_repaired_ast_and_verification() -> None:
    accepted = RepairMove(
        kind="slot_revert",
        slot="root.right",
        before="var:x",
        after="const:1",
        source="embedded_target_slot",
        accepted=True,
        verifier_status="recovered",
    )
    report = RepairReport(
        status="repaired_candidate",
        original_status="snapped_but_failed",
        return_kind="snapped_but_failed",
        moves_attempted=(accepted,),
        accepted_moves=(accepted,),
        repaired_expression=Eml(Var("x"), Const(1.0)),
        verification=_verification_report("recovered"),
        reason="verified_local_move",
    )

    payload = report.as_dict()

    assert payload["status"] == "repaired_candidate"
    assert payload["accepted_moves"] == [accepted.as_dict()]
    assert payload["repaired_ast"]["root"]["kind"] == "eml"
    assert payload["repaired_ast"]["metadata"]["source"] == "repaired_candidate"
    assert payload["verification"]["status"] == "recovered"
    assert payload["candidate_roots_considered"] == []
    assert payload["candidate_root_count"] == 0
    assert payload["variants_by_candidate_root"] == []
    assert payload["deduped_variant_count"] == 0
    assert payload["accepted_candidate_id"] is None
    assert payload["accepted_candidate_source"] is None
    assert payload["accepted_candidate_root_source"] is None


def test_terminal_to_child_repair_applies_new_descendant_assignments() -> None:
    target_expr = Eml(Eml(Var("x"), Const(1.0)), Const(1.0))
    fit = _fit_from_slots({"root.left": "var:x", "root.right": "const:1"})
    report = _run_repair(fit, target_expr, _embedding_for_target(target_expr))

    payload = report.as_dict()
    accepted = payload["accepted_moves"][0]

    assert payload["status"] == "repaired_candidate"
    assert payload["original_status"] == "snapped_but_failed"
    assert payload["return_kind"] == "snapped_but_failed"
    assert payload["verification"]["status"] == "recovered"
    assert accepted["kind"] == "terminal_to_child"
    assert accepted["slot"] == "root.left"
    assert accepted["before"] == "var:x"
    assert accepted["after"] == "child"
    assert accepted["source"] == "embedded_target_slot"
    assert accepted["verifier_status"] == "recovered"
    assert accepted["descendant_assignments"] == [
        {"slot": "root.L.left", "choice": "var:x"},
        {"slot": "root.L.right", "choice": "const:1"},
    ]
    assert accepted["subtree_root"] == "root.L"


def test_child_to_terminal_repair_records_pruned_descendants() -> None:
    target_expr = Eml(Var("x"), Const(1.0))
    fit = _fit_from_slots(
        {
            "root.left": "child",
            "root.L.left": "var:x",
            "root.L.right": "const:1",
            "root.right": "const:1",
        }
    )
    report = _run_repair(fit, target_expr, _embedding_for_target(target_expr))

    accepted = report.as_dict()["accepted_moves"][0]

    assert report.status == "repaired_candidate"
    assert accepted["kind"] == "child_to_terminal"
    assert accepted["slot"] == "root.left"
    assert accepted["before"] == "child"
    assert accepted["after"] == "var:x"
    assert accepted["pruned_assignments"] == [
        {"slot": "root.L.left", "choice": "var:x"},
        {"slot": "root.L.right", "choice": "const:1"},
    ]
    assert accepted["subtree_root"] == "root.L"


def test_child_subtree_replacement_replays_descendant_target_slots() -> None:
    target_expr = Eml(Eml(Var("x"), Const(1.0)), Const(1.0))
    fit = _fit_from_slots(
        {
            "root.left": "child",
            "root.L.left": "const:1",
            "root.L.right": "var:x",
            "root.right": "const:1",
        }
    )
    report = _run_repair(fit, target_expr, _embedding_for_target(target_expr))

    accepted = report.as_dict()["accepted_moves"][0]

    assert report.status == "repaired_candidate"
    assert accepted["kind"] == "child_subtree_replacement"
    assert accepted["slot"] == "root.left"
    assert accepted["before"] == "child"
    assert accepted["after"] == "child"
    assert accepted["descendant_assignments"] == [
        {"slot": "root.L.left", "choice": "var:x"},
        {"slot": "root.L.right", "choice": "const:1"},
    ]
    assert accepted["subtree_root"] == "root.L"


def test_repair_does_not_accept_without_verifier_recovery() -> None:
    target_expr = Eml(Eml(Var("x"), Const(1.0)), Const(1.0))
    wrong_verifier_target = Eml(Const(1.0), Const(1.0))
    fit = _fit_from_slots({"root.left": "var:x", "root.right": "const:1"})

    report = repair_perturbed_candidate(
        fit,
        target_expr=target_expr,
        embedding=_embedding_for_target(target_expr),
        depth=2,
        variables=("x",),
        constants=(1.0,),
        verification_splits=_verification_splits(wrong_verifier_target),
        tolerance=1e-8,
        original_status="snapped_but_failed",
        return_kind="snapped_but_failed",
    )

    payload = report.as_dict()

    assert payload["status"] == "not_repaired"
    assert payload["reason"] == "no_verified_local_move"
    assert payload["accepted_moves"] == []
    assert payload["repaired_ast"] is None
    assert {move["verifier_status"] for move in payload["moves_attempted"]} == {"failed"}


def test_target_free_cleanup_recovers_from_low_margin_slot_alternative() -> None:
    target_expr = Eml(Eml(Var("x"), Const(1.0)), Const(1.0))
    tree = SoftEMLTree(2, ("x",), (1.0,))
    tree.set_slot("root", "right", "const:1", strength=40.0)
    tree.set_slot("root.L", "left", "var:x", strength=40.0)
    tree.set_slot("root.L", "right", "const:1", strength=40.0)
    with torch.no_grad():
        tree.root.left_logits.copy_(torch.tensor([0.0, 2.0, 1.85], dtype=torch.float64))

    fit = _fit_with_selected_candidate(tree)
    report = cleanup_failed_candidate(
        fit,
        depth=2,
        variables=("x",),
        constants=(1.0,),
        verification_splits=_verification_splits(target_expr),
        tolerance=1e-8,
        original_status="snapped_but_failed",
        return_kind="snapped_but_failed",
    )

    payload = report.as_dict()
    accepted = payload["accepted_moves"][0]

    assert payload["status"] == "repaired_candidate"
    assert payload["reason"] == "verified_slot_neighborhood"
    assert payload["verification"]["status"] == "recovered"
    assert payload["variant_count"] >= 1
    assert accepted["slot"] == "root.left"
    assert accepted["before"] == "var:x"
    assert accepted["after"] == "child"
    assert accepted["source"] == "slot_alternative"
    assert accepted["slot_margin"] < 0.2
    assert accepted["probability_gap"] > 0.0
    assert accepted["descendant_assignments"] == [
        {"slot": "root.L.left", "choice": "var:x"},
        {"slot": "root.L.right", "choice": "const:1"},
    ]


def test_target_free_cleanup_defaults_to_selected_root_only() -> None:
    target_expr = Eml(Eml(Var("x"), Const(1.0)), Const(1.0))
    selected = _candidate_from_tree(
        _constant_root_tree(),
        candidate_id="selected",
        source="legacy_final_snap",
        slot_alternatives=(),
    )
    fallback = _candidate_from_tree(
        _terminal_to_child_repairable_tree(),
        candidate_id="fallback",
        source="hardening_checkpoint",
    )
    fit = _fit_with_candidate_pool(selected=selected, fallback=fallback)

    report = _run_candidate_pool_cleanup(fit, target_expr)
    payload = report.as_dict()

    assert payload["status"] == "not_repaired"
    assert payload["reason"] == "missing_slot_alternatives"
    assert payload["candidate_root_count"] == 1
    assert [root["candidate_root_source"] for root in payload["candidate_roots_considered"]] == ["selected"]
    assert payload["accepted_candidate_id"] is None
    assert payload["repaired_ast"] is None


def test_expanded_candidate_pool_repairs_from_fallback_root() -> None:
    target_expr = Eml(Eml(Var("x"), Const(1.0)), Const(1.0))
    selected = _candidate_from_tree(
        _constant_root_tree(),
        candidate_id="selected",
        source="legacy_final_snap",
        slot_alternatives=(),
    )
    fallback = _candidate_from_tree(
        _terminal_to_child_repairable_tree(),
        candidate_id="fallback",
        source="hardening_checkpoint",
    )
    fit = _fit_with_candidate_pool(selected=selected, fallback=fallback)

    report = _run_candidate_pool_cleanup(fit, target_expr, config=RepairConfig.expanded_candidate_pool())
    payload = report.as_dict()
    accepted = payload["accepted_moves"][0]

    assert payload["status"] == "repaired_candidate"
    assert payload["reason"] == "verified_slot_neighborhood"
    assert payload["candidate_root_count"] == 2
    assert [root["candidate_root_source"] for root in payload["candidate_roots_considered"]] == ["selected", "fallback"]
    assert payload["accepted_candidate_id"] == "fallback"
    assert payload["accepted_candidate_source"] == "hardening_checkpoint"
    assert payload["accepted_candidate_root_source"] == "fallback"
    assert payload["variant_count"] == payload["deduped_variant_count"]
    assert payload["variant_count"] >= 1
    assert accepted["candidate_id"] == "fallback"
    assert accepted["candidate_source"] == "hardening_checkpoint"
    assert accepted["candidate_root_source"] == "fallback"


def test_expanded_candidate_pool_repairs_from_retained_root() -> None:
    target_expr = Eml(Eml(Var("x"), Const(1.0)), Const(1.0))
    selected = _candidate_from_tree(
        _constant_root_tree(),
        candidate_id="selected",
        source="legacy_final_snap",
        slot_alternatives=(),
    )
    retained = _candidate_from_tree(
        _terminal_to_child_repairable_tree(),
        candidate_id="retained-001",
        source="late_hardening_checkpoint",
    )
    fit = _fit_with_candidate_pool(selected=selected, candidates=(selected, retained))

    report = _run_candidate_pool_cleanup(fit, target_expr, config=RepairConfig.expanded_candidate_pool())
    payload = report.as_dict()

    assert payload["status"] == "repaired_candidate"
    assert payload["candidate_root_count"] == 2
    assert [root["candidate_root_source"] for root in payload["candidate_roots_considered"]] == ["selected", "retained"]
    assert payload["accepted_candidate_id"] == "retained-001"
    assert payload["accepted_candidate_source"] == "late_hardening_checkpoint"
    assert payload["accepted_candidate_root_source"] == "retained"


def test_expanded_candidate_pool_deduplicates_duplicate_candidate_roots() -> None:
    target_expr = Eml(Eml(Var("x"), Const(1.0)), Const(1.0))
    selected = _candidate_from_tree(
        _terminal_to_child_repairable_tree(),
        candidate_id="selected",
        source="legacy_final_snap",
    )
    fallback = _candidate_from_tree(
        _terminal_to_child_repairable_tree(),
        candidate_id="fallback-duplicate",
        source="hardening_checkpoint",
    )
    retained = _candidate_from_tree(
        _terminal_to_child_repairable_tree(),
        candidate_id="retained-duplicate",
        source="late_hardening_checkpoint",
    )
    fit = _fit_with_candidate_pool(selected=selected, fallback=fallback, candidates=(selected, fallback, retained))

    report = _run_candidate_pool_cleanup(fit, target_expr, config=RepairConfig.expanded_candidate_pool())
    payload = report.as_dict()

    assert payload["status"] == "repaired_candidate"
    assert payload["candidate_root_count"] == 1
    assert payload["candidate_roots_considered"][0]["candidate_id"] == "selected"
    assert payload["variant_count"] == payload["deduped_variant_count"]
    assert payload["variant_count"] >= 1
    assert {move["candidate_id"] for move in payload["moves_attempted"]} == {"selected"}


def test_candidate_pool_dedup_counts_follow_replacement_owner() -> None:
    target_expr = Eml(Eml(Var("x"), Const(1.0)), Const(1.0))
    selected = _candidate_from_tree(
        _terminal_to_child_repairable_tree(),
        candidate_id="selected",
        source="legacy_final_snap",
    )
    fallback = _candidate_from_tree(
        _constant_to_child_repairable_tree(),
        candidate_id="fallback-better-gap",
        source="hardening_checkpoint",
    )
    fit = _fit_with_candidate_pool(selected=selected, fallback=fallback)

    report = _run_candidate_pool_cleanup(fit, target_expr, config=RepairConfig.expanded_candidate_pool())
    payload = report.as_dict()
    by_root = {root["candidate_id"]: root for root in payload["variants_by_candidate_root"]}

    assert payload["status"] == "repaired_candidate"
    assert payload["accepted_candidate_id"] == "fallback-better-gap"
    assert payload["accepted_candidate_root_source"] == "fallback"
    assert by_root["fallback-better-gap"]["deduped_variant_count"] >= 1
    assert sum(root["deduped_variant_count"] for root in by_root.values()) == payload["deduped_variant_count"]


def test_candidate_pool_cleanup_preserves_subtree_move_provenance() -> None:
    target_expr = Eml(Eml(Var("x"), Const(1.0)), Const(1.0))
    selected = _candidate_from_tree(
        _constant_root_tree(),
        candidate_id="selected",
        source="legacy_final_snap",
        slot_alternatives=(),
    )
    fallback = _candidate_from_tree(
        _terminal_to_child_repairable_tree(),
        candidate_id="fallback",
        source="hardening_checkpoint",
    )
    fit = _fit_with_candidate_pool(selected=selected, fallback=fallback)

    report = _run_candidate_pool_cleanup(fit, target_expr, config=RepairConfig.expanded_candidate_pool())
    accepted = report.as_dict()["accepted_moves"][0]

    assert accepted["kind"] == "terminal_to_child"
    assert accepted["slot"] == "root.left"
    assert accepted["before"] == "var:x"
    assert accepted["after"] == "child"
    assert accepted["subtree_root"] == "root.L"
    assert accepted["descendant_assignments"] == [
        {"slot": "root.L.left", "choice": "var:x"},
        {"slot": "root.L.right", "choice": "const:1"},
    ]
    assert accepted["pruned_assignments"] == []
    assert accepted["candidate_root_source"] == "fallback"


def test_candidate_pool_cleanup_does_not_accept_unrecovered_variants() -> None:
    target_expr = Eml(Eml(Eml(Var("x"), Const(1.0)), Const(1.0)), Const(1.0))
    selected = _candidate_from_tree(
        _constant_root_tree(),
        candidate_id="selected",
        source="legacy_final_snap",
        slot_alternatives=(),
    )
    fallback = _candidate_from_tree(
        _terminal_to_child_repairable_tree(),
        candidate_id="fallback",
        source="hardening_checkpoint",
    )
    fit = _fit_with_candidate_pool(selected=selected, fallback=fallback)

    report = _run_candidate_pool_cleanup(fit, target_expr, config=RepairConfig.expanded_candidate_pool())
    payload = report.as_dict()

    assert payload["status"] == "not_repaired"
    assert payload["reason"] == "no_verified_slot_neighborhood"
    assert payload["accepted_moves"] == []
    assert payload["verification"] is None
    assert payload["repaired_ast"] is None
    assert payload["deduped_variant_count"] >= 1
    assert {move["verifier_status"] for move in payload["moves_attempted"]} == {"failed"}
