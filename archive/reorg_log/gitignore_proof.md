# `.gitignore` D4 proof (planned)

The move is simulated against a throwaway git repository containing only the proposed
`.gitignore`; no project file is moved to produce this proof. Every old ignored path is mapped
through `move_plan.csv` to its new path.

| Measure | Before | After |
|---|---:|---:|
| Ignored files (untracked) | 4180 | 4180 |
| Lost (old ignored, new not ignored) | — | **0** |
| Gained (old not ignored, new ignored) | — | **0** |
| Tracked files newly ignored | — | **0** |
| Pre-existing tracked-and-ignored `.log` files | 8 | 8 |

**Verdict: PASS**

## Pattern-level counts

| New pattern | New ignored count |
|---|---:|
| `/archive/residue/` | 2372 |
| `/versions/v2_work/d_results/cache/` | 1392 |
| `/versions/v2_work/d_results/oof/` | 130 |
| `/versions/v3_addons/results/wp8/cache/` | 120 |
| `/versions/v1_frozen/` | 68 |
| `/versions/v3_addons/results/*.npz` | 27 |
| `/versions/v3_addons/results/wp8/**/*.npz` | 11 |
| `/versions/v3_addons/results/wp8/models/` | 10 |
| `*.log` | 8 |
| `/versions/v2_work/literature_*.pdf` | 7 |
| `/evidence/notebook_backups/` | 6 |
| `/versions/v3_addons/results/sources/` | 6 |
| `/versions/v4_addons/release_candidate/` | 6 |
| `*.pre_v4` | 2 |
| `/data/telecom/*.csv` | 2 |
| `/docs/reference/*.docx` | 2 |
| `/versions/v4_addons/snapshots/` | 2 |
| `/docs/reference/tutorial*.ipynb` | 1 |
| `/versions/v2_work/a_bootstrap_calibration.csv` | 1 |
| `/versions/v2_work/a_bootstrap_test.csv` | 1 |
| `/versions/v2_work/a_selected_calibration.csv` | 1 |
| `/versions/v2_work/a_selected_test.csv` | 1 |
| `/versions/v2_work/b_assignments_calibration.csv` | 1 |
| `/versions/v2_work/b_assignments_test.csv` | 1 |
| `/versions/v2_work/c_subgroup_robustness.csv` | 1 |
| `/versions/v2_work/d_results/cv_manifest.csv` | 1 |
| `/versions/v2_work/d_results/cv_manifest.json` | 1 |
| `/versions/v2_work/literature_*.png` | 1 |
| `/versions/v3_addons/results/wp5_calibration_oof.csv` | 1 |
| `/versions/v3_addons/results/wp5_label_shift_raw.csv` | 1 |
| `/versions/v4_addons/CEO_BRIEF*` | 1 |
| `/versions/v4_addons/CEO_QA*` | 1 |
| `/versions/v4_addons/DISCLOSURE_CHECK.md` | 1 |
| `/versions/v4_addons/HUMAN_CHECKLIST.md` | 1 |

## Exact `.gitignore` change

| Old pattern | New pattern | Old count | New count |
|---|---|---:|---:|
| `/telecom/*.csv` | `/data/telecom/*.csv` | 2 | 2 |
| `/*.docx` | `/docs/reference/*.docx` | 2 | 2 |
| `/tutorial*.ipynb` | `/docs/reference/tutorial*.ipynb` | 1 | 1 |
| `/v1_frozen/` | `/versions/v1_frozen/` | 68 | 68 |
| `analysis_outputs/notebook_backups/` | `/evidence/notebook_backups/` | 6 | 6 |
| `v2_work/literature_*.pdf` | `/versions/v2_work/literature_*.pdf` | 7 | 7 |
| `v2_work/literature_*.png` | `/versions/v2_work/literature_*.png` | 1 | 1 |
| `v3_addons/results/sources/` | `/versions/v3_addons/results/sources/` | 6 | 6 |
| `v2_work/d_results/cv_manifest.csv` | `/versions/v2_work/d_results/cv_manifest.csv` | 1 | 1 |
| `v2_work/d_results/cv_manifest.json` | `/versions/v2_work/d_results/cv_manifest.json` | 1 | 1 |
| `v2_work/d_results/cache/` | `/versions/v2_work/d_results/cache/` | 1392 | 1392 |
| `v2_work/d_results/oof/` | `/versions/v2_work/d_results/oof/` | 130 | 130 |
| `v2_work/d_smoke/` | `/archive/residue/ (old path retired)` | 243 | 2372 |
| `v2_work/d_smoke_io/` | `/archive/residue/ (old path retired)` | 1841 | 2372 |
| `v2_work/c_smoke/` | `/archive/residue/ (old path retired)` | 5 | 2372 |
| `v3_addons/results/*.npz` | `/versions/v3_addons/results/*.npz` | 27 | 27 |
| `v3_addons/results/wp5_calibration_oof.csv` | `/versions/v3_addons/results/wp5_calibration_oof.csv` | 1 | 1 |
| `v3_addons/results/wp5_label_shift_raw.csv` | `/versions/v3_addons/results/wp5_label_shift_raw.csv` | 1 | 1 |
| `v3_addons/results/wp8/*.npz` | `/versions/v3_addons/results/wp8/*.npz` | 0 | 0 |
| `v3_addons/results/wp8/**/*.npz` | `/versions/v3_addons/results/wp8/**/*.npz` | 11 | 11 |
| `v3_addons/results/wp8/models/` | `/versions/v3_addons/results/wp8/models/` | 10 | 10 |
| `v3_addons/results/wp8/cache/` | `/versions/v3_addons/results/wp8/cache/` | 181 | 120 |
| `v4_addons/CEO_BRIEF*` | `/versions/v4_addons/CEO_BRIEF*` | 1 | 1 |
| `v4_addons/CEO_QA*` | `/versions/v4_addons/CEO_QA*` | 1 | 1 |
| `v4_addons/HUMAN_CHECKLIST.md` | `/versions/v4_addons/HUMAN_CHECKLIST.md` | 1 | 1 |
| `v4_addons/DISCLOSURE_CHECK.md` | `/versions/v4_addons/DISCLOSURE_CHECK.md` | 1 | 1 |
| `v4_addons/release_candidate/` | `/versions/v4_addons/release_candidate/` | 6 | 6 |
| `v4_addons/snapshots/` | `/versions/v4_addons/snapshots/` | 2 | 2 |
| `v4_addons/m1_work/cache/` | `/archive/residue/ (old path retired)` | 200 | 2372 |

## New rules

- `/archive/residue/` and `/archive/duplicates/` protect lifted run residue and any future duplicate archive.
- `/docs/reference/*.docx` keeps both course Word files ignored at their new destination (narrower than an unanchored `*.docx`).
- No tracked path becomes newly ignored; eight pre-existing tracked `.log` files stay tracked (tracked status wins).
- Some WP8 cache `.npz` paths match the broader `wp8/**/*.npz` rule, so the per-pattern cache count is 120 while all 181 old cache paths remain ignored.

Raw plan: `ignore_invariance_plan.txt`. The runtime proof after each batch is `ignore_invariance_R<n>.txt`.
