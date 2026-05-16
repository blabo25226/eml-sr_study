# Scientific-Law Diagnostics

| law | formula | compile_support | compile_depth | macro_hits | warm_start_status | verifier_status | evidence_regime | artifact_path |
|-----|---------|-----------------|---------------|------------|-------------------|-----------------|-----------------|---------------|
| Beer-Lambert | `exp(-0.8*x)` | supported | 9 |  | same_ast_return | recovered | same_ast_return | artifacts/campaigns/v1.6-standard/runs/v1.3-standard/v1-3-standard-beer-perturbation-sweep-c671cedf25f1.json |
| Shockley | `0.2*exp(1.4*x) - 0.2` | supported | 13 | scaled_exp_minus_one_template | same_ast_return | recovered | same_ast_return | artifacts/campaigns/v1.6-standard/runs/v1.3-standard/v1-3-standard-shockley-warm-316f98a5b1fb.json |
| Arrhenius | `exp(-0.8/x)` | supported | 7 | direct_division_template | same_ast_return | recovered | same_ast_return | artifacts/campaigns/v1.9-arrhenius-evidence/v1.9-arrhenius-evidence/v1-9-arrhenius-evidence-arrhenius-warm-75f6e9c1764d.json |
| Michaelis-Menten | `2*x/(x + 0.5)` | supported | 12 | saturation_ratio_template | same_ast_return | recovered | same_ast_return | artifacts/campaigns/v1.9-michaelis-evidence/v1.9-michaelis-evidence/v1-9-michaelis-evidence-michaelis-warm-a67d8ccfb108.json |
| Planck diagnostic | `x**3/(exp(x) - 1)` | unsupported | 20 | scaled_exp_minus_one_template, direct_division_template | not_applicable | unsupported | compile_only | artifacts/campaigns/v1.6-standard/runs/v1.3-standard/v1-3-standard-planck-diagnostic-2309e6363fc8.json |
| Logistic diagnostic | `1/(1 + 2*exp(-1.3*x))` | unsupported | 27 |  | not_applicable | unsupported | compile_only | artifacts/campaigns/v1.6-standard/runs/v1.3-standard/v1-3-standard-logistic-compile-a99c41f57b97.json |
| Historical Michaelis diagnostic | `2*x/(x + 0.5)` | unsupported | 14 | direct_division_template | unsupported | unsupported | historical_context | artifacts/campaigns/v1.6-standard/runs/v1.3-standard/v1-3-standard-michaelis-warm-diagnostic-9917f8383370.json |
