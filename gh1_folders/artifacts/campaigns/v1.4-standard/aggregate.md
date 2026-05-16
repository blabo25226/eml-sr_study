# Benchmark Evidence: v1.3-standard

Standard v1.3 campaign matrix with shallow blind baselines, perturbation sweeps, and FOR_DEMO diagnostics.

## Summary

| Metric | Value |
|--------|-------|
| total | 16 |
| verifier_recovered | 9 |
| same_ast_return | 4 |
| verified_equivalent_ast | 0 |
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
| shockley | 1 | 1 | 0 | 0 | 0 | 1.000 |

## By Start Mode

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| blind | 6 | 4 | 0 | 0 | 2 | 0.667 |
| compile | 3 | 1 | 0 | 2 | 0 | 0.333 |
| warm_start | 7 | 4 | 4 | 1 | 2 | 0.571 |

## Runs

| Run ID | Formula | Mode | Status | Classification | Artifact |
|--------|---------|------|--------|----------------|----------|
| v1-3-standard-exp-blind-4e3c68a43de2 | exp | blind | recovered | blind_recovery | artifacts/campaigns/v1.4-standard/runs/v1.3-standard/v1-3-standard-exp-blind-4e3c68a43de2.json |
| v1-3-standard-exp-blind-645cada9ed62 | exp | blind | recovered | blind_recovery | artifacts/campaigns/v1.4-standard/runs/v1.3-standard/v1-3-standard-exp-blind-645cada9ed62.json |
| v1-3-standard-log-blind-72524a72595b | log | blind | recovered | blind_recovery | artifacts/campaigns/v1.4-standard/runs/v1.3-standard/v1-3-standard-log-blind-72524a72595b.json |
| v1-3-standard-log-blind-a396abda487c | log | blind | recovered | blind_recovery | artifacts/campaigns/v1.4-standard/runs/v1.3-standard/v1-3-standard-log-blind-a396abda487c.json |
| v1-3-standard-radioactive-decay-blind-a5182baf92cb | radioactive_decay | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.4-standard/runs/v1.3-standard/v1-3-standard-radioactive-decay-blind-a5182baf92cb.json |
| v1-3-standard-radioactive-decay-blind-72661a29e7af | radioactive_decay | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.4-standard/runs/v1.3-standard/v1-3-standard-radioactive-decay-blind-72661a29e7af.json |
| v1-3-standard-beer-perturbation-sweep-299ba6273bd5 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.4-standard/runs/v1.3-standard/v1-3-standard-beer-perturbation-sweep-299ba6273bd5.json |
| v1-3-standard-beer-perturbation-sweep-d713bde30e74 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.4-standard/runs/v1.3-standard/v1-3-standard-beer-perturbation-sweep-d713bde30e74.json |
| v1-3-standard-beer-perturbation-sweep-10022388db85 | beer_lambert | warm_start | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.4-standard/runs/v1.3-standard/v1-3-standard-beer-perturbation-sweep-10022388db85.json |
| v1-3-standard-beer-perturbation-sweep-908c2afdce7f | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.4-standard/runs/v1.3-standard/v1-3-standard-beer-perturbation-sweep-908c2afdce7f.json |
| v1-3-standard-beer-perturbation-sweep-7eb18fd67b2d | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.4-standard/runs/v1.3-standard/v1-3-standard-beer-perturbation-sweep-7eb18fd67b2d.json |
| v1-3-standard-beer-perturbation-sweep-0d444d18be54 | beer_lambert | warm_start | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.4-standard/runs/v1.3-standard/v1-3-standard-beer-perturbation-sweep-0d444d18be54.json |
| v1-3-standard-michaelis-warm-diagnostic-b09b1e8360d8 | michaelis_menten | warm_start | unsupported | unsupported | artifacts/campaigns/v1.4-standard/runs/v1.3-standard/v1-3-standard-michaelis-warm-diagnostic-b09b1e8360d8.json |
| v1-3-standard-logistic-compile-b4c8b70a68a0 | logistic | compile | unsupported | unsupported | artifacts/campaigns/v1.4-standard/runs/v1.3-standard/v1-3-standard-logistic-compile-b4c8b70a68a0.json |
| v1-3-standard-shockley-compile-18bebde5cc6f | shockley | compile | recovered | verifier_recovered | artifacts/campaigns/v1.4-standard/runs/v1.3-standard/v1-3-standard-shockley-compile-18bebde5cc6f.json |
| v1-3-standard-planck-diagnostic-2f4e5cf78436 | planck | compile | unsupported | unsupported | artifacts/campaigns/v1.4-standard/runs/v1.3-standard/v1-3-standard-planck-diagnostic-2f4e5cf78436.json |
