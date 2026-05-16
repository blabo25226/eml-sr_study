# Benchmark Evidence: v1.3-showcase

Showcase v1.3 campaign matrix with expanded seeds, perturbations, and full FOR_DEMO diagnostics.

## Summary

| Metric | Value |
|--------|-------|
| total | 29 |
| verifier_recovered | 19 |
| same_ast_return | 12 |
| verified_equivalent_ast | 0 |
| repaired_candidate | 1 |
| unsupported | 4 |
| failed | 6 |
| execution_error | 0 |
| verifier_recovery_rate | 0.655 |

## By Formula

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| beer_lambert | 15 | 12 | 11 | 0 | 3 | 0.800 |
| damped_oscillator | 1 | 0 | 0 | 1 | 0 | 0.000 |
| exp | 3 | 3 | 0 | 0 | 0 | 1.000 |
| log | 3 | 3 | 0 | 0 | 0 | 1.000 |
| logistic | 1 | 0 | 0 | 1 | 0 | 0.000 |
| michaelis_menten | 1 | 0 | 0 | 1 | 0 | 0.000 |
| planck | 1 | 0 | 0 | 1 | 0 | 0.000 |
| radioactive_decay | 3 | 0 | 0 | 0 | 3 | 0.000 |
| shockley | 1 | 1 | 1 | 0 | 0 | 1.000 |

## By Start Mode

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| blind | 9 | 6 | 0 | 0 | 3 | 0.667 |
| compile | 3 | 0 | 0 | 3 | 0 | 0.000 |
| warm_start | 17 | 13 | 12 | 1 | 3 | 0.765 |

## By Evidence Class

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| repaired_candidate | 1 | 1 | 0 | 0 | 0 | 1.000 |
| same_ast | 12 | 12 | 12 | 0 | 0 | 1.000 |
| scaffolded_blind_training_recovered | 6 | 6 | 0 | 0 | 0 | 1.000 |
| snapped_but_failed | 6 | 0 | 0 | 0 | 6 | 0.000 |
| unsupported | 4 | 0 | 0 | 4 | 0 | 0.000 |

## By Return Kind

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 29 | 19 | 12 | 4 | 6 | 0.655 |

## By Raw Status

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 29 | 19 | 12 | 4 | 6 | 0.655 |

## By Repair Status

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 4 | 0 | 0 | 4 | 0 | 0.000 |
| not_attempted | 18 | 18 | 12 | 0 | 0 | 1.000 |
| not_repaired | 6 | 0 | 0 | 0 | 6 | 0.000 |
| repaired | 1 | 1 | 0 | 0 | 0 | 1.000 |

## Thresholds

No proof threshold metadata.

## Runs

| Run ID | Formula | Mode | Status | Classification | Artifact |
|--------|---------|------|--------|----------------|----------|
| v1-3-showcase-exp-blind-1223988aca5e | exp | blind | recovered | scaffolded_blind_recovery | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-exp-blind-1223988aca5e.json |
| v1-3-showcase-exp-blind-fdfa9d1cebd5 | exp | blind | recovered | scaffolded_blind_recovery | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-exp-blind-fdfa9d1cebd5.json |
| v1-3-showcase-exp-blind-de55d12697cc | exp | blind | recovered | scaffolded_blind_recovery | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-exp-blind-de55d12697cc.json |
| v1-3-showcase-log-blind-f8f1f47a96a6 | log | blind | recovered | scaffolded_blind_recovery | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-log-blind-f8f1f47a96a6.json |
| v1-3-showcase-log-blind-46217afc1013 | log | blind | recovered | scaffolded_blind_recovery | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-log-blind-46217afc1013.json |
| v1-3-showcase-log-blind-002f421e5add | log | blind | recovered | scaffolded_blind_recovery | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-log-blind-002f421e5add.json |
| v1-3-showcase-radioactive-decay-blind-b3e3e9713a2f | radioactive_decay | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-radioactive-decay-blind-b3e3e9713a2f.json |
| v1-3-showcase-radioactive-decay-blind-e6ed81811e49 | radioactive_decay | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-radioactive-decay-blind-e6ed81811e49.json |
| v1-3-showcase-radioactive-decay-blind-ad44bbc72189 | radioactive_decay | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-radioactive-decay-blind-ad44bbc72189.json |
| v1-3-showcase-beer-perturbation-sweep-7a705735af42 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-7a705735af42.json |
| v1-3-showcase-beer-perturbation-sweep-105fd696ec80 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-105fd696ec80.json |
| v1-3-showcase-beer-perturbation-sweep-f5fb4afc3fc3 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-f5fb4afc3fc3.json |
| v1-3-showcase-beer-perturbation-sweep-67732a5a3921 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-67732a5a3921.json |
| v1-3-showcase-beer-perturbation-sweep-898774a53e8f | beer_lambert | warm_start | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-898774a53e8f.json |
| v1-3-showcase-beer-perturbation-sweep-84c321ff4354 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-84c321ff4354.json |
| v1-3-showcase-beer-perturbation-sweep-2c74c6ebc8d3 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-2c74c6ebc8d3.json |
| v1-3-showcase-beer-perturbation-sweep-3601930f8cf8 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-3601930f8cf8.json |
| v1-3-showcase-beer-perturbation-sweep-9d375abe6a37 | beer_lambert | warm_start | repaired_candidate | repaired_candidate | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-9d375abe6a37.json |
| v1-3-showcase-beer-perturbation-sweep-e461b66ca248 | beer_lambert | warm_start | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-e461b66ca248.json |
| v1-3-showcase-beer-perturbation-sweep-5b9a5093b129 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-5b9a5093b129.json |
| v1-3-showcase-beer-perturbation-sweep-ab6e86d19a02 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-ab6e86d19a02.json |
| v1-3-showcase-beer-perturbation-sweep-2e88732ec838 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-2e88732ec838.json |
| v1-3-showcase-beer-perturbation-sweep-51b555e68bc2 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-51b555e68bc2.json |
| v1-3-showcase-beer-perturbation-sweep-9795c140e91e | beer_lambert | warm_start | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-9795c140e91e.json |
| v1-3-showcase-michaelis-warm-diagnostic-137223f28fd1 | michaelis_menten | warm_start | unsupported | unsupported | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-michaelis-warm-diagnostic-137223f28fd1.json |
| v1-3-showcase-logistic-compile-f711ed10dbe9 | logistic | compile | unsupported | unsupported | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-logistic-compile-f711ed10dbe9.json |
| v1-3-showcase-shockley-warm-2fa15c5c91e5 | shockley | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-shockley-warm-2fa15c5c91e5.json |
| v1-3-showcase-damped-oscillator-compile-5bbd87a8b2d5 | damped_oscillator | compile | unsupported | unsupported | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-damped-oscillator-compile-5bbd87a8b2d5.json |
| v1-3-showcase-planck-diagnostic-29e4faa8cb28 | planck | compile | unsupported | unsupported | artifacts/campaigns/v1.6-showcase/runs/v1.3-showcase/v1-3-showcase-planck-diagnostic-29e4faa8cb28.json |
