"""Shared helpers for v4_addons. Must be the first project import in every v4 script.

Thread caps are set before numpy is imported (G3). A write-boundary audit hook
enforces G1/G6. verify_runtime() is the v3 function, extracted by AST from
v3_addons/src/common.py because importing that module installs a v3-only write
hook that would block v4 output.
"""
import os

for _variable in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[_variable] = '6'

import ast
import csv
import json
import re
import sys
from contextlib import redirect_stdout
from datetime import datetime, timezone
from hashlib import sha256
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADDONS = ROOT / 'v4_addons'
GATES = ADDONS / 'gates'
RESULTS = ADDONS / 'results'
REPORTS = ADDONS / 'reports'
SNAPSHOTS = ADDONS / 'snapshots'
V3 = ROOT / 'v3_addons'
V2 = ROOT / 'v2_work'
SEED = 20261028
THREADS = 6
PYTHON = Path('C:/Users/FGstore/AppData/Local/Programs/Python/Python311/python.exe')
TAGS = ('[E]', '[A]', '[R]')

assert sys.dont_write_bytecode, 'run with python -B'
assert Path(sys.executable).resolve() == PYTHON.resolve(), 'use the pinned Python 3.11 interpreter'

_EXTRA_ALLOWED = [Path(item).resolve() for item in os.environ.get('V4_ALLOW_WRITE', '').split(';') if item.strip()]


def _inside(path, parent):
    return path == parent or parent in path.parents


def audit_boundary(event, args):
    candidates = []
    if event == 'open':
        path, mode, flags = args
        writing = (mode is not None and any(letter in mode for letter in 'wax+')) or (
            flags is not None and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
        if writing and not isinstance(path, int):
            candidates.append(path)
    elif event in ('os.mkdir', 'os.remove', 'os.rmdir', 'os.chmod', 'os.utime', 'os.truncate', 'shutil.rmtree'):
        candidates.append(args[0])
    elif event in ('os.rename', 'os.replace', 'os.link', 'os.symlink', 'shutil.move'):
        candidates.extend(args[:2])
    elif event == 'shutil.copyfile':
        candidates.append(args[1])
    for value in candidates:
        try:
            path = Path(os.fsdecode(value)).resolve()
        except (TypeError, ValueError):
            continue
        if _inside(path, GATES):
            raise PermissionError('G6 violation: agent write into gates/: ' + str(path))
        if _inside(path, ROOT) and not _inside(path, ADDONS) and not any(_inside(path, allowed) for allowed in _EXTRA_ALLOWED):
            raise PermissionError('G1 violation: write outside v4_addons: ' + str(path))


sys.addaudithook(audit_boundary)

import numpy as np  # noqa: E402  (after thread caps)


def digest(path):
    result = sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def text_digest(text):
    return sha256(text.encode('utf-8')).hexdigest()


def relpath(path):
    path = Path(path).resolve()
    return path.relative_to(ROOT).as_posix() if _inside(path, ROOT) else path.as_posix()


def file_info(path):
    path = Path(path)
    return dict(path=relpath(path), present=path.is_file(), size=path.stat().st_size if path.is_file() else None,
                sha256=digest(path) if path.is_file() else None)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def today():
    return datetime.now(timezone.utc).date().isoformat()


def rng(task_index):
    return np.random.default_rng(SEED + task_index)


def _load_v3_verify_runtime():
    source_path = V3 / 'src' / 'common.py'
    source = source_path.read_text(encoding='utf-8')
    tree = ast.parse(source)
    node = next(item for item in tree.body if isinstance(item, ast.FunctionDef) and item.name == 'verify_runtime')
    segment = ast.get_source_segment(source, node)
    namespace = dict(np=np, ast=ast, StringIO=StringIO, redirect_stdout=redirect_stdout)
    exec(compile(segment, str(source_path), 'exec'), namespace)
    return namespace['verify_runtime'], text_digest(segment), relpath(source_path)


verify_runtime, VERIFY_RUNTIME_SHA256, VERIFY_RUNTIME_SOURCE = _load_v3_verify_runtime()


def runtime_record():
    pools = verify_runtime()
    return dict(source=VERIFY_RUNTIME_SOURCE, function_sha256=VERIFY_RUNTIME_SHA256, pools=pools,
                thread_cap=THREADS, env={key: os.environ.get(key) for key in (
                    'OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS')})


def provenance(script, task_index, inputs, row_counts=None, created_utc=None):
    paths = sorted({Path(path).resolve() for path in inputs})
    return dict(script=relpath(script), script_sha256=digest(script), seed=SEED + task_index,
                python_version=sys.version, input_files=[file_info(path) for path in paths],
                runtime=runtime_record(), created_utc=created_utc or utc_now(),
                row_counts=row_counts or {}, tags_used=list(TAGS))


def write_json(target, body, script, task_index, inputs, row_counts=None):
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    timestamp = None
    if target.exists():
        try:
            timestamp = json.loads(target.read_text(encoding='utf-8')).get('provenance', {}).get('created_utc')
        except (json.JSONDecodeError, AttributeError):
            timestamp = None
    output = dict(provenance=provenance(script, task_index, inputs, row_counts, timestamp), **body)
    target.write_text(json.dumps(output, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8')
    return output


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


# ---------------------------------------------------------------- source access

_PART = re.compile(r'^([^\[]*)((?:\[\d+\])*)$')


def json_get(obj, key):
    for part in key.split('.'):
        match = _PART.match(part)
        if not match:
            raise ValueError('bad json key part: ' + part)
        name, indices = match.group(1), re.findall(r'\[(\d+)\]', match.group(2))
        if name:
            obj = obj[name]
        for index in indices:
            obj = obj[int(index)]
    return obj


def _same_cell(cell, wanted):
    try:
        return abs(float(cell) - float(wanted)) <= 1e-12 * max(1.0, abs(float(wanted)))
    except (TypeError, ValueError):
        return str(cell) == str(wanted)


def csv_get(path, selector):
    with Path(path).open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    if selector == 'rowcount':
        return len(rows)
    match = re.match(r'^where\((.*)\)\.(\w+)$', selector)
    if not match:
        raise ValueError('bad csv selector: ' + selector)
    conditions = [item.split('=', 1) for item in match.group(1).split(';') if item]
    column = match.group(2)
    hits = [row for row in rows if all(_same_cell(row[name], wanted) for name, wanted in conditions)]
    if len(hits) != 1:
        raise LookupError(f'{selector} matched {len(hits)} rows in {path}')
    cell = hits[0][column]
    try:
        return float(cell)
    except ValueError:
        return cell


def text_get(path, selector, encoding='utf-8'):
    lines = Path(path).read_text(encoding=encoding).splitlines()
    match = re.match(r'^line:(\d+):regex:(.*)$', selector, re.S)
    if match:
        line = lines[int(match.group(1)) - 1]
        found = re.search(match.group(2), line)
        if not found:
            raise LookupError(f'{selector} not found in line {match.group(1)} of {path}')
        value = found.group(1)
        try:
            return float(value.replace(',', ''))
        except ValueError:
            return value
    if selector == 'linecount':
        return len(lines)
    raise ValueError('bad text selector: ' + selector)


def read_source(source_file, source_key, encoding='utf-8'):
    path = ROOT / source_file
    suffix = path.suffix.lower()
    if suffix == '.json':
        return json_get(read_json(path), source_key)
    if suffix == '.csv':
        return csv_get(path, source_key)
    return text_get(path, source_key, encoding)


# ---------------------------------------------------------------- safe formulas

def _formula_namespace(values):
    from scipy.special import expit, logit
    from scipy.stats import beta, norm
    namespace = dict(values)
    namespace.update(
        sqrt=np.sqrt, exp=np.exp, log=np.log, abs=abs, min=min, max=max, round=round,
        norm_cdf=norm.cdf, norm_ppf=norm.ppf, norm_sf=norm.sf,
        beta_cdf=lambda x, a, b: float(beta.cdf(x, a, b)), beta_sf=lambda x, a, b: float(beta.sf(x, a, b)),
        beta_ppf=lambda q, a, b: float(beta.ppf(q, a, b)), beta_mean=lambda a, b: a / (a + b),
        expit=expit, logit=logit)
    return namespace


_ALLOWED_NODES = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Name, ast.Call, ast.Load,
                  ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.USub, ast.UAdd, ast.Mod, ast.FloorDiv,
                  ast.Compare, ast.Gt, ast.Lt, ast.GtE, ast.LtE, ast.Eq, ast.IfExp)


def evaluate(formula, values):
    tree = ast.parse(formula, mode='eval')
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise ValueError(f'disallowed syntax {type(node).__name__} in formula: {formula}')
        if isinstance(node, ast.Call) and not isinstance(node.func, ast.Name):
            raise ValueError('only plain function calls allowed: ' + formula)
    namespace = _formula_namespace(values)
    result = eval(compile(tree, '<formula>', 'eval'), {'__builtins__': {}}, namespace)
    return float(result) if isinstance(result, (np.floating, np.integer)) else result


def close(a, b, rel=1e-9, absolute=1e-9):
    if isinstance(a, bool) or isinstance(b, bool) or isinstance(a, str) or isinstance(b, str):
        return a == b
    return abs(float(a) - float(b)) <= max(absolute, rel * max(abs(float(a)), abs(float(b))))


# ---------------------------------------------------------------- number binding

class Numbers:
    """Collects provenance-bound numbers for one results JSON (G4)."""

    def __init__(self):
        self.entries = {}

    def value(self, name):
        return self.entries[name]['value']

    def values(self):
        return {name: entry['value'] for name, entry in self.entries.items()}

    def source(self, name, source_file, source_key, tag='[E]', note=None, seed=None, value=None, encoding='utf-8'):
        assert tag in TAGS, tag
        source_file = relpath(ROOT / source_file)
        found = read_source(source_file, source_key, encoding)
        if value is not None and not close(found, value):
            raise AssertionError(f'{name}: source value {found!r} != supplied {value!r}')
        entry = dict(value=found, source_file=source_file, source_key=source_key,
                     sha256_of_source=digest(ROOT / source_file), tag=tag, source_encoding=encoding)
        if note:
            entry['note'] = note
        if seed is not None:
            entry['seed'] = seed
        self.entries[name] = entry
        return found

    def derived(self, name, formula, tag='[E]', note=None, seed=None, expect=None, tolerance=None, discrepancy_note=None):
        assert tag in TAGS, tag
        value = evaluate(formula, self.values())
        entry = dict(value=value, formula=formula, inputs=sorted(set(re.findall(r'[A-Za-z_]\w*', formula)) & set(self.entries)),
                     source_file=None, source_key=None, sha256_of_source=None, tag=tag)
        if note:
            entry['note'] = note
        if seed is not None:
            entry['seed'] = seed
        if expect is not None:
            entry['expected'] = expect
            entry['expected_tolerance'] = tolerance
            entry['matches_expected'] = bool(abs(float(value) - float(expect)) <= float(tolerance))
            if not entry['matches_expected'] and discrepancy_note:
                entry['discrepancy_note'] = discrepancy_note
        self.entries[name] = entry
        return value

    def declared(self, name, value, tag, note):
        """A design constant chosen in this brief (tag [R] or [A]); formula is the literal."""
        return self.derived(name, repr(value), tag=tag, note=note)

    def computed(self, name, value, tag, note, source_file=None, source_key=None, seed=None, inputs=None):
        """A value produced by code in this run (e.g. a simulation); provenance is the script + seed."""
        assert tag in TAGS, tag
        entry = dict(value=value, tag=tag, note=note, computed=True, inputs=inputs or [],
                     source_file=relpath(ROOT / source_file) if source_file else None, source_key=source_key,
                     sha256_of_source=digest(ROOT / source_file) if source_file else None)
        if seed is not None:
            entry['seed'] = seed
        self.entries[name] = entry
        return value

    def body(self):
        return dict(numbers=self.entries)


# ---------------------------------------------------------------- rendering

_NUMERIC_TOKEN = re.compile(r'(?<![A-Za-z_\-])[-\u2212+]?\$?\d[\d,]*(?:\.\d+)?%?k?(?![A-Za-z_])')


MINUS = '\u2212'
TIMES = '\u00d7'


def format_number(value, spec):
    """spec examples: 'pct1' -> 12.3%, 'pct2', 'pp1', 'usd0' -> $1,234, 'usd2', 'usdk1' -> $1.2k, 'f3', 'int', 'raw'."""
    if spec == 'raw':
        return repr(value)
    if spec == 'int':
        return f'{int(round(value)):,}'
    if spec == 'intk':
        return f'{int(round(value)):,}k'
    if spec == 'kint':
        return f'{value / 1000:g}k'
    sign = MINUS if value < 0 else ''
    if spec.startswith('pct'):
        return f'{value * 100:.{int(spec[3:])}f}%'
    if spec.startswith('pc'):
        return f'{value:.{int(spec[2:])}f}%'
    if spec.startswith('ppc'):
        return f'{value:.{int(spec[3:])}f} pp'
    if spec.startswith('pp'):
        return f'{value * 100:.{int(spec[2:])}f} pp'
    if spec.startswith('usdk'):
        return f'{sign}${abs(value) / 1000:.{int(spec[4:])}f}k'
    if spec.startswith('usd'):
        return f'{sign}${abs(value):,.{int(spec[3:])}f}'
    if spec.startswith('f'):
        return f'{value:.{int(spec[1:])}f}'
    if spec.startswith('x'):
        return f'{value:.{int(spec[1:])}f}{TIMES}'
    raise ValueError(spec)


class Renderer:
    """Formats bound numbers into report text and records every rendered token (for check_numbers --scan)."""

    def __init__(self, numbers, results_json):
        self.numbers = numbers
        self.results_json = relpath(results_json)
        self.tokens = []

    def n(self, name, spec='raw'):
        value = self.numbers.value(name) if isinstance(self.numbers, Numbers) else self.numbers[name]['value']
        token = format_number(value, spec)
        self.tokens.append(dict(token=token, name=name, spec=spec, value=value))
        return token

    def registry(self):
        return dict(results_json=self.results_json, tokens=self.tokens)

    def write(self, target, text, registry_target):
        target = Path(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')
        Path(registry_target).write_text(json.dumps(dict(report=relpath(target), report_sha256=text_digest(text),
                                                        **self.registry()), indent=2) + '\n', encoding='utf-8')


def gate_file(name):
    path = GATES / name
    return path if path.is_file() else None


def gate_text(name):
    path = gate_file(name)
    return path.read_text(encoding='utf-8').strip() if path else None
