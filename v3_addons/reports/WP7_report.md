# WP7 — Integration proposal and human decision gate
Status: DONE

Inputs:
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/inventory.json` — SHA-256 `c1ec315ff45436d914af3061f9e9d201d34e7d9b8dddd825c2672d9bba2f5369`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/wp1_power.json` — SHA-256 `1342bb553dfd24e4697d210d141392f32f0ac8b43f66ea3627db95622d714305`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/wp2_evsi.json` — SHA-256 `cd64fe05f11e974916e461d6f12764cff53ecd7f62fb8a1e461d966611c2e405`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/wp3_roi_band.json` — SHA-256 `96aa9a75869c53079e1442a26f1f3d08f5261d735e61a5195a658955843a5dd1`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/wp4_protocol.json` — SHA-256 `1fd31cc4461349db720ba88de079a0f0f7d15f3963b283b121af6e7af77676e9`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/wp5_label_shift.json` — SHA-256 `3a4d94fe806c00421f53688c2000bfb2293ecc16320dbb795d9b8375a8a9338e`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/wp6_citations.json` — SHA-256 `26a248816181b2b00365547974e50e2802f49102548f98c5ff827ef50f5ddee1`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/philopateer.pptx` — SHA-256 `a50a66fd77d062bdc45aeefb00ce8652b20b952de06dcb27e8ab4f15c37e46bc`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/philopateer.pdf` — SHA-256 `a51d2c0ff8aa6ebb0f679e680d6424b01cd7b95b9a0d23ae7a2eecc56de210ea`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/philopateer.ipynb` — SHA-256 `aaa170b19923c087f9b38f85b546626b7465a3d17f5ae7037812c6aed5736b35`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/references.txt` — SHA-256 `b12fb18aafc83e2d599e15d04c689ee5cd85c10082c1761ab0c6f1d01606d361`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/analysis_outputs/claims_ledger.csv` — SHA-256 `b4dce03b43f6bd1b9ef3142759e0cb88682527af2f9f8824902521d88729c5b4`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/write_boundary_before.json` — SHA-256 `e7616e3f66541f3fa5e6f6a625702c29034c5b9e6d1b7d452d1bf5e3e3f94bc1`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/final_new_code_tests.json` — SHA-256 `32ff1543fd942b966fcba72170cc75749fcbc9790f3e785bc3a43e3851649931`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/wp6_references_append_option_c.txt` — SHA-256 `42f6a6a7141bff2af8a5aa343264a34e173243cf3fb90840cc4c31dfadbaaa31`.
- [E] `D:/progs/IDE/MainProjs/AI/GCI2026/finalA/v3_addons/results/wp7_readonly_deck_ledger.json` — SHA-256 `741759c8fae3e023b9913f43ae26a13d8c47fdc7fe21d444f7eff74e6e67db7a`.

Population / assumptions:
[A] All financial, power and monitoring conclusions retain the assumptions in their individual reports.
[E] Current deck/ledger read only: 15 slides and 278 data rows.

Method (≤10 lines)
[E] Read the actual presentation order and native text; matched candidate replacements to deterministic ledger row aliases and source keys. Prepared options, exact replacements, handback and file manifest. Compared every outside-sandbox file to the original 4,246-file baseline; no integration or submission.

Results:
[E] WP0–WP6 terminal reports are present; scientific failures remain explicit.
[E] Exactly 15 current slides; replacements only.
[E] All outside files unchanged; frozen delivery hashes retained.
[R] Recommend B first; C only after additional source/monitor/layout review. Human approval remains mandatory.

Acceptance checks:
[E] PASS: 4,246-file directory diff has no additions, removals or changes.
[E] PASS: current 15-slide order and 278-row ledger verified.
[E] PASS: proposal and handback written only inside v3_addons.

Deviations from brief:
[E] No integration QA was run because no integration is authorized.
[R] Future PDF creation must follow the user's LaTeX-only instruction, not the brief's Office-PDF export step; a separate approved QA design is required.

Claims now allowed:
[E/A] Supporting analyses and their acceptance limits; [R] ranked integration choices.

Claims still forbidden:
[R] Applied slide/notebook/reference edits, new test evaluation, new AUC gain, submission or WP8 execution.

Open questions for human: [E] None; integration remains a separate human decision.
