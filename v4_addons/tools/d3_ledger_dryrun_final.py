"""D3 final — ledger dry-run for the final B' text after F1 placeholder resolution.

Copy of d3_ledger_dryrun.py; the original script and its outputs are not edited. New outputs:
  ledger_dryrun/claims_ledger_A_final.csv, ledger_dryrun/claims_ledger_B_PRIME_final.csv, results/d3_ledger_final.json
"""
import csv
import io
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402
import integration_spec as spec_module  # noqa: E402
import integration_final as final_module  # noqa: E402
import check_numbers  # noqa: E402

TASK_INDEX = 14
OUT = c.ADDONS / 'ledger_dryrun'
RESULTS = c.RESULTS / 'd3_ledger_final.json'
D3_RESULTS = 'v4_addons/results/d3_ledger_dryrun.json'
D3_LEDGER = 'v4_addons/ledger_dryrun/claims_ledger_B_PRIME.csv'


def claim_index(claim_id):
    return int(claim_id[1:]) - 1  # C0001 = first data row


def apply(option_name, edits, header, data):
    rows = [list(row) for row in data]
    retired, added = [], []
    for edit in edits:
        for claim_id in edit['retire']:
            retired.append(claim_id)
        for row in edit['add']:
            haystack = (edit['after'] + ' ' + edit.get('right_after', '')).replace('$', '')
            assert row[7] in haystack, f'{option_name} slide {edit["slide"]}: token {row[7]!r} not in final after-text'
            added.append(row)
    for position in sorted({claim_index(claim_id) for claim_id in retired}, reverse=True):
        rows.pop(position)
    rows.extend(added)
    buffer = io.StringIO(newline='')
    writer = csv.writer(buffer, lineterminator='\r\n')
    writer.writerow(header)
    writer.writerows(rows)
    target = OUT / f'claims_ledger_{option_name}_final.csv'
    target.write_bytes(buffer.getvalue().encode('utf-8'))
    return dict(option=option_name, file=target.relative_to(c.ROOT).as_posix(), rows_original=len(data), rows_retired=len(retired),
                rows_added=len(added), rows_total=len(rows), sha256=c.digest(target), retired=retired,
                added_tokens=[row[7] for row in added], slides_touched=sorted({edit['slide'] for edit in edits}))


def read_rows(path):
    raw = Path(path).read_bytes()
    return list(csv.reader(io.StringIO(raw.decode('utf-8'), newline='')))


def count_changed(path_a, path_b):
    left, right = read_rows(path_a), read_rows(path_b)
    assert left[0] == right[0], 'ledger headers differ'
    body_left, body_right = left[1:], right[1:]
    return sum(1 for first, second in zip(body_left, body_right) if first != second) + abs(len(body_left) - len(body_right))


def numeric_tokens(text):
    found = []
    for match in check_numbers.TOKEN.finditer(text.replace('$', '')):
        token = match.group(0).rstrip(',')
        if re.fullmatch(r'\d{1,3},\d{1,2}', token):  # Beta(6,24): a pair, not a thousands group
            found.extend(token.split(','))
        else:
            found.append(token)
    return found


def row_tokens(rows):
    found = set()
    for row in rows:
        for match in check_numbers.TOKEN.finditer(row[7].replace('$', '')):
            found.add(match.group(0).rstrip(','))
    return found


def is_structural(token):
    bare = token.lstrip('+\u2212-')
    return any(re.match(pattern, bare) for pattern in check_numbers.STRUCTURAL)


def coverage_missing(edit, data):
    allowed = row_tokens([row for row in data if row[0] == str(edit['slide'])]) | row_tokens(edit['add'])
    return [token for token in numeric_tokens(edit['after']) if token not in allowed and not is_structural(token)]


def main():
    c.runtime_record()
    OUT.mkdir(exist_ok=True)
    header, data, raw = spec_module.ledger_rows()
    n = final_module.bind_final()
    edits = final_module.final_edits(final_module.plain_formatter(n))
    original_sha = c.digest(c.ROOT / spec_module.LEDGER)

    result_a = apply('A', [], header, data)
    result_b = apply('B_PRIME', edits, header, data)
    assert result_a['sha256'] == original_sha, (result_a['sha256'], original_sha)
    changed = count_changed(c.ROOT / D3_LEDGER, c.ROOT / result_b['file'])
    identical = (c.ROOT / D3_LEDGER).read_bytes() == (c.ROOT / result_b['file']).read_bytes()
    placeholders = sum(edit['after'].count(final_module.PLACEHOLDER_MARKER) for edit in edits)
    missing = {edit['slide']: coverage_missing(edit, data) for edit in edits}

    for edit in edits:
        flag = edit['length_flag_over_15pct']
        print(f'slide {edit["slide"]}: {edit["length_before"]} -> {edit["length_after"]} chars '
              f'({edit["length_delta_pct"]:+.1f}%{" FLAG" if flag else ""}); added rows={len(edit["add"])}; '
              f'missing tokens={missing[edit["slide"]] or "none"}')

    n.computed('rows_added_final', result_b['rows_added'], '[E]', 'rows added for the final B_PRIME text',
               source_file=spec_module.RESULTS, source_key='spec.options.B_PRIME.edits[*].add')
    n.computed('rows_retired_final', result_b['rows_retired'], '[E]', 'rows retired for the final B_PRIME text',
               source_file=spec_module.RESULTS, source_key='spec.options.B_PRIME.edits[*].retire')
    n.computed('rows_changed_final', changed, '[E]', 'data rows that differ between the D3 B_PRIME dry-run and the final dry-run',
               source_file=D3_LEDGER, source_key='all rows')
    n.derived('rows_total_final', 'ledger_rows_original - rows_retired_final + rows_added_final')
    assert n.value('rows_total_final') == result_b['rows_total']
    n.source('rows_total_d3_b_prime', D3_RESULTS, 'numbers.rows_total_B_PRIME.value')
    for slide, edit in zip((11, 13), edits):
        n.computed(f'len_before_slide{slide}', edit['length_before'], '[E]', f'characters in the original slide-{slide} text element',
                   source_file='v3_addons/results/wp7_readonly_deck_ledger.json', source_key=f'slides[slide_number={slide}].text_elements')
        n.computed(f'len_after_slide{slide}', edit['length_after'], '[E]', f'characters in the final slide-{slide} text element (this script)')
        n.derived(f'len_delta_pct_slide{slide}', f'100 * (len_after_slide{slide} - len_before_slide{slide}) / len_before_slide{slide}')
        assert abs(n.value(f'len_delta_pct_slide{slide}') - edit['length_delta_pct']) < 0.05
    n.derived('slide13_growth_ratio', 'len_after_slide13 / len_before_slide13')
    n.computed('decision_needed_count', placeholders, '[E]', 'occurrences of the unresolved placeholder marker in the final slide text')
    n.computed('unbound_tokens_count', sum(len(items) for items in missing.values()), '[E]',
               'numeric tokens in the final slide text without an original or added ledger row')

    body = dict(numbers=n.entries, option='B_PRIME', final_edits=edits, option_A_reproduces_original=result_a['sha256'] == original_sha,
                option_A_sha256=result_a['sha256'], original_sha256=original_sha, option_A=result_a, option_B_PRIME=result_b,
                identical_to_d3_b_prime=identical, d3_b_prime_sha256=c.digest(c.ROOT / D3_LEDGER), changed_rows=changed,
                missing_tokens={str(key): value for key, value in missing.items()}, placeholder_count=placeholders,
                claim_id_convention='C0001 = first data row; CSV line = data-row index + 2 (header is line 1)',
                not_rerun={'C': 'H3_OPTION.txt selects B_PRIME; Option C is not adopted', 'R': 'requires Track M ADOPT-CONFIRMED and M6'})
    c.write_json(RESULTS, body, __file__, TASK_INDEX,
                 [c.ROOT / spec_module.LEDGER, spec_module.RESULTS, c.ROOT / D3_RESULTS, c.ROOT / D3_LEDGER])
    print('original sha256:', original_sha)
    print('final B_PRIME:', result_b['rows_retired'], 'retired,', result_b['rows_added'], 'added,', changed, 'changed,',
          result_b['rows_total'], 'total, sha256', result_b['sha256'][:16] + '...')
    print('identical to D3 B_PRIME:', identical)
    print('option A reproduces original:', result_a['sha256'] == original_sha)
    print('placeholders in final text:', placeholders, '| unbound tokens:', sum(len(items) for items in missing.values()))


if __name__ == '__main__':
    main()
