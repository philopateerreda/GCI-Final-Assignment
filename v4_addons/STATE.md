# v4 STATE

**Project status:** RELEASED_FALLBACK_A_v4.0.0

_Last update (UTC): 2026-10-31T11:19:18.758461+00:00_

| Card | Status | Date | Report | Next gate | Note |
|---|---|---|---|---|---|
| D0 | COMPLETED_ACCEPTED | 2026-10-31 | reports/D0_report.md | none | hashes match; 42/43 section-9 checks reproduce; SE(gamma-hat) convention discrepancy acknowledged |
| D1 | COMPLETED_ACCEPTED | 2026-10-31 | reports/D1_report.md | none | 2 docs refreshed with .pre_v4 backups; addendum + MANIFEST_v4 (344 files) |
| D2 | COMPLETED_ACCEPTED | 2026-10-31 | reports/D2_report.md | none | YARDSTICK.md + yardstick.json; 2 G10 definition discrepancies reported (SE convention; pi* fully loaded) |
| D3 | COMPLETED_ACCEPTED | 2026-10-31 | reports/D3_report.md | none | A reproduces hash; B' 296 rows (+18); C 303 rows (+25); 0 retired |
| D4 | COMPLETED_ACCEPTED | 2026-10-31 | reports/D4_report.md | H3_OPTION.txt | INTEGRATION_PROPOSAL_v4.md; B' recommended; 3 DECISION NEEDED placeholders |
| D5 | COMPLETED_ACCEPTED | 2026-10-31 | reports/D5_report.md | none | WP1-WP5 commands/seeds/hashes; WP2 identities + WP3 closed forms re-checked; 485 numbers bound |
| D6 | COMPLETED_ACCEPTED | 2026-10-31 | reports/D6_report.md | none | queue lift 1.007/0.979/0.972/1.027 vs section 9; Floor + harm-gate DECISION NEEDED; HBS 403 is bot-block only, no edit |
| D7 | COMPLETED_ACCEPTED | 2026-10-31 | reports/D7_report.md | none | pi*(gamma) from exact v2 replay; 1.546417% is startup-included; startup-excluded 1.0361%; exclusive day-60 trigger table; label vs EM precision; variants deferred |
| D8 | COMPLETED_ACCEPTED | 2026-10-31 | reports/D8_report.md | none | Track D summary: 8 cards accepted; 4 open decisions; 4 gates unopened; check_numbers 0 problems; boundary clean |
| M0 | COMPLETED_ACCEPTED | 2026-10-31 | reports/M0_report.md | H1_APPROVED.txt | GO; final_metrics byte-identical; 52/278 ledger rows regeneration-dependent, 25 narrative, 201 unaffected; effort 1.5 d; check_numbers 0 problems; boundary clean |
| M1 | COMPLETED_REJECTED | 2026-10-31 | reports/M1_report.md | none | frozen model already refit on all 75k non-test rows; DeltaS=0 < +0.0015; curve upper 0.000943 < gate; Track M KILL |
| M2 | NOT_RUN_KILLED_BY_M1_GATE | 2026-10-31 |  |  | Track M killed at the M1 gate (DeltaS = 0 below the +0.0015 gate); not run. |
| M3 | NOT_RUN_KILLED_BY_M1_GATE | 2026-10-31 |  |  | Track M killed at the M1 gate; not run. |
| M4 | NOT_RUN_KILLED_BY_M1_GATE | 2026-10-31 |  |  | Track M killed at the M1 gate; not run. |
| M5 | NOT_RUN_KILLED_BY_M1_GATE | 2026-10-31 |  |  | Track M killed at the M1 gate; not run. |
| M6 | NOT_RUN_KILLED_BY_M1_GATE | 2026-10-31 |  |  | Track M killed at the M1 gate; not run. |
| I | NOT_STARTED |  |  |  |  |
| F0 | COMPLETED_ACCEPTED | 2026-10-31 | reports/F0_report.md |  | H0 + H3 written by delegation; M closure note; extrapolations bound, reviewer range omitted |
| F1 | COMPLETED_ACCEPTED | 2026-10-31 | reports/F1_report.md | none; F2 builds the B_PRIME candidate on copies | placeholders resolved; final slide 11/13 text; final ledger 296 rows (0 retired, 18 added, 0 changed); hash unchanged; A reproduces original |
| F2 | STOPPED_GUARDRAIL | 2026-10-31 | reports/F2_report.md | none; fallback A applies (F3 verifies frozen hashes, no promotion) | build pipeline cannot run: 0 LaTeX sources, 0 LaTeX engines; Office export forbidden for new/edited PDFs; fallback A |
| F3 | COMPLETED_ACCEPTED | 2026-10-31 | reports/F3_report.md | none; fallback A release continues with F5 | fallback A applied: frozen v2 hashes unchanged; no promotion; visual QA not performed in F3; ledger 278 rows Option A hash |
| F4 | COMPLETED_ACCEPTED | 2026-10-31 | reports/F4_report.md | none; F5 continues | F4 skipped under fallback A; notebook byte-identical (0 cells added or executed) |
| F5 | COMPLETED_ACCEPTED | 2026-10-31 | reports/F5_report.md | none; F6 disclosure report | CEO_BRIEF (450 words) + CEO_QA (260 words); all 10/10 expected rows match; no PDF (no LaTeX toolchain); fallback A wording |
| F6 | COMPLETED_ACCEPTED | 2026-10-31 | DISCLOSURE_CHECK.md | none; F7 release package | references.txt untouched (SHA and size match D0); disclosure quoted verbatim; HBS 403/200, Columbia 200; no URL invented |
| F7 | COMPLETED_ACCEPTED | 2026-10-31 | RELEASE_RECEIPT.md | CEO review 10-20 Nov; account holder upload by 28 Nov 2026, 11:30 UTC | release_candidate: 6 read-only copies verified; receipt and 5-line checklist written; STATE READY_FOR_CEO_FALLBACK_A |
| R0 | COMPLETED_ACCEPTED | 2026-10-31 | reports/R0_release_preflight.md |  | preconditions pass; boundary clean; 5 of 5 receipt hashes match; 0 files over 5 MB |
| R1 | COMPLETED_ACCEPTED | 2026-10-31 | reports/R1_prepush_checks.md |  | 0 secrets; 0 provider columns in derived CSVs; 0 local paths; README 149 tokens bound; 0 EOL mismatches |
| R3 | COMPLETED_ACCEPTED | 2026-10-31 | reports/R3_release_report.md |  | tag v4.0.0; release/v4 verified in a clean clone; 15 local-only bindings disclosed |

## Authorization record

- **2026-10-31, account holder (philopateer), quoted verbatim:** "I don't want to take decisions, just tell him what you see is the smartest move."
- This sentence is the account holder's authorization for the two gate files `v4_addons/gates/H0_DECISIONS.md` and `v4_addons/gates/H3_OPTION.txt` (v4 Closeout Directive, section 0; G6 amended for exactly these two files). If the account holder later creates, edits or deletes any gate file, their file wins.
- `H1_APPROVED.txt` and `H2_APPROVED.txt` were not created; Track M stays killed. H4 (upload and submission) is never the agent's step.
- **2026-10-31, account holder (philopateer):** asked for the v4 work to be pushed with commits and a better README, and delegated the release decisions to the orchestrator ("I don't want to take decisions, just tell him what you see is the smartest move."). This is the authorization for the v4 release directive, including its section-0 amendment to G1 for `README.md`, `.gitignore`, the release receipt, commits, one branch and one tag. If the account holder later changes any gate file or the repository, their action wins.

## Log

- 2026-10-31T08:22:52.827121+00:00 D0 -> COMPLETED_ACCEPTED (hashes match; 42/43 section-9 checks reproduce; SE(gamma-hat) convention discrepancy acknowledged)
- 2026-10-31T08:29:16.384758+00:00 D1 -> COMPLETED_ACCEPTED (2 docs refreshed with .pre_v4 backups; addendum + MANIFEST_v4 (344 files))
- 2026-10-31T08:38:30.980424+00:00 D2 -> COMPLETED_ACCEPTED (YARDSTICK.md + yardstick.json; 2 G10 definition discrepancies reported (SE convention; pi* fully loaded))
- 2026-10-31T08:47:18.475649+00:00 D3 -> COMPLETED_ACCEPTED (A reproduces hash; B' 296 rows (+18); C 303 rows (+25); 0 retired)
- 2026-10-31T08:48:06.132529+00:00 D3 -> COMPLETED_ACCEPTED (A reproduces hash; B' 296 rows (+18); C 303 rows (+25); 0 retired)
- 2026-10-31T08:51:30.496286+00:00 D4 -> COMPLETED_ACCEPTED (INTEGRATION_PROPOSAL_v4.md; B' recommended; 3 DECISION NEEDED placeholders)
- 2026-10-31T08:57:32.641763+00:00 D5 -> COMPLETED_ACCEPTED (WP1-WP5 commands/seeds/hashes; WP2 identities + WP3 closed forms re-checked; 485 numbers bound)
- 2026-10-31T09:00:33.375717+00:00 D6 -> COMPLETED_ACCEPTED (queue lift 1.007/0.979/0.972/1.027 vs section 9; Floor + harm-gate DECISION NEEDED; HBS 403 is bot-block only, no edit)
- 2026-10-31T09:09:48.278898+00:00 D7 -> COMPLETED_ACCEPTED (pi*(gamma) from exact v2 replay; 1.546417% is startup-included; startup-excluded 1.0361%; exclusive day-60 trigger table; label vs EM precision; variants deferred)
- 2026-10-31T09:13:46.950934+00:00 D8 -> COMPLETED_ACCEPTED (Track D summary: 8 cards accepted; 4 open decisions; 4 gates unopened; check_numbers 0 problems; boundary clean)
- 2026-10-31T09:26:49.470580+00:00 M0 -> COMPLETED_ACCEPTED (GO; final_metrics byte-identical; 52/278 ledger rows regeneration-dependent, 25 narrative, 201 unaffected; effort 1.5 d; check_numbers 0 problems; boundary clean)
- 2026-10-31T09:42:07.848154+00:00 M1 -> COMPLETED_REJECTED (frozen model already refit on all 75k non-test rows; DeltaS=0 < +0.0015; curve upper 0.000943 < gate; Track M KILL)
- 2026-10-31T09:42:08.082007+00:00 M2 -> NOT_STARTED (not run — Track M killed at M1)
- 2026-10-31T10:27:31.360782+00:00 M2 -> NOT_RUN_KILLED_BY_M1_GATE (Track M killed at the M1 gate (DeltaS = 0 below the +0.0015 gate); not run.)
- 2026-10-31T10:27:31.360782+00:00 M3 -> NOT_RUN_KILLED_BY_M1_GATE (Track M killed at the M1 gate; not run.)
- 2026-10-31T10:27:31.360782+00:00 M4 -> NOT_RUN_KILLED_BY_M1_GATE (Track M killed at the M1 gate; not run.)
- 2026-10-31T10:27:31.360782+00:00 M5 -> NOT_RUN_KILLED_BY_M1_GATE (Track M killed at the M1 gate; not run.)
- 2026-10-31T10:27:31.360782+00:00 M6 -> NOT_RUN_KILLED_BY_M1_GATE (Track M killed at the M1 gate; not run.)
- 2026-10-31T10:27:31.360782+00:00 F0 -> COMPLETED_ACCEPTED (H0 + H3 written by delegation; M closure note; extrapolations bound, reviewer range omitted)
- 2026-10-31T10:28:33.012196+00:00 M2 -> NOT_RUN_KILLED_BY_M1_GATE (Track M killed at the M1 gate (DeltaS = 0 below the +0.0015 gate); not run.)
- 2026-10-31T10:28:33.012196+00:00 M3 -> NOT_RUN_KILLED_BY_M1_GATE (Track M killed at the M1 gate; not run.)
- 2026-10-31T10:28:33.012196+00:00 M4 -> NOT_RUN_KILLED_BY_M1_GATE (Track M killed at the M1 gate; not run.)
- 2026-10-31T10:28:33.012196+00:00 M5 -> NOT_RUN_KILLED_BY_M1_GATE (Track M killed at the M1 gate; not run.)
- 2026-10-31T10:28:33.012196+00:00 M6 -> NOT_RUN_KILLED_BY_M1_GATE (Track M killed at the M1 gate; not run.)
- 2026-10-31T10:28:33.012196+00:00 F0 -> COMPLETED_ACCEPTED (H0 + H3 written by delegation; M closure note; extrapolations bound, reviewer range omitted)
- 2026-10-31T10:37:04.670833+00:00 F1 -> COMPLETED_ACCEPTED (placeholders resolved; final slide 11/13 text; final ledger 296 rows (0 retired, 18 added, 0 changed); hash unchanged; A reproduces original)
- 2026-10-31T10:37:28.343745+00:00 F1 -> COMPLETED_ACCEPTED (placeholders resolved; final slide 11/13 text; final ledger 296 rows (0 retired, 18 added, 0 changed); hash unchanged; A reproduces original)
- 2026-10-31T10:37:53.815948+00:00 F1 -> COMPLETED_ACCEPTED (placeholders resolved; final slide 11/13 text; final ledger 296 rows (0 retired, 18 added, 0 changed); hash unchanged; A reproduces original)
- 2026-10-31T10:38:21.045135+00:00 F1 -> COMPLETED_ACCEPTED (placeholders resolved; final slide 11/13 text; final ledger 296 rows (0 retired, 18 added, 0 changed); hash unchanged; A reproduces original)
- 2026-10-31T10:41:17.742368+00:00 F2 -> STOPPED_GUARDRAIL (build pipeline cannot run: 0 LaTeX sources, 0 LaTeX engines; Office export forbidden for new/edited PDFs; fallback A)
- 2026-10-31T10:42:58.224383+00:00 F3 -> COMPLETED_ACCEPTED (fallback A applied: frozen v2 hashes unchanged; no promotion; visual QA not performed in F3; ledger 278 rows Option A hash)
- 2026-10-31T10:43:27.333553+00:00 F4 -> COMPLETED_ACCEPTED (F4 skipped under fallback A; notebook byte-identical (0 cells added or executed))
- 2026-10-31T10:48:31.269721+00:00 F5 -> COMPLETED_ACCEPTED (CEO_BRIEF (472 words) + CEO_QA (260 words); all 10/10 expected rows match; no PDF (no LaTeX toolchain); fallback A wording)
- 2026-10-31T10:49:05.682075+00:00 F5 -> COMPLETED_ACCEPTED (CEO_BRIEF (450 words) + CEO_QA (260 words); all 10/10 expected rows match; no PDF (no LaTeX toolchain); fallback A wording)
- 2026-10-31T10:49:21.379929+00:00 F5 -> COMPLETED_ACCEPTED (CEO_BRIEF (450 words) + CEO_QA (260 words); all 10/10 expected rows match; no PDF (no LaTeX toolchain); fallback A wording)
- 2026-10-31T10:49:44.264669+00:00 F5 -> COMPLETED_ACCEPTED (CEO_BRIEF (450 words) + CEO_QA (260 words); all 10/10 expected rows match; no PDF (no LaTeX toolchain); fallback A wording)
- 2026-10-31T10:51:59.172874+00:00 F6 -> COMPLETED_ACCEPTED (references.txt untouched (SHA and size match D0); disclosure quoted verbatim; HBS 403/200, Columbia 200; no URL invented)
- 2026-10-31T10:54:13.359311+00:00 F7 -> COMPLETED_ACCEPTED (release_candidate: 6 read-only copies verified; receipt and 5-line checklist written; STATE READY_FOR_CEO_FALLBACK_A)
- 2026-10-31T11:19:18.758461+00:00 R0 -> COMPLETED_ACCEPTED (preconditions pass; boundary clean; 5 of 5 receipt hashes match; 0 files over 5 MB)
- 2026-10-31T11:19:18.758461+00:00 R1 -> COMPLETED_ACCEPTED (0 secrets; 0 provider columns in derived CSVs; 0 local paths; README 149 tokens bound; 0 EOL mismatches)
- 2026-10-31T11:19:18.758461+00:00 R3 -> COMPLETED_ACCEPTED (tag v4.0.0; release/v4 verified in a clean clone; 15 local-only bindings disclosed)
- 2026-10-31T11:19:18.758461+00:00 release -> RELEASED_FALLBACK_A_v4.0.0 (branch release/v4; annotated tag v4.0.0; clean-clone verification passed)
