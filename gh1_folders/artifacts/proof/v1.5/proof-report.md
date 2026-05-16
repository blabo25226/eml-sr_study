# EML v1.5 Proof Campaign Report

This bundle keeps bounded proof claims, measured blind boundaries, and older showcase campaigns separate.

## Reproduce

Run this command from a clean checkout:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli proof-campaign --output-root artifacts/proof/v1.5 --overwrite
```

## Bundle Outputs

- `proof-shallow-pure-blind`: [report](campaigns/proof-shallow-pure-blind/report.md), raw runs at [campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind](campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind)
- `proof-shallow`: [report](campaigns/proof-shallow/report.md), raw runs at [campaigns/proof-shallow/runs/v1.5-shallow-proof](campaigns/proof-shallow/runs/v1.5-shallow-proof)
- `proof-basin`: [report](campaigns/proof-basin/report.md), raw runs at [campaigns/proof-basin/runs/proof-perturbed-basin](campaigns/proof-basin/runs/proof-perturbed-basin)
- `proof-basin-probes`: [report](campaigns/proof-basin-probes/report.md), raw runs at [campaigns/proof-basin-probes/runs/proof-perturbed-basin-beer-probes](campaigns/proof-basin-probes/runs/proof-perturbed-basin-beer-probes)
- `proof-depth-curve`: [report](campaigns/proof-depth-curve/report.md), raw runs at [campaigns/proof-depth-curve/runs/proof-depth-curve](campaigns/proof-depth-curve/runs/proof-depth-curve)

- Perturbed basin bound evidence: [diagnostics/basin-bound/basin-bound.md](diagnostics/basin-bound/basin-bound.md)

## Claim Status

| Claim | Verdict | Policy | Passed | Eligible | Rate | Report | Raw Runs |
|-------|---------|--------|--------|----------|------|--------|----------|
| paper-shallow-blind-recovery | bounded | measured_pure_blind_recovery | 2 | 18 | 0.111 | [proof-shallow-pure-blind](campaigns/proof-shallow-pure-blind/report.md) | [runs](campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind) |
| paper-shallow-scaffolded-recovery | passed | scaffolded_bounded_100_percent | 18 | 18 | 1.000 | [proof-shallow](campaigns/proof-shallow/report.md) | [runs](campaigns/proof-shallow/runs/v1.5-shallow-proof) |
| paper-perturbed-true-tree-basin | passed | bounded_100_percent | 9 | 9 | 1.000 | [proof-basin](campaigns/proof-basin/report.md) | [runs](campaigns/proof-basin/runs/proof-perturbed-basin) |
| paper-blind-depth-degradation | bounded | measured_depth_curve | 20 | 20 | 1.000 | [proof-depth-curve](campaigns/proof-depth-curve/report.md) | [runs](campaigns/proof-depth-curve/runs/proof-depth-curve) |

## Depth Curve

| Depth | Blind Rate | Blind Seeds | Perturbed Rate | Perturbed Seeds |
|-------|------------|-------------|----------------|-----------------|
| 2 | 1.000 | 2 | 1.000 | 2 |
| 3 | 1.000 | 2 | 1.000 | 2 |
| 4 | 0.000 | 2 | 1.000 | 2 |
| 5 | 0.000 | 2 | 1.000 | 2 |
| 6 | 0.000 | 2 | 1.000 | 2 |

The paper reports that blind recovery degrades sharply with depth while perturbed true-tree starts return much more reliably. This report treats the depth-curve rows as measured boundary evidence, not as failed product commitments.

## v1.4 Context

These denominators are intentionally separate. v1.5 proof suites are claim-labeled training evidence; v1.4 standard/showcase campaigns are broader presentation baselines and must not be merged into proof rates.

| Campaign | Total Runs | Recovered | Recovery Rate | Blind Runs | Blind Recovered | Blind Rate |
|----------|------------|-----------|---------------|------------|-----------------|------------|
| v1.4-standard | 16 | 9 | 0.562 | 6 | 4 | 0.667 |
| v1.4-showcase | 29 | 18 | 0.621 | 9 | 6 | 0.667 |

## Out of Scope

- `paper-complete-depth-bounded-search` remains representation context, not a training pass/fail claim.
- Universal blind recovery over arbitrary depth-6 formulas remains out of scope for v1.5; the paper reports no such general blind success.
- Compile-only and catalog verification remain useful evidence paths, but they do not satisfy training-proof claims by themselves.
