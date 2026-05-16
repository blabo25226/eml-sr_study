# Operator-Family Comparison

## Recovery

| Operator | Schedule | Formula | Mode | Depth | Recovered | Total | Rate | Unsupported |
|----------|----------|---------|------|-------|-----------|-------|------|-------------|
| raw_eml | fixed | arrhenius | compile | 2 | 0 | 1 | 0.0% | 1 |
| raw_eml | fixed | arrhenius | warm_start | 2 | 1 | 1 | 100.0% | 0 |
| raw_eml | fixed | beer_lambert | compile | 2 | 0 | 1 | 0.0% | 1 |
| raw_eml | fixed | beer_lambert | warm_start | 2 | 1 | 1 | 100.0% | 0 |
| raw_eml | fixed | damped_oscillator | compile | 2 | 0 | 1 | 0.0% | 1 |
| raw_eml | fixed | damped_oscillator | warm_start | 2 | 0 | 1 | 0.0% | 1 |
| raw_eml | fixed | exp | compile | 2 | 1 | 1 | 100.0% | 0 |
| raw_eml | fixed | exp | warm_start | 2 | 1 | 1 | 100.0% | 0 |
| raw_eml | fixed | log | compile | 2 | 0 | 1 | 0.0% | 1 |
| raw_eml | fixed | log | warm_start | 2 | 0 | 1 | 0.0% | 1 |
| raw_eml | fixed | logistic | compile | 2 | 0 | 1 | 0.0% | 1 |
| raw_eml | fixed | logistic | warm_start | 2 | 0 | 1 | 0.0% | 1 |
| raw_eml | fixed | michaelis_menten | compile | 2 | 0 | 1 | 0.0% | 1 |
| raw_eml | fixed | michaelis_menten | warm_start | 2 | 1 | 1 | 100.0% | 0 |
| raw_eml | fixed | planck | compile | 2 | 0 | 1 | 0.0% | 1 |
| raw_eml | fixed | planck | warm_start | 2 | 0 | 1 | 0.0% | 1 |
| raw_eml | fixed | radioactive_decay | compile | 2 | 0 | 1 | 0.0% | 1 |
| raw_eml | fixed | radioactive_decay | warm_start | 2 | 1 | 1 | 100.0% | 0 |
| raw_eml | fixed | scaled_exp_fast_decay | compile | 2 | 0 | 1 | 0.0% | 1 |
| raw_eml | fixed | scaled_exp_fast_decay | warm_start | 2 | 1 | 1 | 100.0% | 0 |
| raw_eml | fixed | scaled_exp_growth | compile | 2 | 0 | 1 | 0.0% | 1 |
| raw_eml | fixed | scaled_exp_growth | warm_start | 2 | 1 | 1 | 100.0% | 0 |
| raw_eml | fixed | shockley | compile | 2 | 0 | 1 | 0.0% | 1 |
| raw_eml | fixed | shockley | warm_start | 2 | 1 | 1 | 100.0% | 0 |

## Diagnostics

| Operator | Schedule | Mode | Depth | Verifier Pass | Unsupported | Repair Attempt | Refit Accept | Active Nodes |
|----------|----------|------|-------|---------------|-------------|----------------|--------------|--------------|
| raw_eml | fixed | compile | 2 | 8.3% | 91.7% | 0.0% | 0.0% | n/a |
| raw_eml | fixed | warm_start | 2 | 66.7% | 33.3% | 0.0% | 0.0% | 19 |
