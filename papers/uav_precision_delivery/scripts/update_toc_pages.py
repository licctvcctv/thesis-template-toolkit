from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"


def compact(text: str) -> str:
    return re.sub(r"\s+", "", text)


def load_json(name: str):
    return json.loads((CONTENT / name).read_text(encoding="utf-8"))


def collect_entries(chapters):
    entries = []

    def visit(node, level):
        entries.append(f"{node['number']} {node['title']}")
        for child in node.get("sections", []):
            visit(child, level + 1)

    for chapter in chapters:
        visit(chapter, 1)
    entries.extend(["参考文献", "致谢"])
    return entries


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python scripts/update_toc_pages.py render_check/<file>.pdf")
    pdf = Path(sys.argv[1])
    if not pdf.exists():
        raise FileNotFoundError(pdf)

    chapters = load_json("chapters.json")
    entries = collect_entries(chapters)
    reader = PdfReader(str(pdf))
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(compact(text))

    body_start = None
    first_heading = compact("第一章 绪论")
    for idx, text in enumerate(pages):
        if first_heading in text and "目录" not in text:
            body_start = idx
            break
    if body_start is None:
        raise RuntimeError("未能在渲染 PDF 中定位第一章正文页")

    page_map = {}
    for entry in entries:
        key = compact(entry)
        for idx in range(body_start, len(pages)):
            if key in pages[idx]:
                page_map[entry] = idx - body_start + 1
                break

    (CONTENT / "toc_pages.json").write_text(
        json.dumps(page_map, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(CONTENT / "toc_pages.json")


if __name__ == "__main__":
    main()
