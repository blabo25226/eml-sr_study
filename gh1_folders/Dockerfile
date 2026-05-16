FROM python:3.11-slim

WORKDIR /app

COPY requirements-lock.txt ./requirements-lock.txt
RUN python -m pip install --no-cache-dir -r requirements-lock.txt

COPY pyproject.toml README.md ./
COPY src ./src
COPY sources ./sources
COPY scripts ./scripts

ENV PYTHONPATH=src

CMD ["python", "-m", "eml_symbolic_regression.cli", "publication-rebuild", "--output-dir", "artifacts/paper/v1.13", "--smoke", "--overwrite", "--allow-dirty"]
