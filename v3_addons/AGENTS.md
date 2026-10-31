## 1. HARD GUARDRAILS (from `FINAL_ASSESSMENT_HANDOFF_CONCISE.md`; violating any = stop and report)

**Never:**
- retrain, refit, rescore rejected challengers, rerun the final evaluation, or reset execution markers;
- "Run All" the notebook (v1 cells retrain/predict);
- modify the five supplied originals, the 67-file v1 snapshot, or the frozen protocol (`v2_work/final_protocol.py`, sha256 `700ca444…218c66a`);
- edit the delivery receipt's `visual_review` string (breaks the hash in `v2_work/visual_review.json`);
- run `restore_v1.py` without `--verify-only`;
- import the quarantined `asl_flag` / `area` models or features;
- fabricate an AI chat-history URL, a source you did not read, or a number you did not compute;
- install packages into the shared Python environment (ask first);
- use the **test split** (15,000 rows) for any *new* computation. Test-derived scalars (G, K, queue counts, prior-stress results) are **quoted from `v2_work/final_metrics.json`**, never recomputed from test rows.

**Environment:**
```bash
PY="C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe"   # NOT the `py` launcher
R="D:/progs/IDE/MainProjs/AI/GCI2026/finalA"
# always: "$PY" -B -X utf8 <script>     (-B = no .pyc writes into protected dirs)
```
SEED = 20261028 (derive per-task seeds as `SEED + task_index`), 6 threads max, CPU only. Allowed libs: numpy, scipy, pandas (already present). Anything else → ask.

**Write boundary:** you may create files **only** under `$R/v3_addons/` (create it). Nothing else is writable until WP7 is approved. Layout:
```
v3_addons/
  src/        # scripts (one per WP, deterministic, seeded)
  tests/      # tests for NEW code only (do not run the old 57-test suite)
  results/    # JSON/CSV outputs, each with a provenance block
  figures/    # PNG drafts (not deck-ready)
  reports/    # WPn_report.md
  HANDBACK.md # final summary (WP7)
```
**Provenance block** required in every results JSON: `{script, seed, python_version, input_files:[{path, sha256}], created_utc, row_counts, tags_used}`.

**Claim language:** obey the "Never say / Say instead" table in the handoff §13 and the extensions in §8 of this file.
