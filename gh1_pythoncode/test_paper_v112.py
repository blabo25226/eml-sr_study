import json

from eml_symbolic_regression.cli import (
    build_parser,
    paper_draft_command,
    paper_figures_command,
    paper_probes_command,
    paper_refresh_command,
    paper_supplement_command,
    paper_training_detail_command,
)
from eml_symbolic_regression.datasets import get_demo
from eml_symbolic_regression.optimize import TrainingConfig, fit_eml_tree
from eml_symbolic_regression.paper_v112 import (
    audit_v112_supplement,
    claim_taxonomy_rows,
    conventional_symbolic_baseline_probe_rows,
    logistic_strict_support_probe_rows,
    logistic_planck_negative_result_rows,
    motif_library_evolution_rows,
    refresh_run_rows,
    training_detail_rows_from_payload,
    v112_depth_refresh_suite,
    v112_shallow_refresh_suite,
    write_v112_bounded_probes,
    write_v112_draft,
    write_v112_paper_facing_assets,
    write_v112_supplement,
    write_v112_training_detail_assets,
)


def _json(path):
    return json.loads(open(path, encoding="utf-8").read())


def test_claim_taxonomy_separates_pure_blind_from_assisted_regimes():
    ledger = _json("artifacts/paper/v1.11/raw-hybrid/claim-ledger.json")

    rows = claim_taxonomy_rows(ledger)
    by_class = {row["evidence_class"]: row for row in rows}

    assert {
        "pure_blind",
        "scaffolded",
        "warm_start",
        "same_ast",
        "perturbed_basin",
        "repair_refit",
        "compile_only",
        "unsupported",
        "failed",
    } <= set(by_class)
    assert by_class["pure_blind"]["eligible_for_pure_blind_rate"] is True
    assert by_class["scaffolded"]["eligible_for_pure_blind_rate"] is False
    assert by_class["same_ast"]["eligible_for_pure_blind_rate"] is False
    assert by_class["unsupported"]["eligible_for_verifier_recovery_rate"] is False
    assert by_class["failed"]["eligible_for_verifier_recovery_rate"] is False


def test_write_v112_draft_outputs_sections_and_taxonomy(tmp_path):
    paths = write_v112_draft(output_dir=tmp_path / "draft")

    manifest = json.loads(paths.manifest_json.read_text(encoding="utf-8"))
    taxonomy = json.loads(paths.claim_taxonomy_json.read_text(encoding="utf-8"))
    abstract = paths.abstract_md.read_text(encoding="utf-8")
    results = paths.results_md.read_text(encoding="utf-8")
    limitations = paths.limitations_md.read_text(encoding="utf-8")

    assert manifest["schema"] == "eml.v112_paper_draft.v1"
    assert manifest["claim_boundary"].startswith("draft scaffold preserves")
    assert paths.methods_md.exists()
    assert paths.claim_taxonomy_csv.exists()
    assert any(row["evidence_class"] == "pure_blind" for row in taxonomy["rows"])
    assert "verifier-gated" in abstract
    assert "Logistic and Planck remain unsupported" in results
    assert "do not establish pure blind discovery" in limitations


def test_paper_draft_cli_writes_manifest(tmp_path, capsys):
    output_dir = tmp_path / "draft"
    args = build_parser().parse_args(["paper-draft", "--output-dir", str(output_dir)])

    assert args.func is paper_draft_command
    assert args.func(args) == 0

    captured = capsys.readouterr().out
    assert "paper draft: manifest ->" in captured
    assert (output_dir / "abstract.md").exists()
    assert (output_dir / "claim-taxonomy.md").exists()


def test_v112_shallow_refresh_suite_has_new_separate_seed_denominators(tmp_path):
    suite = v112_shallow_refresh_suite(tmp_path)
    runs = suite.expanded_runs()

    assert suite.id == "v1.12-shallow-refresh"
    assert len(runs) == 10
    assert {run.seed for run in runs} == {2, 3, 4, 5, 6}
    pure = [run for run in runs if run.case_id == "exp-pure-blind-seed-refresh"]
    scaffolded = [run for run in runs if run.case_id == "exp-scaffolded-seed-refresh"]
    assert len(pure) == 5
    assert len(scaffolded) == 5
    assert all(run.optimizer.scaffold_initializers == () for run in pure)
    assert all(run.optimizer.scaffold_initializers for run in scaffolded)


def test_v112_depth_refresh_suite_uses_current_code_depth_2_to_5_subset(tmp_path):
    suite = v112_depth_refresh_suite(tmp_path)
    runs = suite.expanded_runs()

    assert suite.id == "proof-depth-curve"
    assert len(runs) == 8
    assert {run.case_id for run in runs} == {"depth-2-blind", "depth-3-blind", "depth-4-blind", "depth-5-blind"}
    assert {run.optimizer.depth for run in runs} == {2, 3, 4, 5}
    assert {run.seed for run in runs} == {0, 1}
    assert all(run.start_mode == "blind" for run in runs)


def test_refresh_run_rows_exposes_seed_depth_status_and_artifact_path():
    aggregate = {
        "runs": [
            {
                "suite_id": "suite",
                "case_id": "case",
                "formula": "exp",
                "start_mode": "blind",
                "seed": 2,
                "optimizer": {"depth": 1, "steps": 4, "restarts": 1, "scaffold_initializers": []},
                "evidence_class": "blind_training_recovered",
                "classification": "blind_recovery",
                "status": "recovered",
                "claim_status": "recovered",
                "metrics": {"verifier_status": "recovered", "best_loss": 0.0},
                "reason": "recovered",
                "artifact_path": "artifacts/run.json",
            }
        ]
    }

    rows = refresh_run_rows(aggregate, source="unit")

    assert rows == [
        {
            "source": "unit",
            "suite_id": "suite",
            "case_id": "case",
            "formula": "exp",
            "start_mode": "blind",
            "seed": 2,
            "depth": 1,
            "steps": 4,
            "restarts": 1,
            "scaffold_initializers": "",
            "evidence_class": "blind_training_recovered",
            "classification": "blind_recovery",
            "status": "recovered",
            "claim_status": "recovered",
            "verifier_status": "recovered",
            "best_loss": 0.0,
            "post_snap_loss": None,
            "snap_min_margin": None,
            "reason": "recovered",
            "artifact_path": "artifacts/run.json",
            "claim_boundary": "row belongs only to its source suite/start-mode denominator",
        }
    ]


def test_paper_refresh_cli_is_registered():
    args = build_parser().parse_args(["paper-refresh", "--output-dir", "artifacts/tmp-refresh", "--overwrite"])

    assert args.func is paper_refresh_command
    assert args.output_dir == "artifacts/tmp-refresh"
    assert args.overwrite is True


def test_motif_library_evolution_rows_include_required_laws_and_planck_note():
    payload = _json("artifacts/diagnostics/v1.11-paper-ablations/motif-depth-deltas.json")

    rows = motif_library_evolution_rows(payload)
    by_law = {row["law"]: row for row in rows}

    assert {"Logistic diagnostic", "Planck diagnostic", "Shockley", "Arrhenius", "Michaelis-Menten"} <= set(by_law)
    assert by_law["Logistic diagnostic"]["baseline_depth"] == 27
    assert by_law["Logistic diagnostic"]["motif_depth"] == 15
    assert by_law["Planck diagnostic"]["motif_depth"] == 14
    assert "24 -> 14" in by_law["Planck diagnostic"]["depth_convention_note"]
    assert by_law["Shockley"]["strict_support"] is True


def test_negative_result_rows_keep_logistic_and_planck_unpromoted():
    scientific = _json("artifacts/paper/v1.11/raw-hybrid/scientific-law-table.json")
    motif = _json("artifacts/diagnostics/v1.11-paper-ablations/motif-depth-deltas.json")
    probes = _json("artifacts/campaigns/v1.11-logistic-planck-probes/aggregate.json")

    rows = logistic_planck_negative_result_rows(scientific, motif, probes)
    by_formula = {row["formula_id"]: row for row in rows}

    assert by_formula["logistic"]["promotion"] == "no"
    assert by_formula["logistic"]["compile_support"] == "unsupported"
    assert by_formula["logistic"]["relaxed_motif_depth"] == 15
    assert by_formula["planck"]["promotion"] == "no"
    assert by_formula["planck"]["compile_support"] == "unsupported"
    assert by_formula["planck"]["relaxed_motif_depth"] == 14


def test_write_v112_paper_facing_assets_outputs_captions_tables_and_pipeline(tmp_path):
    draft = write_v112_draft(output_dir=tmp_path / "draft")
    paths = write_v112_paper_facing_assets(output_dir=draft.output_dir, refresh_manifest=tmp_path / "missing-refresh.json")

    manifest = json.loads(paths.manifest_json.read_text(encoding="utf-8"))
    motif = json.loads(paths.motif_evolution_json.read_text(encoding="utf-8"))
    negative = json.loads(paths.negative_results_json.read_text(encoding="utf-8"))
    pipeline = paths.pipeline_svg.read_text(encoding="utf-8")
    captions = paths.figure_captions_md.read_text(encoding="utf-8")

    assert manifest["schema"] == "eml.v112_paper_facing_assets.v1"
    assert manifest["counts"]["motif_rows"] >= 5
    assert any(row["law"] == "Planck diagnostic" for row in motif["rows"])
    assert all(row["promotion"] == "no" for row in negative["rows"])
    assert "<svg" in pipeline
    assert "data preparation" in captions


def test_paper_figures_cli_writes_manifest(tmp_path, capsys):
    output_dir = tmp_path / "draft"
    write_v112_draft(output_dir=output_dir)
    args = build_parser().parse_args(["paper-figures", "--output-dir", str(output_dir)])

    assert args.func is paper_figures_command
    assert args.func(args) == 0

    captured = capsys.readouterr().out
    assert "paper figures: manifest ->" in captured
    assert (output_dir / "figure-captions.md").exists()
    assert (output_dir / "figures" / "pipeline.svg").exists()


def test_conventional_symbolic_baseline_probe_reports_unavailable_without_local_module():
    rows = conventional_symbolic_baseline_probe_rows(("definitely_missing_sr_package_for_test",))

    assert rows[0]["status"] == "unavailable"
    assert rows[0]["diagnostic_only"] is True
    assert rows[0]["denominator_policy"] == "excluded from EML recovery denominators"


def test_logistic_strict_support_probe_keeps_strict_gate_and_no_promotion():
    rows, diagnostic = logistic_strict_support_probe_rows(points=12, seed=0)
    row = rows[0]

    assert diagnostic["schema"] == "eml.v112_logistic_strict_support_diagnostic.v1"
    assert row["strict_gate"] == 13
    assert row["strict_status"] == "unsupported"
    assert row["strict_reason"] == "depth_exceeded"
    assert row["relaxed_depth"] == 15
    assert row["depth_gap_to_strict_gate"] == 2
    assert row["relaxed_macro_hits"] == ["exponential_saturation_template"]
    assert row["relaxed_validation_passed"] is True
    assert row["promotion"] == "no"


def test_write_v112_bounded_probes_outputs_baseline_and_logistic_tables(tmp_path):
    output_dir = tmp_path / "draft"
    paths = write_v112_bounded_probes(
        output_dir=output_dir,
        baseline_modules=("definitely_missing_sr_package_for_test",),
        logistic_points=12,
    )

    manifest = json.loads(paths.manifest_json.read_text(encoding="utf-8"))
    baseline = json.loads(paths.baseline_probe_json.read_text(encoding="utf-8"))
    logistic = json.loads(paths.logistic_probe_json.read_text(encoding="utf-8"))

    assert manifest["schema"] == "eml.v112_bounded_probes.v1"
    assert manifest["statuses"]["baseline"] == "unavailable"
    assert manifest["statuses"]["logistic_promotion"] == "no"
    assert baseline["rows"][0]["status"] == "unavailable"
    assert logistic["rows"][0]["strict_gate"] == 13
    assert paths.logistic_diagnostic_json.exists()


def test_paper_probes_cli_writes_manifest(tmp_path, capsys):
    output_dir = tmp_path / "draft"
    args = build_parser().parse_args(["paper-probes", "--output-dir", str(output_dir)])

    assert args.func is paper_probes_command
    assert args.func(args) == 0

    captured = capsys.readouterr().out
    assert "paper probes: manifest ->" in captured
    assert (output_dir / "bounded-probes-manifest.json").exists()
    assert (output_dir / "tables" / "logistic-strict-support-probe.md").exists()


def test_optimizer_manifest_records_step_trace_for_training_dynamics():
    spec = get_demo("exp")
    splits = spec.make_splits(points=8, seed=0)
    fit = fit_eml_tree(
        splits[0].inputs,
        splits[0].target,
        TrainingConfig(depth=1, steps=3, hardening_steps=2, restarts=1, scaffold_initializers=(), seed=0),
        verification_splits=splits,
    )

    restart = fit.manifest["restarts"][0]
    trace = restart["trace"]

    assert restart["trace_schema"] == "eml.training_step_trace.v1"
    assert len(trace) == 5
    assert trace[0]["phase"] == "fit"
    assert trace[-1]["phase"] == "hardening"
    assert {"fit_loss", "objective_loss", "entropy", "expected_child_use", "clamp_count"} <= set(trace[0])
    assert fit.manifest["trace_summary"]["total_steps_recorded"] == 5


def test_training_detail_rows_extract_step_and_candidate_lifecycle(tmp_path):
    spec = get_demo("exp")
    splits = spec.make_splits(points=8, seed=1)
    fit = fit_eml_tree(
        splits[0].inputs,
        splits[0].target,
        TrainingConfig(depth=1, steps=2, hardening_steps=1, restarts=1, scaffold_initializers=(), seed=1),
        verification_splits=splits,
    )
    payload = {
        "run": {"run_id": "unit-run", "suite_id": "unit", "case_id": "exp", "formula": "exp", "start_mode": "blind", "seed": 1},
        "budget": {"depth": 1, "steps": 2, "hardening_steps": 1},
        "metrics": {"verifier_status": fit.verification.status if fit.verification else None},
        "trained_eml_candidate": fit.manifest,
        "status": fit.status,
        "claim_status": fit.verification.status if fit.verification else fit.status,
        "training_mode": "unit",
        "evidence_class": "unit",
    }

    step_rows, summary_rows, candidate_rows = training_detail_rows_from_payload(payload, source="unit", artifact_path=tmp_path / "run.json")

    assert len(step_rows) == 3
    assert summary_rows[0]["steps_recorded"] == 3
    assert any(row["is_selected"] for row in candidate_rows)


def test_write_v112_training_detail_assets_outputs_tables_and_figures(tmp_path):
    paths = write_v112_training_detail_assets(output_dir=tmp_path / "training-detail")

    manifest = json.loads(paths.manifest_json.read_text(encoding="utf-8"))
    trace_table = json.loads(paths.step_trace_json.read_text(encoding="utf-8"))
    lifecycle = json.loads(paths.candidate_lifecycle_json.read_text(encoding="utf-8"))

    assert manifest["schema"] == "eml.v112_training_detail_assets.v1"
    assert manifest["counts"]["step_trace_rows"] > 0
    assert manifest["counts"]["candidate_lifecycle_rows"] > 0
    assert any("objective_loss" in row for row in trace_table["rows"])
    assert any(row["is_selected"] is True for row in lifecycle["rows"])
    assert "<svg" in paths.shallow_loss_svg.read_text(encoding="utf-8")


def test_paper_training_detail_cli_writes_manifest(tmp_path, capsys):
    output_dir = tmp_path / "training-detail"
    args = build_parser().parse_args(["paper-training-detail", "--output-dir", str(output_dir)])

    assert args.func is paper_training_detail_command
    assert args.func(args) == 0

    captured = capsys.readouterr().out
    assert "paper training detail: manifest ->" in captured
    assert (output_dir / "tables" / "training-step-traces.csv").exists()
    assert (output_dir / "figures" / "depth-loss-curves.svg").exists()


def test_write_v112_supplement_source_locks_and_audit_pass(tmp_path):
    paths = write_v112_supplement(output_dir=tmp_path / "supplement")

    manifest = json.loads(paths.manifest_json.read_text(encoding="utf-8"))
    source_locks = json.loads(paths.source_locks_json.read_text(encoding="utf-8"))
    audit = json.loads(paths.claim_audit_json.read_text(encoding="utf-8"))
    roles = {row["role"] for row in source_locks["sources"]}

    assert manifest["schema"] == "eml.v112_supplement.v1"
    assert manifest["audit_status"] == "passed"
    assert manifest["source_lock_count"] == source_locks["source_count"]
    assert {"v112_draft", "v112_paper_facing", "v112_evidence_refresh", "v112_bounded_probe"} <= roles
    assert audit["status"] == "passed"
    assert any(check["id"] == "bounded_probe_status_visible" for check in audit["checks"])
    assert paths.reproduction_md.exists()


def test_v112_supplement_audit_checks_expected_claim_boundaries():
    audit = audit_v112_supplement(
        draft_dir="artifacts/paper/v1.11/draft",
        refresh_dir="artifacts/campaigns/v1.12-evidence-refresh",
        source_locks=[
            {"role": "v112_draft", "source_path": "draft", "sha256": "x"},
            {"role": "v112_paper_facing", "source_path": "facing", "sha256": "x"},
            {"role": "v112_evidence_refresh", "source_path": "refresh", "sha256": "x"},
            {"role": "v112_bounded_probe", "source_path": "probe", "sha256": "x"},
        ],
    )

    checks = {check["id"]: check for check in audit["checks"]}
    assert audit["status"] == "passed"
    assert checks["logistic_planck_negative_rows_not_promoted"]["status"] == "passed"
    assert checks["depth_refresh_counts"]["status"] == "passed"
    assert checks["training_detail_artifacts_present"]["status"] == "passed"


def test_paper_supplement_cli_writes_manifest(tmp_path, capsys):
    output_dir = tmp_path / "supplement"
    args = build_parser().parse_args(["paper-supplement", "--output-dir", str(output_dir)])

    assert args.func is paper_supplement_command
    assert args.func(args) == 0

    captured = capsys.readouterr().out
    assert "paper supplement: manifest ->" in captured
    assert (output_dir / "manifest.json").exists()
    assert (output_dir / "claim-audit.json").exists()
