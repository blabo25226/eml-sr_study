"""Final v1.11 paper package assembly and claim audit."""

from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .paper_assets import DEFAULT_PAPER_ASSETS_OUTPUT_DIR
from .paper_diagnostics import DEFAULT_PAPER_DIAGNOSTICS_OUTPUT_DIR


DEFAULT_V111_PAPER_PACKAGE_DIR = Path("artifacts") / "paper" / "v1.11"
DEFAULT_V111_RAW_HYBRID_DIR = DEFAULT_V111_PAPER_PACKAGE_DIR / "raw-hybrid"
DEFAULT_V111_TRAINING_DIR = Path("artifacts") / "campaigns" / "v1.11-paper-training"
DEFAULT_V111_PROBE_DIR = Path("artifacts") / "campaigns" / "v1.11-logistic-planck-probes"


class PaperPackageError(RuntimeError):
    """Raised when the final paper package cannot be assembled safely."""


@dataclass(frozen=True)
class PaperPackagePaths:
    output_dir: Path
    manifest_json: Path
    source_locks_json: Path
    claim_audit_json: Path
    claim_audit_md: Path
    reproduction_md: Path
    paper_readiness_md: Path

    def as_dict(self) -> dict[str, str]:
        return {key: str(value) for key, value in self.__dict__.items()}


def write_v111_paper_package(
    *,
    output_dir: Path = DEFAULT_V111_PAPER_PACKAGE_DIR,
    raw_hybrid_dir: Path = DEFAULT_V111_RAW_HYBRID_DIR,
    assets_dir: Path = DEFAULT_PAPER_ASSETS_OUTPUT_DIR,
    diagnostics_dir: Path = DEFAULT_PAPER_DIAGNOSTICS_OUTPUT_DIR,
    training_dir: Path = DEFAULT_V111_TRAINING_DIR,
    probe_dir: Path = DEFAULT_V111_PROBE_DIR,
    overwrite: bool = False,
) -> PaperPackagePaths:
    """Assemble the final v1.11 paper package from locked source artifacts."""

    output_dir = Path(output_dir)
    paths = PaperPackagePaths(
        output_dir=output_dir,
        manifest_json=output_dir / "manifest.json",
        source_locks_json=output_dir / "source-locks.json",
        claim_audit_json=output_dir / "claim-audit.json",
        claim_audit_md=output_dir / "claim-audit.md",
        reproduction_md=output_dir / "reproduction.md",
        paper_readiness_md=output_dir / "paper-readiness.md",
    )
    if paths.manifest_json.exists() and not overwrite:
        raise PaperPackageError(f"{paths.manifest_json} already exists; pass overwrite=True to refresh it")

    output_dir.mkdir(parents=True, exist_ok=True)
    raw_hybrid_dir = Path(raw_hybrid_dir)
    assets_dir = Path(assets_dir)
    diagnostics_dir = Path(diagnostics_dir)
    training_dir = Path(training_dir)
    probe_dir = Path(probe_dir)

    scientific = _read_json(raw_hybrid_dir / "scientific-law-table.json")
    claim_ledger = _read_json(raw_hybrid_dir / "claim-ledger.json")
    assets_manifest = _read_json(assets_dir / "manifest.json")
    diagnostics_manifest = _read_json(diagnostics_dir / "manifest.json")
    training_aggregate = _read_json(training_dir / "aggregate.json")
    probe_aggregate = _read_json(probe_dir / "aggregate.json")
    motif_rows = _read_json(diagnostics_dir / "motif-depth-deltas.json").get("rows", [])
    regime_rows = _read_json(assets_dir / "tables" / "regime_recovery.json").get("rows", [])

    source_locks: list[dict[str, Any]] = []
    source_locks.extend(_snapshot_raw_hybrid(raw_hybrid_dir, output_dir))
    source_locks.extend(_snapshot_assets(assets_manifest, output_dir))
    source_locks.extend(_snapshot_diagnostics(diagnostics_dir, output_dir))
    source_locks.extend(_snapshot_campaign("v1.11-paper-training", training_dir, output_dir / "campaigns" / "v1.11-paper-training"))
    source_locks.extend(
        _snapshot_campaign("v1.11-logistic-planck-probes", probe_dir, output_dir / "campaigns" / "v1.11-logistic-planck-probes")
    )

    audit = audit_v111_claims(
        scientific_law_table=scientific,
        claim_ledger=claim_ledger,
        assets_manifest=assets_manifest,
        training_aggregate=training_aggregate,
        probe_aggregate=probe_aggregate,
        regime_rows=regime_rows,
        source_locks=source_locks,
    )
    _write_json(paths.claim_audit_json, audit)
    paths.claim_audit_md.write_text(_claim_audit_markdown(audit), encoding="utf-8")
    paths.reproduction_md.write_text(_reproduction_markdown(output_dir), encoding="utf-8")
    paths.paper_readiness_md.write_text(
        _paper_readiness_markdown(
            scientific_law_table=scientific,
            training_aggregate=training_aggregate,
            probe_aggregate=probe_aggregate,
            assets_manifest=assets_manifest,
            diagnostics_manifest=diagnostics_manifest,
            motif_rows=motif_rows,
        ),
        encoding="utf-8",
    )

    source_lock_payload = {
        "schema": "eml.v111_paper_source_locks.v1",
        "generated_at": _now_iso(),
        "output_dir": str(output_dir),
        "sources": source_locks,
        "source_count": len(source_locks),
    }
    _write_json(paths.source_locks_json, source_lock_payload)
    manifest = {
        "schema": "eml.v111_paper_package.v1",
        "generated_at": _now_iso(),
        "output_dir": str(output_dir),
        "outputs": paths.as_dict(),
        "source_locks": str(paths.source_locks_json),
        "source_lock_count": len(source_locks),
        "audit_status": audit["status"],
        "claim_audit": str(paths.claim_audit_json),
        "asset_manifest": str(assets_dir / "manifest.json"),
        "raw_hybrid_manifest": str(raw_hybrid_dir / "manifest.json"),
        "diagnostics_manifest": str(diagnostics_dir / "manifest.json"),
        "training_aggregate": str(training_dir / "aggregate.json"),
        "probe_aggregate": str(probe_dir / "aggregate.json"),
        "claim_boundary": "final package preserves regime separation and unsupported diagnostic visibility",
        "reproduction": {
            "commands_markdown": str(paths.reproduction_md),
            "paper_assets_command": "PYTHONPATH=src python -m eml_symbolic_regression.cli paper-assets --output-dir artifacts/paper/v1.11/assets",
            "package_command": "PYTHONPATH=src python -m eml_symbolic_regression.cli paper-package --output-dir artifacts/paper/v1.11 --overwrite",
        },
    }
    _write_json(paths.manifest_json, manifest)
    return paths


def audit_v111_claims(
    *,
    scientific_law_table: Mapping[str, Any],
    claim_ledger: Mapping[str, Any],
    assets_manifest: Mapping[str, Any],
    training_aggregate: Mapping[str, Any],
    probe_aggregate: Mapping[str, Any],
    regime_rows: list[Mapping[str, Any]],
    source_locks: list[Mapping[str, Any]],
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    rows = [row for row in scientific_law_table.get("rows", []) if isinstance(row, Mapping)]
    by_law = {str(row.get("law") or "").lower(): row for row in rows}
    logistic = _first_matching(by_law, "logistic")
    planck = _first_matching(by_law, "planck")
    _check(
        checks,
        "logistic_remains_unsupported",
        logistic is not None and logistic.get("compile_support") == "unsupported" and logistic.get("verifier_status") == "unsupported",
        "Logistic diagnostic is present and unsupported.",
        {"row": logistic},
    )
    _check(
        checks,
        "planck_remains_unsupported",
        planck is not None and planck.get("compile_support") == "unsupported" and planck.get("verifier_status") == "unsupported",
        "Planck diagnostic is present and unsupported.",
        {"row": planck},
    )

    figure_entries = assets_manifest.get("figures") if isinstance(assets_manifest.get("figures"), Mapping) else {}
    figures_ok = bool(figure_entries)
    missing_figure_sources: list[str] = []
    for figure_id, entry in figure_entries.items():
        if not isinstance(entry, Mapping):
            figures_ok = False
            missing_figure_sources.append(str(figure_id))
            continue
        for key in ("svg", "metadata", "source_table_json", "source_table_csv"):
            path = Path(str(entry.get(key) or ""))
            if not path.is_file():
                figures_ok = False
                missing_figure_sources.append(f"{figure_id}:{key}")
    _check(
        checks,
        "figures_have_source_tables",
        figures_ok,
        "Every asset figure has SVG, metadata, source JSON, and source CSV.",
        {"figure_count": len(figure_entries), "missing": missing_figure_sources},
    )

    rules = claim_ledger.get("rules") if isinstance(claim_ledger.get("rules"), Mapping) else {}
    _check(
        checks,
        "loss_only_recovery_forbidden",
        rules.get("loss_only_recovery") == "forbidden",
        "Claim ledger forbids recovery from loss-only fields.",
        {"loss_only_recovery": rules.get("loss_only_recovery")},
    )

    regime_boundaries_ok = bool(regime_rows) and all(
        "suite/start-mode-local" in str(row.get("denominator_rule") or "") for row in regime_rows
    )
    suite_ids = {str(row.get("suite_id")) for row in regime_rows}
    _check(
        checks,
        "regime_denominators_are_separated",
        regime_boundaries_ok and {"v1.11-paper-training", "v1.11-logistic-planck-probes"} <= suite_ids,
        "Regime rows use suite/start-mode-local denominators and include training plus probe suites.",
        {"suite_ids": sorted(suite_ids), "row_count": len(regime_rows)},
    )

    training_counts = training_aggregate.get("counts") if isinstance(training_aggregate.get("counts"), Mapping) else {}
    probe_counts = probe_aggregate.get("counts") if isinstance(probe_aggregate.get("counts"), Mapping) else {}
    _check(
        checks,
        "current_training_results_are_visible",
        training_counts.get("total") == 8
        and training_counts.get("verifier_recovered") == 8
        and probe_counts.get("total") == 4
        and probe_counts.get("verifier_recovered") == 0
        and probe_counts.get("unsupported") == 2
        and probe_counts.get("failed") == 2,
        "Current v1.11 training successes and logistic/Planck probe failures are visible.",
        {"training_counts": training_counts, "probe_counts": probe_counts},
    )

    locks_ok = bool(source_locks) and all(row.get("sha256") and row.get("source_path") for row in source_locks)
    _check(
        checks,
        "source_locks_cover_package_inputs",
        locks_ok,
        "Final package has file-level source locks.",
        {"source_lock_count": len(source_locks)},
    )

    status = "passed" if all(check["status"] == "passed" for check in checks) else "failed"
    return {
        "schema": "eml.v111_claim_audit.v1",
        "generated_at": _now_iso(),
        "status": status,
        "checks": checks,
        "summary": {
            "passed": sum(1 for check in checks if check["status"] == "passed"),
            "failed": sum(1 for check in checks if check["status"] != "passed"),
        },
    }


def _snapshot_raw_hybrid(raw_hybrid_dir: Path, output_dir: Path) -> list[dict[str, Any]]:
    locks = []
    for name in (
        "manifest.json",
        "source-locks.json",
        "claim-ledger.json",
        "claim-boundaries.md",
        "centered-negative-diagnostics.md",
        "raw-hybrid-report.md",
        "regime-summary.json",
        "scientific-law-table.json",
        "scientific-law-table.csv",
        "scientific-law-table.md",
    ):
        src = raw_hybrid_dir / name
        locks.append(_copy_and_lock(f"raw-hybrid-{_stem_id(name)}", "raw_hybrid_package", src, output_dir / "raw-hybrid" / name))
    return locks


def _snapshot_assets(assets_manifest: Mapping[str, Any], output_dir: Path) -> list[dict[str, Any]]:
    locks = [_copy_and_lock("paper-assets-manifest", "paper_assets_manifest", Path(str(assets_manifest["output_dir"])) / "manifest.json", output_dir / "assets" / "manifest.json")]
    tables = assets_manifest.get("tables") if isinstance(assets_manifest.get("tables"), Mapping) else {}
    for table_id, entry in tables.items():
        if not isinstance(entry, Mapping):
            continue
        for key, suffix in (("json", "json"), ("csv", "csv"), ("markdown", "md")):
            src = Path(str(entry.get(key) or ""))
            if src.is_file():
                locks.append(_copy_and_lock(f"asset-table-{table_id}-{suffix}", "paper_asset_table", src, output_dir / "tables" / src.name))
    figures = assets_manifest.get("figures") if isinstance(assets_manifest.get("figures"), Mapping) else {}
    for figure_id, entry in figures.items():
        if not isinstance(entry, Mapping):
            continue
        for key, role in (("svg", "paper_asset_figure"), ("metadata", "paper_asset_figure_metadata")):
            src = Path(str(entry.get(key) or ""))
            if src.is_file():
                locks.append(_copy_and_lock(f"asset-figure-{figure_id}-{key}", role, src, output_dir / "figures" / src.name))
    return locks


def _snapshot_diagnostics(diagnostics_dir: Path, output_dir: Path) -> list[dict[str, Any]]:
    locks = []
    for src in sorted(diagnostics_dir.glob("*.*")):
        if src.suffix in {".json", ".csv", ".md"}:
            locks.append(_copy_and_lock(f"diagnostic-{_stem_id(src.name)}", "paper_diagnostic", src, output_dir / "diagnostics" / src.name))
    return locks


def _snapshot_campaign(source_id: str, campaign_dir: Path, package_dir: Path) -> list[dict[str, Any]]:
    locks = []
    for name in ("campaign-manifest.json", "aggregate.json", "aggregate.md", "report.md"):
        src = campaign_dir / name
        if src.is_file():
            locks.append(_copy_and_lock(f"{source_id}-{_stem_id(name)}", "v1.11_campaign_summary", src, package_dir / name))
    return locks


def _copy_and_lock(source_id: str, role: str, src: Path, dst: Path) -> dict[str, Any]:
    if not src.is_file():
        raise PaperPackageError(f"required source missing: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.resolve() != dst.resolve():
        shutil.copy2(src, dst)
    return {
        "source_id": source_id,
        "role": role,
        "source_path": str(src),
        "package_path": str(dst),
        "sha256": _sha256(src),
        "bytes": src.stat().st_size,
    }


def _claim_audit_markdown(audit: Mapping[str, Any]) -> str:
    lines = [
        "# v1.11 Claim Audit",
        "",
        f"Status: **{audit.get('status')}**",
        "",
        "| Check | Status | Detail |",
        "|-------|--------|--------|",
    ]
    for check in audit.get("checks", []):
        lines.append(f"| {check.get('id')} | {check.get('status')} | {check.get('message')} |")
    lines.append("")
    return "\n".join(lines)


def _reproduction_markdown(output_dir: Path) -> str:
    output_text = str(output_dir)
    return "\n".join(
        [
            "# v1.11 Reproduction Commands",
            "",
            "Run from the repository root.",
            "",
            "```bash",
            "PYTHONPATH=src python -m eml_symbolic_regression.cli raw-hybrid-paper --preset v1.11-paper-evidence-package --output-dir artifacts/paper/v1.11/raw-hybrid --require-existing --overwrite",
            "PYTHONPATH=src python -m eml_symbolic_regression.cli campaign paper-training --label v1.11-paper-training --overwrite",
            "PYTHONPATH=src python -m eml_symbolic_regression.cli campaign paper-probes --label v1.11-logistic-planck-probes --overwrite",
            "PYTHONPATH=src python -m eml_symbolic_regression.cli diagnostics paper-ablations --output-dir artifacts/diagnostics/v1.11-paper-ablations",
            "PYTHONPATH=src python -m eml_symbolic_regression.cli paper-assets --output-dir artifacts/paper/v1.11/assets",
            f"PYTHONPATH=src python -m eml_symbolic_regression.cli paper-package --output-dir {output_text} --overwrite",
            "```",
            "",
        ]
    )


def _paper_readiness_markdown(
    *,
    scientific_law_table: Mapping[str, Any],
    training_aggregate: Mapping[str, Any],
    probe_aggregate: Mapping[str, Any],
    assets_manifest: Mapping[str, Any],
    diagnostics_manifest: Mapping[str, Any],
    motif_rows: list[Mapping[str, Any]],
) -> str:
    training_counts = training_aggregate.get("counts", {})
    probe_counts = probe_aggregate.get("counts", {})
    motif_by_law = {str(row.get("law")): row for row in motif_rows if isinstance(row, Mapping)}
    logistic = motif_by_law.get("Logistic diagnostic", {})
    planck = motif_by_law.get("Planck diagnostic", {})
    supported_laws = [
        row.get("law")
        for row in scientific_law_table.get("rows", [])
        if isinstance(row, Mapping) and row.get("compile_support") == "supported" and row.get("verifier_status") == "recovered"
    ]
    return "\n".join(
        [
            "# v1.11 Paper Readiness Summary",
            "",
            "## Evidence Position",
            "",
            (
                f"- Current-code paper-training campaign: {training_counts.get('verifier_recovered')}/"
                f"{training_counts.get('total')} verifier-recovered runs across pure blind, scaffolded, warm-start, "
                "and perturbed-basin regimes."
            ),
            (
                f"- Logistic/Planck probes: {probe_counts.get('verifier_recovered')}/{probe_counts.get('total')} recovered, "
                f"{probe_counts.get('unsupported')} unsupported, {probe_counts.get('failed')} failed."
            ),
            (
                f"- Supported scientific-law rows: {', '.join(str(item) for item in supported_laws)}."
                if supported_laws
                else "- Supported scientific-law rows: none."
            ),
            (
                f"- Logistic motif depth: {logistic.get('baseline_depth')} -> {logistic.get('motif_depth')} "
                f"with `{logistic.get('macro_hits')}`, still unsupported under the strict gate."
            ),
            (
                f"- Planck motif depth: {planck.get('baseline_depth')} -> {planck.get('motif_depth')} "
                f"with `{planck.get('macro_hits')}`, still unsupported under the strict gate."
            ),
            (
                f"- Paper assets: {assets_manifest.get('counts', {}).get('figures')} figures and "
                f"{assets_manifest.get('counts', {}).get('tables')} source tables."
            ),
            (
                f"- Diagnostics: {diagnostics_manifest.get('counts', {}).get('motif_depth_deltas')} motif rows and "
                f"{diagnostics_manifest.get('counts', {}).get('baseline_diagnostics')} prediction-only baseline rows."
            ),
            "",
            "## Paper Framing",
            "",
            "The material is strong for a verifier-gated hybrid EML symbolic-regression paper: the repository now has real current-code training, source-locked motif ablations, scientific-law support rows, negative logistic/Planck probes, and figure-ready artifacts.",
            "",
            "It should not be framed as broad blind symbolic-regression superiority. The defensible story is representation fidelity, exact candidate generation, honest verifier ownership, strong shallow and basin regimes, and clear failure boundaries as depth and law complexity rise.",
            "",
        ]
    )


def _check(
    checks: list[dict[str, Any]],
    check_id: str,
    condition: bool,
    message: str,
    details: Mapping[str, Any],
) -> None:
    checks.append(
        {
            "id": check_id,
            "status": "passed" if condition else "failed",
            "message": message,
            "details": details,
        }
    )


def _first_matching(rows_by_law: Mapping[str, Mapping[str, Any]], needle: str) -> Mapping[str, Any] | None:
    for law, row in rows_by_law.items():
        if needle in law:
            return row
    return None


def _stem_id(name: str) -> str:
    return name.replace(".", "-").replace("_", "-")


def _read_json(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
