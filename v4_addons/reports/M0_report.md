# M0 — regeneration feasibility and dependency map
Status: COMPLETED_ACCEPTED

The v2 chain is file-driven: cached-probability replay regenerated the A layer and `final_metrics.json` byte-for-byte, and the ledger map in `v4_addons/M0_dependency_map.md` classifies every row. No model was fitted or scored; ledger, deck and notebook files were read only.

## Evidence table

| number | value | source_file | source_key / formula | tag |
|---|---:|---|---|---|
| verdict_go | 1 |  | `1` | [E] |
| entry_points | 11 |  | `11` | [E] |
| calibrator_replay_max_abs_diff | 0.0 |  | `maximum absolute difference between the rebuilt p_s and the cached a_selected_test.p_s when the frozen heldout probabilities are replayed through the frozen calibrator` | [E] |
| csv_parser_ulp_rows | 3,073 |  | `cached p_s values changed by pandas default parsing versus float_precision=round_trip` | [E] |
| served_rows | 15,000 |  | `rows in the cached test frame` | [E] |
| frozen_frame_rows | 15,000 | `v2_work/a_selected_test.csv` | `rowcount` | [E] |
| final_metrics_hash_equal | 1 |  | `1 if the re-emitted final_metrics.json is byte-identical to the frozen file` | [E] |
| final_metrics_keys | 26 |  | `top-level keys compared` | [E] |
| final_metrics_differing_keys | 0 |  | `top-level keys whose parsed values differ` | [E] |
| final_metrics_wall_seconds | 0.23 |  | `wall time of the re-emission (no scoring)` | [E] |
| a_artifacts_hash_equal | 10 |  | `A artifacts reproduced byte-for-byte` | [E] |
| a_artifacts_compared | 10 |  | `A test artifacts compared after regeneration from the cached probability file` | [E] |
| a_replay_wall_seconds | 16.41 |  | `wall time of the A-layer regeneration (bootstrap included)` | [E] |
| ledger_rows_total | 278 | `analysis_outputs/claims_ledger.csv` | `rowcount` | [E] |
| ledger_rows_dependent | 52 |  | `ledger rows whose displayed value is recomputed by the chain from per-row probabilities or selections` | [E] |
| ledger_rows_narrative | 25 |  | `v1 headline and frozen-search performance rows that regeneration does not recompute` | [E] |
| ledger_rows_unaffected | 201 |  | `protocol, financial, design, bibliography and axis rows` | [E] |
| ledger_affected_slides | 7 |  | `distinct slide numbers carrying at least one regeneration-dependent row` | [E] |
| dependent_final_metrics_rows | 40 |  | `regeneration-dependent rows bound to final_metrics.json` | [E] |
| dependent_chart_rows | 12 |  | `regeneration-dependent observed chart values (not axis ticks)` | [E] |
| regeneration_effort_days | 1.5 |  | `1.5` | [A] |

## Acceptance checks

- Entry point located and the full chain traced from code: **PASS**.
- Pipeline drivable by an alternate probability file: **PASS** (A layer 10 of 10 byte-identical; `final_metrics.json` hash-equal flag 1).
- `final_metrics.json` reproduced exactly in replay mode: **PASS**.
- Dependency map enumerates every regeneration-dependent row: **PASS** (52 rows on 7 slides).
- The 278-row ledger is fully accounted for: 52 regeneration / 25 narrative / 201 unaffected: **PASS**.
- No model fitted, no model scored, no test row used for fitting or selection: **PASS**.
- Regeneration effort recorded: **PASS** (1.5 days [A]).
- Boundary check clean before and after: **PASS**.

## Deviations from the brief

- The brief asks for the count of ledger rows "affected". The map splits that into 52 regeneration-dependent rows and 25 narrative rows because the v1 block and the frozen-search performance rows are not recomputed by the chain; the rule is stated in the map.
- B and C were traced by code inspection, not replayed: both read `a_selected_test.csv`, but their once-only test guards are bound to existing outputs, so a replay would have required bypassing a guard. The A and metrics layers carry the byte-exactness proof.
- The replay reads cached test probabilities; this is allowed for M0 only and is logged via `test_guard.log_replay`. The default CSV parser loses one ulp on 3,073 rows; all replay reads use round-trip parsing.

## Open questions / [DECISION NEEDED] items

- Gate H1 is closed: Track M beyond the M2 draft requires a human-created `gates/H1_APPROVED.txt`.
- The M0 GO authorizes no test scoring and no deck edit; gate H2 and Option H3 remain human decisions.

## Commands run

```bash
PY="C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe"; R="D:/progs/IDE/MainProjs/AI/GCI2026/finalA"
cd "$R/v4_addons/tools"
"$PY" -B -X utf8 boundary_check.py --card M0 --phase pre
OPENBLAS_NUM_THREADS=6 OMP_NUM_THREADS=6 MKL_NUM_THREADS=6 NUMEXPR_NUM_THREADS=6 "$PY" -B -X utf8 m0_feasibility.py
"$PY" -B -X utf8 check_numbers.py --scan ../M0_dependency_map.md ../reports/M0_report.md
"$PY" -B -X utf8 boundary_check.py --card M0 --phase post
```

Environment: Python 3.11.9; verify_runtime pools: openblas 0.3.30 num_threads=6, openblas 0.3.30 num_threads=6, openmp None num_threads=6, openmp None num_threads=6; seed 20261038.

Boundary check: before/after hashes clean? yes (pre clean; post-check run after this report; only `v4_addons/` written)
