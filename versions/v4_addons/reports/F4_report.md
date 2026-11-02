# F4 — Append-only notebook supplement — skipped
Status: COMPLETED_ACCEPTED

Summary: **F4 skipped**. The card is optional and must be skipped on any failure; F2 stopped at its guardrail, fallback A adds no number to the deck, and the notebook stays frozen. No cell was appended, no cell was executed, and the notebook is byte-identical to the frozen v2 record.

## Evidence table

| number | value | source_file | source_key / formula | tag |
|---|---:|---|---|---|
| cells_added | 0 |  | `no notebook cell was appended` | [E] |
| cells_executed | 0 |  | `no notebook cell was executed` | [E] |
| max_cells_allowed | 6 |  | `6` | [R] |
| notebook_bytes | 1,857,125 |  | `byte size of the unchanged notebook` | [E] |
| notebook_sha_matches_frozen | 1 |  | `notebook sha256 equals the frozen v2 record` | [E] |

## Acceptance checks

- At most 6 cells appended: **NOT APPLICABLE** — the card was skipped by its own rule.
- Execute only the new cells; first 25 existing cells byte-identical: **NOT APPLICABLE** — no cell was added or run.
- Notebook unchanged: sha256 equals the frozen record (1 match), 1,857,125 bytes: **PASS**.
- Recorded as “F4 skipped”: **PASS** (this report and `STATE.md`).

## Deviations from the brief

- The supplement was not built; this is the directive's prescribed outcome when a prior card fails.

## Open questions / [DECISION NEEDED] items

- F5 continues on the frozen v2 artifacts; the traceability supplement is not part of the submission.

## Commands run

```bash
PY="C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe"; R="D:/progs/IDE/MainProjs/AI/GCI2026/finalA"
cd "$R/v4_addons/tools"
"$PY" -B -X utf8 boundary_check.py --card F4 --phase pre
"$PY" -B -X utf8 f4_skip.py
"$PY" -B -X utf8 check_numbers.py --scan ../reports/F4_report.md
"$PY" -B -X utf8 boundary_check.py --card F4 --phase post
```

Environment: Python 3.11.9; verify_runtime pools: openblas 0.3.30 num_threads=6, openblas 0.3.30 num_threads=6; seed 20261046.

Boundary check: before/after hashes clean? yes (pre clean; post-check run after this report; only v4_addons/ written)
