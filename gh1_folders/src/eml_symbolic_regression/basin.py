"""Deterministic exact EML targets for perturbed-basin proof runs."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

import numpy as np

from .expression import Const, Eml, Expr, Var, format_constant_value
from .master_tree import EmbeddingConfig, EmbeddingResult, SoftEMLTree, embed_expr_into_tree, expressions_equal
from .optimize import FitResult, TrainingConfig, fit_eml_tree
from .verify import DataSplit, VerificationReport
from .warm_start import PerturbationConfig, perturb_tree_logits


@dataclass(frozen=True)
class BasinTargetSpec:
    id: str
    expression: Expr
    variable: str
    train_domain: tuple[float, float]
    heldout_domain: tuple[float, float]
    extrap_domain: tuple[float, float]
    source_document: str
    source_linkage: str


@dataclass(frozen=True)
class BasinTrainingResult:
    status: str
    return_kind: str
    fit: FitResult
    embedding: EmbeddingResult
    verification: VerificationReport | None
    manifest: dict[str, Any]


_X = Var("x")
_ONE = Const(1.0)

_BASIN_TARGETS: tuple[BasinTargetSpec, ...] = (
    BasinTargetSpec(
        id="basin_depth1_exp",
        expression=Eml(_X, _ONE),
        variable="x",
        train_domain=(-1.0, 1.0),
        heldout_domain=(-0.8, 0.8),
        extrap_domain=(1.1, 1.5),
        source_document="sources/NORTH_STAR.md",
        source_linkage="Phase 31 deterministic exact EML basin inventory: depth-1 exp identity",
    ),
    BasinTargetSpec(
        id="basin_depth2_exp_exp",
        expression=Eml(Eml(_X, _ONE), _ONE),
        variable="x",
        train_domain=(-0.8, 0.2),
        heldout_domain=(-0.7, 0.1),
        extrap_domain=(0.3, 0.5),
        source_document="sources/NORTH_STAR.md",
        source_linkage="Phase 31 deterministic exact EML basin inventory: depth-2 nested exp identity",
    ),
    BasinTargetSpec(
        id="basin_depth3_exp_exp_exp",
        expression=Eml(Eml(Eml(_X, _ONE), _ONE), _ONE),
        variable="x",
        train_domain=(-1.0, -0.2),
        heldout_domain=(-0.9, -0.35),
        extrap_domain=(-1.4, -1.1),
        source_document="sources/NORTH_STAR.md",
        source_linkage="Phase 31 deterministic exact EML basin inventory: depth-3 nested exp identity",
    ),
)


def basin_target_specs() -> tuple[BasinTargetSpec, ...]:
    return _BASIN_TARGETS


def basin_target_spec(target_id: str) -> BasinTargetSpec:
    for spec in _BASIN_TARGETS:
        if spec.id == target_id:
            return spec
    available = ", ".join(spec.id for spec in _BASIN_TARGETS)
    raise KeyError(f"Unknown basin target {target_id!r}. Available: {available}")


def fit_perturbed_true_tree(
    inputs: dict[str, Any],
    target: Any,
    config: TrainingConfig,
    target_expr: Expr,
    *,
    embedding_config: EmbeddingConfig | None = None,
    perturbation_config: PerturbationConfig | None = None,
    verification_splits: list[DataSplit] | None = None,
    tolerance: float = 1e-8,
    target_metadata: dict[str, Any] | None = None,
) -> BasinTrainingResult:
    embedding_config = embedding_config or EmbeddingConfig()
    perturbation_config = perturbation_config or PerturbationConfig(seed=config.seed)
    if config.depth < target_expr.depth():
        raise ValueError(f"training depth {config.depth} is smaller than target depth {target_expr.depth()}")

    constants = _sorted_constants(target_expr)
    variables = tuple(sorted(target_expr.variables()))
    config = replace(config, variables=variables, constants=constants)

    probe_tree = SoftEMLTree(config.depth, config.variables, config.constants, operator_family=config.operator_family)
    embedding = embed_expr_into_tree(probe_tree, target_expr, config=embedding_config)
    if not embedding.success:
        raise ValueError(f"embedding failed: {embedding.diagnostics}")

    def initializer(model: SoftEMLTree, restart: int, seed: int) -> dict[str, Any]:
        embedded = embed_expr_into_tree(model, target_expr, config=embedding_config)
        perturbation = perturb_tree_logits(
            model,
            replace(perturbation_config, seed=perturbation_config.seed + restart),
            embedded,
        )
        return {
            "kind": "perturbed_true_tree",
            "restart": restart,
            "seed": seed,
            "embedding": embedded.as_dict(),
            "perturbation": perturbation.as_dict(),
        }

    fit = fit_eml_tree(
        inputs,
        target,
        config,
        initializer=initializer,
        verification_splits=verification_splits,
        tolerance=tolerance,
    )
    verification = fit.verification if verification_splits else None

    if expressions_equal(fit.snap.expression, target_expr):
        return_kind = "same_ast_return"
    elif verification is not None and verification.status == "recovered":
        return_kind = "verified_equivalent_ast"
    elif fit.status == "snapped_candidate":
        return_kind = "snapped_but_failed"
    elif np.isfinite(fit.best_loss):
        return_kind = "soft_fit_only"
    else:
        return_kind = "failed"

    status = "recovered" if verification is not None and verification.status == "recovered" and return_kind in {
        "same_ast_return",
        "verified_equivalent_ast",
    } else return_kind

    manifest = {
        "schema": "eml.perturbed_true_tree_manifest.v1",
        "status": status,
        "raw_status": status,
        "return_kind": return_kind,
        "target_metadata": dict(target_metadata or {}),
        "target_ast": target_expr.to_document(variables=list(config.variables), source="perturbed_true_tree_target"),
        "terminal_bank": {
            "variables": list(config.variables),
            "constants": [format_constant_value(value) for value in config.constants],
        },
        "embedding": embedding.as_dict(),
        "perturbation_config": perturbation_config.__dict__,
        "optimizer": fit.manifest,
        "verification": verification.as_dict() if verification else None,
        "diagnosis": _diagnose_perturbed_true_tree(status, return_kind, fit, verification),
    }
    return BasinTrainingResult(status, return_kind, fit, embedding, verification, manifest)


def _sorted_constants(expression: Expr) -> tuple[complex, ...]:
    return tuple(sorted(expression.constants(), key=lambda value: (value.real, value.imag)))


def _diagnose_perturbed_true_tree(
    status: str,
    return_kind: str,
    fit: FitResult,
    verification: VerificationReport | None,
) -> dict[str, Any]:
    initialization = fit.manifest.get("best_restart", {}).get("initialization") or {}
    perturbation = initialization.get("perturbation") or {}
    changes = perturbation.get("active_slot_changes") or []
    changed_slot_count = sum(1 for item in changes if item.get("changed")) if isinstance(changes, list) else None
    return {
        "status": status,
        "return_kind": return_kind,
        "mechanism": return_kind if status == "recovered" else _failed_mechanism(return_kind, changed_slot_count),
        "active_slot_count": len(changes) if isinstance(changes, list) else None,
        "changed_slot_count": changed_slot_count,
        "snap_min_margin": fit.snap.min_margin,
        "best_loss": fit.best_loss,
        "post_snap_loss": fit.post_snap_loss,
        "verifier_status": verification.status if verification is not None else None,
    }


def _failed_mechanism(return_kind: str, changed_slot_count: int | None) -> str:
    if return_kind in {"snapped_but_failed", "failed"} and changed_slot_count:
        return "active_slot_perturbation"
    return return_kind
