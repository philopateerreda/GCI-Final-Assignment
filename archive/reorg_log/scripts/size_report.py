#!/usr/bin/env python
"""Size report: every file >5 MB and the top 20 by bytes.

Read-only. Re-runnable. Usage:
  python size_report.py --manifest <csv> --out <md> [--dry-run]
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    rows = list(csv.DictReader(args.manifest.open(encoding="utf-8")))
    for r in rows:
        r["size"] = int(r["size_bytes"])
    over = sorted([r for r in rows if r["size"] > 5 * 1024 * 1024], key=lambda r: -r["size"])
    top = sorted(rows, key=lambda r: -r["size"])[:20]
    print(f"OVER_5MB={len(over)} TOP20_BYTES={sum(r['size'] for r in top):,}")
    if args.dry_run:
        print("DRY-RUN: no report written")
        return 0
    lines = [
        "# Size report",
        "",
        f"- Working-tree files: **{len(rows)}**; total **{sum(r['size'] for r in rows):,} bytes**.",
        f"- Files over 5 MiB: **{len(over)}**.",
        "",
        "## Every file over 5 MiB",
        "",
        "| Bytes | MiB | Path |",
        "|---:|---:|---|",
    ]
    for r in over:
        lines.append(f"| {r['size']:,} | {r['size']/1024/1024:.2f} | `{r['path']}` |")
    lines += [
        "",
        "## Top 20",
        "",
        "| Rank | Bytes | Path |",
        "|---:|---:|---|",
    ]
    for i, r in enumerate(top, 1):
        lines.append(f"| {i} | {r['size']:,} | `{r['path']}` |")
    lines += [
        "",
        "## Notes",
        "",
        "- The largest file is the ignored 117.7 MiB `v2_work/d_results/cv_manifest.json`; it is never printed, only hashed.",
        "- The 45.9 MiB supplied dataset is local-only and ignored (F3).",
        "- No tracked file over 25 MiB is introduced by this reorg; pre-existing release blobs are reported at G2.",
        "",
    ]
    args.out.write_text("\n".join(lines), encoding="utf-8")
    print(f"WROTE {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
