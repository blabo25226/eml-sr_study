"""Compiler-driven warm-start helpers for soft EML training."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

import numpy as np
import torch

from .expression import Expr, format_constant_value
from .master_tree import (
    EmbeddingConfig,
    EmbeddingResult,
    SoftEMLTree,
    embed_expr_into_tree,
    expressions_equal,
)
from .optimize import FitResult, TrainingConfig, fit_eml_tree
from .verify import DataSplit, VerificationReport


@dataclass(frozen=True)
class PerturbationConfig:
    seed: int = 0
    noise_scale: float = 0.0


@dataclass(frozen=True)
class PerturbationReport:
    config: PerturbationConfig
    active_slot_changes: tuple[dict[str, Any], ...]
    pre_snap: dict[str, Any]
    post_snap: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "config": self.config.__dict__,
            "active_slot_changes": list(self.active_slot_changes),
            "pre_snap": self.pre_snap,
            "post_snap": self.post_snap,
        }


@dataclass(frozen=True)
class WarmStartResult:
    status: str
    fit: FitResult
    embedding: EmbeddingResult
    verification: VerificationReport | None
    manifest: dict[str, Any]


def _slot_choice(tree: SoftEMLTree, slot: str) -> str:
    node_path, side = slot.rsplit(".", 1)
    node = tree.root
    if node_path != "root":
        for part in node_path.split(".")[1:]:
            node = node.left_child if part == "L" else node.right_child
            if node is None:
                raise ValueError(f"Unknown slot path: {slot}")
    logits = node.left_logits if side == "left" else node.right_logits
    return node.labels[int(torch.argmax(logits.detach()).item())]


def perturb_tree_logits(
    tree: SoftEMLTree,
    config: PerturbationConfig,
    embedding: EmbeddingResult,
) -> PerturbationReport:
    pre_snap = tree.snap().as_dict()
    before = {assignment.slot: _slot_choice(tree, assignment.slot) for assignment in embedding.assignments}

    generator = torch.Generator()
    generator.manual_seed(config.seed)
    with torch.no_grad():
        for parameter in tree.parameters():
            if config.noise_scale:
                noise = torch.randn(
                    parameter.shape,
                    generator=generator,
                    dtype=parameter.dtype,
                    device=parameter.device,
                )
                parameter.add_(noise * config.noise_scale)

    post_snap = tree.snap().as_dict()
    changes = []
    for assignment in embedding.assignments:
        after = _slot_choice(tree, assignment.slot)
        changes.append(
            {
                "slot": assignment.slot,
                "embedded_choice": assignment.choice,
                "pre_choice": before[assignment.slot],
                "post_choice": after,
                "changed": before[assignment.slot] != after,
            }
        )
    return PerturbationReport(config, tuple(changes), pre_snap, post_snap)


def _sorted_constants(expression: Expr) -> tuple[complex, ...]:
    return tuple(sorted(expression.constants(), key=lambda value: (value.real, value.imag)))


def fit_warm_started_eml_tree(
    inputs: dict[str, Any],
    target: Any,
    config: TrainingConfig,
    compiled_expr: Expr,
    *,
    embedding_config: EmbeddingConfig | None = None,
    perturbation_config: PerturbationConfig | None = None,
    verification_splits: list[DataSplit] | None = None,
    tolerance: float = 1e-8,
    compiler_metadata: dict[str, Any] | None = None,
) -> WarmStartResult:
    embedding_config = embedding_config or EmbeddingConfig()
    perturbation_config = perturbation_config or PerturbationConfig(seed=config.seed)
    constants = _sorted_constants(compiled_expr)
    if config.depth < compiled_expr.depth():
        raise ValueError(f"training depth {config.depth} is smaller than compiled depth {compiled_expr.depth()}")
    config = replace(config, variables=tuple(sorted(compiled_expr.variables())), constants=constants)

    probe_tree = SoftEMLTree(config.depth, config.variables, config.constants, operator_family=config.operator_family)
    embedding = embed_expr_into_tree(probe_tree, compiled_expr, config=embedding_config)
    if not embedding.success:
        raise ValueError(f"embedding failed: {embedding.diagnostics}")

    def initializer(model: SoftEMLTree, restart: int, seed: int) -> dict[str, Any]:
        embedded = embed_expr_into_tree(model, compiled_expr, config=embedding_config)
        perturb = perturb_tree_logits(
            model,
            replace(perturbation_config, seed=perturbation_config.seed + restart),
            embedded,
        )
        return {
            "kind": "compiled_warm_start",
            "restart": restart,
            "seed": seed,
            "embedding": embedded.as_dict(),
            "perturbation": perturb.as_dict(),
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

    if expressions_equal(fit.snap.expression, compiled_expr):
        status = "same_ast_return"
    elif verification is not None and verification.status == "recovered":
        status = "verified_equivalent_ast"
    elif fit.status == "snapped_candidate":
        status = "snapped_but_failed"
    elif np.isfinite(fit.best_loss):
        status = "soft_fit_only"
    else:
        status = "failed"

    manifest = {
        "schema": "eml.warm_start_manifest.v1",
        "status": status,
        "compiler_metadata": compiler_metadata,
        "terminal_bank": {
            "variables": list(config.variables),
            "constants": [format_constant_value(value) for value in config.constants],
        },
        "embedding": embedding.as_dict(),
        "perturbation_config": perturbation_config.__dict__,
        "optimizer": fit.manifest,
        "verification": verification.as_dict() if verification else None,
        "diagnosis": _diagnose_warm_start(status, fit, verification),
    }
    return WarmStartResult(status, fit, embedding, verification, manifest)


def _diagnose_warm_start(status: str, fit: FitResult, verification: VerificationReport | None) -> dict[str, Any]:
    initialization = fit.manifest.get("best_restart", {}).get("initialization") or {}
    perturbation = initialization.get("perturbation") or {}
    changes = perturbation.get("active_slot_changes") or []
    active_slot_count = len(changes) if isinstance(changes, list) else None
    changed_slot_count = sum(1 for item in changes if item.get("changed")) if isinstance(changes, list) else None
    verifier_status = verification.status if verification is not None else None

    mechanism = _warm_start_mechanism(
        status,
        changed_slot_count=changed_slot_count,
        post_snap_loss=fit.post_snap_loss,
        snap_min_margin=fit.snap.min_margin,
        verifier_status=verifier_status,
    )
    return {
        "status": status,
        "mechanism": mechanism,
        "active_slot_count": active_slot_count,
        "changed_slot_count": changed_slot_count,
        "snap_min_margin": fit.snap.min_margin,
        "best_loss": fit.best_loss,
        "post_snap_loss": fit.post_snap_loss,
        "verifier_status": verifier_status,
    }


def _warm_start_mechanism(
    status: str,
    *,
    changed_slot_count: int | None,
    post_snap_loss: float,
    snap_min_margin: float,
    verifier_status: str | None,
) -> str:
    if status in {"same_ast_return", "verified_equivalent_ast"}:
        return status
    if changed_slot_count is not None and changed_slot_count > 0:
        return "active_slot_perturbation"
    if not np.isfinite(post_snap_loss):
        return "non_finite_snap"
    if snap_min_margin < 0.1:
        return "snap_instability"
    if status == "soft_fit_only":
        return "soft_fit_only"
    if verifier_status == "failed":
        return "verifier_mismatch"
    return status or "failed"
