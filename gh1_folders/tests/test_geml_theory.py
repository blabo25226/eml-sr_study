import json

from eml_symbolic_regression.branch import principal_log_branch_diagnostics
from eml_symbolic_regression.geml_theory import build_ipi_restricted_theory, write_ipi_restricted_theory


def test_principal_log_branch_diagnostics_detects_cut_risk():
    diagnostics = principal_log_branch_diagnostics([-1.0 + 0.0j, -1.0 + 1e-8j, -1.0 - 1e-8j, 1.0 + 0.0j])
    payload = diagnostics.as_dict()

    assert payload["branch_convention"] == "principal_complex_log_cut_negative_real_axis"
    assert payload["branch_cut_hit_count"] == 1
    assert payload["branch_cut_proximity_count"] == 3
    assert payload["branch_cut_crossing_count"] >= 1
    assert payload["branch_related"] is True


def test_principal_log_branch_crossing_requires_negative_axis_crossing():
    positive_axis = principal_log_branch_diagnostics([-1.0 + 1.0j, 100.0 - 1.0j]).as_dict()
    negative_axis = principal_log_branch_diagnostics([-1.0 + 1.0j, -2.0 - 1.0j]).as_dict()

    assert positive_axis["branch_cut_crossing_count"] == 0
    assert negative_axis["branch_cut_crossing_count"] == 1


def test_ipi_restricted_theory_checks_pass():
    payload = build_ipi_restricted_theory()

    assert payload["status"] == "passed"
    assert {check["id"] for check in payload["checks"]} == {"THRY-01", "THRY-02", "THRY-03", "THRY-04"}
    assert all(check["passed"] for check in payload["checks"])
    assert any("does not prove full" in item for item in payload["non_claims"])


def test_ipi_restricted_theory_rejects_vacuous_or_invalid_samples():
    for kwargs in ({"y_samples": ()}, {"u_samples": ()}, {"y_samples": ("0", "1")}):
        try:
            build_ipi_restricted_theory(**kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid samples should fail: {kwargs}")


def test_write_ipi_restricted_theory_artifacts(tmp_path):
    paths = write_ipi_restricted_theory(tmp_path)
    payload = json.loads(paths.json_path.read_text(encoding="utf-8"))
    markdown = paths.markdown_path.read_text(encoding="utf-8")

    assert payload["status"] == "passed"
    assert "i*pi EML Restricted Theory" in markdown
    assert "Non-Claims" in markdown
