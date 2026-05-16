"""Executable restricted theory checks for i*pi EML."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import mpmath as mp

THEORY_SCHEMA = "eml.ipi_restricted_theory.v1"


@dataclass(frozen=True)
class TheoryArtifactPaths:
    json_path: Path
    markdown_path: Path

    def as_dict(self) -> dict[str, str]:
        return {"json_path": str(self.json_path), "markdown_path": str(self.markdown_path)}


def ipi_eml_value(x: Any, y: Any) -> mp.mpc:
    """Evaluate i*pi EML with high-precision mpmath pi."""

    a = mp.j * mp.pi
    return mp.e ** (a * mp.mpc(x)) - mp.log(mp.mpc(y)) / a


def build_ipi_restricted_theory(
    *,
    y_samples: Iterable[str | float] = ("0.25", "0.5", "1.0", "2.0", "5.0"),
    u_samples: Iterable[str | float] = ("-0.5", "-0.25", "0.0", "0.25", "0.5"),
    tolerance: str = "1e-60",
) -> dict[str, Any]:
    """Build executable checks for the restricted i*pi EML theory contract."""

    previous_dps = mp.mp.dps
    mp.mp.dps = 100
    try:
        tol = mp.mpf(tolerance)
        ys = _positive_real_samples(y_samples, name="y_samples")
        us = _real_samples(u_samples, name="u_samples")
        checks = [
            _reciprocal_check(ys, tol),
            _nested_recovery_check(ys, tol),
            _derivative_check(us, tol),
            _composition_bound_check(us, ys, tol),
        ]
    finally:
        mp.mp.dps = previous_dps

    return {
        "schema": THEORY_SCHEMA,
        "operator": "ipi_eml",
        "branch_convention": "principal complex log with cut on the negative real axis",
        "assumptions": [
            "second-slot identity inputs use y > 0",
            "real-axis derivative and composition checks use real x or u",
            "v > 0 for one-step composition magnitude bounds",
            "mpmath principal log is the executable oracle",
        ],
        "non_claims": [
            "does not prove full scientific-calculator universality",
            "does not prove global closure across complex branch cuts",
            "does not justify benchmark claims outside declared branch-safe domains",
        ],
        "checks": checks,
        "status": "passed" if all(check["passed"] for check in checks) else "failed",
    }


def write_ipi_restricted_theory(output_dir: Path = Path("artifacts") / "theory" / "v1.15") -> TheoryArtifactPaths:
    """Write JSON and Markdown artifacts for the i*pi restricted theory contract."""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = build_ipi_restricted_theory()
    json_path = output_dir / "ipi-restricted-theory.json"
    markdown_path = output_dir / "ipi-restricted-theory.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    markdown_path.write_text(render_ipi_restricted_theory_markdown(payload), encoding="utf-8")
    return TheoryArtifactPaths(json_path=json_path, markdown_path=markdown_path)


def render_ipi_restricted_theory_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# i*pi EML Restricted Theory",
        "",
        f"- Schema: `{payload['schema']}`",
        f"- Status: `{payload['status']}`",
        f"- Branch convention: {payload['branch_convention']}",
        "",
        "## Assumptions",
        "",
        *[f"- {item}" for item in payload["assumptions"]],
        "",
        "## Checked Identities",
        "",
        "| Check | Status | Max error | Statement |",
        "|-------|--------|-----------|-----------|",
    ]
    for check in payload["checks"]:
        lines.append(
            f"| `{check['id']}` | `{check['status']}` | `{check['max_error']}` | {check['statement']} |"
        )
    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            *[f"- {item}" for item in payload["non_claims"]],
            "",
        ]
    )
    return "\n".join(lines)


def _reciprocal_check(ys: list[mp.mpf], tolerance: mp.mpf) -> dict[str, Any]:
    errors = []
    for y in ys:
        actual = ipi_eml_value(ipi_eml_value(1, y), 1)
        expected = -1 / y
        errors.append(abs(actual - expected))
    return _check(
        "THRY-01",
        "i*pi EML(i*pi EML(1, y), 1) = -1/y for y > 0",
        errors,
        tolerance,
    )


def _nested_recovery_check(ys: list[mp.mpf], tolerance: mp.mpf) -> dict[str, Any]:
    errors = []
    for y in ys:
        reciprocal = ipi_eml_value(ipi_eml_value(1, y), 1)
        recovered = -1 / reciprocal
        errors.append(abs(recovered - y))
    return _check(
        "THRY-02",
        "-1 / i*pi EML(i*pi EML(1, y), 1) recovers y for y > 0",
        errors,
        tolerance,
    )


def _derivative_check(us: list[mp.mpf], tolerance: mp.mpf) -> dict[str, Any]:
    errors = []
    for x in us:
        derivative = mp.diff(lambda z: ipi_eml_value(z, 1), x)
        expected = mp.j * mp.pi * mp.e ** (mp.j * mp.pi * x)
        errors.append(abs(derivative - expected))
        errors.append(abs(abs(expected) - mp.pi))
    return _check(
        "THRY-03",
        "d/dx i*pi EML(x, y) = i*pi*exp(i*pi*x), with magnitude pi for real x",
        errors,
        tolerance,
    )


def _composition_bound_check(us: list[mp.mpf], ys: list[mp.mpf], tolerance: mp.mpf) -> dict[str, Any]:
    errors = []
    bound_failures = 0
    for u in us:
        for v in ys:
            actual = abs(ipi_eml_value(ipi_eml_value(u, v), 1))
            lower = mp.e ** (-mp.pi) / v
            upper = mp.e ** mp.pi / v
            if actual + tolerance < lower or actual - tolerance > upper:
                bound_failures += 1
            identity = mp.e ** (mp.j * mp.pi * mp.e ** (mp.j * mp.pi * u)) / v
            errors.append(abs(ipi_eml_value(ipi_eml_value(u, v), 1) - identity))
    check = _check(
        "THRY-04",
        "exp(-pi)/v <= |i*pi EML(i*pi EML(u, v), 1)| <= exp(pi)/v for real u and v > 0",
        errors,
        tolerance,
    )
    check["bound_failures"] = bound_failures
    check["passed"] = bool(check["passed"] and bound_failures == 0)
    check["status"] = "passed" if check["passed"] else "failed"
    return check


def _check(check_id: str, statement: str, errors: list[mp.mpf], tolerance: mp.mpf) -> dict[str, Any]:
    if not errors:
        raise ValueError(f"{check_id} did not evaluate any sample points")
    max_error = max(errors) if errors else mp.mpf("0")
    passed = max_error <= tolerance
    return {
        "id": check_id,
        "statement": statement,
        "max_error": mp.nstr(max_error, 12),
        "tolerance": mp.nstr(tolerance, 12),
        "passed": bool(passed),
        "status": "passed" if passed else "failed",
    }


def _real_samples(values: Iterable[str | float], *, name: str) -> list[mp.mpf]:
    samples = [mp.mpf(str(value)) for value in values]
    if not samples:
        raise ValueError(f"{name} must not be empty")
    if any(not mp.isfinite(value) for value in samples):
        raise ValueError(f"{name} must contain only finite real values")
    return samples


def _positive_real_samples(values: Iterable[str | float], *, name: str) -> list[mp.mpf]:
    samples = _real_samples(values, name=name)
    if any(value <= 0 for value in samples):
        raise ValueError(f"{name} must contain only positive real values")
    return samples
