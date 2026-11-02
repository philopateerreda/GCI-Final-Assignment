#!/usr/bin/env python
"""Build inventory, role map and the per-file move plan from one rule set.

Read-only. Re-runnable. Usage:
  python plan.py --root <finalA> --manifest <csv> --outdir <dir> [--dry-run]
Writes inventory.csv, role_map.csv, role_map.md, move_plan.csv and plan_summary.json.
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT_DOCS = {
    "README.md": ("archive/superseded/README_v2.md", "superseded_readme", "Replaced by the new package README", "low"),
    ".gitignore": (".gitignore", "git_config", "Git ignore rules; edited in place", "high"),
    ".gitattributes": (".gitattributes", "git_config", "Hash-bound evidence attributes; unchanged", "high"),
    "philopateer.ipynb": ("submission/philopateer.ipynb", "handin", "F1 graded notebook", "high"),
    "philopateer.pdf": ("submission/philopateer.pdf", "handin", "F1 graded PDF deck", "high"),
    "philopateer.pptx": ("submission/philopateer.pptx", "handin", "F1 editable deck", "high"),
    "README.docx": ("docs/reference/README.docx", "course_reference", "Course assignment brief (text extraction proves it), not authored work", "high"),
    "ENG_Company _A_ Dataset Overview.docx": ("docs/reference/ENG_Company _A_ Dataset Overview.docx", "course_reference", "Course-supplied dataset dictionary (text extraction proves it)", "high"),
    "tutorial (2).ipynb": ("docs/reference/tutorial (2).ipynb", "course_reference", "Course-supplied tutorial reference; stays ignored", "high"),
    "FINAL_ASSESSMENT_HANDOFF.md": ("docs/FINAL_ASSESSMENT_HANDOFF.md", "doc", "v2 technical handoff", "medium"),
    "FINAL_ASSESSMENT_READING_NOTE.md": ("docs/FINAL_ASSESSMENT_READING_NOTE.md", "doc", "short reading guide", "medium"),
    "FINAL_V2_UPGRADE_REPORT.md": ("docs/FINAL_V2_UPGRADE_REPORT.md", "doc", "v2 QA report", "medium"),
    "analysis_pipeline.py": ("pipeline/analysis_pipeline.py", "pipeline_entry", "Canonical v1+v2 pipeline; Tier C after move", "high"),
    "build_notebook.py": ("pipeline/build_notebook.py", "pipeline_entry", "Notebook builder; Tier A path edits", "high"),
    "export_and_verify.py": ("pipeline/export_and_verify.py", "pipeline_entry", "Deck/PDF export and delivery QA; Tier A path edits", "high"),
    "restore_v1.py": ("pipeline/restore_v1.py", "pipeline_entry", "v1 restore tool; Tier C after move", "high"),
    "requirements-python311.txt": ("pipeline/requirements-python311.txt", "pipeline_metadata", "Pinned Python 3.11 environment", "low"),
    "references.txt": ("pipeline/references.txt", "pipeline_metadata", "Verified bibliography and AI disclosure; also a submission companion", "high"),
}

GROUPS = {
    # root
    "R-F1": dict(match=lambda p: p in {"philopateer.ipynb", "philopateer.pdf", "philopateer.pptx"}, what="Three graded hand-in artifacts (notebook, PDF, PPTX)", produced="v2 canonical run and PowerPoint export", read="assessor; account holder", status="frozen current", evidence="frozen_before.csv F1; analysis_outputs/delivery_checks.json", dest="submission/"),
    "R-COURSE": dict(match=lambda p: p in {"README.docx", "ENG_Company _A_ Dataset Overview.docx"}, what="Two course-supplied Word documents: assignment brief and dataset dictionary", produced="GCI 2026 course", read="author and assessor", status="frozen supplied reference", evidence="extracted_text/README.docx.txt L1-L3, L98; ENG...docx.txt L1-L2; source_manifest.json", dest="docs/reference/"),
    "R-TUTORIAL": dict(match=lambda p: p == "tutorial (2).ipynb", what="Course-supplied tutorial notebook", produced="GCI 2026 course", read="author", status="frozen supplied reference; ignored", evidence="extracted_text/tutorial (2).ipynb.txt cell 1", dest="docs/reference/"),
    "R-DOCS": dict(match=lambda p: p.startswith("FINAL_"), what="Three v2-era explanatory documents", produced="v2 documentation work", read="successor / reviewer", status="current context", evidence="FINAL_ASSESSMENT_HANDOFF.md; README.md L132", dest="docs/"),
    "R-PIPE-C": dict(match=lambda p: p in {"analysis_pipeline.py", "build_notebook.py", "export_and_verify.py", "restore_v1.py"}, what="Four historical pipeline/build/restore entry points; every one needs more than a few path changes or a path-mapping layer", produced="v1/v2 pipeline", read="historical provenance; pre-reorg reruns", status="historical Tier C after move", evidence="analysis_pipeline.py L43-L95, L581, L4184-L4209; build_notebook.py L12-L132; export_and_verify.py L13-L53; restore_v1.py L10-L91", dest="pipeline/"),
    "R-META": dict(match=lambda p: p in {"requirements-python311.txt", "references.txt"}, what="Environment pins and the verified reference/disclosure register", produced="v2 documentation", read="reviewer; pipeline", status="current", evidence="requirements-python311.txt; FINAL_ASSESSMENT_HANDOFF.md Â§13", dest="pipeline/"),
    "R-GIT": dict(match=lambda p: p in {".gitignore", ".gitattributes"}, what="Root git ignore/attribute controls", produced="repository setup", read="git", status="current; .gitignore edited", evidence="git_state.md", dest="keep at root"),
    "R-README": dict(match=lambda p: p == "README.md", what="Old package README, superseded by the new one", produced="v4 release", read="historical", status="superseded", evidence="README.md L1-L155; VERSIONS.md", dest="archive/superseded/"),
    "D-TELECOM": dict(match=lambda p: p.startswith("telecom/"), what="Two supplied applicant-level CSVs (100,000 customers each)", produced="Company A / course", read="canonical pipeline only", status="frozen supplied data; local-only, ignored", evidence="analysis_outputs/audit.json; .gitignore L16", dest="data/telecom/"),
    # evidence
    "E-CORE": dict(match=lambda p: p.startswith("analysis_outputs/") and p.count("/") == 1, what="Evidence receipts: audit, delivery checks, claims ledger, feature manifest, model selection, pilot design, environment, summary, contact sheet", produced="canonical v1/v2 pipeline", read="README; assessor; v3/v4 audits", status="current frozen evidence", evidence="analysis_outputs/audit.json; delivery_checks.json; claims_ledger_build.json", dest="evidence/"),
    "E-CHARTS": dict(match=lambda p: p.startswith("analysis_outputs/charts/"), what="Nine evidence charts", produced="analysis_pipeline.py figure()", read="deck; evidence review", status="current", evidence="analysis_outputs/delivery_checks.json chart checks", dest="evidence/charts/"),
    "E-MODELS": dict(match=lambda p: p.startswith("analysis_outputs/models/"), what="Selected calibrated model bundle", produced="analysis_pipeline.py", read="replay/audit", status="frozen current", evidence="model_selection.json; delivery_checks.json", dest="evidence/models/"),
    "E-BACKUPS": dict(match=lambda p: p.startswith("analysis_outputs/notebook_backups/"), what="Notebook execution backups from the v2 build", produced="build_notebook.py", read="historical audit only", status="historical; ignored", evidence=".gitignore L28-L29; build_notebook.py L129-L132", dest="evidence/notebook_backups/"),
    "E-RENDERS": dict(match=lambda p: p.startswith("analysis_outputs/slide_renders/"), what="Fifteen reviewed deck renders", produced="export_and_verify.py", read="visual receipt", status="current frozen render evidence", evidence="delivery_checks.json render_sha256", dest="evidence/slide_renders/"),
    "E-TABLES": dict(match=lambda p: p.startswith("analysis_outputs/tables/"), what="Fourteen evidence tables and held-out predictions", produced="analysis_pipeline.py", read="README; v3 audits", status="current frozen evidence", evidence="delivery_checks.json; claims_ledger_build.json", dest="evidence/tables/"),
    # versions
    "V1-FROZEN": dict(match=lambda p: p.startswith("v1_frozen/"), what="Immutable 67-file v1 snapshot plus its SHA256 manifest", produced="v1 freeze step", read="restore/audit; F2 verifier", status="frozen; ignored", evidence="v1_frozen/sha256_manifest.json; frozen_coverage.json", dest="versions/v1_frozen/"),
    "V2-DOCS": dict(match=lambda p: p.startswith("v2_work/") and p.count("/") == 1 and p.endswith(".md"), what="Eight v2 workstream and checkpoint documents", produced="v2 run", read="successor; README", status="current v2 record", evidence="v2_work/checkpoint2_summary.md; step0_report.md", dest="versions/v2_work/"),
    "V2-CODE": dict(match=lambda p: p.startswith("v2_work/") and p.count("/") == 1 and p.endswith(".py"), what="Twenty-seven v2 scripts, including the embedded-module source and audits", produced="v2 run", read="historical provenance", status="historical Tier C", evidence="v2_work/step0_report.md; v2_work/analysis_pipeline_v2.py", dest="versions/v2_work/"),
    "V2-LITERATURE": dict(match=lambda p: p.startswith("v2_work/literature_"), what="Nine third-party literature files (seven PDFs, two PNGs), copyright-restricted", produced="research", read="citation checks", status="reference; ignored", evidence=".gitignore L20-L22", dest="versions/v2_work/"),
    "V2-LOGS": dict(match=lambda p: p.startswith("v2_work/") and p.count("/") == 1 and p.endswith(".log"), what="Eight local run logs", produced="v2 run", read="historical debugging", status="historical; ignored", evidence=".gitignore L59", dest="versions/v2_work/"),
    "V2-CORE": dict(match=lambda p: p.startswith("v2_work/") and p.count("/") == 1, what="Remaining v2 root outputs: summaries, specs, gates, chart data, provenance", produced="v2 run", read="v3/v4 audits; README", status="current v2 record", evidence="v2_work/final_metrics.json; final_batch_completion.json; checkpoint2_summary.md", dest="versions/v2_work/"),
    "V2-CHARTS": dict(match=lambda p: p.startswith("v2_work/charts/"), what="Three v2 source charts copied into the deck evidence", produced="v2 generate_visuals.py", read="evidence; deck", status="current", evidence="analysis_outputs/delivery_checks.json", dest="versions/v2_work/charts/"),
    "V2-C-CAL": dict(match=lambda p: p.startswith("v2_work/c_calibration/"), what="Workstream C calibration-partition audit tables", produced="v2 workstream_c.py", read="v2 governance", status="current v2 evidence", evidence="v2_work/c_governance.md; c_summary.json", dest="versions/v2_work/c_calibration/"),
    "V2-C-TEST": dict(match=lambda p: p.startswith("v2_work/c_test/"), what="Workstream C test-partition audit tables", produced="v2 workstream_c.py", read="v2 governance", status="current v2 evidence", evidence="v2_work/c_governance.md; v2_work/test_audit_started.json", dest="versions/v2_work/c_test/"),
    "V2-C-SMOKE": dict(match=lambda p: p.startswith("v2_work/c_smoke/"), what="Smoke fixture for Workstream C (smoke=True)", produced="v2 workstream_c.py --smoke", read="historical debugging", status="scratch/residue", evidence="v2_work/c_smoke/c_governance.md line 1", dest="archive/residue/v2_work/c_smoke/"),
    "V2-D-ROOT": dict(match=lambda p: p.startswith("v2_work/d_results/") and p.count("/") == 2, what="Workstream D root results: gate, folds, ablations, learning curves, manifests", produced="v2 workstream_d.py", read="v3/v4 audits; README", status="current v2 evidence", evidence="v2_work/d_results/gate_d.csv; run_spec.json; final_metrics.json", dest="versions/v2_work/d_results/"),
    "V2-D-CACHE": dict(match=lambda p: p.startswith("v2_work/d_results/cache/"), what="1,392 hash-named prediction caches supporting Workstream D provenance", produced="v2 workstream_d.py", read="provenance only", status="regenerable, evidence-bound; ignored", evidence="v3_addons/results/wp8/bootstrap.json input list; .gitignore L31-L35", dest="versions/v2_work/d_results/cache/"),
    "V2-D-FOLDS": dict(match=lambda p: p.startswith("v2_work/d_results/folds/"), what="290 fold recipes and fold scores", produced="v2 workstream_d.py", read="paired comparison audit", status="current v2 evidence", evidence="v2_work/d_results/paired_fold_differences.csv", dest="versions/v2_work/d_results/folds/"),
    "V2-D-OOF": dict(match=lambda p: p.startswith("v2_work/d_results/oof/"), what="130 out-of-fold prediction arrays, hash-bound by v3 reports", produced="v2 workstream_d.py", read="v3 WP1/WP3/WP5 provenance", status="current v2 evidence; ignored", evidence="v3_addons/reports/WP3_report.md L12-L21; .gitignore L32", dest="versions/v2_work/d_results/oof/"),
    "V2-D-SMOKE": dict(match=lambda p: p.startswith("v2_work/d_smoke/"), what="Workstream D smoke-run outputs", produced="v2 workstream_d.py --smoke", read="historical debugging", status="scratch/residue", evidence=".gitignore L36; v2_work/d_smoke/progress.json", dest="archive/residue/v2_work/d_smoke/"),
    "V2-D-SMOKE-IO": dict(match=lambda p: p.startswith("v2_work/d_smoke_io/"), what="Workstream D I/O smoke outputs", produced="v2 workstream_d.py smoke I/O", read="historical debugging", status="scratch/residue", evidence=".gitignore L37; v2_work/d_smoke_io/cv_manifest.json", dest="archive/residue/v2_work/d_smoke_io/"),
    "V2-PYCACHE": dict(match=lambda p: p.startswith("v2_work/__pycache__/"), what="Twenty-one Python bytecode caches", produced="Python imports during v2 runs", read="none", status="residue", evidence=".gitignore L2-L3", dest="archive/residue/v2_work/__pycache__/"),
    "V3-DOCS": dict(match=lambda p: p.startswith("v3_addons/") and p.count("/") == 1, what="v3 handback, integration proposal, WP8 preregistration, protocol addendum, AGENTS", produced="v3 audit WP7/WP8", read="v4; README", status="current v3 record", evidence="v3_addons/HANDBACK.md; wp8_verification.json", dest="versions/v3_addons/"),
    "V3-REPORTS": dict(match=lambda p: p.startswith("v3_addons/reports/"), what="WP0-WP8 reports and pre-v4 backups", produced="v3 audit", read="v4; reviewer", status="current v3 record", evidence="v3_addons/reports/WP8_report.md; v4_addons/STATE.md", dest="versions/v3_addons/reports/"),
    "V3-FIGURES": dict(match=lambda p: p.startswith("v3_addons/figures/"), what="Five WP figure drafts", produced="v3 WP1-WP5", read="reports", status="current supporting", evidence="v3_addons/REPRODUCIBILITY.md", dest="versions/v3_addons/figures/"),
    "V3-SRC": dict(match=lambda p: p.startswith("v3_addons/src/"), what="Fourteen WP source scripts plus one validation-only PNG", produced="v3 audit", read="reproduction", status="historical Tier C", evidence="v3_addons/REPRODUCIBILITY.md", dest="versions/v3_addons/src/"),
    "V3-TESTS": dict(match=lambda p: p.startswith("v3_addons/tests/"), what="Five new-code test modules and two fixtures", produced="v3 audit", read="audit verification", status="historical Tier C", evidence="v3_addons/results/wp8_tests.json", dest="versions/v3_addons/tests/"),
    "V3-RESULTS": dict(match=lambda p: p.startswith("v3_addons/results/") and not p.endswith((".npz", ".started", ".lock")) and "/wp8/models/" not in p and "/sources/" not in p and "/cache/" not in p, what="v3 result JSON/CSV/PDF/TXT evidence and provenance", produced="v3 WP0-WP8", read="v4 audits; README", status="current v3 evidence", evidence="v3_addons/results/wp8_verification.json; final_new_code_tests.json", dest="versions/v3_addons/results/"),
    "V3-WP8-CACHE": dict(match=lambda p: p.startswith("v3_addons/results/wp8/cache/") and not p.endswith(".started"), what="WP8 per-fold prediction caches and signature JSON", produced="v3 WP8", read="WP8 result/provenance JSON", status="evidence-bound; ignored", evidence="v3_addons/results/wp8/r0_f0.json L19-L49; .gitignore L42-L44", dest="versions/v3_addons/results/wp8/cache/"),
    "V3-WP8-MODELS": dict(match=lambda p: p.startswith("v3_addons/results/wp8/models/"), what="Ten WP8 outer-fold model text dumps", produced="v3 WP8", read="WP8 provenance", status="evidence-bound; ignored", evidence=".gitignore L44; wp8_model.json", dest="versions/v3_addons/results/wp8/models/"),
    "V3-SOURCES": dict(match=lambda p: p.startswith("v3_addons/results/sources/"), what="Six third-party source PDFs", produced="v3 WP6", read="citation verification", status="reference; ignored", evidence=".gitignore L23", dest="versions/v3_addons/results/sources/"),
    "V3-NPZ": dict(match=lambda p: p.startswith("v3_addons/results/") and p.endswith(".npz"), what="Thirty-eight NPZ arrays outside `wp8/cache`; with the 60 cache arrays this is the full 98", produced="v3 audit", read="reports; reproducibility", status="current evidence; ignored", evidence=".gitignore L42-L44; REPRODUCIBILITY.md hashes", dest="versions/v3_addons/results/"),
    "V3-STARTED": dict(match=lambda p: p.endswith(".started"), what="Sixty execution-start markers", produced="v3 WP8 batch runner", read="none", status="run residue", evidence=".gitignore not required; H8", dest="archive/residue/v3_addons/results/wp8/cache/"),
    "V3-LOCK": dict(match=lambda p: p.endswith(".lock"), what="One stale batch lock", produced="v3 WP8 batch runner", read="none", status="run residue", evidence="H8", dest="archive/residue/v3_addons/results/"),
    "V4-DOCS": dict(match=lambda p: p.startswith("v4_addons/") and p.count("/") == 1 and p.endswith(".md"), what="Fifteen v4 closeout, yardstick, reproducibility, CEO and disclosure documents", produced="v4 release", read="README index; CEO", status="current v4 record", evidence="v4_addons/STATE.md; RELEASE_RECEIPT.md", dest="versions/v4_addons/"),
    "V4-MANIFEST": dict(match=lambda p: p == "v4_addons/MANIFEST_v4.json", what="v4 hash/inventory manifest", produced="v4 D1", read="release audit", status="current v4 record", evidence="v4_addons/STATE.md D1", dest="versions/v4_addons/"),
    "V4-GATES": dict(match=lambda p: p.startswith("v4_addons/gates/"), what="Two human-gate records", produced="v4 F0", read="release audit", status="current v4 record", evidence="v4_addons/STATE.md authorization record", dest="versions/v4_addons/gates/"),
    "V4-LEDGER": dict(match=lambda p: p.startswith("v4_addons/ledger_dryrun/"), what="Six alternative claims-ledger dry-runs", produced="v4 D3", read="integration decision", status="current v4 evidence", evidence="v4_addons/reports/D3_report.md", dest="versions/v4_addons/ledger_dryrun/"),
    "V4-M0": dict(match=lambda p: p.startswith("v4_addons/m0_sandbox/"), what="Track M feasibility replay sandbox", produced="v4 M0", read="M1 decision", status="current v4 evidence", evidence="v4_addons/reports/M0_report.md", dest="versions/v4_addons/m0_sandbox/"),
    "V4-M1": dict(match=lambda p: p.startswith("v4_addons/m1_work/") and "/cache/" not in p, what="Track M learning-curve results and progress", produced="v4 M1", read="M1 report", status="current v4 evidence", evidence="v4_addons/reports/M1_report.md", dest="versions/v4_addons/m1_work/"),
    "V4-M1-CACHE": dict(match=lambda p: p.startswith("v4_addons/m1_work/cache/"), what="Two hundred killed Track M fit caches", produced="v4 M1", read="none after track kill", status="run residue", evidence="v4_addons/STATE.md M1; .gitignore L74", dest="archive/residue/v4_addons/m1_work/cache/"),
    "V4-RELEASE": dict(match=lambda p: p.startswith("v4_addons/release_candidate/"), what="Six read-only release copies verified by receipt", produced="v4 F7", read="CEO hand-off", status="evidence-bound copies; ignored", evidence="v4_addons/RELEASE_RECEIPT.md L9-L18; .gitignore L66", dest="versions/v4_addons/release_candidate/"),
    "V4-REPORTS": dict(match=lambda p: p.startswith("v4_addons/reports/"), what="Twenty-four v4 card reports", produced="v4 release", read="STATE; reviewer", status="current v4 record", evidence="v4_addons/STATE.md", dest="versions/v4_addons/reports/"),
    "V4-RESULTS": dict(match=lambda p: p.startswith("v4_addons/results/"), what="Sixty-eight v4 audit, ledger and render-check results", produced="v4 tools", read="reports", status="current v4 evidence", evidence="v4_addons/reports/D0-D8", dest="versions/v4_addons/results/"),
    "V4-SNAPSHOTS": dict(match=lambda p: p.startswith("v4_addons/snapshots/"), what="Allowed-changes policy and baseline snapshot", produced="v4 preflight", read="v4 tools", status="evidence-bound; ignored", evidence="v4_addons/STATE.md D0", dest="versions/v4_addons/snapshots/"),
    "V4-TOOLS": dict(match=lambda p: p.startswith("v4_addons/tools/"), what="Thirty-nine v4 audit/reporting tools", produced="v4 release", read="reproduction", status="historical Tier C", evidence="v4_addons/REPRODUCIBILITY.md", dest="versions/v4_addons/tools/"),
    "R-PYCACHE": dict(match=lambda p: p.startswith("__pycache__/"), what="Root Python bytecode cache", produced="Python import", read="none", status="residue", evidence=".gitignore L2-L3", dest="archive/residue/__pycache__/"),
}


def git_set(root: Path, *args: str) -> set[str]:
    out = subprocess.check_output(["git", "-C", str(root), *args], text=False)
    return {p.decode("utf-8", "surrogateescape") for p in out.split(b"\0") if p}


def destination_for(path: str) -> tuple[str, str, str, str]:
    if path in ROOT_DOCS:
        return ROOT_DOCS[path]
    if path.startswith("analysis_outputs/"):
        return ("evidence/" + path[len("analysis_outputs/"):], "evidence", "analysis_outputs renamed in place", "medium")
    if path.startswith("v1_frozen/"):
        return ("versions/" + path, "version", "v1 snapshot moves as a unit", "high")
    for top in ("v2_work/", "v3_addons/", "v4_addons/"):
        if path.startswith(top):
            residue = (
                path.startswith("v2_work/c_smoke/")
                or path.startswith("v2_work/d_smoke/")
                or path.startswith("v2_work/d_smoke_io/")
                or path.startswith("v2_work/__pycache__/")
                or path.endswith(".started")
                or path.endswith(".lock")
                or path.startswith("v4_addons/m1_work/cache/")
            )
            if residue:
                return ("archive/residue/" + path, "residue", "run residue lifted out of the version", "low")
            return ("versions/" + path, "version", "version folder moves as a unit", "high" if top != "v2_work/" else "medium")
    if path.startswith("__pycache__/"):
        return ("archive/residue/" + path, "residue", "Python bytecode cache", "low")
    if path.startswith("telecom/"):
        return ("data/" + path, "data", "supplied dataset moves under data; stays ignored", "high")
    raise KeyError(path)


def group_for(path: str) -> str:
    for gid, meta in GROUPS.items():
        if meta["match"](path):
            return gid
    raise KeyError(path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--manifest", required=True, type=Path)
    ap.add_argument("--outdir", required=True, type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()
    tracked = git_set(root, "ls-files", "-z")
    ignored = git_set(root, "ls-files", "-z", "--others", "--ignored", "--exclude-standard")
    manifest = list(csv.DictReader(args.manifest.open(encoding="utf-8")))
    inv, role, plan = [], [], []
    seen_dest: dict[str, str] = {}
    group_stats = defaultdict(lambda: {"files": 0, "bytes": 0})
    for row in manifest:
        p = row["path"]
        gid = group_for(p)
        dest, category, reason, risk = destination_for(p)
        if dest in seen_dest:
            raise SystemExit(f"DEST COLLISION: {dest} <- {p} and {seen_dest[dest]}")
        seen_dest[dest] = p
        is_tracked = p in tracked
        is_ignored = p in ignored
        tier = ""
        if p in {"analysis_pipeline.py", "build_notebook.py", "export_and_verify.py", "restore_v1.py"} or (
            p.startswith(("v1_frozen/", "v2_work/", "v3_addons/", "v4_addons/")) and p.endswith(".py")
        ):
            tier = "C"
        needs_ignore = is_ignored and category != "git_config"
        inv.append(
            {
                "path": p,
                "extension": Path(p).suffix.lower() or "(none)",
                "bytes": row["size_bytes"],
                "sha256": row["sha256"],
                "tracked": "yes" if is_tracked else "no",
                "ignored": "yes" if is_ignored else "no",
                "mtime": row["mtime_utc"],
                "group_id": gid,
            }
        )
        role.append({"group_id": gid, "path": p, "bytes": row["size_bytes"]})
        plan.append(
            {
                "old_path": p,
                "new_path": dest,
                "category": category,
                "reason": reason,
                "risk": risk,
                "tier": tier,
                "tracked": "yes" if is_tracked else "no",
                "ignored_before": "yes" if is_ignored else "no",
                "ignored_after_expected": "yes" if is_ignored else "no",
                "needs_gitignore_edit": "yes" if needs_ignore else "no",
                "needs_gitattributes_edit": "no",
            }
        )
        group_stats[gid]["files"] += 1
        group_stats[gid]["bytes"] += int(row["size_bytes"])
    print(f"FILES={len(plan)} DESTINATIONS={len(seen_dest)} GROUPS={len(group_stats)}")
    print(f"TRACKED={sum(1 for r in plan if r['tracked']=='yes')} IGNORED={sum(1 for r in plan if r['ignored_before']=='yes')}")
    counts = Counter(r["category"] for r in plan)
    print(f"CATEGORIES={dict(counts)}")
    long_paths = [r for r in plan if len(str(args.outdir.parent)) + 1 + len(r["new_path"]) > 240]
    print(f"NEW_PATHS_OVER_240_CHARS={len(long_paths)}")
    if args.dry_run:
        print("DRY-RUN: no files written")
        return 0
    args.outdir.mkdir(parents=True, exist_ok=True)
    with (args.outdir / "inventory.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(inv[0].keys()))
        w.writeheader()
        w.writerows(inv)
    with (args.outdir / "role_map.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(role[0].keys()))
        w.writeheader()
        w.writerows(role)
    with (args.outdir / "move_plan.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(plan[0].keys()))
        w.writeheader()
        w.writerows(plan)
    lines = [
        "# Role map â€” every working-tree file, grouped",
        "",
        f"**{len(plan)} files / {sum(int(r['bytes']) for r in inv):,} bytes** in **{len(group_stats)} groups**. "
        "Every file has exactly one group and one `move_plan.csv` row (D1).",
        "",
        "Status vocabulary: `frozen`, `current`, `historical`, `superseded`, `scratch/residue`, `unclear_status`.",
        "",
        "| Group | Files | Bytes | What it is | Produced by | Read by | Status | Evidence | Destination |",
        "|---|---:|---:|---|---|---|---|---|---|",
    ]
    for gid in GROUPS:
        if gid not in group_stats:
            continue
        meta = GROUPS[gid]
        lines.append(
            f"| `{gid}` | {group_stats[gid]['files']} | {group_stats[gid]['bytes']:,} | {meta['what']} | "
            f"{meta['produced']} | {meta['read']} | {meta['status']} | {meta['evidence']} | `{meta['dest']}` |"
        )
    lines += [
        "",
        "## Individually named files that matter",
        "",
        "| Path | Group | One-line answer |",
        "|---|---|---|",
        "| `analysis_outputs/audit.json` | E-CORE | 100,000 Ã— 100 merged rows, 49.562% sample churn, one-to-one ID join, source hashes. |",
        "| `analysis_outputs/delivery_checks.json` | E-CORE | Delivery receipt: 15 PDF pages, 15 slides, 25 executed code cells, 0 errors, 278 claim rows, 0 geometry issues. |",
        "| `analysis_outputs/claims_ledger_build.json` | E-CORE | Build receipt for the 278-row claim ledger and its source files. |",
        "| `analysis_outputs/feature_manifest.json` | E-CORE | Exact 87-feature list, 4 categorical, 26 excluded fields. |",
        "| `analysis_outputs/summary.json` | E-CORE | Consolidated v1/v2 metrics and the `v2_enhancement` block. |",
        "| `v1_frozen/sha256_manifest.json` | V1-FROZEN | 67 root-relative entries; path base is `v1_frozen/`; all 67 PASS. |",
        "| `v2_work/final_metrics.json` | V2-CORE | Consolidated frozen v2 numbers and protocol fingerprints (155,122 bytes). |",
        "| `v2_work/d_results/gate_d.csv` | V2-D-ROOT | Eleven eligible challengers; none promoted. |",
        "| `v3_addons/HANDBACK.md` | V3-DOCS | v3 terminal status; WP8 rejected, integration not applied. |",
        "| `v3_addons/results/wp8_verification.json` | V3-RESULTS | WP8 promotion/gate/verification record and outside snapshot. |",
        "| `v4_addons/STATE.md` | V4-DOCS | v4 release state `RELEASED_FALLBACK_A_v4.0.0` and authorization record. |",
        "| `v4_addons/RELEASE_RECEIPT.md` | V4-DOCS | Six release copies, four frozen-v2 hashes equal, no upload. |",
        "| `v4_addons/YARDSTICK.md` | V4-DOCS | One sheet reconciling 7,872 / 40,000 / 80,000 sample sizes and profit definitions. |",
        "",
        "## Grouping method",
        "",
        "Groups are path + schema signatures, not one group per file. The 2,414 JSON and 1,928 NPZ",
        "files are machine outputs and were classified by directory role and schema; they were never",
        "printed. Per-file membership is in `role_map.csv`; hashes and flags are in `inventory.csv`.",
        "",
    ]
    (args.outdir / "role_map.md").write_text("\n".join(lines), encoding="utf-8")
    summary = {
        "files": len(plan),
        "bytes": sum(int(r["bytes"]) for r in inv),
        "groups": len(group_stats),
        "categories": dict(counts),
        "tracked": sum(1 for r in plan if r["tracked"] == "yes"),
        "ignored": sum(1 for r in plan if r["ignored_before"] == "yes"),
        "new_paths_over_240_chars": len(long_paths),
        "group_stats": dict(group_stats),
    }
    (args.outdir / "plan_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"WROTE {args.outdir / 'inventory.csv'}")
    print(f"WROTE {args.outdir / 'role_map.csv'} {args.outdir / 'role_map.md'}")
    print(f"WROTE {args.outdir / 'move_plan.csv'} {args.outdir / 'plan_summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

