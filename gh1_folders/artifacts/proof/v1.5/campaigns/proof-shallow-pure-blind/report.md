# EML Benchmark Campaign Report: proof-shallow-pure-blind

Measured v1.5 shallow pure-blind campaign with scaffold initializers disabled.

## Reproduce

Run this command from a clean checkout:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign proof-shallow-pure-blind --output-root artifacts/proof/v1.5/campaigns --label proof-shallow-pure-blind --overwrite
```

- Suite: `v1.5-shallow-pure-blind`
- Budget tier: `proof-contract`
- Guardrail: 18 runs; declared shallow pure-blind suite with measured recovery metadata.
- Raw run artifacts: [runs/v1.5-shallow-pure-blind](runs/v1.5-shallow-pure-blind)

## Headline Metrics

| Metric | Value |
|--------|-------|
| Total runs | 18 |
| Verifier recovered | 2 (11.1%) |
| Same-AST warm-start returns | 0 (0.0%) |
| Verified equivalent warm-start recoveries | 0 |
| Unsupported | 0 (0.0%) |
| Failed | 16 (88.9%) |
| Median best soft loss | 0.5998 |
| Median post-snap loss | 1.54 |
| Median runtime seconds | 32.57 |

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

This campaign shows the strongest current behavior when the EML representation is verified after snapping: 2/18 runs passed verifier-owned recovery. Warm-start runs are especially useful evidence: 0 returned to the same compiled EML AST and 0 produced a different verified-equivalent AST. Those are not blind-discovery claims, but they are practical evidence that the paper's uniform EML tree can be compiled, embedded, perturbed, optimized, snapped, and independently verified.

## Limitations

- Blind recovery: 2/18 blind runs recovered. Treat this separately from compiler-assisted paths.
- Same-AST warm-start return: 0 runs snapped back to the compiled seed; useful basin evidence, not discovery.
- Verified-equivalent warm-start recovery: 0 runs snapped to a different exact AST that verified.
- Unsupported gates: 0 runs were blocked by compiler/depth/operator limits and remain in the denominator.
- Failed fits: 16 runs did not pass verifier-owned recovery after training or execution.

## Failed and Unsupported Cases

| Formula | Mode | Class | Reason | Artifact |
|---------|------|-------|--------|----------|
| exp | blind | snapped_but_failed | mpmath_failed | [v1-5-shallow-pure-blind-shallow-exp-pure-blind-33f207a0a258](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-exp-pure-blind-33f207a0a258.json) |
| log | blind | snapped_but_failed | mpmath_failed | [v1-5-shallow-pure-blind-shallow-log-pure-blind-5d23e0133651](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-log-pure-blind-5d23e0133651.json) |
| log | blind | snapped_but_failed | mpmath_failed | [v1-5-shallow-pure-blind-shallow-log-pure-blind-c32f58c05c0c](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-log-pure-blind-c32f58c05c0c.json) |
| log | blind | snapped_but_failed | mpmath_failed | [v1-5-shallow-pure-blind-shallow-log-pure-blind-91b636b0e78c](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-log-pure-blind-91b636b0e78c.json) |
| radioactive_decay | blind | snapped_but_failed | mpmath_failed | [v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-d878d4416efa](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-d878d4416efa.json) |
| radioactive_decay | blind | snapped_but_failed | mpmath_failed | [v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-2aeaeb9d06b0](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-2aeaeb9d06b0.json) |
| radioactive_decay | blind | snapped_but_failed | mpmath_failed | [v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-1ef1396484a0](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-1ef1396484a0.json) |
| beer_lambert | blind | snapped_but_failed | mpmath_failed | [v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-28a17bdc90fb](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-28a17bdc90fb.json) |
| beer_lambert | blind | snapped_but_failed | mpmath_failed | [v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-5e820fffc047](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-5e820fffc047.json) |
| beer_lambert | blind | snapped_but_failed | mpmath_failed | [v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-1c08da9a026e](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-1c08da9a026e.json) |
| scaled_exp_growth | blind | snapped_but_failed | mpmath_failed | [v1-5-shallow-pure-blind-shallow-scaled-exp-growth-pure-blind-f043889c07b4](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-scaled-exp-growth-pure-blind-f043889c07b4.json) |
| scaled_exp_growth | blind | snapped_but_failed | mpmath_failed | [v1-5-shallow-pure-blind-shallow-scaled-exp-growth-pure-blind-20f4a9eea1cb](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-scaled-exp-growth-pure-blind-20f4a9eea1cb.json) |
| scaled_exp_growth | blind | snapped_but_failed | mpmath_failed | [v1-5-shallow-pure-blind-shallow-scaled-exp-growth-pure-blind-a37fab2a6be2](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-scaled-exp-growth-pure-blind-a37fab2a6be2.json) |
| scaled_exp_fast_decay | blind | snapped_but_failed | mpmath_failed | [v1-5-shallow-pure-blind-shallow-scaled-exp-fast-decay-pure-blind-ee6092c7c532](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-scaled-exp-fast-decay-pure-blind-ee6092c7c532.json) |
| scaled_exp_fast_decay | blind | snapped_but_failed | mpmath_failed | [v1-5-shallow-pure-blind-shallow-scaled-exp-fast-decay-pure-blind-a8a19903232a](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-scaled-exp-fast-decay-pure-blind-a8a19903232a.json) |
| scaled_exp_fast_decay | blind | snapped_but_failed | mpmath_failed | [v1-5-shallow-pure-blind-shallow-scaled-exp-fast-decay-pure-blind-e77ad734bff7](runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-scaled-exp-fast-decay-pure-blind-e77ad734bff7.json) |

## Next Experiments

- Improve blind optimizer robustness and compare against this campaign's `snapped_but_failed` cases.
- Reduce compiled arithmetic tree depth for formulas gated as unsupported, especially Michaelis-Menten and Planck-style expressions.
- Expand perturbation sweeps after optimizer changes so same-AST returns and verified-equivalent recoveries can be compared over time.
- Add external noisy datasets only after the synthetic/source-document campaign remains reproducible and interpretable.
