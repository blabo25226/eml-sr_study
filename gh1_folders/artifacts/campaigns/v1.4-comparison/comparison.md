# v1.4 Before/After Campaign Comparison

Compares v1.4 campaign outputs against committed v1.3 baselines.

## Reproduce

Run this command from a clean checkout after v1.4 campaign folders exist:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli diagnostics compare --baseline artifacts/campaigns/v1.3-standard --candidate artifacts/campaigns/v1.4-standard --baseline artifacts/campaigns/v1.3-showcase --candidate artifacts/campaigns/v1.4-showcase --output-dir artifacts/campaigns/v1.4-comparison
```

## Campaign Pairs

| Baseline | Candidate |
|----------|-----------|
| artifacts/campaigns/v1.3-standard | artifacts/campaigns/v1.4-standard |
| artifacts/campaigns/v1.3-showcase | artifacts/campaigns/v1.4-showcase |

## Category Deltas

| Category | Verdict | Recovery Rate | Unsupported Rate | Failure Rate | Median Best Loss | Median Post-Snap Loss | Median Runtime |
|----------|---------|---------------|------------------|--------------|------------------|-----------------------|----------------|
| overall | improved | +0.2 | -0.04444 | -0.1556 | -0.1098 | -3.968e-34 | +0.818 |
| blind_recovery | improved | +0.4667 | 0 | -0.4667 | -1.635 | -31.88 | +0.4047 |
| beer_perturbation | unchanged | 0 | 0 | 0 | 0 | 0 | -0.1359 |
| compiler_coverage | improved | +0.2222 | -0.2222 | 0 | n/a | n/a | +0.003101 |

## Interpretation

- `improved` means recovery increased, unsupported rate decreased, or failure rate decreased.
- `regressed` means the opposite movement dominates.
- Loss and runtime deltas are supporting diagnostics and do not redefine recovery.
