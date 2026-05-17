import pytest

from eml_symbolic_regression.proof import (
    CLAIM_CLASSES,
    EVIDENCE_CLASSES,
    ProofContractError,
    claim_matrix,
    list_claims,
    paper_claim,
    threshold_policies,
    threshold_policy,
    validate_claim_reference,
)


def test_claim_matrix_exposes_stable_paper_claim_ids():
    claims = claim_matrix()

    assert tuple(claims) == (
        "paper-complete-depth-bounded-search",
        "paper-shallow-blind-recovery",
        "paper-shallow-scaffolded-recovery",
        "paper-perturbed-true-tree-basin",
        "paper-blind-depth-degradation",
    )
    assert list_claims() == list(claims.values())
    assert claims["paper-complete-depth-bounded-search"].threshold_policy_id == "contract_context"
    assert claims["paper-shallow-blind-recovery"].threshold_policy_id == "measured_pure_blind_recovery"
    assert claims["paper-shallow-scaffolded-recovery"].threshold_policy_id == "scaffolded_bounded_100_percent"
    assert claims["paper-perturbed-true-tree-basin"].threshold_policy_id == "bounded_100_percent"
    assert claims["paper-blind-depth-degradation"].threshold_policy_id == "measured_depth_curve"


def test_claims_keep_catalog_compile_and_training_classes_distinct():
    assert CLAIM_CLASSES["catalog_verification"] != CLAIM_CLASSES["compile_only_verification"]
    assert EVIDENCE_CLASSES["catalog_verified"] != EVIDENCE_CLASSES["compile_only_verified"]
    assert EVIDENCE_CLASSES["blind_training_recovered"] != EVIDENCE_CLASSES["soft_fit_only"]
    assert EVIDENCE_CLASSES["blind_training_recovered"] != EVIDENCE_CLASSES["scaffolded_blind_training_recovered"]

    shallow_claim = paper_claim("paper-shallow-blind-recovery")
    assert shallow_claim.claim_class == CLAIM_CLASSES["measured_training_boundary"]
    assert shallow_claim.suite_ids == ("v1.5-shallow-pure-blind",)
    assert shallow_claim.case_ids == (
        "shallow-exp-pure-blind",
        "shallow-log-pure-blind",
        "shallow-radioactive-decay-pure-blind",
        "shallow-beer-lambert-pure-blind",
        "shallow-scaled-exp-growth-pure-blind",
        "shallow-scaled-exp-fast-decay-pure-blind",
    )
    assert "sources/paper.pdf" in shallow_claim.source_refs
    assert ".planning/REQUIREMENTS.md" in shallow_claim.source_refs
    assert ".planning/ROADMAP.md" in shallow_claim.source_refs

    scaffolded_claim = paper_claim("paper-shallow-scaffolded-recovery")
    assert scaffolded_claim.claim_class == CLAIM_CLASSES["scaffolded_training_proof"]
    assert scaffolded_claim.suite_ids == ("v1.5-shallow-proof",)
    assert scaffolded_claim.case_ids == (
        "shallow-exp-blind",
        "shallow-log-blind",
        "shallow-radioactive-decay-blind",
        "shallow-beer-lambert-blind",
        "shallow-scaled-exp-growth-blind",
        "shallow-scaled-exp-fast-decay-blind",
    )
    assert any("not pure random" in note for note in scaffolded_claim.notes)

    perturbed_claim = paper_claim("paper-perturbed-true-tree-basin")
    assert perturbed_claim.case_ids == (
        "basin-depth1-perturbed",
        "basin-depth2-perturbed",
        "basin-depth3-perturbed",
        "basin-beer-lambert-bound",
    )
    assert any("declared nonzero perturbation" in note for note in perturbed_claim.notes)
    assert any("return_kind" in note for note in perturbed_claim.notes)
    assert not any("not by itself bounded training proof" in note for note in perturbed_claim.notes)


def test_bounded_100_percent_policy_allows_only_verifier_owned_training_evidence():
    policy = threshold_policy("bounded_100_percent")

    assert policy.required_rate == 1.0
    assert policy.fail_on_unsupported is True
    assert policy.fail_on_execution_error is True
    assert set(policy.allowed_evidence_classes) == {
        EVIDENCE_CLASSES["blind_training_recovered"],
        EVIDENCE_CLASSES["compiler_warm_start_recovered"],
        EVIDENCE_CLASSES["perturbed_true_tree_recovered"],
        EVIDENCE_CLASSES["repaired_candidate"],
        EVIDENCE_CLASSES["verified_equivalent"],
    }
    assert EVIDENCE_CLASSES["catalog_verified"] not in policy.allowed_evidence_classes
    assert EVIDENCE_CLASSES["compile_only_verified"] not in policy.allowed_evidence_classes
    assert EVIDENCE_CLASSES["scaffolded_blind_training_recovered"] not in policy.allowed_evidence_classes
    assert EVIDENCE_CLASSES["same_ast"] not in policy.allowed_evidence_classes


def test_depth_curve_policy_reports_measured_rates_without_requiring_100_percent():
    policies = threshold_policies()
    pure_blind = policies["measured_pure_blind_recovery"]
    scaffolded = policies["scaffolded_bounded_100_percent"]
    measured = policies["measured_depth_curve"]
    context = policies["contract_context"]

    assert pure_blind.required_rate is None
    assert pure_blind.policy_type == "measured_rate"
    assert pure_blind.allowed_evidence_classes == (EVIDENCE_CLASSES["blind_training_recovered"],)
    assert scaffolded.required_rate == 1.0
    assert scaffolded.policy_type == "bounded_rate"
    assert scaffolded.allowed_evidence_classes == (EVIDENCE_CLASSES["scaffolded_blind_training_recovered"],)
    assert measured.required_rate is None
    assert measured.policy_type == "measured_rate"
    assert measured.fail_on_unsupported is False
    assert context.required_rate is None
    assert context.policy_type == "context_only"
    depth_claim = paper_claim("paper-blind-depth-degradation")
    assert depth_claim.case_ids == (
        "depth-2-blind",
        "depth-3-blind",
        "depth-4-blind",
        "depth-5-blind",
        "depth-6-blind",
        "depth-2-perturbed",
        "depth-3-perturbed",
        "depth-4-perturbed",
        "depth-5-perturbed",
        "depth-6-perturbed",
    )
    assert any("Perturbed rows provide comparative basin evidence" in note for note in depth_claim.notes)


def test_unknown_claim_and_policy_ids_fail_closed_with_stable_reason():
    with pytest.raises(ProofContractError) as claim_exc:
        paper_claim("missing-claim")
    assert claim_exc.value.reason == "unknown_claim"
    assert claim_exc.value.as_dict()["path"] == "claim_id"

    with pytest.raises(ProofContractError) as policy_exc:
        threshold_policy("missing-policy")
    assert policy_exc.value.reason == "unknown_threshold_policy"
    assert policy_exc.value.as_dict()["path"] == "threshold_policy_id"

    with pytest.raises(ProofContractError) as ref_exc:
        validate_claim_reference("paper-shallow-blind-recovery", "bounded_100_percent", path="cases[0].claim")
    assert ref_exc.value.reason == "threshold_mismatch"
    assert ref_exc.value.path == "cases[0].claim.threshold_policy_id"
