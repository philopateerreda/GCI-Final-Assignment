#!/usr/bin/env python
"""Read-only text extraction for Office/PDF/notebook artifacts.

Writes only plain-text companions under the requested output directory. Never
re-saves or modifies the source. Usage:
  python extract_text.py --root <finalA> --out <dir> --path <rel> [--path ...] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def extract_docx(src: Path, dst: Path) -> int:
    from docx import Document

    doc = Document(str(src))
    lines = []
    for p in doc.paragraphs:
        lines.append(p.text)
    for ti, table in enumerate(doc.tables, 1):
        lines.append(f"\n[TABLE {ti}]")
        for row in table.rows:
            lines.append(" | ".join(cell.text.replace("\n", " ") for cell in row.cells))
    dst.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(lines)


def extract_pdf(src: Path, dst: Path) -> int:
    import fitz  # pymupdf

    doc = fitz.open(str(src))
    lines = []
    for i, page in enumerate(doc, 1):
        lines.append(f"\n===== PAGE {i} =====")
        lines.append(page.get_text())
    dst.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(doc)


def extract_pptx(src: Path, dst: Path) -> int:
    from pptx import Presentation

    prs = Presentation(str(src))
    lines = []
    for i, slide in enumerate(prs.slides, 1):
        lines.append(f"\n===== SLIDE {i} =====")
        for shape in slide.shapes:
            if getattr(shape, "has_text_frame", False):
                lines.append(shape.text)
            if getattr(shape, "has_table", False):
                for row in shape.table.rows:
                    lines.append(" | ".join(cell.text.replace("\n", " ") for cell in row.cells))
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame:
            notes = slide.notes_slide.notes_text_frame.text.strip()
            if notes:
                lines.append(f"[NOTES] {notes}")
    dst.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(prs.slides)


def extract_ipynb(src: Path, dst: Path) -> int:
    nb = json.loads(src.read_text(encoding="utf-8"))
    lines = []
    for i, cell in enumerate(nb.get("cells", []), 1):
        lines.append(f"\n===== CELL {i} ({cell.get('cell_type')}) =====")
        source = cell.get("source", "")
        lines.append("".join(source) if isinstance(source, list) else str(source))
    dst.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(nb.get("cells", []))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--path", action="append", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()
    handlers = {
        ".docx": (extract_docx, "docx"),
        ".pdf": (extract_pdf, "pdf"),
        ".pptx": (extract_pptx, "pptx"),
        ".ipynb": (extract_ipynb, "ipynb"),
    }
    for rel in args.path:
        src = root / rel
        if not src.is_file():
            print(f"MISSING {rel}", file=sys.stderr)
            return 2
        suffix = src.suffix.lower()
        if suffix not in handlers:
            print(f"UNSUPPORTED {rel}", file=sys.stderr)
            return 2
        handler, tag = handlers[suffix]
        dst = args.out / f"{src.stem}.{tag}.txt"
        print(f"{tag}: {rel} -> {dst.name}")
        if args.dry_run:
            continue
        args.out.mkdir(parents=True, exist_ok=True)
        count = handler(src, dst)
        print(f"  units={count} bytes={dst.stat().st_size}")
    if args.dry_run:
        print("DRY-RUN: no text written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
