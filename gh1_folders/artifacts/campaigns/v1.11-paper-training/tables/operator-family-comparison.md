# Operator-Family Comparison

## Recovery

| Operator | Schedule | Formula | Mode | Depth | Recovered | Total | Rate | Unsupported |
|----------|----------|---------|------|-------|-----------|-------|------|-------------|
| raw_eml | fixed | arrhenius | warm_start | 2 | 1 | 1 | 100.0% | 0 |
| raw_eml | fixed | basin_depth2_exp_exp | perturbed_tree | 2 | 1 | 1 | 100.0% | 0 |
| raw_eml | fixed | exp | blind | 1 | 4 | 4 | 100.0% | 0 |
| raw_eml | fixed | michaelis_menten | warm_start | 2 | 1 | 1 | 100.0% | 0 |
| raw_eml | fixed | shockley | warm_start | 2 | 1 | 1 | 100.0% | 0 |

## Diagnostics

| Operator | Schedule | Mode | Depth | Verifier Pass | Unsupported | Repair Attempt | Refit Accept | Active Nodes |
|----------|----------|------|-------|---------------|-------------|----------------|--------------|--------------|
| raw_eml | fixed | blind | 1 | 100.0% | 0.0% | 0.0% | 0.0% | 3 |
| raw_eml | fixed | perturbed_tree | 2 | 100.0% | 0.0% | 0.0% | 0.0% | 5 |
| raw_eml | fixed | warm_start | 2 | 100.0% | 0.0% | 0.0% | 0.0% | 35 |
