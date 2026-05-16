# EML Benchmark Campaign Report: showcase

Expanded campaign for presentation-grade evidence with more seeds and perturbation levels.

## Reproduce

Run this command from a clean checkout:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign showcase --output-root artifacts/campaigns --label v1.6-showcase --overwrite
```

- Suite: `v1.3-showcase`
- Budget tier: `expanded`
- Guardrail: 29 runs; larger blind and perturbation matrix plus full FOR_DEMO diagnostics.
- Raw run artifacts: [runs/v1.3-showcase](runs/v1.3-showcase)

## Headline Metrics

| Metric | Value |
|--------|-------|
| Total runs | 29 |
| Verifier recovered | 19 (65.5%) |
| Same-AST warm-start returns | 12 (41.4%) |
| Verified equivalent warm-start recoveries | 0 |
| Unsupported | 4 (13.8%) |
| Failed | 6 (20.7%) |
| Median best soft loss | 5.247e-33 |
| Median post-snap loss | 4.503e-32 |
| Median runtime seconds | 15.96 |

## Regime Summary

| Regime | Runs | Verifier Recovered | Same AST | Verified Equivalent | Unsupported | Failed |
|--------|------|--------------------|----------|---------------------|-------------|--------|
| blind | 9 | 6 | 0 | 0 | 0 | 3 |
| warm_start | 17 | 13 | 12 | 0 | 1 | 3 |
| compile | 3 | 0 | 0 | 0 | 3 | 0 |
| catalog | 0 | 0 | 0 | 0 | 0 | 0 |
| perturbed_tree | 0 | 0 | 0 | 0 | 0 | 0 |

This table keeps blind, compiler-assisted warm-start, compile-only, catalog, and perturbed-basin evidence visibly separate before any narrative interpretation.

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

This campaign shows the strongest current behavior when the EML representation is verified after snapping: 19/29 runs passed verifier-owned recovery. Warm-start runs are especially useful evidence: 12 returned to the same compiled EML AST and 0 produced a different verified-equivalent AST. Those are not blind-discovery claims, but they are practical evidence that the paper's uniform EML tree can be compiled, embedded, perturbed, optimized, snapped, and independently verified.

## Limitations

- Blind training recovery: 6/9 blind runs recovered. This campaign records 6 scaffolded blind recoveries and 0 pure random-initialized blind recoveries; compare declared pure-blind proof suites separately.
- Same-AST warm-start return: 12 runs snapped back to the compiled seed; useful basin evidence, not discovery.
- Verified-equivalent warm-start recovery: 0 runs snapped to a different exact AST that verified.
- Unsupported gates: 4 runs were blocked by compiler/depth/operator limits and remain in the denominator.
- Failed fits: 6 runs did not pass verifier-owned recovery after training or execution.

## Failed and Unsupported Cases

| Formula | Mode | Class | Reason | Artifact |
|---------|------|-------|--------|----------|
| radioactive_decay | blind | snapped_but_failed | mpmath_failed | [v1-3-showcase-radioactive-decay-blind-b3e3e9713a2f](runs/v1.3-showcase/v1-3-showcase-radioactive-decay-blind-b3e3e9713a2f.json) |
| radioactive_decay | blind | snapped_but_failed | mpmath_failed | [v1-3-showcase-radioactive-decay-blind-e6ed81811e49](runs/v1.3-showcase/v1-3-showcase-radioactive-decay-blind-e6ed81811e49.json) |
| radioactive_decay | blind | snapped_but_failed | mpmath_failed | [v1-3-showcase-radioactive-decay-blind-ad44bbc72189](runs/v1.3-showcase/v1-3-showcase-radioactive-decay-blind-ad44bbc72189.json) |
| beer_lambert | warm_start | snapped_but_failed | verified | [v1-3-showcase-beer-perturbation-sweep-898774a53e8f](runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-898774a53e8f.json) |
| beer_lambert | warm_start | snapped_but_failed | verified | [v1-3-showcase-beer-perturbation-sweep-e461b66ca248](runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-e461b66ca248.json) |
| beer_lambert | warm_start | snapped_but_failed | verified | [v1-3-showcase-beer-perturbation-sweep-9795c140e91e](runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-9795c140e91e.json) |
| michaelis_menten | warm_start | unsupported | depth_exceeded | [v1-3-showcase-michaelis-warm-diagnostic-137223f28fd1](runs/v1.3-showcase/v1-3-showcase-michaelis-warm-diagnostic-137223f28fd1.json) |
| logistic | compile | unsupported | depth_exceeded | [v1-3-showcase-logistic-compile-f711ed10dbe9](runs/v1.3-showcase/v1-3-showcase-logistic-compile-f711ed10dbe9.json) |
| damped_oscillator | compile | unsupported | unsupported_operator | [v1-3-showcase-damped-oscillator-compile-5bbd87a8b2d5](runs/v1.3-showcase/v1-3-showcase-damped-oscillator-compile-5bbd87a8b2d5.json) |
| planck | compile | unsupported | depth_exceeded | [v1-3-showcase-planck-diagnostic-29e4faa8cb28](runs/v1.3-showcase/v1-3-showcase-planck-diagnostic-29e4faa8cb28.json) |

## Next Experiments

- Improve blind optimizer robustness and compare against this campaign's `snapped_but_failed` cases.
- Reduce compiled arithmetic tree depth for formulas gated as unsupported, especially Michaelis-Menten and Planck-style expressions.
- Expand perturbation sweeps after optimizer changes so same-AST returns and verified-equivalent recoveries can be compared over time.
- Add external noisy datasets only after the synthetic/source-document campaign remains reproducible and interpretable.
