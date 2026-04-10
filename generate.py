"""
通用论文生成器。
用法: python generate.py <模板.docx> <数据.json> [输出.docx]

模板由各学校的 make.py 制作。
数据是包含论文内容的 JSON 文件。
"""
import os
import sys
import json
from docxtpl import DocxTemplate


def generate(template_path, data, output_path):
    """
    从模板和数据生成论文。

    参数:
        template_path: docxtpl 模板文件路径
        data: dict, 包含所有论文数据
        output_path: 输出文件路径
    """
    doc = DocxTemplate(template_path)
    doc.render(data)
    doc.save(output_path)
    print(f"论文已生成: {output_path}")


def main():
    if len(sys.argv) < 3:
        print("用法: python generate.py <模板.docx> <数据.json> [输出.docx]")
        sys.exit(1)

    template = sys.argv[1]
    data_file = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) > 3 else "output.docx"

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    generate(template, data, output)


if __name__ == "__main__":
    main()
