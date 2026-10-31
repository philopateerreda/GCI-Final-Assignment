# D1 — Refresh stale documents
Status: COMPLETED_ACCEPTED

Summary: `v3_addons/HANDBACK.md` and `v3_addons/reports/WP7_report.md` were backed up as `*.pre_v4` and edited in place to state that WP8 was executed and rejected; `WP8_status_addendum.md` records the status vocabulary and five caveats without touching the sealed WP8 report; `MANIFEST_v4.json` inventories every `v3_addons/` file including WP8.

## Evidence table

| number | value | source_file | source_key | tag |
|---|---:|---|---|---|
| wp8_classifier_fits | 50 | `v3_addons/results/wp8_model.json` | `fit_counts.classifier` | [E] |
| wp8_classifier_iterations_value | 385 | `v3_addons/results/wp8_model.json` | `fit_inventory[*].iterations` | [E] |
| wp8_classifier_iterations_distinct_count | 1 | `v3_addons/results/wp8_model.json` | `fit_inventory[*].iterations` | [E] |
| wp8_frozen_n_estimators | 385.0 | `v3_addons/prereg_wp8.md` | `line:29:regex:n_estimators=(\d+)` | [E] |
| wp8_mean_delta_auc | 0.00027605323765323987 | `v3_addons/results/wp8_model.json` | `intervals.auc.mean` | [E] |
| wp8_gate_auc_threshold | 0.003 | `v3_addons/prereg_wp8.md` | `line:46:regex:Mean delta AUC must be >=([0-9.]+)` | [R] |
| wp8_failed_gates | 7 | `v3_addons/results/wp8_model.json` | `promotion.failed_gates` | [E] |
| wp8_total_gates | 11 | `v3_addons/results/wp8_model.json` | `promotion.gates` | [E] |
| wp8_corrected_df | 4 | `v3_addons/results/wp8_model.json` | `intervals.auc.df` | [E] |
| manifest_file_count | 344 | `v4_addons/MANIFEST_v4.json` | `file_count` | [E] |
| manifest_wp8_file_count | 224 | `v4_addons/MANIFEST_v4.json` | `wp8_file_count` | [E] |
| old_manifest_file_count | 118 | `v3_addons/results/wp7_final_verification.json` | `file_count` | [E] |

## Edits applied (exact before → after)

**`v3_addons/HANDBACK.md`** (backup `v3_addons/HANDBACK.md.pre_v4`)

- before: `[R] Human integration gate remains closed; WP8 OFF.`
- after: `[R] Human integration gate remains closed. [E] WP8 was executed; decision `rejected_keep_frozen_v2_stop_model_track`; the WP8 challenger track is closed.`
- before: `no new test-row computation, no frozen file edited, no WP8 run.`
- after: `no new test-row computation, no frozen file edited. [E] WP8 was executed; decision `rejected_keep_frozen_v2_stop_model_track`; the WP8 challenger track is closed. Status vocabulary and caveats: `../v4_addons/WP8_status_addendum.md`.`
- before: `| WP7 | DONE |⏎`
- after: `| WP7 | DONE |⏎| WP8 | COMPLETED_REJECTED (executed after this handback; see `reports/WP8_report.md`) |⏎`
- before: `[E] Files created: **118 sandbox files**, listed completely in [results/wp7_files_created.csv](results/wp7_files_created.csv).`
- after: `[E] Files created at WP7 time: **118 sandbox files**, listed in [results/wp7_files_created.csv](results/wp7_files_created.csv); the complete post-WP8 inventory of `v3_addons/` is `../v4_addons/MANIFEST_v4.json`.`

**`v3_addons/reports/WP7_report.md`** (backup `v3_addons/reports/WP7_report.md.pre_v4`)

- before: `[R] Applied slide/notebook/reference edits, new test evaluation, new AUC gain, submission or WP8 execution.`
- after: `[R] Applied slide/notebook/reference edits, new test evaluation, new AUC gain, or submission. [E] WP8 was executed; decision `rejected_keep_frozen_v2_stop_model_track`; the WP8 challenger track is closed.`

## Acceptance checks

- `grep` for "WP8 OFF" / "no WP8 run" / "WP8 execution" in `v3_addons/**/*.md` excluding the sealed WP8 report and the `.pre_v4` backups: **PASS** (0 hits; see commands).
- Manifest count 344 > 118 and includes 224 WP8 files: **PASS**.
- Backups exist and are byte-identical to the pre-edit files (sha256 recorded in `snapshots/allowed_changes.json`): **PASS**.
- Line endings (CRLF) preserved in both edited files: **PASS** (`file` reports CRLF after edit).
- Boundary check after D1: changes only in the allowed files — `v3_addons/HANDBACK.md` (changed), `v3_addons/HANDBACK.md.pre_v4` (added), `v3_addons/reports/WP7_report.md` (changed), `v3_addons/reports/WP7_report.md.pre_v4` (added): **PASS** (0 unexpected).
- `check_numbers.py`: PASS (see D1 commands).

## Deviations from the brief

- The brief lists line ~48 of `v3_addons/WP7_report.md`; the file lives at `v3_addons/reports/WP7_report.md` (same line 48). Edited there.
- Beyond the two cited sentences, HANDBACK.md received a WP8 row in its status table and a pointer from the stale "118 sandbox files" sentence to `MANIFEST_v4.json`, so the document is internally consistent after the refresh. Both are recorded above and in `results/d1_refresh.json`.

## Open questions / [DECISION NEEDED]

- None.

## Commands run

```bash
PY="C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe"; R="D:/progs/IDE/MainProjs/AI/GCI2026/finalA"
cd "$R/v4_addons/tools"
"$PY" -B -X utf8 boundary_check.py --card D1 --phase pre
V4_ALLOW_WRITE="$R/v3_addons/HANDBACK.md;$R/v3_addons/HANDBACK.md.pre_v4;$R/v3_addons/reports/WP7_report.md;$R/v3_addons/reports/WP7_report.md.pre_v4" "$PY" -B -X utf8 d1_refresh.py
"$PY" -B -X utf8 boundary_check.py --card D1 --phase post
grep -rn "WP8 OFF\|no WP8 run\|WP8 execution" "$R/v3_addons" --include=*.md | grep -v "\.pre_v4\|WP8_report.md"   # expect no output
"$PY" -B -X utf8 d1_report.py
"$PY" -B -X utf8 check_numbers.py --scan ../WP8_status_addendum.md ../reports/D1_report.md
```

Environment: Python 3.11.9; verify_runtime pools: openblas 0.3.30 num_threads=6, openblas 0.3.30 num_threads=6.

Boundary check: before/after hashes clean? yes — pre clean; post shows exactly the 4 allowed changes (2 edited files + 2 backups), 0 unexpected.
