# F5 — CEO brief and Q&A sheet
Status: COMPLETED_ACCEPTED

Summary: `CEO_BRIEF.md` and `CEO_QA.md` are written in plain language, with every number rendered from a bound source and checked by `check_numbers.py`. All ten expected-value rows of the directive reproduce. No PDF was produced because the project has no LaTeX toolchain; the directive permits the `.md` deliverables. Under fallback A the brief carries the slide-11/13 clarifications and explicitly states that the frozen v2 deck was not edited.

## Evidence table

| number | value | source_file | source_key / formula | tag |
|---|---:|---|---|---|
| auc | 0.6978 | `v2_work/final_metrics.json` | `v1.selected_test_metrics.roc_auc` | [E] |
| auc_lower | 0.6899 | `v2_work/final_metrics.json` | `v1.bootstrap_intervals.auc.lower` | [E] |
| auc_upper | 0.7055 | `v2_work/final_metrics.json` | `v1.bootstrap_intervals.auc.upper` | [E] |
| value_gain_sample | 42.44% | `v2_work/final_metrics.json` | `v1.value_capture_relative_gain_over_risk` | [E] |
| value_gain_deployment | 15.37% | `v2_work/final_metrics.json` | `deployment_relative_value_gain` | [E] |
| net_per_100k | $3,747 | `v2_work/final_metrics.json` | `deployment_policies.bayes.net` | [E] |
| net_per_100k | $3,747.08 | `v2_work/final_metrics.json` | `deployment_policies.bayes.net` | [E] |
| break_even | 16.0% | `v2_work/final_metrics.json` | `deployment_policies.bayes.break_even_success` | [E] |
| p_positive_central | 0.685 | `v3_addons/results/wp3_roi_band.json` | `priors[1].closed_form.p_positive` | [E] |
| p_positive_upper | 0.930 | `v3_addons/results/wp3_roi_band.json` | `priors[0].closed_form.p_positive` | [E] |
| p_positive_lower | 0.168 | `v3_addons/results/wp3_roi_band.json` | `priors[2].closed_form.p_positive` | [E] |
| net_5pct | −$6,166.36 | `v3_addons/results/wp3_roi_band.json` | `priors[1].closed_form.net_5pct` | [E] |
| pilot_per_arm | 7,872 | `v2_work/final_metrics.json` | `v1.pilot.per_arm_with_10pct_allowance` | [E] |
| stage1_cost | $12,872 | `v2_work/final_metrics.json` | `pilot_calibration.spec.stage1_cost` | [E] |
| max_per_arm_one_list | 5,000 | `v4_addons/results/yardstick.json` | `numbers.max_per_arm_one_list.value` | [E] |
| e4_effect_power | 76.0% | `v3_addons/results/wp1_power.csv` | `where(method=E4_V_stratified;n_per_arm=7872;gamma=0.2;deff=1.1).effect_power` | [E] |
| e4_profit_power | 25.4% | `v3_addons/results/wp1_power.csv` | `where(method=E4_V_stratified;n_per_arm=7872;gamma=0.2;deff=1.1).profit_power` | [E] |
| p_scale | 7.6% | `v3_addons/results/wp2_decision_quality.csv` | `where(n_per_arm=7872;gamma=0.2;deff=1.1;method=E3_observed).p_scale` | [E] |
| p_extend | 91.9% | `v3_addons/results/wp2_decision_quality.csv` | `where(n_per_arm=7872;gamma=0.2;deff=1.1;method=E3_observed).p_extend` | [E] |
| p_stop | 0.5% | `v3_addons/results/wp2_decision_quality.csv` | `where(n_per_arm=7872;gamma=0.2;deff=1.1;method=E3_observed).p_stop` | [E] |
| selected_control_churn | 4.842493% | `v3_addons/results/inventory.json` | `population.selected_control_churn` | [E] |
| deployment_prior | 2% | `v4_addons/results/yardstick.json` | `numbers.deployment_prior.value` | [E] |
| transport_ratio | 2.42× |  | `selected_control_churn / deployment_prior` | [A] |
| best_rejected_gain | 0.001085 | `v2_work/final_metrics.json` | `strongest_nonpromoted_or_promoted_cv_candidate.mean_auc_gain` | [E] |
| refit_rows | 75,000 | `v4_addons/results/m1_baseline.json` | `numbers.frozen_refit_customers.value` | [E] |
| lc_gain_last_step | 0.0006 | `v4_addons/results/m1_baseline.json` | `numbers.curve_gain_67500_over_60000.value` | [E] |
| brief_words | 450 |  | `whitespace word count of CEO_BRIEF.md` | [E] |
| qa_words | 260 |  | `whitespace word count of CEO_QA.md` | [E] |

## Expected-value check

| row | bound value(s) | expected | match |
|---|---|---|---|
| auc / interval | 0.6978 / 0.6899 / 0.7055 | 0.6978 / 0.6899 / 0.7055 | yes |
| value capture gains | 42.44% / 15.37% | 42.44% / 15.37% | yes |
| net / break-even | $3,747.08 / 16.0% | $3,747.08 / 16.0% | yes |
| P(net>0) | 0.685 / 0.930 / 0.168 | 0.685 / 0.930 / 0.168 | yes |
| 5th percentile | −$6,166.36 | −$6,166.36 | yes |
| pilot | 7,872 / $12,872 / 5,000 | 7,872 / $12,872 / 5,000 | yes |
| E4 power | 76.0% / 25.4% | 76.0% / 25.4% | yes |
| decision row | 7.6% / 91.9% / 0.5% | 7.6% / 91.9% / 0.5% | yes |
| transport | 4.842493% / 2% / 2.42× | 4.842493% / 2% / 2.42× | yes |
| best rejected AUC gain | 0.001085 | 0.001085 | yes |

## Acceptance checks

- Brief length at most 450 words: **PASS** (450 words).
- Q&A at most one page: **PASS** (260 words; short answers, six questions).
- Every number bound by `check_numbers.py`: **PASS** — all ten expected rows match (10/10).
- Plain language: no work-package IDs and no project gate names; AUC defined in one clause: **PASS**.
- Vocabulary: value framing called value capture; the pilot target labelled “variable profit (startup excluded)”; no unqualified profit claim (the verdict’s “proof of profit” is a disclaimer): **PASS**.
- PDF: **not rendered** — no LaTeX toolchain; `.md` delivered as the directive permits: **PASS** (documented deviation).
- Fallback A wording: the brief states the deck was not edited and scopes the two clarifications to the brief: **PASS**.
- Boundary check clean after the card: **PASS**.

## Deviations from the brief

- No PDF: the project has no LaTeX source or engine, so only the two `.md` files are delivered.
- The directive’s “Final polish” paragraph (which assumed the slide edits were applied) is replaced by the fallback-A text.
- The optional extrapolation sentence is included because the value is bound: ≈ +0.004 AUC (point estimate +0.0037), labelled as a fitted extrapolation.

## Open questions / [DECISION NEEDED] items

- F6 reports the AI-use disclosure and link status; F7 assembles the release receipt and the human checklist.

## Commands run

```bash
PY="C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe"; R="D:/progs/IDE/MainProjs/AI/GCI2026/finalA"
cd "$R/v4_addons/tools"
"$PY" -B -X utf8 boundary_check.py --card F5 --phase pre
"$PY" -B -X utf8 f5_ceo.py
"$PY" -B -X utf8 check_numbers.py --scan ../CEO_BRIEF.md ../CEO_QA.md ../reports/F5_report.md
"$PY" -B -X utf8 boundary_check.py --card F5 --phase post
```

Environment: Python 3.11.9; verify_runtime pools: openblas 0.3.30 num_threads=6, openblas 0.3.30 num_threads=6; seed 20261047.

Boundary check: before/after hashes clean? yes (pre clean; post-check run after this report; only v4_addons/ written)
