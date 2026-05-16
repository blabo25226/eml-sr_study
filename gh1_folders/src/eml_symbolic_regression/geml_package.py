"""GEML/i*pi EML evidence package and claim-boundary artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from .benchmark import V115_GEML_TARGETS, builtin_suite


DEFAULT_GEML_PACKAGE_DIR = Path("artifacts") / "paper" / "v1.15-geml"
DEFAULT_THEORY_DIR = Path("artifacts") / "theory" / "v1.15"
DEFAULT_SMOKE_CAMPAIGN_DIR = Path("artifacts") / "campaigns" / "v1.15-geml-oscillatory-smoke"


class GemlPackageError(RuntimeError):
    """Raised when the GEML evidence package cannot be written safely."""


@dataclass(frozen=True)
class GemlEvidencePackagePaths:
    output_dir: Path
    manifest_json: Path
    benchmark_manifest_json: Path
    source_locks_json: Path
    target_family_json: Path
    target_family_csv: Path
    target_family_md: Path
    claim_audit_json: Path
    claim_audit_md: Path
    claim_boundary_md: Path
    reproduction_md: Path

    def as_dict(self) -> dict[str, str]:
        return {key: str(value) for key, value in self.__dict__.items()}


def geml_package_paths(output_dir: Path = DEFAULT_GEML_PACKAGE_DIR) -> GemlEvidencePackagePaths:
    output_dir = Path(output_dir)
    return GemlEvidencePackagePaths(
        output_dir=output_dir,
        manifest_json=output_dir / "manifest.json",
        benchmark_manifest_json=output_dir / "benchmark-manifests.json",
        source_locks_json=output_dir / "source-locks.json",
        target_family_json=output_dir / "target-family-classification.json",
        target_family_csv=output_dir / "target-family-classification.csv",
        target_family_md=output_dir / "target-family-classification.md",
        claim_audit_json=output_dir / "claim-audit.json",
        claim_audit_md=output_dir / "claim-audit.md",
        claim_boundary_md=output_dir / "claim-boundary.md",
        reproduction_md=output_dir / "reproduction.md",
    )


def write_geml_evidence_package(
    output_dir: Path = DEFAULT_GEML_PACKAGE_DIR,
    *,
    campaign_dir: Path | None = None,
    theory_dir: Path = DEFAULT_THEORY_DIR,
    overwrite: bool = False,
) -> GemlEvidencePackagePaths:
    output_dir = Path(output_dir)
    theory_dir = Path(theory_dir)
    paths = geml_package_paths(output_dir)
    if paths.manifest_json.exists() and not overwrite:
        raise GemlPackageError(f"{paths.manifest_json} already exists; pass overwrite=True to refresh")
    paths.output_dir.mkdir(parents=True, exist_ok=True)

    campaign_dir = Path(campaign_dir) if campaign_dir is not None else DEFAULT_SMOKE_CAMPAIGN_DIR
    benchmark_manifest = _benchmark_manifest_payload()
    _write_json(paths.benchmark_manifest_json, benchmark_manifest)
    theory_json_path = theory_dir / "ipi-restricted-theory.json"
    theory_payload = _read_json(theory_json_path) if theory_json_path.is_file() else {}

    paired_rows = _read_paired_rows(campaign_dir)
    paired_summary = _read_json(campaign_dir / "tables" / "geml-paired-summary.json") if (campaign_dir / "tables" / "geml-paired-summary.json").is_file() else _empty_paired_summary()
    classification = _target_family_classification(paired_rows, benchmark_manifest)
    decision = _decision_payload(paired_summary, classification)
    _write_json(paths.target_family_json, {"schema": "eml.v115_geml_target_family_classification.v1", "rows": classification})
    _write_csv(paths.target_family_csv, classification, _TARGET_FAMILY_COLUMNS)
    paths.target_family_md.write_text(_target_family_markdown(classification), encoding="utf-8")

    claim_boundary = _claim_boundary_markdown(decision, classification, campaign_dir)
    paths.claim_boundary_md.write_text(claim_boundary, encoding="utf-8")
    claim_audit = build_geml_claim_audit(
        claim_boundary,
        paired_summary=paired_summary,
        benchmark_manifest=benchmark_manifest,
        theory_payload=theory_payload,
    )
    _write_json(paths.claim_audit_json, claim_audit)
    paths.claim_audit_md.write_text(_claim_audit_markdown(claim_audit), encoding="utf-8")
    paths.reproduction_md.write_text(_reproduction_markdown(campaign_dir), encoding="utf-8")

    input_locks = _source_locks(
        [
            ("roadmap", Path(".planning/ROADMAP.md")),
            ("requirements", Path(".planning/REQUIREMENTS.md")),
            ("ipi_restricted_theory_json", theory_dir / "ipi-restricted-theory.json"),
            ("ipi_restricted_theory_md", theory_dir / "ipi-restricted-theory.md"),
            ("phase_83_verification", Path(".planning/phases/83-i-pi-eml-restricted-theory-and-branch-contract/83-VERIFICATION.md")),
            ("phase_85_verification", Path(".planning/phases/85-oscillatory-benchmark-pack-and-negative-controls/85-VERIFICATION.md")),
            ("phase_86_verification", Path(".planning/phases/86-matched-eml-versus-i-pi-eml-campaign-runner/86-VERIFICATION.md")),
            ("campaign_manifest", campaign_dir / "campaign-manifest.json"),
            ("geml_paired_summary", campaign_dir / "tables" / "geml-paired-summary.json"),
            ("geml_paired_comparison", campaign_dir / "tables" / "geml-paired-comparison.csv"),
        ],
        role="input",
    )
    output_locks = _source_locks(
        [
            ("benchmark_manifests", paths.benchmark_manifest_json),
            ("target_family_json", paths.target_family_json),
            ("target_family_csv", paths.target_family_csv),
            ("target_family_md", paths.target_family_md),
            ("claim_audit_json", paths.claim_audit_json),
            ("claim_audit_md", paths.claim_audit_md),
            ("claim_boundary_md", paths.claim_boundary_md),
            ("reproduction_md", paths.reproduction_md),
        ],
        role="output",
    )
    lock_payload = {
        "schema": "eml.v115_geml_source_locks.v1",
        "inputs": input_locks,
        "outputs": output_locks,
    }
    _write_json(paths.source_locks_json, lock_payload)

    manifest = {
        "schema": "eml.v115_geml_evidence_package.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "claim_audit": {"status": claim_audit["status"], "json": str(paths.claim_audit_json), "markdown": str(paths.claim_audit_md)},
        "theory": {
            "json": str(theory_dir / "ipi-restricted-theory.json"),
            "markdown": str(theory_dir / "ipi-restricted-theory.md"),
        },
        "benchmark_manifests": str(paths.benchmark_manifest_json),
        "campaign_dir": str(campaign_dir),
        "paired_summary": paired_summary,
        "target_family_classification": {
            "json": str(paths.target_family_json),
            "csv": str(paths.target_family_csv),
            "markdown": str(paths.target_family_md),
        },
        "source_locks": str(paths.source_locks_json),
        "reproduction": str(paths.reproduction_md),
        "claim_boundary": str(paths.claim_boundary_md),
        "outputs": _source_locks(
            [
                ("source_locks", paths.source_locks_json),
                ("benchmark_manifests", paths.benchmark_manifest_json),
                ("target_family_json", paths.target_family_json),
                ("target_family_csv", paths.target_family_csv),
                ("target_family_md", paths.target_family_md),
                ("claim_audit_json", paths.claim_audit_json),
                ("claim_audit_md", paths.claim_audit_md),
                ("claim_boundary_md", paths.claim_boundary_md),
                ("reproduction_md", paths.reproduction_md),
            ],
            role="output",
            allow_missing=True,
        ),
    }
    _write_json(paths.manifest_json, manifest)
    return paths


def build_geml_claim_audit(
    claim_text: str,
    *,
    paired_summary: Mapping[str, Any] | None = None,
    benchmark_manifest: Mapping[str, Any] | None = None,
    theory_payload: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    paired_summary = paired_summary or {}
    benchmark_manifest = benchmark_manifest or {}
    theory_payload = theory_payload or {}
    lower_claim = claim_text.lower()
    checks = [
        _claim_check(
            "blocks_global_superiority_language",
            not _contains_any(claim_text, _GLOBAL_SUPERIORITY_PHRASES),
            "Claim boundary does not assert global raw/i*pi superiority.",
        ),
        _claim_check(
            "blocks_broad_blind_recovery_language",
            not _contains_any(claim_text, _BROAD_BLIND_RECOVERY_PHRASES),
            "Claim boundary does not assert broad blind-recovery capability.",
        ),
        _claim_check(
            "blocks_full_universality_language",
            not _contains_any(claim_text, _FULL_UNIVERSALITY_PHRASES),
            "Claim boundary does not assert full universality for i*pi EML.",
        ),
        _claim_check(
            "matched_protocol_referenced",
            "matched protocol" in lower_claim and _manifest_has_geml_suite(benchmark_manifest),
            "Claim boundary is tied to the declared matched protocol.",
        ),
        _claim_check(
            "restricted_theory_referenced",
            "restricted theory" in lower_claim and theory_payload.get("status") == "passed",
            "Claim boundary is tied to the restricted i*pi theory artifact.",
        ),
        _claim_check(
            "decision_is_bounded",
            any(token in lower_claim for token in ("promising", "negative", "inconclusive")),
            "Claim boundary states a bounded decision.",
        ),
        _claim_check(
            "paired_summary_available",
            "paired_rows" in paired_summary,
            "Claim audit has paired summary counts, even when no campaign rows were found.",
        ),
    ]
    return {
        "schema": "eml.v115_geml_claim_audit.v1",
        "status": "passed" if all(check["status"] == "passed" for check in checks) else "failed",
        "checks": checks,
    }


_GLOBAL_SUPERIORITY_PHRASES = (
    "global superiority",
    "globally better",
    "universally better",
    "strictly better than raw eml",
    "dominates raw eml",
)
_BROAD_BLIND_RECOVERY_PHRASES = (
    "broad blind recovery",
    "broad blind-recovery",
    "guaranteed blind recovery",
    "guaranteed blind-recovery",
    "solves blind recovery",
    "recovers arbitrary formulas",
    "reliably recovers arbitrary",
)
_FULL_UNIVERSALITY_PHRASES = (
    "full universality",
    "complete universality",
    "all elementary functions",
    "scientific-calculator universality",
    "scientific calculator universality",
)

_TARGET_FAMILY_COLUMNS = [
    "target_family",
    "declared_targets",
    "paired_rows",
    "ipi_recovery_wins",
    "raw_recovery_wins",
    "both_recovered",
    "neither_recovered",
    "loss_only_outcomes",
    "ipi_lower_post_snap_mse",
    "raw_lower_post_snap_mse",
    "decision_class",
]


def _benchmark_manifest_payload() -> dict[str, Any]:
    return {
        "schema": "eml.v115_geml_benchmark_manifests.v1",
        "suites": [
            builtin_suite("v1.15-geml-oscillatory-smoke").as_dict(),
            builtin_suite("v1.15-geml-oscillatory").as_dict(),
        ],
        "declared_targets": list(V115_GEML_TARGETS),
    }


def _read_paired_rows(campaign_dir: Path) -> list[dict[str, Any]]:
    path = campaign_dir / "tables" / "geml-paired-comparison.csv"
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _empty_paired_summary() -> dict[str, Any]:
    return {
        "schema": "eml.geml_paired_summary.v1",
        "paired_rows": 0,
        "raw_trained_exact_recovery": 0,
        "ipi_trained_exact_recovery": 0,
        "raw_trained_exact_recovery_rate": 0.0,
        "ipi_trained_exact_recovery_rate": 0.0,
        "ipi_recovery_wins": 0,
        "raw_recovery_wins": 0,
        "both_recovered": 0,
        "neither_recovered": 0,
        "loss_only_outcomes": 0,
        "ipi_lower_post_snap_mse": 0,
        "raw_lower_post_snap_mse": 0,
        "negative_control_pairs": 0,
        "target_families": {},
        "comparison_outcomes": {},
    }


def _target_family_classification(rows: list[Mapping[str, Any]], benchmark_manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    declared = _declared_target_families(benchmark_manifest)
    grouped: dict[str, list[Mapping[str, Any]]] = {}
    for row in rows:
        family = str(row.get("target_family") or "unknown")
        if family == "unknown":
            family = _family_from_formula(str(row.get("formula") or ""))
        grouped.setdefault(family, []).append(row)
    families = sorted(set(declared) | set(grouped))
    result: list[dict[str, Any]] = []
    for family in families:
        items = grouped.get(family, [])
        outcome_counts = _count_by_key(items, "comparison_outcome")
        loss_only_outcomes = outcome_counts.get("ipi_lower_post_snap_mse", 0) + outcome_counts.get("raw_lower_post_snap_mse", 0)
        row = {
            "target_family": family,
            "declared_targets": declared.get(family, 0),
            "paired_rows": len(items),
            "ipi_recovery_wins": outcome_counts.get("ipi_recovery_win", 0),
            "raw_recovery_wins": outcome_counts.get("raw_recovery_win", 0),
            "both_recovered": outcome_counts.get("both_recovered", 0),
            "neither_recovered": outcome_counts.get("neutral_no_recovery", 0) + loss_only_outcomes,
            "loss_only_outcomes": loss_only_outcomes,
            "ipi_lower_post_snap_mse": outcome_counts.get("ipi_lower_post_snap_mse", 0),
            "raw_lower_post_snap_mse": outcome_counts.get("raw_lower_post_snap_mse", 0),
        }
        row["decision_class"] = _family_decision(row)
        result.append(row)
    return result


def _declared_target_families(benchmark_manifest: Mapping[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    full_suite = (benchmark_manifest.get("suites") or [{}, {}])[-1]
    seen: set[str] = set()
    for case in full_suite.get("cases", []):
        formula = str(case.get("formula") or "")
        if formula in seen:
            continue
        seen.add(formula)
        family = _family_from_tags(case.get("tags", ()))
        counts[family] = counts.get(family, 0) + 1
    return counts


def _family_from_tags(tags: Iterable[Any]) -> str:
    values = {str(tag) for tag in tags}
    if "negative_control" in values:
        return "negative_control"
    if "log_periodic" in values:
        return "log_periodic"
    if "damped_oscillation" in values:
        return "damped_oscillation"
    if "standing_wave" in values:
        return "standing_wave"
    if "harmonic" in values:
        return "harmonic"
    if "periodic" in values:
        return "periodic"
    return "unknown"


def _family_from_formula(formula: str) -> str:
    if formula in {"exp", "log", "quadratic_polynomial", "rational_decay"}:
        return "negative_control"
    if formula == "log_periodic_oscillation":
        return "log_periodic"
    if formula == "damped_oscillator":
        return "damped_oscillation"
    if formula == "standing_wave_snapshot":
        return "standing_wave"
    if formula == "harmonic_sum":
        return "harmonic"
    if formula in {"sin_pi", "cos_pi"}:
        return "periodic"
    return "unknown"


def _family_decision(row: Mapping[str, Any]) -> str:
    if int(row.get("paired_rows") or 0) == 0:
        return "not_run"
    if int(row.get("ipi_recovery_wins") or 0) > int(row.get("raw_recovery_wins") or 0):
        return "ipi_win"
    if int(row.get("raw_recovery_wins") or 0) > int(row.get("ipi_recovery_wins") or 0):
        return "raw_win"
    if int(row.get("ipi_lower_post_snap_mse") or 0) > int(row.get("raw_lower_post_snap_mse") or 0):
        return "ipi_loss_only_signal"
    if int(row.get("raw_lower_post_snap_mse") or 0) > int(row.get("ipi_lower_post_snap_mse") or 0):
        return "raw_loss_only_signal"
    return "neutral"


def _decision_payload(paired_summary: Mapping[str, Any], classification: list[Mapping[str, Any]]) -> dict[str, Any]:
    paired_rows = int(paired_summary.get("paired_rows") or 0)
    full_target_count = len(V115_GEML_TARGETS)
    ipi_recovery_wins = int(paired_summary.get("ipi_recovery_wins") or 0)
    raw_recovery_wins = int(paired_summary.get("raw_recovery_wins") or 0)
    negative_control = next((row for row in classification if row.get("target_family") == "negative_control"), {})
    negative_control_ipi_wins = int(negative_control.get("ipi_recovery_wins") or 0)
    if paired_rows == 0:
        decision = "inconclusive_no_campaign"
        rationale = "No paired campaign rows were found; only theory and benchmark protocol are packaged."
    elif paired_rows < full_target_count:
        decision = "inconclusive_smoke_only"
        rationale = "Only a subset of the declared matched protocol has paired evidence."
    elif ipi_recovery_wins > raw_recovery_wins and negative_control_ipi_wins == 0:
        decision = "promising"
        rationale = "i*pi EML has more verifier-gated recovery wins than raw EML under the matched protocol."
    elif ipi_recovery_wins > raw_recovery_wins:
        decision = "inconclusive_negative_control_confounded"
        rationale = "i*pi EML has more verifier-gated wins, but negative-control rows prevent an oscillatory-family interpretation."
    elif raw_recovery_wins > ipi_recovery_wins:
        decision = "negative"
        rationale = "Raw EML has more verifier-gated recovery wins than i*pi EML under the matched protocol."
    else:
        decision = "inconclusive"
        rationale = "Matched results do not separate i*pi EML from raw EML by verifier-gated recovery wins."
    return {
        "decision": decision,
        "rationale": rationale,
        "paired_rows": paired_rows,
        "declared_targets": full_target_count,
        "families": {row["target_family"]: row["decision_class"] for row in classification},
    }


def _claim_boundary_markdown(decision: Mapping[str, Any], classification: list[Mapping[str, Any]], campaign_dir: Path) -> str:
    lines = [
        "# GEML/i*pi EML Claim Boundary",
        "",
        f"Decision: `{decision['decision']}`.",
        "",
        decision["rationale"],
        "",
        "This package supports only bounded statements about the declared matched protocol and the restricted theory note. It does not support wider comparative claims, unrestricted blind-recovery claims, or complete-function coverage claims.",
        "",
        f"Campaign directory considered: `{campaign_dir}`",
        "",
        "## Included Evidence",
        "",
        "- Restricted theory note for the i*pi branch contract.",
        "- Benchmark manifests for the smoke and full matched protocols.",
        "- Target-family aggregate tables, including negative-control rows.",
        "- Source locks and reproduction commands for the packaged artifacts.",
        "",
        "## Target Families",
        "",
        "| Family | Declared Targets | Paired Rows | i*pi Wins | Raw Wins | Both | Neither | Loss-Only | Class |",
        "|--------|------------------|-------------|-----------|----------|------|---------|-----------|-------|",
    ]
    for row in classification:
        lines.append(
            "| {target_family} | {declared_targets} | {paired_rows} | {ipi_recovery_wins} | {raw_recovery_wins} | {both_recovered} | {neither_recovered} | {loss_only_outcomes} | {decision_class} |".format(
                **row
            )
        )
    lines.append("")
    return "\n".join(lines)


def _target_family_markdown(rows: list[Mapping[str, Any]]) -> str:
    lines = [
        "# GEML Target-Family Classification",
        "",
        "| Family | Declared Targets | Paired Rows | i*pi Wins | Raw Wins | Both | Neither | Loss-Only | i*pi Lower Loss | Raw Lower Loss | Class |",
        "|--------|------------------|-------------|-----------|----------|------|---------|-----------|----------------|----------------|-------|",
    ]
    for row in rows:
        lines.append(
            "| {target_family} | {declared_targets} | {paired_rows} | {ipi_recovery_wins} | {raw_recovery_wins} | {both_recovered} | {neither_recovered} | {loss_only_outcomes} | {ipi_lower_post_snap_mse} | {raw_lower_post_snap_mse} | {decision_class} |".format(
                **row
            )
        )
    lines.append("")
    return "\n".join(lines)


def _reproduction_markdown(campaign_dir: Path) -> str:
    return "\n".join(
        [
            "# Reproducing the GEML Evidence Package",
            "",
            "Run the cheap smoke campaign:",
            "",
            "```bash",
            "PYTHONPATH=src python -m eml_symbolic_regression.cli campaign geml-oscillatory-smoke --label v1.15-geml-oscillatory-smoke --overwrite",
            "```",
            "",
            "Run the full matched protocol when ready:",
            "",
            "```bash",
            "PYTHONPATH=src python -m eml_symbolic_regression.cli campaign geml-oscillatory --label v1.15-geml-oscillatory --overwrite",
            "```",
            "",
            "Refresh this package:",
            "",
            "```bash",
            f"PYTHONPATH=src python -m eml_symbolic_regression.cli geml-package --campaign-dir {campaign_dir} --overwrite",
            "```",
            "",
        ]
    )


def _claim_check(check_id: str, passed: bool, description: str) -> dict[str, Any]:
    return {"id": check_id, "status": "passed" if passed else "failed", "description": description}


def _contains_any(text: str, phrases: Iterable[str]) -> bool:
    lower = text.lower()
    return any(phrase in lower for phrase in phrases)


def _manifest_has_geml_suite(benchmark_manifest: Mapping[str, Any]) -> bool:
    suites = benchmark_manifest.get("suites")
    if not isinstance(suites, list):
        return False
    suite_ids = {str(suite.get("id") or "") for suite in suites if isinstance(suite, Mapping)}
    return {"v1.15-geml-oscillatory-smoke", "v1.15-geml-oscillatory"} <= suite_ids


def _claim_audit_markdown(audit: Mapping[str, Any]) -> str:
    lines = ["# GEML Claim Audit", "", f"Status: `{audit.get('status')}`", "", "| Check | Status | Description |", "|-------|--------|-------------|"]
    for check in audit.get("checks", []):
        lines.append(f"| {check['id']} | {check['status']} | {check['description']} |")
    lines.append("")
    return "\n".join(lines)


def _count_by_key(rows: list[Mapping[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key) or "")
        counts[value] = counts.get(value, 0) + 1
    return counts


def _source_locks(items: Iterable[tuple[str, Path]], *, role: str, allow_missing: bool = False) -> list[dict[str, Any]]:
    locks: list[dict[str, Any]] = []
    for source_id, path in items:
        if not path.is_file():
            if allow_missing:
                continue
            locks.append({"source_id": source_id, "role": role, "path": str(path), "status": "missing"})
            continue
        locks.append(
            {
                "source_id": source_id,
                "role": role,
                "path": str(path),
                "status": "locked",
                "sha256": _sha256(path),
                "bytes": path.stat().st_size,
            }
        )
    return locks


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[Mapping[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fieldnames})
