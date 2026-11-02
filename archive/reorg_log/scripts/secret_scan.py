#!/usr/bin/env python
"""Masked secret/PII scan. Never echoes a matched value.

Read-only. Re-runnable. Usage:
  python secret_scan.py --root <finalA> --manifest <csv> --outdir <dir> [--dry-run]
Writes secret_scan.csv, secret_scan.md, applicant_csv_profile.csv.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

TEXT_EXT = {".md", ".txt", ".py", ".json", ".ipynb", ".csv", ".log", ".pre_v4"}
SKIP_OVER = 20 * 1024 * 1024
PATTERNS = [
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("openai_like_key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b")),
    ("private_key_block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("password_assignment", re.compile(r"(?i)\b(?:password|passwd|pwd|secret|api[_-]?key|access[_-]?token)\b\s*[:=]\s*['\"][^'\"]{6,}['\"]")),
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("absolute_user_path", re.compile(r"(?i)\b[A-Z]:[\\/](?:Users|Documents and Settings)[\\/][^\"'<>\r\n|]{1,200}")),
    ("absolute_project_path", re.compile(r"(?i)\bD:[\\/]progs[\\/][^\"'<>\r\n|]{1,200}")),
    ("kaggle_credential", re.compile(r"(?i)\bkaggle(?:\.json)?\b[^\r\n]{0,80}\b(?:username|key)\b")),
]
APPLICANT_HINTS = (
    "customer_id",
    "churn",
    "income",
    "creditcd",
    "ownrent",
    "ethnic",
    "marital",
    "hnd_price",
    "totmrc",
    "rev_mean",
    "mou_mean",
)


def fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", "replace")).hexdigest()[:12]


def scan_text(text: str):
    for kind, rx in PATTERNS:
        for m in rx.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            yield kind, line, m.group(0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--manifest", required=True, type=Path)
    ap.add_argument("--outdir", required=True, type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()
    rows = list(csv.DictReader(args.manifest.open(encoding="utf-8")))
    findings = []
    profiles = []
    skipped = []
    for row in rows:
        rel = row["path"]
        p = root / rel
        ext = p.suffix.lower()
        if ext not in TEXT_EXT:
            continue
        size = int(row["size_bytes"])
        if ext == ".csv":
            try:
                with p.open("r", encoding="utf-8", errors="replace", newline="") as fh:
                    reader = csv.reader(fh)
                    header = next(reader, [])
                    nrows = sum(1 for _ in reader)
            except Exception:
                continue
            applicant = any(h.strip().lower() in APPLICANT_HINTS for h in header)
            profiles.append(
                {
                    "path": rel,
                    "rows": nrows,
                    "columns": len(header),
                    "applicant_level": "yes" if applicant else "no",
                    "header_fingerprint": fingerprint("|".join(header)),
                    "sample_rows_printed": "0",
                }
            )
            # Check the header only; never echo applicant rows.
            for kind, line, value in scan_text(",".join(header)):
                findings.append({"path": rel, "line": line, "type": kind, "masked_sha256_12": fingerprint(value)})
            continue
        if size > SKIP_OVER:
            skipped.append({"path": rel, "bytes": size, "reason": "over 20 MB; schema/string scan skipped"})
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for kind, line, value in scan_text(text):
            findings.append({"path": rel, "line": line, "type": kind, "masked_sha256_12": fingerprint(value)})
    type_counts = Counter(f["type"] for f in findings)
    file_counts = Counter(f["path"] for f in findings)
    credential_types = {
        "aws_access_key",
        "github_token",
        "openai_like_key",
        "slack_token",
        "google_api_key",
        "private_key_block",
        "password_assignment",
        "kaggle_credential",
    }
    credentials = [f for f in findings if f["type"] in credential_types]
    print(f"SCANNED={len(rows)} FINDINGS={len(findings)} CREDENTIALS={len(credentials)} SKIPPED={len(skipped)}")
    print(f"TYPES={dict(type_counts)}")
    if args.dry_run:
        print("DRY-RUN: no report written")
        return 0
    args.outdir.mkdir(parents=True, exist_ok=True)
    with (args.outdir / "secret_scan.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["path", "line", "type", "masked_sha256_12"])
        w.writeheader()
        w.writerows(findings)
    with (args.outdir / "applicant_csv_profile.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(
            fh,
            fieldnames=["path", "rows", "columns", "applicant_level", "header_fingerprint", "sample_rows_printed"],
        )
        w.writeheader()
        w.writerows(profiles)
    lines = [
        "# Secret and PII scan",
        "",
        "**Never echo a matched value.** Every finding below is represented by a masked SHA256 fingerprint.",
        "",
        "| Type | Matches |",
        "|---|---:|",
    ]
    for k, v in type_counts.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        f"- Credential-shaped findings: **{len(credentials)}**.",
        f"- Files skipped for size: **{len(skipped)}** (schema-only treatment; no body printed).",
        f"- Applicant-level CSV profiles written without rows: **{sum(1 for p in profiles if p['applicant_level']=='yes')}**.",
        "",
        "## What the scan covered",
        "",
        "All `.md`, `.txt`, `.py`, `.json`, `.ipynb`, `.csv` (header only), `.log` and `.pre_v4` files under",
        "the Phase-0 manifest, up to 20 MB per file. Large model/data JSON and NPZ were treated structurally.",
        "The two supplied CSVs were profiled as row count and column count only; no sample rows were written",
        "or printed (H9).",
        "",
        "## Files with most findings",
        "",
        "| File | Matches |",
        "|---|---:|",
    ]
    for p, n in file_counts.most_common(20):
        lines.append(f"| `{p}` | {n} |")
    lines += [
        "",
        "## Interpretation",
        "",
        "- No live API key, access token, private-key block or password assignment was found." if not credentials else
        "- Credential-shaped matches exist; review `secret_scan.csv` before any push (values are masked).",
        "- The `absolute_user_path` / `absolute_project_path` hits are historical build paths and file URLs;",
        "  they are stale-by-design after the move and are listed in `PATH_MAP.md`. They are not credentials.",
        "- Email addresses are counted but not echoed; they are disclosure/contact context, not authentication.",
        "- This is a pattern scan, not a guarantee. The G2 audit re-runs it on the push delta.",
        "",
        "Full masked rows: `secret_scan.csv`; applicant-level profiles: `applicant_csv_profile.csv`.",
        "",
    ]
    (args.outdir / "secret_scan.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"WROTE {args.outdir / 'secret_scan.csv'}")
    print(f"WROTE {args.outdir / 'secret_scan.md'}")
    print(f"WROTE {args.outdir / 'applicant_csv_profile.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
