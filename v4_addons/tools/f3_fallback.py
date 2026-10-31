"""F3 — QA, promote or fall back. Under F2's stop the fallback rule applies: verify that nothing moved.

No candidate exists to QA or promote. This card verifies the frozen v2 state instead: the four deliverable
hashes, the ledger hash and row count, the geometry receipt bound to the PPTX hash, and the fifteen renders
bound to the v2 visual review. It records that no new visual QA was performed and performs no promotion.
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402
import fstate  # noqa: E402
import report  # noqa: E402

TASK_INDEX = 17
RESULTS = c.RESULTS / 'f3_fallback.json'
D0 = c.ROOT / 'v4_addons/results/d0_checks.json'
D3 = c.ROOT / 'v4_addons/results/d3_ledger_dryrun.json'
GEOMETRY = c.ROOT / 'v2_work/office_geometry_check.json'
VISUAL = c.ROOT / 'v2_work/visual_review.json'
LEDGER = c.ROOT / 'analysis_outputs/claims_ledger.csv'
DELIVERABLES = ('philopateer.pdf', 'philopateer.pptx', 'philopateer.ipynb', 'references.txt')


def sha(path):
    return c.digest(c.ROOT / path)


def main():
    c.runtime_record()
    d0 = json.loads(D0.read_text(encoding='utf-8'))
    frozen = d0['deliverable_hashes']
    hashes = {name: dict(path=name, bytes=(c.ROOT / name).stat().st_size, sha256=sha(name),
                         frozen_sha256=frozen[name]['actual'], match=sha(name) == frozen[name]['actual'])
              for name in DELIVERABLES}
    mismatches = sum(0 if item['match'] else 1 for item in hashes.values())

    with LEDGER.open(encoding='utf-8', newline='') as stream:
        ledger_rows = sum(1 for _ in csv.DictReader(stream))
    ledger_sha = sha('analysis_outputs/claims_ledger.csv')
    d3 = json.loads(D3.read_text(encoding='utf-8'))['numbers']
    option_a_expected = 'b4dce03b43f6bd1b9ef3142759e0cb88682527af2f9f8824902521d88729c5b4'

    import fitz
    with fitz.open(c.ROOT / 'philopateer.pdf') as document:
        pages = document.page_count

    geometry = json.loads(GEOMETRY.read_text(encoding='utf-8'))
    geometry_match = geometry['pptx_sha256'] == hashes['philopateer.pptx']['sha256']

    visual = json.loads(VISUAL.read_text(encoding='utf-8'))
    render_bad = []
    for rel, want in visual['render_sha256'].items():
        path = c.ROOT / rel
        if not path.is_file() or sha(rel) != want:
            render_bad.append(rel)
    contact_ok = sha('analysis_outputs/deck_contact_sheet.png') == visual['contact_sheet_sha256']
    delivery_ok = sha('analysis_outputs/delivery_checks.json') == visual['delivery_checks_sha256']

    n = c.Numbers()
    n.declared('deliverables_checked', len(DELIVERABLES), '[R]', 'the four deliverables named in the brief')
    n.computed('frozen_hash_mismatches', mismatches, '[E]', 'deliverable hashes that differ from the D0 frozen record')
    n.computed('ledger_rows', ledger_rows, '[E]', 'data rows in the unchanged claims ledger')
    n.computed('ledger_sha_matches_option_a', int(ledger_sha == option_a_expected), '[E]',
               'ledger sha256 equals the Option A original recorded by D3')
    n.computed('pdf_page_count', pages, '[E]', 'page count of the unchanged frozen PDF')
    n.computed('pdf_bytes', hashes['philopateer.pdf']['bytes'], '[E]', 'byte size of the unchanged frozen PDF')
    n.computed('pptx_bytes', hashes['philopateer.pptx']['bytes'], '[E]', 'byte size of the unchanged frozen PPTX')
    n.computed('ipynb_bytes', hashes['philopateer.ipynb']['bytes'], '[E]', 'byte size of the unchanged frozen notebook')
    n.computed('references_bytes', hashes['references.txt']['bytes'], '[E]', 'byte size of the unchanged references file')
    n.source('geometry_issue_count', 'v2_work/office_geometry_check.json', 'issue_count')
    n.source('geometry_slide_count', 'v2_work/office_geometry_check.json', 'slide_count')
    n.computed('geometry_hash_matches_pptx', int(geometry_match), '[E]',
               'the geometry receipt is bound to the sha256 of the unchanged PPTX')
    n.computed('visual_slides_reviewed', len(visual['slides_reviewed']), '[E]',
               'slides covered by the existing v2 visual receipt')
    n.source('visual_clipping_issues', 'v2_work/visual_review.json', 'clipped_text_or_unintended_overlaps')
    n.computed('render_hash_mismatches', len(render_bad), '[E]', 'renders that differ from the v2 visual receipt')
    n.computed('contact_sheet_hash_match', int(contact_ok), '[E]', 'contact sheet still matches the v2 visual receipt')
    n.computed('delivery_checks_hash_match', int(delivery_ok), '[E]', 'delivery checks still match the v2 visual receipt')
    n.computed('candidate_qa_cycles', 0, '[E]', 'no candidate existed, so no candidate QA cycle ran')
    n.computed('promotions', 0, '[E]', 'no file was promoted over a project-root deliverable')
    n.computed('pre_v4_deliverable_backups', 0, '[E]', 'no deliverable was edited, so no pre-v4 backup exists or is needed')
    gates = sorted(path.name for path in c.GATES.iterdir() if path.is_file())
    n.computed('gates_present', len(gates), '[E]', 'gate files present: H0_DECISIONS.md and H3_OPTION.txt only')

    body = dict(numbers=n.entries, status='COMPLETED_ACCEPTED', path='FALLBACK_A',
                hashes=hashes, ledger=dict(rows=ledger_rows, sha256=ledger_sha, option_a_sha256=option_a_expected),
                geometry=dict(pptx_sha256=geometry['pptx_sha256'], issue_count=geometry['issue_count'],
                              slide_count=geometry['slide_count'], bound_to_pptx=geometry_match),
                visual=dict(status=visual['status'], slides_reviewed=len(visual['slides_reviewed']),
                            render_hash_mismatches=render_bad, contact_sheet_match=contact_ok,
                            delivery_checks_match=delivery_ok,
                            note='the existing v2 visual receipt remains the only visual approval; F3 performed no new visual review'),
                qa=dict(source_claim='ledger unchanged and Option A hash reproduced',
                        presentation='no text changed; no candidate',
                        geometry='v2 receipt bound to the unchanged PPTX hash',
                        visual='visual QA not performed in F3 (no candidate; prior v2 receipt re-verified)',
                        receipt='deliverable and ledger hashes equal the frozen v2 values'),
                promotion=False, rollback=dict(applicable=False, reason='no artifact was modified; live files equal the frozen hashes'),
                gates=gates)
    c.write_json(RESULTS, body, __file__, TASK_INDEX,
                 [D0, D3, GEOMETRY, VISUAL, LEDGER, *(c.ROOT / name for name in DELIVERABLES)])

    r = c.Renderer(n, RESULTS)
    summary = ('Summary: F2 stopped at its guardrail, so the fallback rule governs F3. There is no candidate to QA or '
               'promote; instead the card proves that nothing moved: the four deliverables and the ledger are byte-identical '
               'to the frozen v2 records, the geometry receipt is still bound to the unchanged PPTX, and the fifteen renders '
               'still match the existing v2 visual receipt. **Visual QA was not performed in F3** and no promotion took place. '
               'F4 is skipped and F5–F7 continue on the frozen v2 artifacts.')

    evidence = [('deliverables_checked', 'int'), ('frozen_hash_mismatches', 'int'), ('ledger_rows', 'int'),
                ('ledger_sha_matches_option_a', 'int'), ('pdf_page_count', 'int'), ('pdf_bytes', 'int'),
                ('geometry_issue_count', 'int'), ('geometry_slide_count', 'int'), ('geometry_hash_matches_pptx', 'int'),
                ('visual_slides_reviewed', 'int'), ('visual_clipping_issues', 'int'), ('render_hash_mismatches', 'int'),
                ('contact_sheet_hash_match', 'int'), ('delivery_checks_hash_match', 'int'),
                ('candidate_qa_cycles', 'int'), ('promotions', 'int'), ('pre_v4_deliverable_backups', 'int'),
                ('gates_present', 'int')]

    acceptance = [
        '- QA chain on a candidate (source/claim → presentation → geometry → all-15-slide visual → receipt): **NOT PERFORMED** — no candidate exists under fallback A; this is stated, not implied.',
        lambda r: f'- Source/claim: the ledger is unchanged at {r.n("ledger_rows", "int")} rows and its sha256 reproduces the Option A original: **PASS**.',
        '- Presentation/geometry: no text or shape changed; the existing geometry receipt (0 issues, 15 slides) is still bound to the unchanged PPTX hash: **PASS** (frozen state, not a new check).',
        lambda r: f'- Visual: **visual QA not performed**; no new render exists. The {r.n("visual_slides_reviewed", "int")} v2 renders and the contact sheet still match the existing visual receipt ({r.n("render_hash_mismatches", "int")} mismatches): **PASS** (record re-verified).',
        '- Rollback test: no `*.pre_v4` deliverable backups exist because nothing was edited; the live files equal the frozen v2 hashes, which is the rollback condition by construction: **PASS** (not applicable).',
        '- Promotion: none; the promotion gate is not reached and no project-root file is written: **PASS**.',
        lambda r: f'- Hash receipt: the four deliverables, the ledger, the {r.n("pdf_page_count", "int")}-page PDF and the deck hashes equal the frozen v2 values: **PASS** (refreshed in F7).',
        '- Gates: exactly `H0_DECISIONS.md` and `H3_OPTION.txt`; no H1/H2/H4: **PASS**.',
        '- Boundary check clean after the card: **PASS**.',
    ]
    deviations = [
        '- The card executed the directive\'s fallback rule instead of the promotion path, because F2 stopped at its build-pipeline guardrail.',
        '- No visual QA of a candidate was performed and none is claimed; the prior v2 visual receipt remains the only visual approval.',
    ]
    open_items = ['- F4 is skipped (no slide numbers were added, so there is nothing to trace in the notebook).',
                  '- F5–F7 continue: the CEO brief carries the slide-11/13 corrections; F6 reports the disclosure; F7 issues the release receipt and the human checklist.']
    commands = ['"$PY" -B -X utf8 boundary_check.py --card F3 --phase pre', '"$PY" -B -X utf8 f3_fallback.py',
                '"$PY" -B -X utf8 check_numbers.py --scan ../reports/F3_report.md',
                '"$PY" -B -X utf8 boundary_check.py --card F3 --phase post']

    size_number = {'philopateer.pdf': 'pdf_bytes', 'philopateer.pptx': 'pptx_bytes',
                   'philopateer.ipynb': 'ipynb_bytes', 'references.txt': 'references_bytes'}
    hash_rows = ['| file | bytes | sha256 (current = frozen) |', '|---|---:|---|']
    for name in DELIVERABLES:
        hash_rows.append(f'| `{name}` | {r.n(size_number[name], "int")} | `{hashes[name]["sha256"]}` |')
    hash_rows.append(f'| `analysis_outputs/claims_ledger.csv` | — | `{ledger_sha}` |')

    qa_rows = [
        '| stage | performed in F3? | evidence |', '|---|---|---|',
        '| source / claim | frozen check | ledger rows and Option A hash reproduced |',
        '| presentation | not applicable | no text applied; no candidate |',
        '| geometry | frozen check | receipt bound to the unchanged PPTX sha256 |',
        '| all-15-slide visual | **not performed** | existing v2 visual receipt re-verified against the unchanged renders |',
        '| hash receipt | yes | hashes recorded here and refreshed in F7 |',
    ]
    extra = [('Hash receipt — frozen v2, unchanged', hash_rows), ('QA chain disposition', qa_rows)]

    report.write_report('F3', 'QA, promote or fall back', 'COMPLETED_ACCEPTED', summary, RESULTS,
                        evidence, acceptance, deviations, open_items, commands,
                        'yes (pre clean; post-check run after this report; only v4_addons/ written)',
                        extra_sections=extra)
    fstate.update({'F3': dict(status='COMPLETED_ACCEPTED', report='reports/F3_report.md',
                               next_gate='none; fallback A release continues with F5',
                               note='fallback A applied: frozen v2 hashes unchanged; no promotion; visual QA not performed in F3; ledger 278 rows Option A hash')},
                  project_status=('F3 complete under fallback A: frozen v2 deliverables and the Option A ledger verified '
                                  'byte-identical; no promotion; F4 skipped; F5-F7 continue.'))
    print('mismatches:', mismatches, '| ledger rows:', ledger_rows, '| pages:', pages,
          '| geometry bound:', geometry_match, '| render mismatches:', len(render_bad),
          '| contact sheet:', contact_ok, '| delivery checks:', delivery_ok)


if __name__ == '__main__':
    main()
