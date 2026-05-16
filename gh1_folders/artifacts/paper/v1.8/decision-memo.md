# v1.8 Paper Decision Memo

**Decision:** `publish_raw_eml_searchability_note`

Do not position the centered family as an empirical improvement. The v1.8 aggregates support a raw-EML searchability/geometry note with centered variants reported as negative or diagnostic evidence.

## Evidence Summary

- Aggregate files: 3
- Runs summarized: 110
- Centered-family evidence present: True
- Raw recovery rate: 80.0%
- Best centered recovery rate: 0.0%

## Operator Groups

| Operator | Runs | Recovered | Recovery Rate | Unsupported Rate | Schedules |
|----------|------|-----------|---------------|------------------|-----------|
| CEML_1 | 10 | 0 | 0.0% | 50.0% | fixed |
| CEML_2 | 10 | 0 | 0.0% | 50.0% | fixed |
| CEML_4 | 10 | 0 | 0.0% | 50.0% | fixed |
| CEML_8 | 10 | 0 | 0.0% | 50.0% | fixed |
| ZEML_1 | 10 | 0 | 0.0% | 50.0% | fixed |
| ZEML_2 | 10 | 0 | 0.0% | 50.0% | fixed |
| ZEML_4 | 10 | 0 | 0.0% | 50.0% | fixed |
| ZEML_8 | 30 | 0 | 0.0% | 50.0% | ZEML_8 -> ZEML_4, ZEML_8 -> ZEML_4 -> ZEML_2 -> ZEML_1, fixed |
| raw_eml | 10 | 8 | 80.0% | 10.0% | fixed |

## Claim Boundary

Centered-family mathematical claims are safe only at the operator/geometry level until constructive completeness is supplied.
Empirical recovery claims require v1.8 family campaign aggregates and must keep regimes separate.
