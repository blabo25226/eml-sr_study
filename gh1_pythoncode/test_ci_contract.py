import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate-ci-contract.py"
SPEC = importlib.util.spec_from_file_location("validate_ci_contract", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
ci_contract = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ci_contract)


def test_dev_ci_contract_validates_current_tree():
    assert ci_contract.validate_dev(ROOT) == []


def test_public_snapshot_contract_accepts_minimal_tree(tmp_path):
    for relative in ci_contract.PUBLIC_REQUIRED_PATHS:
        path = tmp_path / relative
        if "." in path.name:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("placeholder\n", encoding="utf-8")
        else:
            path.mkdir(parents=True, exist_ok=True)

    assert ci_contract.validate_public_snapshot(tmp_path) == []


def test_public_snapshot_contract_rejects_private_and_raw_artifacts(tmp_path):
    for relative in ci_contract.PUBLIC_REQUIRED_PATHS:
        path = tmp_path / relative
        if "." in path.name:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("placeholder\n", encoding="utf-8")
        else:
            path.mkdir(parents=True, exist_ok=True)
    (tmp_path / ".planning").mkdir()
    raw_run = tmp_path / "artifacts" / "campaigns" / "suite" / "runs" / "raw.json"
    raw_run.parent.mkdir(parents=True)
    raw_run.write_text("{}\n", encoding="utf-8")
    aggregate = tmp_path / "artifacts" / "campaigns" / "suite" / "aggregate.json"
    aggregate.write_text("{}\n", encoding="utf-8")

    errors = ci_contract.validate_public_snapshot(tmp_path)

    assert "public snapshot must not contain .planning" in errors
    assert any("artifacts/campaigns/suite/runs" in error for error in errors)
    assert "public snapshot must not contain artifacts/campaigns/suite/aggregate.json" in errors


def test_ci_workflow_declares_required_jobs_and_smoke_commands():
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "Core unit contracts" in workflow
    assert "Selected integration smoke" in workflow
    assert "Clean-room publication smoke" in workflow
    assert "Branch and public snapshot contract" in workflow
    assert "scripts/publication-rebuild.sh" in workflow
    assert "validate-ci-contract.py --mode public-snapshot" in workflow
