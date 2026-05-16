# EML Benchmark Campaign Report: showcase

Expanded campaign for presentation-grade evidence with more seeds and perturbation levels.

## Reproduce

Run this command from a clean checkout:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign showcase --output-root artifacts/campaigns --label v1.3-showcase --overwrite
```

- Suite: `v1.3-showcase`
- Budget tier: `expanded`
- Guardrail: 29 runs; larger blind and perturbation matrix plus full FOR_DEMO diagnostics.
- Raw run artifacts: [runs/v1.3-showcase](runs/v1.3-showcase)

## Headline Metrics

| Metric | Value |
|--------|-------|
| Total runs | 29 |
| Verifier recovered | 13 (44.8%) |
| Same-AST warm-start returns | 11 (37.9%) |
| Verified equivalent warm-start recoveries | 0 |
| Unsupported | 5 (17.2%) |
| Failed | 11 (37.9%) |
| Median best soft loss | 7.036e-05 |
| Median post-snap loss | 4.543e-32 |
| Median runtime seconds | 12.75 |

## Figures

- [recovery by formula](figures/recovery-by-formula.svg)
- [recovery by start mode](figures/recovery-by-start-mode.svg)
- [loss before after snap](figures/loss-before-after-snap.svg)
- [beer perturbation](figures/beer-perturbation.svg)
- [runtime depth budget](figures/runtime-depth-budget.svg)
- [failure taxonomy](figures/failure-taxonomy.svg)

## Tables

- [runs csv](tables/runs.csv)
- [group formula csv](tables/group-formula.csv)
- [group start mode csv](tables/group-start-mode.csv)
- [group perturbation noise csv](tables/group-perturbation-noise.csv)
- [group depth csv](tables/group-depth.csv)
- [group failure class csv](tables/group-failure-class.csv)
- [headline json](tables/headline-metrics.json)
- [headline csv](tables/headline-metrics.csv)
- [failures csv](tables/failures.csv)

## What EML Demonstrates Well

This campaign shows the strongest current behavior when the EML representation is verified after snapping: 13/29 runs passed verifier-owned recovery. Warm-start runs are especially useful evidence: 11 returned to the same compiled EML AST and 0 produced a different verified-equivalent AST. Those are not blind-discovery claims, but they are practical evidence that the paper's uniform EML tree can be compiled, embedded, perturbed, optimized, snapped, and independently verified.

## Limitations

- Blind recovery: 2/9 blind runs recovered. Treat this separately from compiler-assisted paths.
- Same-AST warm-start return: 11 runs snapped back to the compiled seed; useful basin evidence, not discovery.
- Verified-equivalent warm-start recovery: 0 runs snapped to a different exact AST that verified.
- Unsupported gates: 5 runs were blocked by compiler/depth/operator limits and remain in the denominator.
- Failed fits: 11 runs did not pass verifier-owned recovery after training or execution.

## Failed and Unsupported Cases

| Formula | Mode | Class | Reason | Artifact |
|---------|------|-------|--------|----------|
| exp | blind | snapped_but_failed | mpmath_failed | [v1-3-showcase-exp-blind-c693d4329a15](runs/v1.3-showcase/v1-3-showcase-exp-blind-c693d4329a15.json) |
| log | blind | snapped_but_failed | mpmath_failed | [v1-3-showcase-log-blind-332dbad5db03](runs/v1.3-showcase/v1-3-showcase-log-blind-332dbad5db03.json) |
| log | blind | snapped_but_failed | mpmath_failed | [v1-3-showcase-log-blind-a52747a50ca2](runs/v1.3-showcase/v1-3-showcase-log-blind-a52747a50ca2.json) |
| log | blind | snapped_but_failed | mpmath_failed | [v1-3-showcase-log-blind-cf7866232845](runs/v1.3-showcase/v1-3-showcase-log-blind-cf7866232845.json) |
| radioactive_decay | blind | failed | mpmath_failed | [v1-3-showcase-radioactive-decay-blind-4a34febadef0](runs/v1.3-showcase/v1-3-showcase-radioactive-decay-blind-4a34febadef0.json) |
| radioactive_decay | blind | failed | mpmath_failed | [v1-3-showcase-radioactive-decay-blind-8055ab006d29](runs/v1.3-showcase/v1-3-showcase-radioactive-decay-blind-8055ab006d29.json) |
| radioactive_decay | blind | failed | mpmath_failed | [v1-3-showcase-radioactive-decay-blind-396f4bdf4078](runs/v1.3-showcase/v1-3-showcase-radioactive-decay-blind-396f4bdf4078.json) |
| beer_lambert | warm_start | snapped_but_failed | verified | [v1-3-showcase-beer-perturbation-sweep-6ffb162a5bb7](runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-6ffb162a5bb7.json) |
| beer_lambert | warm_start | snapped_but_failed | verified | [v1-3-showcase-beer-perturbation-sweep-89c991bee41e](runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-89c991bee41e.json) |
| beer_lambert | warm_start | snapped_but_failed | verified | [v1-3-showcase-beer-perturbation-sweep-8615aab30e44](runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-8615aab30e44.json) |
| beer_lambert | warm_start | snapped_but_failed | verified | [v1-3-showcase-beer-perturbation-sweep-05cb8f1ed422](runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-05cb8f1ed422.json) |
| michaelis_menten | warm_start | unsupported | depth_exceeded | [v1-3-showcase-michaelis-warm-diagnostic-8f1f8084d61b](runs/v1.3-showcase/v1-3-showcase-michaelis-warm-diagnostic-8f1f8084d61b.json) |
| logistic | compile | unsupported | depth_exceeded | [v1-3-showcase-logistic-compile-5a739cf1c01f](runs/v1.3-showcase/v1-3-showcase-logistic-compile-5a739cf1c01f.json) |
| shockley | compile | unsupported | depth_exceeded | [v1-3-showcase-shockley-compile-0119659ca5dd](runs/v1.3-showcase/v1-3-showcase-shockley-compile-0119659ca5dd.json) |
| damped_oscillator | compile | unsupported | unsupported_operator | [v1-3-showcase-damped-oscillator-compile-9b393796ada0](runs/v1.3-showcase/v1-3-showcase-damped-oscillator-compile-9b393796ada0.json) |
| planck | compile | unsupported | depth_exceeded | [v1-3-showcase-planck-diagnostic-1ba93a0c5966](runs/v1.3-showcase/v1-3-showcase-planck-diagnostic-1ba93a0c5966.json) |

## Next Experiments

- Improve blind optimizer robustness and compare against this campaign's `snapped_but_failed` cases.
- Reduce compiled arithmetic tree depth for formulas gated as unsupported, especially Michaelis-Menten and Planck-style expressions.
- Expand perturbation sweeps after optimizer changes so same-AST returns and verified-equivalent recoveries can be compared over time.
- Add external noisy datasets only after the synthetic/source-document campaign remains reproducible and interpretable.
