# Benchmark Evidence: smoke

Fast CI-scale benchmark contract smoke suite.

## Summary

| Metric | Value |
|--------|-------|
| total | 3 |
| verification_passed | 2 |
| trained_exact_recovery | 2 |
| compile_only_verified_support | 0 |
| same_ast_return | 1 |
| verified_equivalent_ast | 0 |
| repaired_candidate | 0 |
| unsupported | 1 |
| failed | 0 |
| execution_error | 0 |
| verification_passed_rate | 0.667 |
| trained_exact_recovery_rate | 0.667 |

## By Formula

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| beer_lambert | 1 | 1 | 1 | 0 | 1 | 0 | 0 | 1.000 |
| exp | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 1.000 |
| planck | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0.000 |

## By Start Mode

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| blind | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 1.000 |
| compile | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0.000 |
| warm_start | 1 | 1 | 1 | 0 | 1 | 0 | 0 | 1.000 |

## Track Denominators

| Track | Total | Verification Passed | Trained Exact | Compile-only Support | Unsupported | Failed | Verification Rate | Constants Policy |
|-------|-------|---------------------|---------------|----------------------|-------------|--------|-------------------|------------------|
| literal_constants | 3 | 2 | 2 | 0 | 1 | 0 | 0.667 | literal_constants |

## By Benchmark Track

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| literal_constants | 3 | 2 | 2 | 0 | 1 | 1 | 0 | 0.667 |

## By Constants Policy

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| literal_constants | 3 | 2 | 2 | 0 | 1 | 1 | 0 | 0.667 |

## By Evidence Class

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| same_ast | 1 | 1 | 1 | 0 | 1 | 0 | 0 | 1.000 |
| scaffolded_blind_training_recovered | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 1.000 |
| unsupported | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0.000 |

## By Warm-Start Evidence

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| exact_seed_round_trip | 1 | 1 | 1 | 0 | 1 | 0 | 0 | 1.000 |
| not_warm_start | 2 | 1 | 1 | 0 | 0 | 1 | 0 | 0.500 |

## By AST Return Status

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| not_applicable | 2 | 1 | 1 | 0 | 0 | 1 | 0 | 0.500 |
| same_ast | 1 | 1 | 1 | 0 | 1 | 0 | 0 | 1.000 |

## By Return Kind

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| none | 3 | 2 | 2 | 0 | 1 | 1 | 0 | 0.667 |

## By Raw Status

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| none | 3 | 2 | 2 | 0 | 1 | 1 | 0 | 0.667 |

## By Repair Status

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| none | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0.000 |
| not_attempted | 2 | 2 | 2 | 0 | 1 | 0 | 0 | 1.000 |

## Thresholds

No proof threshold metadata.

## Runs

| Run ID | Formula | Mode | Status | Classification | Artifact |
|--------|---------|------|--------|----------------|----------|
| smoke-exp-blind-9d572c5e571b | exp | blind | recovered | scaffolded_blind_recovery | artifacts\benchmarks\smoke\smoke-exp-blind-9d572c5e571b.json |
| smoke-beer-warm-645f8b8afb0d | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts\benchmarks\smoke\smoke-beer-warm-645f8b8afb0d.json |
| smoke-planck-diagnostic-e8ce476b5ad9 | planck | compile | unsupported | unsupported | artifacts\benchmarks\smoke\smoke-planck-diagnostic-e8ce476b5ad9.json |
