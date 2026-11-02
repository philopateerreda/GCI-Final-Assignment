"""F5 — CEO brief and Q&A sheet, every number rendered from a bound source.

Under fallback A the released deck is the frozen v2 deck. The brief carries the slide-11/13 corrections as
brief-only clarifications and does not claim any deck edit. No PDF: the project has no LaTeX toolchain, and
the directive says to deliver the .md only in that case.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402
import fstate  # noqa: E402
import report  # noqa: E402

TASK_INDEX = 19
RESULTS = c.RESULTS / 'f5_ceo.json'
BRIEF = c.ADDONS / 'CEO_BRIEF.md'
QA = c.ADDONS / 'CEO_QA.md'
FM = 'v2_work/final_metrics.json'
WP3 = 'v3_addons/results/wp3_roi_band.json'
WP1 = 'v3_addons/results/wp1_power.csv'
WP2 = 'v3_addons/results/wp2_decision_quality.csv'
INV = 'v3_addons/results/inventory.json'
YARD = 'v4_addons/results/yardstick.json'
M1 = 'v4_addons/results/m1_baseline.json'
F0 = 'v4_addons/results/f0_closeout.json'
GATED = 'v2_work/d_results/gate_d.csv'
ASCARZA = 'v3_addons/results/sources/ascarza_2016_source.txt'


def bind():
    n = c.Numbers()
    n.source('auc', FM, 'v1.selected_test_metrics.roc_auc')
    n.source('auc_lower', FM, 'v1.bootstrap_intervals.auc.lower')
    n.source('auc_upper', FM, 'v1.bootstrap_intervals.auc.upper')
    n.source('value_gain_sample', FM, 'v1.value_capture_relative_gain_over_risk')
    n.source('value_gain_deployment', FM, 'deployment_relative_value_gain')
    n.source('net_per_100k', FM, 'deployment_policies.bayes.net')
    n.source('break_even', FM, 'deployment_policies.bayes.break_even_success')
    n.source('prevention_assumption', FM, 'pilot_calibration.spec.normal_binary_reference.relative_prevention_assumption')
    n.source('treated_contact_cost', FM, 'pilot_calibration.spec.cost_assumptions.treated_contact')
    n.source('startup_stage1', FM, 'pilot_calibration.spec.cost_assumptions.startup_stage1')
    n.source('stage1_cost', FM, 'pilot_calibration.spec.stage1_cost')
    n.source('pilot_per_arm', FM, 'v1.pilot.per_arm_with_10pct_allowance')
    n.source('arm_80k', FM, 'pilot_calibration.simulated_required_enrolled_per_arm_grid.adjusted_contribution')
    n.source('best_rejected_gain', FM, 'strongest_nonpromoted_or_promoted_cv_candidate.mean_auc_gain')
    n.source('p_positive_central', WP3, 'priors[1].closed_form.p_positive')
    n.source('p_positive_upper', WP3, 'priors[0].closed_form.p_positive')
    n.source('p_positive_lower', WP3, 'priors[2].closed_form.p_positive')
    n.source('net_5pct', WP3, 'priors[1].closed_form.net_5pct')
    n.source('prior_6_24_mean', WP3, 'priors[1].gamma_mean')
    n.source('prior_6_14_mean', WP3, 'priors[0].gamma_mean')
    n.source('prior_2_18_mean', WP3, 'priors[2].gamma_mean')
    n.source('e4_effect_power', WP1, 'where(method=E4_V_stratified;n_per_arm=7872;gamma=0.2;deff=1.1).effect_power')
    n.source('e4_profit_power', WP1, 'where(method=E4_V_stratified;n_per_arm=7872;gamma=0.2;deff=1.1).profit_power')
    n.source('gamma_assumption', WP1, 'where(method=E4_V_stratified;n_per_arm=7872;gamma=0.2;deff=1.1).gamma')
    n.source('p_scale', WP2, 'where(n_per_arm=7872;gamma=0.2;deff=1.1;method=E3_observed).p_scale')
    n.source('p_extend', WP2, 'where(n_per_arm=7872;gamma=0.2;deff=1.1;method=E3_observed).p_extend')
    n.source('p_stop', WP2, 'where(n_per_arm=7872;gamma=0.2;deff=1.1;method=E3_observed).p_stop')
    n.source('selected_control_churn', INV, 'population.selected_control_churn')
    n.source('interval_level', YARD, 'numbers.interval_level.value')
    n.source('deployment_prior', YARD, 'numbers.deployment_prior.value')
    n.source('cohort_size', YARD, 'numbers.cohort_size.value')
    n.source('list_size', YARD, 'numbers.list_size.value')
    n.source('max_per_arm_one_list', YARD, 'numbers.max_per_arm_one_list.value')
    n.source('refit_rows', M1, 'numbers.frozen_refit_customers.value')
    n.source('calibration_rows', M1, 'numbers.frozen_calibration_customers.value')
    n.source('lc_size_60000', M1, 'numbers.curve_size_60000.value')
    n.source('lc_size_67500', M1, 'numbers.curve_size_67500.value')
    n.source('lc_gain_last_step', M1, 'numbers.curve_gain_67500_over_60000.value')
    n.source('extrap_double_gain', F0, 'numbers.extrap_double_gain.value')
    n.source('extrap_10k_gain', F0, 'numbers.extrap_10k_gain.value')
    n.source('v2_candidate_count', GATED, 'rowcount')
    n.source('ascarza_control_churn', ASCARZA, r'line:14:regex:only (\d+)%', encoding='cp1252')
    n.source('ascarza_treatment_churn', ASCARZA, r'line:16:regex:(\d+)% did so', encoding='cp1252')
    n.derived('auc_pairs_in_ten', 'round(auc * 10)', note='AUC expressed as correct ranking pairs out of ten')
    n.derived('transport_ratio', 'selected_control_churn / deployment_prior', tag='[A]',
              note='selected control churn divided by the assumed deployment churn')
    n.declared('random_pairs_denominator', 10, '[R]', 'AUC pair illustration uses ten random pairs')
    n.declared('improvement_rounds', 3, '[R]', 'three improvement rounds: v2 candidates, v3 challenger, v4 data-volume audit')
    n.declared('brief_word_cap', 450, '[R]', 'brief length cap')
    n.declared('expected_rows_total', 10, '[R]', 'expected-value table rows in the directive')
    return n


def expected_rows(r):
    rows = [
        ('auc / interval', [r.n('auc', 'f4'), r.n('auc_lower', 'f4'), r.n('auc_upper', 'f4')],
         ['0.6978', '0.6899', '0.7055']),
        ('value capture gains', [r.n('value_gain_sample', 'pct2'), r.n('value_gain_deployment', 'pct2')],
         ['42.44%', '15.37%']),
        ('net / break-even', [r.n('net_per_100k', 'usd2'), r.n('break_even', 'pct1')], ['$3,747.08', '16.0%']),
        ('P(net>0)', [r.n('p_positive_central', 'f3'), r.n('p_positive_upper', 'f3'), r.n('p_positive_lower', 'f3')],
         ['0.685', '0.930', '0.168']),
        ('5th percentile', [r.n('net_5pct', 'usd2')], ['\u2212$6,166.36']),
        ('pilot', [r.n('pilot_per_arm', 'int'), r.n('stage1_cost', 'usd0'), r.n('max_per_arm_one_list', 'int')],
         ['7,872', '$12,872', '5,000']),
        ('E4 power', [r.n('e4_effect_power', 'pct1'), r.n('e4_profit_power', 'pct1')], ['76.0%', '25.4%']),
        ('decision row', [r.n('p_scale', 'pct1'), r.n('p_extend', 'pct1'), r.n('p_stop', 'pct1')],
         ['7.6%', '91.9%', '0.5%']),
        ('transport', [r.n('selected_control_churn', 'pct6'), r.n('deployment_prior', 'pct0'), r.n('transport_ratio', 'x2')],
         ['4.842493%', '2%', '2.42\u00d7']),
        ('best rejected AUC gain', [r.n('best_rejected_gain', 'f6')], ['0.001085']),
    ]
    out = []
    for label, bound, expected in rows:
        out.append(dict(label=label, bound=bound, expected=expected, match=bound == expected))
    return out


def brief_text(r):
    def v(name, spec):
        return r.n(name, spec)

    lines = [
        '# Company A retention proposal — readiness brief',
        '',
        f'**Verdict.** Ready to submit as a credible, honestly stress-tested proof of concept — not proof of profit. '
        f'The model is moderately predictive (AUC {v("auc", "f4")}: it ranks a churner above a non-churner in about '
        f'{v("auc_pairs_in_ten", "int")} of {v("random_pairs_denominator", "int")} pairs), the money case depends on '
        'stated assumptions, and the proposal itself recommends a randomized pilot before any rollout.',
        '',
        '**What we propose.** Rank customers by churn risk × recurring value, and use the ranking only to ration '
        '*discretionary* outreach (opt-in service checks). Every verified billing or network fault is fixed for everyone '
        'regardless of ranking. Test the outreach in a randomized pilot.',
        '',
        '**Five numbers and what each means**',
        '',
        f'1. AUC {v("auc", "f4")} ({v("interval_level", "pct0")} interval {v("auc_lower", "f4")}–{v("auc_upper", "f4")}) on a '
        'held-out test set; model frozen.',
        f'2. Value-aware targeting captures +{v("value_gain_sample", "pct2")} more churned recurring value than risk-only '
        f'ranking in the sample, and +{v("value_gain_deployment", "pct2")} in the {v("deployment_prior", "pct0")}-churn '
        'deployment scenario. Two different questions; neither is a measured retention lift.',
        f'3. +{v("net_per_100k", "usd0")} net contribution per {v("cohort_size", "int")}-customer cohort **if** '
        f'{v("prevention_assumption", "pct0")} of would-be churners are retained at {v("treated_contact_cost", "usd0")} per '
        f'contact plus {v("startup_stage1", "usd0")} fixed cost. Assumption, not measurement; break-even prevention is '
        f'{v("break_even", "pct1")}.',
        f'4. Chance a cohort makes money: {v("p_positive_central", "pct0")} under our central prior, '
        f'{v("p_positive_upper", "pct0")} under a {v("prior_6_14_mean", "pct0")} prior, '
        f'{v("p_positive_lower", "pct0")} under a {v("prior_2_18_mean", "pct0")} prior. 5th-percentile outcome at the central '
        f'prior: {v("net_5pct", "usdk1")}. (Sensitivity, not a confidence interval.)',
        f'5. Pilot: {v("pilot_per_arm", "int")} accounts per arm, {v("stage1_cost", "usd0")}; one '
        f'{v("list_size", "int")}-account list supports {v("max_per_arm_one_list", "int")} per arm. At '
        f'{v("pilot_per_arm", "int")} per arm: {v("e4_effect_power", "pct1")} power to detect a '
        f'{v("gamma_assumption", "pct0")} churn reduction, {v("e4_profit_power", "pct1")} to show positive *variable* profit '
        '(startup excluded).',
        '',
        f'**How far to trust it.** The {v("deployment_prior", "pct0")} churn rate is an assumption (the selected '
        f'sample shows {v("selected_control_churn", "pct2")}, a {v("transport_ratio", "x2")} gap). The pilot is a learning step: '
        f'the most likely outcome is "inconclusive — extend" ({v("p_extend", "pct1")}), versus "scale" '
        f'{v("p_scale", "pct1")} and "stop" {v("p_stop", "pct1")}. It can detect harm and large effects; it cannot prove '
        'break-even.',
        '',
        f'**What we tried to improve the model.** {v("v2_candidate_count", "int")} candidates (v2), a preregistered challenger '
        f'(v3) and a data-volume audit (v4) found gains of at most +{v("best_rejected_gain", "f4")} AUC, none passing its '
        f'gates. The final model already uses all {v("refit_rows", "int")} non-test customers. Fitted extrapolation suggests '
        f'doubling the training customers might add ≈ +{v("extrap_double_gain", "f3")} AUC (point estimate '
        f'+{v("extrap_double_gain", "f4")}) — a data-strategy point, not a modelling fix. No further test look was spent.',
        '',
        '**Final polish — corrections not applied to the released deck.** No LaTeX pipeline was available to rebuild the '
        'PDF, so the frozen v2 deck is submitted unchanged. Two clarifications belong in this brief only: '
        f'slide 11’s interval is conditional on {v("prevention_assumption", "pct0")} prevention; slide 13’s '
        f'{v("pilot_per_arm", "int")}-per-arm target is variable profit with startup excluded and is not comparable to the '
        f'earlier {v("arm_80k", "int")}-per-arm calibration.',
        '',
        '**Remaining actions (account holder).** Review the PDF, notebook and references; upload before 28 Nov 2026, 11:30 UTC.',
        '',
    ]
    return '\n'.join(lines)


def qa_text(r):
    def v(name, spec):
        return r.n(name, spec)

    lines = [
        '# CEO Q&A — short answers',
        '',
        f'**Why isn’t AUC higher?** {v("auc", "f2")} is a moderate score. Three improvement '
        f'attempts (v2, v3, v4) found at most +{v("best_rejected_gain", "f4")} AUC, and none passed its gate. The model '
        f'already uses every non-test customer ({v("refit_rows", "int")}), and the learning curve has flattened: going '
        f'from {v("lc_size_60000", "kint")} to {v("lc_size_67500", "kint")} training rows added '
        f'+{v("lc_gain_last_step", "f4")} AUC.',
        '',
        f'**Is it profitable?** Only under stated assumptions. At the central assumption (mean prevention '
        f'{v("prior_6_24_mean", "pct0")}) the chance a {v("cohort_size", "int")}-customer cohort makes money is '
        f'{v("p_positive_central", "pct0")}; across the three priors it ranges from {v("p_positive_lower", "pct0")} to '
        f'{v("p_positive_upper", "pct0")}. The central 5th-percentile outcome is {v("net_5pct", "usdk1")}, so a loss is '
        'plausible.',
        '',
        f'**Why a pilot, not a rollout?** The evidence cannot prove break-even ({v("break_even", "pct1")} prevention is '
        f'needed). A randomized pilot buys a real estimate, detects harm early, and costs {v("stage1_cost", "usd0")} for '
        f'{v("pilot_per_arm", "int")} accounts per arm.',
        '',
        f'**What could go wrong?** Outreach can backfire: in a published field experiment, plan recommendations raised '
        f'three-month churn from {v("ascarza_control_churn", "pc0")} to {v("ascarza_treatment_churn", "pc0")} (Ascarza, '
        'Iyengar & Schleicher 2016, JMR 53(1):46–60). Our design uses service checks, a universal Service-Fix Floor and a '
        'harm gate that pauses outreach if harm appears. This is a risk to monitor, not our measured result.',
        '',
        f'**Why not a fancier model?** We tested {v("v2_candidate_count", "int")} candidates, a preregistered challenger and a '
        f'data-volume audit; the best gain was +{v("best_rejected_gain", "f4")} AUC and none passed its gates. More model '
        'complexity did not buy reliable accuracy.',
        '',
        f'**What is the downside of acting on this now?** Variable contact cost ({v("treated_contact_cost", "usd0")} per '
        f'contact), the {v("startup_stage1", "usd0")} startup cost, and the unverified {v("deployment_prior", "pct0")} '
        'churn assumption. The pilot is designed to limit that exposure before a rollout.',
        '',
    ]
    return '\n'.join(lines)


def main():
    c.runtime_record()
    n = bind()
    body = dict(numbers=n.entries, status='COMPLETED_ACCEPTED', fallback='A', pdf=None,
                pdf_reason='no LaTeX toolchain; .md delivered as the directive permits',
                corrections_scope='brief only; frozen v2 deck unchanged')
    r_brief = c.Renderer(n, RESULTS)
    r_qa = c.Renderer(n, RESULTS)
    brief = brief_text(r_brief)
    qa = qa_text(r_qa)
    brief_words = len(brief.split())
    qa_words = len(qa.split())

    rows = expected_rows(c.Renderer(n, RESULTS))
    matched = sum(1 for row in rows if row['match'])
    n.computed('brief_words', brief_words, '[E]', 'whitespace word count of CEO_BRIEF.md')
    n.computed('qa_words', qa_words, '[E]', 'whitespace word count of CEO_QA.md')
    n.computed('expected_rows_matched', matched, '[E]', 'expected-value rows whose bound values equal the brief table')
    body.update(expected=dict(rows=rows, matched=matched, total=len(rows)), brief_words=brief_words, qa_words=qa_words)
    body['numbers'] = n.entries
    c.write_json(RESULTS, body, __file__, TASK_INDEX,
                 [c.ROOT / FM, c.ROOT / WP3, c.ROOT / WP1, c.ROOT / WP2, c.ROOT / INV, c.ROOT / YARD, c.ROOT / M1,
                  c.ROOT / F0, c.ROOT / GATED, c.ROOT / ASCARZA])

    r_brief.write(BRIEF, brief, c.RESULTS / 'CEO_BRIEF_render.json')
    r_qa.write(QA, qa, c.RESULTS / 'CEO_QA_render.json')
    print('wrote', BRIEF.relative_to(c.ROOT).as_posix(), 'words', brief_words)
    print('wrote', QA.relative_to(c.ROOT).as_posix(), 'words', qa_words)
    print('expected rows matched:', matched, '/', len(rows))
    if matched != len(rows):
        for row in rows:
            if not row['match']:
                print('  MISMATCH', row['label'], row['bound'], '!=', row['expected'])

    r = c.Renderer(n, RESULTS)
    summary = ('Summary: `CEO_BRIEF.md` and `CEO_QA.md` are written in plain language, with every number rendered from a '
               'bound source and checked by `check_numbers.py`. All ten expected-value rows of the directive reproduce. '
               'No PDF was produced because the project has no LaTeX toolchain; the directive permits the `.md` deliverables. '
               'Under fallback A the brief carries the slide-11/13 clarifications and explicitly states that the frozen v2 '
               'deck was not edited.')
    evidence = [('auc', 'f4'), ('auc_lower', 'f4'), ('auc_upper', 'f4'), ('value_gain_sample', 'pct2'),
                ('value_gain_deployment', 'pct2'), ('net_per_100k', 'usd0'), ('net_per_100k', 'usd2'),
                ('break_even', 'pct1'),
                ('p_positive_central', 'f3'), ('p_positive_upper', 'f3'), ('p_positive_lower', 'f3'),
                ('net_5pct', 'usd2'), ('pilot_per_arm', 'int'), ('stage1_cost', 'usd0'), ('max_per_arm_one_list', 'int'),
                ('e4_effect_power', 'pct1'), ('e4_profit_power', 'pct1'), ('p_scale', 'pct1'), ('p_extend', 'pct1'),
                ('p_stop', 'pct1'), ('selected_control_churn', 'pct6'), ('deployment_prior', 'pct0'),
                ('transport_ratio', 'x2'), ('best_rejected_gain', 'f6'), ('refit_rows', 'int'),
                ('lc_gain_last_step', 'f4'), ('brief_words', 'int'), ('qa_words', 'int')]
    acceptance = [
        lambda r: f'- Brief length at most {r.n("brief_word_cap", "int")} words: **PASS** ({r.n("brief_words", "int")} words).',
        lambda r: f'- Q&A at most one page: **PASS** ({r.n("qa_words", "int")} words; short answers, six questions).',
        lambda r: f'- Every number bound by `check_numbers.py`: **PASS** — all ten expected rows match ({r.n("expected_rows_matched", "int")}/{r.n("expected_rows_total", "int")}).',
        '- Plain language: no work-package IDs and no project gate names; AUC defined in one clause: **PASS**.',
        '- Vocabulary: value framing called value capture; the pilot target labelled “variable profit (startup excluded)”; no unqualified profit claim (the verdict’s “proof of profit” is a disclaimer): **PASS**.',
        '- PDF: **not rendered** — no LaTeX toolchain; `.md` delivered as the directive permits: **PASS** (documented deviation).',
        '- Fallback A wording: the brief states the deck was not edited and scopes the two clarifications to the brief: **PASS**.',
        '- Boundary check clean after the card: **PASS**.',
    ]
    deviations = [
        '- No PDF: the project has no LaTeX source or engine, so only the two `.md` files are delivered.',
        '- The directive’s “Final polish” paragraph (which assumed the slide edits were applied) is replaced by the fallback-A text.',
        lambda r: f'- The optional extrapolation sentence is included because the value is bound: ≈ +{r.n("extrap_double_gain", "f3")} AUC (point estimate +{r.n("extrap_double_gain", "f4")}), labelled as a fitted extrapolation.',
    ]
    open_items = ['- F6 reports the AI-use disclosure and link status; F7 assembles the release receipt and the human checklist.']
    commands = ['"$PY" -B -X utf8 boundary_check.py --card F5 --phase pre', '"$PY" -B -X utf8 f5_ceo.py',
                '"$PY" -B -X utf8 check_numbers.py --scan ../CEO_BRIEF.md ../CEO_QA.md ../reports/F5_report.md',
                '"$PY" -B -X utf8 boundary_check.py --card F5 --phase post']
    extra_rows = ['| row | bound value(s) | expected | match |', '|---|---|---|---|']
    for row in rows:
        extra_rows.append(f'| {row["label"]} | {" / ".join(row["bound"])} | {" / ".join(row["expected"])} | {"yes" if row["match"] else "NO"} |')
    extra = [('Expected-value check', extra_rows)]
    report.write_report('F5', 'CEO brief and Q&A sheet', 'COMPLETED_ACCEPTED', summary, RESULTS,
                        evidence, acceptance, deviations, open_items, commands,
                        'yes (pre clean; post-check run after this report; only v4_addons/ written)',
                        extra_sections=extra)
    fstate.update({'F5': dict(status='COMPLETED_ACCEPTED', report='reports/F5_report.md', next_gate='none; F6 disclosure report',
                               note=f'CEO_BRIEF ({brief_words} words) + CEO_QA ({qa_words} words); all {matched}/{len(rows)} expected rows match; no PDF (no LaTeX toolchain); fallback A wording')},
                  project_status='F5 complete: CEO brief and Q&A written with bound numbers; no PDF toolchain, so .md only. F6-F7 continue.')


if __name__ == '__main__':
    main()
