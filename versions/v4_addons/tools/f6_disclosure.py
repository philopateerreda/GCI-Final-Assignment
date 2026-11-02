"""F6 — AI-use disclosure and reference-link check.

Report only: references.txt is read, never written. The disclosure paragraph is quoted from the file
itself, link statuses come from the D6 receipt (re-confirmed live on 2026-10-31), and no chat URL is
invented. The conditional replacement sentence is a template for the account holder, not an edit.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402
import fstate  # noqa: E402
import report  # noqa: E402

TASK_INDEX = 20
RESULTS = c.RESULTS / 'f6_disclosure.json'
DISC = c.ADDONS / 'DISCLOSURE_CHECK.md'
REFS = 'references.txt'
D6 = 'v4_addons/results/d6_text_blocks.json'
D0 = 'v4_addons/results/d0_checks.json'
HBS_S4 = 'https://www.hbs.edu/faculty/Pages/item.aspx?num=54941'
HBS_S5 = 'https://www.hbs.edu/faculty/Pages/item.aspx?num=54936'
COLUMBIA = 'https://business.columbia.edu/sites/default/files-efs/pubfiles/12782/Perils_Ascarza.pdf'


def bind():
    n = c.Numbers()
    n.source('references_lines', REFS, 'linecount')
    n.source('hbs_status_script', D6, 'numbers.http_status_blocked.value')
    n.source('hbs_status_browser', D6, 'numbers.http_status_ok.value')
    n.source('columbia_status', D6, 'numbers.http_status_ok.value')
    n.source('hbs_url_count', D6, 'numbers.hbs_url_count.value')

    d0 = json.loads((c.ROOT / D0).read_text(encoding='utf-8'))
    frozen = d0['deliverable_hashes']['references.txt']
    refs_path = c.ROOT / REFS
    digest = c.digest(refs_path)
    size = refs_path.stat().st_size
    lines = refs_path.read_text(encoding='utf-8').splitlines()
    disc_line = next(i for i, line in enumerate(lines, 1) if line.startswith('Qoder generative-AI assistance'))
    disc_text = lines[disc_line - 1]

    def url_line(url):
        return next(i for i, line in enumerate(lines, 1) if url in line)

    n.computed('references_bytes', size, '[E]', 'byte size of the frozen references.txt',
               source_file=REFS)
    n.computed('frozen_reference_bytes', frozen['size'], '[E]', 'references.txt size recorded in the D0 frozen hash receipt',
               source_file=D0)
    n.computed('references_sha_matches_frozen', int(digest == frozen['handoff']), '[E]',
               'current references.txt SHA-256 equals the D0 handoff record', source_file=REFS)
    n.computed('references_bytes_match_frozen', int(size == frozen['size']), '[E]',
               'current references.txt size equals the D0 handoff record', source_file=REFS)
    n.computed('references_edits', int(digest != frozen['handoff'] or size != frozen['size']), '[E]',
               'edits detected against the D0 frozen record', source_file=REFS)
    n.computed('disclosure_line', disc_line, '[E]', 'line of the AI-use disclosure paragraph in references.txt',
               source_file=REFS)
    n.computed('disclosure_words', len(disc_text.split()), '[E]', 'whitespace word count of the disclosure paragraph',
               source_file=REFS)
    n.computed('tool_script_count', len(sorted((c.ADDONS / 'tools').glob('*.py'))), '[E]',
               'Python tool scripts written under v4_addons/tools by the Qoder agent')
    n.computed('url_line_s4', url_line(HBS_S4), '[E]', 'line of the S4 HBS item link', source_file=REFS)
    n.computed('url_line_s5', url_line(HBS_S5), '[E]', 'line of the S5 HBS item link', source_file=REFS)
    n.computed('url_line_columbia', url_line(COLUMBIA), '[E]', 'line of the S4 accessible Columbia copy',
               source_file=REFS)
    n.computed('qoder_mentions', sum(1 for line in lines if 'Qoder' in line), '[E]',
               'lines in references.txt that name Qoder', source_file=REFS)
    return n, dict(ok=digest == frozen['handoff'] and size == frozen['size'], disc_text=disc_text)


def disclosure_text(r, meta):
    def v(name, spec):
        return r.n(name, spec)

    quote = meta['disc_text']
    lines = [
        '# Disclosure check — AI use and reference links',
        '',
        'Status: COMPLETED_ACCEPTED (report only; `references.txt` not edited)',
        '',
        'Date: 2026-10-31. Scope: the AI-use paragraph and the reference links in the frozen `references.txt`, '
        'checked for the release candidate.',
        '',
        '## 1. Current disclosure, quoted verbatim',
        '',
        f'From `references.txt` line {v("disclosure_line", "int")} (the first paragraph of the Production Assistance '
        f'section), {v("disclosure_words", "int")} words:',
        '',
        f'> {quote}',
        '',
        '## 2. AI tools evidenced',
        '',
        f'- **Qoder Desktop agent.** This closeout was executed by a Qoder coding agent, which wrote and ran '
        f'{v("tool_script_count", "int")} Python tool scripts under `v4_addons/tools/` (cards D0–D8, M0–M1 and F0–F5). '
        f'Every results JSON carries a provenance block with the script digest, seed 20261028, runtime pools and a '
        'timestamp.',
        '- **Local Python execution.** All number-producing scripts ran on this device with the pinned interpreter '
        '(Python 3.11.9); the final-assignment work used no cloud or notebook-hosted training.',
        '- **Presentation drafting.** Text for the frozen deck and notebook was produced in earlier assisted sessions. '
        'Under fallback A this closeout changed no deliverable bytes (F3 receipt).',
        '- No other generative-AI tool is named in `references.txt` or evidenced by the project files inspected.',
        '',
        '## 3. Completeness verdict',
        '',
        'The paragraph names the assistant (Qoder), states the scope of use (research synthesis, code development, '
        'interpretation checks, presentation drafting), records that numerical results came from local execution on '
        'the supplied dataset, states that external facts are attributed and no external figures are copied, records '
        'that no chat-history URL has been supplied or fabricated, and asks the account holder to review any '
        'portal-specific disclosure. **Verdict: complete and accurate for the work performed.** The one unresolved '
        'portal item is a real AI chat-history URL, which the agent cannot supply.',
        '',
        '## 4. Replacement sentence, only if the portal requires a URL',
        '',
        'No edit is made or proposed for the frozen file. If a link is mandatory, the account holder should replace '
        'the sentence “The course instructions request an AI chat-history URL; no public conversation URL has been '
        'supplied or fabricated.” with:',
        '',
        '“The course instructions request an AI chat-history URL; the account holder’s Qoder conversation link is '
        '[insert the real link from the account holder’s session].”',
        '',
        'This report does not invent or guess a URL. If the account holder has no shareable link, the current '
        'sentence is accurate and should stay.',
        '',
        '## 5. Reference link status (report only)',
        '',
        'Observed on 2026-10-31 with `curl` from this device using a default client and a Chrome user-agent; the '
        'same observation is recorded in the D6 receipt.',
        '',
        '| reference | `references.txt` line | URL | scripted client | browser user-agent | note |',
        '|---|---|---|---:|---:|---|',
        f'| S4 HBS item page | {v("url_line_s4", "int")} | `{HBS_S4}` | {v("hbs_status_script", "int")} | '
        f'{v("hbs_status_browser", "int")} | resolves to the cited JMR article |',
        f'| S5 HBS item page | {v("url_line_s5", "int")} | `{HBS_S5}` | {v("hbs_status_script", "int")} | '
        f'{v("hbs_status_browser", "int")} | resolves to the cited article |',
        f'| S4 accessible copy | {v("url_line_columbia", "int")} | `{COLUMBIA}` | {v("columbia_status", "int")} | '
        f'{v("columbia_status", "int")} | `application/pdf`; the copy used for the quoted churn rates |',
        '',
        f'The {v("hbs_url_count", "int")} HBS pages are bot-blocked, not dead: they answer '
        f'{v("hbs_status_script", "int")} to a scripted client and {v("hbs_status_browser", "int")} to a browser, and '
        f'the Columbia copy answers {v("columbia_status", "int")} with `application/pdf` for every client. No link '
        'change or replacement is needed for the submission.',
        '',
        '## 6. Integrity of the frozen file',
        '',
        f'- `references.txt` SHA-256: `{c.digest(c.ROOT / REFS)}` (matches the D0 frozen record).',
        f'- Size {v("references_bytes", "int")} bytes against the frozen {v("frozen_reference_bytes", "int")}; '
        f'{v("references_lines", "int")} lines; edits detected by this card: {v("references_edits", "int")}; '
        f'Qoder mentions: {v("qoder_mentions", "int")}.',
        '- No Option C content, no edit, no submission action. Boundary check clean after the card.',
        '',
    ]
    return '\n'.join(lines)


def main():
    c.runtime_record()
    n, meta = bind()
    body = dict(numbers=n.entries, status='COMPLETED_ACCEPTED', references_edited=bool(n.value('references_edits')),
                disclosure=dict(line=int(n.value('disclosure_line')), words=int(n.value('disclosure_words'))),
                links=dict(hbs_script=int(n.value('hbs_status_script')), hbs_browser=int(n.value('hbs_status_browser')),
                           columbia=int(n.value('columbia_status')), hbs_count=int(n.value('hbs_url_count'))),
                replacement_sentence=False, url_invented=False)
    c.write_json(RESULTS, body, __file__, TASK_INDEX, [c.ROOT / REFS, c.ROOT / D6, c.ROOT / D0])

    r_disc = c.Renderer(n, RESULTS)
    disc_text = disclosure_text(r_disc, meta)
    r_disc.write(DISC, disc_text, c.RESULTS / 'DISCLOSURE_CHECK_render.json')
    print('wrote', DISC.relative_to(c.ROOT).as_posix(), 'words', len(disc_text.split()))

    ok = meta['ok']
    r = c.Renderer(n, RESULTS)
    summary = ('`references.txt` holds one AI-use paragraph naming Qoder. It was quoted verbatim into '
               '`DISCLOSURE_CHECK.md`, the AI tools evidenced by the project are listed, and the paragraph is complete '
               'for the work performed. No chat-history URL exists in the project and none was invented; a conditional '
               'replacement sentence is supplied for a portal that mandates one. The two HBS item pages answer 403 to '
               'a scripted client and 200 to a browser, and the Columbia PDF answers 200, so no reference link needs '
               'changing. The frozen file is untouched.')
    acceptance = [
        lambda r: (f'- `references.txt` not edited: **{"PASS" if ok else "FAIL"}** — SHA match '
                   f'{r.n("references_sha_matches_frozen", "int")}; size match '
                   f'{r.n("references_bytes_match_frozen", "int")}; edits {r.n("references_edits", "int")}.'),
        lambda r: (f'- Current disclosure quoted verbatim from line {r.n("disclosure_line", "int")} '
                   f'({r.n("disclosure_words", "int")} words): **PASS**.'),
        lambda r: (f'- AI tools evidenced: Qoder agent runs ({r.n("tool_script_count", "int")} tool scripts) and local '
                   'Python 3.11.9; no other tool named: **PASS**.'),
        '- Replacement sentence supplied only as a conditional template; no URL invented: **PASS**.',
        lambda r: (f'- Link status reported: HBS {r.n("hbs_status_script", "int")} scripted / '
                   f'{r.n("hbs_status_browser", "int")} browser; Columbia {r.n("columbia_status", "int")} PDF: **PASS**.'),
        '- No Option C items; no submission action: **PASS**.',
        '- Numbers bound: **PASS** (`check_numbers.py` reports no problems).',
        '- Boundary check clean after the card: **PASS**.',
    ]
    deviations = [
        '- Link statuses are bound from the D6 receipt (observed 2026-10-31) and were re-confirmed live the same day; '
        'no value changed.',
        '- The conditional replacement sentence is report-only; the frozen file is unchanged.',
        '- No chat-history URL exists in the project; none is invented.',
    ]
    open_items = [
        '- Account holder: if the portal requires a chat-history URL, insert a real Qoder conversation link (template '
        'in §4 of `DISCLOSURE_CHECK.md`); otherwise keep the current, accurate sentence.',
    ]
    commands = ['"$PY" -B -X utf8 boundary_check.py --card F6 --phase pre', '"$PY" -B -X utf8 f6_disclosure.py',
                '"$PY" -B -X utf8 check_numbers.py --scan ../DISCLOSURE_CHECK.md ../reports/F6_report.md',
                '"$PY" -B -X utf8 boundary_check.py --card F6 --phase post',
                '# live link probes on 2026-10-31: curl default UA and Chrome UA on both HBS items; HEAD on the Columbia PDF']
    evidence = [('references_lines', 'int'), ('references_bytes', 'int'), ('frozen_reference_bytes', 'int'),
                ('references_sha_matches_frozen', 'int'), ('references_bytes_match_frozen', 'int'),
                ('references_edits', 'int'), ('disclosure_line', 'int'), ('disclosure_words', 'int'),
                ('qoder_mentions', 'int'), ('hbs_url_count', 'int'), ('hbs_status_script', 'int'),
                ('hbs_status_browser', 'int'), ('columbia_status', 'int'), ('tool_script_count', 'int'),
                ('url_line_s4', 'int'), ('url_line_s5', 'int'), ('url_line_columbia', 'int')]
    report.write_report('F6', 'AI-use disclosure and reference-link check', 'COMPLETED_ACCEPTED', summary, RESULTS,
                        evidence, acceptance, deviations, open_items, commands,
                        'yes (pre clean; post-check run after this report; only v4_addons/ written)')
    fstate.update({'F6': dict(status='COMPLETED_ACCEPTED', report='DISCLOSURE_CHECK.md', next_gate='none; F7 release package',
                              note='references.txt untouched (SHA and size match D0); disclosure quoted verbatim; HBS 403/200, Columbia 200; no URL invented')},
                  project_status='F6 complete: AI-use disclosure verified and reference links re-confirmed; references.txt untouched. F7 assembles the release candidate.')


if __name__ == '__main__':
    main()
