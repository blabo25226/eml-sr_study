# EML Benchmark Campaign Report: showcase

Expanded campaign for presentation-grade evidence with more seeds and perturbation levels.

## Reproduce

Run this command from a clean checkout:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign showcase --output-root artifacts/campaigns --label v1.4-showcase --overwrite
```

- Suite: `v1.3-showcase`
- Budget tier: `expanded`
- Guardrail: 29 runs; larger blind and perturbation matrix plus full FOR_DEMO diagnostics.
- Raw run artifacts: [runs/v1.3-showcase](runs/v1.3-showcase)

## Headline Metrics

| Metric | Value |
|--------|-------|
| Total runs | 29 |
| Verifier recovered | 18 (62.1%) |
| Same-AST warm-start returns | 11 (37.9%) |
| Verified equivalent warm-start recoveries | 0 |
| Unsupported | 4 (13.8%) |
| Failed | 7 (24.1%) |
| Median best soft loss | 5.242e-33 |
| Median post-snap loss | 4.503e-32 |
| Median runtime seconds | 12.68 |

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

This campaign shows the strongest current behavior when the EML representation is verified after snapping: 18/29 runs passed verifier-owned recovery. Warm-start runs are especially useful evidence: 11 returned to the same compiled EML AST and 0 produced a different verified-equivalent AST. Those are not blind-discovery claims, but they are practical evidence that the paper's uniform EML tree can be compiled, embedded, perturbed, optimized, snapped, and independently verified.

## Limitations

- Blind recovery: 6/9 blind runs recovered. Treat this separately from compiler-assisted paths.
- Same-AST warm-start return: 11 runs snapped back to the compiled seed; useful basin evidence, not discovery.
- Verified-equivalent warm-start recovery: 0 runs snapped to a different exact AST that verified.
- Unsupported gates: 4 runs were blocked by compiler/depth/operator limits and remain in the denominator.
- Failed fits: 7 runs did not pass verifier-owned recovery after training or execution.

## Failed and Unsupported Cases

| Formula | Mode | Class | Reason | Artifact |
|---------|------|-------|--------|----------|
| radioactive_decay | blind | snapped_but_failed | mpmath_failed | [v1-3-showcase-radioactive-decay-blind-dbaaf54f8dfc](runs/v1.3-showcase/v1-3-showcase-radioactive-decay-blind-dbaaf54f8dfc.json) |
| radioactive_decay | blind | snapped_but_failed | mpmath_failed | [v1-3-showcase-radioactive-decay-blind-1e9c9e6e9a4c](runs/v1.3-showcase/v1-3-showcase-radioactive-decay-blind-1e9c9e6e9a4c.json) |
| radioactive_decay | blind | snapped_but_failed | mpmath_failed | [v1-3-showcase-radioactive-decay-blind-0015db66c35c](runs/v1.3-showcase/v1-3-showcase-radioactive-decay-blind-0015db66c35c.json) |
| beer_lambert | warm_start | snapped_but_failed | verified | [v1-3-showcase-beer-perturbation-sweep-860689755983](runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-860689755983.json) |
| beer_lambert | warm_start | snapped_but_failed | verified | [v1-3-showcase-beer-perturbation-sweep-56c113f0e392](runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-56c113f0e392.json) |
| beer_lambert | warm_start | snapped_but_failed | verified | [v1-3-showcase-beer-perturbation-sweep-2acd7b37ee9f](runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-2acd7b37ee9f.json) |
| beer_lambert | warm_start | snapped_but_failed | verified | [v1-3-showcase-beer-perturbation-sweep-f83ffd7672b5](runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-f83ffd7672b5.json) |
| michaelis_menten | warm_start | unsupported | depth_exceeded | [v1-3-showcase-michaelis-warm-diagnostic-cb89f09c390e](runs/v1.3-showcase/v1-3-showcase-michaelis-warm-diagnostic-cb89f09c390e.json) |
| logistic | compile | unsupported | depth_exceeded | [v1-3-showcase-logistic-compile-4792983fd836](runs/v1.3-showcase/v1-3-showcase-logistic-compile-4792983fd836.json) |
| damped_oscillator | compile | unsupported | unsupported_operator | [v1-3-showcase-damped-oscillator-compile-cdce11ebc3e2](runs/v1.3-showcase/v1-3-showcase-damped-oscillator-compile-cdce11ebc3e2.json) |
| planck | compile | unsupported | depth_exceeded | [v1-3-showcase-planck-diagnostic-46fe96170216](runs/v1.3-showcase/v1-3-showcase-planck-diagnostic-46fe96170216.json) |

## Next Experiments

- Improve blind optimizer robustness and compare against this campaign's `snapped_but_failed` cases.
- Reduce compiled arithmetic tree depth for formulas gated as unsupported, especially Michaelis-Menten and Planck-style expressions.
- Expand perturbation sweeps after optimizer changes so same-AST returns and verified-equivalent recoveries can be compared over time.
- Add external noisy datasets only after the synthetic/source-document campaign remains reproducible and interpretable.
