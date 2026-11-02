#!/usr/bin/env python
"""Reconcile a robocopy mirror: path set, counts, bytes, 20 SHA256 samples, mtimes.

Read-only. Re-runnable. Usage:
  python verify_backup.py --source <finalA> --backup <finalA_BACKUP_...> \
      --out <json> [--dry-run]
The reorg log folder is excluded from the source side because it was created after
the backup.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
from pathlib import Path

EXCLUDE_TOP = {"finalA_reorg_log"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def walk(root: Path, exclude: set[str]) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = Path(dirpath).relative_to(root)
        if rel_dir == Path("."):
            dirnames[:] = [d for d in dirnames if d not in exclude]
        for name in filenames:
            p = Path(dirpath) / name
            out[p.relative_to(root).as_posix()] = p
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--backup", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    src = walk(args.source.resolve(), EXCLUDE_TOP)
    dst = walk(args.backup.resolve(), set())
    missing = sorted(set(src) - set(dst))
    extra = sorted(set(dst) - set(src))
    size_mismatch = []
    for rel in sorted(set(src) & set(dst)):
        if src[rel].stat().st_size != dst[rel].stat().st_size:
            size_mismatch.append(rel)
    keys = sorted(set(src) & set(dst))
    rng = random.Random(20261102)
    sample = rng.sample(keys, min(20, len(keys)))
    # Ensure the frozen artifacts and a .git object are represented.
    for must in [
        "philopateer.ipynb",
        "philopateer.pdf",
        "philopateer.pptx",
        "README.docx",
        "ENG_Company _A_ Dataset Overview.docx",
        "v1_frozen/sha256_manifest.json",
        "telecom/Client.csv",
    ]:
        if must in src and must not in sample:
            sample.append(must)
    sample = sorted(set(sample))[:20]
    hash_ok, hash_bad = 0, []
    mtimes = []
    for rel in sample:
        sh = sha256_file(src[rel])
        bh = sha256_file(dst[rel])
        if sh == bh:
            hash_ok += 1
        else:
            hash_bad.append({"path": rel, "source": sh, "backup": bh})
        mtimes.append(
            {
                "path": rel,
                "source_mtime_ns": src[rel].stat().st_mtime_ns,
                "backup_mtime_ns": dst[rel].stat().st_mtime_ns,
                "equal": src[rel].stat().st_mtime_ns == dst[rel].stat().st_mtime_ns,
            }
        )
    src_bytes = sum(p.stat().st_size for p in src.values())
    dst_bytes = sum(p.stat().st_size for p in dst.values())
    report = {
        "source": str(args.source),
        "backup": str(args.backup),
        "source_files": len(src),
        "backup_files": len(dst),
        "source_bytes": src_bytes,
        "backup_bytes": dst_bytes,
        "missing_in_backup": missing,
        "extra_in_backup": extra,
        "size_mismatch": size_mismatch,
        "sample": sample,
        "hashes_equal": hash_ok,
        "hashes_bad": hash_bad,
        "mtimes": mtimes,
        "mtimes_equal": sum(1 for m in mtimes if m["equal"]),
        "pass": not missing
        and not extra
        and not size_mismatch
        and not hash_bad
        and src_bytes == dst_bytes
        and all(m["equal"] for m in mtimes),
    }
    print(json.dumps({k: report[k] for k in report if k not in {"mtimes", "sample"}}, indent=2))
    print(f"SAMPLE={len(sample)} HASHES_EQUAL={hash_ok} MTIMES_EQUAL={report['mtimes_equal']}")
    if args.dry_run:
        print("DRY-RUN: no report written")
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"WROTE {args.out}")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
