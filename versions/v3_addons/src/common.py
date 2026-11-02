from pathlib import Path
import csv
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
import sys
import ast
from contextlib import redirect_stdout
from io import StringIO

for variable in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[variable] = '6'

import numpy as np
import pandas as pd
from scipy.special import expit, logit

ROOT = Path(__file__).resolve().parents[2]
ADDONS = ROOT / 'v3_addons'
SEED = 20261028
SAMPLE_PRIOR = .49562
THRESHOLD = 1.711493684172072
PYTHON = Path('C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe')
BRIEF = Path('C:/Users/FGstore/.qoder/tmp/D--progs-IDE-MainProjs-AI-GCI2026-finalA/attachments/3462e263-cc13-4104-9c41-44f49963bbaa/4ec2074d-b034-4447-85ba-967f007db8e9.txt')


def audit_boundary(event, args):
    candidates = []
    if event == 'open':
        path, mode, flags = args
        writing = (mode is not None and any(letter in mode for letter in 'wax+')) or (flags is not None and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
        if writing and not isinstance(path, int):
            candidates.append(path)
    elif event in ('os.mkdir', 'os.remove', 'os.rmdir', 'os.chmod', 'os.utime'):
        candidates.append(args[0])
    elif event in ('os.rename', 'os.link', 'os.symlink'):
        candidates.extend(args[:2])
    for value in candidates:
        path = Path(value).resolve()
        if path != ADDONS and ADDONS not in path.parents:
            raise PermissionError('STOP-4: write outside v3_addons: ' + str(path))


sys.addaudithook(audit_boundary)
assert sys.dont_write_bytecode
assert Path(sys.executable).resolve() == PYTHON.resolve()


def digest(path):
    result = sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def file_info(path):
    path = Path(path)
    return dict(path=path.as_posix(), present=path.is_file(), size=path.stat().st_size if path.is_file() else None, sha256=digest(path) if path.is_file() else None)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def rng(task_index):
    return np.random.default_rng(SEED + task_index)


def verify_runtime():
    output = StringIO()
    with redirect_stdout(output):
        np.show_runtime()
    runtime = ast.parse(output.getvalue(), mode='eval')
    pools = [ast.literal_eval(item) for item in ast.walk(runtime) if isinstance(item, ast.Dict)
             and any(isinstance(key, ast.Constant) and key.value == 'num_threads' for key in item.keys)]
    assert pools and all(1 <= item['num_threads'] <= 6 for item in pools), 'STOP-4: numerical thread cap exceeded or unverified'
    return pools


def provenance(script, task_index, inputs, row_counts=None, created_utc=None):
    dependencies = [Path(module.__file__).resolve() for module in tuple(sys.modules.values())
                    if getattr(module, '__file__', None) and Path(module.__file__).suffix == '.py'
                    and Path(module.__file__).resolve().is_relative_to(ADDONS)]
    paths = sorted({Path(path).resolve() for path in list(inputs) + dependencies})
    return dict(script=Path(script).resolve().as_posix(), script_sha256=digest(script), seed=SEED + task_index,
                python_version=sys.version, input_files=[file_info(path) for path in paths],
                runtime_pools=verify_runtime(), created_utc=created_utc or utc_now(),
                row_counts=row_counts or {}, tags_used=['[E]', '[A]', '[R]'])


def write_json(relative, body, script, task_index, inputs, row_counts=None):
    target = ADDONS / relative
    timestamp = None
    if target.exists():
        timestamp = json.loads(target.read_text(encoding='utf-8')).get('provenance', {}).get('created_utc')
    output = dict(provenance=provenance(script, task_index, inputs, row_counts, timestamp), **body)
    target.write_text(json.dumps(output, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8')
    return output


def outside_snapshot():
    return {path.relative_to(ROOT).as_posix(): dict(bytes=path.stat().st_size, sha256=digest(path))
            for path in sorted(ROOT.rglob('*')) if path.is_file() and ADDONS not in path.parents}


def baseline_inputs():
    return [ROOT / f'v2_work/d_results/oof/baseline_lgbm_r{repeat}_f{fold}.npz' for repeat in range(2) for fold in range(5)]


def source_values(ids):
    result = {}
    with (ROOT / 'telecom/Record.csv').open(encoding='utf-8', newline='') as stream:
        for record in csv.DictReader(stream):
            customer = int(record['Customer_ID'])
            if customer in ids:
                result[customer] = record['totmrc_Mean']
    assert set(result) == ids
    return result


def population():
    split = pd.read_csv(ROOT / 'v1_frozen/analysis_outputs/tables/split_manifest.csv')
    allowed = set(split.loc[split.partition.isin(['train', 'validation']), 'Customer_ID'].astype(int))
    rows = []
    for path in baseline_inputs():
        with np.load(path, allow_pickle=False) as arrays:
            assert set(arrays['Customer_ID'].astype(int)) <= allowed
            rows.append(pd.DataFrame({key: arrays[key] for key in ('Customer_ID', 'y', 'raw')}))
    repeated = pd.concat(rows, ignore_index=True)
    assert len(repeated) == 150000 and repeated.groupby('Customer_ID').size().eq(2).all()
    frame = repeated.groupby('Customer_ID', as_index=False).agg(y=('y', 'first'), raw=('raw', 'mean'))
    assert set(frame.Customer_ID.astype(int)) == allowed
    features = json.loads((ROOT / 'analysis_outputs/feature_manifest.json').read_text(encoding='utf-8'))
    model = json.loads((ROOT / 'analysis_outputs/model_selection.json').read_text(encoding='utf-8'))
    frame['value'] = pd.to_numeric(frame.Customer_ID.map(source_values(allowed)), errors='raise').clip(lower=0).fillna(features['monthly_value_training_median']).clip(upper=features['monthly_value_training_p99_cap'])
    frame['p_s'] = expit(model['calibration_slope'] * logit(np.clip(frame.raw.to_numpy(), 1e-6, 1-1e-6)) + model['calibration_intercept'])
    frame['p_d'] = expit(logit(np.clip(frame.p_s.to_numpy(), 1e-6, 1-1e-6)) + logit(.02) - logit(SAMPLE_PRIOR))
    frame['weight'] = weights(frame.y.to_numpy())
    frame['selected'] = frame.p_d * frame.value >= THRESHOLD
    return frame


def weights(y, prior=.02, population_size=100000):
    y = np.asarray(y)
    return np.where(y == 1, population_size * prior / y.sum(), population_size * (1-prior) / (len(y)-y.sum()))


def stored_constants():
    metrics = json.loads((ROOT / 'v2_work/final_metrics.json').read_text(encoding='utf-8'))
    bayes = metrics['deployment_policies']['bayes']
    return dict(G=bayes['actual_gross'] / .2, K=bayes['contacts'] + 5000,
                contact_mass=bayes['contacts'], net=bayes['net'], g_star=bayes['break_even_success'],
                p0=metrics['pilot_calibration']['spec']['normal_binary_reference']['p0'])
