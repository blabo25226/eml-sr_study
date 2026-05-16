# Benchmark Evidence: v1.5-shallow-proof

Bounded v1.5 shallow scaffolded-training proof suite with fixed proof constants and evidenced scaled-exponential depth.

## Summary

| Metric | Value |
|--------|-------|
| total | 18 |
| verifier_recovered | 18 |
| same_ast_return | 0 |
| verified_equivalent_ast | 0 |
| repaired_candidate | 0 |
| unsupported | 0 |
| failed | 0 |
| execution_error | 0 |
| verifier_recovery_rate | 1.000 |

## By Formula

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| beer_lambert | 3 | 3 | 0 | 0 | 0 | 1.000 |
| exp | 3 | 3 | 0 | 0 | 0 | 1.000 |
| log | 3 | 3 | 0 | 0 | 0 | 1.000 |
| radioactive_decay | 3 | 3 | 0 | 0 | 0 | 1.000 |
| scaled_exp_fast_decay | 3 | 3 | 0 | 0 | 0 | 1.000 |
| scaled_exp_growth | 3 | 3 | 0 | 0 | 0 | 1.000 |

## By Start Mode

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| blind | 18 | 18 | 0 | 0 | 0 | 1.000 |

## By Evidence Class

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| scaffolded_blind_training_recovered | 18 | 18 | 0 | 0 | 0 | 1.000 |

## By Return Kind

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 18 | 18 | 0 | 0 | 0 | 1.000 |

## By Raw Status

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 18 | 18 | 0 | 0 | 0 | 1.000 |

## By Repair Status

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| not_attempted | 18 | 18 | 0 | 0 | 0 | 1.000 |

## Thresholds

| Claim | Policy | Eligible | Passed | Failed | Rate | Required | Status |
|-------|--------|----------|--------|--------|------|----------|--------|
| paper-shallow-scaffolded-recovery | scaffolded_bounded_100_percent | 18 | 18 | 0 | 1.000 | 1.000 | passed |

## Runs

| Run ID | Formula | Mode | Status | Classification | Artifact |
|--------|---------|------|--------|----------------|----------|
| v1-5-shallow-proof-shallow-exp-blind-e5b022c6906d | exp | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.6/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-exp-blind-e5b022c6906d.json |
| v1-5-shallow-proof-shallow-exp-blind-6609115edbe5 | exp | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.6/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-exp-blind-6609115edbe5.json |
| v1-5-shallow-proof-shallow-exp-blind-f840e23851e0 | exp | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.6/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-exp-blind-f840e23851e0.json |
| v1-5-shallow-proof-shallow-log-blind-bace3dcddb88 | log | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.6/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-log-blind-bace3dcddb88.json |
| v1-5-shallow-proof-shallow-log-blind-28dcde6891db | log | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.6/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-log-blind-28dcde6891db.json |
| v1-5-shallow-proof-shallow-log-blind-e2bc0d0a6099 | log | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.6/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-log-blind-e2bc0d0a6099.json |
| v1-5-shallow-proof-shallow-radioactive-decay-blind-664e6bbfbc45 | radioactive_decay | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.6/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-radioactive-decay-blind-664e6bbfbc45.json |
| v1-5-shallow-proof-shallow-radioactive-decay-blind-ad04079ff0ff | radioactive_decay | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.6/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-radioactive-decay-blind-ad04079ff0ff.json |
| v1-5-shallow-proof-shallow-radioactive-decay-blind-2aea4e510ed9 | radioactive_decay | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.6/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-radioactive-decay-blind-2aea4e510ed9.json |
| v1-5-shallow-proof-shallow-beer-lambert-blind-98e77d05a5f1 | beer_lambert | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.6/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-beer-lambert-blind-98e77d05a5f1.json |
| v1-5-shallow-proof-shallow-beer-lambert-blind-5cb3e5e925cf | beer_lambert | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.6/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-beer-lambert-blind-5cb3e5e925cf.json |
| v1-5-shallow-proof-shallow-beer-lambert-blind-19bae8ae4d64 | beer_lambert | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.6/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-beer-lambert-blind-19bae8ae4d64.json |
| v1-5-shallow-proof-shallow-scaled-exp-growth-blind-23ab5fe0faf1 | scaled_exp_growth | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.6/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-scaled-exp-growth-blind-23ab5fe0faf1.json |
| v1-5-shallow-proof-shallow-scaled-exp-growth-blind-2c3b6cabfaae | scaled_exp_growth | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.6/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-scaled-exp-growth-blind-2c3b6cabfaae.json |
| v1-5-shallow-proof-shallow-scaled-exp-growth-blind-d9645da015c5 | scaled_exp_growth | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.6/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-scaled-exp-growth-blind-d9645da015c5.json |
| v1-5-shallow-proof-shallow-scaled-exp-fast-decay-blind-0fef82e2d448 | scaled_exp_fast_decay | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.6/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-scaled-exp-fast-decay-blind-0fef82e2d448.json |
| v1-5-shallow-proof-shallow-scaled-exp-fast-decay-blind-84833aade508 | scaled_exp_fast_decay | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.6/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-scaled-exp-fast-decay-blind-84833aade508.json |
| v1-5-shallow-proof-shallow-scaled-exp-fast-decay-blind-04a02d58d84b | scaled_exp_fast_decay | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.6/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-scaled-exp-fast-decay-blind-04a02d58d84b.json |
