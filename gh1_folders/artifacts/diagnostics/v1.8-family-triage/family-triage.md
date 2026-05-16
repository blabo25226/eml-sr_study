# v1.8 Centered-Family Triage

## Inputs

- Smoke aggregate: `artifacts/campaigns/v1.8-family-smoke-triage/aggregate.json`
- Calibration aggregate: `artifacts/campaigns/v1.8-family-calibration/aggregate.json`

## Go/No-Go

- Verdict: `conditional_go_scoped`
- Recommendation: Proceed only with campaigns whose centered paths are explicitly supported or fail-closed; do not treat centered warm-start unsupported rows as recovery failures hidden from denominators.
- Missing integration rows: 10
- Accepted exclusions: 11
- Centered calibration recovered: 0/20

## Classifications

| Source | Case | Operator | Schedule | Mode | Status | Category | Reason | Action |
|--------|------|----------|----------|------|--------|----------|--------|--------|
| smoke | exp-blind-raw | raw_eml | fixed | blind | recovered | trusted_positive | verified | usable_as_recovery_evidence |
| smoke | exp-blind-ceml1 | CEML_1 | fixed | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| smoke | exp-blind-zeml1 | ZEML_1 | fixed | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| smoke | exp-blind-ceml2 | CEML_2 | fixed | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| smoke | exp-blind-zeml2 | ZEML_2 | fixed | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| smoke | exp-blind-ceml4 | CEML_4 | fixed | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| smoke | exp-blind-zeml4 | ZEML_4 | fixed | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| smoke | exp-blind-ceml8 | CEML_8 | fixed | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| smoke | exp-blind-zeml8 | ZEML_8 | fixed | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| smoke | exp-blind-zeml8-4 | ZEML_8 | ZEML_8 -> ZEML_4 | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| smoke | exp-blind-zeml8-4-2-1 | ZEML_8 | ZEML_8 -> ZEML_4 -> ZEML_2 -> ZEML_1 | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| smoke | beer-warm-raw | raw_eml | fixed | warm_start | same_ast_return | trusted_positive | verified | usable_as_recovery_evidence |
| smoke | beer-warm-ceml1 | CEML_1 | fixed | warm_start | unsupported | missing_integration | centered_family_same_family_seed_missing | accepted_fail_closed_until_same_family_seed_exists |
| smoke | beer-warm-zeml1 | ZEML_1 | fixed | warm_start | unsupported | missing_integration | centered_family_same_family_seed_missing | accepted_fail_closed_until_same_family_seed_exists |
| smoke | beer-warm-ceml2 | CEML_2 | fixed | warm_start | unsupported | missing_integration | centered_family_same_family_seed_missing | accepted_fail_closed_until_same_family_seed_exists |
| smoke | beer-warm-zeml2 | ZEML_2 | fixed | warm_start | unsupported | missing_integration | centered_family_same_family_seed_missing | accepted_fail_closed_until_same_family_seed_exists |
| smoke | beer-warm-ceml4 | CEML_4 | fixed | warm_start | unsupported | missing_integration | centered_family_same_family_seed_missing | accepted_fail_closed_until_same_family_seed_exists |
| smoke | beer-warm-zeml4 | ZEML_4 | fixed | warm_start | unsupported | missing_integration | centered_family_same_family_seed_missing | accepted_fail_closed_until_same_family_seed_exists |
| smoke | beer-warm-ceml8 | CEML_8 | fixed | warm_start | unsupported | missing_integration | centered_family_same_family_seed_missing | accepted_fail_closed_until_same_family_seed_exists |
| smoke | beer-warm-zeml8 | ZEML_8 | fixed | warm_start | unsupported | missing_integration | centered_family_same_family_seed_missing | accepted_fail_closed_until_same_family_seed_exists |
| smoke | beer-warm-zeml8-4 | ZEML_8 | ZEML_8 -> ZEML_4 | warm_start | unsupported | missing_integration | centered_family_same_family_seed_missing | accepted_fail_closed_until_same_family_seed_exists |
| smoke | beer-warm-zeml8-4-2-1 | ZEML_8 | ZEML_8 -> ZEML_4 -> ZEML_2 -> ZEML_1 | warm_start | unsupported | missing_integration | centered_family_same_family_seed_missing | accepted_fail_closed_until_same_family_seed_exists |
| smoke | planck-diagnostic-raw | raw_eml | fixed | compile | unsupported | accepted_exclusion | depth_exceeded | keep_stretch_depth_gate_in_denominator |
| smoke | planck-diagnostic-ceml1 | CEML_1 | fixed | compile | unsupported | accepted_exclusion | depth_exceeded | keep_stretch_depth_gate_in_denominator |
| smoke | planck-diagnostic-zeml1 | ZEML_1 | fixed | compile | unsupported | accepted_exclusion | depth_exceeded | keep_stretch_depth_gate_in_denominator |
| smoke | planck-diagnostic-ceml2 | CEML_2 | fixed | compile | unsupported | accepted_exclusion | depth_exceeded | keep_stretch_depth_gate_in_denominator |
| smoke | planck-diagnostic-zeml2 | ZEML_2 | fixed | compile | unsupported | accepted_exclusion | depth_exceeded | keep_stretch_depth_gate_in_denominator |
| smoke | planck-diagnostic-ceml4 | CEML_4 | fixed | compile | unsupported | accepted_exclusion | depth_exceeded | keep_stretch_depth_gate_in_denominator |
| smoke | planck-diagnostic-zeml4 | ZEML_4 | fixed | compile | unsupported | accepted_exclusion | depth_exceeded | keep_stretch_depth_gate_in_denominator |
| smoke | planck-diagnostic-ceml8 | CEML_8 | fixed | compile | unsupported | accepted_exclusion | depth_exceeded | keep_stretch_depth_gate_in_denominator |
| smoke | planck-diagnostic-zeml8 | ZEML_8 | fixed | compile | unsupported | accepted_exclusion | depth_exceeded | keep_stretch_depth_gate_in_denominator |
| smoke | planck-diagnostic-zeml8-4 | ZEML_8 | ZEML_8 -> ZEML_4 | compile | unsupported | accepted_exclusion | depth_exceeded | keep_stretch_depth_gate_in_denominator |
| smoke | planck-diagnostic-zeml8-4-2-1 | ZEML_8 | ZEML_8 -> ZEML_4 -> ZEML_2 -> ZEML_1 | compile | unsupported | accepted_exclusion | depth_exceeded | keep_stretch_depth_gate_in_denominator |
| calibration | cal-exp-blind-raw | raw_eml | fixed | blind | recovered | trusted_positive | verified | usable_as_recovery_evidence |
| calibration | cal-exp-blind-ceml1 | CEML_1 | fixed | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| calibration | cal-exp-blind-zeml1 | ZEML_1 | fixed | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| calibration | cal-exp-blind-ceml2 | CEML_2 | fixed | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| calibration | cal-exp-blind-zeml2 | ZEML_2 | fixed | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| calibration | cal-exp-blind-ceml4 | CEML_4 | fixed | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| calibration | cal-exp-blind-zeml4 | ZEML_4 | fixed | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| calibration | cal-exp-blind-ceml8 | CEML_8 | fixed | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| calibration | cal-exp-blind-zeml8 | ZEML_8 | fixed | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| calibration | cal-exp-blind-zeml8-4 | ZEML_8 | ZEML_8 -> ZEML_4 | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| calibration | cal-exp-blind-zeml8-4-2-1 | ZEML_8 | ZEML_8 -> ZEML_4 -> ZEML_2 -> ZEML_1 | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| calibration | cal-log-blind-raw | raw_eml | fixed | blind | recovered | trusted_positive | verified | usable_as_recovery_evidence |
| calibration | cal-log-blind-ceml1 | CEML_1 | fixed | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| calibration | cal-log-blind-zeml1 | ZEML_1 | fixed | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| calibration | cal-log-blind-ceml2 | CEML_2 | fixed | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| calibration | cal-log-blind-zeml2 | ZEML_2 | fixed | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| calibration | cal-log-blind-ceml4 | CEML_4 | fixed | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| calibration | cal-log-blind-zeml4 | ZEML_4 | fixed | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| calibration | cal-log-blind-ceml8 | CEML_8 | fixed | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| calibration | cal-log-blind-zeml8 | ZEML_8 | fixed | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| calibration | cal-log-blind-zeml8-4 | ZEML_8 | ZEML_8 -> ZEML_4 | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
| calibration | cal-log-blind-zeml8-4-2-1 | ZEML_8 | ZEML_8 -> ZEML_4 -> ZEML_2 -> ZEML_1 | blind | snapped_but_failed | budget_or_operator_behavior | train_failed | use_calibration_before_full_blind_campaign |
