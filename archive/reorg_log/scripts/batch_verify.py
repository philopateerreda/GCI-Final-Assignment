#!/usr/bin/env python
"""Verify one executed batch before its commit.

Read-only. Usage:
  python batch_verify.py --root <finalA> --logdir <dir> --batch R1
Writes batch_<batch>_proof.md and ignore_invariance_<batch>.txt.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path

BATCH_PATHS = {
    "R1": ("README.md", "archive", ".gitignore"),
    "R2": ("v1_frozen", "v2_work", "v3_addons", "v4_addons", "versions", ".gitignore"),
    "R3": ("analysis_outputs", "evidence", ".gitignore"),
    "R4": (
        "FINAL_ASSESSMENT_HANDOFF.md",
        "FINAL_ASSESSMENT_READING_NOTE.md",
        "FINAL_V2_UPGRADE_REPORT.md",
        "README.docx",
        "ENG_Company _A_ Dataset Overview.docx",
        "tutorial (2).ipynb",
        "docs",
        ".gitignore",
    ),
    "R5": ("telecom", "data", ".gitignore"),
    "R6": ("philopateer.ipynb", "philopateer.pdf", "philopateer.pptx", "submission"),
    "R7": (
        "analysis_pipeline.py",
        "build_notebook.py",
        "export_and_verify.py",
        "restore_v1.py",
        "references.txt",
        "requirements-python311.txt",
        "pipeline",
    ),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(root), "-c", "core.quotepath=off", *args])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--logdir", required=True, type=Path)
    ap.add_argument("--batch", required=True)
    args = ap.parse_args()
    root = args.root.resolve()
    logdir = args.logdir.resolve()
    batch = args.batch
    plan = list(csv.DictReader((logdir / "move_plan.csv").open(encoding="utf-8")))
    moves = list(csv.DictReader((logdir / "moves.csv").open(encoding="utf-8")))
    batch_moves = [m for m in moves if m["batch"] == batch]
    expected = []
    for r in plan:
        cat = r["category"]
        b = (
            "R1" if cat == "residue" or r["old_path"] == "README.md" else
            "R2" if cat == "version" else
            "R3" if cat == "evidence" else
            "R4" if cat in {"doc", "course_reference"} else
            "R5" if cat == "data" else
            "R6" if cat == "handin" else
            "R7" if cat in {"pipeline_entry", "pipeline_metadata"} else "ROOT"
        )
        if b == batch:
            expected.append(r)
    errors = []
    if len(batch_moves) != len(expected):
        errors.append(f"move count {len(batch_moves)} != plan {len(expected)}")
    expected_by_old = {r["old_path"]: r for r in expected}
    bytes_total = 0
    for m in batch_moves:
        p = root / m["new_path"]
        if not p.is_file():
            errors.append(f"missing moved file: {m['new_path']}")
            continue
        bytes_total += p.stat().st_size
        if sha256(p) != m["sha256_before"]:
            errors.append(f"sha mismatch: {m['new_path']}")
        if int(m["bytes"]) != p.stat().st_size:
            errors.append(f"size mismatch: {m['new_path']}")
        if int(m["mtime_utc_ticks"]) != p.stat().st_mtime_ns // 100 + 116444736000000000:
            errors.append(f"mtime mismatch: {m['new_path']}")
    # plan has no bytes; sum inventory
    inventory = {r["path"]: int(r["bytes"]) for r in csv.DictReader((logdir / "inventory.csv").open(encoding="utf-8"))}
    expected_bytes = sum(inventory[r["old_path"]] for r in expected)
    if bytes_total != expected_bytes:
        errors.append(f"batch bytes {bytes_total} != plan {expected_bytes}")

    # D4: map baseline ignored paths through all moves so far.
    old_to_new = {m["old_path"]: m["new_path"] for m in moves}
    ignored_before = {p for p in (logdir / "ignored_before.txt").read_text(encoding="utf-8").splitlines() if p}
    tracked_before = {p for p in (logdir / "tracked_before.txt").read_text(encoding="utf-8").splitlines() if p}
    current_ignored = {
        p.decode("utf-8", "surrogateescape")
        for p in git(root, "ls-files", "-z", "--others", "--ignored", "--exclude-standard").split(b"\0")
        if p
    }
    current_ignored = {p for p in current_ignored if not p.startswith("finalA_reorg_log/")}
    mapped = {old_to_new.get(p, p) for p in ignored_before}
    lost = sorted(mapped - current_ignored)
    gained = sorted(current_ignored - mapped)
    if lost:
        errors.append(f"D4 lost {len(lost)} ignored paths")
    if gained:
        errors.append(f"D4 gained {len(gained)} ignored paths")

    # Staged paths: only this batch + .gitignore; tracked moves must be R100.
    staged = git(root, "diff", "--cached", "-M", "--name-status", "-z").split(b"\0")
    staged_paths = []
    r100 = 0
    i = 0
    while i < len(staged) and staged[i]:
        status = staged[i].decode("utf-8", "surrogateescape")
        if status.startswith("R"):
            old = staged[i + 1].decode("utf-8", "surrogateescape")
            new = staged[i + 2].decode("utf-8", "surrogateescape")
            staged_paths.extend([old, new])
            if status == "R100":
                r100 += 1
            i += 3
        else:
            path = staged[i + 1].decode("utf-8", "surrogateescape")
            staged_paths.append(path)
            i += 2
    allowed = set()
    for r in expected:
        allowed.add(r["old_path"])
        allowed.add(r["new_path"])
    allowed.add(".gitignore")
    unexpected = sorted(set(staged_paths) - allowed)
    if unexpected:
        errors.append(f"unexpected staged paths: {unexpected[:5]}")
    tracked_moves = [m for m in batch_moves if m["tracked"] == "yes"]
    if r100 != len(tracked_moves):
        errors.append(f"R100 count {r100} != tracked moves {len(tracked_moves)}")

    # Unstaged / untracked sanity, allowing only the log directory.
    unstaged = git(root, "diff", "--name-only", "-z").split(b"\0")
    unstaged = [p.decode("utf-8", "surrogateescape") for p in unstaged if p]
    untracked = [
        p.decode("utf-8", "surrogateescape")
        for p in git(root, "ls-files", "--others", "--exclude-standard", "-z").split(b"\0")
        if p
    ]
    untracked = [p for p in untracked if not p.startswith("finalA_reorg_log/")]
    if unstaged:
        errors.append(f"unstaged paths: {unstaged[:5]}")
    if untracked:
        errors.append(f"unexpected untracked paths: {untracked[:5]}")

    # Frozen check for batches that touch F1/F2/F3.
    frozen = {}
    if batch in {"R2", "R4", "R5", "R6"}:
        frozen = _frozen_check(root, logdir, batch)
        if not frozen.get("pass"):
            errors.append(f"frozen check failed: {frozen.get('errors')}")

    proof = {
        "batch": batch,
        "expected_files": len(expected),
        "moved_files": len(batch_moves),
        "bytes": bytes_total,
        "expected_bytes": expected_bytes,
        "r100": r100,
        "tracked_moves": len(tracked_moves),
        "ignored_before": len(ignored_before),
        "ignored_now": len(current_ignored),
        "lost": len(lost),
        "gained": len(gained),
        "frozen": frozen,
        "errors": errors,
        "pass": not errors,
    }
    print(json.dumps(proof, indent=2))
    (logdir / f"ignore_invariance_{batch}.txt").write_text(
        f"batch={batch}\nignored_before={len(ignored_before)}\nignored_now={len(current_ignored)}\n"
        f"lost={len(lost)}\ngained={len(gained)}\npass={not lost and not gained}\n",
        encoding="utf-8",
    )
    lines = [
        f"# Batch {batch} proof",
        "",
        f"- Plan rows: **{len(expected)}**; moves: **{len(batch_moves)}**; bytes: **{bytes_total:,}** (plan **{expected_bytes:,}**).",
        f"- Tracked moves shown as `R100`: **{r100}/{len(tracked_moves)}**.",
        f"- D4 ignored set: **{len(ignored_before)} -> {len(current_ignored)}**; lost **{len(lost)}**, gained **{len(gained)}**.",
        f"- Frozen check: **{json.dumps(frozen) if frozen else 'not applicable'}**.",
        f"- Unexpected staged paths: **{len(set(staged_paths) - allowed)}**; unstaged: **{len(unstaged)}**; untracked (outside log): **{len(untracked)}**.",
        "",
        f"**Verdict: {'PASS' if not errors else 'FAIL'}**",
        "",
    ]
    if errors:
        lines += ["## Errors", ""] + [f"- {e}" for e in errors]
    (logdir / f"batch_{batch}_proof.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"WROTE {logdir / f'batch_{batch}_proof.md'}")
    return 0 if not errors else 1


def _batch_of(row: dict[str, str]) -> str:
    cat = row["category"]
    if cat == "residue" or row["old_path"] == "README.md":
        return "R1"
    if cat == "version":
        return "R2"
    if cat == "evidence":
        return "R3"
    if cat in {"doc", "course_reference"}:
        return "R4"
    if cat == "data":
        return "R5"
    if cat == "handin":
        return "R6"
    if cat in {"pipeline_entry", "pipeline_metadata"}:
        return "R7"
    return "ROOT"


def _frozen_check(root: Path, logdir: Path, batch: str) -> dict[str, object]:
    # Use the already-tested scanner; it is read-only.
    out = logdir / f"frozen_{batch}.csv"
    proc = subprocess.run(
        [
            "python",
            str(logdir / "scripts" / "frozen_hashes.py"),
            "--root",
            str(root),
            "--out",
            str(out),
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return {"pass": False, "error": proc.stdout + proc.stderr}
    moves = list(csv.DictReader((logdir / "moves.csv").open(encoding="utf-8")))
    old_to_new = {m["old_path"]: m["new_path"] for m in moves}
    before = list(csv.DictReader((logdir / "frozen_before.csv").open(encoding="utf-8")))
    after = {r["path"]: r for r in csv.DictReader(out.open(encoding="utf-8"))}
    errors: list[str] = []
    checked = 0
    for b in before:
        mapped = old_to_new.get(b["path"], b["path"])
        a = after.get(mapped)
        if a is None:
            errors.append(f"{b['id']} missing after move: {b['path']} -> {mapped}")
            continue
        if a["sha256"] != b["sha256"]:
            errors.append(f"{b['id']} SHA changed: {mapped}")
            continue
        # The v1 manifest row has no expected hash in frozen_before.csv; its
        # SHA equality above is the check. The 67 snapshot rows must say PASS.
        if b["id"] == "F2" and a["match"] not in {"PASS", ""}:
            errors.append(f"F2 manifest check not PASS: {mapped}")
            continue
        checked += 1
    coverage = {}
    cov_path = out.with_name("frozen_coverage.json")
    if cov_path.is_file():
        coverage = json.loads(cov_path.read_text(encoding="utf-8"))
    if not coverage.get("pass"):
        errors.append("frozen_coverage.json pass is false")
    return {
        "pass": not errors,
        "checked": checked,
        "f2_manifest_entries": coverage.get("manifest_entries"),
        "errors": errors[:10],
    }


if __name__ == "__main__":
    raise SystemExit(main())
