import mpmath as mp
import numpy as np
import sympy as sp
from types import SimpleNamespace

import eml_symbolic_regression.optimize as optimize
from eml_symbolic_regression.expression import Const, Eml
from eml_symbolic_regression.optimize import ExactCandidate
from eml_symbolic_regression.verify import DataSplit, VerificationReport, selection_candidate_splits, split_role, verify_candidate


class _StubCandidate:
    candidate_kind = "exact_eml"

    def __init__(
        self,
        *,
        numpy_value: complex,
        mpmath_value: complex | None = None,
        fail_mpmath: bool = False,
        sympy_expr=None,
    ) -> None:
        self.numpy_value = complex(numpy_value)
        self.mpmath_value = complex(mpmath_value) if mpmath_value is not None else complex(numpy_value)
        self.fail_mpmath = fail_mpmath
        self.mpmath_calls = 0
        self.sympy_expr = sympy_expr

    def evaluate_numpy(self, context):
        shape = np.asarray(context["x"], dtype=np.complex128).shape
        return np.full(shape, self.numpy_value, dtype=np.complex128)

    def evaluate_mpmath(self, context):
        self.mpmath_calls += 1
        if self.fail_mpmath:
            raise AssertionError("mpmath evaluation should have been skipped")
        return mp.mpc(self.mpmath_value)

    def to_sympy(self):
        if self.sympy_expr is not None:
            return self.sympy_expr
        raise NotImplementedError


class _LinearCandidate:
    candidate_kind = "exact_eml"

    def evaluate_numpy(self, context):
        return np.asarray(context["x"], dtype=np.complex128) + 1.0

    def evaluate_mpmath(self, context):
        return mp.mpc(context["x"]) + 1

    def to_sympy(self):
        x = sp.Symbol("x")
        return x + 1


class _TwoVariableSumCandidate:
    candidate_kind = "exact_eml"

    def evaluate_numpy(self, context):
        return np.asarray(context["x"], dtype=np.complex128) + np.asarray(context["y"], dtype=np.complex128)

    def evaluate_mpmath(self, context):
        return mp.mpc(context["x"]) + mp.mpc(context["y"])

    def to_sympy(self):
        x = sp.Symbol("x")
        y = sp.Symbol("y")
        return x + y


def _split() -> DataSplit:
    return DataSplit(
        name="heldout",
        inputs={"x": np.asarray([0.0, 1.0, 2.0], dtype=np.complex128)},
        target=np.asarray([1.0, 1.0, 1.0], dtype=np.complex128),
    )


def test_verify_candidate_performs_high_precision_for_exact_match():
    candidate = _StubCandidate(numpy_value=1.0, mpmath_value=1.0)

    report = verify_candidate(candidate, [_split()], tolerance=1e-8)

    assert report.status == "recovered"
    assert report.reason == "verified"
    assert report.high_precision_status == "performed"
    assert report.high_precision_max_error == 0.0
    assert candidate.mpmath_calls > 0


def test_verify_candidate_skips_high_precision_for_decisive_numeric_failure():
    candidate = _StubCandidate(numpy_value=2.0, fail_mpmath=True)

    report = verify_candidate(candidate, [_split()], tolerance=1e-8)

    assert report.status == "failed"
    assert report.reason == "heldout_failed"
    assert report.high_precision_status == "skipped_numeric_failure"
    assert report.high_precision_max_error == 1.0
    assert candidate.mpmath_calls == 0


def test_verify_candidate_keeps_high_precision_for_near_miss_numeric_failure():
    candidate = _StubCandidate(numpy_value=1.005, mpmath_value=1.0)

    report = verify_candidate(candidate, [_split()], tolerance=1e-8)

    assert report.status == "failed"
    assert report.reason == "heldout_failed"
    assert report.high_precision_status == "performed"
    assert report.high_precision_max_error == 0.0
    assert candidate.mpmath_calls > 0


def test_verify_candidate_reports_symbolic_probes_certificate_and_roles():
    x = sp.Symbol("x")
    split = DataSplit(
        name="heldout",
        inputs={"x": np.asarray([0.0, 0.5, 1.0], dtype=np.float64)},
        target=np.asarray([1.0, 1.5, 2.0], dtype=np.complex128),
        target_mpmath=lambda context: mp.mpc(context["x"]) + 1,
        target_sympy=x + 1,
    )

    report = verify_candidate(_LinearCandidate(), [split], tolerance=1e-8, target_sympy=x + 1)
    payload = report.as_dict()

    assert report.status == "recovered"
    assert report.symbolic_status == "passed"
    assert report.dense_random_status == "passed"
    assert report.adversarial_status == "passed"
    assert report.certificate_status == "symbolic_equivalence"
    assert report.evidence_level == "symbolic"
    assert payload["split_results"][0]["role"] == "diagnostic"
    assert payload["metric_roles"]["diagnostic"] == 1


def test_verify_candidate_matches_multivariate_high_precision_targets_by_full_row():
    split = DataSplit(
        name="heldout",
        inputs={
            "x": np.asarray([0.0, 0.0, 1.0], dtype=np.float64),
            "y": np.asarray([0.0, 1.0, 1.0], dtype=np.float64),
        },
        target=np.asarray([0.0, 1.0, 2.0], dtype=np.complex128),
    )

    report = verify_candidate(
        _TwoVariableSumCandidate(),
        [split],
        tolerance=1e-8,
        dense_random_points=0,
        adversarial_points=0,
    )

    assert report.status == "recovered"
    assert report.reason == "verified"
    assert report.high_precision_status == "performed"
    assert report.high_precision_max_error == 0.0


def test_verify_candidate_accepts_zero_symbolic_target():
    split = DataSplit(
        name="verifier",
        inputs={"x": np.asarray([0.0, 1.0], dtype=np.float64)},
        target=np.asarray([0.0, 0.0], dtype=np.complex128),
    )

    report = verify_candidate(_StubCandidate(numpy_value=0.0, sympy_expr=sp.Integer(0)), [split], target_sympy=sp.Integer(0))

    assert report.status == "recovered"
    assert report.symbolic_status == "passed"


def test_verify_candidate_labels_unsupported_layers_when_no_target_metadata():
    report = verify_candidate(_StubCandidate(numpy_value=1.0), [_split()], tolerance=1e-8)

    assert report.symbolic_status == "unsupported_no_target"
    assert report.dense_random_status == "unsupported_no_target_evaluator"
    assert report.adversarial_status == "unsupported_no_target_evaluator"
    assert report.certificate_status == "unsupported_interval_certificate"


def test_verify_candidate_exposes_branch_diagnostics_for_exact_ast():
    candidate = Eml(Const(0.0), Const(-1.0))
    split = DataSplit(
        name="heldout",
        inputs={"x": np.asarray([0.0, 1.0], dtype=np.float64)},
        target=np.asarray([0.0, 0.0], dtype=np.complex128),
    )

    report = verify_candidate(candidate, [split], tolerance=1e-8, dense_random_points=0, adversarial_points=0)
    branch = report.as_dict()["branch_diagnostics"]

    assert report.status == "failed"
    assert branch["status"] == "performed"
    assert branch["branch_convention"] == "principal_complex_log_cut_negative_real_axis"
    assert branch["non_finite_count"] == branch["log_non_finite_input_count"]
    assert branch["near_zero_count"] == branch["log_small_magnitude_count"]
    assert branch["branch_cut_hit_count"] == branch["log_branch_cut_count"]
    assert branch["min_branch_cut_distance"] == branch["log_branch_cut_min_distance"]
    assert branch["log_branch_cut_count"] > 0
    assert branch["branch_related"] is True
    assert branch["candidate_failure_class"] == "branch_related"
    assert branch["branch_safety_guard"]["faithful_verification_unchanged"] is True


def test_selection_candidate_splits_excludes_final_confirmation():
    selection = DataSplit("selection", {"x": np.asarray([1.0])}, np.asarray([1.0]))
    final = DataSplit("final_confirmation", {"x": np.asarray([1.0])}, np.asarray([1.0]))

    assert split_role(final) == "final_confirmation"
    assert selection_candidate_splits([selection, final]) == [selection]


def test_exact_candidate_ranking_ignores_final_confirmation_split(monkeypatch):
    calls = []

    def fake_verify(expression, splits, tolerance):
        names = [split.name for split in splits]
        calls.append((expression, names))
        using_final = any(split_role(split) == "final_confirmation" for split in splits)
        if using_final:
            hp_error = 99.0 if expression == "a" else 0.0
        else:
            hp_error = 0.0 if expression == "a" else 10.0
        return VerificationReport(
            status="recovered",
            candidate_kind="exact_eml",
            reason="verified",
            split_results=[],
            high_precision_max_error=hp_error,
            tolerance=tolerance,
        )

    monkeypatch.setattr(optimize, "verify_candidate", fake_verify)

    def candidate(candidate_id):
        return ExactCandidate(
            candidate_id=candidate_id,
            attempt_index=0,
            random_restart=None,
            seed=0,
            attempt_kind="test",
            source="test",
            checkpoint_index=None,
            hardening_step=None,
            global_step=0,
            temperature=0.0,
            best_fit_loss=0.0,
            pre_snap_loss=0.0,
            post_snap_loss=0.0,
            snap=SimpleNamespace(expression=candidate_id, active_node_count=1, decisions=()),
        )

    selection = DataSplit("selection", {"x": np.asarray([1.0])}, np.asarray([1.0]))
    final = DataSplit("final_confirmation", {"x": np.asarray([1.0])}, np.asarray([1.0]))
    ranked, _ = optimize._select_exact_candidate([candidate("b"), candidate("a")], verification_splits=[selection, final], tolerance=1e-8)

    assert ranked[0].candidate_id == "a"
    assert calls[0] == ("b", ["selection"])
    assert calls[1] == ("b", ["selection", "final_confirmation"])
