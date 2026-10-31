# D2 — Yardstick sheet
Status: COMPLETED_ACCEPTED

Summary: `YARDSTICK.md` + `results/yardstick.json` reconcile the four sample sizes and three profit definitions in one sheet: seven frames, estimator and DEFF tables, eight bridge sentences (≤ 25 words, counts bound), and the pilot-purpose statement with SE(γ̂) derived in code. Two G10 definition discrepancies with the brief are reported (SE convention; π* is fully loaded, not startup-excluded).

## Evidence table

| number | value | source_file | source_key / formula | tag |
|---|---:|---|---|---|
| binary_enrolled_per_arm | 7,872 | `v2_work/final_metrics.json` | `pilot_calibration.spec.normal_binary_reference.enrolled_per_arm` | [E] |
| first_grid_e4_profit | 40,000 | `v3_addons/results/wp1_power.json` | `requirements_at_gamma_20[6].first_qualifying_grid_n` | [E] |
| first_grid_e4_effect | 10,000 | `v3_addons/results/wp1_power.json` | `requirements_at_gamma_20[5].first_qualifying_grid_n` | [E] |
| v2_grid_adjusted_calibration | 80,000 | `v2_work/final_metrics.json` | `pilot_calibration.simulated_required_enrolled_per_arm_grid.adjusted_contribution` | [E] |
| v2_80k_adjusted_calibration | 0.9725 | `v2_work/final_metrics.json` | `pilot_calibration.power_rows[23].simulated_power` | [E] |
| v2_80k_adjusted_test | 0.9525 | `v2_work/final_metrics.json` | `pilot_test.power_rows[23].simulated_power` | [E] |
| max_per_arm_one_list | 5,000 |  | `list_size / 2` | [E] |
| stage1_total_enrolled | 15,744 | `v2_work/final_metrics.json` | `pilot_calibration.spec.stage1_total_enrolled` | [E] |
| planning_portfolio_proxy | 158,000 | `v2_work/final_metrics.json` | `pilot_calibration.spec.planning_portfolio_calibration_proxy` | [E] |
| e4_effect_power_7872_deff1p1 | 0.760 | `v3_addons/results/wp1_power.csv` | `where(method=E4_V_stratified;n_per_arm=7872;gamma=0.2;deff=1.1).effect_power` | [E] |
| e4_profit_power_7872_deff1p1 | 0.254 | `v3_addons/results/wp1_power.csv` | `where(method=E4_V_stratified;n_per_arm=7872;gamma=0.2;deff=1.1).profit_power` | [E] |
| e4_effect_power_5000_deff1p1 | 0.556 | `v3_addons/results/wp1_power.csv` | `where(method=E4_V_stratified;n_per_arm=5000;gamma=0.2;deff=1.1).effect_power` | [E] |
| e4_profit_power_5000_deff1p1 | 0.179 | `v3_addons/results/wp1_power.csv` | `where(method=E4_V_stratified;n_per_arm=5000;gamma=0.2;deff=1.1).profit_power` | [E] |
| est_e2_observed_80000_profit | 0.527 | `v3_addons/results/wp1_power.csv` | `where(method=E2_observed;n_per_arm=80000;gamma=0.2;deff=1.0).profit_power` | [E] |
| est_e4_80000_profit | 0.988 | `v3_addons/results/wp1_power.csv` | `where(method=E4_V_stratified;n_per_arm=80000;gamma=0.2;deff=1.0).profit_power` | [E] |
| spread_80k_profit_e2obs_vs_e4 | 0.461 |  | `est_e4_80000_profit - est_e2_observed_80000_profit` | [E] |
| dq_7872_g20_p_scale | 0.076 | `v3_addons/results/wp2_decision_quality.csv` | `where(n_per_arm=7872;gamma=0.2;deff=1.1).p_scale` | [E] |
| dq_7872_g20_p_extend | 0.919 | `v3_addons/results/wp2_decision_quality.csv` | `where(n_per_arm=7872;gamma=0.2;deff=1.1).p_extend` | [E] |
| dq_7872_g20_p_stop | 0.005 | `v3_addons/results/wp2_decision_quality.csv` | `where(n_per_arm=7872;gamma=0.2;deff=1.1).p_stop` | [E] |
| dq_7872_g0_p_extend | 0.475 | `v3_addons/results/wp2_decision_quality.csv` | `where(n_per_arm=7872;gamma=0.0;deff=1.1).p_extend` | [E] |
| dq_7872_g0_p_stop | 0.525 | `v3_addons/results/wp2_decision_quality.csv` | `where(n_per_arm=7872;gamma=0.0;deff=1.1).p_stop` | [E] |
| se_gamma_hat_difference_scaled | 0.0677 |  | `sqrt(binary_p0 * (1 - binary_p0) / binary_enrolled_per_arm + binary_p1 * (1 - binary_p1) / binary_enrolled_per_arm) / binary_p0` | [E] |
| se_gamma_hat_delta_full | 0.0606 |  | `sqrt((binary_p1 * (1 - binary_p1) / binary_enrolled_per_arm) / binary_p0**2 + (binary_p1**2 / binary_p0**4) * (binary_p0 * (1 - binary_p0) / binary_enrolled_per_arm))` | [E] |
| gap_assumption_to_break_even | 0.0400 |  | `binary_relative_prevention_assumption - g_star` | [E] |
| pi_star_fully_loaded | 0.01546417 | `v3_addons/results/wp5_label_shift.json` | `break_even.first_crossing.prior_star` | [E] |
| pi_star_startup_excluded | 0.01036128 | `v3_addons/results/wp5_break_even_grid.csv` | `actual_gross,contacts (interpolated zero crossing)` | [E] |
| wp5_fixed_cost_in_net | $5,000 | `v3_addons/results/wp5_label_shift.json` | `break_even.economic_assumptions.fixed_cost` | [A] |
| transport_ratio | 2.4212 |  | `selected_control_churn / deployment_prior` | [A] |
| startup_per_enrollee_7872 | 0.3176 |  | `startup_cost / stage1_total_enrolled` | [E] |

## Acceptance checks

- `check_numbers.py --scan ../YARDSTICK.md`: **PASS** — 0 unbound numeric tokens; every number in the sheet is rendered from `results/yardstick.json`.
- Zero hand-typed numbers: **PASS** (render registry `results/YARDSTICK_render.json`; sheet hash recorded).
- Every oracle estimator labelled "oracle — invalid for capacity claims": **PASS** (E2_literal_oracle, E3_literal_oracle in both estimator tables).
- DEFF consistent across the sheet: **PASS** — default 1.1 declared once (`deff_default`) and referenced everywhere; 1.0 / 1.25 only in the sensitivity table; the WP1 grid points are labelled as DEFF-1.0 statements.
- Bridge sentences ≤ 25 words: **PASS** — longest is `deff_statement` at 24 words (all counts bound as `words_*`).
- Pilot purpose statement reproduces WP2 (0.076 / 0.919 / 0.005; γ=0: 0.475 / 0.525) and derives SE(γ̂) in code with the formula recorded: **PASS**.

## Deviations from the brief

- **G10 discrepancy (reported, not tuned):** the brief's "SE(γ̂) ≈ 6.8 pp (delta method)" reproduces as SE(p̂0 − p̂1)/p0 with p0 held fixed (6.77 pp); the full two-arm delta method gives 6.06 pp. Both are bound and shown; the conclusion (pilot cannot resolve break-even) holds under either.
- **G10 discrepancy (reported, not tuned):** WP5's π* = 1.546417% is the crossing of the *fully loaded* net (its grid `net` = gross − contacts − $5,000; `economic_assumptions.fixed_cost`). The brief labels it "startup excluded". The startup-excluded crossing on the same grid is ≈ 1.0361%. The sheet states the correct definition; D7 recomputes both with the exact v2 functions.
- The frames table quotes the v2 80,000/arm power for both partitions (planning rows 0.9725 / 0.5025; descriptive test rows 0.9525 / 0.3725, the latter being the review's source). Both grids select 80,000.

## Open questions / [DECISION NEEDED] items

- None new. The DEFF 1.1 default, three-yardstick wording and 5,000/arm operating case follow `DECISIONS_ASSUMED.md` rows 1–3 (DEFAULT_ASSUMED until `gates/H0_DECISIONS.md`).

## Commands run

```bash
PY="C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe"; R="D:/progs/IDE/MainProjs/AI/GCI2026/finalA"
cd "$R/v4_addons/tools"
"$PY" -B -X utf8 boundary_check.py --card D2 --phase pre
"$PY" -B -X utf8 d2_yardstick.py
"$PY" -B -X utf8 check_numbers.py --scan ../YARDSTICK.md
"$PY" -B -X utf8 d2_report.py
"$PY" -B -X utf8 boundary_check.py --card D2 --phase post
```

Environment: Python 3.11.9; verify_runtime pools: openblas 0.3.30 num_threads=6, openblas 0.3.30 num_threads=6; seed 20261030.

Boundary check: before/after hashes clean? yes (pre clean; post shows only the 4 D1-allowed changes).
