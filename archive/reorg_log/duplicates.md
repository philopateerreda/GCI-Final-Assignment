# Duplicate scan

- Working-tree files scanned: **4971**
- Distinct SHA256: **4704**
- SHA256 groups with >1 path: **243**
- Files in duplicate groups: **510**
- Rows tracked by git: **132**
- Rows that move with smoke/cache residue: **315**
- Separate archive candidates (untracked, unreferenced, not residue): **0**

H7 rule: frozen/evidence-bound duplicates stay with their version and are flagged;
tracked duplicates stay tracked; smoke/cache copies move only with their residue batch.
No file is deleted.

## Largest duplicate groups

| SHA256 (first 12) | Bytes | Copies | Evidence-bound | Tracked copies | Paths |
|---|---:|---:|---|---:|---|
| `aaa170b19923` | 1,857,125 | 2 | yes | 1 | `philopateer.ipynb`<br>`v4_addons/release_candidate/philopateer.ipynb` |
| `4caefcbed46a` | 1,690,023 | 2 | yes | 1 | `analysis_outputs/tables/split_manifest.csv`<br>`v1_frozen/analysis_outputs/tables/split_manifest.csv` |
| `8eaaf9bc7976` | 1,626,703 | 2 | no | 0 | `v2_work/d_smoke/cv_manifest.json`<br>`v2_work/d_smoke_io/cv_manifest.json` |
| `8a59fe9ac8c2` | 1,375,735 | 2 | yes | 1 | `analysis_outputs/models/selected_model.joblib`<br>`v1_frozen/analysis_outputs/models/selected_model.joblib` |
| `62a4e47677f9` | 1,372,506 | 2 | yes | 0 | `analysis_outputs/notebook_backups/philopateer-20261028-123510.ipynb`<br>`v1_frozen/analysis_outputs/notebook_backups/philopateer-20261028-123510.ipynb` |
| `f3ae6fcb733a` | 1,369,505 | 2 | yes | 0 | `analysis_outputs/notebook_backups/philopateer-20261028-121816.ipynb`<br>`v1_frozen/analysis_outputs/notebook_backups/philopateer-20261028-121816.ipynb` |
| `77543f697514` | 1,368,527 | 2 | yes | 0 | `analysis_outputs/notebook_backups/philopateer-20261028-121454.ipynb`<br>`v1_frozen/analysis_outputs/notebook_backups/philopateer-20261028-121454.ipynb` |
| `ac7a5854d9cc` | 1,367,660 | 2 | yes | 0 | `analysis_outputs/notebook_backups/philopateer-20261028-122457.ipynb`<br>`v1_frozen/analysis_outputs/notebook_backups/philopateer-20261028-122457.ipynb` |
| `d94c6885650c` | 1,364,089 | 2 | yes | 0 | `analysis_outputs/notebook_backups/philopateer-20261028-205244.ipynb`<br>`v1_frozen/philopateer.ipynb` |
| `a50a66fd77d0` | 1,310,666 | 2 | yes | 1 | `philopateer.pptx`<br>`v4_addons/release_candidate/philopateer.pptx` |
| `c525318b3e58` | 1,130,545 | 2 | yes | 1 | `analysis_outputs/tables/heldout_predictions.csv`<br>`v1_frozen/analysis_outputs/tables/heldout_predictions.csv` |
| `9e02694d5c26` | 967,934 | 2 | yes | 0 | `v2_work/literature_Ascarza2016.pdf`<br>`v3_addons/results/sources/ascarza_2016_source.pdf` |
| `a51d2c0ff8aa` | 846,608 | 2 | yes | 1 | `philopateer.pdf`<br>`v4_addons/release_candidate/philopateer.pdf` |
| `05ed8c8344cb` | 646,624 | 2 | yes | 1 | `v2_work/a_bootstrap_test.csv`<br>`v4_addons/m0_sandbox/a_replay/a_bootstrap_test.csv` |
| `e7e7ffbd5197` | 630,291 | 2 | no | 2 | `analysis_outputs/charts/risk_value_tradeoff.png`<br>`v2_work/charts/risk_value_tradeoff.png` |
| `c97d9bc6a2df` | 520,124 | 2 | yes | 1 | `v2_work/c_subgroup_robustness.csv`<br>`v2_work/c_test/c_subgroup_robustness.csv` |
| `958565aacb5d` | 426,453 | 2 | yes | 0 | `v2_work/d_results/oof/g1_temporal_r1_f2.npz`<br>`v2_work/d_results/oof/nested_lgbm_r1_f2.npz` |
| `3b04d384c08e` | 425,999 | 2 | yes | 0 | `v2_work/d_results/oof/g1_temporal_r1_f3.npz`<br>`v2_work/d_results/oof/nested_lgbm_r1_f3.npz` |
| `806c218f920c` | 425,870 | 2 | yes | 0 | `v2_work/d_results/oof/g3_billing_gaps_r0_f4.npz`<br>`v2_work/d_results/oof/nested_lgbm_r0_f4.npz` |
| `3aef7d43ed66` | 366,760 | 2 | no | 0 | `v2_work/d_smoke/cv_manifest.csv`<br>`v2_work/d_smoke_io/cv_manifest.csv` |
| `87ca9f1b0e14` | 353,674 | 2 | no | 2 | `analysis_pipeline.py`<br>`v2_work/analysis_pipeline_v2.py` |
| `af8f7f5ed01b` | 224,790 | 2 | no | 2 | `analysis_outputs/charts/value_capture_curve.png`<br>`v2_work/charts/value_capture_curve.png` |
| `78598ec2ce22` | 186,852 | 2 | no | 2 | `analysis_outputs/charts/scenario_waterfall.png`<br>`v2_work/charts/scenario_waterfall.png` |
| `1d14a4fea10a` | 155,122 | 2 | yes | 2 | `v2_work/final_metrics.json`<br>`v4_addons/m0_sandbox/final_metrics/final_metrics.json` |
| `d8343df876f8` | 146,298 | 2 | yes | 1 | `analysis_outputs/charts/model_validation.png`<br>`v1_frozen/analysis_outputs/charts/model_validation.png` |

## Decision

The duplicate groups are frozen/evidence-bound copies, tracked duplicates, or smoke/cache
copies that already move with residue. The proposal therefore sends **no file to a separate
`archive/duplicates/` action**. Tracked copies stay tracked (D4); the frozen/receipt-bound copies
stay with their version. Full per-file data: `duplicates.csv`.
