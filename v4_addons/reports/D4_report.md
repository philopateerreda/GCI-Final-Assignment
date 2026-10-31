# D4 — Integration proposal v4
Status: COMPLETED_ACCEPTED

Summary: `INTEGRATION_PROPOSAL_v4.md` supersedes the WP7 proposal with exact before/after text for A / B′ / C / R, text-length deltas, D3 ledger impact and hashes, QA chain, effort estimates and risks. B′ is recommended; nothing is applied; the human gate H3 is closed.

## Evidence table

| number | value | source_file | source_key / formula | tag |
|---|---:|---|---|---|
| rows_total_A | 278 | `v4_addons/results/d3_ledger_dryrun.json` | `numbers.rows_total_A.value` | [E] |
| rows_total_B_PRIME | 296 | `v4_addons/results/d3_ledger_dryrun.json` | `numbers.rows_total_B_PRIME.value` | [E] |
| rows_total_C | 303 | `v4_addons/results/d3_ledger_dryrun.json` | `numbers.rows_total_C.value` | [E] |
| rows_total_R | 296 | `v4_addons/results/d3_ledger_dryrun.json` | `numbers.rows_total_R.value` | [E] |
| len_delta_pct_slide11 | 48.3 |  | `100 * (len_after_slide11 - len_before_slide11) / len_before_slide11` | [E] |
| len_delta_pct_slide13 | 260.7 |  | `100 * (len_after_slide13 - len_before_slide13) / len_before_slide13` | [E] |
| len_delta_pct_slide12 | 42.7 |  | `100 * (len_after_slide12 - len_before_slide12) / len_before_slide12` | [E] |
| len_delta_pct_slide5 | 41.6 |  | `100 * (len_after_slide5 - len_before_slide5) / len_before_slide5` | [E] |
| len_delta_pct_slide15 | 8.4 |  | `100 * (len_after_slide15 - len_before_slide15) / len_before_slide15` | [E] |
| days_B_PRIME | 1.0 |  | `1.0` | [A] |
| days_C | 1.5 |  | `1.5` | [A] |
| days_R | 4.0 |  | `4.0` | [A] |

## Acceptance checks

- No unbound numbers: **PASS** — `check_numbers.py --scan ../INTEGRATION_PROPOSAL_v4.md` (slide text blocks are the D3 spec strings, themselves rendered from bound sources).
- Placeholders appear only for human decisions and are listed at the top of the file: **PASS** (three `[DECISION NEEDED: …]` items).
- Required B′ content present: slide-11 exact sentence; slide-13 target bridge, feasibility line, DEFF-1.1 E4 numbers, "variable profit, startup excluded", decision row labelled E3_observed / DEFF 1.1 / CI rule, grid wording, pilot-purpose sentence, extension placeholder: **PASS**.
- Text-length deltas computed and flagged above 15%: slide 11 48.3%, slide 13 260.7%, slide 12 42.7%, slide 5 41.6%, slide 15 8.4% — four of five flagged; layout fallback documented.

## Deviations from the brief

- The slide-13 panel required by the brief is far longer than the original six-line box (flagged). A fallback placement (decision/purpose lines to the footer) is proposed rather than silently dropping required content.
- WP7's retire operations for C0137/C0139 are not carried into B′ because the required grid wording keeps both tokens (see D3).

## Open questions / [DECISION NEEDED] items

- `gates/H3_OPTION.txt` (A / B_PRIME / C / R).
- The three `[DECISION NEEDED]` placeholders listed at the top of the proposal.

## Commands run

```bash
PY="C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe"; R="D:/progs/IDE/MainProjs/AI/GCI2026/finalA"
cd "$R/v4_addons/tools"
"$PY" -B -X utf8 boundary_check.py --card D4 --phase pre
"$PY" -B -X utf8 d4_proposal.py
"$PY" -B -X utf8 check_numbers.py --scan ../INTEGRATION_PROPOSAL_v4.md ../reports/D4_report.md
"$PY" -B -X utf8 boundary_check.py --card D4 --phase post
```

Environment: Python 3.11.9; verify_runtime pools: openblas 0.3.30 num_threads=6, openblas 0.3.30 num_threads=6; seed 20261033.

Boundary check: before/after hashes clean? yes (pre/post clean; only the 4 D1-allowed changes).
