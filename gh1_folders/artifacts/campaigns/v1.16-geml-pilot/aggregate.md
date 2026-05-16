# Benchmark Evidence: v1.16-geml-pilot

v1.16 pilot raw EML versus i*pi EML campaign over natural-bias and negative-control targets; used to decide whether the full paper campaign is justified.

## Summary

| Metric | Value |
|--------|-------|
| total | 24 |
| verification_passed | 0 |
| trained_exact_recovery | 0 |
| compile_only_verified_support | 0 |
| same_ast_return | 0 |
| verified_equivalent_ast | 0 |
| repaired_candidate | 2 |
| unsupported | 0 |
| failed | 22 |
| execution_error | 0 |
| verification_passed_rate | 0.000 |
| trained_exact_recovery_rate | 0.000 |

## By Formula

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| cos_pi | 4 | 0 | 0 | 0 | 0 | 0 | 4 | 0.000 |
| exp | 4 | 0 | 0 | 0 | 0 | 0 | 2 | 0.000 |
| harmonic_sum | 4 | 0 | 0 | 0 | 0 | 0 | 4 | 0.000 |
| log | 4 | 0 | 0 | 0 | 0 | 0 | 4 | 0.000 |
| log_periodic_oscillation | 4 | 0 | 0 | 0 | 0 | 0 | 4 | 0.000 |
| sin_pi | 4 | 0 | 0 | 0 | 0 | 0 | 4 | 0.000 |

## By Start Mode

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| blind | 24 | 0 | 0 | 0 | 0 | 0 | 22 | 0.000 |

## Track Denominators

| Track | Total | Verification Passed | Trained Exact | Compile-only Support | Unsupported | Failed | Verification Rate | Constants Policy |
|-------|-------|---------------------|---------------|----------------------|-------------|--------|-------------------|------------------|
| literal_constants | 24 | 0 | 0 | 0 | 0 | 22 | 0.000 | literal_constants |

## By Benchmark Track

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| literal_constants | 24 | 0 | 0 | 0 | 0 | 0 | 22 | 0.000 |

## By Constants Policy

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| literal_constants | 24 | 0 | 0 | 0 | 0 | 0 | 22 | 0.000 |

## By Evidence Class

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| repaired_candidate | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0.000 |
| snapped_but_failed | 22 | 0 | 0 | 0 | 0 | 0 | 22 | 0.000 |

## By Warm-Start Evidence

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| not_warm_start | 24 | 0 | 0 | 0 | 0 | 0 | 22 | 0.000 |

## By AST Return Status

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| not_applicable | 24 | 0 | 0 | 0 | 0 | 0 | 22 | 0.000 |

## By Return Kind

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| none | 24 | 0 | 0 | 0 | 0 | 0 | 22 | 0.000 |

## By Raw Status

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| none | 24 | 0 | 0 | 0 | 0 | 0 | 22 | 0.000 |

## By Repair Status

| Group | Total | Verification Passed | Trained Exact | Compile-only Support | Same AST | Unsupported | Failed | Verification Rate |
|-------|-------|---------------------|---------------|----------------------|----------|-------------|--------|-------------------|
| not_repaired | 22 | 0 | 0 | 0 | 0 | 0 | 22 | 0.000 |
| repaired | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0.000 |

## Thresholds

No proof threshold metadata.

## Runs

| Run ID | Formula | Mode | Status | Classification | Artifact |
|--------|---------|------|--------|----------------|----------|
| v1-16-geml-pilot-sin-pi-raw-v116-blind-220d22c0209c | sin_pi | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.16-geml-pilot/runs/v1.16-geml-pilot/v1-16-geml-pilot-sin-pi-raw-v116-blind-220d22c0209c.json |
| v1-16-geml-pilot-sin-pi-raw-v116-blind-7aaf87676b6f | sin_pi | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.16-geml-pilot/runs/v1.16-geml-pilot/v1-16-geml-pilot-sin-pi-raw-v116-blind-7aaf87676b6f.json |
| v1-16-geml-pilot-sin-pi-ipi-v116-blind-2dbf88bedf2b | sin_pi | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.16-geml-pilot/runs/v1.16-geml-pilot/v1-16-geml-pilot-sin-pi-ipi-v116-blind-2dbf88bedf2b.json |
| v1-16-geml-pilot-sin-pi-ipi-v116-blind-c803be2bb022 | sin_pi | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.16-geml-pilot/runs/v1.16-geml-pilot/v1-16-geml-pilot-sin-pi-ipi-v116-blind-c803be2bb022.json |
| v1-16-geml-pilot-cos-pi-raw-v116-blind-c9906f0a620d | cos_pi | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.16-geml-pilot/runs/v1.16-geml-pilot/v1-16-geml-pilot-cos-pi-raw-v116-blind-c9906f0a620d.json |
| v1-16-geml-pilot-cos-pi-raw-v116-blind-434cf45abd91 | cos_pi | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.16-geml-pilot/runs/v1.16-geml-pilot/v1-16-geml-pilot-cos-pi-raw-v116-blind-434cf45abd91.json |
| v1-16-geml-pilot-cos-pi-ipi-v116-blind-d646ceb81086 | cos_pi | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.16-geml-pilot/runs/v1.16-geml-pilot/v1-16-geml-pilot-cos-pi-ipi-v116-blind-d646ceb81086.json |
| v1-16-geml-pilot-cos-pi-ipi-v116-blind-8400b3ba3d1b | cos_pi | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.16-geml-pilot/runs/v1.16-geml-pilot/v1-16-geml-pilot-cos-pi-ipi-v116-blind-8400b3ba3d1b.json |
| v1-16-geml-pilot-harmonic-sum-raw-v116-blind-894efc04fa0d | harmonic_sum | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.16-geml-pilot/runs/v1.16-geml-pilot/v1-16-geml-pilot-harmonic-sum-raw-v116-blind-894efc04fa0d.json |
| v1-16-geml-pilot-harmonic-sum-raw-v116-blind-a3087f36bc71 | harmonic_sum | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.16-geml-pilot/runs/v1.16-geml-pilot/v1-16-geml-pilot-harmonic-sum-raw-v116-blind-a3087f36bc71.json |
| v1-16-geml-pilot-harmonic-sum-ipi-v116-blind-6dce386f4e7b | harmonic_sum | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.16-geml-pilot/runs/v1.16-geml-pilot/v1-16-geml-pilot-harmonic-sum-ipi-v116-blind-6dce386f4e7b.json |
| v1-16-geml-pilot-harmonic-sum-ipi-v116-blind-cbcffbfb08d5 | harmonic_sum | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.16-geml-pilot/runs/v1.16-geml-pilot/v1-16-geml-pilot-harmonic-sum-ipi-v116-blind-cbcffbfb08d5.json |
| v1-16-geml-pilot-log-periodic-oscillation-raw-v116-blind-c15ac8ea4804 | log_periodic_oscillation | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.16-geml-pilot/runs/v1.16-geml-pilot/v1-16-geml-pilot-log-periodic-oscillation-raw-v116-blind-c15ac8ea4804.json |
| v1-16-geml-pilot-log-periodic-oscillation-raw-v116-blind-cb9b0243d688 | log_periodic_oscillation | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.16-geml-pilot/runs/v1.16-geml-pilot/v1-16-geml-pilot-log-periodic-oscillation-raw-v116-blind-cb9b0243d688.json |
| v1-16-geml-pilot-log-periodic-oscillation-ipi-v116-blind-b9dc27c7c5eb | log_periodic_oscillation | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.16-geml-pilot/runs/v1.16-geml-pilot/v1-16-geml-pilot-log-periodic-oscillation-ipi-v116-blind-b9dc27c7c5eb.json |
| v1-16-geml-pilot-log-periodic-oscillation-ipi-v116-blind-7e17daae2089 | log_periodic_oscillation | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.16-geml-pilot/runs/v1.16-geml-pilot/v1-16-geml-pilot-log-periodic-oscillation-ipi-v116-blind-7e17daae2089.json |
| v1-16-geml-pilot-exp-raw-v116-blind-9954b4b63c6d | exp | blind | repaired_candidate | repaired_candidate | artifacts/campaigns/v1.16-geml-pilot/runs/v1.16-geml-pilot/v1-16-geml-pilot-exp-raw-v116-blind-9954b4b63c6d.json |
| v1-16-geml-pilot-exp-raw-v116-blind-cf128515ef41 | exp | blind | repaired_candidate | repaired_candidate | artifacts/campaigns/v1.16-geml-pilot/runs/v1.16-geml-pilot/v1-16-geml-pilot-exp-raw-v116-blind-cf128515ef41.json |
| v1-16-geml-pilot-exp-ipi-v116-blind-96fd9b472e1c | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.16-geml-pilot/runs/v1.16-geml-pilot/v1-16-geml-pilot-exp-ipi-v116-blind-96fd9b472e1c.json |
| v1-16-geml-pilot-exp-ipi-v116-blind-f16264d68e9f | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.16-geml-pilot/runs/v1.16-geml-pilot/v1-16-geml-pilot-exp-ipi-v116-blind-f16264d68e9f.json |
| v1-16-geml-pilot-log-raw-v116-blind-5017393b5d99 | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.16-geml-pilot/runs/v1.16-geml-pilot/v1-16-geml-pilot-log-raw-v116-blind-5017393b5d99.json |
| v1-16-geml-pilot-log-raw-v116-blind-d348cd35ea0c | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.16-geml-pilot/runs/v1.16-geml-pilot/v1-16-geml-pilot-log-raw-v116-blind-d348cd35ea0c.json |
| v1-16-geml-pilot-log-ipi-v116-blind-84e0e981b471 | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.16-geml-pilot/runs/v1.16-geml-pilot/v1-16-geml-pilot-log-ipi-v116-blind-84e0e981b471.json |
| v1-16-geml-pilot-log-ipi-v116-blind-1cede807b734 | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.16-geml-pilot/runs/v1.16-geml-pilot/v1-16-geml-pilot-log-ipi-v116-blind-1cede807b734.json |
