import json
import os
import subprocess
import sys
from pathlib import Path

from eml_symbolic_regression.benchmark import RunFilter
from eml_symbolic_regression.proof_campaign import PROOF_CAMPAIGN_PRESETS, run_proof_campaign


ROOT = Path(__file__).resolve().parents[1]
CLI_ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src")}


def test_run_proof_campaign_writes_bundle_and_claim_report(tmp_path):
    filters = {
        "proof-shallow-pure-blind": RunFilter(case_ids=("shallow-exp-pure-blind",), seeds=(0,)),
        "proof-shallow": RunFilter(case_ids=("shallow-exp-blind",), seeds=(0,)),
        "proof-basin": RunFilter(case_ids=("basin-depth1-perturbed",), seeds=(0,), perturbation_noises=(0.05,)),
        "proof-basin-probes": RunFilter(case_ids=("basin-beer-lambert-bound-probes",), seeds=(0,), perturbation_noises=(15.0,)),
        "proof-depth-curve": RunFilter(case_ids=("depth-2-blind", "depth-2-perturbed"), seeds=(0,)),
    }

    result = run_proof_campaign(output_root=tmp_path, overwrite=True, campaign_filters=filters)

    assert set(result.campaigns) == set(PROOF_CAMPAIGN_PRESETS)
    assert result.manifest_path.exists()
    assert result.report_path.exists()
    assert result.basin_bound_paths["json"].exists()
    assert result.basin_bound_paths["markdown"].exists()
    assert result.anchor_lock_path.exists()

    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    report = result.report_path.read_text(encoding="utf-8")

    assert manifest["schema"] == "eml.proof_campaign.v1"
    assert manifest["claim_rows"]
    assert any(row["claim_id"] == "paper-shallow-scaffolded-recovery" for row in manifest["claim_rows"])
    assert any(row["claim_id"] == "paper-blind-depth-degradation" and row["verdict"] == "reported" for row in manifest["claim_rows"])
    assert manifest["depth_curve"]
    assert manifest["regime_summary"]
    assert manifest["v14_campaigns"]
    assert manifest["anchor_locks"]
    assert any(lock["label"] == "v1.5" for lock in manifest["anchor_locks"])
    assert "## Claim Status" in report
    assert "## Regime Summary" in report
    assert "paper-shallow-scaffolded-recovery" in report
    assert "paper-blind-depth-degradation" in report
    assert "## Archived Anchors" in report
    assert "## v1.4 Context" in report
    assert "These denominators are intentionally separate" in report
    assert "## Out of Scope" in report


def test_cli_proof_campaign_command_writes_bundle(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "eml_symbolic_regression.cli",
            "proof-campaign",
            "--output-root",
            str(tmp_path),
            "--overwrite",
            "--case",
            "shallow-exp-pure-blind",
            "--case",
            "shallow-exp-blind",
            "--case",
            "basin-depth1-perturbed",
            "--case",
            "basin-beer-lambert-bound-probes",
            "--case",
            "depth-2-blind",
            "--case",
            "depth-2-perturbed",
            "--seed",
            "0",
        ],
        check=True,
        capture_output=True,
        env=CLI_ENV,
        text=True,
    )

    manifest = tmp_path / "proof-campaign.json"
    report = tmp_path / "proof-report.md"
    anchor_lock = tmp_path / "anchor-locks.json"

    assert "proof campaign: root ->" in result.stdout
    assert manifest.exists()
    assert report.exists()
    assert anchor_lock.exists()
    assert "## Claim Status" in report.read_text(encoding="utf-8")
