# Phase 4 verification

HEAD `fc93e64f4b902d07d134ddb44fe5e0ace9b9ca93`; generated 2026-11-02T15:30:35.519066+00:00

| # | Result | Evidence |
|---|---|---|
| V1 | **PASS** | root=['.git', '.gitattributes', '.gitignore', 'README.md', 'archive', 'data', 'docs', 'evidence', 'pipeline', 'submission', 'versions']; missing=[]; extra=[]; finalA_reorg_log exempt until R8 |
| V2 | **PASS** | plan_rows=4971 baseline_rows=4971 inventory_rows=4971 unchanged=1 moved=4969 (moves.csv rows=4969) edited_on_purpose=1 errors=0; baseline_bytes=575499423 plan_bytes=575499423 reconciled_bytes=575499828 |
| V3 | **PASS** | frozen_rows=75 byte_identical=75 errors=0 F1/F2/F3 |
| V4 | **PASS** | status_lines=5 (log-only) probes=7 not_ignored=[] tracked_but_ignored_before=8 after=8 new=[] lost=[] cv_manifest_ignored=6 |
| V5 | **PASS** | renames_R100=788 additions=108 modifications=['.gitignore', 'README.md'] deletions=0 other=0; bad_mods=[] bad_adds=[] |
| V6 | **PASS** | py_parsed=114 parse_errors=0 notebooks=15 code_cells=174 notebook_errors=0 nothing imported or executed |
| V7 | **PASS** | tracked=899 new_over_25MB=[] pre_existing_over_25MB=[] new_frozen_or_dataset_duplicates=[] pre_existing_duplicates=[] (F1 originals excluded) |
| V8 | **PASS** | G1-approved code edits: 0 (all project scripts Tier C, byte-identical); py_modified=0 ps1_modified=0 ipynb_modified=0 py_added_outside_log=0 ps1_added_outside_log=0 ipynb_added_outside_log=0 code_deleted=0 (new reorg tooling under archive/reorg_log is documentation, not project code) |
| V9 | **PASS** | fsck_rc=0 fsck_errors=0 undo_whatif_rc=0 undo_conflicts=1 undo_tail='WOULD_MOVE archive/residue/__pycache__/restore_v1.cpython-311.pyc -> __pycache__/restore_v1.cpython-311.pyc\nCONFLICT_OLD_EXISTS archive/superseded/README_v2.md -> README.md\nUNDO moves=4969 done=4968 conflicts=1 WhatIf=True Batch=' |
| V10 | **PASS** | old_paths_present=[] empty_dirs=[] |

