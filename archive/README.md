# archive — what was retired and why

**What it answers:** where non-delivery material went, and how to undo the move.

**Contents**

| Folder | Files | Bytes | Status |
|---|---:|---:|---|
| `residue/` | 2,372 | 21,305,518 | Git-ignored scratch: smoke runs, caches, `__pycache__`, `.started` markers, killed Track-M fits |
| `superseded/` | 1 | 9,888 | Old `README.md` (pre-v4), kept as `README_v2.md` |
| `duplicates/` | 0 | 0 | No separate action; see `duplicates/README.md` (ignored) |
| `unclear_status/` | 0 | 0 | None; see `unclear_status/README.md` |
| `reorg_log/` | the reorg record | — | Tracked except `extracted_text/` and `verify_clone/` |

**Who reads it:** the author undoing the reorg, and an auditor checking that nothing was lost.

**Current?** No — historical and scratch material only. Nothing here is delivered.

**How it is regenerated:** not needed. Residue is reproducible from its run; superseded material is retained for provenance. No file was deleted in this reorganization.

**Caveats**

- `residue/` is git-ignored and never pushed. It is retained locally so that “nothing deleted” is literally true.
- `reorg_log/` contains the move log (`moves.csv`), the per-file map (`path_map.csv`), `PATH_MAP.md`, batch proofs, the hash manifest, and the re-runnable scripts (`undo_moves.ps1 -WhatIf` is tested).
- `extracted_text/` (course-document text used for classification) and `verify_clone/` (the fresh-clone check) stay ignored.
- The old layout is reachable from branch `pre-reorg`; see `reorg_log/PATH_MAP.md`.
