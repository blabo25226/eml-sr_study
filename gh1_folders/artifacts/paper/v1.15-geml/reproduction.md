# Reproducing the GEML Evidence Package

Run the cheap smoke campaign:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign geml-oscillatory-smoke --label v1.15-geml-oscillatory-smoke --overwrite
```

Run the full matched protocol when ready:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign geml-oscillatory --label v1.15-geml-oscillatory --overwrite
```

Refresh this package:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli geml-package --campaign-dir artifacts/campaigns/v1.15-geml-oscillatory-smoke --overwrite
```
