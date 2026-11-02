from common import ADDONS, ROOT, digest, file_info, outside_snapshot, verify_runtime, write_json
from reporting import write_report

import csv
import json
import posixpath
import zipfile
import xml.etree.ElementTree as ET


NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}


def deck_text():
    text_tag = '{' + NS['a'] + '}t'
    break_tag = '{' + NS['a'] + '}br'
    with zipfile.ZipFile(ROOT / 'philopateer.pptx') as archive:
        relations = {item.attrib['Id']: item.attrib['Target']
                     for item in ET.fromstring(archive.read('ppt/_rels/presentation.xml.rels'))}
        root = ET.fromstring(archive.read('ppt/presentation.xml'))
        paths = [posixpath.normpath(posixpath.join('ppt', relations[item.attrib['{' + NS['r'] + '}id']]))
                 for item in root.findall('.//p:sldId', NS)]
        slides = []
        for index, path in enumerate(paths, 1):
            elements = []
            for shape in ET.fromstring(archive.read(path)).findall('.//p:sp', NS):
                paragraphs = [''.join('\n' if node.tag == break_tag else node.text or ''
                                      for node in paragraph.iter() if node.tag in (text_tag, break_tag))
                              for paragraph in shape.findall('.//a:p', NS)]
                text = '\n'.join(paragraphs)
                if text:
                    elements.append(text)
            slides.append(dict(slide_number=index, part=path, text_elements=elements))
    assert len(slides) == 15
    return slides


def main():
    verify_runtime()
    names = ('inventory', 'wp1_power', 'wp2_evsi', 'wp3_roi_band', 'wp4_protocol', 'wp5_label_shift', 'wp6_citations')
    paths = [ADDONS / f'results/{name}.json' for name in names]
    results = [json.loads(path.read_text(encoding='utf-8')) for path in paths]
    for index, item in enumerate(results):
        allowed = ('DONE', 'PARTIAL', 'DONE_WITH_ORACLE_CAVEAT') if index == 1 else ('DONE', 'PARTIAL')
        assert item.get('status') in allowed
        report = (ADDONS / f'reports/WP{index}_report.md').read_text(encoding='utf-8')
        report_status = 'DONE' if item['status'] == 'DONE_WITH_ORACLE_CAVEAT' else item['status']
        assert any(line.startswith('Status: ' + report_status) for line in report.splitlines())
    validation_path = ADDONS / 'results/final_new_code_tests.json'
    validation = json.loads(validation_path.read_text(encoding='utf-8'))
    assert validation['passed'] is True
    before_path = ADDONS / 'results/write_boundary_before.json'
    before = json.loads(before_path.read_text(encoding='utf-8'))['files']
    after = outside_snapshot()
    difference = dict(files_before=len(before), files_after=len(after),
                      added_outside=sorted(after.keys() - before.keys()),
                      removed_outside=sorted(before.keys() - after.keys()),
                      changed_outside=sorted(key for key in before.keys() & after.keys() if before[key] != after[key]))
    difference['passed'] = before == after
    assert difference['passed'], 'STOP-1: outside-sandbox files changed'
    slides = deck_text()
    ledger_path = ROOT / 'analysis_outputs/claims_ledger.csv'
    with ledger_path.open(encoding='utf-8-sig', newline='') as stream:
        ledger = list(csv.DictReader(stream))
    assert len(ledger) == 278
    ledger_evidence = [dict(claim_id=f'C{index:04d}', csv_line=index + 1, **row)
                       for index, row in enumerate(ledger, 1)]
    wp5_status = results[5]['status']
    mapping = {'13': [row for row in ledger_evidence if row['slide_number'] == '13'],
               '12': [row for row in ledger_evidence if row['slide_number'] == '12'],
               '5': [row for row in ledger_evidence if row['slide_number'] == '5'],
               '15': [row for row in ledger_evidence if row['slide_number'] == '15']}
    evidence_path = ADDONS / 'results/wp7_readonly_deck_ledger.json'
    inputs = paths + [ROOT / 'philopateer.pptx', ROOT / 'philopateer.pdf', ROOT / 'philopateer.ipynb',
                      ROOT / 'references.txt', ledger_path, before_path, validation_path,
                      ADDONS / 'results/wp6_references_append_option_c.txt']
    write_json('results/wp7_readonly_deck_ledger.json',
               dict(status='DONE', slides=slides, claims=ledger_evidence, candidate_claims=mapping,
                    office_read_context='Read-only: revision 0, dirty false, 15 slides. Slides 12/13/15 inspected with read_slide; remaining text read through actual ZIP relationships. No Office save/edit/export.',
                    page_count=15, claim_count=278), __file__, 7, inputs, {'slides': 15, 'claims': 278})
    proposal_path = ADDONS / 'INTEGRATION_PROPOSAL.md'
    proposal_path.write_text(proposal(slides, ledger_evidence, wp5_status), encoding='utf-8')
    files = [path.relative_to(ADDONS).as_posix() for path in sorted(ADDONS.rglob('*')) if path.is_file()]
    intended = ['HANDBACK.md', 'reports/WP7_report.md', 'results/wp7_final_verification.json', 'results/wp7_files_created.csv']
    files = sorted(set(files + intended))
    manifest = ADDONS / 'results/wp7_files_created.csv'
    with manifest.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['relative_path', 'role'])
        for name in files:
            role = 'historical/scratch' if name.startswith(('reports/STOP_', 'results/stop_', 'src/stop_', 'src/__validation_', 'figures/runtime_')) else 'supporting analysis'
            writer.writerow([name, role])
    statuses = {f'WP{i}': result['status'] for i, result in enumerate(results)}
    statuses.update(WP7='DONE', WP8='OFF')
    handback_path = ADDONS / 'HANDBACK.md'
    handback_path.write_text(handback(statuses, difference, len(files), results[5]), encoding='utf-8')
    write_report(7, 'Integration proposal and human decision gate', 'DONE', inputs + [evidence_path],
                 ['[A] All financial, power and monitoring conclusions retain the assumptions in their individual reports.',
                  '[E] Current deck/ledger read only: 15 slides and 278 data rows.'],
                 '[E] Read the actual presentation order and native text; matched candidate replacements to deterministic ledger row aliases and source keys. Prepared options, exact replacements, handback and file manifest. Compared every outside-sandbox file to the original 4,246-file baseline; no integration or submission.',
                 ['[E] WP0–WP6 terminal reports are present; scientific failures remain explicit.',
                  '[E] Exactly 15 current slides; replacements only.',
                  '[E] All outside files unchanged; frozen delivery hashes retained.',
                  '[R] Recommend B first; C only after additional source/monitor/layout review. Human approval remains mandatory.'],
                 ['[E] PASS: 4,246-file directory diff has no additions, removals or changes.',
                  '[E] PASS: current 15-slide order and 278-row ledger verified.',
                  '[E] PASS: proposal and handback written only inside v3_addons.'],
                 ['[E] No integration QA was run because no integration is authorized.',
                  '[R] Future PDF creation must follow the user\'s LaTeX-only instruction, not the brief\'s Office-PDF export step; a separate approved QA design is required.'],
                 '[E/A] Supporting analyses and their acceptance limits; [R] ranked integration choices.',
                 '[R] Applied slide/notebook/reference edits, new test evaluation, new AUC gain, submission or WP8 execution.')
    outputs = paths + [proposal_path, handback_path, manifest, evidence_path, ADDONS / 'reports/WP7_report.md', validation_path]
    assert outside_snapshot() == before, 'STOP-1: outside files changed before final publication'
    write_json('results/wp7_final_verification.json',
               dict(status='DONE', directory_diff=difference, work_packages=statuses,
                    artifacts=[file_info(path) for path in outputs],
                    deliveries=[file_info(ROOT / name) for name in ('philopateer.pdf', 'philopateer.pptx', 'philopateer.ipynb', 'references.txt')],
                    new_code_validation=dict(passed=validation['passed'], final_checks=validation['tests'],
                                             existing_implementation_tests=validation['existing_implementation_tests']),
                    no_integration=True, no_submission=True, no_base_classifier_training=True,
                    authorized_calibration_sigmoid_fits=results[5]['calibration']['new_sigmoid_fits'],
                    no_new_test_computations=True,
                    historical_stop_resolution='Earlier initialization/helper failures were superseded by the authorized import-order fix and compliant full WP0/WP1 reruns. Historical stop records are retained; their old statuses are not current results.',
                    human_gate='STOP after WP7; wait for A/B/C. GO v3-model has not been authorized.',
                    file_count=len(files)), __file__, 7, inputs, {'outside_files': len(after), 'slides': 15, 'claim_rows': 278})
    print(json.dumps({'status': 'DONE', 'outside_files': len(after), 'outside_changes': 0, 'wp5_status': wp5_status, 'integration': 'NOT_APPLIED', 'wp8': 'OFF'}))


def proposal(slides, ledger, wp5_status):
    panel = next(text for text in slides[12]['text_elements'] if text.startswith('Calibration simulation'))
    heading = next(text for text in slides[12]['text_elements'] if text.startswith('Binary learning'))
    footer12 = next(text for text in slides[11]['text_elements'] if text.startswith('[D1, M5'))
    sentence5 = next(text for text in slides[4]['text_elements'] if text.startswith('Value-aware triage'))
    methods15 = next(text for text in slides[14]['text_elements'] if text.startswith('[M1]'))
    methods15_right = next(text for text in slides[14]['text_elements'] if text.startswith('[M3]'))
    append_text = (ADDONS / 'results/wp6_references_append_option_c.txt').read_text(encoding='utf-8').strip()
    removed = [row for row in ledger if row['slide_number'] == '13' and row['displayed_text'] in ('80,000', '160,000')]
    assert [row['claim_id'] for row in removed] == ['C0137', 'C0139']
    removed_ids = ', '.join(row['claim_id'] + ' / CSV line ' + str(row['csv_line']) for row in removed)
    return f'''# Integration proposal — human decision required

[E] Nothing below is applied. Frozen model, notebook, presentation, PDF and references remain unchanged. Current presentation: **15 slides**; current claims ledger: **278 data rows**. [R] Replacements only; no extra page or slide. [E] WP5 terminal status: **{wp5_status}**; acceptance failures, if any, are not repaired by changing a reporting threshold.

## Ranked candidates

### 1. Slide 13: capacity, two nulls and decision quality — highest value

[E] Replace the current right-hand heading and panel. Keep the left-hand enrollment/cost text, central propensity strip, scale/extend/stop rules and exact harm gate unchanged. [R] Use a compact native table in the existing top region; do not overlay the propensity strip or shrink text automatically. Geometry and all-slide visual QA are still required after approval.

**Exact heading before**
```text
{heading}
```
**Exact heading after [R]**
```text
Capacity ≠ profit proof
```
**Exact panel before**
```text
{panel}
```
**Exact panel after [E/A]** — slash pairs are effect / variable-profit power, in percent:

| n/arm [A] | γ=10% [A] | γ=16% [A] | γ=20% [A] | γ=30% [A] |
|---:|---:|---:|---:|---:|
| 5,000 | 19.8 / 2.6 | 42.9 / 7.9 | 59.7 / 19.9 | 93.6 / 60.7 |
| 7,872 | 27.5 / 2.1 | 59.9 / 11.5 | 78.6 / 27.9 | 99.3 / 79.8 |

```text
[E/A] E4 V-stratified; DEFF=1; 1,000 simulations/point.
[E/A] 80%-power γ MDE: 26.0% / 20.7% at 5,000 / 7,872 per arm; interpolated. Profit MDE not established through γ=30%.
[E/A] At 7,872/arm, γ=20%, DEFF=1.1: scale 7.6%, extend 91.9%, stop 0.5% (observable adjusted contribution; no harm assumed).
[A] $1 variable-cost null excludes $5,000 startup and unquoted implementation costs; no validated household-clustered or live power.
```

[E] Sources: `results/wp1_power.json → capacity_mde`, complete MC uncertainty in `power_rows`; `results/wp1_capacity_mde.csv`; `results/wp2_decision_quality.csv` row `n_per_arm=7872,gamma=.20,deff=1.1`; supporting method in `reports/WP1_report.md` and `reports/WP2_report.md`. [E] At γ=.20, first qualifying E4 declared grid is 10,000/arm for effect and 40,000/arm for variable-profit, not an exact minimum and not a resolution of v2's fully loaded 80,000/arm framing. [R] Keep those grid details supporting-only if the panel is crowded.

[E] Ledger impact: retire **{removed_ids}** from the old panel; retain the existing 80% planning target and enrollment/harm values. The 278-row file has no intrinsic IDs: `C0001` means first data row, and CSV line = data-row index+1; exact aliases/keys are captured in `results/wp7_readonly_deck_ledger.json`. Add new rows for every table cell, γ/n/DEFF/replicate/MDE and decision probability; do not reuse old source keys for new values. [R] Risk: low scientific risk, moderate layout/provenance QA. These are empirical conditional simulations, not measured treatment effects. Avoid claiming “powered” solely from 78.6% or rounding 79.8% into an established 80%.

### 2. Slide 12: prior-integrated net sensitivity — Option C

[E] Existing heatmap, break-even and prior-stress values remain unchanged. Replace only the existing footer; do not mislabel a sensitivity band as a confidence interval.

**Exact footer before**
```text
{footer12}
```
**Exact footer after [E/A]**
```text
[D1, M5–M6, M9] Prior-integrated net at the frozen 10% threshold: P(net>0)=17%–93% across assumed prevention priors; 69% under Beta(6,24), centered on 20%. Sensitivity, not a CI or EMPC; no treatment labels.     12
```

[E] Sources: `results/wp3_roi_band.json → priors[].closed_form.p_positive` and `band`; `results/wp6_citation_register.csv → M9`. [A] Beta(6,14) is a verified package default used as an assumption; Beta(6,24) centers on the existing 20% assumption; Beta(2,18) is the reviewer's pessimistic assumption. [E] No existing numeric ledger row is deleted by this footer replacement; all slide-12 heatmap/stress rows remain. Add the 10%, 17%, 93%, 69%, 6/24 and 20% tokens plus appropriate source/prior tags. [R] Risk: medium; reference and layout QA needed, prevention remains unidentified.

### 3. Slide 5 and M5 wording — optional diagnostic-only wording

[E] Preserve the chart and its original quantitative claims; do not replace a verified known-prior correction with an EM result. [R] No numeric live-prior estimate or automatic hold/proceed trigger belongs in this deck.

**Exact slide-5 sentence before**
```text
{sentence5}
```
**Exact slide-5 sentence after [R]**
```text
Value-aware triage is not a response model. EM is a label-shift diagnostic only; stable class-conditionals are unverified and day-60 labels remain ground truth.
```

**Exact slide-15 methods block before**
```text
{methods15}
```
**Exact slide-15 methods block after [E/R]**
```text
[M1] scikit-learn: evaluation and calibration.
[M2] LightGBM: local CPU boosting.
[M5] Saerens et al. (2002): prior adjustment; abstract-only.
[M6] Elkan (2001): costs / known-prior correction.
```

[E] Supporting M5 scope: “Implemented from the standard derivation and validated by simulation; paper read from abstract only.” `results/wp5_label_shift.json` and `results/wp6_citations.json → source_observations.m5` are the source keys. [E] Existing slide-5 numeric prior/chart rows and slide-15 year row are preserved; add day-60 token if this wording is approved. [R] Risk: medium and low priority. WP5 acceptance must be reviewed before any operational use; diagnostic wording does not imply recovery or calibrated live intervals. The brief's “lower bound below π* → hold” and “straddles π* → proceed” overlap; supporting-only conservative hold priority is a recommendation, not a protocol modification. Floor continues.

### 4. References — only sources actually used

[E] Root `references.txt` is untouched. [R] Options A/B require **no new external reference** for the locally computed WP1/WP2 results. [R] Option C with candidate 2 cites M9: preserve all existing reference text and append the exact block below. The corresponding References-field draft is `results/wp6_omnicampus_references_draft.txt`. Existing S4 accessible-copy and M5 abstract-only caveats stay; do not duplicate them.

**Exact append after [E/A/R]** — before: no M9 block
```text
{append_text}
```

**Exact slide-15 right methods block before**
```text
{methods15_right}
```
**Exact block after [R]** — only if M9 is cited in slide 12
```text
[M3] XGBoost; [M4] CatBoost: comparators.
[M7] Deng et al. (2013): pre-period adjustment.
[M8] Neslin et al. (2006): historical churn protocol.
[M9] EMP source: assumed Beta(6,14) default.
```

[E] This removes no existing numeric ledger claim; add package-prior numeric tokens. [R] Supporting-only Nadeau/Bouckaert/ProfTree corrections are not new PDF references. Risk: low content risk, medium if reference-page typography needs adjustment.

### 5. Supporting-only material

[R] Keep WP4 ITT/Floor addendum, EVSI detail and horizons, queue assumption table, label-shift grid/coverage and trigger conflict in `v3_addons`, not new submission pages. [E/A] EVSI is $45–$531 per future cohort across priors; the $12,872 pilot also buys production contacts, so this is not a pure research-cost comparison or funding proof. No AUC/model claim changes.

## Human options — not selected

| Option [R] | Scope | Risk | Indicative effort [A] |
|---|---|---|---|
| A | Submit frozen v2 as-is; retain supporting analyses | None from integration | 0 |
| B | Slide 13 replacement only; no external reference append needed | Low/moderate QA | About 1 day |
| C | Slides 12/13; optional 5 and existing reference-page blocks; M9 if cited | Medium | About 1–1.5 days |
| GO v3-model | Separate WP8 and potential third test use | High; OFF | Separate approved project |

[R] Recommend **B first**: the capacity/profit distinction adds the most decision value without changing the model or economics. C is reasonable if the prior sensitivity earns its limited page space; the monitor is lower priority and diagnostic-only. A is safe if no integration QA is desired. Do not run WP8.

## Separate integration QA — only after approval

[R] Preserve the notebook's frozen execution cells; never Run All. A future integration decision must resolve how new supporting results are reproduced within the submitted notebook, if required by the rubric: the current frozen notebook does not contain WP1–WP5 code. Do not silently imply it does. Any notebook narrative/cache addition needs an explicitly approved scope, not a model retrain.

[R] Approved changes must follow source/claim → presentation → geometry → all-15-slide visual review → hash-bound receipt and refreshed hashes, with ≤15 PDF pages and <10,000,000 bytes. **User instruction overrides the brief's Office-PDF export step: any newly created/edited PDF must use LaTeX only**, with complete professional source, assets and compilation instructions. No PDF is generated now; the future PDF QA/export design needs separate approval. [E] Current unchanged slides are not newly visually certified in this v3 run.

## Reviewer calendar targets [R]

| Target date | Milestone |
|---|---|
| 3 November 2026 | WP0–WP3 done |
| 6 November 2026 | WP4–WP6 done; WP7 proposal delivered |
| 8 November 2026 | Human gate decision |
| 9–13 November 2026 | Integration and QA, only if B/C approved |
| 16 November 2026 | Artifact freeze; no further edits |
| 17–24 November 2026 | Human review, upload, References field and submission |
| 27 November 2026 | Hard backstop; deadline 28 November 2026, 11:30 UTC |

**[R] STOP here. Await A/B/C; no deliverable, reference, notebook, protocol, submission or WP8 action is authorized by this proposal.**
'''


def handback(statuses, difference, count, wp5):
    rows = '\n'.join('| ' + name + ' | ' + statuses[name] + ' |' for name in (f'WP{i}' for i in range(8)))
    grid = wp5['grid_summary']
    originals = wp5['simulation']['original_batches']
    converged = sum(row['converged_originals'] for row in grid)
    failures = sum(row['bootstrap_failures'] for row in grid)
    coverage = [row['coverage_95_generating_prior'] for row in grid]
    errors = ', '.join(f'{row["batch_size"]:,}: {100 * row["median_error"]:+.3f} pp'
                       for row in grid if row['true_prior'] == .02 and row['batch_size'] >= 10_000)
    failed_checks = ', '.join(name for name, check in wp5['acceptance_checks'].items() if not check['passed']) or 'none'
    crossing = wp5['break_even']['first_crossing']
    planning = f'{crossing["prior_star"]:.3%}' if crossing is not None else 'not established'
    return f'''# v3 handback — supporting analysis complete, integration not applied

[E] Company A · philopateer · local CPU only · frozen submission completed locally, **not submitted**. [E] No model promotion or AUC change: retained AUC **0.6978109022**. [R] Human integration gate remains closed; WP8 OFF.

| Work package [E] | Terminal status [E] |
|---|---|
{rows}

## Five headlines

1. [E/A] One 10,000-account list gives at most 5,000/arm: E4 effect/variable-profit power **59.7%/19.9%** at assumed 20% prevention. At 7,872/arm: **78.6%/27.9%**; not fully loaded profit proof.
2. [E/A] Interpolated 80%-effect prevention MDE: **26.0%/20.7%** at 5,000/7,872 per arm. Profit MDE not established through 30%; oracle-prevention statistics are ineligible.
3. [E/A] Information value **$45–$531/future cohort** across assumed priors; below EVPI. The pilot also buys production contacts, so this does not prove pilot funding pays.
4. [E/A] Prior-integrated P(net>0) **17%–93%**, central **69%** under the 20%-centered prior. Not a confidence interval, measured prevention, or EMPC; frozen 10% policy unchanged.
5. [E/A] WP5 completed **{originals:,} batches / 5,000,000 bootstrap fits**: EM convergence **{converged:,}/{originals:,}**; bootstrap failures **{failures:,}**; conditional generating-prior coverage **{min(coverage):.1%}–{max(coverage):.1%}**. At true π=2%, median errors (n: error): **{errors}**. Alternate non-test planning π*: **{planning}**, not a frozen-test reproduction or live estimate.

[E] WP5 failed checks: **{failed_checks}**. [R] Monitor stays **diagnostic only**; day-60 labels override it. Floor and exact harm gate unchanged; no household/treatment/profit labels exist. WP1's terminal caveat excludes unobservable prevention-oracle results from capacity claims.

[R] **Recommend B first**, or C if the prior band warrants added QA; A remains safe. Exact before/after wording and ledger impacts: [INTEGRATION_PROPOSAL.md](INTEGRATION_PROPOSAL.md). No option is applied.

[E] Outside directory diff: **{difference['files_before']:,} → {difference['files_after']:,} files; 0 added, 0 removed, 0 changed.** All four delivery fingerprints remain frozen. Historical initialization stop records are retained but superseded by the authorized correction and compliant reruns.

[E] Files created: **{count} sandbox files**, listed completely in [results/wp7_files_created.csv](results/wp7_files_created.csv). Groups: `src/` scripts, `tests/` new-code checks, `results/` raw/summary/provenance/source evidence, `figures/` reviewed PNG drafts, `reports/WP0–WP7_report.md`, `protocol_addendum.md`, this handback and proposal; historical/scratch files are explicitly marked. [E] Final verification: [results/wp7_final_verification.json](results/wp7_final_verification.json).

[R] Remaining human action: select A/B/C, approve any separate integration/QA scope, and submit before **28 November 2026, 11:30 UTC**. Any new PDF must use LaTeX only. [E] No package installed, no cloud execution/upload, no new test-row computation, no frozen file edited, no WP8 run.
'''


if __name__ == '__main__':
    main()
