#!/usr/bin/env python3
"""Validate CI and public snapshot branch contracts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


DEV_REQUIRED_PATHS = (
    "pyproject.toml",
    "README.md",
    "src/eml_symbolic_regression",
    "tests",
    ".github/workflows/ci.yml",
    ".github/workflows/publish-main.yml",
    "scripts/publication-rebuild.sh",
    "scripts/validate-ci-contract.py",
    "Dockerfile",
    "requirements-lock.txt",
    ".planning/ROADMAP.md",
    "sources/NORTH_STAR.md",
)

PUBLIC_REQUIRED_PATHS = (
    "pyproject.toml",
    "README.md",
    "src/eml_symbolic_regression",
    "tests",
)

PUBLIC_FORBIDDEN_PATHS = (
    "AGENTS.md",
    ".github",
    ".planning",
    "sources",
    "docs",
)


def validate_dev(root: Path) -> list[str]:
    errors = _missing_errors(root, DEV_REQUIRED_PATHS)
    ci_text = _read_text(root / ".github" / "workflows" / "ci.yml")
    publish_text = _read_text(root / ".github" / "workflows" / "publish-main.yml")

    for token in ("tests/test_semantics_expression.py", "tests/test_verify.py", "tests/test_evidence_regression.py"):
        if token not in ci_text:
            errors.append(f"CI workflow does not run {token}")
    for token in ("dev", "main", "publication-rebuild", "public-snapshot"):
        if token not in ci_text:
            errors.append(f"CI workflow missing {token!r} contract")
    if "branches:" not in publish_text or "- dev" not in publish_text:
        errors.append("publish-main workflow must be restricted to dev pushes")
    if "--force-with-lease" not in publish_text:
        errors.append("publish-main workflow must use --force-with-lease")
    if "git rm -r -f --ignore-unmatch \\" not in publish_text or "\n            .github \\" not in publish_text:
        errors.append("publish-main workflow must remove .github from public main")
    if 'git commit -m "Update"' not in publish_text:
        errors.append("publish-main workflow must use the public commit subject 'Update'")
    return errors


def validate_public_snapshot(root: Path) -> list[str]:
    errors = _missing_errors(root, PUBLIC_REQUIRED_PATHS)
    for relative in PUBLIC_FORBIDDEN_PATHS:
        if (root / relative).exists():
            errors.append(f"public snapshot must not contain {relative}")

    artifacts = root / "artifacts"
    if artifacts.exists():
        forbidden = sorted(_forbidden_public_artifacts(artifacts))
        errors.extend(f"public snapshot must not contain {path}" for path in forbidden[:25])
        if len(forbidden) > 25:
            errors.append(f"public snapshot has {len(forbidden) - 25} additional forbidden artifact paths")
    return errors


def _missing_errors(root: Path, required_paths: tuple[str, ...]) -> list[str]:
    return [f"required path missing: {relative}" for relative in required_paths if not (root / relative).exists()]


def _forbidden_public_artifacts(artifacts: Path) -> set[str]:
    forbidden: set[str] = set()
    for path in artifacts.rglob("*"):
        relative = path.relative_to(artifacts)
        parts = relative.parts
        if path.name == ".DS_Store":
            forbidden.add(str(Path("artifacts") / relative))
        if "runs" in parts or "raw-runs" in parts:
            forbidden.add(str(Path("artifacts") / relative))
        if path.is_file() and (
            path.name in {"suite-result.json", "aggregate.json"}
            or path.name.endswith("-suite-result.json")
            or path.name.endswith("-aggregate.json")
            or path.name in {"training-step-traces.json", "training-step-traces.csv", "training-step-traces.md"}
        ):
            forbidden.add(str(Path("artifacts") / relative))
        if "paper" in parts and "sources" in parts:
            forbidden.add(str(Path("artifacts") / relative))
    return forbidden


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("dev", "public-snapshot"), required=True)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args(argv)

    root = args.root.resolve()
    errors = validate_dev(root) if args.mode == "dev" else validate_public_snapshot(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"{args.mode}: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
