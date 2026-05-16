# v1.16 Failure Examples

| Failure Class | Status | Count | Example | Formula | Outcome | Next Step |
|---------------|--------|-------|---------|---------|---------|-----------|
| loss_only_signal | observed | 14 | cos_pi:seed0:depth3 | cos_pi | raw_lower_post_snap_mse | Inspect snap mismatch and candidate-pool alternatives; do not count as recovery. |
| optimization_or_snap_miss | not_observed | 0 |  |  |  | Increase candidate-pool or hardening budget only after checking snap margins. |
| snap_mismatch | not_observed | 0 |  |  |  | Compare soft candidate behavior with snapped AST alternatives near low-margin slots. |
| branch_pathology | not_observed | 0 |  |  |  | Inspect branch-domain construction and guarded-versus-faithful mismatch diagnostics. |
| verifier_mismatch | not_observed | 0 |  |  |  | Inspect split-level verifier evidence and high-precision status. |
| unsupported_or_over_depth | not_observed | 0 |  |  |  | Check target depth, literal constants, and suite support gates before rerunning. |
| numerical_instability | not_observed | 0 |  |  |  | Reduce guard pressure or inspect anomaly traces before increasing budget. |
