# Benchmark Evidence: v1.5-shallow-pure-blind

Measured v1.5 pure random-initialized shallow blind suite with scaffold initializers disabled.

## Summary

| Metric | Value |
|--------|-------|
| total | 1 |
| verifier_recovered | 0 |
| same_ast_return | 0 |
| verified_equivalent_ast | 0 |
| repaired_candidate | 0 |
| unsupported | 0 |
| failed | 1 |
| execution_error | 0 |
| verifier_recovery_rate | 0.000 |

## By Formula

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| scaled_exp_growth | 1 | 0 | 0 | 0 | 1 | 0.000 |

## By Start Mode

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| blind | 1 | 0 | 0 | 0 | 1 | 0.000 |

## By Evidence Class

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| snapped_but_failed | 1 | 0 | 0 | 0 | 1 | 0.000 |

## By Return Kind

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 1 | 0 | 0 | 0 | 1 | 0.000 |

## By Raw Status

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 1 | 0 | 0 | 0 | 1 | 0.000 |

## By Repair Status

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| not_repaired | 1 | 0 | 0 | 0 | 1 | 0.000 |

## Thresholds

| Claim | Policy | Eligible | Passed | Failed | Rate | Required | Status |
|-------|--------|----------|--------|--------|------|----------|--------|
| paper-shallow-blind-recovery | measured_pure_blind_recovery | 1 | 0 | 1 | 0.000 |  | reported |

## Runs

| Run ID | Formula | Mode | Status | Classification | Artifact |
|--------|---------|------|--------|----------------|----------|
| v1-5-shallow-pure-blind-shallow-scaled-exp-growth-pure-blind-9f934ff0ec8a | scaled_exp_growth | blind | snapped_but_failed | snapped_but_failed | artifacts/benchmarks/verify-scaled-exp-growth-seed0/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-scaled-exp-growth-pure-blind-9f934ff0ec8a.json |
