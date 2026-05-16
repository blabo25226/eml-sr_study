# EML Benchmark Campaign Report: paper-training

Compact v1.11 current-code training refresh for paper figures and claim-safe regime rows.

## Reproduce

Run this command from a clean checkout:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign paper-training --output-root artifacts/campaigns --label v1.11-paper-training --overwrite
```

- Suite: `v1.11-paper-training`
- Budget tier: `v1.11-paper`
- Guardrail: 8 runs; pure blind, scaffolded, same-AST warm-start, and perturbed-basin regimes kept separate.
- Raw run artifacts: [runs/v1.11-paper-training](runs/v1.11-paper-training)

## Headline Metrics

| Metric | Value |
|--------|-------|
| Total runs | 8 |
| Verifier recovered | 8 (100.0%) |
| Same-AST exact returns | 4 (50.0%) |
| Verified-equivalent exact returns | 0 |
| Unsupported | 0 (0.0%) |
| Failed | 0 (0.0%) |
| Median best soft loss | 5.981e-32 |
| Median post-snap loss | 0 |
| Median runtime seconds | 1.108 |

## Regime Summary

| Regime | Runs | Verifier Recovered | Same AST | Verified Equivalent | Unsupported | Failed |
|--------|------|--------------------|----------|---------------------|-------------|--------|
| blind | 4 | 4 | 0 | 0 | 0 | 0 |
| warm_start | 3 | 3 | 3 | 0 | 0 | 0 |
| compile | 0 | 0 | 0 | 0 | 0 | 0 |
| catalog | 0 | 0 | 0 | 0 | 0 | 0 |
| perturbed_tree | 1 | 1 | 1 | 0 | 0 | 0 |

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

This campaign shows the strongest current mixed-regime behavior when the EML representation is verified after snapping: 8/8 runs passed verifier-owned recovery. It includes 4/4 blind recoveries, 4 same-AST exact returns, and 0 verified-equivalent exact returns. Those evidence paths remain separated in the tables so blind discovery, warm-start basin behavior, and non-training diagnostics are not merged into one claim.

## Limitations

- Blind training recovery: 4/4 blind runs recovered. This campaign records 2 scaffolded blind recoveries and 2 pure random-initialized blind recoveries; compare declared pure-blind proof suites separately.
- Same-AST exact return: 4 runs snapped back to the compiled seed or exact target; useful basin evidence, not discovery.
- Verified-equivalent exact return: 0 runs snapped to a different exact AST that verified.
- Unsupported gates: 0 runs were blocked by compiler/depth/operator limits and remain in the denominator.
- Failed fits: 0 runs did not pass verifier-owned recovery after training or execution.

## Failed and Unsupported Cases

No failed or unsupported cases in this campaign.

## Next Experiments

- Improve blind optimizer robustness and compare against this campaign's `snapped_but_failed` cases.
- Reduce compiled arithmetic tree depth for formulas gated as unsupported, especially Michaelis-Menten and Planck-style expressions.
- Expand perturbation sweeps after optimizer changes so same-AST returns and verified-equivalent recoveries can be compared over time.
- Add external noisy datasets only after the synthetic/source-document campaign remains reproducible and interpretable.
