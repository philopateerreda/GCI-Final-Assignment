# WP5 — Label-shift EM monitor and alternate non-test break-even trigger
Status: PARTIAL

Inputs:
- [E] `C:/Users/FGstore/.qoder/tmp/D--progs-IDE-MainProjs-AI-GCI2026-finalA/attachments/3462e263-cc13-4104-9c41-44f49963bbaa/4ec2074d-b034-4447-85ba-967f007db8e9.txt` — SHA-256 `a86cbb9698f01401acd2d7b10877355c4b9703ec15f43b7f80361fae3f89dda9`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/analysis_outputs/feature_manifest.json` — SHA-256 `8e0560cedab891acfea8b440b5d7f28516de1e3adc5b06899a442dd8d07fd067`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/analysis_outputs/model_selection.json` — SHA-256 `62e17913b8e7bf7bf1ac8fdd4556d242b524c884a0e929352c2b9e3bb5e9acc3`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/analysis_outputs/source_manifest.json` — SHA-256 `60861fb36607bcf143e313ca94390a67eb38b90c8b431144bb6f8cdb5156686a`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/references.txt` — SHA-256 `b12fb18aafc83e2d599e15d04c689ee5cd85c10082c1761ab0c6f1d01606d361`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/telecom/Record.csv` — SHA-256 `5bd563bb77b357920832510b78d6842060d928cb5de8c0aaf79aa2a647e2271a`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v1_frozen/analysis_outputs/models/selected_model.joblib` — SHA-256 `8a59fe9ac8c2eafb85c442fa1531035399aeecc6530a4b6489914385ecedfa3c`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v1_frozen/analysis_outputs/tables/split_manifest.csv` — SHA-256 `4caefcbed46a834f89cfbf21387f78555e601b43a8cee81d1637c786fb0a21b3`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/a_calibrator.joblib` — SHA-256 `c2cb492d958af024a0b06f7f206282835c1e857d1e9fbb7ed2df138ccdf9ae60`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/a_selected_calibration.csv` — SHA-256 `fa0ee67c5b94431e5313633219c04c8c4c248944564659e06007e0a2aff25648`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/a_spec.json` — SHA-256 `2f258d7d0ff9360d0ff0673abcb8c41e5c6462b2181d8d09dc5e86b4be5c8431`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/common.py` — SHA-256 `c68e6bcd81a24ae6960474ea537c4574fd0139fd83126fae0a853275611b0de7`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/d_results/oof/baseline_lgbm_r0_f0.npz` — SHA-256 `7c95f578448d7cc565fe698b02d6d691818b9c072099ce3d712513a04d1c22cd`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/d_results/oof/baseline_lgbm_r0_f1.npz` — SHA-256 `ab8bdbf05930676d8a99a03c8cac339bf70894528063f90f2730f597d51cead7`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/d_results/oof/baseline_lgbm_r0_f2.npz` — SHA-256 `261e411d43e57bc07e2cea4478ea5ca14eed652d7a504cb2a92bbea2f4e2f1b8`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/d_results/oof/baseline_lgbm_r0_f3.npz` — SHA-256 `3e686c9c9e28ab042a2537c314aefef2dbc05b7c14bde743e4690ea621e0dd50`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/d_results/oof/baseline_lgbm_r0_f4.npz` — SHA-256 `c7ef34ff72ddc81ff7c7f5b9125a3958583c40978121f0dd43cafb6e46ff10cc`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/d_results/oof/baseline_lgbm_r1_f0.npz` — SHA-256 `47298f1db1f8e758d57f7f9a777ccd1c2d5bcf59f913c914ed9f970755e6f453`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/d_results/oof/baseline_lgbm_r1_f1.npz` — SHA-256 `a0f96c7b7d0af44a3332c39f6c41d35cbe17dc3505f5a57d3681135b1b9ea848`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/d_results/oof/baseline_lgbm_r1_f2.npz` — SHA-256 `96066024ef34837f2aa3b640a8ab705100ceb1d46ba43e51cfc2338f9ce09a9d`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/d_results/oof/baseline_lgbm_r1_f3.npz` — SHA-256 `d552473bfe1d333afd55a9f77a7e87de172273218c9181dbbf3f0ce1fc071636`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/d_results/oof/baseline_lgbm_r1_f4.npz` — SHA-256 `4f0fe7e92f48e7adc6aeb92290559dbed0ce34386ca3f2594df20f326d9e14e7`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/final_metrics.json` — SHA-256 `1d14a4fea10ab391631379f82cd6a82e5a65ede4f01db5b540c9aec3612eea1e`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v2_work/workstream_a.py` — SHA-256 `b1ccdd6d40eab51961498ff39c0522f4df57b1d0cd4309aa5b509fc30a3434b8`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/reports/WP3_report.md` — SHA-256 `b491ba1f9b986d1585d852dfcd9d0c2de2380b8c3f6b9cace1299c6b2c2111a5`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/reports/WP4_report.md` — SHA-256 `169cb1c6f36d1f51ead1122e3127d83b04a51091f6f80074ff1c890c9741cf00`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/wp3_roi_band.json` — SHA-256 `96aa9a75869c53079e1442a26f1f3d08f5261d735e61a5195a658955843a5dd1`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/wp4_protocol.json` — SHA-256 `1fd31cc4461349db720ba88de079a0f0f7d15f3963b283b121af6e7af77676e9`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/wp5_tests.json` — SHA-256 `98f28360681b04f3dc74293f41208da88a2e7b9aa4de0ea5e3b586787f15c66b`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/src/common.py` — SHA-256 `5522fe7e7c49f945db5bd12bff6b850652ee12b002014a64f44217b01d13db0d`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/src/png_drafts.py` — SHA-256 `4c9a2135d01750409d1d3be20d3cef404385dcdddf5306d0dcde5b746c0069c8`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/src/reporting.py` — SHA-256 `189d0c2ebcb7616746332e56d568e180bd364346f0422ae1c20712dbdc4f4479`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/src/wp5_labelshift.py` — SHA-256 `c5d7df3f0e47795effc220aa35646e4d6f0d9f4ce018545cc273eca5acbc7f0a`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/wp5_calibration_oof.csv` — SHA-256 `88e58cc3c95e7dc65760f16f66e751a229e7263a27db9b1729c29e3e6ef68194`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/wp5_calibration_oof.json` — SHA-256 `a19d7ecadcc009b07806f3f78b7a4d016473656f0af545e5f102773d818f16b1`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/wp5_label_shift_raw.csv` — SHA-256 `e9a5a77a018d7fab5ed64ec54ef5d8771e4d29bef194a8c26139010d5555e904`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/wp5_label_shift_summary.csv` — SHA-256 `7ff830d7a52f0392d25a9dc66bba4498d62c21d3d9dcfd9cad19b2c99ca929f7`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/wp5_break_even_grid.csv` — SHA-256 `fea512bd2b631e217327c4cbad34101d343f74f55e2ec37411a4dfae11ab4612`.

Population / assumptions:
- [A] Generating pi and class-conditional heldout score pools define synthetic, conditional scenarios; stable P(x|y) and adequate calibration are unverified live.
- [E] 10k saved calibration_policy IDs only for five-fold calibration; 75k train/validation IDs only for planning; no new test-score/outcome computation.
- [E/A] Bootstrap conditions on the fitted empirical folded-score pool and original batch; it excludes calibration/base-model uncertainty.
- [A] New handsets/plans and other covariate shift may be misattributed to prior shift. The balanced 49.562% source prior is not live.
- [E] Percentile intervals include all 500 estimates; boundary atoms at 0/1 can cause nonregular coverage. Intervals with flagged solver failures are numerical diagnostics, not valid confidence claims.

Method (≤10 lines)
[E] Fit exactly five label-stratified SEED+5 heldout sigmoid calibrators with sum logistic loss and slope-only C=1000 penalty. Standardize each heldout logit from actual training prevalence to .49562, then clip its score. Draw Bin(n,pi) positives and uniform within-class score multinomials for 500 batches at each of 20 grid points. Run count-weighted original EM from .49562 (tol1e-8, cap1000); draw exactly 500 full-support batch multinomial bootstraps per original. Solve bootstrap concave likelihoods by endpoint KKT/bracketed Newton with bisection; retain all estimates/flags. Hash-bind complete grid NPZ/JSON checkpoints and final CSVs; evaluate generating-prior coverage. AST-extract only the six pure v2 functions for a .0001-step non-test planning break-even grid.

Results:
| [A] Generating pi | n | [E] Mean bias | Median error | RMSE | Coverage of generating pi | Median/max EM iters | Converged | Bootstrap failures |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.500% | 5,000 | 0.007594 | 0.005355 | 0.014105 | 91.800% | 831/1000 | 300/500 | 0 |
| 0.500% | 10,000 | 0.006368 | 0.005288 | 0.010739 | 90.800% | 922.5/1000 | 276/500 | 0 |
| 0.500% | 50,000 | 0.005676 | 0.005729 | 0.007231 | 76.400% | 947.5/1000 | 275/500 | 0 |
| 0.500% | 100,000 | 0.005480 | 0.005570 | 0.006370 | 57.400% | 953/1000 | 281/500 | 0 |
| 1.000% | 5,000 | 0.006048 | 0.004491 | 0.013899 | 95.200% | 735/1000 | 328/500 | 0 |
| 1.000% | 10,000 | 0.006725 | 0.006096 | 0.011614 | 91.800% | 698/1000 | 378/500 | 0 |
| 1.000% | 50,000 | 0.005313 | 0.005092 | 0.007136 | 78.000% | 730/1000 | 443/500 | 0 |
| 1.000% | 100,000 | 0.005548 | 0.005725 | 0.006477 | 59.600% | 714/1000 | 471/500 | 0 |
| 2.000% | 5,000 | 0.004531 | 0.004044 | 0.014862 | 94.200% | 519.5/1000 | 421/500 | 0 |
| 2.000% | 10,000 | 0.005777 | 0.005679 | 0.012128 | 90.200% | 503/1000 | 464/500 | 0 |
| 2.000% | 50,000 | 0.005048 | 0.004993 | 0.006863 | 82.800% | 510/915 | 500/500 | 0 |
| 2.000% | 100,000 | 0.005151 | 0.005213 | 0.006059 | 69.000% | 507/740 | 500/500 | 0 |
| 3.000% | 5,000 | 0.004749 | 0.005130 | 0.015062 | 95.400% | 406.5/1000 | 474/500 | 0 |
| 3.000% | 10,000 | 0.004584 | 0.005256 | 0.011806 | 92.200% | 402/1000 | 494/500 | 0 |
| 3.000% | 50,000 | 0.004860 | 0.004952 | 0.006777 | 83.200% | 403/562 | 500/500 | 0 |
| 3.000% | 100,000 | 0.004923 | 0.004849 | 0.005875 | 67.200% | 404/485 | 500/500 | 0 |
| 5.000% | 5,000 | 0.003395 | 0.002592 | 0.015941 | 93.600% | 306/1000 | 499/500 | 0 |
| 5.000% | 10,000 | 0.004252 | 0.004399 | 0.012038 | 93.000% | 298/571 | 500/500 | 0 |
| 5.000% | 50,000 | 0.004055 | 0.004083 | 0.006292 | 88.800% | 299/370 | 500/500 | 0 |
| 5.000% | 100,000 | 0.004234 | 0.004230 | 0.005528 | 76.800% | 300/348 | 500/500 | 0 |
[E/A] Alternate non-test planning pi* = 1.546417%; Approximate linear interpolation between adjacent .01-percentage-point planning-grid steps; not live.
[E] Frozen final_metrics quotations (not new test computations): pi=1%: net=-5558.443446; pi=2%: net=3747.082456; pi=5%: net=30740.053631.
[E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/wp5_calibration_oof.csv` — SHA-256 `88e58cc3c95e7dc65760f16f66e751a229e7263a27db9b1729c29e3e6ef68194`.
[E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/wp5_calibration_oof.json` — SHA-256 `a19d7ecadcc009b07806f3f78b7a4d016473656f0af545e5f102773d818f16b1`.
[E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/wp5_label_shift_raw.csv` — SHA-256 `e9a5a77a018d7fab5ed64ec54ef5d8771e4d29bef194a8c26139010d5555e904`.
[E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/wp5_label_shift_summary.csv` — SHA-256 `7ff830d7a52f0392d25a9dc66bba4498d62c21d3d9dcfd9cad19b2c99ca929f7`.
[E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/wp5_break_even_grid.csv` — SHA-256 `fea512bd2b631e217327c4cbad34101d343f74f55e2ec37411a4dfae11ab4612`.
[E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/figures/wp5_em_recovery.png` — SHA-256 `390f433d202da86091be5389b94f2bdddde38e437a6713a0a816789970daf178`.

Acceptance checks:
- [E] PASS: output_counts: {"actual_bootstrap_fits": 5000000, "actual_grid_rows": 20, "actual_raw_rows": 10000, "expected_bootstrap_fits": 5000000, "expected_grid_rows": 20, "expected_raw_rows": 10000, "passed": true}
- [E] FAIL: all_original_em_converged: {"actual_converged": 8604, "actual_total": 10000, "convergence_fraction": 0.8604, "passed": false}
- [E] PASS: no_bootstrap_solver_failures: {"actual_failures": 0, "actual_total": 5000000, "passed": true}
- [E] PASS: planning_crossing_found: {"actual": {"direction": "negative to positive", "lower_net": -59.08632254870827, "lower_prior": 0.0154, "method": "Approximate linear interpolation between adjacent .01-percentage-point planning-grid steps; not live.", "prior_star": 0.015464173262384629, "upper_net": 32.98679381331931, "upper_prior": 0.0155}, "passed": true}
- [E] FAIL: median_error_pi_02_n_10000: {"actual_abs_median_error": 0.005679280738133435, "actual_median_error": 0.005679280738133435, "passed": false, "replicates": 500, "strict_absolute_tolerance": 0.003, "tolerance_percentage_points": 0.3}
- [E] FAIL: median_error_pi_02_n_50000: {"actual_abs_median_error": 0.004992716446334887, "actual_median_error": 0.004992716446334887, "passed": false, "replicates": 500, "strict_absolute_tolerance": 0.003, "tolerance_percentage_points": 0.3}
- [E] FAIL: median_error_pi_02_n_100000: {"actual_abs_median_error": 0.005212748826710923, "actual_median_error": 0.005212748826710923, "passed": false, "replicates": 500, "strict_absolute_tolerance": 0.003, "tolerance_percentage_points": 0.3}

Deviations from brief:
[R] The two brief trigger rules overlap for intervals straddling pi*. Proposed HOLD priority is diagnostic-only, not a frozen protocol change.
[E] Break-even uses the exact v2 pure functions on alternate non-test baseline OOF scores; stored 1/2/5% test-based dollar scalars are quoted, not reproduced.
[E] M5 wording: standard derivation, simulation validation; source read status tracked separately. No WP5 verified-full-text claim.
[E] Bootstrap uses the equivalent concave likelihood Newton solver, not 1000-step EM; original EM retains the specified fixed-point tolerance/cap.
[E] All 10,000 original batches and 5,000,000 bootstrap fits finished; actual acceptance failures below downgrade this analysis to diagnostic-only.
[E] Failed check all_original_em_converged: {"actual_converged": 8604, "actual_total": 10000, "convergence_fraction": 0.8604, "passed": false}
[E] Failed check median_error_pi_02_n_10000: {"actual_abs_median_error": 0.005679280738133435, "actual_median_error": 0.005679280738133435, "passed": false, "replicates": 500, "strict_absolute_tolerance": 0.003, "tolerance_percentage_points": 0.3}
[E] Failed check median_error_pi_02_n_50000: {"actual_abs_median_error": 0.004992716446334887, "actual_median_error": 0.004992716446334887, "passed": false, "replicates": 500, "strict_absolute_tolerance": 0.003, "tolerance_percentage_points": 0.3}
[E] Failed check median_error_pi_02_n_100000: {"actual_abs_median_error": 0.005212748826710923, "actual_median_error": 0.005212748826710923, "passed": false, "replicates": 500, "strict_absolute_tolerance": 0.003, "tolerance_percentage_points": 0.3}

Claims now allowed:
[E/A] Conditional synthetic-batch recovery and generating-prior interval coverage at the stated grid; [R] diagnostic prior monitoring with day-60 label override and continuing Floor.

Claims still forbidden:
[R] Live drift detection, oracle prevalence, verified class-conditionals, causal profitability, calibration-inclusive intervals, a promoted trigger/protocol, or a verified M5 full-text formula.

Open questions for human: [E] None; integration remains a separate human decision.
