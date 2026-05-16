"""Deterministic exact EML targets for Phase 32 depth-curve evidence."""

from __future__ import annotations

from dataclasses import dataclass

from .expression import Const, Eml, Expr, Var, log_expr, log_of


@dataclass(frozen=True)
class DepthCurveTargetSpec:
    id: str
    expression: Expr
    variable: str
    description: str
    train_domain: tuple[float, float]
    heldout_domain: tuple[float, float]
    extrap_domain: tuple[float, float]
    source_document: str
    source_linkage: str


_X = Var("x")
_ONE = Const(1.0)

_DEPTH_CURVE_TARGETS: tuple[DepthCurveTargetSpec, ...] = (
    DepthCurveTargetSpec(
        id="depth_curve_depth2",
        expression=Eml(_ONE, Eml(_X, _ONE)),
        variable="x",
        description="Phase 32 depth-curve exact depth-2 target with linear real-axis behavior.",
        train_domain=(1.2, 2.0),
        heldout_domain=(1.25, 1.9),
        extrap_domain=(2.05, 2.4),
        source_document="sources/NORTH_STAR.md",
        source_linkage="Phase 32 deterministic exact EML depth-curve inventory: depth-2 target",
    ),
    DepthCurveTargetSpec(
        id="depth_curve_depth3",
        expression=log_expr("x"),
        variable="x",
        description="Phase 32 depth-curve exact depth-3 target matching the principal-branch log identity.",
        train_domain=(1.2, 2.0),
        heldout_domain=(1.25, 1.9),
        extrap_domain=(2.05, 2.4),
        source_document="sources/NORTH_STAR.md",
        source_linkage="Phase 32 deterministic exact EML depth-curve inventory: depth-3 target",
    ),
    DepthCurveTargetSpec(
        id="depth_curve_depth4",
        expression=Eml(log_expr("x"), Eml(_X, _X)),
        variable="x",
        description="Phase 32 depth-curve exact depth-4 target with blind training failures above shallow depth.",
        train_domain=(1.2, 2.0),
        heldout_domain=(1.25, 1.9),
        extrap_domain=(2.05, 2.4),
        source_document="sources/NORTH_STAR.md",
        source_linkage="Phase 32 deterministic exact EML depth-curve inventory: depth-4 target",
    ),
    DepthCurveTargetSpec(
        id="depth_curve_depth5",
        expression=Eml(log_of(Eml(_ONE, _X)), _X),
        variable="x",
        description="Phase 32 depth-curve exact depth-5 target chosen to keep the real-axis verification path finite.",
        train_domain=(1.2, 2.0),
        heldout_domain=(1.25, 1.9),
        extrap_domain=(2.05, 2.4),
        source_document="sources/NORTH_STAR.md",
        source_linkage="Phase 32 deterministic exact EML depth-curve inventory: depth-5 target",
    ),
    DepthCurveTargetSpec(
        id="depth_curve_depth6",
        expression=Eml(log_of(Eml(_ONE, Eml(_X, _ONE))), _X),
        variable="x",
        description="Phase 32 depth-curve exact depth-6 target chosen to preserve a finite, verifier-owned real-axis path.",
        train_domain=(1.2, 2.0),
        heldout_domain=(1.25, 1.9),
        extrap_domain=(2.05, 2.4),
        source_document="sources/NORTH_STAR.md",
        source_linkage="Phase 32 deterministic exact EML depth-curve inventory: depth-6 target",
    ),
)


def depth_curve_target_specs() -> tuple[DepthCurveTargetSpec, ...]:
    return _DEPTH_CURVE_TARGETS


def depth_curve_target_spec(target_id: str) -> DepthCurveTargetSpec:
    for spec in _DEPTH_CURVE_TARGETS:
        if spec.id == target_id:
            return spec
    available = ", ".join(spec.id for spec in _DEPTH_CURVE_TARGETS)
    raise KeyError(f"Unknown depth-curve target {target_id!r}. Available: {available}")
