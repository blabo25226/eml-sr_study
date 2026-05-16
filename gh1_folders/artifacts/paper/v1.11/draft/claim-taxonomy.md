# Claim Taxonomy

| evidence_class | paper_label | denominator_rule | eligible_for_pure_blind_rate | eligible_for_verifier_recovery_rate | safe_public_claim |
| --- | --- | --- | --- | --- | --- |
| pure_blind | Pure blind | pure-blind suite rows only; scaffolds, warm starts, repairs, and perturbed starts excluded | true | true | Only verifier-recovered rows in this class may support pure blind recovery rates. |
| scaffolded | Scaffolded blind | scaffolded rows are denominated separately from pure blind rows | false | true | Useful optimizer evidence, but not pure blind discovery. |
| warm_start | Compiler warm start | warm_start rows are denominated separately from pure blind rows | false | true | Basin or compiler-assisted evidence, not random-initialized discovery. |
| same_ast | Same-AST return | same_ast rows are denominated separately from pure blind rows | false | true | Strong representational and basin evidence, not discovery from scratch. |
| perturbed_basin | Perturbed basin | perturbed_basin rows are denominated separately from pure blind rows | false | true | Measures local basin stability, not blind search. |
| repair_refit | Repair/refit | repair_refit rows are denominated separately from pure blind rows | false | true | Post-snap improvement evidence, not the original optimizer discovery event. |
| compile_only | Compile-only | compile_only rows are denominated separately from pure blind rows | false | true | Representation support or unsupported diagnostics, not training recovery. |
| unsupported | Unsupported | visible negative rows inside their original regime denominator | false | false | Must remain visible in denominators where eligible and never count as recovered. |
| failed | Failed | visible negative rows inside their original regime denominator | false | false | Must remain visible and never count as recovered. |
