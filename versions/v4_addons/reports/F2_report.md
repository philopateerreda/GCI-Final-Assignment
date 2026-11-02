# F2 — Build the B′ candidate on copies
Status: STOPPED_GUARDRAIL

Summary: the F2 build pipeline cannot be run. The repository contains no LaTeX source and no LaTeX engine is installed; the only PDF path in the handoff is PowerPoint COM export, which the account holder's standing instruction forbids for any new or edited PDF. The card therefore stops at its own stop condition and the directive's fallback rule applies: Option A — the frozen v2 deliverables stay unchanged, the slide-11/13 corrections move into the CEO brief only, F4 is skipped, and F5–F7 continue.

## Evidence table

| number | value | source_file | source_key / formula | tag |
|---|---:|---|---|---|
| latex_source_files | 0 |  | `count of .tex/.sty/.cls/.bib/.ltx files outside .git and __pycache__` | [E] |
| latex_engines_probed | 5 |  | `5` | [R] |
| latex_engines_found | 0 |  | `engines actually available to build a PDF` | [E] |
| office_export_scripts | 2 |  | `PowerPoint COM export scripts present in the handoff` | [E] |
| deliverables_expected | 4 |  | `4` | [R] |
| candidate_files_created | 0 |  | `no candidate file was created: the stop condition was met first` | [E] |
| frozen_pdf_pages | 15 |  | `page count of the unchanged frozen PDF` | [E] |
| frozen_pdf_bytes | 846,608 |  | `byte size of the unchanged frozen PDF` | [E] |
| frozen_pptx_slides | 15 |  | `slide count of the unchanged frozen PPTX` | [E] |
| pdf_page_cap | 15 |  | `15` | [R] |
| pdf_byte_cap | 10,000,000 |  | `10000000` | [R] |

## Pipeline probe detail

- LaTeX source files found: 0 (`.tex`, `.sty`, `.cls`, `.bib`, `.ltx`; `.git` and `__pycache__` excluded).
- Engines probed: `pdflatex`, `xelatex`, `lualatex`, `tectonic`, `latexmk`; none on `PATH` or in the standard install directories.
- Office export scripts present: `export_and_verify.py` and `v2_work/export_and_verify_v2.py` (PowerPoint COM).
- `python-pptx` version available for read-only inspection: `1.0.2`.
- The account holder's standing instruction overrides the Office export step for any new or edited PDF: LaTeX only.

## Acceptance checks

- Copy the four deliverables, the LaTeX sources and the ledger under `v4_addons/integration/candidate/`: **NOT ATTEMPTED** — the stop condition was met before any copy.
- Apply the identical text to the PPTX and to a LaTeX-built PDF: **NOT ATTEMPTED** — there is no LaTeX source and no engine.
- Candidate PDF LaTeX-only, at most 15 pages and below 10,000,000 bytes: **NOT ATTEMPTED**.
- Candidate ledger matches the F1 dry-run row-for-row: **NOT ATTEMPTED** — no ledger was copied.
- Stop condition: **MET** — `latex_source_files` = 0, `latex_engines_found` = 0; the two Office export scripts are the only build path and are forbidden for this PDF.
- Fallback rule applied: **YES** — Option A; frozen v2 unchanged; corrections carried in the CEO brief only; F4 skipped; F5–F7 continue.
- Boundary check clean before and after: **PASS**.

## Deviations from the brief

- None. The card stopped at its own stop condition; no candidate, no deck edit, no PDF export and no notebook change.

## Open questions / [DECISION NEEDED] items

- F3 records the fallback: it verifies the frozen v2 hashes, performs no promotion, and passes the release to F5–F7.
- F5 carries the slide-11 conditional-interval correction and the slide-13 capacity bridge in the CEO brief only.

## Commands run

```bash
PY="C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe"; R="D:/progs/IDE/MainProjs/AI/GCI2026/finalA"
cd "$R/v4_addons/tools"
"$PY" -B -X utf8 boundary_check.py --card F2 --phase pre
"$PY" -B -X utf8 f2_pipeline_probe.py
"$PY" -B -X utf8 check_numbers.py --scan ../reports/F2_report.md
"$PY" -B -X utf8 boundary_check.py --card F2 --phase post
```

Environment: Python 3.11.9; verify_runtime pools: openblas 0.3.30 num_threads=6, openblas 0.3.30 num_threads=6; seed 20261044.

Boundary check: before/after hashes clean? yes (pre clean; post-check run after this report; only v4_addons/ written)
