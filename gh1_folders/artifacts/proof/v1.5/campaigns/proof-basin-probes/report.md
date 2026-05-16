# EML Benchmark Campaign Report: proof-basin-probes

Visible v1.5 Beer-Lambert perturbed-basin probe campaign outside bounded thresholds.

## Reproduce

Run this command from a clean checkout:

```bash
PYTHONPATH=src python -m eml_symbolic_regression.cli campaign proof-basin-probes --output-root artifacts/proof/v1.5/campaigns --label proof-basin-probes --overwrite
```

- Suite: `proof-perturbed-basin-beer-probes`
- Budget tier: `proof-contract`
- Guardrail: 4 runs; declared Beer-Lambert high-noise probe rows kept outside the bounded proof denominator.
- Raw run artifacts: [runs/proof-perturbed-basin-beer-probes](runs/proof-perturbed-basin-beer-probes)

## Headline Metrics

| Metric | Value |
|--------|-------|
| Total runs | 4 |
| Verifier recovered | 4 (100.0%) |
| Same-AST warm-start returns | 0 (0.0%) |
| Verified equivalent warm-start recoveries | 0 |
| Unsupported | 0 (0.0%) |
| Failed | 0 (0.0%) |
| Median best soft loss | 0.2312 |
| Median post-snap loss | 0.2337 |
| Median runtime seconds | 5.448 |

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

This campaign shows the strongest current behavior when the EML representation is verified after snapping: 4/4 runs passed verifier-owned recovery. Warm-start runs are especially useful evidence: 1 returned to the same compiled EML AST and 0 produced a different verified-equivalent AST. Those are not blind-discovery claims, but they are practical evidence that the paper's uniform EML tree can be compiled, embedded, perturbed, optimized, snapped, and independently verified.

## Limitations

- Blind recovery: 0/0 blind runs recovered. Treat this separately from compiler-assisted paths.
- Same-AST warm-start return: 0 runs snapped back to the compiled seed; useful basin evidence, not discovery.
- Verified-equivalent warm-start recovery: 0 runs snapped to a different exact AST that verified.
- Unsupported gates: 0 runs were blocked by compiler/depth/operator limits and remain in the denominator.
- Failed fits: 0 runs did not pass verifier-owned recovery after training or execution.

## Failed and Unsupported Cases

No failed or unsupported cases in this campaign.

## Next Experiments

- Improve blind optimizer robustness and compare against this campaign's `snapped_but_failed` cases.
- Reduce compiled arithmetic tree depth for formulas gated as unsupported, especially Michaelis-Menten and Planck-style expressions.
- Expand perturbation sweeps after optimizer changes so same-AST returns and verified-equivalent recoveries can be compared over time.
- Add external noisy datasets only after the synthetic/source-document campaign remains reproducible and interpretable.
