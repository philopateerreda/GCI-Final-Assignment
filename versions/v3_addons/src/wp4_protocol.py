from common import ADDONS, ROOT, file_info, verify_runtime, write_json
from reporting import write_report

import json


def main():
    verify_runtime()
    metrics = json.loads((ROOT/'v2_work/final_metrics.json').read_text(encoding='utf-8'))
    source = metrics['pilot_test']
    queues = source['queues']
    assert [row['raw_count'] for row in queues] == [582,266,791,866]
    gates = source['spec']['decision_gates']
    assert gates['one_sided_alpha_per_harm_look'] == .005
    assert gates['harm_looks'] == [.5,1.]
    paper = ADDONS/'results/sources/ascarza_2016_source.txt'
    text = paper.read_text(encoding='utf-8',errors='replace')
    assert '6%' in text and '10%' in text and 'three months' in text
    table=['| Queue hypothesis [R] | Frozen raw rows [E] | Selected at-risk value share [E/A] |',
           '|---|---:|---:|']
    names=('Billing check','Network check','Handset check','Digital-only residual')
    table += [f'| {name} | {row["raw_count"]:,} | {row["share_at_risk_value"]:.1%} |' for name,row in zip(names,queues)]
    lines=['# Protocol addendum — supporting proposal only',
           '', '[R] **ITT estimand.** Randomize linked-household clusters after operational linkage is validated; analyze every enrolled account by assignment. Primary outcome: realized incremental contribution net of all contact, incentive, remediation and implementation costs. Secondary outcomes: days 31–60 churn, V-weighted churn, opt-outs and complaints. Existing data contain no household linkage or treatment labels.',
           '', '[R] **Service-Fix Floor.** Fix every verified billing/network defect regardless of bill, rank or randomized arm. Ranking rations discretionary proactive outreach only. Both arms receive the Floor, so the estimand is discretionary outreach on top of the Floor—not the effect of the Floor. Log Floor-triggered control contacts and associated costs; do not exclude those controls.',
           '', '[E/R] **Unchanged harm gate.** Preregister low usage (`mou_Mean` at/below original-training p25), zero overage revenue and zero care; missing values are not zero. At 50% and 100% information, stop for positive treatment-minus-control churn with one-sided Fisher p≤0.005 at either look; familywise bound ≤0.01 for this stratum. Serious complaints or consent violations escalate immediately regardless of significance. Household-clustered live safety design still requires validation.',
           '', '[R] Small-stratum monitoring is a safety tripwire, not powered subgroup inference. [E] Ascarza, Iyengar and Schleicher (2016), accessible full-text abstract and experiment sections, report 6% control versus 10% treated churn over three months after cost-minimizing plan recommendations. [R] The sleeping-dog hypothesis is preregistered, not verified for Company A or all service contact.',
           '', '## Assumption table for the pitch — not estimable in Stage 1',
           '[E] Counts/shares below are quotations from frozen `final_metrics.json → pilot_test.queues`, not new test-row computation. [A] Monetary interpretation, costs and prevention remain assumptions; no queue-specific prevention effects are findings.']+table+[
           '', '[R] Routing flags are hypotheses, not verified causes. The digital residual includes all remaining cases, not only proven low usage. No queue allocation or causal effect is changed.',
           '', '[E] Sources: frozen handoff §9 and `pilot_test.spec.decision_gates`; existing Ascarza (2016) reference S4, https://business.columbia.edu/sites/default/files-efs/pubfiles/12782/Perils_Ascarza.pdf. HBS item access returned 403; the accessible paper—not that inaccessible page—supports the quotation.']
    target=ADDONS/'protocol_addendum.md'
    target.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    words=len(' '.join(lines).split())
    assert words<=550
    inputs=[ROOT/'v2_work/final_metrics.json',ROOT/'FINAL_ASSESSMENT_HANDOFF.md',ROOT/'references.txt',paper]
    body=dict(status='DONE',new_numerical_estimates=0,quoted_queue_rows=queues,
              quoted_harm_gate=gates,word_count=words,artifact=file_info(target),
              source_scope=dict(ascarza='Accessible full-text abstract and field experiment sections read; 6%/10% over three months, plan recommendations.',
                                hbs='403 Forbidden, not described as read'),
              tags=dict(estimand='[R] proposed ITT by linked household; no linkage observed',queue_table='[E] frozen quotation, [A] economics; no gamma_q findings'))
    write_json('results/wp4_protocol.json',body,__file__,4,inputs,dict(quoted_queues=len(queues),new_estimates=0))
    write_report(4,'ITT, Floor contamination and harm gate','DONE',inputs,
                 ['- [R] Linked-household ITT is a prospective design requirement; current linkage and treatment outcomes do not exist.',
                  '- [A] Queue economics are pitch assumptions, not estimable prevention rates.'],
                 '[E] Quoted the frozen gate and queue scalars, checked them against the handoff, and read the accessible Ascarza paper abstract/experiment sections. Wrote a concise supporting addendum without changing the protocol or any numerical estimate.',
                 table+[f'[E] Addendum contains {words} words; no new numerical estimates.'],
                 ['- [E] PASS: exact queue counts 582/266/791/866 and rounded shares 23.4/10.4/30.7/35.5%.',
                  '- [E] PASS: unchanged .005 per-look harm threshold and .5/1.0 planned looks.',
                  '- [E] PASS: zero new estimates; concise ≤550-word one-page content target.'],
                 ['[E] HBS access was blocked; the existing accessible full-paper copy supports the intervention-specific quote.'],
                 '[R] A proposed ITT estimand, logged Floor contamination, and a preregistered safety tripwire.',
                 '[R] Company A causal effects, queue-specific prevention findings, powered subgroup inference or generalized service-contact harm.')
    print(f'[E] WP4 DONE: {words} words; frozen protocol unchanged.',flush=True)


if __name__ == '__main__':
    main()
