"""
参考文献区域模板制作 - 在参考文献标题后设置 Jinja2 循环。
保留第一条参考文献段落的格式，替换文本为循环变量。
"""
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

_WML_NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}


def setup_refs_template(doc, ref_title_idx):
    """
    在参考文献标题后设置循环。

    参数:
        doc: Document 对象
        ref_title_idx: "参考文献" 标题的段落索引
    """
    paras = doc.paragraphs

    # 找标题后第一个有实际内容的参考文献段落（优先找带编号的）
    sample_idx = None
    for i in range(ref_title_idx + 1, min(ref_title_idx + 10, len(paras))):
        p = paras[i]
        has_num = p._p.find('.//w:numPr', _WML_NS) is not None
        text = (p.text or "").strip()
        # 优先选带编号且有内容的段落
        if has_num and len(text) > 5:
            sample_idx = i
            break
    # 退路：找第一个有长文本的段落
    if sample_idx is None:
        for i in range(ref_title_idx + 1, min(ref_title_idx + 5, len(paras))):
            text = (paras[i].text or "").strip()
            if len(text) > 10 and "空一行" not in text:
                sample_idx = i
                break

    if sample_idx is None:
        print("  警告: 找不到参考文献样本段落")
        return

    sample_p = paras[sample_idx]

    # 替换样本段落文本为循环变量
    if sample_p.runs:
        sample_p.runs[0].text = "{{ ref }}"
        for r in sample_p.runs[1:]:
            r.text = ""

    # 在样本段落前后插入循环控制
    sample_p._p.addprevious(_make_p("{%p for ref in references %}"))
    sample_p._p.addnext(_make_p("{%p endfor %}"))

    # 清空 endfor 之后、致谢之前的段落
    endfor_elem = sample_p._p.getnext()  # 刚插入的 endfor
    elem = endfor_elem.getnext()
    while elem is not None:
        tag = elem.tag.split('}')[-1]
        if tag == 'p':
            texts = [t.text for t in elem.findall('.//w:t', _WML_NS) if t.text]
            full = ''.join(texts).strip()
            # 遇到致谢/附录标题就停止
            if any(kw in full for kw in ['致谢', '致 谢', '致  谢', '附录', '附 录']):
                break
            # 清空文本
            for t_elem in elem.findall('.//w:t', _WML_NS):
                t_elem.text = ""
        elem = elem.getnext()

    print(f"  参考文献循环已设置 (样本段落[{sample_idx}])")


def _make_p(text):
    p = OxmlElement('w:p')
    r = OxmlElement('w:r')
    t = OxmlElement('w:t')
    t.set(qn('xml:space'), 'preserve')
    t.text = text
    r.append(t)
    p.append(r)
    return p
