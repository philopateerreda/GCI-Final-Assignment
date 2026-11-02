# Code edits at G1 — none proposed; Tier C list

**Decision: zero code edits.** Under I-13, all four root entry points and all 88 v2/v3/v4 scripts are Tier C historical snapshots. None is executed by this reorg; none is modified. This keeps the code diff empty and the frozen evidence byte-identical.

## Why all four are Tier C, not A

| File | Coupling that exceeds a few path constants | Consequence |
|---|---|---|
| `analysis_pipeline.py` | 28 path-related lines, including `ROOT / 'telecom'`, `ROOT / 'v1_frozen/...'` in embedded modules, `V2_WORK`, and `ROOT / 'analysis_outputs'`; it is a single 4,209-line v1+v2 monolith. | Make it A would mean editing embedded module bodies, not just constants. Tier C; documented. |
| `build_notebook.py` | Reads the unedited `analysis_pipeline.py`; its generated notebook would still assume the old raw-data and output layout. | Coupled to the Tier C monolith. Tier C. |
| `export_and_verify.py` | Calls `claim_checks.verify_claims(ROOT)` and `run_frozen_batch.verify_completed()`, both of which hard-code old root paths; editing only this file cannot make the verification pass. | Cross-module logic change. Tier C. |
| `restore_v1.py` | `restore()` writes manifest keys directly under `ROOT` (old root layout); the new tree needs a per-key mapping to `submission/`, `pipeline/`, `docs/`, `evidence/`, `versions/`. | Mapping logic, not a path constant. Tier C. |

`v1_frozen/analysis_pipeline.py`, `build_notebook.py`, `export_and_verify.py` are part of F2 and are never edited.

## Historical code list (never edited)

- 92 Python files total: 4 root + 3 in `v1_frozen` + 27 in `v2_work` + 14 in `v3_addons/src` + 5 in `v3_addons/tests` + 39 in `v4_addons/tools` = 92. All are Tier C.
- 15 notebooks: `philopateer.ipynb` (F1), 11 backup/snapshot/release copies, `tutorial (2).ipynb` (course reference), and the v1 copy. None is executed or edited.
- 3 `.py` in `v1_frozen` are frozen by F2; their path strings are root-relative **inside the snapshot** and remain valid after the snapshot moves as a unit.

## Frozen/data records whose path strings go stale (Tier C)

These files record old paths or hashes and are **not** edited:

- `analysis_outputs/audit.json` — `source_sha256` keys use `telecom\Client.csv` / `telecom\Record.csv`.
- `analysis_outputs/delivery_checks.json` — `analysis_outputs/slide_renders/...` render paths and delivery paths.
- `analysis_outputs/claims_ledger_build.json` — v1/v2 source path list.
- `analysis_outputs/source_manifest.json` — `telecom\...` keys.
- `v1_frozen/sha256_manifest.json` — keys are relative to `v1_frozen/`; still valid because the snapshot moves as a unit.
- `v2_work/final_metrics.json` — old `analysis_outputs`, `telecom`, `v1_frozen` source paths.
- `v2_work/d_results/run_spec.json` — old `v2_work` output roots.
- `v3_addons/results/wp8/outside_snapshot.json` — every pre-WP8 outside path and hash.
- `v3_addons/results/write_boundary_before.json` — same outside snapshot.
- `v3_addons/results/wp8/prereg_receipt.json`, `inventory.json`, `final_new_code_tests.json` — absolute old paths.
- `v4_addons/MANIFEST_v4.json` — v3/v4 old paths.
- `v4_addons/results/*.json` — report/render bindings with old paths.

`PATH_MAP.md` maps old top-levels to new ones and lists these as **stale-by-design**. `pre-reorg` keeps the old layout runnable.

## Verification of the no-edit decision

- `dependencies.csv`: 3,049 rows, all Tier C; 0 Tier A/B edits.
- `git diff --stat`: only `.gitignore` / `.gitattributes` (the latter unchanged) and new documentation will appear in R-batches; no `.py` diff.
- Syntax is not re-checked for project code because it is not edited; `ast.parse` already succeeded for all 92 files during Phase 1 (0 parse errors).

## If you want a runnable current-layout pipeline

That is a separate scope: edit `analysis_pipeline.py` (≈28 path points), add a path-mapping layer to `restore_v1.py`, and update `claim_checks.py`/`run_frozen_batch.py` or pass a compatibility root. It would be a **content change** to Tier A/B code and must not be mixed into this reorg. Recommended follow-up, not part of G1.
