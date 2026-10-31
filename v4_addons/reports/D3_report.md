# D3 — Ledger dry-run
Status: COMPLETED_ACCEPTED

Summary: the 278-row claims ledger was copied and the retire/add operations for options A, B′, C and R were applied under `v4_addons/ledger_dryrun/`. A reproduces the original hash; B′ adds 18 rows (296), C adds 25 (303); nothing is retired because the D4 text keeps the `80,000` / `160,000` tokens WP7 had proposed to retire.

## Evidence table

| number | value | source_file | source_key / formula | tag |
|---|---:|---|---|---|
| ledger_rows_original | 278 | `analysis_outputs/claims_ledger.csv` | `rowcount` | [E] |
| rows_retired_A | 0 | `v4_addons/results/integration_spec.json` | `spec.options.A.edits[*].retire` | [E] |
| rows_added_A | 0 | `v4_addons/results/integration_spec.json` | `spec.options.A.edits[*].add` | [E] |
| rows_total_A | 278 |  | `ledger_rows_original - rows_retired_A + rows_added_A` | [E] |
| rows_retired_B_PRIME | 0 | `v4_addons/results/integration_spec.json` | `spec.options.B_PRIME.edits[*].retire` | [E] |
| rows_added_B_PRIME | 18 | `v4_addons/results/integration_spec.json` | `spec.options.B_PRIME.edits[*].add` | [E] |
| rows_total_B_PRIME | 296 |  | `ledger_rows_original - rows_retired_B_PRIME + rows_added_B_PRIME` | [E] |
| rows_retired_C | 0 | `v4_addons/results/integration_spec.json` | `spec.options.C.edits[*].retire` | [E] |
| rows_added_C | 25 | `v4_addons/results/integration_spec.json` | `spec.options.C.edits[*].add` | [E] |
| rows_total_C | 303 |  | `ledger_rows_original - rows_retired_C + rows_added_C` | [E] |
| rows_retired_R | 0 | `v4_addons/results/integration_spec.json` | `spec.options.R.edits[*].retire` | [E] |
| rows_added_R | 18 | `v4_addons/results/integration_spec.json` | `spec.options.R.edits[*].add` | [E] |
| rows_total_R | 296 |  | `ledger_rows_original - rows_retired_R + rows_added_R` | [E] |
| existing_rows_rerender_ok | 275 | `analysis_outputs/claims_ledger.csv` | `all rows` | [E] |
| existing_rows_rerender_mismatch | 3 | `analysis_outputs/claims_ledger.csv` | `all rows` | [E] |

## Dry-run results

| Option | Slides touched | Rows retired | Rows added | New total | sha256 of resulting ledger |
|---|---|---:|---:|---:|---|
| A | — | 0 | 0 | 278 | `b4dce03b43f6bd1b9ef3142759e0cb88682527af2f9f8824902521d88729c5b4` |
| B′ | 11, 13 | 0 | 18 | 296 | `759383e8033c3f9b29974ffde6ba1e519f65f89a0417625c7cc4d92ae2e3583d` |
| C | 5, 11, 12, 13, 15 | 0 | 25 | 303 | `d9b8884a5bf3f2185e0dc4c658a8b8bf39d3d231487879925ae38c23c23e2ae8` |
| R | 11, 13 | 0 | 18 | 296 | `759383e8033c3f9b29974ffde6ba1e519f65f89a0417625c7cc4d92ae2e3583d` |

**Added tokens (B′):** `6`, `24`, `−6.2k`, `1.1`, `90%`, `76.0%`, `25.4%`, `5,000`, `55.6%`, `17.9%`, `10,000`, `158,000`, `20%`, `7.6%`, `91.9%`, `0.5%`, `6.8`, `4.0`

**Added tokens (C, beyond B′):** `17%`, `93%`, `69%`, `6`, `24`, `6`, `14`

Original ledger sha256: `b4dce03b43f6bd1b9ef3142759e0cb88682527af2f9f8824902521d88729c5b4`. Claim-id convention: C0001 = first data row; CSV line = data-row index + 2 (header is line 1).

WP7 proposed retiring C0137 (`80,000`) and C0139 (`160,000`) on slide 13. The D4 B′ text keeps both tokens — `80,000` in the "first qualifying grid point; not an exact minimum" wording and `160,000` only as "unadjusted not established through `160,000`/arm" (section-3 decision 1) — so no row is retired; this is recorded in `results/integration_spec.json` (`wp7_retirements_reversed`). The ledger binds one row per distinct displayed token per slide (e.g. `80%` appears twice on slide 13 with one row), so tokens already present on a slide (`20%`, `95%`, `2.8k`, `4.7k` on slide 11; `10%`, `20%` on slide 12) receive no duplicate row.

Option R uses the B′ ledger as its base; the regenerated model-dependent rows only exist after a Track M ADOPT-CONFIRMED and M6, which have not run.

## Acceptance checks

- Option A reproduces the original ledger hash exactly: **PASS** (`b4dce03b43f6bd1b…` = original).
- B′ and C counts listed and reproducible by re-running `integration_spec.py` + `d3_ledger_dryrun.py` (deterministic CSV writer, CRLF, same column order): **PASS** — B′ 296 rows, C 303 rows.
- Every added row re-renders its `displayed_text` from `formatter × scale × exact_value` (checked at construction) and every added token appears in the after-text of its slide edit: **PASS**.
- Existing-row sanity: 275 of 278 existing rows re-render with their own formatter; 3 do not (chart-axis/textual formats) — informational, no existing row was modified.
- `check_numbers.py`: PASS.

## Deviations from the brief

- The brief's example "retire C0137 (`line 138`) and C0139 (`line 140`)" is not applied, because the D4 B′ panel (which the same card says to apply) keeps both tokens. Retirements would be required only if the human chooses to drop the grid wording from slide 13.
- Ledger copies are written under `v4_addons/ledger_dryrun/`; the original `analysis_outputs/claims_ledger.csv` is untouched (boundary check clean).

## Open questions / [DECISION NEEDED] items

- Whether the slide-13 panel should keep the `80,000` / `160,000` grid wording (then C0137/C0139 stay) or drop it (then retire both) — defaults to keep per DECISIONS_ASSUMED row 1.

## Commands run

```bash
PY="C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe"; R="D:/progs/IDE/MainProjs/AI/GCI2026/finalA"
cd "$R/v4_addons/tools"
"$PY" -B -X utf8 boundary_check.py --card D3 --phase pre
"$PY" -B -X utf8 integration_spec.py
"$PY" -B -X utf8 d3_ledger_dryrun.py
"$PY" -B -X utf8 check_numbers.py
"$PY" -B -X utf8 d3_report.py
"$PY" -B -X utf8 boundary_check.py --card D3 --phase post
```

Environment: Python 3.11.9; verify_runtime pools: openblas 0.3.30 num_threads=6, openblas 0.3.30 num_threads=6; seed 20261032.

Boundary check: before/after hashes clean? yes (pre/post clean; only the 4 D1-allowed changes).
