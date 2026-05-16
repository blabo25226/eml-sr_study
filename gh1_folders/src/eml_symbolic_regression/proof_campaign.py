"""One-command proof campaign orchestration and claim reporting."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .benchmark import RunFilter
from .campaign import CampaignResult, run_campaign
from .diagnostics import write_perturbed_basin_bound_report
from .proof import list_claims, paper_claim


DEFAULT_PROOF_OUTPUT_ROOT = Path("artifacts") / "proof" / "v1.6"
DEFAULT_V14_CAMPAIGNS = (
    Path("artifacts") / "campaigns" / "v1.4-standard",
    Path("artifacts") / "campaigns" / "v1.4-showcase",
)
DEFAULT_ARCHIVED_ANCHORS = (
    Path("artifacts") / "proof" / "v1.5",
    *DEFAULT_V14_CAMPAIGNS,
)
PROOF_CAMPAIGN_PRESETS = (
    "proof-shallow-pure-blind",
    "proof-shallow",
    "proof-basin",
    "proof-basin-probes",
    "proof-depth-curve",
)


@dataclass(frozen=True)
class ProofCampaignResult:
    output_root: Path
    manifest_path: Path
    report_path: Path
    campaigns: Mapping[str, CampaignResult]
    basin_bound_paths: Mapping[str, Path]
    anchor_lock_path: Path

    def as_dict(self) -> dict[str, Any]:
        return {
            "output_root": str(self.output_root),
            "manifest_path": str(self.manifest_path),
            "report_path": str(self.report_path),
            "campaigns": {name: result.as_dict() for name, result in self.campaigns.items()},
            "basin_bound_paths": {key: str(value) for key, value in self.basin_bound_paths.items()},
            "anchor_lock_path": str(self.anchor_lock_path),
        }


def run_proof_campaign(
    *,
    output_root: Path = DEFAULT_PROOF_OUTPUT_ROOT,
    overwrite: bool = False,
    campaign_filters: Mapping[str, RunFilter] | None = None,
    baseline_campaigns: tuple[Path, ...] = DEFAULT_V14_CAMPAIGNS,
    archived_anchor_roots: tuple[Path, ...] = DEFAULT_ARCHIVED_ANCHORS,
    reproduction_command: str | None = None,
) -> ProofCampaignResult:
    output_root = Path(output_root)
    campaign_root = output_root / "campaigns"
    campaign_root.mkdir(parents=True, exist_ok=True)

    campaign_filters = campaign_filters or {}
    campaign_results: dict[str, CampaignResult] = {}
    for preset in PROOF_CAMPAIGN_PRESETS:
        campaign_results[preset] = run_campaign(
            preset,
            output_root=campaign_root,
            label=preset,
            overwrite=overwrite,
            run_filter=campaign_filters.get(preset),
        )

    basin_bound_paths = write_perturbed_basin_bound_report(
        campaign_results["proof-basin"].aggregate_paths["json"],
        campaign_results["proof-basin-probes"].aggregate_paths["json"],
        output_root / "diagnostics" / "basin-bound",
    )

    manifest = _proof_manifest_payload(
        output_root=output_root,
        campaigns=campaign_results,
        basin_bound_paths=basin_bound_paths,
        baseline_campaigns=baseline_campaigns,
        archived_anchor_roots=archived_anchor_roots,
        reproduction_command=reproduction_command
        or f"PYTHONPATH=src python -m eml_symbolic_regression.cli proof-campaign --output-root {output_root}",
    )
    manifest_path = output_root / "proof-campaign.json"
    report_path = output_root / "proof-report.md"
    anchor_lock_path = output_root / "anchor-locks.json"
    _write_json(manifest_path, manifest)
    _write_json(
        anchor_lock_path,
        {
            "schema": "eml.proof_campaign_anchor_lock.v1",
            "campaign_locks": manifest["campaign_locks"],
            "anchor_locks": manifest["anchor_locks"],
        },
    )
    report_path.write_text(render_proof_campaign_report(manifest, output_root), encoding="utf-8")
    return ProofCampaignResult(output_root, manifest_path, report_path, campaign_results, basin_bound_paths, anchor_lock_path)


def render_proof_campaign_report(manifest: Mapping[str, Any], output_root: Path) -> str:
    version_label = _proof_version_label(output_root)
    title = f"# EML {version_label} Proof Campaign Report" if version_label is not None else "# EML Proof Campaign Report"
    lines = [
        title,
        "",
        "This bundle keeps bounded proof claims, measured blind boundaries, and older showcase campaigns separate.",
        "",
        "## Reproduce",
        "",
        "Run this command from a clean checkout:",
        "",
        "```bash",
        str(manifest["reproducibility"]["command"]),
        "```",
        "",
        "## Bundle Outputs",
        "",
    ]
    for name, campaign in manifest.get("campaigns", {}).items():
        report = _relative_link(campaign["report_path"], output_root)
        raw_runs = _relative_link(campaign["raw_run_root"], output_root)
        lines.append(f"- `{name}`: [report]({report}), raw runs at [{raw_runs}]({raw_runs})")

    basin_bound = manifest.get("basin_bound_report", {})
    if basin_bound:
        basin_report = _relative_link(basin_bound["markdown"], output_root)
        lines.extend(["", f"- Perturbed basin bound evidence: [{basin_report}]({basin_report})"])
    if manifest.get("anchor_locks") or manifest.get("campaign_locks"):
        lines.extend(["", "- Anchor locks: [anchor-locks.json](anchor-locks.json)"])

    lines.extend(
        [
            "",
            "## Regime Summary",
            "",
            "| Regime | Runs | Verifier Recovered | Same AST | Verified Equivalent | Unsupported | Failed |",
            "|--------|------|--------------------|----------|---------------------|-------------|--------|",
        ]
    )
    for row in manifest.get("regime_summary", ()):
        lines.append(
            f"| {row['regime']} | {row['total']} | {row['verifier_recovered']} | {row['same_ast_return']} | "
            f"{row['verified_equivalent_ast']} | {row['unsupported']} | {row['failed']} |"
        )

    lines.extend(
        [
            "",
            "## Claim Status",
            "",
            "| Claim | Verdict | Policy | Passed | Eligible | Rate | Report | Raw Runs |",
            "|-------|---------|--------|--------|----------|------|--------|----------|",
        ]
    )
    for row in manifest.get("claim_rows", ()):
        report = _relative_link(row["report_path"], output_root)
        raw_runs = _relative_link(row["raw_run_root"], output_root)
        lines.append(
            f"| {row['claim_id']} | {row['verdict']} | {row['threshold_policy_id']} | {row['passed']} | "
            f"{row['eligible']} | {_format_optional_rate(row['rate'])} | [{row['campaign']}]({report}) | "
            f"[runs]({raw_runs}) |"
        )

    depth_curve_rows = list(manifest.get("depth_curve", ()))
    if depth_curve_rows:
        lines.extend(
            [
                "",
                "## Depth Curve",
                "",
                "| Depth | Blind Rate | Blind Seeds | Perturbed Rate | Perturbed Seeds |",
                "|-------|------------|-------------|----------------|-----------------|",
            ]
        )
        for row in depth_curve_rows:
            lines.append(
                f"| {row['depth']} | {_format_optional_rate(row['blind_rate'])} | {row['blind_seed_count']} | "
                f"{_format_optional_rate(row['perturbed_rate'])} | {row['perturbed_seed_count']} |"
            )
        lines.extend(
            [
                "",
                "The paper reports that blind recovery degrades sharply with depth while perturbed true-tree starts return much more reliably. "
                "This report treats the depth-curve rows as measured boundary evidence, not as failed product commitments.",
            ]
        )

    lines.extend(["", "## Archived Anchors", ""])
    if manifest.get("anchor_locks"):
        lines.extend(
            [
                "These archived proof and campaign anchors are hash-locked so later comparisons can prove which historical files were used.",
                "",
                "| Campaign | File | SHA-256 |",
                "|----------|------|---------|",
            ]
        )
        for campaign in manifest["anchor_locks"]:
            for file_info in campaign["files"]:
                lines.append(f"| {campaign['label']} | {file_info['path']} | `{file_info['sha256']}` |")
    else:
        lines.append("No archived anchor locks were available.")

    lines.extend(["", "## v1.4 Context", ""])
    if manifest.get("v14_campaigns"):
        lines.extend(
            [
                "These denominators are intentionally separate. The proof suites are claim-labeled training evidence; "
                "v1.4 standard/showcase campaigns are broader presentation baselines and must not be merged into proof rates.",
                "",
                "| Campaign | Total Runs | Recovered | Recovery Rate | Blind Runs | Blind Recovered | Blind Rate |",
                "|----------|------------|-----------|---------------|------------|-----------------|------------|",
            ]
        )
        for row in manifest["v14_campaigns"]:
            lines.append(
                f"| {row['campaign']} | {row['total_runs']} | {row['verifier_recovered']} | "
                f"{_format_optional_rate(row['verifier_recovery_rate'])} | {row['blind_total']} | "
                f"{row['blind_recovered']} | {_format_optional_rate(row['blind_recovery_rate'])} |"
            )
    else:
        lines.append("No v1.4 campaign baselines were available.")

    lines.extend(
        [
            "",
            "## Out of Scope",
            "",
            "- `paper-complete-depth-bounded-search` remains representation context, not a training pass/fail claim.",
            "- Universal blind recovery over arbitrary depth-6 formulas remains out of scope for v1.5; the paper reports no such general blind success.",
            "- Compile-only and catalog verification remain useful evidence paths, but they do not satisfy training-proof claims by themselves.",
            "",
        ]
    )
    return "\n".join(lines)


def _proof_manifest_payload(
    *,
    output_root: Path,
    campaigns: Mapping[str, CampaignResult],
    basin_bound_paths: Mapping[str, Path],
    baseline_campaigns: tuple[Path, ...],
    archived_anchor_roots: tuple[Path, ...],
    reproduction_command: str,
) -> dict[str, Any]:
    campaign_payload: dict[str, Any] = {}
    claim_rows: list[dict[str, Any]] = []
    depth_curve_rows: list[dict[str, Any]] = []
    all_runs: list[Mapping[str, Any]] = []

    for name, result in campaigns.items():
        manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
        aggregate = json.loads(result.aggregate_paths["json"].read_text(encoding="utf-8"))
        all_runs.extend(list(aggregate.get("runs", ())))
        campaign_payload[name] = {
            "campaign_dir": str(result.campaign_dir),
            "report_path": str(result.report_path),
            "manifest_path": str(result.manifest_path),
            "raw_run_root": manifest["output"]["raw_run_root"],
            "counts": manifest.get("counts", {}),
            "thresholds": manifest.get("thresholds", []),
        }
        if name == "proof-depth-curve":
            depth_curve_rows = _merge_depth_curve_rows(aggregate.get("depth_curve", []))
        for threshold in manifest.get("thresholds", []):
            verdict = _claim_verdict(threshold.get("status"))
            claim_rows.append(
                {
                    "claim_id": threshold["claim_id"],
                    "claim_class": threshold["claim_class"],
                    "threshold_policy_id": threshold["threshold_policy_id"],
                    "campaign": name,
                    "report_path": str(result.report_path),
                    "raw_run_root": manifest["output"]["raw_run_root"],
                    "passed": threshold["passed"],
                    "eligible": threshold["eligible"],
                    "rate": threshold["rate"],
                    "status": threshold["status"],
                    "verdict": verdict,
                }
            )

    known_claims = {row["claim_id"] for row in claim_rows}
    out_of_scope = [
        claim.as_dict()
        for claim in list_claims()
        if claim.id not in known_claims or claim.claim_class == "contract_context"
    ]

    return {
        "schema": "eml.proof_campaign.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "output_root": str(output_root),
        "reproducibility": {"command": reproduction_command},
        "campaigns": campaign_payload,
        "regime_summary": _regime_summary_rows(all_runs),
        "claim_rows": claim_rows,
        "depth_curve": depth_curve_rows,
        "basin_bound_report": {key: str(value) for key, value in basin_bound_paths.items()},
        "campaign_locks": [_campaign_lock(result.campaign_dir) for result in campaigns.values()],
        "anchor_locks": [_campaign_lock(path) for path in archived_anchor_roots if path.exists()],
        "v14_campaigns": [_load_v14_campaign(path) for path in baseline_campaigns if path.exists()],
        "out_of_scope_claims": out_of_scope,
    }


def _merge_depth_curve_rows(rows: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[int, dict[str, Any]] = {}
    for row in rows:
        depth = int(row["depth"])
        entry = grouped.setdefault(
            depth,
            {
                "depth": depth,
                "blind_rate": None,
                "blind_seed_count": 0,
                "perturbed_rate": None,
                "perturbed_seed_count": 0,
            },
        )
        if row.get("start_mode") == "blind":
            entry["blind_rate"] = row.get("recovery_rate")
            entry["blind_seed_count"] = row.get("seed_count", 0)
        elif row.get("start_mode") == "perturbed_tree":
            entry["perturbed_rate"] = row.get("recovery_rate")
            entry["perturbed_seed_count"] = row.get("seed_count", 0)
    return [grouped[depth] for depth in sorted(grouped)]


def _claim_verdict(status: Any) -> str:
    if status == "passed":
        return "passed"
    if status == "reported":
        return "reported"
    if status == "failed":
        return "failed"
    return "out_of_scope"


def _regime_summary_rows(runs: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for regime in ("blind", "warm_start", "compile", "catalog", "perturbed_tree"):
        regime_runs = [run for run in runs if run.get("start_mode") == regime]
        rows.append(
            {
                "regime": regime,
                "total": len(regime_runs),
                "verifier_recovered": sum(1 for run in regime_runs if run.get("claim_status") == "recovered"),
                "same_ast_return": sum(
                    1
                    for run in regime_runs
                    if run.get("classification") in {"same_ast_warm_start_return", "same_ast_return"}
                ),
                "verified_equivalent_ast": sum(
                    1
                    for run in regime_runs
                    if run.get("classification") in {"verified_equivalent_warm_start_recovery", "verified_equivalent_ast"}
                ),
                "unsupported": sum(1 for run in regime_runs if run.get("classification") == "unsupported"),
                "failed": sum(
                    1
                    for run in regime_runs
                    if run.get("classification") in {"failed", "snapped_but_failed", "soft_fit_only", "execution_failure"}
                ),
            }
        )
    return rows


def _campaign_lock(path: Path) -> dict[str, Any]:
    path = Path(path)
    files = []
    for relative in (
        "aggregate.json",
        "suite-result.json",
        "campaign-manifest.json",
        "report.md",
        "proof-campaign.json",
        "proof-report.md",
        "anchor-locks.json",
        "tables/runs.csv",
        "tables/failures.csv",
    ):
        file_path = path / relative
        if file_path.exists():
            files.append({"path": str(file_path), "sha256": _sha256(file_path)})
    return {"label": path.name, "path": str(path), "files": files}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_v14_campaign(path: Path) -> dict[str, Any]:
    aggregate_path = path / "aggregate.json"
    aggregate = json.loads(aggregate_path.read_text(encoding="utf-8")) if aggregate_path.exists() else {}
    runs = list(aggregate.get("runs", ()))
    blind_rows = [row for row in runs if row.get("start_mode") == "blind"]
    blind_recovered = sum(1 for row in blind_rows if row.get("claim_status") == "recovered")
    blind_total = len(blind_rows)
    counts = aggregate.get("counts", {})
    return {
        "campaign": path.name,
        "path": str(path),
        "total_runs": counts.get("total", 0),
        "verifier_recovered": counts.get("verifier_recovered", 0),
        "verifier_recovery_rate": counts.get("verifier_recovery_rate"),
        "blind_total": blind_total,
        "blind_recovered": blind_recovered,
        "blind_recovery_rate": blind_recovered / blind_total if blind_total else None,
    }


def _relative_link(path: str | Path, base: Path) -> str:
    path_obj = Path(str(path))
    try:
        return path_obj.relative_to(base).as_posix()
    except ValueError:
        return path_obj.as_posix()


def _proof_version_label(path: Path) -> str | None:
    name = Path(path).name
    if name.startswith("v") and any(character.isdigit() for character in name):
        return name
    return None


def _format_optional_rate(value: Any) -> str:
    try:
        if value is None or value == "":
            return "n/a"
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return "n/a"


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
