# VERSIONS — v1 → v4 timeline

**Canonical delivery: frozen v2** — the model, policy, notebook, PDF, PPTX and claim ledger now in `submission/` and `evidence/`. v3 adds an independent audit; v4 is a release/integrity wrapper. Neither changes the delivered model. The release label is `v4.0.0` with **fallback A**: frozen v2 artifacts retained, no promotion.

## Timeline

| Version | What it is | Evidence | Adds / supersedes |
|---|---|---|---|
| **v1** | First complete delivery: 9-code-cell notebook, 15-slide deck, 67-file frozen snapshot, original economics. | `versions/v1_frozen/sha256_manifest.json` (67 entries, all PASS); v1 PDF 585,840 bytes / `b224ad…`; v1 notebook 1,364,089 bytes / `d94c68…` | Superseded by v2; retained as F2 rollback |
| **v2** | Frozen enhancement: 25 executed code cells, 15-page PDF, 15-slide PPTX, 278-row claim ledger, 87 features, sigmoid-calibrated LightGBM, value-aware policy, conditional economics. AUC unchanged at 0.6978. | `evidence/delivery_checks.json`; `docs/FINAL_V2_UPGRADE_REPORT.md`; `versions/v4_addons/RELEASE_RECEIPT.md` (4/4 equal) | **Supersedes v1**; produces the submission |
| **v3** | Independent audit WP0–WP8: power, decision quality, prior sensitivity, ITT protocol, label-shift diagnostic, citations, handback, challenger WP8. WP8 **rejected**. | `versions/v3_addons/HANDBACK.md`; `versions/v3_addons/results/wp8_verification.json`; `versions/v3_addons/prereg_wp8.md` | **Adds to v2**; changes no submission hash |
| **v4** | Integrity/release pass: yardstick reconciliation, ledger dry-run, integration proposal, reproducibility, CEO brief/Q&A, disclosure check, release receipt, M0/M1 feasibility. M1 closed Track M (ΔS = 0 below gate). Fallback A retained frozen v2. | `versions/v4_addons/STATE.md` (`RELEASED_FALLBACK_A_v4.0.0`); `versions/v4_addons/RELEASE_RECEIPT.md`; tag `v4.0.0` | **Adds to v2/v3**; does not supersede the delivery |

## Git facts (2026-11-02)

- `e8f6520` (2026-10-31) is a **single initial import** containing v1, v2 and v3. Git cannot date v1–v3 separately; artifact hashes and handoff docs do.
- Eight v4 commits follow; `6b6f39a` (2026-10-31) is the released commit.
- Annotated tag `v4.0.0` is object `ea15eb0…`, pointing at `6b6f39a`.
- Branch `release/v4` and branch `pre-reorg` are both at `6b6f39a`. **`release/v4` keeps the pre-reorg layout** and is not rewritten by this reorganization.
- The reorganized `main` is the R1–R8 sequence; see `archive/reorg_log/STATE.md` for the exact HEAD.

## Delivered artifact hashes (F1)

| File | Bytes | SHA256 | Also in |
|---|---:|---|---|
| `submission/philopateer.pdf` | 846,608 | `a51d2c0ff8aa6ebb0f679e680d6424b01cd7b95b9a0d23ae7a2eecc56de210ea` | `versions/v4_addons/RELEASE_RECEIPT.md` |
| `submission/philopateer.pptx` | 1,310,666 | `a50a66fd77d062bdc45aeefb00ce8652b20b952de06dcb27e8ab4f15c37e46bc` | `versions/v4_addons/RELEASE_RECEIPT.md` |
| `submission/philopateer.ipynb` | 1,857,125 | `aaa170b19923c087f9b38f85b546626b7465a3d17f5ae7037812c6aed5736b35` | `versions/v4_addons/RELEASE_RECEIPT.md` |

`pipeline/references.txt` is hash `b12fb18a…` in the same receipt. None of the three F1 files matches the v1 manifest.

## What “canonical” means

- **Delivered objects:** v2. **Audit trail:** v3. **Release wrapper:** v4. **Rollback:** v1.
- v4 documents corrections it did **not** apply (fallback A); the deck is unchanged. See `versions/v4_addons/INTEGRATION_PROPOSAL_v4.md`.
- `versions/v1_frozen/`, `versions/v4_addons/release_candidate/`, caches and literature remain git-ignored and local-only.
- Full move history: `archive/reorg_log/PATH_MAP.md` and `path_map.csv`.
