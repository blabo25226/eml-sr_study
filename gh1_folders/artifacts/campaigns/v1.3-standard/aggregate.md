# Benchmark Evidence: v1.3-standard

Standard v1.3 campaign matrix with shallow blind baselines, perturbation sweeps, and FOR_DEMO diagnostics.

## Summary

| Metric | Value |
|--------|-------|
| total | 16 |
| verifier_recovered | 5 |
| same_ast_return | 4 |
| verified_equivalent_ast | 0 |
| unsupported | 4 |
| failed | 7 |
| execution_error | 0 |
| verifier_recovery_rate | 0.312 |

## By Formula

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| beer_lambert | 6 | 4 | 4 | 0 | 2 | 0.667 |
| exp | 2 | 1 | 0 | 0 | 1 | 0.500 |
| log | 2 | 0 | 0 | 0 | 2 | 0.000 |
| logistic | 1 | 0 | 0 | 1 | 0 | 0.000 |
| michaelis_menten | 1 | 0 | 0 | 1 | 0 | 0.000 |
| planck | 1 | 0 | 0 | 1 | 0 | 0.000 |
| radioactive_decay | 2 | 0 | 0 | 0 | 2 | 0.000 |
| shockley | 1 | 0 | 0 | 1 | 0 | 0.000 |

## By Start Mode

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| blind | 6 | 1 | 0 | 0 | 5 | 0.167 |
| compile | 3 | 0 | 0 | 3 | 0 | 0.000 |
| warm_start | 7 | 4 | 4 | 1 | 2 | 0.571 |

## Runs

| Run ID | Formula | Mode | Status | Classification | Artifact |
|--------|---------|------|--------|----------------|----------|
| v1-3-standard-exp-blind-a5022d6098c7 | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.3-standard/runs/v1.3-standard/v1-3-standard-exp-blind-a5022d6098c7.json |
| v1-3-standard-exp-blind-f5720b502dfe | exp | blind | recovered | blind_recovery | artifacts/campaigns/v1.3-standard/runs/v1.3-standard/v1-3-standard-exp-blind-f5720b502dfe.json |
| v1-3-standard-log-blind-194180dc5df0 | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.3-standard/runs/v1.3-standard/v1-3-standard-log-blind-194180dc5df0.json |
| v1-3-standard-log-blind-99aa5ff393ee | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.3-standard/runs/v1.3-standard/v1-3-standard-log-blind-99aa5ff393ee.json |
| v1-3-standard-radioactive-decay-blind-20f83222d0db | radioactive_decay | blind | failed | failed | artifacts/campaigns/v1.3-standard/runs/v1.3-standard/v1-3-standard-radioactive-decay-blind-20f83222d0db.json |
| v1-3-standard-radioactive-decay-blind-83660c5b4b25 | radioactive_decay | blind | failed | failed | artifacts/campaigns/v1.3-standard/runs/v1.3-standard/v1-3-standard-radioactive-decay-blind-83660c5b4b25.json |
| v1-3-standard-beer-perturbation-sweep-583f8b4d1958 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.3-standard/runs/v1.3-standard/v1-3-standard-beer-perturbation-sweep-583f8b4d1958.json |
| v1-3-standard-beer-perturbation-sweep-1fd0469252df | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.3-standard/runs/v1.3-standard/v1-3-standard-beer-perturbation-sweep-1fd0469252df.json |
| v1-3-standard-beer-perturbation-sweep-348eebff7ed4 | beer_lambert | warm_start | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.3-standard/runs/v1.3-standard/v1-3-standard-beer-perturbation-sweep-348eebff7ed4.json |
| v1-3-standard-beer-perturbation-sweep-30add2b53d7d | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.3-standard/runs/v1.3-standard/v1-3-standard-beer-perturbation-sweep-30add2b53d7d.json |
| v1-3-standard-beer-perturbation-sweep-3538303249fd | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.3-standard/runs/v1.3-standard/v1-3-standard-beer-perturbation-sweep-3538303249fd.json |
| v1-3-standard-beer-perturbation-sweep-68c818aed370 | beer_lambert | warm_start | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.3-standard/runs/v1.3-standard/v1-3-standard-beer-perturbation-sweep-68c818aed370.json |
| v1-3-standard-michaelis-warm-diagnostic-37a57673a2e2 | michaelis_menten | warm_start | unsupported | unsupported | artifacts/campaigns/v1.3-standard/runs/v1.3-standard/v1-3-standard-michaelis-warm-diagnostic-37a57673a2e2.json |
| v1-3-standard-logistic-compile-820d90103856 | logistic | compile | unsupported | unsupported | artifacts/campaigns/v1.3-standard/runs/v1.3-standard/v1-3-standard-logistic-compile-820d90103856.json |
| v1-3-standard-shockley-compile-e410a7c053d4 | shockley | compile | unsupported | unsupported | artifacts/campaigns/v1.3-standard/runs/v1.3-standard/v1-3-standard-shockley-compile-e410a7c053d4.json |
| v1-3-standard-planck-diagnostic-837e17c92c48 | planck | compile | unsupported | unsupported | artifacts/campaigns/v1.3-standard/runs/v1.3-standard/v1-3-standard-planck-diagnostic-837e17c92c48.json |
