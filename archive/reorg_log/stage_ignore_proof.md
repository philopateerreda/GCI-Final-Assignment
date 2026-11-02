# Per-batch D4 ignore invariance (planned)

Each row maps already-moved paths to their new location and not-yet-moved paths to their old
location, then applies that batch's `gitignore_Rn.txt` in a throwaway git repository.

| Stage | Paths in play | Ignored before | Ignored after | Lost | Gained | Tracked pattern matches | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| R0 | 4969 | 4180 | 4180 | 0 | 0 | 8 | PASS |
| R1 | 4969 | 4180 | 4180 | 0 | 0 | 8 | PASS |
| R2 | 4969 | 4180 | 4180 | 0 | 0 | 8 | PASS |
| R3 | 4969 | 4180 | 4180 | 0 | 0 | 8 | PASS |
| R4 | 4969 | 4180 | 4180 | 0 | 0 | 8 | PASS |
| R5 | 4969 | 4180 | 4180 | 0 | 0 | 8 | PASS |

The eight tracked `.log` files are matched by `*.log` before and after; tracked status wins, so
they remain tracked and stageable. R6/R7 introduce no ignore-anchor changes and are covered by
the R5 final state plus the runtime re-proof in Phase 3.
