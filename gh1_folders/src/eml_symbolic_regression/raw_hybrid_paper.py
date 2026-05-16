"""Raw-hybrid paper package synthesis from locked evidence artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


RAW_HYBRID_PAPER_PRESET_ID = "v1.9-raw-hybrid-paper"
V111_RAW_HYBRID_PAPER_PRESET_ID = "v1.11-paper-evidence-package"
DEFAULT_RAW_HYBRID_OUTPUT_DIR = Path("artifacts") / "paper" / "v1.9" / "raw-hybrid"
DEFAULT_V111_RAW_HYBRID_OUTPUT_DIR = Path("artifacts") / "paper" / "v1.11" / "raw-hybrid"
REGIME_KEYS = (
    "pure_blind",
    "scaffolded",
    "compile_only",
    "warm_start",
    "same_ast_return",
    "repaired",
    "refit",
    "perturbed_basin",
)
SCIENTIFIC_LAW_COLUMNS = (
    "law",
    "formula",
    "compile_support",
    "compile_depth",
    "macro_hits",
    "warm_start_status",
    "verifier_status",
    "evidence_regime",
    "artifact_path",
)
EXPECTED_RAW_HYBRID_OUTPUTS = {
    "manifest.json",
    "source-locks.json",
    "regime-summary.json",
    "raw-hybrid-report.md",
    "scientific-law-table.json",
    "scientific-law-table.csv",
    "scientific-law-table.md",
    "claim-ledger.json",
    "claim-boundaries.md",
    "centered-negative-diagnostics.md",
}


class RawHybridPaperError(RuntimeError):
    """Raised when the raw-hybrid paper package cannot be generated safely."""


@dataclass(frozen=True, kw_only=True)
class RawHybridSource:
    source_id: str
    role: str
    path: Path
    required: bool = True
    preset_id: str = RAW_HYBRID_PAPER_PRESET_ID
    description: str = ""
    law: str | None = None
    evidence_regime: str | None = None

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "preset_id": self.preset_id,
            "source_id": self.source_id,
            "role": self.role,
            "path": str(self.path),
            "required": self.required,
        }
        if self.description:
            payload["description"] = self.description
        if self.law is not None:
            payload["law"] = self.law
        if self.evidence_regime is not None:
            payload["evidence_regime"] = self.evidence_regime
        return payload


@dataclass(frozen=True, kw_only=True)
class RawHybridPaperPreset:
    preset_id: str
    output_dir: Path
    title: str
    description: str
    sources: tuple[RawHybridSource, ...]


@dataclass(frozen=True)
class RawHybridPaperPaths:
    output_dir: Path
    manifest_json: Path
    source_locks_json: Path
    regime_summary_json: Path
    raw_hybrid_report_md: Path
    scientific_law_table_json: Path
    scientific_law_table_csv: Path
    scientific_law_table_md: Path
    claim_ledger_json: Path
    claim_boundaries_md: Path
    centered_negative_diagnostics_md: Path

    def as_dict(self) -> dict[str, str]:
        return {
            "output_dir": str(self.output_dir),
            "manifest_json": str(self.manifest_json),
            "source_locks_json": str(self.source_locks_json),
            "regime_summary_json": str(self.regime_summary_json),
            "raw_hybrid_report_md": str(self.raw_hybrid_report_md),
            "scientific_law_table_json": str(self.scientific_law_table_json),
            "scientific_law_table_csv": str(self.scientific_law_table_csv),
            "scientific_law_table_md": str(self.scientific_law_table_md),
            "claim_ledger_json": str(self.claim_ledger_json),
            "claim_boundaries_md": str(self.claim_boundaries_md),
            "centered_negative_diagnostics_md": str(self.centered_negative_diagnostics_md),
        }


def default_raw_hybrid_sources() -> tuple[RawHybridSource, ...]:
    """Return the locked evidence inputs for the v1.9 raw-hybrid paper package."""

    proof_root = Path("artifacts") / "proof" / "v1.6" / "campaigns"
    v18_paper = Path("artifacts") / "paper" / "v1.8"
    arrhenius_root = Path("artifacts") / "campaigns" / "v1.9-arrhenius-evidence" / "v1.9-arrhenius-evidence"
    michaelis_root = Path("artifacts") / "campaigns" / "v1.9-michaelis-evidence" / "v1.9-michaelis-evidence"
    repair_root = Path("artifacts") / "campaigns" / "v1.9-repair-evidence"
    standard_runs = Path("artifacts") / "campaigns" / "v1.6-standard" / "runs" / "v1.3-standard"
    return (
        RawHybridSource(
            source_id="proof-shallow-pure-blind-aggregate",
            role="proof_aggregate",
            path=proof_root / "proof-shallow-pure-blind" / "aggregate.json",
            description="v1.6 shallow pure-blind measured boundary aggregate.",
            evidence_regime="pure_blind",
        ),
        RawHybridSource(
            source_id="proof-shallow-scaffolded-aggregate",
            role="proof_aggregate",
            path=proof_root / "proof-shallow" / "aggregate.json",
            description="v1.6 shallow scaffolded recovery aggregate.",
            evidence_regime="scaffolded",
        ),
        RawHybridSource(
            source_id="proof-perturbed-basin-aggregate",
            role="proof_aggregate",
            path=proof_root / "proof-basin" / "aggregate.json",
            description="v1.6 perturbed true-tree basin aggregate.",
            evidence_regime="perturbed_basin",
        ),
        RawHybridSource(
            source_id="proof-basin-probes-aggregate",
            role="proof_aggregate",
            path=proof_root / "proof-basin-probes" / "aggregate.json",
            description="v1.6 Beer-Lambert basin probe aggregate with repaired candidates separated.",
            evidence_regime="perturbed_basin",
        ),
        RawHybridSource(
            source_id="proof-depth-curve-aggregate",
            role="proof_aggregate",
            path=proof_root / "proof-depth-curve" / "aggregate.json",
            description="v1.6 depth-curve measured boundary aggregate.",
            evidence_regime="pure_blind",
        ),
        RawHybridSource(
            source_id="v1.8-centered-decision-json",
            role="centered_negative_diagnostic",
            path=v18_paper / "decision-memo.json",
            description="v1.8 centered-family decision payload.",
        ),
        RawHybridSource(
            source_id="v1.8-centered-decision-markdown",
            role="centered_negative_diagnostic",
            path=v18_paper / "decision-memo.md",
            description="v1.8 centered-family decision memo.",
        ),
        RawHybridSource(
            source_id="v1.8-centered-completeness-boundary",
            role="centered_negative_diagnostic",
            path=v18_paper / "completeness-boundary.md",
            description="v1.8 centered-family completeness caveat.",
        ),
        RawHybridSource(
            source_id="v1.9-arrhenius-aggregate",
            role="scientific_law_aggregate",
            path=arrhenius_root / "aggregate.json",
            description="v1.9 Arrhenius exact compiler warm-start aggregate.",
            law="arrhenius",
            evidence_regime="same_ast_return",
        ),
        RawHybridSource(
            source_id="v1.9-arrhenius-run",
            role="scientific_law_run",
            path=arrhenius_root / "v1-9-arrhenius-evidence-arrhenius-warm-75f6e9c1764d.json",
            description="v1.9 Arrhenius exact compiler warm-start run artifact.",
            law="arrhenius",
            evidence_regime="same_ast_return",
        ),
        RawHybridSource(
            source_id="v1.9-michaelis-aggregate",
            role="scientific_law_aggregate",
            path=michaelis_root / "aggregate.json",
            description="v1.9 Michaelis-Menten exact compiler warm-start aggregate.",
            law="michaelis_menten",
            evidence_regime="same_ast_return",
        ),
        RawHybridSource(
            source_id="v1.9-michaelis-run",
            role="scientific_law_run",
            path=michaelis_root / "v1-9-michaelis-evidence-michaelis-warm-a67d8ccfb108.json",
            description="v1.9 Michaelis-Menten exact compiler warm-start run artifact.",
            law="michaelis_menten",
            evidence_regime="same_ast_return",
        ),
        RawHybridSource(
            source_id="v1.9-repair-aggregate",
            role="repair_evidence",
            path=repair_root / "v1.9-repair-evidence" / "aggregate.json",
            description="v1.9 expanded cleanup repair evidence aggregate.",
            evidence_regime="repaired",
        ),
        RawHybridSource(
            source_id="v1.9-repair-summary-json",
            role="repair_evidence",
            path=repair_root / "repair-evidence-summary.json",
            description="v1.9 expanded cleanup repair summary payload.",
            evidence_regime="repaired",
        ),
        RawHybridSource(
            source_id="v1.9-repair-summary-markdown",
            role="repair_evidence",
            path=repair_root / "repair-evidence-summary.md",
            description="v1.9 expanded cleanup repair summary report.",
            evidence_regime="repaired",
        ),
        RawHybridSource(
            source_id="v1.6-beer-lambert-run",
            role="scientific_law_run",
            path=standard_runs / "v1-3-standard-beer-perturbation-sweep-c671cedf25f1.json",
            description="v1.6 Beer-Lambert warm-start/same-AST diagnostic run artifact.",
            law="beer_lambert",
            evidence_regime="same_ast_return",
        ),
        RawHybridSource(
            source_id="v1.6-shockley-run",
            role="scientific_law_run",
            path=standard_runs / "v1-3-standard-shockley-warm-316f98a5b1fb.json",
            description="v1.6 Shockley warm-start/same-AST diagnostic run artifact.",
            law="shockley",
            evidence_regime="same_ast_return",
        ),
        RawHybridSource(
            source_id="v1.6-planck-diagnostic-run",
            role="scientific_law_run",
            path=standard_runs / "v1-3-standard-planck-diagnostic-2309e6363fc8.json",
            description="v1.6 Planck unsupported compile diagnostic run artifact.",
            law="planck",
            evidence_regime="compile_only",
        ),
        RawHybridSource(
            source_id="v1.6-logistic-diagnostic-run",
            role="scientific_law_run",
            path=standard_runs / "v1-3-standard-logistic-compile-a99c41f57b97.json",
            description="v1.6 logistic unsupported compile diagnostic run artifact.",
            law="logistic",
            evidence_regime="compile_only",
        ),
        RawHybridSource(
            source_id="v1.6-historical-michaelis-diagnostic-run",
            role="scientific_law_run",
            path=standard_runs / "v1-3-standard-michaelis-warm-diagnostic-9917f8383370.json",
            description="v1.6 historical Michaelis unsupported before/after diagnostic run artifact.",
            law="michaelis_menten_historical",
            evidence_regime="historical_context",
        ),
    )


def v111_raw_hybrid_sources() -> tuple[RawHybridSource, ...]:
    """Return locked evidence inputs for the v1.11 paper evidence package."""

    v110_logistic = Path("artifacts") / "campaigns" / "v1.10-logistic-evidence"
    v110_planck = Path("artifacts") / "campaigns" / "v1.10-planck-diagnostics"
    carried = tuple(
        _with_preset(source, V111_RAW_HYBRID_PAPER_PRESET_ID)
        for source in default_raw_hybrid_sources()
        if source.source_id
        not in {
            "v1.6-planck-diagnostic-run",
            "v1.6-logistic-diagnostic-run",
        }
    )
    return (
        *carried,
        RawHybridSource(
            source_id="v1.10-logistic-aggregate",
            role="scientific_law_aggregate",
            path=v110_logistic / "aggregate.json",
            preset_id=V111_RAW_HYBRID_PAPER_PRESET_ID,
            description="v1.10 logistic focused aggregate after exponential-saturation motif work.",
            law="logistic",
            evidence_regime="compile_only",
        ),
        RawHybridSource(
            source_id="v1.10-logistic-run",
            role="scientific_law_run",
            path=v110_logistic / "v1-10-logistic-evidence-logistic-compile-c2af27a35e81.json",
            preset_id=V111_RAW_HYBRID_PAPER_PRESET_ID,
            description="v1.10 logistic unsupported diagnostic with relaxed depth 15 and validated exponential-saturation motif.",
            law="logistic",
            evidence_regime="compile_only",
        ),
        RawHybridSource(
            source_id="v1.10-planck-aggregate",
            role="scientific_law_aggregate",
            path=v110_planck / "aggregate.json",
            preset_id=V111_RAW_HYBRID_PAPER_PRESET_ID,
            description="v1.10 Planck focused aggregate after low-degree power compression.",
            law="planck",
            evidence_regime="compile_only",
        ),
        RawHybridSource(
            source_id="v1.10-planck-run",
            role="scientific_law_run",
            path=v110_planck / "v1-10-planck-diagnostics-planck-compile-795067919a97.json",
            preset_id=V111_RAW_HYBRID_PAPER_PRESET_ID,
            description="v1.10 Planck unsupported diagnostic with relaxed depth 14 and validated low-degree power/direct-division motifs.",
            law="planck",
            evidence_regime="compile_only",
        ),
    )


def paper_package_preset(preset: str = RAW_HYBRID_PAPER_PRESET_ID) -> RawHybridPaperPreset:
    """Return a versioned raw-hybrid paper package preset."""

    normalized = str(preset)
    if normalized in {"v1.9", RAW_HYBRID_PAPER_PRESET_ID}:
        return RawHybridPaperPreset(
            preset_id=RAW_HYBRID_PAPER_PRESET_ID,
            output_dir=DEFAULT_RAW_HYBRID_OUTPUT_DIR,
            title="v1.9 Raw-Hybrid Paper Evidence Report",
            description="v1.9 raw-hybrid package with archived source locks and regime-separated claims.",
            sources=default_raw_hybrid_sources(),
        )
    if normalized in {"v1.11", V111_RAW_HYBRID_PAPER_PRESET_ID}:
        return RawHybridPaperPreset(
            preset_id=V111_RAW_HYBRID_PAPER_PRESET_ID,
            output_dir=DEFAULT_V111_RAW_HYBRID_OUTPUT_DIR,
            title="v1.11 Paper-Strength Evidence Package",
            description=(
                "v1.11 source-locked package using current v1.10 logistic/Planck diagnostics "
                "and preserving regime-separated claim boundaries."
            ),
            sources=v111_raw_hybrid_sources(),
        )
    raise RawHybridPaperError(f"unknown raw-hybrid paper preset: {preset!r}")


def raw_hybrid_paper_presets() -> tuple[str, ...]:
    return (RAW_HYBRID_PAPER_PRESET_ID, V111_RAW_HYBRID_PAPER_PRESET_ID)


def write_raw_hybrid_paper_package(
    *,
    output_dir: Path | None = None,
    preset: str = RAW_HYBRID_PAPER_PRESET_ID,
    require_existing: bool = True,
    overwrite: bool = False,
    reproduction_command: str | None = None,
) -> RawHybridPaperPaths:
    """Write the raw-hybrid paper package from existing evidence artifacts."""

    package = paper_package_preset(preset)
    output_dir = Path(output_dir) if output_dir is not None else package.output_dir
    sources = package.sources
    source_payloads = _load_sources(sources, require_existing=require_existing)
    _prepare_output_dir(output_dir, overwrite=overwrite)

    paths = _package_paths(output_dir)
    regime_summary = build_regime_summary(sources, source_payloads)
    law_rows = build_scientific_law_rows(sources, source_payloads)
    claim_ledger = build_claim_ledger(regime_summary, law_rows)
    centered_diagnostics = render_centered_negative_diagnostics(sources, source_payloads)
    locks = {
        "schema": "eml.raw_hybrid_source_locks.v1",
        "preset_id": package.preset_id,
        "generated_at": _now_iso(),
        "sources": [_source_lock(source) for source in sources if source.path.exists()],
    }
    manifest = _manifest_payload(
        paths,
        preset=package,
        sources=sources,
        source_payloads=source_payloads,
        regime_summary=regime_summary,
        law_rows=law_rows,
        claim_ledger=claim_ledger,
        reproduction_command=reproduction_command
        or f"PYTHONPATH=src python -m eml_symbolic_regression.cli raw-hybrid-paper --preset {package.preset_id} --output-dir {output_dir}",
    )

    _write_json(paths.regime_summary_json, regime_summary)
    paths.raw_hybrid_report_md.write_text(render_raw_hybrid_report(regime_summary, title=package.title), encoding="utf-8")
    _write_json(paths.scientific_law_table_json, {"columns": list(SCIENTIFIC_LAW_COLUMNS), "rows": law_rows})
    _write_scientific_law_csv(paths.scientific_law_table_csv, law_rows)
    paths.scientific_law_table_md.write_text(render_scientific_law_table_markdown(law_rows), encoding="utf-8")
    _write_json(paths.claim_ledger_json, claim_ledger)
    paths.claim_boundaries_md.write_text(render_claim_boundaries(), encoding="utf-8")
    paths.centered_negative_diagnostics_md.write_text(centered_diagnostics, encoding="utf-8")
    _write_json(paths.source_locks_json, locks)
    _write_json(paths.manifest_json, manifest)
    return paths


def build_regime_summary(
    sources: tuple[RawHybridSource, ...],
    source_payloads: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    """Build separate evidence-regime buckets from aggregate and run artifacts."""

    summary = {
        key: {
            "regime": key,
            "description": _regime_description(key),
            "sources": [],
            "runs": [],
            "counts": {
                "total": 0,
                "verifier_recovered": 0,
                "same_ast_return": 0,
                "repaired_candidate": 0,
                "unsupported": 0,
                "failed": 0,
            },
        }
        for key in REGIME_KEYS
    }
    seen: dict[str, set[str]] = {key: set() for key in REGIME_KEYS}

    for source in sources:
        payload = source_payloads.get(source.source_id)
        if not isinstance(payload, Mapping):
            continue
        for run in _source_runs(source, payload):
            row = _regime_run_row(source, run)
            for regime in _regimes_for_run(source, row):
                identity = row.get("artifact_path") or row.get("run_id") or f"{source.source_id}:{len(seen[regime])}"
                if identity in seen[regime]:
                    continue
                seen[regime].add(identity)
                bucket = summary[regime]
                bucket["runs"].append(row)
                if source.source_id not in bucket["sources"]:
                    bucket["sources"].append(source.source_id)

    for bucket in summary.values():
        bucket["sources"].sort()
        bucket["runs"].sort(key=lambda item: (str(item.get("source_id")), str(item.get("run_id")), str(item.get("artifact_path"))))
        bucket["counts"] = _regime_counts(bucket["runs"])
    return summary


def build_scientific_law_rows(
    sources: tuple[RawHybridSource, ...],
    source_payloads: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Extract paper-facing scientific-law table rows from declared run artifacts."""

    rows: list[dict[str, Any]] = []
    for source in sources:
        if source.role != "scientific_law_run":
            continue
        payload = source_payloads.get(source.source_id)
        if not isinstance(payload, Mapping):
            continue
        row = _scientific_law_row(source, payload)
        rows.append(row)
    return sorted(rows, key=lambda row: _law_sort_key(row["law"]))


def build_claim_ledger(
    regime_summary: Mapping[str, Mapping[str, Any]],
    law_rows: list[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build a machine-readable paper claim ledger from classified evidence rows."""

    rows: list[dict[str, Any]] = []
    for regime in REGIME_KEYS:
        bucket = regime_summary.get(regime, {})
        counts = bucket.get("counts", {}) if isinstance(bucket.get("counts"), Mapping) else {}
        rows.append(
            {
                "claim_id": f"v111-regime-{regime}",
                "public_claim": _regime_description(regime),
                "evidence_class": regime,
                "eligible_denominator": regime,
                "source_ids": list(bucket.get("sources", ())) if isinstance(bucket.get("sources"), list) else [],
                "total": counts.get("total", 0),
                "verifier_recovered": counts.get("verifier_recovered", 0),
                "same_ast_return": counts.get("same_ast_return", 0),
                "repaired_candidate": counts.get("repaired_candidate", 0),
                "unsupported": counts.get("unsupported", 0),
                "failed": counts.get("failed", 0),
                "rate_source": "verifier_counts",
            }
        )

    for law in law_rows:
        law_name = str(law.get("law") or "unknown")
        compile_support = str(law.get("compile_support") or "unknown")
        verifier_status = str(law.get("verifier_status") or "unknown")
        evidence_regime = str(law.get("evidence_regime") or "unknown")
        public_claim = "supported diagnostic" if compile_support == "supported" else "unsupported diagnostic"
        if evidence_regime == "same_ast_return":
            public_claim = "same-AST warm-start evidence"
        rows.append(
            {
                "claim_id": f"v111-law-{_slug(law_name)}",
                "public_claim": public_claim,
                "evidence_class": evidence_regime,
                "eligible_denominator": evidence_regime,
                "source_ids": [str(law.get("artifact_path"))],
                "law": law_name,
                "compile_support": compile_support,
                "compile_depth": law.get("compile_depth"),
                "macro_hits": law.get("macro_hits") or [],
                "verifier_status": verifier_status,
                "rate_source": "not_a_rate",
            }
        )

    return {
        "schema": "eml.raw_hybrid_claim_ledger.v1",
        "generated_at": _now_iso(),
        "rules": {
            "recovery_rate_source": "verifier-owned counts only",
            "loss_only_recovery": "forbidden",
            "mixed_regime_blind_claims": "forbidden",
        },
        "rows": rows,
    }


def render_raw_hybrid_report(regime_summary: Mapping[str, Mapping[str, Any]], *, title: str = "v1.9 Raw-Hybrid Paper Evidence Report") -> str:
    lines = [
        f"# {title}",
        "",
        "This package synthesizes locked evidence artifacts without running training, campaigns, or proof suites.",
        "Each evidence path is reported in its own regime bucket so paper claims do not merge incompatible starts.",
        "",
    ]
    for regime in REGIME_KEYS:
        bucket = regime_summary.get(regime, {})
        counts = bucket.get("counts", {}) if isinstance(bucket.get("counts"), Mapping) else {}
        lines.extend(
            [
                f"## {_regime_title(regime)}",
                "",
                str(bucket.get("description") or _regime_description(regime)),
                "",
                "| Metric | Value |",
                "|--------|-------|",
                f"| runs | {counts.get('total', 0)} |",
                f"| verifier_recovered | {counts.get('verifier_recovered', 0)} |",
                f"| same_ast_return | {counts.get('same_ast_return', 0)} |",
                f"| repaired_candidate | {counts.get('repaired_candidate', 0)} |",
                f"| unsupported | {counts.get('unsupported', 0)} |",
                f"| failed | {counts.get('failed', 0)} |",
                "",
                "| Source | Run | Formula | Mode | Evidence Class | Status | Artifact |",
                "|--------|-----|---------|------|----------------|--------|----------|",
            ]
        )
        runs = list(bucket.get("runs", ())) if isinstance(bucket.get("runs"), list) else []
        if runs:
            for run in runs[:12]:
                lines.append(
                    f"| {run.get('source_id', '')} | {run.get('run_id', '')} | {run.get('formula', '')} | "
                    f"{run.get('start_mode', '')} | {run.get('evidence_class', '')} | {run.get('status', '')} | "
                    f"{run.get('artifact_path', '')} |"
                )
            if len(runs) > 12:
                lines.append(f"| ... | {len(runs) - 12} additional runs omitted from this view |  |  |  |  |  |")
        else:
            lines.append("| none |  |  |  |  |  |  |")
        lines.append("")
    return "\n".join(lines)


def render_scientific_law_table_markdown(rows: list[Mapping[str, Any]]) -> str:
    lines = [
        "# Scientific-Law Diagnostics",
        "",
        "| law | formula | compile_support | compile_depth | macro_hits | warm_start_status | verifier_status | evidence_regime | artifact_path |",
        "|-----|---------|-----------------|---------------|------------|-------------------|-----------------|-----------------|---------------|",
    ]
    for row in rows:
        lines.append(
            f"| {row['law']} | `{row['formula']}` | {row['compile_support']} | {_format_cell(row['compile_depth'])} | "
            f"{', '.join(row['macro_hits']) if row['macro_hits'] else ''} | {row['warm_start_status']} | "
            f"{row['verifier_status']} | {row['evidence_regime']} | {row['artifact_path']} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_claim_boundaries() -> str:
    return "\n".join(
        [
            "# Raw-Hybrid Claim Boundaries",
            "",
            "- Raw-hybrid warm-start, same-AST, scaffolded, repaired, refit, compile-only, and perturbed-basin evidence is not blind discovery.",
            "- warm-start evidence is not pure blind discovery.",
            "- same-AST evidence is not pure blind discovery.",
            "- scaffolded evidence is not pure blind discovery.",
            "- repaired evidence is not pure blind discovery.",
            "- refit evidence is not pure blind discovery.",
            "- compile-only evidence is not pure blind discovery.",
            "- perturbed-basin evidence is not pure blind discovery.",
            "- centered-family evidence is reported as negative diagnostic evidence under missing same-family witnesses.",
            "",
        ]
    )


def render_centered_negative_diagnostics(
    sources: tuple[RawHybridSource, ...],
    source_payloads: Mapping[str, Any],
) -> str:
    decision = source_payloads.get("v1.8-centered-decision-json")
    summary = decision.get("evidence_summary", {}) if isinstance(decision, Mapping) else {}
    operator_groups = summary.get("operator_groups", {}) if isinstance(summary, Mapping) else {}
    lines = [
        "# Centered-Family Negative Diagnostics",
        "",
        "These rows are negative diagnostic evidence from v1.8, not a claim that centered families cannot work.",
        "The same-family witness caveat remains active: raw `exp`, `log`, and `scaled_exp` scaffolds are not valid centered-family witnesses.",
        "",
        f"- Decision: `{decision.get('decision') if isinstance(decision, Mapping) else 'unknown'}`",
        f"- Raw recovery rate: {_format_rate(summary.get('raw_recovery_rate') if isinstance(summary, Mapping) else None)}",
        f"- Best centered recovery rate: {_format_rate(summary.get('best_centered_recovery_rate') if isinstance(summary, Mapping) else None)}",
        "",
        "| Operator | Runs | Recovered | Recovery Rate | Unsupported Rate | Schedules |",
        "|----------|------|-----------|---------------|------------------|-----------|",
    ]
    for operator, row in sorted(operator_groups.items()):
        if operator == "raw_eml" or not isinstance(row, Mapping):
            continue
        schedules = row.get("schedules") or []
        lines.append(
            f"| {operator} | {row.get('total', 0)} | {row.get('recovered', 0)} | "
            f"{_format_rate(row.get('recovery_rate'))} | {_format_rate(row.get('unsupported_rate'))} | "
            f"{', '.join(str(item) for item in schedules) or 'fixed'} |"
        )
    lines.append("")
    return "\n".join(lines)


def _with_preset(source: RawHybridSource, preset_id: str) -> RawHybridSource:
    return RawHybridSource(
        source_id=source.source_id,
        role=source.role,
        path=source.path,
        required=source.required,
        preset_id=preset_id,
        description=source.description,
        law=source.law,
        evidence_regime=source.evidence_regime,
    )


def _source_runs(source: RawHybridSource, payload: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    runs = payload.get("runs")
    if isinstance(runs, list):
        return [run for run in runs if isinstance(run, Mapping)]
    if payload.get("schema") == "eml.benchmark_run.v1":
        return [payload]
    if source.role == "repair_evidence" and isinstance(payload.get("cases"), list):
        return [case for case in payload["cases"] if isinstance(case, Mapping)]
    return []


def _regime_run_row(source: RawHybridSource, run: Mapping[str, Any]) -> dict[str, Any]:
    run_payload = run.get("run") if isinstance(run.get("run"), Mapping) else {}
    metrics = run.get("metrics") if isinstance(run.get("metrics"), Mapping) else {}
    refit = run.get("refit") if isinstance(run.get("refit"), Mapping) else {}
    return {
        "source_id": source.source_id,
        "run_id": run.get("run_id") or run_payload.get("run_id") or source.source_id,
        "formula": run.get("formula") or run_payload.get("formula") or source.law,
        "start_mode": run.get("start_mode") or run_payload.get("start_mode"),
        "evidence_class": run.get("evidence_class"),
        "classification": run.get("classification") or run.get("status"),
        "return_kind": run.get("return_kind"),
        "raw_status": run.get("raw_status"),
        "repair_status": run.get("repair_status") or metrics.get("repair_status"),
        "refit_status": metrics.get("refit_status") or refit.get("status"),
        "claim_status": run.get("claim_status"),
        "status": run.get("status") or run.get("claim_status"),
        "artifact_path": str(run.get("artifact_path") or run_payload.get("artifact_path") or source.path),
        "source_path": str(source.path),
    }


def _regimes_for_run(source: RawHybridSource, row: Mapping[str, Any]) -> tuple[str, ...]:
    regimes: set[str] = set()
    start_mode = str(row.get("start_mode") or "")
    evidence_class = str(row.get("evidence_class") or "")
    classification = str(row.get("classification") or "")
    status = str(row.get("status") or "")
    return_kind = str(row.get("return_kind") or "")
    repair_status = str(row.get("repair_status") or "")
    refit_status = str(row.get("refit_status") or "")

    is_scaffolded = evidence_class == "scaffolded_blind_training_recovered"
    is_repaired = repair_status == "repaired" or evidence_class == "repaired_candidate"

    if start_mode == "blind" and not is_scaffolded and not is_repaired and source.role != "repair_evidence":
        regimes.add("pure_blind")
    if is_scaffolded or (source.evidence_regime == "scaffolded" and start_mode == "blind"):
        regimes.add("scaffolded")
    if source.evidence_regime == "compile_only" or start_mode == "compile" or evidence_class == "compile_only_verified":
        regimes.add("compile_only")
    if start_mode == "warm_start" or source.evidence_regime in {"same_ast_return", "warm_start"}:
        regimes.add("warm_start")
    if (
        source.evidence_regime == "same_ast_return"
        or "same_ast" in evidence_class
        or "same_ast" in classification
        or return_kind == "same_ast_return"
        or status == "same_ast_return"
    ):
        regimes.add("same_ast_return")
    if source.evidence_regime == "repaired" or is_repaired:
        regimes.add("repaired")
    if refit_status and refit_status not in {"not_attempted", "None", "null"}:
        regimes.add("refit")
    if start_mode == "perturbed_tree" or (source.evidence_regime == "perturbed_basin" and not start_mode):
        regimes.add("perturbed_basin")
    return tuple(regime for regime in REGIME_KEYS if regime in regimes)


def _regime_counts(runs: list[Mapping[str, Any]]) -> dict[str, int]:
    return {
        "total": len(runs),
        "verifier_recovered": sum(1 for run in runs if run.get("claim_status") == "recovered"),
        "same_ast_return": sum(
            1
            for run in runs
            if "same_ast" in str(run.get("evidence_class") or "")
            or "same_ast" in str(run.get("classification") or "")
            or run.get("return_kind") == "same_ast_return"
            or run.get("status") == "same_ast_return"
        ),
        "repaired_candidate": sum(
            1
            for run in runs
            if run.get("repair_status") == "repaired" or run.get("evidence_class") == "repaired_candidate"
        ),
        "unsupported": sum(
            1
            for run in runs
            if run.get("status") == "unsupported"
            or run.get("claim_status") == "unsupported"
            or run.get("classification") == "unsupported"
        ),
        "failed": sum(
            1
            for run in runs
            if run.get("claim_status") == "failed"
            or run.get("status") in {"failed", "snapped_but_failed", "soft_fit_only", "execution_error"}
        ),
    }


def _scientific_law_row(source: RawHybridSource, payload: Mapping[str, Any]) -> dict[str, Any]:
    compiled = payload.get("compiled_eml") if isinstance(payload.get("compiled_eml"), Mapping) else {}
    warm = payload.get("warm_start_eml") if isinstance(payload.get("warm_start_eml"), Mapping) else {}
    stage_statuses = payload.get("stage_statuses") if isinstance(payload.get("stage_statuses"), Mapping) else {}
    provenance = payload.get("provenance") if isinstance(payload.get("provenance"), Mapping) else {}
    compiled_verification = (
        payload.get("compiled_eml_verification") if isinstance(payload.get("compiled_eml_verification"), Mapping) else {}
    )
    return {
        "law": _law_label(source.law),
        "formula": str(provenance.get("symbolic_expression") or _nested(compiled, ("metadata", "source_expression")) or ""),
        "compile_support": _compile_support(compiled, stage_statuses),
        "compile_depth": _compile_depth(compiled),
        "macro_hits": _macro_hits(compiled),
        "warm_start_status": str(stage_statuses.get("warm_start_attempt") or warm.get("status") or "not_applicable"),
        "verifier_status": str(
            _nested(warm, ("verification", "status"))
            or compiled_verification.get("status")
            or payload.get("claim_status")
            or payload.get("status")
            or "unknown"
        ),
        "evidence_regime": source.evidence_regime or "unknown",
        "artifact_path": str(source.path),
    }


def _compile_support(compiled: Mapping[str, Any], stage_statuses: Mapping[str, Any]) -> str:
    if compiled.get("status") == "unsupported" or stage_statuses.get("compiled_seed") == "unsupported":
        return "unsupported"
    if compiled:
        return "supported"
    return "unknown"


def _compile_depth(compiled: Mapping[str, Any]) -> int | None:
    for path in (
        ("metadata", "depth"),
        ("diagnostic", "relaxed", "metadata", "depth"),
        ("diagnostic", "metadata", "depth"),
        ("diagnostic", "depth"),
    ):
        value = _nested(compiled, path)
        if value is not None:
            try:
                return int(value)
            except (TypeError, ValueError):
                return None
    return None


def _macro_hits(compiled: Mapping[str, Any]) -> list[str]:
    for path in (
        ("metadata", "macro_diagnostics", "hits"),
        ("diagnostic", "relaxed", "metadata", "macro_diagnostics", "hits"),
        ("diagnostic", "metadata", "macro_diagnostics", "hits"),
    ):
        value = _nested(compiled, path)
        if isinstance(value, list):
            return [str(item) for item in value]
    return []


def _nested(payload: Mapping[str, Any], path: tuple[str, ...]) -> Any:
    current: Any = payload
    for key in path:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current


def _write_scientific_law_csv(path: Path, rows: list[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(SCIENTIFIC_LAW_COLUMNS))
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _csv_value(row.get(key)) for key in SCIENTIFIC_LAW_COLUMNS})


def _csv_value(value: Any) -> Any:
    if isinstance(value, list):
        return ";".join(str(item) for item in value)
    if value is None:
        return ""
    return value


def _law_label(law: str | None) -> str:
    return {
        "arrhenius": "Arrhenius",
        "beer_lambert": "Beer-Lambert",
        "shockley": "Shockley",
        "michaelis_menten": "Michaelis-Menten",
        "planck": "Planck diagnostic",
        "logistic": "Logistic diagnostic",
        "michaelis_menten_historical": "Historical Michaelis diagnostic",
    }.get(str(law), str(law or "unknown"))


def _law_sort_key(label: str) -> tuple[int, str]:
    order = {
        "Beer-Lambert": 0,
        "Shockley": 1,
        "Arrhenius": 2,
        "Michaelis-Menten": 3,
        "Planck diagnostic": 4,
        "Logistic diagnostic": 5,
        "Historical Michaelis diagnostic": 6,
    }
    return (order.get(label, 99), label)


def _regime_title(regime: str) -> str:
    return {
        "pure_blind": "Pure Blind",
        "scaffolded": "Scaffolded",
        "compile_only": "Compile Only",
        "warm_start": "Warm Start",
        "same_ast_return": "Same-AST Return",
        "repaired": "Repaired",
        "refit": "Refit",
        "perturbed_basin": "Perturbed Basin",
    }[regime]


def _regime_description(regime: str) -> str:
    return {
        "pure_blind": "Random-initialized blind training evidence, kept separate from repairs and scaffolds.",
        "scaffolded": "Blind training with declared scaffold initializers, not pure blind discovery.",
        "compile_only": "Exact compiler diagnostics that do not train from random initialization.",
        "warm_start": "Compiler-seeded warm-start training attempts.",
        "same_ast_return": "Runs that returned the exact same AST or equivalent same-AST evidence.",
        "repaired": "Verifier-gated local repair evidence, separate from the original selected candidate.",
        "refit": "Frozen exact-tree constant refit diagnostics, separate from discovery evidence.",
        "perturbed_basin": "Perturbed true-tree basin evidence with known starts.",
    }[regime]


def _format_cell(value: Any) -> str:
    return "" if value is None else str(value)


def _format_rate(value: Any) -> str:
    try:
        if value is None or value == "":
            return "n/a"
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return "n/a"


def _slug(value: str) -> str:
    chars = [ch.lower() if ch.isalnum() else "-" for ch in value]
    slug = "".join(chars).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "unknown"


def _package_paths(output_dir: Path) -> RawHybridPaperPaths:
    return RawHybridPaperPaths(
        output_dir=output_dir,
        manifest_json=output_dir / "manifest.json",
        source_locks_json=output_dir / "source-locks.json",
        regime_summary_json=output_dir / "regime-summary.json",
        raw_hybrid_report_md=output_dir / "raw-hybrid-report.md",
        scientific_law_table_json=output_dir / "scientific-law-table.json",
        scientific_law_table_csv=output_dir / "scientific-law-table.csv",
        scientific_law_table_md=output_dir / "scientific-law-table.md",
        claim_ledger_json=output_dir / "claim-ledger.json",
        claim_boundaries_md=output_dir / "claim-boundaries.md",
        centered_negative_diagnostics_md=output_dir / "centered-negative-diagnostics.md",
    )


def _prepare_output_dir(output_dir: Path, *, overwrite: bool) -> None:
    resolved = output_dir.resolve()
    forbidden = {Path.cwd().resolve(), Path.home().resolve(), Path(resolved.anchor).resolve()}
    if resolved in forbidden:
        raise RawHybridPaperError(f"refusing to use unsafe output directory: {output_dir}")
    if output_dir.exists() and not output_dir.is_dir():
        raise RawHybridPaperError(f"output path is not a directory: {output_dir}")
    if output_dir.exists() and any(output_dir.iterdir()):
        if not overwrite:
            raise RawHybridPaperError(f"output directory is not empty: {output_dir}")
        if not _is_raw_hybrid_package_dir(output_dir):
            raise RawHybridPaperError(f"refusing to overwrite unmanaged directory: {output_dir}")
        for name in EXPECTED_RAW_HYBRID_OUTPUTS:
            path = output_dir / name
            if path.is_dir() and not path.is_symlink():
                raise RawHybridPaperError(f"refusing to overwrite directory at generated output path: {path}")
            if path.exists() or path.is_symlink():
                path.unlink()
    output_dir.mkdir(parents=True, exist_ok=True)


def _is_raw_hybrid_package_dir(output_dir: Path) -> bool:
    manifest = output_dir / "manifest.json"
    if not manifest.is_file():
        return False
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return (
        isinstance(payload, Mapping)
        and payload.get("schema") == "eml.raw_hybrid_paper.v1"
        and payload.get("preset_id") in raw_hybrid_paper_presets()
    )


def _load_sources(sources: tuple[RawHybridSource, ...], *, require_existing: bool) -> dict[str, Any]:
    payloads: dict[str, Any] = {}
    for source in sources:
        if not source.path.exists():
            if require_existing and source.required:
                raise RawHybridPaperError(f"missing required source {source.source_id}: {source.path}")
            continue
        if not source.path.is_file():
            raise RawHybridPaperError(f"source must be a file, not a directory, for {source.source_id}: {source.path}")
        if source.path.suffix == ".json":
            try:
                payloads[source.source_id] = json.loads(source.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise RawHybridPaperError(f"invalid JSON in source {source.source_id}: {source.path}") from exc
    return payloads


def _manifest_payload(
    paths: RawHybridPaperPaths,
    *,
    preset: RawHybridPaperPreset,
    sources: tuple[RawHybridSource, ...],
    source_payloads: Mapping[str, Any],
    regime_summary: Mapping[str, Mapping[str, Any]],
    law_rows: list[Mapping[str, Any]],
    claim_ledger: Mapping[str, Any],
    reproduction_command: str,
) -> dict[str, Any]:
    return {
        "schema": "eml.raw_hybrid_paper.v1",
        "preset_id": preset.preset_id,
        "preset": {
            "id": preset.preset_id,
            "title": preset.title,
            "description": preset.description,
        },
        "generated_at": _now_iso(),
        "output_dir": str(paths.output_dir),
        "reproducibility": {"command": reproduction_command},
        "source_locks": str(paths.source_locks_json),
        "outputs": paths.as_dict(),
        "sources": [source.as_dict() for source in sources],
        "loaded_json_sources": sorted(source_payloads),
        "regime_counts": {
            regime: bucket.get("counts", {})
            for regime, bucket in regime_summary.items()
            if isinstance(bucket, Mapping)
        },
        "scientific_law_rows": len(law_rows),
        "claim_ledger_rows": len(claim_ledger.get("rows", ())) if isinstance(claim_ledger.get("rows"), list) else 0,
    }


def _source_lock(source: RawHybridSource) -> dict[str, Any]:
    if not source.path.is_file():
        raise RawHybridPaperError(f"cannot hash non-file source {source.source_id}: {source.path}")
    row = source.as_dict()
    row["sha256"] = _sha256(source.path)
    return row


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
