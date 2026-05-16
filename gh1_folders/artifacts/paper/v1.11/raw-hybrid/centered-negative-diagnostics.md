# Centered-Family Negative Diagnostics

These rows are negative diagnostic evidence from v1.8, not a claim that centered families cannot work.
The same-family witness caveat remains active: raw `exp`, `log`, and `scaled_exp` scaffolds are not valid centered-family witnesses.

- Decision: `publish_raw_eml_searchability_note`
- Raw recovery rate: 0.800
- Best centered recovery rate: 0.000

| Operator | Runs | Recovered | Recovery Rate | Unsupported Rate | Schedules |
|----------|------|-----------|---------------|------------------|-----------|
| CEML_1 | 10 | 0 | 0.000 | 0.500 | fixed |
| CEML_2 | 10 | 0 | 0.000 | 0.500 | fixed |
| CEML_4 | 10 | 0 | 0.000 | 0.500 | fixed |
| CEML_8 | 10 | 0 | 0.000 | 0.500 | fixed |
| ZEML_1 | 10 | 0 | 0.000 | 0.500 | fixed |
| ZEML_2 | 10 | 0 | 0.000 | 0.500 | fixed |
| ZEML_4 | 10 | 0 | 0.000 | 0.500 | fixed |
| ZEML_8 | 30 | 0 | 0.000 | 0.500 | ZEML_8 -> ZEML_4, ZEML_8 -> ZEML_4 -> ZEML_2 -> ZEML_1, fixed |
