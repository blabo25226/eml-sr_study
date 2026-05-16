# Benchmark Evidence: v1.3-showcase

Showcase v1.3 campaign matrix with expanded seeds, perturbations, and full FOR_DEMO diagnostics.

## Summary

| Metric | Value |
|--------|-------|
| total | 29 |
| verifier_recovered | 13 |
| same_ast_return | 11 |
| verified_equivalent_ast | 0 |
| unsupported | 5 |
| failed | 11 |
| execution_error | 0 |
| verifier_recovery_rate | 0.448 |

## By Formula

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| beer_lambert | 15 | 11 | 11 | 0 | 4 | 0.733 |
| damped_oscillator | 1 | 0 | 0 | 1 | 0 | 0.000 |
| exp | 3 | 2 | 0 | 0 | 1 | 0.667 |
| log | 3 | 0 | 0 | 0 | 3 | 0.000 |
| logistic | 1 | 0 | 0 | 1 | 0 | 0.000 |
| michaelis_menten | 1 | 0 | 0 | 1 | 0 | 0.000 |
| planck | 1 | 0 | 0 | 1 | 0 | 0.000 |
| radioactive_decay | 3 | 0 | 0 | 0 | 3 | 0.000 |
| shockley | 1 | 0 | 0 | 1 | 0 | 0.000 |

## By Start Mode

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| blind | 9 | 2 | 0 | 0 | 7 | 0.222 |
| compile | 4 | 0 | 0 | 4 | 0 | 0.000 |
| warm_start | 16 | 11 | 11 | 1 | 4 | 0.688 |

## Runs

| Run ID | Formula | Mode | Status | Classification | Artifact |
|--------|---------|------|--------|----------------|----------|
| v1-3-showcase-exp-blind-c693d4329a15 | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-exp-blind-c693d4329a15.json |
| v1-3-showcase-exp-blind-dcc42f2a76ee | exp | blind | recovered | blind_recovery | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-exp-blind-dcc42f2a76ee.json |
| v1-3-showcase-exp-blind-a27677c888a4 | exp | blind | recovered | blind_recovery | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-exp-blind-a27677c888a4.json |
| v1-3-showcase-log-blind-332dbad5db03 | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-log-blind-332dbad5db03.json |
| v1-3-showcase-log-blind-a52747a50ca2 | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-log-blind-a52747a50ca2.json |
| v1-3-showcase-log-blind-cf7866232845 | log | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-log-blind-cf7866232845.json |
| v1-3-showcase-radioactive-decay-blind-4a34febadef0 | radioactive_decay | blind | failed | failed | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-radioactive-decay-blind-4a34febadef0.json |
| v1-3-showcase-radioactive-decay-blind-8055ab006d29 | radioactive_decay | blind | failed | failed | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-radioactive-decay-blind-8055ab006d29.json |
| v1-3-showcase-radioactive-decay-blind-396f4bdf4078 | radioactive_decay | blind | failed | failed | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-radioactive-decay-blind-396f4bdf4078.json |
| v1-3-showcase-beer-perturbation-sweep-27c1dd807aa8 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-27c1dd807aa8.json |
| v1-3-showcase-beer-perturbation-sweep-640a60497170 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-640a60497170.json |
| v1-3-showcase-beer-perturbation-sweep-a9cf9a640769 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-a9cf9a640769.json |
| v1-3-showcase-beer-perturbation-sweep-b9d747ebc959 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-b9d747ebc959.json |
| v1-3-showcase-beer-perturbation-sweep-6ffb162a5bb7 | beer_lambert | warm_start | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-6ffb162a5bb7.json |
| v1-3-showcase-beer-perturbation-sweep-186003aebe9f | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-186003aebe9f.json |
| v1-3-showcase-beer-perturbation-sweep-098bf41383ad | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-098bf41383ad.json |
| v1-3-showcase-beer-perturbation-sweep-d6cf949e5337 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-d6cf949e5337.json |
| v1-3-showcase-beer-perturbation-sweep-89c991bee41e | beer_lambert | warm_start | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-89c991bee41e.json |
| v1-3-showcase-beer-perturbation-sweep-8615aab30e44 | beer_lambert | warm_start | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-8615aab30e44.json |
| v1-3-showcase-beer-perturbation-sweep-75c7f17caa7d | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-75c7f17caa7d.json |
| v1-3-showcase-beer-perturbation-sweep-5de5751a8845 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-5de5751a8845.json |
| v1-3-showcase-beer-perturbation-sweep-0b418b8b99d9 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-0b418b8b99d9.json |
| v1-3-showcase-beer-perturbation-sweep-5eab2a4656c1 | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-5eab2a4656c1.json |
| v1-3-showcase-beer-perturbation-sweep-05cb8f1ed422 | beer_lambert | warm_start | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-05cb8f1ed422.json |
| v1-3-showcase-michaelis-warm-diagnostic-8f1f8084d61b | michaelis_menten | warm_start | unsupported | unsupported | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-michaelis-warm-diagnostic-8f1f8084d61b.json |
| v1-3-showcase-logistic-compile-5a739cf1c01f | logistic | compile | unsupported | unsupported | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-logistic-compile-5a739cf1c01f.json |
| v1-3-showcase-shockley-compile-0119659ca5dd | shockley | compile | unsupported | unsupported | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-shockley-compile-0119659ca5dd.json |
| v1-3-showcase-damped-oscillator-compile-9b393796ada0 | damped_oscillator | compile | unsupported | unsupported | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-damped-oscillator-compile-9b393796ada0.json |
| v1-3-showcase-planck-diagnostic-1ba93a0c5966 | planck | compile | unsupported | unsupported | artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-planck-diagnostic-1ba93a0c5966.json |
