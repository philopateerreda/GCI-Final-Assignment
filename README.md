# Company A — Churn Prediction & Retention Targeting

**Retain contribution, not just customers.**

A calibrated LightGBM risk model, a value-weighted contact policy, a frozen evaluation protocol — and an independent audit that reports the results that weaken the case.

> **Test ROC-AUC 0.6978** [0.6899, 0.7055] · value-aware targeting captures **20.83%** of churned recurring value vs **14.62%** risk-only (**+42.4%**) · **+15.37%** relative under a 2% deployment prior.
> Sources: `evidence/summary.json` (AUC, AP, value capture, bootstrap); `docs/FINAL_ASSESSMENT_READING_NOTE.md` (2% deployment); `docs/FINAL_ASSESSMENT_HANDOFF.md` (intervals).

`Frozen v2 delivery · v3 audit · v4 release label v4.0.0 (fallback A) · economics conditional, not causal`

## What is in this package

| Folder | What it holds |
|---|---|
| `submission/` | The three F1 hand-ins: notebook, PDF, PPTX. Frozen; never edited or re-run. |
| `pipeline/` | The four Tier-C scripts that produced them, plus references and pins. Reproduction commands, not run. |
| `data/` | The two supplied CSVs. Git-ignored, local-only, **not redistributed**. |
| `evidence/` | Receipts, the 278-row claim ledger, 87-feature manifest, model bundle, tables, charts, renders. |
| `versions/` | v1 snapshot, frozen v2 work, v3 audit, v4 release wrapper. Canonical statement in `VERSIONS.md`. |
| `docs/` | Handoff, reading note, v2 upgrade report, course references. |
| `archive/` | Residue, the superseded README, and the full reorganization log. Nothing deleted. |

## Headline results

| Result | Value | Source |
|---|---|---|
| Test ROC-AUC | **0.6978** [0.6899, 0.7055] | `evidence/summary.json` |
| Average precision | 0.6883 | `evidence/summary.json` |
| Sample value capture, value-aware vs risk-only (1,500 of 15,000 rows per list) | 20.83% vs 14.62% → **+42.4%** [36.4%, 49.0%] | `evidence/summary.json`; `docs/FINAL_ASSESSMENT_READING_NOTE.md` |
| Relative value gain, 2% deployment prior | **+15.37%** [11.26%, 19.67%] | `docs/FINAL_ASSESSMENT_HANDOFF.md` |
| Conditional net, 100k cohort at 20% prevention | **+$3,747.08** [$2,761.37, $4,660.64] | `docs/FINAL_ASSESSMENT_HANDOFF.md` |
| Break-even prevention rate | 15.9993% | `docs/FINAL_ASSESSMENT_HANDOFF.md` |
| Features / population / sample churn | 87 / 100,000 × 100 / 49.562% | `evidence/feature_manifest.json`; `evidence/audit.json` |

The delivered model is a sigmoid-calibrated LightGBM with 385 trees, 31 leaves and learning rate 0.03, refit on all 75,000 non-test rows (`docs/FINAL_ASSESSMENT_HANDOFF.md`; `evidence/summary.json`). The frozen risk × value contact threshold is 1.7115 on the 2% prior (`docs/FINAL_ASSESSMENT_HANDOFF.md`). The split is 60,000 train + 15,000 validation + 10,000 calibration + 15,000 test (`evidence/tables/data_partitions.csv`).

## The submission

`submission/philopateer.ipynb` has 25 executed code cells and 0 errors; the deck is 15 PDF pages (846,608 bytes) and 15 slides (1,310,666 bytes) (`evidence/delivery_checks.json`). Every headline number is bound in a 278-row claim ledger (`evidence/claims_ledger.csv`; receipt in `evidence/delivery_checks.json`).

## Reproduce

- To **inspect**, no run is needed: `evidence/` and `versions/v2_work/final_metrics.json` carry every frozen result.
- To **replay**, follow `pipeline/README.md`; those commands are documented, not run during the reorganization.
- Environment: Python 3.11.9, six threads, seed `20261028` (`evidence/environment.json`).
- The supplied CSVs are not in the repository; place them under `data/telecom/` (git-ignored) before replaying.
- Do **not** run `submission/philopateer.ipynb`: it is the frozen record and its cells use old paths.

## The audit trail

- v2 tested 11 eligible challengers; none was promoted (`docs/FINAL_ASSESSMENT_HANDOFF.md`). The AUC stayed at 0.6978.
- v3's preregistered challenger was rejected: ΔAUC +0.000276 against a +0.003 gate (`versions/v4_addons/WP8_status_addendum.md`).
- v4's Track M found the frozen model already uses all 75,000 non-test rows: ΔS = 0, below its +0.0015 gate (`versions/v4_addons/reports/M1_report.md`).
- v4 released as **fallback A**: the delivered deck is unchanged; corrections are documented, not applied (`versions/v4_addons/STATE.md`).

## Caveats

- The churn **ranking** is measured. The policy gain is a **retrospective** value-capture comparison. The dollar net is a **conditional** scenario built on assumed prevention, cost, margin and horizon.
- No offer was tested: there is no causal retention lift and no measured profit. The +42.4% and +15.37% answer different questions and must not be mixed.
- The test split had been scored in v1; v2 reused those cached probabilities and discloses the reuse (`docs/FINAL_ASSESSMENT_HANDOFF.md`).
- The dataset belongs to the case provider and is **not redistributed**. The notebook retains its executed outputs; nothing was stripped.
- v1 remains the rollback snapshot (`versions/v1_frozen/`, git-ignored). Branch `pre-reorg` holds the old layout; see `archive/reorg_log/PATH_MAP.md`.

## Author

**Philopateer Reda** · Omnicampus `philopateer` · GCI 2026 — Company A case.
