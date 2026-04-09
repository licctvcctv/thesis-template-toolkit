"""
文档结构扫描 - 识别文档的逻辑分区（封面/声明/摘要/目录/正文等）。
"""
import re
from docx import Document


# 各分区的关键词模式（按优先级排列）
SECTION_MARKERS = {
    "cover": ["届本科生毕业", "本科毕业论文", "毕业设计（论文）"],
    "declaration": ["原创性声明", "原创性申明", "学术诚信"],
    "abstract_zh": ["摘  要", "摘 要"],
    "abstract_en": ["ABSTRACT", "Abstract"],
    "toc": ["目  录", "目 录"],
    "body": [],  # 特殊处理
    "conclusion": ["结  论", "结 论", "结论"],
    "acknowledgement": ["致  谢", "致 谢", "致谢"],
    "references": ["参考文献"],
    "appendix": ["附  录", "附 录", "附录"],
}


def scan_structure(doc_path):
    """
    扫描文档分区结构。

    返回:
        {
            "doc_path": str,
            "total_paragraphs": int,
            "total_tables": int,
            "total_sections": int,
            "styles_used": {style_name: count},
            "parts": {
                "cover": {"start": para_idx, "text": "..."},
                "abstract_zh": {"start": para_idx, "text": "..."},
                ...
            },
            "body_start": para_idx,
            "body_end": para_idx,
        }
    """
    doc = Document(doc_path)
    paras = doc.paragraphs
    result = {
        "doc_path": doc_path,
        "total_paragraphs": len(paras),
        "total_tables": len(doc.tables),
        "total_sections": len(doc.sections),
        "styles_used": _count_styles(paras),
        "parts": {},
    }

    # 定位各分区
    for name, keywords in SECTION_MARKERS.items():
        for kw in keywords:
            for i, p in enumerate(paras):
                if kw in (p.text or ""):
                    result["parts"][name] = {
                        "start": i,
                        "text": (p.text or "").strip()[:60],
                    }
                    break
            if name in result["parts"]:
                break

    # 正文起始：目录之后，致谢之前，第一个匹配章节标题的段落
    toc_end = result["parts"].get("toc", {}).get("start", 0)
    ack_start = result["parts"].get(
        "acknowledgement", {}).get("start", len(paras))
    # 跳过目录条目（含 tab）
    for i in range(toc_end + 1, ack_start):
        text = (paras[i].text or "").strip()
        if '\t' in text:
            continue
        if (re.match(r'^\d+[\s　]+', text)
                or re.match(r'^第[一二三四五六七八九十]+章', text)):
            result["body_start"] = i
            break

    result["body_end"] = ack_start

    return result


def _count_styles(paras):
    """统计使用的段落样式"""
    styles = {}
    for p in paras:
        name = p.style.name if p.style else "None"
        styles[name] = styles.get(name, 0) + 1
    return styles
