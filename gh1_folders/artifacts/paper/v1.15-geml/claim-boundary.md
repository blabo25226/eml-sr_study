# GEML/i*pi EML Claim Boundary

Decision: `inconclusive_smoke_only`.

Only a subset of the declared matched protocol has paired evidence.

This package supports only bounded statements about the declared matched protocol and the restricted theory note. It does not support wider comparative claims, unrestricted blind-recovery claims, or complete-function coverage claims.

Campaign directory considered: `artifacts/campaigns/v1.15-geml-oscillatory-smoke`

## Included Evidence

- Restricted theory note for the i*pi branch contract.
- Benchmark manifests for the smoke and full matched protocols.
- Target-family aggregate tables, including negative-control rows.
- Source locks and reproduction commands for the packaged artifacts.

## Target Families

| Family | Declared Targets | Paired Rows | i*pi Wins | Raw Wins | Both | Neither | Loss-Only | Class |
|--------|------------------|-------------|-----------|----------|------|---------|-----------|-------|
| damped_oscillation | 1 | 0 | 0 | 0 | 0 | 0 | 0 | not_run |
| harmonic | 1 | 0 | 0 | 0 | 0 | 0 | 0 | not_run |
| log_periodic | 1 | 0 | 0 | 0 | 0 | 0 | 0 | not_run |
| negative_control | 4 | 1 | 0 | 0 | 0 | 1 | 1 | raw_loss_only_signal |
| periodic | 2 | 1 | 0 | 0 | 0 | 1 | 1 | ipi_loss_only_signal |
| standing_wave | 1 | 0 | 0 | 0 | 0 | 0 | 0 | not_run |
