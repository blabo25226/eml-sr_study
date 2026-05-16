"""Scaffold witness availability by EML operator family."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .semantics import EmlOperator

CENTERED_FAMILY_SAME_FAMILY_WITNESS_MISSING = "centered_family_same_family_witness_missing"


@dataclass(frozen=True)
class ScaffoldWitness:
    """Paper-grounded scaffold witness available for a specific operator family."""

    kind: str
    operator_family: str
    attempt_kind: str
    min_depth: int
    strategy: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "operator_family": self.operator_family,
            "attempt_kind": self.attempt_kind,
            "min_depth": self.min_depth,
            "strategy": self.strategy,
        }


@dataclass(frozen=True)
class ScaffoldPlan:
    """Resolved scaffold availability for a requested operator family."""

    enabled: tuple[str, ...]
    exclusions: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "enabled": list(self.enabled),
            "exclusions": list(self.exclusions),
        }


_SCAFFOLD_WITNESSES = (
    ScaffoldWitness("exp", "raw_eml", "scaffold_exp", 1, "generic_paper_primitive"),
    ScaffoldWitness("log", "raw_eml", "scaffold_log", 3, "generic_paper_primitive"),
    ScaffoldWitness("scaled_exp", "raw_eml", "scaffold_scaled_exp", 9, "paper_scaled_exponential_family"),
)


def known_scaffold_kinds() -> tuple[str, ...]:
    """Return scaffold kinds with at least one registered witness."""

    return tuple(dict.fromkeys(witness.kind for witness in _SCAFFOLD_WITNESSES))


def list_scaffold_witnesses() -> list[dict[str, Any]]:
    """Return JSON-safe registry entries in deterministic source order."""

    return [witness.as_dict() for witness in _SCAFFOLD_WITNESSES]


def scaffold_exclusion_code(kind: str, reason: str) -> str:
    return f"{kind}:{reason}"


def scaffold_witness_for(kind: str, operator: EmlOperator) -> ScaffoldWitness | None:
    """Return the same-family witness for a scaffold kind, if one exists."""

    for witness in _SCAFFOLD_WITNESSES:
        if witness.kind == kind and witness.operator_family == operator.family:
            return witness
    return None


def resolve_scaffold_plan(requested: Iterable[str], operator: EmlOperator) -> ScaffoldPlan:
    """Resolve requested scaffold names against the active operator family."""

    requested_kinds = tuple(dict.fromkeys(str(kind) for kind in requested))
    known_kinds = set(known_scaffold_kinds())
    enabled: list[str] = []
    exclusions: list[str] = []

    for kind in requested_kinds:
        witness = scaffold_witness_for(kind, operator)
        if witness is not None:
            enabled.append(kind)
        elif kind in known_kinds and not operator.is_raw:
            exclusions.append(scaffold_exclusion_code(kind, CENTERED_FAMILY_SAME_FAMILY_WITNESS_MISSING))

    return ScaffoldPlan(tuple(enabled), tuple(dict.fromkeys(exclusions)))
