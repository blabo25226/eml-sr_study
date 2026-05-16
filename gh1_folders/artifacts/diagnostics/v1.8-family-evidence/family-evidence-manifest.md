# v1.8 Family Evidence Manifest

- Completed campaigns: 3
- Scoped campaigns: 5
- Completed campaigns with regression locks: 3

## Completed

| Campaign | Aggregate | Locks | Command |
|----------|-----------|-------|---------|
| family-smoke | `artifacts/campaigns/v1.8-family-smoke-triage/aggregate.json` | `artifacts/campaigns/v1.8-family-smoke-triage/tables/operator-family-locks.json` | `PYTHONPATH=src python -m eml_symbolic_regression.cli campaign family-smoke --output-root artifacts/campaigns --label v1.8-family-smoke-triage --overwrite` |
| family-calibration | `artifacts/campaigns/v1.8-family-calibration/aggregate.json` | `artifacts/campaigns/v1.8-family-calibration/tables/operator-family-locks.json` | `PYTHONPATH=src python -m eml_symbolic_regression.cli campaign family-calibration --output-root artifacts/campaigns --label v1.8-family-calibration --overwrite` |
| family-standard | `artifacts/campaigns/v1.8-family-standard-scoped/aggregate.json` | `artifacts/campaigns/v1.8-family-standard-scoped/tables/operator-family-locks.json` | `PYTHONPATH=src python -m eml_symbolic_regression.cli campaign family-standard --output-root artifacts/campaigns --label v1.8-family-standard-scoped --overwrite --formula exp --formula log --formula beer_lambert --seed 0` |

## Scoped

| Campaign | Reason |
|----------|--------|
| family-shallow-pure-blind | scoped after calibration because centered exp/log blind variants recovered 0/20 and full pure-blind matrix would mainly expand known centered failures |
| family-shallow | scoped until same-family centered scaffold/witness support exists; centered warm-start rows remain fail-closed in denominators |
| family-basin | centered perturbed-tree paths require same-family exact target seeds and remain explicit unsupported gates |
| family-depth-curve | scoped because centered shallow calibration showed no positive signal; defer larger depth sweep until centered shallow behavior improves |
| family-showcase | skipped because earlier evidence showed no meaningful centered-family positive signal |
