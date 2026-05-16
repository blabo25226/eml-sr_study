# EML Benchmark Campaign Report: paper-tracks

Combined v1.13 basis-only and literal-constant benchmark tracks with separated denominators.

## Reproduce

Run this command from a clean checkout:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign paper-tracks --output-root artifacts/campaigns --label v1.13-paper-tracks-final --overwrite
```

- Suite: `v1.13-paper-tracks`
- Budget tier: `v1.13-paper`
- Guardrail: 24 configured rows; every publication target appears once in the basis-only compiler policy track and once in the literal-constant warm-start track.
- Raw run artifacts: [runs/v1.13-paper-tracks](runs/v1.13-paper-tracks)

## Headline Metrics

| Metric | Value |
|--------|-------|
| Total runs | 24 |
| Verifier recovered | 9 (37.5%) |
| Same-AST exact returns | 8 (33.3%) |
| Verified-equivalent exact returns | 0 |
| Unsupported | 15 (62.5%) |
| Failed | 0 (0.0%) |
| Median best soft loss | 1.736e-32 |
| Median post-snap loss | 3.513e-32 |
| Median runtime seconds | 0.02438 |

## Regime Summary

| Regime | Runs | Verifier Recovered | Same AST | Verified Equivalent | Unsupported | Failed |
|--------|------|--------------------|----------|---------------------|-------------|--------|
| blind | 0 | 0 | 0 | 0 | 0 | 0 |
| warm_start | 12 | 8 | 8 | 0 | 4 | 0 |
| compile | 12 | 1 | 0 | 0 | 11 | 0 |
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

This campaign shows the strongest current mixed-regime behavior when the EML representation is verified after snapping: 9/24 runs passed verifier-owned recovery. It includes 0/0 blind recoveries, 8 same-AST exact returns, and 0 verified-equivalent exact returns. Those evidence paths remain separated in the tables so blind discovery, warm-start basin behavior, and non-training diagnostics are not merged into one claim.

## Limitations

- Blind training recovery: 0/0 blind runs recovered.
- Same-AST exact return: 8 runs snapped back to the compiled seed or exact target; useful basin evidence, not discovery.
- Verified-equivalent exact return: 0 runs snapped to a different exact AST that verified.
- Unsupported gates: 15 runs were blocked by compiler/depth/operator limits and remain in the denominator.
- Failed fits: 0 runs did not pass verifier-owned recovery after training or execution.

## Failed and Unsupported Cases

| Formula | Mode | Class | Reason | Artifact |
|---------|------|-------|--------|----------|
| log | compile | unsupported | constant_policy | [v1-13-paper-tracks-log-basis-only-compile-b90f584d8bb1](runs/v1.13-paper-tracks/v1-13-paper-tracks-log-basis-only-compile-b90f584d8bb1.json) |
| radioactive_decay | compile | unsupported | constant_policy | [v1-13-paper-tracks-radioactive-decay-basis-only-compile-59cbbd644b4b](runs/v1.13-paper-tracks/v1-13-paper-tracks-radioactive-decay-basis-only-compile-59cbbd644b4b.json) |
| beer_lambert | compile | unsupported | constant_policy | [v1-13-paper-tracks-beer-lambert-basis-only-compile-7be75ecbaa63](runs/v1.13-paper-tracks/v1-13-paper-tracks-beer-lambert-basis-only-compile-7be75ecbaa63.json) |
| scaled_exp_growth | compile | unsupported | constant_policy | [v1-13-paper-tracks-scaled-exp-growth-basis-only-compile-6de3215052b7](runs/v1.13-paper-tracks/v1-13-paper-tracks-scaled-exp-growth-basis-only-compile-6de3215052b7.json) |
| scaled_exp_fast_decay | compile | unsupported | constant_policy | [v1-13-paper-tracks-scaled-exp-fast-decay-basis-only-compile-1b1c434047ab](runs/v1.13-paper-tracks/v1-13-paper-tracks-scaled-exp-fast-decay-basis-only-compile-1b1c434047ab.json) |
| arrhenius | compile | unsupported | constant_policy | [v1-13-paper-tracks-arrhenius-basis-only-compile-c088f39bd857](runs/v1.13-paper-tracks/v1-13-paper-tracks-arrhenius-basis-only-compile-c088f39bd857.json) |
| michaelis_menten | compile | unsupported | constant_policy | [v1-13-paper-tracks-michaelis-menten-basis-only-compile-c2a4f388bd95](runs/v1.13-paper-tracks/v1-13-paper-tracks-michaelis-menten-basis-only-compile-c2a4f388bd95.json) |
| logistic | compile | unsupported | constant_policy | [v1-13-paper-tracks-logistic-basis-only-compile-a32e36271e81](runs/v1.13-paper-tracks/v1-13-paper-tracks-logistic-basis-only-compile-a32e36271e81.json) |
| shockley | compile | unsupported | constant_policy | [v1-13-paper-tracks-shockley-basis-only-compile-28e169b25e29](runs/v1.13-paper-tracks/v1-13-paper-tracks-shockley-basis-only-compile-28e169b25e29.json) |
| damped_oscillator | compile | unsupported | unsupported_operator | [v1-13-paper-tracks-damped-oscillator-basis-only-compile-19df93053992](runs/v1.13-paper-tracks/v1-13-paper-tracks-damped-oscillator-basis-only-compile-19df93053992.json) |
| planck | compile | unsupported | constant_policy | [v1-13-paper-tracks-planck-basis-only-compile-561b8c556ba4](runs/v1.13-paper-tracks/v1-13-paper-tracks-planck-basis-only-compile-561b8c556ba4.json) |
| log | warm_start | unsupported | depth_exceeded | [v1-13-paper-tracks-log-literal-warm-682593206b87](runs/v1.13-paper-tracks/v1-13-paper-tracks-log-literal-warm-682593206b87.json) |
| logistic | warm_start | unsupported | depth_exceeded | [v1-13-paper-tracks-logistic-literal-warm-9ea281dbf3ec](runs/v1.13-paper-tracks/v1-13-paper-tracks-logistic-literal-warm-9ea281dbf3ec.json) |
| damped_oscillator | warm_start | unsupported | unsupported_operator | [v1-13-paper-tracks-damped-oscillator-literal-warm-4ac09e7e05b3](runs/v1.13-paper-tracks/v1-13-paper-tracks-damped-oscillator-literal-warm-4ac09e7e05b3.json) |
| planck | warm_start | unsupported | depth_exceeded | [v1-13-paper-tracks-planck-literal-warm-00693e8cb013](runs/v1.13-paper-tracks/v1-13-paper-tracks-planck-literal-warm-00693e8cb013.json) |

## Next Experiments

- Improve blind optimizer robustness and compare against this campaign's `snapped_but_failed` cases.
- Reduce compiled arithmetic tree depth for formulas gated as unsupported, especially Michaelis-Menten and Planck-style expressions.
- Expand perturbation sweeps after optimizer changes so same-AST returns and verified-equivalent recoveries can be compared over time.
- Add external noisy datasets only after the synthetic/source-document campaign remains reproducible and interpretable.
