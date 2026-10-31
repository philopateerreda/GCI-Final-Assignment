from pathlib import Path
import os
os.environ['OMP_NUM_THREADS'] = '6'
os.environ['MKL_NUM_THREADS'] = '6'
os.environ['OPENBLAS_NUM_THREADS'] = '6'
import json
import re
import numpy as np
import pandas as pd
from scipy.special import expit, logit
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression
import joblib

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'v2_work'
SEED = 20261028
THREADS = 6
PRIOR = .4956
COLORS = {'ink': '#132D3A', 'teal': '#007F82', 'amber': '#C87E26', 'muted': '#73838B', 'light': '#EDF3F3'}


def dump(name, value):
    def convert(obj):
        if isinstance(obj, dict):
            return {str(k): convert(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [convert(v) for v in obj]
        if isinstance(obj, np.ndarray):
            return convert(obj.tolist())
        if isinstance(obj, np.generic):
            return convert(obj.item())
        if isinstance(obj, float) and not np.isfinite(obj):
            return None
        return obj
    (WORK / name).write_text(json.dumps(convert(value), indent=2, allow_nan=False), encoding='utf-8')


def load_data():
    data = pd.read_csv(ROOT / 'telecom/Record.csv').merge(pd.read_csv(ROOT / 'telecom/Client.csv'), on='Customer_ID', validate='one_to_one')
    split = pd.read_csv(ROOT / 'v1_frozen/analysis_outputs/tables/split_manifest.csv')
    labels = data.Customer_ID.map(split.set_index('Customer_ID').partition)
    partitions = {name: np.flatnonzero(labels.eq(name)) for name in ['train', 'validation', 'calibration_policy', 'test']}
    assert [len(partitions[k]) for k in partitions] == [60000, 15000, 10000, 15000]
    return data, partitions


def operational_features(data, train_idx):
    source = (ROOT / 'v1_frozen/analysis_pipeline.py').read_text(encoding='utf-8')
    section = re.split(r'^# %% Operational features\n', source, flags=re.MULTILINE)[1].split('# %% Model selection')[0]
    section = section.split("save_json('feature_manifest.json'")[0]
    env = {'data': data, 'train_idx': train_idx, 'np': np, 'pd': pd}
    exec(compile(section, 'frozen-operational-features', 'exec'), env)
    return env['X_native'], env['cat_cols']


def values(data, train_idx, column='totmrc_Mean'):
    train = data.iloc[train_idx][column].clip(lower=0)
    median, cap = float(train.median()), float(train.quantile(.99))
    return data[column].clip(lower=0).fillna(median).clip(upper=cap).to_numpy(), {'median': median, 'p99': cap}


def shift(probability, prior=.02, sample_prior=PRIOR):
    return expit(logit(np.clip(probability, 1e-6, 1-1e-6)) + logit(prior) - logit(sample_prior))


def weights(y, prior=.02, population=100000):
    y = np.asarray(y)
    return np.where(y == 1, population * prior / y.sum(), population * (1-prior) / (len(y)-y.sum()))


def cutoff(score, weight, share):
    order = np.argsort(-np.asarray(score), kind='stable')
    cumulative = np.cumsum(np.asarray(weight)[order])
    return float(np.asarray(score)[order[min(np.searchsorted(cumulative, np.sum(weight)*share), len(order)-1)]])


class Calibrator:
    def __init__(self, method='sigmoid'):
        self.method = method

    def transform(self, p):
        p = np.clip(p, 1e-6, 1-1e-6)
        return np.c_[np.log(p), -np.log1p(-p)] if self.method == 'beta' else logit(p).reshape(-1, 1)

    def fit(self, p, y):
        if self.method == 'isotonic':
            self.model = IsotonicRegression(out_of_bounds='clip', y_min=1e-6, y_max=1-1e-6).fit(p, y)
        else:
            self.model = LogisticRegression(C=1000, solver='lbfgs', random_state=SEED, max_iter=1000).fit(self.transform(p), y)
        return self

    def predict(self, p):
        result = self.model.predict(p) if self.method == 'isotonic' else self.model.predict_proba(self.transform(p))[:, 1]
        return np.clip(result, 1e-6, 1-1e-6)


def frozen_predictions(partition='calibration_policy'):
    data, splits = load_data()
    idx = splits[partition]
    X, cats = operational_features(data, splits['train'])
    bundle = joblib.load(ROOT / 'v1_frozen/analysis_outputs/models/selected_model.joblib')
    raw = bundle['model'].predict_proba(X.iloc[idx])[:, 1]
    ps = bundle['calibrator'].predict_proba(logit(np.clip(raw, 1e-6, 1-1e-6)).reshape(-1, 1))[:, 1]
    v, limits = values(data, splits['train'])
    frame = pd.DataFrame({'Customer_ID': data.iloc[idx].Customer_ID.to_numpy(), 'y': data.iloc[idx].churn.to_numpy(), 'p_raw': raw, 'p_s': ps, 'p_d': shift(ps), 'value': v[idx], 'weight': weights(data.iloc[idx].churn.to_numpy()), 'partition': partition})
    return data, splits, frame
