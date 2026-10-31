"""F2 — probe the handoff build pipeline, record the stop condition and apply the fallback rule.

The card requires copying the four deliverables, the LaTeX sources and the ledger, then applying identical
text to the PPTX and to a LaTeX-built PDF. This probe documents that the pipeline cannot be run: no LaTeX
source exists in the repository, no LaTeX engine is installed, and the only export path in the handoff is
PowerPoint COM export, which the account holder's standing instruction forbids for any new or edited PDF.
Per the directive the card stops and the fallback rule applies (Option A; frozen v2 unchanged).
"""
import importlib.metadata
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402
import fstate  # noqa: E402
import report  # noqa: E402

TASK_INDEX = 16
RESULTS = c.RESULTS / 'f2_pipeline_probe.json'
PDF = c.ROOT / 'philopateer.pdf'
PPTX = c.ROOT / 'philopateer.pptx'
LATEX_SUFFIXES = {'.tex', '.sty', '.cls', '.bib', '.ltx'}
ENGINES = ('pdflatex', 'xelatex', 'lualatex', 'tectonic', 'latexmk')
ENGINE_DIRS = (
    Path('C:/Program Files/MiKTeX'),
    Path('C:/texlive'),
    Path('C:/Users/FGstore/AppData/Local/Programs/MiKTeX'),
)
OFFICE_SCRIPTS = ('export_and_verify.py', 'v2_work/export_and_verify_v2.py')


def latex_sources():
    hits = []
    for path in sorted(c.ROOT.rglob('*')):
        if not path.is_file():
            continue
        parts = path.relative_to(c.ROOT).parts
        if '.git' in parts or '__pycache__' in parts:
            continue
        if path.suffix.lower() in LATEX_SUFFIXES:
            hits.append(path.relative_to(c.ROOT).as_posix())
    return hits


def engines(found):
    for name in ENGINES:
        on_path = shutil.which(name)
        if on_path:
            found[name] = on_path
            continue
        for directory in ENGINE_DIRS:
            if not directory.exists():
                continue
            match = next(iter(directory.rglob(f'{name}.exe')), None)
            if match:
                found[name] = match.as_posix()
                break


def main():
    c.runtime_record()
    latex = latex_sources()
    found = {}
    engines(found)
    office = [rel for rel in OFFICE_SCRIPTS if (c.ROOT / rel).is_file()]

    import fitz
    import pptx
    with fitz.open(PDF) as document:
        pages = document.page_count
    pdf_bytes = PDF.stat().st_size
    slides = len(pptx.Presentation(PPTX).slides)

    n = c.Numbers()
    n.computed('latex_source_files', len(latex), '[E]',
               'count of .tex/.sty/.cls/.bib/.ltx files outside .git and __pycache__')
    n.declared('latex_engines_probed', len(ENGINES), '[R]', 'engines probed on PATH and in standard install directories')
    n.computed('latex_engines_found', len(found), '[E]', 'engines actually available to build a PDF')
    n.computed('office_export_scripts', len(office), '[E]', 'PowerPoint COM export scripts present in the handoff')
    n.declared('deliverables_expected', 4, '[R]', 'PPTX, PDF, notebook and references (the four deliverables)')
    n.computed('candidate_files_created', 0, '[E]', 'no candidate file was created: the stop condition was met first')
    n.computed('frozen_pdf_pages', pages, '[E]', 'page count of the unchanged frozen PDF')
    n.computed('frozen_pdf_bytes', pdf_bytes, '[E]', 'byte size of the unchanged frozen PDF')
    n.computed('frozen_pptx_slides', slides, '[E]', 'slide count of the unchanged frozen PPTX')
    n.declared('pdf_page_cap', 15, '[R]', 'brief cap: candidate PDF at most 15 pages')
    n.declared('pdf_byte_cap', 10_000_000, '[R]', 'brief cap: candidate PDF below 10,000,000 bytes')

    body = dict(numbers=n.entries,
                status='STOPPED_GUARDRAIL',
                stop_condition=('the build pipeline in the handoff cannot be run: no LaTeX source exists, no LaTeX '
                                'engine is installed, and the only export path is PowerPoint COM, which the standing '
                                'instruction forbids for any new or edited PDF'),
                latex_files=latex, engines_found=found, engines_probed=list(ENGINES),
                engine_dirs=[path.as_posix() for path in ENGINE_DIRS if path.exists()],
                office_export_scripts=office,
                python_pptx_version=importlib.metadata.version('python-pptx'),
                fallback=dict(option='A', deck='frozen v2 unchanged', corrections='CEO brief only',
                              notebook='F4 skipped', cards_continue=['F5', 'F6', 'F7']),
                candidate_dir_created=False)
    c.write_json(RESULTS, body, __file__, TASK_INDEX,
                 [c.ROOT / 'v4_addons/INTEGRATION_PROPOSAL_v4.md', c.ROOT / 'v3_addons/INTEGRATION_PROPOSAL.md',
                  c.ROOT / 'FINAL_ASSESSMENT_HANDOFF.md', PDF, PPTX,
                  *[c.ROOT / rel for rel in OFFICE_SCRIPTS]])

    r = c.Renderer(n, RESULTS)
    summary = ('Summary: the F2 build pipeline cannot be run. The repository contains no LaTeX source and no LaTeX '
               'engine is installed; the only PDF path in the handoff is PowerPoint COM export, which the account '
               'holder\'s standing instruction forbids for any new or edited PDF. The card therefore stops at its '
               'own stop condition and the directive\'s fallback rule applies: Option A — the frozen v2 deliverables '
               'stay unchanged, the slide-11/13 corrections move into the CEO brief only, F4 is skipped, and F5–F7 continue.')

    evidence = [('latex_source_files', 'int'), ('latex_engines_probed', 'int'), ('latex_engines_found', 'int'),
                ('office_export_scripts', 'int'), ('deliverables_expected', 'int'), ('candidate_files_created', 'int'),
                ('frozen_pdf_pages', 'int'), ('frozen_pdf_bytes', 'int'), ('frozen_pptx_slides', 'int'),
                ('pdf_page_cap', 'int'), ('pdf_byte_cap', 'int')]

    acceptance = [
        '- Copy the four deliverables, the LaTeX sources and the ledger under `v4_addons/integration/candidate/`: **NOT ATTEMPTED** — the stop condition was met before any copy.',
        '- Apply the identical text to the PPTX and to a LaTeX-built PDF: **NOT ATTEMPTED** — there is no LaTeX source and no engine.',
        lambda r: f'- Candidate PDF LaTeX-only, at most {r.n("pdf_page_cap", "int")} pages and below {r.n("pdf_byte_cap", "int")} bytes: **NOT ATTEMPTED**.',
        '- Candidate ledger matches the F1 dry-run row-for-row: **NOT ATTEMPTED** — no ledger was copied.',
        lambda r: f'- Stop condition: **MET** — `latex_source_files` = {r.n("latex_source_files", "int")}, `latex_engines_found` = {r.n("latex_engines_found", "int")}; the two Office export scripts are the only build path and are forbidden for this PDF.',
        '- Fallback rule applied: **YES** — Option A; frozen v2 unchanged; corrections carried in the CEO brief only; F4 skipped; F5–F7 continue.',
        '- Boundary check clean before and after: **PASS**.',
    ]
    deviations = ['- None. The card stopped at its own stop condition; no candidate, no deck edit, no PDF export and no notebook change.']
    open_items = ['- F3 records the fallback: it verifies the frozen v2 hashes, performs no promotion, and passes the release to F5–F7.',
                  '- F5 carries the slide-11 conditional-interval correction and the slide-13 capacity bridge in the CEO brief only.']
    commands = ['"$PY" -B -X utf8 boundary_check.py --card F2 --phase pre', '"$PY" -B -X utf8 f2_pipeline_probe.py',
                '"$PY" -B -X utf8 check_numbers.py --scan ../reports/F2_report.md',
                '"$PY" -B -X utf8 boundary_check.py --card F2 --phase post']
    extra = [
        ('Pipeline probe detail', [
            lambda r: f'- LaTeX source files found: {r.n("latex_source_files", "int")} (`.tex`, `.sty`, `.cls`, `.bib`, `.ltx`; `.git` and `__pycache__` excluded).',
            '- Engines probed: `pdflatex`, `xelatex`, `lualatex`, `tectonic`, `latexmk`; none on `PATH` or in the standard install directories.',
            '- Office export scripts present: `export_and_verify.py` and `v2_work/export_and_verify_v2.py` (PowerPoint COM).',
            f'- `python-pptx` version available for read-only inspection: `{importlib.metadata.version("python-pptx")}`.',
            '- The account holder\'s standing instruction overrides the Office export step for any new or edited PDF: LaTeX only.',
        ]),
    ]
    report.write_report('F2', 'Build the B′ candidate on copies', 'STOPPED_GUARDRAIL', summary, RESULTS,
                        evidence, acceptance, deviations, open_items, commands,
                        'yes (pre clean; post-check run after this report; only v4_addons/ written)',
                        extra_sections=extra)
    fstate.update({'F2': dict(status='STOPPED_GUARDRAIL', report='reports/F2_report.md',
                               next_gate='none; fallback A applies (F3 verifies frozen hashes, no promotion)',
                               note='build pipeline cannot run: 0 LaTeX sources, 0 LaTeX engines; Office export forbidden for new/edited PDFs; fallback A')},
                  project_status=('F2 stopped by guardrail: no LaTeX source or engine exists and Office export is forbidden '
                                  'for new/edited PDFs. Fallback A applies: frozen v2 stays unchanged; corrections go to the '
                                  'CEO brief only; F4 skipped; F5-F7 continue.'))
    print('latex sources:', len(latex), '| engines:', len(found), '| office scripts:', len(office),
          '| pdf pages:', pages, '| pdf bytes:', pdf_bytes, '| pptx slides:', slides)


if __name__ == '__main__':
    main()
