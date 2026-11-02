# Canonical version and v1–v4 timeline

**Canonical delivery: frozen v2.0.0** — the model, policy, notebook, PDF, PPTX and claim ledger now in `submission/`. v3 and v4 add audit and release evidence; neither changes the delivered model. The v4 release label is `v4.0.0` with **fallback A**: frozen v2 artifacts retained.

## Truth hierarchy

1. Git history (dates/messages) — but this repository has **one initial import commit** `e8f6520` (31 Oct 2026) containing v1/v2/v3, then eight v4 commits. Git alone cannot date v1–v3.
2. Hash/delivery records — `analysis_outputs/delivery_checks.json`, `v4_addons/RELEASE_RECEIPT.md`, `v1_frozen/sha256_manifest.json`.
3. Handoff/reading docs — `FINAL_ASSESSMENT_HANDOFF.md`, `FINAL_ASSESSMENT_READING_NOTE.md`, `v3_addons/HANDBACK.md`, `v4_addons/STATE.md`.
4. mtimes — used only as a last tie-breaker.

## Timeline

| Version | What it is | Evidence | Supersedes or adds? |
|---|---|---|---|
| **v1** | First complete delivery: 9-code-cell notebook, 15-slide deck, 67-file frozen snapshot, original economics. | `v1_frozen/sha256_manifest.json` (67 entries, all PASS); v1 PDF 585,840 bytes / hash `b224ad…`; v1 notebook 1,364,089 bytes / `d94c68…`. | Superseded by v2. Retained only as F2. |
| **v2** | Frozen enhancement: 25 executed code cells, 15-page PDF, 15-slide PPTX, 278-row claim ledger, 87 features, sigmoid-calibrated LightGBM, value-aware policy, conditional economics. AUC unchanged at 0.6978. | `analysis_outputs/delivery_checks.json`; `FINAL_V2_UPGRADE_REPORT.md`; current F1 hashes; `v4_addons/RELEASE_RECEIPT.md` 4/4 equal. | **Supersedes v1** and produces the submission. |
| **v3** | Independent audit WP0–WP8: power, decision quality, prior sensitivity, ITT protocol, label-shift diagnostic, citations, handback, WP8 challenger. WP8 **rejected**; integration proposal only. | `v3_addons/HANDBACK.md`; `v3_addons/results/wp8_verification.json`; `v3_addons/prereg_wp8.md`. | **Adds to v2**; does not supersede the delivery and changes no submission hash. |
| **v4** | Integrity/release pass: yardstick reconciliation, ledger dry-run, integration proposal, reproducibility, CEO brief/Q&A, disclosure check, release receipt, M0/M1 feasibility. M1 closed Track M. Fallback A retained frozen v2. | `v4_addons/STATE.md` (`RELEASED_FALLBACK_A_v4.0.0`); `v4_addons/RELEASE_RECEIPT.md`; tag `v4.0.0` at `6b6f39a`. | **Adds to v2/v3**; does not supersede the delivery. `release/v4` keeps the pre-reorg layout. |

## Current artifact hashes (F1)

| File | Bytes | SHA256 |
|---|---:|---|
| `philopateer.pdf` | 846,608 | `a51d2c0ff8aa6ebb0f679e680d6424b01cd7b95b9a0d23ae7a2eecc56de210ea` |
| `philopateer.pptx` | 1,310,666 | `a50a66fd77d062bdc45aeefb00ce8652b20b952de06dcb27e8ab4f15c37e46bc` |
| `philopateer.ipynb` | 1,857,125 | `aaa170b19923c087f9b38f85b546626b7465a3d17f5ae7037812c6aed5736b35` |

All three match `v4_addons/RELEASE_RECEIPT.md` and `analysis_outputs/delivery_checks.json`; none match the v1 manifest. `references.txt` hash `b12fb18a…` also matches the v4 receipt.

## What “canonical” means here

- The **delivered** objects are v2. v4 is a release wrapper, not a new model or a new deck.
- v1 remains the rollback snapshot; v3/v4 are the audit trail.
- `release/v4` keeps the old layout and is not rewritten.
- Git tag `v4.0.0` is an annotated tag object `ea15eb0…` pointing at commit `6b6f39a`; branch `main` and `origin/main` are at `6b6f39a`.
