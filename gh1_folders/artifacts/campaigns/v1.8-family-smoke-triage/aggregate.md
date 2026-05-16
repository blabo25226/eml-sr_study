# Benchmark Evidence: v1.8-family-smoke

CI-scale v1.8 raw-vs-centered operator-family smoke matrix with expanded fixed scales and schedules.

## Summary

| Metric | Value |
|--------|-------|
| total | 33 |
| verifier_recovered | 2 |
| same_ast_return | 1 |
| verified_equivalent_ast | 0 |
| repaired_candidate | 0 |
| unsupported | 21 |
| failed | 10 |
| execution_error | 0 |
| verifier_recovery_rate | 0.061 |

## By Formula

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| beer_lambert | 11 | 1 | 1 | 10 | 0 | 0.091 |
| exp | 11 | 1 | 0 | 0 | 10 | 0.091 |
| planck | 11 | 0 | 0 | 11 | 0 | 0.000 |

## By Start Mode

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| blind | 11 | 1 | 0 | 0 | 10 | 0.091 |
| compile | 11 | 0 | 0 | 11 | 0 | 0.000 |
| warm_start | 11 | 1 | 1 | 10 | 0 | 0.091 |

## By Evidence Class

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| same_ast | 1 | 1 | 1 | 0 | 0 | 1.000 |
| scaffolded_blind_training_recovered | 1 | 1 | 0 | 0 | 0 | 1.000 |
| snapped_but_failed | 10 | 0 | 0 | 0 | 10 | 0.000 |
| unsupported | 21 | 0 | 0 | 21 | 0 | 0.000 |

## By Return Kind

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 33 | 2 | 1 | 21 | 10 | 0.061 |

## By Raw Status

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 33 | 2 | 1 | 21 | 10 | 0.061 |

## By Repair Status

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 21 | 0 | 0 | 21 | 0 | 0.000 |
| not_attempted | 2 | 2 | 1 | 0 | 0 | 1.000 |
| not_repaired | 10 | 0 | 0 | 0 | 10 | 0.000 |

## Thresholds

No proof threshold metadata.

## Runs

| Run ID | Formula | Mode | Status | Classification | Artifact |
|--------|---------|------|--------|----------------|----------|
| v1-8-family-smoke-exp-blind-raw-0e8e3a02d2a9 | exp | blind | recovered | scaffolded_blind_recovery | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-exp-blind-raw-0e8e3a02d2a9.json |
| v1-8-family-smoke-exp-blind-ceml1-6f5f824f0a5a | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-exp-blind-ceml1-6f5f824f0a5a.json |
| v1-8-family-smoke-exp-blind-zeml1-317104765e0b | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-exp-blind-zeml1-317104765e0b.json |
| v1-8-family-smoke-exp-blind-ceml2-90ba09a5dd4a | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-exp-blind-ceml2-90ba09a5dd4a.json |
| v1-8-family-smoke-exp-blind-zeml2-a372af7f93e7 | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-exp-blind-zeml2-a372af7f93e7.json |
| v1-8-family-smoke-exp-blind-ceml4-dd30620a15a6 | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-exp-blind-ceml4-dd30620a15a6.json |
| v1-8-family-smoke-exp-blind-zeml4-bba5d8a1daa3 | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-exp-blind-zeml4-bba5d8a1daa3.json |
| v1-8-family-smoke-exp-blind-ceml8-23631eb6c4f1 | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-exp-blind-ceml8-23631eb6c4f1.json |
| v1-8-family-smoke-exp-blind-zeml8-fef4c45fa8c1 | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-exp-blind-zeml8-fef4c45fa8c1.json |
| v1-8-family-smoke-exp-blind-zeml8-4-d17ddd5caa2c | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-exp-blind-zeml8-4-d17ddd5caa2c.json |
| v1-8-family-smoke-exp-blind-zeml8-4-2-1-2d6854735245 | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-exp-blind-zeml8-4-2-1-2d6854735245.json |
| v1-8-family-smoke-beer-warm-raw-ca4657fc89fe | beer_lambert | warm_start | same_ast_return | same_ast_warm_start_return | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-beer-warm-raw-ca4657fc89fe.json |
| v1-8-family-smoke-beer-warm-ceml1-c34e4399439f | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-beer-warm-ceml1-c34e4399439f.json |
| v1-8-family-smoke-beer-warm-zeml1-28da08b4b6cf | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-beer-warm-zeml1-28da08b4b6cf.json |
| v1-8-family-smoke-beer-warm-ceml2-e6701dba96c1 | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-beer-warm-ceml2-e6701dba96c1.json |
| v1-8-family-smoke-beer-warm-zeml2-476861cccd0c | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-beer-warm-zeml2-476861cccd0c.json |
| v1-8-family-smoke-beer-warm-ceml4-fc67fb681b02 | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-beer-warm-ceml4-fc67fb681b02.json |
| v1-8-family-smoke-beer-warm-zeml4-6a949990d9ee | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-beer-warm-zeml4-6a949990d9ee.json |
| v1-8-family-smoke-beer-warm-ceml8-2fc8b32444e2 | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-beer-warm-ceml8-2fc8b32444e2.json |
| v1-8-family-smoke-beer-warm-zeml8-ec67179bb78c | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-beer-warm-zeml8-ec67179bb78c.json |
| v1-8-family-smoke-beer-warm-zeml8-4-81f368278d4c | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-beer-warm-zeml8-4-81f368278d4c.json |
| v1-8-family-smoke-beer-warm-zeml8-4-2-1-fe2502914c5b | beer_lambert | warm_start | unsupported | unsupported | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-beer-warm-zeml8-4-2-1-fe2502914c5b.json |
| v1-8-family-smoke-planck-diagnostic-raw-8ee86832d8a7 | planck | compile | unsupported | unsupported | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-planck-diagnostic-raw-8ee86832d8a7.json |
| v1-8-family-smoke-planck-diagnostic-ceml1-38ded6f58ca3 | planck | compile | unsupported | unsupported | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-planck-diagnostic-ceml1-38ded6f58ca3.json |
| v1-8-family-smoke-planck-diagnostic-zeml1-caaa73ea632b | planck | compile | unsupported | unsupported | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-planck-diagnostic-zeml1-caaa73ea632b.json |
| v1-8-family-smoke-planck-diagnostic-ceml2-a4ce0774fc16 | planck | compile | unsupported | unsupported | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-planck-diagnostic-ceml2-a4ce0774fc16.json |
| v1-8-family-smoke-planck-diagnostic-zeml2-595426850711 | planck | compile | unsupported | unsupported | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-planck-diagnostic-zeml2-595426850711.json |
| v1-8-family-smoke-planck-diagnostic-ceml4-a28b07a2fac8 | planck | compile | unsupported | unsupported | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-planck-diagnostic-ceml4-a28b07a2fac8.json |
| v1-8-family-smoke-planck-diagnostic-zeml4-9b85fe53e8ca | planck | compile | unsupported | unsupported | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-planck-diagnostic-zeml4-9b85fe53e8ca.json |
| v1-8-family-smoke-planck-diagnostic-ceml8-4eace4f6f021 | planck | compile | unsupported | unsupported | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-planck-diagnostic-ceml8-4eace4f6f021.json |
| v1-8-family-smoke-planck-diagnostic-zeml8-03bcb971710c | planck | compile | unsupported | unsupported | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-planck-diagnostic-zeml8-03bcb971710c.json |
| v1-8-family-smoke-planck-diagnostic-zeml8-4-df0ff05244cc | planck | compile | unsupported | unsupported | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-planck-diagnostic-zeml8-4-df0ff05244cc.json |
| v1-8-family-smoke-planck-diagnostic-zeml8-4-2-1-7751e6ca8d8a | planck | compile | unsupported | unsupported | artifacts/campaigns/v1.8-family-smoke-triage/runs/v1.8-family-smoke/v1-8-family-smoke-planck-diagnostic-zeml8-4-2-1-7751e6ca8d8a.json |
