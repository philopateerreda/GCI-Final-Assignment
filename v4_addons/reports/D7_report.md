# D7 — Monitor wrap-up (diagnostic only)
Status: COMPLETED_ACCEPTED

Summary: `MONITOR_WRAPUP.md` recomputes π*(γ) for five assumed prevention values from the exact v2 functions, resolves the trigger into three mutually exclusive day-60 states, and quantifies label vs EM precision; the 1.546417% figure reproduces as the startup-included crossing, not the startup-excluded one the brief names.

## Evidence table

| number | value | source_file | source_key / formula | tag |
|---|---:|---|---|---|
| pi_star_incl_15 | 2.0748% | `v4_addons/results/d7_pi_star_grid.csv` | `net_included_15` | [E] |
| pi_star_incl_20 | 1.5464% | `v4_addons/results/d7_pi_star_grid.csv` | `net_included_20` | [E] |
| pi_star_incl_25 | 1.2331% | `v4_addons/results/d7_pi_star_grid.csv` | `net_included_25` | [E] |
| pi_star_incl_30 | 1.0252% | `v4_addons/results/d7_pi_star_grid.csv` | `net_included_30` | [E] |
| pi_star_excl_10 | 2.0918% | `v4_addons/results/d7_pi_star_grid.csv` | `net_excluded_10` | [E] |
| pi_star_excl_15 | 1.3855% | `v4_addons/results/d7_pi_star_grid.csv` | `net_excluded_15` | [E] |
| pi_star_excl_20 | 1.0361% | `v4_addons/results/d7_pi_star_grid.csv` | `net_excluded_20` | [E] |
| pi_star_excl_25 | 0.8276% | `v4_addons/results/d7_pi_star_grid.csv` | `net_excluded_25` | [E] |
| pi_star_excl_30 | 0.6892% | `v4_addons/results/d7_pi_star_grid.csv` | `net_excluded_30` | [E] |
| wp5_pi_star_recorded | 1.546417% | `v3_addons/results/wp5_label_shift.json` | `break_even.first_crossing.prior_star` | [E] |
| pi_star_reproduction_abs_diff | 0.0 |  | `absolute difference between the recomputed startup-included crossing at gamma=0.20 and the WP5-recorded crossing` | [E] |
| pi_star_startup_effect_20 | 0.51 | `v4_addons/results/d7_pi_star_grid.csv` | `net_included_20 - net_excluded_20` | [E] |
| margin_fully_loaded_pp | 0.454 |  | `(deployment_prior_2pct - pi_star_incl_20) * 100` | [E] |
| label_se_10k | 0.140 pp |  | `sqrt(deployment_prior_2pct * (1 - deployment_prior_2pct) / n_10k)` | [E] |
| label_se_50k | 0.063 pp |  | `sqrt(deployment_prior_2pct * (1 - deployment_prior_2pct) / n_50k)` | [E] |
| label_se_100k | 0.044 pp |  | `sqrt(deployment_prior_2pct * (1 - deployment_prior_2pct) / n_100k)` | [E] |
| em_bias_10k | 0.578 pp | `v3_addons/results/wp5_label_shift.json` | `grid_summary[9].bias` | [E] |
| em_bias_50k | 0.505 pp | `v3_addons/results/wp5_label_shift.json` | `grid_summary[10].bias` | [E] |
| em_bias_100k | 0.515 pp | `v3_addons/results/wp5_label_shift.json` | `grid_summary[11].bias` | [E] |

## Acceptance checks

- π*(γ) computed for all five gammas under both cost definitions with the exact v2 functions: **PASS**.
- γ = 0.20 startup-included crossing reproduces the WP5-recorded value within 1e-6: **PASS** (absolute difference 0.0).
- Section 9 labels that same value "startup excluded"; the recomputation shows it is the startup-included crossing. **FAIL as labelled → reported under G10, not tuned.**
- Trigger rule is one mutually exclusive table driven by day-60 labels, EM diagnostic-only: **PASS**.
- Label precision (0.140 pp / 0.063 pp / 0.044 pp) reproduced: **PASS**.
- EM variants deferred because the bias at the 2% prior exceeds the 0.15 pp threshold: **PASS**.
- No test rows read, no new fits: **PASS** (`test_rows_used = 0`, `new_model_fits = 0`).

## Deviations from the brief

- The brief's check "startup excluded gives 1.546417%" does not hold: that is the startup-included crossing, and the startup-excluded crossing is 1.0361%. The number reproduces exactly; only its label in the brief is wrong (G10).
- D0 bound WP5's `first_crossing.prior_star` using the brief's "startup excluded" label; this card supersedes that label and keeps the value.
- The brief describes the label-vs-EM precision advantage as roughly tenfold; the recorded ratios are 4.1 / 8.1 / 11.6 label standard errors at the three cohort sizes, so the advantage is size-dependent.

## Open questions / [DECISION NEEDED] items

- `[DECISION NEEDED]` fix the π* definition (startup included vs excluded) before any operational monitor; the choice moves the HOLD boundary by 0.51 pp.
- `[DECISION NEEDED]` Floor contact cost (carried from D6).
- `[DECISION NEEDED]` harm-gate action and owner (carried from D6).
- `[DECISION NEEDED]` extension budget (carried from D4).

## Commands run

```bash
PY="C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe"; R="D:/progs/IDE/MainProjs/AI/GCI2026/finalA"
cd "$R/v4_addons/tools"
"$PY" -B -X utf8 boundary_check.py --card D7 --phase pre
"$PY" -B -X utf8 d7_monitor.py
"$PY" -B -X utf8 check_numbers.py --scan ../MONITOR_WRAPUP.md ../reports/D7_report.md
"$PY" -B -X utf8 boundary_check.py --card D7 --phase post
```

Environment: Python 3.11.9; verify_runtime pools: openblas 0.3.30 num_threads=6, openblas 0.3.30 num_threads=6; seed 20261036.

Boundary check: before/after hashes clean? yes (pre/post clean; only the 4 D1-allowed changes).
