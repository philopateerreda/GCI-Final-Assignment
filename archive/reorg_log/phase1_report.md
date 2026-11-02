# Phase 1 — Read everything, then explain it

**Status: PASS**, with two disclosed concerns (course-document placement; notebook outputs). No project code executed, no project byte changed; `git status` shows only the untracked `finalA_reorg_log/`.

## Inventory

| Measure | Value |
|---|---:|
| Working-tree files in Phase-0 manifest | 4,971 |
| Working-tree bytes | 575,499,423 |
| Distinct SHA256 | 4,704 |
| Groups in `role_map.csv` | 56 |
| Tracked / ignored at baseline | 791 / 4,180 |
| `.git` files / bytes (after `pre-reorg`) | 1,330 / 18,045,027 |
| Root entries | 27 (18 files, 9 dirs) |

Every file has one `inventory.csv` row and one `role_map.csv` group. No file was left unclassified.

## How the files were read

- All `.md`, `.txt`, `.py` and notebook **sources**: full or section-level reading; 691-line handoff, v2 checkpoint/literature/governance, v3 handback/preregistration, v4 state/receipt/reproducibility/yardstick.
- 2,414 JSON / 1,928 NPZ: schema, key/shape and role, never printed. The 117.7 MiB manifest was hashed once.
- 15 notebooks: JSON structure and output scan; none executed.
- 5 F1 artifacts + 2 course DOCX + tutorial: text extracted to `extracted_text/`; no re-save.
- 92 `.py`: AST path scan; no import, no `py_compile`, no bytecode in the tree.

## Scans produced

| File | Result |
|---|---|
| `role_map.md` / `role_map.csv` | 56 groups; every file classified |
| `dependencies.csv` / `.md` | 3,049 path rows; 92 Python + 15 notebooks; 0 parse errors; all Tier C |
| `duplicates.csv` / `.md` | 243 SHA256 groups / 510 files; 132 tracked; 315 residue copies; **0 separate duplicate moves** |
| `secret_scan.md` / `.csv` | 0 credential-shaped hits; 73 user-path + 10,000 project-path + 12 email hits, all masked |
| `applicant_csv_profile.csv` | 16 applicant-level CSVs profiled as rows/columns only; **0 sample rows** |
| `notebook_output_scan.md` / `.csv` | 15 notebooks; 178 outputs flagged >20 rows or applicant columns; nothing stripped |
| `size_report.md` | 6 files >5 MiB; top 20 listed |
| `link_scan.md` / `.csv` | 45 external URLs, 59 `file:///` links, 655 repo-path refs, 202 distinct breaking paths |
| `git_state.md` | `.gitignore` anchors, 37 matching patterns, nested/LFS check, ignored baseline |

## What the package is

A GCI 2026 Company A churn/retention consulting proof of concept. The frozen v2 delivery is a 25-code-cell notebook, a 15-page PDF, a 15-slide editable PPTX, a 278-row claim ledger, 87 operational features, and a conditional value-aware policy. v1 is frozen in a 67-file snapshot. v3 is an independent audit (WP0–WP8; WP8 rejected). v4 is an integrity/release pass (`RELEASED_FALLBACK_A_v4.0.0`) that did not change the delivery.

## Concerns found

1. **Notebook outputs.** `philopateer.ipynb` has 60 outputs; 16 exceed 20 rows and expose applicant-level column names (`Customer_ID`, `income`, `ownrent`, etc.). The scan does not reproduce values. The notebook is F1, already in the public remote, and cannot be edited; this is disclosed, not silently stripped. A privacy decision is required before any push that keeps F1.
2. **Course-document placement.** Text extraction proves `README.docx` is the course assignment brief (title “Final Assignment README”, deadline, grading) and `ENG_Company _A_ Dataset Overview.docx` is the supplied dataset dictionary. They are not authored submission artifacts. The target layout's `submission/` and `data/` placements conflict with that evidence; the proposed tree puts both in `docs/reference/` (decision 1 at G1).
3. **No unclear files.** Every item has a role. `archive/unclear_status/` remains as an empty documented folder (README only), not a dumping ground.

## Artifacts

`inventory.csv`, `role_map.md`, `role_map.csv`, `dependencies.csv`, `dependencies.md`, `duplicates.csv`, `duplicates.md`, `secret_scan.md`, `secret_scan.csv`, `applicant_csv_profile.csv`, `notebook_output_scan.md`, `notebook_output_scan.csv`, `size_report.md`, `link_scan.md`, `link_scan.csv`, `git_state.md`, `ignored_before.txt`, `tracked_before.txt`, `gitignore_baseline.csv`, `extracted_text\`.
