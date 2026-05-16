import hashlib
import json
import shlex
from pathlib import Path

import pytest

from eml_symbolic_regression.cli import build_parser, raw_hybrid_paper_command
from eml_symbolic_regression.raw_hybrid_paper import (
    RAW_HYBRID_PAPER_PRESET_ID,
    V111_RAW_HYBRID_PAPER_PRESET_ID,
    RawHybridPaperError,
    RawHybridSource,
    default_raw_hybrid_sources,
    v111_raw_hybrid_sources,
    write_raw_hybrid_paper_package,
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def test_default_raw_hybrid_sources_cover_required_evidence():
    sources = default_raw_hybrid_sources()
    source_ids = {source.source_id for source in sources}

    assert {source.preset_id for source in sources} == {RAW_HYBRID_PAPER_PRESET_ID}
    assert {
        "proof-shallow-pure-blind-aggregate",
        "proof-shallow-scaffolded-aggregate",
        "proof-perturbed-basin-aggregate",
        "proof-basin-probes-aggregate",
        "proof-depth-curve-aggregate",
        "v1.8-centered-decision-json",
        "v1.8-centered-decision-markdown",
        "v1.8-centered-completeness-boundary",
        "v1.9-arrhenius-aggregate",
        "v1.9-arrhenius-run",
        "v1.9-michaelis-aggregate",
        "v1.9-michaelis-run",
        "v1.9-repair-aggregate",
        "v1.9-repair-summary-json",
        "v1.6-beer-lambert-run",
        "v1.6-shockley-run",
        "v1.6-planck-diagnostic-run",
        "v1.6-logistic-diagnostic-run",
    } <= source_ids
    assert all(source.required for source in sources)
    assert all(source.path.suffix in {".json", ".md"} for source in sources)
    assert all(source.path.is_file() for source in sources)


def test_v111_sources_replace_stale_logistic_and_planck_diagnostics():
    sources = v111_raw_hybrid_sources()
    source_ids = {source.source_id for source in sources}

    assert {source.preset_id for source in sources} == {V111_RAW_HYBRID_PAPER_PRESET_ID}
    assert "v1.10-logistic-aggregate" in source_ids
    assert "v1.10-logistic-run" in source_ids
    assert "v1.10-planck-aggregate" in source_ids
    assert "v1.10-planck-run" in source_ids
    assert "v1.6-logistic-diagnostic-run" not in source_ids
    assert "v1.6-planck-diagnostic-run" not in source_ids
    assert all(source.path.is_file() for source in sources)


def test_raw_hybrid_package_fails_closed_on_missing_required_source(tmp_path, monkeypatch):
    missing = tmp_path / "missing" / "aggregate.json"
    monkeypatch.setattr(
        "eml_symbolic_regression.raw_hybrid_paper.default_raw_hybrid_sources",
        lambda: (
            RawHybridSource(
                source_id="missing-required",
                role="proof_aggregate",
                path=missing,
                required=True,
            ),
        ),
    )

    with pytest.raises(RawHybridPaperError) as exc:
        write_raw_hybrid_paper_package(output_dir=tmp_path / "paper", require_existing=True)

    assert "missing-required" in str(exc.value)
    assert str(missing) in str(exc.value)


def test_raw_hybrid_source_locks_hash_specific_files(tmp_path):
    paths = write_raw_hybrid_paper_package(
        output_dir=tmp_path / "paper",
        require_existing=True,
        reproduction_command="PYTHONPATH=src python -m eml_symbolic_regression.cli raw-hybrid-paper --output-dir out",
    )

    locks = json.loads(paths.source_locks_json.read_text(encoding="utf-8"))

    assert locks["schema"] == "eml.raw_hybrid_source_locks.v1"
    assert locks["preset_id"] == RAW_HYBRID_PAPER_PRESET_ID
    assert locks["sources"]
    for row in locks["sources"]:
        path = Path(row["path"])
        assert path.is_file()
        assert row["source_id"]
        assert row["role"]
        assert row["required"] is True
        assert row["sha256"] == _sha256(path)


def test_raw_hybrid_manifest_records_package_contract(tmp_path):
    paths = write_raw_hybrid_paper_package(
        output_dir=tmp_path / "paper",
        require_existing=True,
        reproduction_command="PYTHONPATH=src python -m eml_symbolic_regression.cli raw-hybrid-paper --output-dir out",
    )

    manifest = json.loads(paths.manifest_json.read_text(encoding="utf-8"))

    assert manifest["schema"] == "eml.raw_hybrid_paper.v1"
    assert manifest["preset_id"] == RAW_HYBRID_PAPER_PRESET_ID
    assert manifest["preset"]["id"] == RAW_HYBRID_PAPER_PRESET_ID
    assert manifest["reproducibility"]["command"] == (
        "PYTHONPATH=src python -m eml_symbolic_regression.cli raw-hybrid-paper --output-dir out"
    )
    assert manifest["source_locks"] == str(paths.source_locks_json)
    assert manifest["outputs"]["manifest_json"] == str(paths.manifest_json)
    assert manifest["outputs"]["source_locks_json"] == str(paths.source_locks_json)
    assert manifest["outputs"]["claim_ledger_json"] == str(paths.claim_ledger_json)


def test_v111_manifest_and_claim_ledger_record_current_contract(tmp_path):
    paths = write_raw_hybrid_paper_package(
        output_dir=tmp_path / "paper",
        preset=V111_RAW_HYBRID_PAPER_PRESET_ID,
        require_existing=True,
        reproduction_command=(
            "PYTHONPATH=src python -m eml_symbolic_regression.cli raw-hybrid-paper "
            "--preset v1.11-paper-evidence-package --output-dir out"
        ),
    )

    manifest = json.loads(paths.manifest_json.read_text(encoding="utf-8"))
    ledger = json.loads(paths.claim_ledger_json.read_text(encoding="utf-8"))
    locks = json.loads(paths.source_locks_json.read_text(encoding="utf-8"))

    assert manifest["preset_id"] == V111_RAW_HYBRID_PAPER_PRESET_ID
    assert manifest["claim_ledger_rows"] == len(ledger["rows"])
    assert ledger["schema"] == "eml.raw_hybrid_claim_ledger.v1"
    assert ledger["rules"]["loss_only_recovery"] == "forbidden"
    source_ids = {row["source_id"] for row in locks["sources"]}
    assert "v1.10-logistic-run" in source_ids
    assert "v1.10-planck-run" in source_ids


def test_raw_hybrid_report_keeps_required_regimes_separate(tmp_path):
    paths = write_raw_hybrid_paper_package(output_dir=tmp_path / "paper", require_existing=True)

    summary = json.loads(paths.regime_summary_json.read_text(encoding="utf-8"))
    report = paths.raw_hybrid_report_md.read_text(encoding="utf-8")
    claim_boundaries = paths.claim_boundaries_md.read_text(encoding="utf-8")

    required_regimes = {
        "pure_blind",
        "scaffolded",
        "compile_only",
        "warm_start",
        "same_ast_return",
        "repaired",
        "refit",
        "perturbed_basin",
    }
    assert required_regimes <= set(summary)
    assert summary["pure_blind"]["runs"]
    assert summary["scaffolded"]["runs"]
    assert summary["perturbed_basin"]["runs"]
    assert summary["repaired"]["runs"]
    assert all(run["start_mode"] == "blind" for run in summary["pure_blind"]["runs"])
    assert not any(
        run["evidence_class"] in {"scaffolded_blind_training_recovered", "repaired_candidate"}
        or run["repair_status"] == "repaired"
        for run in summary["pure_blind"]["runs"]
    )
    assert all(run["evidence_class"] == "scaffolded_blind_training_recovered" for run in summary["scaffolded"]["runs"])
    assert all(run["start_mode"] == "perturbed_tree" for run in summary["perturbed_basin"]["runs"])
    assert "overall recovery" not in report.lower()
    assert "merged recovery" not in report.lower()
    for heading in (
        "Pure Blind",
        "Scaffolded",
        "Compile Only",
        "Warm Start",
        "Same-AST Return",
        "Repaired",
        "Refit",
        "Perturbed Basin",
    ):
        assert f"## {heading}" in report
    for phrase in (
        "warm-start evidence is not pure blind discovery",
        "same-AST evidence is not pure blind discovery",
        "scaffolded evidence is not pure blind discovery",
        "repaired evidence is not pure blind discovery",
        "refit evidence is not pure blind discovery",
        "compile-only evidence is not pure blind discovery",
        "perturbed-basin evidence is not pure blind discovery",
    ):
        assert phrase in claim_boundaries


def test_scientific_law_table_contains_required_columns_and_rows(tmp_path):
    paths = write_raw_hybrid_paper_package(output_dir=tmp_path / "paper", require_existing=True)

    payload = json.loads(paths.scientific_law_table_json.read_text(encoding="utf-8"))
    csv_header = paths.scientific_law_table_csv.read_text(encoding="utf-8").splitlines()[0].split(",")
    markdown = paths.scientific_law_table_md.read_text(encoding="utf-8")
    rows = payload["rows"]
    required_columns = {
        "law",
        "formula",
        "compile_support",
        "compile_depth",
        "macro_hits",
        "warm_start_status",
        "verifier_status",
        "evidence_regime",
        "artifact_path",
    }

    assert required_columns <= set(payload["columns"])
    assert required_columns <= set(csv_header)
    assert all(required_columns <= set(row) for row in rows)
    assert "| law | formula | compile_support |" in markdown

    by_law = {row["law"]: row for row in rows}
    assert by_law["Beer-Lambert"]["evidence_regime"] == "same_ast_return"
    assert by_law["Shockley"]["evidence_regime"] == "same_ast_return"
    assert by_law["Arrhenius"]["formula"] == "exp(-0.8/x)"
    assert by_law["Arrhenius"]["compile_support"] == "supported"
    assert by_law["Arrhenius"]["compile_depth"] == 7
    assert by_law["Arrhenius"]["macro_hits"] == ["direct_division_template"]
    assert by_law["Arrhenius"]["warm_start_status"] == "same_ast_return"
    assert by_law["Arrhenius"]["verifier_status"] == "recovered"
    assert by_law["Arrhenius"]["evidence_regime"] == "same_ast_return"
    assert "blind" not in by_law["Arrhenius"]["evidence_regime"]
    assert by_law["Michaelis-Menten"]["formula"] == "2*x/(x + 0.5)"
    assert by_law["Michaelis-Menten"]["compile_support"] == "supported"
    assert by_law["Michaelis-Menten"]["compile_depth"] == 12
    assert by_law["Michaelis-Menten"]["macro_hits"] == ["saturation_ratio_template"]
    assert by_law["Michaelis-Menten"]["evidence_regime"] == "same_ast_return"
    assert "blind" not in by_law["Michaelis-Menten"]["evidence_regime"]
    assert by_law["Planck diagnostic"]["compile_support"] == "unsupported"
    assert by_law["Planck diagnostic"]["evidence_regime"] == "compile_only"
    assert by_law["Logistic diagnostic"]["compile_support"] == "unsupported"
    assert by_law["Logistic diagnostic"]["evidence_regime"] == "compile_only"
    assert by_law["Historical Michaelis diagnostic"]["evidence_regime"] == "historical_context"


def test_v111_scientific_law_table_uses_current_logistic_and_planck_rows(tmp_path):
    paths = write_raw_hybrid_paper_package(
        output_dir=tmp_path / "paper",
        preset=V111_RAW_HYBRID_PAPER_PRESET_ID,
        require_existing=True,
    )

    rows = json.loads(paths.scientific_law_table_json.read_text(encoding="utf-8"))["rows"]
    by_law = {row["law"]: row for row in rows}

    logistic = by_law["Logistic diagnostic"]
    planck = by_law["Planck diagnostic"]
    assert logistic["compile_support"] == "unsupported"
    assert logistic["compile_depth"] == 15
    assert logistic["macro_hits"] == ["exponential_saturation_template"]
    assert "v1.10-logistic-evidence" in logistic["artifact_path"]
    assert "v1.6" not in logistic["artifact_path"]
    assert planck["compile_support"] == "unsupported"
    assert planck["compile_depth"] == 14
    assert planck["macro_hits"] == [
        "low_degree_power_template",
        "scaled_exp_minus_one_template",
        "direct_division_template",
    ]
    assert "v1.10-planck-diagnostics" in planck["artifact_path"]
    assert "v1.6" not in planck["artifact_path"]
    assert by_law["Michaelis-Menten"]["compile_depth"] == 12


def test_centered_diagnostics_keep_same_family_witness_caveat(tmp_path):
    paths = write_raw_hybrid_paper_package(output_dir=tmp_path / "paper", require_existing=True)

    centered = paths.centered_negative_diagnostics_md.read_text(encoding="utf-8").lower()

    assert "same-family witness" in centered
    assert "negative diagnostic" in centered
    assert "impossibility" not in centered
    assert "best centered recovery rate" in centered


def test_raw_hybrid_cli_parser_and_command_writes_package(tmp_path, capsys):
    output_dir = tmp_path / "paper root"
    args = build_parser().parse_args(["raw-hybrid-paper", "--output-dir", str(output_dir), "--require-existing"])

    assert args.func is raw_hybrid_paper_command
    assert args.preset == RAW_HYBRID_PAPER_PRESET_ID
    assert args.output_dir == str(output_dir)
    assert args.require_existing is True

    result = args.func(args)
    captured = capsys.readouterr().out

    assert result == 0
    assert "manifest ->" in captured
    assert "report ->" in captured
    assert "scientific laws ->" in captured
    assert "claim boundaries ->" in captured
    assert "source locks ->" in captured
    assert (output_dir / "manifest.json").exists()
    assert (output_dir / "raw-hybrid-report.md").exists()
    assert (output_dir / "scientific-law-table.json").exists()
    assert (output_dir / "claim-ledger.json").exists()
    assert (output_dir / "claim-boundaries.md").exists()
    assert (output_dir / "source-locks.json").exists()


def test_v111_cli_parser_and_command_writes_current_package(tmp_path):
    output_dir = tmp_path / "paper"
    args = build_parser().parse_args(
        [
            "raw-hybrid-paper",
            "--preset",
            V111_RAW_HYBRID_PAPER_PRESET_ID,
            "--output-dir",
            str(output_dir),
            "--require-existing",
        ]
    )

    assert args.func is raw_hybrid_paper_command
    assert args.preset == V111_RAW_HYBRID_PAPER_PRESET_ID
    assert args.func(args) == 0

    manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
    rows = json.loads((output_dir / "scientific-law-table.json").read_text(encoding="utf-8"))["rows"]
    by_law = {row["law"]: row for row in rows}

    assert manifest["preset_id"] == V111_RAW_HYBRID_PAPER_PRESET_ID
    assert "--preset v1.11-paper-evidence-package" in manifest["reproducibility"]["command"]
    assert by_law["Logistic diagnostic"]["compile_depth"] == 15
    assert by_law["Planck diagnostic"]["compile_depth"] == 14


def test_raw_hybrid_cli_refuses_silent_overwrite(tmp_path):
    output_dir = tmp_path / "paper"
    parser = build_parser()
    first = parser.parse_args(["raw-hybrid-paper", "--output-dir", str(output_dir), "--require-existing"])
    assert first.func(first) == 0

    second = parser.parse_args(["raw-hybrid-paper", "--output-dir", str(output_dir), "--require-existing"])
    with pytest.raises(RawHybridPaperError):
        second.func(second)

    stale = output_dir / "stale.txt"
    stale.write_text("preserve me", encoding="utf-8")
    replacement = parser.parse_args(["raw-hybrid-paper", "--output-dir", str(output_dir), "--require-existing", "--overwrite"])
    assert replacement.func(replacement) == 0
    assert stale.read_text(encoding="utf-8") == "preserve me"
    assert (output_dir / "manifest.json").exists()


def test_raw_hybrid_cli_refuses_unsafe_overwrite_targets(tmp_path):
    parser = build_parser()

    cwd_args = parser.parse_args(["raw-hybrid-paper", "--output-dir", ".", "--require-existing", "--overwrite"])
    with pytest.raises(RawHybridPaperError, match="unsafe output directory"):
        cwd_args.func(cwd_args)

    parent_dir = tmp_path / "parent"
    (parent_dir / "paper").mkdir(parents=True)
    parent_args = parser.parse_args(
        ["raw-hybrid-paper", "--output-dir", str(parent_dir), "--require-existing", "--overwrite"]
    )
    with pytest.raises(RawHybridPaperError, match="unmanaged directory"):
        parent_args.func(parent_args)

    unmanaged_dir = tmp_path / "unmanaged"
    unmanaged_dir.mkdir()
    (unmanaged_dir / "notes.txt").write_text("not generated by raw-hybrid-paper", encoding="utf-8")
    unmanaged_args = parser.parse_args(
        ["raw-hybrid-paper", "--output-dir", str(unmanaged_dir), "--require-existing", "--overwrite"]
    )
    with pytest.raises(RawHybridPaperError, match="unmanaged directory"):
        unmanaged_args.func(unmanaged_args)


def test_raw_hybrid_cli_reproduction_command_quotes_shell_sensitive_paths(tmp_path):
    output_dir = tmp_path / "paper root; echo injected"
    args = build_parser().parse_args(["raw-hybrid-paper", "--output-dir", str(output_dir), "--require-existing", "--overwrite"])

    assert args.func(args) == 0
    manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
    command = manifest["reproducibility"]["command"]

    assert command == shlex.join(shlex.split(command))
    assert shlex.split(command) == [
        "PYTHONPATH=src",
        "python",
        "-m",
        "eml_symbolic_regression.cli",
        "raw-hybrid-paper",
        "--output-dir",
        str(output_dir),
        "--require-existing",
        "--overwrite",
    ]
