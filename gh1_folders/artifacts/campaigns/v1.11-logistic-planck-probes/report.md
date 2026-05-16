# EML Benchmark Campaign Report: paper-probes

Focused v1.11 logistic and Planck compile diagnostics plus low-budget real blind probes.

## Reproduce

Run this command from a clean checkout:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign paper-probes --output-root artifacts/campaigns --label v1.11-logistic-planck-probes --overwrite
```

- Suite: `v1.11-logistic-planck-probes`
- Budget tier: `v1.11-paper`
- Guardrail: 4 runs; compile diagnostics and unsupported/stretch blind probes only, with no promotion from loss.
- Raw run artifacts: [runs/v1.11-logistic-planck-probes](runs/v1.11-logistic-planck-probes)

## Headline Metrics

| Metric | Value |
|--------|-------|
| Total runs | 4 |
| Verifier recovered | 0 (0.0%) |
| Same-AST exact returns | 0 (0.0%) |
| Verified-equivalent exact returns | 0 |
| Unsupported | 2 (50.0%) |
| Failed | 2 (50.0%) |
| Median best soft loss | 102.5 |
| Median post-snap loss | inf |
| Median runtime seconds | 1.03 |

## Regime Summary

| Regime | Runs | Verifier Recovered | Same AST | Verified Equivalent | Unsupported | Failed |
|--------|------|--------------------|----------|---------------------|-------------|--------|
| blind | 2 | 0 | 0 | 0 | 0 | 2 |
| warm_start | 0 | 0 | 0 | 0 | 0 | 0 |
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
- [operator family recovery csv](tables/operator-family-recovery.csv)
- [operator family diagnostics csv](tables/operator-family-diagnostics.csv)
- [operator family comparison md](tables/operator-family-comparison.md)
- [operator family locks json](tables/operator-family-locks.json)
- [headline json](tables/headline-metrics.json)
- [headline csv](tables/headline-metrics.csv)
- [failures csv](tables/failures.csv)

## What EML Demonstrates Well

This campaign shows the strongest current mixed-regime behavior when the EML representation is verified after snapping: 0/4 runs passed verifier-owned recovery. It includes 0/2 blind recoveries, 0 same-AST exact returns, and 0 verified-equivalent exact returns. Those evidence paths remain separated in the tables so blind discovery, warm-start basin behavior, and non-training diagnostics are not merged into one claim.

## Limitations

- Blind training recovery: 0/2 blind runs recovered. This campaign records 0 scaffolded blind recoveries and 0 pure random-initialized blind recoveries; compare declared pure-blind proof suites separately.
- Same-AST exact return: 0 runs snapped back to the compiled seed or exact target; useful basin evidence, not discovery.
- Verified-equivalent exact return: 0 runs snapped to a different exact AST that verified.
- Unsupported gates: 2 runs were blocked by compiler/depth/operator limits and remain in the denominator.
- Failed fits: 2 runs did not pass verifier-owned recovery after training or execution.

## Failed and Unsupported Cases

| Formula | Mode | Class | Reason | Artifact |
|---------|------|-------|--------|----------|
| logistic | compile | unsupported | depth_exceeded | [v1-11-logistic-planck-probes-logistic-compile-d9b410fc6d87](runs/v1.11-logistic-planck-probes/v1-11-logistic-planck-probes-logistic-compile-d9b410fc6d87.json) |
| planck | compile | unsupported | depth_exceeded | [v1-11-logistic-planck-probes-planck-compile-9565da4ea47b](runs/v1.11-logistic-planck-probes/v1-11-logistic-planck-probes-planck-compile-9565da4ea47b.json) |
| logistic | blind | snapped_but_failed | train_failed | [v1-11-logistic-planck-probes-logistic-blind-probe-b35045193c4c](runs/v1.11-logistic-planck-probes/v1-11-logistic-planck-probes-logistic-blind-probe-b35045193c4c.json) |
| planck | blind | failed | train_failed | [v1-11-logistic-planck-probes-planck-blind-probe-be823c997bf6](runs/v1.11-logistic-planck-probes/v1-11-logistic-planck-probes-planck-blind-probe-be823c997bf6.json) |

## Next Experiments

- Improve blind optimizer robustness and compare against this campaign's `snapped_but_failed` cases.
- Reduce compiled arithmetic tree depth for formulas gated as unsupported, especially Michaelis-Menten and Planck-style expressions.
- Expand perturbation sweeps after optimizer changes so same-AST returns and verified-equivalent recoveries can be compared over time.
- Add external noisy datasets only after the synthetic/source-document campaign remains reproducible and interpretable.
