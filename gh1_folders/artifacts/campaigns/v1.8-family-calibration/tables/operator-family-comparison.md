# Operator-Family Comparison

## Recovery

| Operator | Schedule | Formula | Mode | Depth | Recovered | Total | Rate | Unsupported |
|----------|----------|---------|------|-------|-----------|-------|------|-------------|
| CEML_1 | fixed | exp | blind | 1 | 0 | 1 | 0.0% | 0 |
| CEML_1 | fixed | log | blind | 3 | 0 | 1 | 0.0% | 0 |
| CEML_2 | fixed | exp | blind | 1 | 0 | 1 | 0.0% | 0 |
| CEML_2 | fixed | log | blind | 3 | 0 | 1 | 0.0% | 0 |
| CEML_4 | fixed | exp | blind | 1 | 0 | 1 | 0.0% | 0 |
| CEML_4 | fixed | log | blind | 3 | 0 | 1 | 0.0% | 0 |
| CEML_8 | fixed | exp | blind | 1 | 0 | 1 | 0.0% | 0 |
| CEML_8 | fixed | log | blind | 3 | 0 | 1 | 0.0% | 0 |
| ZEML_1 | fixed | exp | blind | 1 | 0 | 1 | 0.0% | 0 |
| ZEML_1 | fixed | log | blind | 3 | 0 | 1 | 0.0% | 0 |
| ZEML_2 | fixed | exp | blind | 1 | 0 | 1 | 0.0% | 0 |
| ZEML_2 | fixed | log | blind | 3 | 0 | 1 | 0.0% | 0 |
| ZEML_4 | fixed | exp | blind | 1 | 0 | 1 | 0.0% | 0 |
| ZEML_4 | fixed | log | blind | 3 | 0 | 1 | 0.0% | 0 |
| ZEML_8 | ZEML_8 -> ZEML_4 | exp | blind | 1 | 0 | 1 | 0.0% | 0 |
| ZEML_8 | ZEML_8 -> ZEML_4 | log | blind | 3 | 0 | 1 | 0.0% | 0 |
| ZEML_8 | ZEML_8 -> ZEML_4 -> ZEML_2 -> ZEML_1 | exp | blind | 1 | 0 | 1 | 0.0% | 0 |
| ZEML_8 | ZEML_8 -> ZEML_4 -> ZEML_2 -> ZEML_1 | log | blind | 3 | 0 | 1 | 0.0% | 0 |
| ZEML_8 | fixed | exp | blind | 1 | 0 | 1 | 0.0% | 0 |
| ZEML_8 | fixed | log | blind | 3 | 0 | 1 | 0.0% | 0 |
| raw_eml | fixed | exp | blind | 1 | 1 | 1 | 100.0% | 0 |
| raw_eml | fixed | log | blind | 3 | 1 | 1 | 100.0% | 0 |

## Diagnostics

| Operator | Schedule | Mode | Depth | Verifier Pass | Unsupported | Repair Attempt | Refit Accept | Active Nodes |
|----------|----------|------|-------|---------------|-------------|----------------|--------------|--------------|
| CEML_1 | fixed | blind | 1 | 0.0% | 0.0% | 100.0% | 0.0% | 3 |
| CEML_1 | fixed | blind | 3 | 0.0% | 0.0% | 100.0% | 0.0% | 7 |
| CEML_2 | fixed | blind | 1 | 0.0% | 0.0% | 100.0% | 0.0% | 3 |
| CEML_2 | fixed | blind | 3 | 0.0% | 0.0% | 100.0% | 0.0% | 3 |
| CEML_4 | fixed | blind | 1 | 0.0% | 0.0% | 100.0% | 0.0% | 3 |
| CEML_4 | fixed | blind | 3 | 0.0% | 0.0% | 100.0% | 0.0% | 7 |
| CEML_8 | fixed | blind | 1 | 0.0% | 0.0% | 100.0% | 0.0% | 3 |
| CEML_8 | fixed | blind | 3 | 0.0% | 0.0% | 100.0% | 0.0% | 7 |
| ZEML_1 | fixed | blind | 1 | 0.0% | 0.0% | 100.0% | 0.0% | 3 |
| ZEML_1 | fixed | blind | 3 | 0.0% | 0.0% | 100.0% | 0.0% | 7 |
| ZEML_2 | fixed | blind | 1 | 0.0% | 0.0% | 100.0% | 0.0% | 3 |
| ZEML_2 | fixed | blind | 3 | 0.0% | 0.0% | 100.0% | 0.0% | 3 |
| ZEML_4 | fixed | blind | 1 | 0.0% | 0.0% | 100.0% | 0.0% | 3 |
| ZEML_4 | fixed | blind | 3 | 0.0% | 0.0% | 100.0% | 0.0% | 3 |
| ZEML_8 | ZEML_8 -> ZEML_4 | blind | 1 | 0.0% | 0.0% | 100.0% | 0.0% | 3 |
| ZEML_8 | ZEML_8 -> ZEML_4 | blind | 3 | 0.0% | 0.0% | 100.0% | 0.0% | 3 |
| ZEML_8 | ZEML_8 -> ZEML_4 -> ZEML_2 -> ZEML_1 | blind | 1 | 0.0% | 0.0% | 100.0% | 0.0% | 3 |
| ZEML_8 | ZEML_8 -> ZEML_4 -> ZEML_2 -> ZEML_1 | blind | 3 | 0.0% | 0.0% | 100.0% | 0.0% | 3 |
| ZEML_8 | fixed | blind | 1 | 0.0% | 0.0% | 100.0% | 0.0% | 3 |
| ZEML_8 | fixed | blind | 3 | 0.0% | 0.0% | 100.0% | 0.0% | 3 |
| raw_eml | fixed | blind | 1 | 100.0% | 0.0% | 0.0% | 0.0% | 3 |
| raw_eml | fixed | blind | 3 | 100.0% | 0.0% | 0.0% | 0.0% | 7 |
