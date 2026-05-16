# Repair Evidence Summary: v1.9-repair-evidence

Focused before/after evidence for default selected-only cleanup versus expanded candidate-pool cleanup.

## Outcome

- Pair count: 2
- Default repaired count: 0
- Expanded repaired count: 0
- Expanded improvements over paired default: 0
- Regressions in final status: 0
- Missing repair metadata cases: 0
- Fallback manifests preserved for all runs: true

Expanded candidate-pool cleanup produced no measured repair improvement over paired default cleanup; all paired runs stayed snapped_but_failed/not_repaired while selected and fallback optimizer manifests remained preserved.

This suite is focused repair evidence only. Repaired candidates, if any, are repaired_candidate evidence; they are not blind discovery, same-AST warm-start recovery, compile-only evidence, or perturbed true-tree recovery.

## Sources

- Suite result: `artifacts/campaigns/v1.9-repair-evidence/v1.9-repair-evidence/suite-result.json`
- Aggregate JSON: `artifacts/campaigns/v1.9-repair-evidence/v1.9-repair-evidence/aggregate.json`
- Aggregate Markdown: `artifacts/campaigns/v1.9-repair-evidence/v1.9-repair-evidence/aggregate.md`

## Paired Runs

| Formula | Mode | Noise | Default Status | Expanded Status | Default Repair | Expanded Repair | Roots Default -> Expanded | Deduped Variants Default -> Expanded | Fallback Manifests |
|---------|------|-------|----------------|-----------------|----------------|-----------------|---------------------------|--------------------------------------|--------------------|
| beer_lambert | warm_start | 35.0 | snapped_but_failed | snapped_but_failed | not_repaired | not_repaired | 1 -> 1 | 24 -> 88 | preserved |
| radioactive_decay | blind | 0.0 | snapped_but_failed | snapped_but_failed | not_repaired | not_repaired | 1 -> 3 | 24 -> 156 | preserved |

## Run Artifacts

| Case | Preset | Run ID | Artifact |
|------|--------|--------|----------|
| repair-beer-warm-default | selected_only | v1-9-repair-evidence-repair-beer-warm-default-bf1ad372adab | `artifacts/campaigns/v1.9-repair-evidence/v1.9-repair-evidence/v1-9-repair-evidence-repair-beer-warm-default-bf1ad372adab.json` |
| repair-beer-warm-expanded | expanded_candidate_pool | v1-9-repair-evidence-repair-beer-warm-expanded-5a37dc178e67 | `artifacts/campaigns/v1.9-repair-evidence/v1.9-repair-evidence/v1-9-repair-evidence-repair-beer-warm-expanded-5a37dc178e67.json` |
| repair-radioactive-blind-default | selected_only | v1-9-repair-evidence-repair-radioactive-blind-default-1074c1beacc2 | `artifacts/campaigns/v1.9-repair-evidence/v1.9-repair-evidence/v1-9-repair-evidence-repair-radioactive-blind-default-1074c1beacc2.json` |
| repair-radioactive-blind-expanded | expanded_candidate_pool | v1-9-repair-evidence-repair-radioactive-blind-expanded-52a3670eccfb | `artifacts/campaigns/v1.9-repair-evidence/v1.9-repair-evidence/v1-9-repair-evidence-repair-radioactive-blind-expanded-52a3670eccfb.json` |
