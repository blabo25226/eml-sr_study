# Methods Draft Skeleton

## EML Representation

Define the EML operator and the complete depth-bounded binary tree grammar. State that exact candidate formulas are represented as EML ASTs, with literal constants reported as explicit provenance when used.

## Differentiable Search

Describe the PyTorch `complex128` soft master tree, categorical logits, restart budgets, hardening, and training-mode numerical guards. Make clear that soft loss is a candidate-generation signal, not the recovery criterion.

## Snapping and Candidate Pooling

Describe argmax snapping, late-hardening candidate pools, fallback preservation, local cleanup, and post-snap refit as verifier-ranked stages.

## Compiler and Motif Library

Describe the SymPy-to-EML compiler as a structural, validation-gated source of exact seeds and diagnostics. Motifs are reusable transformations; formula-name recognizers and silent gate relaxation are excluded.

## Verification Contract

State the verifier-owned recovery contract: training split, held-out split, extrapolation split, exact candidate checks, and high-precision checks. A row is recovered only when the verifier status passes.

## Evidence Regimes

Use `claim-taxonomy.md` as the methods table for regime separation: pure blind, scaffolded, warm-start, same-AST, perturbed-basin, repair/refit, compile-only, unsupported, and failed.
