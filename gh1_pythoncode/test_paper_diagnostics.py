import json

from eml_symbolic_regression.cli import build_parser, diagnostics_paper_ablations_command
from eml_symbolic_regression.paper_diagnostics import (
    baseline_diagnostic_rows,
    motif_depth_delta_rows,
    regime_comparison_rows,
    write_paper_diagnostics,
)


def test_motif_depth_delta_rows_include_current_logistic_and_planck():
    payload = json.loads(open("artifacts/paper/v1.11/raw-hybrid/scientific-law-table.json", encoding="utf-8").read())

    rows = motif_depth_delta_rows(payload)
    by_law = {row["law"]: row for row in rows}

    assert by_law["Logistic diagnostic"]["motif_depth"] == 15
    assert by_law["Logistic diagnostic"]["baseline_depth"] == 27
    assert by_law["Logistic diagnostic"]["depth_delta"] == 12
    assert by_law["Logistic diagnostic"]["strict_support"] is False
    assert by_law["Logistic diagnostic"]["macro_hits"] == "exponential_saturation_template"
    assert by_law["Planck diagnostic"]["motif_depth"] == 14
    assert by_law["Planck diagnostic"]["baseline_depth"] == 24
    assert by_law["Planck diagnostic"]["depth_delta"] == 10
    assert by_law["Planck diagnostic"]["strict_support"] is False
    assert "low_degree_power_template" in by_law["Planck diagnostic"]["macro_hits"]
    assert by_law["Michaelis-Menten"]["strict_support"] is True


def test_regime_comparison_rows_keep_training_and_probes_separate():
    training = json.loads(open("artifacts/campaigns/v1.11-paper-training/aggregate.json", encoding="utf-8").read())
    probes = json.loads(open("artifacts/campaigns/v1.11-logistic-planck-probes/aggregate.json", encoding="utf-8").read())

    rows = regime_comparison_rows((("training", training), ("probes", probes)))

    by_suite_group = {(row["suite_id"], row["group"], row["key"]): row for row in rows}
    assert by_suite_group[("training", "start_mode", "blind")]["verifier_recovered"] == 4
    assert by_suite_group[("training", "evidence_class", "same_ast")]["runs"] == 3
    assert by_suite_group[("probes", "start_mode", "compile")]["unsupported"] == 2
    assert by_suite_group[("probes", "start_mode", "blind")]["failed"] == 2
    assert all(row["denominator_rule"] == "group-local verifier-owned runs" for row in rows)


def test_baseline_diagnostics_are_prediction_only():
    rows = baseline_diagnostic_rows(("logistic",))

    assert {row["baseline_name"] for row in rows} == {"mean", "linear", "cubic", "log_linear_positive"}
    assert all(row["assistance_level"] == "prediction_only_curve_fit" for row in rows)
    assert all("not EML symbolic recovery" in row["claim_boundary"] for row in rows)
    assert any(row["heldout_mse"] is not None for row in rows)


def test_write_paper_diagnostics_outputs_all_tables(tmp_path):
    paths = write_paper_diagnostics(output_dir=tmp_path / "diagnostics")

    manifest = json.loads(paths.manifest_json.read_text(encoding="utf-8"))
    motif = json.loads(paths.motif_depth_deltas_json.read_text(encoding="utf-8"))
    baseline_md = paths.baseline_diagnostics_md.read_text(encoding="utf-8")

    assert manifest["schema"] == "eml.paper_diagnostics.v1"
    assert manifest["counts"]["motif_depth_deltas"] >= 4
    assert manifest["counts"]["baseline_diagnostics"] == 20
    assert any(row["law"] == "Planck diagnostic" for row in motif["rows"])
    assert "prediction-only conventional diagnostics" in baseline_md
    assert paths.regime_comparison_csv.exists()
    assert paths.repair_refit_csv.exists()


def test_paper_ablations_cli_writes_diagnostics(tmp_path, capsys):
    output_dir = tmp_path / "diagnostics"
    args = build_parser().parse_args(["diagnostics", "paper-ablations", "--output-dir", str(output_dir)])

    assert args.func is diagnostics_paper_ablations_command
    assert args.func(args) == 0

    captured = capsys.readouterr().out
    assert "paper diagnostics: manifest ->" in captured
    assert (output_dir / "manifest.json").exists()
    assert (output_dir / "motif-depth-deltas.json").exists()
    assert (output_dir / "baseline-diagnostics.csv").exists()
