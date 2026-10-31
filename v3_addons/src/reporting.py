from common import ADDONS, file_info


def write_report(index, title, status, inputs, assumptions, method, results, acceptance, deviations, allowed, forbidden):
    hashes = [file_info(path) for path in inputs]
    lines = [f'# WP{index} — {title}', f'Status: {status}', '', 'Inputs:']
    lines.extend(f'- [E] `{item["path"]}` — SHA-256 `{item["sha256"]}`.' for item in hashes)
    lines += ['', 'Population / assumptions:'] + assumptions
    lines += ['', 'Method (≤10 lines)', method, '', 'Results:'] + results
    lines += ['', 'Acceptance checks:'] + acceptance
    lines += ['', 'Deviations from brief:'] + (deviations or ['[E] None.'])
    lines += ['', 'Claims now allowed:', allowed, '', 'Claims still forbidden:', forbidden,
              '', 'Open questions for human: [E] None; integration remains a separate human decision.']
    (ADDONS/f'reports/WP{index}_report.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
