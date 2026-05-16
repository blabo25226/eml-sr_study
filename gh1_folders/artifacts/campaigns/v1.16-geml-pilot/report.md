# EML Benchmark Campaign Report: geml-v116-pilot

Pilot v1.16 raw EML versus i*pi EML campaign for deciding whether full paper evidence is warranted.

## Reproduce

Run this command from a clean checkout:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign geml-v116-pilot --output-root artifacts/campaigns --label v1.16-geml-pilot --overwrite
```

- Suite: `v1.16-geml-pilot`
- Budget tier: `v1.16-geml`
- Guardrail: 12 configured cases across 2 seeds; pilot must show exact recovery signal before full campaign.
- Raw run artifacts: [runs/v1.16-geml-pilot](runs/v1.16-geml-pilot)

## Headline Metrics

| Metric | Value |
|--------|-------|
| Total runs | 24 |
| Verification-passed rows | 0 (0.0%) |
| Trained exact recoveries | 0 (0.0%) |
| Compile-only verified support | 0 (0.0%) |
| Same-AST exact returns | 0 (0.0%) |
| Verified-equivalent exact returns | 0 |
| Unsupported | 0 (0.0%) |
| Failed | 22 (91.7%) |
| Median best soft loss | 1.078 |
| Median post-snap loss | 1.443 |
| Median runtime seconds | 2.098 |

## Regime Summary

| Regime | Runs | Verification Passed | Trained Exact | Compile-only Support | Same AST | Verified Equivalent | Unsupported | Failed |
|--------|------|---------------------|---------------|----------------------|----------|---------------------|-------------|--------|
| blind | 24 | 0 | 0 | 0 | 0 | 0 | 0 | 22 |
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

- Paired rows: 12
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

This campaign measures the current pure random-initialized blind boundary: 0/24 blind runs are trained exact recoveries, including 0 threshold-eligible pure blind recoveries, plus 2 repaired candidates. These rows are recovery-boundary evidence, not warm-start exact-return evidence.

## Limitations

- Blind training recovery: 0/24 blind runs recovered. This campaign records 0 scaffolded blind recoveries and 0 pure random-initialized blind recoveries; compare declared pure-blind proof suites separately.
- Same-AST exact return: 0 runs snapped back to the compiled seed or exact target; seed-retention evidence, not discovery.
- Verified-equivalent exact return: 0 runs snapped to a different exact AST that verified.
- Unsupported gates: 0 runs were blocked by compiler/depth/operator limits and remain in the denominator.
- Failed fits: 22 runs did not pass verifier-owned recovery after training or execution.

## Failed and Unsupported Cases

| Formula | Mode | Class | Reason | Artifact |
|---------|------|-------|--------|----------|
| sin_pi | blind | snapped_but_failed | train_failed | [v1-16-geml-pilot-sin-pi-raw-v116-blind-220d22c0209c](runs/v1.16-geml-pilot/v1-16-geml-pilot-sin-pi-raw-v116-blind-220d22c0209c.json) |
| sin_pi | blind | snapped_but_failed | train_failed | [v1-16-geml-pilot-sin-pi-raw-v116-blind-7aaf87676b6f](runs/v1.16-geml-pilot/v1-16-geml-pilot-sin-pi-raw-v116-blind-7aaf87676b6f.json) |
| sin_pi | blind | snapped_but_failed | train_failed | [v1-16-geml-pilot-sin-pi-ipi-v116-blind-2dbf88bedf2b](runs/v1.16-geml-pilot/v1-16-geml-pilot-sin-pi-ipi-v116-blind-2dbf88bedf2b.json) |
| sin_pi | blind | snapped_but_failed | train_failed | [v1-16-geml-pilot-sin-pi-ipi-v116-blind-c803be2bb022](runs/v1.16-geml-pilot/v1-16-geml-pilot-sin-pi-ipi-v116-blind-c803be2bb022.json) |
| cos_pi | blind | snapped_but_failed | train_failed | [v1-16-geml-pilot-cos-pi-raw-v116-blind-c9906f0a620d](runs/v1.16-geml-pilot/v1-16-geml-pilot-cos-pi-raw-v116-blind-c9906f0a620d.json) |
| cos_pi | blind | snapped_but_failed | train_failed | [v1-16-geml-pilot-cos-pi-raw-v116-blind-434cf45abd91](runs/v1.16-geml-pilot/v1-16-geml-pilot-cos-pi-raw-v116-blind-434cf45abd91.json) |
| cos_pi | blind | snapped_but_failed | train_failed | [v1-16-geml-pilot-cos-pi-ipi-v116-blind-d646ceb81086](runs/v1.16-geml-pilot/v1-16-geml-pilot-cos-pi-ipi-v116-blind-d646ceb81086.json) |
| cos_pi | blind | snapped_but_failed | train_failed | [v1-16-geml-pilot-cos-pi-ipi-v116-blind-8400b3ba3d1b](runs/v1.16-geml-pilot/v1-16-geml-pilot-cos-pi-ipi-v116-blind-8400b3ba3d1b.json) |
| harmonic_sum | blind | snapped_but_failed | train_failed | [v1-16-geml-pilot-harmonic-sum-raw-v116-blind-894efc04fa0d](runs/v1.16-geml-pilot/v1-16-geml-pilot-harmonic-sum-raw-v116-blind-894efc04fa0d.json) |
| harmonic_sum | blind | snapped_but_failed | train_failed | [v1-16-geml-pilot-harmonic-sum-raw-v116-blind-a3087f36bc71](runs/v1.16-geml-pilot/v1-16-geml-pilot-harmonic-sum-raw-v116-blind-a3087f36bc71.json) |
| harmonic_sum | blind | snapped_but_failed | train_failed | [v1-16-geml-pilot-harmonic-sum-ipi-v116-blind-6dce386f4e7b](runs/v1.16-geml-pilot/v1-16-geml-pilot-harmonic-sum-ipi-v116-blind-6dce386f4e7b.json) |
| harmonic_sum | blind | snapped_but_failed | train_failed | [v1-16-geml-pilot-harmonic-sum-ipi-v116-blind-cbcffbfb08d5](runs/v1.16-geml-pilot/v1-16-geml-pilot-harmonic-sum-ipi-v116-blind-cbcffbfb08d5.json) |
| log_periodic_oscillation | blind | snapped_but_failed | train_failed | [v1-16-geml-pilot-log-periodic-oscillation-raw-v116-blind-c15ac8ea4804](runs/v1.16-geml-pilot/v1-16-geml-pilot-log-periodic-oscillation-raw-v116-blind-c15ac8ea4804.json) |
| log_periodic_oscillation | blind | snapped_but_failed | train_failed | [v1-16-geml-pilot-log-periodic-oscillation-raw-v116-blind-cb9b0243d688](runs/v1.16-geml-pilot/v1-16-geml-pilot-log-periodic-oscillation-raw-v116-blind-cb9b0243d688.json) |
| log_periodic_oscillation | blind | snapped_but_failed | train_failed | [v1-16-geml-pilot-log-periodic-oscillation-ipi-v116-blind-b9dc27c7c5eb](runs/v1.16-geml-pilot/v1-16-geml-pilot-log-periodic-oscillation-ipi-v116-blind-b9dc27c7c5eb.json) |
| log_periodic_oscillation | blind | snapped_but_failed | train_failed | [v1-16-geml-pilot-log-periodic-oscillation-ipi-v116-blind-7e17daae2089](runs/v1.16-geml-pilot/v1-16-geml-pilot-log-periodic-oscillation-ipi-v116-blind-7e17daae2089.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-16-geml-pilot-exp-ipi-v116-blind-96fd9b472e1c](runs/v1.16-geml-pilot/v1-16-geml-pilot-exp-ipi-v116-blind-96fd9b472e1c.json) |
| exp | blind | snapped_but_failed | train_failed | [v1-16-geml-pilot-exp-ipi-v116-blind-f16264d68e9f](runs/v1.16-geml-pilot/v1-16-geml-pilot-exp-ipi-v116-blind-f16264d68e9f.json) |
| log | blind | snapped_but_failed | train_failed | [v1-16-geml-pilot-log-raw-v116-blind-5017393b5d99](runs/v1.16-geml-pilot/v1-16-geml-pilot-log-raw-v116-blind-5017393b5d99.json) |
| log | blind | snapped_but_failed | train_failed | [v1-16-geml-pilot-log-raw-v116-blind-d348cd35ea0c](runs/v1.16-geml-pilot/v1-16-geml-pilot-log-raw-v116-blind-d348cd35ea0c.json) |
| log | blind | snapped_but_failed | train_failed | [v1-16-geml-pilot-log-ipi-v116-blind-84e0e981b471](runs/v1.16-geml-pilot/v1-16-geml-pilot-log-ipi-v116-blind-84e0e981b471.json) |
| log | blind | snapped_but_failed | train_failed | [v1-16-geml-pilot-log-ipi-v116-blind-1cede807b734](runs/v1.16-geml-pilot/v1-16-geml-pilot-log-ipi-v116-blind-1cede807b734.json) |

## Next Experiments

- Improve blind optimizer stability and compare against this campaign's `snapped_but_failed` cases.
- Reduce compiled arithmetic tree depth for formulas gated as unsupported, especially Michaelis-Menten and Planck-style expressions.
- Expand perturbation sweeps after optimizer changes so same-AST returns and verified-equivalent recoveries can be compared over time.
- Add external noisy datasets only after the synthetic/source-document campaign remains reproducible and interpretable.
