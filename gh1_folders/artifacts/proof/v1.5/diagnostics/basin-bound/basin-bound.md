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
| bounded | proof-perturbed-basin | basin-beer-lambert-bound | proof-perturbed-basin-basin-beer-lambert-bound-6d5706dd5485 | 0 | 5 | recovered | recovered | perturbed_true_tree_recovered | same_ast_return | recovered | not_attempted | 0 | 0 | verified | artifacts/proof/v1.5/campaigns/proof-basin/runs/proof-perturbed-basin/proof-perturbed-basin-basin-beer-lambert-bound-6d5706dd5485.json | 5d1629b052a46b12fc2e98bd441d60c3537dcf0e25d681224fe8cc22fc278294 |
| bounded | proof-perturbed-basin | basin-beer-lambert-bound | proof-perturbed-basin-basin-beer-lambert-bound-d817ff8c67cb | 1 | 5 | recovered | recovered | perturbed_true_tree_recovered | same_ast_return | recovered | not_attempted | 0 | 0 | verified | artifacts/proof/v1.5/campaigns/proof-basin/runs/proof-perturbed-basin/proof-perturbed-basin-basin-beer-lambert-bound-d817ff8c67cb.json | 395dbb69b96971360b23232b27cc55868f7aaaa04a246c2e13a5c847053c82c2 |
| probe | proof-perturbed-basin-beer-probes | basin-beer-lambert-bound-probes | proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-5cf0e6c92e03 | 0 | 15 | recovered | recovered | perturbed_true_tree_recovered | same_ast_return | recovered | not_attempted | 0 | 0 | verified | artifacts/proof/v1.5/campaigns/proof-basin-probes/runs/proof-perturbed-basin-beer-probes/proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-5cf0e6c92e03.json | 1b380e25299ae41b60bd352257c10846be88339ae0bc76a7edc6709706c716f7 |
| probe | proof-perturbed-basin-beer-probes | basin-beer-lambert-bound-probes | proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-ad931dbdc4c2 | 1 | 15 | repaired_candidate | recovered | repaired_candidate | snapped_but_failed | snapped_but_failed | repaired | 1 | 1 | mpmath_failed | artifacts/proof/v1.5/campaigns/proof-basin-probes/runs/proof-perturbed-basin-beer-probes/proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-ad931dbdc4c2.json | 95e2c01050454f9fc6f39f321d3c6c18f5e9a58b2b7634b0c637eb556ea1b058 |
| probe | proof-perturbed-basin-beer-probes | basin-beer-lambert-bound-probes | proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-6a284155128b | 0 | 35 | repaired_candidate | recovered | repaired_candidate | snapped_but_failed | snapped_but_failed | repaired | 5 | 6 | mpmath_failed | artifacts/proof/v1.5/campaigns/proof-basin-probes/runs/proof-perturbed-basin-beer-probes/proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-6a284155128b.json | b48d50a36125f1f0705435d3650ff534a392c3498567078409e88c836069559e |
| probe | proof-perturbed-basin-beer-probes | basin-beer-lambert-bound-probes | proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-dc2f5b284504 | 1 | 35 | repaired_candidate | recovered | repaired_candidate | snapped_but_failed | snapped_but_failed | repaired | 3 | 1 | mpmath_failed | artifacts/proof/v1.5/campaigns/proof-basin-probes/runs/proof-perturbed-basin-beer-probes/proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-dc2f5b284504.json | b2b306e2677c48a0f587b3ce3d9deda7388c1c5c549b690e5dea2297d246c717 |
