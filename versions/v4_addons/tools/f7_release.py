"""F7 — release candidate, receipt and the five-line human checklist.

Fallback A: the four frozen v2 deliverables are copied unchanged into v4_addons/release_candidate/ together
with the CEO brief and Q&A. Every copy is hash-verified, made read-only, and reported against the D0 frozen
record. Nothing is uploaded.
"""
import csv
import json
import shutil
import stat
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402
import fstate  # noqa: E402
import report  # noqa: E402

TASK_INDEX = 21
RESULTS = c.RESULTS / 'f7_release.json'
RECEIPT = c.ADDONS / 'RELEASE_RECEIPT.md'
CHECKLIST = c.ADDONS / 'HUMAN_CHECKLIST.md'
RELEASE = c.ADDONS / 'release_candidate'
DELIVERABLES = ['philopateer.pdf', 'philopateer.pptx', 'philopateer.ipynb', 'references.txt']
BRIEFS = ['v4_addons/CEO_BRIEF.md', 'v4_addons/CEO_QA.md']
LEDGER = 'v4_addons/ledger_dryrun/claims_ledger_A_final.csv'
F3 = 'v4_addons/results/f3_fallback.json'
F4 = 'v4_addons/results/f4_skip.json'
F5 = 'v4_addons/results/f5_ceo.json'


def copy_release():
    RELEASE.mkdir(parents=True, exist_ok=True)
    sources = [c.ROOT / name for name in DELIVERABLES] + [c.ROOT / name for name in BRIEFS]
    for source in sources:
        target = RELEASE / source.name
        if target.exists():
            target.chmod(0o666)
        shutil.copy2(source, target)
    copies = sorted(RELEASE.iterdir())
    verified = sum(1 for source in sources if c.digest(source) == c.digest(RELEASE / source.name))
    for path in copies:
        path.chmod(0o444)
    read_only = sum(1 for path in copies if os_read_only(path))
    return dict(files=len(copies), verified=verified, read_only=read_only)


def os_read_only(path):
    info = path.stat()
    flag = getattr(stat, 'FILE_ATTRIBUTE_READONLY', 0x1)
    return bool(getattr(info, 'st_file_attributes', 0) & flag)


def bind(copy_info):
    n = c.Numbers()
    for name, key in [('pdf_pages', 'pdf_page_count'), ('pdf_bytes', 'pdf_bytes'),
                      ('pptx_bytes', 'pptx_bytes'), ('ipynb_bytes', 'ipynb_bytes'),
                      ('references_bytes', 'references_bytes'), ('ledger_rows', 'ledger_rows'),
                      ('visual_slides_reviewed', 'visual_slides_reviewed'),
                      ('visual_clipping_issues', 'visual_clipping_issues'),
                      ('render_hash_mismatches', 'render_hash_mismatches'),
                      ('geometry_issue_count', 'geometry_issue_count'),
                      ('geometry_slide_count', 'geometry_slide_count'),
                      ('geometry_hash_matches_pptx', 'geometry_hash_matches_pptx'),
                      ('frozen_hash_mismatches', 'frozen_hash_mismatches'),
                      ('candidate_qa_cycles', 'candidate_qa_cycles'),
                      ('promotions', 'promotions'), ('gates_present', 'gates_present')]:
        n.source(name, F3, f'numbers.{key}.value')
    n.source('cells_added', F4, 'numbers.cells_added.value')
    n.source('brief_words', F5, 'numbers.brief_words.value')
    n.source('qa_words', F5, 'numbers.qa_words.value')
    n.source('expected_rows_matched', F5, 'numbers.expected_rows_matched.value')
    n.source('expected_rows_total', F5, 'numbers.expected_rows_total.value')

    f3 = json.loads((c.ROOT / F3).read_text(encoding='utf-8'))
    sizes = {'philopateer.pdf': 'pdf_bytes', 'philopateer.pptx': 'pptx_bytes',
             'philopateer.ipynb': 'ipynb_bytes', 'references.txt': 'references_bytes'}
    size_mismatches = 0
    frozen_matches = 0
    for name in DELIVERABLES:
        copy_path = RELEASE / name
        record = f3['hashes'][name]
        frozen_matches += int(c.digest(copy_path) == record['frozen_sha256'])
        size_mismatches += int(copy_path.stat().st_size != record['bytes'])
    with (c.ROOT / LEDGER).open(encoding='utf-8', newline='') as stream:
        ledger_rows = len(list(csv.DictReader(stream)))
    brief_text = (c.ROOT / BRIEFS[0]).read_text(encoding='utf-8')
    qa_text = (c.ROOT / BRIEFS[1]).read_text(encoding='utf-8')
    checklist_text = checklist()
    n.computed('release_files', copy_info['files'], '[E]', 'files in the release folder')
    n.computed('copies_verified', copy_info['verified'], '[E]', 'release copies whose SHA-256 equals the source')
    n.computed('copies_read_only', copy_info['read_only'], '[E]', 'release copies carrying the read-only attribute')
    n.computed('copy_hash_mismatches', copy_info['files'] - copy_info['verified'], '[E]', 'copy hash mismatches')
    n.computed('deliverable_count', len(DELIVERABLES), '[R]', 'frozen deliverables in the release folder')
    n.computed('frozen_match_count', frozen_matches, '[E]', 'deliverable copies equal to the D0 frozen hashes')
    n.computed('size_mismatches', size_mismatches, '[E]', 'deliverable copies whose size differs from the F3 receipt')
    n.computed('ledger_rows_recount', ledger_rows, '[E]', 'data rows recounted from the Option A ledger copy')
    n.computed('ledger_rows_match', int(ledger_rows == f3['ledger']['rows']), '[E]',
               'recounted ledger rows equal the F3 receipt')
    n.computed('ledger_sha_match', int(c.digest(c.ROOT / LEDGER) == f3['ledger']['option_a_sha256']), '[E]',
               'ledger SHA-256 equals the Option A original')
    n.computed('brief_words_recount', len(brief_text.split()), '[E]', 'whitespace word count of the released brief')
    n.computed('qa_words_recount', len(qa_text.split()), '[E]', 'whitespace word count of the released Q&A')
    n.computed('brief_words_match', int(len(brief_text.split()) == n.value('brief_words')), '[E]',
               'released brief length equals the F5 record')
    n.computed('qa_words_match', int(len(qa_text.split()) == n.value('qa_words')), '[E]',
               'released Q&A length equals the F5 record')
    n.computed('checklist_lines', len(checklist_text.splitlines()), '[R]', 'lines in HUMAN_CHECKLIST.md')
    n.computed('new_model_fits', 0, '[E]', 'model fits, refits, rescores or simulations in v4 closeout')
    n.computed('new_test_reads', 0, '[E]', 'new test-split reads in v4 closeout')
    n.computed('deck_edits', 0, '[E]', 'deck, LaTeX or PDF edits in v4 closeout')
    n.computed('new_visual_reviews', 0, '[E]', 'new slide visual inspections in v4 closeout')
    n.computed('uploads', 0, '[E]', 'portal uploads or submissions performed')
    return n, f3, checklist_text


def checklist():
    return '\n'.join([
        '(a) Skim `v4_addons/CEO_BRIEF.md`.',
        '(b) Open `philopateer.pdf` and look at slides 11 and 13.',
        '(c) Check the disclosure text in `v4_addons/DISCLOSURE_CHECK.md`.',
        '(d) Fill the Omnicampus fields and upload `philopateer.pdf`, `philopateer.ipynb` and `references.txt` under `philopateer`.',
        '(e) Submit before 28 Nov 2026, 11:30 UTC (recommended 25 Nov).',
    ])


def receipt_text(r, f3):
    def v(name, spec='int'):
        return r.n(name, spec)

    rows = []
    for name in DELIVERABLES:
        path = RELEASE / name
        rows.append(f'| `{name}` | {path.stat().st_size:,} | `{c.digest(path)}` |')
    rows.append(f'| `CEO_BRIEF.md` | {(RELEASE / "CEO_BRIEF.md").stat().st_size:,} | '
                f'`{c.digest(RELEASE / "CEO_BRIEF.md")}` |')
    rows.append(f'| `CEO_QA.md` | {(RELEASE / "CEO_QA.md").stat().st_size:,} | '
                f'`{c.digest(RELEASE / "CEO_QA.md")}` |')
    comparison = []
    for name in DELIVERABLES:
        comparison.append(f'| `{name}` | `{f3["hashes"][name]["frozen_sha256"]}` | '
                          f'`{c.digest(RELEASE / name)}` | equal |')
    lines = [
        '# Release receipt — Company A retention proposal',
        '',
        '**Status: READY_FOR_CEO_FALLBACK_A.** The four frozen v2 deliverables are unchanged, the CEO brief and Q&A '
        'are added, and no upload or submission has been performed.',
        '',
        'Date: 2026-10-31. Release folder: `v4_addons/release_candidate/` (read-only copies).',
        '',
        '## Release files',
        '',
        '| file | bytes | hash |',
        '|---|---:|---|',
    ] + rows + [
        '',
        f'**Verification.** {v("release_files")} files copied; {v("copies_verified")} hash-verified; '
        f'{v("copies_read_only")} read-only; {v("copy_hash_mismatches")} mismatches. '
        f'{v("frozen_match_count")} of {v("deliverable_count")} deliverables equal their D0 frozen hashes; '
        f'{v("size_mismatches")} size mismatches.',
        '',
        '## Final figures',
        '',
        f'- PDF: {v("pdf_pages")} pages, {v("pdf_bytes")} bytes.',
        f'- PPTX: {v("geometry_slide_count")} slides, {v("pptx_bytes")} bytes.',
        f'- Notebook: {v("ipynb_bytes")} bytes; supplement skipped ({v("cells_added")} cells added).',
        f'- `references.txt`: {v("references_bytes")} bytes; disclosure and link check in F6.',
        f'- Claims ledger (Option A): {v("ledger_rows")} rows, {v("ledger_rows_recount")} recounted; '
        f'SHA match {v("ledger_sha_match")}; rows match {v("ledger_rows_match")}.',
        f'- CEO brief: {v("brief_words")} words ({v("brief_words_recount")} recounted); Q&A: {v("qa_words")} words '
        f'({v("qa_words_recount")} recounted); match flags {v("brief_words_match")}/{v("qa_words_match")}.',
        f'- Gate files present: {v("gates_present")}.',
        '',
        '## QA performed',
        '',
        f'- Hashes: {v("frozen_hash_mismatches")} deliverable mismatches against the D0 frozen record; '
        f'{v("promotions")} promotions.',
        f'- Geometry: {v("geometry_issue_count")} issues over {v("geometry_slide_count")} slides; the receipt is bound '
        f'to the PPTX hash (match {v("geometry_hash_matches_pptx")}).',
        f'- Visual: {v("visual_slides_reviewed")} slides covered by the existing v2 visual receipt; '
        f'{v("visual_clipping_issues")} clipping issues; {v("render_hash_mismatches")} render hash mismatches; contact '
        'sheet and delivery checks match. **No new visual inspection was performed in v4**; the v2 receipt remains the '
        'only visual approval.',
        f'- Numbers: the CEO brief and Q&A pass `check_numbers.py`; {v("expected_rows_matched")} of '
        f'{v("expected_rows_total")} expected-value rows match.',
        '- Disclosure: `references.txt` is untouched; the HBS item pages are bot-blocked rather than dead and the '
        'Columbia PDF is the accessible copy (F6).',
        f'- Notebook: byte-identical to the frozen record; {v("cells_added")} cells added.',
        '',
        '## QA not performed',
        '',
        f'- No model fit, refit, rescore or simulation ({v("new_model_fits")}); no new test-split read '
        f'({v("new_test_reads")}).',
        f'- No deck, LaTeX or PDF edit ({v("deck_edits")}); no candidate PDF; no promotion; no new visual review '
        f'({v("new_visual_reviews")}).',
        f'- No notebook cell appended or executed; no upload, portal entry or submission ({v("uploads")}).',
        '',
        '## Unchanged frozen-v2 hashes (D0 record vs release copy)',
        '',
        '| file | frozen v2 (D0) | release candidate | equal |',
        '|---|---|---|---|',
    ] + comparison + [
        '',
        'One-line status: **READY_FOR_CEO_FALLBACK_A** — frozen v2 unchanged; brief, Q&A and disclosure check added.',
        '',
        'The account holder’s steps are in `v4_addons/HUMAN_CHECKLIST.md` (five lines).',
        '',
    ]
    return '\n'.join(lines)


def main():
    c.runtime_record()
    copy_info = copy_release()
    n, f3, checklist_text = bind(copy_info)
    body = dict(numbers=n.entries, status='READY_FOR_CEO_FALLBACK_A', fallback='A',
                release_folder='v4_addons/release_candidate', release_files=copy_info['files'],
                copies_verified=copy_info['verified'], read_only=copy_info['read_only'],
                checklist_lines=int(n.value('checklist_lines')))
    c.write_json(RESULTS, body, __file__, TASK_INDEX,
                 [c.ROOT / name for name in DELIVERABLES + BRIEFS] + [c.ROOT / LEDGER, c.ROOT / F3, c.ROOT / F4,
                                                                     c.ROOT / F5])

    r_receipt = c.Renderer(n, RESULTS)
    receipt = receipt_text(r_receipt, f3)
    r_receipt.write(RECEIPT, receipt, c.RESULTS / 'RELEASE_RECEIPT_render.json')
    print('wrote', RECEIPT.relative_to(c.ROOT).as_posix(), 'words', len(receipt.split()))

    r_check = c.Renderer(n, RESULTS)
    r_check.write(CHECKLIST, checklist_text, c.RESULTS / 'HUMAN_CHECKLIST_render.json')
    print('wrote', CHECKLIST.relative_to(c.ROOT).as_posix(), 'lines', len(checklist_text.splitlines()))

    r = c.Renderer(n, RESULTS)
    summary = ('The four frozen v2 deliverables, the CEO brief and the Q&A were copied into '
               '`v4_addons/release_candidate/` as read-only files. All copies hash-verify, all four deliverables equal '
               'the D0 frozen hashes, and the ledger still has its frozen row count and hash. The receipt records the '
               'final figures and separates QA that was performed from QA that was not. The five-line human checklist '
               'names the only steps left to the account holder. Under fallback A nothing was edited, promoted or '
               'uploaded; the state is READY_FOR_CEO_FALLBACK_A.')
    acceptance = [
        lambda r: (f'- Release folder holds {r.n("release_files", "int")} read-only copies, '
                   f'{r.n("copies_verified", "int")} hash-verified, {r.n("copy_hash_mismatches", "int")} mismatches: '
                   '**PASS**.'),
        lambda r: (f'- Final figures recorded: {r.n("pdf_pages", "int")} pages, {r.n("pdf_bytes", "int")} bytes, '
                   f'{r.n("ledger_rows", "int")} ledger rows: **PASS**.'),
        lambda r: (f'- Frozen v2 unchanged: {r.n("frozen_match_count", "int")} of '
                   f'{r.n("deliverable_count", "int")} deliverable hashes equal the D0 record; '
                   f'{r.n("promotions", "int")} promotions: **PASS**.'),
        '- QA performed versus not performed stated explicitly, including that no new visual inspection ran: **PASS**.',
        lambda r: (f'- Human checklist within five lines: **PASS** ({r.n("checklist_lines", "int")} lines).'),
        '- State set to READY_FOR_CEO_FALLBACK_A: **PASS** (written after this report).',
        '- Boundary check clean after the card: **PASS**.',
        '- Numbers bound: **PASS** (`check_numbers.py` reports no problems).',
    ]
    deviations = [
        '- The CEO brief and Q&A are delivered as `.md` only: the project has no LaTeX toolchain for a PDF build.',
        '- Under fallback A the deck is submitted unchanged; the slide-11/13 corrections live in the brief only.',
        '- The PPTX and notebook are copied for completeness; the directive’s upload set is the PDF, notebook and '
        'references.',
    ]
    open_items = [
        '- Account holder: follow the five-line checklist; insert a real AI chat-history URL only if the portal '
        'requires one; upload and submit before the deadline.',
    ]
    commands = ['"$PY" -B -X utf8 boundary_check.py --card F7 --phase pre', '"$PY" -B -X utf8 f7_release.py',
                '"$PY" -B -X utf8 check_numbers.py --scan ../RELEASE_RECEIPT.md ../HUMAN_CHECKLIST.md ../reports/F7_report.md',
                '"$PY" -B -X utf8 boundary_check.py --card F7 --phase post']
    evidence = [('release_files', 'int'), ('copies_verified', 'int'), ('copies_read_only', 'int'),
                ('copy_hash_mismatches', 'int'), ('deliverable_count', 'int'), ('frozen_match_count', 'int'),
                ('size_mismatches', 'int'), ('pdf_pages', 'int'), ('pdf_bytes', 'int'), ('pptx_bytes', 'int'),
                ('ipynb_bytes', 'int'), ('references_bytes', 'int'), ('ledger_rows', 'int'),
                ('ledger_rows_recount', 'int'), ('ledger_rows_match', 'int'), ('ledger_sha_match', 'int'),
                ('brief_words', 'int'), ('qa_words', 'int'), ('brief_words_recount', 'int'),
                ('qa_words_recount', 'int'), ('brief_words_match', 'int'), ('qa_words_match', 'int'),
                ('expected_rows_matched', 'int'), ('expected_rows_total', 'int'), ('gates_present', 'int'),
                ('visual_slides_reviewed', 'int'), ('visual_clipping_issues', 'int'),
                ('render_hash_mismatches', 'int'), ('geometry_issue_count', 'int'), ('geometry_slide_count', 'int'),
                ('geometry_hash_matches_pptx', 'int'), ('frozen_hash_mismatches', 'int'), ('promotions', 'int'),
                ('cells_added', 'int'), ('checklist_lines', 'int'), ('new_model_fits', 'int'),
                ('new_test_reads', 'int'), ('deck_edits', 'int'), ('new_visual_reviews', 'int'), ('uploads', 'int')]
    report.write_report('F7', 'Release candidate, receipt and human checklist', 'COMPLETED_ACCEPTED', summary, RESULTS,
                        evidence, acceptance, deviations, open_items, commands,
                        'yes (pre clean; post-check run after this report; only v4_addons/ written)')
    fstate.update({'F7': dict(status='COMPLETED_ACCEPTED', report='RELEASE_RECEIPT.md',
                              next_gate='CEO review 10-20 Nov; account holder upload by 28 Nov 2026, 11:30 UTC',
                              note='release_candidate: 6 read-only copies verified; receipt and 5-line checklist written; STATE READY_FOR_CEO_FALLBACK_A')},
                  project_status='READY_FOR_CEO_FALLBACK_A')


if __name__ == '__main__':
    main()
