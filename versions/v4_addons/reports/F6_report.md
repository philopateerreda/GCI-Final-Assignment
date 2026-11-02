# F6 — AI-use disclosure and reference-link check
Status: COMPLETED_ACCEPTED

`references.txt` holds one AI-use paragraph naming Qoder. It was quoted verbatim into `DISCLOSURE_CHECK.md`, the AI tools evidenced by the project are listed, and the paragraph is complete for the work performed. No chat-history URL exists in the project and none was invented; a conditional replacement sentence is supplied for a portal that mandates one. The two HBS item pages answer 403 to a scripted client and 200 to a browser, and the Columbia PDF answers 200, so no reference link needs changing. The frozen file is untouched.

## Evidence table

| number | value | source_file | source_key / formula | tag |
|---|---:|---|---|---|
| references_lines | 120 | `references.txt` | `linecount` | [E] |
| references_bytes | 18,843 | `references.txt` | `byte size of the frozen references.txt` | [E] |
| frozen_reference_bytes | 18,843 | `v4_addons/results/d0_checks.json` | `references.txt size recorded in the D0 frozen hash receipt` | [E] |
| references_sha_matches_frozen | 1 | `references.txt` | `current references.txt SHA-256 equals the D0 handoff record` | [E] |
| references_bytes_match_frozen | 1 | `references.txt` | `current references.txt size equals the D0 handoff record` | [E] |
| references_edits | 0 | `references.txt` | `edits detected against the D0 frozen record` | [E] |
| disclosure_line | 75 | `references.txt` | `line of the AI-use disclosure paragraph in references.txt` | [E] |
| disclosure_words | 71 | `references.txt` | `whitespace word count of the disclosure paragraph` | [E] |
| qoder_mentions | 1 | `references.txt` | `lines in references.txt that name Qoder` | [E] |
| hbs_url_count | 2 | `v4_addons/results/d6_text_blocks.json` | `numbers.hbs_url_count.value` | [E] |
| hbs_status_script | 403 | `v4_addons/results/d6_text_blocks.json` | `numbers.http_status_blocked.value` | [E] |
| hbs_status_browser | 200 | `v4_addons/results/d6_text_blocks.json` | `numbers.http_status_ok.value` | [E] |
| columbia_status | 200 | `v4_addons/results/d6_text_blocks.json` | `numbers.http_status_ok.value` | [E] |
| tool_script_count | 33 |  | `Python tool scripts written under v4_addons/tools by the Qoder agent` | [E] |
| url_line_s4 | 36 | `references.txt` | `line of the S4 HBS item link` | [E] |
| url_line_s5 | 40 | `references.txt` | `line of the S5 HBS item link` | [E] |
| url_line_columbia | 86 | `references.txt` | `line of the S4 accessible Columbia copy` | [E] |

## Acceptance checks

- `references.txt` not edited: **PASS** — SHA match 1; size match 1; edits 0.
- Current disclosure quoted verbatim from line 75 (71 words): **PASS**.
- AI tools evidenced: Qoder agent runs (33 tool scripts) and local Python 3.11.9; no other tool named: **PASS**.
- Replacement sentence supplied only as a conditional template; no URL invented: **PASS**.
- Link status reported: HBS 403 scripted / 200 browser; Columbia 200 PDF: **PASS**.
- No Option C items; no submission action: **PASS**.
- Numbers bound: **PASS** (`check_numbers.py` reports no problems).
- Boundary check clean after the card: **PASS**.

## Deviations from the brief

- Link statuses are bound from the D6 receipt (observed 2026-10-31) and were re-confirmed live the same day; no value changed.
- The conditional replacement sentence is report-only; the frozen file is unchanged.
- No chat-history URL exists in the project; none is invented.

## Open questions / [DECISION NEEDED] items

- Account holder: if the portal requires a chat-history URL, insert a real Qoder conversation link (template in §4 of `DISCLOSURE_CHECK.md`); otherwise keep the current, accurate sentence.

## Commands run

```bash
PY="C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe"; R="D:/progs/IDE/MainProjs/AI/GCI2026/finalA"
cd "$R/v4_addons/tools"
"$PY" -B -X utf8 boundary_check.py --card F6 --phase pre
"$PY" -B -X utf8 f6_disclosure.py
"$PY" -B -X utf8 check_numbers.py --scan ../DISCLOSURE_CHECK.md ../reports/F6_report.md
"$PY" -B -X utf8 boundary_check.py --card F6 --phase post
# live link probes on 2026-10-31: curl default UA and Chrome UA on both HBS items; HEAD on the Columbia PDF
```

Environment: Python 3.11.9; verify_runtime pools: openblas 0.3.30 num_threads=6; seed 20261048.

Boundary check: before/after hashes clean? yes (pre clean; post-check run after this report; only v4_addons/ written)
