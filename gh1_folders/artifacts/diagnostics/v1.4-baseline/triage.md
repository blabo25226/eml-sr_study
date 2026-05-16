# Baseline Failure Triage

Committed v1.3 campaign failures grouped for v1.4 improvement work.

## Baselines

| Campaign | Runs | Verifier recovered | Unsupported | Failed |
|----------|------|--------------------|-------------|--------|
| v1.3-standard | 16 | 5 | 4 | 7 |
| v1.3-showcase | 29 | 13 | 5 | 11 |

## Failure Groups

| Formula | Mode | Perturbation | Class | Count |
|---------|------|--------------|-------|-------|
| beer_lambert | warm_start | 15.0 | snapped_but_failed | 1 |
| beer_lambert | warm_start | 35.0 | snapped_but_failed | 5 |
| damped_oscillator | compile | 0.0 | unsupported | 1 |
| exp | blind | 0.0 | snapped_but_failed | 2 |
| log | blind | 0.0 | snapped_but_failed | 5 |
| logistic | compile | 0.0 | unsupported | 2 |
| michaelis_menten | warm_start | 0.0 | unsupported | 2 |
| planck | compile | 0.0 | unsupported | 2 |
| radioactive_decay | blind | 0.0 | failed | 5 |
| shockley | compile | 0.0 | unsupported | 2 |

## Focused Diagnostic Subsets

| Target | Runs | Formula filter | Mode filter | Noise filter |
|--------|------|----------------|-------------|--------------|
| beer-perturbation-failures | 6 | beer_lambert | warm_start | 15.0, 35.0 |
| blind-failures | 12 | exp, log, radioactive_decay | blind | 0.0 |
| compiler-depth-gates | 9 | damped_oscillator, logistic, michaelis_menten, planck, shockley | compile, warm_start | 0.0 |

## Representative Failure Runs

| Campaign | Formula | Mode | Seed | Noise | Class | Reason | Metrics | Artifact |
|----------|---------|------|------|-------|-------|--------|---------|----------|
| v1.3-standard | exp | blind | 0 | 0.0 | snapped_but_failed | mpmath_failed | best=4.276; snap=6.65; margin=0.4618; changed=n/a; verifier=failed | [v1-3-standard-exp-blind-a5022d6098c7](artifacts/campaigns/v1.3-standard/runs/v1.3-standard/v1-3-standard-exp-blind-a5022d6098c7.json) |
| v1.3-standard | log | blind | 0 | 0.0 | snapped_but_failed | mpmath_failed | best=1.635; snap=57.11; margin=0.0656; changed=n/a; verifier=failed | [v1-3-standard-log-blind-194180dc5df0](artifacts/campaigns/v1.3-standard/runs/v1.3-standard/v1-3-standard-log-blind-194180dc5df0.json) |
| v1.3-standard | log | blind | 1 | 0.0 | snapped_but_failed | mpmath_failed | best=0.9829; snap=57.27; margin=0.04021; changed=n/a; verifier=failed | [v1-3-standard-log-blind-99aa5ff393ee](artifacts/campaigns/v1.3-standard/runs/v1.3-standard/v1-3-standard-log-blind-99aa5ff393ee.json) |
| v1.3-standard | radioactive_decay | blind | 0 | 0.0 | failed | mpmath_failed | best=662.4; snap=inf; margin=0.01639; changed=n/a; verifier=failed | [v1-3-standard-radioactive-decay-blind-20f83222d0db](artifacts/campaigns/v1.3-standard/runs/v1.3-standard/v1-3-standard-radioactive-decay-blind-20f83222d0db.json) |
| v1.3-standard | radioactive_decay | blind | 1 | 0.0 | failed | mpmath_failed | best=605.1; snap=inf; margin=0.05137; changed=n/a; verifier=failed | [v1-3-standard-radioactive-decay-blind-83660c5b4b25](artifacts/campaigns/v1.3-standard/runs/v1.3-standard/v1-3-standard-radioactive-decay-blind-83660c5b4b25.json) |
| v1.3-standard | beer_lambert | warm_start | 0 | 35.0 | snapped_but_failed | verified | best=6.972; snap=7.225; margin=0.9726; changed=5; verifier=failed | [v1-3-standard-beer-perturbation-sweep-348eebff7ed4](artifacts/campaigns/v1.3-standard/runs/v1.3-standard/v1-3-standard-beer-perturbation-sweep-348eebff7ed4.json) |
| v1.3-standard | beer_lambert | warm_start | 1 | 35.0 | snapped_but_failed | verified | best=0.2193; snap=0.2193; margin=1; changed=3; verifier=failed | [v1-3-standard-beer-perturbation-sweep-68c818aed370](artifacts/campaigns/v1.3-standard/runs/v1.3-standard/v1-3-standard-beer-perturbation-sweep-68c818aed370.json) |
| v1.3-standard | michaelis_menten | warm_start | 0 | 0.0 | unsupported | depth_exceeded | best=n/a; snap=n/a; margin=n/a; changed=n/a; verifier=None | [v1-3-standard-michaelis-warm-diagnostic-37a57673a2e2](artifacts/campaigns/v1.3-standard/runs/v1.3-standard/v1-3-standard-michaelis-warm-diagnostic-37a57673a2e2.json) |
| v1.3-standard | logistic | compile | 0 | 0.0 | unsupported | depth_exceeded | best=n/a; snap=n/a; margin=n/a; changed=n/a; verifier=None | [v1-3-standard-logistic-compile-820d90103856](artifacts/campaigns/v1.3-standard/runs/v1.3-standard/v1-3-standard-logistic-compile-820d90103856.json) |
| v1.3-standard | shockley | compile | 0 | 0.0 | unsupported | depth_exceeded | best=n/a; snap=n/a; margin=n/a; changed=n/a; verifier=None | [v1-3-standard-shockley-compile-e410a7c053d4](artifacts/campaigns/v1.3-standard/runs/v1.3-standard/v1-3-standard-shockley-compile-e410a7c053d4.json) |
| v1.3-standard | planck | compile | 0 | 0.0 | unsupported | depth_exceeded | best=n/a; snap=n/a; margin=n/a; changed=n/a; verifier=None | [v1-3-standard-planck-diagnostic-837e17c92c48](artifacts/campaigns/v1.3-standard/runs/v1.3-standard/v1-3-standard-planck-diagnostic-837e17c92c48.json) |
| v1.3-showcase | exp | blind | 0 | 0.0 | snapped_but_failed | mpmath_failed | best=4.276; snap=6.65; margin=0.6864; changed=n/a; verifier=failed | [v1-3-showcase-exp-blind-c693d4329a15](artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-exp-blind-c693d4329a15.json) |
| v1.3-showcase | log | blind | 0 | 0.0 | snapped_but_failed | mpmath_failed | best=1.573; snap=57.11; margin=0.1955; changed=n/a; verifier=failed | [v1-3-showcase-log-blind-332dbad5db03](artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-log-blind-332dbad5db03.json) |
| v1.3-showcase | log | blind | 1 | 0.0 | snapped_but_failed | mpmath_failed | best=0.9862; snap=57.27; margin=0.04023; changed=n/a; verifier=failed | [v1-3-showcase-log-blind-a52747a50ca2](artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-log-blind-a52747a50ca2.json) |
| v1.3-showcase | log | blind | 2 | 0.0 | snapped_but_failed | mpmath_failed | best=1.32; snap=57.16; margin=0.06249; changed=n/a; verifier=failed | [v1-3-showcase-log-blind-cf7866232845](artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-log-blind-cf7866232845.json) |
| v1.3-showcase | radioactive_decay | blind | 0 | 0.0 | failed | mpmath_failed | best=652.9; snap=inf; margin=0.01639; changed=n/a; verifier=failed | [v1-3-showcase-radioactive-decay-blind-4a34febadef0](artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-radioactive-decay-blind-4a34febadef0.json) |
| v1.3-showcase | radioactive_decay | blind | 1 | 0.0 | failed | mpmath_failed | best=693.6; snap=inf; margin=0.05083; changed=n/a; verifier=failed | [v1-3-showcase-radioactive-decay-blind-8055ab006d29](artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-radioactive-decay-blind-8055ab006d29.json) |
| v1.3-showcase | radioactive_decay | blind | 2 | 0.0 | failed | mpmath_failed | best=780.5; snap=inf; margin=0.001516; changed=n/a; verifier=failed | [v1-3-showcase-radioactive-decay-blind-396f4bdf4078](artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-radioactive-decay-blind-396f4bdf4078.json) |
| v1.3-showcase | beer_lambert | warm_start | 0 | 35.0 | snapped_but_failed | verified | best=6.919; snap=7.225; margin=0.9851; changed=5; verifier=failed | [v1-3-showcase-beer-perturbation-sweep-6ffb162a5bb7](artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-6ffb162a5bb7.json) |
| v1.3-showcase | beer_lambert | warm_start | 1 | 15.0 | snapped_but_failed | verified | best=0.2151; snap=0.2193; margin=0.9999; changed=1; verifier=failed | [v1-3-showcase-beer-perturbation-sweep-89c991bee41e](artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-89c991bee41e.json) |
| v1.3-showcase | beer_lambert | warm_start | 1 | 35.0 | snapped_but_failed | verified | best=0.2193; snap=0.2193; margin=1; changed=3; verifier=failed | [v1-3-showcase-beer-perturbation-sweep-8615aab30e44](artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-8615aab30e44.json) |
| v1.3-showcase | beer_lambert | warm_start | 2 | 35.0 | snapped_but_failed | verified | best=0.3736; snap=0.07479; margin=0.2743; changed=7; verifier=failed | [v1-3-showcase-beer-perturbation-sweep-05cb8f1ed422](artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-beer-perturbation-sweep-05cb8f1ed422.json) |
| v1.3-showcase | michaelis_menten | warm_start | 0 | 0.0 | unsupported | depth_exceeded | best=n/a; snap=n/a; margin=n/a; changed=n/a; verifier=None | [v1-3-showcase-michaelis-warm-diagnostic-8f1f8084d61b](artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-michaelis-warm-diagnostic-8f1f8084d61b.json) |
| v1.3-showcase | logistic | compile | 0 | 0.0 | unsupported | depth_exceeded | best=n/a; snap=n/a; margin=n/a; changed=n/a; verifier=None | [v1-3-showcase-logistic-compile-5a739cf1c01f](artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-logistic-compile-5a739cf1c01f.json) |
| v1.3-showcase | shockley | compile | 0 | 0.0 | unsupported | depth_exceeded | best=n/a; snap=n/a; margin=n/a; changed=n/a; verifier=None | [v1-3-showcase-shockley-compile-0119659ca5dd](artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-shockley-compile-0119659ca5dd.json) |
| v1.3-showcase | damped_oscillator | compile | 0 | 0.0 | unsupported | unsupported_operator | best=n/a; snap=n/a; margin=n/a; changed=n/a; verifier=None | [v1-3-showcase-damped-oscillator-compile-9b393796ada0](artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-damped-oscillator-compile-9b393796ada0.json) |
| v1.3-showcase | planck | compile | 0 | 0.0 | unsupported | depth_exceeded | best=n/a; snap=n/a; margin=n/a; changed=n/a; verifier=None | [v1-3-showcase-planck-diagnostic-1ba93a0c5966](artifacts/campaigns/v1.3-showcase/runs/v1.3-showcase/v1-3-showcase-planck-diagnostic-1ba93a0c5966.json) |

## Baseline Locks

| Campaign | File | SHA-256 |
|----------|------|---------|
| v1.3-standard | artifacts/campaigns/v1.3-standard/aggregate.json | `886d4a5ed558c7089df653da4ac641d17bb862717ad0561806a5cd88ec0f7e8e` |
| v1.3-standard | artifacts/campaigns/v1.3-standard/suite-result.json | `1beae94ce644381d5369fc75f57f749a359a9734ddce6eb71681e15c6c91c2c8` |
| v1.3-standard | artifacts/campaigns/v1.3-standard/campaign-manifest.json | `54a753197fe143f9a79741564fffe25ebe5b14fd2003213b167a25cb5f70824a` |
| v1.3-standard | artifacts/campaigns/v1.3-standard/tables/runs.csv | `5be8287f724612c20eea54403d6b3b7ffad41bfa09ed5f3e576510874230f27a` |
| v1.3-standard | artifacts/campaigns/v1.3-standard/tables/failures.csv | `a570df2e1539d6436acd8810b6334b4c613bff8c877cc198968ed62a17f1bbac` |
| v1.3-showcase | artifacts/campaigns/v1.3-showcase/aggregate.json | `28ff4e7b5eda78ad2045eec13eac3c042a0b6173dbffaebf9a3e0d9b970dee7c` |
| v1.3-showcase | artifacts/campaigns/v1.3-showcase/suite-result.json | `1329913d7045850ad8027a99a314ae6d3a4a72586ad54c5a84bcec3ccce07606` |
| v1.3-showcase | artifacts/campaigns/v1.3-showcase/campaign-manifest.json | `b8e3bce7014b2ad23f8a658f84bc2fa1b3593f0932288da85b986d52da29c018` |
| v1.3-showcase | artifacts/campaigns/v1.3-showcase/tables/runs.csv | `3a3a0f396b628fd824a2961cb3dd22d46d93506024467f4cbff7423e084e96d5` |
| v1.3-showcase | artifacts/campaigns/v1.3-showcase/tables/failures.csv | `1b635c3be5307d97a4a6ce075c580a645ccbcb970f27899aeb7c8daf0c9bf22e` |
