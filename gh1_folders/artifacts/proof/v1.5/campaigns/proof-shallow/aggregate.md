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
| none | 18 | 18 | 0 | 0 | 0 | 1.000 |

## Thresholds

| Claim | Policy | Eligible | Passed | Failed | Rate | Required | Status |
|-------|--------|----------|--------|--------|------|----------|--------|
| paper-shallow-scaffolded-recovery | scaffolded_bounded_100_percent | 18 | 18 | 0 | 1.000 | 1.000 | passed |

## Runs

| Run ID | Formula | Mode | Status | Classification | Artifact |
|--------|---------|------|--------|----------------|----------|
| v1-5-shallow-proof-shallow-exp-blind-cee11eed1e10 | exp | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.5/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-exp-blind-cee11eed1e10.json |
| v1-5-shallow-proof-shallow-exp-blind-3d2b2992b565 | exp | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.5/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-exp-blind-3d2b2992b565.json |
| v1-5-shallow-proof-shallow-exp-blind-09db733c882a | exp | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.5/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-exp-blind-09db733c882a.json |
| v1-5-shallow-proof-shallow-log-blind-dbe932daf1eb | log | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.5/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-log-blind-dbe932daf1eb.json |
| v1-5-shallow-proof-shallow-log-blind-df3b9fdcd927 | log | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.5/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-log-blind-df3b9fdcd927.json |
| v1-5-shallow-proof-shallow-log-blind-b1e60a866d62 | log | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.5/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-log-blind-b1e60a866d62.json |
| v1-5-shallow-proof-shallow-radioactive-decay-blind-b5dcba9ef5c4 | radioactive_decay | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.5/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-radioactive-decay-blind-b5dcba9ef5c4.json |
| v1-5-shallow-proof-shallow-radioactive-decay-blind-0fbc9f97f650 | radioactive_decay | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.5/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-radioactive-decay-blind-0fbc9f97f650.json |
| v1-5-shallow-proof-shallow-radioactive-decay-blind-cc19fce061dd | radioactive_decay | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.5/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-radioactive-decay-blind-cc19fce061dd.json |
| v1-5-shallow-proof-shallow-beer-lambert-blind-288c8a34c6fd | beer_lambert | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.5/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-beer-lambert-blind-288c8a34c6fd.json |
| v1-5-shallow-proof-shallow-beer-lambert-blind-020a842bb97c | beer_lambert | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.5/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-beer-lambert-blind-020a842bb97c.json |
| v1-5-shallow-proof-shallow-beer-lambert-blind-dbd5b90008f1 | beer_lambert | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.5/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-beer-lambert-blind-dbd5b90008f1.json |
| v1-5-shallow-proof-shallow-scaled-exp-growth-blind-909e567a513a | scaled_exp_growth | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.5/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-scaled-exp-growth-blind-909e567a513a.json |
| v1-5-shallow-proof-shallow-scaled-exp-growth-blind-46aeecb2e742 | scaled_exp_growth | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.5/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-scaled-exp-growth-blind-46aeecb2e742.json |
| v1-5-shallow-proof-shallow-scaled-exp-growth-blind-7b2cad0dbb26 | scaled_exp_growth | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.5/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-scaled-exp-growth-blind-7b2cad0dbb26.json |
| v1-5-shallow-proof-shallow-scaled-exp-fast-decay-blind-6bc7e0d8694d | scaled_exp_fast_decay | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.5/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-scaled-exp-fast-decay-blind-6bc7e0d8694d.json |
| v1-5-shallow-proof-shallow-scaled-exp-fast-decay-blind-3ad0963da6b8 | scaled_exp_fast_decay | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.5/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-scaled-exp-fast-decay-blind-3ad0963da6b8.json |
| v1-5-shallow-proof-shallow-scaled-exp-fast-decay-blind-1aa2410befb8 | scaled_exp_fast_decay | blind | recovered | scaffolded_blind_recovery | artifacts/proof/v1.5/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-scaled-exp-fast-decay-blind-1aa2410befb8.json |
