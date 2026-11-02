#!/usr/bin/env python
"""Create a SHA256 manifest of a folder's working tree (read-only).

Excludes .git and the reorg log itself by default. Re-runnable; writes atomically.
Usage:
  python make_manifest.py --root <finalA> --out <csv> [--dry-run]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

EXCLUDES = {".git", "finalA_reorg_log"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def mtime_iso(ns: int) -> str:
    dt = datetime.fromtimestamp(ns / 1e9, tz=timezone.utc)
    return dt.isoformat(timespec="microseconds")


def collect(root: Path) -> list[Path]:
    out: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = Path(dirpath).relative_to(root)
        dirnames[:] = sorted(
            d for d in dirnames if not (rel_dir == Path(".") and d in EXCLUDES)
        )
        for name in sorted(filenames):
            p = Path(dirpath) / name
            rel = p.relative_to(root)
            if rel.parts and rel.parts[0] in EXCLUDES:
                continue
            out.append(p)
    return sorted(out, key=lambda p: p.relative_to(root).as_posix())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        print(f"ERROR: root not found: {root}", file=sys.stderr)
        return 2
    files = collect(root)
    total_bytes = sum(p.stat().st_size for p in files)
    print(f"FILES={len(files)} BYTES={total_bytes}")
    if args.dry_run:
        print("DRY-RUN: no manifest written")
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix="manifest-", suffix=".csv", dir=args.out.parent)
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["path", "size_bytes", "mtime_utc", "sha256"])
            for i, p in enumerate(files, 1):
                st = p.stat()
                w.writerow(
                    [
                        p.relative_to(root).as_posix(),
                        st.st_size,
                        mtime_iso(st.st_mtime_ns),
                        sha256_file(p),
                    ]
                )
                if i % 500 == 0:
                    print(f"hashed {i}/{len(files)}", flush=True)
        os.replace(tmp_name, args.out)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)
    summary = {
        "root": str(root),
        "files": len(files),
        "bytes": total_bytes,
        "excluded_top_level": sorted(EXCLUDES),
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "manifest": str(args.out),
    }
    summary_path = args.out.with_name(args.out.stem + "_summary.json")
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"WROTE {args.out}")
    print(f"WROTE {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
