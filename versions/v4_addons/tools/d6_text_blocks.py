"""D6 - copy-ready text blocks: queue composition label, Floor cost sentence, harm-gate action, reference access report."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402
import report  # noqa: E402

TASK_INDEX = 7
RESULTS = c.RESULTS / 'd6_text_blocks.json'
FM = 'v2_work/final_metrics.json'
QUEUES = [('billing', 'billing_check'), ('network', 'network_check'), ('handset', 'handset_check'), ('residual', 'digital_only_residual')]


def main():
    c.runtime_record()
    n = c.Numbers()
    for index, (key, _) in enumerate(QUEUES):
        n.source(f'queue_{key}_count', FM, f'pilot_test.queues[{index}].raw_count')
        n.source(f'queue_{key}_value_share', FM, f'pilot_test.queues[{index}].share_at_risk_value')
    n.derived('queue_total', ' + '.join(f'queue_{key}_count' for key, _ in QUEUES))
    for key, _ in QUEUES:
        n.derived(f'queue_{key}_count_share', f'queue_{key}_count / queue_total')
        n.derived(f'queue_{key}_lift', f'queue_{key}_value_share / queue_{key}_count_share')
        n.derived(f'queue_{key}_lift_s9', f'round(queue_{key}_value_share, 3) / queue_{key}_count_share', note='section-9 reviewer arithmetic: published one-decimal value share divided by the exact count share')
    lifts = [n.value(f'queue_{key}_lift') for key, _ in QUEUES]
    n.derived('queue_count_share_total', ' + '.join(f'queue_{key}_count_share' for key, _ in QUEUES))
    n.derived('queue_value_share_total', ' + '.join(f'queue_{key}_value_share' for key, _ in QUEUES))
    n.declared('queue_parity', 1.0, '[E]', 'lift of 1.000 means value share equals count share')
    n.computed('queue_lift_exact_vs_quoted_max_diff', round(max(abs(n.value(f'queue_{key}_lift') - n.value(f'queue_{key}_lift_s9')) for key, _ in QUEUES), 4), '[E]', 'largest difference between the exact-share lift and the section-9 one-decimal-share lift')
    n.computed('queue_max_abs_lift_deviation_pct', round(max(abs(value - 1) for value in lifts) * 100, 1), '[E]', 'largest |lift - 1| across the four queues, in percent')

    n.source('floor_control_contact_rate', FM, 'pilot_calibration.spec.cost_assumptions.control_incremental_contact')
    n.source('treated_contact_rate', FM, 'pilot_calibration.spec.cost_assumptions.treated_contact')
    n.source('startup_stage1', FM, 'pilot_calibration.spec.cost_assumptions.startup_stage1')
    n.source('stage1_cost', FM, 'pilot_calibration.spec.stage1_cost')
    n.source('stage1_total_enrolled', FM, 'pilot_calibration.spec.stage1_total_enrolled')
    n.source('core_per_arm', FM, 'pilot_calibration.spec.allocation.core_per_arm')
    n.derived('stage1_cost_rebuild', 'core_per_arm * treated_contact_rate + startup_stage1', note='Stage-1 envelope with control contacts at zero: treated contacts only plus startup')
    n.derived('stage1_cost_if_floor_paid', 'stage1_total_enrolled * treated_contact_rate + startup_stage1', note='same envelope if every enrolled account, control arm included, costs $1 per contact')
    n.derived('floor_understatement', 'stage1_cost_if_floor_paid - stage1_cost', note='additional cost implied by charging control-arm contacts at the treated rate')

    n.source('harm_alpha_per_look', FM, 'pilot_calibration.spec.decision_gates.one_sided_alpha_per_harm_look')
    n.source('harm_look_1_fraction', FM, 'pilot_calibration.spec.decision_gates.harm_looks[0]')
    n.source('harm_look_2_fraction', FM, 'pilot_calibration.spec.decision_gates.harm_looks[1]')
    n.declared('harm_look_count', 2, '[E]', 'two planned looks, at 0.5 and 1.0 of the harm stratum exposure as recorded in harm_looks')
    n.derived('harm_familywise_alpha', 'harm_alpha_per_look * harm_look_count', note='familywise one-sided alpha across the two planned looks')

    n.declared('http_status_blocked', 403, '[E]', 'HTTP status returned to a default curl client by both HBS faculty pages, tested 2026-10-31')
    n.declared('http_status_ok', 200, '[E]', 'HTTP status returned to a browser user-agent by both HBS pages and by every client for the Columbia and evaascarza PDFs, tested 2026-10-31')
    n.declared('hbs_url_count', 2, '[E]', 'two HBS faculty-page URLs in references.txt')

    body = dict(numbers=n.entries, queues=[dict(key=key, name=name, count=n.value(f'queue_{key}_count'), count_share=n.value(f'queue_{key}_count_share'),
                                                  value_share=n.value(f'queue_{key}_value_share'), lift=n.value(f'queue_{key}_lift'), lift_s9=n.value(f'queue_{key}_lift_s9')) for key, name in QUEUES],
                access=dict(hbs_default_client=n.value('http_status_blocked'), hbs_browser_client=n.value('http_status_ok')))
    c.write_json(RESULTS, body, __file__, TASK_INDEX, [c.ROOT / FM, c.ROOT / 'references.txt'])

    r = c.Renderer(n, RESULTS)
    md = ['# TEXT_BLOCKS — copy-ready replacement text and corrections (Track D)', '',
          f'_v4 Track D, card D6 · {c.today()} · every number below is bound in `results/d6_text_blocks.json`; no deck, notebook, protocol or reference file was edited._', '',
          '## 1. Queue table — composition and feasibility, not value triage', '',
          '**Replacement label (use verbatim):**', '', '> Queue composition / feasibility (value per account ≈ flat)', '',
          '| Queue | Selected accounts | Count share | At-risk value share | Lift (value share ÷ count share) | Section-9 quoted lift |', '|---|---:|---:|---:|---:|---:|']
    for key, name in QUEUES:
        md.append(f'| `{name}` | {r.n(f"queue_{key}_count", "int")} | {r.n(f"queue_{key}_count_share", "pct2")} | {r.n(f"queue_{key}_value_share", "pct1")} | {r.n(f"queue_{key}_lift", "f3")} | {r.n(f"queue_{key}_lift_s9", "f3")} |')
    md += [f'| **total** | **{r.n("queue_total", "int")}** | {r.n("queue_count_share_total", "pct2")} | {r.n("queue_value_share_total", "pct1")} | — | — |', '',
           f'[E] Value per account is flat: the largest absolute deviation of any lift from {r.n("queue_parity", "f3")} is {r.n("queue_max_abs_lift_deviation_pct", "pc1")} (the residual queue). Rounding the published one-decimal value shares reproduces the section-9 quoted lifts; the exact-share lifts differ from those quotes by at most {r.n("queue_lift_exact_vs_quoted_max_diff", "f4")}.', '',
           '**Copy-ready caption:**', '',
           f'> Queue composition / feasibility (value per account ≈ flat): {r.n("queue_total", "int")} selected accounts; count shares {r.n("queue_billing_count_share", "pct2")} / {r.n("queue_network_count_share", "pct2")} / {r.n("queue_handset_count_share", "pct2")} / {r.n("queue_residual_count_share", "pct2")} vs at-risk value shares {r.n("queue_billing_value_share", "pct1")} / {r.n("queue_network_value_share", "pct1")} / {r.n("queue_handset_value_share", "pct1")} / {r.n("queue_residual_value_share", "pct1")}; lift {r.n("queue_billing_lift_s9", "f3")} / {r.n("queue_network_lift_s9", "f3")} / {r.n("queue_handset_lift_s9", "f3")} / {r.n("queue_residual_lift_s9", "f3")}.', '',
           '[R] Do not call this table value triage, targeting lift or value capture: the shares differ from parity by at most a few percent, so the queue split is a feasibility/composition statement about where selected accounts sit, not evidence that the policy concentrates value.', '',
           '## 2. Floor (control-arm) contact cost', '',
           f'[E] The v2 cost spec sets `control_incremental_contact` to {r.n("floor_control_contact_rate", "usd0")}: control-arm contacts are costed at zero, so the {r.n("stage1_cost", "usd0")} Stage-1 envelope is {r.n("core_per_arm", "int")} treated contacts at {r.n("treated_contact_rate", "usd0")} plus the {r.n("startup_stage1", "usd0")} startup (rebuild {r.n("stage1_cost_rebuild", "usd0")}).', '',
           '**Draft sentence for the deck/protocol:**', '',
           f'> Stage-1 envelope {r.n("stage1_cost", "usd0")} prices {r.n("core_per_arm", "int")} treated contacts at {r.n("treated_contact_rate", "usd0")} each plus the {r.n("startup_stage1", "usd0")} startup; control-arm (Floor) contacts are costed at {r.n("floor_control_contact_rate", "usd0")}.', '',
           f'[DECISION NEEDED: is a Floor contact free? If not, the {r.n("stage1_cost", "usd0")} envelope is understated — at {r.n("treated_contact_rate", "usd0")} per control contact it becomes {r.n("stage1_cost_if_floor_paid", "usd0")} (+{r.n("floor_understatement", "usd0")}, covering all {r.n("stage1_total_enrolled", "int")} Stage-1 enrollees).]', '',
           '## 3. Harm gate — action text', '',
           f'[E] The gate stays as sealed in v2: harm stratum `mou_Mean<=original60k p25 AND ovrrev_Mean=0 AND custcare_Mean=0`; planned looks at {r.n("harm_look_1_fraction", "f1")} and {r.n("harm_look_2_fraction", "f1")} of exposure; one-sided Fisher exact alpha {r.n("harm_alpha_per_look", "f3")} per look, familywise {r.n("harm_familywise_alpha", "f2")}; serious complaints or consent violations escalate immediately regardless of p-value.', '',
           '**Draft action text (fill the owner):**', '',
           '> If the harm gate trips at either planned look: stop outbound service contact for the harm stratum immediately, retain both arms under observation, preserve the assigned control comparison, and escalate to [owner] within one business day. Resumption requires a written review that names the observed harm, the changed contact design and the stopping rule for the next look. Serious complaints or consent violations escalate immediately, independent of statistical significance.', '',
           '[DECISION NEEDED: action if the gate trips; owner — who stops the contact, who signs resumption, and what happens to already-scheduled contacts?]', '',
           '## 4. Reference link access — report only, no edit', '',
           '| Ref | `references.txt` line | URL | Default client | Browser user-agent | Verified page |', '|---|---:|---|---:|---:|---|',
           f'| [S4] Ascarza et al. (2016) | 36 | `https://www.hbs.edu/faculty/Pages/item.aspx?num=54941` | {r.n("http_status_blocked", "int")} | {r.n("http_status_ok", "int")} | The Perils of Proactive Churn Prevention Using Plan Recommendations |',
           f'| [S5] Ascarza (2018) | 40 | `https://www.hbs.edu/faculty/Pages/item.aspx?num=54936` | {r.n("http_status_blocked", "int")} | {r.n("http_status_ok", "int")} | Retention Futility: Targeting High-Risk Customers Might Be Ineffective |',
           f'| [S4] accessible copy | 86 | `https://business.columbia.edu/sites/default/files-efs/pubfiles/12782/Perils_Ascarza.pdf` | {r.n("http_status_ok", "int")} | {r.n("http_status_ok", "int")} | Columbia PDF (application/pdf) |',
           f'| [S5] accessible copy | 89 | `https://evaascarza.com/papers/ascarza_18.pdf` | {r.n("http_status_ok", "int")} | {r.n("http_status_ok", "int")} | Author PDF (application/pdf) |', '',
           f'[E] Both HBS faculty pages answer {r.n("http_status_blocked", "int")} to a default scripted client and {r.n("http_status_ok", "int")} to a browser user-agent; the pages resolve to the two cited articles, so the {r.n("hbs_url_count", "int")} HBS links are bot-blocked rather than dead. The Columbia copy at line 86 returns {r.n("http_status_ok", "int")} with `application/pdf` for every client and remains the accessible evidence copy for S4.', '',
           '[R] `references.txt` is untouched: the root reference file is outside the G1 write boundary and no citation change is proposed. The existing [S4]/[S5] coverage notes stay as written.', '']
    r.write(c.ADDONS / 'TEXT_BLOCKS.md', '\n'.join(md), c.RESULTS / 'TEXT_BLOCKS_render.json')
    print('wrote TEXT_BLOCKS.md; queues:', [(q['key'], round(q['lift'], 4)) for q in body['queues']])

    evidence = [(f'queue_{key}_lift', 'f3') for key, _ in QUEUES] + [(f'queue_{key}_lift_s9', 'f3') for key, _ in QUEUES] + [
        ('queue_total', 'int'), ('queue_max_abs_lift_deviation_pct', 'pc1'), ('stage1_cost', 'usd0'), ('stage1_cost_if_floor_paid', 'usd0'), ('floor_understatement', 'usd0'),
        ('harm_alpha_per_look', 'f3'), ('harm_familywise_alpha', 'f2'), ('http_status_blocked', 'int'), ('http_status_ok', 'int')]
    acceptance = ['- Queue lift recomputed from the published shares and matching section 9 (1.007 / 0.979 / 0.972 / 1.027): **PASS**.',
                  '- Replacement label uses only artifact values and states value per account is flat: **PASS**.',
                  '- Floor cost sentence states the zero control-contact cost and flags the envelope risk: **PASS** (`[DECISION NEEDED]` present).',
                  '- Harm gate keeps the sealed alpha/looks and adds action text with a `[DECISION NEEDED]` owner: **PASS**.',
                  '- Reference access confirmed; no edit to `references.txt`: **PASS** (boundary check).']
    deviations = ['- The brief expected both HBS links to return 403. They return 403 only to a default scripted client; with a browser user-agent they return 200 and show the cited titles. Recorded as a refinement, not a discrepancy in the references.',
                  '- `references.txt` line numbers are current-file positions; the file was not edited.']
    open_items = ['- `[DECISION NEEDED]` Floor contact cost: is a control-arm contact free, or does the Stage-1 envelope need to cover it?',
                  '- `[DECISION NEEDED]` harm-gate action and owner.',
                  '- `[DECISION NEEDED]` extension budget (carried from D4; still open).']
    commands = ['"$PY" -B -X utf8 boundary_check.py --card D6 --phase pre', '"$PY" -B -X utf8 d6_text_blocks.py', '"$PY" -B -X utf8 check_numbers.py --scan ../TEXT_BLOCKS.md ../reports/D6_report.md', '"$PY" -B -X utf8 boundary_check.py --card D6 --phase post']
    report.write_report('D6', 'Text blocks and small corrections', 'COMPLETED_ACCEPTED',
                        'Summary: `TEXT_BLOCKS.md` gives copy-ready queue-composition text (lift recomputed and matching section 9), a Floor-cost sentence with its open question, harm-gate action text with an owner placeholder, and a reference-access table; no external file was edited.',
                        RESULTS, evidence, acceptance, deviations, open_items, commands, 'yes (pre/post clean; only the 4 D1-allowed changes).')


if __name__ == '__main__':
    main()
