"""Small validation records for bounded compiler motif searches."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np
import sympy as sp

from .expression import Expr


@dataclass(frozen=True)
class MotifSearchRecord:
    motif_name: str
    target_family: str
    candidate_construction: str
    sample_count: int
    max_abs_error: float
    mse: float
    tolerance: float
    accepted: bool
    baseline_depth: int | None = None
    candidate_depth: int | None = None
    baseline_node_count: int | None = None
    candidate_node_count: int | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "motif_name": self.motif_name,
            "target_family": self.target_family,
            "candidate_construction": self.candidate_construction,
            "sample_count": self.sample_count,
            "max_abs_error": self.max_abs_error,
            "mse": self.mse,
            "tolerance": self.tolerance,
            "accepted": self.accepted,
            "baseline_depth": self.baseline_depth,
            "candidate_depth": self.candidate_depth,
            "baseline_node_count": self.baseline_node_count,
            "candidate_node_count": self.candidate_node_count,
        }


def validate_motif_candidate(
    *,
    motif_name: str,
    target_family: str,
    target_expression: sp.Expr,
    candidate: Expr,
    variables: Sequence[str],
    inputs: Mapping[str, Any],
    candidate_construction: str,
    tolerance: float = 1e-8,
    baseline_depth: int | None = None,
    baseline_node_count: int | None = None,
) -> MotifSearchRecord:
    """Validate one bounded motif candidate on independent numeric samples."""

    symbols = [sp.Symbol(name) for name in variables]
    ordinary = sp.lambdify(symbols, target_expression, modules="numpy")
    values = [np.asarray(inputs[name], dtype=np.complex128) for name in variables]
    with np.errstate(all="ignore"):
        expected = np.asarray(ordinary(*values), dtype=np.complex128)
        actual = candidate.evaluate_numpy(inputs)
        residual = actual - expected

    finite = np.all(np.isfinite(expected)) and np.all(np.isfinite(actual))
    max_abs = float(np.max(np.abs(residual))) if finite and residual.size else float("inf")
    mse = float(np.mean(np.abs(residual) ** 2)) if finite and residual.size else float("inf")
    return MotifSearchRecord(
        motif_name=motif_name,
        target_family=target_family,
        candidate_construction=candidate_construction,
        sample_count=int(np.size(residual)),
        max_abs_error=max_abs,
        mse=mse,
        tolerance=float(tolerance),
        accepted=bool(finite and max_abs <= tolerance),
        baseline_depth=baseline_depth,
        candidate_depth=candidate.depth(),
        baseline_node_count=baseline_node_count,
        candidate_node_count=candidate.node_count(),
    )
