from hashlib import sha256
import json
from pathlib import Path

import pandas as pd
from pptx import Presentation

from claim_checks import json_key, numeric_mentions
from common import ROOT, WORK


def build():
    bindings = json.loads((WORK / 'ledger_bindings.json').read_text(encoding='utf-8'))
    assert all(binding['location'] == 'native' for binding in bindings)
    from chart_inventory import prepare_numeric_sources
    for number in prepare_numeric_sources():
        bindings.append({key: number[key] for key in ('slide_number', 'source_file_or_json_key',
                         'epistemic_type', 'prior_regime', 'formatter', 'unicode_minus')})
        bindings[-1]['location'] = 'chart'
    documents, records = {}, []
    for binding in bindings:
        relative, key = binding['source_file_or_json_key'].split('::', 1)
        if relative not in documents:
            documents[relative] = json.loads((ROOT / relative).read_text(encoding='utf-8'))
        actual = json_key(documents[relative], key)
        scale = binding.get('scale', 1)
        shown = actual * scale if isinstance(actual, (int, float)) and scale != 1 else actual
        displayed = binding['formatter'].format(shown)
        if binding.get('unicode_minus'):
            displayed = displayed.replace('-', '−')
        records.append({**binding, 'displayed_text': displayed,
                        'exact_value': json.dumps(actual, allow_nan=False)})
    frame = pd.DataFrame(records)
    deck = Presentation(ROOT / 'philopateer.pptx')
    omissions = []
    for number, slide in enumerate(deck.slides, 1):
        registered = set(frame.loc[(frame.slide_number == number) & (frame.location == 'native'), 'displayed_text'])
        for shape in slide.shapes:
            if shape.has_text_frame:
                for token in numeric_mentions(shape.text):
                    if token not in registered:
                        omissions.append({'slide': number, 'token': token, 'text': shape.text})
    assert not omissions, omissions
    target = ROOT / 'analysis_outputs/claims_ledger.csv'
    frame.to_csv(target, index=False)
    report = {'rows': len(frame), 'source_files': sorted(documents),
              'ledger_sha256': sha256(target.read_bytes()).hexdigest(),
              'binding_sha256': sha256((WORK / 'ledger_bindings.json').read_bytes()).hexdigest(),
              'native_number_coverage': True,
              'derivation': 'Every displayed quantity is formatted from an explicit independent source binding; no source values are inferred from slide text.'}
    (ROOT / 'analysis_outputs/claims_ledger_build.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report


if __name__ == '__main__':
    print(json.dumps(build(), indent=2))
