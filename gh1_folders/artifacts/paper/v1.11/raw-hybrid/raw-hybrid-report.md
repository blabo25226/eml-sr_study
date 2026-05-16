# v1.11 Paper-Strength Evidence Package

This package synthesizes locked evidence artifacts without running training, campaigns, or proof suites.
Each evidence path is reported in its own regime bucket so paper claims do not merge incompatible starts.

## Pure Blind

Random-initialized blind training evidence, kept separate from repairs and scaffolds.

| Metric | Value |
|--------|-------|
| runs | 25 |
| verifier_recovered | 4 |
| same_ast_return | 0 |
| repaired_candidate | 0 |
| unsupported | 0 |
| failed | 21 |

| Source | Run | Formula | Mode | Evidence Class | Status | Artifact |
|--------|-----|---------|------|----------------|--------|----------|
| proof-depth-curve-aggregate | proof-depth-curve-depth-2-blind-0b1b5fc59dd8 | depth_curve_depth2 | blind | blind_training_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-2-blind-0b1b5fc59dd8.json |
| proof-depth-curve-aggregate | proof-depth-curve-depth-2-blind-2dace23147bf | depth_curve_depth2 | blind | blind_training_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-2-blind-2dace23147bf.json |
| proof-depth-curve-aggregate | proof-depth-curve-depth-4-blind-0f9bab635276 | depth_curve_depth4 | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-4-blind-0f9bab635276.json |
| proof-depth-curve-aggregate | proof-depth-curve-depth-4-blind-344a2756d697 | depth_curve_depth4 | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-4-blind-344a2756d697.json |
| proof-depth-curve-aggregate | proof-depth-curve-depth-5-blind-81eda26add96 | depth_curve_depth5 | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-5-blind-81eda26add96.json |
| proof-depth-curve-aggregate | proof-depth-curve-depth-5-blind-f855e27799b5 | depth_curve_depth5 | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-5-blind-f855e27799b5.json |
| proof-depth-curve-aggregate | proof-depth-curve-depth-6-blind-804a64fb5351 | depth_curve_depth6 | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-6-blind-804a64fb5351.json |
| proof-depth-curve-aggregate | proof-depth-curve-depth-6-blind-d2ecd073c61c | depth_curve_depth6 | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-6-blind-d2ecd073c61c.json |
| proof-shallow-pure-blind-aggregate | v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-4908b626f452 | beer_lambert | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-4908b626f452.json |
| proof-shallow-pure-blind-aggregate | v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-8599744dc0b5 | beer_lambert | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-8599744dc0b5.json |
| proof-shallow-pure-blind-aggregate | v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-d4b6b4704428 | beer_lambert | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-d4b6b4704428.json |
| proof-shallow-pure-blind-aggregate | v1-5-shallow-pure-blind-shallow-exp-pure-blind-1325a323dee1 | exp | blind | blind_training_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-exp-pure-blind-1325a323dee1.json |
| ... | 13 additional runs omitted from this view |  |  |  |  |  |

## Scaffolded

Blind training with declared scaffold initializers, not pure blind discovery.

| Metric | Value |
|--------|-------|
| runs | 20 |
| verifier_recovered | 20 |
| same_ast_return | 0 |
| repaired_candidate | 0 |
| unsupported | 0 |
| failed | 0 |

| Source | Run | Formula | Mode | Evidence Class | Status | Artifact |
|--------|-----|---------|------|----------------|--------|----------|
| proof-depth-curve-aggregate | proof-depth-curve-depth-3-blind-a0df4b0ab1b4 | depth_curve_depth3 | blind | scaffolded_blind_training_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-3-blind-a0df4b0ab1b4.json |
| proof-depth-curve-aggregate | proof-depth-curve-depth-3-blind-d6c26a917882 | depth_curve_depth3 | blind | scaffolded_blind_training_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-3-blind-d6c26a917882.json |
| proof-shallow-scaffolded-aggregate | v1-5-shallow-proof-shallow-beer-lambert-blind-19bae8ae4d64 | beer_lambert | blind | scaffolded_blind_training_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-beer-lambert-blind-19bae8ae4d64.json |
| proof-shallow-scaffolded-aggregate | v1-5-shallow-proof-shallow-beer-lambert-blind-5cb3e5e925cf | beer_lambert | blind | scaffolded_blind_training_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-beer-lambert-blind-5cb3e5e925cf.json |
| proof-shallow-scaffolded-aggregate | v1-5-shallow-proof-shallow-beer-lambert-blind-98e77d05a5f1 | beer_lambert | blind | scaffolded_blind_training_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-beer-lambert-blind-98e77d05a5f1.json |
| proof-shallow-scaffolded-aggregate | v1-5-shallow-proof-shallow-exp-blind-6609115edbe5 | exp | blind | scaffolded_blind_training_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-exp-blind-6609115edbe5.json |
| proof-shallow-scaffolded-aggregate | v1-5-shallow-proof-shallow-exp-blind-e5b022c6906d | exp | blind | scaffolded_blind_training_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-exp-blind-e5b022c6906d.json |
| proof-shallow-scaffolded-aggregate | v1-5-shallow-proof-shallow-exp-blind-f840e23851e0 | exp | blind | scaffolded_blind_training_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-exp-blind-f840e23851e0.json |
| proof-shallow-scaffolded-aggregate | v1-5-shallow-proof-shallow-log-blind-28dcde6891db | log | blind | scaffolded_blind_training_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-log-blind-28dcde6891db.json |
| proof-shallow-scaffolded-aggregate | v1-5-shallow-proof-shallow-log-blind-bace3dcddb88 | log | blind | scaffolded_blind_training_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-log-blind-bace3dcddb88.json |
| proof-shallow-scaffolded-aggregate | v1-5-shallow-proof-shallow-log-blind-e2bc0d0a6099 | log | blind | scaffolded_blind_training_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-log-blind-e2bc0d0a6099.json |
| proof-shallow-scaffolded-aggregate | v1-5-shallow-proof-shallow-radioactive-decay-blind-2aea4e510ed9 | radioactive_decay | blind | scaffolded_blind_training_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-shallow/runs/v1.5-shallow-proof/v1-5-shallow-proof-shallow-radioactive-decay-blind-2aea4e510ed9.json |
| ... | 8 additional runs omitted from this view |  |  |  |  |  |

## Compile Only

Exact compiler diagnostics that do not train from random initialization.

| Metric | Value |
|--------|-------|
| runs | 2 |
| verifier_recovered | 0 |
| same_ast_return | 0 |
| repaired_candidate | 0 |
| unsupported | 2 |
| failed | 0 |

| Source | Run | Formula | Mode | Evidence Class | Status | Artifact |
|--------|-----|---------|------|----------------|--------|----------|
| v1.10-logistic-aggregate | v1-10-logistic-evidence-logistic-compile-c2af27a35e81 | logistic | compile | unsupported | unsupported | artifacts/campaigns/v1.10-logistic-evidence/v1-10-logistic-evidence-logistic-compile-c2af27a35e81.json |
| v1.10-planck-aggregate | v1-10-planck-diagnostics-planck-compile-795067919a97 | planck | compile | unsupported | unsupported | artifacts/campaigns/v1.10-planck-diagnostics/v1-10-planck-diagnostics-planck-compile-795067919a97.json |

## Warm Start

Compiler-seeded warm-start training attempts.

| Metric | Value |
|--------|-------|
| runs | 7 |
| verifier_recovered | 4 |
| same_ast_return | 4 |
| repaired_candidate | 0 |
| unsupported | 1 |
| failed | 2 |

| Source | Run | Formula | Mode | Evidence Class | Status | Artifact |
|--------|-----|---------|------|----------------|--------|----------|
| v1.6-beer-lambert-run | v1-3-standard-beer-perturbation-sweep-c671cedf25f1 | beer_lambert | warm_start | same_ast | same_ast_return | artifacts/campaigns/v1.6-standard/runs/v1.3-standard/v1-3-standard-beer-perturbation-sweep-c671cedf25f1.json |
| v1.6-historical-michaelis-diagnostic-run | v1-3-standard-michaelis-warm-diagnostic-9917f8383370 | michaelis_menten | warm_start | unsupported | unsupported | artifacts/campaigns/v1.6-standard/runs/v1.3-standard/v1-3-standard-michaelis-warm-diagnostic-9917f8383370.json |
| v1.6-shockley-run | v1-3-standard-shockley-warm-316f98a5b1fb | shockley | warm_start | same_ast | same_ast_return | artifacts/campaigns/v1.6-standard/runs/v1.3-standard/v1-3-standard-shockley-warm-316f98a5b1fb.json |
| v1.9-arrhenius-aggregate | v1-9-arrhenius-evidence-arrhenius-warm-75f6e9c1764d | arrhenius | warm_start | same_ast | same_ast_return | artifacts/campaigns/v1.9-arrhenius-evidence/v1.9-arrhenius-evidence/v1-9-arrhenius-evidence-arrhenius-warm-75f6e9c1764d.json |
| v1.9-michaelis-aggregate | v1-9-michaelis-evidence-michaelis-warm-a67d8ccfb108 | michaelis_menten | warm_start | same_ast | same_ast_return | artifacts/campaigns/v1.9-michaelis-evidence/v1.9-michaelis-evidence/v1-9-michaelis-evidence-michaelis-warm-a67d8ccfb108.json |
| v1.9-repair-aggregate | v1-9-repair-evidence-repair-beer-warm-default-bf1ad372adab | beer_lambert | warm_start | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.9-repair-evidence/v1.9-repair-evidence/v1-9-repair-evidence-repair-beer-warm-default-bf1ad372adab.json |
| v1.9-repair-aggregate | v1-9-repair-evidence-repair-beer-warm-expanded-5a37dc178e67 | beer_lambert | warm_start | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.9-repair-evidence/v1.9-repair-evidence/v1-9-repair-evidence-repair-beer-warm-expanded-5a37dc178e67.json |

## Same-AST Return

Runs that returned the exact same AST or equivalent same-AST evidence.

| Metric | Value |
|--------|-------|
| runs | 24 |
| verifier_recovered | 24 |
| same_ast_return | 24 |
| repaired_candidate | 0 |
| unsupported | 0 |
| failed | 0 |

| Source | Run | Formula | Mode | Evidence Class | Status | Artifact |
|--------|-----|---------|------|----------------|--------|----------|
| proof-basin-probes-aggregate | proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-2d877a2bc9fc | beer_lambert | perturbed_tree | perturbed_true_tree_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-basin-probes/runs/proof-perturbed-basin-beer-probes/proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-2d877a2bc9fc.json |
| proof-depth-curve-aggregate | proof-depth-curve-depth-2-perturbed-63c9dbc22949 | depth_curve_depth2 | perturbed_tree | perturbed_true_tree_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-2-perturbed-63c9dbc22949.json |
| proof-depth-curve-aggregate | proof-depth-curve-depth-2-perturbed-e76ace19ca5b | depth_curve_depth2 | perturbed_tree | perturbed_true_tree_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-2-perturbed-e76ace19ca5b.json |
| proof-depth-curve-aggregate | proof-depth-curve-depth-3-perturbed-35d5a61c1b73 | depth_curve_depth3 | perturbed_tree | perturbed_true_tree_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-3-perturbed-35d5a61c1b73.json |
| proof-depth-curve-aggregate | proof-depth-curve-depth-3-perturbed-5a87ef481565 | depth_curve_depth3 | perturbed_tree | perturbed_true_tree_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-3-perturbed-5a87ef481565.json |
| proof-depth-curve-aggregate | proof-depth-curve-depth-4-perturbed-01bf488498af | depth_curve_depth4 | perturbed_tree | perturbed_true_tree_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-4-perturbed-01bf488498af.json |
| proof-depth-curve-aggregate | proof-depth-curve-depth-4-perturbed-1c743390bc74 | depth_curve_depth4 | perturbed_tree | perturbed_true_tree_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-4-perturbed-1c743390bc74.json |
| proof-depth-curve-aggregate | proof-depth-curve-depth-5-perturbed-acbbb1e43aa6 | depth_curve_depth5 | perturbed_tree | perturbed_true_tree_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-5-perturbed-acbbb1e43aa6.json |
| proof-depth-curve-aggregate | proof-depth-curve-depth-5-perturbed-ca69c9157585 | depth_curve_depth5 | perturbed_tree | perturbed_true_tree_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-5-perturbed-ca69c9157585.json |
| proof-depth-curve-aggregate | proof-depth-curve-depth-6-perturbed-598372e89c3d | depth_curve_depth6 | perturbed_tree | perturbed_true_tree_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-6-perturbed-598372e89c3d.json |
| proof-depth-curve-aggregate | proof-depth-curve-depth-6-perturbed-ac9bfe446f0f | depth_curve_depth6 | perturbed_tree | perturbed_true_tree_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-6-perturbed-ac9bfe446f0f.json |
| proof-perturbed-basin-aggregate | proof-perturbed-basin-basin-beer-lambert-bound-0a5e00e13e43 | beer_lambert | perturbed_tree | perturbed_true_tree_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-basin/runs/proof-perturbed-basin/proof-perturbed-basin-basin-beer-lambert-bound-0a5e00e13e43.json |
| ... | 12 additional runs omitted from this view |  |  |  |  |  |

## Repaired

Verifier-gated local repair evidence, separate from the original selected candidate.

| Metric | Value |
|--------|-------|
| runs | 8 |
| verifier_recovered | 4 |
| same_ast_return | 0 |
| repaired_candidate | 4 |
| unsupported | 0 |
| failed | 4 |

| Source | Run | Formula | Mode | Evidence Class | Status | Artifact |
|--------|-----|---------|------|----------------|--------|----------|
| proof-basin-probes-aggregate | proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-752352286603 | beer_lambert | perturbed_tree | repaired_candidate | repaired_candidate | artifacts/proof/v1.6/campaigns/proof-basin-probes/runs/proof-perturbed-basin-beer-probes/proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-752352286603.json |
| proof-basin-probes-aggregate | proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-99306eda3f85 | beer_lambert | perturbed_tree | repaired_candidate | repaired_candidate | artifacts/proof/v1.6/campaigns/proof-basin-probes/runs/proof-perturbed-basin-beer-probes/proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-99306eda3f85.json |
| proof-basin-probes-aggregate | proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-e17e44438210 | beer_lambert | perturbed_tree | repaired_candidate | repaired_candidate | artifacts/proof/v1.6/campaigns/proof-basin-probes/runs/proof-perturbed-basin-beer-probes/proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-e17e44438210.json |
| proof-shallow-pure-blind-aggregate | v1-5-shallow-pure-blind-shallow-exp-pure-blind-38ff2b4c6e37 | exp | blind | repaired_candidate | repaired_candidate | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-exp-pure-blind-38ff2b4c6e37.json |
| v1.9-repair-aggregate | v1-9-repair-evidence-repair-beer-warm-default-bf1ad372adab | beer_lambert | warm_start | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.9-repair-evidence/v1.9-repair-evidence/v1-9-repair-evidence-repair-beer-warm-default-bf1ad372adab.json |
| v1.9-repair-aggregate | v1-9-repair-evidence-repair-beer-warm-expanded-5a37dc178e67 | beer_lambert | warm_start | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.9-repair-evidence/v1.9-repair-evidence/v1-9-repair-evidence-repair-beer-warm-expanded-5a37dc178e67.json |
| v1.9-repair-aggregate | v1-9-repair-evidence-repair-radioactive-blind-default-1074c1beacc2 | radioactive_decay | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.9-repair-evidence/v1.9-repair-evidence/v1-9-repair-evidence-repair-radioactive-blind-default-1074c1beacc2.json |
| v1.9-repair-aggregate | v1-9-repair-evidence-repair-radioactive-blind-expanded-52a3670eccfb | radioactive_decay | blind | snapped_but_failed | snapped_but_failed | artifacts/campaigns/v1.9-repair-evidence/v1.9-repair-evidence/v1-9-repair-evidence-repair-radioactive-blind-expanded-52a3670eccfb.json |

## Refit

Frozen exact-tree constant refit diagnostics, separate from discovery evidence.

| Metric | Value |
|--------|-------|
| runs | 36 |
| verifier_recovered | 22 |
| same_ast_return | 7 |
| repaired_candidate | 3 |
| unsupported | 0 |
| failed | 14 |

| Source | Run | Formula | Mode | Evidence Class | Status | Artifact |
|--------|-----|---------|------|----------------|--------|----------|
| proof-basin-probes-aggregate | proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-2d877a2bc9fc | beer_lambert | perturbed_tree | perturbed_true_tree_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-basin-probes/runs/proof-perturbed-basin-beer-probes/proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-2d877a2bc9fc.json |
| proof-basin-probes-aggregate | proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-752352286603 | beer_lambert | perturbed_tree | repaired_candidate | repaired_candidate | artifacts/proof/v1.6/campaigns/proof-basin-probes/runs/proof-perturbed-basin-beer-probes/proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-752352286603.json |
| proof-basin-probes-aggregate | proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-99306eda3f85 | beer_lambert | perturbed_tree | repaired_candidate | repaired_candidate | artifacts/proof/v1.6/campaigns/proof-basin-probes/runs/proof-perturbed-basin-beer-probes/proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-99306eda3f85.json |
| proof-basin-probes-aggregate | proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-e17e44438210 | beer_lambert | perturbed_tree | repaired_candidate | repaired_candidate | artifacts/proof/v1.6/campaigns/proof-basin-probes/runs/proof-perturbed-basin-beer-probes/proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-e17e44438210.json |
| proof-perturbed-basin-aggregate | proof-perturbed-basin-basin-beer-lambert-bound-0a5e00e13e43 | beer_lambert | perturbed_tree | perturbed_true_tree_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-basin/runs/proof-perturbed-basin/proof-perturbed-basin-basin-beer-lambert-bound-0a5e00e13e43.json |
| proof-perturbed-basin-aggregate | proof-perturbed-basin-basin-beer-lambert-bound-627e93d6dc9d | beer_lambert | perturbed_tree | perturbed_true_tree_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-basin/runs/proof-perturbed-basin/proof-perturbed-basin-basin-beer-lambert-bound-627e93d6dc9d.json |
| proof-shallow-pure-blind-aggregate | v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-4908b626f452 | beer_lambert | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-4908b626f452.json |
| proof-shallow-pure-blind-aggregate | v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-8599744dc0b5 | beer_lambert | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-8599744dc0b5.json |
| proof-shallow-pure-blind-aggregate | v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-d4b6b4704428 | beer_lambert | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-beer-lambert-pure-blind-d4b6b4704428.json |
| proof-shallow-pure-blind-aggregate | v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-03920c466c9d | radioactive_decay | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-03920c466c9d.json |
| proof-shallow-pure-blind-aggregate | v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-a48b19cb28a2 | radioactive_decay | blind | snapped_but_failed | snapped_but_failed | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-a48b19cb28a2.json |
| proof-shallow-pure-blind-aggregate | v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-b8c2dbde649d | radioactive_decay | blind | failed | failed | artifacts/proof/v1.6/campaigns/proof-shallow-pure-blind/runs/v1.5-shallow-pure-blind/v1-5-shallow-pure-blind-shallow-radioactive-decay-pure-blind-b8c2dbde649d.json |
| ... | 24 additional runs omitted from this view |  |  |  |  |  |

## Perturbed Basin

Perturbed true-tree basin evidence with known starts.

| Metric | Value |
|--------|-------|
| runs | 23 |
| verifier_recovered | 23 |
| same_ast_return | 20 |
| repaired_candidate | 3 |
| unsupported | 0 |
| failed | 0 |

| Source | Run | Formula | Mode | Evidence Class | Status | Artifact |
|--------|-----|---------|------|----------------|--------|----------|
| proof-basin-probes-aggregate | proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-2d877a2bc9fc | beer_lambert | perturbed_tree | perturbed_true_tree_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-basin-probes/runs/proof-perturbed-basin-beer-probes/proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-2d877a2bc9fc.json |
| proof-basin-probes-aggregate | proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-752352286603 | beer_lambert | perturbed_tree | repaired_candidate | repaired_candidate | artifacts/proof/v1.6/campaigns/proof-basin-probes/runs/proof-perturbed-basin-beer-probes/proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-752352286603.json |
| proof-basin-probes-aggregate | proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-99306eda3f85 | beer_lambert | perturbed_tree | repaired_candidate | repaired_candidate | artifacts/proof/v1.6/campaigns/proof-basin-probes/runs/proof-perturbed-basin-beer-probes/proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-99306eda3f85.json |
| proof-basin-probes-aggregate | proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-e17e44438210 | beer_lambert | perturbed_tree | repaired_candidate | repaired_candidate | artifacts/proof/v1.6/campaigns/proof-basin-probes/runs/proof-perturbed-basin-beer-probes/proof-perturbed-basin-beer-probes-basin-beer-lambert-bound-probes-e17e44438210.json |
| proof-depth-curve-aggregate | proof-depth-curve-depth-2-perturbed-63c9dbc22949 | depth_curve_depth2 | perturbed_tree | perturbed_true_tree_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-2-perturbed-63c9dbc22949.json |
| proof-depth-curve-aggregate | proof-depth-curve-depth-2-perturbed-e76ace19ca5b | depth_curve_depth2 | perturbed_tree | perturbed_true_tree_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-2-perturbed-e76ace19ca5b.json |
| proof-depth-curve-aggregate | proof-depth-curve-depth-3-perturbed-35d5a61c1b73 | depth_curve_depth3 | perturbed_tree | perturbed_true_tree_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-3-perturbed-35d5a61c1b73.json |
| proof-depth-curve-aggregate | proof-depth-curve-depth-3-perturbed-5a87ef481565 | depth_curve_depth3 | perturbed_tree | perturbed_true_tree_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-3-perturbed-5a87ef481565.json |
| proof-depth-curve-aggregate | proof-depth-curve-depth-4-perturbed-01bf488498af | depth_curve_depth4 | perturbed_tree | perturbed_true_tree_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-4-perturbed-01bf488498af.json |
| proof-depth-curve-aggregate | proof-depth-curve-depth-4-perturbed-1c743390bc74 | depth_curve_depth4 | perturbed_tree | perturbed_true_tree_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-4-perturbed-1c743390bc74.json |
| proof-depth-curve-aggregate | proof-depth-curve-depth-5-perturbed-acbbb1e43aa6 | depth_curve_depth5 | perturbed_tree | perturbed_true_tree_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-5-perturbed-acbbb1e43aa6.json |
| proof-depth-curve-aggregate | proof-depth-curve-depth-5-perturbed-ca69c9157585 | depth_curve_depth5 | perturbed_tree | perturbed_true_tree_recovered | recovered | artifacts/proof/v1.6/campaigns/proof-depth-curve/runs/proof-depth-curve/proof-depth-curve-depth-5-perturbed-ca69c9157585.json |
| ... | 11 additional runs omitted from this view |  |  |  |  |  |
