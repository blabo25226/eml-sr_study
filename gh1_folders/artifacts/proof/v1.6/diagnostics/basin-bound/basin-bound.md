# Perturbed Basin Bound Report

- Formula: `beer_lambert`
- Declared noise grid: 5, 15, 35
- Declared bounded proof max: 5
- Raw supported max: 5
- Repaired supported max: 35
- Claim recommendation: `probe_supports_35`
- Expected seed/noise rows: 6
- Missing seed/noise rows: 0

High-noise probe rows remain separate from bounded proof thresholds. Probe evidence can support a follow-up bound only when it forms a continuous declared-grid prefix.

## Rows

| Source | Suite | Case | Run | Seed | Noise | Status | Claim | Evidence | Return Kind | Raw Status | Repair Status | Changed Slots | Accepted Repair Moves | Reason | Artifact | Artifact SHA256 |
|--------|-------|------|-----|------|-------|--------|-------|----------|-------------|------------|---------------|---------------|-----------------------|--------|----------|----------|
| bounded | proof-perturbed-basin | basin-beer-lambert-bound | proof-perturbed-basin-basin-beer-lambert-bound-0a5e00e13e43 | 0 | 5 | recovered | recovered | perturbed_true_tree_recovered | same_ast_return | recovered | not_attempted | 0 | 0 | verified | artifacts/proof/v1.6/campaigns/proof-basin/runs/proof-perturbed-basin/proof-perturbed-basin-basin-beer-lambert-bound-0a5e00e13e43.json | 89ae7fe16125ec1b4cfe343c3ecc4a85c654e7bad17718f37da23fabcd4aca06 |
| bounded | proof-perturbed-basin | basin-beer-lambert-bound | proof-perturbed-basin-basin-beer-lambert-bound-627e93d6dc9d | 1 | 5 | recovered | recovered | perturbed_true_tree_recovered | same_ast_return | recovered | not_attempted | 0 | 0 | verified | artifacts/proof/v1.6/campaigns/proof-basin/runs/proof-perturbed-basin/proof-perturbed-basin-basin-beer-lambert-bound-627e93d6dc9d.json | 1ab5d47fa1ff329b5555024cd18242e9e334123f33cd47ce17e5c70aac0f13c8 |
| probe | proof-perturbed-basin-beer-probes | basin-beer-lambert-bound-probes | proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-2d877a2bc9fc | 0 | 15 | recovered | recovered | perturbed_true_tree_recovered | same_ast_return | recovered | not_attempted | 0 | 0 | verified | artifacts/proof/v1.6/campaigns/proof-basin-probes/runs/proof-perturbed-basin-beer-probes/proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-2d877a2bc9fc.json | 5715c3a585fd2d522fb46229b5599500402398b40ff270753b6cf063def5cfe5 |
| probe | proof-perturbed-basin-beer-probes | basin-beer-lambert-bound-probes | proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-752352286603 | 1 | 15 | repaired_candidate | recovered | repaired_candidate | snapped_but_failed | snapped_but_failed | repaired | 1 | 1 | train_failed | artifacts/proof/v1.6/campaigns/proof-basin-probes/runs/proof-perturbed-basin-beer-probes/proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-752352286603.json | f50016d2197849e409fd8801201c0e3f6f2d0284b9793f0dc1423640b2e90276 |
| probe | proof-perturbed-basin-beer-probes | basin-beer-lambert-bound-probes | proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-e17e44438210 | 0 | 35 | repaired_candidate | recovered | repaired_candidate | snapped_but_failed | snapped_but_failed | repaired | 5 | 6 | train_failed | artifacts/proof/v1.6/campaigns/proof-basin-probes/runs/proof-perturbed-basin-beer-probes/proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-e17e44438210.json | 5088a033b7b9900e64f147e80defa76295e44f5b993fdec1eb6f1fd1e063fbb5 |
| probe | proof-perturbed-basin-beer-probes | basin-beer-lambert-bound-probes | proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-99306eda3f85 | 1 | 35 | repaired_candidate | recovered | repaired_candidate | snapped_but_failed | snapped_but_failed | repaired | 3 | 1 | train_failed | artifacts/proof/v1.6/campaigns/proof-basin-probes/runs/proof-perturbed-basin-beer-probes/proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-99306eda3f85.json | 52261c08df1a03fc89fc0624a967df3adc6f7fc1fcbd5dc118cda6109470a90e |
