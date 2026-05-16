#!/usr/bin/env bash
set -euo pipefail

PYTHONPATH=src python -m eml_symbolic_regression.cli publication-rebuild \
  --output-dir artifacts/paper/v1.14 \
  --smoke \
  --overwrite \
  --allow-dirty
