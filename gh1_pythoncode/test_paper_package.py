import json

import pytest

from eml_symbolic_regression.cli import build_parser, paper_package_command
from eml_symbolic_regression.paper_package import PaperPackageError, audit_v111_claims, write_v111_paper_package


def _json(path):
    return json.loads(open(path, encoding="utf-8").read())


def test_audit_keeps_logistic_and_planck_unsupported():
    scientific = _json("artifacts/paper/v1.11/raw-hybrid/scientific-law-table.json")
    claim_ledger = _json("artifacts/paper/v1.11/raw-hybrid/claim-ledger.json")
    assets_manifest = _json("artifacts/paper/v1.11/assets/manifest.json")
    training = _json("artifacts/campaigns/v1.11-paper-training/aggregate.json")
    probes = _json("artifacts/campaigns/v1.11-logistic-planck-probes/aggregate.json")
    regime_rows = _json("artifacts/paper/v1.11/assets/tables/regime_recovery.json")["rows"]

    audit = audit_v111_claims(
        scientific_law_table=scientific,
        claim_ledger=claim_ledger,
        assets_manifest=assets_manifest,
        training_aggregate=training,
        probe_aggregate=probes,
        regime_rows=regime_rows,
        source_locks=[{"source_path": "x", "sha256": "abc"}],
    )

    assert audit["status"] == "passed"
    checks = {check["id"]: check for check in audit["checks"]}
    assert checks["logistic_remains_unsupported"]["status"] == "passed"
    assert checks["planck_remains_unsupported"]["status"] == "passed"
    assert checks["regime_denominators_are_separated"]["status"] == "passed"


def test_audit_fails_if_logistic_is_promoted_without_source_support():
    scientific = _json("artifacts/paper/v1.11/raw-hybrid/scientific-law-table.json")
    mutated = json.loads(json.dumps(scientific))
    for row in mutated["rows"]:
        if row["law"] == "Logistic diagnostic":
            row["compile_support"] = "supported"
            row["verifier_status"] = "recovered"
    claim_ledger = _json("artifacts/paper/v1.11/raw-hybrid/claim-ledger.json")
    assets_manifest = _json("artifacts/paper/v1.11/assets/manifest.json")
    training = _json("artifacts/campaigns/v1.11-paper-training/aggregate.json")
    probes = _json("artifacts/campaigns/v1.11-logistic-planck-probes/aggregate.json")
    regime_rows = _json("artifacts/paper/v1.11/assets/tables/regime_recovery.json")["rows"]

    audit = audit_v111_claims(
        scientific_law_table=mutated,
        claim_ledger=claim_ledger,
        assets_manifest=assets_manifest,
        training_aggregate=training,
        probe_aggregate=probes,
        regime_rows=regime_rows,
        source_locks=[{"source_path": "x", "sha256": "abc"}],
    )

    assert audit["status"] == "failed"
    checks = {check["id"]: check for check in audit["checks"]}
    assert checks["logistic_remains_unsupported"]["status"] == "failed"


def test_write_v111_paper_package_writes_manifest_locks_and_audit(tmp_path):
    paths = write_v111_paper_package(output_dir=tmp_path / "paper")

    manifest = json.loads(paths.manifest_json.read_text(encoding="utf-8"))
    locks = json.loads(paths.source_locks_json.read_text(encoding="utf-8"))
    audit = json.loads(paths.claim_audit_json.read_text(encoding="utf-8"))
    readiness = paths.paper_readiness_md.read_text(encoding="utf-8")

    assert manifest["schema"] == "eml.v111_paper_package.v1"
    assert manifest["audit_status"] == "passed"
    assert locks["schema"] == "eml.v111_paper_source_locks.v1"
    assert locks["source_count"] >= 30
    assert audit["status"] == "passed"
    assert (paths.output_dir / "figures" / "scientific_law_support.svg").exists()
    assert (paths.output_dir / "tables" / "regime_recovery.csv").exists()
    assert (paths.output_dir / "raw-hybrid" / "scientific-law-table.json").exists()
    assert "Logistic/Planck probes: 0/4 recovered" in readiness
    assert "broad blind symbolic-regression superiority" in readiness


def test_paper_package_refuses_existing_manifest_without_overwrite(tmp_path):
    output_dir = tmp_path / "paper"
    write_v111_paper_package(output_dir=output_dir)

    with pytest.raises(PaperPackageError):
        write_v111_paper_package(output_dir=output_dir)

    refreshed = write_v111_paper_package(output_dir=output_dir, overwrite=True)
    assert refreshed.manifest_json.exists()


def test_paper_package_cli_writes_package(tmp_path, capsys):
    output_dir = tmp_path / "paper"
    args = build_parser().parse_args(["paper-package", "--output-dir", str(output_dir)])

    assert args.func is paper_package_command
    assert args.func(args) == 0

    captured = capsys.readouterr().out
    assert "paper package: manifest ->" in captured
    assert "(passed)" in captured
    assert (output_dir / "manifest.json").exists()
    assert (output_dir / "claim-audit.json").exists()
