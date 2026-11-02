# Phase 0 — Safety net report

**Status: PASS.** No project code executed; no tracked path changed; `main` still at `6b6f39a`.

## Pre-flight

| Check | Result |
|---|---|
| Free space on D: | 99,692,457,984 bytes (~92.8 GiB); requirement ~1.2 GB — PASS |
| Reparse points / junctions under `finalA` | none — PASS |
| Office lock files (`~$*`) | none — PASS |
| Processes whose image is under `finalA` | none — PASS |
| Destination `finalA_BACKUP_20261102` existed | no — PASS (first attempt) |
| Windows permission issue creating sibling backup dir | repaired by bundled ACL diagnostic; backup dir created; source ACLs/contents unchanged (recovery records in `AI\GCI2026\acl-recovery-20261102\`) |

## Backup (I-2)

`robocopy "<root>" "D:\progs\IDE\MainProjs\AI\GCI2026\finalA_BACKUP_20261102" /E /COPY:DAT /DCOPY:DAT /XJ /R:1 /W:1`

| Metric | Source at backup | Backup |
|---|---:|---:|
| Files | 6,299 | 6,299 |
| Directories | 336 | 336 |
| Bytes | 593,544,196 | 593,544,196 |
| Failed / extras | 0 / 0 | — |

- 20 deterministic sample SHA256 pairs: **20/20 equal**
- 20 sample mtimes: **20/20 equal (ns)**
- Detail: `backup_verify.json`

## Manifest (working tree only)

- `hash_manifest_before.csv`: **4,971 files / 575,499,423 bytes**, SHA256 + size + UTC mtime.
- `.git` excluded from the worktree manifest. Before `pre-reorg`: **1,328 files / 18,044,773 bytes**.
- `finalA_reorg_log\` did not exist at backup time and is excluded from the Phase-0 manifest.
- 117 MB JSON hashed once; every file hashed once (no sampling).

## Git facts (I-7)

| Fact | Value |
|---|---|
| Branch | `main` |
| HEAD | `6b6f39a` — `chore(release): record v4.0.0 verification and final state` |
| Status | clean (`status --porcelain` = 0) |
| Branches | `main`, `release/v4` (both at `6b6f39a`) |
| Remote | `origin https://github.com/philopateerreda/GCI-Final-Assignment.git` |
| `git ls-remote origin` | exit 0; `refs/heads/main` = `6b6f39a96d0b9f34f05dcc437fa6e9fcacd9b0d9` |
| Local vs `origin/main` | 0 ahead / 0 behind |
| `pre-reorg` | created at `6b6f39a`; did **not** switch branch |
| Tracked files | 791 |
| Nested ignore/attribute files | none (only root `.gitignore` / `.gitattributes`) |
| LFS | none configured (`git lfs ls-files` empty) |

## Frozen hashes (I-4 / F1–F3)

| ID | Items | Result |
|---|---|---|
| F1 | 5 hand-in artifacts | 5/5 SHA256 recorded |
| F2 | 67 manifest entries + manifest file (68 files) | 67/67 PASS, 0 missing, 0 uncovered; base = `v1_frozen\`; manifest unmodified |
| F3 | `telecom/Client.csv`, `telecom/Record.csv` | 2/2 SHA256 recorded |

The v1 manifest keys were tested against both candidate bases in memory: `v1_frozen` matched 67/67, `finalA` matched 38/67. The base is therefore `v1_frozen\` — **not** root-relative. No remap of the file was needed.

## Artifacts

- `hash_manifest_before.csv`, `hash_manifest_before_summary.json`
- `frozen_before.csv`, `frozen_coverage.json`
- `backup_verify.json`
- `scripts\make_manifest.py`, `scripts\verify_backup.py`, `scripts\frozen_hashes.py`
