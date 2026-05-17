import json
import os
import subprocess
import sys
from pathlib import Path

from eml_symbolic_regression.datasets import get_demo
from eml_symbolic_regression.verify import verify_candidate


ROOT = Path(__file__).resolve().parents[1]
CLI_ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src")}


def test_exact_eml_demos_are_recovered():
    for name in ("exp", "log"):
        spec = get_demo(name)
        report = verify_candidate(spec.candidate, spec.make_splits(points=32), tolerance=1e-8)
        assert report.status == "recovered"


def test_catalog_showcase_is_not_labeled_exact_recovery():
    spec = get_demo("planck")
    report = verify_candidate(spec.candidate, spec.make_splits(points=32), tolerance=1e-8)
    assert report.status == "verified_showcase"
    assert report.reason == "verified_non_eml_candidate"


def test_cli_demo_writes_report(tmp_path):
    output = tmp_path / "exp-report.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "eml_symbolic_regression.cli",
            "demo",
            "exp",
            "--points",
            "24",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        env=CLI_ENV,
        text=True,
    )
    assert "exp: recovered" in result.stdout
    payload = json.loads(output.read_text())
    assert payload["claim_status"] == "recovered"
    assert payload["verification"]["status"] == "recovered"


def test_cli_demo_train_eml_writes_selection_and_fallback_provenance(tmp_path):
    output = tmp_path / "exp-trained-report.json"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "eml_symbolic_regression.cli",
            "demo",
            "exp",
            "--points",
            "24",
            "--train-eml",
            "--depth",
            "1",
            "--steps",
            "2",
            "--restarts",
            "1",
            "--hardening-steps",
            "2",
            "--hardening-emit-interval",
            "1",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        env=CLI_ENV,
        text=True,
    )
    payload = json.loads(output.read_text())
    selection = payload["trained_eml_candidate"]["selection"]

    assert payload["trained_eml_verification"]["status"] == "recovered"
    assert selection["mode"] == "verifier_gated_exact_candidate_pool"
    assert selection["selected_candidate_id"] == payload["trained_eml_candidate"]["selected_candidate"]["candidate_id"]
    assert selection["fallback_candidate_id"] == payload["trained_eml_candidate"]["fallback_candidate"]["candidate_id"]
    assert payload["trained_eml_candidate"]["fallback_candidate"]["source"] == "legacy_final_snap"


def test_cli_verify_paper():
    result = subprocess.run(
        [sys.executable, "-m", "eml_symbolic_regression.cli", "verify-paper", "--points", "24"],
        check=True,
        capture_output=True,
        env=CLI_ENV,
        text=True,
    )
    assert "exp: recovered" in result.stdout
    assert "log: recovered" in result.stdout


def test_cli_list_demos():
    result = subprocess.run(
        [sys.executable, "-m", "eml_symbolic_regression.cli", "list-demos"],
        check=True,
        capture_output=True,
        env=CLI_ENV,
        text=True,
    )
    assert "planck:" in result.stdout
    assert "michaelis_menten:" in result.stdout


def test_cli_benchmark_writes_v110_focused_campaign_artifacts(tmp_path):
    output_root = tmp_path / "campaigns"

    for suite_id, case_id, expected_depth, expected_hits in (
        ("v1.10-logistic-evidence", "logistic-compile", 15, ["exponential_saturation_template"]),
        (
            "v1.10-planck-diagnostics",
            "planck-compile",
            14,
            ["low_degree_power_template", "scaled_exp_minus_one_template", "direct_division_template"],
        ),
    ):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "eml_symbolic_regression.cli",
                "benchmark",
                suite_id,
                "--output-dir",
                str(output_root),
            ],
            check=True,
            capture_output=True,
            env=CLI_ENV,
            text=True,
        )

        suite_dir = output_root / suite_id
        suite_result = suite_dir / "suite-result.json"
        aggregate = suite_dir / "aggregate.json"
        aggregate_md = suite_dir / "aggregate.md"

        assert f"{suite_id}: 1 runs, 1 unsupported, 0 failed" in result.stdout
        assert suite_result.exists()
        assert aggregate.exists()
        assert aggregate_md.exists()

        suite_payload = json.loads(suite_result.read_text(encoding="utf-8"))
        run_path = Path(suite_payload["results"][0]["artifact_path"])
        run_payload = json.loads(run_path.read_text(encoding="utf-8"))
        aggregate_payload = json.loads(aggregate.read_text(encoding="utf-8"))
        relaxed = run_payload["compiled_eml"]["diagnostic"]["relaxed"]

        assert suite_payload["suite"]["id"] == suite_id
        assert suite_payload["counts"]["unsupported"] == 1
        assert aggregate_payload["counts"]["unsupported"] == 1
        assert run_payload["run"]["case_id"] == case_id
        assert run_payload["status"] == "unsupported"
        assert "warm_start_eml" not in run_payload
        assert relaxed["metadata"]["depth"] == expected_depth
        assert relaxed["metadata"]["macro_diagnostics"]["hits"] == expected_hits
        assert aggregate_payload["runs"][0]["classification"] == "unsupported"


def test_cli_paper_decision_writes_package(tmp_path):
    aggregate = tmp_path / "aggregate.json"
    aggregate.write_text(
        json.dumps(
            {
                "schema": "eml.benchmark_aggregate.v1",
                "suite": {"id": "synthetic"},
                "runs": [
                    {
                        "claim_status": "recovered",
                        "classification": "blind_training_recovered",
                        "optimizer": {"operator_family": {"label": "raw_eml"}, "operator_schedule": []},
                        "metrics": {"operator_family": "raw_eml"},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "paper"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "eml_symbolic_regression.cli",
            "paper-decision",
            "--aggregate",
            str(aggregate),
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        env=CLI_ENV,
        text=True,
    )

    assert "paper decision: memo" in result.stdout
    payload = json.loads((output_dir / "decision-memo.json").read_text())
    assert payload["decision"] == "wait_for_centered_family_evidence"
    assert (output_dir / "safe-claims.md").exists()
