# EML Benchmark Campaign Report: proof-shallow-pure-blind

Measured v1.5 shallow pure-blind campaign with scaffold initializers disabled.

## Reproduce

Run this command from a clean checkout:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign proof-shallow-pure-blind --output-root artifacts/proof/v1.6/campaigns --label proof-shallow-pure-blind --overwrite
```

- Suite: `v1.5-shallow-pure-blind`
- Budget tier: `proof-contract`
- Guardrail: 18 runs; declared shallow pure-blind suite with measured recovery metadata.
- Raw run artifacts: [runs/v1.5-shallow-pure-blind](runs/v1.5-shallow-pure-blind)

## Headline Metrics

| Metric | Value |
|--------|-------|
| Total runs | 18 |
| Verifier recovered | 3 (16.7%) |
| Same-AST exact returns | 0 (0.0%) |
| Verified-equivalent exact returns | 0 |
| Unsupported | 0 (0.0%) |
| Failed | 15 (83.3%) |
| Median best soft loss | 0.6989 |
| Median post-snap loss | 0.9236 |
| Median runtime seconds | 41.86 |

## Regime Summary

| Regime | Runs | Verifier Recovered | Same AST | Verified Equivalent | Unsupported | Failed |
|--------|------|--------------------|----------|---------------------|-------------|--------|
| blind | 18 | 3 | 0 | 0 | 0 | 15 |
| warm_start | 0 | 0 | 0 | 0 | 0 | 0 |
| compile | 0 | 0 | 0 | 0 | 0 | 0 |
| catalog | 0 | 0 | 0 | 0 | 0 | 0 |
| perturbed_tree | 0 | 0 | 0 | 0 | 0 | 0 |

This table keeps blind, compiler-assisted warm-start, compile-only, catalog, and perturbed-basin evidence visibly separate before any narrative interpretation.

## Proof Contract

| Claim | Threshold | Status | Passed | Eligible | Rate |
|-------|-----------|--------|--------|----------|------|
| paper-shallow-blind-recovery | measured_pure_blind_recovery | reported | 2 | 18 | 0.111 |

Bounded proof thresholds count only allowed verifier-owned training evidence classes; catalog and compile-only verification remain separate evidence classes.

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

This campaign measures the current pure random-initialized blind boundary: 3/18 blind runs passed verifier-owned recovery, including 2 threshold-eligible pure blind recoveries, plus 1 repaired candidate. These rows are recovery-boundary evidence, not warm-start basin evidence.

## Limitations

- Blind training recovery: 3/18 blind runs recovered. This campaign records 0 scaffolded blind recoveries and 2 pure random-initialized blind recoveries; compare declared pure-blind proof suites separately.
- Same-AST exact return: 0 runs snapped back to the compiled seed or exact target; useful basin evidence, not discovery.
- Verified-equivalent exact return: 0 runs snapped to a different exact AST that verified.
- Unsupported gates: 0 runs were blocked by compiler/depth/operator limits and remain in the denominator.
- Failed fits: 15 runs did not pass verifier-owned recovery after training or execution.

## Failed and Unsupported Cases

| Formula | Mode | Class | Reason | Artifact |
|---------|------|-------|--------|----------|
| log | blind | snapped_but_failed | train_failed | [v1-5-shallow-pure-blind-shallow-log-pure-blind-9f03a09a571f](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-log-pure-blind-9f03a09a571f.json) |
| log | blind | snapped_but_failed | train_failed | [v1-5-shallow-pure-blind-shallow-log-pure-blind-3941715f3d32](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-log-pure-blind-3941715f3d32.json) |
| log | blind | snapped_but_failed | train_failed | [v1-5-shallow-pure-blind-shallow-log-pure-blind-03a03c8b35da](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-log-pure-blind-03a03c8b35da.json) |
| radioactive_decay | blind | failed | train_failed | [v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-b8c2dbde649d](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-b8c2dbde649d.json) |
| radioactive_decay | blind | snapped_but_failed | train_failed | [v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-03920c466c9d](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-03920c466c9d.json) |
| radioactive_decay | blind | snapped_but_failed | train_failed | [v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-a48b19cb28a2](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-a48b19cb28a2.json) |
| beer_lambert | blind | snapped_but_failed | train_failed | [v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-d4b6b4704428](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-d4b6b4704428.json) |
| beer_lambert | blind | snapped_but_failed | train_failed | [v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-8599744dc0b5](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-8599744dc0b5.json) |
| beer_lambert | blind | snapped_but_failed | train_failed | [v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-4908b626f452](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-4908b626f452.json) |
| scaled_exp_growth | blind | snapped_but_failed | train_failed | [v1-5-shallow-pure-blind-shallow-scaled-exp-growth-pure-blind-9f934ff0ec8a](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-scaled-exp-growth-pure-blind-9f934ff0ec8a.json) |
| scaled_exp_growth | blind | snapped_but_failed | train_failed | [v1-5-shallow-pure-blind-shallow-scaled-exp-growth-pure-blind-33355177daa0](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-scaled-exp-growth-pure-blind-33355177daa0.json) |
| scaled_exp_growth | blind | snapped_but_failed | train_failed | [v1-5-shallow-pure-blind-shallow-scaled-exp-growth-pure-blind-a546d2037d2d](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-scaled-exp-growth-pure-blind-a546d2037d2d.json) |
| scaled_exp_fast_decay | blind | snapped_but_failed | train_failed | [v1-5-shallow-pure-blind-shallow-scaled-exp-fast-decay-pure-blind-ac77563226c3](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-scaled-exp-fast-decay-pure-blind-ac77563226c3.json) |
| scaled_exp_fast_decay | blind | snapped_but_failed | train_failed | [v1-5-shallow-pure-blind-shallow-scaled-exp-fast-decay-pure-blind-367714cb8a2b](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-scaled-exp-fast-decay-pure-blind-367714cb8a2b.json) |
| scaled_exp_fast_decay | blind | snapped_but_failed | train_failed | [v1-5-shallow-pure-blind-shallow-scaled-exp-fast-decay-pure-blind-a33822512a4d](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-scaled-exp-fast-decay-pure-blind-a33822512a4d.json) |

## Next Experiments

- Improve blind optimizer robustness and compare against this campaign's `snapped_but_failed` cases.
- Reduce compiled arithmetic tree depth for formulas gated as unsupported, especially Michaelis-Menten and Planck-style expressions.
- Expand perturbation sweeps after optimizer changes so same-AST returns and verified-equivalent recoveries can be compared over time.
- Add external noisy datasets only after the synthetic/source-document campaign remains reproducible and interpretable.
