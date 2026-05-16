# Conventional Symbolic Baseline Probe

| baseline_id | checked_modules | detected_modules | status | formula | reason | limitation | diagnostic_only | denominator_policy | claim_boundary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| conventional_symbolic_regression | ['pysr', 'gplearn', 'pyoperon', 'karoo_gp'] | [] | unavailable | not_run | no_local_symbolic_regression_package | PySR, gplearn, PyOperon, and karoo-gp were not importable locally; no dependency installation was attempted in this bounded phase. | true | excluded from EML recovery denominators | absence of a conventional SR comparator is reported as a limitation, not hidden |
