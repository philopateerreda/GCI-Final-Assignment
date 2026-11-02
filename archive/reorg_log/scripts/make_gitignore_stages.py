#!/usr/bin/env python
"""Generate the exact .gitignore state after each R-batch and prove the final text.

Read-only apart from the log folder. Usage:
  python make_gitignore_stages.py --root <finalA> --outdir <dir> [--dry-run]
"""
from __future__ import annotations

import argparse
from pathlib import Path


def replace(text: str, old: str, new: str) -> str:
    if old not in text:
        raise SystemExit(f"pattern not found: {old!r}")
    return text.replace(old, new, 1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--outdir", required=True, type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()
    current = (root / ".gitignore").read_text(encoding="utf-8")
    stages = {}
    # R1: residue and duplicate directories; retire old smoke anchors.
    s = current
    for line in (
        "v2_work/d_smoke/\n",
        "v2_work/d_smoke_io/\n",
        "v2_work/c_smoke/\n",
        "v4_addons/m1_work/cache/\n",
    ):
        s = s.replace(line, "")
    s = s.rstrip("\n") + (
        "\n\n# Reorganization archive (git-ignored by design)\n"
        "/archive/residue/\n"
        "/archive/duplicates/\n"
        "/archive/reorg_log/extracted_text/\n"
        "/archive/reorg_log/verify_clone/\n"
    )
    stages["R1"] = s
    # R2: all version anchors.
    s = stages["R1"]
    s = replace(s, "/v1_frozen/\n", "/versions/v1_frozen/\n")
    s = replace(s, "v2_work/literature_*.pdf", "/versions/v2_work/literature_*.pdf")
    s = replace(s, "v2_work/literature_*.png", "/versions/v2_work/literature_*.png")
    s = replace(s, "v3_addons/results/sources/", "/versions/v3_addons/results/sources/")
    s = replace(s, "v3_addons/results/*.npz", "/versions/v3_addons/results/*.npz")
    s = replace(s, "v3_addons/results/wp5_calibration_oof.csv", "/versions/v3_addons/results/wp5_calibration_oof.csv")
    s = replace(s, "v3_addons/results/wp5_label_shift_raw.csv", "/versions/v3_addons/results/wp5_label_shift_raw.csv")
    s = replace(s, "v3_addons/results/wp8/*.npz", "/versions/v3_addons/results/wp8/*.npz")
    s = replace(s, "v3_addons/results/wp8/**/*.npz", "/versions/v3_addons/results/wp8/**/*.npz")
    s = replace(s, "v3_addons/results/wp8/models/", "/versions/v3_addons/results/wp8/models/")
    s = replace(s, "v3_addons/results/wp8/cache/", "/versions/v3_addons/results/wp8/cache/")
    for name in (
        "v2_work/d_results/cache/",
        "v2_work/d_results/oof/",
        "v2_work/d_results/cv_manifest.csv",
        "v2_work/d_results/cv_manifest.json",
        "v2_work/a_selected_test.csv",
        "v2_work/a_selected_calibration.csv",
        "v2_work/a_bootstrap_test.csv",
        "v2_work/a_bootstrap_calibration.csv",
        "v2_work/b_assignments_test.csv",
        "v2_work/b_assignments_calibration.csv",
        "v2_work/c_subgroup_robustness.csv",
    ):
        s = replace(s, name, "/versions/" + name)
    for name in (
        "v4_addons/CEO_BRIEF*",
        "v4_addons/CEO_QA*",
        "v4_addons/HUMAN_CHECKLIST.md",
        "v4_addons/DISCLOSURE_CHECK.md",
        "v4_addons/release_candidate/",
        "v4_addons/snapshots/",
        "v4_addons/m1_work/folds/",
        "v4_addons/m1_work/oof/",
    ):
        s = replace(s, name, "/versions/" + name)
    stages["R2"] = s
    # R3: evidence notebook backups.
    s = replace(stages["R2"], "analysis_outputs/notebook_backups/", "/evidence/notebook_backups/")
    stages["R3"] = s
    # R4: docs references.
    s = replace(stages["R3"], "/*.docx", "/docs/reference/*.docx")
    s = replace(s, "/tutorial*.ipynb", "/docs/reference/tutorial*.ipynb")
    stages["R4"] = s
    # R5: telecom data.
    s = replace(stages["R4"], "/telecom/*.csv", "/data/telecom/*.csv")
    stages["R5"] = s
    target = (args.outdir / "gitignore_after.txt").read_text(encoding="utf-8")
    if s.strip() != target.strip():
        print("STAGE R5 DOES NOT EQUAL PROPOSED FILE")
        print("--- R5 ---")
        print(s)
        print("--- target ---")
        print(target)
        return 1
    print("STAGES R1-R5 VALID; R5 == gitignore_after.txt")
    if args.dry_run:
        print("DRY-RUN: no stage files written")
        return 0
    for name, text in stages.items():
        (args.outdir / f"gitignore_{name}.txt").write_text(text, encoding="utf-8")
        print(f"WROTE {args.outdir / f'gitignore_{name}.txt'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
