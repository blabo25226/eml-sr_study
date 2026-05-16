import csv
import json
from pathlib import Path

from eml_symbolic_regression.baselines import DENOMINATOR_POLICY, write_baseline_harness
from eml_symbolic_regression.cli import baseline_harness_command, build_parser


def _load_rows(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))["rows"]


def test_baseline_harness_writes_matched_rows_and_dependency_locks(tmp_path):
    paths = write_baseline_harness(
        output_dir=tmp_path / "baselines",
        datasets=("unit_aware_ohm_law",),
        adapters=("eml_reference", "polynomial_least_squares", "pysr"),
        seeds=(0,),
        constants_policies=("literal_constants",),
        start_conditions=("blind", "warm_start"),
        points=14,
        overwrite=True,
    )

    manifest = json.loads(paths.manifest_json.read_text(encoding="utf-8"))
    rows = _load_rows(paths.rows_json)
    locks = json.loads(paths.dependency_locks_json.read_text(encoding="utf-8"))
    report = paths.report_md.read_text(encoding="utf-8")

    assert manifest["schema"] == "eml.baseline_harness_manifest.v1"
    assert manifest["counts"]["total"] == 6
    assert manifest["denominator_policy"] == DENOMINATOR_POLICY
    assert manifest["claim_surface"]["policy"] == "quarantined_appendix_or_future_work_only"
    assert manifest["claim_surface"]["main_surface_comparison_claim"] is False
    assert manifest["claim_surface"]["main_surface_eligible_rows"] == 0
    assert paths.rows_csv.exists()
    assert "Matched Baseline Harness Report" in report
    assert "diagnostic scaffolding and future-work context" in report

    manifest_hashes = {row["dataset_manifest_sha256"] for row in rows}
    assert len(manifest_hashes) == 1
    assert {row["budget"]["time_seconds"] for row in rows} == {5.0}
    assert {row["budget"]["max_evaluations"] for row in rows} == {1000}
    assert all(row["denominator_policy"] == DENOMINATOR_POLICY for row in rows)
    assert all("adapter_launch_status" in row for row in rows)
    assert all("fixed_budget_launched" in row for row in rows)
    assert all(row["main_surface_eligible"] is False for row in rows)

    eml_warm = next(row for row in rows if row["adapter"] == "eml_reference" and row["start_condition"] == "warm_start")
    assert eml_warm["status"] == "completed"
    assert eml_warm["adapter_launch_status"] == "fixed_budget_completed"
    assert eml_warm["fixed_budget_launched"] is True
    assert eml_warm["model"]["source"] == "clean_reference_candidate"
    assert eml_warm["final_confirmation"]["status"] == "passed"

    polynomial = next(row for row in rows if row["adapter"] == "polynomial_least_squares" and row["start_condition"] == "blind")
    assert polynomial["status"] == "completed"
    assert polynomial["baseline_family"] == "conventional_symbolic_regression"
    assert polynomial["model"]["source"] == "fixed_polynomial_feature_lstsq"
    assert polynomial["final_confirmation"]["status"] == "passed"
    assert polynomial["model"]["expression"]

    external = [row for row in rows if row["adapter"] == "pysr"]
    assert {row["status"] for row in external} == {"unavailable"}
    assert all(row["reason"] == "missing_optional_dependency" for row in external)
    assert all(row["adapter_launch_status"] == "not_launched_missing_dependency" for row in external)
    assert any(adapter["adapter"] == "pysr" and adapter["import_status"] == "missing" for adapter in locks["adapters"])
    assert all(lock["sha256"] for lock in locks["source_locks"] if lock["present"])

    csv_rows = list(csv.DictReader(paths.rows_csv.open(encoding="utf-8")))
    assert {"dependency_status", "adapter_launch_status", "fixed_budget_launched", "main_surface_eligible"} <= set(csv_rows[0])
    assert next(row for row in csv_rows if row["adapter"] == "pysr")["adapter_launch_status"] == "not_launched_missing_dependency"


def test_baseline_harness_fails_closed_for_basis_only_literal_reference(tmp_path):
    paths = write_baseline_harness(
        output_dir=tmp_path / "baselines",
        datasets=("noisy_beer_lambert_sweep",),
        adapters=("eml_reference",),
        seeds=(0,),
        constants_policies=("basis_only",),
        start_conditions=("warm_start",),
        points=12,
        overwrite=True,
    )
    rows = _load_rows(paths.rows_json)

    assert len(rows) == 1
    assert rows[0]["status"] == "unsupported"
    assert rows[0]["reason"] == "constants_policy_requires_literal_constants"
    assert rows[0]["adapter_launch_status"] == "not_launched_unsupported_contract"
    assert rows[0]["fixed_budget_launched"] is False
    assert rows[0]["dataset_manifest"]["noise_policy"]["type"] == "gaussian_relative"


def test_cli_baseline_harness_writes_artifact_bundle(tmp_path):
    output_dir = tmp_path / "cli-baselines"
    args = build_parser().parse_args(
        [
            "baseline-harness",
            "--output-dir",
            str(output_dir),
            "--dataset",
            "unit_aware_ohm_law",
            "--adapter",
            "polynomial_least_squares",
            "--constants-policy",
            "literal_constants",
            "--start-condition",
            "blind",
            "--points",
            "12",
            "--overwrite",
        ]
    )

    assert baseline_harness_command(args) == 0
    manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
    rows = _load_rows(output_dir / "baseline-runs.json")

    assert manifest["schema"] == "eml.baseline_harness_manifest.v1"
    assert manifest["config"]["datasets"] == ["unit_aware_ohm_law"]
    assert manifest["config"]["adapters"] == ["polynomial_least_squares"]
    assert manifest["outputs"]["rows_csv"].endswith("baseline-runs.csv")
    assert len(rows) == 1
    assert rows[0]["status"] == "completed"
    assert rows[0]["adapter"] == "polynomial_least_squares"
