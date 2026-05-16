# EML Benchmark Campaign Report: smoke

Fast campaign for CI and development checks.

## Reproduce

Run this command from a clean checkout:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign smoke --output-root artifacts/campaigns --label v1.3-smoke --overwrite
```

- Suite: `smoke`
- Budget tier: `ci`
- Guardrail: 3 runs; shallow blind baseline, one warm-start recovery path, one unsupported diagnostic.
- Raw run artifacts: [runs/smoke](runs/smoke)

## Headline Metrics

| Metric | Value |
|--------|-------|
| Total runs | 3 |
| Verifier recovered | 1 (33.3%) |
| Same-AST warm-start returns | 1 (33.3%) |
| Verified equivalent warm-start recoveries | 0 |
| Unsupported | 1 (33.3%) |
| Failed | 1 (33.3%) |
| Median best soft loss | 3.297 |
| Median post-snap loss | 3.325 |
| Median runtime seconds | 0.2741 |

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

This campaign shows the strongest current behavior when the EML representation is verified after snapping: 1/3 runs passed verifier-owned recovery. Warm-start runs are especially useful evidence: 1 returned to the same compiled EML AST and 0 produced a different verified-equivalent AST. Those are not blind-discovery claims, but they are practical evidence that the paper's uniform EML tree can be compiled, embedded, perturbed, optimized, snapped, and independently verified.

## Limitations

- Blind recovery: 0/1 blind runs recovered. Treat this separately from compiler-assisted paths.
- Same-AST warm-start return: 1 runs snapped back to the compiled seed; useful basin evidence, not discovery.
- Verified-equivalent warm-start recovery: 0 runs snapped to a different exact AST that verified.
- Unsupported gates: 1 runs were blocked by compiler/depth/operator limits and remain in the denominator.
- Failed fits: 1 runs did not pass verifier-owned recovery after training or execution.

## Failed and Unsupported Cases

| Formula | Mode | Class | Reason | Artifact |
|---------|------|-------|--------|----------|
| exp | blind | snapped_but_failed | mpmath_failed | [smoke-exp-blind-44cae09389c3](runs/smoke/smoke-exp-blind-44cae09389c3.json) |
| planck | compile | unsupported | depth_exceeded | [smoke-planck-diagnostic-aaf175aaa0f7](runs/smoke/smoke-planck-diagnostic-aaf175aaa0f7.json) |

## Next Experiments

- Improve blind optimizer robustness and compare against this campaign's `snapped_but_failed` cases.
- Reduce compiled arithmetic tree depth for formulas gated as unsupported, especially Michaelis-Menten and Planck-style expressions.
- Expand perturbation sweeps after optimizer changes so same-AST returns and verified-equivalent recoveries can be compared over time.
- Add external noisy datasets only after the synthetic/source-document campaign remains reproducible and interpretable.
