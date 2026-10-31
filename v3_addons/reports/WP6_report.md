# WP6 — Source corrections and citation hygiene
Status: DONE

Inputs:
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/references.txt` — SHA-256 `b12fb18aafc83e2d599e15d04c689ee5cd85c10082c1761ab0c6f1d01606d361`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/wp5_label_shift.json` — SHA-256 `3a4d94fe806c00421f53688c2000bfb2293ecc16320dbb795d9b8375a8a9338e`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/reports/WP5_report.md` — SHA-256 `7eadb863a180e4f951734b6c6a326f0e0a0809517c44f5cd73abb9ce644fdf61`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/sources/ascarza_2016_source.pdf` — SHA-256 `9e02694d5c2699ec9b59dc4a03ad42d3eca8d3c39a461a7e362bce87d7ab9e8c`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/sources/ascarza_2016_source.txt` — SHA-256 `0cfda524a29346e7db5640034deda927f4150d2f2b1eaa86688a0fd504aea326`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/sources/bouckaert_frank_2004.pdf` — SHA-256 `ff5379a16cfb0f64bb80900c809f8c74ed01bf1c4c22cc9f54597f9e94fbb386`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/sources/bouckaert_frank_2004.txt` — SHA-256 `f057ac41e049f2c29abc362db9c755e4bdd2f5567107aa0766c7974da9e13443`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/sources/nadeau_bengio_source.pdf` — SHA-256 `e3a1ec656312feba41dec7fa474fe8b0780472bb77427655e1fee6c3f664df54`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/sources/nadeau_bengio_source.txt` — SHA-256 `3ae5f35cbb5e329ce21b7b01d20f654fe3b41bf41a848de2943dfe6e2a761967`.

Population / assumptions:
[A] Prevention priors remain assumed inputs, not learned treatment effects.
[E] Every access scope is recorded; inaccessible pages are not cited as read.

Method (≤10 lines)
[E] Opened the package source, arXiv metadata, PubMed abstract and accessible papers; recorded exactly the inspected coverage. Drafted conditional append text without editing the submitted references.

Results:
[E] EMP defaults alpha=6/beta=14; arXiv identifier belongs to Höppner et al.
[E] Ascarza quotation is supported by the accessible paper, not the blocked HBS item.
[E] Nadeau manuscript/published-version distinction and heuristic repeated-CV correction are explicit.
[E] M5 remains abstract-only; no full-text formula-verification claim is supported.
[R] Only M9 is a new conditional Option-C citation; Options A/B need no appended source.

Acceptance checks:
[E] PASS: all_read_statuses_present
[E] PASS: only_used_new_source_marked_Y
[E] PASS: emp_default_verified
[E] PASS: arxiv_identity_verified
[E] PASS: ascarza_quote_supported_by_accessible_copy
[E] PASS: blocked_pages_not_claimed_read
[E] PASS: no_duplicate_existing_citations
[E] PASS: no_root_reference_edit

Deviations from brief:
[E] HBS access returned 403; Springer access returned 303. Accessible copies and verified version labels are used instead.

Claims now allowed:
[E] The verified default, citation identity, intervention-specific rates and stated source coverage.

Claims still forbidden:
[R] Unread-source content, a Company A prevention estimate, changed CV gates or integrated references.

Open questions for human: [E] None; integration remains a separate human decision.
