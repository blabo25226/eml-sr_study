# EML Benchmark Campaign Report: standard

Default evidence campaign for crisp numbers, tables, plots, and report narrative.

## Reproduce

Run this command from a clean checkout:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign standard --output-root artifacts/campaigns --label v1.6-standard --overwrite
```

- Suite: `v1.3-standard`
- Budget tier: `showcase-default`
- Guardrail: 16 runs; shallow blind baselines, Beer-Lambert perturbations, and selected FOR_DEMO diagnostics.
- Raw run artifacts: [runs/v1.3-standard](runs/v1.3-standard)

## Headline Metrics

| Metric | Value |
|--------|-------|
| Total runs | 16 |
| Verifier recovered | 9 (56.2%) |
| Same-AST warm-start returns | 5 (31.2%) |
| Verified equivalent warm-start recoveries | 0 |
| Unsupported | 3 (18.8%) |
| Failed | 4 (25.0%) |
| Median best soft loss | 1.14e-32 |
| Median post-snap loss | 4.543e-32 |
| Median runtime seconds | 1.426 |

## Regime Summary

| Regime | Runs | Verifier Recovered | Same AST | Verified Equivalent | Unsupported | Failed |
|--------|------|--------------------|----------|---------------------|-------------|--------|
| blind | 6 | 4 | 0 | 0 | 0 | 2 |
| warm_start | 8 | 5 | 5 | 0 | 1 | 2 |
| compile | 2 | 0 | 0 | 0 | 2 | 0 |
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

This campaign shows the strongest current behavior when the EML representation is verified after snapping: 9/16 runs passed verifier-owned recovery. Warm-start runs are especially useful evidence: 5 returned to the same compiled EML AST and 0 produced a different verified-equivalent AST. Those are not blind-discovery claims, but they are practical evidence that the paper's uniform EML tree can be compiled, embedded, perturbed, optimized, snapped, and independently verified.

## Limitations

- Blind training recovery: 4/6 blind runs recovered. This campaign records 4 scaffolded blind recoveries and 0 pure random-initialized blind recoveries; compare declared pure-blind proof suites separately.
- Same-AST warm-start return: 5 runs snapped back to the compiled seed; useful basin evidence, not discovery.
- Verified-equivalent warm-start recovery: 0 runs snapped to a different exact AST that verified.
- Unsupported gates: 3 runs were blocked by compiler/depth/operator limits and remain in the denominator.
- Failed fits: 4 runs did not pass verifier-owned recovery after training or execution.

## Failed and Unsupported Cases

| Formula | Mode | Class | Reason | Artifact |
|---------|------|-------|--------|----------|
| radioactive_decay | blind | snapped_but_failed | mpmath_failed | [v1-3-standard-radioactive-decay-blind-89532c08e43a](runs/v1.3-standard/v1-3-standard-radioactive-decay-blind-89532c08e43a.json) |
| radioactive_decay | blind | snapped_but_failed | mpmath_failed | [v1-3-standard-radioactive-decay-blind-4f7c8ca23154](runs/v1.3-standard/v1-3-standard-radioactive-decay-blind-4f7c8ca23154.json) |
| beer_lambert | warm_start | snapped_but_failed | verified | [v1-3-standard-beer-perturbation-sweep-7ab0d86550b5](runs/v1.3-standard/v1-3-standard-beer-perturbation-sweep-7ab0d86550b5.json) |
| beer_lambert | warm_start | snapped_but_failed | verified | [v1-3-standard-beer-perturbation-sweep-0a5d1d92fa79](runs/v1.3-standard/v1-3-standard-beer-perturbation-sweep-0a5d1d92fa79.json) |
| michaelis_menten | warm_start | unsupported | depth_exceeded | [v1-3-standard-michaelis-warm-diagnostic-9917f8383370](runs/v1.3-standard/v1-3-standard-michaelis-warm-diagnostic-9917f8383370.json) |
| logistic | compile | unsupported | depth_exceeded | [v1-3-standard-logistic-compile-a99c41f57b97](runs/v1.3-standard/v1-3-standard-logistic-compile-a99c41f57b97.json) |
| planck | compile | unsupported | depth_exceeded | [v1-3-standard-planck-diagnostic-2309e6363fc8](runs/v1.3-standard/v1-3-standard-planck-diagnostic-2309e6363fc8.json) |

## Next Experiments

- Improve blind optimizer robustness and compare against this campaign's `snapped_but_failed` cases.
- Reduce compiled arithmetic tree depth for formulas gated as unsupported, especially Michaelis-Menten and Planck-style expressions.
- Expand perturbation sweeps after optimizer changes so same-AST returns and verified-equivalent recoveries can be compared over time.
- Add external noisy datasets only after the synthetic/source-document campaign remains reproducible and interpretable.
