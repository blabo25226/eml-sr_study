import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from eml_symbolic_regression.benchmark import RunFilter, load_suite, run_benchmark_suite, write_aggregate_reports
from eml_symbolic_regression.diagnostics import (
    build_perturbed_basin_bound_report,
    render_perturbed_basin_bound_markdown,
    write_perturbed_basin_bound_report,
)


def _aggregate(suite_id: str, rows: list[dict], *, cases: list[dict] | None = None) -> dict:
    suite = {"id": suite_id}
    if cases is not None:
        suite["cases"] = cases
    return {
        "schema": "eml.benchmark_aggregate.v1",
        "suite": suite,
        "runs": rows,
    }


def _case(
    *,
    suite_id: str = "proof-perturbed-basin",
    case_id: str = "basin-beer-lambert-bound",
    formula: str = "beer_lambert",
    seeds: tuple[int, ...] = (0, 1),
    perturbation_noise: tuple[float, ...] = (5.0,),
) -> dict:
    return {
        "id": case_id,
        "formula": formula,
        "start_mode": "perturbed_tree",
        "seeds": list(seeds),
        "perturbation_noise": list(perturbation_noise),
        "suite_id": suite_id,
    }


def _row(
    *,
    noise: float,
    evidence_class: str,
    suite_id: str = "proof-perturbed-basin",
    case_id: str = "basin-beer-lambert-bound",
    formula: str = "beer_lambert",
    seed: int = 0,
    status: str | None = None,
    claim_status: str | None = None,
    return_kind: str = "same_ast_return",
    raw_status: str = "recovered",
    repair_status: str = "not_attempted",
    changed_slot_count: int | None = 0,
    repair_accepted_move_count: int | None = 0,
    reason: str = "verified",
    run_id: str | None = None,
) -> dict:
    status = status or ("repaired_candidate" if evidence_class == "repaired_candidate" else "recovered")
    claim_status = claim_status or ("failed" if evidence_class not in {"perturbed_true_tree_recovered", "repaired_candidate"} else "recovered")
    run_id = run_id or f"{case_id}-seed{seed}-noise{noise:g}"
    return {
        "suite_id": suite_id,
        "case_id": case_id,
        "run_id": run_id,
        "artifact_path": f"artifacts/benchmarks/{suite_id}/{run_id}.json",
        "formula": formula,
        "seed": seed,
        "perturbation_noise": noise,
        "status": status,
        "claim_status": claim_status,
        "evidence_class": evidence_class,
        "return_kind": return_kind,
        "raw_status": raw_status,
        "repair_status": repair_status,
        "reason": reason,
        "metrics": {
            "changed_slot_count": changed_slot_count,
            "repair_accepted_move_count": repair_accepted_move_count,
            "repair_status": repair_status,
            "verifier_status": "recovered" if claim_status == "recovered" else "failed",
        },
        "stage_statuses": {"perturbed_true_tree_attempt": raw_status},
    }


def _write_row_artifacts(root: Path, rows: list[dict]) -> None:
    for row in rows:
        artifact_path = row.get("artifact_path")
        if not artifact_path:
            continue
        path = Path(str(artifact_path))
        target = path if path.is_absolute() else root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps({"run_id": row.get("run_id"), "seed": row.get("seed")}, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_bound_report_keeps_probe_rows_and_computes_continuous_prefixes(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    bounded_rows = [_row(noise=5.0, evidence_class="perturbed_true_tree_recovered", seed=0)]
    probe_rows = [
        _row(
            noise=15.0,
            evidence_class="repaired_candidate",
            suite_id="proof-perturbed-basin-beer-probes",
            case_id="basin-beer-lambert-bound-probes",
            status="repaired_candidate",
            return_kind="snapped_but_failed",
            raw_status="snapped_but_failed",
            repair_status="repaired",
            changed_slot_count=2,
            repair_accepted_move_count=1,
        ),
        _row(
            noise=35.0,
            evidence_class="snapped_but_failed",
            suite_id="proof-perturbed-basin-beer-probes",
            case_id="basin-beer-lambert-bound-probes",
            status="snapped_but_failed",
            claim_status="failed",
            return_kind="snapped_but_failed",
            raw_status="snapped_but_failed",
            repair_status="not_repaired",
            changed_slot_count=3,
            reason="verifier_mismatch",
        ),
        _row(noise=15.0, evidence_class="perturbed_true_tree_recovered", formula="exp"),
    ]
    _write_row_artifacts(tmp_path, [*bounded_rows, *probe_rows])
    bounded = _aggregate("proof-perturbed-basin", bounded_rows)
    probe = _aggregate("proof-perturbed-basin-beer-probes", probe_rows)

    report = build_perturbed_basin_bound_report(bounded, probe)

    assert report["schema"] == "eml.perturbed_basin_bound_report.v1"
    assert report["declared_noise_grid"] == [5.0, 15.0, 35.0]
    assert report["bounded_noise_values"] == [5.0]
    assert report["probe_noise_values"] == [15.0, 35.0]
    assert report["declared_bound_noise_max"] == 5.0
    assert report["raw_supported_noise_max"] == 5.0
    assert report["repaired_supported_noise_max"] == 15.0
    assert report["unsupported_noise_values"] == [35.0]
    assert report["claim_recommendation"] == "probe_supports_15"
    assert [row["perturbation_noise"] for row in report["rows"]] == [5.0, 15.0, 35.0]

    repaired = next(row for row in report["rows"] if row["perturbation_noise"] == 15.0)
    failed = next(row for row in report["rows"] if row["perturbation_noise"] == 35.0)
    assert repaired["evidence_class"] == "repaired_candidate"
    assert repaired["repair_status"] == "repaired"
    assert repaired["return_kind"] == "snapped_but_failed"
    assert repaired["changed_slot_count"] == 2
    assert repaired["repair_accepted_move_count"] == 1
    assert failed["reason"] == "verifier_mismatch"
    assert failed["artifact_path"].endswith("noise35.json")


def test_supported_max_uses_continuous_prefix_not_isolated_higher_pass(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    bounded_rows = [_row(noise=5.0, evidence_class="perturbed_true_tree_recovered")]
    probe_rows = [
        _row(
            noise=15.0,
            evidence_class="snapped_but_failed",
            suite_id="proof-perturbed-basin-beer-probes",
            case_id="basin-beer-lambert-bound-probes",
            status="snapped_but_failed",
            claim_status="failed",
            return_kind="snapped_but_failed",
            raw_status="snapped_but_failed",
            repair_status="not_repaired",
        ),
        _row(
            noise=35.0,
            evidence_class="perturbed_true_tree_recovered",
            suite_id="proof-perturbed-basin-beer-probes",
            case_id="basin-beer-lambert-bound-probes",
        ),
    ]
    _write_row_artifacts(tmp_path, [*bounded_rows, *probe_rows])
    bounded = _aggregate("proof-perturbed-basin", bounded_rows)
    probe = _aggregate("proof-perturbed-basin-beer-probes", probe_rows)

    report = build_perturbed_basin_bound_report(bounded, probe)

    assert report["raw_supported_noise_max"] == 5.0
    assert report["repaired_supported_noise_max"] == 5.0
    assert report["unsupported_noise_values"] == [15.0]
    assert report["claim_recommendation"] == "support_declared_bound"


def test_supported_bound_requires_all_expected_seed_rows(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rows = [_row(noise=5.0, evidence_class="perturbed_true_tree_recovered", seed=0)]
    _write_row_artifacts(tmp_path, rows)
    bounded = _aggregate(
        "proof-perturbed-basin",
        rows,
        cases=[_case(seeds=(0, 1), perturbation_noise=(5.0,))],
    )

    report = build_perturbed_basin_bound_report(bounded)

    assert report["raw_supported_noise_max"] is None
    assert report["repaired_supported_noise_max"] is None
    assert report["incomplete_noise_values"] == [5.0]
    assert report["unsupported_noise_values"] == [5.0]
    assert report["claim_recommendation"] == "narrow_to_none"
    assert report["missing_seed_noise_rows"] == [
        {
            "row_source": "bounded",
            "suite_id": "proof-perturbed-basin",
            "case_id": "basin-beer-lambert-bound",
            "formula": "beer_lambert",
            "seed": 1,
            "perturbation_noise": 5.0,
            "reason": "missing_expected_seed_noise_row",
        }
    ]
    markdown = render_perturbed_basin_bound_markdown(report)
    assert "## Missing Seed/Noise Rows" in markdown
    assert "missing_expected_seed_noise_row" in markdown


@pytest.mark.parametrize("artifact_case", ["missing_path", "absolute_path", "missing_checksum", "invalid_checksum"])
def test_bound_support_requires_durable_raw_artifact_checksums(tmp_path, monkeypatch, artifact_case):
    monkeypatch.chdir(tmp_path)
    row = _row(noise=5.0, evidence_class="perturbed_true_tree_recovered", seed=0)
    if artifact_case == "missing_path":
        row.pop("artifact_path")
    elif artifact_case == "absolute_path":
        row["artifact_path"] = str(tmp_path / "absolute-run.json")
        _write_row_artifacts(tmp_path, [row])
    elif artifact_case == "missing_checksum":
        row["artifact_path"] = "artifacts/benchmarks/missing-run.json"
    elif artifact_case == "invalid_checksum":
        _write_row_artifacts(tmp_path, [row])
        row["artifact_sha256"] = "0" * 64

    report = build_perturbed_basin_bound_report(
        _aggregate(
            "proof-perturbed-basin",
            [row],
            cases=[_case(seeds=(0,), perturbation_noise=(5.0,))],
        )
    )

    assert report["raw_supported_noise_max"] is None
    assert report["repaired_supported_noise_max"] is None
    assert report["invalid_artifact_noise_values"] == [5.0]
    assert report["incomplete_noise_values"] == [5.0]
    assert report["unsupported_noise_values"] == [5.0]
    assert report["claim_recommendation"] == "narrow_to_none"


def test_failed_declared_bound_recommends_narrowing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rows = [
        _row(
            noise=5.0,
            evidence_class="snapped_but_failed",
            status="snapped_but_failed",
            claim_status="failed",
            return_kind="snapped_but_failed",
            raw_status="snapped_but_failed",
            repair_status="not_repaired",
        )
    ]
    _write_row_artifacts(tmp_path, rows)
    bounded = _aggregate("proof-perturbed-basin", rows)

    report = build_perturbed_basin_bound_report(bounded)

    assert report["raw_supported_noise_max"] is None
    assert report["repaired_supported_noise_max"] is None
    assert report["unsupported_noise_values"] == [5.0]
    assert report["claim_recommendation"] == "narrow_to_none"


@pytest.mark.parametrize(
    "evidence_class",
    ["scaffolded_blind_training_recovered", "compile_only_verified", "catalog_verified", "same_ast"],
)
def test_forbidden_evidence_classes_do_not_support_perturbed_basin_bounds(tmp_path, monkeypatch, evidence_class):
    monkeypatch.chdir(tmp_path)
    rows = [_row(noise=5.0, evidence_class=evidence_class, status="recovered", claim_status="recovered")]
    _write_row_artifacts(tmp_path, rows)
    bounded = _aggregate("proof-perturbed-basin", rows)

    report = build_perturbed_basin_bound_report(bounded)

    assert report["raw_supported_noise_max"] is None
    assert report["repaired_supported_noise_max"] is None
    assert report["unsupported_noise_values"] == [5.0]
    assert report["claim_recommendation"] == "narrow_to_none"


def test_repaired_rows_cannot_inflate_raw_perturbed_recovery(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rows = [
        _row(
            noise=5.0,
            evidence_class="perturbed_true_tree_recovered",
            status="repaired_candidate",
            claim_status="recovered",
            return_kind="snapped_but_failed",
            raw_status="snapped_but_failed",
            repair_status="repaired",
            repair_accepted_move_count=1,
        )
    ]
    _write_row_artifacts(tmp_path, rows)
    bounded = _aggregate("proof-perturbed-basin", rows)

    report = build_perturbed_basin_bound_report(bounded)

    assert report["rows"][0]["evidence_class"] == "repaired_candidate"
    assert report["rows"][0]["raw_status"] == "snapped_but_failed"
    assert report["raw_supported_noise_max"] is None
    assert report["repaired_supported_noise_max"] == 5.0


def test_write_bound_report_outputs_json_and_markdown(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    bounded_path = tmp_path / "bounded" / "aggregate.json"
    probe_path = tmp_path / "probe" / "aggregate.json"
    bounded_path.parent.mkdir()
    probe_path.parent.mkdir()
    bounded_rows = [_row(noise=5.0, evidence_class="perturbed_true_tree_recovered")]
    probe_rows = [
        _row(
            noise=15.0,
            evidence_class="repaired_candidate",
            suite_id="proof-perturbed-basin-beer-probes",
            case_id="basin-beer-lambert-bound-probes",
            status="repaired_candidate",
            return_kind="snapped_but_failed",
            raw_status="snapped_but_failed",
            repair_status="repaired",
        )
    ]
    _write_row_artifacts(tmp_path, [*bounded_rows, *probe_rows])
    bounded_path.write_text(
        json.dumps(_aggregate("proof-perturbed-basin", bounded_rows)),
        encoding="utf-8",
    )
    probe_path.write_text(
        json.dumps(_aggregate("proof-perturbed-basin-beer-probes", probe_rows)),
        encoding="utf-8",
    )

    paths = write_perturbed_basin_bound_report(bounded_path, probe_path, tmp_path / "evidence")

    payload = json.loads(paths["json"].read_text(encoding="utf-8"))
    markdown = paths["markdown"].read_text(encoding="utf-8")
    assert paths["json"].name == "basin-bound.json"
    assert paths["markdown"].name == "basin-bound.md"
    assert payload["schema"] == "eml.perturbed_basin_bound_report.v1"
    assert payload["probe_noise_values"] == [15.0]
    assert "proof-perturbed-basin-beer-probes" in markdown
    assert "repaired_candidate" in markdown


def test_cli_diagnostics_basin_bound_writes_reports(tmp_path):
    bounded_path = tmp_path / "bounded.json"
    probe_path = tmp_path / "probe.json"
    output_dir = tmp_path / "diagnostics"
    repo_root = Path(__file__).parents[1]
    bounded_rows = [_row(noise=5.0, evidence_class="perturbed_true_tree_recovered")]
    probe_rows = [
        _row(
            noise=35.0,
            evidence_class="snapped_but_failed",
            suite_id="proof-perturbed-basin-beer-probes",
            case_id="basin-beer-lambert-bound-probes",
            status="snapped_but_failed",
            claim_status="failed",
            return_kind="snapped_but_failed",
            raw_status="snapped_but_failed",
            repair_status="not_repaired",
        )
    ]
    _write_row_artifacts(tmp_path, [*bounded_rows, *probe_rows])
    bounded_path.write_text(
        json.dumps(_aggregate("proof-perturbed-basin", bounded_rows)),
        encoding="utf-8",
    )
    probe_path.write_text(
        json.dumps(_aggregate("proof-perturbed-basin-beer-probes", probe_rows)),
        encoding="utf-8",
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "src")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "eml_symbolic_regression.cli",
            "diagnostics",
            "basin-bound",
            "--bounded-aggregate",
            str(bounded_path),
            "--probe-aggregate",
            str(probe_path),
            "--output-dir",
            str(output_dir),
        ],
        cwd=tmp_path,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "basin-bound.json" in result.stdout
    assert "basin-bound.md" in result.stdout
    assert json.loads((output_dir / "basin-bound.json").read_text(encoding="utf-8"))["unsupported_noise_values"] == [35.0]
    assert "proof-perturbed-basin-beer-probes" in (output_dir / "basin-bound.md").read_text(encoding="utf-8")


def test_committed_basin_bound_evidence_uses_repo_relative_raw_artifacts():
    repo_root = Path(__file__).parents[1]
    evidence_dir = repo_root / "artifacts" / "diagnostics" / "phase31-basin-bound"
    report = json.loads((evidence_dir / "basin-bound.json").read_text(encoding="utf-8"))
    markdown = (evidence_dir / "basin-bound.md").read_text(encoding="utf-8")

    assert "/tmp/" not in markdown
    assert report["missing_seed_noise_rows"] == []
    assert report["invalid_artifact_noise_values"] == []
    assert len(report["expected_seed_noise_rows"]) == 6
    for row in report["rows"]:
        artifact_path = Path(row["artifact_path"])
        assert not artifact_path.is_absolute()
        assert str(artifact_path).startswith("artifacts/diagnostics/phase31-basin-bound/raw-runs/")
        assert (repo_root / artifact_path).exists()
        assert isinstance(row.get("artifact_sha256"), str)
        assert len(row["artifact_sha256"]) == 64
        assert row["artifact_sha256"] == _sha256(repo_root / artifact_path)


@pytest.mark.integration
def test_beer_lambert_bound_and_probe_evidence_generates_stable_report():
    output_dir = Path("artifacts") / "diagnostics" / "phase31-basin-bound"
    artifact_root = output_dir / "raw-runs"
    bounded_suite = load_suite("proof-perturbed-basin")
    bounded_suite = type(bounded_suite)(
        bounded_suite.id,
        bounded_suite.description,
        bounded_suite.cases,
        artifact_root / "bounded",
        bounded_suite.schema,
    )
    bounded_result = run_benchmark_suite(
        bounded_suite,
        run_filter=RunFilter(case_ids=("basin-beer-lambert-bound",)),
    )
    bounded_paths = write_aggregate_reports(bounded_result, stable_snapshot=True)

    probe_suite = load_suite("proof-perturbed-basin-beer-probes")
    probe_suite = type(probe_suite)(
        probe_suite.id,
        probe_suite.description,
        probe_suite.cases,
        artifact_root / "probe",
        probe_suite.schema,
    )
    probe_result = run_benchmark_suite(
        probe_suite,
        run_filter=RunFilter(case_ids=("basin-beer-lambert-bound-probes",)),
    )
    probe_paths = write_aggregate_reports(probe_result, stable_snapshot=True)

    report_paths = write_perturbed_basin_bound_report(bounded_paths["json"], probe_paths["json"], output_dir)
    report = json.loads(report_paths["json"].read_text(encoding="utf-8"))
    markdown = report_paths["markdown"].read_text(encoding="utf-8")
    bounded_aggregate = json.loads(bounded_paths["json"].read_text(encoding="utf-8"))
    probe_aggregate = json.loads(probe_paths["json"].read_text(encoding="utf-8"))

    bounded_rows = [row for row in bounded_aggregate["runs"] if row["formula"] == "beer_lambert"]
    probe_rows = [row for row in probe_aggregate["runs"] if row["formula"] == "beer_lambert"]
    expected_artifacts = {row["artifact_path"] for row in [*bounded_rows, *probe_rows]}
    reported_artifacts = {row["artifact_path"] for row in report["rows"]}

    assert len(bounded_rows) == 2
    assert len(probe_rows) == 4
    assert bounded_aggregate["generated_at"] == "1970-01-01T00:00:00+00:00"
    assert probe_aggregate["generated_at"] == "1970-01-01T00:00:00+00:00"
    assert bounded_aggregate["environment"]["code_version"] == "snapshot"
    assert probe_aggregate["environment"]["code_version"] == "snapshot"
    assert bounded_aggregate["thresholds"][0]["eligible"] == 2
    assert probe_aggregate["thresholds"] == []
    assert set(report["bounded_noise_values"]) == {5.0}
    assert set(report["probe_noise_values"]) == {15.0, 35.0}
    assert expected_artifacts <= reported_artifacts
    assert all(not Path(path).is_absolute() for path in reported_artifacts)
    assert all(str(path).startswith("artifacts/diagnostics/phase31-basin-bound/raw-runs/") for path in reported_artifacts)
    assert all(row["artifact_sha256"] for row in report["rows"])
    for artifact_path in expected_artifacts:
        payload = json.loads(Path(artifact_path).read_text(encoding="utf-8"))
        assert payload["environment"]["code_version"] == "snapshot"
        assert payload["timing"]["elapsed_seconds"] == 0.0
    assert "/tmp/" not in markdown
    assert {row["perturbation_noise"] for row in report["rows"] if row["row_source"] == "probe"} == {15.0, 35.0}
    assert report["raw_supported_noise_max"] in {None, 5.0, 15.0, 35.0}
    assert report["repaired_supported_noise_max"] in {None, 5.0, 15.0, 35.0}
    assert report_paths["json"] == output_dir / "basin-bound.json"
    assert report_paths["markdown"] == output_dir / "basin-bound.md"
    assert report_paths["json"].exists()
    assert report_paths["markdown"].exists()
