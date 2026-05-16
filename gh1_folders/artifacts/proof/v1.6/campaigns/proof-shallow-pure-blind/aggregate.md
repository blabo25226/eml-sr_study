# Benchmark Evidence: v1.5-shallow-pure-blind

Measured v1.5 pure random-initialized shallow blind suite with scaffold initializers disabled.

## Summary

| Metric | Value |
|--------|-------|
| total | 18 |
| verifier_recovered | 3 |
| same_ast_return | 0 |
| verified_equivalent_ast | 0 |
| repaired_candidate | 1 |
| unsupported | 0 |
| failed | 15 |
| execution_error | 0 |
| verifier_recovery_rate | 0.167 |

## By Formula

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| beer_lambert | 3 | 0 | 0 | 0 | 3 | 0.000 |
| exp | 3 | 3 | 0 | 0 | 0 | 1.000 |
| log | 3 | 0 | 0 | 0 | 3 | 0.000 |
| radioactive_decay | 3 | 0 | 0 | 0 | 3 | 0.000 |
| scaled_exp_fast_decay | 3 | 0 | 0 | 0 | 3 | 0.000 |
| scaled_exp_growth | 3 | 0 | 0 | 0 | 3 | 0.000 |

## By Start Mode

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| blind | 18 | 3 | 0 | 0 | 15 | 0.167 |

## By Evidence Class

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| blind_training_recovered | 2 | 2 | 0 | 0 | 0 | 1.000 |
| failed | 1 | 0 | 0 | 0 | 1 | 0.000 |
| repaired_candidate | 1 | 1 | 0 | 0 | 0 | 1.000 |
| snapped_but_failed | 14 | 0 | 0 | 0 | 14 | 0.000 |

## By Return Kind

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 18 | 3 | 0 | 0 | 15 | 0.167 |

## By Raw Status

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 18 | 3 | 0 | 0 | 15 | 0.167 |

## By Repair Status

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| not_attempted | 2 | 2 | 0 | 0 | 0 | 1.000 |
| not_repaired | 15 | 0 | 0 | 0 | 15 | 0.000 |
| repaired | 1 | 1 | 0 | 0 | 0 | 1.000 |

## Thresholds

| Claim | Policy | Eligible | Passed | Failed | Rate | Required | Status |
|-------|--------|----------|--------|--------|------|----------|--------|
| paper-shallow-blind-recovery | measured_pure_blind_recovery | 18 | 2 | 16 | 0.111 |  | reported |

## Runs

| Run ID | Formula | Mode | Status | Classification | Artifact |
|--------|---------|------|--------|----------------|----------|
| v1-5-shallow-pure-blind-shallow-exp-pure-blind-38ff2b4c6e37 | exp | blind | repaired_candidate | repaired_candidate | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-exp-pure-blind-38ff2b4c6e37.json |
| v1-5-shallow-pure-blind-shallow-exp-pure-blind-47735df30507 | exp | blind | recovered | blind_recovery | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-exp-pure-blind-47735df30507.json |
| v1-5-shallow-pure-blind-shallow-exp-pure-blind-1325a323dee1 | exp | blind | recovered | blind_recovery | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-exp-pure-blind-1325a323dee1.json |
| v1-5-shallow-pure-blind-shallow-log-pure-blind-9f03a09a571f | log | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-log-pure-blind-9f03a09a571f.json |
| v1-5-shallow-pure-blind-shallow-log-pure-blind-3941715f3d32 | log | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-log-pure-blind-3941715f3d32.json |
| v1-5-shallow-pure-blind-shallow-log-pure-blind-03a03c8b35da | log | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-log-pure-blind-03a03c8b35da.json |
| v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-b8c2dbde649d | radioactive_decay | blind | failed | failed | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-b8c2dbde649d.json |
| v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-03920c466c9d | radioactive_decay | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-03920c466c9d.json |
| v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-a48b19cb28a2 | radioactive_decay | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-a48b19cb28a2.json |
| v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-d4b6b4704428 | beer_lambert | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-d4b6b4704428.json |
| v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-8599744dc0b5 | beer_lambert | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-8599744dc0b5.json |
| v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-4908b626f452 | beer_lambert | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-4908b626f452.json |
| v1-5-shallow-pure-blind-shallow-scaled-exp-growth-pure-blind-9f934ff0ec8a | scaled_exp_growth | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-scaled-exp-growth-pure-blind-9f934ff0ec8a.json |
| v1-5-shallow-pure-blind-shallow-scaled-exp-growth-pure-blind-33355177daa0 | scaled_exp_growth | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-scaled-exp-growth-pure-blind-33355177daa0.json |
| v1-5-shallow-pure-blind-shallow-scaled-exp-growth-pure-blind-a546d2037d2d | scaled_exp_growth | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-scaled-exp-growth-pure-blind-a546d2037d2d.json |
| v1-5-shallow-pure-blind-shallow-scaled-exp-fast-decay-pure-blind-ac77563226c3 | scaled_exp_fast_decay | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-scaled-exp-fast-decay-pure-blind-ac77563226c3.json |
| v1-5-shallow-pure-blind-shallow-scaled-exp-fast-decay-pure-blind-367714cb8a2b | scaled_exp_fast_decay | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-scaled-exp-fast-decay-pure-blind-367714cb8a2b.json |
| v1-5-shallow-pure-blind-shallow-scaled-exp-fast-decay-pure-blind-a33822512a4d | scaled_exp_fast_decay | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-scaled-exp-fast-decay-pure-blind-a33822512a4d.json |
