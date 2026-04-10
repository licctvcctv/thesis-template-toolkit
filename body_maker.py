"""
正文区域模板制作 - 保留样本段落格式，插入 Jinja2 循环标签。

核心逻辑：
1. 在正文区域找到 H1/H2/H3/BODY 各一个样本段落
2. 把样本段落的文本换成 Jinja2 变量（只改 run.text）
3. 在样本段落周围插入 {%p for %} / {%p endfor %} 控制段落
4. 清空正文区域其他段落（只清文本，不删段落）

这样生成的内容会完全继承模板的格式，零硬编码。
"""
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from scanner import scan_structure, scan_body

_WML_NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}


def setup_body_template(doc_path, output_path=None):
    """
    在模板正文区域设置 Jinja2 循环结构。

    修改后的正文区域结构：
        {%p for ch in chapters %}
        {{ ch.title }}              ← H1 样本段落格式
        {%p for sec in ch.sections %}
        {{ sec.title }}             ← H2 样本段落格式
        {%p for para in sec.content %}
        {{ para }}                  ← BODY 样本段落格式
        {%p endfor %}
        {%p for sub in sec.subsections %}
        {{ sub.title }}             ← H3 样本段落格式
        {%p for p2 in sub.content %}
        {{ p2 }}                    ← BODY 样本段落格式（复用）
        {%p endfor %}
        {%p endfor %}
        {%p endfor %}
        {%p endfor %}

    返回修改后的 Document 对象。
    """
    doc = Document(doc_path)
    paras = doc.paragraphs

    # 1. 扫描定位
    s = scan_structure(doc_path)
    bs = s.get('body_start')
    be = s.get('body_end', len(paras))
    if not bs:
        print(f"  警告: 未找到正文区域")
        return doc

    body = scan_body(doc_path, bs, be)

    h1_idx = body['h1_samples'][0]['idx'] if body['h1_samples'] else None
    h2_idx = body['h2_samples'][0]['idx'] if body['h2_samples'] else None
    h3_idx = body['h3_samples'][0]['idx'] if body['h3_samples'] else None
    body_idx = body['body_samples'][0]['idx'] if body['body_samples'] else None

    if not all([h1_idx, body_idx]):
        print(f"  警告: 样本段落不足 h1={h1_idx} body={body_idx}")
        return doc

    # 找第二个正文段落作为 sub.content 的样本
    body2_idx = body['body_samples'][1]['idx'] if len(body['body_samples']) > 1 else body_idx

    keep = {h1_idx, h2_idx, h3_idx, body_idx, body2_idx} - {None}

    # 2. 清空正文区域非样本段落（只清文本，不删段落）
    _keep_keywords = ['参考文献', '致谢', '致 谢', '致  谢',
                      '附录', '附 录', '附  录']
    # 检测图/表标签段落并保留
    import re as _re
    _fig_pat = _re.compile(r'^图\d')
    _tbl_pat = _re.compile(r'^表\d')
    for i in range(bs, be):
        if i in keep:
            continue
        p = paras[i]
        if p._p.find('.//w:sectPr', _WML_NS) is not None:
            continue
        text = (p.text or "").strip()
        # 保留特殊标题段落
        if any(kw in text for kw in _keep_keywords):
            continue
        # 保留带编号的段落（参考文献列表等）
        if p._p.find('.//w:numPr', _WML_NS) is not None and len(text) > 5:
            continue
        # 保留图/表标签段落（作为格式样本）
        if _fig_pat.match(text) or _tbl_pat.match(text):
            # 替换为 Jinja2 变量，保留格式
            if p.runs:
                if _fig_pat.match(text):
                    p.runs[0].text = "{{ fig_caption }}"
                else:
                    p.runs[0].text = "{{ tbl_caption }}"
                for r in p.runs[1:]:
                    r.text = ""
            continue
        for r in p.runs:
            r.text = ""

    # 删除正文区域的表格（示例表格不保留）
    body_elem = doc.element.body
    tables_to_remove = []
    para_count = 0
    for elem in body_elem:
        tag = elem.tag.split('}')[-1]
        if tag == 'p':
            para_count += 1
        elif tag == 'tbl' and bs <= para_count <= be:
            tables_to_remove.append(elem)
    for tbl in tables_to_remove:
        body_elem.remove(tbl)

    # 3. 替换样本段落文本为 Jinja2 变量
    # H1 标题设置页前分页（每章另起一页）
    paras[h1_idx].paragraph_format.page_break_before = True
    _replace_para_text(paras[h1_idx], "{{ ch.title }}")
    if h2_idx:
        _replace_para_text(paras[h2_idx], "{{ sec.title }}")
    if h3_idx:
        _replace_para_text(paras[h3_idx], "{{ sub.title }}")
    _replace_para_text(paras[body_idx], "{{ para }}")
    if body2_idx != body_idx:
        _replace_para_text(paras[body2_idx], "{{ p2 }}")
    else:
        # 需要复制 body 样本段落作为 sub.content 的模板
        # 简化处理：sub.content 复用同一个变量名
        pass

    # 4. 重排样本段落到正确逻辑顺序，然后插入控制标签
    # 正确顺序：H1 → H2 → BODY → H3 → BODY2
    # 有些模板中 BODY 可能在 H2 前面，需要调整 DOM 顺序

    h1_p = paras[h1_idx]._p
    h2_p = paras[h2_idx]._p if h2_idx else None
    h3_p = paras[h3_idx]._p if h3_idx else None
    body_p = paras[body_idx]._p
    body2_p = paras[body2_idx]._p if body2_idx != body_idx else None

    # 确保 DOM 顺序：H1 → H2 → BODY → H3 → BODY2
    # 把所有样本段落移到 H1 后面按正确顺序排列
    anchor = h1_p
    if h2_p is not None and h2_p is not h1_p:
        anchor.addnext(h2_p)
        anchor = h2_p
    if body_p is not anchor:
        anchor.addnext(body_p)
        anchor = body_p
    if h3_p is not None and h3_p is not anchor:
        anchor.addnext(h3_p)
        anchor = h3_p
    if body2_p is not None and body2_p is not anchor:
        anchor.addnext(body2_p)
        anchor = body2_p

    # 现在 DOM 顺序正确，按序插入控制标签
    _insert_before(h1_p, "{%p for ch in chapters %}")

    if h2_p is not None:
        _insert_before(h2_p, "{%p for sec in ch.sections %}")

    _insert_before(body_p, "{%p for para in sec.content %}")
    endfor_content = _insert_after(body_p, "{%p endfor %}")

    if h3_p is not None:
        _insert_before(h3_p, "{%p for sub in sec.subsections %}")
        if body2_p is not None:
            _insert_before(body2_p, "{%p for p2 in sub.content %}")
            endfor_sub_content = _insert_after(body2_p, "{%p endfor %}")
        else:
            p_for = _insert_after(h3_p, "{%p for p2 in sub.content %}")
            p_var = _insert_after(p_for, "{{ p2 }}")
            endfor_sub_content = _insert_after(p_var, "{%p endfor %}")
        last = _insert_after(endfor_sub_content, "{%p endfor %}")
    else:
        last = endfor_content

    if h2_p is not None:
        last = _insert_after(last, "{%p endfor %}")
    _insert_after(last, "{%p endfor %}")

    # 5. 移除正文前的 sectPr（修复 LibreOffice 不渲染问题）
    # 找到 for ch in chapters 标签前面最近的 sectPr
    for_ch = None
    for elem in doc.element.body:
        tag = elem.tag.split('}')[-1]
        if tag == 'p':
            texts = [t.text for t in elem.findall(
                './/w:t', _WML_NS) if t.text]
            if any('for ch in chapters' in (t or '') for t in texts):
                for_ch = elem
                break
    if for_ch is not None:
        prev = for_ch.getprevious()
        while prev is not None:
            if prev.find('.//w:sectPr', _WML_NS) is not None:
                sect = prev.find('.//w:sectPr', _WML_NS)
                sect.getparent().remove(sect)
                break
            prev = prev.getprevious()

    if output_path:
        doc.save(output_path)
        print(f"  正文循环已设置: {output_path}")

    return doc


def _replace_para_text(para, new_text):
    """替换段落文本，只改第一个有文字的 run，清空其余"""
    found = False
    for r in para.runs:
        if not found and r.text.strip():
            r.text = new_text
            found = True
        elif found:
            r.text = ""
    if not found and para.runs:
        para.runs[0].text = new_text


def _insert_before(ref_elem, text):
    p = _make_p(text)
    ref_elem.addprevious(p)
    return p


def _insert_after(ref_elem, text):
    p = _make_p(text)
    ref_elem.addnext(p)
    return p


def _make_p(text):
    p = OxmlElement('w:p')
    r = OxmlElement('w:r')
    t = OxmlElement('w:t')
    t.set(qn('xml:space'), 'preserve')
    t.text = text
    r.append(t)
    p.append(r)
    return p
