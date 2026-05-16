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
| bounded | proof-perturbed-basin | basin-beer-lambert-bound | proof-perturbed-basin-basin-beer-lambert-bound-f716bb6f9e3e | 0 | 5 | recovered | recovered | perturbed_true_tree_recovered | same_ast_return | recovered | not_attempted | 0 | 0 | verified | artifacts/diagnostics/phase31-basin-bound/raw-runs/bounded/proof-perturbed-basin/proof-perturbed-basin-basin-beer-lambert-bound-f716bb6f9e3e.json | dcb889b8ade73171a5a6faa7e112ee370f12663a46f13027480dc6a88c2c723b |
| bounded | proof-perturbed-basin | basin-beer-lambert-bound | proof-perturbed-basin-basin-beer-lambert-bound-88212187883e | 1 | 5 | recovered | recovered | perturbed_true_tree_recovered | same_ast_return | recovered | not_attempted | 0 | 0 | verified | artifacts/diagnostics/phase31-basin-bound/raw-runs/bounded/proof-perturbed-basin/proof-perturbed-basin-basin-beer-lambert-bound-88212187883e.json | 0797cd0224433a836089445594da8fd8d62072ce5bf1741c187c3e8197f8b00e |
| probe | proof-perturbed-basin-beer-probes | basin-beer-lambert-bound-probes | proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-18d83e2efbce | 0 | 15 | recovered | recovered | perturbed_true_tree_recovered | same_ast_return | recovered | not_attempted | 0 | 0 | verified | artifacts/diagnostics/phase31-basin-bound/raw-runs/probe/proof-perturbed-basin-beer-probes/proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-18d83e2efbce.json | 09108fba0e69287aa899eceb5ce05a6f199577eb74ef9e8eb51e473ef14f1d4d |
| probe | proof-perturbed-basin-beer-probes | basin-beer-lambert-bound-probes | proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-015438da428c | 1 | 15 | repaired_candidate | recovered | repaired_candidate | snapped_but_failed | snapped_but_failed | repaired | 1 | 1 | mpmath_failed | artifacts/diagnostics/phase31-basin-bound/raw-runs/probe/proof-perturbed-basin-beer-probes/proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-015438da428c.json | d1788f269b212696ce76377f51e201fdfde592049607c73640ec0562cfb69064 |
| probe | proof-perturbed-basin-beer-probes | basin-beer-lambert-bound-probes | proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-8d0fd251f11f | 0 | 35 | repaired_candidate | recovered | repaired_candidate | snapped_but_failed | snapped_but_failed | repaired | 5 | 6 | mpmath_failed | artifacts/diagnostics/phase31-basin-bound/raw-runs/probe/proof-perturbed-basin-beer-probes/proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-8d0fd251f11f.json | 1643106adbac2a51c86bdd6beecff96277de690c4a1cdb4b12466e7793ccfb06 |
| probe | proof-perturbed-basin-beer-probes | basin-beer-lambert-bound-probes | proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-2535ff9f4d39 | 1 | 35 | repaired_candidate | recovered | repaired_candidate | snapped_but_failed | snapped_but_failed | repaired | 3 | 1 | mpmath_failed | artifacts/diagnostics/phase31-basin-bound/raw-runs/probe/proof-perturbed-basin-beer-probes/proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-2535ff9f4d39.json | 273118eb257f1b2e0653b52014e7daae14474d6d4f5589cfd4a59c28fd908f7a |
