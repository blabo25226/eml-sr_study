# Regime Comparison

| suite_id | group | key | runs | verifier_recovered | same_ast_return | repaired_candidate | unsupported | failed | recovery_rate | evidence_classes | denominator_rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v1.11-paper-training | start_mode | blind | 4 | 4 | 0 | 0 | 0 | 0 | 1 | {"blind_training_recovered": 2, "scaffolded_blind_training_recovered": 2} | group-local verifier-owned runs |
| v1.11-paper-training | start_mode | perturbed_tree | 1 | 1 | 1 | 0 | 0 | 0 | 1 | {"perturbed_true_tree_recovered": 1} | group-local verifier-owned runs |
| v1.11-paper-training | start_mode | warm_start | 3 | 3 | 3 | 0 | 0 | 0 | 1 | {"same_ast": 3} | group-local verifier-owned runs |
| v1.11-paper-training | evidence_class | blind_training_recovered | 2 | 2 | 0 | 0 | 0 | 0 | 1 | {"blind_training_recovered": 2} | group-local verifier-owned runs |
| v1.11-paper-training | evidence_class | perturbed_true_tree_recovered | 1 | 1 | 1 | 0 | 0 | 0 | 1 | {"perturbed_true_tree_recovered": 1} | group-local verifier-owned runs |
| v1.11-paper-training | evidence_class | same_ast | 3 | 3 | 3 | 0 | 0 | 0 | 1 | {"same_ast": 3} | group-local verifier-owned runs |
| v1.11-paper-training | evidence_class | scaffolded_blind_training_recovered | 2 | 2 | 0 | 0 | 0 | 0 | 1 | {"scaffolded_blind_training_recovered": 2} | group-local verifier-owned runs |
| v1.11-logistic-planck-probes | start_mode | blind | 2 | 0 | 0 | 0 | 0 | 2 | 0 | {"failed": 1, "snapped_but_failed": 1} | group-local verifier-owned runs |
| v1.11-logistic-planck-probes | start_mode | compile | 2 | 0 | 0 | 0 | 2 | 0 | 0 | {"unsupported": 2} | group-local verifier-owned runs |
| v1.11-logistic-planck-probes | evidence_class | failed | 1 | 0 | 0 | 0 | 0 | 1 | 0 | {"failed": 1} | group-local verifier-owned runs |
| v1.11-logistic-planck-probes | evidence_class | snapped_but_failed | 1 | 0 | 0 | 0 | 0 | 1 | 0 | {"snapped_but_failed": 1} | group-local verifier-owned runs |
| v1.11-logistic-planck-probes | evidence_class | unsupported | 2 | 0 | 0 | 0 | 2 | 0 | 0 | {"unsupported": 2} | group-local verifier-owned runs |
