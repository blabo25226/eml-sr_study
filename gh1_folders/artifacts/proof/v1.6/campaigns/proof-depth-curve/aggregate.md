# Benchmark Evidence: proof-depth-curve

Measured v1.5 blind-vs-perturbed depth curve over deterministic exact EML targets at depths 2 through 6.

## Summary

| Metric | Value |
|--------|-------|
| total | 20 |
| verifier_recovered | 14 |
| same_ast_return | 10 |
| verified_equivalent_ast | 0 |
| repaired_candidate | 0 |
| unsupported | 0 |
| failed | 6 |
| execution_error | 0 |
| verifier_recovery_rate | 0.700 |

## By Formula

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| depth_curve_depth2 | 4 | 4 | 2 | 0 | 0 | 1.000 |
| depth_curve_depth3 | 4 | 4 | 2 | 0 | 0 | 1.000 |
| depth_curve_depth4 | 4 | 2 | 2 | 0 | 2 | 0.500 |
| depth_curve_depth5 | 4 | 2 | 2 | 0 | 2 | 0.500 |
| depth_curve_depth6 | 4 | 2 | 2 | 0 | 2 | 0.500 |

## By Start Mode

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| blind | 10 | 4 | 0 | 0 | 6 | 0.400 |
| perturbed_tree | 10 | 10 | 10 | 0 | 0 | 1.000 |

## By Evidence Class

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| blind_training_recovered | 2 | 2 | 0 | 0 | 0 | 1.000 |
| perturbed_true_tree_recovered | 10 | 10 | 10 | 0 | 0 | 1.000 |
| scaffolded_blind_training_recovered | 2 | 2 | 0 | 0 | 0 | 1.000 |
| snapped_but_failed | 6 | 0 | 0 | 0 | 6 | 0.000 |

## By Return Kind

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 10 | 4 | 0 | 0 | 6 | 0.400 |
| same_ast_return | 10 | 10 | 10 | 0 | 0 | 1.000 |

## By Raw Status

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 10 | 4 | 0 | 0 | 6 | 0.400 |
| recovered | 10 | 10 | 10 | 0 | 0 | 1.000 |

## By Repair Status

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| not_attempted | 14 | 14 | 10 | 0 | 0 | 1.000 |
| not_repaired | 6 | 0 | 0 | 0 | 6 | 0.000 |

## Depth Curve

| Depth | Mode | Seeds | Recovered | Total | Rate | Median Best Loss | Median Post-Snap Loss | Median Runtime | Median Snap Margin |
|-------|------|-------|-----------|-------|------|------------------|-----------------------|----------------|--------------------|
| 2 | blind | 2 | 2 | 2 | 1.000 | 8.4e-07 | 0 | 1.254 | 0.7704 |
| 2 | perturbed_tree | 2 | 2 | 2 | 1.000 | 0 | 0 | 0.9889 | 1 |
| 3 | blind | 2 | 2 | 2 | 1.000 | 0 | 0 | 1.884 | 1 |
| 3 | perturbed_tree | 2 | 2 | 2 | 1.000 | 0 | 0 | 1.001 | 1 |
| 4 | blind | 2 | 0 | 2 | 0.000 | 0.2319 | 0.636 | 2.723 | 0.5003 |
| 4 | perturbed_tree | 2 | 2 | 2 | 1.000 | 0 | 0 | 1.163 | 1 |
| 5 | blind | 2 | 0 | 2 | 0.000 | 2.007 | 2.014 | 4.674 | 1 |
| 5 | perturbed_tree | 2 | 2 | 2 | 1.000 | 0 | 0 | 1.235 | 1 |
| 6 | blind | 2 | 0 | 2 | 0.000 | 0.2871 | 0.3389 | 8.57 | 1 |
| 6 | perturbed_tree | 2 | 2 | 2 | 1.000 | 0 | 0 | 1.558 | 1 |

## Thresholds

| Claim | Policy | Eligible | Passed | Failed | Rate | Required | Status |
|-------|--------|----------|--------|--------|------|----------|--------|
| paper-blind-depth-degradation | measured_depth_curve | 20 | 20 | 0 | 1.000 |  | reported |

## Runs

| Run ID | Formula | Mode | Status | Classification | Artifact |
|--------|---------|------|--------|----------------|----------|
| proof-depth-curve-depth-2-blind-0b1b5fc59dd8 | depth_curve_depth2 | blind | recovered | blind_recovery | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-2-blind-0b1b5fc59dd8.json |
| proof-depth-curve-depth-2-blind-2dace23147bf | depth_curve_depth2 | blind | recovered | blind_recovery | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-2-blind-2dace23147bf.json |
| proof-depth-curve-depth-3-blind-d6c26a917882 | depth_curve_depth3 | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-3-blind-d6c26a917882.json |
| proof-depth-curve-depth-3-blind-a0df4b0ab1b4 | depth_curve_depth3 | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-3-blind-a0df4b0ab1b4.json |
| proof-depth-curve-depth-4-blind-0f9bab635276 | depth_curve_depth4 | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-4-blind-0f9bab635276.json |
| proof-depth-curve-depth-4-blind-344a2756d697 | depth_curve_depth4 | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-4-blind-344a2756d697.json |
| proof-depth-curve-depth-5-blind-f855e27799b5 | depth_curve_depth5 | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-5-blind-f855e27799b5.json |
| proof-depth-curve-depth-5-blind-81eda26add96 | depth_curve_depth5 | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-5-blind-81eda26add96.json |
| proof-depth-curve-depth-6-blind-804a64fb5351 | depth_curve_depth6 | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-6-blind-804a64fb5351.json |
| proof-depth-curve-depth-6-blind-d2ecd073c61c | depth_curve_depth6 | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-6-blind-d2ecd073c61c.json |
| proof-depth-curve-depth-2-perturbed-e76ace19ca5b | depth_curve_depth2 | perturbed_tree | recovered | same_ast_return | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-2-perturbed-e76ace19ca5b.json |
| proof-depth-curve-depth-2-perturbed-63c9dbc22949 | depth_curve_depth2 | perturbed_tree | recovered | same_ast_return | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-2-perturbed-63c9dbc22949.json |
| proof-depth-curve-depth-3-perturbed-5a87ef481565 | depth_curve_depth3 | perturbed_tree | recovered | same_ast_return | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-3-perturbed-5a87ef481565.json |
| proof-depth-curve-depth-3-perturbed-35d5a61c1b73 | depth_curve_depth3 | perturbed_tree | recovered | same_ast_return | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-3-perturbed-35d5a61c1b73.json |
| proof-depth-curve-depth-4-perturbed-01bf488498af | depth_curve_depth4 | perturbed_tree | recovered | same_ast_return | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-4-perturbed-01bf488498af.json |
| proof-depth-curve-depth-4-perturbed-1c743390bc74 | depth_curve_depth4 | perturbed_tree | recovered | same_ast_return | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-4-perturbed-1c743390bc74.json |
| proof-depth-curve-depth-5-perturbed-acbbb1e43aa6 | depth_curve_depth5 | perturbed_tree | recovered | same_ast_return | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-5-perturbed-acbbb1e43aa6.json |
| proof-depth-curve-depth-5-perturbed-ca69c9157585 | depth_curve_depth5 | perturbed_tree | recovered | same_ast_return | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-5-perturbed-ca69c9157585.json |
| proof-depth-curve-depth-6-perturbed-ac9bfe446f0f | depth_curve_depth6 | perturbed_tree | recovered | same_ast_return | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-6-perturbed-ac9bfe446f0f.json |
| proof-depth-curve-depth-6-perturbed-598372e89c3d | depth_curve_depth6 | perturbed_tree | recovered | same_ast_return | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-6-perturbed-598372e89c3d.json |
