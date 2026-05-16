# Operator-Family Comparison

## Recovery

| Operator | Schedule | Formula | Mode | Depth | Recovered | Total | Rate | Unsupported |
|----------|----------|---------|------|-------|-----------|-------|------|-------------|
| CEML_1 | fixed | beer_lambert | warm_start | 2 | 0 | 1 | 0.0% | 1 |
| CEML_1 | fixed | exp | blind | 1 | 0 | 1 | 0.0% | 0 |
| CEML_1 | fixed | planck | compile | 2 | 0 | 1 | 0.0% | 1 |
| CEML_2 | fixed | beer_lambert | warm_start | 2 | 0 | 1 | 0.0% | 1 |
| CEML_2 | fixed | exp | blind | 1 | 0 | 1 | 0.0% | 0 |
| CEML_2 | fixed | planck | compile | 2 | 0 | 1 | 0.0% | 1 |
| CEML_4 | fixed | beer_lambert | warm_start | 2 | 0 | 1 | 0.0% | 1 |
| CEML_4 | fixed | exp | blind | 1 | 0 | 1 | 0.0% | 0 |
| CEML_4 | fixed | planck | compile | 2 | 0 | 1 | 0.0% | 1 |
| CEML_8 | fixed | beer_lambert | warm_start | 2 | 0 | 1 | 0.0% | 1 |
| CEML_8 | fixed | exp | blind | 1 | 0 | 1 | 0.0% | 0 |
| CEML_8 | fixed | planck | compile | 2 | 0 | 1 | 0.0% | 1 |
| ZEML_1 | fixed | beer_lambert | warm_start | 2 | 0 | 1 | 0.0% | 1 |
| ZEML_1 | fixed | exp | blind | 1 | 0 | 1 | 0.0% | 0 |
| ZEML_1 | fixed | planck | compile | 2 | 0 | 1 | 0.0% | 1 |
| ZEML_2 | fixed | beer_lambert | warm_start | 2 | 0 | 1 | 0.0% | 1 |
| ZEML_2 | fixed | exp | blind | 1 | 0 | 1 | 0.0% | 0 |
| ZEML_2 | fixed | planck | compile | 2 | 0 | 1 | 0.0% | 1 |
| ZEML_4 | fixed | beer_lambert | warm_start | 2 | 0 | 1 | 0.0% | 1 |
| ZEML_4 | fixed | exp | blind | 1 | 0 | 1 | 0.0% | 0 |
| ZEML_4 | fixed | planck | compile | 2 | 0 | 1 | 0.0% | 1 |
| ZEML_8 | ZEML_8 -> ZEML_4 | beer_lambert | warm_start | 2 | 0 | 1 | 0.0% | 1 |
| ZEML_8 | ZEML_8 -> ZEML_4 | exp | blind | 1 | 0 | 1 | 0.0% | 0 |
| ZEML_8 | ZEML_8 -> ZEML_4 | planck | compile | 2 | 0 | 1 | 0.0% | 1 |
| ZEML_8 | ZEML_8 -> ZEML_4 -> ZEML_2 -> ZEML_1 | beer_lambert | warm_start | 2 | 0 | 1 | 0.0% | 1 |
| ZEML_8 | ZEML_8 -> ZEML_4 -> ZEML_2 -> ZEML_1 | exp | blind | 1 | 0 | 1 | 0.0% | 0 |
| ZEML_8 | ZEML_8 -> ZEML_4 -> ZEML_2 -> ZEML_1 | planck | compile | 2 | 0 | 1 | 0.0% | 1 |
| ZEML_8 | fixed | beer_lambert | warm_start | 2 | 0 | 1 | 0.0% | 1 |
| ZEML_8 | fixed | exp | blind | 1 | 0 | 1 | 0.0% | 0 |
| ZEML_8 | fixed | planck | compile | 2 | 0 | 1 | 0.0% | 1 |
| raw_eml | fixed | beer_lambert | warm_start | 2 | 1 | 1 | 100.0% | 0 |
| raw_eml | fixed | exp | blind | 1 | 1 | 1 | 100.0% | 0 |
| raw_eml | fixed | planck | compile | 2 | 0 | 1 | 0.0% | 1 |

## Diagnostics

| Operator | Schedule | Mode | Depth | Verifier Pass | Unsupported | Repair Attempt | Refit Accept | Active Nodes |
|----------|----------|------|-------|---------------|-------------|----------------|--------------|--------------|
| CEML_1 | fixed | blind | 1 | 0.0% | 0.0% | 100.0% | 0.0% | 3 |
| CEML_1 | fixed | compile | 2 | 0.0% | 100.0% | 0.0% | 0.0% | n/a |
| CEML_1 | fixed | warm_start | 2 | 100.0% | 100.0% | 0.0% | 0.0% | n/a |
| CEML_2 | fixed | blind | 1 | 0.0% | 0.0% | 100.0% | 0.0% | 3 |
| CEML_2 | fixed | compile | 2 | 0.0% | 100.0% | 0.0% | 0.0% | n/a |
| CEML_2 | fixed | warm_start | 2 | 100.0% | 100.0% | 0.0% | 0.0% | n/a |
| CEML_4 | fixed | blind | 1 | 0.0% | 0.0% | 100.0% | 0.0% | 3 |
| CEML_4 | fixed | compile | 2 | 0.0% | 100.0% | 0.0% | 0.0% | n/a |
| CEML_4 | fixed | warm_start | 2 | 100.0% | 100.0% | 0.0% | 0.0% | n/a |
| CEML_8 | fixed | blind | 1 | 0.0% | 0.0% | 100.0% | 0.0% | 3 |
| CEML_8 | fixed | compile | 2 | 0.0% | 100.0% | 0.0% | 0.0% | n/a |
| CEML_8 | fixed | warm_start | 2 | 100.0% | 100.0% | 0.0% | 0.0% | n/a |
| ZEML_1 | fixed | blind | 1 | 0.0% | 0.0% | 100.0% | 0.0% | 3 |
| ZEML_1 | fixed | compile | 2 | 0.0% | 100.0% | 0.0% | 0.0% | n/a |
| ZEML_1 | fixed | warm_start | 2 | 100.0% | 100.0% | 0.0% | 0.0% | n/a |
| ZEML_2 | fixed | blind | 1 | 0.0% | 0.0% | 100.0% | 0.0% | 3 |
| ZEML_2 | fixed | compile | 2 | 0.0% | 100.0% | 0.0% | 0.0% | n/a |
| ZEML_2 | fixed | warm_start | 2 | 100.0% | 100.0% | 0.0% | 0.0% | n/a |
| ZEML_4 | fixed | blind | 1 | 0.0% | 0.0% | 100.0% | 0.0% | 3 |
| ZEML_4 | fixed | compile | 2 | 0.0% | 100.0% | 0.0% | 0.0% | n/a |
| ZEML_4 | fixed | warm_start | 2 | 100.0% | 100.0% | 0.0% | 0.0% | n/a |
| ZEML_8 | ZEML_8 -> ZEML_4 | blind | 1 | 0.0% | 0.0% | 100.0% | 0.0% | 3 |
| ZEML_8 | ZEML_8 -> ZEML_4 | compile | 2 | 0.0% | 100.0% | 0.0% | 0.0% | n/a |
| ZEML_8 | ZEML_8 -> ZEML_4 | warm_start | 2 | 100.0% | 100.0% | 0.0% | 0.0% | n/a |
| ZEML_8 | ZEML_8 -> ZEML_4 -> ZEML_2 -> ZEML_1 | blind | 1 | 0.0% | 0.0% | 100.0% | 0.0% | 3 |
| ZEML_8 | ZEML_8 -> ZEML_4 -> ZEML_2 -> ZEML_1 | compile | 2 | 0.0% | 100.0% | 0.0% | 0.0% | n/a |
| ZEML_8 | ZEML_8 -> ZEML_4 -> ZEML_2 -> ZEML_1 | warm_start | 2 | 100.0% | 100.0% | 0.0% | 0.0% | n/a |
| ZEML_8 | fixed | blind | 1 | 0.0% | 0.0% | 100.0% | 0.0% | 3 |
| ZEML_8 | fixed | compile | 2 | 0.0% | 100.0% | 0.0% | 0.0% | n/a |
| ZEML_8 | fixed | warm_start | 2 | 100.0% | 100.0% | 0.0% | 0.0% | n/a |
| raw_eml | fixed | blind | 1 | 100.0% | 0.0% | 0.0% | 0.0% | 3 |
| raw_eml | fixed | compile | 2 | 0.0% | 100.0% | 0.0% | 0.0% | n/a |
| raw_eml | fixed | warm_start | 2 | 100.0% | 0.0% | 0.0% | 0.0% | 19 |
