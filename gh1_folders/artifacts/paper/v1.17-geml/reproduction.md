# v1.17 Reproduction

Run the staged package rebuild in order:

1.

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli geml-v117-snap-diagnostics --output-dir artifacts/paper/v1.17-geml/snap-diagnostics --campaign-dir artifacts/campaigns/v1.16-geml-pilot --overwrite
```

2.

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli geml-v117-neighborhoods --output-dir artifacts/paper/v1.17-geml/neighborhoods --snap-diagnostics-dir artifacts/paper/v1.17-geml/snap-diagnostics --overwrite
```

3.

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli geml-v117-rank-candidates --output-dir artifacts/paper/v1.17-geml/ranking --neighborhoods-dir artifacts/paper/v1.17-geml/neighborhoods --overwrite
```

4.

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli geml-v117-sandbox --output-dir artifacts/paper/v1.17-geml/sandbox --ranking-dir artifacts/paper/v1.17-geml/ranking --overwrite
```

5.

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli geml-v117-package --output-dir artifacts/paper/v1.17-geml --snap-diagnostics-dir artifacts/paper/v1.17-geml/snap-diagnostics --neighborhoods-dir artifacts/paper/v1.17-geml/neighborhoods --ranking-dir artifacts/paper/v1.17-geml/ranking --sandbox-dir artifacts/paper/v1.17-geml/sandbox --v116-package-dir artifacts/paper/v1.16-geml --overwrite
```
