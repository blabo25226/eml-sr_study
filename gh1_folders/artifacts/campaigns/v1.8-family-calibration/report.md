# EML Benchmark Campaign Report: family-calibration

Focused v1.8 exp/log operator-family calibration probes before full campaigns.

## Reproduce

Run this command from a clean checkout:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign family-calibration --output-root artifacts/campaigns --label v1.8-family-calibration --overwrite
```

- Suite: `v1.8-family-calibration`
- Budget tier: `v1.8-family-calibration`
- Guardrail: 22 runs; exp/log shallow probes across raw, fixed centered scales, and declared ZEML schedules.
- Raw run artifacts: [runs/v1.8-family-calibration](runs/v1.8-family-calibration)

## Headline Metrics

| Metric | Value |
|--------|-------|
| Total runs | 22 |
| Verifier recovered | 2 (9.1%) |
| Same-AST exact returns | 0 (0.0%) |
| Verified-equivalent exact returns | 0 |
| Unsupported | 0 (0.0%) |
| Failed | 20 (90.9%) |
| Median best soft loss | 0.6217 |
| Median post-snap loss | 1.166 |
| Median runtime seconds | 1.21 |

## Regime Summary

| Regime | Runs | Verifier Recovered | Same AST | Verified Equivalent | Unsupported | Failed |
|--------|------|--------------------|----------|---------------------|-------------|--------|
| blind | 22 | 2 | 0 | 0 | 0 | 20 |
| warm_start | 0 | 0 | 0 | 0 | 0 | 0 |
| compile | 0 | 0 | 0 | 0 | 0 | 0 |
| catalog | 0 | 0 | 0 | 0 | 0 | 0 |
| perturbed_tree | 0 | 0 | 0 | 0 | 0 | 0 |

This table keeps blind, compiler-assisted warm-start, compile-only, catalog, and perturbed-basin evidence visibly separate before any narrative interpretation.

## Operator-Family Comparison

Family rows keep recovery regimes separate by formula, start mode, training mode, depth, fixed operator, and continuation schedule.

- [comparison markdown](tables/operator-family-comparison.md)
- [recovery CSV](tables/operator-family-recovery.csv)
- [diagnostics CSV](tables/operator-family-diagnostics.csv)
- [regression locks JSON](tables/operator-family-locks.json)

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
- [operator family recovery csv](tables/operator-family-recovery.csv)
- [operator family diagnostics csv](tables/operator-family-diagnostics.csv)
- [operator family comparison md](tables/operator-family-comparison.md)
- [operator family locks json](tables/operator-family-locks.json)
- [headline json](tables/headline-metrics.json)
- [headline csv](tables/headline-metrics.csv)
- [failures csv](tables/failures.csv)

## What EML Demonstrates Well

This campaign shows the strongest current bounded blind-training behavior in this bundle: 2/22 blind runs passed verifier-owned recovery, and all 2 recovered rows are scaffolded blind recoveries. Read these results as bounded scaffolded-training evidence, not as pure random-initialized blind discovery.

## Limitations

- Blind training recovery: 2/22 blind runs recovered. This campaign records 2 scaffolded blind recoveries and 0 pure random-initialized blind recoveries; compare declared pure-blind proof suites separately.
- Same-AST exact return: 0 runs snapped back to the compiled seed or exact target; useful basin evidence, not discovery.
- Verified-equivalent exact return: 0 runs snapped to a different exact AST that verified.
- Unsupported gates: 0 runs were blocked by compiler/depth/operator limits and remain in the denominator.
- Failed fits: 20 runs did not pass verifier-owned recovery after training or execution.

## Failed and Unsupported Cases

| Formula | Mode | Class | Reason | Artifact |
|---------|------|-------|--------|----------|
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-calibration-cal-exp-blind-ceml1-da80ed604deb](runs/v1.8-family-calibration/v1-8-family-calibration-cal-exp-blind-ceml1-da80ed604deb.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-calibration-cal-exp-blind-zeml1-36850fb8c754](runs/v1.8-family-calibration/v1-8-family-calibration-cal-exp-blind-zeml1-36850fb8c754.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-calibration-cal-exp-blind-ceml2-28bdf8eae7cb](runs/v1.8-family-calibration/v1-8-family-calibration-cal-exp-blind-ceml2-28bdf8eae7cb.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-calibration-cal-exp-blind-zeml2-3c5545485466](runs/v1.8-family-calibration/v1-8-family-calibration-cal-exp-blind-zeml2-3c5545485466.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-calibration-cal-exp-blind-ceml4-7a34d37e5806](runs/v1.8-family-calibration/v1-8-family-calibration-cal-exp-blind-ceml4-7a34d37e5806.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-calibration-cal-exp-blind-zeml4-97033b3e7f90](runs/v1.8-family-calibration/v1-8-family-calibration-cal-exp-blind-zeml4-97033b3e7f90.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-calibration-cal-exp-blind-ceml8-d51a7b70d1e9](runs/v1.8-family-calibration/v1-8-family-calibration-cal-exp-blind-ceml8-d51a7b70d1e9.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-calibration-cal-exp-blind-zeml8-e3b9ab80a7e5](runs/v1.8-family-calibration/v1-8-family-calibration-cal-exp-blind-zeml8-e3b9ab80a7e5.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-calibration-cal-exp-blind-zeml8-4-b101857743a1](runs/v1.8-family-calibration/v1-8-family-calibration-cal-exp-blind-zeml8-4-b101857743a1.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-calibration-cal-exp-blind-zeml8-4-2-1-da490deccc81](runs/v1.8-family-calibration/v1-8-family-calibration-cal-exp-blind-zeml8-4-2-1-da490deccc81.json) |
| log | blind | snapped_but_failed | train_failed | [v1-8-family-calibration-cal-log-blind-ceml1-145faacc55eb](runs/v1.8-family-calibration/v1-8-family-calibration-cal-log-blind-ceml1-145faacc55eb.json) |
| log | blind | snapped_but_failed | train_failed | [v1-8-family-calibration-cal-log-blind-zeml1-fa1413e3a2b9](runs/v1.8-family-calibration/v1-8-family-calibration-cal-log-blind-zeml1-fa1413e3a2b9.json) |
| log | blind | snapped_but_failed | train_failed | [v1-8-family-calibration-cal-log-blind-ceml2-0c6593c3dbee](runs/v1.8-family-calibration/v1-8-family-calibration-cal-log-blind-ceml2-0c6593c3dbee.json) |
| log | blind | snapped_but_failed | train_failed | [v1-8-family-calibration-cal-log-blind-zeml2-81ac561176ce](runs/v1.8-family-calibration/v1-8-family-calibration-cal-log-blind-zeml2-81ac561176ce.json) |
| log | blind | snapped_but_failed | train_failed | [v1-8-family-calibration-cal-log-blind-ceml4-f22755a5508a](runs/v1.8-family-calibration/v1-8-family-calibration-cal-log-blind-ceml4-f22755a5508a.json) |
| log | blind | snapped_but_failed | train_failed | [v1-8-family-calibration-cal-log-blind-zeml4-cd5f02bf0c9f](runs/v1.8-family-calibration/v1-8-family-calibration-cal-log-blind-zeml4-cd5f02bf0c9f.json) |
| log | blind | snapped_but_failed | train_failed | [v1-8-family-calibration-cal-log-blind-ceml8-9ebccfce1ce0](runs/v1.8-family-calibration/v1-8-family-calibration-cal-log-blind-ceml8-9ebccfce1ce0.json) |
| log | blind | snapped_but_failed | train_failed | [v1-8-family-calibration-cal-log-blind-zeml8-ffe837486086](runs/v1.8-family-calibration/v1-8-family-calibration-cal-log-blind-zeml8-ffe837486086.json) |
| log | blind | snapped_but_failed | train_failed | [v1-8-family-calibration-cal-log-blind-zeml8-4-b461504b22c9](runs/v1.8-family-calibration/v1-8-family-calibration-cal-log-blind-zeml8-4-b461504b22c9.json) |
| log | blind | snapped_but_failed | train_failed | [v1-8-family-calibration-cal-log-blind-zeml8-4-2-1-2312f10518d4](runs/v1.8-family-calibration/v1-8-family-calibration-cal-log-blind-zeml8-4-2-1-2312f10518d4.json) |

## Next Experiments

- Improve blind optimizer robustness and compare against this campaign's `snapped_but_failed` cases.
- Reduce compiled arithmetic tree depth for formulas gated as unsupported, especially Michaelis-Menten and Planck-style expressions.
- Expand perturbation sweeps after optimizer changes so same-AST returns and verified-equivalent recoveries can be compared over time.
- Add external noisy datasets only after the synthetic/source-document campaign remains reproducible and interpretable.
