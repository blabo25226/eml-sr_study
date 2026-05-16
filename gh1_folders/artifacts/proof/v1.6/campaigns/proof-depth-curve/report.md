# EML Benchmark Campaign Report: proof-depth-curve

Measured v1.5 blind-vs-perturbed depth-curve campaign over deterministic exact EML targets.

## Reproduce

Run this command from a clean checkout:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign proof-depth-curve --output-root artifacts/proof/v1.6/campaigns --label proof-depth-curve --overwrite
```

- Suite: `proof-depth-curve`
- Budget tier: `proof-contract`
- Guardrail: 20 runs; exact depth-2 through depth-6 blind and perturbed rows with fixed seeds and budgets.
- Raw run artifacts: [runs/proof-depth-curve](runs/proof-depth-curve)

## Headline Metrics

| Metric | Value |
|--------|-------|
| Total runs | 20 |
| Verifier recovered | 14 (70.0%) |
| Same-AST exact returns | 10 (50.0%) |
| Verified-equivalent exact returns | 0 |
| Unsupported | 0 (0.0%) |
| Failed | 6 (30.0%) |
| Median best soft loss | 0 |
| Median post-snap loss | 0 |
| Median runtime seconds | 1.407 |

## Regime Summary

| Regime | Runs | Verifier Recovered | Same AST | Verified Equivalent | Unsupported | Failed |
|--------|------|--------------------|----------|---------------------|-------------|--------|
| blind | 10 | 4 | 0 | 0 | 0 | 6 |
| warm_start | 0 | 0 | 0 | 0 | 0 | 0 |
| compile | 0 | 0 | 0 | 0 | 0 | 0 |
| catalog | 0 | 0 | 0 | 0 | 0 | 0 |
| perturbed_tree | 10 | 10 | 10 | 0 | 0 | 0 |

This table keeps blind, compiler-assisted warm-start, compile-only, catalog, and perturbed-basin evidence visibly separate before any narrative interpretation.

## Proof Contract

| Claim | Threshold | Status | Passed | Eligible | Rate |
|-------|-----------|--------|--------|----------|------|
| paper-blind-depth-degradation | measured_depth_curve | reported | 20 | 20 | 1.000 |

Bounded proof thresholds count only allowed verifier-owned training evidence classes; catalog and compile-only verification remain separate evidence classes.

## Depth Curve

| Depth | Mode | Seeds | Recovered | Total | Rate | Median Best Loss | Median Post-Snap Loss | Median Runtime | Median Snap Margin |
|-------|------|-------|-----------|-------|------|------------------|-----------------------|----------------|--------------------|
| 2 | blind | 2 | 2 | 2 | 1.000 | 8.4e-07 | 0 | 1.254 | 0.7704 |
| 2 | perturbed_tree | 2 | 2 | 2 | 1.000 | 0 | 0 | 0.9889 | 1 |
| 3 | blind | 2 | 2 | 2 | 1.000 | 0 | 0 | 1.884 | 1 |
| 3 | perturbed_tree | 2 | 2 | 2 | 1.000 | 0 | 0 | 1.001 | 1 |
| 4 | blind | 2 | 0 | 2 | 0.000 | 0.2319 | 0.636 | 2.723 | 0.5003 |
| 4 | perturbed_tree | 2 | 2 | 2 | 1.000 | 0 | 0 | 1.163 | 1 |
| 5 | blind | 2 | 0 | 2 | 0.000 | 2.007 | 2.014 | 4.674 | 1 |
| 5 | perturbed_tree | 2 | 2 | 2 | 1.000 | 0 | 0 | 1.235 | 1 |
| 6 | blind | 2 | 0 | 2 | 0.000 | 0.2871 | 0.3389 | 8.57 | 1 |
| 6 | perturbed_tree | 2 | 2 | 2 | 1.000 | 0 | 0 | 1.558 | 1 |

The paper reports that blind recovery falls sharply with depth while perturbed true-tree starts return much more reliably. This campaign shows blind recovery only through depth 3 in this inventory, alongside perturbed recovery at every measured depth through 6. Those deeper blind failures are measured boundary evidence, not product regressions or failed proof claims.

## Figures

- [recovery by formula](figures/recovery-by-formula.svg)
- [recovery by start mode](figures/recovery-by-start-mode.svg)
- [loss before after snap](figures/loss-before-after-snap.svg)
- [beer perturbation](figures/beer-perturbation.svg)
- [runtime depth budget](figures/runtime-depth-budget.svg)
- [failure taxonomy](figures/failure-taxonomy.svg)
- [depth curve recovery](figures/depth-curve-recovery.svg)

## Tables

- [runs csv](tables/runs.csv)
- [group formula csv](tables/group-formula.csv)
- [group start mode csv](tables/group-start-mode.csv)
- [group perturbation noise csv](tables/group-perturbation-noise.csv)
- [group depth csv](tables/group-depth.csv)
- [group failure class csv](tables/group-failure-class.csv)
- [group evidence class csv](tables/group-evidence-class.csv)
- [group claim csv](tables/group-claim.csv)
- [group threshold policy csv](tables/group-threshold-policy.csv)
- [depth curve csv](tables/depth-curve.csv)
- [headline json](tables/headline-metrics.json)
- [headline csv](tables/headline-metrics.csv)
- [failures csv](tables/failures.csv)

## What EML Demonstrates Well

This campaign shows the strongest current mixed-regime behavior when the EML representation is verified after snapping: 14/20 runs passed verifier-owned recovery. It includes 4/10 blind recoveries, 10 same-AST exact returns, and 0 verified-equivalent exact returns. Those evidence paths remain separated in the tables so blind discovery, warm-start basin behavior, and non-training diagnostics are not merged into one claim.

## Limitations

- Blind training recovery: 4/10 blind runs recovered. This campaign records 2 scaffolded blind recoveries and 2 pure random-initialized blind recoveries; compare declared pure-blind proof suites separately.
- Same-AST exact return: 10 runs snapped back to the compiled seed or exact target; useful basin evidence, not discovery.
- Verified-equivalent exact return: 0 runs snapped to a different exact AST that verified.
- Unsupported gates: 0 runs were blocked by compiler/depth/operator limits and remain in the denominator.
- Failed fits: 6 runs did not pass verifier-owned recovery after training or execution.

## Failed and Unsupported Cases

| Formula | Mode | Class | Reason | Artifact |
|---------|------|-------|--------|----------|
| depth_curve_depth4 | blind | snapped_but_failed | train_failed | [proof-depth-curve-depth-4-blind-0f9bab635276](runs/proof-depth-curve/proof-depth-curve-depth-4-blind-0f9bab635276.json) |
| depth_curve_depth4 | blind | snapped_but_failed | train_failed | [proof-depth-curve-depth-4-blind-344a2756d697](runs/proof-depth-curve/proof-depth-curve-depth-4-blind-344a2756d697.json) |
| depth_curve_depth5 | blind | snapped_but_failed | train_failed | [proof-depth-curve-depth-5-blind-f855e27799b5](runs/proof-depth-curve/proof-depth-curve-depth-5-blind-f855e27799b5.json) |
| depth_curve_depth5 | blind | snapped_but_failed | train_failed | [proof-depth-curve-depth-5-blind-81eda26add96](runs/proof-depth-curve/proof-depth-curve-depth-5-blind-81eda26add96.json) |
| depth_curve_depth6 | blind | snapped_but_failed | train_failed | [proof-depth-curve-depth-6-blind-804a64fb5351](runs/proof-depth-curve/proof-depth-curve-depth-6-blind-804a64fb5351.json) |
| depth_curve_depth6 | blind | snapped_but_failed | train_failed | [proof-depth-curve-depth-6-blind-d2ecd073c61c](runs/proof-depth-curve/proof-depth-curve-depth-6-blind-d2ecd073c61c.json) |

## Next Experiments

- Improve blind optimizer robustness and compare against this campaign's `snapped_but_failed` cases.
- Reduce compiled arithmetic tree depth for formulas gated as unsupported, especially Michaelis-Menten and Planck-style expressions.
- Expand perturbation sweeps after optimizer changes so same-AST returns and verified-equivalent recoveries can be compared over time.
- Add external noisy datasets only after the synthetic/source-document campaign remains reproducible and interpretable.
