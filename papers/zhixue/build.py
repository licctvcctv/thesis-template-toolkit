"""
智学云课论文组装器。
读取所有章节 JSON，组装成完整数据，调用 generate.py 导出。

用法: python build.py <模板.docx> [输出.docx]
"""
import os
import sys
import json
import glob

# 项目根目录
ROOT = os.path.join(os.path.dirname(__file__), "../..")
sys.path.insert(0, ROOT)
from generate import generate

HERE = os.path.dirname(os.path.abspath(__file__))


def load_json(filename):
    path = os.path.join(HERE, filename)
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_data():
    """组装所有章节数据"""
    # 元数据（封面/摘要/致谢）
    meta = load_json("meta.json")
    if not meta:
        raise FileNotFoundError("meta.json not found")

    # 加载所有章节（按文件名排序）
    chapters = []
    ch_files = sorted(glob.glob(os.path.join(HERE, "ch*.json")))
    for ch_file in ch_files:
        ch = load_json(os.path.basename(ch_file))
        if ch:
            chapters.append(ch)
            print(f"  加载: {os.path.basename(ch_file)}"
                  f" -> {ch['title']}")

    # 参考文献
    refs_data = load_json("references.json")
    references = refs_data.get("references", []) if refs_data else []

    # 组装完整数据
    data = {**meta, "chapters": chapters, "references": references}
    return data


def main():
    if len(sys.argv) < 2:
        print("用法: python build.py <模板.docx> [输出.docx]")
        sys.exit(1)

    template = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "output.docx"

    print("组装论文数据...")
    data = build_data()
    print(f"  {len(data['chapters'])} 章, "
          f"{len(data.get('references', []))} 条参考文献")

    print(f"生成论文: {template} -> {output}")
    generate(template, data, output)


if __name__ == "__main__":
    main()
