# Operator-Family Comparison

## Recovery

| Operator | Schedule | Formula | Mode | Depth | Recovered | Total | Rate | Unsupported |
|----------|----------|---------|------|-------|-----------|-------|------|-------------|
| raw_eml | fixed | logistic | blind | 3 | 0 | 1 | 0.0% | 0 |
| raw_eml | fixed | logistic | compile | 2 | 0 | 1 | 0.0% | 1 |
| raw_eml | fixed | planck | blind | 3 | 0 | 1 | 0.0% | 0 |
| raw_eml | fixed | planck | compile | 2 | 0 | 1 | 0.0% | 1 |

## Diagnostics

| Operator | Schedule | Mode | Depth | Verifier Pass | Unsupported | Repair Attempt | Refit Accept | Active Nodes |
|----------|----------|------|-------|---------------|-------------|----------------|--------------|--------------|
| raw_eml | fixed | blind | 3 | 0.0% | 0.0% | 100.0% | 100.0% | 5 |
| raw_eml | fixed | compile | 2 | 0.0% | 100.0% | 0.0% | 0.0% | n/a |
