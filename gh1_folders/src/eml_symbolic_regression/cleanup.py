"""Verifier-gated cleanup helpers and SymPy export."""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from .expression import Candidate
from .verify import DataSplit, VerificationReport, verify_candidate


@dataclass(frozen=True)
class CleanupReport:
    original: str
    cleaned: str
    original_tree_size: int | None
    verification: VerificationReport | None

    def as_dict(self) -> dict[str, object]:
        return {
            "original": self.original,
            "cleaned": self.cleaned,
            "original_tree_size": self.original_tree_size,
            "verification": self.verification.as_dict() if self.verification else None,
        }


def readable_expression(candidate: Candidate) -> sp.Expr:
    expr = candidate.to_sympy()
    # Use targeted, predictable rewrites; do not treat this as proof.
    return sp.factor(sp.cancel(sp.powsimp(expr, force=False)))


def cleanup_candidate(
    candidate: Candidate,
    splits: list[DataSplit] | None = None,
    *,
    tolerance: float = 1e-8,
) -> CleanupReport:
    original = str(candidate.to_sympy())
    cleaned_expr = readable_expression(candidate)
    verification = verify_candidate(candidate, splits, tolerance=tolerance) if splits is not None else None
    tree_size = candidate.node_count() if hasattr(candidate, "node_count") else None
    return CleanupReport(original, str(cleaned_expr), tree_size, verification)
