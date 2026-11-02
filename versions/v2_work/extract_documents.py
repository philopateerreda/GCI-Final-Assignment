from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'v2_work'
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
for name, target in [('README.docx', 'assessment_requirements.md'), ('ENG_Company _A_ Dataset Overview.docx', 'dataset_overview.txt')]:
    with ZipFile(ROOT / name) as archive:
        tree = ET.fromstring(archive.read('word/document.xml'))
    body = tree.find('w:body', NS)
    lines, rows = [], []
    for element in body:
        if element.tag.endswith('}p'):
            lines.append(''.join(element.itertext()) if False else ''.join(t.text or '' for t in element.findall('.//w:t', NS)))
        elif element.tag.endswith('}tbl'):
            for row in element.findall('w:tr', NS):
                cells = ['\n'.join(''.join(t.text or '' for t in p.findall('.//w:t', NS)) for p in cell.findall('.//w:p', NS)) for cell in row.findall('w:tc', NS)]
                rows.append(cells)
                lines.append(' | '.join(cells))
    (OUT / target).write_text('\n\n'.join(lines), encoding='utf-8')
    (OUT / (target.split('.')[0] + '_tables.json')).write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding='utf-8')
    print(name, ':', len(lines), 'paragraphs/table rows;', len(rows), 'table rows')
