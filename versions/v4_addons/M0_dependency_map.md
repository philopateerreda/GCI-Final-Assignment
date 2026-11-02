# M0 — regeneration dependency map
Status: COMPLETED_ACCEPTED

**Verdict: GO.** The v2 metric chain is drivable by an alternate `a_selected_test.csv`: replaying the cached frozen probabilities regenerated the A layer byte-for-byte (10 of 10 artifacts) and re-emitted `final_metrics.json` byte-for-byte (26 top-level keys, 0 differing). Estimated regeneration effort: 1.5 days [A]. No model was fitted or scored; every replay used cached probabilities.

## Pipeline map

| layer | entry | input | outputs |
|---|---|---|---|
| A — policy comparison | `workstream_a.py` (`analyze`) | `a_selected_{partition}.csv` + frozen split manifest | `a_policies_test.csv`, `a_profit_curves_test.csv`, `a_overlap_test.csv`, `a_dual_valuation_test.csv`, `a_value_proxy_sensitivity_test.csv`, `a_bootstrap_test.csv`, `a_intervals_test.csv`, `a_calibration_uncertainty_test.csv`, `a_summary_test.json` |
| B — pilot diagnostics | `workstream_b.py` (same file, `workstream_b.py:244`) | `a_selected_test.csv` + `b_design.json` | `b_power_test.csv`, `b_queues_test.csv`, `b_cells_test.csv`, `b_assignments_test.csv`, `b_summary_test.json` |
| C — governance audit | `workstream_c.py` (same file, `workstream_c.py:145`) | `a_selected_test.csv` + ceiling results | `c_test/c_summary.json`, `c_test/c_subgroup_robustness.csv`, `c_test/c_equity.csv` |
| metrics | `final_metrics.py` (`build`) | A/B/C summaries, scored `d_results/`, frozen protocol | `final_metrics.json` |
| charts | `generate_visuals.py` | `final_metrics.json` + cached test frame | figures, `chart_claims.json`, `chart_numeric_sources.json` |
| ledger | `build_claim_ledger.py` | `ledger_bindings.json`, chart sources, deck | `analysis_outputs/claims_ledger.csv` |

The batch driver `run_frozen_batch.py` sequences A → B → C → metrics and enforces the freeze; `build_v2_canonical.py` assembles the canonical notebook from the same modules. 11 entry-point files are hash-recorded in `results/m0_feasibility.json`.

## Replay evidence

- Maximum absolute difference between the rebuilt `p_s` and the cached `a_selected_test.csv`: 0.0 over 15,000 rows.
- `final_metrics.json`: byte-identical (1 flag), 26 top-level keys, 0 differing, 0.23 s.
- A layer: 10 of 10 artifacts byte-identical, 16.41 s including the bootstrap and calibration-uncertainty refits.
- CSV parser caveat: pandas' default parser changes 3,073 of 15,000 `p_s` values by one ulp; every replay read uses `float_precision='round_trip'`. Without it the A-layer CSVs differ in the last digits.

## Dependency rule

A ledger row is **regeneration-dependent** when its displayed value is recomputed by the chain from per-row probabilities or selections: the deployment policy table and its intervals, prevented churners, retained revenue, the heatmap net cells, prior-stress net cells, pilot queue composition, and the observed chart values.

Rows that describe the frozen search or the v1 deliverable are **narrative**: the v1 headline block and the frozen-search candidate, proxy and power rows. Regeneration neither recomputes nor invalidates them; an admitted model would add a new claim, not overwrite the v1 record.

Everything else is **unaffected**: protocol constants, financial assumptions, design constants, bibliography, axis ticks and ordinals.

Of the 278 ledger rows, 52 are regeneration-dependent, 25 are narrative and 201 are unaffected. The dependent rows sit on 7 slides: 40 bound to `final_metrics.json` and 12 observed chart values.

## Regeneration-dependent rows by slide

| slide | rows |
|---|---:|
| 2 | 1 |
| 5 | 9 |
| 8 | 3 |
| 9 | 6 |
| 10 | 12 |
| 11 | 7 |
| 12 | 14 |

## Every regeneration-dependent ledger number

Exact values are the ledger `exact_value` column (raw, unscaled); displayed text is quoted from the frozen ledger.

| claim | slide | source | displayed | exact value |
|---|---:|---|---|---:|
| C0005 | 2 | `v2_work/final_metrics.json::deployment_policies.bayes.net` | `3.7k` | 3747.082455665277 |
| C0060 | 9 | `v2_work/final_metrics.json::deployment_policies.bayes.value_recall` | `29.5%` | 0.2951286030895049 |
| C0061 | 9 | `v2_work/final_metrics.json::deployment_policies.value.value_recall` | `15.0%` | 0.1502562153110172 |
| C0062 | 9 | `v2_work/final_metrics.json::deployment_policies.risk.value_recall` | `25.6%` | 0.255800562523395 |
| C0063 | 9 | `v2_work/final_metrics.json::deployment_relative_value_gain` | `+15.4%` | 0.1537449338584349 |
| C0064 | 9 | `v2_work/final_metrics.json::deployment_intervals.relative_value_gain_vs_risk.lower` | `+11.3%` | 0.1126109293543485 |
| C0065 | 9 | `v2_work/final_metrics.json::deployment_intervals.relative_value_gain_vs_risk.upper` | `+19.7%` | 0.196668463579351 |
| C0072 | 10 | `v2_work/final_metrics.json::pilot_test.queues.0.raw_count` | `582` | 582.0 |
| C0073 | 10 | `v2_work/final_metrics.json::pilot_test.queues.0.mean_bill` | `68.7` | 68.74004858077647 |
| C0074 | 10 | `v2_work/final_metrics.json::pilot_test.queues.0.share_at_risk_value` | `23.4%` | 0.2340620297453866 |
| C0075 | 10 | `v2_work/final_metrics.json::pilot_test.queues.1.raw_count` | `266` | 266.0 |
| C0076 | 10 | `v2_work/final_metrics.json::pilot_test.queues.1.mean_bill` | `59.7` | 59.661242760755975 |
| C0077 | 10 | `v2_work/final_metrics.json::pilot_test.queues.1.share_at_risk_value` | `10.4%` | 0.1040392484440546 |
| C0078 | 10 | `v2_work/final_metrics.json::pilot_test.queues.2.raw_count` | `791` | 791.0 |
| C0079 | 10 | `v2_work/final_metrics.json::pilot_test.queues.2.mean_bill` | `62.9` | 62.86842695788842 |
| C0080 | 10 | `v2_work/final_metrics.json::pilot_test.queues.2.share_at_risk_value` | `30.7%` | 0.3067027654002414 |
| C0081 | 10 | `v2_work/final_metrics.json::pilot_test.queues.3.raw_count` | `866` | 866.0 |
| C0082 | 10 | `v2_work/final_metrics.json::pilot_test.queues.3.mean_bill` | `64.7` | 64.67478199897347 |
| C0083 | 10 | `v2_work/final_metrics.json::pilot_test.queues.3.share_at_risk_value` | `35.5%` | 0.3551959564103172 |
| C0087 | 11 | `v2_work/final_metrics.json::deployment_policies.bayes.net` | `3.7k` | 3747.082455665277 |
| C0088 | 11 | `v2_work/final_metrics.json::deployment_policies.bayes.contacts` | `9,985` | 9984.92153410634 |
| C0098 | 11 | `v2_work/final_metrics.json::deployment_intervals.net.lower` | `2.8k` | 2761.36950443581 |
| C0099 | 11 | `v2_work/final_metrics.json::deployment_intervals.net.upper` | `4.7k` | 4660.637082299275 |
| C0100 | 11 | `v2_work/final_metrics.json::deployment_prevented` | `95` | 95.27908540685944 |
| C0101 | 11 | `v2_work/final_metrics.json::deployment_retained_revenue` | `31.2k` | 31220.00664961936 |
| C0102 | 11 | `v2_work/final_metrics.json::deployment_policies.bayes.actual_gross` | `18.7k` | 18732.003989771616 |
| C0104 | 12 | `v2_work/final_metrics.json::heatmap.0.net` | `−5.6` | -5618.919539220531 |
| C0105 | 12 | `v2_work/final_metrics.json::heatmap.1.net` | `−15.6` | -15603.84107332687 |
| C0106 | 12 | `v2_work/final_metrics.json::heatmap.2.net` | `−45.6` | -45558.605675645886 |
| C0107 | 12 | `v2_work/final_metrics.json::heatmap.3.net` | `+3.7` | 3747.082455665277 |
| C0108 | 12 | `v2_work/final_metrics.json::heatmap.4.net` | `−6.2` | -6237.839078441062 |
| C0109 | 12 | `v2_work/final_metrics.json::heatmap.5.net` | `−36.2` | -36192.60368076008 |
| C0110 | 12 | `v2_work/final_metrics.json::heatmap.6.net` | `+13.1` | 13113.084450551089 |
| C0111 | 12 | `v2_work/final_metrics.json::heatmap.7.net` | `+3.1` | 3128.162916444748 |
| C0112 | 12 | `v2_work/final_metrics.json::heatmap.8.net` | `−26.8` | -26826.60168587427 |
| C0122 | 12 | `v2_work/final_metrics.json::deployment_policies.bayes.break_even_contact_cost` | `1.38` | 1.3752741013403111 |
| C0123 | 12 | `v2_work/final_metrics.json::deployment_policies.bayes.break_even_success` | `16.0%` | 0.1599927219990843 |
| C0127 | 12 | `v2_work/final_metrics.json::prior_stress.0.net` | `−5.6k` | -5558.443445736175 |
| C0128 | 12 | `v2_work/final_metrics.json::prior_stress.1.net` | `+3.7k` | 3747.082455665277 |
| C0129 | 12 | `v2_work/final_metrics.json::prior_stress.2.net` | `+30.7k` | 30740.05363149663 |
| C0211 | 8 | `v2_work/chart_numeric_sources.json::18.value` | `0.619` | 0.6193292385072477 |
| C0212 | 8 | `v2_work/chart_numeric_sources.json::19.value` | `0.698` | 0.6978109022411016 |
| C0213 | 8 | `v2_work/chart_numeric_sources.json::20.value` | `0.500` | 0.5 |
| C0232 | 5 | `v2_work/chart_numeric_sources.json::39.value` | `1,774` | 1774.0 |
| C0233 | 5 | `v2_work/chart_numeric_sources.json::40.value` | `53.9` | 53.85016444911885 |
| C0234 | 5 | `v2_work/chart_numeric_sources.json::41.value` | `6.6%` | 0.0659507289078484 |
| C0235 | 5 | `v2_work/chart_numeric_sources.json::42.value` | `731` | 731.0 |
| C0236 | 5 | `v2_work/chart_numeric_sources.json::43.value` | `78.7` | 78.71660564863997 |
| C0237 | 5 | `v2_work/chart_numeric_sources.json::44.value` | `2.8%` | 0.0280273565068158 |
| C0238 | 5 | `v2_work/chart_numeric_sources.json::45.value` | `1,117` | 1117.0 |
| C0239 | 5 | `v2_work/chart_numeric_sources.json::46.value` | `24.6` | 24.572827043571245 |
| C0240 | 5 | `v2_work/chart_numeric_sources.json::47.value` | `4.9%` | 0.0493181304266715 |

## Narrative rows (not recomputed by regeneration)

18 v1 headline rows, 3 frozen-search candidate rows, 3 proxy-recoverability rows and 1 pilot-power row. They stay as the v1/WP8 record unless a human rewrites the narrative.

| claim | slide | source |
|---|---:|---|
| C0001 | 1 | `v1_frozen/analysis_outputs/summary.json::audit.rows` |
| C0003 | 2 | `v1_frozen/analysis_outputs/summary.json::value_capture_relative_gain_over_risk` |
| C0004 | 2 | `v1_frozen/analysis_outputs/summary.json::ranking_top10.Risk only.contact_fraction` |
| C0020 | 4 | `v1_frozen/analysis_outputs/summary.json::audit.rows` |
| C0021 | 4 | `v1_frozen/analysis_outputs/summary.json::audit.columns` |
| C0022 | 4 | `v1_frozen/analysis_outputs/summary.json::audit.sample_churn_rate` |
| C0025 | 4 | `v1_frozen/analysis_outputs/summary.json::audit.negative_equipment_age` |
| C0034 | 7 | `v1_frozen/analysis_outputs/summary.json::test_customers` |
| C0039 | 7 | `v2_work/final_metrics.json::strongest_nonpromoted_or_promoted_cv_candidate.mean_auc_gain` |
| C0040 | 7 | `v2_work/final_metrics.json::strongest_nonpromoted_or_promoted_cv_candidate.corrected_auc_lower` |
| C0041 | 7 | `v2_work/final_metrics.json::strongest_nonpromoted_or_promoted_cv_candidate.corrected_auc_upper` |
| C0043 | 7 | `v2_work/final_metrics.json::proxy_recoverability.0.auc` |
| C0044 | 7 | `v2_work/final_metrics.json::proxy_recoverability.1.auc` |
| C0045 | 7 | `v2_work/final_metrics.json::proxy_recoverability.2.auc` |
| C0048 | 8 | `v1_frozen/analysis_outputs/summary.json::selected_test_metrics.roc_auc` |
| C0049 | 8 | `v1_frozen/analysis_outputs/summary.json::test_customers` |
| C0051 | 8 | `v1_frozen/analysis_outputs/summary.json::bootstrap_intervals.auc.lower` |
| C0052 | 8 | `v1_frozen/analysis_outputs/summary.json::bootstrap_intervals.auc.upper` |
| C0053 | 8 | `v1_frozen/analysis_outputs/summary.json::selected_test_metrics.accuracy` |
| C0054 | 8 | `v1_frozen/analysis_outputs/summary.json::selected_test_metrics.brier` |
| C0067 | 9 | `v1_frozen/analysis_outputs/summary.json::ranking_top10.Risk × recurring value.customers_contacted` |
| C0068 | 9 | `v1_frozen/analysis_outputs/summary.json::ranking_top10.Risk × recurring value.recurring_value_recall` |
| C0069 | 9 | `v1_frozen/analysis_outputs/summary.json::ranking_top10.Risk only.recurring_value_recall` |
| C0070 | 9 | `v1_frozen/analysis_outputs/summary.json::value_capture_relative_gain_over_risk` |
| C0137 | 13 | `v2_work/final_metrics.json::pilot_calibration.simulated_required_enrolled_per_arm_grid.adjusted_contribution` |

## Notebook and PDF

The notebook (`philopateer.ipynb`) replays the v1 frozen outputs and is not driven by the v2 probability file; frozen cells are not edited. The PDF carries the same claims as the deck, so the regenerated set above applies to both.

## Manual regeneration steps

1. Copy `v2_work/` to `v4_addons/regen/v2_work/` so the frozen tree and the once-only test guards stay untouched.
2. Replace `a_selected_test.csv` with the candidate model's per-row file (same columns). This is an M5 output: it requires ADOPT-CONFIRMED and gate H2, and is not authorized by M0.
3. Regenerate the A layer with `workstream_a.analyze(cal, frame, data, splits, 'test')`; 10 of 10 artifacts were reproduced exactly in replay.
4. Regenerate B and C with `--partition test`; both read `a_selected_test.csv`. Their once-only guards pass only in the copy.
5. Re-emit `final_metrics.json` with `final_metrics.build()`.
6. Regenerate the charts with `generate_visuals.py`, then the ledger with `build_claim_ledger.py`.
7. Diff the 278-row ledger against the frozen file; 52 rows are expected to move.
8. Apply Option R to the deck and PDF only after gate H3.

Read every `a_selected_*.csv` with `float_precision='round_trip'`; the default parser shifts 3,073 values by one ulp and breaks byte-exactness. Effort: 1.5 days [A].

## What M0 does not authorize

- No new model was fitted or scored; no test row was used for fitting, scoring or selection. The replay read cached probabilities only and is logged through `test_guard.log_replay`.
- GO is a pipeline verdict, not a model verdict: the M1 sample-size gate still decides whether Track M continues, and the M2 preregistration still needs gate H1.
