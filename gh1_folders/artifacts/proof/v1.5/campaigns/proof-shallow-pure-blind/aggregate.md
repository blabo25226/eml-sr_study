# Benchmark Evidence: v1.5-shallow-pure-blind

Measured v1.5 pure random-initialized shallow blind suite with scaffold initializers disabled.

## Summary

| Metric | Value |
|--------|-------|
| total | 18 |
| verifier_recovered | 2 |
| same_ast_return | 0 |
| verified_equivalent_ast | 0 |
| repaired_candidate | 0 |
| unsupported | 0 |
| failed | 16 |
| execution_error | 0 |
| verifier_recovery_rate | 0.111 |

## By Formula

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| beer_lambert | 3 | 0 | 0 | 0 | 3 | 0.000 |
| exp | 3 | 2 | 0 | 0 | 1 | 0.667 |
| log | 3 | 0 | 0 | 0 | 3 | 0.000 |
| radioactive_decay | 3 | 0 | 0 | 0 | 3 | 0.000 |
| scaled_exp_fast_decay | 3 | 0 | 0 | 0 | 3 | 0.000 |
| scaled_exp_growth | 3 | 0 | 0 | 0 | 3 | 0.000 |

## By Start Mode

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| blind | 18 | 2 | 0 | 0 | 16 | 0.111 |

## By Evidence Class

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| blind_training_recovered | 2 | 2 | 0 | 0 | 0 | 1.000 |
| snapped_but_failed | 16 | 0 | 0 | 0 | 16 | 0.000 |

## By Return Kind

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 18 | 2 | 0 | 0 | 16 | 0.111 |

## By Raw Status

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 18 | 2 | 0 | 0 | 16 | 0.111 |

## By Repair Status

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 18 | 2 | 0 | 0 | 16 | 0.111 |

## Thresholds

| Claim | Policy | Eligible | Passed | Failed | Rate | Required | Status |
|-------|--------|----------|--------|--------|------|----------|--------|
| paper-shallow-blind-recovery | measured_pure_blind_recovery | 18 | 2 | 16 | 0.111 |  | reported |

## Runs

| Run ID | Formula | Mode | Status | Classification | Artifact |
|--------|---------|------|--------|----------------|----------|
| v1-5-shallow-pure-blind-shallow-exp-pure-blind-33f207a0a258 | exp | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.5/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-exp-pure-blind-33f207a0a258.json |
| v1-5-shallow-pure-blind-shallow-exp-pure-blind-b54683f79f14 | exp | blind | recovered | blind_recovery | artifacts/proof/v1.5/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-exp-pure-blind-b54683f79f14.json |
| v1-5-shallow-pure-blind-shallow-exp-pure-blind-306d467800f2 | exp | blind | recovered | blind_recovery | artifacts/proof/v1.5/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-exp-pure-blind-306d467800f2.json |
| v1-5-shallow-pure-blind-shallow-log-pure-blind-5d23e0133651 | log | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.5/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-log-pure-blind-5d23e0133651.json |
| v1-5-shallow-pure-blind-shallow-log-pure-blind-c32f58c05c0c | log | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.5/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-log-pure-blind-c32f58c05c0c.json |
| v1-5-shallow-pure-blind-shallow-log-pure-blind-91b636b0e78c | log | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.5/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-log-pure-blind-91b636b0e78c.json |
| v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-d878d4416efa | radioactive_decay | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.5/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-d878d4416efa.json |
| v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-2aeaeb9d06b0 | radioactive_decay | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.5/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-2aeaeb9d06b0.json |
| v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-1ef1396484a0 | radioactive_decay | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.5/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-1ef1396484a0.json |
| v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-28a17bdc90fb | beer_lambert | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.5/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-28a17bdc90fb.json |
| v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-5e820fffc047 | beer_lambert | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.5/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-5e820fffc047.json |
| v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-1c08da9a026e | beer_lambert | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.5/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-1c08da9a026e.json |
| v1-5-shallow-pure-blind-shallow-scaled-exp-growth-pure-blind-f043889c07b4 | scaled_exp_growth | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.5/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-scaled-exp-growth-pure-blind-f043889c07b4.json |
| v1-5-shallow-pure-blind-shallow-scaled-exp-growth-pure-blind-20f4a9eea1cb | scaled_exp_growth | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.5/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-scaled-exp-growth-pure-blind-20f4a9eea1cb.json |
| v1-5-shallow-pure-blind-shallow-scaled-exp-growth-pure-blind-a37fab2a6be2 | scaled_exp_growth | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.5/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-scaled-exp-growth-pure-blind-a37fab2a6be2.json |
| v1-5-shallow-pure-blind-shallow-scaled-exp-fast-decay-pure-blind-ee6092c7c532 | scaled_exp_fast_decay | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.5/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-scaled-exp-fast-decay-pure-blind-ee6092c7c532.json |
| v1-5-shallow-pure-blind-shallow-scaled-exp-fast-decay-pure-blind-a8a19903232a | scaled_exp_fast_decay | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.5/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-scaled-exp-fast-decay-pure-blind-a8a19903232a.json |
| v1-5-shallow-pure-blind-shallow-scaled-exp-fast-decay-pure-blind-e77ad734bff7 | scaled_exp_fast_decay | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.5/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-scaled-exp-fast-decay-pure-blind-e77ad734bff7.json |
