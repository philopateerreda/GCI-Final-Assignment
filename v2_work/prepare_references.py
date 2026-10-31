import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'v2_work'


def prepare():
    evidence = json.loads((WORK / 'literature_verification.json').read_text(encoding='utf-8'))
    sources = {row['id']: row for row in evidence['sources']}
    text = (ROOT / 'v1_frozen/references.txt').read_text(encoding='utf-8')
    text = text.replace('[S1] T-Mobile US, Inc. (11 February 2026). 2025 Form 10-K, year ended 31 December 2025.',
                        '[S1] T-Mobile US, Inc. 2025 Annual Report, including Form 10-K for the year ended 31 December 2025 (published 2026).')
    additions = []
    for key in ('TMobile2025', 'ATT2025', 'Ascarza2016', 'Ascarza2018'):
        source = sources[key]
        identity = source.get('existing_reference_id', {'Ascarza2016': 'S4', 'Ascarza2018': 'S5'}.get(key))
        additions.append(f"[{identity}] Accessible evidence copy: {source['accessed_url']}\nCoverage: {source['verification_coverage']}. {source['scope_caveat']}")
    for identity, key in (('M5', 'Saerens2002'), ('M6', 'Elkan2001'), ('M7', 'CUPED2013'), ('M8', 'Neslin2006')):
        source = sources[key]
        metadata = source['bibliographic_metadata']
        additions.append(f"[{identity}] {', '.join(metadata['authors'])} ({metadata['year']}). {metadata['title']}. {metadata['venue']}, {metadata['pages']}.\n{source['accessed_url']}\nVerified coverage: {source['verification_coverage']}. {source['permitted_reference_use']} {source['scope_caveat']}")
    additions.append('ENHANCEMENT DISCIPLINE AND INTERPRETATION\n\nThe 15,000-customer test partition was previously evaluated for v1. Enhancement model, feature, calibrator and budget decisions use only the original 75,000 train/validation rows or the separate 10,000 calibration-policy rows. A frozen specification precedes the final descriptive test batch. Reproducibility replay is not a second model-selection search. Prior reuse and pointwise exploratory confidence intervals limit confirmatory interpretation.\n\nSample benchmark: sample-calibrated p_s times recurring value, 1,500 of 15,000 unweighted rows. Deployment scenario: prior-shifted p_d times recurring value with outcome-stratified evaluation weights; its calibration-fitted 10% nominal budget can have a different achieved test mass and raw customer count. These are distinct regimes. A non-binding marginal variable-profit gate does not prove overconfidence.\n\nModel headroom uses paired 2 x 5 repeated non-test CV with a conservative corrected-t interval, variance multiplied by 1/10 + mean(held-out/train), with four degrees of freedom. These are pointwise, exploratory intervals, not simultaneous selection-adjusted guarantees. Unsuccessful experiments do not prove an information ceiling.\n\nThe supplied CSVs contain no _Range fields; the dictionary does not establish the _Mean window length. avg3 and avg6 are used only with their verified three-/six-month definitions. Income is an ordinal code 1-9, not currency. Excluded-attribute recoverability is audited on non-test operational features; exclusion is not a fairness certificate. asl_flag and area are quarantined diagnostic-ceiling variables, never deployable decision features.\n\nMandatory Service-Fix Floor: fix every verified network fault or billing error irrespective of bill size or discretionary list selection. Value-aware ranking rations only scarce proactive discretionary outreach. Routing and the low-usage/zero-overage/zero-care monitoring stratum are operational hypotheses, not treatment-effect findings.\n\nThe staged pilot logs eligibility, inclusion and treatment propensities; adds sampled risk-only drops and below-cutoff learning accounts without double-counting value-aware additions. Monte Carlo contribution and ANCOVA/CUPED-style power are cross-sectional simulation proxies, not verified longitudinal variance reduction. Re-estimate live baseline, pre/post billing covariance, household clustering, measurement costs, intervention effects and sequential thresholds before launch. The approximately $13k core contact/startup envelope is a churn-learning experiment, not profit-powered rollout proof; Stage 2 learning allocations are not powered policy comparisons. Enrollment must span enough unique linked accounts across a larger portfolio or successive cohorts, rather than treating one 100,000-account financial scenario as sufficient pilot capacity.')
    target = WORK / 'references_v2.txt'
    target.write_text(text + '\n\nENHANCEMENT LITERATURE AND VERIFIED EVIDENCE COPIES\n\n' + '\n\n'.join(additions) + '\n', encoding='utf-8')
    return target


if __name__ == '__main__':
    print(prepare())
