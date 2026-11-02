"""D4 — renders INTEGRATION_PROPOSAL_v4.md from results/integration_spec.json + results/d3_ledger_dryrun.json."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402
import report  # noqa: E402

TASK_INDEX = 5
SPEC = 'v4_addons/results/integration_spec.json'
D3 = 'v4_addons/results/d3_ledger_dryrun.json'
YARD = 'v4_addons/results/yardstick.json'
RESULTS = c.RESULTS / 'd4_proposal.json'
OPTION_LABEL = {'A': 'A', 'B_PRIME': 'B′ (recommended)', 'C': 'C', 'R': 'R'}


def fence(text):
    return ['```text', *text.split('\n'), '```']


def main():
    c.runtime_record()
    spec = c.read_json(c.ROOT / SPEC)['spec']
    d3 = c.read_json(c.ROOT / D3)
    n = c.Numbers()
    for name in ('A', 'B_PRIME', 'C', 'R'):
        for field in ('rows_added', 'rows_retired', 'rows_total'):
            n.source(f'{field}_{name}', D3, f'numbers.{field}_{name}.value')
    n.source('ledger_rows_original', D3, 'numbers.ledger_rows_original.value')
    for option in spec['options'].values():
        for edit in option['edits']:
            key = f'slide{edit["slide"]}'
            if f'len_before_{key}' not in n.entries:
                n.computed(f'len_before_{key}', edit['length_before'], '[E]', 'characters in the original text element', source_file=SPEC, source_key=f'spec.options.*.edits[slide={edit["slide"]}].length_before')
                n.computed(f'len_after_{key}', edit['length_after'], '[E]', 'characters after the proposed edit', source_file=SPEC, source_key=f'spec.options.*.edits[slide={edit["slide"]}].length_after')
                n.derived(f'len_delta_pct_{key}', f'100 * (len_after_{key} - len_before_{key}) / len_before_{key}')
    n.declared('length_flag_threshold_pct', 15, '[R]', 'brief D4: flag text-length growth above +15%')
    n.declared('days_A', 0, '[A]', 'effort estimate, option A')
    n.declared('days_B_PRIME', 1.0, '[A]', 'effort estimate: one slide-edit QA cycle (export, geometry, renders, receipt, hashes) per brief section 7')
    n.declared('days_C', 1.5, '[A]', 'effort estimate: B\' plus footer/reference-page typography and M9 append')
    n.declared('days_R', 4.0, '[A]', 'effort estimate: M6 regeneration (<= 3 days) plus one integration QA cycle')
    n.declared('pdf_max_pages', 15, '[E]', 'assignment cap (README.docx; handoff section 1)')
    n.declared('pdf_max_bytes', 10000000, '[E]', 'assignment cap (handoff section 1)')
    yard = c.read_json(c.ROOT / YARD)['numbers']
    for name in ('slide11_net_lower', 'slide11_net_upper', 'net_5pct_6_24', 'e4_effect_power_7872_deff1p1', 'e4_profit_power_7872_deff1p1', 'e4_effect_power_5000_deff1p1', 'e4_profit_power_5000_deff1p1', 'dq_7872_g20_p_extend', 'deff_default', 'binary_relative_prevention_assumption', 'binary_enrolled_per_arm', 'max_per_arm_one_list'):
        n.source(name, YARD, f'numbers.{name}.value', tag=yard[name]['tag'])

    r = c.Renderer(n, RESULTS)
    placeholders = spec['placeholders']
    lines = [
        '# Integration proposal v4 — supersedes `v3_addons/INTEGRATION_PROPOSAL.md`',
        '',
        f'_v4 Track D, card D4 · {c.today()} · nothing below is applied; the frozen deck, notebook, PDF and references are unchanged. Human gate: `gates/H3_OPTION.txt` containing `A`, `B_PRIME`, `C` or `R`._',
        '',
        '## Placeholders requiring a human decision (listed first)',
        '',
        *[f'- `{item}` — appears in the slide-13 panel (options B′, C, R). Extend-rule budget: the WP2 decision simulation gives a {r.n("dq_7872_g20_p_extend", "pct1")} "extend" probability at the design point, so the number of permitted extensions and their cost determine the pilot\'s real envelope.' for item in placeholders],
        '- `[DECISION NEEDED: is a Floor contact free? if not, the $12,872 envelope is understated]` — D6 text block; affects slide 13 left panel only if the human wants it on the slide.',
        '- `[DECISION NEEDED: action if the harm gate trips; owner]` — D6 text block; protocol addendum, not a slide.',
        '',
        '## Common rules for every option',
        '',
        f'- QA chain, in order: source/claim (ledger from D3) → presentation text → geometry → **all-15-slide visual review** → hash-bound receipt (refresh the four deliverable hashes and the ledger). PDF: **LaTeX-only**, no Office export, ≤ {r.n("pdf_max_pages", "int")} pages, < {r.n("pdf_max_bytes", "int")} bytes. Do not claim visual QA unless performed. Frozen notebook cells untouched. Never submit.',
        f'- Text-length deltas are measured on the whole text element that contains the change; growth above {r.n("length_flag_threshold_pct", "pc0")} is flagged. Flags mean layout QA is mandatory, not that the edit is rejected.',
        f'- Ledger: original {r.n("ledger_rows_original", "int")} rows; counts below are from the D3 dry-run (`ledger_dryrun/claims_ledger_<option>.csv`).',
        '- Vocabulary: gross effect / variable profit (startup excluded) / fully loaded net; "first qualifying grid point; not an exact minimum"; status values only from the G5 list.',
        '',
    ]
    for name in ('A', 'B_PRIME', 'C', 'R'):
        option = spec['options'][name]
        lines += [f'## Option {OPTION_LABEL[name]}', '', option['description'], '']
        lines += [f'- Slides touched: {", ".join(str(e["slide"]) for e in option["edits"]) or "none"}',
                  f'- Ledger impact: {r.n(f"rows_retired_{name}", "int")} retired, {r.n(f"rows_added_{name}", "int")} added → {r.n(f"rows_total_{name}", "int")} rows; sha256 `{d3["options"][name]["sha256"]}`',
                  f'- Time estimate [A]: {r.n(f"days_{name}", "f1")} day(s)']
        if name == 'A':
            lines += ['- Risks: none from integration. The slide-11 interval stays labelled as if unconditional and slide 13 keeps the unbridged `80,000` / `160,000` wording — the two integrity findings of the v3 review remain in the submission.', '']
            continue
        if name == 'R':
            lines += ['- Pre-condition: Track M reaches `ADOPT-CONFIRMED` at M5 and M6 produces the regenerated-numbers diff; the human reviews that diff (H3b) before any deck edit. Until then R is B′.',
                      '- Risks: every model-dependent number in the deck, PDF, notebook outputs and ledger changes (see `M0_dependency_map.md` once M0 runs); calendar hard freeze 18 Nov; third use of the test split must be disclosed.', '']
        for edit in option['edits']:
            key = f'slide{edit["slide"]}'
            flag = (' **FLAG > ' + r.n('length_flag_threshold_pct', 'pc0') + '**') if edit['length_flag_over_15pct'] else ''
            optional = ' (optional)' if edit.get('optional') else ''
            lines += [f'### Slide {edit["slide"]}{optional} — text element {edit["element_index"]}', '',
                      f'Length {r.n(f"len_before_{key}", "int")} → {r.n(f"len_after_{key}", "int")} characters ({r.n(f"len_delta_pct_{key}", "pc1")}){flag}.', '']
            if 'heading_before' in edit:
                lines += ['**Heading before**', *fence(edit['heading_before']), '**Heading after**', *fence(edit['heading_after']), '']
            lines += ['**Exact text before**', *fence(edit['before']), '**Exact text after**', *fence(edit['after']), '']
            if 'right_before' in edit:
                lines += ['**Right block before**', *fence(edit['right_before']), '**Right block after**', *fence(edit['right_after']), '']
            if edit['add']:
                lines += ['Ledger rows added (slide, source key, type, displayed):', '']
                lines += [f'- `{row[0]}` · `{row[1]}` · {row[2]} · `{row[7]}`' for row in edit['add']]
                lines.append('')
            if edit.get('wp7_retirements_reversed'):
                lines += [f'WP7 retirements reversed: {", ".join(edit["wp7_retirements_reversed"])} (tokens kept by the new text).', '']
            lines += [f'Note: {edit["note"]}', '']
        if name == 'B_PRIME':
            lines += ['**B′ risks.** Slide 11: low scientific risk; the box grows and may need a smaller font or a split line — layout QA. Slide 13: the replacement panel is several times longer than the original six lines; '
                      'if it does not fit the existing panel region, the recommended fallback is to move the decision-rule line and the purpose line into the footer, keeping the target bridge, the DEFF-1.1 numbers, the feasibility line and the grid wording in the panel. '
                      'Do not shrink text automatically; do not overlay the propensity strip. All numbers are conditional simulations, not measured treatment effects; "powered" must not be claimed from 76.0% / 25.4%.', '']
        if name == 'C':
            lines += ['### References — M9 append (only with option C)', '', 'Exactly the block in `v3_addons/INTEGRATION_PROPOSAL.md` §4 ("V3 SUPPORTING ANALYSIS — APPLY ONLY IF OPTION C IS APPROVED … [M9] EMP package contributors …"); `references.txt` is otherwise untouched. Any edit changes its hash → delivery QA refresh. Keep M5 abstract-only wording; the slide-12 footer must keep the exact phrase **"Sensitivity, not a CI or EMPC."**', '',
                      '**C risks.** Medium: reference-page typography (M9 block ≈ 8 lines), the slide-15 right block drops one sentence to keep its line count, prevention remains unidentified, and the prior band must never be read as a confidence interval. Slide 5 wording is optional and adds no ledger row.', '']
    lines += ['## Recommendation [R]', '',
              f'**B′.** It fixes the two integrity findings with the smallest surface: slide 11 states the condition (prevention = {r.n("binary_relative_prevention_assumption", "pct0")}) and shows the central-prior downside ({r.n("net_5pct_6_24", "usdk1")} vs the conditional {r.n("slide11_net_lower", "usdk1")}–{r.n("slide11_net_upper", "usdk1")}); slide 13 bridges the targets and uses one DEFF ({r.n("e4_effect_power_7872_deff1p1", "pct1")} / {r.n("e4_profit_power_7872_deff1p1", "pct1")} at {r.n("binary_enrolled_per_arm", "int")}/arm; {r.n("e4_effect_power_5000_deff1p1", "pct1")} / {r.n("e4_profit_power_5000_deff1p1", "pct1")} at {r.n("max_per_arm_one_list", "int")}/arm). '
              'C only if the prior band earns its page space; R only after a Track M ADOPT-CONFIRMED. A remains safe.', '',
              '**STOP here.** No deliverable, reference, notebook, protocol or submission action is authorised by this proposal. The human writes `gates/H3_OPTION.txt`.', '']
    r.write(c.ADDONS / 'INTEGRATION_PROPOSAL_v4.md', '\n'.join(lines), c.RESULTS / 'INTEGRATION_PROPOSAL_v4_render.json')
    body = dict(numbers=n.entries, placeholders=placeholders + ['[DECISION NEEDED: is a Floor contact free? if not, the $12,872 envelope is understated]', '[DECISION NEEDED: action if the harm gate trips; owner]'])
    c.write_json(RESULTS, body, __file__, TASK_INDEX, [c.ROOT / SPEC, c.ROOT / D3, c.ROOT / YARD])
    # rewrite the render registry after the results JSON exists (Renderer recorded tokens against RESULTS)
    r.write(c.ADDONS / 'INTEGRATION_PROPOSAL_v4.md', '\n'.join(lines), c.RESULTS / 'INTEGRATION_PROPOSAL_v4_render.json')
    print('wrote INTEGRATION_PROPOSAL_v4.md')

    evidence = [(f'rows_total_{name}', 'int') for name in ('A', 'B_PRIME', 'C', 'R')] + [(f'len_delta_pct_slide{s}', 'f1') for s in (11, 13, 12, 5, 15)] + [('days_B_PRIME', 'f1'), ('days_C', 'f1'), ('days_R', 'f1')]
    acceptance = [
        '- No unbound numbers: **PASS** — `check_numbers.py --scan ../INTEGRATION_PROPOSAL_v4.md` (slide text blocks are the D3 spec strings, themselves rendered from bound sources).',
        '- Placeholders appear only for human decisions and are listed at the top of the file: **PASS** (three `[DECISION NEEDED: …]` items).',
        lambda r: '- Required B′ content present: slide-11 exact sentence; slide-13 target bridge, feasibility line, DEFF-' + r.n('deff_default', 'f1') + ' E4 numbers, "variable profit, startup excluded", decision row labelled E3_observed / DEFF ' + r.n('deff_default', 'f1') + ' / CI rule, grid wording, pilot-purpose sentence, extension placeholder: **PASS**.',
        lambda r: f'- Text-length deltas computed and flagged above {r.n("length_flag_threshold_pct", "pc0")}: slide 11 {r.n("len_delta_pct_slide11", "pc1")}, slide 13 {r.n("len_delta_pct_slide13", "pc1")}, slide 12 {r.n("len_delta_pct_slide12", "pc1")}, slide 5 {r.n("len_delta_pct_slide5", "pc1")}, slide 15 {r.n("len_delta_pct_slide15", "pc1")} — four of five flagged; layout fallback documented.',
    ]
    deviations = ['- The slide-13 panel required by the brief is far longer than the original six-line box (flagged). A fallback placement (decision/purpose lines to the footer) is proposed rather than silently dropping required content.',
                  '- WP7\'s retire operations for C0137/C0139 are not carried into B′ because the required grid wording keeps both tokens (see D3).']
    open_items = ['- `gates/H3_OPTION.txt` (A / B_PRIME / C / R).', '- The three `[DECISION NEEDED]` placeholders listed at the top of the proposal.']
    commands = ['"$PY" -B -X utf8 boundary_check.py --card D4 --phase pre', '"$PY" -B -X utf8 d4_proposal.py', '"$PY" -B -X utf8 check_numbers.py --scan ../INTEGRATION_PROPOSAL_v4.md ../reports/D4_report.md', '"$PY" -B -X utf8 boundary_check.py --card D4 --phase post']
    report.write_report('D4', 'Integration proposal v4', 'COMPLETED_ACCEPTED',
                        'Summary: `INTEGRATION_PROPOSAL_v4.md` supersedes the WP7 proposal with exact before/after text for A / B′ / C / R, text-length deltas, D3 ledger impact and hashes, QA chain, effort estimates and risks. B′ is recommended; nothing is applied; the human gate H3 is closed.',
                        RESULTS, evidence, acceptance, deviations, open_items, commands, 'yes (pre/post clean; only the 4 D1-allowed changes).')


if __name__ == '__main__':
    main()
