# v1.17 GEML Evidence Package

This package is additive: the v1.16 package remains intact and is source-locked as the before-state reference.

Final decision: `still_inconclusive`
Broader campaign gate: `block_broader_campaigns`

## Before And After

- Before: `artifacts/paper/v1.16-geml/manifest.json`
- Snap diagnostics: `artifacts/paper/v1.17-geml/snap-diagnostics/manifest.json`
- Neighborhood candidates: `artifacts/paper/v1.17-geml/neighborhoods/manifest.json`
- Verifier-first ranking: `artifacts/paper/v1.17-geml/ranking/manifest.json`
- Focused sandbox: `artifacts/paper/v1.17-geml/sandbox/manifest.json`

## Claim Boundary

v1.17 is an additive snap-first analysis over the intact v1.16 package. Exact-signal claims require verifier-gated natural exact recovery, loss-only rows remain diagnostic, and the v1.16 failure taxonomy remains the context for non-recovery rows.

The v1.16 failure taxonomy is preserved as the reference for failure and non-recovery interpretation.

## Files

- `final-decision.json` and `final-decision.md` - final gate-controlled decision.
- `claim-audit.json` and `claim-audit.md` - claim language and source-lock audit.
- `source-locks.json` - required and optional input locks plus output locks.
- `reproduction.md` - commands to rebuild the staged v1.17 package.
