import json

from eml_symbolic_regression.paper_decision import write_paper_decision_package


def _aggregate(*runs):
    return {
        "schema": "eml.benchmark_aggregate.v1",
        "suite": {"id": "synthetic-family"},
        "runs": list(runs),
    }


def _run(operator: str, *, recovered: bool, schedule=None):
    return {
        "claim_status": "recovered" if recovered else "failed",
        "classification": "blind_training_recovered" if recovered else "snapped_but_failed",
        "optimizer": {
            "operator_family": {"label": operator},
            "operator_schedule": schedule or [],
        },
        "metrics": {
            "operator_family": operator,
            "operator_schedule": " -> ".join(item["label"] for item in (schedule or [])),
        },
    }


def test_paper_decision_waits_when_centered_evidence_is_missing(tmp_path):
    aggregate_path = tmp_path / "aggregate.json"
    aggregate_path.write_text(json.dumps(_aggregate(_run("raw_eml", recovered=True))), encoding="utf-8")

    paths = write_paper_decision_package((aggregate_path,), output_dir=tmp_path / "paper")
    payload = json.loads(paths.decision_json.read_text())
    memo = paths.decision_markdown.read_text(encoding="utf-8")

    assert payload["decision"] == "wait_for_centered_family_evidence"
    assert payload["evidence_summary"]["has_centered_evidence"] is False
    assert str(aggregate_path) in paths.safe_claims.read_text(encoding="utf-8")
    assert str(aggregate_path) in paths.unsafe_claims.read_text(encoding="utf-8")
    assert "Safe Claims" in paths.safe_claims.read_text(encoding="utf-8")
    assert "Unsafe Claims" in paths.unsafe_claims.read_text(encoding="utf-8")
    assert "exact recovery versus depth" in paths.figure_inventory.read_text(encoding="utf-8")
    assert "Status:** incomplete" in paths.completeness_boundary.read_text(encoding="utf-8")
    assert "centered-family empirical paper" in memo
    assert "current family campaigns" in memo
    assert "v1.7 family campaigns" not in memo


def test_paper_decision_can_select_publish_when_centered_beats_raw(tmp_path):
    aggregate_path = tmp_path / "aggregate.json"
    aggregate_path.write_text(
        json.dumps(
            _aggregate(
                _run("raw_eml", recovered=False),
                _run("CEML_2", recovered=True),
                _run("ZEML_8", recovered=True, schedule=[{"label": "ZEML_8"}, {"label": "ZEML_4"}]),
            )
        ),
        encoding="utf-8",
    )

    paths = write_paper_decision_package((aggregate_path,), output_dir=tmp_path / "paper")
    payload = json.loads(paths.decision_json.read_text())

    assert payload["decision"] == "publish_robustness_geometry_paper_now"
    assert payload["evidence_summary"]["has_centered_evidence"] is True
    assert payload["evidence_summary"]["operator_groups"]["ZEML_8"]["schedules"] == ["ZEML_8 -> ZEML_4"]


def test_paper_decision_selects_raw_note_when_centered_does_not_beat_raw(tmp_path):
    aggregate_path = tmp_path / "aggregate.json"
    aggregate_path.write_text(
        json.dumps(
            _aggregate(
                _run("raw_eml", recovered=True),
                _run("CEML_2", recovered=False),
                _run("ZEML_8", recovered=False),
            )
        ),
        encoding="utf-8",
    )

    paths = write_paper_decision_package((aggregate_path,), output_dir=tmp_path / "paper")
    payload = json.loads(paths.decision_json.read_text())
    memo = paths.decision_markdown.read_text(encoding="utf-8")

    assert payload["decision"] == "publish_raw_eml_searchability_note"
    assert "negative or diagnostic evidence" in memo
