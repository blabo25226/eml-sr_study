# Benchmark Evidence: smoke

Fast CI-scale benchmark contract smoke suite.

## Summary

| Metric | Value |
|--------|-------|
| total | 3 |
| verifier_recovered | 1 |
| same_ast_return | 1 |
| verified_equivalent_ast | 0 |
| unsupported | 1 |
| failed | 1 |
| execution_error | 0 |
| verifier_recovery_rate | 0.333 |

## By Formula

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| beer_lambert | 1 | 1 | 1 | 0 | 0 | 1.000 |
| exp | 1 | 0 | 0 | 0 | 1 | 0.000 |
| planck | 1 | 0 | 0 | 1 | 0 | 0.000 |

## By Start Mode

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| blind | 1 | 0 | 0 | 0 | 1 | 0.000 |
| compile | 1 | 0 | 0 | 1 | 0 | 0.000 |
| warm_start | 1 | 1 | 1 | 0 | 0 | 1.000 |

## Runs

| Run ID | Formula | Mode | Status | Classification | Artifact |
|--------|---------|------|--------|----------------|----------|
| smoke-exp-blind-44cae09389c3 | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/benchmarks/smoke/smoke-exp-blind-44cae09389c3.json |
| smoke-beer-warm-35bbd89a434a | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/benchmarks/smoke/smoke-beer-warm-35bbd89a434a.json |
| smoke-planck-diagnostic-aaf175aaa0f7 | planck | compile | unsupported | unsupported | artifacts/benchmarks/smoke/smoke-planck-diagnostic-aaf175aaa0f7.json |
