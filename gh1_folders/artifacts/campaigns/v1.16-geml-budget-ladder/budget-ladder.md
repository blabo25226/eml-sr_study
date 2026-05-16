# v1.16 GEML Budget Ladder

Decision: `stop_full_campaign_fail_closed`

Pilot did not show clean verifier-gated i*pi exact recovery signal; full campaign should not run.

| Tier | Status | Pairs | i*pi Wins | Raw Wins | Loss-Only | Source Locks |
|------|--------|-------|-----------|----------|-----------|--------------|
| smoke | performed | 2 | 0 | 0 | 2 | True |
| pilot | performed | 12 | 0 | 0 | 12 | True |
| full | blocked |  |  |  |  |  |

## Commands

### smoke

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign geml-v116-smoke --label v1.16-geml-smoke --overwrite
```

### pilot

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign geml-v116-pilot --label v1.16-geml-pilot --overwrite
```

### full

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign geml-v116-full --label v1.16-geml-full --overwrite
```
