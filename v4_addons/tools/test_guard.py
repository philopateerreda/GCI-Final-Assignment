"""G2 test-split guard.

Any v4 script that would read or score rows of the 15,000-row test split must call require_test_access().
It raises unless v4_addons/gates/H2_APPROVED.txt exists and contains ADOPT (human-created; the agent never
writes into gates/). test_ids() / assert_no_test_rows() let Track D and M0-M4 scripts prove they stayed on
non-test rows. Replaying cached frozen *probabilities* to reproduce published numbers (card M0) is not a
test-row read of features and is logged separately via log_replay().
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402

SPLIT_MANIFEST = c.ROOT / 'v1_frozen' / 'analysis_outputs' / 'tables' / 'split_manifest.csv'
GATE = c.GATES / 'H2_APPROVED.txt'
LOG = c.RESULTS / 'test_access_log.jsonl'


class TestSplitLocked(PermissionError):
    pass


def _log(kind, detail):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(dict(kind=kind, utc=c.utc_now(), detail=detail), sort_keys=True) + '\n')


def require_test_access(reason):
    if not GATE.is_file():
        _log('denied', dict(reason=reason, gate=GATE.relative_to(c.ROOT).as_posix()))
        raise TestSplitLocked('G2: test split locked; gates/H2_APPROVED.txt absent. Reason requested: ' + reason)
    content = GATE.read_text(encoding='utf-8').strip().upper()
    if 'ADOPT' not in content:
        _log('denied', dict(reason=reason, gate_content=content))
        raise TestSplitLocked('G2: H2 gate present but not ADOPT (' + content + ')')
    _log('granted', dict(reason=reason, gate_content=content, gate_sha256=c.digest(GATE)))
    return True


def test_ids():
    import pandas as pd
    split = pd.read_csv(SPLIT_MANIFEST, usecols=['Customer_ID', 'partition'])
    return set(split.loc[split.partition == 'test', 'Customer_ID'].astype(int))


def non_test_ids():
    import pandas as pd
    split = pd.read_csv(SPLIT_MANIFEST, usecols=['Customer_ID', 'partition'])
    return {name: set(group.Customer_ID.astype(int)) for name, group in split.groupby('partition') if name != 'test'}


def assert_no_test_rows(ids, context):
    overlap = set(int(item) for item in ids) & test_ids()
    _log('non_test_assertion', dict(context=context, rows=len(set(ids)), overlap=len(overlap)))
    if overlap:
        raise TestSplitLocked(f'G2: {len(overlap)} test-split rows present in {context}')
    return True


def log_replay(context, files):
    _log('cached_probability_replay', dict(context=context, files=[c.file_info(path) for path in files]))


if __name__ == '__main__':
    try:
        require_test_access('dry run from command line')
        print('test access GRANTED (H2 gate present with ADOPT)')
    except TestSplitLocked as error:
        print('test access DENIED:', error)
        sys.exit(2)
