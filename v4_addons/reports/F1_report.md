# F1 — Resolve placeholders and final text
Status: COMPLETED_ACCEPTED

Summary: `INTEGRATION_DECISIONS_ADDENDUM.md` resolves every `[DECISION NEEDED]` item, fixes the final slide 11 and slide 13 text with the required glosses and term audit, and records the final ledger dry-run — unchanged from the D3 B′ dry-run, with Option A still reproducing the original hash. No deck, notebook, PDF or reference file was edited.

## Evidence table

| number | value | source_file | source_key / formula | tag |
|---|---:|---|---|---|
| pilot_per_arm | 7,872 | `v2_work/final_metrics.json` | `v1.pilot.per_arm_with_10pct_allowance` | [E] |
| treated_contact_cost | $1 | `v2_work/final_metrics.json` | `pilot_calibration.spec.cost_assumptions.treated_contact` | [E] |
| extension_variable_cost | $7,872 |  | `pilot_per_arm * treated_contact_cost` | [A] |
| startup_stage1 | $5,000 | `v2_work/final_metrics.json` | `pilot_calibration.spec.cost_assumptions.startup_stage1` | [E] |
| stage1_cost | $12,872 | `v2_work/final_metrics.json` | `pilot_calibration.spec.stage1_cost` | [E] |
| control_incremental_contact | $0 | `v2_work/final_metrics.json` | `pilot_calibration.spec.cost_assumptions.control_incremental_contact` | [E] |
| rows_retired_final | 0 | `v4_addons/results/d3_ledger_final.json` | `numbers.rows_retired_final.value` | [E] |
| rows_added_final | 18 | `v4_addons/results/d3_ledger_final.json` | `numbers.rows_added_final.value` | [E] |
| rows_changed_final | 0 | `v4_addons/results/d3_ledger_final.json` | `numbers.rows_changed_final.value` | [E] |
| rows_total_final | 296 | `v4_addons/results/d3_ledger_final.json` | `numbers.rows_total_final.value` | [E] |
| rows_total_d3_b_prime | 296 | `v4_addons/results/d3_ledger_final.json` | `numbers.rows_total_d3_b_prime.value` | [E] |
| len_before_slide11 | 151 | `v4_addons/results/d3_ledger_final.json` | `numbers.len_before_slide11.value` | [E] |
| len_after_slide11 | 289 | `v4_addons/results/d3_ledger_final.json` | `numbers.len_after_slide11.value` | [E] |
| len_delta_pct_slide11 | 91.4% | `v4_addons/results/d3_ledger_final.json` | `numbers.len_delta_pct_slide11.value` | [E] |
| len_before_slide13 | 219 | `v4_addons/results/d3_ledger_final.json` | `numbers.len_before_slide13.value` | [E] |
| len_after_slide13 | 941 | `v4_addons/results/d3_ledger_final.json` | `numbers.len_after_slide13.value` | [E] |
| len_delta_pct_slide13 | 329.7% | `v4_addons/results/d3_ledger_final.json` | `numbers.len_delta_pct_slide13.value` | [E] |
| slide13_growth_ratio | 4.3× | `v4_addons/results/d3_ledger_final.json` | `numbers.slide13_growth_ratio.value` | [E] |
| decision_needed_count | 0 | `v4_addons/results/d3_ledger_final.json` | `numbers.decision_needed_count.value` | [E] |
| unbound_tokens_count | 0 | `v4_addons/results/d3_ledger_final.json` | `numbers.unbound_tokens_count.value` | [E] |

## Acceptance checks

- Every `[DECISION NEEDED]` item in `INTEGRATION_PROPOSAL_v4.md` and `TEXT_BLOCKS.md` has a final wording in the addendum §1; none remains in the final slide text: **PASS**.
- Final slide 13 contains every required element (target bridge, feasibility line, DEFF numbers, the variable-profit/startup wording, the decision-rule row labelled `E3_observed, DEFF 1.1, CI rule`, the grid wording, the pilot-purpose sentence and the extension sentence): **PASS** (addendum §3).
- `Beta(6,24)` is followed by “the assumed prevention prior (mean `20%`)”: **PASS** (addendum §2).
- Every term on the two edited slides is glossed, defined or self-evident: **PASS** (addendum §4).
- The final dry-run was produced by a `*_final` copy; the D3 script and outputs are unchanged: **PASS**.
- Final ledger: 0 retired, 18 added, 0 changed, 296 rows; hash identical to the D3 B′ dry-run: **PASS**.
- Option A reproduces the original 278-row ledger hash: **PASS**.
- Zero unbound numeric tokens in the final slide text and in the addendum/report: **PASS**.
- Boundary check clean before and after: **PASS**.

## Deviations from the brief

- The slide-11 box grows by 91.4% (above the +15% rule) because the required Beta gloss cannot fit otherwise. The flag is recorded; F3 must inspect the box and use the D4 fallback (wrap, then reduce font if needed) without dropping the gloss.
- The slide-13 panel grows by 329.7% and is 4.3× the original six-line box. The D4 fallback (move the decision-rule and purpose lines to the footer) is restated; F3 decides after the all-15-slide review.
- “WP1 E4” in the D4 text became “Power simulation (E4)”: WP1 is an internal work-package code that was undefined on the slide, and E4 is now glossed inline. The required E4 numbers are unchanged.
- “Prior-integrated” became “Averaged over” so that the phrase is self-explanatory; the added ledger rows are unchanged.
- “SE(γ̂) ≈ 6.8 pp” and “4.0 pp” became “6.8 percentage points” and “4.0-percentage-point” for the same reason; the bound values are unchanged.
- Option C and Option R were not re-run in the final dry-run (H3 selects B′; C is not adopted; R needs M6).

## Open questions / [DECISION NEEDED] items

- None for F1. F2 (candidate build on copies) is next.

## Commands run

```bash
PY="C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe"; R="D:/progs/IDE/MainProjs/AI/GCI2026/finalA"
cd "$R/v4_addons/tools"
"$PY" -B -X utf8 boundary_check.py --card F1 --phase pre
"$PY" -B -X utf8 d3_ledger_dryrun_final.py
"$PY" -B -X utf8 f1_decisions.py
"$PY" -B -X utf8 check_numbers.py --scan ../INTEGRATION_DECISIONS_ADDENDUM.md ../reports/F1_report.md
"$PY" -B -X utf8 boundary_check.py --card F1 --phase post
```

Environment: Python 3.11.9; verify_runtime pools: openblas 0.3.30 num_threads=6, openblas 0.3.30 num_threads=6; seed 20261043.

Boundary check: before/after hashes clean? yes (pre clean; post-check run after this report; only v4_addons/ written)
