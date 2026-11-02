# F3 — QA, promote or fall back
Status: COMPLETED_ACCEPTED

Summary: F2 stopped at its guardrail, so the fallback rule governs F3. There is no candidate to QA or promote; instead the card proves that nothing moved: the four deliverables and the ledger are byte-identical to the frozen v2 records, the geometry receipt is still bound to the unchanged PPTX, and the fifteen renders still match the existing v2 visual receipt. **Visual QA was not performed in F3** and no promotion took place. F4 is skipped and F5–F7 continue on the frozen v2 artifacts.

## Evidence table

| number | value | source_file | source_key / formula | tag |
|---|---:|---|---|---|
| deliverables_checked | 4 |  | `4` | [R] |
| frozen_hash_mismatches | 0 |  | `deliverable hashes that differ from the D0 frozen record` | [E] |
| ledger_rows | 278 |  | `data rows in the unchanged claims ledger` | [E] |
| ledger_sha_matches_option_a | 1 |  | `ledger sha256 equals the Option A original recorded by D3` | [E] |
| pdf_page_count | 15 |  | `page count of the unchanged frozen PDF` | [E] |
| pdf_bytes | 846,608 |  | `byte size of the unchanged frozen PDF` | [E] |
| geometry_issue_count | 0 | `v2_work/office_geometry_check.json` | `issue_count` | [E] |
| geometry_slide_count | 15 | `v2_work/office_geometry_check.json` | `slide_count` | [E] |
| geometry_hash_matches_pptx | 1 |  | `the geometry receipt is bound to the sha256 of the unchanged PPTX` | [E] |
| visual_slides_reviewed | 15 |  | `slides covered by the existing v2 visual receipt` | [E] |
| visual_clipping_issues | 0 | `v2_work/visual_review.json` | `clipped_text_or_unintended_overlaps` | [E] |
| render_hash_mismatches | 0 |  | `renders that differ from the v2 visual receipt` | [E] |
| contact_sheet_hash_match | 1 |  | `contact sheet still matches the v2 visual receipt` | [E] |
| delivery_checks_hash_match | 1 |  | `delivery checks still match the v2 visual receipt` | [E] |
| candidate_qa_cycles | 0 |  | `no candidate existed, so no candidate QA cycle ran` | [E] |
| promotions | 0 |  | `no file was promoted over a project-root deliverable` | [E] |
| pre_v4_deliverable_backups | 0 |  | `no deliverable was edited, so no pre-v4 backup exists or is needed` | [E] |
| gates_present | 2 |  | `gate files present: H0_DECISIONS.md and H3_OPTION.txt only` | [E] |

## Hash receipt — frozen v2, unchanged

| file | bytes | sha256 (current = frozen) |
|---|---:|---|
| `philopateer.pdf` | 846,608 | `a51d2c0ff8aa6ebb0f679e680d6424b01cd7b95b9a0d23ae7a2eecc56de210ea` |
| `philopateer.pptx` | 1,310,666 | `a50a66fd77d062bdc45aeefb00ce8652b20b952de06dcb27e8ab4f15c37e46bc` |
| `philopateer.ipynb` | 1,857,125 | `aaa170b19923c087f9b38f85b546626b7465a3d17f5ae7037812c6aed5736b35` |
| `references.txt` | 18,843 | `b12fb18aafc83e2d599e15d04c689ee5cd85c10082c1761ab0c6f1d01606d361` |
| `analysis_outputs/claims_ledger.csv` | — | `b4dce03b43f6bd1b9ef3142759e0cb88682527af2f9f8824902521d88729c5b4` |

## QA chain disposition

| stage | performed in F3? | evidence |
|---|---|---|
| source / claim | frozen check | ledger rows and Option A hash reproduced |
| presentation | not applicable | no text applied; no candidate |
| geometry | frozen check | receipt bound to the unchanged PPTX sha256 |
| all-15-slide visual | **not performed** | existing v2 visual receipt re-verified against the unchanged renders |
| hash receipt | yes | hashes recorded here and refreshed in F7 |

## Acceptance checks

- QA chain on a candidate (source/claim → presentation → geometry → all-15-slide visual → receipt): **NOT PERFORMED** — no candidate exists under fallback A; this is stated, not implied.
- Source/claim: the ledger is unchanged at 278 rows and its sha256 reproduces the Option A original: **PASS**.
- Presentation/geometry: no text or shape changed; the existing geometry receipt (0 issues, 15 slides) is still bound to the unchanged PPTX hash: **PASS** (frozen state, not a new check).
- Visual: **visual QA not performed**; no new render exists. The 15 v2 renders and the contact sheet still match the existing visual receipt (0 mismatches): **PASS** (record re-verified).
- Rollback test: no `*.pre_v4` deliverable backups exist because nothing was edited; the live files equal the frozen v2 hashes, which is the rollback condition by construction: **PASS** (not applicable).
- Promotion: none; the promotion gate is not reached and no project-root file is written: **PASS**.
- Hash receipt: the four deliverables, the ledger, the 15-page PDF and the deck hashes equal the frozen v2 values: **PASS** (refreshed in F7).
- Gates: exactly `H0_DECISIONS.md` and `H3_OPTION.txt`; no H1/H2/H4: **PASS**.
- Boundary check clean after the card: **PASS**.

## Deviations from the brief

- The card executed the directive's fallback rule instead of the promotion path, because F2 stopped at its build-pipeline guardrail.
- No visual QA of a candidate was performed and none is claimed; the prior v2 visual receipt remains the only visual approval.

## Open questions / [DECISION NEEDED] items

- F4 is skipped (no slide numbers were added, so there is nothing to trace in the notebook).
- F5–F7 continue: the CEO brief carries the slide-11/13 corrections; F6 reports the disclosure; F7 issues the release receipt and the human checklist.

## Commands run

```bash
PY="C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe"; R="D:/progs/IDE/MainProjs/AI/GCI2026/finalA"
cd "$R/v4_addons/tools"
"$PY" -B -X utf8 boundary_check.py --card F3 --phase pre
"$PY" -B -X utf8 f3_fallback.py
"$PY" -B -X utf8 check_numbers.py --scan ../reports/F3_report.md
"$PY" -B -X utf8 boundary_check.py --card F3 --phase post
```

Environment: Python 3.11.9; verify_runtime pools: openblas 0.3.30 num_threads=6, openblas 0.3.30 num_threads=6; seed 20261045.

Boundary check: before/after hashes clean? yes (pre clean; post-check run after this report; only v4_addons/ written)
