"""
段落级扫描 - 提取段落的详细 run 信息。
供 AI 查看内容和格式，决定哪些 run 需要替换。
"""
from docx import Document

_WML_NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}


def _load(doc_or_path):
    if isinstance(doc_or_path, str):
        return Document(doc_or_path)
    return doc_or_path


def scan_paragraphs(doc_or_path, start=0, end=None, detail=False):
    """
    扫描指定范围段落。接受文件路径或已加载的 Document 对象。

    返回:
        [{"idx", "text", "style", "has_sectPr", "has_numPr",
          "alignment", "runs"(if detail)}]
    """
    doc = _load(doc_or_path)
    paras = doc.paragraphs
    end = end or len(paras)
    results = []

    for i in range(start, min(end, len(paras))):
        p = paras[i]
        text = (p.text or "").strip()
        if not text and not detail:
            continue

        info = {
            "idx": i,
            "text": text[:100],
            "style": p.style.name if p.style else "None",
            "has_sectPr": p._p.find('.//w:sectPr', _WML_NS) is not None,
            "has_numPr": p._p.find('.//w:numPr', _WML_NS) is not None,
            "alignment": str(p.paragraph_format.alignment)
                         if p.paragraph_format.alignment else None,
        }

        if detail:
            info["runs"] = _get_runs(p)

        results.append(info)

    return results


def scan_para_runs(doc_or_path, para_idx):
    """Scan a single paragraph's runs in detail."""
    result = scan_paragraphs(doc_or_path, start=para_idx,
                             end=para_idx + 1, detail=True)
    return result[0] if result else None


def _get_runs(para):
    runs = []
    for j, r in enumerate(para.runs):
        runs.append({
            "idx": j,
            "text": r.text,
            "font": r.font.name,
            "size": r.font.size,
            "bold": r.font.bold,
            "underline": r.font.underline,
        })
    return runs
