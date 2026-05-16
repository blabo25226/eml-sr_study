"""Verifier-gated local repair for perturbed true-tree near misses."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .expression import CenteredEml, Expr
from .master_tree import EmbeddingResult, NeighborhoodMove, SoftEMLTree, expand_snap_neighborhood
from .optimize import ExactCandidate, FitResult
from .verify import DataSplit, VerificationReport, verify_candidate


@dataclass(frozen=True)
class RepairConfig:
    max_target_reverts: int = 8
    strength: float = 30.0
    allow_target_slot_reverts: bool = True
    allow_catalog_alternatives: bool = False
    cleanup_top_k: int = 2
    cleanup_max_slots: int = 4
    cleanup_beam_width: int = 8
    cleanup_max_moves: int = 2
    cleanup_candidate_sources: tuple[str, ...] = ("selected",)

    @classmethod
    def expanded_candidate_pool(cls) -> "RepairConfig":
        return cls(
            cleanup_top_k=3,
            cleanup_max_slots=8,
            cleanup_beam_width=32,
            cleanup_max_moves=3,
            cleanup_candidate_sources=("selected", "fallback", "retained"),
        )


@dataclass(frozen=True)
class RepairMove:
    kind: str
    slot: str
    before: str
    after: str
    source: str
    accepted: bool
    verifier_status: str | None = None
    descendant_assignments: tuple[dict[str, str], ...] = ()
    pruned_assignments: tuple[dict[str, str], ...] = ()
    subtree_root: str | None = None
    slot_margin: float | None = None
    probability_gap: float | None = None
    rank: int | None = None
    candidate_id: str | None = None
    candidate_source: str | None = None
    candidate_root_source: str | None = None

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "kind": self.kind,
            "slot": self.slot,
            "before": self.before,
            "after": self.after,
            "source": self.source,
            "accepted": self.accepted,
            "verifier_status": self.verifier_status,
            "descendant_assignments": [dict(assignment) for assignment in self.descendant_assignments],
            "pruned_assignments": [dict(assignment) for assignment in self.pruned_assignments],
            "subtree_root": self.subtree_root,
        }
        if self.slot_margin is not None:
            payload["slot_margin"] = self.slot_margin
        if self.probability_gap is not None:
            payload["probability_gap"] = self.probability_gap
        if self.rank is not None:
            payload["rank"] = self.rank
        if self.candidate_id is not None:
            payload["candidate_id"] = self.candidate_id
        if self.candidate_source is not None:
            payload["candidate_source"] = self.candidate_source
        if self.candidate_root_source is not None:
            payload["candidate_root_source"] = self.candidate_root_source
        return payload


@dataclass(frozen=True)
class RepairReport:
    status: str
    original_status: str
    return_kind: str
    moves_attempted: tuple[RepairMove, ...]
    accepted_moves: tuple[RepairMove, ...]
    repaired_expression: Expr | None
    verification: VerificationReport | None
    reason: str
    variant_count: int = 0
    candidate_roots_considered: tuple[dict[str, Any], ...] = ()
    candidate_root_count: int = 0
    variants_by_candidate_root: tuple[dict[str, Any], ...] = ()
    deduped_variant_count: int = 0
    accepted_candidate_id: str | None = None
    accepted_candidate_source: str | None = None
    accepted_candidate_root_source: str | None = None

    def as_dict(self) -> dict[str, Any]:
        verified = self.status == "repaired_candidate" and self.verification is not None and self.verification.status == "recovered"
        repaired_ast = (
            self.repaired_expression.to_document(source="repaired_candidate")
            if verified and self.repaired_expression is not None
            else None
        )
        return {
            "status": self.status,
            "original_status": self.original_status,
            "return_kind": self.return_kind,
            "moves_attempted": [move.as_dict() for move in self.moves_attempted],
            "accepted_moves": [move.as_dict() for move in self.accepted_moves],
            "repaired_ast": repaired_ast,
            "verification": self.verification.as_dict() if self.verification is not None else None,
            "reason": self.reason,
            "variant_count": self.variant_count,
            "candidate_roots_considered": [dict(root) for root in self.candidate_roots_considered],
            "candidate_root_count": self.candidate_root_count,
            "variants_by_candidate_root": [dict(root) for root in self.variants_by_candidate_root],
            "deduped_variant_count": self.deduped_variant_count,
            "accepted_candidate_id": self.accepted_candidate_id,
            "accepted_candidate_source": self.accepted_candidate_source,
            "accepted_candidate_root_source": self.accepted_candidate_root_source,
        }


@dataclass(frozen=True)
class _CleanupRoot:
    candidate: ExactCandidate
    root_source: str
    root_order: int
    ast_key: str


@dataclass(frozen=True)
class _CleanupVariant:
    expression: Expr
    moves: tuple[RepairMove, ...]
    root: _CleanupRoot


def cleanup_failed_candidate(
    fit: FitResult,
    *,
    depth: int,
    variables: tuple[str, ...],
    constants: tuple[complex, ...],
    verification_splits: list[DataSplit],
    tolerance: float,
    config: RepairConfig | None = None,
    original_status: str,
    return_kind: str,
) -> RepairReport:
    config = config or RepairConfig()
    roots = _cleanup_candidate_roots(fit, config)
    candidate_roots = tuple(_candidate_root_payload(root) for root in roots)
    if not roots:
        return RepairReport(
            status="not_repaired",
            original_status=original_status,
            return_kind=return_kind,
            moves_attempted=(),
            accepted_moves=(),
            repaired_expression=None,
            verification=None,
            reason="missing_slot_alternatives",
            candidate_roots_considered=candidate_roots,
            candidate_root_count=len(candidate_roots),
        )

    variant_counts_by_root: dict[int, int] = {}
    deduped_variants: dict[str, _CleanupVariant] = {}
    roots_with_alternatives = 0
    for root in roots:
        bounded = _bounded_slot_alternatives(root.candidate, config)
        variants = ()
        if bounded:
            roots_with_alternatives += 1
            variants = expand_snap_neighborhood(
                root.candidate.snap,
                bounded,
                depth=depth,
                variables=variables,
                constants=constants,
                operator_family=(
                    root.candidate.snap.expression.operator
                    if isinstance(root.candidate.snap.expression, CenteredEml)
                    else None
                ),
                beam_width=config.cleanup_beam_width,
                max_moves=config.cleanup_max_moves,
                max_slots=config.cleanup_max_slots,
                strength=config.strength,
            )
            for variant in variants:
                moves = tuple(
                    _repair_move_from_neighborhood(
                        move,
                        candidate_id=root.candidate.candidate_id,
                        candidate_source=root.candidate.source,
                        candidate_root_source=root.root_source,
                    )
                    for move in variant.moves
                )
                cleanup_variant = _CleanupVariant(expression=variant.expression, moves=moves, root=root)
                key = _expression_dedup_key(variant.expression)
                existing = deduped_variants.get(key)
                if existing is None:
                    deduped_variants[key] = cleanup_variant
                elif _cleanup_variant_dedup_key(cleanup_variant) < _cleanup_variant_dedup_key(existing):
                    deduped_variants[key] = cleanup_variant
        variant_counts_by_root[root.root_order] = len(variants)

    deduped_variant_count = len(deduped_variants)
    deduped_counts_by_root: dict[int, int] = {root.root_order: 0 for root in roots}
    for variant in deduped_variants.values():
        deduped_counts_by_root[variant.root.root_order] += 1
    variants_by_root = tuple(
        _candidate_root_variant_payload(
            root,
            variant_count=variant_counts_by_root.get(root.root_order, 0),
            deduped_variant_count=deduped_counts_by_root.get(root.root_order, 0),
        )
        for root in roots
    )
    if roots_with_alternatives == 0:
        return RepairReport(
            status="not_repaired",
            original_status=original_status,
            return_kind=return_kind,
            moves_attempted=(),
            accepted_moves=(),
            repaired_expression=None,
            verification=None,
            reason="missing_slot_alternatives",
            candidate_roots_considered=candidate_roots,
            candidate_root_count=len(candidate_roots),
            variants_by_candidate_root=variants_by_root,
            deduped_variant_count=deduped_variant_count,
        )
    if not deduped_variants:
        return RepairReport(
            status="not_repaired",
            original_status=original_status,
            return_kind=return_kind,
            moves_attempted=(),
            accepted_moves=(),
            repaired_expression=None,
            verification=None,
            reason="empty_slot_neighborhood",
            variant_count=0,
            candidate_roots_considered=candidate_roots,
            candidate_root_count=len(candidate_roots),
            variants_by_candidate_root=variants_by_root,
            deduped_variant_count=deduped_variant_count,
        )

    attempted: list[RepairMove] = []
    evaluated: list[tuple[tuple[RepairMove, ...], Expr, VerificationReport, _CleanupRoot]] = []
    for variant in sorted(deduped_variants.values(), key=_cleanup_variant_dedup_key):
        verification = verify_candidate(variant.expression, verification_splits, tolerance=tolerance)
        moves = tuple(
            _with_verification(move, verification.status, accepted=verification.status == "recovered") for move in variant.moves
        )
        attempted.extend(moves)
        evaluated.append((moves, variant.expression, verification, variant.root))

    best_moves, best_expression, best_verification, best_root = min(
        evaluated,
        key=lambda item: _cleanup_ranking_key(item[2], item[1], item[0])
        + (item[3].root_order, item[3].candidate.candidate_id),
    )
    if best_verification.status == "recovered":
        return RepairReport(
            status="repaired_candidate",
            original_status=original_status,
            return_kind=return_kind,
            moves_attempted=tuple(attempted),
            accepted_moves=best_moves,
            repaired_expression=best_expression,
            verification=best_verification,
            reason="verified_slot_neighborhood",
            variant_count=deduped_variant_count,
            candidate_roots_considered=candidate_roots,
            candidate_root_count=len(candidate_roots),
            variants_by_candidate_root=variants_by_root,
            deduped_variant_count=deduped_variant_count,
            accepted_candidate_id=best_root.candidate.candidate_id,
            accepted_candidate_source=best_root.candidate.source,
            accepted_candidate_root_source=best_root.root_source,
        )

    return RepairReport(
        status="not_repaired",
        original_status=original_status,
        return_kind=return_kind,
        moves_attempted=tuple(attempted),
        accepted_moves=(),
        repaired_expression=None,
        verification=None,
        reason="no_verified_slot_neighborhood",
        variant_count=deduped_variant_count,
        candidate_roots_considered=candidate_roots,
        candidate_root_count=len(candidate_roots),
        variants_by_candidate_root=variants_by_root,
        deduped_variant_count=deduped_variant_count,
    )


def repair_perturbed_candidate(
    fit: FitResult,
    *,
    target_expr: Expr,
    embedding: EmbeddingResult,
    depth: int,
    variables: tuple[str, ...],
    constants: tuple[complex, ...],
    verification_splits: list[DataSplit],
    tolerance: float,
    config: RepairConfig | None = None,
    original_status: str,
    return_kind: str,
) -> RepairReport:
    config = config or RepairConfig()
    if config.allow_catalog_alternatives:
        return RepairReport(
            status="not_repaired",
            original_status=original_status,
            return_kind=return_kind,
            moves_attempted=(),
            accepted_moves=(),
            repaired_expression=None,
            verification=None,
            reason="catalog_alternatives_disabled",
            variant_count=0,
        )
    if not config.allow_target_slot_reverts:
        return RepairReport(
            status="not_repaired",
            original_status=original_status,
            return_kind=return_kind,
            moves_attempted=(),
            accepted_moves=(),
            repaired_expression=None,
            verification=None,
            reason="target_slot_reverts_disabled",
            variant_count=0,
        )

    snapped_slot_map = _snapped_slot_map(fit)
    target_slot_map = _target_slot_map(embedding)
    moves = _target_neighborhood_moves(snapped_slot_map, target_slot_map)
    attempted: list[RepairMove] = []

    for move in moves:
        candidate = _candidate_from_moves(
            snapped_slot_map,
            (move,),
            depth=depth,
            variables=variables,
            constants=constants,
            strength=config.strength,
        )
        verification = verify_candidate(candidate, verification_splits, tolerance=tolerance)
        attempted_move = _with_verification(move, verification.status, accepted=verification.status == "recovered")
        attempted.append(attempted_move)
        if verification.status == "recovered":
            return RepairReport(
                status="repaired_candidate",
                original_status=original_status,
                return_kind=return_kind,
                moves_attempted=tuple(attempted),
                accepted_moves=(attempted_move,),
                repaired_expression=candidate,
                verification=verification,
                reason="verified_local_move",
                variant_count=len(moves),
            )

    if len(moves) > 1 and len(moves) <= config.max_target_reverts:
        candidate = _candidate_from_moves(
            snapped_slot_map,
            moves,
            depth=depth,
            variables=variables,
            constants=constants,
            strength=config.strength,
        )
        verification = verify_candidate(candidate, verification_splits, tolerance=tolerance)
        accepted = verification.status == "recovered"
        combined_moves = tuple(_with_verification(move, verification.status, accepted=accepted) for move in moves)
        attempted.extend(combined_moves)
        if accepted:
            return RepairReport(
                status="repaired_candidate",
                original_status=original_status,
                return_kind=return_kind,
                moves_attempted=tuple(attempted),
                accepted_moves=combined_moves,
                repaired_expression=candidate,
                verification=verification,
                reason="verified_target_neighborhood",
                variant_count=len(moves),
            )

    return RepairReport(
        status="not_repaired",
        original_status=original_status,
        return_kind=return_kind,
        moves_attempted=tuple(attempted),
        accepted_moves=(),
        repaired_expression=None,
        verification=None,
        reason="no_verified_local_move",
        variant_count=len(moves),
    )


def _cleanup_candidate_roots(fit: FitResult, config: RepairConfig) -> tuple[_CleanupRoot, ...]:
    enabled = set(config.cleanup_candidate_sources)
    roots: list[_CleanupRoot] = []
    seen: set[str] = set()

    def add(candidate: ExactCandidate | None, root_source: str) -> None:
        if candidate is None:
            return
        ast_key = _expression_dedup_key(candidate.snap.expression)
        if ast_key in seen:
            return
        seen.add(ast_key)
        roots.append(
            _CleanupRoot(
                candidate=candidate,
                root_source=root_source,
                root_order=len(roots),
                ast_key=ast_key,
            )
        )

    if "selected" in enabled:
        add(fit.selected_candidate, "selected")
    if "fallback" in enabled:
        add(fit.fallback_candidate, "fallback")
    if "retained" in enabled:
        for candidate in fit.candidates:
            add(candidate, "retained")

    return tuple(roots)


def _bounded_slot_alternatives(candidate: ExactCandidate, config: RepairConfig) -> tuple[Any, ...]:
    slot_alternatives = tuple(
        item
        for item in candidate.slot_alternatives[: config.cleanup_max_slots]
        if item.alternatives[: config.cleanup_top_k]
    )
    return tuple(
        type(group)(
            slot=group.slot,
            current_choice=group.current_choice,
            current_probability=group.current_probability,
            current_margin=group.current_margin,
            alternatives=group.alternatives[: config.cleanup_top_k],
        )
        for group in slot_alternatives
    )


def _candidate_root_payload(root: _CleanupRoot) -> dict[str, Any]:
    return {
        "candidate_id": root.candidate.candidate_id,
        "candidate_source": root.candidate.source,
        "candidate_root_source": root.root_source,
        "root_order": root.root_order,
        "slot_alternative_count": len(root.candidate.slot_alternatives),
    }


def _candidate_root_variant_payload(
    root: _CleanupRoot,
    *,
    variant_count: int,
    deduped_variant_count: int,
) -> dict[str, Any]:
    payload = _candidate_root_payload(root)
    payload["variant_count"] = variant_count
    payload["deduped_variant_count"] = deduped_variant_count
    return payload


def _expression_dedup_key(expression: Expr) -> str:
    return json.dumps(expression.to_document(), sort_keys=True)


def _cleanup_variant_dedup_key(variant: _CleanupVariant) -> tuple[Any, ...]:
    return (
        len(variant.moves),
        sum(move.probability_gap or 0.0 for move in variant.moves),
        variant.root.root_order,
        variant.root.candidate.candidate_id,
        tuple(move.slot for move in variant.moves),
        tuple(move.after for move in variant.moves),
    )


def _snapped_slot_map(fit: FitResult) -> dict[str, str]:
    return {f"{decision.path}.{decision.side}": decision.choice for decision in fit.snap.decisions}


def _target_slot_map(embedding: EmbeddingResult) -> dict[str, str]:
    return {assignment.slot: assignment.choice for assignment in embedding.assignments}


def _target_neighborhood_moves(snapped: dict[str, str], target: dict[str, str]) -> tuple[RepairMove, ...]:
    moves: list[RepairMove] = []
    covered_descendants: set[str] = set()

    for slot in _sorted_slots(sorted(set(snapped) | set(target))):
        before = snapped.get(slot)
        after = target.get(slot)
        if before == "child" and after == "child":
            subtree_root = _child_root(slot)
            target_descendants = _descendant_assignments(target, subtree_root)
            snapped_descendants = _descendant_assignments(snapped, subtree_root)
            if target_descendants and target_descendants != snapped_descendants:
                moves.append(
                    RepairMove(
                        kind="child_subtree_replacement",
                        slot=slot,
                        before="child",
                        after="child",
                        source="embedded_target_slot",
                        accepted=False,
                        descendant_assignments=target_descendants,
                        pruned_assignments=_pruned_assignments(snapped, target, subtree_root),
                        subtree_root=subtree_root,
                    )
                )
                covered_descendants.update(assignment["slot"] for assignment in target_descendants)
                covered_descendants.update(assignment["slot"] for assignment in snapped_descendants)

    for slot in _sorted_slots(sorted(set(snapped) | set(target))):
        if slot in covered_descendants:
            continue
        before = snapped.get(slot)
        after = target.get(slot)
        if before == after or after is None:
            continue
        if before is None:
            moves.append(
                RepairMove(
                    kind="slot_revert",
                    slot=slot,
                    before="<unset>",
                    after=after,
                    source="embedded_target_slot",
                    accepted=False,
                )
            )
            continue
        if before != "child" and after == "child":
            subtree_root = _child_root(slot)
            descendant_assignments = _descendant_assignments(target, subtree_root)
            moves.append(
                RepairMove(
                    kind="terminal_to_child",
                    slot=slot,
                    before=before,
                    after=after,
                    source="embedded_target_slot",
                    accepted=False,
                    descendant_assignments=descendant_assignments,
                    subtree_root=subtree_root,
                )
            )
            covered_descendants.update(assignment["slot"] for assignment in descendant_assignments)
            continue
        if before == "child" and after != "child":
            subtree_root = _child_root(slot)
            moves.append(
                RepairMove(
                    kind="child_to_terminal",
                    slot=slot,
                    before=before,
                    after=after,
                    source="embedded_target_slot",
                    accepted=False,
                    pruned_assignments=_descendant_assignments(snapped, subtree_root),
                    subtree_root=subtree_root,
                )
            )
            continue
        moves.append(
            RepairMove(
                kind="slot_revert",
                slot=slot,
                before=before,
                after=after,
                source="embedded_target_slot",
                accepted=False,
            )
        )

    return tuple(moves)


def _candidate_from_moves(
    snapped_slot_map: dict[str, str],
    moves: tuple[RepairMove, ...],
    *,
    depth: int,
    variables: tuple[str, ...],
    constants: tuple[complex, ...],
    strength: float,
) -> Expr:
    slot_map = dict(snapped_slot_map)
    for move in moves:
        slot_map[move.slot] = move.after
        for assignment in move.descendant_assignments:
            slot_map[assignment["slot"]] = assignment["choice"]

    tree = SoftEMLTree(depth, variables, constants)
    for slot, choice in _slot_items_for_replay(slot_map):
        node_path, side = slot.rsplit(".", 1)
        tree.set_slot(node_path, side, choice, strength=strength)
    return tree.snap().expression


def _with_verification(move: RepairMove, verifier_status: str, *, accepted: bool) -> RepairMove:
    return RepairMove(
        kind=move.kind,
        slot=move.slot,
        before=move.before,
        after=move.after,
        source=move.source,
        accepted=accepted,
        verifier_status=verifier_status,
        descendant_assignments=move.descendant_assignments,
        pruned_assignments=move.pruned_assignments,
        subtree_root=move.subtree_root,
        slot_margin=move.slot_margin,
        probability_gap=move.probability_gap,
        rank=move.rank,
        candidate_id=move.candidate_id,
        candidate_source=move.candidate_source,
        candidate_root_source=move.candidate_root_source,
    )


def _repair_move_from_neighborhood(
    move: NeighborhoodMove,
    *,
    candidate_id: str | None = None,
    candidate_source: str | None = None,
    candidate_root_source: str | None = None,
) -> RepairMove:
    return RepairMove(
        kind=_move_kind(move.before, move.after),
        slot=move.slot,
        before=move.before,
        after=move.after,
        source="slot_alternative",
        accepted=False,
        descendant_assignments=tuple(assignment.as_dict() for assignment in move.descendant_assignments),
        pruned_assignments=tuple(assignment.as_dict() for assignment in move.pruned_assignments),
        subtree_root=move.subtree_root,
        slot_margin=move.slot_margin,
        probability_gap=move.probability_gap,
        rank=move.rank,
        candidate_id=candidate_id,
        candidate_source=candidate_source,
        candidate_root_source=candidate_root_source,
    )


def _move_kind(before: str, after: str) -> str:
    if before != "child" and after == "child":
        return "terminal_to_child"
    if before == "child" and after != "child":
        return "child_to_terminal"
    if before == "child" and after == "child":
        return "child_subtree_replacement"
    return "slot_revert"


def _cleanup_ranking_key(
    verification: VerificationReport,
    expression: Expr,
    moves: tuple[RepairMove, ...],
) -> tuple[Any, ...]:
    heldout_error = _verification_group_error(verification, lambda name: "hold" in name or "valid" in name)
    extrapolation_error = _verification_group_error(verification, lambda name: "extra" in name)
    return (
        _verification_status_rank(verification.status),
        extrapolation_error,
        verification.high_precision_max_error,
        heldout_error,
        expression.node_count(),
        len(moves),
        sum(move.probability_gap or 0.0 for move in moves),
    )


def _verification_group_error(report: VerificationReport, predicate: Any) -> float:
    values = [result.max_abs_error for result in report.split_results if predicate(result.name.lower())]
    return float(max(values)) if values else 0.0


def _verification_status_rank(status: str | None) -> int:
    return {
        "recovered": 0,
        "verified_showcase": 1,
        "failed": 2,
        None: 3,
    }.get(status, 3)


def _child_root(slot: str) -> str:
    node_path, side = slot.rsplit(".", 1)
    return f"{node_path}.{'L' if side == 'left' else 'R'}"


def _descendant_assignments(slot_map: dict[str, str], subtree_root: str) -> tuple[dict[str, str], ...]:
    return tuple({"slot": slot, "choice": slot_map[slot]} for slot in _sorted_slots(slot for slot in slot_map if slot.startswith(f"{subtree_root}.")))


def _pruned_assignments(snapped: dict[str, str], target: dict[str, str], subtree_root: str) -> tuple[dict[str, str], ...]:
    pruned = [slot for slot in snapped if slot.startswith(f"{subtree_root}.") and slot not in target]
    return tuple({"slot": slot, "choice": snapped[slot]} for slot in _sorted_slots(pruned))


def _slot_items_for_replay(slot_map: dict[str, str]) -> tuple[tuple[str, str], ...]:
    return tuple((slot, slot_map[slot]) for slot in _sorted_slots(slot_map))


def _sorted_slots(slots: Any) -> list[str]:
    return sorted(slots, key=lambda slot: (slot.count("."), slot))
