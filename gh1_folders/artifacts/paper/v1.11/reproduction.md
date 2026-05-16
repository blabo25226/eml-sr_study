# v1.11 Reproduction Commands

Run from the repository root.

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli raw-hybrid-paper --preset v1.11-paper-evidence-package --output-dir artifacts/paper/v1.11/raw-hybrid --require-existing --overwrite
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign paper-training --label v1.11-paper-training --overwrite
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign paper-probes --label v1.11-logistic-planck-probes --overwrite
PYTHONPATH=src python -m eml_symbolic_regression.cli diagnostics paper-ablations --output-dir artifacts/diagnostics/v1.11-paper-ablations
PYTHONPATH=src python -m eml_symbolic_regression.cli paper-assets --output-dir artifacts/paper/v1.11/assets
PYTHONPATH=src python -m eml_symbolic_regression.cli paper-package --output-dir artifacts/paper/v1.11 --overwrite
```
