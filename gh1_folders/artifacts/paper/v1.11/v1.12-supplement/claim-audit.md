# v1.12 Claim Audit

Status: **passed**

| Check | Status | Detail |
|-------|--------|--------|
| draft_sections_present | passed | Draft section skeletons are present. |
| claim_taxonomy_complete | passed | Claim taxonomy covers all evidence regimes. |
| paper_facing_assets_present | passed | Paper-facing motif, negative-result, pipeline, and caption artifacts are present. |
| shallow_refresh_counts | passed | Shallow refresh keeps pure-blind and scaffolded seed denominators separate. |
| depth_refresh_counts | passed | Depth refresh covers depths 2 through 5 with at least two rows each. |
| logistic_planck_negative_rows_not_promoted | passed | Logistic and Planck negative rows remain unsupported and unpromoted. |
| bounded_probe_status_visible | passed | Bounded baseline and logistic strict-support probe outcomes are visible and non-promotional. |
| training_detail_artifacts_present | passed | Training-detail artifacts expose per-step losses, run summaries, candidate lifecycle rows, and loss-curve figures. |
| source_locks_cover_v112_artifact_families | passed | Source locks cover draft, paper-facing, evidence-refresh, and bounded-probe artifact families. |
