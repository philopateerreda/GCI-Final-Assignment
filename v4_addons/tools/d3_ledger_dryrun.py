"""D3 — ledger dry-run: apply each option's retire/add operations to a copy of the 278-row claims ledger."""
import csv
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402
import integration_spec as spec_module  # noqa: E402

TASK_INDEX = 4
OUT = c.ADDONS / 'ledger_dryrun'
RESULTS = c.RESULTS / 'd3_ledger_dryrun.json'


def claim_index(claim_id):
    return int(claim_id[1:]) - 1  # C0001 = first data row


def apply(option_name, option, header, data):
    rows = [list(row) for row in data]
    retired, added = [], []
    for edit in option['edits']:
        for claim_id in edit['retire']:
            retired.append(dict(claim_id=claim_id, csv_line=claim_index(claim_id) + 2, row=rows[claim_index(claim_id)]))
        for row in edit['add']:
            haystack = (edit['after'] + ' ' + edit.get('right_after', '')).replace('$', '')
            assert row[7] in haystack, f'{option_name} slide {edit["slide"]}: token {row[7]!r} not in after-text'
            added.append(row)
    retire_positions = sorted({claim_index(item['claim_id']) for item in retired}, reverse=True)
    for position in retire_positions:
        rows.pop(position)
    rows.extend(added)
    buffer = io.StringIO(newline='')
    writer = csv.writer(buffer, lineterminator='\r\n')
    writer.writerow(header)
    writer.writerows(rows)
    payload = buffer.getvalue().encode('utf-8')
    target = OUT / f'claims_ledger_{option_name}.csv'
    target.write_bytes(payload)
    return dict(option=option_name, file=target.relative_to(c.ROOT).as_posix(), rows_original=len(data), rows_retired=len(retired), rows_added=len(added),
                rows_total=len(rows), sha256=c.digest(target), retired=retired, added_tokens=[row[7] for row in added],
                slides_touched=sorted({edit['slide'] for edit in option['edits']}))


def validate_existing(header, data):
    """Sanity: how many existing rows re-render to their displayed_text with the ledger's own formatter/scale."""
    ok = bad = 0
    for row in data:
        record = dict(zip(header, row))
        try:
            rendered = spec_module.render_ledger_display(record['formatter'], record['scale'], record['exact_value'], record['unicode_minus'])
            ok += rendered == record['displayed_text']
            bad += rendered != record['displayed_text']
        except Exception:  # noqa: BLE001
            bad += 1
    return ok, bad


def main():
    c.runtime_record()
    OUT.mkdir(exist_ok=True)
    header, data, raw = spec_module.ledger_rows()
    spec = c.read_json(spec_module.RESULTS)['spec']
    original_sha = c.digest(c.ROOT / spec_module.LEDGER)
    results = {name: apply(name, option, header, data) for name, option in spec['options'].items()}
    ok, bad = validate_existing(header, data)
    n = c.Numbers()
    n.source('ledger_rows_original', spec_module.LEDGER, 'rowcount')
    for name, item in results.items():
        n.computed(f'rows_added_{name}', item['rows_added'], '[E]', f'rows added for option {name}', source_file=spec_module.RESULTS.relative_to(c.ROOT).as_posix(), source_key=f'spec.options.{name}.edits[*].add')
        n.computed(f'rows_retired_{name}', item['rows_retired'], '[E]', f'rows retired for option {name}', source_file=spec_module.RESULTS.relative_to(c.ROOT).as_posix(), source_key=f'spec.options.{name}.edits[*].retire')
        n.derived(f'rows_total_{name}', f'ledger_rows_original - rows_retired_{name} + rows_added_{name}')
        assert n.value(f'rows_total_{name}') == item['rows_total']
    n.computed('existing_rows_rerender_ok', ok, '[E]', 'existing rows whose displayed_text re-renders from formatter/scale/exact_value', source_file=spec_module.LEDGER, source_key='all rows')
    n.computed('existing_rows_rerender_mismatch', bad, '[E]', 'existing rows that do not re-render (chart-axis or textual formats)', source_file=spec_module.LEDGER, source_key='all rows')
    body = dict(numbers=n.entries, original_sha256=original_sha, option_A_reproduces_original=results['A']['sha256'] == original_sha, options=results,
                claim_id_convention='C0001 = first data row; CSV line = data-row index + 2 (header is line 1)')
    c.write_json(RESULTS, body, __file__, TASK_INDEX, [c.ROOT / spec_module.LEDGER, spec_module.RESULTS])
    print('original sha256:', original_sha)
    for name, item in results.items():
        print(f'{name}: retired={item["rows_retired"]} added={item["rows_added"]} total={item["rows_total"]} sha256={item["sha256"][:16]}... slides={item["slides_touched"]}')
    print('A reproduces original:', body['option_A_reproduces_original'])
    print(f'existing rows re-render check: ok={ok} mismatch={bad}')


if __name__ == '__main__':
    main()
