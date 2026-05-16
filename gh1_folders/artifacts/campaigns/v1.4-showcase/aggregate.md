# Benchmark Evidence: v1.3-showcase

Showcase v1.3 campaign matrix with expanded seeds, perturbations, and full FOR_DEMO diagnostics.

## Summary

| Metric | Value |
|--------|-------|
| total | 29 |
| verifier_recovered | 18 |
| same_ast_return | 11 |
| verified_equivalent_ast | 0 |
| unsupported | 4 |
| failed | 7 |
| execution_error | 0 |
| verifier_recovery_rate | 0.621 |

## By Formula

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| beer_lambert | 15 | 11 | 11 | 0 | 4 | 0.733 |
| damped_oscillator | 1 | 0 | 0 | 1 | 0 | 0.000 |
| exp | 3 | 3 | 0 | 0 | 0 | 1.000 |
| log | 3 | 3 | 0 | 0 | 0 | 1.000 |
| logistic | 1 | 0 | 0 | 1 | 0 | 0.000 |
| michaelis_menten | 1 | 0 | 0 | 1 | 0 | 0.000 |
| planck | 1 | 0 | 0 | 1 | 0 | 0.000 |
| radioactive_decay | 3 | 0 | 0 | 0 | 3 | 0.000 |
| shockley | 1 | 1 | 0 | 0 | 0 | 1.000 |

## By Start Mode

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| blind | 9 | 6 | 0 | 0 | 3 | 0.667 |
| compile | 4 | 1 | 0 | 3 | 0 | 0.250 |
| warm_start | 16 | 11 | 11 | 1 | 4 | 0.688 |

## Runs

| Run ID | Formula | Mode | Status | Classification | Artifact |
|--------|---------|------|--------|----------------|----------|
| v1-3-showcase-exp-blind-c9b0efbce9ee | exp | blind | recovered | blind_recovery | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-exp-blind-c9b0efbce9ee.json |
| v1-3-showcase-exp-blind-09e5792b415c | exp | blind | recovered | blind_recovery | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-exp-blind-09e5792b415c.json |
| v1-3-showcase-exp-blind-730f8205e3a5 | exp | blind | recovered | blind_recovery | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-exp-blind-730f8205e3a5.json |
| v1-3-showcase-log-blind-4295ef60db62 | log | blind | recovered | blind_recovery | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-log-blind-4295ef60db62.json |
| v1-3-showcase-log-blind-a1794a209f92 | log | blind | recovered | blind_recovery | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-log-blind-a1794a209f92.json |
| v1-3-showcase-log-blind-1d187302bd3e | log | blind | recovered | blind_recovery | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-log-blind-1d187302bd3e.json |
| v1-3-showcase-radioactive-decay-blind-dbaaf54f8dfc | radioactive_decay | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-radioactive-decay-blind-dbaaf54f8dfc.json |
| v1-3-showcase-radioactive-decay-blind-1e9c9e6e9a4c | radioactive_decay | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-radioactive-decay-blind-1e9c9e6e9a4c.json |
| v1-3-showcase-radioactive-decay-blind-0015db66c35c | radioactive_decay | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-radioactive-decay-blind-0015db66c35c.json |
| v1-3-showcase-beer-perturbation-sweep-435be952d0ca | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-435be952d0ca.json |
| v1-3-showcase-beer-perturbation-sweep-69eabbb6d241 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-69eabbb6d241.json |
| v1-3-showcase-beer-perturbation-sweep-937ebfff3599 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-937ebfff3599.json |
| v1-3-showcase-beer-perturbation-sweep-a55eaf5ac72f | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-a55eaf5ac72f.json |
| v1-3-showcase-beer-perturbation-sweep-860689755983 | beer_lambert | warm_start | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-860689755983.json |
| v1-3-showcase-beer-perturbation-sweep-642d7c182505 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-642d7c182505.json |
| v1-3-showcase-beer-perturbation-sweep-ed542eadbeb0 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-ed542eadbeb0.json |
| v1-3-showcase-beer-perturbation-sweep-20388cb78c9d | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-20388cb78c9d.json |
| v1-3-showcase-beer-perturbation-sweep-56c113f0e392 | beer_lambert | warm_start | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-56c113f0e392.json |
| v1-3-showcase-beer-perturbation-sweep-2acd7b37ee9f | beer_lambert | warm_start | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-2acd7b37ee9f.json |
| v1-3-showcase-beer-perturbation-sweep-f11f07ab5477 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-f11f07ab5477.json |
| v1-3-showcase-beer-perturbation-sweep-d8563b7ff680 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-d8563b7ff680.json |
| v1-3-showcase-beer-perturbation-sweep-09e504e576e9 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-09e504e576e9.json |
| v1-3-showcase-beer-perturbation-sweep-6e963c8bca4f | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-6e963c8bca4f.json |
| v1-3-showcase-beer-perturbation-sweep-f83ffd7672b5 | beer_lambert | warm_start | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-f83ffd7672b5.json |
| v1-3-showcase-michaelis-warm-diagnostic-cb89f09c390e | michaelis_menten | warm_start | unsupported | unsupported | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-michaelis-warm-diagnostic-cb89f09c390e.json |
| v1-3-showcase-logistic-compile-4792983fd836 | logistic | compile | unsupported | unsupported | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-logistic-compile-4792983fd836.json |
| v1-3-showcase-shockley-compile-8e2473a415b0 | shockley | compile | recovered | verifier_recovered | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-shockley-compile-8e2473a415b0.json |
| v1-3-showcase-damped-oscillator-compile-cdce11ebc3e2 | damped_oscillator | compile | unsupported | unsupported | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-damped-oscillator-compile-cdce11ebc3e2.json |
| v1-3-showcase-planck-diagnostic-46fe96170216 | planck | compile | unsupported | unsupported | artifacts/campaigns/v1.4-showcase/runs/v1.3-showcase/v1-3-showcase-planck-diagnostic-46fe96170216.json |
