# D0 — Preflight, provenance and tooling
Status: COMPLETED_ACCEPTED

Summary: v4_addons tree created (tools, results, reports, gates [empty, human-only], snapshots); baseline snapshot of the project tree taken; the four deliverable hashes match the handoff; section-9 self-checks reproduced from artifacts with one acknowledged convention discrepancy (SE of gamma-hat), reported and not tuned. G1/G2/G4 tooling (boundary_check.py, test_guard.py, check_numbers.py) runs on dry examples.

## Evidence table

| number | value | source_file | source_key / formula | tag |
|---|---:|---|---|---|
| G | 93660.01994885807 |  | `bayes_actual_gross / prevention_assumption` | [E] |
| K | 14984.92153410634 |  | `bayes_contacts + startup_cost` | [E] |
| g_star | 0.1599927219990843 |  | `K / G` | [E] |
| net_at_20 | 3747.082455665277 |  | `G * 0.2 - K` | [E] |
| slide11_net_lower | 2761.36950443581 | `v2_work/final_metrics.json` | `deployment_intervals.net.lower` | [E] |
| slide11_net_upper | 4660.637082299275 | `v2_work/final_metrics.json` | `deployment_intervals.net.upper` | [E] |
| p_positive_6_14 | 0.9300037463815178 |  | `beta_sf(g_star, prior_6_14_a, prior_6_14_b)` | [E] |
| p_positive_6_24 | 0.6850373137534997 |  | `beta_sf(g_star, prior_6_24_a, prior_6_24_b)` | [E] |
| p_positive_2_18 | 0.16823329149846597 |  | `beta_sf(g_star, prior_2_18_a, prior_2_18_b)` | [E] |
| net_5pct_6_14 | -1172.9190819783926 |  | `G * beta_ppf(0.05, prior_6_14_a, prior_6_14_b) - K` | [E] |
| net_5pct_6_24 | -6166.359913496997 |  | `G * beta_ppf(0.05, prior_6_24_a, prior_6_24_b) - K` | [E] |
| net_5pct_2_18 | -13202.279123826023 |  | `G * beta_ppf(0.05, prior_2_18_a, prior_2_18_b) - K` | [E] |
| evpi_6_14 | 195.7130475430422 |  | `G * beta_mean(prior_6_14_a, prior_6_14_b) * beta_sf(g_star, prior_6_14_a + 1, prior_6_14_b) - K * beta_sf(g_star, prior_6_14_a, prior_6_14_b) - max(expected_net_6_14, 0)` | [E] |
| evpi_6_24 | 1093.2864143914449 |  | `G * beta_mean(prior_6_24_a, prior_6_24_b) * beta_sf(g_star, prior_6_24_a + 1, prior_6_24_b) - K * beta_sf(g_star, prior_6_24_a, prior_6_24_b) - max(expected_net_6_24, 0)` | [E] |
| evpi_2_18 | 832.3583536234751 |  | `G * beta_mean(prior_2_18_a, prior_2_18_b) * beta_sf(g_star, prior_2_18_a + 1, prior_2_18_b) - K * beta_sf(g_star, prior_2_18_a, prior_2_18_b) - max(expected_net_2_18, 0)` | [E] |
| evsi_7872_6_14 | 45.27087200565012 | `v3_addons/results/wp2_evsi.json` | `scenarios[0].evsi_per_cohort` | [E] |
| evsi_7872_6_24 | 531.2203023304611 | `v3_addons/results/wp2_evsi.json` | `scenarios[2].evsi_per_cohort` | [E] |
| evsi_7872_2_18 | 455.44761065250725 | `v3_addons/results/wp2_evsi.json` | `scenarios[4].evsi_per_cohort` | [E] |
| e4_effect_7872_deff1p0 | 0.786 | `v3_addons/results/wp1_power.csv` | `where(method=E4_V_stratified;n_per_arm=7872;gamma=0.2;deff=1.0).effect_power` | [E] |
| e4_profit_7872_deff1p0 | 0.279 | `v3_addons/results/wp1_power.csv` | `where(method=E4_V_stratified;n_per_arm=7872;gamma=0.2;deff=1.0).profit_power` | [E] |
| e4_effect_7872_deff1p1 | 0.76 | `v3_addons/results/wp1_power.csv` | `where(method=E4_V_stratified;n_per_arm=7872;gamma=0.2;deff=1.1).effect_power` | [E] |
| e4_profit_7872_deff1p1 | 0.254 | `v3_addons/results/wp1_power.csv` | `where(method=E4_V_stratified;n_per_arm=7872;gamma=0.2;deff=1.1).profit_power` | [E] |
| e4_effect_7872_deff1p25 | 0.725 | `v3_addons/results/wp1_power.csv` | `where(method=E4_V_stratified;n_per_arm=7872;gamma=0.2;deff=1.25).effect_power` | [E] |
| e4_profit_7872_deff1p25 | 0.216 | `v3_addons/results/wp1_power.csv` | `where(method=E4_V_stratified;n_per_arm=7872;gamma=0.2;deff=1.25).profit_power` | [E] |
| e4_effect_5000_deff1p1 | 0.556 | `v3_addons/results/wp1_power.csv` | `where(method=E4_V_stratified;n_per_arm=5000;gamma=0.2;deff=1.1).effect_power` | [E] |
| e4_profit_5000_deff1p1 | 0.179 | `v3_addons/results/wp1_power.csv` | `where(method=E4_V_stratified;n_per_arm=5000;gamma=0.2;deff=1.1).profit_power` | [E] |
| dq_7872_g20_deff1p1_p_scale | 0.076 | `v3_addons/results/wp2_decision_quality.csv` | `where(n_per_arm=7872;gamma=0.2;deff=1.1).p_scale` | [E] |
| dq_7872_g20_deff1p1_p_extend | 0.919 | `v3_addons/results/wp2_decision_quality.csv` | `where(n_per_arm=7872;gamma=0.2;deff=1.1).p_extend` | [E] |
| dq_7872_g20_deff1p1_p_stop | 0.005 | `v3_addons/results/wp2_decision_quality.csv` | `where(n_per_arm=7872;gamma=0.2;deff=1.1).p_stop` | [E] |
| e1_binary_power_7872 | 0.832 | `v3_addons/results/wp1_power.csv` | `where(method=E1_churn;n_per_arm=7872;gamma=0.2;deff=1.0).effect_power` | [E] |
| e1_normal_approx_7872 | 0.839877574130021 |  | `norm_cdf((p0 - p1) / sqrt(p0 * (1 - p0) / enrolled_per_arm + p1 * (1 - p1) / enrolled_per_arm) - norm_ppf(0.975))` | [E] |
| selected_control_churn | 0.04842492833163853 | `v3_addons/results/inventory.json` | `population.selected_control_churn` | [E] |
| transport_ratio | 2.4212464165819263 |  | `selected_control_churn / deployment_prior` | [A] |
| pi_star_g20_startup_excluded | 0.015464173262384629 | `v3_addons/results/wp5_label_shift.json` | `break_even.first_crossing.prior_star` | [E] |
| queue_billing_lift_exact | 1.0074319321515355 |  | `queue_billing_value_share / queue_billing_count_share` | [E] |
| queue_network_lift_exact | 0.9797681103472066 |  | `queue_network_value_share / queue_network_count_share` | [E] |
| queue_handset_lift_exact | 0.9712900471903978 |  | `queue_handset_value_share / queue_handset_count_share` | [E] |
| queue_residual_lift_exact | 1.0274432688312296 |  | `queue_residual_value_share / queue_residual_count_share` | [E] |
| se_gamma_hat_difference_scaled | 0.06770666750982451 |  | `sqrt(p0 * (1 - p0) / enrolled_per_arm + p1 * (1 - p1) / enrolled_per_arm) / p0` | [E] |
| se_gamma_hat_delta_full | 0.0605922379589923 |  | `sqrt((p1 * (1 - p1) / enrolled_per_arm) / p0**2 + (p1**2 / p0**4) * (p0 * (1 - p0) / enrolled_per_arm))` | [E] |
| gap_assumption_to_break_even | 0.04000727800091572 |  | `prevention_assumption - g_star` | [E] |

## Acceptance checks

- Deliverable hashes vs handoff: **PASS** — philopateer.ipynb match; philopateer.pdf match; philopateer.pptx match; references.txt match
- Section-9 reproductions: **42 of 43 within tolerance**; acknowledged convention discrepancies: se_gamma_hat_delta_full.
  - `se_gamma_hat_difference_scaled` = 6.77 pp reproduces the brief's ≈ 6.8 pp (SE of the churn difference ÷ p0, p0 held fixed).
  - `se_gamma_hat_delta_full` = 6.06 pp is the full two-arm delta method. Both are several times the 4.0 pp gap between the assumed prevention and break-even (1.69 and 1.51 SEs per gap). Conclusion unchanged: the pilot cannot resolve break-even.
  - Queue lifts: the brief's 0.979 / 0.972 (network / handset) reproduce only from the one-decimal published value shares; exact shares give 0.980 / 0.971. Both variants are stored; value per account is flat either way.
  - v2 80,000/arm power: the review quotes the descriptive `pilot_test` rows (adjusted 0.9525 / unadjusted 0.3725); the planning `pilot_calibration` rows read 0.9725 / 0.5025. Both grids select 80,000 as the first qualifying grid point.
- Boundary check before/after D0: see `results/boundary_log.jsonl` (clean).
- Tools dry-run: `test_guard.py` denies access without `gates/H2_APPROVED.txt` (exit 2); `check_numbers.py` re-reads every bound source; `boundary_check.py` compares against `snapshots/baseline_2026-10-31.json`.

## Deviations from the brief

- `verify_runtime()` is executed from the v3 source text (AST-extracted, sha256 recorded in every provenance block) instead of `import common`, because importing `v3_addons/src/common.py` installs an audit hook that forbids every write outside `v3_addons/` and would block v4 output. The function body is unchanged.
- The baseline snapshot excludes `.git/` and `__pycache__/` (not project artifacts; `.git` index changes on read). File count therefore differs from the v3 4,246-file diff, which excluded `v3_addons/` instead.
- `V3_REJECTION_REVIEW.md` is not in the project root; it was read from the Obsidian vault path `01_Projects/GCI2026/2- final A/details/v3/V3_REJECTION_REVIEW.md` (read-only).

## Open questions / [DECISION NEEDED]

- None blocking. Section-3 defaults are recorded in `DECISIONS_ASSUMED.md` as DEFAULT_ASSUMED until `gates/H0_DECISIONS.md` exists.

## Commands run

```bash
PY="C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe"
cd D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v4_addons/tools
"$PY" -B -X utf8 boundary_check.py --snapshot
"$PY" -B -X utf8 boundary_check.py --card D0 --phase pre
"$PY" -B -X utf8 test_guard.py          # exit 2 = denied (expected)
"$PY" -B -X utf8 d0_preflight.py
"$PY" -B -X utf8 check_numbers.py
"$PY" -B -X utf8 d0_report.py
"$PY" -B -X utf8 boundary_check.py --card D0 --phase post
```

Environment: Python 3.11.9; verify_runtime pools: openblas 0.3.30 num_threads=6, openblas 0.3.30 num_threads=6; thread cap 6; seed 20,261,028.

Boundary check: before/after hashes clean? yes (see `results/boundary_log.jsonl`, card D0).
