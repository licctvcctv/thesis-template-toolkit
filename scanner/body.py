"""
正文区域扫描 - 在正文中找到格式样本（标题/表格/图片/正文段落）。

对于长论文（几十章），只需要保留一章作为格式样本。
本模块帮助 AI 找到：哪一章包含最完整的格式样本。
"""
import re
from docx import Document

_WML_NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

# 标题模式
_H1 = re.compile(r'^\d+[\s　]+\S')
_H2 = re.compile(r'^\d+\.\d+[\s　]+\S')
_H3 = re.compile(r'^\d+\.\d+\.\d+[\s　]+\S')
_H1_CN = re.compile(r'^第[一二三四五六七八九十]+章')


def scan_body(doc_or_path, body_start, body_end):
    """
    扫描正文区域，定位格式样本。

    返回:
        {
            "h1_samples": [{"idx": para_idx, "text": ...}],
            "h2_samples": [...],
            "h3_samples": [...],
            "body_samples": [...],  # 普通正文段落
            "table_indices": [...],  # 表格在 body elements 中的位置
            "has_figures": bool,
            "best_chapter": {  # 包含最多格式样本的章节
                "start": para_idx,
                "end": para_idx,
                "has_h2": bool,
                "has_h3": bool,
                "has_table": bool,
                "has_figure": bool,
            }
        }
    """
    doc = doc_or_path if not isinstance(doc_or_path, str) \
        else Document(doc_or_path)
    paras = doc.paragraphs

    h1s, h2s, h3s, bodies = [], [], [], []
    has_figure = False

    for i in range(body_start, min(body_end, len(paras))):
        text = (paras[i].text or "").strip()
        if not text:
            continue
        # 跳过目录条目
        if '\t' in text and len(text) < 60:
            continue

        if _H3.match(text):
            h3s.append({"idx": i, "text": text[:50]})
        elif _H2.match(text):
            h2s.append({"idx": i, "text": text[:50]})
        elif _H1.match(text) or _H1_CN.match(text):
            h1s.append({"idx": i, "text": text[:50]})
        elif len(text) > 20:
            bodies.append({"idx": i, "text": text[:50]})

        if "图" in text and re.match(r'^图\d', text):
            has_figure = True

    # 检测表格
    tables = _find_tables_in_range(doc, body_start, body_end)

    # 找最佳章节（包含最多格式元素的章节）
    best = _find_best_chapter(
        h1s, h2s, h3s, tables, has_figure,
        body_start, body_end)

    return {
        "h1_samples": h1s[:5],
        "h2_samples": h2s[:5],
        "h3_samples": h3s[:5],
        "body_samples": bodies[:3],
        "table_count": len(tables),
        "has_figures": has_figure,
        "best_chapter": best,
    }


def _find_tables_in_range(doc, start, end):
    """找到正文范围内的表格位置"""
    tables = []
    body = doc.element.body
    para_idx = 0
    for elem in body:
        tag = elem.tag.split('}')[-1]
        if tag == 'p':
            para_idx += 1
        elif tag == 'tbl':
            if start <= para_idx <= end:
                tables.append(para_idx)
    return tables


def _find_best_chapter(h1s, h2s, h3s, tables, has_fig,
                       body_start, body_end):
    """找包含最多格式样本的章节"""
    if not h1s:
        return {"start": body_start, "end": body_end}

    best = None
    best_score = -1

    for i, h1 in enumerate(h1s):
        ch_start = h1["idx"]
        ch_end = h1s[i + 1]["idx"] if i + 1 < len(h1s) \
            else body_end

        score = 0
        has_h2 = any(ch_start < h["idx"] < ch_end for h in h2s)
        has_h3 = any(ch_start < h["idx"] < ch_end for h in h3s)
        has_tbl = any(ch_start < t < ch_end for t in tables)

        if has_h2: score += 2
        if has_h3: score += 2
        if has_tbl: score += 3

        if score > best_score:
            best_score = score
            best = {
                "start": ch_start,
                "end": ch_end,
                "has_h2": has_h2,
                "has_h3": has_h3,
                "has_table": has_tbl,
                "has_figure": has_fig,
                "score": score,
            }

    return best or {"start": body_start, "end": body_end}
