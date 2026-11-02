# Release receipt — Company A retention proposal

**Status: READY_FOR_CEO_FALLBACK_A.** The four frozen v2 deliverables are unchanged, the CEO brief and Q&A are added, and no upload or submission has been performed.

Date: 2026-10-31. Release folder: `v4_addons/release_candidate/` (read-only copies).

## Release files

| file | bytes | hash |
|---|---:|---|
| `philopateer.pdf` | 846,608 | `a51d2c0ff8aa6ebb0f679e680d6424b01cd7b95b9a0d23ae7a2eecc56de210ea` |
| `philopateer.pptx` | 1,310,666 | `a50a66fd77d062bdc45aeefb00ce8652b20b952de06dcb27e8ab4f15c37e46bc` |
| `philopateer.ipynb` | 1,857,125 | `aaa170b19923c087f9b38f85b546626b7465a3d17f5ae7037812c6aed5736b35` |
| `references.txt` | 18,843 | `b12fb18aafc83e2d599e15d04c689ee5cd85c10082c1761ab0c6f1d01606d361` |
| `CEO_BRIEF.md` | 2,929 | `02f5a1ea0e0862b6eef6da7b9c4e55f2e0e2bf7d1599d7f9f671009fab2e81c1` |
| `CEO_QA.md` | 1,632 | `763217d07fb8987de8affd550b064324337de1e03615b164dee480fbb9e20dae` |

**Verification.** 6 files copied; 6 hash-verified; 6 read-only; 0 mismatches. 4 of 4 deliverables equal their D0 frozen hashes; 0 size mismatches.

## Final figures

- PDF: 15 pages, 846,608 bytes.
- PPTX: 15 slides, 1,310,666 bytes.
- Notebook: 1,857,125 bytes; supplement skipped (0 cells added).
- `references.txt`: 18,843 bytes; disclosure and link check in F6.
- Claims ledger (Option A): 278 rows, 278 recounted; SHA match 1; rows match 1.
- CEO brief: 450 words (450 recounted); Q&A: 260 words (260 recounted); match flags 1/1.
- Gate files present: 2.

## QA performed

- Hashes: 0 deliverable mismatches against the D0 frozen record; 0 promotions.
- Geometry: 0 issues over 15 slides; the receipt is bound to the PPTX hash (match 1).
- Visual: 15 slides covered by the existing v2 visual receipt; 0 clipping issues; 0 render hash mismatches; contact sheet and delivery checks match. **No new visual inspection was performed in v4**; the v2 receipt remains the only visual approval.
- Numbers: the CEO brief and Q&A pass `check_numbers.py`; 10 of 10 expected-value rows match.
- Disclosure: `references.txt` is untouched; the HBS item pages are bot-blocked rather than dead and the Columbia PDF is the accessible copy (F6).
- Notebook: byte-identical to the frozen record; 0 cells added.

## QA not performed

- No model fit, refit, rescore or simulation (0); no new test-split read (0).
- No deck, LaTeX or PDF edit (0); no candidate PDF; no promotion; no new visual review (0).
- No notebook cell appended or executed; no upload, portal entry or submission (0).

## Unchanged frozen-v2 hashes (D0 record vs release copy)

| file | frozen v2 (D0) | release candidate | equal |
|---|---|---|---|
| `philopateer.pdf` | `a51d2c0ff8aa6ebb0f679e680d6424b01cd7b95b9a0d23ae7a2eecc56de210ea` | `a51d2c0ff8aa6ebb0f679e680d6424b01cd7b95b9a0d23ae7a2eecc56de210ea` | equal |
| `philopateer.pptx` | `a50a66fd77d062bdc45aeefb00ce8652b20b952de06dcb27e8ab4f15c37e46bc` | `a50a66fd77d062bdc45aeefb00ce8652b20b952de06dcb27e8ab4f15c37e46bc` | equal |
| `philopateer.ipynb` | `aaa170b19923c087f9b38f85b546626b7465a3d17f5ae7037812c6aed5736b35` | `aaa170b19923c087f9b38f85b546626b7465a3d17f5ae7037812c6aed5736b35` | equal |
| `references.txt` | `b12fb18aafc83e2d599e15d04c689ee5cd85c10082c1761ab0c6f1d01606d361` | `b12fb18aafc83e2d599e15d04c689ee5cd85c10082c1761ab0c6f1d01606d361` | equal |

One-line status: **READY_FOR_CEO_FALLBACK_A** — frozen v2 unchanged; brief, Q&A and disclosure check added.

The account holder’s steps are in `v4_addons/HUMAN_CHECKLIST.md` (five lines).
