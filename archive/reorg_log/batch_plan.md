# Batch plan — one commit per batch

Counts/bytes are from `move_plan.csv` + `inventory.csv`; new READMEs/log files are extra. Every batch is dry-runnable, uses `-LiteralPath`, and commits only its own paths plus its `.gitignore` stage.

| Batch | Commit | Content | Files | Bytes | `.gitignore` state |
|---|---|---|---:|---:|---|
| R1 | `R1_archive` | 2,372 run-residue files + old `README.md` → `archive/`; add archive READMEs | 2,373 | 21,315,406 | `gitignore_R1.txt` (add `/archive/residue/`, `/archive/duplicates/`; retire smoke/m1-cache anchors) |
| R2 | `R2_versions` | `v1_frozen`, `v2_work`, `v3_addons`, `v4_addons` → `versions/` | 2,519 | 483,407,799 | `gitignore_R2.txt` (all version anchors) |
| R3 | `R3_evidence` | `analysis_outputs/` → `evidence/` | 60 | 15,473,401 | `gitignore_R3.txt` (notebook backups) |
| R4 | `R4_docs` | 3 `FINAL_*` + 3 course references → `docs/` | 6 | 2,761,409 | `gitignore_R4.txt` (`*.docx`, tutorial) |
| R5 | `R5_data` | `telecom/` → `data/telecom/` | 2 | 48,120,207 | `gitignore_R5.txt` (`/data/telecom/*.csv`; final) |
| R6 | `R6_submission` | 3 F1 artifacts → `submission/` | 3 | 4,014,399 | no change |
| R7 | `R7_pipeline` | 4 scripts + `references.txt` + `requirements` → `pipeline/` | 6 | 405,172 | no change |
| R8 | `R8_log` | new READMEs, `VERSIONS.md`, `PATH_MAP.md`, then `finalA_reorg_log/` → `archive/reorg_log/` | new docs + log | — | no change |

Root keeps only `README.md`, `.gitignore`, `.gitattributes` and the seven folders; `.git` is untouched.

## Per-batch loop

1. `python scripts/apply_moves.py --batch R1 --dry-run`; output must equal the batch slice of `move_plan.csv`.
2. Execute; every move appended to `moves.csv` (old, new, sha256, bytes, mtime, tracked, timestamp).
3. Reconcile: count/bytes; re-hash every moved file against `hash_manifest_before.csv`; re-verify touched frozen items.
4. `git status --porcelain --ignored`: only batch paths + its `.gitignore` + staged log report.
5. D4: map `ignored_before.txt` through `moves.csv`; must equal the current ignored set. Every tracked move must show `R100` in `git diff --cached -M --name-status`.
6. Commit with counts, bytes, proof status and SHA of the batch proof.
7. Update `STATE.md`. A failed check stops the batch; roll back that batch from `undo_moves.ps1`.

## Same-commit ignore edits (I-9)

- R1 uses `gitignore_R1.txt`; R2 `R2`; R3 `R3`; R4 `R4`; R5 `R5`.
- `R6`/`R7` cross no ignore anchor: all moved files are tracked, or already under a tracked path.
- `.gitattributes` is never edited: `* -text`, no path anchor.

## Commit names and messages

```
R1_archive       chore(reorg): archive run residue and superseded README
R2_versions      chore(reorg): move v1-v4 under versions/
R3_evidence      chore(reorg): rename analysis_outputs to evidence/
R4_docs          chore(reorg): move context notes and course references to docs/
R5_data          chore(reorg): move supplied dataset to data/telecom/
R6_submission    chore(reorg): move frozen delivery artifacts to submission/
R7_pipeline      chore(reorg): move historical pipeline and metadata
R8_log           docs(reorg): add package documentation and reorg audit trail
```

Each message body records: files, bytes, `F1/F2/F3` result (if touched), `R100` count, D4 result, and the proof filename.

## Preconditions

- **Close editors/Office/sync/AV** before R1 (the `.qoder-office-pptx-locks/` empty folder is the only lock trace).
- Confirm no `~$*`, no Office/process handles under the tree.
- Confirm free space ≥ 1.2 GB and the backup is intact.
- G1 reply must be exactly `approved`; no push until G2 and the word `push`.

## Batch-specific notes

- **R1** lifts only run residue (smoke, caches, `*.started`, `*.lock`, `__pycache__`, v4 M1 cache). It does not lift evidence-bound model/OOF caches.
- **R2** is the largest batch. `v1_frozen` moves as a unit (I-12) and F2 is re-verified before commit.
- **R3** renames `analysis_outputs` in place; `evidence/notebook_backups` stays ignored. The flat form is chosen because the pipeline's own path constants are Tier C and the frozen records already carry stale `analysis_outputs` strings; nesting would not avoid those edits.
- **R4** uses evidence from the DOCX text for both course documents; see decision 1.
- **R5** must not log sample rows. Only headers/counts were profiled.
- **R6** re-verifies F1 hashes before and after; no docx is moved here (both course docx moved in R4).
- **R7** moves all four scripts unchanged (Tier C). `pipeline/README.md` will point reproduction at `pre-reorg`, not claim current-layout execution.
- **R8** moves the log into `archive/reorg_log/`; `extracted_text/` and `secret_scan.csv` stay ignored only if they contain sensitive matches. The scan found no credentials, but `extracted_text/` contains course text and is kept out of git.
