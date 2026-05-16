# v1.16 Claim Audit

Status: `passed`

| Check | Status | Description |
|-------|--------|-------------|
| gate_has_all_outcomes | passed | Gate config defines all allowed v1.16 outcomes. |
| exact_recovery_only_positive_gate | passed | Positive recovery numerator is verifier-gated trained exact recovery only. |
| blocks_loss_only_recovery_claims | passed | Claim text does not promote loss-only improvement to recovery. |
| blocks_global_superiority_language | passed | Claim text avoids global raw/i*pi superiority claims. |
| blocks_broad_blind_recovery_language | passed | Claim text avoids broad blind-recovery claims. |
| blocks_full_universality_language | passed | Claim text avoids full i*pi/GEML universality claims. |
| negative_controls_visible | passed | Claim text keeps negative controls visible. |
| paper_positive_requires_gate_pass | passed | Paper-positive language appears only when the gate evaluates paper_positive. |
| source_locks_present | passed | Package includes source-lock tables. |
| final_decision_is_allowed | passed | Final decision is one of the predefined v1.16 outcomes. |
| final_readme_matches_gate | passed | README and final decision use the gate-controlled outcome. |
| ablation_assets_present | passed | Final package includes ablation assets. |
| figure_metadata_present | passed | Final package includes figure metadata. |
| reproduction_commands_present | passed | Final package includes reproduction commands. |
| negative_control_cherry_picking_blocked | passed | Final package keeps negative controls visible. |
