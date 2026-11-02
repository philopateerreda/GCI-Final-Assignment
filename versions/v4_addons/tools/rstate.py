"""Record the release cards and the final state after the verification clone passes."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4common as c  # noqa: E402
import fstate  # noqa: E402

AUTHORIZATION = (
    "**2026-10-31, account holder (philopateer):** asked for the v4 work to be pushed with commits and a better "
    "README, and delegated the release decisions to the orchestrator (\"I don't want to take decisions, just tell him "
    "what you see is the smartest move.\"). This is the authorization for the v4 release directive, including its "
    "section-0 amendment to G1 for `README.md`, `.gitignore`, the release receipt, commits, one branch and one tag. "
    "If the account holder later changes any gate file or the repository, their action wins."
)
CARDS = {
    'R0': dict(report='reports/R0_release_preflight.md',
               note='preconditions pass; boundary clean; 5 of 5 receipt hashes match; 0 files over 5 MB'),
    'R1': dict(report='reports/R1_prepush_checks.md',
               note='0 secrets; 0 provider columns in derived CSVs; 0 local paths; README 149 tokens bound; 0 EOL mismatches'),
    'R3': dict(report='reports/R3_release_report.md',
               note='tag v4.0.0; release/v4 verified in a clean clone; 15 local-only bindings disclosed'),
}


def main():
    fstate.CARDS = fstate.CARDS + list(CARDS)
    state = fstate.load()
    if AUTHORIZATION not in state['authorization']:
        state['authorization'].append(AUTHORIZATION)
    for card, row in CARDS.items():
        current = state['cards'].setdefault(card, {})
        if current.get('status') == 'COMPLETED_ACCEPTED':
            continue
        current.update(status='COMPLETED_ACCEPTED', date=c.today(), report=row['report'],
                       next_gate=None, note=row['note'])
        state['log'].append(f'{c.utc_now()} {card} -> COMPLETED_ACCEPTED' + (f" ({row['note']})" if row['note'] else ''))
    if state.get('project_status') != 'RELEASED_FALLBACK_A_v4.0.0':
        state['log'].append(f'{c.utc_now()} release -> RELEASED_FALLBACK_A_v4.0.0 '
                            '(branch release/v4; annotated tag v4.0.0; clean-clone verification passed)')
    state['project_status'] = 'RELEASED_FALLBACK_A_v4.0.0'
    fstate.save(state)
    print(fstate.STATE_MD.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
