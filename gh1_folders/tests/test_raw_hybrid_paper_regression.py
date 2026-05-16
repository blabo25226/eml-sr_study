import hashlib
import json
import re
from pathlib import Path


PACKAGE_ROOT = Path("artifacts/paper/v1.9/raw-hybrid")

EXPECTED_FILES = {
    "manifest.json",
    "source-locks.json",
    "regime-summary.json",
    "raw-hybrid-report.md",
    "scientific-law-table.json",
    "scientific-law-table.csv",
    "scientific-law-table.md",
    "claim-boundaries.md",
    "centered-negative-diagnostics.md",
}

REQUIRED_SOURCE_IDS = {
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
    "v1.9-repair-summary-markdown",
    "v1.6-beer-lambert-run",
    "v1.6-shockley-run",
    "v1.6-planck-diagnostic-run",
    "v1.6-logistic-diagnostic-run",
    "v1.6-historical-michaelis-diagnostic-run",
}

REQUIRED_REGIMES = {
    "pure_blind",
    "scaffolded",
    "compile_only",
    "warm_start",
    "same_ast_return",
    "repaired",
    "refit",
    "perturbed_basin",
}

REQUIRED_COLUMNS = {
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

REQUIRED_LAWS = {
    "Beer-Lambert",
    "Shockley",
    "Arrhenius",
    "Michaelis-Menten",
    "Planck diagnostic",
    "Logistic diagnostic",
    "Historical Michaelis diagnostic",
}

FORBIDDEN_PHRASES = {
    "universal blind recovery",
    "warm-start blind discovery",
    "same-ast blind discovery",
    "centered families are impossible",
    "intrinsically impossible",
    "planck solved",
}


def _read_json(name: str):
    return json.loads((PACKAGE_ROOT / name).read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def test_raw_hybrid_package_files_exist():
    missing = sorted(name for name in EXPECTED_FILES if not (PACKAGE_ROOT / name).exists())
    assert not missing, (
        "missing raw-hybrid package artifacts; run "
        "`PYTHONPATH=src python -m eml_symbolic_regression.cli raw-hybrid-paper "
        "--output-dir artifacts/paper/v1.9/raw-hybrid --require-existing --overwrite`: "
        f"{missing}"
    )


def test_raw_hybrid_manifest_and_source_locks_are_stable():
    manifest = _read_json("manifest.json")
    locks = _read_json("source-locks.json")

    assert manifest["schema"] == "eml.raw_hybrid_paper.v1"
    assert manifest["preset_id"] == "v1.9-raw-hybrid-paper"
    assert manifest["preset"]["id"] == "v1.9-raw-hybrid-paper"
    assert "raw-hybrid-paper" in manifest["reproducibility"]["command"]

    source_ids = {row["source_id"] for row in locks["sources"]}
    assert REQUIRED_SOURCE_IDS <= source_ids
    for row in locks["sources"]:
        path = Path(row["path"])
        assert path.is_file(), row["source_id"]
        assert re.fullmatch(r"[0-9a-f]{64}", row["sha256"]), row["source_id"]
        assert row["sha256"] == _sha256(path), row["source_id"]


def test_raw_hybrid_regime_summary_preserves_required_buckets():
    regimes = _read_json("regime-summary.json")

    assert REQUIRED_REGIMES <= set(regimes)
    assert regimes["pure_blind"]["runs"]
    assert regimes["scaffolded"]["runs"]
    assert regimes["perturbed_basin"]["runs"]
    assert all(row["start_mode"] == "blind" for row in regimes["pure_blind"]["runs"])
    assert not any(
        row["evidence_class"] in {"scaffolded_blind_training_recovered", "repaired_candidate"}
        for row in regimes["pure_blind"]["runs"]
    )


def test_scientific_law_table_locks_required_rows_and_fields():
    rows = _read_json("scientific-law-table.json")["rows"]
    by_law = {row["law"]: row for row in rows}

    assert REQUIRED_LAWS <= set(by_law)
    assert all(REQUIRED_COLUMNS <= set(row) for row in rows)
    assert by_law["Arrhenius"]["macro_hits"] == ["direct_division_template"]
    assert by_law["Michaelis-Menten"]["macro_hits"] == ["saturation_ratio_template"]
    assert "scaled_exp_minus_one_template" in by_law["Shockley"]["macro_hits"]
    assert by_law["Arrhenius"]["evidence_regime"] == "same_ast_return"
    assert by_law["Michaelis-Menten"]["evidence_regime"] == "same_ast_return"
    assert by_law["Planck diagnostic"]["compile_support"] == "unsupported"
    assert by_law["Logistic diagnostic"]["compile_support"] == "unsupported"
    assert by_law["Historical Michaelis diagnostic"]["evidence_regime"] == "historical_context"
    assert by_law["Historical Michaelis diagnostic"]["compile_support"] == "unsupported"


def test_report_claim_wording_preserves_boundaries():
    text = "\n".join(
        [
            (PACKAGE_ROOT / "raw-hybrid-report.md").read_text(encoding="utf-8"),
            (PACKAGE_ROOT / "claim-boundaries.md").read_text(encoding="utf-8"),
            (PACKAGE_ROOT / "centered-negative-diagnostics.md").read_text(encoding="utf-8"),
        ]
    ).lower()

    for phrase in ("not blind discovery", "same-family witness", "negative diagnostic"):
        assert phrase in text
    for phrase in FORBIDDEN_PHRASES:
        assert phrase not in text
