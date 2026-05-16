# Benchmark Evidence: v1.15-geml-oscillatory-smoke

Cheap v1.15 raw EML versus i*pi EML smoke subset over one natural oscillatory target and one negative control with matched blind-training budgets.

## Summary

| Metric | Value |
|--------|-------|
| total | 4 |
| verification_passed | 0 |
| trained_exact_recovery | 0 |
| compile_only_verified_support | 0 |
| same_ast_return | 0 |
| verified_equivalent_ast | 0 |
| repaired_candidate | 2 |
| unsupported | 0 |
| failed | 2 |
| execution_error | 0 |
| verification_passed_rate | 0.000 |
| trained_exact_recovery_rate | 0.000 |

## By Formula

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| exp | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0.000 |
| sin_pi | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0.000 |

## By Start Mode

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| blind | 4 | 0 | 0 | 0 | 0 | 0 | 2 | 0.000 |

## Track Denominators

| Track | Total | Verification Passed | Trained Exact | Compile-only Support | Unsupported | Failed | Verification Rate | Constants Policy |
|-------|-------|---------------------|---------------|----------------------|-------------|--------|-------------------|------------------|
| literal_constants | 4 | 0 | 0 | 0 | 0 | 2 | 0.000 | literal_constants |

## By Benchmark Track

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| literal_constants | 4 | 0 | 0 | 0 | 0 | 0 | 2 | 0.000 |

## By Constants Policy

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| literal_constants | 4 | 0 | 0 | 0 | 0 | 0 | 2 | 0.000 |

## By Evidence Class

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| repaired_candidate | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0.000 |
| snapped_but_failed | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0.000 |

## By Warm-Start Evidence

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| not_warm_start | 4 | 0 | 0 | 0 | 0 | 0 | 2 | 0.000 |

## By AST Return Status

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| not_applicable | 4 | 0 | 0 | 0 | 0 | 0 | 2 | 0.000 |

## By Return Kind

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| none | 4 | 0 | 0 | 0 | 0 | 0 | 2 | 0.000 |

## By Raw Status

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| none | 4 | 0 | 0 | 0 | 0 | 0 | 2 | 0.000 |

## By Repair Status

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| not_repaired | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0.000 |
| repaired | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0.000 |

## Thresholds

No proof threshold metadata.

## Runs

| Run ID | Formula | Mode | Status | Classification | Artifact |
|--------|---------|------|--------|----------------|----------|
| v1-15-geml-oscillatory-smoke-sin-pi-raw-blind-70170745a2b0 | sin_pi | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.15-geml-oscillatory-smoke/runs/v1.15-geml-oscillatory-smoke/v1-15-geml-oscillatory-smoke-sin-pi-raw-blind-70170745a2b0.json |
| v1-15-geml-oscillatory-smoke-sin-pi-ipi-blind-ea7864a411cc | sin_pi | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.15-geml-oscillatory-smoke/runs/v1.15-geml-oscillatory-smoke/v1-15-geml-oscillatory-smoke-sin-pi-ipi-blind-ea7864a411cc.json |
| v1-15-geml-oscillatory-smoke-exp-raw-blind-5acc64d4b218 | exp | blind | repaired_candidate | repaired_candidate | artifacts/campaigns/v1.15-geml-oscillatory-smoke/runs/v1.15-geml-oscillatory-smoke/v1-15-geml-oscillatory-smoke-exp-raw-blind-5acc64d4b218.json |
| v1-15-geml-oscillatory-smoke-exp-ipi-blind-a38affbc171c | exp | blind | repaired_candidate | repaired_candidate | artifacts/campaigns/v1.15-geml-oscillatory-smoke/runs/v1.15-geml-oscillatory-smoke/v1-15-geml-oscillatory-smoke-exp-ipi-blind-a38affbc171c.json |
