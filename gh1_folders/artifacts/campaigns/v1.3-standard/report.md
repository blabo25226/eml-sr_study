# EML Benchmark Campaign Report: standard

Default evidence campaign for crisp numbers, tables, plots, and report narrative.

## Reproduce

Run this command from a clean checkout:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign standard --output-root artifacts/campaigns --label v1.3-standard --overwrite
```

- Suite: `v1.3-standard`
- Budget tier: `showcase-default`
- Guardrail: 16 runs; shallow blind baselines, Beer-Lambert perturbations, and selected FOR_DEMO diagnostics.
- Raw run artifacts: [runs/v1.3-standard](runs/v1.3-standard)

## Headline Metrics

| Metric | Value |
|--------|-------|
| Total runs | 16 |
| Verifier recovered | 5 (31.2%) |
| Same-AST warm-start returns | 4 (25.0%) |
| Verified equivalent warm-start recoveries | 0 |
| Unsupported | 4 (25.0%) |
| Failed | 7 (43.8%) |
| Median best soft loss | 0.6011 |
| Median post-snap loss | 3.435 |
| Median runtime seconds | 0.3151 |

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

This campaign shows the strongest current behavior when the EML representation is verified after snapping: 5/16 runs passed verifier-owned recovery. Warm-start runs are especially useful evidence: 4 returned to the same compiled EML AST and 0 produced a different verified-equivalent AST. Those are not blind-discovery claims, but they are practical evidence that the paper's uniform EML tree can be compiled, embedded, perturbed, optimized, snapped, and independently verified.

## Limitations

- Blind recovery: 1/6 blind runs recovered. Treat this separately from compiler-assisted paths.
- Same-AST warm-start return: 4 runs snapped back to the compiled seed; useful basin evidence, not discovery.
- Verified-equivalent warm-start recovery: 0 runs snapped to a different exact AST that verified.
- Unsupported gates: 4 runs were blocked by compiler/depth/operator limits and remain in the denominator.
- Failed fits: 7 runs did not pass verifier-owned recovery after training or execution.

## Failed and Unsupported Cases

| Formula | Mode | Class | Reason | Artifact |
|---------|------|-------|--------|----------|
| exp | blind | snapped_but_failed | mpmath_failed | [v1-3-standard-exp-blind-a5022d6098c7](runs/v1.3-standard/v1-3-standard-exp-blind-a5022d6098c7.json) |
| log | blind | snapped_but_failed | mpmath_failed | [v1-3-standard-log-blind-194180dc5df0](runs/v1.3-standard/v1-3-standard-log-blind-194180dc5df0.json) |
| log | blind | snapped_but_failed | mpmath_failed | [v1-3-standard-log-blind-99aa5ff393ee](runs/v1.3-standard/v1-3-standard-log-blind-99aa5ff393ee.json) |
| radioactive_decay | blind | failed | mpmath_failed | [v1-3-standard-radioactive-decay-blind-20f83222d0db](runs/v1.3-standard/v1-3-standard-radioactive-decay-blind-20f83222d0db.json) |
| radioactive_decay | blind | failed | mpmath_failed | [v1-3-standard-radioactive-decay-blind-83660c5b4b25](runs/v1.3-standard/v1-3-standard-radioactive-decay-blind-83660c5b4b25.json) |
| beer_lambert | warm_start | snapped_but_failed | verified | [v1-3-standard-beer-perturbation-sweep-348eebff7ed4](runs/v1.3-standard/v1-3-standard-beer-perturbation-sweep-348eebff7ed4.json) |
| beer_lambert | warm_start | snapped_but_failed | verified | [v1-3-standard-beer-perturbation-sweep-68c818aed370](runs/v1.3-standard/v1-3-standard-beer-perturbation-sweep-68c818aed370.json) |
| michaelis_menten | warm_start | unsupported | depth_exceeded | [v1-3-standard-michaelis-warm-diagnostic-37a57673a2e2](runs/v1.3-standard/v1-3-standard-michaelis-warm-diagnostic-37a57673a2e2.json) |
| logistic | compile | unsupported | depth_exceeded | [v1-3-standard-logistic-compile-820d90103856](runs/v1.3-standard/v1-3-standard-logistic-compile-820d90103856.json) |
| shockley | compile | unsupported | depth_exceeded | [v1-3-standard-shockley-compile-e410a7c053d4](runs/v1.3-standard/v1-3-standard-shockley-compile-e410a7c053d4.json) |
| planck | compile | unsupported | depth_exceeded | [v1-3-standard-planck-diagnostic-837e17c92c48](runs/v1.3-standard/v1-3-standard-planck-diagnostic-837e17c92c48.json) |

## Next Experiments

- Improve blind optimizer robustness and compare against this campaign's `snapped_but_failed` cases.
- Reduce compiled arithmetic tree depth for formulas gated as unsupported, especially Michaelis-Menten and Planck-style expressions.
- Expand perturbation sweeps after optimizer changes so same-AST returns and verified-equivalent recoveries can be compared over time.
- Add external noisy datasets only after the synthetic/source-document campaign remains reproducible and interpretable.
