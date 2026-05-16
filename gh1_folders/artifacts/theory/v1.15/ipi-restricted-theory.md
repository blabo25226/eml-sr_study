# i*pi EML Restricted Theory

- Schema: `eml.ipi_restricted_theory.v1`
- Status: `passed`
- Branch convention: principal complex log with cut on the negative real axis

## Assumptions

- second-slot identity inputs use y > 0
- real-axis derivative and composition checks use real x or u
- v > 0 for one-step composition magnitude bounds
- mpmath principal log is the executable oracle

## Checked Identities

| Check | Status | Max error | Statement |
|-------|--------|-----------|-----------|
| `THRY-01` | `passed` | `3.14663077128e-102` | i*pi EML(i*pi EML(1, y), 1) = -1/y for y > 0 |
| `THRY-02` | `passed` | `5.72845633632e-101` | -1 / i*pi EML(i*pi EML(1, y), 1) recovers y for y > 0 |
| `THRY-03` | `passed` | `1.23567901433e-102` | d/dx i*pi EML(x, y) = i*pi*exp(i*pi*x), with magnitude pi for real x |
| `THRY-04` | `passed` | `1.82877982605e-99` | exp(-pi)/v <= |i*pi EML(i*pi EML(u, v), 1)| <= exp(pi)/v for real u and v > 0 |

## Non-Claims

- does not prove full scientific-calculator universality
- does not prove global closure across complex branch cuts
- does not justify benchmark claims outside declared branch-safe domains
