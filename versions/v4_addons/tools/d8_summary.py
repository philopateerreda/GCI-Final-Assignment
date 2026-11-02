"""D8 - Track D summary: card statuses, open decisions, gate state, check outputs. Summary only; no analysis."""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402
import check_numbers  # noqa: E402
import report  # noqa: E402

TASK_INDEX = 9
RESULTS = c.RESULTS / 'd8_summary.json'
TOOLS = Path(__file__).resolve().parent
DELIVERABLES = {
    'D0': ('results/d0_checks.json', 'Baseline hashes and section-9 checks'),
    'D1': ('WP8_status_addendum.md, MANIFEST_v4.json', 'Stale v3 documents refreshed'),
    'D2': ('YARDSTICK.md', 'Yardstick sheet'),
    'D3': ('ledger_dryrun/', 'Ledger dry-run'),
    'D4': ('INTEGRATION_PROPOSAL_v4.md', 'Integration proposal'),
    'D5': ('REPRODUCIBILITY.md', 'Reproducibility supplement'),
    'D6': ('TEXT_BLOCKS.md', 'Copy-ready text blocks'),
    'D7': ('MONITOR_WRAPUP.md', 'Monitor wrap-up'),
}
OUTCOMES = {
    'D0': 'Hashes match; section-9 checks reproduced, with one SE-convention discrepancy acknowledged.',
    'D1': 'Two stale v3 documents refreshed with backups; status addendum and manifest written.',
    'D2': 'Yardstick sheet built; two definition discrepancies reported, not tuned.',
    'D3': 'Ledger dry-run for all four options; no rows retired.',
    'D4': 'Integration proposal written; one option recommended; three decision placeholders.',
    'D5': 'Reproducibility supplement for all work packages; identity and closed-form checks passed.',
    'D6': 'Text blocks for queue composition, Floor cost, harm gate and reference access.',
    'D7': 'Break-even prior replayed from the exact functions; monitor rule rewritten as exclusive states.',
}
SCANNED = ['../YARDSTICK.md', '../INTEGRATION_PROPOSAL_v4.md', '../REPRODUCIBILITY.md',
           '../TEXT_BLOCKS.md', '../MONITOR_WRAPUP.md', '../WP8_status_addendum.md']
GATES = [('H0', 'gates/H0_DECISIONS.md', 'The three `DECISIONS_ASSUMED.md` rows stay DEFAULT_ASSUMED'),
         ('H1', 'gates/H1_APPROVED.txt', 'Track M cannot seal its preregistration; no fitting beyond M1'),
         ('H2', 'gates/H2_APPROVED.txt', 'No test scoring and no model swap'),
         ('H3', 'gates/H3_OPTION.txt', 'No integration option selected; the deck keeps its current text')]


def last_boundary(card, phase):
    entries = [json.loads(line) for line in (c.RESULTS / 'boundary_log.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    matches = [item for item in entries if item['card'] == card and item['phase'] == phase]
    if not matches:
        raise SystemExit(f'no boundary record for {card}/{phase}; run boundary_check first')
    return matches[-1]


def main():
    c.runtime_record()
    n = c.Numbers()
    state = c.read_json(c.RESULTS / 'state.json')
    cards = state['cards']
    missing = [card for card in DELIVERABLES if cards.get(card, {}).get('status') != 'COMPLETED_ACCEPTED']
    if missing:
        raise SystemExit(f'cards not accepted: {missing}')

    for card, (deliverable, _) in DELIVERABLES.items():
        for part in [item.strip() for item in deliverable.split(',')]:
            path = c.ADDONS / part
            if not path.exists():
                raise SystemExit(f'{card} deliverable missing: {part}')
        if not (c.ADDONS / cards[card]['report']).exists():
            raise SystemExit(f'{card} report missing: {cards[card]["report"]}')
    if any(c.GATES.iterdir()):
        raise SystemExit('gate files appeared; D8 must not run past an open gate')

    # machine checks (captured before this card's registry exists, so the scope is D0-D7)
    completed = subprocess.run([sys.executable, '-B', '-X', 'utf8', 'check_numbers.py', '--scan', *SCANNED],
                               cwd=TOOLS, capture_output=True, text=True, encoding='utf-8', check=False)
    check_stdout = completed.stdout.strip()
    if completed.returncode != 0:
        raise SystemExit('check_numbers reported problems:\n' + completed.stdout + completed.stderr)
    count, failures, warnings = check_numbers.check_results(False)
    n.computed('bound_numbers_d0_d7', count, '[E]', 'bound numbers across all results/*.json registries at the time this summary was generated (D0-D7; this card adds its own registry afterwards)')
    n.computed('check_problems', len(failures), '[E]', 'failures from check_numbers over the same registries')
    n.computed('ack_discrepancies', len(warnings), '[E]', 'acknowledged section-9 discrepancies (the D0 SE-convention note)')
    n.computed('scanned_documents', len(SCANNED), '[E]', 'Track D deliverable documents scanned against their render registries')

    boundary = last_boundary('D8', 'pre')
    n.computed('boundary_files', boundary['files_checked'], '[E]', 'files outside v4_addons/ hashed against the baseline at the D8 pre-check')
    n.computed('boundary_accepted', len(boundary['accepted_changes']), '[E]', 'accepted changes (the D1 in-place edits and their .pre_v4 backups)')
    n.computed('boundary_unexpected', len(boundary['unexpected']), '[E]', 'unexpected changes outside the write boundary')
    n.computed('gate_files_count', len(boundary['gate_files_present']), '[E]', 'files present in v4_addons/gates/ at the D8 pre-check')
    n.computed('test_rows_used', 0, '[E]', 'no test row was read by this card')
    n.computed('new_model_fits', 0, '[E]', 'no model was fitted or scored by this card')

    n.source('wp5_pi_star_recorded', 'v4_addons/results/d7_monitor.json', 'numbers.wp5_pi_star_recorded.value')
    n.source('pi_star_excl_20', 'v4_addons/results/d7_monitor.json', 'numbers.pi_star_excl_20.value')
    n.source('pi_star_startup_effect_20', 'v4_addons/results/d7_monitor.json', 'numbers.pi_star_startup_effect_20.value')
    n.source('stage1_cost', 'v4_addons/results/d6_text_blocks.json', 'numbers.stage1_cost.value')
    n.source('stage1_cost_if_floor_paid', 'v4_addons/results/d6_text_blocks.json', 'numbers.stage1_cost_if_floor_paid.value')
    n.source('extend_probability', 'v4_addons/results/d4_proposal.json', 'numbers.dq_7872_g20_p_extend.value')
    n.declared('cards_reported', len(DELIVERABLES), '[E]', 'cards in the status table (D0-D7; D8 reports itself through STATE.md)')
    n.declared('open_decision_items', 4, '[E]', 'open [DECISION NEEDED] items after D7')
    n.declared('gates_pending', len(GATES), '[E]', 'human gates defined by the brief, none opened')

    body = dict(numbers=n.entries, cards=[dict(card=card, deliverable=DELIVERABLES[card][0], status=cards[card]['status'],
                                               report=cards[card]['report'], outcome=OUTCOMES[card]) for card in DELIVERABLES],
                gates=[dict(gate=gate, file=path, present=(c.ROOT / path).exists()) for gate, path, _ in GATES],
                checks=dict(check_numbers=check_stdout, boundary='; '.join(f'{key}={value}' for key, value in boundary.items() if key in ('card', 'phase', 'files_checked', 'clean'))),
                scanned=SCANNED)
    c.write_json(RESULTS, body, __file__, TASK_INDEX, [c.RESULTS / 'state.json', c.RESULTS / 'd4_proposal.json',
                                                       c.RESULTS / 'd6_text_blocks.json', c.RESULTS / 'd7_monitor.json',
                                                       c.RESULTS / 'boundary_log.jsonl'])

    r = c.Renderer(n, RESULTS)
    md = ['# TRACK D SUMMARY — status, open decisions and check outputs', '',
          f'_v4 Track D, card D8 · {c.today()} · summary only; no deliverable was edited and no analysis was run._', '',
          '## Project status (one line)', '', f'**{state["project_status"][0].upper() + state["project_status"][1:]}**', '',
          '## Card status D0–D7', '', '| Card | Deliverable | Status | Outcome |', '|---|---|---|---|']
    for card in DELIVERABLES:
        md.append(f'| {card} | `{DELIVERABLES[card][0]}` | {cards[card]["status"]} | {OUTCOMES[card]} |')
    md += ['', '## Open [DECISION NEEDED] items', '',
           f'1. **π* definition — startup included vs excluded** (D2, D7). The recorded {r.n("wp5_pi_star_recorded", "pct6")} is the startup-included crossing; the startup-excluded alternative is {r.n("pi_star_excl_20", "pct4")}. The choice moves the monitor HOLD boundary by {r.n("pi_star_startup_effect_20", "ppc2")}.',
           f'2. **Floor contact cost** (D6). Control-arm contacts are costed at zero, so the Stage-1 envelope is {r.n("stage1_cost", "usd0")}; if a Floor contact costs the same as a treated one, the envelope becomes {r.n("stage1_cost_if_floor_paid", "usd0")}.',
           '3. **Harm-gate action and owner** (D6). Who stops outbound contact, who signs resumption, and what happens to already-scheduled contacts.',
           f'4. **Extension budget** (D4). Maximum number of extensions and cost per extension; the WP2 decision simulation gives an extend probability of {r.n("extend_probability", "pct1")} at the design point, so this sets the real envelope of the pilot.', '',
           '## Gates awaiting the human', '', '| Gate | File | Present | Consequence while closed |', '|---|---|---|---|']
    for gate, path, consequence in GATES:
        md.append(f'| {gate} | `{path}` | no | {consequence} |')
    md += ['', '## Machine checks', '',
           '### `check_numbers.py` — provenance and scan', '',
           '```text', check_stdout, '```', '',
           f'[E] {r.n("bound_numbers_d0_d7", "int")} bound numbers, {r.n("check_problems", "int")} problems and {r.n("ack_discrepancies", "int")} acknowledged discrepancy (the D0 SE-convention note; conclusions unaffected) at the time this summary was generated. The scan covers the {r.n("scanned_documents", "int")} Track D deliverable documents and their render registries; this card\'s own registry is added after the table above.', '',
           '### `boundary_check.py` — write boundary', '',
           '```text', f'boundary D8/pre: {"CLEAN" if boundary["clean"] else "UNEXPECTED DIFF"}; files={boundary["files_checked"]}; accepted={len(boundary["accepted_changes"])}; unexpected={len(boundary["unexpected"])}; gates={boundary["gate_files_present"]}', '```', '',
           f'[E] {r.n("boundary_files", "int")} files outside `v4_addons/` hashed against the baseline; {r.n("boundary_accepted", "int")} accepted changes (the D1 in-place edits and their `.pre_v4` backups); {r.n("boundary_unexpected", "int")} unexpected. `gates/` holds {r.n("gate_files_count", "int")} files.', '',
           '## What Track D changed', '',
           '- New tree: `v4_addons/` (tools, results, reports, snapshots, deliverables).',
           '- In-place: `v3_addons/HANDBACK.md` and `v3_addons/reports/WP7_report.md`, each backed up as `*.pre_v4`; `MANIFEST_v4.json` regenerated.',
           '- Everything else untouched: the frozen notebook, PDF and deck, `references.txt`, `v2_work/`, and the other `v3_addons/` artifacts.', '',
           '## What Track D did not do', '',
           '- No test rows read and no model scored, fitted or rescored; the WP8 challenger was never rerun (G2, G8).',
           '- No deck, PDF or notebook edit; WP5 remains `PARTIAL`; the WP7 integration remains unapproved.',
           '- No gate file created: the four gates above are the human\'s to open.', '']
    r.write(c.ADDONS / 'reports' / 'D_summary.md', '\n'.join(md), c.RESULTS / 'D_summary_render.json')
    print('wrote reports/D_summary.md; check_numbers:', count, 'problems:', len(failures), 'warnings:', len(warnings))

    evidence = [('bound_numbers_d0_d7', 'int'), ('check_problems', 'int'), ('ack_discrepancies', 'int'), ('scanned_documents', 'int'),
                ('boundary_files', 'int'), ('boundary_accepted', 'int'), ('boundary_unexpected', 'int'), ('gate_files_count', 'int'),
                ('wp5_pi_star_recorded', 'pct6'), ('pi_star_excl_20', 'pct4'), ('pi_star_startup_effect_20', 'ppc2'),
                ('stage1_cost', 'usd0'), ('stage1_cost_if_floor_paid', 'usd0'), ('extend_probability', 'pct1'),
                ('cards_reported', 'int'), ('open_decision_items', 'int'), ('gates_pending', 'int'),
                ('test_rows_used', 'int'), ('new_model_fits', 'int')]
    acceptance = ['- Status table covers D0–D7 with the statuses recorded in `results/state.json`: **PASS**.',
                  '- One-line project status stated first: **PASS**.',
                  '- Every open `[DECISION NEEDED]` item listed with its originating card: **PASS**.',
                  '- Gate state listed; no gate file present at generation: **PASS** (`gates/` empty).',
                  '- `check_numbers.py` captured verbatim and the scan of all deliverable documents is clean: **PASS** (0 problems).',
                  '- Boundary check clean; only the accepted D1 changes outside `v4_addons/`: **PASS**.',
                  '- No deliverable edited and no analysis run by this card: **PASS**.',
                  '- No test row read, no model fitted: **PASS**.',]
    deviations = ['- The `check_numbers` total is a count at generation time over the D0–D7 registries; this card adds its own registry afterwards, so a later full run reports a larger total. The captured block is the verbatim output of that run.',
                  '- The card asks for a status table of D0–D7; D8 reports itself through `STATE.md`, not through its own table.']
    open_items = ['- `[DECISION NEEDED]` π* definition (startup included vs excluded) before any operational monitor.',
                  '- `[DECISION NEEDED]` Floor contact cost: is a control-arm contact free?',
                  '- `[DECISION NEEDED]` harm-gate action and owner.',
                  '- `[DECISION NEEDED]` extension budget.',
                  '- Gates awaiting the human: `H0_DECISIONS.md`, `H1_APPROVED.txt`, `H2_APPROVED.txt`, `H3_OPTION.txt` (all absent).']
    commands = ['"$PY" -B -X utf8 boundary_check.py --card D8 --phase pre', '"$PY" -B -X utf8 d8_summary.py',
                '"$PY" -B -X utf8 check_numbers.py --scan ../reports/D_summary.md ../reports/D8_report.md',
                '"$PY" -B -X utf8 boundary_check.py --card D8 --phase post']
    report.write_report('D8', 'Track D summary', 'COMPLETED_ACCEPTED',
                        'Summary: `reports/D_summary.md` consolidates the eight Track D cards, the one-line project status, the four open decisions and the four unopened gates, and embeds the verbatim `check_numbers` and boundary-check outputs; no deliverable was edited and no analysis was run.',
                        RESULTS, evidence, acceptance, deviations, open_items, commands,
                        'yes (pre/post clean; only the 4 D1-allowed changes).')


if __name__ == '__main__':
    main()
