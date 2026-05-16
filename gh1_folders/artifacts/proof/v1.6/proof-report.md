# EML v1.6 Proof Campaign Report

This bundle keeps bounded proof claims, measured blind boundaries, and older showcase campaigns separate.

## Reproduce

Run this command from a clean checkout:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli proof-campaign --output-root artifacts/proof/v1.6 --overwrite
```

## Bundle Outputs

- `proof-shallow-pure-blind`: [report](campaigns/proof-shallow-pure-blind/report.md), raw runs at [campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind](campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind)
- `proof-shallow`: [report](campaigns/proof-shallow/report.md), raw runs at [campaigns/proof-shallow/runs/v1.5-shallow-proof](campaigns/proof-shallow/runs/v1.5-shallow-proof)
- `proof-basin`: [report](campaigns/proof-basin/report.md), raw runs at [campaigns/proof-basin/runs/proof-perturbed-basin](campaigns/proof-basin/runs/proof-perturbed-basin)
- `proof-basin-probes`: [report](campaigns/proof-basin-probes/report.md), raw runs at [campaigns/proof-basin-probes/runs/proof-perturbed-basin-beer-probes](campaigns/proof-basin-probes/runs/proof-perturbed-basin-beer-probes)
- `proof-depth-curve`: [report](campaigns/proof-depth-curve/report.md), raw runs at [campaigns/proof-depth-curve/runs/proof-depth-curve](campaigns/proof-depth-curve/runs/proof-depth-curve)

- Perturbed basin bound evidence: [diagnostics/basin-bound/basin-bound.md](diagnostics/basin-bound/basin-bound.md)

- Anchor locks: [anchor-locks.json](anchor-locks.json)

## Regime Summary

| Regime | Runs | Verifier Recovered | Same AST | Verified Equivalent | Unsupported | Failed |
|--------|------|--------------------|----------|---------------------|-------------|--------|
| blind | 46 | 25 | 0 | 0 | 0 | 21 |
| warm_start | 0 | 0 | 0 | 0 | 0 | 0 |
| compile | 0 | 0 | 0 | 0 | 0 | 0 |
| catalog | 0 | 0 | 0 | 0 | 0 | 0 |
| perturbed_tree | 23 | 23 | 20 | 0 | 0 | 0 |

## Claim Status

| Claim | Verdict | Policy | Passed | Eligible | Rate | Report | Raw Runs |
|-------|---------|--------|--------|----------|------|--------|----------|
| paper-shallow-blind-recovery | reported | measured_pure_blind_recovery | 2 | 18 | 0.111 | [proof-shallow-pure-blind](campaigns/proof-shallow-pure-blind/report.md) | [runs](campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind) |
| paper-shallow-scaffolded-recovery | passed | scaffolded_bounded_100_percent | 18 | 18 | 1.000 | [proof-shallow](campaigns/proof-shallow/report.md) | [runs](campaigns/proof-shallow/runs/v1.5-shallow-proof) |
| paper-perturbed-true-tree-basin | passed | bounded_100_percent | 9 | 9 | 1.000 | [proof-basin](campaigns/proof-basin/report.md) | [runs](campaigns/proof-basin/runs/proof-perturbed-basin) |
| paper-blind-depth-degradation | reported | measured_depth_curve | 20 | 20 | 1.000 | [proof-depth-curve](campaigns/proof-depth-curve/report.md) | [runs](campaigns/proof-depth-curve/runs/proof-depth-curve) |

## Depth Curve

| Depth | Blind Rate | Blind Seeds | Perturbed Rate | Perturbed Seeds |
|-------|------------|-------------|----------------|-----------------|
| 2 | 1.000 | 2 | 1.000 | 2 |
| 3 | 1.000 | 2 | 1.000 | 2 |
| 4 | 0.000 | 2 | 1.000 | 2 |
| 5 | 0.000 | 2 | 1.000 | 2 |
| 6 | 0.000 | 2 | 1.000 | 2 |

The paper reports that blind recovery degrades sharply with depth while perturbed true-tree starts return much more reliably. This report treats the depth-curve rows as measured boundary evidence, not as failed product commitments.

## Archived Anchors

These archived proof and campaign anchors are hash-locked so later comparisons can prove which historical files were used.

| Campaign | File | SHA-256 |
|----------|------|---------|
| v1.5 | artifacts/proof/v1.5/proof-campaign.json | `1c7bce85956110b168bf5b18b0e12e4432416ead400ab361ad2bce292d1eeef4` |
| v1.5 | artifacts/proof/v1.5/proof-report.md | `32012f232c9e84fdf14e8f75bec698cb394d6ad51c1d343fe4035a1758d1718a` |
| v1.4-standard | artifacts/campaigns/v1.4-standard/aggregate.json | `6fd82e7e428655b850f71c458c386a19764b9b3b631502bc1f2d122ec0320dc9` |
| v1.4-standard | artifacts/campaigns/v1.4-standard/suite-result.json | `86cd31cff51e0e7e6decd7241850ac75d9e6617e915b94257bfbb46801b0d2ab` |
| v1.4-standard | artifacts/campaigns/v1.4-standard/campaign-manifest.json | `f37b60a04ac65db5f6ca559a33c0232ef3b816ab59d6a10a32dce5eda5ff97b6` |
| v1.4-standard | artifacts/campaigns/v1.4-standard/report.md | `2968124092ed16e3787215f7ad4e6df371954c87ecad1fafb132bb3e56214298` |
| v1.4-standard | artifacts/campaigns/v1.4-standard/tables/runs.csv | `4cee19812d3309a925c0e11bebd3432d3af3b885a3edcac8f5b592974a667d8a` |
| v1.4-standard | artifacts/campaigns/v1.4-standard/tables/failures.csv | `1d948a516cffc308104b09485401a46a3b5faf8a9e79dab410ea7628a8dfc413` |
| v1.4-showcase | artifacts/campaigns/v1.4-showcase/aggregate.json | `e2419aecfd6198c9716e2ca44eeaac51a7edbc5bdba46a3c0930675e706987da` |
| v1.4-showcase | artifacts/campaigns/v1.4-showcase/suite-result.json | `c86d025f0793e58713c5d873c89b6d96a4d1061f9084d89b110f484bc760b81a` |
| v1.4-showcase | artifacts/campaigns/v1.4-showcase/campaign-manifest.json | `b5f39842313059e51ee6f55f166e2545ced37990fbf1e81c4c25a31884d912f0` |
| v1.4-showcase | artifacts/campaigns/v1.4-showcase/report.md | `42596e4424d46fb63430a75a8411bf43423112d973ff7a69e5db002a4d9cfab2` |
| v1.4-showcase | artifacts/campaigns/v1.4-showcase/tables/runs.csv | `45c97f90a1230d7e06552ec2ef60a9085447bf8fb067fc12beb57138948d01ec` |
| v1.4-showcase | artifacts/campaigns/v1.4-showcase/tables/failures.csv | `cf063b9e2fa9af72310809fb1690bee25e516a49ed4a1f6ac9211b2f50d0ff33` |

## v1.4 Context

These denominators are intentionally separate. The proof suites are claim-labeled training evidence; v1.4 standard/showcase campaigns are broader presentation baselines and must not be merged into proof rates.

| Campaign | Total Runs | Recovered | Recovery Rate | Blind Runs | Blind Recovered | Blind Rate |
|----------|------------|-----------|---------------|------------|-----------------|------------|
| v1.4-standard | 16 | 9 | 0.562 | 6 | 4 | 0.667 |
| v1.4-showcase | 29 | 18 | 0.621 | 9 | 6 | 0.667 |

## Out of Scope

- `paper-complete-depth-bounded-search` remains representation context, not a training pass/fail claim.
- Universal blind recovery over arbitrary depth-6 formulas remains out of scope for v1.5; the paper reports no such general blind success.
- Compile-only and catalog verification remain useful evidence paths, but they do not satisfy training-proof claims by themselves.
