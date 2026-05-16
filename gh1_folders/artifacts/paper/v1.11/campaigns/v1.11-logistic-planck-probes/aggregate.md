# Benchmark Evidence: v1.11-logistic-planck-probes

v1.11 focused logistic and Planck compile diagnostics plus low-budget real blind probes. Rows remain unsupported/stretch diagnostics unless the unchanged verifier contract passes.

## Summary

| Metric | Value |
|--------|-------|
| total | 4 |
| verifier_recovered | 0 |
| same_ast_return | 0 |
| verified_equivalent_ast | 0 |
| repaired_candidate | 0 |
| unsupported | 2 |
| failed | 2 |
| execution_error | 0 |
| verifier_recovery_rate | 0.000 |

## By Formula

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| logistic | 2 | 0 | 0 | 1 | 1 | 0.000 |
| planck | 2 | 0 | 0 | 1 | 1 | 0.000 |

## By Start Mode

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| blind | 2 | 0 | 0 | 0 | 2 | 0.000 |
| compile | 2 | 0 | 0 | 2 | 0 | 0.000 |

## By Evidence Class

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| failed | 1 | 0 | 0 | 0 | 1 | 0.000 |
| snapped_but_failed | 1 | 0 | 0 | 0 | 1 | 0.000 |
| unsupported | 2 | 0 | 0 | 2 | 0 | 0.000 |

## By Return Kind

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 4 | 0 | 0 | 2 | 2 | 0.000 |

## By Raw Status

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 4 | 0 | 0 | 2 | 2 | 0.000 |

## By Repair Status

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 2 | 0 | 0 | 2 | 0 | 0.000 |
| not_repaired | 2 | 0 | 0 | 0 | 2 | 0.000 |

## Thresholds

No proof threshold metadata.

## Runs

| Run ID | Formula | Mode | Status | Classification | Artifact |
|--------|---------|------|--------|----------------|----------|
| v1-11-logistic-planck-probes-logistic-compile-d9b410fc6d87 | logistic | compile | unsupported | unsupported | artifacts/campaigns/v1.11-logistic-planck-probes/runs/v1.11-logistic-planck-probes/v1-11-logistic-planck-probes-logistic-compile-d9b410fc6d87.json |
| v1-11-logistic-planck-probes-planck-compile-9565da4ea47b | planck | compile | unsupported | unsupported | artifacts/campaigns/v1.11-logistic-planck-probes/runs/v1.11-logistic-planck-probes/v1-11-logistic-planck-probes-planck-compile-9565da4ea47b.json |
| v1-11-logistic-planck-probes-logistic-blind-probe-b35045193c4c | logistic | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.11-logistic-planck-probes/runs/v1.11-logistic-planck-probes/v1-11-logistic-planck-probes-logistic-blind-probe-b35045193c4c.json |
| v1-11-logistic-planck-probes-planck-blind-probe-be823c997bf6 | planck | blind | failed | failed | artifacts/campaigns/v1.11-logistic-planck-probes/runs/v1.11-logistic-planck-probes/v1-11-logistic-planck-probes-planck-blind-probe-be823c997bf6.json |
