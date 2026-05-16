# Benchmark Evidence: v1.8-family-calibration

Focused v1.8 family calibration probes for shallow exp/log behavior across fixed scales and schedules.

## Summary

| Metric | Value |
|--------|-------|
| total | 22 |
| verifier_recovered | 2 |
| same_ast_return | 0 |
| verified_equivalent_ast | 0 |
| repaired_candidate | 0 |
| unsupported | 0 |
| failed | 20 |
| execution_error | 0 |
| verifier_recovery_rate | 0.091 |

## By Formula

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| exp | 11 | 1 | 0 | 0 | 10 | 0.091 |
| log | 11 | 1 | 0 | 0 | 10 | 0.091 |

## By Start Mode

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| blind | 22 | 2 | 0 | 0 | 20 | 0.091 |

## By Evidence Class

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| scaffolded_blind_training_recovered | 2 | 2 | 0 | 0 | 0 | 1.000 |
| snapped_but_failed | 20 | 0 | 0 | 0 | 20 | 0.000 |

## By Return Kind

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 22 | 2 | 0 | 0 | 20 | 0.091 |

## By Raw Status

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 22 | 2 | 0 | 0 | 20 | 0.091 |

## By Repair Status

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| not_attempted | 2 | 2 | 0 | 0 | 0 | 1.000 |
| not_repaired | 20 | 0 | 0 | 0 | 20 | 0.000 |

## Thresholds

No proof threshold metadata.

## Runs

| Run ID | Formula | Mode | Status | Classification | Artifact |
|--------|---------|------|--------|----------------|----------|
| v1-8-family-calibration-cal-exp-blind-raw-e9105374ad46 | exp | blind | recovered | scaffolded_blind_recovery | artifacts/campaigns/v1.8-family-calibration/runs/v1.8-family-calibration/v1-8-family-calibration-cal-exp-blind-raw-e9105374ad46.json |
| v1-8-family-calibration-cal-exp-blind-ceml1-da80ed604deb | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-calibration/runs/v1.8-family-calibration/v1-8-family-calibration-cal-exp-blind-ceml1-da80ed604deb.json |
| v1-8-family-calibration-cal-exp-blind-zeml1-36850fb8c754 | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-calibration/runs/v1.8-family-calibration/v1-8-family-calibration-cal-exp-blind-zeml1-36850fb8c754.json |
| v1-8-family-calibration-cal-exp-blind-ceml2-28bdf8eae7cb | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-calibration/runs/v1.8-family-calibration/v1-8-family-calibration-cal-exp-blind-ceml2-28bdf8eae7cb.json |
| v1-8-family-calibration-cal-exp-blind-zeml2-3c5545485466 | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-calibration/runs/v1.8-family-calibration/v1-8-family-calibration-cal-exp-blind-zeml2-3c5545485466.json |
| v1-8-family-calibration-cal-exp-blind-ceml4-7a34d37e5806 | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-calibration/runs/v1.8-family-calibration/v1-8-family-calibration-cal-exp-blind-ceml4-7a34d37e5806.json |
| v1-8-family-calibration-cal-exp-blind-zeml4-97033b3e7f90 | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-calibration/runs/v1.8-family-calibration/v1-8-family-calibration-cal-exp-blind-zeml4-97033b3e7f90.json |
| v1-8-family-calibration-cal-exp-blind-ceml8-d51a7b70d1e9 | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-calibration/runs/v1.8-family-calibration/v1-8-family-calibration-cal-exp-blind-ceml8-d51a7b70d1e9.json |
| v1-8-family-calibration-cal-exp-blind-zeml8-e3b9ab80a7e5 | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-calibration/runs/v1.8-family-calibration/v1-8-family-calibration-cal-exp-blind-zeml8-e3b9ab80a7e5.json |
| v1-8-family-calibration-cal-exp-blind-zeml8-4-b101857743a1 | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-calibration/runs/v1.8-family-calibration/v1-8-family-calibration-cal-exp-blind-zeml8-4-b101857743a1.json |
| v1-8-family-calibration-cal-exp-blind-zeml8-4-2-1-da490deccc81 | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-calibration/runs/v1.8-family-calibration/v1-8-family-calibration-cal-exp-blind-zeml8-4-2-1-da490deccc81.json |
| v1-8-family-calibration-cal-log-blind-raw-e8a2eaff5220 | log | blind | recovered | scaffolded_blind_recovery | artifacts/campaigns/v1.8-family-calibration/runs/v1.8-family-calibration/v1-8-family-calibration-cal-log-blind-raw-e8a2eaff5220.json |
| v1-8-family-calibration-cal-log-blind-ceml1-145faacc55eb | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-calibration/runs/v1.8-family-calibration/v1-8-family-calibration-cal-log-blind-ceml1-145faacc55eb.json |
| v1-8-family-calibration-cal-log-blind-zeml1-fa1413e3a2b9 | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-calibration/runs/v1.8-family-calibration/v1-8-family-calibration-cal-log-blind-zeml1-fa1413e3a2b9.json |
| v1-8-family-calibration-cal-log-blind-ceml2-0c6593c3dbee | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-calibration/runs/v1.8-family-calibration/v1-8-family-calibration-cal-log-blind-ceml2-0c6593c3dbee.json |
| v1-8-family-calibration-cal-log-blind-zeml2-81ac561176ce | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-calibration/runs/v1.8-family-calibration/v1-8-family-calibration-cal-log-blind-zeml2-81ac561176ce.json |
| v1-8-family-calibration-cal-log-blind-ceml4-f22755a5508a | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-calibration/runs/v1.8-family-calibration/v1-8-family-calibration-cal-log-blind-ceml4-f22755a5508a.json |
| v1-8-family-calibration-cal-log-blind-zeml4-cd5f02bf0c9f | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-calibration/runs/v1.8-family-calibration/v1-8-family-calibration-cal-log-blind-zeml4-cd5f02bf0c9f.json |
| v1-8-family-calibration-cal-log-blind-ceml8-9ebccfce1ce0 | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-calibration/runs/v1.8-family-calibration/v1-8-family-calibration-cal-log-blind-ceml8-9ebccfce1ce0.json |
| v1-8-family-calibration-cal-log-blind-zeml8-ffe837486086 | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-calibration/runs/v1.8-family-calibration/v1-8-family-calibration-cal-log-blind-zeml8-ffe837486086.json |
| v1-8-family-calibration-cal-log-blind-zeml8-4-b461504b22c9 | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-calibration/runs/v1.8-family-calibration/v1-8-family-calibration-cal-log-blind-zeml8-4-b461504b22c9.json |
| v1-8-family-calibration-cal-log-blind-zeml8-4-2-1-2312f10518d4 | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-calibration/runs/v1.8-family-calibration/v1-8-family-calibration-cal-log-blind-zeml8-4-2-1-2312f10518d4.json |
