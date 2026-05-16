# Corrected Publication Rebuild

Mode: `full`

Run:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli publication-rebuild --output-dir artifacts/paper/v1.14 --overwrite --allow-dirty
```

The full rebuild regenerates v1.13 paper-track evidence, matched baseline context, dataset manifests, claim audit, and release-gate artifacts.
Output root: `artifacts/paper/v1.14`
