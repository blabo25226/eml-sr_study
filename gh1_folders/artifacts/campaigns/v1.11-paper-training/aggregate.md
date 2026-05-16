# Benchmark Evidence: v1.11-paper-training

Compact v1.11 current-code training refresh with pure blind, scaffolded, same-AST warm-start, and perturbed-basin regimes kept separate.

## Summary

| Metric | Value |
|--------|-------|
| total | 8 |
| verifier_recovered | 8 |
| same_ast_return | 4 |
| verified_equivalent_ast | 0 |
| repaired_candidate | 0 |
| unsupported | 0 |
| failed | 0 |
| execution_error | 0 |
| verifier_recovery_rate | 1.000 |

## By Formula

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| arrhenius | 1 | 1 | 1 | 0 | 0 | 1.000 |
| basin_depth2_exp_exp | 1 | 1 | 1 | 0 | 0 | 1.000 |
| exp | 4 | 4 | 0 | 0 | 0 | 1.000 |
| michaelis_menten | 1 | 1 | 1 | 0 | 0 | 1.000 |
| shockley | 1 | 1 | 1 | 0 | 0 | 1.000 |

## By Start Mode

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| blind | 4 | 4 | 0 | 0 | 0 | 1.000 |
| perturbed_tree | 1 | 1 | 1 | 0 | 0 | 1.000 |
| warm_start | 3 | 3 | 3 | 0 | 0 | 1.000 |

## By Evidence Class

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| blind_training_recovered | 2 | 2 | 0 | 0 | 0 | 1.000 |
| perturbed_true_tree_recovered | 1 | 1 | 1 | 0 | 0 | 1.000 |
| same_ast | 3 | 3 | 3 | 0 | 0 | 1.000 |
| scaffolded_blind_training_recovered | 2 | 2 | 0 | 0 | 0 | 1.000 |

## By Return Kind

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 7 | 7 | 3 | 0 | 0 | 1.000 |
| same_ast_return | 1 | 1 | 1 | 0 | 0 | 1.000 |

## By Raw Status

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 7 | 7 | 3 | 0 | 0 | 1.000 |
| recovered | 1 | 1 | 1 | 0 | 0 | 1.000 |

## By Repair Status

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| not_attempted | 8 | 8 | 4 | 0 | 0 | 1.000 |

## Thresholds

No proof threshold metadata.

## Runs

| Run ID | Formula | Mode | Status | Classification | Artifact |
|--------|---------|------|--------|----------------|----------|
| v1-11-paper-training-exp-pure-blind-02b2ebc9a4bf | exp | blind | recovered | blind_recovery | artifacts/campaigns/v1.11-paper-training/runs/v1.11-paper-training/v1-11-paper-training-exp-pure-blind-02b2ebc9a4bf.json |
| v1-11-paper-training-exp-pure-blind-484769b6d061 | exp | blind | recovered | blind_recovery | artifacts/campaigns/v1.11-paper-training/runs/v1.11-paper-training/v1-11-paper-training-exp-pure-blind-484769b6d061.json |
| v1-11-paper-training-exp-scaffolded-64550481e523 | exp | blind | recovered | scaffolded_blind_recovery | artifacts/campaigns/v1.11-paper-training/runs/v1.11-paper-training/v1-11-paper-training-exp-scaffolded-64550481e523.json |
| v1-11-paper-training-exp-scaffolded-b7facf8bcdec | exp | blind | recovered | scaffolded_blind_recovery | artifacts/campaigns/v1.11-paper-training/runs/v1.11-paper-training/v1-11-paper-training-exp-scaffolded-b7facf8bcdec.json |
| v1-11-paper-training-shockley-warm-8328865acd4f | shockley | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.11-paper-training/runs/v1.11-paper-training/v1-11-paper-training-shockley-warm-8328865acd4f.json |
| v1-11-paper-training-arrhenius-warm-2e7a23831737 | arrhenius | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.11-paper-training/runs/v1.11-paper-training/v1-11-paper-training-arrhenius-warm-2e7a23831737.json |
| v1-11-paper-training-michaelis-warm-93d60f54c668 | michaelis_menten | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.11-paper-training/runs/v1.11-paper-training/v1-11-paper-training-michaelis-warm-93d60f54c668.json |
| v1-11-paper-training-basin-depth2-perturbed-9c94515981c5 | basin_depth2_exp_exp | perturbed_tree | recovered | same_ast_return | artifacts/campaigns/v1.11-paper-training/runs/v1.11-paper-training/v1-11-paper-training-basin-depth2-perturbed-9c94515981c5.json |
