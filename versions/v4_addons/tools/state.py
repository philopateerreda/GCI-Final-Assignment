"""Maintains v4_addons/STATE.md from results/state.json (one row per card)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402

STATE_JSON = c.RESULTS / 'state.json'
STATE_MD = c.ADDONS / 'STATE.md'
CARDS = ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'M0', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'I']
STATUSES = ('COMPLETED_ACCEPTED', 'COMPLETED_REJECTED', 'PARTIAL', 'BLOCKED', 'STOPPED_GUARDRAIL', 'NOT_STARTED', 'IN_PROGRESS')


def load():
    if STATE_JSON.exists():
        return json.loads(STATE_JSON.read_text(encoding='utf-8'))
    return dict(project_status='model track rejected (WP8); monitor non-operational (WP5); integration unapproved (WP7); frozen v2 remains the submission.',
                cards={card: dict(status='NOT_STARTED', date=None, report=None, next_gate=None, note=None) for card in CARDS}, blockers=[], log=[])


def save(state):
    STATE_JSON.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')
    lines = ['# v4 STATE', '', f'**Project status:** {state["project_status"]}', '', f'_Last update (UTC): {c.utc_now()}_', '',
             '| Card | Status | Date | Report | Next gate | Note |', '|---|---|---|---|---|---|']
    for card in CARDS:
        row = state['cards'][card]
        lines.append(f'| {card} | {row["status"]} | {row["date"] or ""} | {row["report"] or ""} | {row["next_gate"] or ""} | {row["note"] or ""} |')
    if state['blockers']:
        lines += ['', '## Blockers', ''] + [f'- {item}' for item in state['blockers']]
    lines += ['', '## Log', ''] + [f'- {item}' for item in state['log'][-60:]]
    STATE_MD.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def update(card, status, report=None, next_gate=None, note=None, blocker=None, project_status=None):
    assert status in STATUSES, status
    state = load()
    row = state['cards'][card]
    row.update(status=status, date=c.today(), report=report or row.get('report'), next_gate=next_gate, note=note)
    state['log'].append(f'{c.utc_now()} {card} -> {status}' + (f' ({note})' if note else ''))
    if blocker:
        state['blockers'].append(f'{c.today()} {card}: {blocker}')
    if project_status:
        state['project_status'] = project_status
    save(state)
    return state


if __name__ == '__main__':
    card, status = sys.argv[1], sys.argv[2]
    extra = dict(item.split('=', 1) for item in sys.argv[3:])
    update(card, status, **extra)
    print(STATE_MD.read_text(encoding='utf-8'))
