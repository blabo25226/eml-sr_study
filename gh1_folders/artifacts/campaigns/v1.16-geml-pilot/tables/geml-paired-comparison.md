# GEML Paired Comparison

| Metric | Value |
|--------|-------|
| paired_rows | 12 |
| raw_trained_exact_recovery_rate | 0.000 |
| ipi_trained_exact_recovery_rate | 0.000 |
| raw_recovery_wins | 0 |
| ipi_recovery_wins | 0 |
| both_recovered | 0 |
| neither_recovered | 12 |

## Pairs

| Formula | Family | Raw Recovery | i*pi Recovery | Outcome | Raw Post MSE | i*pi Post MSE |
|---------|--------|--------------|---------------|---------|--------------|---------------|
| cos_pi | periodic | False | False | raw_lower_post_snap_mse | 0.667 | 3.074 |
| cos_pi | periodic | False | False | ipi_lower_post_snap_mse | 0.6662 | 0.5299 |
| exp | negative_control | False | False | raw_lower_post_snap_mse | 0.5639 | 3.24 |
| exp | negative_control | False | False | raw_lower_post_snap_mse | 0.5639 | 3.239 |
| harmonic_sum | harmonic | False | False | raw_lower_post_snap_mse | 0.845 | 2.728 |
| harmonic_sum | harmonic | False | False | raw_lower_post_snap_mse | 0.8404 | 2.73 |
| log | negative_control | False | False | ipi_lower_post_snap_mse | 2.302 | 1.624 |
| log | negative_control | False | False | ipi_lower_post_snap_mse | 2.809 | 1.616 |
| log_periodic_oscillation | log_periodic | False | False | raw_lower_post_snap_mse | 0.9672 | 1.453 |
| log_periodic_oscillation | log_periodic | False | False | raw_lower_post_snap_mse | 0.9657 | 1.434 |
| sin_pi | periodic | False | False | raw_lower_post_snap_mse | 0.6536 | 2.533 |
| sin_pi | periodic | False | False | raw_lower_post_snap_mse | 0.6568 | 2.538 |
