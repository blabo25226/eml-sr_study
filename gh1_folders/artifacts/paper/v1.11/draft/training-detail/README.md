# v1.12 Training Detail Artifacts

Runs inspected: 18.
Step-trace rows: 4472.
Run-summary rows: 58.
Candidate-lifecycle rows: 232.

## Tables

- `artifacts/paper/v1.11/draft/training-detail/tables/training-step-traces.csv`: per-step fit loss, objective loss, entropy, size penalty, temperature, operator family, and anomaly counters.
- `artifacts/paper/v1.11/draft/training-detail/tables/training-run-summaries.csv`: per-restart loss summaries and final anomaly totals.
- `artifacts/paper/v1.11/draft/training-detail/tables/candidate-lifecycle.csv`: exact candidate pool lifecycle, snap margins, post-snap loss, verifier status, and selected/fallback flags.

## Figures

- `artifacts/paper/v1.11/draft/training-detail/figures/shallow-loss-curves.svg`: shallow refresh loss curves.
- `artifacts/paper/v1.11/draft/training-detail/figures/depth-loss-curves.svg`: depth-refresh loss curves.

## Claim Boundary

These artifacts illustrate optimizer dynamics and candidate selection. Recovery claims still come only from verifier status, not from loss curves alone.
