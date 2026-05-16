# Safe Claims

## Evidence Inputs

These claims are scoped to the supplied aggregate files:

- `artifacts/campaigns/v1.8-family-smoke-triage/aggregate.json`
- `artifacts/campaigns/v1.8-family-calibration/aggregate.json`
- `artifacts/campaigns/v1.8-family-standard-scoped/aggregate.json`

## Claims

- cEML_{s,t} is an affine-normalized transport of raw EML that preserves the exp-log inverse-pair structure.
- At the neutral point (0,t), cEML_{s,t} has output 0 and local Jacobian (+1,-1).
- The scale s is a curvature knob: local second derivatives shrink as s grows.
- The inverse-branch singularity is shifted to y=t-s, so singularity distance is a measurable diagnostic.
- On bounded boxes away from the shifted singularity, the large-s limit approaches subtraction.
