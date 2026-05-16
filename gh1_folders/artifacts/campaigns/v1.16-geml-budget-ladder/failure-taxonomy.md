# v1.16 GEML Failure Taxonomy

| Tier | Pair | Formula | Family | Outcome | Failure Class | Next Step |
|------|------|---------|--------|---------|---------------|-----------|
| smoke | exp:seed0:depth2 | exp | negative_control | raw_lower_post_snap_mse | loss_only_signal | Inspect snap mismatch and candidate-pool alternatives; do not count as recovery. |
| smoke | sin_pi:seed0:depth3 | sin_pi | periodic | raw_lower_post_snap_mse | loss_only_signal | Inspect snap mismatch and candidate-pool alternatives; do not count as recovery. |
| pilot | cos_pi:seed0:depth3 | cos_pi | periodic | raw_lower_post_snap_mse | loss_only_signal | Inspect snap mismatch and candidate-pool alternatives; do not count as recovery. |
| pilot | cos_pi:seed1:depth3 | cos_pi | periodic | ipi_lower_post_snap_mse | loss_only_signal | Inspect snap mismatch and candidate-pool alternatives; do not count as recovery. |
| pilot | exp:seed0:depth2 | exp | negative_control | raw_lower_post_snap_mse | loss_only_signal | Inspect snap mismatch and candidate-pool alternatives; do not count as recovery. |
| pilot | exp:seed1:depth2 | exp | negative_control | raw_lower_post_snap_mse | loss_only_signal | Inspect snap mismatch and candidate-pool alternatives; do not count as recovery. |
| pilot | harmonic_sum:seed0:depth3 | harmonic_sum | harmonic | raw_lower_post_snap_mse | loss_only_signal | Inspect snap mismatch and candidate-pool alternatives; do not count as recovery. |
| pilot | harmonic_sum:seed1:depth3 | harmonic_sum | harmonic | raw_lower_post_snap_mse | loss_only_signal | Inspect snap mismatch and candidate-pool alternatives; do not count as recovery. |
| pilot | log:seed0:depth2 | log | negative_control | ipi_lower_post_snap_mse | loss_only_signal | Inspect snap mismatch and candidate-pool alternatives; do not count as recovery. |
| pilot | log:seed1:depth2 | log | negative_control | ipi_lower_post_snap_mse | loss_only_signal | Inspect snap mismatch and candidate-pool alternatives; do not count as recovery. |
| pilot | log_periodic_oscillation:seed0:depth3 | log_periodic_oscillation | log_periodic | raw_lower_post_snap_mse | loss_only_signal | Inspect snap mismatch and candidate-pool alternatives; do not count as recovery. |
| pilot | log_periodic_oscillation:seed1:depth3 | log_periodic_oscillation | log_periodic | raw_lower_post_snap_mse | loss_only_signal | Inspect snap mismatch and candidate-pool alternatives; do not count as recovery. |
| pilot | sin_pi:seed0:depth3 | sin_pi | periodic | raw_lower_post_snap_mse | loss_only_signal | Inspect snap mismatch and candidate-pool alternatives; do not count as recovery. |
| pilot | sin_pi:seed1:depth3 | sin_pi | periodic | raw_lower_post_snap_mse | loss_only_signal | Inspect snap mismatch and candidate-pool alternatives; do not count as recovery. |
