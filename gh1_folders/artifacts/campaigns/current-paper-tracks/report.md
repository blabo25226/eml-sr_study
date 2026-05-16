# EML Benchmark Campaign Report: paper-tracks

Combined v1.13 basis-only and literal-constant benchmark tracks with separated denominators.

## Reproduce

Run this command from a clean checkout:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign paper-tracks --output-root 'artifacts\campaigns' --label current-paper-tracks --overwrite
```

- Suite: `v1.13-paper-tracks`
- Budget tier: `v1.13-paper`
- Guardrail: 24 configured rows; every publication target appears once in the basis-only compiler policy track and once in the literal-constant warm-start track.
- Raw run artifacts: [runs/v1.13-paper-tracks](runs/v1.13-paper-tracks)

## Headline Metrics

| Metric | Value |
|--------|-------|
| Total runs | 24 |
| Verification-passed rows | 9 (37.5%) |
| Trained exact recoveries | 8 (33.3%) |
| Compile-only verified support | 1 (4.2%) |
| Same-AST exact returns | 8 (33.3%) |
| Verified-equivalent exact returns | 0 |
| Unsupported | 15 (62.5%) |
| Failed | 0 (0.0%) |
| Median best soft loss | 5.947e-32 |
| Median post-snap loss | 3.455e-32 |
| Median runtime seconds | 0.08527 |

## Regime Summary

| Regime | Runs | Verification Passed | Trained Exact | Compile-only Support | Same AST | Verified Equivalent | Unsupported | Failed |
|--------|------|---------------------|---------------|----------------------|----------|---------------------|-------------|--------|
| blind | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| warm_start | 12 | 8 | 8 | 0 | 8 | 0 | 4 | 0 |
| compile | 12 | 1 | 0 | 1 | 0 | 0 | 11 | 0 |
| catalog | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| perturbed_tree | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

This table keeps blind, compiler-assisted warm-start, compile-only, catalog, and perturbed true-tree evidence visibly separate before any narrative interpretation.

## Warm-Start Evidence

| Run | Evidence | Perturbation Noise | Warm Steps | Warm Restarts | Total Restarts | Return Kind | AST Return |
|-----|----------|--------------------|------------|---------------|----------------|-------------|------------|
| v1-13-paper-tracks-exp-literal-warm-f53942aad6c4 | exact_seed_round_trip | 0.0 | 1 | 1 | 1 |  | same_ast |
| v1-13-paper-tracks-log-literal-warm-9a40ffd91e38 | unsupported | 0.0 | 1 | 1 | 1 |  | unsupported |
| v1-13-paper-tracks-radioactive-decay-literal-warm-f404a736ffb9 | exact_seed_round_trip | 0.0 | 1 | 1 | 1 |  | same_ast |
| v1-13-paper-tracks-beer-lambert-literal-warm-adfce05dbfa9 | exact_seed_round_trip | 0.0 | 1 | 1 | 1 |  | same_ast |
| v1-13-paper-tracks-scaled-exp-growth-literal-warm-cf7b378f615e | exact_seed_round_trip | 0.0 | 1 | 1 | 1 |  | same_ast |
| v1-13-paper-tracks-scaled-exp-fast-decay-literal-warm-308039976a83 | exact_seed_round_trip | 0.0 | 1 | 1 | 1 |  | same_ast |
| v1-13-paper-tracks-arrhenius-literal-warm-6ea396db7d91 | exact_seed_round_trip | 0.0 | 1 | 1 | 1 |  | same_ast |
| v1-13-paper-tracks-michaelis-menten-literal-warm-cfacd8bc2b60 | exact_seed_round_trip | 0.0 | 1 | 1 | 1 |  | same_ast |
| v1-13-paper-tracks-logistic-literal-warm-0f6989cbe549 | unsupported | 0.0 | 1 | 1 | 1 |  | unsupported |
| v1-13-paper-tracks-shockley-literal-warm-9be8e689169b | exact_seed_round_trip | 0.0 | 1 | 1 | 1 |  | same_ast |
| v1-13-paper-tracks-damped-oscillator-literal-warm-de3e7e8afc6c | unsupported | 0.0 | 1 | 1 | 1 |  | unsupported |
| v1-13-paper-tracks-planck-literal-warm-a31543749aa2 | unsupported | 0.0 | 1 | 1 | 1 |  | unsupported |

Rows labeled `exact_seed_round_trip` are exact seed round-trips: they start from the compiled seed with zero perturbation and return to the same exact AST.

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

This campaign shows the strongest current mixed-regime behavior when the EML representation is verified after snapping: 9/24 rows passed verification, split into 8 trained exact recoveries and 1 compile-only verified support rows. It includes 0/0 blind recoveries, 8 same-AST exact returns, and 0 verified-equivalent exact returns. Those evidence paths remain separated in the tables so blind discovery, warm-start exact returns, and non-training diagnostics are not merged into one claim.

## Limitations

- Blind training recovery: 0/0 blind runs recovered.
- Same-AST exact return: 8 runs snapped back to the compiled seed or exact target; seed-retention evidence, not discovery.
- Verified-equivalent exact return: 0 runs snapped to a different exact AST that verified.
- Unsupported gates: 15 runs were blocked by compiler/depth/operator limits and remain in the denominator.
- Failed fits: 0 runs did not pass verifier-owned recovery after training or execution.

## Failed and Unsupported Cases

| Formula | Mode | Class | Reason | Artifact |
|---------|------|-------|--------|----------|
| log | compile | unsupported | constant_policy | [v1-13-paper-tracks-log-basis-only-compile-32f1f1ecb80c](runs/v1.13-paper-tracks/v1-13-paper-tracks-log-basis-only-compile-32f1f1ecb80c.json) |
| radioactive_decay | compile | unsupported | constant_policy | [v1-13-paper-tracks-radioactive-decay-basis-only-compile-ebe90922f383](runs/v1.13-paper-tracks/v1-13-paper-tracks-radioactive-decay-basis-only-compile-ebe90922f383.json) |
| beer_lambert | compile | unsupported | constant_policy | [v1-13-paper-tracks-beer-lambert-basis-only-compile-69e15fc06bef](runs/v1.13-paper-tracks/v1-13-paper-tracks-beer-lambert-basis-only-compile-69e15fc06bef.json) |
| scaled_exp_growth | compile | unsupported | constant_policy | [v1-13-paper-tracks-scaled-exp-growth-basis-only-compile-6036bc33a562](runs/v1.13-paper-tracks/v1-13-paper-tracks-scaled-exp-growth-basis-only-compile-6036bc33a562.json) |
| scaled_exp_fast_decay | compile | unsupported | constant_policy | [v1-13-paper-tracks-scaled-exp-fast-decay-basis-only-compile-1f7a12b07d05](runs/v1.13-paper-tracks/v1-13-paper-tracks-scaled-exp-fast-decay-basis-only-compile-1f7a12b07d05.json) |
| arrhenius | compile | unsupported | constant_policy | [v1-13-paper-tracks-arrhenius-basis-only-compile-fc0729d1e8c7](runs/v1.13-paper-tracks/v1-13-paper-tracks-arrhenius-basis-only-compile-fc0729d1e8c7.json) |
| michaelis_menten | compile | unsupported | constant_policy | [v1-13-paper-tracks-michaelis-menten-basis-only-compile-2309755498fa](runs/v1.13-paper-tracks/v1-13-paper-tracks-michaelis-menten-basis-only-compile-2309755498fa.json) |
| logistic | compile | unsupported | constant_policy | [v1-13-paper-tracks-logistic-basis-only-compile-ef8ffeed064f](runs/v1.13-paper-tracks/v1-13-paper-tracks-logistic-basis-only-compile-ef8ffeed064f.json) |
| shockley | compile | unsupported | constant_policy | [v1-13-paper-tracks-shockley-basis-only-compile-dc9d2db8a8d6](runs/v1.13-paper-tracks/v1-13-paper-tracks-shockley-basis-only-compile-dc9d2db8a8d6.json) |
| damped_oscillator | compile | unsupported | unsupported_operator | [v1-13-paper-tracks-damped-oscillator-basis-only-compile-9f887e42dbf9](runs/v1.13-paper-tracks/v1-13-paper-tracks-damped-oscillator-basis-only-compile-9f887e42dbf9.json) |
| planck | compile | unsupported | constant_policy | [v1-13-paper-tracks-planck-basis-only-compile-f40737d8466b](runs/v1.13-paper-tracks/v1-13-paper-tracks-planck-basis-only-compile-f40737d8466b.json) |
| log | warm_start | unsupported | depth_exceeded | [v1-13-paper-tracks-log-literal-warm-9a40ffd91e38](runs/v1.13-paper-tracks/v1-13-paper-tracks-log-literal-warm-9a40ffd91e38.json) |
| logistic | warm_start | unsupported | depth_exceeded | [v1-13-paper-tracks-logistic-literal-warm-0f6989cbe549](runs/v1.13-paper-tracks/v1-13-paper-tracks-logistic-literal-warm-0f6989cbe549.json) |
| damped_oscillator | warm_start | unsupported | unsupported_operator | [v1-13-paper-tracks-damped-oscillator-literal-warm-de3e7e8afc6c](runs/v1.13-paper-tracks/v1-13-paper-tracks-damped-oscillator-literal-warm-de3e7e8afc6c.json) |
| planck | warm_start | unsupported | depth_exceeded | [v1-13-paper-tracks-planck-literal-warm-a31543749aa2](runs/v1.13-paper-tracks/v1-13-paper-tracks-planck-literal-warm-a31543749aa2.json) |

## Next Experiments

- Improve blind optimizer stability and compare against this campaign's `snapped_but_failed` cases.
- Reduce compiled arithmetic tree depth for formulas gated as unsupported, especially Michaelis-Menten and Planck-style expressions.
- Expand perturbation sweeps after optimizer changes so same-AST returns and verified-equivalent recoveries can be compared over time.
- Add external noisy datasets only after the synthetic/source-document campaign remains reproducible and interpretable.
