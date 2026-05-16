# Operator-Family Comparison

## Recovery

| Operator | Schedule | Formula | Mode | Depth | Recovered | Total | Rate | Unsupported |
|----------|----------|---------|------|-------|-----------|-------|------|-------------|
| ipi_eml | fixed | cos_pi | blind | 3 | 0 | 2 | 0.0% | 0 |
| ipi_eml | fixed | exp | blind | 2 | 0 | 2 | 0.0% | 0 |
| ipi_eml | fixed | harmonic_sum | blind | 3 | 0 | 2 | 0.0% | 0 |
| ipi_eml | fixed | log | blind | 2 | 0 | 2 | 0.0% | 0 |
| ipi_eml | fixed | log_periodic_oscillation | blind | 3 | 0 | 2 | 0.0% | 0 |
| ipi_eml | fixed | sin_pi | blind | 3 | 0 | 2 | 0.0% | 0 |
| raw_eml | fixed | cos_pi | blind | 3 | 0 | 2 | 0.0% | 0 |
| raw_eml | fixed | exp | blind | 2 | 0 | 2 | 0.0% | 0 |
| raw_eml | fixed | harmonic_sum | blind | 3 | 0 | 2 | 0.0% | 0 |
| raw_eml | fixed | log | blind | 2 | 0 | 2 | 0.0% | 0 |
| raw_eml | fixed | log_periodic_oscillation | blind | 3 | 0 | 2 | 0.0% | 0 |
| raw_eml | fixed | sin_pi | blind | 3 | 0 | 2 | 0.0% | 0 |

## Diagnostics

| Operator | Schedule | Mode | Depth | Verifier Pass | Unsupported | Repair Attempt | Refit Accept | Active Nodes |
|----------|----------|------|-------|---------------|-------------|----------------|--------------|--------------|
| ipi_eml | fixed | blind | 2 | 0.0% | 0.0% | 100.0% | 0.0% | 3 |
| ipi_eml | fixed | blind | 3 | 0.0% | 0.0% | 100.0% | 12.5% | 3 |
| raw_eml | fixed | blind | 2 | 0.0% | 0.0% | 100.0% | 0.0% | 5 |
| raw_eml | fixed | blind | 3 | 0.0% | 0.0% | 100.0% | 50.0% | 5 |
