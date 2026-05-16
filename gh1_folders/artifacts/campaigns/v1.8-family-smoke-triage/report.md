# EML Benchmark Campaign Report: family-smoke

CI-scale v1.8 raw-vs-centered operator-family smoke campaign.

## Reproduce

Run this command from a clean checkout:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign family-smoke --output-root artifacts/campaigns --label v1.8-family-smoke-triage --overwrite
```

- Suite: `v1.8-family-smoke`
- Budget tier: `ci`
- Guardrail: 33 runs; raw, fixed CEML/ZEML s={1,2,4,8}, and continuation variants over the smoke suite.
- Raw run artifacts: [runs/v1.8-family-smoke](runs/v1.8-family-smoke)

## Headline Metrics

| Metric | Value |
|--------|-------|
| Total runs | 33 |
| Verifier recovered | 2 (6.1%) |
| Same-AST exact returns | 1 (3.0%) |
| Verified-equivalent exact returns | 0 |
| Unsupported | 21 (63.6%) |
| Failed | 10 (30.3%) |
| Median best soft loss | 1.933 |
| Median post-snap loss | 2.131 |
| Median runtime seconds | 0.02287 |

## Regime Summary

| Regime | Runs | Verifier Recovered | Same AST | Verified Equivalent | Unsupported | Failed |
|--------|------|--------------------|----------|---------------------|-------------|--------|
| blind | 11 | 1 | 0 | 0 | 0 | 10 |
| warm_start | 11 | 1 | 1 | 0 | 10 | 0 |
| compile | 11 | 0 | 0 | 0 | 11 | 0 |
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

This campaign shows the strongest current mixed-regime behavior when the EML representation is verified after snapping: 2/33 runs passed verifier-owned recovery. It includes 1/11 blind recoveries, 1 same-AST exact returns, and 0 verified-equivalent exact returns. Those evidence paths remain separated in the tables so blind discovery, warm-start basin behavior, and non-training diagnostics are not merged into one claim.

## Limitations

- Blind training recovery: 1/11 blind runs recovered. This campaign records 1 scaffolded blind recoveries and 0 pure random-initialized blind recoveries; compare declared pure-blind proof suites separately.
- Same-AST exact return: 1 runs snapped back to the compiled seed or exact target; useful basin evidence, not discovery.
- Verified-equivalent exact return: 0 runs snapped to a different exact AST that verified.
- Unsupported gates: 21 runs were blocked by compiler/depth/operator limits and remain in the denominator.
- Failed fits: 10 runs did not pass verifier-owned recovery after training or execution.

## Failed and Unsupported Cases

| Formula | Mode | Class | Reason | Artifact |
|---------|------|-------|--------|----------|
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-smoke-exp-blind-ceml1-6f5f824f0a5a](runs/v1.8-family-smoke/v1-8-family-smoke-exp-blind-ceml1-6f5f824f0a5a.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-smoke-exp-blind-zeml1-317104765e0b](runs/v1.8-family-smoke/v1-8-family-smoke-exp-blind-zeml1-317104765e0b.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-smoke-exp-blind-ceml2-90ba09a5dd4a](runs/v1.8-family-smoke/v1-8-family-smoke-exp-blind-ceml2-90ba09a5dd4a.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-smoke-exp-blind-zeml2-a372af7f93e7](runs/v1.8-family-smoke/v1-8-family-smoke-exp-blind-zeml2-a372af7f93e7.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-smoke-exp-blind-ceml4-dd30620a15a6](runs/v1.8-family-smoke/v1-8-family-smoke-exp-blind-ceml4-dd30620a15a6.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-smoke-exp-blind-zeml4-bba5d8a1daa3](runs/v1.8-family-smoke/v1-8-family-smoke-exp-blind-zeml4-bba5d8a1daa3.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-smoke-exp-blind-ceml8-23631eb6c4f1](runs/v1.8-family-smoke/v1-8-family-smoke-exp-blind-ceml8-23631eb6c4f1.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-smoke-exp-blind-zeml8-fef4c45fa8c1](runs/v1.8-family-smoke/v1-8-family-smoke-exp-blind-zeml8-fef4c45fa8c1.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-smoke-exp-blind-zeml8-4-d17ddd5caa2c](runs/v1.8-family-smoke/v1-8-family-smoke-exp-blind-zeml8-4-d17ddd5caa2c.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-smoke-exp-blind-zeml8-4-2-1-2d6854735245](runs/v1.8-family-smoke/v1-8-family-smoke-exp-blind-zeml8-4-2-1-2d6854735245.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-smoke-beer-warm-ceml1-c34e4399439f](runs/v1.8-family-smoke/v1-8-family-smoke-beer-warm-ceml1-c34e4399439f.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-smoke-beer-warm-zeml1-28da08b4b6cf](runs/v1.8-family-smoke/v1-8-family-smoke-beer-warm-zeml1-28da08b4b6cf.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-smoke-beer-warm-ceml2-e6701dba96c1](runs/v1.8-family-smoke/v1-8-family-smoke-beer-warm-ceml2-e6701dba96c1.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-smoke-beer-warm-zeml2-476861cccd0c](runs/v1.8-family-smoke/v1-8-family-smoke-beer-warm-zeml2-476861cccd0c.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-smoke-beer-warm-ceml4-fc67fb681b02](runs/v1.8-family-smoke/v1-8-family-smoke-beer-warm-ceml4-fc67fb681b02.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-smoke-beer-warm-zeml4-6a949990d9ee](runs/v1.8-family-smoke/v1-8-family-smoke-beer-warm-zeml4-6a949990d9ee.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-smoke-beer-warm-ceml8-2fc8b32444e2](runs/v1.8-family-smoke/v1-8-family-smoke-beer-warm-ceml8-2fc8b32444e2.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-smoke-beer-warm-zeml8-ec67179bb78c](runs/v1.8-family-smoke/v1-8-family-smoke-beer-warm-zeml8-ec67179bb78c.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-smoke-beer-warm-zeml8-4-81f368278d4c](runs/v1.8-family-smoke/v1-8-family-smoke-beer-warm-zeml8-4-81f368278d4c.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-smoke-beer-warm-zeml8-4-2-1-fe2502914c5b](runs/v1.8-family-smoke/v1-8-family-smoke-beer-warm-zeml8-4-2-1-fe2502914c5b.json) |
| planck | compile | unsupported | depth_exceeded | [v1-8-family-smoke-planck-diagnostic-raw-8ee86832d8a7](runs/v1.8-family-smoke/v1-8-family-smoke-planck-diagnostic-raw-8ee86832d8a7.json) |
| planck | compile | unsupported | depth_exceeded | [v1-8-family-smoke-planck-diagnostic-ceml1-38ded6f58ca3](runs/v1.8-family-smoke/v1-8-family-smoke-planck-diagnostic-ceml1-38ded6f58ca3.json) |
| planck | compile | unsupported | depth_exceeded | [v1-8-family-smoke-planck-diagnostic-zeml1-caaa73ea632b](runs/v1.8-family-smoke/v1-8-family-smoke-planck-diagnostic-zeml1-caaa73ea632b.json) |
| planck | compile | unsupported | depth_exceeded | [v1-8-family-smoke-planck-diagnostic-ceml2-a4ce0774fc16](runs/v1.8-family-smoke/v1-8-family-smoke-planck-diagnostic-ceml2-a4ce0774fc16.json) |
| planck | compile | unsupported | depth_exceeded | [v1-8-family-smoke-planck-diagnostic-zeml2-595426850711](runs/v1.8-family-smoke/v1-8-family-smoke-planck-diagnostic-zeml2-595426850711.json) |
| planck | compile | unsupported | depth_exceeded | [v1-8-family-smoke-planck-diagnostic-ceml4-a28b07a2fac8](runs/v1.8-family-smoke/v1-8-family-smoke-planck-diagnostic-ceml4-a28b07a2fac8.json) |
| planck | compile | unsupported | depth_exceeded | [v1-8-family-smoke-planck-diagnostic-zeml4-9b85fe53e8ca](runs/v1.8-family-smoke/v1-8-family-smoke-planck-diagnostic-zeml4-9b85fe53e8ca.json) |
| planck | compile | unsupported | depth_exceeded | [v1-8-family-smoke-planck-diagnostic-ceml8-4eace4f6f021](runs/v1.8-family-smoke/v1-8-family-smoke-planck-diagnostic-ceml8-4eace4f6f021.json) |
| planck | compile | unsupported | depth_exceeded | [v1-8-family-smoke-planck-diagnostic-zeml8-03bcb971710c](runs/v1.8-family-smoke/v1-8-family-smoke-planck-diagnostic-zeml8-03bcb971710c.json) |
| planck | compile | unsupported | depth_exceeded | [v1-8-family-smoke-planck-diagnostic-zeml8-4-df0ff05244cc](runs/v1.8-family-smoke/v1-8-family-smoke-planck-diagnostic-zeml8-4-df0ff05244cc.json) |
| planck | compile | unsupported | depth_exceeded | [v1-8-family-smoke-planck-diagnostic-zeml8-4-2-1-7751e6ca8d8a](runs/v1.8-family-smoke/v1-8-family-smoke-planck-diagnostic-zeml8-4-2-1-7751e6ca8d8a.json) |

## Next Experiments

- Improve blind optimizer robustness and compare against this campaign's `snapped_but_failed` cases.
- Reduce compiled arithmetic tree depth for formulas gated as unsupported, especially Michaelis-Menten and Planck-style expressions.
- Expand perturbation sweeps after optimizer changes so same-AST returns and verified-equivalent recoveries can be compared over time.
- Add external noisy datasets only after the synthetic/source-document campaign remains reproducible and interpretable.
