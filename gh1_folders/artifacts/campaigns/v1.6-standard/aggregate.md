# Benchmark Evidence: v1.3-standard

Standard v1.3 campaign matrix with shallow blind baselines, perturbation sweeps, and FOR_DEMO diagnostics.

## Summary

| Metric | Value |
|--------|-------|
| total | 16 |
| verifier_recovered | 9 |
| same_ast_return | 5 |
| verified_equivalent_ast | 0 |
| repaired_candidate | 0 |
| unsupported | 3 |
| failed | 4 |
| execution_error | 0 |
| verifier_recovery_rate | 0.562 |

## By Formula

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| beer_lambert | 6 | 4 | 4 | 0 | 2 | 0.667 |
| exp | 2 | 2 | 0 | 0 | 0 | 1.000 |
| log | 2 | 2 | 0 | 0 | 0 | 1.000 |
| logistic | 1 | 0 | 0 | 1 | 0 | 0.000 |
| michaelis_menten | 1 | 0 | 0 | 1 | 0 | 0.000 |
| planck | 1 | 0 | 0 | 1 | 0 | 0.000 |
| radioactive_decay | 2 | 0 | 0 | 0 | 2 | 0.000 |
| shockley | 1 | 1 | 1 | 0 | 0 | 1.000 |

## By Start Mode

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| blind | 6 | 4 | 0 | 0 | 2 | 0.667 |
| compile | 2 | 0 | 0 | 2 | 0 | 0.000 |
| warm_start | 8 | 5 | 5 | 1 | 2 | 0.625 |

## By Evidence Class

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| same_ast | 5 | 5 | 5 | 0 | 0 | 1.000 |
| scaffolded_blind_training_recovered | 4 | 4 | 0 | 0 | 0 | 1.000 |
| snapped_but_failed | 4 | 0 | 0 | 0 | 4 | 0.000 |
| unsupported | 3 | 0 | 0 | 3 | 0 | 0.000 |

## By Return Kind

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 16 | 9 | 5 | 3 | 4 | 0.562 |

## By Raw Status

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 16 | 9 | 5 | 3 | 4 | 0.562 |

## By Repair Status

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 3 | 0 | 0 | 3 | 0 | 0.000 |
| not_attempted | 9 | 9 | 5 | 0 | 0 | 1.000 |
| not_repaired | 4 | 0 | 0 | 0 | 4 | 0.000 |

## Thresholds

No proof threshold metadata.

## Runs

| Run ID | Formula | Mode | Status | Classification | Artifact |
|--------|---------|------|--------|----------------|----------|
| v1-3-standard-exp-blind-614ae767075b | exp | blind | recovered | scaffolded_blind_recovery | artifacts/campaigns/v1.6-standard/runs/v1.3-standard/v1-3-standard-exp-blind-614ae767075b.json |
| v1-3-standard-exp-blind-648611a34c09 | exp | blind | recovered | scaffolded_blind_recovery | artifacts/campaigns/v1.6-standard/runs/v1.3-standard/v1-3-standard-exp-blind-648611a34c09.json |
| v1-3-standard-log-blind-6ae6e02d45eb | log | blind | recovered | scaffolded_blind_recovery | artifacts/campaigns/v1.6-standard/runs/v1.3-standard/v1-3-standard-log-blind-6ae6e02d45eb.json |
| v1-3-standard-log-blind-0c0b9d47ee16 | log | blind | recovered | scaffolded_blind_recovery | artifacts/campaigns/v1.6-standard/runs/v1.3-standard/v1-3-standard-log-blind-0c0b9d47ee16.json |
| v1-3-standard-radioactive-decay-blind-89532c08e43a | radioactive_decay | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.6-standard/runs/v1.3-standard/v1-3-standard-radioactive-decay-blind-89532c08e43a.json |
| v1-3-standard-radioactive-decay-blind-4f7c8ca23154 | radioactive_decay | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.6-standard/runs/v1.3-standard/v1-3-standard-radioactive-decay-blind-4f7c8ca23154.json |
| v1-3-standard-beer-perturbation-sweep-c671cedf25f1 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.6-standard/runs/v1.3-standard/v1-3-standard-beer-perturbation-sweep-c671cedf25f1.json |
| v1-3-standard-beer-perturbation-sweep-1d8cb4154f82 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.6-standard/runs/v1.3-standard/v1-3-standard-beer-perturbation-sweep-1d8cb4154f82.json |
| v1-3-standard-beer-perturbation-sweep-7ab0d86550b5 | beer_lambert | warm_start | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.6-standard/runs/v1.3-standard/v1-3-standard-beer-perturbation-sweep-7ab0d86550b5.json |
| v1-3-standard-beer-perturbation-sweep-e788a78570ad | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.6-standard/runs/v1.3-standard/v1-3-standard-beer-perturbation-sweep-e788a78570ad.json |
| v1-3-standard-beer-perturbation-sweep-733ae644e204 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.6-standard/runs/v1.3-standard/v1-3-standard-beer-perturbation-sweep-733ae644e204.json |
| v1-3-standard-beer-perturbation-sweep-0a5d1d92fa79 | beer_lambert | warm_start | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.6-standard/runs/v1.3-standard/v1-3-standard-beer-perturbation-sweep-0a5d1d92fa79.json |
| v1-3-standard-michaelis-warm-diagnostic-9917f8383370 | michaelis_menten | warm_start | unsupported | unsupported | artifacts/campaigns/v1.6-standard/runs/v1.3-standard/v1-3-standard-michaelis-warm-diagnostic-9917f8383370.json |
| v1-3-standard-logistic-compile-a99c41f57b97 | logistic | compile | unsupported | unsupported | artifacts/campaigns/v1.6-standard/runs/v1.3-standard/v1-3-standard-logistic-compile-a99c41f57b97.json |
| v1-3-standard-shockley-warm-316f98a5b1fb | shockley | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.6-standard/runs/v1.3-standard/v1-3-standard-shockley-warm-316f98a5b1fb.json |
| v1-3-standard-planck-diagnostic-2309e6363fc8 | planck | compile | unsupported | unsupported | artifacts/campaigns/v1.6-standard/runs/v1.3-standard/v1-3-standard-planck-diagnostic-2309e6363fc8.json |
