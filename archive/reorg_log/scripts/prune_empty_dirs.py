#!/usr/bin/env python
"""Remove empty directories left behind by the reorganization.

Files are never touched. The git directory is excluded.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()
    removed: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        p = Path(dirpath)
        if p == root or ".git" in p.parts:
            continue
        try:
            next(p.iterdir())
            continue
        except StopIteration:
            pass
        try:
            if args.write:
                p.rmdir()
            removed.append(p.relative_to(root).as_posix())
        except OSError:
            pass
    removed.sort()
    print(f"empty_dirs={len(removed)} write={args.write}")
    for r in removed:
        print(r)
    log = root / "finalA_reorg_log" / "empty_dirs_removed.txt"
    if args.write:
        log.write_text("\n".join(removed) + ("\n" if removed else ""), encoding="utf-8")
        print(f"WROTE {log}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
