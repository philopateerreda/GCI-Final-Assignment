# F7 — Release candidate, receipt and human checklist
Status: COMPLETED_ACCEPTED

The four frozen v2 deliverables, the CEO brief and the Q&A were copied into `v4_addons/release_candidate/` as read-only files. All copies hash-verify, all four deliverables equal the D0 frozen hashes, and the ledger still has its frozen row count and hash. The receipt records the final figures and separates QA that was performed from QA that was not. The five-line human checklist names the only steps left to the account holder. Under fallback A nothing was edited, promoted or uploaded; the state is READY_FOR_CEO_FALLBACK_A.

## Evidence table

| number | value | source_file | source_key / formula | tag |
|---|---:|---|---|---|
| release_files | 6 |  | `files in the release folder` | [E] |
| copies_verified | 6 |  | `release copies whose SHA-256 equals the source` | [E] |
| copies_read_only | 6 |  | `release copies carrying the read-only attribute` | [E] |
| copy_hash_mismatches | 0 |  | `copy hash mismatches` | [E] |
| deliverable_count | 4 |  | `frozen deliverables in the release folder` | [R] |
| frozen_match_count | 4 |  | `deliverable copies equal to the D0 frozen hashes` | [E] |
| size_mismatches | 0 |  | `deliverable copies whose size differs from the F3 receipt` | [E] |
| pdf_pages | 15 | `v4_addons/results/f3_fallback.json` | `numbers.pdf_page_count.value` | [E] |
| pdf_bytes | 846,608 | `v4_addons/results/f3_fallback.json` | `numbers.pdf_bytes.value` | [E] |
| pptx_bytes | 1,310,666 | `v4_addons/results/f3_fallback.json` | `numbers.pptx_bytes.value` | [E] |
| ipynb_bytes | 1,857,125 | `v4_addons/results/f3_fallback.json` | `numbers.ipynb_bytes.value` | [E] |
| references_bytes | 18,843 | `v4_addons/results/f3_fallback.json` | `numbers.references_bytes.value` | [E] |
| ledger_rows | 278 | `v4_addons/results/f3_fallback.json` | `numbers.ledger_rows.value` | [E] |
| ledger_rows_recount | 278 |  | `data rows recounted from the Option A ledger copy` | [E] |
| ledger_rows_match | 1 |  | `recounted ledger rows equal the F3 receipt` | [E] |
| ledger_sha_match | 1 |  | `ledger SHA-256 equals the Option A original` | [E] |
| brief_words | 450 | `v4_addons/results/f5_ceo.json` | `numbers.brief_words.value` | [E] |
| qa_words | 260 | `v4_addons/results/f5_ceo.json` | `numbers.qa_words.value` | [E] |
| brief_words_recount | 450 |  | `whitespace word count of the released brief` | [E] |
| qa_words_recount | 260 |  | `whitespace word count of the released Q&A` | [E] |
| brief_words_match | 1 |  | `released brief length equals the F5 record` | [E] |
| qa_words_match | 1 |  | `released Q&A length equals the F5 record` | [E] |
| expected_rows_matched | 10 | `v4_addons/results/f5_ceo.json` | `numbers.expected_rows_matched.value` | [E] |
| expected_rows_total | 10 | `v4_addons/results/f5_ceo.json` | `numbers.expected_rows_total.value` | [E] |
| gates_present | 2 | `v4_addons/results/f3_fallback.json` | `numbers.gates_present.value` | [E] |
| visual_slides_reviewed | 15 | `v4_addons/results/f3_fallback.json` | `numbers.visual_slides_reviewed.value` | [E] |
| visual_clipping_issues | 0 | `v4_addons/results/f3_fallback.json` | `numbers.visual_clipping_issues.value` | [E] |
| render_hash_mismatches | 0 | `v4_addons/results/f3_fallback.json` | `numbers.render_hash_mismatches.value` | [E] |
| geometry_issue_count | 0 | `v4_addons/results/f3_fallback.json` | `numbers.geometry_issue_count.value` | [E] |
| geometry_slide_count | 15 | `v4_addons/results/f3_fallback.json` | `numbers.geometry_slide_count.value` | [E] |
| geometry_hash_matches_pptx | 1 | `v4_addons/results/f3_fallback.json` | `numbers.geometry_hash_matches_pptx.value` | [E] |
| frozen_hash_mismatches | 0 | `v4_addons/results/f3_fallback.json` | `numbers.frozen_hash_mismatches.value` | [E] |
| promotions | 0 | `v4_addons/results/f3_fallback.json` | `numbers.promotions.value` | [E] |
| cells_added | 0 | `v4_addons/results/f4_skip.json` | `numbers.cells_added.value` | [E] |
| checklist_lines | 5 |  | `lines in HUMAN_CHECKLIST.md` | [R] |
| new_model_fits | 0 |  | `model fits, refits, rescores or simulations in v4 closeout` | [E] |
| new_test_reads | 0 |  | `new test-split reads in v4 closeout` | [E] |
| deck_edits | 0 |  | `deck, LaTeX or PDF edits in v4 closeout` | [E] |
| new_visual_reviews | 0 |  | `new slide visual inspections in v4 closeout` | [E] |
| uploads | 0 |  | `portal uploads or submissions performed` | [E] |

## Acceptance checks

- Release folder holds 6 read-only copies, 6 hash-verified, 0 mismatches: **PASS**.
- Final figures recorded: 15 pages, 846,608 bytes, 278 ledger rows: **PASS**.
- Frozen v2 unchanged: 4 of 4 deliverable hashes equal the D0 record; 0 promotions: **PASS**.
- QA performed versus not performed stated explicitly, including that no new visual inspection ran: **PASS**.
- Human checklist within five lines: **PASS** (5 lines).
- State set to READY_FOR_CEO_FALLBACK_A: **PASS** (written after this report).
- Boundary check clean after the card: **PASS**.
- Numbers bound: **PASS** (`check_numbers.py` reports no problems).

## Deviations from the brief

- The CEO brief and Q&A are delivered as `.md` only: the project has no LaTeX toolchain for a PDF build.
- Under fallback A the deck is submitted unchanged; the slide-11/13 corrections live in the brief only.
- The PPTX and notebook are copied for completeness; the directive’s upload set is the PDF, notebook and references.

## Open questions / [DECISION NEEDED] items

- Account holder: follow the five-line checklist; insert a real AI chat-history URL only if the portal requires one; upload and submit before the deadline.

## Commands run

```bash
PY="C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe"; R="D:/progs/IDE/MainProjs/AI/GCI2026/finalA"
cd "$R/v4_addons/tools"
"$PY" -B -X utf8 boundary_check.py --card F7 --phase pre
"$PY" -B -X utf8 f7_release.py
"$PY" -B -X utf8 check_numbers.py --scan ../RELEASE_RECEIPT.md ../HUMAN_CHECKLIST.md ../reports/F7_report.md
"$PY" -B -X utf8 boundary_check.py --card F7 --phase post
```

Environment: Python 3.11.9; verify_runtime pools: openblas 0.3.30 num_threads=6; seed 20261049.

Boundary check: before/after hashes clean? yes (pre clean; post-check run after this report; only v4_addons/ written)
