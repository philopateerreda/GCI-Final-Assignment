# Git state and ignore proof (H1, H2)

## Baseline

- Branch: `main`; HEAD `6b6f39a`; clean.
- Tracked files: **791**.
- Ignored files: **4180** (`ignored_before.txt`).
- Untracked, not ignored: **43** (only the reorg log).
- Nested `.gitignore` / `.gitattributes`: **0 / 0**.
- Git LFS: **none**.

## `.gitattributes`

```text
# Hash-bound evidence bundle: keep file bytes exactly as produced.
* -text
```

No path anchors. Moving files does not change attribute matching; **no `.gitattributes` edit is needed**.

## `.gitignore` — patterns that actually match files

| Line | Pattern | Ignored files | Example |
|---:|---|---:|---|
| 2 | `__pycache__/` | 22 | `v2_work/__pycache__/workstream_d.cpython-311.pyc` |
| 16 | `/telecom/*.csv` | 2 | `telecom/Record.csv` |
| 17 | `/*.docx` | 2 | `README.docx` |
| 18 | `/tutorial*.ipynb` | 1 | `tutorial (2).ipynb` |
| 21 | `v2_work/literature_*.pdf` | 7 | `v2_work/literature_TMobile2025_annual.pdf` |
| 22 | `v2_work/literature_*.png` | 1 | `v2_work/literature_Elkan2001_page975.png` |
| 23 | `v3_addons/results/sources/` | 6 | `v3_addons/results/sources/nadeau_bengio_source.txt` |
| 26 | `/v1_frozen/` | 68 | `v1_frozen/sha256_manifest.json` |
| 29 | `analysis_outputs/notebook_backups/` | 6 | `analysis_outputs/notebook_backups/philopateer-20261028-205244.ipynb` |
| 32 | `v2_work/d_results/cache/` | 1392 | `v2_work/d_results/cache/ffdcf6770df16b1ba5536eabfe04392928c72691dbf9e5a77a14ebeb0694d518.npz` |
| 33 | `v2_work/d_results/oof/` | 130 | `v2_work/d_results/oof/nested_xgboost_r1_f4.npz` |
| 34 | `v2_work/d_results/cv_manifest.csv` | 1 | `v2_work/d_results/cv_manifest.csv` |
| 35 | `v2_work/d_results/cv_manifest.json` | 1 | `v2_work/d_results/cv_manifest.json` |
| 36 | `v2_work/d_smoke/` | 243 | `v2_work/d_smoke/run_spec.json` |
| 37 | `v2_work/d_smoke_io/` | 1841 | `v2_work/d_smoke_io/summary.json` |
| 38 | `v2_work/c_smoke/` | 5 | `v2_work/c_smoke/c_summary.json` |
| 39 | `v3_addons/results/*.npz` | 27 | `v3_addons/results/wp5_grid_19.npz` |
| 40 | `v3_addons/results/wp5_calibration_oof.csv` | 1 | `v3_addons/results/wp5_calibration_oof.csv` |
| 41 | `v3_addons/results/wp5_label_shift_raw.csv` | 1 | `v3_addons/results/wp5_label_shift_raw.csv` |
| 43 | `v3_addons/results/wp8/**/*.npz` | 11 | `v3_addons/results/wp8/r1_f4.npz` |
| 44 | `v3_addons/results/wp8/models/` | 10 | `v3_addons/results/wp8/models/r1_f4_outer.txt` |
| 45 | `v3_addons/results/wp8/cache/` | 181 | `v3_addons/results/wp8/cache/r1_f4_sigmoid.started` |
| 48 | `v2_work/a_selected_test.csv` | 1 | `v2_work/a_selected_test.csv` |
| 49 | `v2_work/a_selected_calibration.csv` | 1 | `v2_work/a_selected_calibration.csv` |
| 50 | `v2_work/a_bootstrap_test.csv` | 1 | `v2_work/a_bootstrap_test.csv` |
| 51 | `v2_work/a_bootstrap_calibration.csv` | 1 | `v2_work/a_bootstrap_calibration.csv` |
| 52 | `v2_work/b_assignments_test.csv` | 1 | `v2_work/b_assignments_test.csv` |
| 53 | `v2_work/b_assignments_calibration.csv` | 1 | `v2_work/b_assignments_calibration.csv` |
| 54 | `v2_work/c_subgroup_robustness.csv` | 1 | `v2_work/c_subgroup_robustness.csv` |
| 57 | `*.pre_v4` | 2 | `v3_addons/reports/WP7_report.md.pre_v4` |
| 62 | `v4_addons/CEO_BRIEF*` | 1 | `v4_addons/CEO_BRIEF.md` |
| 63 | `v4_addons/CEO_QA*` | 1 | `v4_addons/CEO_QA.md` |
| 64 | `v4_addons/HUMAN_CHECKLIST.md` | 1 | `v4_addons/HUMAN_CHECKLIST.md` |
| 65 | `v4_addons/DISCLOSURE_CHECK.md` | 1 | `v4_addons/DISCLOSURE_CHECK.md` |
| 66 | `v4_addons/release_candidate/` | 6 | `v4_addons/release_candidate/references.txt` |
| 69 | `v4_addons/snapshots/` | 2 | `v4_addons/snapshots/baseline_2026-10-31.json` |
| 70 | `v4_addons/m1_work/cache/` | 200 | `v4_addons/m1_work/cache/fd8c70a6078c7a2ac43f2049cbf33b16e38d546ae90acafe27593342f4cdab21.npz` |

## Root anchors and what would break if moved without a same-commit edit (I-9)

| Anchor | Protects today | If the folder moves unchanged |
|---|---|---|
| `/telecom/*.csv` | both supplied CSVs | dataset becomes unignored under `data/telecom/` |
| `/*.docx` | `README.docx`, `ENG_Company _A_ Dataset Overview.docx` | both become unignored under `docs/reference/` |
| `/tutorial*.ipynb` | course tutorial | tutorial becomes unignored under `docs/reference/` |
| `/v1_frozen/` | 68 immutable v1 files | snapshot becomes unignored under `versions/v1_frozen/` |
| `v2_work/literature_*` | 9 literature files | paths become stale under `versions/v2_work/` |
| `v2_work/d_results/cv_manifest.*` | 145 MB manifests | paths become stale under `versions/v2_work/` |
| `v2_work/{c_smoke,d_smoke,d_smoke_io}/` | smoke residue | must be ignored under `archive/residue/` |
| `v3_addons/results/*.npz`, `wp8/**/*.npz`, `wp8/models/` | large evidence | paths become stale under `versions/v3_addons/` |
| `v4_addons/release_candidate/`, `snapshots/`, `m1_work/cache/` | release copies and caches | paths become stale under `versions/v4_addons/` |

## Same-commit edit rule

The `.gitignore` is rewritten in the **same commit as each batch that crosses a root anchor**. The
mapping is old pattern → new pattern, plus `archive/residue/` and `archive/duplicates/`. The D4 proof
maps the post-move ignored set back through `moves.csv` and compares it to `ignored_before.txt`.

## LFS check

`git lfs ls-files` produced no LFS entries.
