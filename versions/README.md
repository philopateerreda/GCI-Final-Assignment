# versions — the audit trail

**What it answers:** which version is canonical, what each later version added, and where the rollback lives.

**Contents**

| Folder | Files | What it is | Tracked? |
|---|---:|---|---|
| `v1_frozen/` | 68 | F2: 67-file v1 snapshot + `sha256_manifest.json` | No (ignored) |
| `v2_work/` | 1,990 | Frozen v2 protocol, workstreams A–D, results, logs, charts | Partly (core evidence tracked; caches/OOF ignored) |
| `v3_addons/` | 283 | Independent audit WP0–WP8: reports, source, tests, results, figures | Yes, except caches/models/sources |
| `v4_addons/` | 178 | v4 release wrapper: reports, tools, yardstick, receipts, gates, release copies | Yes, except release copies/snapshots/caches |

Full timeline and hashes: `VERSIONS.md`.

**Who reads it:** the assessor checking the audit trail, and the author restoring a version.

**Current?** Mixed by design: **v2 is the canonical delivery**; v3 adds audit; v4 is the release label `v4.0.0` with fallback A; v1 is the rollback snapshot. None of v1/v3/v4 replaces the submission.

**How it is regenerated:** not automatically. v3/v4 are historical audit runs; their scripts are Tier C and still assume the old layout. Re-running them is a separate approved scope (see `v4_addons/REPRODUCIBILITY.md`). Do not run them from the new root.

**Caveats**

- `v1_frozen/` and `v4_addons/release_candidate/` are git-ignored and local-only.
- Large caches, OOF arrays, WP8 models, literature PDFs and `.pre_v4` backups are ignored; they stay with their version.
- The old path strings inside v2/v3/v4 records are stale by design; use `archive/reorg_log/path_map.csv`.
- Branch `release/v4` keeps the pre-reorg layout and is not rewritten. `pre-reorg` is the old-layout restore point.
