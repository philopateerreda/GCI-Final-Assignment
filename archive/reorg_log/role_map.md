# Role map â€” every working-tree file, grouped

**4971 files / 575,499,423 bytes** in **56 groups**. Every file has exactly one group and one `move_plan.csv` row (D1).

Status vocabulary: `frozen`, `current`, `historical`, `superseded`, `scratch/residue`, `unclear_status`.

| Group | Files | Bytes | What it is | Produced by | Read by | Status | Evidence | Destination |
|---|---:|---:|---|---|---|---|---|---|
| `R-F1` | 3 | 4,014,399 | Three graded hand-in artifacts (notebook, PDF, PPTX) | v2 canonical run and PowerPoint export | assessor; account holder | frozen current | frozen_before.csv F1; analysis_outputs/delivery_checks.json | `submission/` |
| `R-COURSE` | 2 | 1,578,466 | Two course-supplied Word documents: assignment brief and dataset dictionary | GCI 2026 course | author and assessor | frozen supplied reference | extracted_text/README.docx.txt L1-L3, L98; ENG...docx.txt L1-L2; source_manifest.json | `docs/reference/` |
| `R-TUTORIAL` | 1 | 1,110,775 | Course-supplied tutorial notebook | GCI 2026 course | author | frozen supplied reference; ignored | extracted_text/tutorial (2).ipynb.txt cell 1 | `docs/reference/` |
| `R-DOCS` | 3 | 72,168 | Three v2-era explanatory documents | v2 documentation work | successor / reviewer | current context | FINAL_ASSESSMENT_HANDOFF.md; README.md L132 | `docs/` |
| `R-PIPE-C` | 4 | 385,983 | Four historical pipeline/build/restore entry points; every one needs more than a few path changes or a path-mapping layer | v1/v2 pipeline | historical provenance; pre-reorg reruns | historical Tier C after move | analysis_pipeline.py L43-L95, L581, L4184-L4209; build_notebook.py L12-L132; export_and_verify.py L13-L53; restore_v1.py L10-L91 | `pipeline/` |
| `R-META` | 2 | 19,189 | Environment pins and the verified reference/disclosure register | v2 documentation | reviewer; pipeline | current | requirements-python311.txt; FINAL_ASSESSMENT_HANDOFF.md Â§13 | `pipeline/` |
| `R-GIT` | 2 | 1,630 | Root git ignore/attribute controls | repository setup | git | current; .gitignore edited | git_state.md | `keep at root` |
| `R-README` | 1 | 9,888 | Old package README, superseded by the new one | v4 release | historical | superseded | README.md L1-L155; VERSIONS.md | `archive/superseded/` |
| `D-TELECOM` | 2 | 48,120,207 | Two supplied applicant-level CSVs (100,000 customers each) | Company A / course | canonical pipeline only | frozen supplied data; local-only, ignored | analysis_outputs/audit.json; .gitignore L16 | `data/telecom/` |
| `E-CORE` | 15 | 1,096,061 | Evidence receipts: audit, delivery checks, claims ledger, feature manifest, model selection, pilot design, environment, summary, contact sheet | canonical v1/v2 pipeline | README; assessor; v3/v4 audits | current frozen evidence | analysis_outputs/audit.json; delivery_checks.json; claims_ledger_build.json | `evidence/` |
| `E-CHARTS` | 9 | 1,635,187 | Nine evidence charts | analysis_pipeline.py figure() | deck; evidence review | current | analysis_outputs/delivery_checks.json chart checks | `evidence/charts/` |
| `E-MODELS` | 1 | 1,375,735 | Selected calibrated model bundle | analysis_pipeline.py | replay/audit | frozen current | model_selection.json; delivery_checks.json | `evidence/models/` |
| `E-BACKUPS` | 6 | 6,905,591 | Notebook execution backups from the v2 build | build_notebook.py | historical audit only | historical; ignored | .gitignore L28-L29; build_notebook.py L129-L132 | `evidence/notebook_backups/` |
| `E-RENDERS` | 15 | 1,621,376 | Fifteen reviewed deck renders | export_and_verify.py | visual receipt | current frozen render evidence | delivery_checks.json render_sha256 | `evidence/slide_renders/` |
| `E-TABLES` | 14 | 2,839,451 | Fourteen evidence tables and held-out predictions | analysis_pipeline.py | README; v3 audits | current frozen evidence | delivery_checks.json; claims_ledger_build.json | `evidence/tables/` |
| `V1-FROZEN` | 68 | 15,477,684 | Immutable 67-file v1 snapshot plus its SHA256 manifest | v1 freeze step | restore/audit; F2 verifier | frozen; ignored | v1_frozen/sha256_manifest.json; frozen_coverage.json | `versions/v1_frozen/` |
| `V2-DOCS` | 8 | 57,525 | Eight v2 workstream and checkpoint documents | v2 run | successor; README | current v2 record | v2_work/checkpoint2_summary.md; step0_report.md | `versions/v2_work/` |
| `V2-CODE` | 27 | 712,214 | Twenty-seven v2 scripts, including the embedded-module source and audits | v2 run | historical provenance | historical Tier C | v2_work/step0_report.md; v2_work/analysis_pipeline_v2.py | `versions/v2_work/` |
| `V2-LITERATURE` | 9 | 24,699,219 | Nine third-party literature files (seven PDFs, two PNGs), copyright-restricted | research | citation checks | reference; ignored | .gitignore L20-L22 | `versions/v2_work/` |
| `V2-LOGS` | 8 | 97,449 | Eight local run logs | v2 run | historical debugging | historical; ignored | .gitignore L59 | `versions/v2_work/` |
| `V2-CORE` | 65 | 10,069,452 | Remaining v2 root outputs: summaries, specs, gates, chart data, provenance | v2 run | v3/v4 audits; README | current v2 record | v2_work/final_metrics.json; final_batch_completion.json; checkpoint2_summary.md | `versions/v2_work/` |
| `V2-CHARTS` | 3 | 1,041,933 | Three v2 source charts copied into the deck evidence | v2 generate_visuals.py | evidence; deck | current | analysis_outputs/delivery_checks.json | `versions/v2_work/charts/` |
| `V2-C-CAL` | 4 | 612,278 | Workstream C calibration-partition audit tables | v2 workstream_c.py | v2 governance | current v2 evidence | v2_work/c_governance.md; c_summary.json | `versions/v2_work/c_calibration/` |
| `V2-C-TEST` | 5 | 609,795 | Workstream C test-partition audit tables | v2 workstream_c.py | v2 governance | current v2 evidence | v2_work/c_governance.md; v2_work/test_audit_started.json | `versions/v2_work/c_test/` |
| `V2-C-SMOKE` | 5 | 546,470 | Smoke fixture for Workstream C (smoke=True) | v2 workstream_c.py --smoke | historical debugging | scratch/residue | v2_work/c_smoke/c_governance.md line 1 | `archive/residue/v2_work/c_smoke/` |
| `V2-D-ROOT` | 49 | 154,123,375 | Workstream D root results: gate, folds, ablations, learning curves, manifests | v2 workstream_d.py | v3/v4 audits; README | current v2 evidence | v2_work/d_results/gate_d.csv; run_spec.json; final_metrics.json | `versions/v2_work/d_results/` |
| `V2-D-CACHE` | 1392 | 90,406,780 | 1,392 hash-named prediction caches supporting Workstream D provenance | v2 workstream_d.py | provenance only | regenerable, evidence-bound; ignored | v3_addons/results/wp8/bootstrap.json input list; .gitignore L31-L35 | `versions/v2_work/d_results/cache/` |
| `V2-D-FOLDS` | 290 | 631,393 | 290 fold recipes and fold scores | v2 workstream_d.py | paired comparison audit | current v2 evidence | v2_work/d_results/paired_fold_differences.csv | `versions/v2_work/d_results/folds/` |
| `V2-D-OOF` | 130 | 65,331,686 | 130 out-of-fold prediction arrays, hash-bound by v3 reports | v2 workstream_d.py | v3 WP1/WP3/WP5 provenance | current v2 evidence; ignored | v3_addons/reports/WP3_report.md L12-L21; .gitignore L32 | `versions/v2_work/d_results/oof/` |
| `V2-D-SMOKE` | 243 | 2,817,081 | Workstream D smoke-run outputs | v2 workstream_d.py --smoke | historical debugging | scratch/residue | .gitignore L36; v2_work/d_smoke/progress.json | `archive/residue/v2_work/d_smoke/` |
| `V2-D-SMOKE-IO` | 1841 | 11,187,208 | Workstream D I/O smoke outputs | v2 workstream_d.py smoke I/O | historical debugging | scratch/residue | .gitignore L37; v2_work/d_smoke_io/cv_manifest.json | `archive/residue/v2_work/d_smoke_io/` |
| `V2-PYCACHE` | 21 | 564,565 | Twenty-one Python bytecode caches | Python imports during v2 runs | none | residue | .gitignore L2-L3 | `archive/residue/v2_work/__pycache__/` |
| `V3-DOCS` | 6 | 32,529 | v3 handback, integration proposal, WP8 preregistration, protocol addendum, AGENTS | v3 audit WP7/WP8 | v4; README | current v3 record | v3_addons/HANDBACK.md; wp8_verification.json | `versions/v3_addons/` |
| `V3-REPORTS` | 11 | 86,735 | WP0-WP8 reports and pre-v4 backups | v3 audit | v4; reviewer | current v3 record | v3_addons/reports/WP8_report.md; v4_addons/STATE.md | `versions/v3_addons/reports/` |
| `V3-FIGURES` | 5 | 148,358 | Five WP figure drafts | v3 WP1-WP5 | reports | current supporting | v3_addons/REPRODUCIBILITY.md | `versions/v3_addons/figures/` |
| `V3-SRC` | 15 | 340,822 | Fourteen WP source scripts plus one validation-only PNG | v3 audit | reproduction | historical Tier C | v3_addons/REPRODUCIBILITY.md | `versions/v3_addons/src/` |
| `V3-TESTS` | 7 | 64,911 | Five new-code test modules and two fixtures | v3 audit | audit verification | historical Tier C | v3_addons/results/wp8_tests.json | `versions/v3_addons/tests/` |
| `V3-RESULTS` | 65 | 10,105,816 | v3 result JSON/CSV/PDF/TXT evidence and provenance | v3 WP0-WP8 | v4 audits; README | current v3 evidence | v3_addons/results/wp8_verification.json; final_new_code_tests.json | `versions/v3_addons/results/` |
| `V3-WP8-CACHE` | 121 | 15,232,269 | WP8 per-fold prediction caches and signature JSON | v3 WP8 | WP8 result/provenance JSON | evidence-bound; ignored | v3_addons/results/wp8/r0_f0.json L19-L49; .gitignore L42-L44 | `versions/v3_addons/results/wp8/cache/` |
| `V3-WP8-MODELS` | 10 | 13,749,357 | Ten WP8 outer-fold model text dumps | v3 WP8 | WP8 provenance | evidence-bound; ignored | .gitignore L44; wp8_model.json | `versions/v3_addons/results/wp8/models/` |
| `V3-SOURCES` | 6 | 2,124,650 | Six third-party source PDFs | v3 WP6 | citation verification | reference; ignored | .gitignore L23 | `versions/v3_addons/results/sources/` |
| `V3-NPZ` | 38 | 69,813,793 | Thirty-eight NPZ arrays outside `wp8/cache`; with the 60 cache arrays this is the full 98 | v3 audit | reports; reproducibility | current evidence; ignored | .gitignore L42-L44; REPRODUCIBILITY.md hashes | `versions/v3_addons/results/` |
| `V3-STARTED` | 60 | 3,840 | Sixty execution-start markers | v3 WP8 batch runner | none | run residue | .gitignore not required; H8 | `archive/residue/v3_addons/results/wp8/cache/` |
| `V4-DOCS` | 15 | 104,370 | Fifteen v4 closeout, yardstick, reproducibility, CEO and disclosure documents | v4 release | README index; CEO | current v4 record | v4_addons/STATE.md; RELEASE_RECEIPT.md | `versions/v4_addons/` |
| `V4-MANIFEST` | 1 | 65,600 | v4 hash/inventory manifest | v4 D1 | release audit | current v4 record | v4_addons/STATE.md D1 | `versions/v4_addons/` |
| `V4-GATES` | 2 | 5,241 | Two human-gate records | v4 F0 | release audit | current v4 record | v4_addons/STATE.md authorization record | `versions/v4_addons/gates/` |
| `V4-LEDGER` | 6 | 209,080 | Six alternative claims-ledger dry-runs | v4 D3 | integration decision | current v4 evidence | v4_addons/reports/D3_report.md | `versions/v4_addons/ledger_dryrun/` |
| `V4-M0` | 12 | 998,295 | Track M feasibility replay sandbox | v4 M0 | M1 decision | current v4 evidence | v4_addons/reports/M0_report.md | `versions/v4_addons/m0_sandbox/` |
| `V4-M1` | 3 | 4,857 | Track M learning-curve results and progress | v4 M1 | M1 report | current v4 evidence | v4_addons/reports/M1_report.md | `versions/v4_addons/m1_work/` |
| `V4-M1-CACHE` | 200 | 6,181,979 | Two hundred killed Track M fit caches | v4 M1 | none after track kill | run residue | v4_addons/STATE.md M1; .gitignore L74 | `archive/residue/v4_addons/m1_work/cache/` |
| `V4-RELEASE` | 6 | 4,037,803 | Six read-only release copies verified by receipt | v4 F7 | CEO hand-off | evidence-bound copies; ignored | v4_addons/RELEASE_RECEIPT.md L9-L18; .gitignore L66 | `versions/v4_addons/release_candidate/` |
| `V4-REPORTS` | 24 | 123,165 | Twenty-four v4 card reports | v4 release | STATE; reviewer | current v4 record | v4_addons/STATE.md | `versions/v4_addons/reports/` |
| `V4-RESULTS` | 68 | 947,440 | Sixty-eight v4 audit, ledger and render-check results | v4 tools | reports | current v4 evidence | v4_addons/reports/D0-D8 | `versions/v4_addons/results/` |
| `V4-SNAPSHOTS` | 2 | 872,350 | Allowed-changes policy and baseline snapshot | v4 preflight | v4 tools | evidence-bound; ignored | v4_addons/STATE.md D0 | `versions/v4_addons/snapshots/` |
| `V4-TOOLS` | 39 | 469,576 | Thirty-nine v4 audit/reporting tools | v4 release | reproduction | historical Tier C | v4_addons/REPRODUCIBILITY.md | `versions/v4_addons/tools/` |
| `R-PYCACHE` | 1 | 4,374 | Root Python bytecode cache | Python import | none | residue | .gitignore L2-L3 | `archive/residue/__pycache__/` |

## Individually named files that matter

| Path | Group | One-line answer |
|---|---|---|
| `analysis_outputs/audit.json` | E-CORE | 100,000 Ã— 100 merged rows, 49.562% sample churn, one-to-one ID join, source hashes. |
| `analysis_outputs/delivery_checks.json` | E-CORE | Delivery receipt: 15 PDF pages, 15 slides, 25 executed code cells, 0 errors, 278 claim rows, 0 geometry issues. |
| `analysis_outputs/claims_ledger_build.json` | E-CORE | Build receipt for the 278-row claim ledger and its source files. |
| `analysis_outputs/feature_manifest.json` | E-CORE | Exact 87-feature list, 4 categorical, 26 excluded fields. |
| `analysis_outputs/summary.json` | E-CORE | Consolidated v1/v2 metrics and the `v2_enhancement` block. |
| `v1_frozen/sha256_manifest.json` | V1-FROZEN | 67 root-relative entries; path base is `v1_frozen/`; all 67 PASS. |
| `v2_work/final_metrics.json` | V2-CORE | Consolidated frozen v2 numbers and protocol fingerprints (155,122 bytes). |
| `v2_work/d_results/gate_d.csv` | V2-D-ROOT | Eleven eligible challengers; none promoted. |
| `v3_addons/HANDBACK.md` | V3-DOCS | v3 terminal status; WP8 rejected, integration not applied. |
| `v3_addons/results/wp8_verification.json` | V3-RESULTS | WP8 promotion/gate/verification record and outside snapshot. |
| `v4_addons/STATE.md` | V4-DOCS | v4 release state `RELEASED_FALLBACK_A_v4.0.0` and authorization record. |
| `v4_addons/RELEASE_RECEIPT.md` | V4-DOCS | Six release copies, four frozen-v2 hashes equal, no upload. |
| `v4_addons/YARDSTICK.md` | V4-DOCS | One sheet reconciling 7,872 / 40,000 / 80,000 sample sizes and profit definitions. |

## Grouping method

Groups are path + schema signatures, not one group per file. The 2,414 JSON and 1,928 NPZ
files are machine outputs and were classified by directory role and schema; they were never
printed. Per-file membership is in `role_map.csv`; hashes and flags are in `inventory.csv`.
