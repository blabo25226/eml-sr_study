"""Principal-log branch diagnostics for EML second-slot inputs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

BRANCH_DIAGNOSTIC_SCHEMA = "eml.branch_diagnostics.v1"
PRINCIPAL_LOG_BRANCH = "principal_complex_log_cut_negative_real_axis"


@dataclass(frozen=True)
class BranchDiagnostics:
    """Machine-readable diagnostics for principal-log branch risk."""

    input_count: int
    non_finite_count: int
    near_zero_count: int
    branch_cut_hit_count: int
    branch_cut_proximity_count: int
    branch_cut_crossing_count: int
    min_branch_cut_distance: float | None
    convention: str = PRINCIPAL_LOG_BRANCH

    @property
    def invalid_domain_skip_count(self) -> int:
        return self.non_finite_count + self.near_zero_count

    @property
    def branch_related(self) -> bool:
        return bool(
            self.invalid_domain_skip_count
            or self.branch_cut_hit_count
            or self.branch_cut_proximity_count
            or self.branch_cut_crossing_count
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": BRANCH_DIAGNOSTIC_SCHEMA,
            "branch_convention": self.convention,
            "input_count": self.input_count,
            "non_finite_count": self.non_finite_count,
            "near_zero_count": self.near_zero_count,
            "invalid_domain_skip_count": self.invalid_domain_skip_count,
            "branch_cut_hit_count": self.branch_cut_hit_count,
            "branch_cut_proximity_count": self.branch_cut_proximity_count,
            "branch_cut_crossing_count": self.branch_cut_crossing_count,
            "min_branch_cut_distance": self.min_branch_cut_distance,
            "branch_related": self.branch_related,
        }


def principal_log_branch_diagnostics(
    values: Any,
    *,
    proximity_tolerance: float = 1e-6,
    zero_tolerance: float = 1e-12,
) -> BranchDiagnostics:
    """Summarize branch-cut risk for principal complex log inputs."""

    arr = np.asarray(values, dtype=np.complex128).reshape(-1)
    if arr.size == 0:
        return BranchDiagnostics(0, 0, 0, 0, 0, 0, None)

    finite = np.isfinite(arr.real) & np.isfinite(arr.imag)
    finite_values = arr[finite]
    non_finite_count = int(arr.size - finite_values.size)
    if finite_values.size == 0:
        return BranchDiagnostics(int(arr.size), non_finite_count, 0, 0, 0, 0, None)

    real = finite_values.real
    imag = finite_values.imag
    magnitude = np.abs(finite_values)
    zero_tol = max(float(zero_tolerance), 0.0)
    proximity_tol = max(float(proximity_tolerance), zero_tol)

    near_zero = magnitude <= zero_tol
    on_negative_axis = real <= 0.0
    branch_cut_hit = on_negative_axis & (np.abs(imag) <= zero_tol)
    branch_cut_proximity = on_negative_axis & (np.abs(imag) <= proximity_tol)
    distances = np.where(on_negative_axis, np.abs(imag), magnitude)

    crossing_count = _branch_cut_crossing_count(finite_values, proximity_tolerance=proximity_tol)

    return BranchDiagnostics(
        input_count=int(arr.size),
        non_finite_count=non_finite_count,
        near_zero_count=int(np.count_nonzero(near_zero)),
        branch_cut_hit_count=int(np.count_nonzero(branch_cut_hit)),
        branch_cut_proximity_count=int(np.count_nonzero(branch_cut_proximity)),
        branch_cut_crossing_count=crossing_count,
        min_branch_cut_distance=float(np.min(distances)) if distances.size else None,
    )


def merge_branch_diagnostics(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Merge branch diagnostic dictionaries by summing counts and taking min distance."""

    if not items:
        return BranchDiagnostics(0, 0, 0, 0, 0, 0, None).as_dict()
    min_distances = [
        float(item["min_branch_cut_distance"])
        for item in items
        if item.get("min_branch_cut_distance") is not None and np.isfinite(float(item["min_branch_cut_distance"]))
    ]
    merged = {
        "schema": BRANCH_DIAGNOSTIC_SCHEMA,
        "branch_convention": PRINCIPAL_LOG_BRANCH,
        "input_count": sum(int(item.get("input_count", 0)) for item in items),
        "non_finite_count": sum(int(item.get("non_finite_count", 0)) for item in items),
        "near_zero_count": sum(int(item.get("near_zero_count", 0)) for item in items),
        "invalid_domain_skip_count": sum(int(item.get("invalid_domain_skip_count", 0)) for item in items),
        "branch_cut_hit_count": sum(int(item.get("branch_cut_hit_count", 0)) for item in items),
        "branch_cut_proximity_count": sum(int(item.get("branch_cut_proximity_count", 0)) for item in items),
        "branch_cut_crossing_count": sum(int(item.get("branch_cut_crossing_count", 0)) for item in items),
        "min_branch_cut_distance": min(min_distances) if min_distances else None,
    }
    merged["branch_related"] = bool(
        merged["invalid_domain_skip_count"]
        or merged["branch_cut_hit_count"]
        or merged["branch_cut_proximity_count"]
        or merged["branch_cut_crossing_count"]
    )
    return merged


def _branch_cut_crossing_count(values: np.ndarray, *, proximity_tolerance: float) -> int:
    if values.size < 2:
        return 0
    count = 0
    for left, right in zip(values[:-1], values[1:]):
        if left.imag * right.imag >= 0.0:
            continue
        crossing_fraction = -left.imag / (right.imag - left.imag)
        crossing_real = left.real + crossing_fraction * (right.real - left.real)
        if crossing_real <= proximity_tolerance:
            count += 1
    return count
