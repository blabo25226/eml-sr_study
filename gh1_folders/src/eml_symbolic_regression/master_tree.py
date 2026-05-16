"""Complete depth-bounded differentiable EML master trees."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import torch

from .expression import CenteredEml, Const, Eml, Expr, Geml, Var
from .semantics import AnomalyStats, EmlOperator, TrainingSemanticsConfig, as_complex_tensor, centered_eml_torch, raw_eml_operator
from .witnesses import CENTERED_FAMILY_SAME_FAMILY_WITNESS_MISSING, scaffold_witness_for


def _canonical_constant(value: complex) -> complex:
    value = complex(value)
    return complex(0.0 if abs(value.real) < 1e-15 else value.real, 0.0 if abs(value.imag) < 1e-15 else value.imag)


def normalize_constants(constants: tuple[complex, ...] = (1.0,)) -> tuple[complex, ...]:
    seen: list[complex] = []
    for value in (1.0, *constants):
        canonical = _canonical_constant(value)
        if not any(abs(canonical - existing) <= 1e-12 for existing in seen):
            seen.append(canonical)
    return tuple(sorted(seen, key=lambda item: (item.real, item.imag)))


def constant_label(value: complex) -> str:
    value = _canonical_constant(value)
    if abs(value.imag) < 1e-15:
        real = float(value.real)
        body = str(int(real)) if real.is_integer() else repr(real)
    else:
        body = repr(complex(value))
    return f"const:{body}"


def parse_constant_label(label: str) -> complex:
    if not label.startswith("const:"):
        raise ValueError(f"Not a constant label: {label}")
    body = label.split(":", 1)[1]
    return _canonical_constant(complex(float(body)) if "j" not in body else complex(body))


def expressions_equal(left: Expr, right: Expr, *, constant_tolerance: float = 1e-12) -> bool:
    if isinstance(left, Const) and isinstance(right, Const):
        return abs(complex(left.value) - complex(right.value)) <= constant_tolerance
    if isinstance(left, Var) and isinstance(right, Var):
        return left.name == right.name
    if isinstance(left, Eml) and isinstance(right, Eml):
        return expressions_equal(left.left, right.left, constant_tolerance=constant_tolerance) and expressions_equal(
            left.right, right.right, constant_tolerance=constant_tolerance
        )
    if isinstance(left, CenteredEml) and isinstance(right, CenteredEml):
        return left.operator == right.operator and expressions_equal(
            left.left,
            right.left,
            constant_tolerance=constant_tolerance,
        ) and expressions_equal(left.right, right.right, constant_tolerance=constant_tolerance)
    if isinstance(left, Geml) and isinstance(right, Geml):
        return left.operator == right.operator and expressions_equal(
            left.left,
            right.left,
            constant_tolerance=constant_tolerance,
        ) and expressions_equal(left.right, right.right, constant_tolerance=constant_tolerance)
    return False


@dataclass(frozen=True)
class SnapDecision:
    path: str
    side: str
    choice: str
    probability: float
    margin: float


@dataclass(frozen=True)
class SnapResult:
    expression: Expr
    decisions: list[SnapDecision]
    min_margin: float
    active_node_count: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "min_margin": self.min_margin,
            "active_node_count": self.active_node_count,
            "decisions": [decision.__dict__ for decision in self.decisions],
            "ast": self.expression.to_document(),
        }


@dataclass(frozen=True)
class ReplayAssignment:
    slot: str
    choice: str

    def as_dict(self) -> dict[str, str]:
        return {"slot": self.slot, "choice": self.choice}


@dataclass(frozen=True)
class SlotAlternative:
    choice: str
    probability: float
    probability_gap: float
    rank: int
    descendant_assignments: tuple[ReplayAssignment, ...] = ()
    subtree_root: str | None = None

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "choice": self.choice,
            "probability": self.probability,
            "probability_gap": self.probability_gap,
            "rank": self.rank,
        }
        if self.descendant_assignments:
            payload["descendant_assignments"] = [assignment.as_dict() for assignment in self.descendant_assignments]
        if self.subtree_root is not None:
            payload["subtree_root"] = self.subtree_root
        return payload


@dataclass(frozen=True)
class ActiveSlotAlternatives:
    slot: str
    current_choice: str
    current_probability: float
    current_margin: float
    alternatives: tuple[SlotAlternative, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "slot": self.slot,
            "current_choice": self.current_choice,
            "current_probability": self.current_probability,
            "current_margin": self.current_margin,
            "alternatives": [alternative.as_dict() for alternative in self.alternatives],
        }


@dataclass(frozen=True)
class NeighborhoodMove:
    slot: str
    before: str
    after: str
    slot_margin: float
    probability_gap: float
    rank: int
    descendant_assignments: tuple[ReplayAssignment, ...] = ()
    pruned_assignments: tuple[ReplayAssignment, ...] = ()
    subtree_root: str | None = None

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "slot": self.slot,
            "before": self.before,
            "after": self.after,
            "slot_margin": self.slot_margin,
            "probability_gap": self.probability_gap,
            "rank": self.rank,
        }
        if self.descendant_assignments:
            payload["descendant_assignments"] = [assignment.as_dict() for assignment in self.descendant_assignments]
        if self.pruned_assignments:
            payload["pruned_assignments"] = [assignment.as_dict() for assignment in self.pruned_assignments]
        if self.subtree_root is not None:
            payload["subtree_root"] = self.subtree_root
        return payload


@dataclass(frozen=True)
class NeighborhoodVariant:
    expression: Expr
    moves: tuple[NeighborhoodMove, ...]
    heuristic_gap: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "moves": [move.as_dict() for move in self.moves],
            "heuristic_gap": self.heuristic_gap,
            "ast": self.expression.to_document(source="snap_neighborhood_candidate"),
        }


@dataclass(frozen=True)
class EmbeddingConfig:
    strength: float = 30.0


@dataclass(frozen=True)
class EmbeddingAssignment:
    slot: str
    choice: str

    def as_dict(self) -> dict[str, str]:
        return {"slot": self.slot, "choice": self.choice}


@dataclass(frozen=True)
class EmbeddingResult:
    success: bool
    assignments: tuple[EmbeddingAssignment, ...]
    snap: SnapResult
    round_trip_equal: bool
    diagnostics: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "assignments": [assignment.as_dict() for assignment in self.assignments],
            "snap": self.snap.as_dict(),
            "round_trip_equal": self.round_trip_equal,
            "diagnostics": list(self.diagnostics),
        }


class EmbeddingError(ValueError):
    def __init__(self, reason: str, detail: str) -> None:
        self.reason = reason
        self.detail = detail
        super().__init__(f"{reason}: {detail}")

    def as_dict(self) -> dict[str, str]:
        return {"reason": self.reason, "detail": self.detail}


class _SoftNode(torch.nn.Module):
    def __init__(
        self,
        depth: int,
        variables: tuple[str, ...],
        constants: tuple[complex, ...],
        operator_family: EmlOperator,
        path: str = "root",
    ) -> None:
        super().__init__()
        if depth < 1:
            raise ValueError("EML master-node depth must be >= 1")
        self.depth = depth
        self.variables = variables
        self.constants = constants
        self.operator_family = operator_family
        self.path = path
        self.left_child = _SoftNode(depth - 1, variables, constants, operator_family, f"{path}.L") if depth > 1 else None
        self.right_child = _SoftNode(depth - 1, variables, constants, operator_family, f"{path}.R") if depth > 1 else None
        choices = len(self.base_labels) + (1 if depth > 1 else 0)
        self.left_logits = torch.nn.Parameter(torch.zeros(choices, dtype=torch.float64))
        self.right_logits = torch.nn.Parameter(torch.zeros(choices, dtype=torch.float64))

    @property
    def base_labels(self) -> list[str]:
        return [*[constant_label(value) for value in self.constants], *[f"var:{name}" for name in self.variables]]

    @property
    def labels(self) -> list[str]:
        labels = self.base_labels
        return [*labels, "child"] if self.depth > 1 else labels

    def reset_parameters(self, generator: torch.Generator | None = None, scale: float = 0.05) -> None:
        with torch.no_grad():
            self.left_logits.normal_(0.0, scale, generator=generator)
            self.right_logits.normal_(0.0, scale, generator=generator)
        if self.left_child is not None:
            self.left_child.reset_parameters(generator, scale)
        if self.right_child is not None:
            self.right_child.reset_parameters(generator, scale)

    def slot_catalog(self) -> dict[str, list[str]]:
        catalog = {
            f"{self.path}.left": self.labels,
            f"{self.path}.right": self.labels,
        }
        if self.left_child is not None:
            catalog.update(self.left_child.slot_catalog())
        if self.right_child is not None:
            catalog.update(self.right_child.slot_catalog())
        return catalog

    def _base_tensors(self, context: Mapping[str, torch.Tensor]) -> list[torch.Tensor]:
        first = next(iter(context.values()))
        values = [torch.zeros_like(first, dtype=torch.complex128) + value for value in self.constants]
        values.extend(context[name].to(dtype=torch.complex128) for name in self.variables)
        return values

    def _slot_value(
        self,
        logits: torch.Tensor,
        candidates: list[torch.Tensor],
        temperature: float,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        probs = torch.softmax(logits / temperature, dim=0).to(dtype=torch.complex128)
        value = torch.zeros_like(candidates[0], dtype=torch.complex128)
        for probability, candidate in zip(probs, candidates):
            value = value + probability * candidate
        return value, probs

    def forward(
        self,
        context: Mapping[str, torch.Tensor],
        *,
        temperature: float,
        training_semantics: bool,
        stats: AnomalyStats | None,
        semantics: TrainingSemanticsConfig | None = None,
    ) -> torch.Tensor:
        left_candidates = self._base_tensors(context)
        right_candidates = self._base_tensors(context)
        if self.left_child is not None:
            left_candidates.append(
                self.left_child(
                    context,
                    temperature=temperature,
                    training_semantics=training_semantics,
                    stats=stats,
                    semantics=semantics,
                )
            )
        if self.right_child is not None:
            right_candidates.append(
                self.right_child(
                    context,
                    temperature=temperature,
                    training_semantics=training_semantics,
                    stats=stats,
                    semantics=semantics,
                )
            )
        left, _ = self._slot_value(self.left_logits, left_candidates, temperature)
        right, _ = self._slot_value(self.right_logits, right_candidates, temperature)
        return centered_eml_torch(
            left,
            right,
            operator=self.operator_family,
            training=training_semantics,
            semantics=semantics,
            stats=stats,
            node=self.path,
        )

    def gate_entropy(self, temperature: float = 1.0) -> torch.Tensor:
        entropy = torch.tensor(0.0, dtype=torch.float64, device=self.left_logits.device)
        for logits in (self.left_logits, self.right_logits):
            probs = torch.softmax(logits / temperature, dim=0)
            entropy = entropy - torch.sum(probs * torch.log(probs + 1e-12))
        if self.left_child is not None:
            entropy = entropy + self.left_child.gate_entropy(temperature)
        if self.right_child is not None:
            entropy = entropy + self.right_child.gate_entropy(temperature)
        return entropy

    def expected_child_use(self, temperature: float = 1.0) -> torch.Tensor:
        if self.depth == 1:
            return torch.tensor(0.0, dtype=torch.float64, device=self.left_logits.device)
        value = torch.tensor(0.0, dtype=torch.float64, device=self.left_logits.device)
        value = value + torch.softmax(self.left_logits / temperature, dim=0)[-1]
        value = value + torch.softmax(self.right_logits / temperature, dim=0)[-1]
        if self.left_child is not None:
            value = value + self.left_child.expected_child_use(temperature)
        if self.right_child is not None:
            value = value + self.right_child.expected_child_use(temperature)
        return value

    def _snap_slot(self, side: str, decisions: list[SnapDecision]) -> Expr:
        logits = self.left_logits if side == "left" else self.right_logits
        probs = torch.softmax(logits.detach(), dim=0)
        order = torch.argsort(probs, descending=True)
        index = int(order[0].item())
        second = float(probs[order[1]].item()) if len(order) > 1 else 0.0
        probability = float(probs[index].item())
        margin = probability - second
        choice = self.labels[index]
        decisions.append(SnapDecision(self.path, side, choice, probability, margin))
        if choice.startswith("const:"):
            return Const(parse_constant_label(choice))
        if choice.startswith("var:"):
            return Var(choice.split(":", 1)[1])
        if choice == "child":
            child = self.left_child if side == "left" else self.right_child
            if child is None:
                raise RuntimeError("Snapped child choice without a child node")
            return child._snap(decisions)
        raise RuntimeError(f"Unknown slot choice: {choice}")

    def _snap(self, decisions: list[SnapDecision]) -> Expr:
        left = self._snap_slot("left", decisions)
        right = self._snap_slot("right", decisions)
        if self.operator_family.is_raw:
            return Eml(left, right)
        if self.operator_family.is_geml:
            return Geml(left, right, self.operator_family)
        return CenteredEml(left, right, self.operator_family)

    def _subtree_assignments(self) -> tuple[ReplayAssignment, ...]:
        decisions: list[SnapDecision] = []
        self._snap(decisions)
        return tuple(ReplayAssignment(f"{decision.path}.{decision.side}", decision.choice) for decision in decisions)

    def set_slot(self, node_path: str, side: str, choice: str, strength: float = 30.0) -> None:
        if self.path == node_path:
            logits = self.left_logits if side == "left" else self.right_logits
            if choice not in self.labels:
                raise ValueError(f"Choice {choice!r} is not legal at {node_path}.{side}: {self.labels}")
            with torch.no_grad():
                logits.fill_(-strength)
                logits[self.labels.index(choice)] = strength
            return
        for child in (self.left_child, self.right_child):
            if child is not None and node_path.startswith(child.path):
                child.set_slot(node_path, side, choice, strength)
                return
        raise ValueError(f"Unknown node path: {node_path}")

    def set_operator(self, operator_family: EmlOperator) -> None:
        self.operator_family = operator_family
        if self.left_child is not None:
            self.left_child.set_operator(operator_family)
        if self.right_child is not None:
            self.right_child.set_operator(operator_family)


class SoftEMLTree(torch.nn.Module):
    """A complete depth-bounded EML tree with soft categorical gates."""

    def __init__(
        self,
        depth: int,
        variables: tuple[str, ...] = ("x",),
        constants: tuple[complex, ...] = (1.0,),
        operator_family: EmlOperator | None = None,
    ) -> None:
        super().__init__()
        self.depth = depth
        self.variables = tuple(variables)
        self.constants = normalize_constants(constants)
        self.operator_family = operator_family or raw_eml_operator()
        self.root = _SoftNode(depth, self.variables, self.constants, self.operator_family)

    def reset_parameters(self, seed: int | None = None, scale: float = 0.05) -> None:
        generator = torch.Generator()
        if seed is not None:
            generator.manual_seed(seed)
        self.root.reset_parameters(generator, scale)

    def set_operator(self, operator_family: EmlOperator) -> None:
        self.operator_family = operator_family
        self.root.set_operator(operator_family)

    def forward(
        self,
        context: Mapping[str, Any],
        *,
        temperature: float = 1.0,
        training_semantics: bool = True,
        stats: AnomalyStats | None = None,
        semantics: TrainingSemanticsConfig | None = None,
    ) -> torch.Tensor:
        tensor_context = {name: as_complex_tensor(value) for name, value in context.items()}
        return self.root(
            tensor_context,
            temperature=temperature,
            training_semantics=training_semantics,
            stats=stats,
            semantics=semantics,
        )

    def slot_catalog(self) -> dict[str, list[str]]:
        return self.root.slot_catalog()

    def _node_for_path(self, node_path: str) -> _SoftNode:
        node = self.root
        if node_path == "root":
            return node
        for part in node_path.split(".")[1:]:
            node = node.left_child if part == "L" else node.right_child
            if node is None:
                raise ValueError(f"Unknown node path: {node_path}")
        return node

    def parameter_count(self) -> int:
        return sum(parameter.numel() for parameter in self.parameters())

    def expected_univariate_parameter_count(self) -> int:
        if len(self.variables) != 1:
            raise ValueError("The paper's 5 * 2^n - 6 count is for univariate trees")
        if self.constants != (1.0 + 0.0j,):
            raise ValueError("The paper's 5 * 2^n - 6 count assumes the pure const:1 terminal bank")
        return 5 * (2**self.depth) - 6

    def gate_entropy(self, temperature: float = 1.0) -> torch.Tensor:
        return self.root.gate_entropy(temperature)

    def expected_child_use(self, temperature: float = 1.0) -> torch.Tensor:
        return self.root.expected_child_use(temperature)

    def snap(self) -> SnapResult:
        decisions: list[SnapDecision] = []
        expression = self.root._snap(decisions)
        min_margin = min((decision.margin for decision in decisions), default=1.0)
        return SnapResult(
            expression=expression,
            decisions=decisions,
            min_margin=min_margin,
            active_node_count=expression.node_count(),
        )

    def active_slot_alternatives(
        self,
        top_k: int = 2,
        *,
        max_slots: int | None = None,
        margin_threshold: float | None = None,
    ) -> tuple[ActiveSlotAlternatives, ...]:
        if top_k <= 0:
            return ()
        snap = self.snap()
        ranked = sorted(snap.decisions, key=lambda item: (item.margin, f"{item.path}.{item.side}"))
        groups: list[ActiveSlotAlternatives] = []
        for decision in ranked:
            if margin_threshold is not None and decision.margin > margin_threshold:
                continue
            node = self._node_for_path(decision.path)
            logits = node.left_logits if decision.side == "left" else node.right_logits
            child = node.left_child if decision.side == "left" else node.right_child
            probs = torch.softmax(logits.detach(), dim=0)
            order = torch.argsort(probs, descending=True)
            alternatives: list[SlotAlternative] = []
            for index in order.tolist():
                choice = node.labels[int(index)]
                if choice == decision.choice:
                    continue
                subtree_root = child.path if choice == "child" and child is not None else None
                descendant_assignments = child._subtree_assignments() if choice == "child" and child is not None else ()
                alternatives.append(
                    SlotAlternative(
                        choice=choice,
                        probability=float(probs[index].item()),
                        probability_gap=max(0.0, decision.probability - float(probs[index].item())),
                        rank=len(alternatives) + 1,
                        descendant_assignments=descendant_assignments,
                        subtree_root=subtree_root,
                    )
                )
                if len(alternatives) >= top_k:
                    break
            if alternatives:
                groups.append(
                    ActiveSlotAlternatives(
                        slot=f"{decision.path}.{decision.side}",
                        current_choice=decision.choice,
                        current_probability=decision.probability,
                        current_margin=decision.margin,
                        alternatives=tuple(alternatives),
                    )
                )
            if max_slots is not None and len(groups) >= max_slots:
                break
        return tuple(groups)

    def set_slot(self, node_path: str, side: str, choice: str, strength: float = 30.0) -> None:
        self.root.set_slot(node_path, side, choice, strength=strength)

    def _require_scaffold_witness(self, kind: str) -> None:
        if scaffold_witness_for(kind, self.operator_family) is None:
            raise EmbeddingError(
                CENTERED_FAMILY_SAME_FAMILY_WITNESS_MISSING,
                f"{kind} scaffold has no same-family witness for operator {self.operator_family.label}",
            )

    def force_exp(self, variable: str = "x") -> None:
        self._require_scaffold_witness("exp")
        self.set_slot("root", "left", f"var:{variable}")
        self.set_slot("root", "right", constant_label(1.0))

    def force_log(self, variable: str = "x") -> None:
        self._require_scaffold_witness("log")
        if self.depth < 3:
            raise ValueError("The paper log identity requires depth >= 3 in this scaffold")
        self.set_slot("root", "left", constant_label(1.0))
        self.set_slot("root", "right", "child")
        self.set_slot("root.R", "left", "child")
        self.set_slot("root.R", "right", constant_label(1.0))
        self.set_slot("root.R.L", "left", constant_label(1.0))
        self.set_slot("root.R.L", "right", f"var:{variable}")

    def force_scaled_exp(self, variable: str, coefficient: complex, strength: float = 30.0) -> EmbeddingResult:
        self._require_scaffold_witness("scaled_exp")
        from .compiler import scaled_exponential_expr

        expression = scaled_exponential_expr(variable, coefficient)
        return self.embed_expr(expression, EmbeddingConfig(strength=strength))

    def embed_expr(self, expression: Expr, config: EmbeddingConfig | None = None) -> EmbeddingResult:
        return embed_expr_into_tree(self, expression, config=config)


def _leaf_choice(tree: SoftEMLTree, expression: Expr) -> str:
    if isinstance(expression, Const):
        label = constant_label(expression.value)
        if label not in tree.root.base_labels:
            raise EmbeddingError("missing_constant", f"{label} is not in terminal bank {tree.root.base_labels}")
        return label
    if isinstance(expression, Var):
        label = f"var:{expression.name}"
        if label not in tree.root.base_labels:
            raise EmbeddingError("missing_variable", f"{label} is not in terminal bank {tree.root.base_labels}")
        return label
    raise EmbeddingError("incompatible_tree", f"expected leaf, got {type(expression).__name__}")


def _operator_for_expression(expression: Expr) -> EmlOperator:
    if isinstance(expression, Eml):
        return raw_eml_operator()
    if isinstance(expression, CenteredEml):
        return expression.operator
    if isinstance(expression, Geml):
        return expression.operator
    raise EmbeddingError("incompatible_tree", f"expected operator node, got {type(expression).__name__}")


def _operator_children(expression: Expr) -> tuple[Expr, Expr]:
    if isinstance(expression, (Eml, CenteredEml, Geml)):
        return expression.left, expression.right
    raise EmbeddingError("incompatible_tree", f"expected operator node, got {type(expression).__name__}")


def _embed_slot(
    tree: SoftEMLTree,
    node: _SoftNode,
    side: str,
    expression: Expr,
    config: EmbeddingConfig,
    assignments: list[EmbeddingAssignment],
) -> None:
    slot = f"{node.path}.{side}"
    if isinstance(expression, (Eml, CenteredEml, Geml)):
        expression_operator = _operator_for_expression(expression)
        if expression_operator != tree.operator_family:
            raise EmbeddingError(
                "operator_family_mismatch",
                f"tree operator {tree.operator_family.label} cannot embed {expression_operator.label}",
            )
        child = node.left_child if side == "left" else node.right_child
        if child is None:
            raise EmbeddingError("depth_too_small", f"{slot} needs a child node for expression depth {expression.depth()}")
        node.set_slot(node.path, side, "child", strength=config.strength)
        assignments.append(EmbeddingAssignment(slot, "child"))
        _embed_node(tree, child, expression, config, assignments)
        return

    choice = _leaf_choice(tree, expression)
    node.set_slot(node.path, side, choice, strength=config.strength)
    assignments.append(EmbeddingAssignment(slot, choice))


def _embed_node(
    tree: SoftEMLTree,
    node: _SoftNode,
    expression: Expr,
    config: EmbeddingConfig,
    assignments: list[EmbeddingAssignment],
) -> None:
    expression_operator = _operator_for_expression(expression)
    if expression_operator != tree.operator_family:
        raise EmbeddingError(
            "operator_family_mismatch",
            f"tree operator {tree.operator_family.label} cannot embed {expression_operator.label}",
        )
    left, right = _operator_children(expression)
    _embed_slot(tree, node, "left", left, config, assignments)
    _embed_slot(tree, node, "right", right, config, assignments)


def embed_expr_into_tree(
    tree: SoftEMLTree,
    expression: Expr,
    *,
    config: EmbeddingConfig | None = None,
) -> EmbeddingResult:
    config = config or EmbeddingConfig()
    expression_operator = _operator_for_expression(expression)
    if expression_operator != tree.operator_family:
        raise EmbeddingError(
            "operator_family_mismatch",
            f"tree operator {tree.operator_family.label} cannot embed {expression_operator.label}",
        )
    if expression.depth() > tree.depth:
        raise EmbeddingError("depth_too_small", f"expression depth {expression.depth()} exceeds tree depth {tree.depth}")
    missing_variables = sorted(expression.variables() - set(tree.variables))
    if missing_variables:
        raise EmbeddingError("missing_variable", f"missing variables: {missing_variables}")
    missing_constants = [
        constant_label(value)
        for value in expression.constants()
        if not any(abs(complex(value) - complex(existing)) <= 1e-12 for existing in tree.constants)
    ]
    if missing_constants:
        raise EmbeddingError("missing_constant", f"missing constants: {missing_constants}")

    assignments: list[EmbeddingAssignment] = []
    _embed_node(tree, tree.root, expression, config, assignments)
    snap = tree.snap()
    round_trip = expressions_equal(expression, snap.expression)
    diagnostics = () if round_trip else ("snap_round_trip_mismatch",)
    return EmbeddingResult(bool(round_trip), tuple(assignments), snap, bool(round_trip), diagnostics)


def slot_map_from_snap(snap: SnapResult) -> dict[str, str]:
    return {f"{decision.path}.{decision.side}": decision.choice for decision in snap.decisions}


def replay_slot_map_expression(
    slot_map: Mapping[str, str],
    *,
    depth: int,
    variables: tuple[str, ...],
    constants: tuple[complex, ...],
    operator_family: EmlOperator | None = None,
    strength: float = 30.0,
) -> Expr:
    tree = SoftEMLTree(depth, variables, constants, operator_family=operator_family)
    for slot, choice in _slot_items_for_replay(slot_map):
        node_path, side = slot.rsplit(".", 1)
        tree.set_slot(node_path, side, choice, strength=strength)
    return tree.snap().expression


def expand_snap_neighborhood(
    snap: SnapResult,
    slot_alternatives: Sequence[ActiveSlotAlternatives],
    *,
    depth: int,
    variables: tuple[str, ...],
    constants: tuple[complex, ...],
    operator_family: EmlOperator | None = None,
    beam_width: int = 8,
    max_moves: int = 2,
    max_slots: int | None = None,
    strength: float = 30.0,
) -> tuple[NeighborhoodVariant, ...]:
    if beam_width <= 0 or max_moves <= 0:
        return ()
    base_slot_map = slot_map_from_snap(snap)
    groups = sorted(slot_alternatives, key=lambda item: (item.current_margin, item.slot))
    if max_slots is not None:
        groups = groups[:max_slots]
    beam: list[tuple[NeighborhoodMove, ...]] = [()]
    variants: dict[str, NeighborhoodVariant] = {}

    for group in groups:
        next_beam: dict[str, tuple[NeighborhoodMove, ...]] = {_state_signature(state): state for state in beam}
        for state in beam:
            used_slots = {move.slot for move in state}
            if len(state) >= max_moves or group.slot in used_slots:
                continue
            for alternative in group.alternatives:
                move = _move_from_alternative(base_slot_map, group, alternative)
                new_state = (*state, move)
                expression = replay_slot_map_expression(
                    _slot_map_with_moves(base_slot_map, new_state),
                    depth=depth,
                    variables=variables,
                    constants=constants,
                    operator_family=operator_family,
                    strength=strength,
                )
                key = json.dumps(expression.to_document(source="snap_neighborhood_candidate"), sort_keys=True)
                candidate = NeighborhoodVariant(
                    expression=expression,
                    moves=new_state,
                    heuristic_gap=sum(item.probability_gap for item in new_state),
                )
                existing = variants.get(key)
                if existing is None or _variant_rank_key(candidate) < _variant_rank_key(existing):
                    variants[key] = candidate
                signature = _state_signature(new_state)
                incumbent = next_beam.get(signature)
                if incumbent is None or _state_rank_key(new_state) < _state_rank_key(incumbent):
                    next_beam[signature] = new_state
        beam = sorted(next_beam.values(), key=_state_rank_key)[:beam_width]
    return tuple(sorted(variants.values(), key=_variant_rank_key))


def _child_root(slot: str) -> str:
    node_path, side = slot.rsplit(".", 1)
    return f"{node_path}.{'L' if side == 'left' else 'R'}"


def _descendant_assignments_from_slot_map(slot_map: Mapping[str, str], subtree_root: str) -> tuple[ReplayAssignment, ...]:
    return tuple(
        ReplayAssignment(slot, slot_map[slot])
        for slot in _sorted_slots(slot for slot in slot_map if slot.startswith(f"{subtree_root}."))
    )


def _move_from_alternative(
    slot_map: Mapping[str, str],
    group: ActiveSlotAlternatives,
    alternative: SlotAlternative,
) -> NeighborhoodMove:
    subtree_root = alternative.subtree_root
    if group.current_choice == "child" and subtree_root is None:
        subtree_root = _child_root(group.slot)
    pruned_assignments = (
        _descendant_assignments_from_slot_map(slot_map, subtree_root)
        if group.current_choice == "child" and alternative.choice != "child" and subtree_root is not None
        else ()
    )
    return NeighborhoodMove(
        slot=group.slot,
        before=group.current_choice,
        after=alternative.choice,
        slot_margin=group.current_margin,
        probability_gap=alternative.probability_gap,
        rank=alternative.rank,
        descendant_assignments=alternative.descendant_assignments,
        pruned_assignments=pruned_assignments,
        subtree_root=subtree_root,
    )


def _slot_map_with_moves(slot_map: Mapping[str, str], moves: Sequence[NeighborhoodMove]) -> dict[str, str]:
    replay = dict(slot_map)
    for move in moves:
        replay[move.slot] = move.after
        for assignment in move.descendant_assignments:
            replay[assignment.slot] = assignment.choice
    return replay


def _slot_items_for_replay(slot_map: Mapping[str, str]) -> tuple[tuple[str, str], ...]:
    return tuple((slot, slot_map[slot]) for slot in _sorted_slots(slot_map))


def _sorted_slots(slots: Sequence[str] | Mapping[str, str] | Any) -> list[str]:
    return sorted(slots, key=lambda slot: (str(slot).count("."), str(slot)))


def _state_signature(state: Sequence[NeighborhoodMove]) -> str:
    return "|".join(f"{move.slot}:{move.after}" for move in state)


def _state_rank_key(state: Sequence[NeighborhoodMove]) -> tuple[Any, ...]:
    return (
        len(state),
        sum(move.probability_gap for move in state),
        tuple(move.slot for move in state),
        tuple(move.after for move in state),
    )


def _variant_rank_key(variant: NeighborhoodVariant) -> tuple[Any, ...]:
    return (
        len(variant.moves),
        variant.heuristic_gap,
        variant.expression.node_count(),
        tuple(move.slot for move in variant.moves),
        tuple(move.after for move in variant.moves),
    )
