# Benchmark Evidence: proof-depth-curve

v1.12 current-code subset of proof-depth-curve, blind depths 2 through 5 with two seeds each.

## Summary

| Metric | Value |
|--------|-------|
| total | 8 |
| verifier_recovered | 4 |
| same_ast_return | 0 |
| verified_equivalent_ast | 0 |
| repaired_candidate | 0 |
| unsupported | 0 |
| failed | 4 |
| execution_error | 0 |
| verifier_recovery_rate | 0.500 |

## By Formula

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| depth_curve_depth2 | 2 | 2 | 0 | 0 | 0 | 1.000 |
| depth_curve_depth3 | 2 | 2 | 0 | 0 | 0 | 1.000 |
| depth_curve_depth4 | 2 | 0 | 0 | 0 | 2 | 0.000 |
| depth_curve_depth5 | 2 | 0 | 0 | 0 | 2 | 0.000 |

## By Start Mode

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| blind | 8 | 4 | 0 | 0 | 4 | 0.500 |

## By Evidence Class

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| blind_training_recovered | 2 | 2 | 0 | 0 | 0 | 1.000 |
| scaffolded_blind_training_recovered | 2 | 2 | 0 | 0 | 0 | 1.000 |
| snapped_but_failed | 4 | 0 | 0 | 0 | 4 | 0.000 |

## By Return Kind

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 8 | 4 | 0 | 0 | 4 | 0.500 |

## By Raw Status

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 8 | 4 | 0 | 0 | 4 | 0.500 |

## By Repair Status

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| not_attempted | 4 | 4 | 0 | 0 | 0 | 1.000 |
| not_repaired | 4 | 0 | 0 | 0 | 4 | 0.000 |

## Depth Curve

| Depth | Mode | Seeds | Recovered | Total | Rate | Median Best Loss | Median Post-Snap Loss | Median Runtime | Median Snap Margin |
|-------|------|-------|-----------|-------|------|------------------|-----------------------|----------------|--------------------|
| 2 | blind | 2 | 2 | 2 | 1.000 | 8.4e-07 | 0 | 1.272 | 0.7704 |
| 3 | blind | 2 | 2 | 2 | 1.000 | 0 | 0 | 1.796 | 1 |
| 4 | blind | 2 | 0 | 2 | 0.000 | 0.2319 | 0.636 | 2.72 | 0.5003 |
| 5 | blind | 2 | 0 | 2 | 0.000 | 2.007 | 2.014 | 4.591 | 1 |

## Thresholds

| Claim | Policy | Eligible | Passed | Failed | Rate | Required | Status |
|-------|--------|----------|--------|--------|------|----------|--------|
| paper-blind-depth-degradation | measured_depth_curve | 8 | 8 | 0 | 1.000 |  | reported |

## Runs

| Run ID | Formula | Mode | Status | Classification | Artifact |
|--------|---------|------|--------|----------------|----------|
| proof-depth-curve-depth-2-blind-496b59f4c7cc | depth_curve_depth2 | blind | recovered | blind_recovery | artifacts/campaigns/v1.12-evidence-refresh/runs/proof-depth-curve/proof-depth-curve-depth-2-blind-496b59f4c7cc.json |
| proof-depth-curve-depth-2-blind-5ee1d10da503 | depth_curve_depth2 | blind | recovered | blind_recovery | artifacts/campaigns/v1.12-evidence-refresh/runs/proof-depth-curve/proof-depth-curve-depth-2-blind-5ee1d10da503.json |
| proof-depth-curve-depth-3-blind-4748c0afa168 | depth_curve_depth3 | blind | recovered | scaffolded_blind_recovery | artifacts/campaigns/v1.12-evidence-refresh/runs/proof-depth-curve/proof-depth-curve-depth-3-blind-4748c0afa168.json |
| proof-depth-curve-depth-3-blind-df010bca44c8 | depth_curve_depth3 | blind | recovered | scaffolded_blind_recovery | artifacts/campaigns/v1.12-evidence-refresh/runs/proof-depth-curve/proof-depth-curve-depth-3-blind-df010bca44c8.json |
| proof-depth-curve-depth-4-blind-bb92e8f39df6 | depth_curve_depth4 | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.12-evidence-refresh/runs/proof-depth-curve/proof-depth-curve-depth-4-blind-bb92e8f39df6.json |
| proof-depth-curve-depth-4-blind-53c3fee6869c | depth_curve_depth4 | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.12-evidence-refresh/runs/proof-depth-curve/proof-depth-curve-depth-4-blind-53c3fee6869c.json |
| proof-depth-curve-depth-5-blind-59fab048ae26 | depth_curve_depth5 | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.12-evidence-refresh/runs/proof-depth-curve/proof-depth-curve-depth-5-blind-59fab048ae26.json |
| proof-depth-curve-depth-5-blind-20b87b5ab8f8 | depth_curve_depth5 | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.12-evidence-refresh/runs/proof-depth-curve/proof-depth-curve-depth-5-blind-20b87b5ab8f8.json |
