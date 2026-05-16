# EML Benchmark Campaign Report: geml-oscillatory-smoke

Cheap v1.15 raw EML versus i*pi EML smoke campaign for branch-safe matched manifests.

## Reproduce

Run this command from a clean checkout:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign geml-oscillatory-smoke --output-root artifacts/campaigns --label v1.15-geml-oscillatory-smoke --overwrite
```

- Suite: `v1.15-geml-oscillatory-smoke`
- Budget tier: `v1.15-geml`
- Guardrail: 4 configured rows; sin(pi*x) and exp each paired across raw EML and i*pi EML.
- Raw run artifacts: [runs/v1.15-geml-oscillatory-smoke](runs/v1.15-geml-oscillatory-smoke)

## Headline Metrics

| Metric | Value |
|--------|-------|
| Total runs | 4 |
| Verification-passed rows | 0 (0.0%) |
| Trained exact recoveries | 0 (0.0%) |
| Compile-only verified support | 0 (0.0%) |
| Same-AST exact returns | 0 (0.0%) |
| Verified-equivalent exact returns | 0 |
| Unsupported | 0 (0.0%) |
| Failed | 2 (50.0%) |
| Median best soft loss | 0.7222 |
| Median post-snap loss | 0.6087 |
| Median runtime seconds | 1.22 |

## Regime Summary

| Regime | Runs | Verification Passed | Trained Exact | Compile-only Support | Same AST | Verified Equivalent | Unsupported | Failed |
|--------|------|---------------------|---------------|----------------------|----------|---------------------|-------------|--------|
| blind | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| warm_start | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| compile | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| catalog | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| perturbed_tree | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

This table keeps blind, compiler-assisted warm-start, compile-only, catalog, and perturbed true-tree evidence visibly separate before any narrative interpretation.

## Operator-Family Comparison

Family rows keep recovery regimes separate by formula, start mode, training mode, depth, fixed operator, and continuation schedule.

- [comparison markdown](tables/operator-family-comparison.md)
- [recovery CSV](tables/operator-family-recovery.csv)
- [diagnostics CSV](tables/operator-family-diagnostics.csv)
- [regression locks JSON](tables/operator-family-locks.json)

## GEML Paired Comparison

Rows compare matched raw EML and i*pi EML runs using verifier-gated trained recovery, not loss alone.

- Paired rows: 2
- Raw trained exact recovery rate: 0.0%
- i*pi trained exact recovery rate: 0.0%
- [paired markdown](tables/geml-paired-comparison.md)
- [paired CSV](tables/geml-paired-comparison.csv)
- [paired summary JSON](tables/geml-paired-summary.json)

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
- [geml paired comparison csv](tables/geml-paired-comparison.csv)
- [geml paired summary json](tables/geml-paired-summary.json)
- [geml paired comparison md](tables/geml-paired-comparison.md)
- [headline json](tables/headline-metrics.json)
- [headline csv](tables/headline-metrics.csv)
- [failures csv](tables/failures.csv)

## What EML Demonstrates Well

This campaign measures the current pure random-initialized blind boundary: 0/4 blind runs are trained exact recoveries, including 0 threshold-eligible pure blind recoveries, plus 2 repaired candidates. These rows are recovery-boundary evidence, not warm-start exact-return evidence.

## Limitations

- Blind training recovery: 0/4 blind runs recovered. This campaign records 0 scaffolded blind recoveries and 0 pure random-initialized blind recoveries; compare declared pure-blind proof suites separately.
- Same-AST exact return: 0 runs snapped back to the compiled seed or exact target; seed-retention evidence, not discovery.
- Verified-equivalent exact return: 0 runs snapped to a different exact AST that verified.
- Unsupported gates: 0 runs were blocked by compiler/depth/operator limits and remain in the denominator.
- Failed fits: 2 runs did not pass verifier-owned recovery after training or execution.

## Failed and Unsupported Cases

| Formula | Mode | Class | Reason | Artifact |
|---------|------|-------|--------|----------|
| sin_pi | blind | snapped_but_failed | train_failed | [v1-15-geml-oscillatory-smoke-sin-pi-raw-blind-70170745a2b0](runs/v1.15-geml-oscillatory-smoke/v1-15-geml-oscillatory-smoke-sin-pi-raw-blind-70170745a2b0.json) |
| sin_pi | blind | snapped_but_failed | train_failed | [v1-15-geml-oscillatory-smoke-sin-pi-ipi-blind-ea7864a411cc](runs/v1.15-geml-oscillatory-smoke/v1-15-geml-oscillatory-smoke-sin-pi-ipi-blind-ea7864a411cc.json) |

## Next Experiments

- Improve blind optimizer stability and compare against this campaign's `snapped_but_failed` cases.
- Reduce compiled arithmetic tree depth for formulas gated as unsupported, especially Michaelis-Menten and Planck-style expressions.
- Expand perturbation sweeps after optimizer changes so same-AST returns and verified-equivalent recoveries can be compared over time.
- Add external noisy datasets only after the synthetic/source-document campaign remains reproducible and interpretable.
