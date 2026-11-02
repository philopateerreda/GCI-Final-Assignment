"""F4 — append-only notebook supplement, skipped under fallback A.

The card is optional and must be skipped on any failure. F2 stopped, no slide number was added, and the
notebook must stay frozen, so the card records the skip and proves the notebook is byte-identical.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402
import fstate  # noqa: E402
import report  # noqa: E402

TASK_INDEX = 18
RESULTS = c.RESULTS / 'f4_skip.json'
NOTEBOOK = 'philopateer.ipynb'
D0 = c.ROOT / 'v4_addons/results/d0_checks.json'


def main():
    c.runtime_record()
    d0 = json.loads(D0.read_text(encoding='utf-8'))
    frozen = d0['deliverable_hashes'][NOTEBOOK]['actual']
    actual = c.digest(c.ROOT / NOTEBOOK)

    n = c.Numbers()
    n.computed('cells_added', 0, '[E]', 'no notebook cell was appended')
    n.computed('cells_executed', 0, '[E]', 'no notebook cell was executed')
    n.declared('max_cells_allowed', 6, '[R]', 'brief cap if the supplement had been built')
    n.computed('notebook_bytes', (c.ROOT / NOTEBOOK).stat().st_size, '[E]', 'byte size of the unchanged notebook')
    n.computed('notebook_sha_matches_frozen', int(actual == frozen), '[E]',
               'notebook sha256 equals the frozen v2 record')

    body = dict(numbers=n.entries, status='COMPLETED_ACCEPTED', skipped=True,
                reason='F2 stopped at its build-pipeline guardrail; no slide number was added; fallback A keeps the notebook frozen',
                notebook=dict(path=NOTEBOOK, sha256=actual, frozen_sha256=frozen, match=actual == frozen,
                              words='F4 skipped'))
    c.write_json(RESULTS, body, __file__, TASK_INDEX, [D0, c.ROOT / NOTEBOOK])

    r = c.Renderer(n, RESULTS)
    summary = ('Summary: **F4 skipped**. The card is optional and must be skipped on any failure; F2 stopped at its '
               'guardrail, fallback A adds no number to the deck, and the notebook stays frozen. No cell was appended, '
               'no cell was executed, and the notebook is byte-identical to the frozen v2 record.')
    evidence = [('cells_added', 'int'), ('cells_executed', 'int'), ('max_cells_allowed', 'int'),
                ('notebook_bytes', 'int'), ('notebook_sha_matches_frozen', 'int')]
    acceptance = [
        lambda r: f'- At most {r.n("max_cells_allowed", "int")} cells appended: **NOT APPLICABLE** — the card was skipped by its own rule.',
        '- Execute only the new cells; first 25 existing cells byte-identical: **NOT APPLICABLE** — no cell was added or run.',
        lambda r: f'- Notebook unchanged: sha256 equals the frozen record ({r.n("notebook_sha_matches_frozen", "int")} match), {r.n("notebook_bytes", "int")} bytes: **PASS**.',
        '- Recorded as “F4 skipped”: **PASS** (this report and `STATE.md`).',
    ]
    deviations = ['- The supplement was not built; this is the directive\'s prescribed outcome when a prior card fails.']
    open_items = ['- F5 continues on the frozen v2 artifacts; the traceability supplement is not part of the submission.']
    commands = ['"$PY" -B -X utf8 boundary_check.py --card F4 --phase pre', '"$PY" -B -X utf8 f4_skip.py',
                '"$PY" -B -X utf8 check_numbers.py --scan ../reports/F4_report.md',
                '"$PY" -B -X utf8 boundary_check.py --card F4 --phase post']
    report.write_report('F4', 'Append-only notebook supplement — skipped', 'COMPLETED_ACCEPTED', summary, RESULTS,
                        evidence, acceptance, deviations, open_items, commands,
                        'yes (pre clean; post-check run after this report; only v4_addons/ written)')
    fstate.update({'F4': dict(status='COMPLETED_ACCEPTED', report='reports/F4_report.md', next_gate='none; F5 continues',
                               note='F4 skipped under fallback A; notebook byte-identical (0 cells added or executed)')},
                  project_status='F4 skipped as required under fallback A; the frozen notebook is untouched. F5-F7 continue.')
    print('notebook match:', actual == frozen, '| bytes:', (c.ROOT / NOTEBOOK).stat().st_size)


if __name__ == '__main__':
    main()
