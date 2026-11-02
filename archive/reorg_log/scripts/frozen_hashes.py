#!/usr/bin/env python
"""Hash the frozen set (F1, F2, F3) and prove v1 manifest coverage.

Read-only. Re-runnable. Usage:
  python frozen_hashes.py --root <finalA> --out <csv> [--dry-run]
The v1 manifest keys are interpreted in memory against candidate bases; the
manifest itself is never modified.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

F1 = [
    "philopateer.ipynb",
    "philopateer.pdf",
    "philopateer.pptx",
    "README.docx",
    "ENG_Company _A_ Dataset Overview.docx",
]
F3 = ["telecom/Client.csv", "telecom/Record.csv"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()
    v1_candidates = [root / "v1_frozen", root / "versions" / "v1_frozen"]
    v1dir = next((p for p in v1_candidates if (p / "sha256_manifest.json").is_file()), None)
    if v1dir is None:
        print("ERROR: no v1_frozen/sha256_manifest.json in either layout", file=sys.stderr)
        return 2
    manifest_path = v1dir / "sha256_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    # Candidate path bases for manifest keys. Do not trust a single base.
    candidates = [v1dir, root]
    scores = {}
    for base in candidates:
        scores[str(base)] = sum(
            1
            for rel, meta in manifest.items()
            if (base / rel).is_file()
            and sha256_file(base / rel) == meta.get("sha256")
        )
    base = max(candidates, key=lambda b: scores[str(b)])
    rows = []

    def locate(rel: str, kind: str) -> Path | None:
        if kind == "f1":
            bases = [root, root / "submission", root / "docs" / "reference"]
            for b in bases:
                if (b / rel).is_file():
                    return b / rel
            for b in bases:
                if (b / Path(rel).name).is_file():
                    return b / Path(rel).name
        elif kind == "f3":
            for b in [root, root / "data"]:
                if (b / rel).is_file():
                    return b / rel
        return None

    def add(fid, item, path, expected=None, note="", kind="f1"):
        p = locate(path, kind)
        if p is None:
            rows.append([fid, item, path, "", "", expected or "", "MISSING", note])
            return
        digest = sha256_file(p)
        size = p.stat().st_size
        match = "" if expected is None else ("PASS" if digest == expected else "FAIL")
        rows.append([fid, item, p.relative_to(root).as_posix(), digest, size, expected or "", match, note])

    for rel in F1:
        add("F1", "hand-in artifact", rel)
    add("F2", "v1 manifest", (v1dir / "sha256_manifest.json").relative_to(root).as_posix())
    for rel, meta in sorted(manifest.items()):
        p = base / rel
        expected = meta.get("sha256", "")
        if p.is_file():
            digest = sha256_file(p)
            rows.append(
                [
                    "F2",
                    "v1 snapshot",
                    p.relative_to(root).as_posix(),
                    digest,
                    p.stat().st_size,
                    expected,
                    "PASS" if digest == expected else "FAIL",
                    f"manifest_bytes={meta.get('bytes')}",
                ]
            )
        else:
            rows.append(
                ["F2", "v1 snapshot", p.relative_to(root).as_posix(), "", "", expected, "MISSING", ""]
            )
    for rel in F3:
        add("F3", "supplied dataset", rel, kind="f3")
    v1_files = sorted(
        p.relative_to(v1dir).as_posix()
        for p in v1dir.rglob("*")
        if p.is_file()
    )
    manifest_files = sorted(manifest.keys())
    uncovered = sorted(set(v1_files) - set(manifest_files) - {"sha256_manifest.json"})
    extra = sorted(set(manifest_files) - set(v1_files))
    f2_rows = [r for r in rows if r[0] == "F2" and r[1] == "v1 snapshot"]
    coverage = {
        "manifest_entries": len(manifest),
        "manifest_base": base.relative_to(root).as_posix() or ".",
        "candidate_match_counts": scores,
        "v1_tree_files_excluding_manifest": len(v1_files) - 1,
        "v1_tree_files_including_manifest": len(v1_files),
        "manifest_entries_present": sum(1 for r in f2_rows if r[6] != "MISSING"),
        "manifest_entries_pass": sum(1 for r in f2_rows if r[6] == "PASS"),
        "manifest_entries_fail": sum(1 for r in f2_rows if r[6] == "FAIL"),
        "manifest_entries_missing": sum(1 for r in f2_rows if r[6] == "MISSING"),
        "v1_files_uncovered_by_manifest": uncovered,
        "manifest_entries_without_v1_file": extra,
        "pass": all(r[6] == "PASS" for r in rows if r[6]),
    }
    print(json.dumps(coverage, indent=2))
    if not args.dry_run:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["id", "item", "path", "sha256", "bytes", "expected_sha256", "match", "note"])
            w.writerows(rows)
        (args.out.with_name("frozen_coverage.json")).write_text(
            json.dumps(coverage, indent=2) + "\n", encoding="utf-8"
        )
        print(f"WROTE {args.out}")
        print(f"WROTE {args.out.with_name('frozen_coverage.json')}")
    else:
        print("DRY-RUN: no files written")
    return 0 if coverage["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
