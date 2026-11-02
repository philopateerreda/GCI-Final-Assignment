"""C1-C4 preparation: frozen-policy audits and opt-in, non-test proxy CV.

Execution is explicit; importing this module never fits a model. C4 sensitive
ceiling fits belong to workstream D. All generated artifacts stay in v2_work.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

for _variable in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                  "NUMEXPR_NUM_THREADS"):
    os.environ[_variable] = "6"

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, roc_auc_score
from sklearn.model_selection import KFold, StratifiedKFold

try:
    from . import common
except ImportError:
    import common

ROOT, WORK = common.ROOT, common.WORK
SEED, THREADS = common.SEED, common.THREADS
PYTHON = Path("C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe")
BOOTSTRAPS = 300
DEPLOYMENT_PRIOR = 0.02
SAMPLE_THRESHOLD = 0.5
MIN_N, MIN_CLASS = 200, 30
MISSING = "__MISSING__"
ATTRIBUTES = ("income", "ownrent", "marital", "creditcd", "prizm_social_one")
BINARY_CODINGS = {"creditcd": {"N": 0, "Y": 1}, "ownrent": {"R": 0, "O": 1}}
MISSING_TARGET_TOKENS = {"", "NAN", "NONE", "NULL", "<NA>", MISSING}
REQUIRED_SELECTED = ("Customer_ID", "y", "p_s", "p_d", "value", "weight",
                     "selected_risk", "selected_bayes")
PROTOCOL = "C-20261028-fold-local-income-v1"
PROXY_PARAMS = {
    "objective": "binary", "n_estimators": 160, "learning_rate": 0.04,
    "max_depth": 4, "num_leaves": 15, "min_child_samples": 200,
    "subsample": 0.8, "subsample_freq": 1, "colsample_bytree": 0.8,
    "reg_alpha": 1.0, "reg_lambda": 10.0, "class_weight": "balanced",
    "n_jobs": THREADS, "random_state": SEED, "verbosity": -1,
    "deterministic": True, "force_col_wise": True,
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def json_safe(value):
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, np.ndarray)):
        return [json_safe(v) for v in value]
    if isinstance(value, np.generic):
        return json_safe(value.item())
    if isinstance(value, Path):
        return str(value.resolve())
    if value is pd.NA:
        return None
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def write_json(path, value):
    path.write_text(json.dumps(json_safe(value), indent=2, allow_nan=False),
                    encoding="utf-8")


def stable_seed(*parts):
    digest = hashlib.sha256("|".join(map(str, parts)).encode()).digest()
    return (SEED + int.from_bytes(digest[:4], "little")) % (2**32)


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inside_work(path):
    path = path.resolve()
    require(path.is_relative_to(WORK.resolve()), "Artifact paths must stay inside v2_work.")
    return path


def normalize_category(series):
    result = series.astype("string").str.strip().str.upper()
    return result.mask(result.isin(MISSING_TARGET_TOKENS)).fillna(MISSING)


def verified_income(series):
    normalized = normalize_category(series)
    numeric = pd.to_numeric(normalized.mask(normalized.eq(MISSING)), errors="raise")
    known = numeric.dropna().to_numpy(dtype=float)
    require(np.isfinite(known).all(), "Income contains nonfinite nonmissing codes.")
    require(((known >= 1) & (known <= 9) & (known == np.floor(known))).all(),
            "Verify the income schema: expected ordinal codes 1-9, not currency.")
    return numeric.astype(float)


def group_columns(data):
    result = pd.DataFrame(index=data.index)
    income = verified_income(data["income"])
    result["income"] = income.map(lambda x: MISSING if pd.isna(x) else str(int(x)))
    for attribute in ATTRIBUTES[1:]:
        result[attribute] = normalize_category(data[attribute])
    return result


def reference_groups(data, splits):
    # The group vocabulary is fixed from the original 75k, never from test.
    indices = np.concatenate([splits["train"], splits["validation"]])
    groups = group_columns(data.iloc[indices])
    return {attribute: sorted(set(groups[attribute]) | {MISSING})
            for attribute in ATTRIBUTES}


def parse_selection(series, name):
    if pd.api.types.is_bool_dtype(series):
        require(not series.isna().any(), f"{name} contains missing selections.")
        return series.astype(bool)
    text = series.astype("string").str.strip().str.lower()
    coding = {"true": True, "false": False, "1": True, "0": False,
              "1.0": True, "0.0": False}
    require(text.isin(coding).all(), f"{name} must contain explicit booleans or 0/1.")
    return text.map(coding).astype(bool)


def load_selected(data, splits, partition):
    path = WORK / f"a_selected_{partition}.csv"
    require(path.exists(), f"Workstream A must first produce {path}.")
    frame = pd.read_csv(path)
    require(set(REQUIRED_SELECTED).issubset(frame),
            f"{path} must contain {', '.join(REQUIRED_SELECTED)}.")
    require(not frame["Customer_ID"].isna().any() and frame["Customer_ID"].is_unique,
            "Selected-policy Customer_ID must be complete and unique.")
    split_name = "calibration_policy" if partition == "calibration" else "test"
    expected = data.iloc[splits[split_name]].set_index("Customer_ID")
    require(set(frame["Customer_ID"]) == set(expected.index),
            f"{path} must cover exactly the original {split_name} partition.")
    frame = frame.set_index("Customer_ID").loc[expected.index].reset_index()
    for column in ("y", "p_s", "p_d", "value", "weight"):
        frame[column] = pd.to_numeric(frame[column], errors="raise")
        require(np.isfinite(frame[column]).all(), f"{column} must be finite.")
    require(frame["y"].isin([0, 1]).all(), "y must be explicitly coded 0/1.")
    require(np.array_equal(frame["y"].to_numpy(), expected["churn"].to_numpy()),
            "A's outcomes do not match the immutable source partition.")
    for probability in ("p_s", "p_d"):
        require(frame[probability].between(0, 1).all(), f"Invalid {probability}.")
    require(frame["value"].ge(0).all() and frame["weight"].gt(0).all(),
            "Policy value must be nonnegative and deployment weights positive.")
    for policy in ("risk", "bayes"):
        frame[f"selected_{policy}"] = parse_selection(frame[f"selected_{policy}"], policy)
    if "partition" in frame:
        require(frame["partition"].isin([partition, split_name]).all(),
                "A's partition declaration does not match this CLI partition.")
    w, y = frame["weight"].to_numpy(), frame["y"].to_numpy()
    require(np.isclose(np.dot(w, y) / w.sum(), DEPLOYMENT_PRIOR, atol=1e-7),
            "Expected the declared 2% deployment scenario in A's weights.")
    for label in (0, 1):
        class_weights = w[y == label]
        require(len(class_weights) > 0 and np.allclose(class_weights, class_weights[0]),
                "Expected outcome-stratified, constant-within-class deployment weights.")
    for attribute in ATTRIBUTES:
        frame[attribute] = expected[attribute].to_numpy()
    frame["raw_totmrc_Mean"] = expected["totmrc_Mean"].to_numpy()
    return frame, path


def ratio(numerator, denominator):
    return float(numerator / denominator) if denominator > 0 else np.nan


def performance(y, ps, pd_, value, weights, risk, bayes, model_selected):
    result = {}
    for regime, w, probability in (("sample", np.ones(len(y)), ps),
                                    ("deployment", weights, pd_)):
        positive, negative = w * y, w * (1 - y)
        total, pos, neg = w.sum(), positive.sum(), negative.sum()
        result[(regime, "model", "calibration_observed_expected")] = ratio(
            pos, np.dot(w, probability))
        policies = {"model": model_selected, "risk": risk, "bayes": bayes}
        for policy, selected in policies.items():
            result[(regime, policy, "tpr")] = ratio(np.dot(positive, selected), pos)
            result[(regime, policy, "fpr")] = ratio(np.dot(negative, selected), neg)
            result[(regime, policy, "selection_rate")] = ratio(np.dot(w, selected), total)
            if policy != "model":
                result[(regime, policy, "precision")] = ratio(
                    np.dot(positive, selected), np.dot(w, selected))
                result[(regime, policy, "churn_value_capture")] = ratio(
                    np.dot(positive * value, selected), np.dot(positive, value))
        for metric in ("tpr", "fpr", "selection_rate", "precision", "churn_value_capture"):
            result[(regime, "bayes_minus_risk", metric)] = (
                result[(regime, "bayes", metric)] - result[(regime, "risk", metric)])
    return result


def suppression_reason(metric, policy, counts):
    reasons = []
    if counts["n"] < MIN_N:
        reasons.append("n<200")
    if metric in ("tpr", "calibration_observed_expected", "churn_value_capture"):
        if counts["n_positive"] < MIN_CLASS:
            reasons.append("positive_class<30")
    if metric == "fpr" and counts["n_negative"] < MIN_CLASS:
        reasons.append("negative_class<30")
    if metric == "precision":
        policies = ("risk", "bayes") if policy == "bayes_minus_risk" else (policy,)
        for selected_policy in policies:
            if counts[f"n_selected_{selected_policy}"] < MIN_N:
                reasons.append(f"{selected_policy}_selected_n<200")
            if counts[f"n_selected_positive_{selected_policy}"] < MIN_CLASS:
                reasons.append(f"{selected_policy}_selected_positive<30")
            if counts[f"n_selected_negative_{selected_policy}"] < MIN_CLASS:
                reasons.append(f"{selected_policy}_selected_negative<30")
    return ";".join(reasons)


def percentile_ci(values):
    finite = np.asarray(values)[np.isfinite(values)]
    if len(finite) < int(0.9 * BOOTSTRAPS):
        return np.nan, np.nan, len(finite)
    lower, upper = np.quantile(finite, [0.025, 0.975])
    return float(lower), float(upper), len(finite)


def subgroup_audit(frame, universe, partition):
    groups = group_columns(frame)
    records = []
    for attribute in ATTRIBUTES:
        observed = set(groups[attribute])
        # New categories are reported, not merged away or used for decisions.
        for group in sorted(set(universe[attribute]) | observed):
            subset = frame.loc[groups[attribute].eq(group)]
            y = subset["y"].to_numpy(dtype=int)
            ps, pd_ = subset["p_s"].to_numpy(), subset["p_d"].to_numpy()
            value, w = subset["value"].to_numpy(), subset["weight"].to_numpy()
            risk = subset["selected_risk"].to_numpy(dtype=bool)
            bayes = subset["selected_bayes"].to_numpy(dtype=bool)
            model = ps >= SAMPLE_THRESHOLD
            counts = {"n": len(y), "n_positive": int(y.sum()),
                      "n_negative": int((1 - y).sum()),
                      "deployment_mass": float(w.sum()),
                      "deployment_positive_mass": float(np.dot(w, y)),
                      "deployment_negative_mass": float(np.dot(w, 1 - y)),
                      "sample_expected_churn_mass": float(ps.sum()),
                      "deployment_expected_churn_mass": float(np.dot(w, pd_))}
            for policy, selected in (("risk", risk), ("bayes", bayes), ("model", model)):
                counts.update({
                    f"n_selected_{policy}": int(selected.sum()),
                    f"n_selected_positive_{policy}": int(np.dot(y, selected)),
                    f"n_selected_negative_{policy}": int(np.dot(1 - y, selected)),
                    f"deployment_selected_mass_{policy}": float(np.dot(w, selected)),
                    f"deployment_selected_positive_mass_{policy}": float(np.dot(w * y, selected)),
                    f"deployment_selected_negative_mass_{policy}": float(np.dot(w * (1 - y), selected)),
                })
            estimates = performance(y, ps, pd_, value, w, risk, bayes, model)
            keys = list(estimates)
            draws = np.full((BOOTSTRAPS if len(y) else 0, len(keys)), np.nan)
            if len(y):
                rng = np.random.default_rng(stable_seed(partition, attribute, group))
                for replicate in range(BOOTSTRAPS):
                    sample = rng.integers(0, len(y), len(y))
                    metrics = performance(y[sample], ps[sample], pd_[sample], value[sample],
                                          w[sample], risk[sample], bayes[sample], model[sample])
                    draws[replicate] = [metrics[key] for key in keys]
            for column, (regime, policy, metric) in enumerate(keys):
                reason = suppression_reason(metric, policy, counts)
                lower, upper, valid = percentile_ci(draws[:, column])
                if not reason and (not np.isfinite(estimates[(regime, policy, metric)])
                                   or not np.isfinite(lower)):
                    reason = "zero_denominator_or_insufficient_finite_bootstraps"
                suppressed = bool(reason)
                records.append({
                    "partition": partition, "attribute": attribute, "group": group,
                    "is_missing_group": group == MISSING,
                    "absent_group": not len(y), "unseen_in_train_validation": group not in universe[attribute],
                    "regime": regime, "policy": policy, "metric": metric,
                    "estimate": np.nan if suppressed else estimates[(regime, policy, metric)],
                    "ci_low": np.nan if suppressed else lower,
                    "ci_high": np.nan if suppressed else upper,
                    "suppressed": suppressed, "suppression_reason": reason,
                    "small_n": counts["n"] < MIN_N,
                    "small_positive_class": counts["n_positive"] < MIN_CLASS,
                    "small_negative_class": counts["n_negative"] < MIN_CLASS,
                    "bootstrap_replicates": len(draws), "finite_bootstrap_replicates": valid,
                    "sample_model_threshold": SAMPLE_THRESHOLD,
                    "deployment_model_threshold_equivalent": float(common.shift(
                        SAMPLE_THRESHOLD, prior=DEPLOYMENT_PRIOR)),
                    **counts,
                })
    return pd.DataFrame(records)


def weighted_quantile(values, weights, quantile):
    # Inverse empirical CDF for both unit and deployment weights; no interpolation.
    if not len(values) or weights.sum() <= 0:
        return np.nan
    order = np.argsort(values, kind="stable")
    cumulative = np.cumsum(weights[order])
    position = min(np.searchsorted(cumulative, quantile * cumulative[-1], side="left"),
                   len(order) - 1)
    return float(values[order[position]])


def distribution(values, w, selected, income=False):
    finite = np.isfinite(values)
    valid = selected & finite
    v, mass = values[valid], w[valid]
    result = {"selected_mass": float(w[selected].sum()),
              "observed_mass": float(mass.sum()),
              "missing_mass": float(w[selected & ~finite].sum()),
              "mean_ordinal_code" if income else "mean": ratio(np.dot(mass, v), mass.sum()),
              "minimum": float(v.min()) if len(v) else np.nan,
              "maximum": float(v.max()) if len(v) else np.nan}
    if not income:
        result["negative_mass"] = float(w[selected & finite & (values < 0)].sum())
    for q in (0.1, 0.25, 0.5, 0.75, 0.9, 0.99):
        result[f"p{int(q * 100)}"] = weighted_quantile(v, mass, q)
    return result


def equity_audit(frame, universe, partition):
    groups = group_columns(frame)
    records = []
    all_rows = np.ones(len(frame), dtype=bool)
    policies = {"population": all_rows,
                "risk": frame["selected_risk"].to_numpy(dtype=bool),
                "bayes": frame["selected_bayes"].to_numpy(dtype=bool)}
    for regime, w in (("sample", np.ones(len(frame))),
                      ("deployment", frame["weight"].to_numpy())):
        for attribute in ATTRIBUTES:
            for group in sorted(set(universe[attribute]) | set(groups[attribute])):
                member = groups[attribute].eq(group).to_numpy()
                group_mass = w[member].sum()
                measures = {name: {
                    "count": float(w[member & selected].sum()),
                    "share_of_selected": ratio(w[member & selected].sum(), w[selected].sum()),
                    "within_group_selection_rate": ratio(w[member & selected].sum(), group_mass),
                } for name, selected in policies.items()}
                for metric in ("count", "share_of_selected", "within_group_selection_rate"):
                    row = {name: measures[name][metric] for name in policies}
                    records.append({
                        "partition": partition, "section": "category_mix",
                        "attribute": attribute, "group": group, "regime": regime,
                        "metric": metric, **row,
                        "bayes_minus_risk": row["bayes"] - row["risk"],
                        "n_population": int(member.sum()),
                        "n_risk": int((member & policies["risk"]).sum()),
                        "n_bayes": int((member & policies["bayes"]).sum()),
                        "population_mass": float(group_mass),
                        "risk_total_mass": float(w[policies["risk"]].sum()),
                        "bayes_total_mass": float(w[policies["bayes"]].sum()),
                        "small_n": int(member.sum()) < MIN_N,
                        "is_missing_group": group == MISSING,
                        "absent_group": not member.any(),
                        "unseen_in_train_validation": group not in universe[attribute],
                        "interpretation": "exact descriptive mix, not an inferential quality estimate",
                    })
        for column in ("income", "value", "raw_totmrc_Mean"):
            values = (verified_income(frame[column]).to_numpy() if column == "income"
                      else pd.to_numeric(frame[column], errors="raise").to_numpy(dtype=float))
            measures = {name: distribution(values, w, selected, income=column == "income")
                        for name, selected in policies.items()}
            for metric in measures["population"]:
                row = {name: measures[name][metric] for name in policies}
                records.append({
                    "partition": partition, "section": "income_distribution" if column == "income" else "bill_distribution",
                    "attribute": column, "group": "__ALL__", "regime": regime,
                    "metric": metric, **row, "bayes_minus_risk": row["bayes"] - row["risk"],
                    "n_population": len(frame), "n_risk": int(policies["risk"].sum()),
                    "n_bayes": int(policies["bayes"].sum()),
                    "population_mass": float(w.sum()),
                    "risk_total_mass": float(w[policies["risk"]].sum()),
                    "bayes_total_mass": float(w[policies["bayes"]].sum()),
                    "interpretation": ("income is an ordinal 1-9 code, not currency; code means are descriptive"
                                       if column == "income" else
                                       "A's value is training-capped/imputed; raw_totmrc_Mean is unimputed source billing"),
                })
    return pd.DataFrame(records)


def operational_matrix(non_test):
    """Reproduce the frozen row-local 87 features without fitting a vocabulary."""
    manifest_path = ROOT / "v1_frozen/analysis_outputs/feature_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    names, cats = manifest["features"], manifest["categorical_features"]
    require(len(names) == len(set(names)) == 87, "Expected exactly 87 frozen operational features.")
    forbidden = set(manifest["excluded_features"]) | set(ATTRIBUTES) | {"asl_flag", "area"}
    require(not forbidden.intersection(names), "Sensitive targets are prohibited proxy inputs.")
    X = non_test[[name for name in names if name in non_test]].copy()
    X["equipment_age_invalid"] = (X["eqpdays"] < 0).astype("int8")
    X["eqpdays"] = X["eqpdays"].where(X["eqpdays"] >= 0)
    for name, numerator, denominator in (
        ("usage_recent_to_lifetime", "avg3mou", "avgmou"),
        ("usage_three_to_six_months", "avg3mou", "avg6mou"),
        ("revenue_recent_to_lifetime", "avg3rev", "avgrev"),
        ("revenue_three_to_six_months", "avg3rev", "avg6rev"),
        ("overage_charge_share", "ovrrev_Mean", "rev_Mean"),
        ("recurring_charge_share", "totmrc_Mean", "rev_Mean"),
        ("failed_call_index", "drop_blk_Mean", "attempt_Mean"),
        ("usage_change_scaled", "change_mou", "avg3mou"),
        ("revenue_change_scaled", "change_rev", "avg3rev"),
    ):
        X[name] = X[numerator] / X[denominator].clip(lower=1)
    X["care_calls_per_100_attempts"] = 100 * X["custcare_Mean"] / X["attempt_Mean"].clip(lower=1)
    X["equipment_age_to_tenure"] = X["eqpdays"] / (30.4375 * X["months"].clip(lower=1))
    X["inactive_household_lines"] = (X["uniqsubs"] - X["actvsubs"]).clip(lower=0)
    require(set(X) == set(names), "Frozen operational feature contract has changed.")
    X = X[names]
    require(set(cats).issubset(X), "Invalid frozen categorical feature manifest.")
    for column in cats:
        X[column] = X[column].fillna(MISSING).astype(str)
    numeric = [column for column in names if column not in cats]
    X[numeric] = X[numeric].replace([np.inf, -np.inf], np.nan).astype("float32")
    return X, cats, manifest


def proxy_inputs(data, splits):
    indices = np.concatenate([splits["train"], splits["validation"]])
    require(len(indices) == 75000 and not np.intersect1d(indices, splits["test"]).size,
            "Proxy CV must use only the original 60k train + 15k validation.")
    non_test = data.iloc[indices].reset_index(drop=True)
    X, cats, manifest = operational_matrix(non_test)
    targets, descriptions = {}, {}
    for target, coding in BINARY_CODINGS.items():
        normalized = normalize_category(non_test[target])
        counts = normalized.value_counts(dropna=False).to_dict()
        observed = set(normalized) - {MISSING}
        require(observed == set(coding),
                f"Verify {target} before fitting: observed {sorted(observed)}, expected {sorted(coding)}.")
        labels = normalized.map(coding).astype(float)
        require(labels.notna().sum() >= 5 * MIN_N, f"Too few observed {target} targets for five-fold CV.")
        targets[target] = labels
        descriptions[target] = {"observed_values": counts, "coding": coding,
                                "label_definition": "credit-card present (Y=1)" if target == "creditcd" else "home owner (O=1)",
                                "missing_targets_dropped": int(labels.isna().sum())}
    income = verified_income(non_test["income"])
    train_income = verified_income(data.iloc[splits["train"]]["income"])
    require(train_income.notna().any(), "Original 60k train has no observed income.")
    reference = float(train_income.dropna().median())
    require(income.notna().sum() >= 5 * MIN_N, "Too few observed income labels for five-fold CV.")
    targets["income_high"] = income
    descriptions["income_high"] = {
        "observed_values": normalize_category(non_test["income"]).value_counts(dropna=False).to_dict(),
        "coding": {"income>fold_training_median": 1, "income<=fold_training_median": 0},
        "label_definition": "high income ordinal code, strictly above the fold-training observed median",
        "missing_targets_dropped": int(income.isna().sum()),
        "original_60000_train_reference_threshold": reference,
        "reference_high_count_train_validation": int(income.gt(reference).sum()),
        "reference_low_count_train_validation": int(income.le(reference).sum()),
        "reference_threshold_role": "fixed non-test reporting reference only; not the CV target threshold",
        "ties": "median ties are low; labels are not forced to 50/50",
    }
    digest = hashlib.sha256()
    digest.update(json.dumps({"protocol": PROTOCOL, "params": PROXY_PARAMS,
                              "descriptions": descriptions, "features": manifest},
                             sort_keys=True, default=str).encode())
    digest.update(pd.util.hash_pandas_object(X, index=False).to_numpy().tobytes())
    digest.update(pd.util.hash_pandas_object(non_test[["Customer_ID", "creditcd", "ownrent", "income"]],
                                            index=False).to_numpy().tobytes())
    digest.update(pd.util.hash_pandas_object(data.iloc[splits["train"]][["Customer_ID", "income"]],
                                            index=False).to_numpy().tobytes())
    return X, cats, targets, descriptions, digest.hexdigest()


def fold_features(X, cats, train, validation):
    fitted, held = X.iloc[train].copy(), X.iloc[validation].copy()
    unknown_counts = {}
    for column in cats:
        vocabulary = sorted(fitted[column].unique().tolist())
        unknown_counts[column] = int((~held[column].isin(vocabulary)).sum())
        fitted[column] = pd.Categorical(fitted[column], categories=vocabulary)
        held[column] = pd.Categorical(held[column], categories=vocabulary)
    # LightGBM handles numeric NaN natively; no global imputation or label imputation.
    return fitted, held, unknown_counts


def proxy_bootstrap(y, probability, seed):
    rng = np.random.default_rng(seed)
    negative, positive = np.flatnonzero(y == 0), np.flatnonzero(y == 1)
    require(len(positive) and len(negative), "Both explicitly coded classes are required for AUC.")
    draws = np.empty((BOOTSTRAPS, 2))
    for replicate in range(BOOTSTRAPS):
        sample = np.concatenate([rng.choice(negative, len(negative), replace=True),
                                 rng.choice(positive, len(positive), replace=True)])
        draws[replicate, 0] = roc_auc_score(y[sample], probability[sample])
        draws[replicate, 1] = balanced_accuracy_score(y[sample], probability[sample] >= 0.5)
    return np.quantile(draws, [0.025, 0.975], axis=0)


def proxy_metric_row(target, scope, fold, y, probability, description, fingerprint,
                     threshold, n_train, n_train_positive, unknown_counts):
    require(np.isfinite(probability).all(), "Nonfinite out-of-fold proxy probabilities.")
    auc = float(roc_auc_score(y, probability))
    balanced = float(balanced_accuracy_score(y, probability >= 0.5))
    ci = proxy_bootstrap(y, probability, stable_seed("proxy", target, scope, fold))
    return {
        "target": target, "scope": scope, "fold": fold,
        "source_partition": "original_train_60000_plus_validation_15000", "test_used": False,
        "feature_count": 87, "n_folds": 5, "n": len(y),
        "n_positive": int(y.sum()), "n_negative": int((1 - y).sum()),
        "positive_fraction": float(y.mean()), "n_train": n_train,
        "n_train_positive": n_train_positive,
        "n_train_negative": n_train - n_train_positive if np.isfinite(n_train) else np.nan,
        "auc": auc, "auc_ci_low": float(ci[0, 0]), "auc_ci_high": float(ci[1, 0]),
        "baseline_auc": 0.5, "auc_minus_baseline": auc - 0.5,
        "auc_minus_baseline_ci_low": float(ci[0, 0] - 0.5),
        "auc_minus_baseline_ci_high": float(ci[1, 0] - 0.5),
        "balanced_accuracy": balanced, "balanced_accuracy_ci_low": float(ci[0, 1]),
        "balanced_accuracy_ci_high": float(ci[1, 1]), "baseline_balanced_accuracy": 0.5,
        "balanced_accuracy_minus_baseline": balanced - 0.5,
        "balanced_accuracy_minus_baseline_ci_low": float(ci[0, 1] - 0.5),
        "balanced_accuracy_minus_baseline_ci_high": float(ci[1, 1] - 0.5),
        "classification_threshold": 0.5, "fold_training_income_threshold": threshold,
        "original_60000_train_income_reference_threshold": description.get("original_60000_train_reference_threshold", np.nan),
        "label_definition": description["label_definition"],
        "target_coding_json": json.dumps(description["coding"], sort_keys=True),
        "verified_observed_values_json": json.dumps(description["observed_values"], sort_keys=True),
        "missing_targets_dropped": description["missing_targets_dropped"],
        "unseen_fold_validation_categories_json": json.dumps(unknown_counts, sort_keys=True),
        "positive_probability_column": "model.classes_ == 1; never flip/maximize AUC after scoring",
        "model_parameters_json": json.dumps(PROXY_PARAMS, sort_keys=True),
        "bootstrap_replicates": BOOTSTRAPS,
        "ci_interpretation": "descriptive stratified held-out-row bootstrap; models and income thresholds fixed, no refit uncertainty",
        "protocol": PROTOCOL, "cache_fingerprint": fingerprint,
    }


def proxy_cv(X, cats, targets, descriptions, fingerprint):
    # Imported only in the explicit opt-in path; no training on import or smoke.
    from lightgbm import LGBMClassifier

    records = []
    for target, labels in targets.items():
        valid = np.flatnonzero(labels.notna().to_numpy())
        observed_labels = labels.iloc[valid].to_numpy()
        if target == "income_high":
            splitter = KFold(n_splits=5, shuffle=True, random_state=SEED)
            folds = splitter.split(valid)
        else:
            observed_labels = observed_labels.astype(int)
            require(min(np.bincount(observed_labels, minlength=2)) >= 5,
                    f"{target} has too few members of one class for five-fold stratification.")
            splitter = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
            folds = splitter.split(valid, observed_labels)
        oof_probability = np.full(len(valid), np.nan)
        oof_labels = np.full(len(valid), -1, dtype=int)
        fold_thresholds = []
        for fold, (training, held_out) in enumerate(folds, start=1):
            threshold = np.nan
            if target == "income_high":
                threshold = float(np.median(observed_labels[training]))
                # Both labels use only this fold's training threshold. Missing income
                # was removed before splitting, and ties belong to the low class.
                y_train = (observed_labels[training] > threshold).astype(int)
                y_held = (observed_labels[held_out] > threshold).astype(int)
                fold_thresholds.append(threshold)
            else:
                y_train, y_held = observed_labels[training], observed_labels[held_out]
            require(set(np.unique(y_train)) == {0, 1} and set(np.unique(y_held)) == {0, 1},
                    f"{target} fold {fold} lacks a class; do not change labels or tune around this.")
            X_train, X_held, unseen = fold_features(X, cats, valid[training], valid[held_out])
            model = LGBMClassifier(**PROXY_PARAMS)
            model.fit(X_train, y_train, categorical_feature=cats)
            classes = np.asarray(model.classes_)
            require(set(classes.tolist()) == {0, 1}, "Unexpected fitted proxy class coding.")
            positive_column = int(np.flatnonzero(classes == 1)[0])
            probability = model.predict_proba(X_held)[:, positive_column]
            oof_probability[held_out], oof_labels[held_out] = probability, y_held
            records.append(proxy_metric_row(target, "fold", fold, y_held, probability,
                                             descriptions[target], fingerprint, threshold,
                                             len(y_train), int(y_train.sum()), unseen))
        require(np.isfinite(oof_probability).all() and (oof_labels >= 0).all(),
                "Every observed target must have exactly one out-of-fold prediction.")
        pooled = proxy_metric_row(target, "pooled_oof", 0, oof_labels, oof_probability,
                                  descriptions[target], fingerprint, np.nan, np.nan, np.nan, {})
        pooled["fold_income_thresholds_json"] = json.dumps(fold_thresholds)
        pooled["pooled_label_caveat"] = (
            "fold-local income definitions can vary; pooled OOF AUC is descriptive, read fold results too"
            if target == "income_high" else "one explicit binary coding across all folds")
        records.append(pooled)
    return pd.DataFrame(records)


def empty_proxy_table():
    return pd.DataFrame(columns=["target", "scope", "fold", "auc", "auc_ci_low", "auc_ci_high",
                                 "baseline_auc", "balanced_accuracy", "protocol", "cache_fingerprint"])


def load_proxy_cache():
    path = WORK / "c_proxy_cv.csv"
    if not path.exists():
        return empty_proxy_table()
    cached = pd.read_csv(path)
    if cached.empty:
        return cached
    required = {"protocol", "cache_fingerprint", "target", "scope", "fold", "test_used",
                "feature_count", "source_partition", "verified_observed_values_json",
                "target_coding_json", "label_definition", "missing_targets_dropped",
                "original_60000_train_income_reference_threshold", "model_parameters_json",
                "bootstrap_replicates", "baseline_auc", "baseline_balanced_accuracy"}
    require(required.issubset(cached), "Existing c_proxy_cv.csv lacks the verifiable CV cache contract.")
    require(cached["protocol"].eq(PROTOCOL).all() and cached["feature_count"].eq(87).all(),
            "Existing proxy cache uses a different protocol; it must not be silently refitted.")
    require(cached["source_partition"].eq("original_train_60000_plus_validation_15000").all()
            and cached["bootstrap_replicates"].eq(BOOTSTRAPS).all()
            and cached["baseline_auc"].eq(0.5).all()
            and cached["baseline_balanced_accuracy"].eq(0.5).all()
            and cached["model_parameters_json"].map(lambda x: json.loads(x) == PROXY_PARAMS).all(),
            "Existing proxy cache does not match the frozen non-test training/metric contract.")
    require(cached["test_used"].astype(str).str.lower().isin(["false", "0"]).all(),
            "Rejecting a proxy cache that used test.")
    require(len(cached) == 18 and not cached.duplicated(["target", "scope", "fold"]).any(),
            "Expected five fold rows and one pooled row for each of three targets.")
    expected = {(target, "fold", fold) for target in ("creditcd", "ownrent", "income_high") for fold in range(1, 6)}
    expected |= {(target, "pooled_oof", 0) for target in ("creditcd", "ownrent", "income_high")}
    require(set(zip(cached["target"], cached["scope"], cached["fold"])) == expected,
            "Proxy cache fold coverage is incomplete.")
    require(cached["cache_fingerprint"].nunique() == 1, "Proxy cache contains mixed input fingerprints.")
    return cached


def ceiling_bridge(explicit_path=None):
    candidates = ([inside_work(explicit_path)] if explicit_path else
                  [WORK / name for name in ("d_diagnostic_ceiling.csv", "d_sensitive_ceiling.csv",
                                             "d_ceiling.csv", "d_diagnostic_ceiling.json")])
    available = [path for path in candidates if path.exists()]
    if explicit_path:
        require(bool(available), f"D's diagnostic-ceiling output does not exist: {explicit_path}")
    if not available:
        return {"status": "pending_D_outputs", "fit_owner": "D", "C_sensitive_fits": 0,
                "sensitive_columns": ["asl_flag", "area"],
                "boundary": "Separate diagnostic ceiling only; never a deployed-baseline feature or promotion decision.",
                "numerical_claims": [], "sources": []}
    sources = []
    for path in available:
        path = inside_work(path)
        require(path.suffix.lower() in (".csv", ".json"), "Ceiling bridge accepts only local CSV/JSON tables.")
        payload = (pd.read_csv(path).where(lambda x: x.notna(), None).to_dict("records")
                   if path.suffix.lower() == ".csv" else json.loads(path.read_text(encoding="utf-8")))
        sources.append({"path": str(path), "sha256": sha256_file(path), "raw_D_output": json_safe(payload)})
    return {"status": "D_outputs_available_read_only_unverified", "fit_owner": "D", "C_sensitive_fits": 0,
            "sensitive_columns": ["asl_flag", "area"], "sources": sources,
            "boundary": "Quarantined raw D diagnostic results, separate from deployed baseline and proxy CV.",
            "numerical_claims": [],
            "review_required": ["Verify paired non-test CV baseline and explicit asl_flag/area ablations.",
                                "Verify delta-AUC direction, uncertainty, fold protocol and provenance with D.",
                                "Do not use D's test numbers for choices or treat ceiling results as deployable."]}


def governance_text(summary):
    audit = summary.get("audit", {})
    bridge = summary["diagnostic_ceiling"]
    proxy = summary.get("proxy_cv", {})
    source = summary.get("selected_input", {}).get("path", "not available")
    return f"""# Workstream C governance: audited, not a certification

Partition: {summary['partition']}. Smoke fixture/subsample: {summary.get('smoke', False)}.
Selected input: `{source}`. Policy selections are consumed unchanged from A.
Proxy status: {proxy.get('status', 'not_run')}. Ceiling status: {bridge['status']}.

## Mandatory service-fix floor
Any customer with a verified network fault or billing error receives technical or
billing remediation regardless of plan price, estimated income, credit, housing,
marital status, social-group code, model score or proactive-contact selection.
Risk x Value rations only scarce, discretionary proactive outreach. Failure to
select an account never removes access to support, complaint handling, defect
remediation or consent/opt-out protections. This floor is a mandatory launch
requirement, not an implemented service guarantee in this retrospective dataset.

## C1: frozen, post-hoc subgroup diagnostics
Income, ownrent, marital, creditcd and prizm_social_one are audit-only attributes;
none is an input to the deployed baseline. Income is an estimated ordinal 1-9
code, not income in currency. Literal unknown category codes remain visible;
missing groups and groups absent from the audited partition have explicit rows.
Reference categories come from the original 75k train+validation. Newly observed
categories are flagged rather than pooled or hidden. Counts are never suppressed.

Calibration observed/expected is sum(y)/sum(p_s) in the sample and
sum(weight*y)/sum(weight*p_d) in the declared 2% deployment scenario. Ratios
near one do not prove calibration in every score band. The model classification
threshold is the predeclared sample p_s >= 0.5; its Bayes deployment equivalent is
{summary.get('thresholds', {}).get('deployment_equivalent', 'not available')}.
Policy capture TPR/FPR, selection, precision and churn-value capture use A's
frozen risk and Bayes lists, not a classifier threshold or a test-derived budget.
TPR/FPR are conditional-class rates and consequently coincide across these two
regimes under A's constant-within-outcome weights; they are not two independent
replications. A's deployment weights are scenario population mass, not observed
customer counts or demographic prevalence estimates. Deployment interpretation
assumes prior/label shift with stable class-conditional feature and group
distributions; this assumption is not verified by reweighting the sample.

There are {BOOTSTRAPS} paired within-subgroup row bootstrap draws, shared across
both policies, the classifier and both prior regimes. Policy differences are
Bayes minus risk on each identical draw. Weights, predictions and selections
remain fixed. CIs are descriptive percentile intervals, conditional on fitted
models, calibration and cutoffs; they exclude refitting/prior uncertainty and
have no multiplicity adjustment. Point estimates and CIs are suppressed for
n<200; TPR/value-capture/calibration also require >=30 observed positives, FPR
requires >=30 negatives, and precision additionally requires adequate selected
rows and both selected classes. Undefined denominators and inadequate finite
bootstrap coverage are suppressed. Raw counts and scenario masses remain shown.
These are audit diagnostics, not Equal Opportunity or other legal compliance
certification. Suppressed rows: {audit.get('suppressed_metric_rows', 'not available')}.

## C2: recoverability, not deployed sensitive-attribute modeling
An explicit --proxy-cv run fits three diagnostic binary models once, using only
the original 60k train plus 15k validation. It never uses calibration or test for
training or selection. The 87 frozen operational features are the only inputs;
category vocabularies are fitted inside each training fold, unknown held-out
categories become native missing values, and numeric missingness is handled
natively. Missing targets are dropped, not imputed. creditcd maps N=0,Y=1;
ownrent maps R=0,O=1. All observed non-test values must be verified against these
codings before any fit. Positive probabilities are read from classes_==1;
AUC is never flipped after seeing a result, including negative results.

Income's original-60k observed median is a fixed non-test reporting reference.
Every income CV fold independently fits its own observed training median and
codes strictly-above-median as high=1, ties/at-or-below as low=0 on both its train
and held-out rows. Fold-local definitions may differ, so pooled income OOF AUC
is descriptive and must be read with all five fold results. Median ties are not
randomly split to manufacture balanced labels. The reference threshold never
uses test and is not substituted for fold-training thresholds.

The model is fixed regularized small-capacity LightGBM, six threads, seed
20261028, five folds, no hyperparameter search or early-stopping selection.
Training class balancing uses training labels only; balanced accuracy uses the
fixed 0.5 positive-probability cutoff. Constant-score baseline ROC-AUC and
balanced accuracy are 0.5. Paired differences from these constants and 300
stratified held-out-row bootstrap CIs are descriptive, not confidence intervals
for independent refitted folds. Operational proxy recoverability would support
only the caveat that excluding demographic columns reduces direct reliance but
does not guarantee statistical independence; no result is asserted before fit.
Cached CV results are reused, never retrained by a test audit or smoke run.

## C3: exact list-composition shifts
c_equity.csv records population, risk, Bayes and Bayes-minus-risk group counts,
shares and within-group selections in both the unweighted sample and A's
weighted deployment scenario. Denominators are explicit; absent/missing groups
stay visible. Income-code and bill distributions include means, inverse-empirical
CDF quantiles and observed/missing masses. The raw totmrc_Mean distribution is
unimputed and uncapped; A's value distribution is separately labeled as the
training-capped/imputed policy value. Weighted masses can be fractional and
are not raw counts. These are exact retrospective descriptions, not causal
retention, saved revenue, model-quality inference or a parity certification.

## C4: diagnostic ceiling boundary
asl_flag (Account Spending Limit) and area (geographic market) remain governance-
sensitive and prohibited in the deployed baseline and C's proxy features.
D owns all sensitive-ceiling fits. C only attaches local, read-only D results
with hashes, separately quarantined in c_summary.json; it neither validates nor
promotes numerical delta-AUC claims automatically. Pending outputs mean pending,
not zero loss. --bridge-only can attach later D tables without rescoring test.
Main must verify D's paired non-test CV comparison, sensitivity coding and CIs
before citing any ceiling claim. No web citations are fetched or fabricated here.

## Partition and claim boundaries
All policy/model choices are frozen outside test. v1 previously evaluated the
locked 15k test; this historical reuse must remain disclosed. This script guards
against repeating a completed or started C test audit and forbids proxy training
or smoke on test. Test is reporting only, not a source of thresholds, encoders,
feature selection, sensitive ceiling fitting or policy promotion. Risk is not
value or responsiveness; retrospective capture is not saved revenue; sample
and deployment priors are labeled separately. Pilot treatment/control evidence,
service-floor operational enforcement and legal review remain prerequisites to
scaling. Root deliverables and v1_frozen are read-only to this workstream.
"""


def publish_reports(directory, summary, subgroups=None, equity=None, canonical=True):
    if subgroups is not None:
        subgroups.to_csv(directory / "c_subgroup_robustness.csv", index=False)
    if equity is not None:
        equity.to_csv(directory / "c_equity.csv", index=False)
    write_json(directory / "c_summary.json", summary)
    (directory / "c_governance.md").write_text(governance_text(summary), encoding="utf-8")
    if canonical:
        for name in ("c_subgroup_robustness.csv", "c_equity.csv", "c_summary.json", "c_governance.md"):
            require((directory / name).exists(), f"Missing archived report {name}.")
            shutil.copyfile(directory / name, WORK / name)


def attach_bridge(args):
    directory = inside_work(WORK / f"c_{args.partition}")
    summary_path = directory / "c_summary.json"
    require(summary_path.exists(), "Run the partition audit first; bridge-only cannot score or train.")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["diagnostic_ceiling"] = ceiling_bridge(args.ceiling_results)
    latest_path = WORK / "c_summary.json"
    latest = json.loads(latest_path.read_text(encoding="utf-8")) if latest_path.exists() else {}
    publish_reports(directory, summary, canonical=latest.get("partition") == args.partition)
    return summary_path


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--partition", choices=("calibration", "test"), default="calibration")
    result.add_argument("--proxy-cv", action="store_true",
                        help="Opt in once to fixed five-fold proxy fits on the original 75k; reuse an existing matching cache.")
    result.add_argument("--smoke", action="store_true",
                        help="Calibration-only schema/target/cache validation and 512-row audit; never fits, never publishes canonical outputs.")
    result.add_argument("--ceiling-results", type=Path,
                        help="Read-only D CSV/JSON inside v2_work; C never fits sensitive ceilings.")
    result.add_argument("--bridge-only", action="store_true",
                        help="Attach later D outputs to saved reports without reading predictions, rescoring or fitting.")
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    require(Path(sys.executable).resolve() == PYTHON.resolve(),
            f"Use only the explicit interpreter: {PYTHON}")
    require(SEED == 20261028 and THREADS == 6, "Unexpected seed/thread contract in common.py.")
    require(WORK.is_dir(), "v2_work must already exist; never create or modify root assets.")
    require(not (args.partition == "test" and (args.proxy_cv or args.smoke)),
            "Test audits cannot train proxy CV or run smoke. Use calibration for those flags.")
    require(not (args.smoke and args.proxy_cv), "Smoke is fit-free; do not combine it with --proxy-cv.")
    require(not (args.bridge_only and (args.proxy_cv or args.smoke)),
            "Bridge-only cannot train or run smoke.")
    if args.bridge_only:
        path = attach_bridge(args)
        print(f"Updated read-only C4 bridge: {path}")
        return
    directory = inside_work(WORK / ("c_smoke" if args.smoke else f"c_{args.partition}"))
    if args.partition == "test":
        require(not (directory / "c_summary.json").exists()
                and not (directory / "test_audit_started.json").exists(),
                "C test audit is already completed/started. Do not rescore; use --bridge-only for later D outputs.")
    data, splits = common.load_data()
    universe = reference_groups(data, splits)
    frame, selected_path = load_selected(data, splits, args.partition)
    bridge = ceiling_bridge(args.ceiling_results)
    proxy = load_proxy_cache()
    proxy_status = "reused_non_test_cache" if not proxy.empty else "not_run_use_proxy_cv_on_calibration"
    descriptions, fingerprint = {}, None
    if args.proxy_cv or args.smoke:
        X, cats, targets, descriptions, fingerprint = proxy_inputs(data, splits)
        if not proxy.empty:
            require(proxy["cache_fingerprint"].eq(fingerprint).all(),
                    "Proxy inputs/spec differ from the once-run cache. Do not silently refit or chase results.")
        if args.proxy_cv and proxy.empty:
            marker = WORK / "c_proxy_cv_started.json"
            require(not marker.exists(),
                    "Proxy CV was already started without a complete cache. Do not automatically repeat fits; investigate the prior run.")
            with marker.open("x", encoding="utf-8") as handle:
                json.dump({"protocol": PROTOCOL, "cache_fingerprint": fingerprint,
                           "parameters": PROXY_PARAMS, "planned_fits": 15,
                           "source_partition": "original_train_60000_plus_validation_15000",
                           "test_used": False}, handle, indent=2)
            proxy = proxy_cv(X, cats, targets, descriptions, fingerprint)
            proxy.to_csv(WORK / "c_proxy_cv.csv", index=False)
            proxy_status = "completed_once_original_75k"
        elif args.smoke and proxy.empty:
            proxy_status = "smoke_verified_codings_no_fits"
    if not descriptions and not proxy.empty:
        for row in proxy.loc[proxy["scope"].eq("pooled_oof")].to_dict("records"):
            descriptions[row["target"]] = {
                "observed_values": json.loads(row["verified_observed_values_json"]),
                "coding": json.loads(row["target_coding_json"]),
                "label_definition": row["label_definition"],
                "missing_targets_dropped": int(row["missing_targets_dropped"]),
                "verification_source": "once-run original-75k cache, not this audited partition",
            }
            if row["target"] == "income_high":
                descriptions[row["target"]]["original_60000_train_reference_threshold"] = row[
                    "original_60000_train_income_reference_threshold"]
    if not args.smoke and not (WORK / "c_proxy_cv.csv").exists():
        empty_proxy_table().to_csv(WORK / "c_proxy_cv.csv", index=False)
    directory.mkdir(exist_ok=True)
    if args.partition == "test":
        # Exclusive marker is created before metrics, so a failed run cannot be
        # mistaken for permission to inspect/evaluate test a second time.
        with (directory / "test_audit_started.json").open("x", encoding="utf-8") as handle:
            json.dump({"protocol": PROTOCOL, "selected_input": str(selected_path.resolve()),
                       "selected_sha256": sha256_file(selected_path), "seed": SEED}, handle, indent=2)
    if args.smoke:
        frame = frame.sort_values("Customer_ID", kind="stable").iloc[:512].copy()
    subgroups = subgroup_audit(frame, universe, args.partition)
    equity = equity_audit(frame, universe, args.partition)
    unique_groups = subgroups.drop_duplicates(["attribute", "group"])
    pooled = (proxy.loc[proxy["scope"].eq("pooled_oof")].to_dict("records")
              if not proxy.empty else [])
    summary = {
        "protocol": PROTOCOL, "partition": args.partition, "smoke": args.smoke,
        "publishable": not args.smoke, "seed": SEED, "threads": THREADS,
        "interpreter": str(PYTHON), "bootstrap_replicates": BOOTSTRAPS,
        "selected_input": {"path": str(selected_path.resolve()), "sha256": sha256_file(selected_path),
                           "policies": "A selections consumed unchanged; no C cutoff/budget fitting"},
        "thresholds": {"model_sample": SAMPLE_THRESHOLD,
                       "deployment_equivalent": float(common.shift(SAMPLE_THRESHOLD, prior=DEPLOYMENT_PRIOR)),
                       "sample_prior_for_equivalence": common.PRIOR, "deployment_prior": DEPLOYMENT_PRIOR,
                       "classification_rule_used": "p_s >= 0.5, never a policy-capture threshold",
                       "max_A_pd_difference_from_common_shift": float(np.max(np.abs(
                           frame["p_d"].to_numpy() - common.shift(frame["p_s"].to_numpy(), prior=DEPLOYMENT_PRIOR)))),
                       "equivalence_note": "deployment equivalent assumes common.shift; model metrics use the declared sample threshold even if A's mapping differs"},
        "population": {"n": len(frame), "n_positive": int(frame["y"].sum()),
                       "deployment_mass": float(frame["weight"].sum()),
                       "weighted_churn_prior": ratio(np.dot(frame["weight"], frame["y"]), frame["weight"].sum()),
                       "sample_churn_prior_observed": float(frame["y"].mean()),
                       "deployment_mass_note": "A scenario weights, not actual population counts; smoke subset is not renormalized"},
        "audit": {"attributes": list(ATTRIBUTES), "reference_group_source": "original_75k_train_plus_validation",
                  "reference_groups": universe, "metric_rows": len(subgroups),
                  "suppressed_metric_rows": int(subgroups["suppressed"].sum()),
                  "missing_groups": unique_groups.loc[unique_groups["is_missing_group"],
                                                       ["attribute", "group", "n", "n_positive", "n_negative"]].to_dict("records"),
                  "absent_groups": unique_groups.loc[unique_groups["absent_group"], ["attribute", "group"]].to_dict("records"),
                  "new_groups": unique_groups.loc[unique_groups["unseen_in_train_validation"], ["attribute", "group", "n"]].to_dict("records"),
                  "small_n_rule": "n<200; class-specific denominators need >=30; selected precision additionally checked",
                  "counts_never_suppressed": True,
                  "ci_method": "300 paired IID within-group row resamples; fixed A weights, models and lists; percentile 95%, descriptive, no multiplicity correction"},
        "proxy_cv": {"status": proxy_status, "path": str((WORK / "c_proxy_cv.csv").resolve()),
                     "source_partition": "original_train_60000_plus_validation_15000",
                     "test_used": False, "fits_allowed_only_by_proxy_cv": True,
                     "new_fits_this_invocation": 15 if proxy_status == "completed_once_original_75k" else 0,
                     "parameters": PROXY_PARAMS, "target_definitions_verified_non_test": descriptions,
                     "cache_fingerprint": fingerprint if fingerprint else (str(proxy["cache_fingerprint"].iloc[0]) if not proxy.empty else None),
                     "pooled_descriptive_results": pooled,
                     "income_reference_note": "original60k median is a reporting reference; actual target median is fitted within each CV train fold; ties low, no artificial label balancing",
                     "baseline_auc": 0.5, "baseline_balanced_accuracy": 0.5,
                     "auc_orientation": "explicit positive class=1; no post-result flipping",
                     "ci_scope": "descriptive stratified OOF row bootstrap, not model-refit or independent-fold uncertainty"},
        "equity": {"rows": len(equity), "policy_difference": "bayes_minus_risk",
                   "regimes": ["unweighted sample", "A deployment weighted"],
                   "counts_and_differences": "exact descriptive; all population/selection denominators visible",
                   "quantiles": "inverse weighted empirical CDF; same definition with unit sample weights",
                   "bill_columns": {"value": "A training-capped/imputed policy value",
                                    "raw_totmrc_Mean": "unimputed, uncapped source billing"},
                   "income_units": "ordinal estimated-income code 1-9, never dollars",
                   "service_fix_floor": "mandatory remediation of every verified network/billing defect regardless of bill or selection",
                   "claim_word": "audited"},
        "diagnostic_ceiling": bridge,
        "discipline": {"root_edits": False, "sensitive_C_fits": 0, "test_decisions": False,
                       "v1_test_previously_evaluated": True,
                       "test_audit_repetition_guard": "exclusive started marker and archived completed summary; later C4 updates use bridge-only",
                       "causal_retention_claim": False, "citation_verification_owner": "main"},
        "outputs": {"archive_directory": str(directory.resolve()),
                    "subgroups": str((directory / "c_subgroup_robustness.csv").resolve()),
                    "equity": str((directory / "c_equity.csv").resolve()),
                    "summary": str((directory / "c_summary.json").resolve()),
                    "governance": str((directory / "c_governance.md").resolve()),
                    "canonical_note": "top-level requested filenames mirror the latest full audit; partition archives preserve calibration/test separately; smoke never replaces either"},
    }
    publish_reports(directory, summary, subgroups, equity, canonical=not args.smoke)
    if args.smoke:
        # A fit-free smoke report is separate from the once-run shared proxy cache.
        empty_proxy_table().to_csv(directory / "c_proxy_cv.csv", index=False)
    print(f"Wrote C audits to {directory.resolve()}; proxy CV: {proxy_status}.")


if __name__ == "__main__":
    main()
