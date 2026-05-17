import csv
import json

from eml_symbolic_regression.cli import (
    build_parser,
    geml_v117_neighborhoods_command,
    geml_v117_package_command,
    geml_v117_rank_candidates_command,
    geml_v117_sandbox_command,
    geml_v117_snap_diagnostics_command,
)
from eml_symbolic_regression.master_tree import SoftEMLTree
from eml_symbolic_regression.paper_v117 import (
    write_v117_candidate_ranking,
    write_v117_evidence_package,
    write_v117_neighborhood_candidates,
    write_v117_recovery_sandbox,
    write_v117_snap_diagnostics,
)


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_v117_fixture_campaign(campaign_dir):
    table_dir = campaign_dir / "tables"
    table_dir.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "pair_id": "sin_pi:seed0:depth3",
            "formula": "sin_pi",
            "target_family": "periodic",
            "seed": "0",
            "comparison_outcome": "ipi_lower_post_snap_mse",
            "raw_status": "snapped_but_failed",
            "ipi_status": "snapped_but_failed",
            "raw_verification_outcome": "failed",
            "ipi_verification_outcome": "failed",
            "raw_trained_exact_recovery": "False",
            "ipi_trained_exact_recovery": "False",
            "raw_selected_candidate_id": "raw-selected",
            "ipi_selected_candidate_id": "ipi-selected",
            "raw_fallback_candidate_id": "raw-fallback",
            "ipi_fallback_candidate_id": "ipi-fallback",
            "raw_snap_min_margin": "0.42",
            "ipi_snap_min_margin": "0.03",
            "raw_snap_active_node_count": "7",
            "ipi_snap_active_node_count": "9",
            "raw_low_margin_slot_count": "0",
            "ipi_low_margin_slot_count": "2",
            "raw_lowest_margin_slots_json": "[]",
            "ipi_lowest_margin_slots_json": json.dumps(
                [{"slot": "root.left", "choice": "child", "probability": 0.51, "margin": 0.03}]
            ),
            "raw_low_confidence_alternatives_json": "[]",
            "ipi_low_confidence_alternatives_json": json.dumps(
                [{"slot": "root.left", "alternatives": [{"choice": "var:x", "probability_gap": 0.03}]}]
            ),
            "raw_pre_snap_mse": "0.2",
            "ipi_pre_snap_mse": "0.2",
            "raw_post_snap_mse": "0.3",
            "ipi_post_snap_mse": "0.1",
            "raw_post_snap_minus_soft_best": "0.28",
            "ipi_post_snap_minus_soft_best": "0.08",
            "raw_post_snap_minus_pre_snap": "0.1",
            "ipi_post_snap_minus_pre_snap": "-0.1",
            "raw_branch_cut_crossing_count": "0",
            "ipi_branch_cut_crossing_count": "0",
            "raw_branch_cut_proximity_count": "0",
            "ipi_branch_cut_proximity_count": "4",
            "raw_branch_input_count": "0",
            "ipi_branch_input_count": "8",
            "raw_artifact_path": "artifacts/raw.json",
            "ipi_artifact_path": "artifacts/ipi.json",
        },
        {
            "pair_id": "exp:seed0:depth3",
            "formula": "exp",
            "target_family": "negative_control",
            "seed": "0",
            "comparison_outcome": "raw_recovery_win",
            "raw_status": "recovered",
            "ipi_status": "snapped_but_failed",
            "raw_verification_outcome": "recovered",
            "ipi_verification_outcome": "failed",
            "raw_trained_exact_recovery": "True",
            "ipi_trained_exact_recovery": "False",
            "raw_selected_candidate_id": "raw-exact",
            "ipi_selected_candidate_id": "ipi-failed",
            "raw_snap_min_margin": "0.9",
            "ipi_snap_min_margin": "0.9",
        },
    ]
    fieldnames = sorted({key for row in rows for key in row})
    with (table_dir / "geml-paired-comparison.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    _write_json(table_dir / "geml-paired-summary.json", {"schema": "fixture", "paired_rows": 2})
    _write_json(campaign_dir / "campaign-manifest.json", {"schema": "fixture"})


def _write_v117_package_inputs(tmp_path, *, exact_signal):
    v116 = tmp_path / "v116"
    snap = tmp_path / "snap"
    neighborhoods = tmp_path / "neighborhoods"
    ranking = tmp_path / "ranking"
    sandbox = tmp_path / "sandbox"
    _write_json(v116 / "manifest.json", {"schema": "eml.v116_final_decision_manifest.v1", "decision": "inconclusive"})
    _write_json(snap / "manifest.json", {"schema": "eml.v117_snap_diagnostics_manifest.v1", "outputs": {}})
    _write_json(snap / "snap-diagnostics.json", {"schema": "eml.v117_snap_diagnostics.v1", "rows": [{"diagnostic_id": "d0"}]})
    _write_json(snap / "snap-neighborhood-seeds.json", {"schema": "eml.v117_snap_neighborhood_seeds.v1", "rows": [{"seed_id": "s0"}]})
    _write_json(neighborhoods / "manifest.json", {"schema": "eml.v117_neighborhood_manifest.v1", "outputs": {}})
    _write_json(neighborhoods / "neighborhood-candidates.json", {"schema": "eml.v117_neighborhood_candidates.v1", "rows": [{"candidate_uid": "c0"}]})
    ranked_rows = [
        {
            "candidate_uid": "c0",
            "candidate_id": "exact" if exact_signal else "loss-only",
            "target_family": "periodic",
            "operator_family": "ipi_eml",
            "evidence_class": "exact_recovery" if exact_signal else "loss_only",
            "selected": True,
        }
    ]
    _write_json(ranking / "manifest.json", {"schema": "eml.v117_candidate_ranking_manifest.v1", "outputs": {}, "counts": {"total": 1}})
    _write_json(ranking / "ranked-candidates.json", {"schema": "eml.v117_candidate_ranking.v1", "rows": ranked_rows})
    sandbox_decision = "exact_signal_found" if exact_signal else "no_exact_signal"
    sandbox_gate = "allow_next_campaign_planning" if exact_signal else "block_broader_campaigns"
    natural_exact_count = 1 if exact_signal else 0
    _write_json(
        sandbox / "manifest.json",
        {
            "schema": "eml.v117_recovery_sandbox_manifest.v1",
            "decision": sandbox_decision,
            "exact_signal_found": exact_signal,
            "broader_campaign_gate": sandbox_gate,
            "outputs": {},
        },
    )
    _write_json(
        sandbox / "sandbox-results.json",
        {
            "schema": "eml.v117_recovery_sandbox.v1",
            "decision": sandbox_decision,
            "exact_signal_found": exact_signal,
            "broader_campaign_gate": sandbox_gate,
            "natural_exact_recovery_count": natural_exact_count,
            "negative_control_exact_recovery_count": 0,
            "summary_rows": [{"group": "ipi_eml:periodic", "exact_recovery": natural_exact_count}],
            "selected_exact_candidates": ranked_rows if exact_signal else [],
        },
    )
    return {
        "v116": v116,
        "snap": snap,
        "neighborhoods": neighborhoods,
        "ranking": ranking,
        "sandbox": sandbox,
    }


def test_write_v117_snap_diagnostics_emits_low_margin_raw_and_ipi_rows(tmp_path):
    campaign_dir = tmp_path / "campaign"
    _write_v117_fixture_campaign(campaign_dir)

    paths = write_v117_snap_diagnostics(tmp_path / "snap", campaign_dir=campaign_dir)

    manifest = json.loads(paths.manifest_json.read_text(encoding="utf-8"))
    diagnostics = json.loads(paths.snap_diagnostics_json.read_text(encoding="utf-8"))["rows"]
    seeds = json.loads(paths.snap_neighborhood_seeds_json.read_text(encoding="utf-8"))["rows"]
    csv_text = paths.snap_diagnostics_csv.read_text(encoding="utf-8")

    assert manifest["schema"] == "eml.v117_snap_diagnostics_manifest.v1"
    assert manifest["counts"]["diagnostic_rows"] == 4
    assert manifest["counts"]["neighborhood_seed_rows"] == 2
    assert any(row["operator_family"] == "raw_eml" for row in diagnostics)
    ipi = next(row for row in diagnostics if row["candidate_id"] == "ipi-selected")
    assert ipi["snap_mismatch_class"] == "low_margin_snap_mismatch"
    assert ipi["neighborhood_seed"] is True
    assert "root.left" in ipi["lowest_margin_slots_json"]
    assert "raw-selected" in csv_text
    assert {row["target_formula_leakage"] for row in seeds} == {False}


def test_v117_snap_diagnostics_do_not_seed_exact_recovery_rows(tmp_path):
    campaign_dir = tmp_path / "campaign"
    _write_v117_fixture_campaign(campaign_dir)

    paths = write_v117_snap_diagnostics(tmp_path / "snap", campaign_dir=campaign_dir)
    seeds = json.loads(paths.snap_neighborhood_seeds_json.read_text(encoding="utf-8"))["rows"]

    assert all(row["pair_id"] == "sin_pi:seed0:depth3" for row in seeds)
    assert [row["operator_family"] for row in seeds] == ["ipi_eml", "raw_eml"]


def test_cli_registers_geml_v117_snap_diagnostics():
    args = build_parser().parse_args(["geml-v117-snap-diagnostics", "--output-dir", "out", "--campaign-dir", "campaign"])
    assert args.func is geml_v117_snap_diagnostics_command
    assert args.campaign_dir == "campaign"


def test_write_v117_neighborhood_candidates_generates_bounded_deterministic_variants(tmp_path):
    snap_dir = tmp_path / "snap"
    artifact = tmp_path / "candidate.json"
    tree = SoftEMLTree(2, ("x",))
    tree.set_slot("root", "left", "child", strength=40.0)
    tree.set_slot("root", "right", "const:1", strength=40.0)
    tree.set_slot("root.L", "left", "var:x", strength=40.0)
    tree.set_slot("root.L", "right", "const:1", strength=40.0)
    tree.root.right_logits.data.copy_(tree.root.right_logits.data.new_tensor([2.0, 1.9, 0.0]))
    tree.root.left_child.left_logits.data.copy_(tree.root.left_child.left_logits.data.new_tensor([1.8, 2.0]))
    snap = tree.snap()
    candidate = {
        "candidate_id": "raw-selected",
        "snap": snap.as_dict(),
        "slot_alternatives": [item.as_dict() for item in tree.active_slot_alternatives(top_k=1, max_slots=2)],
    }
    _write_json(
        artifact,
        {
            "trained_eml_candidate": {
                "config": {
                    "variables": ["x"],
                    "constants": ["1"],
                    "operator_family": tree.operator_family.as_dict(),
                },
                "candidates": [candidate],
                "selected_candidate": candidate,
            }
        },
    )
    _write_json(
        snap_dir / "snap-neighborhood-seeds.json",
        {
            "schema": "fixture",
            "rows": [
                {
                    "seed_id": "sin_pi:seed0:raw:selected",
                    "pair_id": "sin_pi:seed0:depth2",
                    "formula": "sin_pi",
                    "target_family": "periodic",
                    "seed": "0",
                    "operator_family": "raw_eml",
                    "candidate_id": "raw-selected",
                    "fallback_candidate_id": "raw-fallback",
                    "comparison_outcome": "raw_lower_post_snap_mse",
                    "artifact_path": str(artifact),
                    "target_formula_leakage": False,
                }
            ],
        },
    )

    first = write_v117_neighborhood_candidates(tmp_path / "neighborhoods-a", snap_diagnostics_dir=snap_dir, candidate_budget=6)
    second = write_v117_neighborhood_candidates(tmp_path / "neighborhoods-b", snap_diagnostics_dir=snap_dir, candidate_budget=6)

    first_rows = json.loads(first.neighborhood_candidates_json.read_text(encoding="utf-8"))["rows"]
    second_rows = json.loads(second.neighborhood_candidates_json.read_text(encoding="utf-8"))["rows"]
    assert first_rows == second_rows
    assert [row["provenance"] for row in first_rows[:2]] == ["original_snap", "fallback_snap"]
    assert any(row["move_count"] == 1 for row in first_rows)
    assert any(row["move_count"] == 2 for row in first_rows)
    assert {row["target_formula_leakage"] for row in first_rows} == {False}
    assert all("target_tree" not in row for row in first_rows)


def test_cli_registers_geml_v117_neighborhoods():
    args = build_parser().parse_args(["geml-v117-neighborhoods", "--output-dir", "out", "--snap-diagnostics-dir", "snap"])
    assert args.func is geml_v117_neighborhoods_command
    assert args.snap_diagnostics_dir == "snap"


def test_write_v117_candidate_ranking_promotes_verifier_status_before_loss(tmp_path):
    neighborhoods = tmp_path / "neighborhoods"
    _write_json(
        neighborhoods / "neighborhood-candidates.json",
        {
            "schema": "fixture",
            "rows": [
                {
                    "candidate_uid": "seed:failed-low-loss",
                    "seed_id": "seed",
                    "pair_id": "pair",
                    "formula": "sin_pi",
                    "target_family": "periodic",
                    "seed": "0",
                    "operator_family": "ipi_eml",
                    "candidate_id": "failed-low-loss",
                    "provenance": "snap_neighborhood_1_slot",
                    "verifier_status": "failed",
                    "post_snap_mse": 1e-9,
                    "move_count": 1,
                    "heuristic_gap": 0.01,
                },
                {
                    "candidate_uid": "seed:recovered-higher-loss",
                    "seed_id": "seed",
                    "pair_id": "pair",
                    "formula": "sin_pi",
                    "target_family": "periodic",
                    "seed": "0",
                    "operator_family": "ipi_eml",
                    "candidate_id": "recovered-higher-loss",
                    "provenance": "snap_neighborhood_2_slot",
                    "verifier_status": "recovered",
                    "post_snap_mse": 0.1,
                    "high_precision_max_error": 1e-12,
                    "move_count": 2,
                    "heuristic_gap": 0.2,
                },
                {
                    "candidate_uid": "seed:original",
                    "seed_id": "seed",
                    "pair_id": "pair",
                    "formula": "sin_pi",
                    "target_family": "periodic",
                    "seed": "0",
                    "operator_family": "ipi_eml",
                    "candidate_id": "original",
                    "provenance": "original_snap",
                    "verifier_status": "failed",
                    "post_snap_mse": 0.2,
                },
                {
                    "candidate_uid": "seed:fallback",
                    "seed_id": "seed",
                    "pair_id": "pair",
                    "formula": "sin_pi",
                    "target_family": "periodic",
                    "seed": "0",
                    "operator_family": "ipi_eml",
                    "candidate_id": "fallback",
                    "provenance": "fallback_snap",
                    "verifier_status": "pending",
                },
            ],
        },
    )

    paths = write_v117_candidate_ranking(tmp_path / "ranking", neighborhoods_dir=neighborhoods)
    payload = json.loads(paths.ranked_candidates_json.read_text(encoding="utf-8"))
    rows = payload["rows"]

    assert payload["selected_candidate"]["candidate_id"] == "recovered-higher-loss"
    assert rows[0]["candidate_id"] == "recovered-higher-loss"
    failed = next(row for row in rows if row["candidate_id"] == "failed-low-loss")
    assert failed["evidence_class"] == "loss_only"
    assert "lower post-snap loss is diagnostic" in failed["rejection_reason"]
    assert payload["counts"]["by_evidence_class"]["exact_recovery"] == 1
    assert payload["counts"]["by_evidence_class"]["fallback"] == 1
    assert payload["counts"]["by_evidence_class"]["original_snap"] == 1
    assert payload["counts"]["by_evidence_class"]["loss_only"] == 1


def test_cli_registers_geml_v117_rank_candidates():
    args = build_parser().parse_args(["geml-v117-rank-candidates", "--output-dir", "out", "--neighborhoods-dir", "neighborhoods"])
    assert args.func is geml_v117_rank_candidates_command
    assert args.neighborhoods_dir == "neighborhoods"


def test_write_v117_recovery_sandbox_blocks_when_exact_signal_absent(tmp_path):
    ranking = tmp_path / "ranking"
    _write_json(
        ranking / "ranked-candidates.json",
        {
            "schema": "fixture",
            "rows": [
                {
                    "candidate_id": "loss-only",
                    "operator_family": "ipi_eml",
                    "target_family": "periodic",
                    "evidence_class": "loss_only",
                    "selected": True,
                },
                {
                    "candidate_id": "negative-control",
                    "operator_family": "raw_eml",
                    "target_family": "negative_control",
                    "evidence_class": "original_snap",
                },
            ],
        },
    )

    paths = write_v117_recovery_sandbox(tmp_path / "sandbox", ranking_dir=ranking)
    manifest = json.loads(paths.manifest_json.read_text(encoding="utf-8"))
    results = json.loads(paths.sandbox_results_json.read_text(encoding="utf-8"))

    assert manifest["exact_signal_found"] is False
    assert manifest["broader_campaign_gate"] == "block_broader_campaigns"
    assert results["natural_exact_recovery_count"] == 0


def test_write_v117_recovery_sandbox_opens_gate_for_natural_exact_signal(tmp_path):
    ranking = tmp_path / "ranking"
    _write_json(
        ranking / "ranked-candidates.json",
        {
            "schema": "fixture",
            "rows": [
                {
                    "candidate_id": "exact-natural",
                    "operator_family": "ipi_eml",
                    "target_family": "periodic",
                    "evidence_class": "exact_recovery",
                    "selected": True,
                },
                {
                    "candidate_id": "raw-loss",
                    "operator_family": "raw_eml",
                    "target_family": "periodic",
                    "evidence_class": "loss_only",
                },
            ],
        },
    )

    paths = write_v117_recovery_sandbox(tmp_path / "sandbox", ranking_dir=ranking)
    manifest = json.loads(paths.manifest_json.read_text(encoding="utf-8"))
    results = json.loads(paths.sandbox_results_json.read_text(encoding="utf-8"))

    assert manifest["exact_signal_found"] is True
    assert manifest["broader_campaign_gate"] == "allow_next_campaign_planning"
    assert results["natural_exact_recovery_count"] == 1


def test_cli_registers_geml_v117_sandbox():
    args = build_parser().parse_args(["geml-v117-sandbox", "--output-dir", "out", "--ranking-dir", "ranking"])
    assert args.func is geml_v117_sandbox_command
    assert args.ranking_dir == "ranking"


def test_write_v117_evidence_package_preserves_v116_and_blocks_without_exact_signal(tmp_path):
    inputs = _write_v117_package_inputs(tmp_path, exact_signal=False)

    paths = write_v117_evidence_package(
        tmp_path / "package",
        snap_diagnostics_dir=inputs["snap"],
        neighborhoods_dir=inputs["neighborhoods"],
        ranking_dir=inputs["ranking"],
        sandbox_dir=inputs["sandbox"],
        v116_package_dir=inputs["v116"],
    )
    manifest = json.loads(paths.manifest_json.read_text(encoding="utf-8"))
    decision = json.loads(paths.final_decision_json.read_text(encoding="utf-8"))
    audit = json.loads(paths.claim_audit_json.read_text(encoding="utf-8"))
    locks = json.loads(paths.source_locks_json.read_text(encoding="utf-8"))
    readme = paths.package_readme_md.read_text(encoding="utf-8")

    assert manifest["schema"] == "eml.v117_evidence_package.v1"
    assert manifest["decision"] == "still_inconclusive"
    assert decision["broader_campaign_gate"] == "block_broader_campaigns"
    assert decision["next_campaign_allowed"] is False
    assert audit["status"] == "passed"
    v116_lock = next(row for row in locks["inputs"] if row["source_id"] == "v116_package_manifest")
    assert v116_lock["status"] == "locked"
    assert v116_lock["required"] is True
    assert "v1.16 package remains intact" in readme
    assert "additive" in readme.lower()


def test_write_v117_evidence_package_opens_gate_only_for_exact_signal(tmp_path):
    inputs = _write_v117_package_inputs(tmp_path, exact_signal=True)

    paths = write_v117_evidence_package(
        tmp_path / "package",
        snap_diagnostics_dir=inputs["snap"],
        neighborhoods_dir=inputs["neighborhoods"],
        ranking_dir=inputs["ranking"],
        sandbox_dir=inputs["sandbox"],
        v116_package_dir=inputs["v116"],
    )
    manifest = json.loads(paths.manifest_json.read_text(encoding="utf-8"))
    decision = json.loads(paths.final_decision_json.read_text(encoding="utf-8"))
    audit = json.loads(paths.claim_audit_json.read_text(encoding="utf-8"))

    assert manifest["decision"] == "exact_signal_found"
    assert manifest["broader_campaign_gate"] == "allow_next_campaign_planning"
    assert decision["next_campaign_allowed"] is True
    assert audit["status"] == "passed"


def test_cli_registers_geml_v117_package():
    args = build_parser().parse_args(
        [
            "geml-v117-package",
            "--output-dir",
            "out",
            "--snap-diagnostics-dir",
            "snap",
            "--neighborhoods-dir",
            "neighborhoods",
            "--ranking-dir",
            "ranking",
            "--sandbox-dir",
            "sandbox",
            "--v116-package-dir",
            "v116",
        ]
    )
    assert args.func is geml_v117_package_command
    assert args.v116_package_dir == "v116"
