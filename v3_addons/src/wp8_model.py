"""WP8's single preregistered batch. Importing never seals, fits, or writes.

Use the authorized Python 3.11 interpreter with -B -X utf8 and exactly one of
--seal, --run, --verify. Only --run can fit; there is deliberately no smoke fit.
Historical code is read/hash-bound, never imported or executed.
"""
import common  # Install the unchanged sandbox/runtime guard BEFORE other imports.

import argparse
import csv
from dataclasses import dataclass
from hashlib import sha256
import importlib.metadata
import json
from pathlib import Path
import sys
import warnings
from contextlib import contextmanager

import numpy as np
import pandas as pd
from scipy.special import expit, logit
from scipy.stats import t as student_t
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, train_test_split
from threadpoolctl import threadpool_limits

ROOT, ADDONS, SEED = common.ROOT, common.ADDONS, common.SEED
SCRIPT = Path(__file__).resolve()
TEST_SCRIPT = ADDONS / 'tests/test_wp8.py'
PREREG = ADDONS / 'prereg_wp8.md'
OUT = ADDONS / 'results/wp8'
SUMMARY = ADDONS / 'results/wp8_model.json'
REPORT = ADDONS / 'reports/WP8_report.md'
RECEIPT = OUT / 'prereg_receipt.json'
SNAPSHOT = OUT / 'outside_snapshot.json'
TAU = 1.711493684172072
PRIOR, THREADS, DRAWS = .02, 6, 100000
CANDIDATE = 'wp8_fixed_contrasts'
LGBM_SPEC = dict(n_estimators=385, learning_rate=.03, num_leaves=31,
                 min_child_samples=100, reg_lambda=12, subsample=.85,
                 subsample_freq=1, colsample_bytree=.85, n_jobs=6,
                 random_state=SEED, verbosity=-1, deterministic=True,
                 force_col_wise=True)
SIGMOID_SPEC = dict(C=1000, solver='lbfgs', max_iter=1000, random_state=SEED)
CATEGORICAL = ('new_cell', 'dualband', 'refurb_new', 'hnd_webcap')
RAW_FEATURES = tuple(('rev_Mean mou_Mean totmrc_Mean da_Mean ovrmou_Mean '
    'ovrrev_Mean vceovr_Mean datovr_Mean roam_Mean change_mou change_rev '
    'drop_vce_Mean drop_dat_Mean blck_vce_Mean blck_dat_Mean unan_vce_Mean '
    'unan_dat_Mean plcd_vce_Mean plcd_dat_Mean recv_vce_Mean recv_sms_Mean '
    'comp_vce_Mean comp_dat_Mean custcare_Mean ccrndmou_Mean cc_mou_Mean '
    'inonemin_Mean threeway_Mean mou_cvce_Mean mou_cdat_Mean mou_rvce_Mean '
    'owylis_vce_Mean mouowylisv_Mean iwylis_vce_Mean mouiwylisv_Mean '
    'peak_vce_Mean peak_dat_Mean mou_peav_Mean mou_pead_Mean opk_vce_Mean '
    'opk_dat_Mean mou_opkv_Mean mou_opkd_Mean drop_blk_Mean attempt_Mean '
    'complete_Mean callfwdv_Mean callwait_Mean months uniqsubs actvsubs new_cell '
    'totcalls totmou totrev adjrev adjmou adjqty avgrev avgmou avgqty avg3mou '
    'avg3qty avg3rev avg6mou avg6qty avg6rev dualband refurb_new hnd_price '
    'phones models hnd_webcap eqpdays').split())
RAW_NUMERIC = tuple(c for c in RAW_FEATURES if c not in CATEGORICAL)
FROZEN_ADDED = tuple(('equipment_age_invalid usage_recent_to_lifetime '
    'usage_three_to_six_months revenue_recent_to_lifetime revenue_three_to_six_months '
    'overage_charge_share recurring_charge_share failed_call_index '
    'care_calls_per_100_attempts equipment_age_to_tenure inactive_household_lines '
    'usage_change_scaled revenue_change_scaled').split())
# There are 74 raw fields and 13 frozen transformations, including invalid age.
FROZEN_FEATURES = RAW_FEATURES + FROZEN_ADDED
NEW_FEATURES = (
    'wp8_mou_3_6_contrast', 'wp8_mou_mean_3_contrast',
    'wp8_mou_contrast_difference', 'wp8_mou_log_curvature',
    'wp8_rev_3_6_contrast', 'wp8_rev_mean_3_contrast',
    'wp8_rev_contrast_difference', 'wp8_rev_log_curvature',
    'wp8_qty_3_6_contrast', 'wp8_qty_3_lifetime_contrast', 'wp8_qty_log_3_6',
    'wp8_tenure_equipment_gap', 'wp8_price_per_month', 'wp8_phones_per_month',
    'wp8_models_per_phone', 'wp8_days_per_model',
    'wp8_price_tenure_peer_ratio', 'wp8_days_tenure_peer_ratio',
    'wp8_recurring_usage_peer_ratio',
    'wp8_missing_total', 'wp8_missing_recent_history', 'wp8_missing_billing',
    'wp8_missing_care', 'wp8_missing_equipment', 'wp8_missing_tenure_lines',
    'wp8_missing_calls_usage')
FEATURES = FROZEN_FEATURES + NEW_FEATURES
FAMILY_NAMES = ('recent_history', 'billing', 'care', 'equipment', 'tenure_lines', 'calls_usage')
METRICS = ('auc', 'value_capture', 'contact_share', 'baseline_tail_brier',
           'baseline_tail_logloss', 'own_tail_brier', 'own_tail_logloss',
           'sample_brier', 'sample_logloss', 'deployment_brier',
           'deployment_logloss', 'calibrated_auc', 'raw_contacts')
TAIL_METRICS = METRICS[3:7]
NA_TOKENS = frozenset(('', '#N/A', '#N/A N/A', '#NA', '-1.#IND', '-1.#QNAN',
    '-NaN', '-nan', '1.#IND', '1.#QNAN', '<NA>', 'N/A', 'NA', 'NULL', 'NaN',
    'None', 'n/a', 'nan', 'null'))
BASE_RECIPE = dict(backend='lgbm', groups=[], drop=[], sensitive=False, value_weighted=False)


def require(condition, message):
    if not condition:
        raise RuntimeError('WP8 STOP: ' + message)


def clean(value):
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [clean(v) for v in value]
    if isinstance(value, np.ndarray):
        return clean(value.tolist())
    if isinstance(value, np.generic):
        return clean(value.item())
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def signature_hash(body):
    return sha256(json.dumps(clean(body), sort_keys=True, separators=(',', ':'),
                             allow_nan=False).encode('utf-8')).hexdigest()


def indices_hash(indices):
    return sha256(np.asarray(indices, dtype='<i8').tobytes()).hexdigest()


def float_hash(values):
    return sha256(np.asarray(values, dtype='<f8').tobytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def arrays_at(path):
    with np.load(path, allow_pickle=False) as archive:
        return {name: archive[name].copy() for name in archive.files}


def result_json(path, body, inputs, counts=None):
    path = Path(path).resolve()
    require(path.is_relative_to(ADDONS / 'results'), 'JSON output outside results')
    require(not path.exists(), 'refusing to overwrite JSON ' + str(path))
    return common.write_json(path.relative_to(ADDONS).as_posix(), clean(body), SCRIPT,
                             8, inputs, counts or {})


def save_npz(path, arrays):
    require(Path(path).resolve().is_relative_to(OUT), 'NPZ output outside WP8')
    with Path(path).open('xb') as stream:
        np.savez_compressed(stream, **arrays)


def missingness_families():
    families = {
        'recent_history': tuple(c for c in RAW_NUMERIC if c.startswith(('avg3', 'avg6'))
                                or c in ('change_mou', 'change_rev')),
        'billing': tuple(('rev_Mean totmrc_Mean da_Mean ovrrev_Mean vceovr_Mean '
                          'datovr_Mean roam_Mean totrev adjrev avgrev').split()),
        'care': ('custcare_Mean', 'ccrndmou_Mean', 'cc_mou_Mean'),
        'equipment': ('hnd_price', 'phones', 'models', 'eqpdays'),
        'tenure_lines': ('months', 'uniqsubs', 'actvsubs')}
    assigned = [c for columns in families.values() for c in columns]
    families['calls_usage'] = tuple(c for c in RAW_NUMERIC if c not in assigned)
    flattened = [c for columns in families.values() for c in columns]
    require(len(flattened) == len(set(flattened)) == len(RAW_NUMERIC)
            and set(flattened) == set(RAW_NUMERIC), 'missingness families do not partition raw numeric fields')
    return families


def source_header(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        header = csv.DictReader(stream).fieldnames
    require(header is not None and len(header) == len(set(header)), 'invalid CSV header')
    require('Customer_ID' in header, 'missing pairing ID')
    return header


def filtered_source(path, allowed, columns):
    """No numeric conversion, including target conversion, before the ID filter."""
    rows, order = {}, []
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        require(set(columns) <= set(reader.fieldnames or []), 'missing allowed source column')
        for row in reader:
            customer = int(row['Customer_ID'])  # ID only, never a predictor.
            if customer not in allowed:
                continue
            require(customer not in rows, 'duplicate allowed customer')
            rows[customer] = {column: row[column] for column in columns}
            order.append(customer)
    require(set(rows) == set(allowed), 'source/split pairing incomplete')
    return rows, order


def allowed_partitions(path):
    partitions = {}
    counts = dict(train=0, validation=0, calibration_policy=0, test=0)
    seen = set()
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        for row in csv.DictReader(stream):
            customer, partition = int(row['Customer_ID']), row['partition']
            require(customer not in seen and partition in counts, 'invalid split manifest')
            seen.add(customer)
            counts[partition] += 1
            if partition in ('train', 'validation'):
                partitions[customer] = partition
    require(counts == dict(train=60000, validation=15000, calibration_policy=10000, test=15000),
            'original split sizes changed')
    return partitions


@dataclass
class Pool:
    raw: pd.DataFrame
    ids: np.ndarray
    y: np.ndarray


def ordered_pool_ids(record_order, partitions):
    return np.array([c for name in ('train', 'validation') for c in record_order
                     if partitions[c] == name], dtype=np.int64)


def load_pool():
    partitions = allowed_partitions(ROOT / 'v1_frozen/analysis_outputs/tables/split_manifest.csv')
    record_path, client_path = ROOT / 'telecom/Record.csv', ROOT / 'telecom/Client.csv'
    record_header, client_header = source_header(record_path), source_header(client_path)
    record_columns = [c for c in record_header if c in RAW_FEATURES]
    client_columns = [c for c in client_header if c in RAW_FEATURES]
    require(tuple(record_columns + client_columns) == RAW_FEATURES, 'raw header/order differs from frozen manifest')
    require('churn' in record_header and 'churn' not in client_columns, 'target location changed')
    record, record_order = filtered_source(record_path, partitions, record_columns + ['churn'])
    client, _ = filtered_source(client_path, partitions, client_columns)
    # This reproduces D's pool_index, NOT shuffled manifest or Customer_ID order.
    ids = ordered_pool_ids(record_order, partitions)
    records = [{**record[int(c)], **client[int(c)]} for c in ids]
    frame = pd.DataFrame.from_records(records, columns=list(RAW_FEATURES) + ['churn'])
    for column in RAW_NUMERIC + ('churn',):
        frame[column] = pd.to_numeric(frame[column].mask(frame[column].isin(NA_TOKENS)), errors='raise').astype('float64')
    for column in CATEGORICAL:
        frame[column] = frame[column].mask(frame[column].isin(NA_TOKENS)).fillna('__MISSING__').astype(str)
    require(frame.churn.notna().all() and set(frame.churn.unique()) == {0, 1}, 'invalid allowed targets')
    require(len(ids) == len(set(ids)) == 75000, 'pool count changed')
    return Pool(frame.loc[:, RAW_FEATURES].copy(), ids, frame.churn.to_numpy(dtype=np.int64))


def frozen_features(raw):
    """Literal equivalents of frozen lines 193-211; excluded fields are never needed."""
    X = raw.loc[:, RAW_FEATURES].copy()
    X['equipment_age_invalid'] = (X.eqpdays < 0).astype('int8')
    X['eqpdays'] = X.eqpdays.where(X.eqpdays >= 0)
    X['usage_recent_to_lifetime'] = X.avg3mou / X.avgmou.clip(lower=1)
    X['usage_three_to_six_months'] = X.avg3mou / X.avg6mou.clip(lower=1)
    X['revenue_recent_to_lifetime'] = X.avg3rev / X.avgrev.clip(lower=1)
    X['revenue_three_to_six_months'] = X.avg3rev / X.avg6rev.clip(lower=1)
    X['overage_charge_share'] = X.ovrrev_Mean / X.rev_Mean.clip(lower=1)
    X['recurring_charge_share'] = X.totmrc_Mean / X.rev_Mean.clip(lower=1)
    X['failed_call_index'] = X.drop_blk_Mean / X.attempt_Mean.clip(lower=1)
    X['care_calls_per_100_attempts'] = 100 * X.custcare_Mean / X.attempt_Mean.clip(lower=1)
    X['equipment_age_to_tenure'] = X.eqpdays / (30.4375 * X.months.clip(lower=1))
    X['inactive_household_lines'] = (X.uniqsubs - X.actvsubs).clip(lower=0)
    X['usage_change_scaled'] = X.change_mou / X.avg3mou.clip(lower=1)
    X['revenue_change_scaled'] = X.change_rev / X.avg3rev.clip(lower=1)
    for column in CATEGORICAL:
        X[column] = X[column].fillna('__MISSING__').astype(str)
    numeric = [c for c in X if c not in CATEGORICAL]
    X[numeric] = X[numeric].replace([np.inf, -np.inf], np.nan).astype('float32')
    require(tuple(X.columns) == FROZEN_FEATURES and len(X.columns) == 87, 'frozen feature mismatch')
    return X


def peer_table(grouping, numerator):
    grouping = np.asarray(grouping, dtype=float)
    numerator = np.asarray(numerator, dtype=float)
    valid_group = grouping[np.isfinite(grouping)]
    fill = float(np.median(valid_group)) if len(valid_group) else 0.0
    edges = np.unique(np.quantile(valid_group, np.arange(.1, 1, .1), method='linear')) if len(valid_group) else np.array([])
    bins = np.searchsorted(edges, np.where(np.isfinite(grouping), grouping, fill), side='right')
    valid_price = numerator[np.isfinite(numerator)]
    fallback = float(np.median(valid_price)) if len(valid_price) else 0.0
    medians = {str(int(group)): float(np.median(numerator[(bins == group) & np.isfinite(numerator)]))
               for group in np.unique(bins) if np.any((bins == group) & np.isfinite(numerator))}
    return dict(edges=edges.tolist(), missing_group_median=fill,
                group_medians=medians, global_fallback_median=fallback,
                training_n=len(grouping), quantile_method='linear', bin_side='right')


def peer_ratio(grouping, numerator, table):
    grouping = np.asarray(grouping, dtype=float)
    bins = np.searchsorted(table['edges'], np.where(np.isfinite(grouping), grouping,
                           table['missing_group_median']), side='right')
    denominator = np.array([table['group_medians'].get(str(int(b)), table['global_fallback_median']) for b in bins])
    return np.asarray(numerator, dtype=float) / np.maximum(denominator, 1)


def fit_reference(raw):
    """Accept fitting rows only; this function has no labels or scored-batch input."""
    days = raw.eqpdays.where(raw.eqpdays >= 0)
    return dict(training_n=len(raw),
        category_vocabularies={c: sorted(raw[c].fillna('__MISSING__').astype(str).unique().tolist()) for c in CATEGORICAL},
        peers=dict(price_tenure=peer_table(raw.months, raw.hnd_price),
                   days_tenure=peer_table(raw.months, days),
                   recurring_usage=peer_table(raw.avg3mou, raw.totmrc_Mean.clip(lower=0))))


def contrasts(a, b):
    return (a - b) / (a.abs() + b.abs() + 1)


def transform_features(raw, reference):
    """Scoring is row-local. Only the previously fitted reference supplies statistics."""
    X = frozen_features(raw)
    additions = {}
    for kind in ('mou', 'rev'):
        mean, recent, six = raw[kind + '_Mean'], raw['avg3' + kind], raw['avg6' + kind]
        first, second = contrasts(recent, six), contrasts(mean, recent)
        additions['wp8_' + kind + '_3_6_contrast'] = first
        additions['wp8_' + kind + '_mean_3_contrast'] = second
        additions['wp8_' + kind + '_contrast_difference'] = second - first
        additions['wp8_' + kind + '_log_curvature'] = (np.log1p(mean.clip(lower=0))
            - 2 * np.log1p(recent.clip(lower=0)) + np.log1p(six.clip(lower=0)))
    additions['wp8_qty_3_6_contrast'] = contrasts(raw.avg3qty, raw.avg6qty)
    additions['wp8_qty_3_lifetime_contrast'] = contrasts(raw.avg3qty, raw.avgqty)
    additions['wp8_qty_log_3_6'] = np.log1p(raw.avg3qty.clip(lower=0)) - np.log1p(raw.avg6qty.clip(lower=0))
    days, months, phones, models = raw.eqpdays.where(raw.eqpdays >= 0), raw.months.clip(lower=1), raw.phones.clip(lower=1), raw.models.clip(lower=1)
    additions['wp8_tenure_equipment_gap'] = (30.4375 * raw.months - days) / (30.4375 * months)
    additions['wp8_price_per_month'] = raw.hnd_price / months
    additions['wp8_phones_per_month'] = raw.phones / months
    additions['wp8_models_per_phone'] = raw.models / phones
    additions['wp8_days_per_model'] = days / models
    additions['wp8_price_tenure_peer_ratio'] = peer_ratio(raw.months, raw.hnd_price, reference['peers']['price_tenure'])
    additions['wp8_days_tenure_peer_ratio'] = peer_ratio(raw.months, days, reference['peers']['days_tenure'])
    additions['wp8_recurring_usage_peer_ratio'] = peer_ratio(raw.avg3mou, raw.totmrc_Mean.clip(lower=0), reference['peers']['recurring_usage'])
    missing = raw.loc[:, RAW_NUMERIC].replace([np.inf, -np.inf], np.nan).copy()
    missing['eqpdays'] = missing.eqpdays.where(missing.eqpdays >= 0)
    additions['wp8_missing_total'] = missing.isna().sum(axis=1)
    for family, columns in missingness_families().items():
        additions['wp8_missing_' + family] = missing.loc[:, columns].isna().sum(axis=1)
    require(tuple(additions) == NEW_FEATURES, 'new feature order mismatch')
    extra = pd.DataFrame(additions, index=raw.index).replace([np.inf, -np.inf], np.nan).astype('float32')
    X = pd.concat([X, extra], axis=1)
    for column in CATEGORICAL:
        vocabulary = reference['category_vocabularies'][column]
        X[column] = pd.Categorical(X[column].where(X[column].isin(vocabulary)), categories=vocabulary)
    require(tuple(X.columns) == FEATURES and len(X.columns) == 113, 'fixed bundle mismatch')
    return X


@dataclass
class Fold:
    repeat: int
    number: int
    train: np.ndarray
    test: np.ndarray
    development: np.ndarray
    calibration: np.ndarray

    @property
    def tag(self):
        return f'r{self.repeat}_f{self.number}'


def outer_folds(y):
    folds = []
    for repeat in range(2):
        splitter = StratifiedKFold(5, shuffle=True, random_state=SEED + repeat)
        for number, (train, test) in enumerate(splitter.split(np.zeros(len(y)), y)):
            dev, cal = train_test_split(train, test_size=.20, stratify=y[train],
                                       random_state=SEED + 1000 + 5 * repeat + number)
            folds.append(Fold(repeat, number, np.sort(train), np.sort(test), np.sort(dev), np.sort(cal)))
    return folds


def inner_folds(fold, y):
    splitter = StratifiedKFold(3, shuffle=True, random_state=SEED)
    return [(fold.development[tr], fold.development[te]) for tr, te in
            splitter.split(np.zeros(len(fold.development)), y[fold.development])]


def value_limits(raw_training):
    values = raw_training.totmrc_Mean.clip(lower=0)
    result = dict(median=float(values.median()), p99=float(values.quantile(.99)))
    require(all(np.isfinite(v) for v in result.values()), 'invalid training-only V limits')
    return result


def values(raw, limits):
    result = raw.totmrc_Mean.clip(lower=0).fillna(limits['median']).clip(upper=limits['p99']).to_numpy(dtype=float)
    require(np.isfinite(result).all() and (result >= 0).all(), 'invalid fold-local V')
    return result


def deployment_weights(y):
    y = np.asarray(y)
    positive = np.count_nonzero(y == 1)
    negative = np.count_nonzero(y == 0)
    require(positive > 0 and negative > 0 and positive + negative == len(y), 'weights need both binary classes')
    return np.where(y == 1, len(y) * PRIOR / positive, len(y) * (1 - PRIOR) / negative)


def sigmoid_probability(raw, slope, intercept):
    return np.clip(expit(slope * logit(np.clip(raw, 1e-6, 1 - 1e-6)) + intercept), 1e-6, 1 - 1e-6)


def shift_probability(p_s, sample_prior):
    return expit(logit(np.clip(p_s, 1e-6, 1 - 1e-6)) + logit(PRIOR) - logit(sample_prior))


def weighted_losses(y, probability, weight, mask):
    if not np.any(mask) or np.sum(weight[mask]) <= 0:
        return float('nan'), float('nan')
    p, target, w = np.clip(probability[mask], 1e-6, 1 - 1e-6), y[mask], weight[mask]
    return (float(np.average((target - p) ** 2, weights=w)),
            float(np.average(-(target * np.log(p) + (1 - target) * np.log1p(-p)), weights=w)))


def measure(y, raw, p_s, p_d, V, baseline_tail):
    y, raw, p_s, p_d, V = map(np.asarray, (y, raw, p_s, p_d, V))
    w = deployment_weights(y)
    own = p_d * V >= TAU
    brier_shared, loss_shared = weighted_losses(y, p_d, w, baseline_tail)
    brier_own, loss_own = weighted_losses(y, p_d, w, own)
    all_rows = np.ones(len(y), dtype=bool)
    sample_brier, sample_loss = weighted_losses(y, p_s, np.ones(len(y)), all_rows)
    dep_brier, dep_loss = weighted_losses(y, p_d, w, all_rows)
    churn_value = w * y * V
    capture = float(churn_value[own].sum() / churn_value.sum()) if churn_value.sum() > 0 else float('nan')
    return dict(auc=float(roc_auc_score(y, raw)), value_capture=capture,
                contact_share=float(w[own].sum() / w.sum()),
                baseline_tail_brier=brier_shared, baseline_tail_logloss=loss_shared,
                own_tail_brier=brier_own, own_tail_logloss=loss_own,
                sample_brier=sample_brier, sample_logloss=sample_loss,
                deployment_brier=dep_brier, deployment_logloss=dep_loss,
                calibrated_auc=float(roc_auc_score(y, p_s)), raw_contacts=int(own.sum()))


def bootstrap(differences, draws=DRAWS):
    """Joint paired resampling, hierarchical first then IID, with one task-8 RNG."""
    differences = np.asarray(differences, dtype=float)
    require(differences.ndim == 2 and differences.shape[0] == 10, 'bootstrap requires ten ordered folds')
    rng = np.random.default_rng(SEED + 8)
    repetitions = rng.integers(0, 2, size=(draws, 2))
    within = rng.integers(0, 5, size=(draws, 2, 5))
    hierarchical_indices = (repetitions[:, :, None] * 5 + within).reshape(draws, 10).astype('int8')
    iid_indices = rng.integers(0, 10, size=(draws, 10)).astype('int8')
    # Bounded transient allocation; columns always travel together.
    hierarchical = np.empty((draws, differences.shape[1]), dtype=float)
    iid = np.empty_like(hierarchical)
    for start in range(0, draws, 2000):
        stop = min(start + 2000, draws)
        hierarchical[start:stop] = differences[hierarchical_indices[start:stop]].mean(axis=1)
        iid[start:stop] = differences[iid_indices[start:stop]].mean(axis=1)
    return dict(hierarchical=hierarchical, iid=iid,
                hierarchical_indices=hierarchical_indices, iid_indices=iid_indices,
                differences=differences)


def interval_summary(differences, samples, names=METRICS):
    result = {}
    for column, name in enumerate(names):
        vector = np.asarray(differences)[:, column]
        if not np.isfinite(vector).all():
            result[name] = dict(complete=False, mean=None, iid=None, hierarchical=None,
                                corrected_t=None, conservative=None, corrected_se=None, df=4)
            continue
        mean = float(vector.mean())
        se = float(np.sqrt((.1 + .25) * np.var(vector, ddof=1)))
        margin = float(student_t.ppf(.975, 4) * se)
        corrected = [mean - margin, mean + margin]
        hierarchy = np.percentile(samples['hierarchical'][:, column], [2.5, 97.5], method='linear').tolist()
        iid = np.percentile(samples['iid'][:, column], [2.5, 97.5], method='linear').tolist()
        result[name] = dict(complete=True, mean=mean, iid=iid, hierarchical=hierarchy,
            corrected_t=corrected, conservative=[min(hierarchy[0], corrected[0]), max(hierarchy[1], corrected[1])],
            corrected_se=se, df=4)
    return result


def promotion_gates(intervals, complete, converged, protected=True):
    def available(name):
        item = intervals.get(name, {})
        return bool(item.get('complete') and item.get('conservative') is not None
                    and np.isfinite(item['conservative']).all() and np.isfinite(item['mean']))
    gates = dict(ten_complete_finite_id_matched_folds=bool(complete),
                 all_classifier_and_sigmoid_fits_converged=bool(converged),
                 protected_fingerprints_and_outside_boundary_unchanged=bool(protected))
    auc, capture = intervals.get('auc', {}), intervals.get('value_capture', {})
    gates['mean_delta_auc_ge_0_003'] = available('auc') and auc['mean'] >= .003
    gates['conservative_auc_lower_gt_0'] = available('auc') and auc['conservative'][0] > 0
    gates['mean_fixed_tau_value_capture_gain_gt_0'] = available('value_capture') and capture['mean'] > 0
    gates['conservative_value_capture_lower_gt_0'] = available('value_capture') and capture['conservative'][0] > 0
    for name in TAIL_METRICS:
        gates[name + '_conservative_upper_le_0'] = available(name) and intervals[name]['conservative'][1] <= 0
    gates = {key: bool(value) for key, value in gates.items()}
    return dict(gates=gates, failed_gates=[key for key, passed in gates.items() if not passed],
                passed=all(gates.values()))


def outside_diff(before, after):
    return dict(files_before=len(before), files_after=len(after),
                added_outside=sorted(after.keys() - before.keys()),
                removed_outside=sorted(before.keys() - after.keys()),
                changed_outside=sorted(k for k in before.keys() & after.keys() if before[k] != after[k]),
                passed=before == after)


def verify_baseline_pair(pool, fold, arrays, metric, recipe):
    required = ('Customer_ID', 'y', 'pool_index', 'raw', 'p_s', 'p_d', 'value',
                'deployment_weight', 'own_tail', 'baseline_tail')
    require(set(required) <= set(arrays), 'missing baseline OOF arrays')
    require(all(np.asarray(arrays[k]).shape == (15000,) for k in required), 'baseline fold length')
    for key, expected in (('Customer_ID', pool.ids[fold.test]), ('y', pool.y[fold.test]), ('pool_index', fold.test)):
        require(np.array_equal(arrays[key], expected), 'baseline ' + key + ' mismatch ' + fold.tag)
    for key in ('raw', 'p_s', 'p_d'):
        require(np.isfinite(arrays[key]).all() and ((arrays[key] >= 0) & (arrays[key] <= 1)).all(), 'invalid baseline probability')
    limits = value_limits(pool.raw.iloc[fold.train])
    require(limits == recipe['outer_training_value_limits'], 'baseline outer V limits mismatch')
    require(value_limits(pool.raw.iloc[fold.development]) == recipe['development_value_limits'], 'baseline development V limits mismatch')
    require(np.array_equal(arrays['value'], values(pool.raw.iloc[fold.test], limits)), 'baseline fold-local V mismatch')
    require(np.array_equal(arrays['deployment_weight'], deployment_weights(pool.y[fold.test])), 'baseline weights mismatch')
    require(float(pool.y[fold.calibration].mean()) == metric['sample_prior'], 'baseline calibration prior mismatch')
    ps = sigmoid_probability(arrays['raw'], metric['calibration_slope'], metric['calibration_intercept'])
    require(np.allclose(ps, arrays['p_s'], rtol=0, atol=2e-15), 'baseline sigmoid pairing mismatch')
    require(np.allclose(shift_probability(arrays['p_s'], metric['sample_prior']), arrays['p_d'], rtol=0, atol=2e-15), 'baseline prior shift mismatch')
    historical_tail = arrays['p_d'] * arrays['value'] >= metric['threshold']
    require(np.array_equal(arrays['own_tail'], historical_tail)
            and np.array_equal(arrays['baseline_tail'], historical_tail), 'historical baseline tail mismatch')
    require(abs(roc_auc_score(arrays['y'], arrays['raw']) - metric['auc']) < 1e-14, 'baseline AUC metadata mismatch')
    require(recipe['recipe'] == BASE_RECIPE, 'ineligible outer baseline recipe')


@dataclass
class Context:
    pool: Pool
    folds: list
    baseline_outer: dict
    baseline_inner: dict
    baseline_metrics: dict
    input_paths: list
    signature: dict

    @property
    def binding(self):
        return signature_hash(self.signature)


def verify_historical_source_identity():
    recorded = read_json(ROOT / 'v1_frozen/analysis_outputs/audit.json')['source_sha256']
    expected = {name.replace('\\', '/'): digest for name, digest in recorded.items()}
    require(set(expected) == {'telecom/Client.csv', 'telecom/Record.csv'}, 'historical CSV hash evidence incomplete')
    for name, digest in expected.items():
        require(common.digest(ROOT / name) == digest, 'historical CSV predictor identity mismatch: ' + name)
    return expected


def build_context():
    common.verify_runtime()
    historical_source_sha256 = verify_historical_source_identity()
    manifest_path = ROOT / 'analysis_outputs/feature_manifest.json'
    manifest = read_json(manifest_path)
    require(manifest['features'] == list(FROZEN_FEATURES)
            and manifest['categorical_features'] == list(CATEGORICAL)
            and manifest['feature_count'] == 87, 'exact frozen manifest mismatch')
    require(not set(manifest['excluded_features']) & set(FEATURES), 'excluded feature leaked')
    frozen_manifest = ROOT / 'v1_frozen/analysis_outputs/feature_manifest.json'
    require(read_json(frozen_manifest) == manifest, 'frozen/current feature manifest divergence')
    versions = {name: importlib.metadata.version(name) for name in
                ('numpy', 'pandas', 'scipy', 'scikit-learn', 'lightgbm', 'threadpoolctl')}
    sources = [PREREG, SCRIPT, TEST_SCRIPT, Path(common.__file__).resolve(),
               ROOT / 'telecom/Record.csv', ROOT / 'telecom/Client.csv', manifest_path,
               frozen_manifest, ROOT / 'v1_frozen/analysis_outputs/tables/split_manifest.csv',
               ROOT / 'v1_frozen/analysis_pipeline.py', ROOT / 'v2_work/common.py',
               ROOT / 'v2_work/workstream_d.py', ROOT / 'v2_work/d_results/run_spec.json',
               ROOT / 'v1_frozen/analysis_outputs/model_selection.json',
               ROOT / 'v1_frozen/analysis_outputs/audit.json',
               ROOT / 'v2_work/d_results/baseline_folds.json']
    run_spec = read_json(ROOT / 'v2_work/d_results/run_spec.json')
    require(run_spec['smoke'] is False and run_spec['input_rows'] == 75000
            and run_spec['model_specs']['lgbm'] == LGBM_SPEC, 'baseline runtime specification mismatch')
    require(all(run_spec['versions'][k] == v for k, v in versions.items()), 'baseline/library version mismatch')
    for name, expected in run_spec['source_hashes'].items():
        require(common.digest(Path(name)) == expected, 'historical baseline source hash mismatch: ' + name)
    pool = load_pool()
    folds = outer_folds(pool.y)
    metric_rows = read_json(ROOT / 'v2_work/d_results/baseline_folds.json')
    require(len(metric_rows) == 10, 'baseline metrics count')
    metrics = {(row['repeat'], row['fold']): row for row in metric_rows}
    require(len(metrics) == 10, 'duplicate baseline fold metadata')
    baseline_outer = {}
    for fold in folds:
        path = ROOT / f'v2_work/d_results/oof/baseline_lgbm_{fold.tag}.npz'
        recipe_path = ROOT / f'v2_work/d_results/folds/baseline_lgbm_{fold.tag}_recipe.json'
        arrays = arrays_at(path)
        verify_baseline_pair(pool, fold, arrays, metrics[(fold.repeat, fold.number)], read_json(recipe_path))
        baseline_outer[fold.tag] = arrays
        sources.extend((path, recipe_path))
    # Discover metadata FIRST; arbitrary raw caches are not candidates for reuse.
    eligible = {}
    for metadata_path in sorted((ROOT / 'v2_work/d_results/cache').glob('*.json')):
        metadata = read_json(metadata_path)
        tag = metadata.get('first_tag', '')
        if tag.startswith('screen/') and '/baseline/i' in tag:
            require(tag not in eligible, 'duplicate baseline inner tag')
            eligible[tag] = (metadata_path, metadata)
    expected_tags = {f'screen/{fold.tag}/baseline/i{i}' for fold in folds for i in range(3)}
    require(set(eligible) == expected_tags and len(eligible) == 30, 'exactly 30 eligible baseline inner caches required')
    baseline_inner = {}
    for fold in folds:
        for i, (train, predict) in enumerate(inner_folds(fold, pool.y)):
            tag = f'screen/{fold.tag}/baseline/i{i}'
            path, metadata = eligible[tag]
            signature = dict(recipe=BASE_RECIPE, train_hash=indices_hash(train),
                             predict_hash=indices_hash(predict), specification=LGBM_SPEC,
                             want_training=False, resubstitution=False)
            require(metadata['signature'] == signature, 'baseline inner train/predict/recipe signature mismatch')
            old_key = sha256(json.dumps(signature, sort_keys=True).encode()).hexdigest()
            require(path.stem == old_key, 'baseline cache key mismatch')
            require(metadata['base_features'] == list(FROZEN_FEATURES)
                    and metadata['features'] == list(FROZEN_FEATURES)
                    and metadata['categorical_features'] == list(CATEGORICAL), 'baseline inner feature signature mismatch')
            require(metadata['fit_n'] == len(train) and metadata['predict_n'] == len(predict), 'baseline inner sizes mismatch')
            require(metadata['category_vocabularies'] == fit_reference(pool.raw.iloc[train])['category_vocabularies'], 'baseline categories not fit-local')
            prediction_path = path.with_suffix('.npz')
            raw = arrays_at(prediction_path)['raw']
            require(raw.shape == (16000,) and np.isfinite(raw).all()
                    and ((raw >= 0) & (raw <= 1)).all(), 'invalid baseline inner raw cache')
            baseline_inner[f'{fold.tag}_i{i}'] = dict(raw=raw, metadata=metadata,
                metadata_path=path, prediction_path=prediction_path)
            sources.extend((path, prediction_path))
    protected_paths = [ROOT / name for name in ('philopateer.ipynb', 'philopateer.pdf',
        'philopateer.pptx', 'references.txt', 'v2_work/final_protocol.py', 'v2_work/final_metrics.json',
        'v1_frozen/analysis_outputs/models/selected_model.joblib')]
    protected_paths += [ADDONS / 'results/wp7_final_verification.json', ADDONS / 'results/wp7_files_created.csv']
    sources.extend(protected_paths)
    sources = sorted(set(p.resolve() for p in sources))
    require(all(p.is_file() for p in sources), 'required source/protected file missing')
    signature = dict(schema=1, candidate=CANDIDATE, prereg_sha256=common.digest(PREREG),
        script_sha256=common.digest(SCRIPT), tests_sha256=common.digest(TEST_SCRIPT),
        python=sys.version, interpreter=Path(sys.executable).resolve().as_posix(), versions=versions,
        input_files=[common.file_info(path) for path in sources],
        historical_source_sha256=historical_source_sha256,
        protected_fingerprints=[common.file_info(path) for path in protected_paths],
        pool_ids_sha256=indices_hash(pool.ids), pool_y_sha256=indices_hash(pool.y),
        raw_numeric_sha256=float_hash(pool.raw.loc[:, RAW_NUMERIC].to_numpy()),
        features=list(FEATURES), categorical_features=list(CATEGORICAL),
        missingness_families=clean(missingness_families()), classifier_parameters=LGBM_SPEC,
        sigmoid_parameters=SIGMOID_SPEC, tau=TAU, deployment_prior=PRIOR,
        seed=SEED, bootstrap_seed=SEED + 8, bootstrap_draws_each=DRAWS,
        classifier_fits=50, sigmoid_fits=10, baseline_refits=0,
        fold_indices=[dict(tag=f.tag, train=indices_hash(f.train), test=indices_hash(f.test),
                          development=indices_hash(f.development), calibration=indices_hash(f.calibration)) for f in folds])
    return Context(pool, folds, baseline_outer, baseline_inner, metrics, sources, signature)


def read_receipt(context, check_outside=True):
    require(RECEIPT.is_file() and SNAPSHOT.is_file(), '--seal is required before --run/--verify')
    receipt, snapshot = read_json(RECEIPT), read_json(SNAPSHOT)
    require(receipt['signature'] == context.signature and receipt['signature_sha256'] == context.binding,
            'immutable preregistration/code/data/source/version receipt mismatch')
    require(receipt['outside_snapshot_sha256'] == common.digest(SNAPSHOT), 'outside snapshot hash mismatch')
    require('provenance' in receipt and 'provenance' in snapshot, 'receipt/snapshot lacks provenance')
    require(receipt['status'] == 'SEALED_NO_FITS' and receipt['fits_performed'] == 0
            and receipt['planned_classifier_fits'] == 50 and receipt['planned_sigmoid_fits'] == 10, 'invalid pre-fit receipt')
    check_provenance(receipt, RECEIPT)
    check_provenance(snapshot, SNAPSHOT)
    if check_outside:
        require(snapshot['files'] == common.outside_snapshot(), 'outside-sandbox fingerprint changed since seal')
    return receipt


def seal():
    context = build_context()
    if RECEIPT.exists() or SNAPSHOT.exists():
        read_receipt(context)
        return dict(status='EXISTING_IMMUTABLE_SEAL_VALID', signature_sha256=context.binding)
    require(not SUMMARY.exists() and not REPORT.exists(), 'unsealed final outputs already exist')
    require(not OUT.exists() or not any(OUT.iterdir()), 'unsealed WP8 directory is not empty')
    OUT.mkdir(parents=True, exist_ok=True)
    snapshot = common.outside_snapshot()
    result_json(SNAPSHOT, dict(files=snapshot, role='immutable pre-fit outside-sandbox baseline'),
                context.input_paths, {'outside_files': len(snapshot)})
    result_json(RECEIPT, dict(status='SEALED_NO_FITS', signature=context.signature,
        signature_sha256=context.binding, outside_snapshot_sha256=common.digest(SNAPSHOT),
        planned_classifier_fits=50, planned_sigmoid_fits=10, fits_performed=0,
        authorization='GO v3-model; single fixed preregistered WP8 candidate'),
        context.input_paths + [SNAPSHOT], {'train': 60000, 'validation': 15000, 'pool': 75000})
    return dict(status='SEALED_NO_FITS', signature_sha256=context.binding)


def plan(context):
    jobs = {}
    for fold in context.folds:
        for i, (train, predict) in enumerate(inner_folds(fold, context.pool.y)):
            jobs[f'{fold.tag}_inner{i}'] = ('classifier', train, predict)
        jobs[f'{fold.tag}_development'] = ('classifier', fold.development, fold.calibration)
        jobs[f'{fold.tag}_outer'] = ('classifier', fold.train, fold.test)
        jobs[f'{fold.tag}_sigmoid'] = ('sigmoid', fold.calibration, fold.test)
    return jobs


def fit_signature(context, tag, kind, train, predict, dependencies=None):
    require(np.intersect1d(train, predict).size == 0, 'fit/scoring indices overlap')
    pool = context.pool
    return dict(seal_signature_sha256=context.binding, tag=tag, kind=kind,
                parameters=LGBM_SPEC if kind == 'classifier' else SIGMOID_SPEC,
                train_indices_sha256=indices_hash(train), predict_indices_sha256=indices_hash(predict),
                train_ids_sha256=indices_hash(pool.ids[train]), predict_ids_sha256=indices_hash(pool.ids[predict]),
                train_y_sha256=indices_hash(pool.y[train]), predict_y_sha256=indices_hash(pool.y[predict]),
                train_n=len(train), predict_n=len(predict), dependencies=dependencies or {})


def cache_paths(tag):
    return (OUT / 'cache' / (tag + '.json'), OUT / 'cache' / (tag + '.npz'),
            OUT / 'cache' / (tag + '.started'))


def check_provenance(body, path):
    p = body.get('provenance', {})
    require(p.get('script') == SCRIPT.as_posix() and p.get('script_sha256') == common.digest(SCRIPT)
            and p.get('seed') == SEED + 8 and p.get('tags_used') == ['[E]', '[A]', '[R]']
            and p.get('python_version') == sys.version and p.get('created_utc')
            and p.get('row_counts') and p.get('input_files'), 'invalid task-8 provenance: ' + str(path))
    for source in p['input_files']:
        require(source['present'] and Path(source['path']).is_file()
                and common.digest(source['path']) == source['sha256'], 'provenance input hash mismatch')


def load_complete_cache(context, tag, expected_signature=None):
    marker, prediction, started = cache_paths(tag)
    present = [p.exists() for p in (marker, prediction, started)]
    if not any(present):
        return None
    require(all(present), 'incomplete/orphan fit cache; will NOT refit: ' + tag)
    metadata = read_json(marker)
    check_provenance(metadata, marker)
    signature = metadata['signature']
    require(metadata['signature_sha256'] == signature_hash(signature)
            and started.read_text(encoding='utf-8') == metadata['signature_sha256'], 'fit marker signature mismatch')
    require(signature['seal_signature_sha256'] == context.binding, 'cache bound to different receipt')
    if expected_signature is not None:
        require(signature == expected_signature, 'cache train/predict/parameter/dependency signature mismatch: ' + tag)
    require(metadata['prediction_sha256'] == common.digest(prediction), 'prediction NPZ hash mismatch')
    require(metadata['fit_completed'] is True and metadata['fit_count'] == 1, 'ambiguous fit count')
    require(metadata['fit_started_utc'] >= read_json(RECEIPT)['provenance']['created_utc'], 'fit predates seal')
    require(isinstance(metadata['converged'], bool) and isinstance(metadata['warnings'], list)
            and all(isinstance(w.get('convergence_warning'), bool) for w in metadata['warnings']), 'missing warning/convergence evidence')
    require(metadata['converged'] == (not any(w['convergence_warning'] for w in metadata['warnings'])), 'warning/convergence mismatch')
    if signature['kind'] == 'classifier':
        require(1 <= metadata['fitted_iterations'] <= LGBM_SPEC['n_estimators'], 'invalid fixed-budget classifier iteration count')
    else:
        require(len(metadata['n_iter']) == 1 and 1 <= metadata['n_iter'][0] <= SIGMOID_SPEC['max_iter'], 'invalid sigmoid iteration count')
        require(metadata['n_iter'][0] < SIGMOID_SPEC['max_iter'] or not metadata['converged'], 'sigmoid max-iteration convergence mismatch')
    arrays = arrays_at(prediction)
    _, train, predict = plan(context)[tag]
    for key, expected in (('Customer_ID', context.pool.ids[predict]), ('y', context.pool.y[predict]), ('pool_index', predict)):
        require(np.array_equal(arrays[key], expected), 'cached prediction pairing mismatch')
    probability_keys = ('raw',) if signature['kind'] == 'classifier' else ('p_s', 'p_d', 'calibration_p_s', 'calibration_p_d')
    for key in probability_keys:
        require(np.isfinite(arrays[key]).all() and ((arrays[key] >= 0) & (arrays[key] <= 1)).all(), 'invalid candidate cached probabilities')
        require(arrays[key].shape == (len(train) if key.startswith('calibration_') else len(predict),), 'candidate cache shape mismatch')
    if signature['kind'] == 'classifier':
        require(metadata['training_reference'] == fit_reference(context.pool.raw.iloc[train]), 'peer/category references are not training-only')
        require(metadata['features'] == list(FEATURES), 'cached feature bundle changed')
        if tag.endswith('_outer'):
            model_path = OUT / 'models' / (tag + '.txt')
            require(metadata['model']['path'] == model_path.as_posix() and model_path.is_file()
                    and metadata['model']['sha256'] == common.digest(model_path), 'outer booster hash/path mismatch')
    return arrays, metadata


def preflight_outputs(context):
    jobs = plan(context)
    expected = {tag + suffix for tag in jobs for suffix in ('.json', '.npz', '.started')} | {'_run.lock'}
    root_names = {'prereg_receipt.json', 'outside_snapshot.json', 'models', 'cache', 'bootstrap.json', 'bootstrap.npz'}
    root_names |= {f.tag + suffix for f in context.folds for suffix in ('.json', '.npz')}
    require({p.name for p in OUT.iterdir()} <= root_names, 'unexpected WP8 artifacts')
    directory = OUT / 'cache'
    if directory.exists():
        require({p.name for p in directory.iterdir()} <= expected, 'unexpected cache artifacts')
    cached_metadata = {}
    for tag, (kind, train, predict) in jobs.items():
        base = fit_signature(context, tag, kind, train, predict)
        cached = load_complete_cache(context, tag)
        if cached:
            metadata = cached[1]
            cached_metadata[tag] = metadata
            signature = metadata['signature']
            require({k: v for k, v in signature.items() if k != 'dependencies'} ==
                    {k: v for k, v in base.items() if k != 'dependencies'}, 'planned fit signature mismatch')
            if kind == 'classifier':
                require(signature == base, 'unexpected classifier dependency')
    for fold in context.folds:
        tag = fold.tag + '_sigmoid'
        if tag in cached_metadata:
            dependencies = {}
            for name in ('development', 'outer'):
                source_tag = fold.tag + '_' + name
                require(source_tag in cached_metadata, 'orphan sigmoid dependency')
                dependencies[name] = dict(prediction_sha256=cached_metadata[source_tag]['prediction_sha256'],
                                          marker_sha256=common.digest(cache_paths(source_tag)[0]))
            require(cached_metadata[tag]['signature']['dependencies'] == dependencies, 'sigmoid dependency changed')
    for fold in context.folds:
        pair = [OUT / (fold.tag + suffix) for suffix in ('.json', '.npz')]
        require(all(p.exists() for p in pair) or not any(p.exists() for p in pair), 'orphan outer OOF artifact')
    pair = [OUT / 'bootstrap.json', OUT / 'bootstrap.npz']
    require(all(p.exists() for p in pair) or not any(p.exists() for p in pair), 'orphan bootstrap artifact')
    models = OUT / 'models'
    if models.exists():
        require({p.name for p in models.iterdir()} <= {f.tag + '_outer.txt' for f in context.folds}, 'unexpected models')
        for p in models.iterdir():
            require(cache_paths(p.stem)[0].is_file(), 'orphan model; will NOT refit')


@contextmanager
def run_lock():
    """One process, sequential fits; OS lock is released even on exceptions."""
    import msvcrt
    path = OUT / 'cache/_run.lock'
    with path.open('a+b') as stream:
        if stream.tell() == 0:
            stream.write(b'0')
            stream.flush()
        stream.seek(0)
        try:
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError as error:
            raise RuntimeError('WP8 STOP: another batch process holds the fit lock') from error
        try:
            yield
        finally:
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)


class Runner:
    def __init__(self, context, receipt):
        require(read_receipt(context, check_outside=False) == receipt, 'runner requires the prior immutable receipt')
        self.context, self.receipt = context, receipt
        self.receipt_sha256 = common.digest(RECEIPT)
        self.jobs = plan(context)
        self.new_classifier_fits = self.new_sigmoid_fits = self.cache_hits = 0
        self.used = set()

    def start(self, tag, signature):
        require(tag in self.jobs and tag not in self.used, 'unplanned or duplicate fit request')
        require(common.digest(RECEIPT) == self.receipt_sha256, 'preregistration receipt changed during batch')
        require(common.digest(PREREG) == self.receipt['signature']['prereg_sha256']
                and common.digest(SCRIPT) == self.receipt['signature']['script_sha256'], 'prereg/script changed during batch')
        self.used.add(tag)
        existing = load_complete_cache(self.context, tag, signature)
        if existing:
            self.cache_hits += 1
            return existing, None
        marker, prediction, started = cache_paths(tag)
        require(not marker.exists() and not prediction.exists() and not started.exists(), 'orphan cache cannot be reset')
        with started.open('x', encoding='utf-8') as stream:
            stream.write(signature_hash(signature))
        return None, common.utc_now()

    def finish(self, tag, signature, arrays, metadata, started):
        marker, prediction, _ = cache_paths(tag)
        save_npz(prediction, arrays)
        body = dict(signature=signature, signature_sha256=signature_hash(signature),
                    prediction_sha256=common.digest(prediction), fit_started_utc=started,
                    fit_completed=True, fit_count=1, **metadata)
        # Completion JSON is LAST: any prior partial artifact prevents a refit.
        body = result_json(marker, body, self.context.input_paths + [RECEIPT, prediction],
                           {'fit_rows': signature['train_n'], 'predict_rows': signature['predict_n'], 'fit_count': 1})
        return arrays, body

    def classifier(self, tag):
        kind, train, predict = self.jobs[tag]
        require(kind == 'classifier', 'wrong fit kind')
        signature = fit_signature(self.context, tag, kind, train, predict)
        cached, started = self.start(tag, signature)
        if cached:
            return cached
        from lightgbm import LGBMClassifier
        pool = self.context.pool
        reference = fit_reference(pool.raw.iloc[train])
        X_train = transform_features(pool.raw.iloc[train], reference)
        X_predict = transform_features(pool.raw.iloc[predict], reference)
        model = LGBMClassifier(**LGBM_SPEC)
        with warnings.catch_warnings(record=True) as recorded, threadpool_limits(limits=THREADS):
            warnings.simplefilter('always')
            self.new_classifier_fits += 1
            model.fit(X_train, pool.y[train])
            raw = np.asarray(model.predict_proba(X_predict)[:, 1], dtype=float)
        require(raw.shape == (len(predict),) and np.isfinite(raw).all(), 'nonfinite classifier predictions')
        warning_rows = [dict(category=w.category.__name__, message=str(w.message),
                             convergence_warning=issubclass(w.category, ConvergenceWarning)) for w in recorded]
        converged = not any(issubclass(w.category, ConvergenceWarning) for w in recorded)
        model_info = None
        if tag.endswith('_outer'):
            model_path = (OUT / 'models' / (tag + '.txt')).resolve()
            require(model_path.parent == (OUT / 'models').resolve() and not model_path.exists(), 'unsafe/existing outer model path')
            # Native LightGBM persistence is explicitly confined, not a temp path.
            model.booster_.save_model(str(model_path))
            model_info = common.file_info(model_path)
        metadata = dict(training_reference=reference, features=list(FEATURES),
                        warnings=warning_rows, converged=converged,
                        fitted_iterations=int(model.n_iter_), model=model_info)
        arrays = dict(Customer_ID=pool.ids[predict], y=pool.y[predict], pool_index=predict, raw=raw)
        return self.finish(tag, signature, arrays, metadata, started)

    def sigmoid(self, fold, development, outer):
        tag = fold.tag + '_sigmoid'
        kind, train, predict = self.jobs[tag]
        dependencies = {name: dict(prediction_sha256=item[1]['prediction_sha256'],
                                   marker_sha256=common.digest(cache_paths(fold.tag + '_' + name)[0]))
                        for name, item in (('development', development), ('outer', outer))}
        signature = fit_signature(self.context, tag, kind, train, predict, dependencies)
        cached, started = self.start(tag, signature)
        if cached:
            return cached
        raw_cal, raw_outer = development[0]['raw'], outer[0]['raw']
        model = LogisticRegression(**SIGMOID_SPEC)
        with warnings.catch_warnings(record=True) as recorded, threadpool_limits(limits=THREADS):
            warnings.simplefilter('always')
            self.new_sigmoid_fits += 1
            model.fit(logit(np.clip(raw_cal, 1e-6, 1 - 1e-6)).reshape(-1, 1), self.context.pool.y[train])
            ps_cal = np.clip(model.predict_proba(logit(np.clip(raw_cal, 1e-6, 1 - 1e-6)).reshape(-1, 1))[:, 1], 1e-6, 1 - 1e-6)
            ps_outer = np.clip(model.predict_proba(logit(np.clip(raw_outer, 1e-6, 1 - 1e-6)).reshape(-1, 1))[:, 1], 1e-6, 1 - 1e-6)
        prior = float(self.context.pool.y[train].mean())
        arrays = dict(Customer_ID=self.context.pool.ids[predict], y=self.context.pool.y[predict], pool_index=predict,
                      p_s=ps_outer, p_d=shift_probability(ps_outer, prior),
                      calibration_p_s=ps_cal, calibration_p_d=shift_probability(ps_cal, prior))
        metadata = dict(slope=float(model.coef_[0, 0]), intercept=float(model.intercept_[0]),
                        sample_prior=prior, n_iter=model.n_iter_.tolist(),
                        warnings=[dict(category=w.category.__name__, message=str(w.message),
                                       convergence_warning=issubclass(w.category, ConvergenceWarning)) for w in recorded],
                        converged=not any(issubclass(w.category, ConvergenceWarning) for w in recorded),
                        training_reference={name: item[1]['training_reference'] for name, item in
                                            (('development', development), ('outer', outer))})
        return self.finish(tag, signature, arrays, metadata, started)


def immutable_oof(context, fold, arrays, body):
    npz, marker = OUT / (fold.tag + '.npz'), OUT / (fold.tag + '.json')
    if marker.exists():
        metadata = read_json(marker)
        check_provenance(metadata, marker)
        require(metadata['npz_sha256'] == common.digest(npz), 'outer OOF hash mismatch')
        require({k: metadata[k] for k in body} == clean(body), 'outer OOF metadata mismatch')
        stored = arrays_at(npz)
        require(set(stored) == set(arrays) and all(np.array_equal(stored[k], arrays[k], equal_nan=True) for k in stored), 'outer OOF content mismatch')
    else:
        require(not npz.exists(), 'orphan OOF NPZ')
        save_npz(npz, arrays)
        result_json(marker, dict(npz_sha256=common.digest(npz), **body),
                    context.input_paths + [RECEIPT, npz], {'outer_oof_rows': len(fold.test)})
    return dict(npz=common.file_info(npz), metadata=common.file_info(marker))


def make_fold(context, runner, fold):
    pool = context.pool
    diagnostics, inner_converged = [], True
    cache_bindings = {}
    for i, (_, heldout) in enumerate(inner_folds(fold, pool.y)):
        tag = fold.tag + f'_inner{i}'
        candidate = runner.classifier(tag)
        baseline = context.baseline_inner[fold.tag + f'_i{i}']
        candidate_auc = float(roc_auc_score(pool.y[heldout], candidate[0]['raw']))
        baseline_auc = float(roc_auc_score(pool.y[heldout], baseline['raw']))
        diagnostics.append(dict(inner=i, rows=len(heldout), candidate_auc=candidate_auc,
                                baseline_auc=baseline_auc, delta_auc=candidate_auc - baseline_auc,
                                selection_used=False))
        inner_converged &= candidate[1]['converged'] and baseline['metadata']['converged']
        cache_bindings[tag] = common.file_info(cache_paths(tag)[0])
    dev = runner.classifier(fold.tag + '_development')
    outer = runner.classifier(fold.tag + '_outer')
    sigmoid = runner.sigmoid(fold, dev, outer)
    for tag in (fold.tag + '_development', fold.tag + '_outer', fold.tag + '_sigmoid'):
        cache_bindings[tag] = common.file_info(cache_paths(tag)[0])
    baseline = context.baseline_outer[fold.tag]
    raw, ps, pd_ = outer[0]['raw'], sigmoid[0]['p_s'], sigmoid[0]['p_d']
    limits = value_limits(pool.raw.iloc[fold.train])
    dev_limits = value_limits(pool.raw.iloc[fold.development])
    V = values(pool.raw.iloc[fold.test], limits)
    cal_V = values(pool.raw.iloc[fold.calibration], dev_limits)
    own, shared = pd_ * V >= TAU, baseline['p_d'] * V >= TAU
    candidate_metrics = measure(pool.y[fold.test], raw, ps, pd_, V, shared)
    baseline_metrics = measure(pool.y[fold.test], baseline['raw'], baseline['p_s'], baseline['p_d'], V, shared)
    converged = bool(inner_converged and dev[1]['converged'] and outer[1]['converged'] and sigmoid[1]['converged']
                     and context.baseline_metrics[(fold.repeat, fold.number)]['converged'])
    arrays = dict(Customer_ID=pool.ids[fold.test], y=pool.y[fold.test], pool_index=fold.test,
                  raw=raw, p_s=ps, p_d=pd_, V=V, value=V, deployment_weight=deployment_weights(pool.y[fold.test]),
                  baseline_raw=baseline['raw'], baseline_p_s=baseline['p_s'], baseline_p_d=baseline['p_d'],
                  score=pd_ * V, baseline_score=baseline['p_d'] * V,
                  own_tail=own, baseline_tail=shared, frozen_tau_own_tail=own, frozen_tau_baseline_tail=shared,
                  historical_baseline_tail=baseline['own_tail'], tau=np.array(TAU),
                  repeat=np.array(fold.repeat), fold=np.array(fold.number))
    body = dict(signature_sha256=context.binding, tag=fold.tag, repeat=fold.repeat, fold=fold.number,
                train_n=60000, development_n=48000, calibration_n=12000, heldout_n=15000,
                tau=TAU, candidate_metrics=candidate_metrics, baseline_metrics=baseline_metrics,
                differences={name: candidate_metrics[name] - baseline_metrics[name] for name in METRICS},
                inner_diagnostics=diagnostics, converged=converged, cache_bindings=cache_bindings,
                outer_training_value_limits=limits, development_value_limits=dev_limits,
                calibration_sample_prior=sigmoid[1]['sample_prior'],
                calibration_fixed_tau_contact_share=float(deployment_weights(pool.y[fold.calibration])[
                    sigmoid[0]['calibration_p_d'] * cal_V >= TAU].sum() / len(fold.calibration)))
    artifact = immutable_oof(context, fold, arrays, body)
    return clean(body), artifact


def bootstrap_artifact(context, differences):
    npz, marker = OUT / 'bootstrap.npz', OUT / 'bootstrap.json'
    generated = bootstrap(differences)
    arrays = dict(**generated, metric_names=np.array(METRICS), seed=np.array(SEED + 8))
    body = dict(signature_sha256=context.binding, draws_each=DRAWS, seed=SEED + 8,
                metric_names=list(METRICS), percentile_method='linear',
                order='hierarchical repetitions then within-repetition folds; IID follows on same RNG')
    if marker.exists():
        metadata = read_json(marker)
        check_provenance(metadata, marker)
        require(metadata['npz_sha256'] == common.digest(npz)
                and {k: metadata[k] for k in body} == body, 'bootstrap binding mismatch')
        stored = arrays_at(npz)
        require(set(stored) == set(arrays) and all(np.array_equal(stored[k], arrays[k], equal_nan=True)
                if stored[k].dtype.kind not in 'US' else np.array_equal(stored[k], arrays[k]) for k in arrays), 'bootstrap deterministic reconstruction mismatch')
    else:
        require(not npz.exists(), 'orphan bootstrap NPZ')
        save_npz(npz, arrays)
        result_json(marker, dict(npz_sha256=common.digest(npz), **body),
                    context.input_paths + [RECEIPT, npz], {'hierarchical_draws': DRAWS, 'iid_draws': DRAWS, 'paired_folds': 10})
    return generated, dict(npz=common.file_info(npz), metadata=common.file_info(marker))


def format_number(value):
    return 'NONFINITE / unavailable' if value is None else f'{value:.12g}'


def render_report(summary):
    lines = ['# WP8 — fixed preregistered contrasts', '', 'Status: ' + summary['status'], '',
        '[E] Preregistration SHA-256: ' + summary['prereg_sha256'],
        '[E] Script SHA-256: ' + summary['script_sha256'], '',
        '[A] One fixed 113-feature LightGBM candidate (frozen 87 + 26). No tuning, early stopping, blending or target encoding.',
        '[E] 50 complete classifier fits: 30 inner diagnostic, 10 development, 10 outer; 10 complete sigmoid fits. '
        'Baseline reused: 30 inner and 10 outer caches; baseline refits: 0.',
        '[E] 150,000 repeated outer OOF rows; 75,000 unique customers, each twice. No new test look or original calibration-policy feature processing.',
        '[A] Policy uses unchanged numeric tau=1.711493684172072 for both models; deployment prior 0.02 is hypothetical. '
        'Value limits and peer/category references are fit-training-only.', '',
        '## Equal-weight outer mean metrics', '', '| Metric | Candidate | Cached baseline | Paired difference |', '|---|---:|---:|---:|']
    for name in METRICS:
        lines.append('| ' + name + ' | ' + ' | '.join(format_number(summary['mean_metrics'][key][name])
                     for key in ('candidate', 'baseline', 'difference')) + ' |')
    lines += ['', '## All ten paired folds', '', '| Fold | Candidate AUC | Baseline AUC | Delta AUC | Delta capture | Candidate contact share | Baseline contact share | Converged |', '|---|---:|---:|---:|---:|---:|---:|---|']
    for row in summary['folds']:
        lines.append('| ' + row['tag'] + ' | ' + ' | '.join(format_number(x) for x in
            (row['candidate_metrics']['auc'], row['baseline_metrics']['auc'], row['differences']['auc'],
             row['differences']['value_capture'], row['candidate_metrics']['contact_share'], row['baseline_metrics']['contact_share']))
            + ' | ' + str(row['converged']) + ' |')
    lines += ['', '## Complete per-fold metrics', '', '| Fold | Metric | Candidate | Baseline | Difference |', '|---|---|---:|---:|---:|']
    for row in summary['folds']:
        for name in METRICS:
            lines.append('| ' + row['tag'] + ' | ' + name + ' | ' + ' | '.join(format_number(v) for v in
                (row['candidate_metrics'][name], row['baseline_metrics'][name], row['differences'][name])) + ' |')
    lines += ['', '## Joint paired intervals', '', '| Metric | Liberal IID | Hierarchical | Corrected t (df=4) | Conservative envelope |', '|---|---|---|---|---|']
    for name, item in summary['intervals'].items():
        def interval_text(key):
            endpoints = item[key]
            return 'unavailable' if endpoints is None else '[' + ', '.join(format_number(v) for v in endpoints) + ']'
        lines.append('| ' + name + ' | ' + ' | '.join(interval_text(k) for k in ('iid', 'hierarchical', 'corrected_t', 'conservative')) + ' |')
    lines += ['', '[A] 100,000 hierarchical and 100,000 IID paired draws saved with all metric columns and resampling indices. '
        'Linear percentile endpoints. Corrected SE=sqrt((1/10+0.25)*sample variance), df=4. '
        'Conservative interval envelopes hierarchical and corrected-t endpoints.',
        '[A] Repeated folds share customers/training rows. Hierarchical resampling is an exploratory variance heuristic, '
        'not independently sampled cohort uncertainty; no calibrated coverage or post-selection guarantee.', '', '## Every gate', '']
    lines += ['- [E] ' + ('PASS' if passed else 'FAIL') + ': ' + name for name, passed in summary['promotion']['gates'].items()]
    lines += ['', '[E] Failed gates: ' + (', '.join(summary['promotion']['failed_gates']) or 'none'),
              '[R] ' + summary['decision'], '', '## Warnings and non-adaptive inner evidence', '']
    for fit in summary['fit_inventory']:
        lines.append('- [E] ' + fit['tag'] + ': converged=' + str(fit['converged']) +
                     '; iterations=' + str(fit['iterations']) + '; warnings=' + json.dumps(fit['warnings'], ensure_ascii=False))
    for fold in summary['folds']:
        lines.append('- [E] ' + fold['tag'] + ' inner paired AUC differences (diagnostic only): ' +
                     ', '.join(format_number(item['delta_auc']) for item in fold['inner_diagnostics']))
    lines += ['', '## Integrity, limitations and stopping boundary', '',
        '[E] Outside-sandbox full directory diff: ' + json.dumps(summary['outside_sandbox_diff'], sort_keys=True),
        '[E] Frozen delivery unchanged: ' + str(summary['frozen_delivery_unchanged']) +
        '; historical WP7 receipt and 118-file manifest unchanged: ' + str(summary['wp7_unchanged']) + '.',
        '[A] Sigmoid trained from a 48k development model is applied to a 60k refit: fit-size-shift limitation. '
        'The _Mean window is unspecified; curvature/contrasts are undated proxies, not verified acceleration or temporal validation.',
        '[R] No test scoring even if all gates pass. Passing means eligible_requires_separate_confirmatory_scope, '
        'not deployment or delivery integration. Failing retains frozen v2 and stops this model track; no further candidate/revision/seed sweep.',
        '[E] No notebook, PDF, PPTX, reference, configuration, old model/test, or historical receipt was edited.', '']
    return '\n'.join(lines)


def fit_inventory(context):
    inventory = []
    for tag, (kind, train, predict) in plan(context).items():
        cached = load_complete_cache(context, tag)
        require(cached is not None, 'missing completed fit ' + tag)
        metadata = cached[1]
        inventory.append(dict(tag=tag, kind=kind, fit_count=metadata['fit_count'],
            train_n=len(train), predict_n=len(predict), converged=metadata['converged'],
            iterations=metadata['fitted_iterations'] if kind == 'classifier' else metadata['n_iter'][0],
            warnings=metadata['warnings'], marker=common.file_info(cache_paths(tag)[0])))
    require(sum(row['fit_count'] for row in inventory if row['kind'] == 'classifier') == 50
            and sum(row['fit_count'] for row in inventory if row['kind'] == 'sigmoid') == 10, 'completed fit count mismatch')
    return inventory


def run():
    context = build_context()
    receipt = read_receipt(context)
    if SUMMARY.exists():
        return verify_outputs(context)
    for directory in (OUT, OUT / 'models', OUT / 'cache'):
        directory.mkdir(parents=True, exist_ok=True)
    with run_lock(), threadpool_limits(limits=THREADS):
        preflight_outputs(context)
        runner = Runner(context, receipt)
        rows, artifacts = [], []
        for fold in context.folds:
            row, artifact = make_fold(context, runner, fold)
            rows.append(row)
            artifacts.append(artifact)
        require(len(runner.used) == 60, 'fit plan incomplete')
        differences = np.array([[row['differences'][name] if row['differences'][name] is not None else np.nan
                                 for name in METRICS] for row in rows], dtype=float)
        samples, bootstrap_files = bootstrap_artifact(context, differences)
        intervals = interval_summary(differences, samples)
        inventory = fit_inventory(context)
        before = read_json(SNAPSHOT)['files']
        after = common.outside_snapshot()
        difference = outside_diff(before, after)
        protected = context.signature['protected_fingerprints']
        fingerprint_ok = all(common.digest(item['path']) == item['sha256'] for item in protected)
        complete = len(rows) == 10 and np.isfinite(differences).all()
        converged = all(row['converged'] for row in rows) and all(row['converged'] for row in inventory)
        promotion = promotion_gates(intervals, complete, converged, difference['passed'] and fingerprint_ok)
        decision = ('eligible_requires_separate_confirmatory_scope' if promotion['passed'] else 'rejected_keep_frozen_v2_stop_model_track')
        means = {which: {name: float(np.mean([row[which + '_metrics'][name] if row[which + '_metrics'][name] is not None else np.nan
                                            for row in rows])) for name in METRICS} for which in ('candidate', 'baseline')}
        means['difference'] = {name: float(differences[:, i].mean()) for i, name in enumerate(METRICS)}
        summary = clean(dict(status='COMPLETED', candidate=CANDIDATE, decision=decision,
            signature_sha256=context.binding, prereg_sha256=common.digest(PREREG), script_sha256=common.digest(SCRIPT),
            receipt=common.file_info(RECEIPT), outside_snapshot=common.file_info(SNAPSHOT),
            features=list(FEATURES), new_features=list(NEW_FEATURES), tau=TAU, deployment_prior=PRIOR,
            row_counts=dict(repeated_oof=150000, unique_customers=75000, times_per_customer=2, train=60000, validation=15000),
            fit_counts=dict(classifier=50, inner=30, development=10, outer=10, sigmoid=10, baseline_refits=0,
                            reused_baseline_inner=30, reused_baseline_outer=10, reused_baseline_total=40),
            session_counts=dict(new_classifier_fits=runner.new_classifier_fits, new_sigmoid_fits=runner.new_sigmoid_fits,
                                completed_cache_hits=runner.cache_hits),
            fit_inventory=inventory, folds=rows, mean_metrics=means, intervals=intervals,
            promotion=promotion, oof_artifacts=artifacts, bootstrap=bootstrap_files,
            outside_sandbox_diff=difference, protected_fingerprints=protected,
            frozen_delivery_unchanged=difference['passed'] and fingerprint_ok, wp7_unchanged=fingerprint_ok,
            no_new_test_look=True, no_original_calibration_policy_feature_processing=True,
            no_delivery_integration=True, no_baseline_refit=True,
            limitations=['48k development-to-calibration / 60k refit fit-size shift',
                         'undated _Mean contrast proxies', 'exploratory repeated-fold variance heuristic; no calibrated coverage']))
        report_text = render_report(summary)
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        if REPORT.exists():
            require(REPORT.read_text(encoding='utf-8') == report_text, 'existing report mismatch; never overwrite')
        else:
            with REPORT.open('x', encoding='utf-8', newline='\n') as stream:
                stream.write(report_text)
        summary['report'] = common.file_info(REPORT)
        inputs = context.input_paths + [RECEIPT, SNAPSHOT, REPORT, OUT / 'bootstrap.npz', OUT / 'bootstrap.json']
        inputs += [OUT / (f.tag + suffix) for f in context.folds for suffix in ('.npz', '.json')]
        inputs += [cache_paths(tag)[0] for tag in plan(context)]
        result_json(SUMMARY, summary, inputs, summary['row_counts'])
    return verify_outputs(context)


def independent_metrics(arrays, baseline=False):
    """Verification implementation independent of measure()/weighted_losses()."""
    y = arrays['y'].astype(float)
    raw = arrays['baseline_raw' if baseline else 'raw']
    ps = arrays['baseline_p_s' if baseline else 'p_s']
    pd_ = arrays['baseline_p_d' if baseline else 'p_d']
    V = arrays['V']
    w = np.where(y == 1, len(y) * .02 / y.sum(), len(y) * .98 / (len(y) - y.sum()))
    own = pd_ * V >= 1.711493684172072
    shared = arrays['baseline_p_d'] * V >= 1.711493684172072
    def losses(probability, mask, weight):
        if not mask.any():
            return (None, None)
        p = np.clip(probability[mask], .000001, .999999)
        target, ww = y[mask], weight[mask]
        return (float(np.sum(ww * (target - p) ** 2) / ww.sum()),
                float(np.sum(ww * (-target * np.log(p) - (1 - target) * np.log(1 - p))) / ww.sum()))
    bs, ls = losses(pd_, shared, w)
    bo, lo = losses(pd_, own, w)
    sb, sl = losses(ps, np.ones(len(y), bool), np.ones(len(y)))
    db, dl = losses(pd_, np.ones(len(y), bool), w)
    denominator = (w * y * V).sum()
    return dict(auc=float(roc_auc_score(y, raw)), value_capture=float((w * y * V)[own].sum() / denominator) if denominator > 0 else None,
                contact_share=float(w[own].sum() / w.sum()), baseline_tail_brier=bs, baseline_tail_logloss=ls,
                own_tail_brier=bo, own_tail_logloss=lo, sample_brier=sb, sample_logloss=sl,
                deployment_brier=db, deployment_logloss=dl, calibrated_auc=float(roc_auc_score(y, ps)), raw_contacts=int(own.sum()))


def numerically_equal(a, b, tolerance=2e-13):
    if isinstance(a, dict) and isinstance(b, dict):
        return set(a) == set(b) and all(numerically_equal(a[k], b[k], tolerance) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(numerically_equal(x, y, tolerance) for x, y in zip(a, b))
    if a is None or b is None:
        return a is b
    if isinstance(a, (float, int)) and isinstance(b, (float, int)):
        return bool(np.isclose(a, b, rtol=0, atol=tolerance))
    return a == b


def verify_outputs(context=None):
    """Read-only actual-output audit. No model loading, fitting, or test scoring."""
    context = context or build_context()
    read_receipt(context)
    require(SUMMARY.is_file(), 'no completed output to verify')
    summary = read_json(SUMMARY)
    check_provenance(summary, SUMMARY)
    require(summary['signature_sha256'] == context.binding and summary['status'] == 'COMPLETED', 'final signature/status mismatch')
    preflight_outputs(context)
    inventory = fit_inventory(context)
    inventory_by_tag = {item['tag']: item for item in inventory}
    require(summary['fit_inventory'] == inventory, 'fit inventory mismatch')
    require(summary['fit_counts'] == dict(classifier=50, inner=30, development=10, outer=10, sigmoid=10,
        baseline_refits=0, reused_baseline_inner=30, reused_baseline_outer=10, reused_baseline_total=40), 'classifier/sigmoid/baseline counts mismatch')
    for binding in (summary['receipt'], summary['outside_snapshot'], summary['report']):
        require(binding == common.file_info(binding['path']), 'final artifact hash mismatch')
    require(summary['features'] == list(FEATURES) and summary['new_features'] == list(NEW_FEATURES)
            and summary['tau'] == TAU and summary['deployment_prior'] == PRIOR, 'final fixed specification changed')
    require(len(summary['folds']) == len(summary['oof_artifacts']) == 10, 'not ten output folds')
    repeated_ids, repeat_ids, verified_rows = [], {0: [], 1: []}, []
    for fold, row, artifact in zip(context.folds, summary['folds'], summary['oof_artifacts']):
        require(row['tag'] == fold.tag and row['repeat'] == fold.repeat and row['fold'] == fold.number, 'fold order/tag mismatch')
        require([row[k] for k in ('train_n', 'development_n', 'calibration_n', 'heldout_n')] == [60000, 48000, 12000, 15000], 'actual fold size metadata mismatch')
        require(row['outer_training_value_limits'] == value_limits(context.pool.raw.iloc[fold.train])
                and row['development_value_limits'] == value_limits(context.pool.raw.iloc[fold.development]), 'actual training-only value limits mismatch')
        npz, marker = OUT / (fold.tag + '.npz'), OUT / (fold.tag + '.json')
        require(artifact == dict(npz=common.file_info(npz), metadata=common.file_info(marker)), 'OOF summary hash binding mismatch')
        metadata, arrays = read_json(marker), arrays_at(npz)
        check_provenance(metadata, marker)
        require(metadata['npz_sha256'] == common.digest(npz) and {k: metadata[k] for k in row} == row, 'OOF metadata binding mismatch')
        for key, expected in (('Customer_ID', context.pool.ids[fold.test]), ('pool_index', fold.test), ('y', context.pool.y[fold.test])):
            require(np.array_equal(arrays[key], expected), 'actual OOF pairing mismatch')
        require(arrays['tau'].item() == TAU and arrays['repeat'].item() == fold.repeat and arrays['fold'].item() == fold.number, 'OOF scalar fold/tau mismatch')
        V = values(context.pool.raw.iloc[fold.test], value_limits(context.pool.raw.iloc[fold.train]))
        require(np.array_equal(arrays['V'], V) and np.array_equal(arrays['value'], V), 'actual V mismatch')
        baseline = context.baseline_outer[fold.tag]
        for key in ('raw', 'p_s', 'p_d'):
            require(np.array_equal(arrays['baseline_' + key], baseline[key]), 'actual baseline prediction mismatch')
        require(np.array_equal(arrays['historical_baseline_tail'], baseline['own_tail']), 'historical tail pairing mismatch')
        require(np.array_equal(arrays['deployment_weight'], deployment_weights(arrays['y'])), 'actual outcome weights mismatch')
        outer = load_complete_cache(context, fold.tag + '_outer', fit_signature(context, fold.tag + '_outer', 'classifier', fold.train, fold.test))
        dev = load_complete_cache(context, fold.tag + '_development', fit_signature(context, fold.tag + '_development', 'classifier', fold.development, fold.calibration))
        dependencies = {name: dict(prediction_sha256=item[1]['prediction_sha256'], marker_sha256=common.digest(cache_paths(fold.tag + '_' + name)[0]))
                        for name, item in (('development', dev), ('outer', outer))}
        sigmoid = load_complete_cache(context, fold.tag + '_sigmoid', fit_signature(context, fold.tag + '_sigmoid', 'sigmoid', fold.calibration, fold.test, dependencies))
        require(sigmoid[1]['training_reference'] == {'development': dev[1]['training_reference'], 'outer': outer[1]['training_reference']}, 'sigmoid peer reference binding mismatch')
        for key, expected in (('raw', outer[0]['raw']), ('p_s', sigmoid[0]['p_s']), ('p_d', sigmoid[0]['p_d'])):
            require(np.array_equal(arrays[key], expected), 'OOF classifier/sigmoid cache mismatch')
        for prefix, raw in (('', outer[0]['raw']), ('calibration_', dev[0]['raw'])):
            ps = sigmoid_probability(raw, sigmoid[1]['slope'], sigmoid[1]['intercept'])
            require(np.allclose(ps, sigmoid[0][prefix + 'p_s'], rtol=0, atol=2e-15)
                    and np.allclose(shift_probability(sigmoid[0][prefix + 'p_s'], sigmoid[1]['sample_prior']),
                                    sigmoid[0][prefix + 'p_d'], rtol=0, atol=2e-15), 'actual sigmoid/shift reconstruction mismatch')
        require(sigmoid[1]['sample_prior'] == float(context.pool.y[fold.calibration].mean())
                and row['calibration_sample_prior'] == sigmoid[1]['sample_prior'], 'sigmoid internal sample prior mismatch')
        cal_V = values(context.pool.raw.iloc[fold.calibration], row['development_value_limits'])
        cal_selected = sigmoid[0]['calibration_p_d'] * cal_V >= TAU
        cal_share = float(deployment_weights(context.pool.y[fold.calibration])[cal_selected].sum() / len(fold.calibration))
        require(numerically_equal(row['calibration_fixed_tau_contact_share'], cal_share), 'internal-calibration fixed-tau share mismatch')
        for key, mask in (('own_tail', arrays['p_d'] * V >= TAU), ('baseline_tail', arrays['baseline_p_d'] * V >= TAU)):
            require(np.array_equal(arrays[key], mask) and np.array_equal(arrays['frozen_tau_' + key], mask), 'numeric fixed-tau tail mismatch')
        require(np.array_equal(arrays['score'], arrays['p_d'] * V)
                and np.array_equal(arrays['baseline_score'], arrays['baseline_p_d'] * V), 'fixed-tau policy score mismatch')
        candidate_metrics, baseline_metrics = independent_metrics(arrays), independent_metrics(arrays, baseline=True)
        delta = {name: None if candidate_metrics[name] is None or baseline_metrics[name] is None else candidate_metrics[name] - baseline_metrics[name] for name in METRICS}
        require(numerically_equal(candidate_metrics, row['candidate_metrics'])
                and numerically_equal(baseline_metrics, row['baseline_metrics'])
                and numerically_equal(delta, row['differences']), 'independent actual metric reconstruction mismatch')
        require(len(row['inner_diagnostics']) == 3, 'inner diagnostic count mismatch')
        for i, (train, predict) in enumerate(inner_folds(fold, context.pool.y)):
            tag = fold.tag + f'_inner{i}'
            cached = load_complete_cache(context, tag, fit_signature(context, tag, 'classifier', train, predict))
            base = context.baseline_inner[fold.tag + f'_i{i}']
            ca = float(roc_auc_score(context.pool.y[predict], cached[0]['raw']))
            ba = float(roc_auc_score(context.pool.y[predict], base['raw']))
            require(numerically_equal(row['inner_diagnostics'][i], dict(inner=i, rows=16000, candidate_auc=ca,
                baseline_auc=ba, delta_auc=ca - ba, selection_used=False)), 'inner paired diagnostic mismatch')
        expected_tags = {fold.tag + suffix for suffix in ('_inner0', '_inner1', '_inner2', '_development', '_outer', '_sigmoid')}
        require(set(row['cache_bindings']) == expected_tags, 'fold must bind all six fit markers')
        expected_convergence = all(inventory_by_tag[tag]['converged'] for tag in expected_tags)
        expected_convergence &= context.baseline_metrics[(fold.repeat, fold.number)]['converged']
        expected_convergence &= all(context.baseline_inner[fold.tag + f'_i{i}']['metadata']['converged'] for i in range(3))
        require(row['converged'] == bool(expected_convergence), 'fold convergence evidence mismatch')
        for tag, binding in row['cache_bindings'].items():
            require(binding == common.file_info(cache_paths(tag)[0]), 'fold cache marker hash mismatch')
        verified_rows.append(dict(candidate_metrics=candidate_metrics, baseline_metrics=baseline_metrics, differences=delta))
        repeated_ids.extend(arrays['Customer_ID'].tolist())
        repeat_ids[fold.repeat].extend(arrays['Customer_ID'].tolist())
    ids, counts = np.unique(repeated_ids, return_counts=True)
    require(len(repeated_ids) == 150000 and len(ids) == 75000 and (counts == 2).all()
            and set(ids) == set(context.pool.ids), '150k OOF /75k ID multiplicity mismatch')
    require(all(len(group) == 75000 and len(set(group)) == 75000 and set(group) == set(context.pool.ids)
                for group in repeat_ids.values()), 'each repetition must cover 75k IDs once')
    differences = np.array([[np.nan if row['differences'][name] is None else row['differences'][name] for name in METRICS]
                            for row in verified_rows], dtype=float)
    means = {which: {name: None if any(row[which + '_metrics'][name] is None for row in verified_rows) else
                    float(np.mean([row[which + '_metrics'][name] for row in verified_rows])) for name in METRICS} for which in ('candidate', 'baseline')}
    means['difference'] = clean({name: float(differences[:, i].mean()) for i, name in enumerate(METRICS)})
    require(numerically_equal(summary['mean_metrics'], means), 'equal-weight mean metric mismatch')
    bootstrap_npz, bootstrap_marker = OUT / 'bootstrap.npz', OUT / 'bootstrap.json'
    require(summary['bootstrap'] == dict(npz=common.file_info(bootstrap_npz), metadata=common.file_info(bootstrap_marker)), 'bootstrap summary binding mismatch')
    bootstrap_meta = read_json(bootstrap_marker)
    check_provenance(bootstrap_meta, bootstrap_marker)
    require(bootstrap_meta['npz_sha256'] == common.digest(bootstrap_npz) and bootstrap_meta['draws_each'] == 100000
            and bootstrap_meta['seed'] == SEED + 8 and bootstrap_meta['signature_sha256'] == context.binding, 'bootstrap metadata mismatch')
    saved = arrays_at(bootstrap_npz)
    require(saved['metric_names'].tolist() == list(METRICS) and saved['seed'].item() == SEED + 8
            and np.allclose(saved['differences'], differences, rtol=0, atol=2e-13, equal_nan=True), 'bootstrap paired input mismatch')
    # Independent resampling-index reconstruction (not bootstrap()).
    rng = np.random.default_rng(SEED + 8)
    repetitions = rng.integers(0, 2, size=(100000, 2))
    within = rng.integers(0, 5, size=(100000, 2, 5))
    hidx = (repetitions[:, :, None] * 5 + within).reshape(100000, 10).astype('int8')
    iidx = rng.integers(0, 10, size=(100000, 10)).astype('int8')
    require(np.array_equal(saved['hierarchical_indices'], hidx) and np.array_equal(saved['iid_indices'], iidx), 'bootstrap seed/index reconstruction mismatch')
    for key, index in (('hierarchical', hidx), ('iid', iidx)):
        require(saved[key].shape == (100000, len(METRICS)), 'bootstrap draw count mismatch')
        for start in range(0, 100000, 2000):
            expected = saved['differences'][index[start:start + 2000]].mean(axis=1)
            require(np.array_equal(saved[key][start:start + 2000], expected, equal_nan=True), 'saved paired bootstrap means mismatch')
    intervals = interval_summary(saved['differences'], saved)
    require(numerically_equal(intervals, summary['intervals']), 'interval/envelope reconstruction mismatch')
    difference = outside_diff(read_json(SNAPSHOT)['files'], common.outside_snapshot())
    require(difference == summary['outside_sandbox_diff'] and difference['passed'], 'actual protected directory diff mismatch')
    require(summary['protected_fingerprints'] == context.signature['protected_fingerprints']
            and all(common.file_info(item['path']) == item for item in summary['protected_fingerprints']), 'protected/WP7 fingerprints mismatch')
    promotion = promotion_gates(intervals, np.isfinite(saved['differences']).all(),
                                all(row['converged'] for row in summary['folds']) and all(row['converged'] for row in inventory), True)
    require(promotion == summary['promotion'], 'gate reconstruction mismatch')
    expected_decision = 'eligible_requires_separate_confirmatory_scope' if promotion['passed'] else 'rejected_keep_frozen_v2_stop_model_track'
    require(summary['decision'] == expected_decision and all(summary[k] is True for k in
            ('no_new_test_look', 'no_delivery_integration', 'no_baseline_refit', 'frozen_delivery_unchanged', 'wp7_unchanged',
             'no_original_calibration_policy_feature_processing')), 'confirmatory/integration boundary mismatch')
    require(summary['row_counts'] == dict(repeated_oof=150000, unique_customers=75000, times_per_customer=2,
                                         train=60000, validation=15000), 'summary row counts mismatch')
    require(REPORT.read_text(encoding='utf-8') == render_report(summary), 'actual report/summary mismatch')
    return dict(status='VERIFIED_READ_ONLY', decision=summary['decision'], failed_gates=promotion['failed_gates'],
                classifier_fits=50, sigmoid_fits=10, reused_baseline_caches=40,
                repeated_oof_rows=150000, unique_customers=75000, no_new_test_look=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    options = parser.add_mutually_exclusive_group(required=True)
    options.add_argument('--seal', action='store_true', help='hash-bound preregistration receipt; NO fits')
    options.add_argument('--run', action='store_true', help='execute/resume only the sealed fixed batch')
    options.add_argument('--verify', action='store_true', help='independently verify existing actual outputs; NO fits/writes')
    args = parser.parse_args()
    operation = seal if args.seal else run if args.run else verify_outputs
    print(json.dumps(operation(), sort_keys=True, allow_nan=False))


if __name__ == '__main__':
    main()
