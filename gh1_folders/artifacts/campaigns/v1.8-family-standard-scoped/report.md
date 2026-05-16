# EML Benchmark Campaign Report: family-standard

v1.8 standard-style raw-vs-centered operator-family comparison campaign.

## Reproduce

Run this command from a clean checkout:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign family-standard --output-root artifacts/campaigns --label v1.8-family-standard-scoped --overwrite --formula exp --formula log --formula beer_lambert --seed 0
```

- Suite: `v1.8-family-standard`
- Budget tier: `v1.8-family-matrix`
- Guardrail: Standard-style comparison cloned across expanded v1.8 operator variants with isolated v1.8 outputs.
- Raw run artifacts: [runs/v1.8-family-standard](runs/v1.8-family-standard)

## Headline Metrics

| Metric | Value |
|--------|-------|
| Total runs | 55 |
| Verifier recovered | 4 (7.3%) |
| Same-AST exact returns | 2 (3.6%) |
| Verified-equivalent exact returns | 0 |
| Unsupported | 30 (54.5%) |
| Failed | 21 (38.2%) |
| Median best soft loss | 1.076 |
| Median post-snap loss | 1.336 |
| Median runtime seconds | 0.02662 |

## Regime Summary

| Regime | Runs | Verifier Recovered | Same AST | Verified Equivalent | Unsupported | Failed |
|--------|------|--------------------|----------|---------------------|-------------|--------|
| blind | 22 | 2 | 0 | 0 | 0 | 20 |
| warm_start | 33 | 2 | 2 | 0 | 30 | 1 |
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

This campaign shows the strongest current mixed-regime behavior when the EML representation is verified after snapping: 4/55 runs passed verifier-owned recovery. It includes 2/22 blind recoveries, 2 same-AST exact returns, and 0 verified-equivalent exact returns. Those evidence paths remain separated in the tables so blind discovery, warm-start basin behavior, and non-training diagnostics are not merged into one claim.

## Limitations

- Blind training recovery: 2/22 blind runs recovered. This campaign records 2 scaffolded blind recoveries and 0 pure random-initialized blind recoveries; compare declared pure-blind proof suites separately.
- Same-AST exact return: 2 runs snapped back to the compiled seed or exact target; useful basin evidence, not discovery.
- Verified-equivalent exact return: 0 runs snapped to a different exact AST that verified.
- Unsupported gates: 30 runs were blocked by compiler/depth/operator limits and remain in the denominator.
- Failed fits: 21 runs did not pass verifier-owned recovery after training or execution.

## Failed and Unsupported Cases

| Formula | Mode | Class | Reason | Artifact |
|---------|------|-------|--------|----------|
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-standard-exp-blind-ceml1-4ac74eb747e9](runs/v1.8-family-standard/v1-8-family-standard-exp-blind-ceml1-4ac74eb747e9.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-standard-exp-blind-zeml1-c9c4d5c0452f](runs/v1.8-family-standard/v1-8-family-standard-exp-blind-zeml1-c9c4d5c0452f.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-standard-exp-blind-ceml2-3460d3d0f07b](runs/v1.8-family-standard/v1-8-family-standard-exp-blind-ceml2-3460d3d0f07b.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-standard-exp-blind-zeml2-052d8389ce66](runs/v1.8-family-standard/v1-8-family-standard-exp-blind-zeml2-052d8389ce66.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-standard-exp-blind-ceml4-26af8c11d98f](runs/v1.8-family-standard/v1-8-family-standard-exp-blind-ceml4-26af8c11d98f.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-standard-exp-blind-zeml4-fc85b8b90bd9](runs/v1.8-family-standard/v1-8-family-standard-exp-blind-zeml4-fc85b8b90bd9.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-standard-exp-blind-ceml8-57c361c3087d](runs/v1.8-family-standard/v1-8-family-standard-exp-blind-ceml8-57c361c3087d.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-standard-exp-blind-zeml8-e04f0ac48af2](runs/v1.8-family-standard/v1-8-family-standard-exp-blind-zeml8-e04f0ac48af2.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-standard-exp-blind-zeml8-4-f86120c07c43](runs/v1.8-family-standard/v1-8-family-standard-exp-blind-zeml8-4-f86120c07c43.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-8-family-standard-exp-blind-zeml8-4-2-1-22405499cfd3](runs/v1.8-family-standard/v1-8-family-standard-exp-blind-zeml8-4-2-1-22405499cfd3.json) |
| log | blind | snapped_but_failed | train_failed | [v1-8-family-standard-log-blind-ceml1-500936c57f56](runs/v1.8-family-standard/v1-8-family-standard-log-blind-ceml1-500936c57f56.json) |
| log | blind | snapped_but_failed | train_failed | [v1-8-family-standard-log-blind-zeml1-4298c6f72051](runs/v1.8-family-standard/v1-8-family-standard-log-blind-zeml1-4298c6f72051.json) |
| log | blind | snapped_but_failed | train_failed | [v1-8-family-standard-log-blind-ceml2-65b963c89fe2](runs/v1.8-family-standard/v1-8-family-standard-log-blind-ceml2-65b963c89fe2.json) |
| log | blind | snapped_but_failed | train_failed | [v1-8-family-standard-log-blind-zeml2-047716b7ebfd](runs/v1.8-family-standard/v1-8-family-standard-log-blind-zeml2-047716b7ebfd.json) |
| log | blind | snapped_but_failed | train_failed | [v1-8-family-standard-log-blind-ceml4-8bfc5907251e](runs/v1.8-family-standard/v1-8-family-standard-log-blind-ceml4-8bfc5907251e.json) |
| log | blind | snapped_but_failed | train_failed | [v1-8-family-standard-log-blind-zeml4-1e4906b2ec67](runs/v1.8-family-standard/v1-8-family-standard-log-blind-zeml4-1e4906b2ec67.json) |
| log | blind | snapped_but_failed | train_failed | [v1-8-family-standard-log-blind-ceml8-1cb2f880fa79](runs/v1.8-family-standard/v1-8-family-standard-log-blind-ceml8-1cb2f880fa79.json) |
| log | blind | snapped_but_failed | train_failed | [v1-8-family-standard-log-blind-zeml8-aea3cc56bb3e](runs/v1.8-family-standard/v1-8-family-standard-log-blind-zeml8-aea3cc56bb3e.json) |
| log | blind | snapped_but_failed | train_failed | [v1-8-family-standard-log-blind-zeml8-4-330e850cf115](runs/v1.8-family-standard/v1-8-family-standard-log-blind-zeml8-4-330e850cf115.json) |
| log | blind | snapped_but_failed | train_failed | [v1-8-family-standard-log-blind-zeml8-4-2-1-2fd93e56ae3b](runs/v1.8-family-standard/v1-8-family-standard-log-blind-zeml8-4-2-1-2fd93e56ae3b.json) |
| beer_lambert | warm_start | snapped_but_failed | verified | [v1-8-family-standard-beer-perturbation-sweep-raw-7b05bd4371e8](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-raw-7b05bd4371e8.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-ceml1-146335ce3726](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-ceml1-146335ce3726.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-ceml1-55d57998a902](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-ceml1-55d57998a902.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-ceml1-5bb6d361f55c](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-ceml1-5bb6d361f55c.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-zeml1-32c4d2e4d993](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml1-32c4d2e4d993.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-zeml1-5c03faa3db0d](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml1-5c03faa3db0d.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-zeml1-f2b4e5a617ba](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml1-f2b4e5a617ba.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-ceml2-a0369f6c88f9](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-ceml2-a0369f6c88f9.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-ceml2-ddb5f3a08a00](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-ceml2-ddb5f3a08a00.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-ceml2-b0c30057282d](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-ceml2-b0c30057282d.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-zeml2-486c46e2f769](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml2-486c46e2f769.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-zeml2-274fd7b0df71](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml2-274fd7b0df71.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-zeml2-5d0d1805d66e](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml2-5d0d1805d66e.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-ceml4-740b75a4dfc1](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-ceml4-740b75a4dfc1.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-ceml4-64abb61351e3](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-ceml4-64abb61351e3.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-ceml4-e22858d2497a](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-ceml4-e22858d2497a.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-zeml4-a4c14acf6544](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml4-a4c14acf6544.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-zeml4-0981a6b74629](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml4-0981a6b74629.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-zeml4-c43701519585](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml4-c43701519585.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-ceml8-52ca002e41e7](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-ceml8-52ca002e41e7.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-ceml8-180ebe5aefb4](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-ceml8-180ebe5aefb4.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-ceml8-423f08ba249e](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-ceml8-423f08ba249e.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-zeml8-d2fb5d5d1422](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml8-d2fb5d5d1422.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-zeml8-a08d9eab88b3](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml8-a08d9eab88b3.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-zeml8-8b46234c400d](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml8-8b46234c400d.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-zeml8-4-de36987134db](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml8-4-de36987134db.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-zeml8-4-4809cd878a8a](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml8-4-4809cd878a8a.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-zeml8-4-b39172296e88](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml8-4-b39172296e88.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-zeml8-4-2-1-fc695301052f](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml8-4-2-1-fc695301052f.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-zeml8-4-2-1-40893926f4de](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml8-4-2-1-40893926f4de.json) |
| beer_lambert | warm_start | unsupported | centered_family_same_family_seed_missing | [v1-8-family-standard-beer-perturbation-sweep-zeml8-4-2-1-79858f854a23](runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml8-4-2-1-79858f854a23.json) |

## Next Experiments

- Improve blind optimizer robustness and compare against this campaign's `snapped_but_failed` cases.
- Reduce compiled arithmetic tree depth for formulas gated as unsupported, especially Michaelis-Menten and Planck-style expressions.
- Expand perturbation sweeps after optimizer changes so same-AST returns and verified-equivalent recoveries can be compared over time.
- Add external noisy datasets only after the synthetic/source-document campaign remains reproducible and interpretable.
