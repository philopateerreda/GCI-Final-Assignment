"""STATE.md/state.json writer for the closeout cards F0-F7.

state.py (Track D/M tooling) is left untouched: its status vocabulary has no
NOT_RUN_KILLED_BY_M1_GATE and it does not render the delegation record. This
module writes the same JSON shape plus an `authorization` section.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402

STATE_JSON = c.RESULTS / 'state.json'
STATE_MD = c.ADDONS / 'STATE.md'
BASE_CARDS = ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'M0', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'I']
CARDS = BASE_CARDS + [f'F{index}' for index in range(8)]
STATUSES = ('COMPLETED_ACCEPTED', 'COMPLETED_REJECTED', 'PARTIAL', 'BLOCKED', 'STOPPED_GUARDRAIL',
            'NOT_STARTED', 'IN_PROGRESS', 'NOT_RUN_KILLED_BY_M1_GATE')
AUTHORIZATION = [
    '**2026-10-31, account holder (philopateer), quoted verbatim:** "I don\'t want to take decisions, just tell him what you see is the smartest move."',
    'This sentence is the account holder\'s authorization for the two gate files `v4_addons/gates/H0_DECISIONS.md` and `v4_addons/gates/H3_OPTION.txt` (v4 Closeout Directive, section 0; G6 amended for exactly these two files). If the account holder later creates, edits or deletes any gate file, their file wins.',
    '`H1_APPROVED.txt` and `H2_APPROVED.txt` were not created; Track M stays killed. H4 (upload and submission) is never the agent\'s step.',
]


def load():
    if STATE_JSON.exists():
        return json.loads(STATE_JSON.read_text(encoding='utf-8'))
    return dict(project_status='closeout not started', cards={}, blockers=[], log=[], authorization=list(AUTHORIZATION))


def save(state):
    for card in CARDS:
        state['cards'].setdefault(card, dict(status='NOT_STARTED', date=None, report=None, next_gate=None, note=None))
    state.setdefault('authorization', list(AUTHORIZATION))
    STATE_JSON.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')
    lines = ['# v4 STATE', '', f'**Project status:** {state["project_status"]}', '', f'_Last update (UTC): {c.utc_now()}_', '',
             '| Card | Status | Date | Report | Next gate | Note |', '|---|---|---|---|---|---|']
    for card in CARDS:
        row = state['cards'][card]
        lines.append(f'| {card} | {row["status"]} | {row["date"] or ""} | {row["report"] or ""} | {row["next_gate"] or ""} | {row["note"] or ""} |')
    lines += ['', '## Authorization record', ''] + [f'- {item}' for item in state['authorization']]
    if state['blockers']:
        lines += ['', '## Blockers', ''] + [f'- {item}' for item in state['blockers']]
    lines += ['', '## Log', ''] + [f'- {item}' for item in state['log'][-80:]]
    STATE_MD.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def update(cards, project_status=None):
    """cards: {card: {status, report, next_gate, note}}; one save per call."""
    state = load()
    for card, row in cards.items():
        assert row['status'] in STATUSES, row['status']
        current = state['cards'].setdefault(card, {})
        current.update(status=row['status'], date=row.get('date') or c.today(),
                       report=row.get('report'), next_gate=row.get('next_gate'), note=row.get('note'))
        state['log'].append(f'{c.utc_now()} {card} -> {row["status"]}' + (f' ({row["note"]})' if row.get('note') else ''))
    if project_status:
        state['project_status'] = project_status
    save(state)
    return state
