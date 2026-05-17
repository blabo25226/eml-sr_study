import json

import numpy as np
import pytest
import torch

from eml_symbolic_regression.expression import Geml, Var, ceml_s_expr, ipi_eml_expr
from eml_symbolic_regression.master_tree import EmbeddingConfig, EmbeddingError, SoftEMLTree, embed_expr_into_tree, expand_snap_neighborhood
from eml_symbolic_regression.semantics import ceml_s_operator, geml_operator, ipi_eml_operator, zeml_s_operator


def test_univariate_parameter_count_matches_paper():
    for depth in (1, 2, 3):
        tree = SoftEMLTree(depth, ("x",))
        assert tree.parameter_count() == tree.expected_univariate_parameter_count()
        assert tree.parameter_count() == 5 * (2**depth) - 6


def test_force_exp_snaps_to_paper_identity():
    tree = SoftEMLTree(1, ("x",))
    tree.force_exp("x")
    snap = tree.snap()
    x = np.linspace(-1.0, 1.0, 10)
    np.testing.assert_allclose(snap.expression.evaluate_numpy({"x": x}), np.exp(x), atol=1e-12)
    assert snap.min_margin > 0.99


@pytest.mark.parametrize(
    ("kind", "call"),
    (
        ("exp", lambda tree: tree.force_exp("x")),
        ("log", lambda tree: tree.force_log("x")),
        ("scaled_exp", lambda tree: tree.force_scaled_exp("x", -0.8)),
    ),
)
def test_centered_tree_rejects_raw_scaffold_helpers_without_same_family_witness(kind, call):
    tree = SoftEMLTree(1, ("x",), operator_family=ceml_s_operator(2.0))
    before = [(decision.path, decision.side, decision.choice) for decision in tree.snap().decisions]

    with pytest.raises(EmbeddingError) as exc:
        call(tree)

    after = [(decision.path, decision.side, decision.choice) for decision in tree.snap().decisions]
    assert exc.value.reason == "centered_family_same_family_witness_missing"
    assert kind in exc.value.detail
    assert "CEML_2" in exc.value.detail
    assert after == before


def test_centered_embedding_requires_matching_operator_family():
    tree = SoftEMLTree(1, ("x",), operator_family=zeml_s_operator(2.0))

    with pytest.raises(EmbeddingError, match="operator_family_mismatch"):
        tree.embed_expr(ceml_s_expr(tree.snap().expression.left, tree.snap().expression.right, s=2.0))


def test_geml_one_canonicalizes_to_raw_master_tree():
    tree = SoftEMLTree(1, ("x",), operator_family=geml_operator(1.0))
    snap = tree.snap()

    assert tree.operator_family.is_raw
    assert snap.expression.to_node()["kind"] == "eml"


def test_ipi_eml_tree_snaps_and_embeds_same_family_expression():
    tree = SoftEMLTree(1, ("x", "y"), operator_family=ipi_eml_operator())
    expression = ipi_eml_expr(Var("x"), Var("y"))

    result = embed_expr_into_tree(tree, expression, config=EmbeddingConfig(strength=40.0))
    snap = tree.snap()

    assert result.success
    assert result.round_trip_equal
    assert isinstance(snap.expression, Geml)
    assert snap.expression.operator.label == "ipi_eml"
    assert snap.expression.to_node()["operator"]["named_specialization"] == "ipi_eml"


def test_force_log_snaps_to_paper_identity():
    tree = SoftEMLTree(3, ("x",))
    tree.force_log("x")
    snap = tree.snap()
    x = np.linspace(0.25, 3.0, 10)
    np.testing.assert_allclose(snap.expression.evaluate_numpy({"x": x}), np.log(x), atol=1e-12)
    assert snap.expression.depth() == 3


def test_slot_catalog_exposes_child_choices():
    tree = SoftEMLTree(2, ("x",))
    catalog = tree.slot_catalog()
    assert catalog["root.left"] == ["const:1", "var:x", "child"]
    assert catalog["root.L.left"] == ["const:1", "var:x"]


def test_force_scaled_exp_snaps_to_exact_depth_nine_shape():
    tree = SoftEMLTree(9, ("x",), constants=(-0.8,))

    embedding = tree.force_scaled_exp("x", -0.8)
    snap = tree.snap()

    x = np.linspace(0.0, 3.0, 12)
    np.testing.assert_allclose(snap.expression.evaluate_numpy({"x": x}), np.exp(-0.8 * x), atol=1e-12)
    assert embedding.success
    assert embedding.round_trip_equal
    assert snap.expression.depth() == 9
    assert snap.active_node_count == 19
    assert snap.min_margin > 0.99
    assert embedding.snap.min_margin > 0.99


def test_force_scaled_exp_requires_coefficient_in_constant_bank():
    tree = SoftEMLTree(9, ("x",), constants=(1.0,))

    with pytest.raises(EmbeddingError, match="missing_constant"):
        tree.force_scaled_exp("x", -0.8)


def test_active_slot_alternatives_capture_replayable_child_subtree() -> None:
    tree = SoftEMLTree(2, ("x",))
    tree.set_slot("root", "right", "const:1", strength=40.0)
    tree.set_slot("root.L", "left", "var:x", strength=40.0)
    tree.set_slot("root.L", "right", "const:1", strength=40.0)

    with torch.no_grad():
        tree.root.left_logits.copy_(torch.tensor([0.0, 2.0, 1.8], dtype=torch.float64))

    alternatives = tree.active_slot_alternatives(top_k=2, max_slots=1)

    assert len(alternatives) == 1
    assert alternatives[0].slot == "root.left"
    assert alternatives[0].current_choice == "var:x"
    assert alternatives[0].current_margin < 0.2
    assert [item.choice for item in alternatives[0].alternatives] == ["child", "const:1"]
    assert alternatives[0].alternatives[0].subtree_root == "root.L"
    assert [item.as_dict() for item in alternatives[0].alternatives[0].descendant_assignments] == [
        {"slot": "root.L.left", "choice": "var:x"},
        {"slot": "root.L.right", "choice": "const:1"},
    ]


def test_expand_snap_neighborhood_deduplicates_parent_overrides() -> None:
    tree = SoftEMLTree(2, ("x",))
    tree.set_slot("root", "left", "child", strength=40.0)
    tree.set_slot("root", "right", "const:1", strength=40.0)
    tree.set_slot("root.L", "left", "var:x", strength=40.0)
    tree.set_slot("root.L", "right", "const:1", strength=40.0)

    with torch.no_grad():
        tree.root.left_logits.copy_(torch.tensor([0.0, 1.8, 2.0], dtype=torch.float64))
        tree.root.left_child.left_logits.copy_(torch.tensor([1.8, 2.0], dtype=torch.float64))

    snap = tree.snap()
    variants = expand_snap_neighborhood(
        snap,
        tree.active_slot_alternatives(top_k=1, max_slots=2),
        depth=2,
        variables=("x",),
        constants=(1.0,),
        beam_width=8,
        max_moves=2,
    )

    serialized = [json.dumps(item.expression.to_document(), sort_keys=True) for item in variants]

    assert len(serialized) == len(set(serialized))
    terminal_variant = [
        item
        for item in variants
        if item.moves and item.moves[0].slot == "root.left" and item.moves[0].after == "var:x"
    ]
    assert len(terminal_variant) == 1
    assert len(terminal_variant[0].moves) == 1
