# v1.8 Family Full-Run Gate

**Verdict:** `conditional_go_scoped`

Proceed only with campaigns whose centered paths are explicitly supported or fail-closed; do not treat centered warm-start unsupported rows as recovery failures hidden from denominators.

## Accepted Exclusions

- depth_exceeded

## Remaining Risks

- centered warm-start needs same-family exact seeds before it can become supported evidence
- centered blind exp/log calibration may reflect search geometry rather than implementation support
- Planck compile depth remains a stretch-target exclusion across raw and centered families
