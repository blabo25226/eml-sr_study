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
| v1-13-paper-tracks-exp-basis-only-compile-3063b13aa4e5 | exp | compile | recovered | verifier_recovered | artifacts/paper/v1.14/linked-artifacts/campaigns/v1.14-corrected-paper-tracks/runs/v1.13-paper-tracks/v1-13-paper-tracks-exp-basis-only-compile-3063b13aa4e5.json |
| v1-13-paper-tracks-log-basis-only-compile-b90f584d8bb1 | log | compile | unsupported | unsupported | artifacts/paper/v1.14/linked-artifacts/campaigns/v1.14-corrected-paper-tracks/runs/v1.13-paper-tracks/v1-13-paper-tracks-log-basis-only-compile-b90f584d8bb1.json |
| v1-13-paper-tracks-radioactive-decay-basis-only-compile-59cbbd644b4b | radioactive_decay | compile | unsupported | unsupported | artifacts/paper/v1.14/linked-artifacts/campaigns/v1.14-corrected-paper-tracks/runs/v1.13-paper-tracks/v1-13-paper-tracks-radioactive-decay-basis-only-compile-59cbbd644b4b.json |
| v1-13-paper-tracks-beer-lambert-basis-only-compile-7be75ecbaa63 | beer_lambert | compile | unsupported | unsupported | artifacts/paper/v1.14/linked-artifacts/campaigns/v1.14-corrected-paper-tracks/runs/v1.13-paper-tracks/v1-13-paper-tracks-beer-lambert-basis-only-compile-7be75ecbaa63.json |
| v1-13-paper-tracks-scaled-exp-growth-basis-only-compile-6de3215052b7 | scaled_exp_growth | compile | unsupported | unsupported | artifacts/paper/v1.14/linked-artifacts/campaigns/v1.14-corrected-paper-tracks/runs/v1.13-paper-tracks/v1-13-paper-tracks-scaled-exp-growth-basis-only-compile-6de3215052b7.json |
| v1-13-paper-tracks-scaled-exp-fast-decay-basis-only-compile-1b1c434047ab | scaled_exp_fast_decay | compile | unsupported | unsupported | artifacts/paper/v1.14/linked-artifacts/campaigns/v1.14-corrected-paper-tracks/runs/v1.13-paper-tracks/v1-13-paper-tracks-scaled-exp-fast-decay-basis-only-compile-1b1c434047ab.json |
| v1-13-paper-tracks-arrhenius-basis-only-compile-c088f39bd857 | arrhenius | compile | unsupported | unsupported | artifacts/paper/v1.14/linked-artifacts/campaigns/v1.14-corrected-paper-tracks/runs/v1.13-paper-tracks/v1-13-paper-tracks-arrhenius-basis-only-compile-c088f39bd857.json |
| v1-13-paper-tracks-michaelis-menten-basis-only-compile-c2a4f388bd95 | michaelis_menten | compile | unsupported | unsupported | artifacts/paper/v1.14/linked-artifacts/campaigns/v1.14-corrected-paper-tracks/runs/v1.13-paper-tracks/v1-13-paper-tracks-michaelis-menten-basis-only-compile-c2a4f388bd95.json |
| v1-13-paper-tracks-logistic-basis-only-compile-a32e36271e81 | logistic | compile | unsupported | unsupported | artifacts/paper/v1.14/linked-artifacts/campaigns/v1.14-corrected-paper-tracks/runs/v1.13-paper-tracks/v1-13-paper-tracks-logistic-basis-only-compile-a32e36271e81.json |
| v1-13-paper-tracks-shockley-basis-only-compile-28e169b25e29 | shockley | compile | unsupported | unsupported | artifacts/paper/v1.14/linked-artifacts/campaigns/v1.14-corrected-paper-tracks/runs/v1.13-paper-tracks/v1-13-paper-tracks-shockley-basis-only-compile-28e169b25e29.json |
| v1-13-paper-tracks-damped-oscillator-basis-only-compile-19df93053992 | damped_oscillator | compile | unsupported | unsupported | artifacts/paper/v1.14/linked-artifacts/campaigns/v1.14-corrected-paper-tracks/runs/v1.13-paper-tracks/v1-13-paper-tracks-damped-oscillator-basis-only-compile-19df93053992.json |
| v1-13-paper-tracks-planck-basis-only-compile-561b8c556ba4 | planck | compile | unsupported | unsupported | artifacts/paper/v1.14/linked-artifacts/campaigns/v1.14-corrected-paper-tracks/runs/v1.13-paper-tracks/v1-13-paper-tracks-planck-basis-only-compile-561b8c556ba4.json |
| v1-13-paper-tracks-exp-literal-warm-9b23eed6fa6a | exp | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/paper/v1.14/linked-artifacts/campaigns/v1.14-corrected-paper-tracks/runs/v1.13-paper-tracks/v1-13-paper-tracks-exp-literal-warm-9b23eed6fa6a.json |
| v1-13-paper-tracks-log-literal-warm-682593206b87 | log | warm_start | unsupported | unsupported | artifacts/paper/v1.14/linked-artifacts/campaigns/v1.14-corrected-paper-tracks/runs/v1.13-paper-tracks/v1-13-paper-tracks-log-literal-warm-682593206b87.json |
| v1-13-paper-tracks-radioactive-decay-literal-warm-2c95fb8d28a3 | radioactive_decay | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/paper/v1.14/linked-artifacts/campaigns/v1.14-corrected-paper-tracks/runs/v1.13-paper-tracks/v1-13-paper-tracks-radioactive-decay-literal-warm-2c95fb8d28a3.json |
| v1-13-paper-tracks-beer-lambert-literal-warm-6bde0341b85f | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/paper/v1.14/linked-artifacts/campaigns/v1.14-corrected-paper-tracks/runs/v1.13-paper-tracks/v1-13-paper-tracks-beer-lambert-literal-warm-6bde0341b85f.json |
| v1-13-paper-tracks-scaled-exp-growth-literal-warm-de37e614d838 | scaled_exp_growth | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/paper/v1.14/linked-artifacts/campaigns/v1.14-corrected-paper-tracks/runs/v1.13-paper-tracks/v1-13-paper-tracks-scaled-exp-growth-literal-warm-de37e614d838.json |
| v1-13-paper-tracks-scaled-exp-fast-decay-literal-warm-2ec985eec55a | scaled_exp_fast_decay | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/paper/v1.14/linked-artifacts/campaigns/v1.14-corrected-paper-tracks/runs/v1.13-paper-tracks/v1-13-paper-tracks-scaled-exp-fast-decay-literal-warm-2ec985eec55a.json |
| v1-13-paper-tracks-arrhenius-literal-warm-b1aea4d7678e | arrhenius | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/paper/v1.14/linked-artifacts/campaigns/v1.14-corrected-paper-tracks/runs/v1.13-paper-tracks/v1-13-paper-tracks-arrhenius-literal-warm-b1aea4d7678e.json |
| v1-13-paper-tracks-michaelis-menten-literal-warm-a45fcb5297df | michaelis_menten | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/paper/v1.14/linked-artifacts/campaigns/v1.14-corrected-paper-tracks/runs/v1.13-paper-tracks/v1-13-paper-tracks-michaelis-menten-literal-warm-a45fcb5297df.json |
| v1-13-paper-tracks-logistic-literal-warm-9ea281dbf3ec | logistic | warm_start | unsupported | unsupported | artifacts/paper/v1.14/linked-artifacts/campaigns/v1.14-corrected-paper-tracks/runs/v1.13-paper-tracks/v1-13-paper-tracks-logistic-literal-warm-9ea281dbf3ec.json |
| v1-13-paper-tracks-shockley-literal-warm-99701f065be5 | shockley | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/paper/v1.14/linked-artifacts/campaigns/v1.14-corrected-paper-tracks/runs/v1.13-paper-tracks/v1-13-paper-tracks-shockley-literal-warm-99701f065be5.json |
| v1-13-paper-tracks-damped-oscillator-literal-warm-4ac09e7e05b3 | damped_oscillator | warm_start | unsupported | unsupported | artifacts/paper/v1.14/linked-artifacts/campaigns/v1.14-corrected-paper-tracks/runs/v1.13-paper-tracks/v1-13-paper-tracks-damped-oscillator-literal-warm-4ac09e7e05b3.json |
| v1-13-paper-tracks-planck-literal-warm-00693e8cb013 | planck | warm_start | unsupported | unsupported | artifacts/paper/v1.14/linked-artifacts/campaigns/v1.14-corrected-paper-tracks/runs/v1.13-paper-tracks/v1-13-paper-tracks-planck-literal-warm-00693e8cb013.json |
