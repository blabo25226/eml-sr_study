# v1.16 Final GEML/i*pi Decision

**Decision:** `inconclusive`

The package is inconclusive; no positive i*pi/GEML recovery claim is supported.

The evidence is incomplete, loss-only, or confounded; no positive claim is allowed.

Negative controls remain visible. Loss-only improvements remain diagnostic. Exact recovery requires verifier-gated snapped candidates.

## Gate Metrics

- Paired rows: 12
- Unique seeds: 2
- Complete denominator: False
- Natural i*pi exact recovery wins: 0
- Natural raw exact recovery wins: 0
- Negative-control i*pi exact recovery wins: 0
- Loss-only outcomes: 12

## Included Evidence

- `package_manifest`: `artifacts/paper/v1.16-geml/manifest.json`
- `gate_evaluation`: `artifacts/paper/v1.16-geml/gate-evaluation.json`
- `claim_audit`: `artifacts/paper/v1.16-geml/claim-audit.json`
- `ablation_manifest`: `artifacts/paper/v1.16-geml/ablations/manifest.json`
- `ablation_table`: `artifacts/paper/v1.16-geml/ablations/ablation-table.json`
- `failure_examples`: `artifacts/paper/v1.16-geml/ablations/failure-examples.json`
- `figure_metadata`: `artifacts/paper/v1.16-geml/ablations/figure-metadata.json`
- `reproduction`: `artifacts/paper/v1.16-geml/reproduction.md`

## Figures

- `family_recovery`: `artifacts/paper/v1.16-geml/ablations/figures/family-recovery.svg`
- `loss_before_after_snap`: `artifacts/paper/v1.16-geml/ablations/figures/loss-before-after-snap.svg`
- `branch_anomalies`: `artifacts/paper/v1.16-geml/ablations/figures/branch-anomalies.svg`
- `runtime`: `artifacts/paper/v1.16-geml/ablations/figures/runtime.svg`
- `representative_curves`: `artifacts/paper/v1.16-geml/ablations/figures/representative-curves.svg`

## Reproduction Commands

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign geml-v116-smoke --label v1.16-geml-smoke --overwrite
```

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign geml-v116-pilot --label v1.16-geml-pilot --overwrite
```

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli geml-v116-ladder --pilot-dir artifacts/campaigns/v1.16-geml-pilot --output-dir artifacts/campaigns/v1.16-geml-budget-ladder --overwrite
```

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli geml-paper-v116 --campaign-dir artifacts/campaigns/v1.16-geml-pilot --budget-ladder-dir artifacts/campaigns/v1.16-geml-budget-ladder --output-dir artifacts/paper/v1.16-geml --min-unique-seeds 3 --overwrite
```

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli geml-v116-ablations --campaign-dir artifacts/campaigns/v1.16-geml-pilot --budget-ladder-dir artifacts/campaigns/v1.16-geml-budget-ladder --package-dir artifacts/paper/v1.16-geml --output-dir artifacts/paper/v1.16-geml/ablations --overwrite
```

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli geml-v116-final --campaign-dir artifacts/campaigns/v1.16-geml-pilot --budget-ladder-dir artifacts/campaigns/v1.16-geml-budget-ladder --package-dir artifacts/paper/v1.16-geml --ablation-dir artifacts/paper/v1.16-geml/ablations --output-dir artifacts/paper/v1.16-geml/final-decision --overwrite
```
