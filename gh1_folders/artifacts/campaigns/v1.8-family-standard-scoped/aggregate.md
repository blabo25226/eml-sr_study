# Benchmark Evidence: v1.8-family-standard

v1.8 standard-style raw-vs-centered operator-family comparison matrix.

## Summary

| Metric | Value |
|--------|-------|
| total | 55 |
| verifier_recovered | 4 |
| same_ast_return | 2 |
| verified_equivalent_ast | 0 |
| repaired_candidate | 0 |
| unsupported | 30 |
| failed | 21 |
| execution_error | 0 |
| verifier_recovery_rate | 0.073 |

## By Formula

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| beer_lambert | 33 | 2 | 2 | 30 | 1 | 0.061 |
| exp | 11 | 1 | 0 | 0 | 10 | 0.091 |
| log | 11 | 1 | 0 | 0 | 10 | 0.091 |

## By Start Mode

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| blind | 22 | 2 | 0 | 0 | 20 | 0.091 |
| warm_start | 33 | 2 | 2 | 30 | 1 | 0.061 |

## By Evidence Class

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| same_ast | 2 | 2 | 2 | 0 | 0 | 1.000 |
| scaffolded_blind_training_recovered | 2 | 2 | 0 | 0 | 0 | 1.000 |
| snapped_but_failed | 21 | 0 | 0 | 0 | 21 | 0.000 |
| unsupported | 30 | 0 | 0 | 30 | 0 | 0.000 |

## By Return Kind

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 55 | 4 | 2 | 30 | 21 | 0.073 |

## By Raw Status

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 55 | 4 | 2 | 30 | 21 | 0.073 |

## By Repair Status

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 30 | 0 | 0 | 30 | 0 | 0.000 |
| not_attempted | 4 | 4 | 2 | 0 | 0 | 1.000 |
| not_repaired | 21 | 0 | 0 | 0 | 21 | 0.000 |

## Thresholds

No proof threshold metadata.

## Runs

| Run ID | Formula | Mode | Status | Classification | Artifact |
|--------|---------|------|--------|----------------|----------|
| v1-8-family-standard-exp-blind-raw-db98b346491e | exp | blind | recovered | scaffolded_blind_recovery | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-exp-blind-raw-db98b346491e.json |
| v1-8-family-standard-exp-blind-ceml1-4ac74eb747e9 | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-exp-blind-ceml1-4ac74eb747e9.json |
| v1-8-family-standard-exp-blind-zeml1-c9c4d5c0452f | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-exp-blind-zeml1-c9c4d5c0452f.json |
| v1-8-family-standard-exp-blind-ceml2-3460d3d0f07b | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-exp-blind-ceml2-3460d3d0f07b.json |
| v1-8-family-standard-exp-blind-zeml2-052d8389ce66 | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-exp-blind-zeml2-052d8389ce66.json |
| v1-8-family-standard-exp-blind-ceml4-26af8c11d98f | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-exp-blind-ceml4-26af8c11d98f.json |
| v1-8-family-standard-exp-blind-zeml4-fc85b8b90bd9 | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-exp-blind-zeml4-fc85b8b90bd9.json |
| v1-8-family-standard-exp-blind-ceml8-57c361c3087d | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-exp-blind-ceml8-57c361c3087d.json |
| v1-8-family-standard-exp-blind-zeml8-e04f0ac48af2 | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-exp-blind-zeml8-e04f0ac48af2.json |
| v1-8-family-standard-exp-blind-zeml8-4-f86120c07c43 | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-exp-blind-zeml8-4-f86120c07c43.json |
| v1-8-family-standard-exp-blind-zeml8-4-2-1-22405499cfd3 | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-exp-blind-zeml8-4-2-1-22405499cfd3.json |
| v1-8-family-standard-log-blind-raw-49258e1cb4d3 | log | blind | recovered | scaffolded_blind_recovery | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-log-blind-raw-49258e1cb4d3.json |
| v1-8-family-standard-log-blind-ceml1-500936c57f56 | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-log-blind-ceml1-500936c57f56.json |
| v1-8-family-standard-log-blind-zeml1-4298c6f72051 | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-log-blind-zeml1-4298c6f72051.json |
| v1-8-family-standard-log-blind-ceml2-65b963c89fe2 | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-log-blind-ceml2-65b963c89fe2.json |
| v1-8-family-standard-log-blind-zeml2-047716b7ebfd | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-log-blind-zeml2-047716b7ebfd.json |
| v1-8-family-standard-log-blind-ceml4-8bfc5907251e | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-log-blind-ceml4-8bfc5907251e.json |
| v1-8-family-standard-log-blind-zeml4-1e4906b2ec67 | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-log-blind-zeml4-1e4906b2ec67.json |
| v1-8-family-standard-log-blind-ceml8-1cb2f880fa79 | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-log-blind-ceml8-1cb2f880fa79.json |
| v1-8-family-standard-log-blind-zeml8-aea3cc56bb3e | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-log-blind-zeml8-aea3cc56bb3e.json |
| v1-8-family-standard-log-blind-zeml8-4-330e850cf115 | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-log-blind-zeml8-4-330e850cf115.json |
| v1-8-family-standard-log-blind-zeml8-4-2-1-2fd93e56ae3b | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-log-blind-zeml8-4-2-1-2fd93e56ae3b.json |
| v1-8-family-standard-beer-perturbation-sweep-raw-866e8b638594 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-raw-866e8b638594.json |
| v1-8-family-standard-beer-perturbation-sweep-raw-c0220ac1cfdd | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-raw-c0220ac1cfdd.json |
| v1-8-family-standard-beer-perturbation-sweep-raw-7b05bd4371e8 | beer_lambert | warm_start | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-raw-7b05bd4371e8.json |
| v1-8-family-standard-beer-perturbation-sweep-ceml1-146335ce3726 | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-ceml1-146335ce3726.json |
| v1-8-family-standard-beer-perturbation-sweep-ceml1-55d57998a902 | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-ceml1-55d57998a902.json |
| v1-8-family-standard-beer-perturbation-sweep-ceml1-5bb6d361f55c | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-ceml1-5bb6d361f55c.json |
| v1-8-family-standard-beer-perturbation-sweep-zeml1-32c4d2e4d993 | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml1-32c4d2e4d993.json |
| v1-8-family-standard-beer-perturbation-sweep-zeml1-5c03faa3db0d | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml1-5c03faa3db0d.json |
| v1-8-family-standard-beer-perturbation-sweep-zeml1-f2b4e5a617ba | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml1-f2b4e5a617ba.json |
| v1-8-family-standard-beer-perturbation-sweep-ceml2-a0369f6c88f9 | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-ceml2-a0369f6c88f9.json |
| v1-8-family-standard-beer-perturbation-sweep-ceml2-ddb5f3a08a00 | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-ceml2-ddb5f3a08a00.json |
| v1-8-family-standard-beer-perturbation-sweep-ceml2-b0c30057282d | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-ceml2-b0c30057282d.json |
| v1-8-family-standard-beer-perturbation-sweep-zeml2-486c46e2f769 | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml2-486c46e2f769.json |
| v1-8-family-standard-beer-perturbation-sweep-zeml2-274fd7b0df71 | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml2-274fd7b0df71.json |
| v1-8-family-standard-beer-perturbation-sweep-zeml2-5d0d1805d66e | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml2-5d0d1805d66e.json |
| v1-8-family-standard-beer-perturbation-sweep-ceml4-740b75a4dfc1 | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-ceml4-740b75a4dfc1.json |
| v1-8-family-standard-beer-perturbation-sweep-ceml4-64abb61351e3 | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-ceml4-64abb61351e3.json |
| v1-8-family-standard-beer-perturbation-sweep-ceml4-e22858d2497a | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-ceml4-e22858d2497a.json |
| v1-8-family-standard-beer-perturbation-sweep-zeml4-a4c14acf6544 | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml4-a4c14acf6544.json |
| v1-8-family-standard-beer-perturbation-sweep-zeml4-0981a6b74629 | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml4-0981a6b74629.json |
| v1-8-family-standard-beer-perturbation-sweep-zeml4-c43701519585 | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml4-c43701519585.json |
| v1-8-family-standard-beer-perturbation-sweep-ceml8-52ca002e41e7 | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-ceml8-52ca002e41e7.json |
| v1-8-family-standard-beer-perturbation-sweep-ceml8-180ebe5aefb4 | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-ceml8-180ebe5aefb4.json |
| v1-8-family-standard-beer-perturbation-sweep-ceml8-423f08ba249e | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-ceml8-423f08ba249e.json |
| v1-8-family-standard-beer-perturbation-sweep-zeml8-d2fb5d5d1422 | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml8-d2fb5d5d1422.json |
| v1-8-family-standard-beer-perturbation-sweep-zeml8-a08d9eab88b3 | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml8-a08d9eab88b3.json |
| v1-8-family-standard-beer-perturbation-sweep-zeml8-8b46234c400d | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml8-8b46234c400d.json |
| v1-8-family-standard-beer-perturbation-sweep-zeml8-4-de36987134db | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml8-4-de36987134db.json |
| v1-8-family-standard-beer-perturbation-sweep-zeml8-4-4809cd878a8a | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml8-4-4809cd878a8a.json |
| v1-8-family-standard-beer-perturbation-sweep-zeml8-4-b39172296e88 | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml8-4-b39172296e88.json |
| v1-8-family-standard-beer-perturbation-sweep-zeml8-4-2-1-fc695301052f | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml8-4-2-1-fc695301052f.json |
| v1-8-family-standard-beer-perturbation-sweep-zeml8-4-2-1-40893926f4de | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml8-4-2-1-40893926f4de.json |
| v1-8-family-standard-beer-perturbation-sweep-zeml8-4-2-1-79858f854a23 | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-standard-scoped/runs/v1.8-family-standard/v1-8-family-standard-beer-perturbation-sweep-zeml8-4-2-1-79858f854a23.json |
