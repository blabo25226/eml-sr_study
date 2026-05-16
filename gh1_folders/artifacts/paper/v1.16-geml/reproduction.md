# Reproducing the v1.16 GEML Decision Package

Run the v1.16 pilot campaign:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign geml-v116-pilot --label v1.16-geml-pilot --overwrite
```

Refresh this package:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli geml-paper-v116 --campaign-dir artifacts/campaigns/v1.16-geml-pilot --min-unique-seeds 3 --overwrite
```
