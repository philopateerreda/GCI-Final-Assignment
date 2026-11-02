"""WP5 implementation; execution is explicit and gated on terminal WP3/WP4.

Only the five authorized two-parameter, calibration-partition sigmoid fits are
new fits. Batch estimation sees score counts, not labels. All bootstrap draws
are exact multinomials; count compression deletes zero-count terms only.
No computation or output writing takes place on import (apart from common's
required runtime guard). New solver-equivalence tests must be run separately.
"""

# The runtime/write guard and numerical thread caps must be installed FIRST.
from common import (
    ADDONS, ROOT, SEED, SAMPLE_PRIOR, BRIEF, rng, write_json, file_info,
    digest, verify_runtime, baseline_inputs, population,
)

import argparse
import ast
from concurrent.futures import ThreadPoolExecutor, as_completed
from hashlib import sha256
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit, logit

from reporting import write_report
from png_drafts import line_plot

TASK_INDEX = 5
TASK_SEED = SEED + TASK_INDEX
TRUE_PRIORS = (.005, .01, .02, .03, .05)
BATCH_SIZES = (5_000, 10_000, 50_000, 100_000)
ORIGINAL_REPLICATES = 500
BOOTSTRAP_REPLICATES = 500
FOLDS = 5
TOLERANCE = 1e-8
MAX_ITERATIONS = 1000
SIGMOID_C = 1000.
SCORE_EPSILON = 1e-6
MAX_WORKERS = 6
BOOTSTRAP_TILE = 50  # <=10k supports: bounded matrices, not batch-size matrices.
LEGACY_SAMPLE_PRIOR = .4956  # Exact defaults in v2, NOT the WP5 EM prior.
CALIBRATION_ROWS = 10_000
PLANNING_ROWS = 75_000
GRID = tuple((prior, n) for prior in TRUE_PRIORS for n in BATCH_SIZES)
OOF_CSV = ADDONS / 'results/wp5_calibration_oof.csv'
OOF_JSON = ADDONS / 'results/wp5_calibration_oof.json'
PRIMARY_JSON = ADDONS / 'results/wp5_label_shift.json'

# Integer codes are saved for every bootstrap fit, including failures.
SOLVER_INTERIOR = 0
SOLVER_LOWER_KKT = 1
SOLVER_UPPER_KKT = 2
SOLVER_FLAT = 3
SOLVER_ITERATION_CAP = 4
SOLVER_NONFINITE = 5
SOLVER_FLAGS = {
    SOLVER_INTERIOR: 'converged interior root',
    SOLVER_LOWER_KKT: 'exact lower endpoint KKT maximizer (0)',
    SOLVER_UPPER_KKT: 'exact upper endpoint KKT maximizer (1)',
    SOLVER_FLAT: 'flat likelihood; nonidentifiable, counted as failure',
    SOLVER_ITERATION_CAP: 'iteration cap; counted as failure',
    SOLVER_NONFINITE: 'nonfinite derivative/information; counted as failure',
}
_WORKER_A = None
_WORKER_SCORES = None
_WORKER_POSITIVE = None
_WORKER_NEGATIVE = None
_WORKER_POSITIVE_PROBABILITY = None
_WORKER_NEGATIVE_PROBABILITY = None


def require_predecessors():
    """Terminal PARTIAL is completion of a job, not acceptance of its evidence."""
    records = []
    for index, filename in ((3, 'wp3_roi_band.json'), (4, 'wp4_protocol.json')):
        result = ADDONS / 'results' / filename
        report = ADDONS / f'reports/WP{index}_report.md'
        if not result.is_file() or not report.is_file():
            raise RuntimeError(f'WP5 not started: WP{index} result and terminal report are required.')
        body = json.loads(result.read_text(encoding='utf-8'))
        status = body.get('status')
        if status not in ('DONE', 'PARTIAL') or f'Status: {status}' not in report.read_text(encoding='utf-8').splitlines():
            raise RuntimeError(f'WP5 not started: WP{index} result/report lack matching terminal status.')
        records.append(dict(work_package=index, status=status, result=file_info(result),
                            report=file_info(report), acceptance_inherited=False))
    return records


def input_paths(predecessors):
    """Hash opaque model artifacts, never deserialize/import model libraries."""
    paths = [
        ROOT / 'v2_work/a_selected_calibration.csv',
        ROOT / 'v2_work/common.py', ROOT / 'v2_work/workstream_a.py',
        ROOT / 'v2_work/a_spec.json', ROOT / 'v2_work/a_calibrator.joblib',
        ROOT / 'v2_work/final_metrics.json',
        ROOT / 'v1_frozen/analysis_outputs/tables/split_manifest.csv',
        ROOT / 'v1_frozen/analysis_outputs/models/selected_model.joblib',
        ROOT / 'analysis_outputs/model_selection.json',
        ROOT / 'analysis_outputs/feature_manifest.json',
        ROOT / 'analysis_outputs/source_manifest.json',
        ROOT / 'telecom/Record.csv', ROOT / 'references.txt', BRIEF,
        Path(__file__).resolve(), ADDONS / 'src/common.py',
        ADDONS / 'src/reporting.py', ADDONS / 'src/png_drafts.py',
        ADDONS / 'results/wp5_tests.json',
    ] + baseline_inputs()
    for row in predecessors:
        paths.extend(Path(row[key]['path']) for key in ('result', 'report'))
    paths = sorted(set(Path(path).resolve() for path in paths))
    missing = [path.as_posix() for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError('STOP-2: missing read-only WP5 inputs: ' + ', '.join(missing))
    return paths


def input_fingerprint(paths):
    records = [dict(path=Path(path).resolve().as_posix(), sha256=digest(path))
               for path in sorted(set(paths))]
    text = json.dumps(records, sort_keys=True, separators=(',', ':'))
    return sha256(text.encode('utf-8')).hexdigest()


def load_calibration():
    split = pd.read_csv(ROOT / 'v1_frozen/analysis_outputs/tables/split_manifest.csv',
                        usecols=['Customer_ID', 'partition'], dtype={'Customer_ID': 'int64'})
    assert not split.Customer_ID.duplicated().any(), 'Split IDs must be unique.'
    saved = split.loc[split.partition.eq('calibration_policy'), 'Customer_ID'].to_numpy()
    cal = pd.read_csv(ROOT / 'v2_work/a_selected_calibration.csv',
                      usecols=['Customer_ID', 'partition', 'y', 'p_raw', 'p_s', 'value'],
                      dtype={'Customer_ID': 'int64'}, float_precision='round_trip')
    assert len(saved) == len(cal) == CALIBRATION_ROWS, 'Exactly 10k calibration-policy rows required.'
    assert not cal.Customer_ID.duplicated().any(), 'Calibration cache has duplicate IDs.'
    assert np.array_equal(np.sort(cal.Customer_ID.to_numpy()), np.sort(saved)), 'Cache IDs differ from saved calibration_policy IDs.'
    assert cal.partition.eq('calibration_policy').all(), 'Non-calibration rows in cache.'
    cal = cal.sort_values('Customer_ID', kind='stable').reset_index(drop=True)
    labels = cal.y.to_numpy(dtype=float)
    raw = cal.p_raw.to_numpy(dtype=float)
    ps = cal.p_s.to_numpy(dtype=float)
    values = cal.value.to_numpy(dtype=float)
    if not np.isin(labels, (0., 1.)).all() or not 0 < labels.sum() < len(cal):
        raise ValueError('Calibration cache requires binary labels and both classes.')
    # Do not clip raw inputs or intermediate heldout predictions. The only new
    # probability clipping is AFTER the actual training-prior standardization.
    if not np.isfinite(raw).all() or not np.all((raw > 0) & (raw < 1)):
        raise ValueError('Raw probabilities must be strictly inside (0,1) for the unmodified raw-score logit.')
    if not np.isfinite(ps).all() or not np.all((ps >= 0) & (ps <= 1)):
        raise ValueError('Invalid frozen p_s in the planning cache.')
    if not np.isfinite(values).all() or np.any(values < 0):
        raise ValueError('Invalid frozen recurring-value proxy; WP5 does not impute or retune it.')
    allowed = set(split.loc[split.partition.isin(['train', 'validation']), 'Customer_ID'].astype(int))
    assert len(allowed) == PLANNING_ROWS
    assert allowed.isdisjoint(set(saved))
    return cal, allowed


def stratified_fold_assignment(labels):
    """Permutation within label, round-robin assignment; no sklearn imports."""
    labels = np.asarray(labels)
    if labels.ndim != 1 or not np.isin(labels, (0, 1)).all():
        raise ValueError('Fold assignment requires one-dimensional binary labels.')
    generator = rng(TASK_INDEX)
    assignment = np.full(len(labels), -1, dtype=np.int8)
    offset = 0
    for label in (0, 1):
        indices = np.flatnonzero(labels == label)
        if len(indices) < FOLDS:
            raise ValueError('Each label must occur in all five folds.')
        shuffled = generator.permutation(indices)
        assignment[shuffled] = (np.arange(len(indices)) + offset) % FOLDS
        offset += len(indices)
    assert np.all((assignment >= 0) & (assignment < FOLDS))
    return assignment


def sigmoid_loss_gradient(parameters, raw_logit, labels):
    """Sum Bernoulli loss + slope^2/(2*C); intercept is unpenalized."""
    slope, intercept = parameters
    z = slope * raw_logit + intercept
    residual = expit(z) - labels
    loss = np.sum(np.logaddexp(0., z) - labels * z) + slope * slope / (2. * SIGMOID_C)
    gradient = np.array([np.sum(residual * raw_logit) + slope / SIGMOID_C,
                         np.sum(residual)], dtype=float)
    return float(loss), gradient


def fold_sigmoids(cal):
    """Exactly five fits; each score is predicted only when its ID is held out."""
    labels = cal.y.to_numpy(dtype=np.int8)
    raw_logit = logit(cal.p_raw.to_numpy(dtype=float))
    assignment = stratified_fold_assignment(labels)
    output = cal[['Customer_ID', 'y', 'p_raw']].copy()
    output['raw_logit'] = raw_logit
    output['fold'] = assignment
    columns = ('p_s_oof', 'heldout_probability_before_prior_shift', 'slope', 'intercept',
               'fold_training_prevalence', 'prior_intercept_shift', 'standardized_intercept')
    for column in columns:
        output[column] = np.nan
    parameters = []
    predicted = np.zeros(len(cal), dtype=np.int8)
    for fold in range(FOLDS):
        heldout = assignment == fold
        training = ~heldout
        training_prior = float(labels[training].mean())
        result = minimize(sigmoid_loss_gradient, np.array([1., 0.]),
                          args=(raw_logit[training], labels[training].astype(float)),
                          method='L-BFGS-B', jac=True,
                          options=dict(maxiter=MAX_ITERATIONS, maxls=100,
                                       ftol=1e-13, gtol=1e-8))
        if not result.success or not np.isfinite(result.x).all() or not np.isfinite(result.fun):
            raise RuntimeError(f'Authorized fold {fold} sigmoid fit failed: {result.message}')
        slope, intercept = map(float, result.x)
        delta = float(logit(SAMPLE_PRIOR) - logit(training_prior))
        heldout_logit = slope * raw_logit[heldout] + intercept
        before_shift = expit(heldout_logit)  # Not clipped before standardization.
        score = np.clip(expit(heldout_logit + delta), SCORE_EPSILON, 1. - SCORE_EPSILON)
        row_values = (score, before_shift, slope, intercept, training_prior, delta, intercept + delta)
        for column, value in zip(columns, row_values):
            output.loc[heldout, column] = value
        predicted[heldout] += 1
        parameters.append(dict(
            fold=fold, slope=slope, intercept=intercept, training_prevalence=training_prior,
            prior_intercept_shift=delta, standardized_intercept=intercept + delta,
            training_rows=int(training.sum()), heldout_rows=int(heldout.sum()),
            training_positive_rows=int(labels[training].sum()),
            heldout_positive_rows=int(labels[heldout].sum()),
            training_ids=cal.loc[training, 'Customer_ID'].astype(int).tolist(),
            heldout_ids=cal.loc[heldout, 'Customer_ID'].astype(int).tolist(),
            optimizer='scipy.optimize.minimize L-BFGS-B', success=bool(result.success),
            optimizer_iterations=int(result.nit), objective_sum_loss=float(result.fun),
            gradient_max_abs=float(np.max(np.abs(result.jac))), message=str(result.message),
        ))
    assert np.all(predicted == 1), 'Each calibration ID must have exactly one heldout prediction.'
    assert not output[list(columns)].isna().any().any()
    return output, parameters


def validate_folded(frame, cal, parameters):
    if len(frame) != CALIBRATION_ROWS or len(parameters) != FOLDS:
        raise ValueError('Incomplete folded score cache; never resume a partial calibration pool.')
    required = {'Customer_ID', 'y', 'p_raw', 'raw_logit', 'fold', 'p_s_oof', 'slope',
                'intercept', 'fold_training_prevalence', 'prior_intercept_shift',
                'standardized_intercept', 'heldout_probability_before_prior_shift'}
    if not required <= set(frame.columns):
        raise ValueError('Folded score cache schema mismatch.')
    assert not frame.Customer_ID.duplicated().any()
    assert np.array_equal(frame.Customer_ID.to_numpy(), cal.Customer_ID.to_numpy())
    assert np.array_equal(frame.y.to_numpy(), cal.y.to_numpy())
    assert np.array_equal(frame.p_raw.to_numpy(), cal.p_raw.to_numpy())
    labels = cal.y.to_numpy(dtype=np.int8)
    assignment = stratified_fold_assignment(labels)
    assert np.array_equal(frame.fold.to_numpy(), assignment), 'Saved folds are not deterministic SEED+5 stratified folds.'
    raw_logit = logit(cal.p_raw.to_numpy(dtype=float))
    scores = frame.p_s_oof.to_numpy(dtype=float)
    assert np.isfinite(scores).all() and np.all((scores >= SCORE_EPSILON) & (scores <= 1. - SCORE_EPSILON))
    assert np.allclose(frame.raw_logit.to_numpy(), raw_logit, rtol=0., atol=1e-14)
    for fold, row in enumerate(parameters):
        heldout = assignment == fold
        training = ~heldout
        prior = float(labels[training].mean())
        delta = float(logit(SAMPLE_PRIOR) - logit(prior))
        assert row['fold'] == fold and row['success'] is True
        assert row['training_prevalence'] == prior
        assert row['training_ids'] == cal.loc[training, 'Customer_ID'].astype(int).tolist()
        assert row['heldout_ids'] == cal.loc[heldout, 'Customer_ID'].astype(int).tolist()
        assert row['training_rows'] == int(training.sum()) and row['heldout_rows'] == int(heldout.sum())
        expected = np.clip(expit(row['slope'] * raw_logit[heldout] + row['intercept'] + delta),
                           SCORE_EPSILON, 1. - SCORE_EPSILON)
        assert np.allclose(scores[heldout], expected, rtol=0., atol=1e-14)
        for column, value in (('slope', row['slope']), ('intercept', row['intercept']),
                              ('fold_training_prevalence', prior), ('prior_intercept_shift', delta),
                              ('standardized_intercept', row['intercept'] + delta)):
            assert np.allclose(frame.loc[heldout, column].to_numpy(), value, rtol=0., atol=1e-14)


def prepare_folded(cal, inputs, fingerprint):
    identity = dict(script_sha256=digest(__file__), seed=SEED, task_seed=TASK_SEED,
                    input_fingerprint=fingerprint, sample_prior=SAMPLE_PRIOR)
    if OOF_CSV.exists() != OOF_JSON.exists():
        raise RuntimeError('Incomplete OOF CSV/JSON pair; explicit review required, no partial-pool resume.')
    if OOF_CSV.is_file():
        body = json.loads(OOF_JSON.read_text(encoding='utf-8'))
        if body.get('identity') != identity or body.get('artifact', {}).get('sha256') != digest(OOF_CSV):
            raise RuntimeError('OOF cache identity/hash mismatch; refusing stale-score resume or silent overwrite.')
        frame = pd.read_csv(OOF_CSV, dtype={'Customer_ID': 'int64'}, float_precision='round_trip')
        parameters = body['calibrator_parameters']
        validate_folded(frame, cal, parameters)
        return frame, body, True
    frame, parameters = fold_sigmoids(cal)
    validate_folded(frame, cal, parameters)
    frame.to_csv(OOF_CSV, index=False, float_format='%.17g', lineterminator='\n')
    body = write_json('results/wp5_calibration_oof.json', dict(
        status='DONE', identity=identity, artifact=file_info(OOF_CSV),
        calibrator_parameters=parameters, calibration_ids=frame.Customer_ID.astype(int).tolist(),
        fold_assignment='Sorted saved calibration IDs; SEED+5 permutation within label; round-robin with class offsets.',
        objective='sum(logaddexp(0,slope*logit(p_raw)+intercept)-y*(slope*logit(p_raw)+intercept)) + slope^2/(2*1000)',
        prior_standardization='Add logit(.49562)-logit(actual fold-training prevalence) to heldout logit BEFORE clipping.',
        clipping='Only standardized heldout score is clipped to [1e-6,1-1e-6]; raw logits and intermediate probabilities are not clipped.',
        new_fits=FOLDS, base_classifier_refits=0, test_rows_used=0,
    ), __file__, TASK_INDEX, inputs, dict(calibration_policy=CALIBRATION_ROWS, folds=FOLDS, test_rows_used=0))
    return frame, body, False


def score_likelihood_ratio(scores, sample_prior=SAMPLE_PRIOR):
    scores = np.asarray(scores, dtype=float)
    if scores.ndim != 1 or not np.isfinite(scores).all() or not np.all((scores > 0) & (scores < 1)):
        raise ValueError('Likelihood ratios require finite, strictly interior standardized scores.')
    if not 0 < sample_prior < 1:
        raise ValueError('Sample prior must be strictly interior.')
    return (scores / (1. - scores)) / (sample_prior / (1. - sample_prior))


def count_em(ratio, counts, sample_prior=SAMPLE_PRIOR, tol=TOLERANCE, max_iter=MAX_ITERATIONS):
    """Mandatory original-batch EM; exactly the mean over repeated score rows.

    The fixed-point stopping criterion is |new_pi-pi| < tol, not a likelihood
    gradient criterion. It need not locate a boundary/root within tol in pi;
    iterations/convergence are therefore reported separately from Newton.
    """
    ratio = np.asarray(ratio, dtype=float)
    counts = np.asarray(counts)
    if ratio.ndim != 1 or counts.shape != ratio.shape or counts.dtype.kind not in 'iu':
        raise ValueError('EM needs equal-length score ratios and integer score counts.')
    if np.any(counts < 0) or not np.isfinite(ratio).all() or np.any(ratio <= 0):
        raise ValueError('Invalid ratio/count values.')
    n = int(counts.sum())
    if n <= 0 or not 0 < sample_prior < 1 or tol <= 0 or max_iter < 1:
        raise ValueError('Invalid EM batch or solver settings.')
    support = counts > 0
    ratio, counts = ratio[support], counts[support]  # Algebraic removal only.
    pi = float(sample_prior)
    for iteration in range(1, max_iter + 1):
        numerator = pi * ratio
        posterior = numerator / ((1. - pi) + numerator)
        new_pi = float(np.sum(counts * posterior) / n)
        if not np.isfinite(new_pi) or not 0 <= new_pi <= 1:
            raise FloatingPointError('Original EM produced an invalid prior; no estimate clipping is permitted.')
        if abs(new_pi - pi) < tol:
            return new_pi, iteration, True
        pi = new_pi
    return pi, max_iter, False


def safeguarded_newton(a, count_matrix, warm_start, tol=TOLERANCE, max_iter=MAX_ITERATIONS):
    """Exact concave bootstrap likelihood maximizer, vectorized across rows.

    D=sum(c*a/(1+pi*a)); I=sum(c*(a/(1+pi*a))^2). Endpoint KKT tests retain
    EXACT 0/1. Otherwise D is strictly decreasing: bracketed Newton with
    bisection whenever the step leaves its bracket, and periodic bisection
    if the bracket stalls. Converged/failed rows are frozen. No dot/matmul,
    BLAS-backed reductions, quantization, or row subsampling is used.

    Returns every estimate, iteration count, flag, and bisection count.
    Flat likelihoods have no unique maximizer and are explicitly failures.
    """
    a = np.asarray(a, dtype=float)
    counts = np.asarray(count_matrix)
    if a.ndim != 1 or counts.ndim != 2 or counts.shape[1] != len(a):
        raise ValueError('Newton expects (supports,) and (rows,supports).')
    if counts.dtype.kind not in 'iu' or np.any(counts < 0) or np.any(counts.sum(axis=1) <= 0):
        raise ValueError('Each likelihood row requires nonnegative integer counts and positive total.')
    if not np.isfinite(a).all() or np.any(a <= -1.) or tol <= 0 or max_iter < 1:
        raise ValueError('Invalid likelihood support or solver settings.')
    rows = len(counts)
    warm = np.broadcast_to(np.asarray(warm_start, dtype=float), (rows,)).copy()
    if not np.isfinite(warm).all() or not np.all((warm >= 0) & (warm <= 1)):
        raise ValueError('Warm starts must be finite priors in [0,1].')
    estimates = warm.copy()
    iterations = np.zeros(rows, dtype=np.int16)
    flags = np.full(rows, SOLVER_ITERATION_CAP, dtype=np.int8)
    bisections = np.zeros(rows, dtype=np.int16)
    d0 = np.einsum('ij,j->i', counts, a, optimize=False)
    endpoint_q = a / (1. + a)
    d1 = np.einsum('ij,j->i', counts, endpoint_q, optimize=False)
    info0 = np.einsum('ij,j,j->i', counts, a, a, optimize=False)
    flat = info0 == 0.
    invalid = ~np.isfinite(d0) | ~np.isfinite(d1) | ~np.isfinite(info0)
    lower = (d0 <= 0.) & ~flat & ~invalid
    upper = (d1 >= 0.) & ~flat & ~invalid & ~lower
    estimates[lower], flags[lower] = 0., SOLVER_LOWER_KKT
    estimates[upper], flags[upper] = 1., SOLVER_UPPER_KKT
    flags[flat], flags[invalid] = SOLVER_FLAT, SOLVER_NONFINITE
    active = ~(flat | invalid | lower | upper)
    low, high = np.zeros(rows), np.ones(rows)
    for iteration in range(1, max_iter + 1):
        index = np.flatnonzero(active)
        if not len(index):
            break
        pi = estimates[index]
        selected_counts = counts[index]  # Bounded tile; rows freeze once done.
        q = a[None, :] / (1. + pi[:, None] * a[None, :])
        derivative = np.einsum('ij,ij->i', selected_counts, q, optimize=False)
        information = np.einsum('ij,ij,ij->i', selected_counts, q, q, optimize=False)
        iterations[index] = iteration
        bad = ~np.isfinite(derivative) | ~np.isfinite(information) | (information <= 0.)
        if np.any(bad):
            flags[index[bad]] = SOLVER_NONFINITE
            active[index[bad]] = False
        good = ~bad
        index, pi = index[good], pi[good]
        derivative, information = derivative[good], information[good]
        if not len(index):
            continue
        positive = derivative > 0.
        negative = derivative < 0.
        low[index[positive]] = pi[positive]
        high[index[negative]] = pi[negative]
        correction = derivative / information
        # A local Newton correction is the usual root tolerance; a narrow
        # bracket is an independent safeguard. Do not declare an interior
        # root at an endpoint unless that endpoint passed its KKT test.
        narrow = (high[index] - low[index]) <= tol
        stationary = ((np.abs(correction) <= tol) & (pi > 0.) & (pi < 1.))
        done = stationary | narrow | (derivative == 0.)
        if np.any(done):
            finished = index[done]
            estimates[finished] = np.where(narrow[done] & ~stationary[done],
                                           .5 * (low[finished] + high[finished]), pi[done])
            flags[finished] = SOLVER_INTERIOR
            active[finished] = False
        index, pi, correction = index[~done], pi[~done], correction[~done]
        if not len(index):
            continue
        candidate = pi + correction
        midpoint = .5 * (low[index] + high[index])
        outside = (~np.isfinite(candidate) | (candidate <= low[index]) |
                   (candidate >= high[index]) | (candidate == pi))
        # Force bracket progress every eighth unconverged iteration, even
        # for pathological curvature where valid Newton steps barely move.
        fallback = outside | (iteration % 8 == 0)
        candidate[fallback] = midpoint[fallback]
        bisections[index[fallback]] += 1
        estimates[index] = candidate
    assert np.isfinite(estimates).all() and np.all((estimates >= 0.) & (estimates <= 1.))
    return estimates, iterations, flags, bisections


def bootstrap_batch(generator, a, counts, n, original_estimate):
    """Exactly 500 Mult(n, counts/n) draws over EVERY occupied original score."""
    counts = np.asarray(counts)
    support = counts > 0
    supported_counts = counts[support]
    supported_a = np.asarray(a, dtype=float)[support]
    assert int(supported_counts.sum()) == n
    probability = supported_counts.astype(float) / n  # No probability renormalization/quantization.
    estimates = np.empty(BOOTSTRAP_REPLICATES, dtype=float)
    iterations = np.empty(BOOTSTRAP_REPLICATES, dtype=np.int16)
    flags = np.empty(BOOTSTRAP_REPLICATES, dtype=np.int8)
    bisections = np.empty(BOOTSTRAP_REPLICATES, dtype=np.int16)
    for start in range(0, BOOTSTRAP_REPLICATES, BOOTSTRAP_TILE):
        stop = min(start + BOOTSTRAP_TILE, BOOTSTRAP_REPLICATES)
        draws = generator.multinomial(n, probability, size=stop - start)
        assert np.all(draws.sum(axis=1) == n)
        fitted = safeguarded_newton(supported_a, draws, original_estimate)
        estimates[start:stop], iterations[start:stop], flags[start:stop], bisections[start:stop] = fitted
    # Never discard failed fits: return all 500 and mark any failure separately.
    interval = np.quantile(estimates, (.025, .975), method='linear')
    return estimates, iterations, flags, bisections, interval


def construct_synthetic_counts(generator, positive_indices, negative_indices, n, true_prior,
                               positive_probability=None, negative_probability=None):
    """Labels/class membership are used here ONLY, not passed to estimators."""
    positive_indices = np.asarray(positive_indices, dtype=np.intp)
    negative_indices = np.asarray(negative_indices, dtype=np.intp)
    if not len(positive_indices) or not len(negative_indices) or not 0 < true_prior < 1 or n <= 0:
        raise ValueError('Synthetic batches require two nonempty classes, positive n, and interior generating prior.')
    if positive_probability is None:
        positive_probability = np.full(len(positive_indices), 1. / len(positive_indices))
    if negative_probability is None:
        negative_probability = np.full(len(negative_indices), 1. / len(negative_indices))
    n_positive = int(generator.binomial(n, true_prior))
    # Each original heldout-score ID is a separate exact category, even when
    # two IDs have the same floating-point score. This is not score binning.
    counts = np.zeros(len(positive_indices) + len(negative_indices), dtype=np.int64)
    counts[positive_indices] = generator.multinomial(n_positive, positive_probability)
    counts[negative_indices] = generator.multinomial(n - n_positive, negative_probability)
    assert int(counts.sum()) == n
    return counts, n_positive


def initialize_worker(scores, positive_indices, negative_indices):
    """Read-only worker state; workers neither report nor write checkpoints."""
    global _WORKER_A, _WORKER_SCORES, _WORKER_POSITIVE, _WORKER_NEGATIVE
    global _WORKER_POSITIVE_PROBABILITY, _WORKER_NEGATIVE_PROBABILITY
    _WORKER_SCORES = np.asarray(scores, dtype=float).copy()
    _WORKER_A = score_likelihood_ratio(_WORKER_SCORES) - 1.
    _WORKER_POSITIVE = np.asarray(positive_indices, dtype=np.intp).copy()
    _WORKER_NEGATIVE = np.asarray(negative_indices, dtype=np.intp).copy()
    joined = np.concatenate((_WORKER_POSITIVE, _WORKER_NEGATIVE))
    assert np.array_equal(np.sort(joined), np.arange(len(scores)))
    _WORKER_POSITIVE_PROBABILITY = np.full(len(_WORKER_POSITIVE), 1. / len(_WORKER_POSITIVE))
    _WORKER_NEGATIVE_PROBABILITY = np.full(len(_WORKER_NEGATIVE), 1. / len(_WORKER_NEGATIVE))
    for array in (_WORKER_A, _WORKER_SCORES, _WORKER_POSITIVE, _WORKER_NEGATIVE,
                  _WORKER_POSITIVE_PROBABILITY, _WORKER_NEGATIVE_PROBABILITY):
        array.setflags(write=False)


def simulate_replicate(task):
    grid_index, rep_index, true_prior, n = task
    generator = np.random.default_rng(np.random.SeedSequence(
        TASK_SEED, spawn_key=(int(grid_index), int(rep_index))))
    counts, n_positive = construct_synthetic_counts(
        generator, _WORKER_POSITIVE, _WORKER_NEGATIVE, n, true_prior,
        _WORKER_POSITIVE_PROBABILITY, _WORKER_NEGATIVE_PROBABILITY)
    occupied = counts > 0
    # Use the original ratio, not a reconstructed/rounded score.
    ratio = score_likelihood_ratio(_WORKER_SCORES[occupied])
    estimate, iterations, converged = count_em(ratio, counts[occupied])
    boots, boot_iterations, flags, bisections, interval = bootstrap_batch(
        generator, _WORKER_A, counts, n, estimate)
    return dict(
        replicate=rep_index, estimate=estimate, iterations=iterations, converged=converged,
        bootstrap_estimates=boots, bootstrap_iterations=boot_iterations,
        solver_flags=flags, bootstrap_bisections=bisections, interval=interval,
        realized_prior=n_positive / n, n_positive=n_positive,
        occupied_scores=int(occupied.sum()),
        mean_score=float(np.sum(counts * _WORKER_SCORES) / n),
    )


def checkpoint_identity(grid_index, folded_sha, fingerprint):
    true_prior, n = GRID[grid_index]
    return dict(script_sha256=digest(__file__), folded_score_sha256=folded_sha,
                seed=SEED, task_seed=TASK_SEED, input_fingerprint=fingerprint,
                grid_index=grid_index, true_prior=true_prior, batch_size=n,
                original_replicates=ORIGINAL_REPLICATES, bootstrap_replicates=BOOTSTRAP_REPLICATES)


def empty_grid_arrays(identity):
    return dict(
        original_estimates=np.empty(ORIGINAL_REPLICATES, dtype=float),
        iterations=np.empty(ORIGINAL_REPLICATES, dtype=np.int16),
        convergence=np.empty(ORIGINAL_REPLICATES, dtype=bool),
        bootestimates=np.empty((ORIGINAL_REPLICATES, BOOTSTRAP_REPLICATES), dtype=float),
        original_realized_pi=np.empty(ORIGINAL_REPLICATES, dtype=float),
        intervals=np.empty((ORIGINAL_REPLICATES, 2), dtype=float),
        solverflags=np.empty((ORIGINAL_REPLICATES, BOOTSTRAP_REPLICATES), dtype=np.int8),
        bootstrap_iterations=np.empty((ORIGINAL_REPLICATES, BOOTSTRAP_REPLICATES), dtype=np.int16),
        bootstrap_bisections=np.empty((ORIGINAL_REPLICATES, BOOTSTRAP_REPLICATES), dtype=np.int16),
        original_n_positive=np.empty(ORIGINAL_REPLICATES, dtype=np.int64),
        occupied_scores=np.empty(ORIGINAL_REPLICATES, dtype=np.int32),
        mean_score=np.empty(ORIGINAL_REPLICATES, dtype=float),
        replicate_ids=np.arange(ORIGINAL_REPLICATES, dtype=np.int32),
        script_sha256=np.asarray(identity['script_sha256']),
        folded_score_sha256=np.asarray(identity['folded_score_sha256']),
        seed=np.asarray(SEED, dtype=np.int64), task_seed=np.asarray(TASK_SEED, dtype=np.int64),
        grid_index=np.asarray(identity['grid_index'], dtype=np.int32),
        true_prior=np.asarray(identity['true_prior']), batch_size=np.asarray(identity['batch_size'], dtype=np.int64),
    )


def validate_grid_arrays(arrays, identity):
    vector = (ORIGINAL_REPLICATES,)
    boots = (ORIGINAL_REPLICATES, BOOTSTRAP_REPLICATES)
    shapes = {name: vector for name in ('original_estimates', 'iterations', 'convergence',
                                      'original_realized_pi', 'original_n_positive',
                                      'occupied_scores', 'mean_score', 'replicate_ids')}
    shapes.update({name: boots for name in ('bootestimates', 'solverflags', 'bootstrap_iterations', 'bootstrap_bisections')})
    shapes['intervals'] = (ORIGINAL_REPLICATES, 2)
    scalar_names = ('script_sha256', 'folded_score_sha256', 'seed', 'task_seed',
                    'grid_index', 'true_prior', 'batch_size')
    shapes.update({name: () for name in scalar_names})
    if set(arrays) != set(shapes) or any(arrays[name].shape != shape for name, shape in shapes.items()):
        raise ValueError('Incomplete/unknown checkpoint arrays; no silent partial replicate counts.')
    for name in scalar_names:
        if arrays[name].item() != identity[name]:
            raise ValueError(f'Checkpoint scalar identity mismatch: {name}.')
    assert np.array_equal(arrays['replicate_ids'], np.arange(ORIGINAL_REPLICATES))
    assert arrays['convergence'].dtype.kind == 'b'
    for name in ('iterations', 'solverflags', 'bootstrap_iterations', 'bootstrap_bisections',
                 'original_n_positive', 'occupied_scores', 'replicate_ids'):
        assert arrays[name].dtype.kind in 'iu'
    for name in ('original_estimates', 'bootestimates', 'original_realized_pi'):
        assert np.isfinite(arrays[name]).all() and np.all((arrays[name] >= 0) & (arrays[name] <= 1))
    assert np.isfinite(arrays['mean_score']).all()
    assert np.all((arrays['iterations'] >= 1) & (arrays['iterations'] <= MAX_ITERATIONS))
    assert np.all((arrays['bootstrap_iterations'] >= 0) & (arrays['bootstrap_iterations'] <= MAX_ITERATIONS))
    assert np.all((arrays['bootstrap_bisections'] >= 0) & (arrays['bootstrap_bisections'] <= MAX_ITERATIONS))
    assert np.isin(arrays['solverflags'], list(SOLVER_FLAGS)).all()
    assert np.all((arrays['occupied_scores'] >= 1) & (arrays['occupied_scores'] <= CALIBRATION_ROWS))
    assert np.all((arrays['original_n_positive'] >= 0) & (arrays['original_n_positive'] <= identity['batch_size']))
    assert np.array_equal(arrays['original_realized_pi'], arrays['original_n_positive'] / identity['batch_size'])
    expected_intervals = np.quantile(arrays['bootestimates'], (.025, .975), axis=1, method='linear').T
    assert np.array_equal(arrays['intervals'], expected_intervals), 'Checkpoint intervals are not all-500-fit percentiles.'
    assert np.all(arrays['bootestimates'][arrays['solverflags'] == SOLVER_LOWER_KKT] == 0.)
    assert np.all(arrays['bootestimates'][arrays['solverflags'] == SOLVER_UPPER_KKT] == 1.)


def checkpoint_paths(grid_index):
    stem = f'wp5_grid_{grid_index:02d}'
    return ADDONS / f'results/{stem}.npz', ADDONS / f'results/{stem}.json'


def resume_grid(identity):
    npz_path, json_path = checkpoint_paths(identity['grid_index'])
    if npz_path.exists() != json_path.exists():
        raise RuntimeError(f'Incomplete checkpoint pair {npz_path.name}; explicit review required, not a partial resume.')
    if not npz_path.is_file():
        return None
    body = json.loads(json_path.read_text(encoding='utf-8'))
    if body.get('identity') != identity or body.get('artifact', {}).get('sha256') != digest(npz_path):
        raise RuntimeError(f'Checkpoint identity/hash mismatch {npz_path.name}; refusing stale resume.')
    required_counts = dict(original_replicates=ORIGINAL_REPLICATES,
                           bootstrap_fits=ORIGINAL_REPLICATES * BOOTSTRAP_REPLICATES,
                           calibration_pool=CALIBRATION_ROWS, test_rows_used=0)
    if body.get('provenance', {}).get('row_counts') != required_counts:
        raise ValueError('Checkpoint JSON replicate counts are incomplete or inconsistent.')
    with np.load(npz_path, allow_pickle=False) as saved:
        arrays = {name: saved[name].copy() for name in saved.files}
    validate_grid_arrays(arrays, identity)
    if body.get('bootstrap_failures') != int(np.count_nonzero(arrays['solverflags'] >= SOLVER_FLAT)):
        raise ValueError('Checkpoint solver failure count mismatch.')
    return arrays


def compute_grid(executor, identity):
    arrays = empty_grid_arrays(identity)
    seen = np.zeros(ORIGINAL_REPLICATES, dtype=bool)
    futures = [executor.submit(simulate_replicate,
                               (identity['grid_index'], rep, identity['true_prior'], identity['batch_size']))
               for rep in range(ORIGINAL_REPLICATES)]
    for future in as_completed(futures):
        row = future.result()
        rep = int(row['replicate'])
        if not 0 <= rep < ORIGINAL_REPLICATES or seen[rep]:
            raise RuntimeError('Worker returned an invalid/duplicate replicate index.')
        arrays['original_estimates'][rep] = row['estimate']
        arrays['iterations'][rep] = row['iterations']
        arrays['convergence'][rep] = row['converged']
        arrays['bootestimates'][rep] = row['bootstrap_estimates']
        arrays['original_realized_pi'][rep] = row['realized_prior']
        arrays['intervals'][rep] = row['interval']
        arrays['solverflags'][rep] = row['solver_flags']
        arrays['bootstrap_iterations'][rep] = row['bootstrap_iterations']
        arrays['bootstrap_bisections'][rep] = row['bootstrap_bisections']
        arrays['original_n_positive'][rep] = row['n_positive']
        arrays['occupied_scores'][rep] = row['occupied_scores']
        arrays['mean_score'][rep] = row['mean_score']
        seen[rep] = True
    assert seen.all(), 'All 500 original batches and their 500 bootstrap fits are mandatory.'
    validate_grid_arrays(arrays, identity)
    return arrays


def save_grid(arrays, identity, inputs):
    """Called by the main process only, after the entire grid has completed."""
    validate_grid_arrays(arrays, identity)
    npz_path, json_path = checkpoint_paths(identity['grid_index'])
    temporary = npz_path.with_suffix('.npz.pending')
    with temporary.open('wb') as stream:
        np.savez_compressed(stream, **arrays)
    temporary.replace(npz_path)
    counts = dict(original_replicates=ORIGINAL_REPLICATES,
                  bootstrap_fits=ORIGINAL_REPLICATES * BOOTSTRAP_REPLICATES,
                  calibration_pool=CALIBRATION_ROWS, test_rows_used=0)
    failures = int(np.count_nonzero(arrays['solverflags'] >= SOLVER_FLAT))
    write_json(json_path.relative_to(ADDONS).as_posix(), dict(
        status='DONE' if arrays['convergence'].all() and failures == 0 else 'PARTIAL',
        computation_complete=True, identity=identity, artifact=file_info(npz_path),
        original_converged=int(arrays['convergence'].sum()), bootstrap_failures=failures,
        solver_flags=SOLVER_FLAGS,
        rng='numpy.random.SeedSequence(SEED+5, spawn_key=(grid_index, replicate_index)); one independent stream per original batch.',
        zero_removal='Original positive-count score supports only; zero contributions inside each resample remain algebraically zero.',
        resampling='Exactly 500 Mult(n,original_scorecounts/n), not stratified bootstrap, Poisson, subsampling, delta method, or quantized support.',
        confidence_interval='Linear 2.5/97.5 percentiles of all 500 returned estimates, including explicitly flagged failed iterates.',
    ), __file__, TASK_INDEX, inputs + [OOF_CSV, OOF_JSON], counts)


def grid_statistics(arrays, grid_index):
    true_prior, n = GRID[grid_index]
    estimates = arrays['original_estimates']
    errors = estimates - true_prior
    intervals = arrays['intervals']
    failures_by_original = np.count_nonzero(arrays['solverflags'] >= SOLVER_FLAT, axis=1)
    covered = (intervals[:, 0] <= true_prior) & (true_prior <= intervals[:, 1])
    coverage = float(covered.mean())
    summary = dict(
        grid_index=grid_index, true_prior=true_prior, batch_size=n,
        original_replicates=ORIGINAL_REPLICATES,
        bootstrap_fits=ORIGINAL_REPLICATES * BOOTSTRAP_REPLICATES,
        mean_estimate=float(estimates.mean()), median_estimate=float(np.median(estimates)),
        bias=float(errors.mean()), median_error=float(np.median(errors)),
        rmse=float(np.sqrt(np.mean(errors * errors))),
        coverage_95_generating_prior=coverage,
        coverage_mc_se=float(np.sqrt(coverage * (1. - coverage) / ORIGINAL_REPLICATES)),
        median_iterations=float(np.median(arrays['iterations'])), max_iterations=int(arrays['iterations'].max()),
        converged_originals=int(arrays['convergence'].sum()), convergence_fraction=float(arrays['convergence'].mean()),
        bootstrap_failures=int(failures_by_original.sum()),
        intervals_with_failed_bootstrap=int(np.count_nonzero(failures_by_original)),
        bootstrap_median_iterations=float(np.median(arrays['bootstrap_iterations'])),
        bootstrap_max_iterations=int(arrays['bootstrap_iterations'].max()),
        bootstrap_lower_boundary_fits=int(np.count_nonzero(arrays['solverflags'] == SOLVER_LOWER_KKT)),
        bootstrap_upper_boundary_fits=int(np.count_nonzero(arrays['solverflags'] == SOLVER_UPPER_KKT)),
        mean_realized_prior=float(arrays['original_realized_pi'].mean()),
        median_interval_width=float(np.median(intervals[:, 1] - intervals[:, 0])),
    )
    raw = pd.DataFrame(dict(
        grid_index=np.full(ORIGINAL_REPLICATES, grid_index),
        replicate=arrays['replicate_ids'], true_prior=np.full(ORIGINAL_REPLICATES, true_prior),
        batch_size=np.full(ORIGINAL_REPLICATES, n), estimate=estimates, error=errors,
        iterations=arrays['iterations'], converged=arrays['convergence'],
        realized_prior=arrays['original_realized_pi'], n_positive=arrays['original_n_positive'],
        lower_95=intervals[:, 0], upper_95=intervals[:, 1], covers_generating_prior=covered,
        bootstrap_fits=np.full(ORIGINAL_REPLICATES, BOOTSTRAP_REPLICATES),
        bootstrap_failures=failures_by_original,
        interval_solver_valid=failures_by_original == 0,
        bootstrap_max_iterations=arrays['bootstrap_iterations'].max(axis=1),
        bootstrap_bisection_steps=arrays['bootstrap_bisections'].sum(axis=1),
        occupied_scores=arrays['occupied_scores'], mean_score=arrays['mean_score'],
    ))
    return summary, raw


def safe_v2_functions():
    """AST-extract ONLY the six supplied PURE functions, not their imports.

    Restrict builtins and call sites; source changes that add IO, fitting,
    imports, decorators, or arbitrary callable attributes are rejected.
    v2 common's PRIOR-dependent defaults are evaluated with PRIOR=.4956.
    """
    namespace = dict(np=np, expit=expit, logit=logit, PRIOR=LEGACY_SAMPLE_PRIOR,
                     __builtins__={'float': float, 'int': int, 'min': min, 'max': max, 'len': len})
    sources = ((ROOT / 'v2_work/common.py', ('shift', 'weights', 'cutoff')),
               (ROOT / 'v2_work/workstream_a.py', ('scores', 'measure', 'fit_thresholds')))
    allowed_names = {'shift', 'weights', 'cutoff', 'scores', 'measure', 'fit_thresholds',
                     'expit', 'logit', 'float', 'int', 'min', 'max', 'len'}
    allowed_np_calls = {'asarray', 'where', 'clip', 'argsort', 'cumsum', 'searchsorted', 'sum', 'count_nonzero'}
    audit = []
    for source_path, names in sources:
        tree = ast.parse(source_path.read_text(encoding='utf-8'), filename=source_path.as_posix())
        functions = []
        for name in names:
            matches = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name]
            if len(matches) != 1 or matches[0].decorator_list:
                raise ValueError(f'Expected exactly one undecorated pure v2 function {name}.')
            function = matches[0]
            for node in ast.walk(function):
                if isinstance(node, (ast.Import, ast.ImportFrom, ast.Global, ast.Nonlocal,
                                     ast.With, ast.AsyncWith, ast.ClassDef, ast.Lambda)):
                    raise ValueError(f'Forbidden construct in extracted v2 function {name}.')
                if isinstance(node, ast.Attribute) and node.attr.startswith('_'):
                    raise ValueError(f'Private attribute forbidden in extracted v2 function {name}.')
                if isinstance(node, ast.Call):
                    call = node.func
                    if isinstance(call, ast.Name):
                        safe = call.id in allowed_names
                    elif isinstance(call, ast.Attribute):
                        safe = ((isinstance(call.value, ast.Name) and call.value.id == 'np'
                                 and call.attr in allowed_np_calls) or call.attr in {'to_numpy', 'items', 'sum'})
                    else:
                        safe = False
                    if not safe:
                        raise ValueError(f'Unapproved call in extracted v2 function {name}: {ast.unparse(call)}')
            functions.append(function)
        extracted = ast.Module(body=functions, type_ignores=[])
        exec(compile(ast.fix_missing_locations(extracted), source_path.as_posix(), 'exec'), namespace)
        audit.append(dict(source=file_info(source_path), extracted_functions=list(names),
                          exact_ast_source=[ast.unparse(function) for function in functions],
                          top_level_imports_executed=False))
    return {name: namespace[name] for name in ('shift', 'weights', 'cutoff', 'scores', 'measure', 'fit_thresholds')}, audit


def planning_break_even(cal, allowed_ids):
    functions, extraction = safe_v2_functions()
    # The required loader reads ONLY baseline cached non-test outcomes/scores;
    # source_values streams Record.csv but retains V solely for allowed IDs.
    frame = population()
    assert len(frame) == PLANNING_ROWS and not frame.Customer_ID.duplicated().any()
    assert set(frame.Customer_ID.astype(int)) == allowed_ids
    assert allowed_ids.isdisjoint(set(cal.Customer_ID.astype(int)))
    assert np.isfinite(frame[['p_s', 'value']].to_numpy()).all()
    assert np.isin(frame.y.to_numpy(), (0, 1)).all()
    rows = []
    # Integer ticks avoid cumulative floating-point additions: 251 priors.
    for prior in np.arange(50, 301, dtype=np.int64) / 10_000.:
        prior = float(prior)
        threshold = functions['fit_thresholds'](cal, prior=prior, fraction=.1, cost=1.)['bayes']
        score = functions['scores'](frame, prior=prior)['bayes']
        mask = score >= threshold
        measured = functions['measure'](frame, mask, prior=prior, cost=1., success=.2)
        rows.append(dict(prior=prior, threshold=threshold, **measured))
    fine = pd.DataFrame(rows)
    assert len(fine) == 251 and np.isfinite(fine.net.to_numpy()).all()
    first_crossing = None
    net = fine.net.to_numpy()
    for index, value in enumerate(net):
        if value == 0.:
            row = rows[index]
            first_crossing = dict(prior_star=row['prior'], lower_prior=row['prior'], upper_prior=row['prior'],
                                  lower_net=0., upper_net=0., direction='exact sampled zero',
                                  method='Exact zero on the non-test planning grid, not a live prior.')
            break
        if index and np.signbit(net[index - 1]) != np.signbit(value):
            left, right = rows[index - 1], rows[index]
            prior_star = left['prior'] - left['net'] * (right['prior'] - left['prior']) / (right['net'] - left['net'])
            first_crossing = dict(prior_star=float(prior_star), lower_prior=left['prior'], upper_prior=right['prior'],
                                  lower_net=left['net'], upper_net=right['net'],
                                  direction='negative to positive' if left['net'] < 0 else 'positive to negative',
                                  method='Approximate linear interpolation between adjacent .01-percentage-point planning-grid steps; not live.')
            break
    metrics_path = ROOT / 'v2_work/final_metrics.json'
    stored = json.loads(metrics_path.read_text(encoding='utf-8')).get('prior_stress', [])
    quotes = [dict(row) for row in stored if row.get('prior') in (.01, .02, .05)]
    if len(quotes) != 3 or {row['prior'] for row in quotes} != {.01, .02, .05}:
        raise ValueError('Frozen final_metrics prior-stress quotes are missing/duplicated.')
    csv_path = ADDONS / 'results/wp5_break_even_grid.csv'
    fine.to_csv(csv_path, index=False, float_format='%.17g', lineterminator='\n')
    audit = dict(
        status='DONE' if first_crossing is not None else 'PARTIAL',
        method='Exact read-only v2 pure-function replay on alternate non-test planning population; not a reproduction of frozen test dollars.',
        frozen_sample_prior_default=LEGACY_SAMPLE_PRIOR, em_sample_prior=SAMPLE_PRIOR,
        calibration_threshold_input='10k saved calibration_policy cache p_s (not new OOF p_s_oof); weighted 10% cutoff at EACH prior.',
        evaluation_input='75k common.population(): baseline repeated-OOF raw scores averaged by ID and the frozen baseline sigmoid; non-test only.',
        economic_assumptions=dict(population=100_000, cost=1., success=.2, months=6, margin=.6, fixed_cost=5000., intended_fraction=.1),
        grid=dict(start=.005, stop=.03, step=.0001, step_percentage_points=.01, points=len(fine)),
        first_crossing=first_crossing, artifact=file_info(csv_path), pure_function_extraction=extraction,
        frozen_quoted_points=quotes, frozen_quote_source=file_info(metrics_path),
        frozen_quote_scope='Verbatim stored 1/2/5% final_metrics.prior_stress scalars; no test rows loaded or recomputed.',
        planning_one_two_percent_points=[row for row in rows if row['prior'] in (.01, .02)],
        new_model_fits=0, test_score_or_outcome_rows_loaded=0,
        record_loading='common.source_values streams the source CSV and retains only allowed-ID values; no test-row frame is materialized.',
        limitations='Thresholds include score ties and are re-derived on calibration at each assumed prior. This grid is alternate non-test planning, not a live estimate or promoted policy.',
    )
    return audit, csv_path


def trigger_audit(planning):
    source = BRIEF.read_text(encoding='utf-8')
    matches = [line for line in source.splitlines() if 'Trigger rule [R]:' in line and 'lower 95% bound' in line]
    if len(matches) != 1:
        raise ValueError('Cannot preserve the unique two input trigger rules verbatim.')
    line = matches[0]
    suffix = line.split('each monthly batch: estimate π̂ with interval; ', 1)[1]
    clauses = suffix.split('; ')
    if len(clauses) < 3 or not clauses[0].startswith('if lower') or not clauses[1].startswith('if interval straddles'):
        raise ValueError('Input trigger rule structure changed; review required.')
    crossing = planning['first_crossing']
    return dict(
        source=file_info(BRIEF), source_line_verbatim=line,
        input_rule_1_verbatim=clauses[0], input_rule_2_verbatim=clauses[1],
        contradiction='Every interval strictly straddling pi* also has lower < pi*: HOLD and proceed overlap.',
        proposed_priority='HOLD discretionary outreach and review whenever lower_95 < pi*; otherwise proceed diagnostic-only. Service-Fix Floor continues in every case.',
        comparison='Strict lower_95 < pi*; equality is not HOLD under this diagnostic proposal.',
        deviation='Conservative HOLD priority resolves the brief contradiction. This is a supporting recommendation, NOT a frozen protocol change.',
        maturity_override='Day-60 mature labels always override the unlabeled EM estimate; Floor continues.',
        prior_star=crossing['prior_star'] if crossing is not None else None,
        unavailable_prior_star_action='No trigger classification is produced without a planning-grid crossing; human review required.',
        live_policy_changed=False, diagnostic_only=True,
    )


def acceptance_checks(summary, raw, planning):
    total_originals = int(summary.original_replicates.sum())
    total_boots = int(summary.bootstrap_fits.sum())
    converged = int(summary.converged_originals.sum())
    failures = int(summary.bootstrap_failures.sum())
    expected_originals = len(GRID) * ORIGINAL_REPLICATES
    expected_boots = expected_originals * BOOTSTRAP_REPLICATES
    checks = dict(
        output_counts=dict(passed=len(summary) == len(GRID) and len(raw) == total_originals == expected_originals
                           and total_boots == expected_boots,
                           actual_grid_rows=len(summary), expected_grid_rows=len(GRID),
                           actual_raw_rows=len(raw), expected_raw_rows=expected_originals,
                           actual_bootstrap_fits=total_boots, expected_bootstrap_fits=expected_boots),
        all_original_em_converged=dict(passed=converged == expected_originals,
                                      actual_converged=converged, actual_total=total_originals,
                                      convergence_fraction=converged / total_originals),
        no_bootstrap_solver_failures=dict(passed=failures == 0, actual_failures=failures, actual_total=total_boots),
        planning_crossing_found=dict(passed=planning['first_crossing'] is not None,
                                     actual=planning['first_crossing']),
    )
    target = summary.loc[summary.true_prior.eq(.02) & summary.batch_size.ge(10_000)]
    assert len(target) == 3
    for row in target.to_dict(orient='records'):
        checks[f'median_error_pi_02_n_{row["batch_size"]}'] = dict(
            passed=abs(row['median_error']) < .003, actual_median_error=row['median_error'],
            actual_abs_median_error=abs(row['median_error']), strict_absolute_tolerance=.003,
            tolerance_percentage_points=.3, replicates=ORIGINAL_REPLICATES)
    return checks


def report_lines(summary, checks, planning, artifacts):
    results = [
        '| [A] Generating pi | n | [E] Mean bias | Median error | RMSE | Coverage of generating pi | Median/max EM iters | Converged | Bootstrap failures |',
        '|---:|---:|---:|---:|---:|---:|---:|---:|---:|',
    ]
    for row in summary.to_dict(orient='records'):
        results.append(f'| {row["true_prior"]:.3%} | {row["batch_size"]:,} | {row["bias"]:.6f} | '
                       f'{row["median_error"]:.6f} | {row["rmse"]:.6f} | {row["coverage_95_generating_prior"]:.3%} | '
                       f'{row["median_iterations"]:g}/{row["max_iterations"]} | {row["converged_originals"]}/500 | '
                       f'{row["bootstrap_failures"]} |')
    cross = planning['first_crossing']
    if cross:
        results.append(f'[E/A] Alternate non-test planning pi* = {cross["prior_star"]:.6%}; {cross["method"]}')
    else:
        results.append('[E] No sign crossing found in the .5%-3% alternate non-test planning grid; no trigger threshold claimed.')
    results.append('[E] Frozen final_metrics quotations (not new test computations): ' +
                   '; '.join(f'pi={row["prior"]:.0%}: net={row["net"]:.6f}' for row in planning['frozen_quoted_points']) + '.')
    results.extend(f'[E] `{item["path"]}` — SHA-256 `{item["sha256"]}`.' for item in artifacts)
    acceptance = [f'- [E] {"PASS" if check["passed"] else "FAIL"}: {name}: ' +
                  json.dumps(check, sort_keys=True, allow_nan=False) for name, check in checks.items()]
    return results, acceptance


def main(argv=None):
    verify_runtime()
    parser = argparse.ArgumentParser(description='Explicit WP5 job; requires terminal WP3 and WP4. No reduced-run mode.')
    parser.add_argument('--workers', type=int, choices=range(1, MAX_WORKERS + 1), default=MAX_WORKERS)
    args = parser.parse_args(argv)
    predecessors = require_predecessors()
    tests = json.loads((ADDONS / 'results/wp5_tests.json').read_text(encoding='utf-8'))
    assert tests.get('passed') is True, 'WP5 requires passing separate new-code checks.'
    inputs = input_paths(predecessors)
    for directory in ('results', 'figures', 'reports'):
        if not (ADDONS / directory).is_dir():
            raise FileNotFoundError(f'Required sandbox output directory missing: {(ADDONS / directory).as_posix()}')
    fingerprint = input_fingerprint(inputs)
    cal, allowed_ids = load_calibration()
    folded, folded_provenance, _ = prepare_folded(cal, inputs, fingerprint)
    folded_sha = digest(OOF_CSV)
    scores = folded.p_s_oof.to_numpy(dtype=float)
    # Class membership goes only to synthetic-batch construction. All batch
    # EM/Newton routines receive unlabeled score ratios and integer counts.
    labels = folded.y.to_numpy(dtype=np.int8)
    positive, negative = np.flatnonzero(labels == 1), np.flatnonzero(labels == 0)
    summaries, raw_frames, checkpoint_files = [], [], []
    initialize_worker(scores, positive, negative)
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        for grid_index, (true_prior, n) in enumerate(GRID):
            identity = checkpoint_identity(grid_index, folded_sha, fingerprint)
            arrays = resume_grid(identity)
            resumed = arrays is not None
            if not resumed:
                arrays = compute_grid(executor, identity)
                save_grid(arrays, identity, inputs)
            summary, raw = grid_statistics(arrays, grid_index)
            summaries.append(summary)
            raw_frames.append(raw)
            checkpoint_files.extend(checkpoint_paths(grid_index))
            print(f'[E] WP5 grid {grid_index + 1}/20 pi={true_prior:g} n={n}: '
                  f'500 originals / 250000 bootstraps {"resumed" if resumed else "completed"}; '
                  f'EM converged={summary["converged_originals"]}/500, '
                  f'bootstrap failures={summary["bootstrap_failures"]}.', flush=True)
            # Statistical failures never stop subsequent grid points.
    summary_frame = pd.DataFrame(summaries)
    raw_frame = pd.concat(raw_frames, ignore_index=True)
    assert len(summary_frame) == 20 and len(raw_frame) == 10_000
    assert not raw_frame.duplicated(['grid_index', 'replicate']).any()
    raw_path = ADDONS / 'results/wp5_label_shift_raw.csv'
    summary_path = ADDONS / 'results/wp5_label_shift_summary.csv'
    raw_frame.to_csv(raw_path, index=False, float_format='%.17g', lineterminator='\n')
    summary_frame.to_csv(summary_path, index=False, float_format='%.17g', lineterminator='\n')
    planning, planning_path = planning_break_even(cal, allowed_ids)
    trigger = trigger_audit(planning)
    checks = acceptance_checks(summary_frame, raw_frame, planning)
    status = 'DONE' if all(check['passed'] for check in checks.values()) else 'PARTIAL'
    series = []
    colors = ((0, 126, 134), (189, 125, 20), (91, 110, 129), (105, 76, 154))
    for n, color in zip(BATCH_SIZES, colors):
        subset = summary_frame.loc[summary_frame.batch_size.eq(n)].sort_values('true_prior')
        series.append(dict(label=f'n={n:,}', x=subset.true_prior.to_numpy(),
                           y=subset.median_estimate.to_numpy(), color=color))
    series.append(dict(label='Ideal diagonal', x=np.array([0., max(TRUE_PRIORS)]),
                       y=np.array([0., max(TRUE_PRIORS)]), color=(24, 43, 65)))
    figure = line_plot(ADDONS / 'figures/wp5_em_recovery.png',
                       'WP5 conditional EM recovery - median of 500 batches',
                       'Generating prior (fraction)', 'Median estimated prior (fraction)', series)
    artifacts = [file_info(path) for path in [OOF_CSV, OOF_JSON, raw_path, summary_path, planning_path,
                                            figure] + checkpoint_files]
    assert all(item['present'] and item['sha256'] for item in artifacts)
    results, acceptance = report_lines(summary_frame, checks, planning, artifacts[:6])
    deviations = [
        '[R] The two brief trigger rules overlap for intervals straddling pi*. Proposed HOLD priority is diagnostic-only, not a frozen protocol change.',
        '[E] Break-even uses the exact v2 pure functions on alternate non-test baseline OOF scores; stored 1/2/5% test-based dollar scalars are quoted, not reproduced.',
        '[E] M5 wording: standard derivation, simulation validation; source read status tracked separately. No WP5 verified-full-text claim.',
        '[E] Bootstrap uses the equivalent concave likelihood Newton solver, not 1000-step EM; original EM retains the specified fixed-point tolerance/cap.',
    ]
    if status == 'PARTIAL':
        deviations.append('[E] All 10,000 original batches and 5,000,000 bootstrap fits finished; actual acceptance failures below downgrade this analysis to diagnostic-only.')
        deviations.extend('[E] Failed check ' + name + ': ' + json.dumps(check, sort_keys=True)
                          for name, check in checks.items() if not check['passed'])
    report_inputs = inputs + [OOF_CSV, OOF_JSON, raw_path, summary_path, planning_path]
    write_report(
        5, 'Label-shift EM monitor and alternate non-test break-even trigger', status, report_inputs,
        [
            '- [A] Generating pi and class-conditional heldout score pools define synthetic, conditional scenarios; stable P(x|y) and adequate calibration are unverified live.',
            '- [E] 10k saved calibration_policy IDs only for five-fold calibration; 75k train/validation IDs only for planning; no new test-score/outcome computation.',
            '- [E/A] Bootstrap conditions on the fitted empirical folded-score pool and original batch; it excludes calibration/base-model uncertainty.',
            '- [A] New handsets/plans and other covariate shift may be misattributed to prior shift. The balanced 49.562% source prior is not live.',
            '- [E] Percentile intervals include all 500 estimates; boundary atoms at 0/1 can cause nonregular coverage. Intervals with flagged solver failures are numerical diagnostics, not valid confidence claims.',
        ],
        '[E] Fit exactly five label-stratified SEED+5 heldout sigmoid calibrators with sum logistic loss and slope-only C=1000 penalty. '
        'Standardize each heldout logit from actual training prevalence to .49562, then clip its score. '
        'Draw Bin(n,pi) positives and uniform within-class score multinomials for 500 batches at each of 20 grid points. '
        'Run count-weighted original EM from .49562 (tol1e-8, cap1000); draw exactly 500 full-support batch multinomial bootstraps per original. '
        'Solve bootstrap concave likelihoods by endpoint KKT/bracketed Newton with bisection; retain all estimates/flags. '
        'Hash-bind complete grid NPZ/JSON checkpoints and final CSVs; evaluate generating-prior coverage. '
        'AST-extract only the six pure v2 functions for a .0001-step non-test planning break-even grid.',
        results, acceptance, deviations,
        '[E/A] Conditional synthetic-batch recovery and generating-prior interval coverage at the stated grid; [R] diagnostic prior monitoring with day-60 label override and continuing Floor.',
        '[R] Live drift detection, oracle prevalence, verified class-conditionals, causal profitability, calibration-inclusive intervals, a promoted trigger/protocol, or a verified M5 full-text formula.',
    )
    report_path = ADDONS / 'reports/WP5_report.md'
    artifacts.append(file_info(report_path))
    # Bind inputs once more after the long job: changing inputs mid-run must
    # not silently certify results against a different model/cache/script.
    if input_fingerprint(inputs) != fingerprint or digest(OOF_CSV) != folded_sha:
        raise RuntimeError('Inputs changed during WP5; refusing to publish a primary success/partial record.')
    total_originals = int(summary_frame.original_replicates.sum())
    total_boots = int(summary_frame.bootstrap_fits.sum())
    body = dict(
        status=status, computation_complete=True, statistical_acceptance=all(check['passed'] for check in checks.values()),
        use_scope='diagnostic-only supporting analysis; not a frozen protocol change or live deployment validation',
        predecessor_completion=predecessors,
        identity=dict(script_sha256=digest(__file__), folded_score_sha256=folded_sha,
                      seed=SEED, task_seed=TASK_SEED, input_fingerprint=fingerprint),
        execution=dict(workers=args.workers, worker_backend='stdlib ThreadPoolExecutor; initialized immutable state shared by at most six workers',
                       bootstrap_tile=BOOTSTRAP_TILE, maximum_supports=CALIBRATION_ROWS,
                       worker_reductions='elementwise sum/einsum(optimize=False), no dot/matmul or BLAS reductions',
                       operational_resume_logging='Console only; cache-hit counts are excluded from hash-bound numerical results for deterministic reruns.',
                       resume_policy='Exact script SHA, folded-score SHA, SEED/task seed, input fingerprint, grid identity, NPZ hash, complete shapes/counts, replicate IDs and all-fit percentiles must match.'),
        simulation=dict(generating_priors=list(TRUE_PRIORS), batch_sizes=list(BATCH_SIZES),
                        original_replicates_per_grid=ORIGINAL_REPLICATES,
                        bootstrap_resamples_per_original=BOOTSTRAP_REPLICATES,
                        original_batches=total_originals, bootstrap_fits=total_boots,
                        construction='Npositive~Bin(n,pi); uniform multinomial within each heldout-score class; combine exact per-ID counts.',
                        bootstrap='Mult(n, counts/n) on every positive-count score ID; remove zero terms algebraically only.',
                        rng='SeedSequence(SEED+5,spawn_key=(gridindex,repindex)); deterministic independently of scheduling/resume.',
                        labels_scope='Labels construct calibration folds and synthetic class-conditional batches; batch estimators receive only unlabeled score ratios/counts.'),
        calibration=dict(sample_prior=SAMPLE_PRIOR, rows=CALIBRATION_ROWS, folds=FOLDS,
                         new_sigmoid_fits=FOLDS, new_base_model_fits=0,
                         provenance=file_info(OOF_JSON), calibrator_parameters=folded_provenance['calibrator_parameters']),
        original_em=dict(start=SAMPLE_PRIOR, tolerance=TOLERANCE, max_iterations=MAX_ITERATIONS,
                         stopping='abs(new_pi-pi)<1e-8; weighted posterior mean is mathematically identical to repeated score rows.',
                         posterior='pi*r / ((1-pi)+pi*r), r=odds(p_s)/odds(.49562)', estimate_clipping=False),
        bootstrap_solver=dict(method='Safeguarded Newton unique concave likelihood maximizer, except explicitly flagged flat likelihoods.',
                              likelihood='sum(counts*log(1+pi*(r-1))) plus pi-independent constant',
                              derivative='sum(counts*a/(1+pi*a))', information='sum(counts*(a/(1+pi*a))^2)',
                              a='odds(p_s)/odds(.49562)-1', tolerance=TOLERANCE, max_iterations=MAX_ITERATIONS,
                              endpoints='D(0)<=0 -> exact 0; D(1)>=0 -> exact 1; flat/nonfinite are failures.',
                              safeguards='Bracketed Newton, outside-step and periodic bisection; freeze converged/failed rows.',
                              estimate_clipping=False, flags=SOLVER_FLAGS,
                              retained_estimates=total_boots,
                              new_test_status='Separate solver-equivalence, boundary, determinism and fold-isolation checks passed; hash-bound results/wp5_tests.json is an input.',
                              equivalence_caveat='EM fixed-point step tolerance is not the same as Newton root tolerance, especially near boundaries; tests compare against genuinely converged EM.'),
        interval=dict(method='All-500-estimate linear percentile bootstrap, 2.5%/97.5%',
                      coverage_target='GENERATING pi, not realized positive fraction or pi_hat',
                      failed_fits='Retained and counted; interval_solver_valid false for any failed bootstrap fit.',
                      calibration_uncertainty_included=False,
                      boundary_caveat='Nonregular boundary likelihoods/0-or-1 atoms can invalidate nominal percentile coverage.'),
        grid_summary=summary_frame.to_dict(orient='records'), acceptance_checks=checks,
        numerical_output_counts=dict(raw_csv_rows=len(raw_frame), summary_csv_rows=len(summary_frame),
                                     grid_npz_files=len(GRID), grid_json_files=len(GRID),
                                     original_estimates=total_originals, bootstrap_estimates=total_boots,
                                     calibration_oof_csv_rows=CALIBRATION_ROWS, planning_grid_csv_rows=251,
                                     recovery_plot_series=len(series), recovery_plot_finite_pairs=22,
                                     test_score_or_outcome_rows_loaded=0),
        break_even=planning, trigger=trigger,
        m5=dict(method_statement='Implemented from the standard derivation and validated by simulation; paper read from abstract only.',
                source_read_status='PubMed metadata and original abstract opened; explicit EM update equation is not displayed. No full-text formula verification.',
                source_url='https://pubmed.ncbi.nlm.nih.gov/11747533/',
                existing_read_status_source=file_info(ROOT / 'references.txt'),
                full_text_formula_verified=False, new_paper_access_attempted=True),
        assumptions=[
            'Stable class-conditional feature/score distributions and adequate probability calibration are unverified for live Company A.',
            'Covariate shift from handsets/plans can be misattributed to prevalence shift.',
            'Synthetic bootstrap conditions on the fitted empirical calibration pool; it excludes calibration/base-model uncertainty.',
            'The .49562 sample prior is balanced retrospective sampling, not a measured live prior.',
            'Planning economics use assumed 20% success, 6 months, 60% margin, $1/contact and $5000 fixed; no causal treatment labels exist.',
            'Day-60 mature labels override estimates; the Service-Fix Floor continues.',
        ], deviations=deviations, artifacts=artifacts,
    )
    row_counts = dict(calibration_policy=CALIBRATION_ROWS, planning_non_test=PLANNING_ROWS,
                      grids=len(GRID), original_batches=total_originals, bootstrap_fits=total_boots,
                      raw_csv=len(raw_frame), summary_csv=len(summary_frame), planning_grid=251,
                      test_rows_used=0)
    write_json('results/wp5_label_shift.json', body, __file__, TASK_INDEX,
               inputs + [OOF_CSV, OOF_JSON, raw_path, summary_path, planning_path] + checkpoint_files,
               row_counts)
    print(f'[E] WP5 {status}: {total_originals:,} originals, {total_boots:,} bootstrap fits; '
          f'original EM convergence={int(summary_frame.converged_originals.sum())}/{total_originals}, '
          f'bootstrap failures={int(summary_frame.bootstrap_failures.sum())}. '
          f'Actual acceptance recorded in {PRIMARY_JSON.as_posix()}.', flush=True)


if __name__ == '__main__':
    main()
