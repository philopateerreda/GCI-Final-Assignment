import json
from pathlib import Path

from common import ADDONS, ROOT, digest, outside_snapshot, utc_now, write_json


def main():
    before = json.loads((ADDONS/'results/write_boundary_before.json').read_text(encoding='utf-8'))['files']
    after = outside_snapshot()
    added = sorted(set(after)-set(before))
    removed = sorted(set(before)-set(after))
    changed = sorted(key for key in set(before)&set(after) if before[key]!=after[key])
    boundary_pass = not (added or removed or changed)
    reason = '[E] NumPy/SciPy were initialized before common.py applied thread environment variables. Data-free np.show_runtime inspection confirmed both OpenBLAS pools configured for 12 threads, exceeding the six-thread maximum.'
    for relative in ('results/inventory.json','results/wp1_power.json','results/wp1_tests.json'):
        path = ADDONS/relative
        record = json.loads(path.read_text(encoding='utf-8'))
        record['status'] = 'BLOCKED_THREAD_GUARDRAIL'
        record['validity'] = dict(approved_for_integration=False, reason=reason, prior_numeric_results='Retained for audit only; no adoption or integration claim until a compliant rerun is verified.')
        record['provenance']['status_amendment'] = dict(script=Path(__file__).resolve().as_posix(),script_sha256=digest(__file__), created_utc=utc_now(), reason=reason)
        path.write_text(json.dumps(record,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')
    intended = {'reports/STOP_REPORT.md','results/stop_report.json'}
    created = sorted(set(path.relative_to(ADDONS).as_posix() for path in ADDONS.rglob('*') if path.is_file()) | intended)
    body = dict(status='BLOCKED_WAITING_FOR_HUMAN', stop_condition='Section 1 HARD GUARDRAILS: six threads maximum was not enforced before BLAS initialization',
                reason=reason,
                runtime_inspection=dict(method='Data-free import of wp1_power followed by numpy.show_runtime; no simulation/data load in inspection.',
                                        numpy_openblas_threads=12,scipy_openblas_threads=12,required_maximum=6),
                wp_status=dict(WP0='BLOCKED: integrity/input checks passed; numerical outputs quarantined for runtime compliance',
                               WP1='BLOCKED: draft numerical grid saved; figure export failed; outputs quarantined',
                               WP2='NOT_STARTED',WP3='NOT_STARTED',WP4='NOT_STARTED',WP5='NOT_STARTED',WP6='NOT_STARTED',WP7='NOT_REACHED',WP8='OFF'),
                other_findings=[
                    '[E] WP1 ran all 48 n/prevention points but then failed because the concurrently prepared PNG helper was not yet available. No full WP1 completion is claimed.',
                    '[E] The draft report wrote DONE before figure generation. Its status and the affected JSON statuses are now marked BLOCKED.',
                    '[E] Literal Appendix C E2/E3 use latent prevented outcomes, unavailable to actual randomized trials. They are explicitly oracle diagnostics, not valid pilot-capacity claims.',
                    '[E] CSV source scanning filters non-test IDs before parsing numeric V; no test outcomes or values enter a scientific data frame or new metric. The reviewer strict no-read concern is stronger than the brief actual no-new-test-computation rule.',
                    '[E] Full handoff exists; the named concise handoff is missing. No input required training or test-split reconstruction.',
                    '[E] The PNG helper agent was stopped. Its helper source and a validation-only PNG inside src are retained as unfinished drafts.',
                    '[E] All task-owned analytical/background work has stopped; no package was installed and no submission was made.',
                ],
                directory_diff=dict(passed=boundary_pass, files_before=len(before),files_after=len(after),added_outside=added,removed_outside=removed,changed_outside=changed),
                files_created=created,
                requested_human_decision='[R] Authorize sandbox-only import-order correction, explicit six-thread launch environment, runtime verification before numerics, helper validation, and compliant WP0/WP1 rerun; or retain the stop.',
                no_integration=True,no_model_training=True,no_new_test_metrics=True)
    inputs=[ADDONS/'results/write_boundary_before.json',ADDONS/'src/wp1_power.py',ADDONS/'src/wp0_preflight.py',ADDONS/'src/common.py']
    write_json('results/stop_report.json',body,__file__,0,inputs,dict(outside_files=len(after)))
    report=[
        '# Mandatory stop — v3 decision-grade add-ons', 'Status: BLOCKED [E]; waiting for the human', '',
        '## Reason',reason,'',
        '[E] The authoritative brief section 1 says any hard-guardrail violation requires a stop and report. WP2–WP7 have not started; WP8 remains OFF.', '',
        '## Current status',
        '| Package | Status [E] |','|---|---|',
    ]
    report += [f'| {wp} | {status} |' for wp,status in body['wp_status'].items()]
    report += ['', '## Other findings']+['- '+item for item in body['other_findings']]
    report += ['', '## Frozen-file integrity',
               f'[E] Full content-hash directory diff: {len(before):,} files before, {len(after):,} after; {len(added)} additions, {len(removed)} removals, {len(changed)} modifications outside v3_addons. '+('PASS.' if boundary_pass else 'FAIL; inspect machine report.'),
               '[E] No final deliverable, notebook, references, protocol, execution marker, supplied original or v1 snapshot has changed.', '',
               '## Required decision',
               body['requested_human_decision'],
               '[R] Keep all current WP1 numbers as unapproved audit drafts; do not put them into the submission or interpret the oracle estimators as observed trial evidence.', '',
               '## Files created [E]']
    report += ['- '+name for name in created]
    report += ['', '[E] Machine evidence and input fingerprints: ../results/stop_report.json. No work continues without the human response.']
    (ADDONS/'reports/STOP_REPORT.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    assert boundary_pass, 'STOP-4: outside-sandbox directory diff failed'
    print(json.dumps(dict(status=body['status'],outside_files=len(after),outside_changes=len(added)+len(removed)+len(changed)),indent=2))


if __name__ == '__main__':
    main()
