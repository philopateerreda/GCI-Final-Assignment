# evidence — what proves the result

**What it answers:** what the frozen run produced and how the delivery is bound to it.

**Contents**

| Area | Files | What it is |
|---|---:|---|
| Core receipts | 15 | `audit.json`, `delivery_checks.json`, `claims_ledger.csv` (278 rows), `summary.json`, `feature_manifest.json` (87 features), `model_selection.json`, `pilot_design.json`, `environment.json`, `source_manifest.json`, `presentation_text.txt`, and supporting JSON/TXT |
| `charts/` | 9 | Evidence charts used by the deck |
| `tables/` | 14 | Model, policy, sensitivity, segment and held-out prediction tables |
| `models/` | 1 | Selected calibrated model bundle (`selected_model.joblib`) |
| `slide_renders/` | 15 | Reviewed 1600×900 deck renders |
| `notebook_backups/` | 6 | v2 execution backups (git-ignored) |

**Who reads it:** the assessor, the v3/v4 audit layers, and anyone checking a headline number.

**Current?** Yes — frozen v2 evidence. `delivery_checks.json` binds the PDF/PPTX/notebook, the 278-row ledger and the render hashes; `versions/v4_addons/RELEASE_RECEIPT.md` binds the release copies.

**How it is regenerated:** by `pipeline/analysis_pipeline.py` and `pipeline/export_and_verify.py`; commands are in `pipeline/README.md`, **not run** during the reorganization.

**Caveats**

- Several JSON keys still use old paths — e.g. `audit.json` says `telecom\Client.csv`, `delivery_checks.json` says `analysis_outputs/slide_renders/…`. These are stale by design; rewriting them would break the receipts. Resolve with `archive/reorg_log/path_map.csv`.
- `gate_d_passed: false` means no challenger was promoted. It is the correct frozen outcome, not a delivery failure.
- `notebook_backups/` is ignored and never pushed. The submitted notebook itself remains in `submission/` with its outputs intact.
- The charts and renders are historical artifacts; do not regenerate them in place.
