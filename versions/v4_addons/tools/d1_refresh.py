"""D1 — refresh stale v3 documents (HANDBACK.md, reports/WP7_report.md), write WP8 status addendum and MANIFEST_v4.json.

Run with the explicit G1 exception for the two in-place edits and their backups:
  V4_ALLOW_WRITE="<root>/v3_addons/HANDBACK.md;<root>/v3_addons/HANDBACK.md.pre_v4;<root>/v3_addons/reports/WP7_report.md;<root>/v3_addons/reports/WP7_report.md.pre_v4"
"""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402

TASK_INDEX = 1
WP8 = 'v3_addons/results/wp8_model.json'
PREREG = 'v3_addons/prereg_wp8.md'
WP8_REPORT = 'v3_addons/reports/WP8_report.md'
WP7V = 'v3_addons/results/wp7_final_verification.json'
NEW_WORDING = 'WP8 was executed; decision `rejected_keep_frozen_v2_stop_model_track`; the WP8 challenger track is closed.'

EDITS = {
    'v3_addons/HANDBACK.md': [
        ('[R] Human integration gate remains closed; WP8 OFF.',
         '[R] Human integration gate remains closed. [E] ' + NEW_WORDING),
        ('no new test-row computation, no frozen file edited, no WP8 run.',
         'no new test-row computation, no frozen file edited. [E] ' + NEW_WORDING + ' Status vocabulary and caveats: `../v4_addons/WP8_status_addendum.md`.'),
        ('| WP7 | DONE |{nl}',
         '| WP7 | DONE |{nl}| WP8 | COMPLETED_REJECTED (executed after this handback; see `reports/WP8_report.md`) |{nl}'),
        ('[E] Files created: **118 sandbox files**, listed completely in [results/wp7_files_created.csv](results/wp7_files_created.csv).',
         '[E] Files created at WP7 time: **118 sandbox files**, listed in [results/wp7_files_created.csv](results/wp7_files_created.csv); the complete post-WP8 inventory of `v3_addons/` is `../v4_addons/MANIFEST_v4.json`.'),
    ],
    'v3_addons/reports/WP7_report.md': [
        ('[R] Applied slide/notebook/reference edits, new test evaluation, new AUC gain, submission or WP8 execution.',
         '[R] Applied slide/notebook/reference edits, new test evaluation, new AUC gain, or submission. [E] ' + NEW_WORDING),
    ],
}
FORBIDDEN_AFTER = ('WP8 OFF', 'no WP8 run', 'WP8 execution')


def apply_edits():
    allowed = {}
    for rel, replacements in EDITS.items():
        path = c.ROOT / rel
        backup = path.with_name(path.name + '.pre_v4')
        with path.open(encoding='utf-8', newline='') as stream:
            original = stream.read()
        newline = '\r\n' if '\r\n' in original else '\n'
        pre_sha = c.digest(path)
        if not backup.exists():
            shutil.copyfile(path, backup)
        assert c.digest(backup) == pre_sha, 'backup does not match original'
        text = original
        for old, new in replacements:
            old, new = old.replace('{nl}', newline), new.replace('{nl}', newline)
            assert text.count(old) == 1, f'{rel}: expected exactly one occurrence of {old[:60]!r}, found {text.count(old)}'
            text = text.replace(old, new)
        with path.open('w', encoding='utf-8', newline='') as stream:
            stream.write(text)
        post_sha = c.digest(path)
        for phrase in FORBIDDEN_AFTER:
            assert phrase not in text, f'{rel}: still contains {phrase!r}'
        allowed[rel] = dict(kind='changed', pre_sha256=pre_sha, post_sha256=post_sha, card='D1', reason='stale WP8 status wording refreshed; backup kept as *.pre_v4')
        allowed[rel + '.pre_v4'] = dict(kind='added', post_sha256=pre_sha, card='D1', reason='byte-identical backup of the pre-v4 document')
    target = c.SNAPSHOTS / 'allowed_changes.json'
    existing = json.loads(target.read_text(encoding='utf-8')) if target.exists() else {}
    existing.update(allowed)
    target.write_text(json.dumps(existing, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return allowed


def manifest():
    files = {}
    for path in sorted((c.ROOT / 'v3_addons').rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts:
            files[path.relative_to(c.ROOT).as_posix()] = dict(size=path.stat().st_size, sha256=c.digest(path))
    wp8_files = sorted(key for key in files if 'wp8' in key.lower())
    old_count = c.read_source(WP7V, 'file_count')
    body = dict(created_utc=c.utc_now(), scope='every file under v3_addons/ (excluding __pycache__), including WP8 outputs and the two *.pre_v4 backups',
                file_count=len(files), old_manifest_file_count=old_count, old_manifest_source=WP7V,
                wp8_file_count=len(wp8_files), wp8_files=wp8_files, total_bytes=sum(item['size'] for item in files.values()), files=files)
    (c.ADDONS / 'MANIFEST_v4.json').write_text(json.dumps(body, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    return body


def main():
    c.runtime_record()
    allowed = apply_edits()
    man = manifest()

    n = c.Numbers()
    n.source('wp8_classifier_fits', WP8, 'fit_counts.classifier')
    n.source('wp8_sigmoid_fits', WP8, 'fit_counts.sigmoid')
    n.source('wp8_mean_delta_auc', WP8, 'intervals.auc.mean')
    n.source('wp8_corrected_df', WP8, 'intervals.auc.df')
    n.source('wp8_corrected_se', WP8, 'intervals.auc.corrected_se')
    n.source('wp8_iid_lower', WP8, 'intervals.auc.iid[0]')
    n.source('wp8_iid_upper', WP8, 'intervals.auc.iid[1]')
    n.source('wp8_conservative_lower', WP8, 'intervals.auc.conservative[0]')
    n.source('wp8_conservative_upper', WP8, 'intervals.auc.conservative[1]')
    n.source('wp8_frozen_n_estimators', PREREG, 'line:29:regex:n_estimators=(\\d+)')
    inventory = c.read_json(c.ROOT / WP8)['fit_inventory']
    classifier_iterations = sorted({item['iterations'] for item in inventory if item['kind'] == 'classifier'})
    n.computed('wp8_classifier_iterations_distinct_count', len(classifier_iterations), '[E]', 'number of distinct iteration counts across classifier fits', source_file=WP8, source_key='fit_inventory[*].iterations')
    n.computed('wp8_classifier_iterations_value', classifier_iterations[0], '[E]', 'the single iteration count reported by every classifier fit', source_file=WP8, source_key='fit_inventory[*].iterations')
    n.computed('wp8_classifier_converged_true', sum(1 for item in inventory if item['kind'] == 'classifier' and item['converged']), '[E]', 'classifier fits flagged converged', source_file=WP8, source_key='fit_inventory[*].converged')
    n.source('wp8_gate_auc_threshold', PREREG, 'line:46:regex:Mean delta AUC must be >=([0-9.]+)', tag='[R]')
    n.computed('wp8_failed_gates', len(c.read_source(WP8, 'promotion.failed_gates')), '[E]', 'gates failed', source_file=WP8, source_key='promotion.failed_gates')
    n.computed('wp8_total_gates', len(c.read_source(WP8, 'promotion.gates')), '[E]', 'gates evaluated', source_file=WP8, source_key='promotion.gates')
    n.source('wp8_development_fits', WP8_REPORT, 'line:9:regex:(\\d+) development', note='development fits per WP8 report line 9')
    n.computed('manifest_file_count', man['file_count'], '[E]', 'files under v3_addons/ in MANIFEST_v4.json', source_file='v4_addons/MANIFEST_v4.json', source_key='file_count')
    n.computed('manifest_wp8_file_count', man['wp8_file_count'], '[E]', 'WP8 files included', source_file='v4_addons/MANIFEST_v4.json', source_key='wp8_file_count')
    n.source('old_manifest_file_count', WP7V, 'file_count')
    n.declared('wp8_dev_train_rows_k', 48, '[E]', 'development fit size (thousand rows) per WP8 limitations "48k development-to-calibration / 60k refit fit-size shift"')
    n.declared('wp8_refit_train_rows_k', 60, '[E]', 'outer refit size (thousand rows), same source string')
    n.declared('corrected_t_fold_term', 0.1, '[E]', '1/10 term in SE = sqrt((1/10 + 0.25) * sample variance), WP8_report line 199')
    n.declared('corrected_t_ratio_term', 0.25, '[E]', 'heldout/train ratio term, same formula')

    body = dict(numbers=n.entries, edits={rel: [dict(before=old, after=new) for old, new in items] for rel, items in EDITS.items()},
                allowed_changes=allowed, manifest_summary={k: v for k, v in man.items() if k != 'files'},
                wp8_limitations=c.read_json(c.ROOT / WP8)['limitations'], forbidden_phrases_checked=list(FORBIDDEN_AFTER))
    inputs = [c.ROOT / p for p in (WP8, PREREG, WP8_REPORT, WP7V)] + [c.ROOT / rel for rel in EDITS]
    c.write_json(c.RESULTS / 'd1_refresh.json', body, __file__, TASK_INDEX, inputs)
    print('edits applied:', {rel: len(items) for rel, items in EDITS.items()})
    print('manifest files:', man['file_count'], 'wp8 files:', man['wp8_file_count'], 'old count:', man['old_manifest_file_count'])


if __name__ == '__main__':
    main()
