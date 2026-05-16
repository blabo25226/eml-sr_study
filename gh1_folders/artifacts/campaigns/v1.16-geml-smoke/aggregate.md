# Benchmark Evidence: v1.16-geml-smoke

Cheap v1.16 raw EML versus i*pi EML smoke check with generic i*pi primitive initializers and matched negative-control visibility.

## Summary

| Metric | Value |
|--------|-------|
| total | 4 |
| verification_passed | 0 |
| trained_exact_recovery | 0 |
| compile_only_verified_support | 0 |
| same_ast_return | 0 |
| verified_equivalent_ast | 0 |
| repaired_candidate | 1 |
| unsupported | 0 |
| failed | 3 |
| execution_error | 0 |
| verification_passed_rate | 0.000 |
| trained_exact_recovery_rate | 0.000 |

## By Formula

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| exp | 2 | 0 | 0 | 0 | 0 | 0 | 1 | 0.000 |
| sin_pi | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0.000 |

## By Start Mode

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| blind | 4 | 0 | 0 | 0 | 0 | 0 | 3 | 0.000 |

## Track Denominators

| Track | Total | Verification Passed | Trained Exact | Compile-only Support | Unsupported | Failed | Verification Rate | Constants Policy |
|-------|-------|---------------------|---------------|----------------------|-------------|--------|-------------------|------------------|
| literal_constants | 4 | 0 | 0 | 0 | 0 | 3 | 0.000 | literal_constants |

## By Benchmark Track

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| literal_constants | 4 | 0 | 0 | 0 | 0 | 0 | 3 | 0.000 |

## By Constants Policy

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| literal_constants | 4 | 0 | 0 | 0 | 0 | 0 | 3 | 0.000 |

## By Evidence Class

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| repaired_candidate | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0.000 |
| snapped_but_failed | 3 | 0 | 0 | 0 | 0 | 0 | 3 | 0.000 |

## By Warm-Start Evidence

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| not_warm_start | 4 | 0 | 0 | 0 | 0 | 0 | 3 | 0.000 |

## By AST Return Status

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| not_applicable | 4 | 0 | 0 | 0 | 0 | 0 | 3 | 0.000 |

## By Return Kind

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| none | 4 | 0 | 0 | 0 | 0 | 0 | 3 | 0.000 |

## By Raw Status

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| none | 4 | 0 | 0 | 0 | 0 | 0 | 3 | 0.000 |

## By Repair Status

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| not_repaired | 3 | 0 | 0 | 0 | 0 | 0 | 3 | 0.000 |
| repaired | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0.000 |

## Thresholds

No proof threshold metadata.

## Runs

| Run ID | Formula | Mode | Status | Classification | Artifact |
|--------|---------|------|--------|----------------|----------|
| v1-16-geml-smoke-sin-pi-raw-v116-blind-7e3efe6e564e | sin_pi | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.16-geml-smoke/runs/v1.16-geml-smoke/v1-16-geml-smoke-sin-pi-raw-v116-blind-7e3efe6e564e.json |
| v1-16-geml-smoke-sin-pi-ipi-v116-blind-e7efd47e48bd | sin_pi | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.16-geml-smoke/runs/v1.16-geml-smoke/v1-16-geml-smoke-sin-pi-ipi-v116-blind-e7efd47e48bd.json |
| v1-16-geml-smoke-exp-raw-v116-blind-739ffa409112 | exp | blind | repaired_candidate | repaired_candidate | artifacts/campaigns/v1.16-geml-smoke/runs/v1.16-geml-smoke/v1-16-geml-smoke-exp-raw-v116-blind-739ffa409112.json |
| v1-16-geml-smoke-exp-ipi-v116-blind-e8fe36239cff | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.16-geml-smoke/runs/v1.16-geml-smoke/v1-16-geml-smoke-exp-ipi-v116-blind-e8fe36239cff.json |
