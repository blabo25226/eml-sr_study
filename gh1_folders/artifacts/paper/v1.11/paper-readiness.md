# v1.11 Paper Readiness Summary

## Evidence Position

- Current-code paper-training campaign: 8/8 verifier-recovered runs across pure blind, scaffolded, warm-start, and perturbed-basin regimes.
- Logistic/Planck probes: 0/4 recovered, 2 unsupported, 2 failed.
- Supported scientific-law rows: Beer-Lambert, Shockley, Arrhenius, Michaelis-Menten.
- Logistic motif depth: 27 -> 15 with `exponential_saturation_template`, still unsupported under the strict gate.
- Planck motif depth: 24 -> 14 with `low_degree_power_template;scaled_exp_minus_one_template;direct_division_template`, still unsupported under the strict gate.
- Paper assets: 7 figures and 7 source tables.
- Diagnostics: 6 motif rows and 20 prediction-only baseline rows.

## Paper Framing

The material is strong for a verifier-gated hybrid EML symbolic-regression paper: the repository now has real current-code training, source-locked motif ablations, scientific-law support rows, negative logistic/Planck probes, and figure-ready artifacts.

It should not be framed as broad blind symbolic-regression superiority. The defensible story is representation fidelity, exact candidate generation, honest verifier ownership, strong shallow and basin regimes, and clear failure boundaries as depth and law complexity rise.
