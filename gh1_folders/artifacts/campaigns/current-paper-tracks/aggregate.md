# Benchmark Evidence: v1.13-paper-tracks

Combined v1.13 publication target suite with basis-only and literal-constant tracks kept as separate aggregate denominators.

## Summary

| Metric | Value |
|--------|-------|
| total | 24 |
| verification_passed | 9 |
| trained_exact_recovery | 8 |
| compile_only_verified_support | 1 |
| same_ast_return | 8 |
| verified_equivalent_ast | 0 |
| repaired_candidate | 0 |
| unsupported | 15 |
| failed | 0 |
| execution_error | 0 |
| verification_passed_rate | 0.375 |
| trained_exact_recovery_rate | 0.333 |

## By Formula

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| arrhenius | 2 | 1 | 1 | 0 | 1 | 1 | 0 | 0.500 |
| beer_lambert | 2 | 1 | 1 | 0 | 1 | 1 | 0 | 0.500 |
| damped_oscillator | 2 | 0 | 0 | 0 | 0 | 2 | 0 | 0.000 |
| exp | 2 | 2 | 1 | 1 | 1 | 0 | 0 | 1.000 |
| log | 2 | 0 | 0 | 0 | 0 | 2 | 0 | 0.000 |
| logistic | 2 | 0 | 0 | 0 | 0 | 2 | 0 | 0.000 |
| michaelis_menten | 2 | 1 | 1 | 0 | 1 | 1 | 0 | 0.500 |
| planck | 2 | 0 | 0 | 0 | 0 | 2 | 0 | 0.000 |
| radioactive_decay | 2 | 1 | 1 | 0 | 1 | 1 | 0 | 0.500 |
| scaled_exp_fast_decay | 2 | 1 | 1 | 0 | 1 | 1 | 0 | 0.500 |
| scaled_exp_growth | 2 | 1 | 1 | 0 | 1 | 1 | 0 | 0.500 |
| shockley | 2 | 1 | 1 | 0 | 1 | 1 | 0 | 0.500 |

## By Start Mode

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| compile | 12 | 1 | 0 | 1 | 0 | 11 | 0 | 0.083 |
| warm_start | 12 | 8 | 8 | 0 | 8 | 4 | 0 | 0.667 |

## Track Denominators

| Track | Total | Verification Passed | Trained Exact | Compile-only Support | Unsupported | Failed | Verification Rate | Constants Policy |
|-------|-------|---------------------|---------------|----------------------|-------------|--------|-------------------|------------------|
| basis_only | 12 | 1 | 0 | 1 | 11 | 0 | 0.083 | basis_only |
| literal_constants | 12 | 8 | 8 | 0 | 4 | 0 | 0.667 | literal_constants |

## By Benchmark Track

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| basis_only | 12 | 1 | 0 | 1 | 0 | 11 | 0 | 0.083 |
| literal_constants | 12 | 8 | 8 | 0 | 8 | 4 | 0 | 0.667 |

## By Constants Policy

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| basis_only | 12 | 1 | 0 | 1 | 0 | 11 | 0 | 0.083 |
| literal_constants | 12 | 8 | 8 | 0 | 8 | 4 | 0 | 0.667 |

## By Evidence Class

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| compile_only_verified | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 1.000 |
| same_ast | 8 | 8 | 8 | 0 | 8 | 0 | 0 | 1.000 |
| unsupported | 15 | 0 | 0 | 0 | 0 | 15 | 0 | 0.000 |

## By Warm-Start Evidence

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| exact_seed_round_trip | 8 | 8 | 8 | 0 | 8 | 0 | 0 | 1.000 |
| not_warm_start | 12 | 1 | 0 | 1 | 0 | 11 | 0 | 0.083 |
| unsupported | 4 | 0 | 0 | 0 | 0 | 4 | 0 | 0.000 |

## By AST Return Status

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| not_applicable | 12 | 1 | 0 | 1 | 0 | 11 | 0 | 0.083 |
| same_ast | 8 | 8 | 8 | 0 | 8 | 0 | 0 | 1.000 |
| unsupported | 4 | 0 | 0 | 0 | 0 | 4 | 0 | 0.000 |

## By Return Kind

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| none | 24 | 9 | 8 | 1 | 8 | 15 | 0 | 0.375 |

## By Raw Status

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| none | 24 | 9 | 8 | 1 | 8 | 15 | 0 | 0.375 |

## By Repair Status

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| none | 16 | 1 | 0 | 1 | 0 | 15 | 0 | 0.062 |
| not_attempted | 8 | 8 | 8 | 0 | 8 | 0 | 0 | 1.000 |

## Thresholds

No proof threshold metadata.

## Runs

| Run ID | Formula | Mode | Status | Classification | Artifact |
|--------|---------|------|--------|----------------|----------|
| v1-13-paper-tracks-exp-basis-only-compile-af02888f5ef5 | exp | compile | recovered | verifier_recovered | artifacts\campaigns\current-paper-tracks\runs\v1.13-paper-tracks\v1-13-paper-tracks-exp-basis-only-compile-af02888f5ef5.json |
| v1-13-paper-tracks-log-basis-only-compile-32f1f1ecb80c | log | compile | unsupported | unsupported | artifacts\campaigns\current-paper-tracks\runs\v1.13-paper-tracks\v1-13-paper-tracks-log-basis-only-compile-32f1f1ecb80c.json |
| v1-13-paper-tracks-radioactive-decay-basis-only-compile-ebe90922f383 | radioactive_decay | compile | unsupported | unsupported | artifacts\campaigns\current-paper-tracks\runs\v1.13-paper-tracks\v1-13-paper-tracks-radioactive-decay-basis-only-compile-ebe90922f383.json |
| v1-13-paper-tracks-beer-lambert-basis-only-compile-69e15fc06bef | beer_lambert | compile | unsupported | unsupported | artifacts\campaigns\current-paper-tracks\runs\v1.13-paper-tracks\v1-13-paper-tracks-beer-lambert-basis-only-compile-69e15fc06bef.json |
| v1-13-paper-tracks-scaled-exp-growth-basis-only-compile-6036bc33a562 | scaled_exp_growth | compile | unsupported | unsupported | artifacts\campaigns\current-paper-tracks\runs\v1.13-paper-tracks\v1-13-paper-tracks-scaled-exp-growth-basis-only-compile-6036bc33a562.json |
| v1-13-paper-tracks-scaled-exp-fast-decay-basis-only-compile-1f7a12b07d05 | scaled_exp_fast_decay | compile | unsupported | unsupported | artifacts\campaigns\current-paper-tracks\runs\v1.13-paper-tracks\v1-13-paper-tracks-scaled-exp-fast-decay-basis-only-compile-1f7a12b07d05.json |
| v1-13-paper-tracks-arrhenius-basis-only-compile-fc0729d1e8c7 | arrhenius | compile | unsupported | unsupported | artifacts\campaigns\current-paper-tracks\runs\v1.13-paper-tracks\v1-13-paper-tracks-arrhenius-basis-only-compile-fc0729d1e8c7.json |
| v1-13-paper-tracks-michaelis-menten-basis-only-compile-2309755498fa | michaelis_menten | compile | unsupported | unsupported | artifacts\campaigns\current-paper-tracks\runs\v1.13-paper-tracks\v1-13-paper-tracks-michaelis-menten-basis-only-compile-2309755498fa.json |
| v1-13-paper-tracks-logistic-basis-only-compile-ef8ffeed064f | logistic | compile | unsupported | unsupported | artifacts\campaigns\current-paper-tracks\runs\v1.13-paper-tracks\v1-13-paper-tracks-logistic-basis-only-compile-ef8ffeed064f.json |
| v1-13-paper-tracks-shockley-basis-only-compile-dc9d2db8a8d6 | shockley | compile | unsupported | unsupported | artifacts\campaigns\current-paper-tracks\runs\v1.13-paper-tracks\v1-13-paper-tracks-shockley-basis-only-compile-dc9d2db8a8d6.json |
| v1-13-paper-tracks-damped-oscillator-basis-only-compile-9f887e42dbf9 | damped_oscillator | compile | unsupported | unsupported | artifacts\campaigns\current-paper-tracks\runs\v1.13-paper-tracks\v1-13-paper-tracks-damped-oscillator-basis-only-compile-9f887e42dbf9.json |
| v1-13-paper-tracks-planck-basis-only-compile-f40737d8466b | planck | compile | unsupported | unsupported | artifacts\campaigns\current-paper-tracks\runs\v1.13-paper-tracks\v1-13-paper-tracks-planck-basis-only-compile-f40737d8466b.json |
| v1-13-paper-tracks-exp-literal-warm-f53942aad6c4 | exp | warm_start | same_ast_return | same_ast_warm_start_return | artifacts\campaigns\current-paper-tracks\runs\v1.13-paper-tracks\v1-13-paper-tracks-exp-literal-warm-f53942aad6c4.json |
| v1-13-paper-tracks-log-literal-warm-9a40ffd91e38 | log | warm_start | unsupported | unsupported | artifacts\campaigns\current-paper-tracks\runs\v1.13-paper-tracks\v1-13-paper-tracks-log-literal-warm-9a40ffd91e38.json |
| v1-13-paper-tracks-radioactive-decay-literal-warm-f404a736ffb9 | radioactive_decay | warm_start | same_ast_return | same_ast_warm_start_return | artifacts\campaigns\current-paper-tracks\runs\v1.13-paper-tracks\v1-13-paper-tracks-radioactive-decay-literal-warm-f404a736ffb9.json |
| v1-13-paper-tracks-beer-lambert-literal-warm-adfce05dbfa9 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts\campaigns\current-paper-tracks\runs\v1.13-paper-tracks\v1-13-paper-tracks-beer-lambert-literal-warm-adfce05dbfa9.json |
| v1-13-paper-tracks-scaled-exp-growth-literal-warm-cf7b378f615e | scaled_exp_growth | warm_start | same_ast_return | same_ast_warm_start_return | artifacts\campaigns\current-paper-tracks\runs\v1.13-paper-tracks\v1-13-paper-tracks-scaled-exp-growth-literal-warm-cf7b378f615e.json |
| v1-13-paper-tracks-scaled-exp-fast-decay-literal-warm-308039976a83 | scaled_exp_fast_decay | warm_start | same_ast_return | same_ast_warm_start_return | artifacts\campaigns\current-paper-tracks\runs\v1.13-paper-tracks\v1-13-paper-tracks-scaled-exp-fast-decay-literal-warm-308039976a83.json |
| v1-13-paper-tracks-arrhenius-literal-warm-6ea396db7d91 | arrhenius | warm_start | same_ast_return | same_ast_warm_start_return | artifacts\campaigns\current-paper-tracks\runs\v1.13-paper-tracks\v1-13-paper-tracks-arrhenius-literal-warm-6ea396db7d91.json |
| v1-13-paper-tracks-michaelis-menten-literal-warm-cfacd8bc2b60 | michaelis_menten | warm_start | same_ast_return | same_ast_warm_start_return | artifacts\campaigns\current-paper-tracks\runs\v1.13-paper-tracks\v1-13-paper-tracks-michaelis-menten-literal-warm-cfacd8bc2b60.json |
| v1-13-paper-tracks-logistic-literal-warm-0f6989cbe549 | logistic | warm_start | unsupported | unsupported | artifacts\campaigns\current-paper-tracks\runs\v1.13-paper-tracks\v1-13-paper-tracks-logistic-literal-warm-0f6989cbe549.json |
| v1-13-paper-tracks-shockley-literal-warm-9be8e689169b | shockley | warm_start | same_ast_return | same_ast_warm_start_return | artifacts\campaigns\current-paper-tracks\runs\v1.13-paper-tracks\v1-13-paper-tracks-shockley-literal-warm-9be8e689169b.json |
| v1-13-paper-tracks-damped-oscillator-literal-warm-de3e7e8afc6c | damped_oscillator | warm_start | unsupported | unsupported | artifacts\campaigns\current-paper-tracks\runs\v1.13-paper-tracks\v1-13-paper-tracks-damped-oscillator-literal-warm-de3e7e8afc6c.json |
| v1-13-paper-tracks-planck-literal-warm-a31543749aa2 | planck | warm_start | unsupported | unsupported | artifacts\campaigns\current-paper-tracks\runs\v1.13-paper-tracks\v1-13-paper-tracks-planck-literal-warm-a31543749aa2.json |
