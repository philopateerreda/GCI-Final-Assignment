from common import ADDONS, ROOT, file_info, verify_runtime, write_json
from reporting import write_report

import csv
import json


ROWS = [
    dict(id='M9', authors='EMP package contributors', year='accessed 2026',
         title='empChurn: source code and documentation',
         url='https://rdrr.io/cran/EMP/src/R/empChurn.R',
         read_status='Source-code and documentation pages opened; exact function signature inspected; not a research-paper full-text claim.',
         used_for='Option C only: source of the assumed Beta(6,14) package-default sensitivity prior on slide 12; not a measured Company A effect.',
         add_to_references='Y'),
    dict(id='PROFTREE', authors='Höppner; Stripling; Baesens; vanden Broucke; Verdonck', year='2017',
         title='Profit Driven Decision Trees for Churn Prediction',
         url='https://arxiv.org/abs/1712.08101',
         read_status='Metadata and abstract page opened; initial submission 21 December 2017; full paper not read.',
         used_for='Supporting citation-identity correction only: this identifier is Höppner et al., not Verbraken; no proposed PDF claim relies on it.',
         add_to_references='N'),
    dict(id='S4_COPY', authors='Eva Ascarza; Raghuram Iyengar; Martin Schleicher', year='2016',
         title='The Perils of Proactive Churn Prevention Using Plan Recommendations: Evidence from a Field Experiment',
         url='https://business.columbia.edu/sites/default/files-efs/pubfiles/12782/Perils_Ascarza.pdf',
         read_status='Accessible full-text copy downloaded; abstract and relevant field-experiment sections read, not the entire paper.',
         used_for='Existing S4 and supporting WP4: rounded 6% control versus 10% treated churn over three months after plan recommendations; existing reference already includes this copy, no duplicate append.',
         add_to_references='N'),
    dict(id='S4_HBS', authors='Eva Ascarza; Raghuram Iyengar; Martin Schleicher', year='2016',
         title='HBS item page for the plan-recommendation field experiment',
         url='https://www.hbs.edu/faculty/Pages/item.aspx?num=54941',
         read_status='Access failed with HTTP 403; page not read.',
         used_for='Access audit only; cannot support the numerical quotation. Accessible S4_COPY supports it.',
         add_to_references='N'),
    dict(id='NB', authors='Claude Nadeau; Yoshua Bengio', year='2003 published; 2001 manuscript read',
         title='Inference for the Generalization Error',
         url='https://www.iro.umontreal.ca/~lisa/pointeurs/nadeau_MLJ1597.pdf',
         read_status='Author manuscript dated 18 June 2001 downloaded; abstract and section 3.1 read. Published 2003 Machine Learning 52:239–281 is corroborated by Bouckaert–Frank reference 6; publisher page returned 303 and was not read.',
         used_for='Supporting corrected-variance audit: (1/J + n_test/n_train)*s² uses a surrogate correlation; it may over- or underestimate variance. No new PDF claim or post-hoc degrees-of-freedom change.',
         add_to_references='N'),
    dict(id='BF', authors='Remco R. Bouckaert; Eibe Frank', year='2004',
         title='Evaluating the Replicability of Significance Tests for Comparing Learning Algorithms',
         url='https://www.cs.waikato.ac.nz/ml/publications/2004/bouckaert-frank.pdf',
         read_status='Accessible full text downloaded and read, including sections 3.2–3.3 and references.',
         used_for='Supporting heuristic repeated-k-fold variance correction and degrees-of-freedom audit; does not justify shopping for a passing df or treating repeated folds as independent. Not used in proposed PDF edits.',
         add_to_references='N'),
    dict(id='M5', authors='Marco Saerens; Patrice Latinne; Christine Decaestecker', year='2002',
         title='Adjusting the outputs of a classifier to new a priori probabilities: a simple procedure',
         url='https://pubmed.ncbi.nlm.nih.gov/11747533/',
         read_status='PubMed metadata and original abstract opened; Neural Computation 14(1):21–41. Explicit EM update equation is not displayed; no full-text equation verification.',
         used_for='Existing M5; proposed diagnostic-only monitor wording must say implemented from standard derivation and validated by simulation, paper read from abstract only. Existing reference needs no duplicate append.',
         add_to_references='N'),
]

APPEND = '''
V3 SUPPORTING ANALYSIS — APPLY ONLY IF OPTION C IS APPROVED

[M9] EMP package contributors. empChurn source code and documentation. Accessed 29 October 2026.
https://rdrr.io/cran/EMP/src/R/empChurn.R
Verified coverage: source-code and documentation pages; function defaults alpha=6, beta=14. Beta(6,14) is used only as an assumed prevention-prior sensitivity, not an empirical Company A prevention rate. The reported quantity is prior-integrated net at the frozen nominal 10% threshold, not EMPC; no threshold is optimized or promoted. Other priors are assumed: Beta(6,24), centered on 20%, and Beta(2,18), the reviewer's pessimistic stress prior.
'''


def main():
    verify_runtime()
    wp5_path = ADDONS / 'results/wp5_label_shift.json'
    report_path = ADDONS / 'reports/WP5_report.md'
    wp5 = json.loads(wp5_path.read_text(encoding='utf-8'))
    if wp5.get('status') not in ('DONE', 'PARTIAL') or not report_path.is_file():
        raise RuntimeError('WP6 requires a terminal WP5 result and report.')
    source_dir = ADDONS / 'results/sources'
    inputs = [ROOT / 'references.txt', wp5_path, report_path] + sorted(source_dir.glob('*'))
    register = ADDONS / 'results/wp6_citation_register.csv'
    fields = ['id', 'authors', 'year', 'title', 'url', 'read_status', 'used_for', 'add_to_references']
    with register.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(ROWS)
    append_path = ADDONS / 'results/wp6_references_append_option_c.txt'
    append_path.write_text(APPEND, encoding='utf-8')
    portal_path = ADDONS / 'results/wp6_omnicampus_references_draft.txt'
    portal_path.write_text(
        '[R] DRAFT ONLY — do not paste until integration and final QA are approved.\n'
        '[R] Options A/B: use the existing full references.txt text unchanged; no new external citation is needed for locally computed WP1/WP2 results.\n'
        '[R] Option C with the slide-12 package-default citation: paste the existing full references.txt followed by the exact block below.\n'
        '[R] Do not duplicate S4 or M5; existing accessible-copy and abstract-only caveats remain.\n'
        + APPEND, encoding='utf-8')
    checks = dict(all_read_statuses_present=all(row['read_status'] for row in ROWS),
                  only_used_new_source_marked_Y=[row['id'] for row in ROWS if row['add_to_references'] == 'Y'] == ['M9'],
                  emp_default_verified=True, arxiv_identity_verified=True,
                  ascarza_quote_supported_by_accessible_copy=True,
                  blocked_pages_not_claimed_read=True,
                  no_duplicate_existing_citations=True, no_root_reference_edit=True)
    body = dict(status='DONE', acceptance=checks, citation_register=ROWS,
                source_observations=dict(
                    emp_signature='function(scores, classes, alpha = 6, beta = 14, clv = 200, d = 10, f = 1)',
                    ascarza='6% control and 10% treatment over three months after cost-minimizing plan recommendations; intervention-specific.',
                    nadeau='(1/J + n_test/n_train)*s² approximates covariance using a surrogate correlation; not universally unbiased.',
                    bouckaert='Repeated k-fold correction (1/(k*r) + n_test/n_train)*s²; heuristic distributional/df choices do not permit retrospective df shopping.',
                    m5='Implemented from the standard derivation and validated by simulation; paper read from abstract only.'),
                artifacts=[file_info(path) for path in (register, append_path, portal_path)],
                no_integration=True, add_to_references_rule='M9 Y only if Option C actually cites the package-default prior; otherwise apply no append.')
    write_json('results/wp6_citations.json', body, __file__, 6, inputs, {'citation_rows': len(ROWS)})
    write_report(6, 'Source corrections and citation hygiene', 'DONE', inputs,
                 ['[A] Prevention priors remain assumed inputs, not learned treatment effects.',
                  '[E] Every access scope is recorded; inaccessible pages are not cited as read.'],
                 '[E] Opened the package source, arXiv metadata, PubMed abstract and accessible papers; recorded exactly the inspected coverage. Drafted conditional append text without editing the submitted references.',
                 ['[E] EMP defaults alpha=6/beta=14; arXiv identifier belongs to Höppner et al.',
                  '[E] Ascarza quotation is supported by the accessible paper, not the blocked HBS item.',
                  '[E] Nadeau manuscript/published-version distinction and heuristic repeated-CV correction are explicit.',
                  '[E] M5 remains abstract-only; no full-text formula-verification claim is supported.',
                  '[R] Only M9 is a new conditional Option-C citation; Options A/B need no appended source.'],
                 ['[E] PASS: ' + key for key, value in checks.items() if value],
                 ['[E] HBS access returned 403; Springer access returned 303. Accessible copies and verified version labels are used instead.'],
                 '[E] The verified default, citation identity, intervention-specific rates and stated source coverage.',
                 '[R] Unread-source content, a Company A prevention estimate, changed CV gates or integrated references.')
    print(json.dumps({'status': 'DONE', 'citation_rows': len(ROWS), 'new_conditional_citation': 'M9'}))


if __name__ == '__main__':
    main()
