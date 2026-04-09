"""
论文生成主入口。
用法: python3 generate.py

生成结果: output_thesis.docx
"""
import os
import sys
from docxtpl import DocxTemplate

from config import (
    COVER, ABSTRACT_ZH, KEYWORDS_ZH,
    ABSTRACT_EN, KEYWORDS_EN, ACKNOWLEDGEMENT,
)
from chapters import CHAPTERS
from references import REFERENCES
from builder import build_chapters, build_references

# 模板路径
TEMPLATE = os.path.join(os.path.dirname(__file__), "thesis_template.docx")
OUTPUT = os.path.join(os.path.dirname(__file__), "output_thesis.docx")


def main():
    if not os.path.exists(TEMPLATE):
        print(f"错误：找不到模板文件 {TEMPLATE}")
        print("请先将 thesis_template.docx 放到本目录下。")
        sys.exit(1)

    doc = DocxTemplate(TEMPLATE)

    # 构建子文档
    chapters_sd = build_chapters(doc, CHAPTERS)
    refs_sd = build_references(doc, REFERENCES)

    # 组装上下文
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
