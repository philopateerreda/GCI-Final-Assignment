# PATH_MAP — every old path → new path

_Reorg of 2026-11-02. 4,971 originals / 575,499,423 bytes: 4,969 moved, 1 unchanged (`.gitattributes`), 1 edited (`.gitignore`). Per-file map: `path_map.csv` (4,971 rows; columns `old_path,new_path,change,category,tier,tracked,group_id,bytes,sha256`)._

## Directory level

| Old | New | Files | Bytes | Note |
|---|---|---:|---:|---|
| `README.md` | `archive/superseded/README_v2.md` | 1 | 9,888 | Old README; the new root `README.md` is a new file |
| `analysis_outputs/` | `evidence/` | 60 | 15,473,401 | Renamed in place (no nested `evidence/analysis_outputs/`) |
| `telecom/` | `data/telecom/` | 2 | 48,120,207 | Supplied dataset; git-ignored, not redistributed |
| `v1_frozen/` | `versions/v1_frozen/` | 68 | 15,477,684 | F2 snapshot + SHA256 manifest; git-ignored |
| `v2_work/` | `versions/v2_work/` | 1,990 | 348,393,099 | Frozen v2 protocol and results |
| `v2_work/c_smoke/`, `d_smoke/`, `d_smoke_io/`, `__pycache__/` | `archive/residue/v2_work/` | 2,110 | 15,115,324 | Scratch only; git-ignored |
| `v3_addons/` | `versions/v3_addons/` | 283 | 111,699,239 | Independent audit WP0–WP8 |
| `v3_addons/results/wp8/cache/*.started` | `archive/residue/v3_addons/results/wp8/cache/` | 61 | 3,841 | Execution-start markers |
| `v4_addons/` | `versions/v4_addons/` | 178 | 7,837,777 | v4 release wrapper |
| `v4_addons/m1_work/cache/` | `archive/residue/v4_addons/m1_work/cache/` | 200 | 6,181,979 | Killed Track M fit caches |
| `philopateer.ipynb`, `.pdf`, `.pptx` | `submission/` | 3 | 4,014,399 | F1 hand-in artifacts |
| `FINAL_*.md` (3 files) | `docs/` | 3 | 72,168 | Handoff, reading note, v2 upgrade report |
| `README.docx`, `ENG_Company _A_ Dataset Overview.docx`, `tutorial (2).ipynb` | `docs/reference/` | 3 | 2,689,241 | Course references; git-ignored |
| `analysis_pipeline.py`, `build_notebook.py`, `export_and_verify.py`, `restore_v1.py`, `references.txt`, `requirements-python311.txt` | `pipeline/` | 6 | 405,172 | Tier C; byte-identical |
| `__pycache__/` (root) | `archive/residue/__pycache__/` | 1 | 4,374 | Bytecode residue |

Totals reconcile to the Phase-0 manifest: 4,971 files / 575,499,423 bytes (including the 75-byte `.gitattributes` and the 1,555-byte `.gitignore`; the latter is now 1,960 bytes after the approved ignore edits).

## Archive detail

| Archive path | Files | Bytes | Why |
|---|---:|---:|---|
| `archive/residue/v2_work/c_smoke/` | 5 | 546,470 | v2 smoke fixture (`smoke=True`) |
| `archive/residue/v2_work/d_smoke/` | 243 | 2,817,081 | Workstream D smoke run |
| `archive/residue/v2_work/d_smoke_io/` | 1,841 | 11,187,208 | Workstream D I/O smoke run |
| `archive/residue/v2_work/__pycache__/` | 21 | 564,565 | Python bytecode |
| `archive/residue/v3_addons/results/wp8/cache/` | 61 | 3,841 | `.started` execution markers |
| `archive/residue/v4_addons/m1_work/cache/` | 200 | 6,181,979 | Caches from the killed Track M fit |
| `archive/residue/__pycache__/` | 1 | 4,374 | Root Python bytecode |
| `archive/superseded/README_v2.md` | 1 | 9,888 | Superseded README |
| `archive/duplicates/` | 0 | 0 | No separate archive action: all 510 duplicate files are evidence-bound, tracked, or move with residue (see `duplicates.csv`) |
| `archive/unclear_status/` | 0 | 0 | None left after classification |
| `archive/reorg_log/` | this log | — | Moves, hashes, proofs, scripts; tracked except `extracted_text/` and `verify_clone/` |

## Stale-by-design references (Tier C and frozen records)

These path strings still name the **old** layout on purpose. Rewriting them would break hashes or falsify what was executed.

- **Tier C dependency rows: 3,049** (`dependencies.csv`); tier A=0, B=0. All 92 `.py` files are byte-identical to `pre-reorg` (V8).
- **202 distinct repo paths** referenced in hand-in text, READMEs, docs and notebook sources break on move (`link_scan.md`); 45 external URLs are unaffected.
- `evidence/audit.json` keys `source_sha256` as `telecom\Client.csv` and `telecom\Record.csv`.
- `evidence/delivery_checks.json` keys `render_sha256` as `analysis_outputs/slide_renders/…`; the claims ledger and `claims_ledger_build.json` also cite old source paths.
- `versions/v1_frozen/sha256_manifest.json` keys are relative to the v1 root; `versions/v4_addons/RELEASE_RECEIPT.md` cites `release_candidate/` paths.
- `versions/v2_work/`, `versions/v3_addons/` and `versions/v4_addons/` result files and reports contain absolute old paths (`D:/…/finalA/analysis_outputs/…`).
- Resolve any old path via `path_map.csv`; do not edit the record.

## Working-directory assumptions

| Script | `ROOT` is | Expects beside it | Consequence in the new layout |
|---|---|---|---|
| `pipeline/analysis_pipeline.py` | `Path.cwd()` | `telecom/`, `analysis_outputs/`, `v1_frozen/`, `v2_work/` | Must run from an old-layout workspace, not from the repo root |
| `pipeline/build_notebook.py` | Script's parent | `analysis_pipeline.py`, `references.txt`; writes `philopateer.ipynb`, `analysis_outputs/notebook_backups/` | Running it in place would write into `pipeline/`; use a staging copy |
| `pipeline/export_and_verify.py` | Script's parent | `analysis_outputs/`, `v2_work/`, `philopateer.*`, `v1_frozen/` | Windows + Office required; staging copy only |
| `pipeline/restore_v1.py` | Script's parent | `v1_frozen/` beside the script | Stage `versions/v1_frozen` as `v1_frozen/`; restore target must be outside this tree |
| `versions/v2_work/*.py` | Their own directories | `v1_frozen`, `v2_work`, `telecom` | Historical; not re-run in this reorg |
| `versions/v3_addons/src/*.py` | `v3_addons` | Old paths, hash-bound outputs | Historical; reproduction is a separate approved scope |
| `versions/v4_addons/tools/*.py` | Repo root | Old paths, hash-bound results | Historical; read-only audit tools |

## Undo

1. Filesystem: `archive/reorg_log/scripts/undo_moves.ps1 -WhatIf` (tested; 4,969 moves), then without `-WhatIf` to reverse newest-first.
2. Git: `git revert` the R1–R8 commits newest-first; never reset.
3. Old layout: branch `pre-reorg` at `6b6f39a`, also `release/v4`; backup at `D:\progs\IDE\MainProjs\AI\GCI2026\finalA_BACKUP_20261102`.
4. `moves.csv` is the append-only move log; `path_map.csv` is the sorted read-only view.
