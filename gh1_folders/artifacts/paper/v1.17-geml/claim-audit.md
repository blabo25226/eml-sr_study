# v1.17 Claim Audit

Status: `passed`

| Check | Status | Description |
|-------|--------|-------------|
| final_decision_is_allowed | passed | Final decision is one of the predefined v1.17 outcomes. |
| gate_controls_next_campaign | passed | Broader campaign planning follows the sandbox gate. |
| exact_signal_counts_match_decision | passed | Exact-signal decisions require natural exact recovery and no negative-control exact recovery. |
| v116_package_locked | passed | v1.16 package manifest is source-locked as the before-state reference. |
| required_sources_locked | passed | Required v1.16 and v1.17 source artifacts are locked. |
| additive_boundary_stated | passed | Package states that v1.17 comparisons are additive and do not mutate v1.16. |
| loss_only_not_promoted | passed | Package does not promote loss-only diagnostics into recovery claims. |
| failure_taxonomy_referenced | passed | Package preserves failure taxonomy context for non-recovery rows. |
| reproduction_commands_present | passed | Package includes reproduction commands for all v1.17 stages. |
