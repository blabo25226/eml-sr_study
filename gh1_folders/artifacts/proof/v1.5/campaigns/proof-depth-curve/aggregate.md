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
| none | 10 | 4 | 0 | 0 | 6 | 0.400 |
| not_attempted | 10 | 10 | 10 | 0 | 0 | 1.000 |

## Depth Curve

| Depth | Mode | Seeds | Recovered | Total | Rate | Median Best Loss | Median Post-Snap Loss | Median Runtime | Median Snap Margin |
|-------|------|-------|-----------|-------|------|------------------|-----------------------|----------------|--------------------|
| 2 | blind | 2 | 2 | 2 | 1.000 | 8.4e-07 | 0 | 0.2536 | 0.77 |
| 2 | perturbed_tree | 2 | 2 | 2 | 1.000 | 0 | 0 | 0.03073 | 1 |
| 3 | blind | 2 | 2 | 2 | 1.000 | 0 | 0 | 0.6651 | 1 |
| 3 | perturbed_tree | 2 | 2 | 2 | 1.000 | 0 | 0 | 0.05048 | 1 |
| 4 | blind | 2 | 0 | 2 | 0.000 | 0.1544 | 0.1544 | 1.375 | 1 |
| 4 | perturbed_tree | 2 | 2 | 2 | 1.000 | 0 | 0 | 0.1229 | 1 |
| 5 | blind | 2 | 0 | 2 | 0.000 | 1.642 | 13.19 | 2.797 | 1 |
| 5 | perturbed_tree | 2 | 2 | 2 | 1.000 | 0 | 0 | 0.2315 | 1 |
| 6 | blind | 2 | 0 | 2 | 0.000 | 0.2871 | 0.3389 | 5.795 | 1 |
| 6 | perturbed_tree | 2 | 2 | 2 | 1.000 | 0 | 0 | 0.4517 | 1 |

## Thresholds

| Claim | Policy | Eligible | Passed | Failed | Rate | Required | Status |
|-------|--------|----------|--------|--------|------|----------|--------|
| paper-blind-depth-degradation | measured_depth_curve | 20 | 20 | 0 | 1.000 |  | reported |

## Runs

| Run ID | Formula | Mode | Status | Classification | Artifact |
|--------|---------|------|--------|----------------|----------|
| proof-depth-curve-depth-2-blind-17bd9a2936b1 | depth_curve_depth2 | blind | recovered | blind_recovery | artifacts/proof/v1.5/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-2-blind-17bd9a2936b1.json |
| proof-depth-curve-depth-2-blind-4c184578f74f | depth_curve_depth2 | blind | recovered | blind_recovery | artifacts/proof/v1.5/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-2-blind-4c184578f74f.json |
| proof-depth-curve-depth-3-blind-8f85ae959a38 | depth_curve_depth3 | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.5/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-3-blind-8f85ae959a38.json |
| proof-depth-curve-depth-3-blind-ac82db6d6764 | depth_curve_depth3 | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.5/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-3-blind-ac82db6d6764.json |
| proof-depth-curve-depth-4-blind-6ad7eec175ad | depth_curve_depth4 | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.5/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-4-blind-6ad7eec175ad.json |
| proof-depth-curve-depth-4-blind-e38357e3bcab | depth_curve_depth4 | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.5/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-4-blind-e38357e3bcab.json |
| proof-depth-curve-depth-5-blind-c01a728c6cbe | depth_curve_depth5 | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.5/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-5-blind-c01a728c6cbe.json |
| proof-depth-curve-depth-5-blind-ba7e09d15414 | depth_curve_depth5 | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.5/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-5-blind-ba7e09d15414.json |
| proof-depth-curve-depth-6-blind-7e47c402949e | depth_curve_depth6 | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.5/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-6-blind-7e47c402949e.json |
| proof-depth-curve-depth-6-blind-03115ea5f9ea | depth_curve_depth6 | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.5/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-6-blind-03115ea5f9ea.json |
| proof-depth-curve-depth-2-perturbed-3de1d79cc0f3 | depth_curve_depth2 | perturbed_tree | recovered | same_ast_return | artifacts/proof/v1.5/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-2-perturbed-3de1d79cc0f3.json |
| proof-depth-curve-depth-2-perturbed-91916fa77565 | depth_curve_depth2 | perturbed_tree | recovered | same_ast_return | artifacts/proof/v1.5/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-2-perturbed-91916fa77565.json |
| proof-depth-curve-depth-3-perturbed-c384e08766a9 | depth_curve_depth3 | perturbed_tree | recovered | same_ast_return | artifacts/proof/v1.5/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-3-perturbed-c384e08766a9.json |
| proof-depth-curve-depth-3-perturbed-cbeb5a468777 | depth_curve_depth3 | perturbed_tree | recovered | same_ast_return | artifacts/proof/v1.5/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-3-perturbed-cbeb5a468777.json |
| proof-depth-curve-depth-4-perturbed-68710a3a7bad | depth_curve_depth4 | perturbed_tree | recovered | same_ast_return | artifacts/proof/v1.5/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-4-perturbed-68710a3a7bad.json |
| proof-depth-curve-depth-4-perturbed-164d3257b4f0 | depth_curve_depth4 | perturbed_tree | recovered | same_ast_return | artifacts/proof/v1.5/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-4-perturbed-164d3257b4f0.json |
| proof-depth-curve-depth-5-perturbed-e7be40516916 | depth_curve_depth5 | perturbed_tree | recovered | same_ast_return | artifacts/proof/v1.5/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-5-perturbed-e7be40516916.json |
| proof-depth-curve-depth-5-perturbed-3ce3b8651941 | depth_curve_depth5 | perturbed_tree | recovered | same_ast_return | artifacts/proof/v1.5/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-5-perturbed-3ce3b8651941.json |
| proof-depth-curve-depth-6-perturbed-9ab7f2bd6d7c | depth_curve_depth6 | perturbed_tree | recovered | same_ast_return | artifacts/proof/v1.5/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-6-perturbed-9ab7f2bd6d7c.json |
| proof-depth-curve-depth-6-perturbed-b55882837434 | depth_curve_depth6 | perturbed_tree | recovered | same_ast_return | artifacts/proof/v1.5/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-6-perturbed-b55882837434.json |
