# Regime Recovery

| suite_id | regime | runs | verifier_recovered | same_ast_return | unsupported | failed | recovery_rate | unsupported_rate | failure_rate | evidence_classes | denominator_rule | claim_boundary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v1.11-paper-training | blind | 4 | 4 | 0 | 0 | 0 | 1 | 0 | 0 | {"blind_training_recovered": 2, "scaffolded_blind_training_recovered": 2} | suite/start-mode-local runs | do not combine regimes into a blind-discovery denominator |
| v1.11-paper-training | perturbed_tree | 1 | 1 | 1 | 0 | 0 | 1 | 0 | 0 | {"perturbed_true_tree_recovered": 1} | suite/start-mode-local runs | do not combine regimes into a blind-discovery denominator |
| v1.11-paper-training | warm_start | 3 | 3 | 3 | 0 | 0 | 1 | 0 | 0 | {"same_ast": 3} | suite/start-mode-local runs | do not combine regimes into a blind-discovery denominator |
| v1.11-logistic-planck-probes | blind | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 1 | {"failed": 1, "snapped_but_failed": 1} | suite/start-mode-local runs | do not combine regimes into a blind-discovery denominator |
| v1.11-logistic-planck-probes | compile | 2 | 0 | 0 | 2 | 0 | 0 | 1 | 0 | {"unsupported": 2} | suite/start-mode-local runs | do not combine regimes into a blind-discovery denominator |
