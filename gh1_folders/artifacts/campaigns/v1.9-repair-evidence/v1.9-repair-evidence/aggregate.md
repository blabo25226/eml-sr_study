# Benchmark Evidence: v1.9-repair-evidence

Focused v1.9 near-miss before/after suite for default versus expanded verifier-gated cleanup.

## Summary

| Metric | Value |
|--------|-------|
| total | 4 |
| verifier_recovered | 0 |
| same_ast_return | 0 |
| verified_equivalent_ast | 0 |
| repaired_candidate | 0 |
| unsupported | 0 |
| failed | 4 |
| execution_error | 0 |
| verifier_recovery_rate | 0.000 |

## By Formula

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| beer_lambert | 2 | 0 | 0 | 0 | 2 | 0.000 |
| radioactive_decay | 2 | 0 | 0 | 0 | 2 | 0.000 |

## By Start Mode

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| blind | 2 | 0 | 0 | 0 | 2 | 0.000 |
| warm_start | 2 | 0 | 0 | 0 | 2 | 0.000 |

## By Evidence Class

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| snapped_but_failed | 4 | 0 | 0 | 0 | 4 | 0.000 |

## By Return Kind

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 4 | 0 | 0 | 0 | 4 | 0.000 |

## By Raw Status

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| none | 4 | 0 | 0 | 0 | 4 | 0.000 |

## By Repair Status

| Group | Total | Verifier Recovered | Same AST | Unsupported | Failed | Recovery Rate |
|-------|-------|--------------------|----------|-------------|--------|---------------|
| not_repaired | 4 | 0 | 0 | 0 | 4 | 0.000 |

## Thresholds

No proof threshold metadata.

## Runs

| Run ID | Formula | Mode | Status | Classification | Artifact |
|--------|---------|------|--------|----------------|----------|
| v1-9-repair-evidence-repair-radioactive-blind-default-1074c1beacc2 | radioactive_decay | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.9-repair-evidence/v1.9-repair-evidence/v1-9-repair-evidence-repair-radioactive-blind-default-1074c1beacc2.json |
| v1-9-repair-evidence-repair-radioactive-blind-expanded-52a3670eccfb | radioactive_decay | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.9-repair-evidence/v1.9-repair-evidence/v1-9-repair-evidence-repair-radioactive-blind-expanded-52a3670eccfb.json |
| v1-9-repair-evidence-repair-beer-warm-default-bf1ad372adab | beer_lambert | warm_start | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.9-repair-evidence/v1.9-repair-evidence/v1-9-repair-evidence-repair-beer-warm-default-bf1ad372adab.json |
| v1-9-repair-evidence-repair-beer-warm-expanded-5a37dc178e67 | beer_lambert | warm_start | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.9-repair-evidence/v1.9-repair-evidence/v1-9-repair-evidence-repair-beer-warm-expanded-5a37dc178e67.json |
