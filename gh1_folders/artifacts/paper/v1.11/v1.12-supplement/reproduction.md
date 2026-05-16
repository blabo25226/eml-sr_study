# v1.12 Supplement Reproduction Commands

Run from the repository root.

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli paper-draft --output-dir artifacts/paper/v1.11/draft
PYTHONPATH=src python -m eml_symbolic_regression.cli paper-refresh --output-dir artifacts/campaigns/v1.12-evidence-refresh --overwrite
PYTHONPATH=src python -m eml_symbolic_regression.cli paper-figures --output-dir artifacts/paper/v1.11/draft
PYTHONPATH=src python -m eml_symbolic_regression.cli paper-probes --output-dir artifacts/paper/v1.11/draft
PYTHONPATH=src python -m eml_symbolic_regression.cli paper-supplement --output-dir artifacts/paper/v1.11/v1.12-supplement --overwrite
```

The baseline probe is optional and fail-closed: if no conventional symbolic-regression package is importable locally, the supplement records `unavailable` rather than installing dependencies.
