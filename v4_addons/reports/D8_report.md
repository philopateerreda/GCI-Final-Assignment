# D8 — Track D summary
Status: COMPLETED_ACCEPTED

Summary: `reports/D_summary.md` consolidates the eight Track D cards, the one-line project status, the four open decisions and the four unopened gates, and embeds the verbatim `check_numbers` and boundary-check outputs; no deliverable was edited and no analysis was run.

## Evidence table

| number | value | source_file | source_key / formula | tag |
|---|---:|---|---|---|
| bound_numbers_d0_d7 | 595 |  | `bound numbers across all results/*.json registries at the time this summary was generated (D0-D7; this card adds its own registry afterwards)` | [E] |
| check_problems | 0 |  | `failures from check_numbers over the same registries` | [E] |
| ack_discrepancies | 1 |  | `acknowledged section-9 discrepancies (the D0 SE-convention note)` | [E] |
| scanned_documents | 6 |  | `Track D deliverable documents scanned against their render registries` | [E] |
| boundary_files | 4,571 |  | `files outside v4_addons/ hashed against the baseline at the D8 pre-check` | [E] |
| boundary_accepted | 4 |  | `accepted changes (the D1 in-place edits and their .pre_v4 backups)` | [E] |
| boundary_unexpected | 0 |  | `unexpected changes outside the write boundary` | [E] |
| gate_files_count | 0 |  | `files present in v4_addons/gates/ at the D8 pre-check` | [E] |
| wp5_pi_star_recorded | 1.546417% | `v4_addons/results/d7_monitor.json` | `numbers.wp5_pi_star_recorded.value` | [E] |
| pi_star_excl_20 | 1.0361% | `v4_addons/results/d7_monitor.json` | `numbers.pi_star_excl_20.value` | [E] |
| pi_star_startup_effect_20 | 0.51 pp | `v4_addons/results/d7_monitor.json` | `numbers.pi_star_startup_effect_20.value` | [E] |
| stage1_cost | $12,872 | `v4_addons/results/d6_text_blocks.json` | `numbers.stage1_cost.value` | [E] |
| stage1_cost_if_floor_paid | $20,744 | `v4_addons/results/d6_text_blocks.json` | `numbers.stage1_cost_if_floor_paid.value` | [E] |
| extend_probability | 91.9% | `v4_addons/results/d4_proposal.json` | `numbers.dq_7872_g20_p_extend.value` | [E] |
| cards_reported | 8 |  | `8` | [E] |
| open_decision_items | 4 |  | `4` | [E] |
| gates_pending | 4 |  | `4` | [E] |
| test_rows_used | 0 |  | `no test row was read by this card` | [E] |
| new_model_fits | 0 |  | `no model was fitted or scored by this card` | [E] |

## Acceptance checks

- Status table covers D0–D7 with the statuses recorded in `results/state.json`: **PASS**.
- One-line project status stated first: **PASS**.
- Every open `[DECISION NEEDED]` item listed with its originating card: **PASS**.
- Gate state listed; no gate file present at generation: **PASS** (`gates/` empty).
- `check_numbers.py` captured verbatim and the scan of all deliverable documents is clean: **PASS** (0 problems).
- Boundary check clean; only the accepted D1 changes outside `v4_addons/`: **PASS**.
- No deliverable edited and no analysis run by this card: **PASS**.
- No test row read, no model fitted: **PASS**.

## Deviations from the brief

- The `check_numbers` total is a count at generation time over the D0–D7 registries; this card adds its own registry afterwards, so a later full run reports a larger total. The captured block is the verbatim output of that run.
- The card asks for a status table of D0–D7; D8 reports itself through `STATE.md`, not through its own table.

## Open questions / [DECISION NEEDED] items

- `[DECISION NEEDED]` π* definition (startup included vs excluded) before any operational monitor.
- `[DECISION NEEDED]` Floor contact cost: is a control-arm contact free?
- `[DECISION NEEDED]` harm-gate action and owner.
- `[DECISION NEEDED]` extension budget.
- Gates awaiting the human: `H0_DECISIONS.md`, `H1_APPROVED.txt`, `H2_APPROVED.txt`, `H3_OPTION.txt` (all absent).

## Commands run

```bash
PY="C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe"; R="D:/progs/IDE/MainProjs/AI/GCI2026/finalA"
cd "$R/v4_addons/tools"
"$PY" -B -X utf8 boundary_check.py --card D8 --phase pre
"$PY" -B -X utf8 d8_summary.py
"$PY" -B -X utf8 check_numbers.py --scan ../reports/D_summary.md ../reports/D8_report.md
"$PY" -B -X utf8 boundary_check.py --card D8 --phase post
```

Environment: Python 3.11.9; verify_runtime pools: openblas 0.3.30 num_threads=6, openblas 0.3.30 num_threads=6; seed 20261037.

Boundary check: before/after hashes clean? yes (pre/post clean; only the 4 D1-allowed changes).
