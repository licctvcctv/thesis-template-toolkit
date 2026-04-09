"""
论文生成主入口。
用法: python3 generate.py
"""
import os
from docxtpl import DocxTemplate

from config import (
    COVER, ABSTRACT_ZH, KEYWORDS_ZH,
    ABSTRACT_EN, KEYWORDS_EN, ACKNOWLEDGEMENT,
)
from chapters import CHAPTERS
from references import REFERENCES
from builder import build_chapters, build_references

TEMPLATE = os.path.join(os.path.dirname(__file__), "thesis_template.docx")
OUTPUT = os.path.join(os.path.dirname(__file__), "output_thesis.docx")


def main():
    try:
        doc = DocxTemplate(TEMPLATE)
    except FileNotFoundError:
        raise SystemExit(f"找不到模板文件: {TEMPLATE}")

    chapters_sd = build_chapters(doc, CHAPTERS)
    refs_sd = build_references(doc, REFERENCES)

    context = {
        **COVER,
        "abstract_zh": ABSTRACT_ZH,
        "keywords_zh": KEYWORDS_ZH,
        "abstract_en": ABSTRACT_EN,
        "keywords_en": KEYWORDS_EN,
        "acknowledgement": ACKNOWLEDGEMENT,
        "chapters_subdoc": chapters_sd,
        "refs_subdoc": refs_sd,
    }

    doc.render(context)
    doc.save(OUTPUT)
    print(f"论文已生成: {OUTPUT}")


if __name__ == "__main__":
    main()
