# v1.16 Ablation Table

Loss-only rows are diagnostics and never count as recovery.

| Dimension | Variant | Status | Operator | Pairs | Exact | Loss-Only | Effect | Next Step |
|-----------|---------|--------|----------|-------|-------|-----------|--------|-----------|
| initialization | raw random restarts | measured_pilot | raw_eml | 12 | 0 | 9 | No verifier-gated exact recovery; raw won more loss-only rows. | Do not promote loss-only results; inspect snap margins and branch diagnostics before increasing budget. |
| initialization | generic i*pi phase initializers | measured_pilot | ipi_eml | 12 | 0 | 3 | Generic phase initialization produced loss-only signals but no exact recovery. | Do not promote loss-only results; inspect snap margins and branch diagnostics before increasing budget. |
| branch_guards | guarded training with faithful verification | measured_pilot | matched | 12 | 0 | 12 | Branch diagnostics remained visible; branch-related rows did not become verified recoveries. | Compare faithful and guarded traces on the same candidates before adding stronger branch penalties. |
| constants | literal constants including pi | measured_pilot | matched | 12 | 0 | 12 | Literal pi support was present, so failure is not explained by missing pi alone. | Only test reduced constant catalogs as a controlled ablation after exact recovery appears. |
| depth | depth 2 | measured_pilot | matched | 4 | 0 | 4 | Depth remained within the pilot budget; no depth bucket produced exact recovery. | Increase depth only with a paired budget increase and exact-recovery denominator intact. |
| depth | depth 3 | measured_pilot | matched | 8 | 0 | 8 | Depth remained within the pilot budget; no depth bucket produced exact recovery. | Increase depth only with a paired budget increase and exact-recovery denominator intact. |
| budget | pilot steps/restarts | measured_pilot | matched | 12 | 0 | 12 | Pilot budget produced only diagnostic loss-only differences. | Full or larger budgets stay blocked until a smaller pilot shows exact-recovery signal. |
| candidate_pooling | verifier-gated hardening candidate pool | measured_pilot | matched | 12 | 0 | 12 | Candidate pooling selected snapped candidates but none passed the verifier. | Inspect low-margin slots and add neighborhood candidates before increasing campaign size. |
| branch_guards | unguarded faithful-only training | not_run_blocked_by_pilot_gate | matched |  |  |  | Not measured in v1.16 because the pilot gate failed closed. | Run only as a controlled diagnostic after a measured exact-recovery signal appears. |
| constants | no-pi literal catalog | not_run_blocked_by_pilot_gate | matched |  |  |  | Not measured in v1.16 because the pilot gate failed closed. | Use to test constant dependence once the current pi-enabled denominator has a positive signal. |
| budget | full multi-seed campaign budget | not_run_blocked_by_pilot_gate | matched |  |  |  | Not measured in v1.16 because the pilot gate failed closed. | Blocked by the Phase 90 ladder because the pilot had no exact i*pi recovery. |
| candidate_pooling | expanded local snap-neighborhood pool | not_run_blocked_by_pilot_gate | matched |  |  |  | Not measured in v1.16 because the pilot gate failed closed. | Prioritize if future pilot rows show near-miss snap margins. |
