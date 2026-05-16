# EML Benchmark Campaign Report: proof-shallow

Bounded v1.5 shallow proof campaign for scaffolded training evidence.

## Reproduce

Run this command from a clean checkout:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign proof-shallow --output-root artifacts/proof/v1.6/campaigns --label proof-shallow --overwrite
```

- Suite: `v1.5-shallow-proof`
- Budget tier: `proof-contract`
- Guardrail: 18 runs; declared shallow scaffolded-training proof suite with bounded threshold metadata.
- Raw run artifacts: [runs/v1.5-shallow-proof](runs/v1.5-shallow-proof)

## Headline Metrics

| Metric | Value |
|--------|-------|
| Total runs | 18 |
| Verifier recovered | 18 (100.0%) |
| Same-AST exact returns | 0 (0.0%) |
| Verified-equivalent exact returns | 0 |
| Unsupported | 0 (0.0%) |
| Failed | 0 (0.0%) |
| Median best soft loss | 6.398e-33 |
| Median post-snap loss | 2.188e-32 |
| Median runtime seconds | 100 |

## Regime Summary

| Regime | Runs | Verifier Recovered | Same AST | Verified Equivalent | Unsupported | Failed |
|--------|------|--------------------|----------|---------------------|-------------|--------|
| blind | 18 | 18 | 0 | 0 | 0 | 0 |
| warm_start | 0 | 0 | 0 | 0 | 0 | 0 |
| compile | 0 | 0 | 0 | 0 | 0 | 0 |
| catalog | 0 | 0 | 0 | 0 | 0 | 0 |
| perturbed_tree | 0 | 0 | 0 | 0 | 0 | 0 |

This table keeps blind, compiler-assisted warm-start, compile-only, catalog, and perturbed-basin evidence visibly separate before any narrative interpretation.

## Proof Contract

| Claim | Threshold | Status | Passed | Eligible | Rate |
|-------|-----------|--------|--------|----------|------|
| paper-shallow-scaffolded-recovery | scaffolded_bounded_100_percent | passed | 18 | 18 | 1.000 |

Bounded proof thresholds count only allowed verifier-owned training evidence classes; catalog and compile-only verification remain separate evidence classes.

## Figures

- [recovery by formula](figures/recovery-by-formula.svg)
- [recovery by start mode](figures/recovery-by-start-mode.svg)
- [loss before after snap](figures/loss-before-after-snap.svg)
- [beer perturbation](figures/beer-perturbation.svg)
- [runtime depth budget](figures/runtime-depth-budget.svg)
- [failure taxonomy](figures/failure-taxonomy.svg)
- [depth curve recovery](figures/depth-curve-recovery.svg)

## Tables

- [runs csv](tables/runs.csv)
- [group formula csv](tables/group-formula.csv)
- [group start mode csv](tables/group-start-mode.csv)
- [group perturbation noise csv](tables/group-perturbation-noise.csv)
- [group depth csv](tables/group-depth.csv)
- [group failure class csv](tables/group-failure-class.csv)
- [group evidence class csv](tables/group-evidence-class.csv)
- [group claim csv](tables/group-claim.csv)
- [group threshold policy csv](tables/group-threshold-policy.csv)
- [depth curve csv](tables/depth-curve.csv)
- [headline json](tables/headline-metrics.json)
- [headline csv](tables/headline-metrics.csv)
- [failures csv](tables/failures.csv)

## What EML Demonstrates Well

This campaign shows the strongest current bounded blind-training behavior in this bundle: 18/18 blind runs passed verifier-owned recovery, and all 18 recovered rows are scaffolded blind recoveries. Read these results as bounded scaffolded-training evidence, not as pure random-initialized blind discovery.

## Limitations

- Blind training recovery: 18/18 blind runs recovered. This campaign records 18 scaffolded blind recoveries and 0 pure random-initialized blind recoveries; compare declared pure-blind proof suites separately.
- Same-AST exact return: 0 runs snapped back to the compiled seed or exact target; useful basin evidence, not discovery.
- Verified-equivalent exact return: 0 runs snapped to a different exact AST that verified.
- Unsupported gates: 0 runs were blocked by compiler/depth/operator limits and remain in the denominator.
- Failed fits: 0 runs did not pass verifier-owned recovery after training or execution.

## Failed and Unsupported Cases

No failed or unsupported cases in this campaign.

## Next Experiments

- Improve blind optimizer robustness and compare against this campaign's `snapped_but_failed` cases.
- Reduce compiled arithmetic tree depth for formulas gated as unsupported, especially Michaelis-Menten and Planck-style expressions.
- Expand perturbation sweeps after optimizer changes so same-AST returns and verified-equivalent recoveries can be compared over time.
- Add external noisy datasets only after the synthetic/source-document campaign remains reproducible and interpretable.
