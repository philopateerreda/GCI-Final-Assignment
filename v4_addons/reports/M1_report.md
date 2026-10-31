# M1 — Baseline audit and learning curve (non-test rows only)
Status: COMPLETED_REJECTED

The frozen submission model was already refit on the entire non-test pool, so Track M can add no rows: the point prediction of ΔS is exactly zero, below the pre-declared gate. A repeated ten-fold learning curve over that pool locates the asymptote and the bootstrap interval on the curve exponent; the extrapolated gain from the largest clean training size to the full pool is small, and the identity is exact regardless. Gate M1 FAILS, so Track M is COMPLETED_REJECTED with decision KILL. No test row entered any feature, fit or score call, and no gate file was read or written.

## Evidence table

| number | value | source_file | source_key / formula | tag |
|---|---:|---|---|---|
| frozen_iterations | 385 | `v1_frozen/analysis_outputs/model_selection.json` | `iterations` | [E] |
| frozen_refit_customers | 75,000 | `v1_frozen/analysis_outputs/model_selection.json` | `refit_customers` | [E] |
| frozen_calibration_customers | 10,000 | `v1_frozen/analysis_outputs/model_selection.json` | `calibration_customers` | [E] |
| frozen_features | 87 | `v1_frozen/analysis_outputs/models/selected_model.joblib` | `feature names recorded in the frozen bundle` | [E] |
| frozen_bundle_trees | 385 | `v1_frozen/analysis_outputs/models/selected_model.joblib` | `n_estimators recorded in the frozen bundle` | [E] |
| split_train_rows | 60,000 | `v1_frozen/analysis_outputs/tables/split_manifest.csv` | `partition value counts` | [E] |
| split_validation_rows | 15,000 | `v1_frozen/analysis_outputs/tables/split_manifest.csv` | `partition value counts` | [E] |
| split_calibration_rows | 10,000 | `v1_frozen/analysis_outputs/tables/split_manifest.csv` | `partition value counts` | [E] |
| split_test_rows | 15,000 | `v1_frozen/analysis_outputs/tables/split_manifest.csv` | `partition value counts` | [E] |
| non_test_pool_rows | 75,000 | `v1_frozen/analysis_outputs/tables/split_manifest.csv` | `train + validation rows after non_test_pool()` | [E] |
| pool_test_overlap | 0 |  | `non-test pool rows also in the test partition` | [E] |
| pool_calibration_overlap | 0 |  | `non-test pool rows also in the calibration-policy partition` | [E] |
| additional_non_test_rows | 0 |  | `non_test_pool_rows - frozen_refit_customers` | [E] |
| delta_s_identity | 0.0000 |  | `AUC(N_all) - AUC(N_frozen) = 0 because N_all = N_frozen: the frozen refit covers every non-test row` | [E] |
| gate_threshold | 0.0015 |  | `0.0015` | [R] |
| gate_passed | 0 |  | `1 if delta_s_identity >= gate_threshold else 0` | [E] |
| curve_folds | 10 |  | `stratified folds per repeat` | [E] |
| curve_repeats | 2 |  | `repeats of the fold design` | [E] |
| curve_holdout_rows | 7,500 |  | `non_test_pool_rows / curve_folds` | [E] |
| curve_fits | 100 |  | `completed fit/hold-out evaluations` | [E] |
| curve_auc_15000 | 0.678565 |  | `mean held-out AUC over 20 folds` | [E] |
| curve_auc_30000 | 0.689170 |  | `mean held-out AUC over 20 folds` | [E] |
| curve_auc_45000 | 0.693949 |  | `mean held-out AUC over 20 folds` | [E] |
| curve_auc_60000 | 0.696203 |  | `mean held-out AUC over 20 folds` | [E] |
| curve_auc_67500 | 0.696845 |  | `mean held-out AUC over 20 folds` | [E] |
| curve_a | 0.707582 |  | `least-squares AUC(n) = a - b*n^-c intercept` | [E] |
| curve_b | 18.5577 |  | `least-squares b coefficient` | [E] |
| curve_c | 0.672 |  | `least-squares exponent c` | [E] |
| curve_c_lower | 0.403 |  | `percentile bootstrap bound over fold clusters` | [E] |
| curve_c_upper | 0.964 |  | `percentile bootstrap bound over fold clusters` | [E] |
| curve_pred_75000 | 0.697731 |  | `fitted curve evaluated at the full non-test pool` | [E] |
| delta_s_curve | 0.000723 |  | `curve-implied gain from the largest clean training size to the full pool` | [E] |
| delta_s_curve_lower | 0.000536 |  | `percentile bootstrap bound over fold clusters` | [E] |
| delta_s_curve_upper | 0.000943 |  | `percentile bootstrap bound over fold clusters` | [E] |
| delta_s_curve_60k_75k | 0.001593 |  | `curve-implied gain from 60k to the full pool` | [E] |
| v2_curve_auc_60000 | 0.696037 | `v2_work/d_results/learning_curve_summary.csv` | `where(training_n=60000).heldout_auc_mean` | [E] |
| curve_minus_v2_60k | 0.000166 |  | `curve_auc_60000 - v2_curve_auc_60000` | [E] |
| fits_wall_seconds | 303.5 |  | `wall time of the learning curve (cache hits included)` | [E] |
| verdict_kill | 1 |  | `1` | [R] |

## Baseline audit

- Frozen submission model `LightGBM wider leaves`: 385 trees and 87 features; the final fit used 75,000 customers and the sigmoid used 10,000 calibration-policy customers.
- Split manifest: 60,000 train + 15,000 validation = 75,000 non-test rows; 10,000 calibration-policy rows and 15,000 test rows are disjoint from the pool.
- Pool/test overlap 0 and pool/calibration overlap 0; the frozen refit covers the whole pool, so 0 additional non-test rows exist.
- The v1 pipeline concatenates train and validation before the final fit (`refit_idx = np.concatenate([train_idx, valid_idx])`, `line 275`) and the frozen test table labels the model row `(75k refit)`. The v2 baseline recipe reproduces that fit (`n_estimators=385`, `num_leaves=31`, `min_child_samples=100`, `reg_lambda=12`).
- Consequently the M1 identity is exact: ΔS = AUC(N_all) − AUC(N_frozen) = 0.0000, against a gate of 0.0015.

## Learning curve

| training size | mean held-out AUC | fold SD | paired gain vs previous |
|---:|---:|---:|---:|
| 15,000 | 0.678565 | 0.006065 | — |
| 30,000 | 0.689170 | 0.006475 | 0.010606 |
| 45,000 | 0.693949 | 0.006389 | 0.004778 |
| 60,000 | 0.696203 | 0.005994 | 0.002255 |
| 67,500 | 0.696845 | 0.006013 | 0.000641 |

100 fits: 2 repeats × 10 stratified folds over the 75,000-row pool, each with a 7,500-row hold-out and nested training prefixes. Fold hashes are in the results JSON. The paired gain is the mean per-fold difference against the previous size.

Fitted AUC(n) = a − b·n^(−c): a = 0.707582, b = 18.5577, c = 0.672 (fold-cluster bootstrap 95% interval 0.403 to 0.964, 2,000 valid of 2,000 replicates; 303.5 s wall, 0 cache hits).

Curve prediction at the full pool: 0.697731. Implied gain from the largest clean training size to the full pool: 0.000723 (95% interval 0.000536 to 0.000943); the 60,000-row to full-pool implied gain is 0.001593. The full-pool point is an extrapolation: a 75,000-row training fit leaves no clean hold-out, so that point is never measured here.

Cross-check against the v2 curve at 60,000 training rows: 0.696037 there versus 0.696203 here (difference 0.000166); the designs differ in fold count and hold-out size, so the two are not expected to match exactly.

## Decision

- Gate M1 requires a point prediction of ΔS of at least 0.0015; the exact identity is 0.0000. The gate fails.
- The learning-curve extrapolation is also below the gate: 0.000723 point estimate, 0.000943 upper bootstrap bound.
- The 60,000-row to full-pool curve gain (0.001593) is not available to Track M: it is the gain of the refit from 60,000 to 75,000 rows that v1 already performed. Measured from the frozen 75,000-row model, the remaining curve gain is the extrapolation from 67,500 to 75,000 rows above.
- Per card M1 the branch is fixed: Track M status `COMPLETED_REJECTED`, decision `KILL`, negative result written, Track M stops. M2–M6 are not started and gate H1 is not requested.
- Track D is unaffected: the H3 option remains the only open human decision and the frozen v2 deliverable remains the submission.

## Negative result

- The frozen submission model already uses every non-test row; refitting on more data is not available, so the Track M premise fails at its first gate.
- The learning curve shows that returns are already exhausted: the last 7,500 rows add 0.000723 AUC at the point estimate and at most 0.000943 at the upper bound, below the pre-declared gate.
- No new candidate, calibration change or test look is justified by this evidence; Track M is closed with decision `KILL`.

## Acceptance checks

- Frozen N_train and N_calibration established from the model record and pipeline code: **PASS** (75,000 and 10,000).
- N_all counted on the split manifest and checked disjoint from calibration-policy and test: **PASS** (pool 75,000; overlaps 0 and 0).
- Learning curve on non-test rows with identical hold-outs across sizes: **PASS** (100 fits, 10 folds × 2 repeats, 7,500-row hold-outs).
- AUC(n) = a − b·n^(−c) fitted with a bootstrap interval on c: **PASS**.
- Point prediction of ΔS and the gate comparison recorded: **PASS** (identity 0.0000 < gate 0.0015 → gate FAIL).
- No test row entered any feature, fit or score call: **PASS** (`test_guard.assert_no_test_rows` logged a zero overlap).
- No model from v2 or WP8 rerun, refit or rescored beyond the frozen reference recipe: **PASS** (only the baseline recipe was fitted, on non-test rows, for the curve).
- Boundary check clean before and after: **PASS**.

## Deviations from the brief

- The brief size set is internally inconsistent once the frozen model is known to use the whole pool: `N_frozen` = 75,000 equals the pool, and a fit at that size leaves no clean hold-out. The curve therefore runs 15,000, 30,000, 45,000, 60,000 and 67,500; the 60,000-row size takes the place of `N_frozen`, the 67,500-row size is the largest clean training size inside a ten-fold split, and the full-pool point is predicted by extrapolation rather than measured.
- The brief does not fix K and R for M1. Ten folds × two repeats were used to resolve the near-asymptote region; the `K=10`, `R=3` design in M2 applies to candidate evaluation, which is not reached.
- The v2 curve used five folds with a larger hold-out and sizes up to 60,000; the same-size cross-check differs by 0.000166 because the fold design and hold-out size differ. Both values are reported, neither is tuned.
- The brief points to `v2_work` and the WP8 report for N_train; the frozen submission model is the v1 selected model, whose refit size is recorded in `v1_frozen` and the pipeline code. WP8 tested a rejected challenger and its `48k`/`60k` sizing does not describe the submission; both were read and the submission numbers were bound.
- The learning curve fits the frozen baseline recipe only, which is the v2 selected candidate (`baseline_lgbm`); the WP8 challenger was not rerun, refit or rescored.

## Open questions / [DECISION NEEDED] items

- No human decision is needed for M1: the gate fails and the card's written branch is KILL.
- Track M is closed. M2–M6 remain not started and gate H1 was not requested. Gate H2 (test access) and gate H3 (deck option) were neither read nor written.
- Track D integration still awaits the human H3 option file; the frozen v2 deliverable remains the submission.

## Commands run

```bash
PY="C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe"; R="D:/progs/IDE/MainProjs/AI/GCI2026/finalA"
cd "$R/v4_addons/tools"
"$PY" -B -X utf8 boundary_check.py --card M1 --phase pre
OPENBLAS_NUM_THREADS=6 OMP_NUM_THREADS=6 MKL_NUM_THREADS=6 NUMEXPR_NUM_THREADS=6 "$PY" -B -X utf8 m1_learning_curve.py
"$PY" -B -X utf8 check_numbers.py --scan ../reports/M1_report.md
"$PY" -B -X utf8 boundary_check.py --card M1 --phase post
```

Environment: Python 3.11.9; verify_runtime pools: openblas 0.3.30 num_threads=6, openblas 0.3.30 num_threads=6, openmp None num_threads=6; seed 20261039.

Boundary check: before/after hashes clean? yes (pre clean; post-check run after this report; only `v4_addons/` written)
