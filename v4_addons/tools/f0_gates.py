"""F0 -- write the two gate files authorized by closeout directive section 0.

This script deliberately does not import v4common: its audit hook blocks every
agent write into gates/, and section 0 amends G6 for exactly these two files
(H0_DECISIONS.md and H3_OPTION.txt). No other gate file is created. An existing
file with different content is never overwritten: a human gate file wins.
"""
import json
import sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADDONS = ROOT / 'v4_addons'
GATES = ADDONS / 'gates'
RESULTS = ADDONS / 'results'
SOURCE = ADDONS / 'DECISIONS_ASSUMED.md'
DELEGATION = "I don't want to take decisions, just tell him what you see is the smartest move."

TITLE = '# v4 — decisions adopted by delegation (H0_DECISIONS.md, 2026-10-31)'
HEADER = """**Gate file created by the agent on 2026-10-31 under section 0 of the v4 Closeout Directive; G6 is amended for exactly two files (this one and `H3_OPTION.txt`).** The account holder's delegation, quoted verbatim:

> I don't want to take decisions, just tell him what you see is the smartest move.

Source: a verbatim copy of `v4_addons/DECISIONS_ASSUMED.md` with every `DEFAULT_ASSUMED` replaced by `ADOPTED_BY_DELEGATION 2026-10-31`, the stale preamble and closing paragraph refreshed (this file now exists; Track M is closed), and the three decisions not previously tabled added as rows 11-13. No row content was otherwise changed. If the account holder later creates, edits or deletes any gate file, their file wins."""

OLD_PREAMBLE = ('Status of every row: **DEFAULT_ASSUMED** unless `v4_addons/gates/H0_DECISIONS.md` (human-created) overrides it. '
                'Checked at the start of every card; no such file existed when this table was written (2026-10-31).')
NEW_PREAMBLE = ('Status of every row: **ADOPTED_BY_DELEGATION 2026-10-31**. This file is the gate; a later edit by the account holder wins. '
                'Checked at the start of every card.')

OLD_FLAGS = ('Additional human decisions flagged inside cards as `[DECISION NEEDED: …]`: extension budget (D4), Floor contact cost (D6), '
             'harm-gate action and owner (D6), Track M thresholds (M2, gate H1).')
NEW_FLAGS = ('The `[DECISION NEEDED: …]` items previously flagged in cards D4, D6 and M2 are resolved by rows 11-13 and by the Track M closure below.')
OLD_CLOSING = ('Track M itself reopens the model track in a different form; that is a human decision (gate H1). Until `gates/H1_APPROVED.txt` exists, '
               'only M0 (feasibility, no fitting), M1 (non-test learning curve) and the M2 draft are executed; nothing is sealed and no test row is touched.')
EXTRA_TABLE = """## Additional decisions adopted (section 0, 2026-10-31)

The directive's other section-0 choices are already rows 3 (DEFF 1.1), 5 (monitor diagnostic only) and 9 (integration option B', recorded in `H3_OPTION.txt`). The three decisions not previously tabled are:

| # | Question | Decision [R] | Rationale | Status |
|---|---|---|---|---|
| 11 | Pilot extension budget (slide 13 placeholder) | **At most one equal-sized extension cohort, then stop.** Slide 13 carries no dollar figure; the CEO brief carries the bound variable cost (expected treated contacts x $1 = $7,872; startup assumed not to recur [A]). | A second extension would double the cost and still not resolve break-even. | ADOPTED_BY_DELEGATION 2026-10-31 |
| 12 | Floor (control-arm) contact cost | **Not an incremental pilot cost.** Floor fixes occur in both arms, are logged, and the v2 cost spec sets `control_incremental_contact = 0.0`. Counted pilot cost = discretionary outreach to treated accounts only; the Stage-1 envelope $12,872 = 7,872 treated contacts at $1 plus the $5,000 startup. | Consistent with ITT and the $12,872 envelope. | ADOPTED_BY_DELEGATION 2026-10-31 |
| 13 | Harm-gate action | **"If the gate trips: pause discretionary outreach in the treated arm; the Service-Fix Floor continues for everyone; the Company A pilot owner (named at kickoff) reviews before any restart."** No time limits, no personal names. | Role-based, no invented parameters. | ADOPTED_BY_DELEGATION 2026-10-31 |"""
NEW_CLOSING = ('Track M is closed at the M1 gate (KILL): the frozen model was already refit on all 75,000 non-test rows, so the point prediction of the extra gain is exactly zero against the +0.0015 gate. '
               'M2 to M6 are `NOT_RUN_KILLED_BY_M1_GATE`; `H1_APPROVED.txt` and `H2_APPROVED.txt` are not created. '
               'Under this closeout no model is fitted, refit, rescored or simulated, no candidate is added, and no new test row is read.')


def build_h0():
    text = SOURCE.read_text(encoding='utf-8')
    for marker in (OLD_PREAMBLE, OLD_FLAGS, OLD_CLOSING, '# v4 — decisions assumed (section 3 of the v4 brief)'):
        if marker not in text:
            raise SystemExit(f'source text changed; marker not found: {marker[:60]}...')
    text = text.replace('# v4 — decisions assumed (section 3 of the v4 brief)', TITLE)
    text = text.replace(OLD_PREAMBLE, NEW_PREAMBLE)
    text = text.replace(OLD_FLAGS, NEW_FLAGS)
    text = text.replace(OLD_CLOSING, EXTRA_TABLE + '\n\n' + NEW_CLOSING)
    text = text.replace('DEFAULT_ASSUMED', 'ADOPTED_BY_DELEGATION 2026-10-31')
    return text.replace(TITLE, TITLE + '\n\n' + HEADER, 1)


def write_if_allowed(path, text, previous):
    existed = path.exists()
    if existed:
        current = path.read_text(encoding='utf-8')
        if current == text:
            return 'unchanged'
        agent_hash = previous.get('files', {}).get(path.name, {}).get('sha256') if previous else None
        if agent_hash != digest(path):
            raise SystemExit(f'{path.name} was changed after the agent wrote it; a human gate file wins — refusing to overwrite')
    path.write_text(text, encoding='utf-8')
    return 'rewritten' if existed else 'written'


def digest(path):
    result = sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def main():
    GATES.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    record_path = RESULTS / 'f0_gate_record.json'
    previous = json.loads(record_path.read_text(encoding='utf-8')) if record_path.exists() else None
    targets = {'H0_DECISIONS.md': build_h0(), 'H3_OPTION.txt': 'B_PRIME\n'}
    actions = {name: write_if_allowed(GATES / name, text, previous) for name, text in targets.items()}
    present = sorted(path.name for path in GATES.iterdir() if path.is_file())
    if present != sorted(targets):
        raise SystemExit(f'unexpected gate files present: {present}')
    record = dict(card='F0', created_utc=datetime.now(timezone.utc).isoformat(), delegation=DELEGATION,
                  amendment='v4 Closeout Directive section 0: G6 amended for exactly H0_DECISIONS.md and H3_OPTION.txt',
                  actions=actions, gates_dir=present,
                  files={name: dict(size=(GATES / name).stat().st_size, sha256=digest(GATES / name)) for name in targets},
                  source=dict(path=SOURCE.relative_to(ROOT).as_posix(), sha256=digest(SOURCE)))
    target = record_path
    target.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(dict(actions=actions, gates=present, record=target.relative_to(ROOT).as_posix())))


if __name__ == '__main__':
    main()
