"""Local-only D1-D5/C4 experiments; importing this module never fits a model.

Run with the shared Python 3.11 interpreter and --run, or --smoke for a separate
non-decision, reduced-compute end-to-end check. No calibration-policy/test rows
are passed to any experiment. The only 75k fit is a BASELINE RESUBSTITUTION
learning-curve diagnostic, not a production refit or a held-out 75k result.

Outer CV: sequential 2 x 5 stratified folds. All adaptive feature selection and
blend weights are learned inside an outer fold's development portion. Its
separate 20% calibration slice supplies sigmoid calibration and contact cutoffs.
Models are then refitted on the complete outer training fold, never outer labels.
This is split-calibrate/refit calibration (48k -> 60k fit-size shift), not a claim
that the calibration model and the final model are the very same fitted object.

Intervals use conservative Nadeau-Bengio-style corrected t standard errors:
 sqrt((1 / number_of_paired_folds + mean(test_n / train_n)) * sample_variance).
Degrees of freedom are k-1=4, conservatively not 9 independent repeated folds.
Gate D additionally requires non-positive corrected upper bounds for weighted
Brier AND log loss on the SAME baseline-defined tail, and on each policy's tail.
All thresholds defining these nominal weighted top deciles come from inner
held-out calibration rows, not from sorting the outer holdout to set a cutoff.
"""
from __future__ import annotations

import os

for _variable in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                  "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_variable] = "6"

import argparse
from dataclasses import asdict, dataclass
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
import time
import warnings

import numpy as np
import pandas as pd
from scipy import sparse
from scipy.optimize import minimize
from scipy.special import expit, logit
from scipy.stats import t as student_t
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, SplineTransformer, StandardScaler
from threadpoolctl import threadpool_limits

try:
    from . import common
except ImportError:
    import common

SEED = common.SEED
THREADS = common.THREADS
SHARED_PYTHON = Path("C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe")
REPEATS, FOLDS, INNER_FOLDS = 2, 5, 3
DEPLOYMENT_PRIOR, CONTACT_SHARE, M_ESTIMATE = .02, .10, 50.0
SMOKE_ROWS = 1000
GROUPS = ("g1_temporal", "g2_range", "g3_billing_gaps", "g4_call_care",
          "g5_equipment_cycle", "g6_tenure_pricing")
AVAILABLE_GROUPS = tuple(g for g in GROUPS if g != "g2_range")
BLEND_MODELS = ("lgbm", "catboost", "xgboost", "spline_logistic")
BASELINE_NAME = "baseline_lgbm"

# No early stopping, grid search, or outer-label-dependent iteration budgets.
MODEL_SPECS = {
    "lgbm": dict(n_estimators=385, learning_rate=.03, num_leaves=31,
                 min_child_samples=100, reg_lambda=12, subsample=.85,
                 subsample_freq=1, colsample_bytree=.85, n_jobs=THREADS,
                 random_state=SEED, verbosity=-1, deterministic=True,
                 force_col_wise=True),
    "catboost": dict(iterations=500, learning_rate=.04, depth=6,
                     l2_leaf_reg=8, loss_function="Logloss", random_seed=SEED,
                     thread_count=THREADS, task_type="CPU",
                     allow_writing_files=False, verbose=False),
    "xgboost": dict(n_estimators=500, learning_rate=.04, max_depth=5,
                    min_child_weight=20, reg_lambda=12, subsample=.85,
                    colsample_bytree=.85, tree_method="hist",
                    enable_categorical=True, eval_metric="logloss",
                    n_jobs=THREADS, random_state=SEED),
    "spline_logistic": dict(C=.1, solver="lbfgs", max_iter=1500,
                            random_state=SEED),
}

GROUP_NOTES = {
    "g1_temporal": {
        "status": "available",
        "definition": "avg3/avg6/lifetime ratios and differences for mou/qty/rev; "
                      "mou_Mean and rev_Mean versus avg3 are explicitly undated comparisons",
        "window_caveat": "avg3=3 months; avg6=6 months; _Mean window unspecified. "
                         "No inferred 3/4-month _Mean, time-normalized acceleration, "
                         "or reinterpretation of change_* percentages as absolute changes.",
    },
    "g2_range": {"status": "unavailable", "reason": "Neither supplied CSV contains "
                 "_Range columns; totmrc_Range, ovrrev_Range, mou_Range cannot be tested. "
                 "No invented fields or reconstructed volatility."},
    "g3_billing_gaps": {"status": "available", "definition":
                        "totrev-adjrev; totmou-adjmou; totcalls-adjqty"},
    "g4_call_care": {"status": "available", "definition":
                     "comp_vce_Mean/(plcd_vce_Mean+.5); "
                     "inonemin_Mean/(complete_Mean+.5); "
                     "ccrndmou_Mean/(custcare_Mean+.1)"},
    "g5_equipment_cycle": {"status": "available", "definition":
                           "retain v1's valid eqpdays/(30.4375*max(months,1)), without duplicating it; "
                           "add valid eqpdays/max(phones,1), months%12, and "
                           "hnd_price exact observed price tiers, m=50 encoding. "
                           "Every training value is inner-OOF; inference maps fit training only."},
    "g6_tenure_pricing": {"status": "available", "definition":
                          "nonnegative totmrc_Mean/max(tenure-decile train median,1); "
                          "tenure quantile edges, missing-tenure fill and price medians "
                          "fit exclusively on the current fitting rows"},
}


@dataclass(frozen=True)
class Recipe:
    backend: str = "lgbm"
    groups: tuple[str, ...] = ()
    drop: tuple[str, ...] = ()
    sensitive: bool = False
    value_weighted: bool = False


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
        return f"r{self.repeat}_f{self.number}"


def _clean(value):
    if isinstance(value, dict):
        return {str(k): _clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_clean(v) for v in value]
    if isinstance(value, np.ndarray):
        return _clean(value.tolist())
    if isinstance(value, np.generic):
        return _clean(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def _digest(value):
    return hashlib.sha256(json.dumps(_clean(value), sort_keys=True).encode()).hexdigest()


def _indices_hash(indices):
    return hashlib.sha256(np.asarray(indices, dtype="<i8").tobytes()).hexdigest()


def _file_hash(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


class Artifacts:
    """Atomic completion markers; rerunning the identical command resumes fits."""

    def __init__(self, directory):
        self.directory = Path(directory).resolve()
        work = common.WORK.resolve()
        if self.directory == work or work not in self.directory.parents:
            raise ValueError("Artifacts must be in a dedicated child of v2_work")
        self.directory.mkdir(parents=True, exist_ok=True)
        for name in ("cache", "folds", "oof"):
            (self.directory / name).mkdir(exist_ok=True)

    def path(self, relative):
        target = (self.directory / relative).resolve()
        if self.directory not in target.parents:
            raise ValueError("Artifact path escapes the experiment directory")
        return target

    def replace(self, temporary, target):
        # Windows readers can briefly lock an otherwise writable destination.
        for attempt in range(8):
            try:
                os.replace(temporary, target)
                return
            except PermissionError as error:
                if os.name != 'nt' or getattr(error, 'winerror', None) not in (5, 32, 33) or attempt == 7:
                    raise
                time.sleep(.02 * 2 ** attempt)

    def json(self, relative, value):
        target = self.path(relative)
        temporary = target.with_name(target.name + ".tmp")
        temporary.write_text(json.dumps(_clean(value), indent=2, allow_nan=False),
                             encoding="utf-8")
        self.replace(temporary, target)

    def read_json(self, relative):
        return json.loads(self.path(relative).read_text(encoding="utf-8"))

    def npz(self, relative, **arrays):
        target = self.path(relative)
        temporary = target.with_name(target.name + ".tmp")
        with temporary.open("wb") as handle:
            np.savez_compressed(handle, **arrays)
        self.replace(temporary, target)

    def table(self, relative, records):
        frame = records if isinstance(records, pd.DataFrame) else pd.DataFrame(records)
        target = self.path(relative + ".csv")
        temporary = target.with_name(target.name + ".tmp")
        frame.to_csv(temporary, index=False, float_format="%.12g")
        self.replace(temporary, target)
        self.json(relative + ".json", frame.to_dict(orient="records"))

    def bind(self, metadata):
        path = self.path("run_spec.json")
        if path.exists():
            previous = self.read_json("run_spec.json")
            if previous != _clean(metadata):
                raise RuntimeError("Resume specification/data/code mismatch. Use a new "
                                   "v2_work output directory; existing results were not changed.")
        else:
            self.json("run_spec.json", metadata)


def non_test_pool(data, splits):
    """Discard forbidden partitions before any feature or model function is called."""
    if len(splits["train"]) != 60000 or len(splits["validation"]) != 15000:
        raise AssertionError("Original 60k/15k training partitions required")
    keep = np.r_[splits["train"], splits["validation"]].astype(int)
    forbidden = np.r_[splits["calibration_policy"], splits["test"]]
    if len(np.unique(keep)) != 75000 or np.intersect1d(keep, forbidden).size:
        raise AssertionError("Non-test pool is not exactly original train+validation")
    pool = data.iloc[keep].copy().reset_index(drop=True)
    if not pool.Customer_ID.is_unique or not set(pool.churn.unique()) <= {0, 1}:
        raise AssertionError("Unique customers and binary targets required")
    pool["_original_partition"] = np.r_[np.repeat("train", 60000),
                                        np.repeat("validation", 15000)]
    return pool


def outer_folds(y):
    y = np.asarray(y)
    for repeat in range(REPEATS):
        splitter = StratifiedKFold(FOLDS, shuffle=True, random_state=SEED + repeat)
        for number, (train, test) in enumerate(splitter.split(np.zeros(len(y)), y)):
            development, calibration = train_test_split(
                train, test_size=.20, stratify=y[train],
                random_state=SEED + 1000 + repeat * FOLDS + number)
            yield Fold(repeat, number, np.sort(train), np.sort(test),
                       np.sort(development), np.sort(calibration))


def corrected_interval(differences, ratios, folds=FOLDS):
    """Paired intervals, never an IID bootstrap over repeated folds."""
    difference = np.asarray(differences, dtype=float)
    ratio = np.broadcast_to(np.asarray(ratios, dtype=float), difference.shape)
    valid = np.isfinite(difference) & np.isfinite(ratio)
    if not valid.all() or len(difference) < 2:
        return dict(n_pairs=len(difference), mean=None, lower=None, upper=None,
                    corrected_se=None, test_train_ratio=None, df=folds - 1,
                    complete=False)
    variance = float(np.var(difference, ddof=1))
    correction = 1 / len(difference) + float(np.mean(ratio))
    standard_error = float(np.sqrt(correction * variance))
    degrees = min(folds - 1, len(difference) - 1)
    margin = float(student_t.ppf(.975, degrees) * standard_error)
    mean = float(difference.mean())
    return dict(n_pairs=len(difference), mean=mean, lower=mean - margin,
                upper=mean + margin, corrected_se=standard_error,
                test_train_ratio=float(ratio.mean()), df=degrees, complete=True)


def _price_keys(series):
    # Price is already a discrete observed field, not a learned/external tier scheme.
    return pd.to_numeric(series, errors="coerce").map(
        lambda value: "__MISSING__" if pd.isna(value) else format(float(value), ".12g"))


def m_estimate_map(keys, y, m=M_ESTIMATE):
    y = np.asarray(y, dtype=float)
    prior = float(y.mean())
    aggregate = pd.DataFrame({"key": np.asarray(keys), "y": y}).groupby("key").y.agg(
        ["sum", "count"])
    return ((aggregate["sum"] + m * prior) / (aggregate["count"] + m)).to_dict(), prior


def oof_m_estimate(keys, y, seed=SEED, folds=INNER_FOLDS):
    keys, y = pd.Series(keys).reset_index(drop=True), np.asarray(y)
    output = np.full(len(y), np.nan)
    splitter = StratifiedKFold(folds, shuffle=True, random_state=seed)
    for train, heldout in splitter.split(np.zeros(len(y)), y):
        mapping, prior = m_estimate_map(keys.iloc[train], y[train])
        output[heldout] = keys.iloc[heldout].map(mapping).fillna(prior)
    assert np.isfinite(output).all()
    return output


def tenure_pricing(data, train):
    tenure = pd.to_numeric(data.months, errors="coerce")
    fit_tenure = tenure.iloc[train].dropna()
    fill = float(fit_tenure.median()) if len(fit_tenure) else 0.0
    edges = (np.unique(np.quantile(fit_tenure, np.arange(.1, 1, .1)))
             if len(fit_tenure) else np.array([], dtype=float))
    bins = np.searchsorted(edges, tenure.fillna(fill).to_numpy(), side="right")
    price = pd.to_numeric(data.totmrc_Mean, errors="coerce").clip(lower=0)
    fit_price = price.iloc[train]
    fallback = float(fit_price.median()) if fit_price.notna().any() else 0.0
    medians = pd.DataFrame({"bin": bins[train], "price": fit_price.to_numpy()}).groupby(
        "bin").price.median().dropna().to_dict()
    denominator = pd.Series(bins).map(medians).fillna(fallback).clip(lower=1)
    feature = price.to_numpy() / denominator.to_numpy()
    return feature, dict(tenure_edges=edges, tenure_fill=fill,
                         price_medians=medians, fallback_price_median=fallback)


def design(data, train, predict, recipe):
    """Build fit-local features, including cross-fitted target encoding."""
    if "_original_partition" in data:
        source = data.drop(columns="_original_partition")
    else:
        source = data
    X, cats = common.operational_features(source, np.asarray(train))
    if len(X.columns) != 87:
        raise AssertionError("Frozen operational_features must reproduce exactly 87 columns")
    base = X.columns.tolist()
    metadata = {"base_features": base, "category_vocabularies":
                {c: X[c].cat.categories.tolist() for c in cats}, "feature_statistics": {}}
    for group in recipe.groups:
        if group not in AVAILABLE_GROUPS:
            raise ValueError(f"Unavailable or unknown feature group: {group}")
        if group == "g1_temporal":
            for kind in ("mou", "qty", "rev"):
                recent, six, lifetime = (source[f"avg3{kind}"], source[f"avg6{kind}"],
                                         source[f"avg{kind}"])
                X[f"g1_{kind}_3_minus_6"] = recent - six
                X[f"g1_{kind}_3_minus_lifetime"] = recent - lifetime
                # Revenue/usage ratios are already in v1; avoid duplicate additions.
                if kind == "qty":
                    X["g1_qty_3_to_6"] = recent / six.clip(lower=1)
                    X["g1_qty_3_to_lifetime"] = recent / lifetime.clip(lower=1)
                if kind in ("mou", "rev"):
                    X[f"g1_{kind}_unspecified_mean_minus_3"] = source[f"{kind}_Mean"] - recent
                    X[f"g1_{kind}_unspecified_mean_to_3"] = source[f"{kind}_Mean"] / recent.clip(lower=1)
        elif group == "g3_billing_gaps":
            for left, right in (("totrev", "adjrev"), ("totmou", "adjmou"), ("totcalls", "adjqty")):
                X[f"g3_{left}_minus_{right}"] = source[left] - source[right]
        elif group == "g4_call_care":
            X["g4_completion_ratio"] = source.comp_vce_Mean / (source.plcd_vce_Mean + .5)
            X["g4_short_inbound_ratio"] = source.inonemin_Mean / (source.complete_Mean + .5)
            X["g4_care_minutes_per_call"] = source.ccrndmou_Mean / (source.custcare_Mean + .1)
        elif group == "g5_equipment_cycle":
            days = source.eqpdays.where(source.eqpdays >= 0)
            # The months-relative equipment ratio already exists among v1's 87.
            X["g5_equipment_days_per_phone"] = days / source.phones.clip(lower=1)
            X["g5_months_mod_12"] = source.months % 12
            keys = _price_keys(source.hnd_price)
            mapping, prior = m_estimate_map(keys.iloc[train], source.churn.iloc[train])
            X["g5_hnd_price_oof_m50"] = keys.map(mapping).fillna(prior).to_numpy()
            X.iloc[train, X.columns.get_loc("g5_hnd_price_oof_m50")] = oof_m_estimate(
                keys.iloc[train], source.churn.iloc[train].to_numpy())
            metadata["feature_statistics"]["hnd_price_encoding"] = {
                "m": M_ESTIMATE, "mapping": mapping, "prior": prior,
                "training_values": "3-fold inner-OOF, including when fit is itself an inner fold"}
        elif group == "g6_tenure_pricing":
            feature, statistics = tenure_pricing(source, train)
            X["g6_tenure_relative_recurring_price"] = feature
            metadata["feature_statistics"]["tenure_pricing"] = statistics
    if recipe.sensitive:
        for column in ("asl_flag", "area"):
            values = source[column].fillna("__MISSING__").astype(str)
            vocabulary = sorted(values.iloc[train].unique())
            X[column] = pd.Categorical(values, categories=vocabulary)
            cats.append(column)
            metadata["category_vocabularies"][column] = vocabulary
    X = X.drop(columns=list(recipe.drop))
    cats = [c for c in cats if c in X]
    numeric = [c for c in X if c not in cats]
    X[numeric] = X[numeric].replace([np.inf, -np.inf], np.nan).astype("float32")
    if not recipe.sensitive and {"asl_flag", "area"}.intersection(X):
        raise AssertionError("Sensitive attributes leaked into deployable features")
    metadata["features"] = X.columns.tolist()
    metadata["categorical_features"] = cats
    return X.iloc[train].copy(), X.iloc[predict].copy(), cats, metadata


def model_spec(backend, smoke=False):
    specification = MODEL_SPECS[backend].copy()
    if smoke:
        if backend == "lgbm":
            specification.update(n_estimators=8, num_leaves=7, min_child_samples=5)
        elif backend == "catboost":
            specification.update(iterations=8, depth=3)
        elif backend == "xgboost":
            specification.update(n_estimators=8, max_depth=3, min_child_weight=2)
        else:
            specification["max_iter"] = 200
    return specification


class TrainQuantileSplines(TransformerMixin, BaseEstimator):
    """SplineTransformer with train quantile knots, robust to ties/constants.

    Sparse/binary billing and missingness fields have tied quantiles. Using an
    unmodified five-knot quantile spline can yield degenerate BSplines. We retain
    unique TRAIN quantiles per feature; constant columns stay at the fitted value.
    This is a fixed preprocessing rule, not an outer-data-driven model choice.
    """

    def __init__(self, n_knots=5, degree=3):
        self.n_knots, self.degree = n_knots, degree

    def fit(self, X, y=None):
        X = np.asarray(X, dtype=float)
        self.n_features_in_ = X.shape[1]
        self.transformers_, self.quantile_knots_ = [], []
        for column in range(self.n_features_in_):
            knots = np.unique(np.quantile(X[:, column], np.linspace(0, 1, self.n_knots)))
            self.quantile_knots_.append(knots)
            transformer = None
            if len(knots) > 1:
                transformer = SplineTransformer(knots=knots.reshape(-1, 1), degree=self.degree,
                                                include_bias=False, extrapolation="constant",
                                                sparse_output=True).fit(X[:, [column]])
            self.transformers_.append(transformer)
        return self

    def transform(self, X):
        X = np.asarray(X, dtype=float)
        if X.shape[1] != self.n_features_in_:
            raise ValueError("Spline input feature count changed")
        blocks = [transformer.transform(X[:, [column]]) if transformer is not None
                  else sparse.csr_matrix(np.full((len(X), 1), self.quantile_knots_[column][0]))
                  for column, transformer in enumerate(self.transformers_)]
        return sparse.hstack(blocks, format="csr")


def spline_pipeline(X, cats, specification, smoke=False):
    numeric = [c for c in X if c not in cats]
    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median", add_indicator=True,
                                 keep_empty_features=True)),
        ("spline", TrainQuantileSplines(n_knots=3 if smoke else 5, degree=3)),
        ("scale", StandardScaler(with_mean=False)),
    ])
    preprocessing = ColumnTransformer([
        ("numeric", numeric_pipeline, numeric),
        ("category", OneHotEncoder(handle_unknown="ignore", min_frequency=25,
                                   sparse_output=True), cats),
    ], sparse_threshold=1.0)
    return Pipeline([("preprocessing", preprocessing),
                     ("model", LogisticRegression(**specification))])


def fit_blend(oof_probabilities, y):
    probabilities, y = np.asarray(oof_probabilities), np.asarray(y)
    logits = logit(np.clip(probabilities, 1e-6, 1 - 1e-6))
    n_models = logits.shape[1]

    def objective(weights):
        score = logits @ weights
        loss = float(np.mean(np.logaddexp(0, score) - y * score))
        gradient = logits.T @ (expit(score) - y) / len(y)
        return loss, gradient

    result = minimize(objective, np.full(n_models, 1 / n_models), jac=True,
                      method="SLSQP", bounds=[(0, 1)] * n_models,
                      constraints=[{"type": "eq", "fun": lambda w: w.sum() - 1,
                                    "jac": lambda w: np.ones_like(w)}],
                      options={"maxiter": 200, "ftol": 1e-10})
    if not result.success or abs(result.x.sum() - 1) > 1e-6 or result.x.min() < -1e-8:
        raise RuntimeError(f"Constrained OOF blending failed: {result.message}")
    weights = np.clip(result.x, 0, 1)
    return weights / weights.sum(), {"optimizer": "SLSQP", "objective": "OOF log loss",
                                    "iterations": int(result.nit), "success": True}


def blend_predict(probabilities, weights):
    return expit(logit(np.clip(probabilities, 1e-6, 1 - 1e-6)) @ weights)


def weighted_losses(y, probability, weight, mask):
    y, probability, weight, mask = map(np.asarray, (y, probability, weight, mask))
    if not mask.any() or weight[mask].sum() <= 0:
        return np.nan, np.nan
    p, target, w = np.clip(probability[mask], 1e-6, 1 - 1e-6), y[mask], weight[mask]
    brier = float(np.average((target - p) ** 2, weights=w))
    loss = float(np.average(-(target * np.log(p) + (1 - target) * np.log1p(-p)), weights=w))
    return brier, loss


def calibrated_predictions(raw_calibration, y_calibration, raw_outer,
                           value_calibration, value_outer):
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always", ConvergenceWarning)
        calibrator = common.Calibrator("sigmoid").fit(raw_calibration, y_calibration)
    calibration_converged = not any(issubclass(w.category, ConvergenceWarning) for w in recorded)
    calibration_probability = calibrator.predict(raw_calibration)
    outer_probability = calibrator.predict(raw_outer)
    sample_prior = float(np.mean(y_calibration))
    pd_calibration = common.shift(calibration_probability, DEPLOYMENT_PRIOR, sample_prior)
    pd_outer = common.shift(outer_probability, DEPLOYMENT_PRIOR, sample_prior)
    calibration_weights = common.weights(y_calibration, DEPLOYMENT_PRIOR,
                                         population=len(y_calibration))
    cutoff = common.cutoff(pd_calibration * value_calibration,
                           calibration_weights, CONTACT_SHARE)
    sample_cutoff = common.cutoff(calibration_probability, np.ones(len(y_calibration)), .1)
    return dict(p_s=outer_probability, p_d=pd_outer,
                score=pd_outer * value_outer, threshold=cutoff,
                sample_risk_threshold=sample_cutoff, sample_prior=sample_prior,
                calibration_slope=float(calibrator.model.coef_[0, 0]),
                calibration_intercept=float(calibrator.model.intercept_[0]),
                calibration_converged=calibration_converged,
                calibration_method="fixed sigmoid; inner held-out calibration slice")


def measure(fold, y, raw, prediction, value, baseline_tail=None):
    weight = common.weights(y, DEPLOYMENT_PRIOR, population=len(y))
    own = prediction["score"] >= prediction["threshold"]
    shared = own if baseline_tail is None else np.asarray(baseline_tail)
    own_brier, own_loss = weighted_losses(y, prediction["p_d"], weight, own)
    shared_brier, shared_loss = weighted_losses(y, prediction["p_d"], weight, shared)
    sample_tail = prediction["p_s"] >= prediction["sample_risk_threshold"]
    sample_brier, sample_loss = weighted_losses(y, prediction["p_s"], np.ones(len(y)), sample_tail)
    brier, loss = weighted_losses(y, prediction["p_s"], np.ones(len(y)), np.ones(len(y), bool))
    weighted_brier, weighted_loss = weighted_losses(y, prediction["p_d"], weight, np.ones(len(y), bool))
    churn_value = weight * np.asarray(y) * value
    denominator = churn_value.sum()
    metrics = dict(repeat=fold.repeat, fold=fold.number, train_n=len(fold.train),
                   heldout_n=len(fold.test), development_n=len(fold.development),
                   calibration_n=len(fold.calibration), auc=float(roc_auc_score(y, raw)),
                   calibrated_auc=float(roc_auc_score(y, prediction["p_s"])),
                   sample_brier=brier, sample_logloss=loss,
                   deployment_weighted_brier=weighted_brier,
                   deployment_weighted_logloss=weighted_loss,
                   baseline_tail_brier=shared_brier, baseline_tail_logloss=shared_loss,
                   own_tail_brier=own_brier, own_tail_logloss=own_loss,
                   sample_risk_tail_brier=sample_brier, sample_risk_tail_logloss=sample_loss,
                   weighted_value_capture=float(churn_value[own].sum() / denominator)
                   if denominator > 0 else np.nan,
                   weighted_contact_share=float(weight[own].sum() / weight.sum()),
                   raw_contacts=int(own.sum()), baseline_tail_n=int(shared.sum()),
                   threshold=prediction["threshold"], sample_prior=prediction["sample_prior"],
                   calibration_slope=prediction["calibration_slope"],
                   calibration_intercept=prediction["calibration_intercept"])
    return metrics, own, shared


def feature_families(features):
    """Disjoint, exhaustive diagnostic families; omission does not remove proxies."""
    prescribed = {
        "recent_history": "change_mou change_rev avg3mou avg3qty avg3rev avg6mou avg6qty "
                          "avg6rev usage_recent_to_lifetime usage_three_to_six_months "
                          "revenue_recent_to_lifetime revenue_three_to_six_months "
                          "usage_change_scaled revenue_change_scaled",
        "billing_revenue": "rev_Mean totmrc_Mean da_Mean ovrrev_Mean vceovr_Mean datovr_Mean "
                           "roam_Mean totrev adjrev avgrev overage_charge_share recurring_charge_share",
        "usage_volume": "mou_Mean ovrmou_Mean totmou adjmou avgmou",
        "care": "custcare_Mean ccrndmou_Mean cc_mou_Mean care_calls_per_100_attempts",
        "equipment": "new_cell dualband refurb_new hnd_price phones models hnd_webcap "
                     "eqpdays equipment_age_invalid equipment_age_to_tenure",
        "tenure_household": "months uniqsubs actvsubs inactive_household_lines",
    }
    families = {name: tuple(c for c in columns.split() if c in features)
                for name, columns in prescribed.items()}
    assigned = [c for columns in families.values() for c in columns]
    families["calls_network"] = tuple(c for c in features if c not in assigned)
    flattened = [c for columns in families.values() for c in columns]
    assert len(flattened) == len(set(flattened)) == len(features)
    return families


class Runner:
    def __init__(self, data, store, smoke=False):
        self.data, self.store, self.smoke = data, store, smoke
        self.y = data.churn.to_numpy(dtype=int)
        self.started = time.perf_counter()
        self.new_fits, self.cache_hits = 0, 0

    def progress(self, phase, fold=None, **extra):
        self.store.json("progress.json", dict(phase=phase,
                        fold=fold.tag if fold else None, new_fits=self.new_fits,
                        cache_hits=self.cache_hits, current_session_seconds=time.perf_counter() - self.started,
                        decision_allowed=not self.smoke, **extra))

    def fit(self, train, predict, recipe, tag, want_training=False, resubstitution=False):
        train, predict = np.asarray(train), np.asarray(predict)
        if (np.intersect1d(train, predict).size and not resubstitution):
            raise AssertionError("Held-out fit prediction request overlaps fitting rows")
        if recipe.sensitive and not tag.startswith("ceiling/"):
            raise AssertionError("asl_flag/area are permitted ONLY in the diagnostic ceiling")
        specification = model_spec(recipe.backend, self.smoke)
        signature = dict(recipe=asdict(recipe), train_hash=_indices_hash(train),
                         predict_hash=_indices_hash(predict), specification=specification,
                         want_training=want_training, resubstitution=resubstitution)
        key = _digest(signature)
        metadata_name, prediction_name = f"cache/{key}.json", f"cache/{key}.npz"
        if self.store.path(metadata_name).exists() and self.store.path(prediction_name).exists():
            metadata = self.store.read_json(metadata_name)
            if metadata["signature"] != _clean(signature):
                raise RuntimeError("Fit cache signature mismatch")
            with np.load(self.store.path(prediction_name), allow_pickle=False) as arrays:
                result = {name: arrays[name].copy() for name in arrays.files}
            if not np.isfinite(result["raw"]).all() or len(result["raw"]) != len(predict):
                raise RuntimeError("Invalid prediction cache")
            self.cache_hits += 1
            return result, metadata
        self.progress("fitting", tag=tag, recipe=asdict(recipe))
        start = time.perf_counter()
        X_train, X_predict, cats, statistics = design(self.data, train, predict, recipe)
        numeric = [c for c in X_train if c not in cats]
        if recipe.backend == "lgbm":
            from lightgbm import LGBMClassifier
            model = LGBMClassifier(**specification)
        elif recipe.backend == "xgboost":
            from xgboost import XGBClassifier
            model = XGBClassifier(**specification)
        elif recipe.backend == "catboost":
            from catboost import CatBoostClassifier
            # These medians belong to THIS fit, never a global imputer.
            medians = X_train[numeric].median().fillna(0)
            X_train[numeric] = X_train[numeric].fillna(medians)
            X_predict[numeric] = X_predict[numeric].fillna(medians)
            for c in cats:
                X_train[c] = X_train[c].astype(object).where(X_train[c].notna(), "__UNKNOWN__").astype(str)
                X_predict[c] = X_predict[c].astype(object).where(X_predict[c].notna(), "__UNKNOWN__").astype(str)
            statistics["feature_statistics"]["catboost_medians"] = medians.to_dict()
            model = CatBoostClassifier(**specification, cat_features=cats)
        elif recipe.backend == "spline_logistic":
            model = spline_pipeline(X_train, cats, specification, self.smoke)
        else:
            raise ValueError(recipe.backend)
        sample_weight = None
        if recipe.value_weighted:
            if recipe.backend != "lgbm":
                raise ValueError("The weighted challenger is fixed to LightGBM")
            value, value_limits = common.values(self.data, train)
            sample_weight = np.maximum(value[train], 1e-6)
            sample_weight /= sample_weight.mean()
            statistics["feature_statistics"]["value_weight_limits"] = value_limits
            statistics["feature_statistics"]["value_weight_rule"] = "train-only floor/median/p99 V; "
            statistics["feature_statistics"]["value_weight_rule"] += "max(V,1e-6), normalize mean to 1"
        with warnings.catch_warnings(record=True) as recorded, threadpool_limits(limits=THREADS):
            warnings.simplefilter("always", ConvergenceWarning)
            if sample_weight is None:
                model.fit(X_train, self.y[train])
            else:
                model.fit(X_train, self.y[train], sample_weight=sample_weight)
            raw = np.asarray(model.predict_proba(X_predict)[:, 1], dtype=float)
            result = {"raw": raw}
            if want_training:
                result["training_raw"] = np.asarray(model.predict_proba(X_train)[:, 1], dtype=float)
        if recipe.backend == "spline_logistic":
            preprocessing = model.named_steps["preprocessing"]
            numeric_fit = preprocessing.named_transformers_["numeric"]
            statistics["feature_statistics"]["spline_logistic"] = {
                "imputer_medians": numeric_fit.named_steps["imputer"].statistics_,
                "quantile_knots": numeric_fit.named_steps["spline"].quantile_knots_,
                "knot_rule": "unique train quantiles; constants held at fitted value; cubic SplineTransformer",
                "one_hot_categories": preprocessing.named_transformers_["category"].categories_,
                "logistic_iterations": model.named_steps["model"].n_iter_}
        if not all(np.isfinite(array).all() for array in result.values()):
            raise RuntimeError("Model returned non-finite predictions")
        metadata = dict(signature=signature, first_tag=tag, fit_n=len(train),
                        predict_n=len(predict), seconds=time.perf_counter() - start,
                        converged=not any(issubclass(w.category, ConvergenceWarning) for w in recorded),
                        warnings=[str(w.message) for w in recorded], **statistics)
        self.store.npz(prediction_name, **result)
        self.store.json(metadata_name, metadata)  # Completion marker goes LAST.
        self.new_fits += 1
        return result, _clean(metadata)

    def raw_pair(self, fold, recipe, tag):
        is_baseline = recipe == Recipe()
        outer, outer_meta = self.fit(fold.train, fold.test, recipe, tag + "/outer",
                                    want_training=is_baseline)
        calibration, calibration_meta = self.fit(fold.development, fold.calibration,
                                                 recipe, tag + "/calibration")
        return outer["raw"], calibration["raw"], outer_meta, calibration_meta

    def evaluate_arrays(self, fold, name, raw, raw_calibration, recipe,
                        baseline_tail=None, converged=True, save_oof=True, extra=None):
        development_value, development_limits = common.values(self.data, fold.development)
        outer_value, outer_limits = common.values(self.data, fold.train)
        prediction = calibrated_predictions(raw_calibration, self.y[fold.calibration], raw,
                                            development_value[fold.calibration], outer_value[fold.test])
        metrics, own, shared = measure(fold, self.y[fold.test], raw, prediction,
                                      outer_value[fold.test], baseline_tail)
        metrics.update(candidate=name, converged=bool(converged and prediction["calibration_converged"]),
                       calibration_converged=prediction["calibration_converged"],
                       decision_allowed=not self.smoke, sensitive_diagnostic=recipe.sensitive,
                       backend=recipe.backend, groups="|".join(recipe.groups),
                       value_weighted=recipe.value_weighted)
        if save_oof:
            self.store.npz(f"oof/{name}_{fold.tag}.npz",
                           Customer_ID=self.data.Customer_ID.iloc[fold.test].to_numpy(),
                           y=self.y[fold.test], pool_index=fold.test, raw=raw,
                           p_s=prediction["p_s"], p_d=prediction["p_d"],
                           value=outer_value[fold.test],
                           deployment_weight=common.weights(self.y[fold.test], DEPLOYMENT_PRIOR,
                                                            population=len(fold.test)),
                           own_tail=own, baseline_tail=shared)
        self.store.json(f"folds/{name}_{fold.tag}_recipe.json", dict(
            recipe=asdict(recipe), development_value_limits=development_limits,
            outer_training_value_limits=outer_limits,
            calibration_source="20% held-out slice of outer training fold; never original 10k",
            threshold_source="calibrated development-fit predictions on that slice only",
            extra=extra))
        return metrics, own

    def evaluate(self, fold, name, recipe, baseline_tail=None, save_oof=True, tag=None):
        raw, raw_cal, outer_meta, calibration_meta = self.raw_pair(fold, recipe, tag or name)
        metrics, mask = self.evaluate_arrays(
            fold, name, raw, raw_cal, recipe, baseline_tail,
            converged=outer_meta["converged"] and calibration_meta["converged"], save_oof=save_oof)
        return metrics, mask

    def baseline(self, fold):
        return self.evaluate(fold, BASELINE_NAME, Recipe())

    def checkpoint(self, phase, fold, records):
        self.store.table(f"folds/{phase}_{fold.tag}", records)
        self.progress(phase + "_fold_complete", fold)

    def nested_screen(self, fold):
        """Group inclusion uses inner development folds, never outer outcomes."""
        development = fold.development
        splitter = StratifiedKFold(INNER_FOLDS, shuffle=True, random_state=SEED)
        inner = [(development[tr], development[te]) for tr, te in splitter.split(
            np.zeros(len(development)), self.y[development])]
        baseline_aucs, records, selected = [], [], []
        for number, (train, heldout) in enumerate(inner):
            probabilities, _ = self.fit(train, heldout, Recipe(),
                                        f"screen/{fold.tag}/baseline/i{number}")
            baseline_aucs.append(roc_auc_score(self.y[heldout], probabilities["raw"]))
        for group in AVAILABLE_GROUPS:
            differences = []
            for number, (train, heldout) in enumerate(inner):
                probabilities, _ = self.fit(train, heldout, Recipe(groups=(group,)),
                                            f"screen/{fold.tag}/{group}/i{number}")
                differences.append(float(roc_auc_score(self.y[heldout], probabilities["raw"]) -
                                         baseline_aucs[number]))
            positive = float(np.mean(differences)) > 0
            if positive:
                selected.append(group)
            records.append(dict(group=group, inner_paired_auc_mean=float(np.mean(differences)),
                                inner_paired_auc_differences=differences, keep=positive,
                                reason="positive inner paired AUC" if positive else "non-positive inner paired AUC"))
        records.append(dict(group="g2_range", keep=False, reason=GROUP_NOTES["g2_range"]["reason"]))
        self.store.json(f"folds/nested_screen_{fold.tag}.json", dict(
            outer_repeat=fold.repeat, outer_fold=fold.number,
            selection_population="outer development only", development_n=len(development),
            selected_groups=selected, records=records))
        return tuple(selected), inner, records

    def inner_oof(self, fold, inner, backend, groups):
        development = fold.development
        position = {int(row): i for i, row in enumerate(development)}
        probabilities = np.full(len(development), np.nan)
        converged = True
        for number, (train, heldout) in enumerate(inner):
            result, metadata = self.fit(train, heldout, Recipe(backend=backend, groups=groups),
                                        f"blend/{fold.tag}/{backend}/i{number}")
            converged = converged and metadata["converged"]
            probabilities[[position[int(row)] for row in heldout]] = result["raw"]
        assert np.isfinite(probabilities).all()
        return probabilities, bool(converged)


def _stratified_order(indices, y, seed):
    """Nested prefixes, proportionally interleaved and reproducible."""
    rng = np.random.default_rng(seed)
    classes = [rng.permutation(indices[y[indices] == label]) for label in (0, 1)]
    ranks = [(np.arange(len(group)) + .5) / len(group) for group in classes]
    together = np.r_[classes[0], classes[1]]
    return together[np.argsort(np.r_[ranks[0], ranks[1]], kind="stable")]


def run_d1(runner, folds):
    """Measure the frozen baseline noise before any feature/model experiments."""
    records = []
    for fold in folds:
        metrics, _ = runner.baseline(fold)
        records.append(metrics)
        runner.checkpoint("d1", fold, [metrics])
        runner.store.table("baseline_folds", records)
    frame = pd.DataFrame(records)
    interval = corrected_interval(frame.auc, frame.heldout_n / frame.train_n)
    runner.store.table("noise_floor", [dict(
        baseline=BASELINE_NAME, mean_auc=interval["mean"],
        corrected_mean_auc_lower=interval["lower"], corrected_mean_auc_upper=interval["upper"],
        fold_auc_sd=float(frame.auc.std(ddof=1)), corrected_se=interval["corrected_se"],
        test_train_ratio=interval["test_train_ratio"], df=interval["df"],
        repeated_fold_count=len(frame), decision_allowed=not runner.smoke,
        interpretation="baseline variability diagnostic, NOT an unpaired challenger test; "
                       "all model gates later use corrected intervals of paired fold differences")])
    return records


def run_d2(runner, folds, features):
    learning, ablations, baselines, ceiling = [], [], [], []
    families = feature_families(features)
    runner.store.json("feature_families.json", dict(families=families,
                      caveat="disjoint column omission; remaining correlated proxies are not removed"))
    for fold in folds:
        baseline, baseline_tail = runner.baseline(fold)
        baselines.append(baseline)
        order = _stratified_order(fold.train, runner.y, SEED + 2000 + fold.repeat * FOLDS + fold.number)
        if runner.smoke:
            sizes = [max(40, int(len(order) * fraction)) for fraction in (1 / 6, 5 / 12, 5 / 6)]
        else:
            sizes = [10000, 25000, 50000]
        for count in sizes + [len(order)]:
            train = np.sort(order[:count])
            result, metadata = runner.fit(train, fold.test, Recipe(),
                                          f"learning/{fold.tag}/{count}", want_training=True)
            learning.append(dict(repeat=fold.repeat, fold=fold.number,
                                 requested_label=f"smoke_{count}" if runner.smoke else str(count),
                                 training_n=count, heldout_n=len(fold.test),
                                 evaluation="outer_heldout", heldout_auc=float(roc_auc_score(
                                     runner.y[fold.test], result["raw"])),
                                 training_auc=float(roc_auc_score(runner.y[train], result["training_raw"])),
                                 fit_seconds=metadata["seconds"], decision_allowed=not runner.smoke))
        fold_ablation = []
        for family, drop in families.items():
            name = "without_" + family
            metrics, _ = runner.evaluate(fold, name, Recipe(drop=drop), baseline_tail, save_oof=False)
            metrics["family"] = family
            ablations.append(metrics)
            fold_ablation.append(metrics)
        # C4 is not in the candidate pool and never flows into nested screening/blending.
        metrics, _ = runner.evaluate(fold, "diagnostic_ceiling_asl_area", Recipe(sensitive=True),
                                     baseline_tail, save_oof=False, tag="ceiling/asl_area")
        ceiling.append(metrics)
        runner.checkpoint("d2", fold, [baseline] + fold_ablation + [metrics])
        runner.store.table("learning_curve_folds", learning)
        runner.store.table("baseline_folds", baselines)
        runner.store.table("ablation_folds", ablations)
        runner.store.table("diagnostic_ceiling_folds", ceiling)
    # This is deliberately NOT a new CV point with a fictitious 75k holdout.
    all_rows = np.arange(len(runner.data))
    result, metadata = runner.fit(all_rows, all_rows, Recipe(), "learning/final_training_only",
                                  resubstitution=True)
    learning.append(dict(repeat=-1, fold=-1, requested_label="smoke_training_only" if runner.smoke
                         else "final_fit75k_training_only", training_n=len(all_rows), heldout_n=0,
                         evaluation="resubstitution_training_only_NOT_HELDOUT",
                         heldout_auc=np.nan, training_auc=float(roc_auc_score(runner.y, result["raw"])),
                         fit_seconds=metadata["seconds"], decision_allowed=False))
    runner.store.table("learning_curve_folds", learning)
    summary = []
    heldout = pd.DataFrame(learning).query("heldout_n > 0")
    for size, group in heldout.groupby("training_n", sort=True):
        ci = corrected_interval(group.heldout_auc, group.heldout_n / group.training_n)
        summary.append(dict(training_n=int(size), evaluation="outer_heldout",
                            heldout_auc_mean=ci["mean"], lower=ci["lower"], upper=ci["upper"],
                            corrected_se=ci["corrected_se"], df=ci["df"],
                            training_auc_mean=float(group.training_auc.mean()),
                            decision_allowed=not runner.smoke))
    summary.append(dict(training_n=len(all_rows), evaluation="training_only_NOT_HELDOUT",
                        heldout_auc_mean=None, lower=None, upper=None,
                        training_auc_mean=learning[-1]["training_auc"], decision_allowed=False))
    runner.store.table("learning_curve_summary", summary)
    return baselines, ablations, ceiling


def run_d3(runner, folds):
    results = []
    for fold in folds:
        _, baseline_tail = runner.baseline(fold)
        records = []
        for group in AVAILABLE_GROUPS:
            metrics, _ = runner.evaluate(fold, group, Recipe(groups=(group,)), baseline_tail)
            results.append(metrics)
            records.append(metrics)
        runner.checkpoint("d3", fold, records)
        runner.store.table("feature_group_folds", results)
    return results


def run_d4(runner, folds):
    results, screens, blend_rows = [], [], []
    for fold in folds:
        _, baseline_tail = runner.baseline(fold)
        groups, inner, screen = runner.nested_screen(fold)
        screens.extend(dict(repeat=fold.repeat, fold=fold.number, **record) for record in screen)
        inner_results = [runner.inner_oof(fold, inner, backend, groups) for backend in BLEND_MODELS]
        oof = np.column_stack([result[0] for result in inner_results])
        inner_converged = all(result[1] for result in inner_results)
        weights, optimizer = fit_blend(oof, runner.y[fold.development])
        runner.store.npz(f"oof/inner_blend_training_{fold.tag}.npz",
                         pool_index=fold.development,
                         Customer_ID=runner.data.Customer_ID.iloc[fold.development].to_numpy(),
                         y=runner.y[fold.development], probabilities=oof, weights=weights)
        blend_rows.append(dict(repeat=fold.repeat, fold=fold.number,
                               selected_groups="|".join(groups), **dict(zip(BLEND_MODELS, weights)),
                               source="3-fold OOF inside outer development; calibration/outer labels excluded",
                               inner_components_converged=inner_converged,
                               optimizer_iterations=optimizer["iterations"], decision_allowed=not runner.smoke))
        raw_outer, raw_calibration, convergence, records = [], [], [], []
        for backend in BLEND_MODELS:
            recipe = Recipe(backend=backend, groups=groups)
            name = "nested_" + backend
            raw, raw_cal, outer_meta, cal_meta = runner.raw_pair(fold, recipe, name)
            converged = outer_meta["converged"] and cal_meta["converged"]
            metrics, _ = runner.evaluate_arrays(fold, name, raw, raw_cal, recipe, baseline_tail,
                                                converged=converged,
                                                extra={"group_screen": screen})
            results.append(metrics)
            records.append(metrics)
            raw_outer.append(raw)
            raw_calibration.append(raw_cal)
            convergence.append(converged)
        blend_raw = blend_predict(np.column_stack(raw_outer), weights)
        blend_cal = blend_predict(np.column_stack(raw_calibration), weights)
        metrics, _ = runner.evaluate_arrays(fold, "nested_blend", blend_raw, blend_cal,
                                            Recipe(backend="blend", groups=groups), baseline_tail,
                                            converged=all(convergence) and inner_converged,
                                            extra={"weights": dict(zip(BLEND_MODELS, weights)),
                                                   "optimizer": optimizer, "group_screen": screen,
                                                   "inner_components_converged": inner_converged})
        results.append(metrics)
        records.append(metrics)
        metrics, _ = runner.evaluate(fold, "nested_value_weighted_lgbm",
                                     Recipe(groups=groups, value_weighted=True), baseline_tail)
        results.append(metrics)
        records.append(metrics)
        runner.checkpoint("d4", fold, records)
        runner.store.table("model_folds", results)
        runner.store.table("nested_group_screen", screens)
        runner.store.table("blend_weights", blend_rows)
    return results, screens, blend_rows


def paired_tables(baseline_records, candidate_records):
    baseline = pd.DataFrame(baseline_records).set_index(["repeat", "fold"])
    summaries, paired = [], []
    metrics = ("auc", "baseline_tail_brier", "baseline_tail_logloss", "own_tail_brier",
               "own_tail_logloss", "weighted_value_capture", "sample_brier", "sample_logloss")
    for candidate, group in pd.DataFrame(candidate_records).groupby("candidate", sort=True):
        group = group.set_index(["repeat", "fold"]).sort_index()
        if not group.index.is_unique or set(group.index) != set(baseline.index):
            raise AssertionError("Every comparison requires all ten paired outer folds")
        reference = baseline.loc[group.index]
        for metric in metrics:
            difference = group[metric].to_numpy() - reference[metric].to_numpy()
            ratios = group.heldout_n.to_numpy() / group.train_n.to_numpy()
            interval = corrected_interval(difference, ratios)
            summaries.append(dict(candidate=candidate, metric=metric, **interval))
            for i, (repeat, fold) in enumerate(group.index):
                paired.append(dict(candidate=candidate, metric=metric, repeat=repeat, fold=fold,
                                   baseline=float(reference.iloc[i][metric]),
                                   challenger=float(group.iloc[i][metric]), difference=float(difference[i]),
                                   test_train_ratio=float(ratios[i])))
    return summaries, paired


def gate_tables(intervals, candidate_records, smoke=False):
    by_key = {(row["candidate"], row["metric"]): row for row in intervals}
    frame = pd.DataFrame(candidate_records)
    gates = []
    for name, group in frame.groupby("candidate", sort=True):
        auc = by_key[(name, "auc")]
        complete = len(group) == REPEATS * FOLDS and auc["complete"]
        gain = complete and auc["mean"] >= .001 and auc["lower"] > 0
        tail_metrics = ("baseline_tail_brier", "baseline_tail_logloss", "own_tail_brier", "own_tail_logloss")
        tail = all(by_key[(name, metric)]["complete"] and
                   by_key[(name, metric)]["upper"] <= 0 for metric in tail_metrics)
        converged = bool(group.converged.all())
        value = by_key[(name, "weighted_value_capture")]
        weighted_challenger = name == "nested_value_weighted_lgbm"
        # Additional conservative business gate for the explicitly value-weighted challenger.
        value_gate = (not weighted_challenger or
                      (value["complete"] and value["mean"] > 0 and value["lower"] > 0))
        eligible = not bool(group.sensitive_diagnostic.any()) and not name.startswith("without_")
        reasons = []
        for condition, reason in ((complete, "incomplete paired folds"), (gain, "AUC mean/CI gate failed"),
                                  (tail, "weighted tail non-degradation not established"),
                                  (converged, "model convergence warning"),
                                  (value_gate, "weighted value-capture improvement not established"),
                                  (eligible, "diagnostic only"), (not smoke, "smoke is non-decision")):
            if not condition:
                reasons.append(reason)
        gates.append(dict(candidate=name, eligible=eligible, mean_auc_gain=auc["mean"],
                          corrected_auc_lower=auc["lower"], corrected_auc_upper=auc["upper"],
                          auc_gate=bool(gain), weighted_tail_gate=bool(tail),
                          converged=converged, value_gate=bool(value_gate),
                          mean_weighted_value_capture_gain=value["mean"],
                          corrected_value_capture_lower=value["lower"],
                          pass_gate_d=bool(complete and gain and tail and converged and value_gate and eligible and not smoke),
                          decision_allowed=not smoke, reason="; ".join(reasons) or "all preregistered gates passed"))
    return gates


def summarize_groups(intervals, smoke):
    rows = []
    for group in GROUPS:
        if group not in AVAILABLE_GROUPS:
            rows.append(dict(group=group, available=False, keep=False, decision_allowed=False,
                             reason=GROUP_NOTES[group]["reason"]))
            continue
        ci = next(row for row in intervals if row["candidate"] == group and row["metric"] == "auc")
        positive = ci["complete"] and ci["mean"] > 0
        rows.append(dict(group=group, available=True, mean_auc_gain=ci["mean"],
                         corrected_lower=ci["lower"], corrected_upper=ci["upper"],
                         keep=bool(positive and not smoke), positive_cv_signal=bool(positive),
                         decision_allowed=not smoke,
                         reason="positive paired CV signal, not automatic promotion" if positive
                         else "rejected: non-positive paired CV improvement",
                         caveat="global diagnostic summary; nested candidates select inside each outer train"))
    return rows


def selected_recipe(gates, features, screens, smoke):
    passing = [row for row in gates if row["pass_gate_d"]]
    # Fixed tie break: greatest corrected lower bound, greatest mean gain, name.
    passing.sort(key=lambda row: (-row["corrected_auc_lower"], -row["mean_auc_gain"], row["candidate"]))
    selected = passing[0]["candidate"] if passing else BASELINE_NAME
    groups = (selected,) if selected in AVAILABLE_GROUPS else ()
    nested = selected.startswith("nested_")
    backend = (selected.removeprefix("nested_") if nested else "lgbm")
    if backend == "value_weighted_lgbm":
        backend = "lgbm"
    per_fold = [{"repeat": r["repeat"], "fold": r["fold"], "group": r["group"], "keep": r["keep"]}
                for r in screens]
    return dict(selected_candidate=selected, gate_d_passed=bool(passing), decision_allowed=not smoke,
                baseline_retained=not bool(passing), base_features=features,
                selected_feature_groups=list(groups) if not nested else "training-local selection algorithm",
                feature_selection=("On final non-test fitting population, make fixed stratified 80/20 "
                                   "development/calibration split, screen each available group by 3-fold "
                                   "paired OOF AUC on development, retain positive means, then fit with "
                                   "that set. Do not use the globally screened group list as a fixed "
                                   "feature set: the evaluated recipe is this nested selection algorithm."
                                   if nested else "fixed baseline plus listed singleton group, if any"),
                outer_fold_feature_selections=per_fold if nested else [],
                sensitive_features_deployable=False, unavailable_group="g2_range",
                backend=backend, model_specs=MODEL_SPECS,
                blend_components=list(BLEND_MODELS) if backend == "blend" else [],
                blend_rule="nonnegative sum-to-one log-odds weights, fit using development inner-OOF only",
                weighted_training=selected == "nested_value_weighted_lgbm",
                calibration="fixed sigmoid on development-fit predictions for internal held-out calibration",
                value_rule="train-only nonnegative recurring value, median missing fill, p99 clipping",
                threshold_rule="prior-shifted risk*value; weighted10% cutoff from internal held-out calibration",
                final_refit_owner="Main; this workstream never scores original calibration_policy/test",
                final_refit_required=bool(passing),
                learning_curve_75k="baseline training-only diagnostic; not a production model artifact",
                selection_caveat="Gate D intervals are conservative paired, pointwise exploratory intervals, "
                                 "not simultaneous post-model-selection confidence guarantees")


def export_selected_oof(runner, selected, folds):
    records = []
    for fold in folds:
        with np.load(runner.store.path(f"oof/{selected}_{fold.tag}.npz"), allow_pickle=False) as arrays:
            frame = pd.DataFrame({key: arrays[key] for key in
                                  ("Customer_ID", "pool_index", "y", "raw", "p_s", "p_d", "value")})
        frame["repeat"], frame["fold"] = fold.repeat, fold.number
        records.append(frame)
    frame = pd.concat(records, ignore_index=True).sort_values(["repeat", "pool_index"])
    coverage = frame.groupby(["repeat", "pool_index"]).size()
    assert len(frame) == REPEATS * len(runner.data) and (coverage == 1).all()
    runner.store.table("selected_oof_repeated", frame)
    mean = frame.groupby(["pool_index", "Customer_ID", "y"], as_index=False)[["raw", "p_s", "p_d", "value"]].mean()
    mean["n_repeats"] = REPEATS
    mean["purpose"] = "non-test cross-fitted predictions; averaging repeats is not extra independent data"
    runner.store.table("selected_oof_mean", mean)


def package_versions():
    return {name: importlib.metadata.version(name) for name in
            ("numpy", "pandas", "scipy", "scikit-learn", "lightgbm", "catboost", "xgboost", "threadpoolctl")}


def validate_environment():
    actual = Path(sys.executable).resolve()
    if os.path.normcase(str(actual)) != os.path.normcase(str(SHARED_PYTHON.resolve())):
        raise RuntimeError(f"Use only the shared interpreter: {SHARED_PYTHON}")
    if SEED != 20261028 or THREADS != 6:
        raise AssertionError("common must retain SEED=20261028 and six CPU threads")
    selection = json.loads((common.ROOT / "v1_frozen/analysis_outputs/model_selection.json").read_text(encoding="utf-8"))
    if selection["iterations"] != 385 or selection["selected_model"] != "LightGBM wider leaves":
        raise AssertionError("Frozen baseline provenance changed")
    return package_versions()


def run(smoke=False, output=None):
    versions = validate_environment()  # No downloads or dependency installation.
    data, partitions = common.load_data()
    pool = non_test_pool(data, partitions)
    del data, partitions
    if smoke:
        chosen, _ = train_test_split(np.arange(len(pool)), train_size=SMOKE_ROWS,
                                     stratify=pool.churn, random_state=SEED)
        pool = pool.iloc[np.sort(chosen)].reset_index(drop=True)
    folds = list(outer_folds(pool.churn))
    source = pool.drop(columns="_original_partition")
    X, _ = common.operational_features(source, folds[0].train)
    features = X.columns.tolist()
    del X
    frozen_manifest = json.loads((common.ROOT / "v1_frozen/analysis_outputs/feature_manifest.json").read_text(encoding="utf-8"))
    if features != frozen_manifest["features"]:
        raise AssertionError("The baseline feature list differs from the frozen manifest")
    paths = [Path(__file__), Path(common.__file__),
             common.ROOT / "v1_frozen/analysis_pipeline.py",
             common.ROOT / "v1_frozen/analysis_outputs/model_selection.json",
             common.ROOT / "v1_frozen/analysis_outputs/feature_manifest.json",
             common.ROOT / "v1_frozen/analysis_outputs/tables/split_manifest.csv"]
    input_hash = hashlib.sha256(pd.util.hash_pandas_object(pool, index=True).values.tobytes()).hexdigest()
    metadata = dict(schema_version=1, seed=SEED, cpu_threads=THREADS, interpreter=str(SHARED_PYTHON),
                    smoke=smoke, decision_allowed=not smoke, input_rows=len(pool), input_hash=input_hash,
                    source_hashes={str(path): _file_hash(path) for path in paths}, versions=versions,
                    outer_repeats=REPEATS, outer_folds=FOLDS, inner_folds=INNER_FOLDS,
                    model_specs={name: model_spec(name, smoke) for name in BLEND_MODELS},
                    calibration_fraction=.2, contact_share=CONTACT_SHARE,
                    deployment_prior=DEPLOYMENT_PRIOR, group_notes=GROUP_NOTES,
                    interval="corrected t: variance*(1/10+outer test/train=.25), conservative df=4",
                    primary_auc="raw-score sample ROC AUC; calibrated AUC reported separately",
                    primary_tail="Brier/logloss of prior-shifted probabilities on outcome-reweighted "
                                 "outer samples in the baseline-defined nominal weighted10% tail; "
                                 "cutoff comes ONLY from the outer-training internal calibration slice",
                    tail_gate="corrected 95% upper<=0 for paired Brier/logloss degradation on "
                              "baseline-fixed AND own-policy tails; no noninferiority margin",
                    restricted_rows="exact original train+validation only; no original 10k/15k decisions",
                    execution="sequential CPU; fixed specs, no sweeps; predictions cached, models not persisted")
    default = common.WORK / ("d_smoke" if smoke else "d_results")
    store = Artifacts(Path(output) if output else default)
    store.bind(metadata)
    store.json("feature_hypotheses.json", GROUP_NOTES)
    manifest = []
    for fold in folds:
        for kind, rows in (("outer_test", fold.test), ("development", fold.development),
                           ("inner_calibration", fold.calibration)):
            manifest.append(pd.DataFrame({"Customer_ID": pool.Customer_ID.iloc[rows].to_numpy(),
                                          "pool_index": rows, "repeat": fold.repeat,
                                          "fold": fold.number, "role": kind,
                                          "original_partition": pool._original_partition.iloc[rows].to_numpy()}))
    store.table("cv_manifest", pd.concat(manifest, ignore_index=True))
    runner = Runner(pool, store, smoke)
    try:
        with threadpool_limits(limits=THREADS):
            run_d1(runner, folds)
            baselines, ablations, ceiling = run_d2(runner, folds, features)
            groups = run_d3(runner, folds)
            group_intervals, _ = paired_tables(baselines, groups)
            store.table("feature_group_intervals", group_intervals)
            store.table("feature_group_decisions", summarize_groups(group_intervals, smoke))
            models, screens, weights = run_d4(runner, folds)
        candidates = groups + models
        intervals, paired = paired_tables(baselines, candidates + ablations + ceiling)
        gates = gate_tables(intervals, candidates, smoke)
        group_summary = summarize_groups(intervals, smoke)
        store.table("all_fold_metrics", baselines + candidates + ablations + ceiling)
        store.table("paired_fold_differences", paired)
        store.table("paired_corrected_intervals", intervals)
        store.table("feature_group_decisions", group_summary)
        store.table("gate_d", gates)
        ablation_ci = [row for row in intervals if row["candidate"].startswith("without_")]
        ceiling_ci = [row for row in intervals if row["candidate"].startswith("diagnostic_ceiling_")]
        store.table("ablation_summary", ablation_ci)
        store.table("diagnostic_ceiling_summary", ceiling_ci)
        recipe = selected_recipe(gates, features, screens, smoke)
        # Exact feature names, vocabularies and feature statistics are also persisted per fit.
        feature_catalog = {}
        for group in AVAILABLE_GROUPS:
            _, _, _, statistics = design(pool, folds[0].train, folds[0].test, Recipe(groups=(group,)))
            feature_catalog[group] = [c for c in statistics["features"] if c not in features]
        recipe["optional_feature_catalog"] = feature_catalog
        if recipe["selected_candidate"].startswith("nested_"):
            recipe["selected_features_by_outer_fold"] = [dict(
                repeat=fold.repeat, fold=fold.number,
                features=features + [column for record in screens
                    if record["repeat"] == fold.repeat and record["fold"] == fold.number
                    and record["keep"] for column in feature_catalog[record["group"]]])
                for fold in folds]
            recipe["selected_features"] = "training-local; see per-fold lists and final feature-selection rule"
        else:
            recipe["selected_features"] = features + [column
                for group in recipe["selected_feature_groups"] for column in feature_catalog[group]]
        store.json("selected_model_recipe.json", recipe)
        if recipe["gate_d_passed"]:
            export_selected_oof(runner, recipe["selected_candidate"], folds)
        fit_metadata = [json.loads(path.read_text(encoding="utf-8"))
                        for path in store.path("cache").glob("*.json")]
        runtime = dict(current_session_seconds=time.perf_counter() - runner.started,
                       cumulative_completed_fit_seconds=sum(row["seconds"] for row in fit_metadata),
                       completed_unique_fits=len(fit_metadata), new_fits=runner.new_fits,
                       cache_hits=runner.cache_hits, execution="sequential; six CPU threads per fit",
                       decision_allowed=not smoke)
        store.table("fit_runtime", [dict(tag=row["first_tag"], fit_n=row["fit_n"],
                    predict_n=row["predict_n"], seconds=row["seconds"], converged=row["converged"],
                    backend=row["signature"]["recipe"]["backend"],
                    groups="|".join(row["signature"]["recipe"]["groups"]),
                    sensitive_diagnostic=row["signature"]["recipe"]["sensitive"],
                    decision_allowed=not smoke) for row in fit_metadata])
        store.table("runtime_table", [runtime])
        store.json("runtime.json", runtime)
        store.json("summary.json", dict(status="complete", decision_allowed=not smoke,
                   gate_d_passed=recipe["gate_d_passed"], selected_candidate=recipe["selected_candidate"],
                   original_calibration_policy_rows_used=0, original_test_rows_used=0,
                   repeated_oof_rows=REPEATS * len(pool), runtime=runtime,
                   issues=[GROUP_NOTES["g2_range"]["reason"], GROUP_NOTES["g1_temporal"]["window_caveat"],
                           "Final refit/test scoring belongs to Main, conditional on Gate D.",
                           "Training-only 75k baseline learning point is not held-out evidence.",
                           "Corrected intervals are exploratory pointwise, not selection-adjusted.",
                           "48k calibration-source fit versus 60k outer refit can shift calibration."]))
        runner.progress("complete", selected_candidate=recipe["selected_candidate"],
                        gate_d_passed=recipe["gate_d_passed"])
        return recipe
    except Exception as error:
        runner.progress("interrupted_or_failed", error_type=type(error).__name__, error=str(error),
                        recovery="Rerun the identical command; completed atomic fit caches are reused")
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--run", action="store_true", help="Full non-test 2x5 repeated CV; no locked-test scoring")
    modes.add_argument("--smoke", action="store_true", help="All stages on 1000 original non-test rows; NON-DECISION")
    parser.add_argument("--output-dir", type=Path, help="Dedicated child of v2_work; default d_results/d_smoke")
    args = parser.parse_args(argv)
    return run(smoke=args.smoke, output=args.output_dir)


if __name__ == "__main__":
    main()
