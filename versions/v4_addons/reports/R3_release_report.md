# R3 — Release report

Status: RELEASED_FALLBACK_A_v4.0.0

v4 is published on branch `release/v4` from base `e8f6520`. Annotated tag `v4.0.0` targets this report commit. Fallback A: the four frozen v2 deliverables, the ledger and the README's claim boundary are unchanged.

## Commits on release/v4

| commit | subject | files |
|---|---|---:|
| `9077624` | chore(v4): add provenance tooling and boundary checks | 46 |
| `ebe942a` | docs(v3): refresh status text and manifest after WP8 | 8 |
| `6a7a786` | docs(v4): add yardstick reconciling pilot sizes and profit | 5 |
| `7b1d635` | docs(v4): add ledger dry-run and integration proposal v4 | 20 |
| `60f85dd` | docs(v4): add reproducibility supplement and monitor wrap-up | 21 |
| `2569954` | docs(v4): record regeneration check and close model track at M1 | 31 |
| `788ece6` | docs: rewrite README for v4 | 1 |
| `4fa266e` | chore(release): add v4 release receipt and hashes | 33 |
| this commit | chore(release): record v4.0.0 verification and final state | 8 |

The 8 commits above were pushed and verified in a clean clone before this report and the final state line were added.

## Verification clone

A fresh clone of the public repository (`release/v4`) was created outside the project and checked:

| check | result |
|---|---|
| tracked files under `telecom/` | 0 |
| deliverable and ledger hashes | 4 of 4 deliverables plus the 278-row ledger equal the receipt |
| README checker | PASS — 149 tokens, 105 distinct, 24 paths |
| commit order | the 8 planned commits, in order |
| tree size | 786 files, 32,602,884 bytes |

### Known limitation

Running `check_numbers.py` in the clone reports 15 bindings whose source files are intentionally not published. The build environment passes every binding (`check_numbers` reports 0 problems), with 1 acknowledged discrepancy (the SE convention documented in D0). The unpublished sources are:

- `/v1_frozen/` — the immutable v1 snapshot, 15 MB and 68 files, retained locally by the original project;
- `v2_work/a_selected_test.csv` and `v2_work/a_selected_calibration.csv` — per-row score artefacts;
- `v3_addons/results/sources/` — third-party literature under copyright.

These exclusions predate v4 and are consistent with the public repository's rules. A reviewer cloning the repository will see the same 15 missing-source notices; no headline or ledger figure depends on them.

## Excluded files

| category | files | why excluded |
|---|---:|---|
| caches and regenerable intermediates | 4,088 | rebuildable from seeds; keeps the public tree small |
| telecom raw data | 2 | provider data; never pushed |
| v1_frozen | 68 | immutable v1 snapshot retained locally by the original project |
| release_candidate copies | 6 | duplicate read-only copies of the delivered files |
| per-row v2 artifacts | 2 | large per-customer score files; regenerable |
| third-party sources | 6 | copyrighted literature, not redistributable |
| snapshots | 2 | contain absolute local paths |
| internal readiness docs | 4 | internal release readiness material |
| .pre_v4 backups | 2 | git history is the backup |

Total ignored in the work tree: 4,180 files, 542,863,590 bytes. None of them is committed. The largest excluded group is regenerable caches (4,088 files).

## README

No open queries. Every token is bound to an existing artifact, every relative path resolves, the two template corrections are kept (the per-look harm gate; the relative value wording), and the fallback A wording states that the delivered deck is unchanged.

## Deviations from the directive

- The deck commit (#7) and the notebook commit (#8) were skipped under fallback A: there is no promoted deck and no notebook supplement.
- The release receipt commit was split. The eight content commits were pushed and clone-verified first; this report and the final state form the ninth commit, because RELEASED cannot be claimed before verification. The tag targets this commit.
- No force push, no history rewrite, no tag moved or deleted, no GitHub Release created, and no credential stored.

## Final state

`STATE.md` is set to `RELEASED_FALLBACK_A_v4.0.0`. Branch `release/v4` and tag `v4.0.0` are pushed; the default branch is fast-forwarded to this commit after the clone checks above pass.
