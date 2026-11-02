from pathlib import Path
from hashlib import sha256
import json
import re
import pandas as pd
from pptx import Presentation

NUMBER = re.compile(r'(?<![\w])(?:[+\-−]?\d+(?:,\d{3})*(?:\.\d+)?(?:%|k|MB)?)')


def numeric_mentions(text):
    text=re.sub(r'https?://\S+','',text)
    text=re.sub(r'\[[^\]]+\]','',text)
    return [m.group(0) for m in NUMBER.finditer(text)]


def json_key(document,key):
    current=document
    for part in key.split('.'):
        current=current[int(part)] if isinstance(current,list) else current[part]
    return current


def verify_chart_ledger(ledger, numbers):
    for number in numbers:
        matching = ledger.loc[ledger.slide_number.eq(number['slide_number']) & ledger.location.eq('chart') &
                              ledger.source_file_or_json_key.eq(number['source_file_or_json_key'])]
        assert len(matching) == 1, number['source_file_or_json_key']
        row = matching.iloc[0]
        for key in ('displayed_text', 'formatter', 'epistemic_type', 'prior_regime'):
            assert row[key] == number[key], (number['slide_number'], key, row[key], number[key])
        assert json.loads(row.exact_value) == number['value']
        assert str(row.unicode_minus).lower() == str(number['unicode_minus']).lower()
    return True


def verify_claims(root):
    root=Path(root)
    ledger=pd.read_csv(root/'analysis_outputs/claims_ledger.csv',keep_default_na=False,
                       dtype={'displayed_text':str,'exact_value':str})
    required={'slide_number','displayed_text','exact_value','source_file_or_json_key','epistemic_type','prior_regime'}
    assert required.issubset(ledger.columns)
    assert set(ledger.epistemic_type).issubset({'observed','assumed','simulated'})
    assert set(ledger.prior_regime).issubset({'sample_49.56%','deployment_2.0%','external_context'})
    presentation=Presentation(root/'philopateer.pptx')
    assert len(presentation.slides)<=15
    provenance_checks=[]

    def verify_provenance(value):
        if isinstance(value,dict):
            if 'source_file' in value and 'source_sha256' in value:
                path=root/value['source_file']
                assert sha256(path.read_bytes()).hexdigest()==value['source_sha256'],str(path)
                provenance_checks.append(value['source_file'])
            for child in value.values():
                verify_provenance(child)
        elif isinstance(value,list):
            for child in value:
                verify_provenance(child)

    static=json.loads((root/'v2_work/static_claim_sources.json').read_text(encoding='utf-8'))
    verify_provenance(static)
    sources={}
    for _,row in ledger.iterrows():
        path,key=row.source_file_or_json_key.split('::',1)
        if path not in sources:
            sources[path]=json.loads((root/path).read_text(encoding='utf-8'))
        actual=json_key(sources[path],key)
        recorded=json.loads(row.exact_value)
        assert actual==recorded,(row.slide_number,row.displayed_text,path,key,actual,recorded)
        if row.get('formatter',''):
            scale=float(row.get('scale',1) or 1)
            scaled=actual*scale if isinstance(actual,(int,float)) and scale!=1 else actual
            display=row.formatter.format(scaled)
            if str(row.get('unicode_minus','')).lower()=='true':
                display=display.replace('-','−')
            assert display==row.displayed_text,(display,row.displayed_text)
        if row.get('location','native')=='native':
            slide=presentation.slides[int(row.slide_number)-1]
            text='\n'.join(shape.text for shape in slide.shapes if shape.has_text_frame)
            assert row.displayed_text in text,(row.slide_number,row.displayed_text)
    uncovered=[]
    for number,slide in enumerate(presentation.slides,1):
        registered=set(ledger.loc[ledger.slide_number.eq(number),'displayed_text'])
        for shape in slide.shapes:
            if shape.has_text_frame:
                for mention in numeric_mentions(shape.text):
                    if mention not in registered:
                        uncovered.append({'slide':number,'token':mention,'context':shape.text})
    assert not uncovered,uncovered
    from chart_inventory import prepare_numeric_sources, verify_embedded_images
    chart_numbers=prepare_numeric_sources()
    verify_chart_ledger(ledger, chart_numbers)
    image_checks=verify_embedded_images()
    references=(root/'references.txt').read_text(encoding='utf-8')
    cited=set()
    for slide in presentation.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                cited.update(re.findall(r'\b[SDM]\d+\b',shape.text))
    for citation in cited:
        assert f'[{citation}]' in references,f'Missing reference: {citation}'
    return {'ledger_rows':len(ledger),'all_native_numeric_mentions_covered':True,
            'values_verified_against_source_json':True,'all_chart_numeric_mentions_covered':True,
            'chart_exact_source_bindings_and_regimes_verified':True,
            'new_chart_plotted_coordinates_independently_verified':True,
            'chart_values_and_axis_scales_registered':True,'slide_citations_match_references':True,
            'static_source_provenance_hashes_verified':sorted(set(provenance_checks)),
            **image_checks,'ledger_sha256':sha256((root/'analysis_outputs/claims_ledger.csv').read_bytes()).hexdigest()}
