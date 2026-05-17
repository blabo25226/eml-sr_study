import json

from eml_symbolic_regression.cli import build_parser, paper_assets_command
from eml_symbolic_regression.paper_assets import (
    failure_taxonomy_rows,
    regime_recovery_rows,
    scientific_law_support_rows,
    write_paper_assets,
)


def test_regime_recovery_rows_keep_probe_failures_visible():
    training = json.loads(open("artifacts/campaigns/v1.11-paper-training/aggregate.json", encoding="utf-8").read())
    probes = json.loads(open("artifacts/campaigns/v1.11-logistic-planck-probes/aggregate.json", encoding="utf-8").read())

    rows = regime_recovery_rows((("training", training), ("probes", probes)))
    by_suite_regime = {(row["suite_id"], row["regime"]): row for row in rows}

    assert by_suite_regime[("training", "blind")]["verifier_recovered"] == 4
    assert by_suite_regime[("training", "warm_start")]["same_ast_return"] == 3
    assert by_suite_regime[("probes", "compile")]["unsupported"] == 2
    assert by_suite_regime[("probes", "blind")]["failed"] == 2
    assert all("do not combine regimes" in row["claim_boundary"] for row in rows)


def test_scientific_law_support_rows_do_not_promote_logistic_or_planck():
    payload = json.loads(open("artifacts/paper/v1.11/raw-hybrid/scientific-law-table.json", encoding="utf-8").read())

    rows = scientific_law_support_rows(payload)
    by_law = {row["law"]: row for row in rows}

    assert by_law["Logistic diagnostic"]["compile_support"] == "unsupported"
    assert by_law["Logistic diagnostic"]["strict_supported_and_verified"] is False
    assert by_law["Planck diagnostic"]["compile_support"] == "unsupported"
    assert by_law["Planck diagnostic"]["strict_supported_and_verified"] is False
    assert by_law["Shockley"]["strict_supported_and_verified"] is True


def test_failure_taxonomy_rows_include_logistic_and_planck_probe_failures():
    training = json.loads(open("artifacts/campaigns/v1.11-paper-training/aggregate.json", encoding="utf-8").read())
    probes = json.loads(open("artifacts/campaigns/v1.11-logistic-planck-probes/aggregate.json", encoding="utf-8").read())

    rows = failure_taxonomy_rows((("training", training), ("probes", probes)))
    labels = {(row["formula"], row["start_mode"], row["classification"]) for row in rows}

    assert ("logistic", "compile", "unsupported") in labels
    assert ("logistic", "blind", "snapped_but_failed") in labels
    assert ("planck", "compile", "unsupported") in labels
    assert ("planck", "blind", "failed") in labels


def test_write_paper_assets_outputs_tables_figures_and_metadata(tmp_path):
    paths = write_paper_assets(output_dir=tmp_path / "assets")

    manifest = json.loads(paths.manifest_json.read_text(encoding="utf-8"))
    support_table = json.loads(paths.table_json["scientific_law_support"].read_text(encoding="utf-8"))
    motif_svg = paths.figures["motif_depth_deltas"].read_text(encoding="utf-8")
    support_metadata = json.loads(paths.figure_metadata["scientific_law_support"].read_text(encoding="utf-8"))

    assert manifest["schema"] == "eml.paper_assets.v1"
    assert manifest["counts"]["tables"] == 7
    assert manifest["counts"]["figures"] == 7
    assert manifest["counts"]["source_locks"] >= 6
    assert support_table["schema"] == "eml.paper_asset_table.v1"
    assert any(row["law"] == "Logistic diagnostic" and row["compile_support"] == "unsupported" for row in support_table["rows"])
    assert "<svg" in motif_svg
    assert "<rect" in motif_svg
    assert support_metadata["source_table_json"] == str(paths.table_json["scientific_law_support"])
    assert "unsupported diagnostic laws" in support_metadata["claim_boundary"]
    assert paths.table_csv["baseline_diagnostics"].exists()
    assert paths.table_md["training_lifecycle"].exists()


def test_paper_assets_cli_writes_manifest(tmp_path, capsys):
    output_dir = tmp_path / "assets"
    args = build_parser().parse_args(["paper-assets", "--output-dir", str(output_dir)])

    assert args.func is paper_assets_command
    assert args.func(args) == 0

    captured = capsys.readouterr().out
    assert "paper assets: manifest ->" in captured
    assert (output_dir / "manifest.json").exists()
    assert (output_dir / "figures" / "regime_recovery.svg").exists()
    assert (output_dir / "tables" / "regime_recovery.csv").exists()
