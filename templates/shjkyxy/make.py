"""
上海健康医学院本科毕业论文模板制作。
用法: cd thesis_project && python -m templates.shjkyxy.make <原始论文.docx>

模板结构 (以"基于机器学习的中药方剂推荐系统"为参考):
- P0-P25:   封面页 (P1 校徽, P2 标题头, P4 院徽, P6 中文题目, P8 英文题目, P25 sectPr)
- P26-P54:  原创性声明 + 使用授权说明
- P55-P64:  中文摘要 + 关键词 [sectPr@P55]
- P65-P75:  英文摘要 + 关键词 [sectPr@P65]
- P76-P125: 目录页 [sectPr@P76, Heading 1@P86 "目  录"]
- P126-P284: 正文6章
- P285-P298: 参考文献 (Heading 1)
- P299-P303: 致谢 (Heading 1)

关键 style 名称:
  Heading 1        — 摘要/ABSTRACT/目录/参考文献/致谢 标题
  Thesis Heading 1 — 章标题 (1 绪论, 2 相关技术...)
  Thesis Heading 2 — 节标题 (1.1 研究背景...)
  Normal           — 正文/封面/声明
"""
import os
import sys
import copy

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def make(src_path, out_path):
    out_dir = os.path.dirname(out_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    doc = Document(src_path)
    paras = doc.paragraphs

    print(f"原始: {len(paras)} 段落, {len(doc.tables)} 表格")

    # ========== Step 1: 封面 - 替换题目字段 ==========
    for i, p in enumerate(paras[:30]):
        t = (p.text or '').strip()
        # P6: 中文题目
        if '中药方剂' in t or '设计与实现' in t:
            if p.runs and len(t) > 10:
                # Check if this is the Chinese title (not English)
                if all(ord(c) < 128 for c in t[:5]):
                    continue  # skip English title
                p.runs[0].text = "{{ title_zh }}"
                for r in p.runs[1:]:
                    r.text = ""
                print(f"  封面中文题目: P{i}")
        # P8: English title
        if t.startswith('Machine Learning') or t.startswith('Design and'):
            if p.runs:
                p.runs[0].text = "{{ title_en }}"
                for r in p.runs[1:]:
                    r.text = ""
                print(f"  封面英文题目: P{i}")

    # 封面字段 — 原始论文P9-P24都是空段，需要往里面填入Jinja2变量
    # 选取P11-P16来放字段（居中的空段，位于题目下方）
    cover_fields = [
        (11, "学    院：{{ department }}"),
        (12, "专    业：{{ major }}"),
        (13, "姓    名：{{ name }}"),
        (14, "学    号：{{ student_id }}"),
        (15, "指导教师：{{ advisor }}"),
        (16, "{{ year }} 年 {{ month }} 月"),
    ]
    for idx, text in cover_fields:
        if idx < len(paras):
            p = paras[idx]
            if p.runs:
                p.runs[0].text = text
            else:
                p.add_run(text)

    print("  Step 1: 封面字段替换完成")

    # ========== Step 2: 保存格式样本 ==========
    body_pPr = None
    body_rPr = None
    ch_heading_pPr = None
    ch_heading_rPr = None
    sec_heading_pPr = None
    sec_heading_rPr = None

    # 先找到正文起始位置（第一个Thesis Heading 1），只从正文区域取格式样本
    body_area_start = False
    for p in paras:
        style = p.style.name if p.style else ''
        t = (p.text or '').strip()
        if style == 'Thesis Heading 1' and not body_area_start:
            body_area_start = True
        if style == 'Thesis Heading 1' and ch_heading_pPr is None and t:
            ch_heading_pPr = copy.deepcopy(p._p.pPr) if p._p.pPr is not None else None
            ch_heading_rPr = copy.deepcopy(p.runs[0]._r.find(qn('w:rPr'))) if p.runs else None
        elif style == 'Thesis Heading 2' and sec_heading_pPr is None and t:
            sec_heading_pPr = copy.deepcopy(p._p.pPr) if p._p.pPr is not None else None
            sec_heading_rPr = copy.deepcopy(p.runs[0]._r.find(qn('w:rPr'))) if p.runs else None
        elif style == 'Normal' and body_pPr is None and body_area_start and len(t) > 30:
            pPr = p._p.pPr
            if pPr is not None:
                ind = pPr.find(qn('w:ind'))
                if ind is not None and ind.get(qn('w:firstLine'), '0') != '0':
                    body_pPr = copy.deepcopy(pPr)
                    body_rPr = copy.deepcopy(p.runs[0]._r.find(qn('w:rPr'))) if p.runs else None

    print("  Step 2: 格式样本保存完成")

    # ========== Step 3: 中文摘要 → Jinja2 ==========
    for i, p in enumerate(paras):
        s = p.style.name if p.style else ''
        t = (p.text or '').strip()
        if s == 'Heading 1' and '摘' in t and '要' in t and 'ABSTRACT' not in t.upper():
            # Found 摘要 title, replace next body paragraphs
            for j in range(i + 1, min(i + 10, len(paras))):
                pj = paras[j]
                tj = (pj.text or '').strip()
                sj = pj.style.name if pj.style else ''
                if sj == 'Heading 1':
                    break
                if tj and '关键词' not in tj and sj == 'Normal':
                    # First body paragraph → loop
                    pj.runs[0].text = "{%p for para in abstract_zh_list %}"
                    for r in pj.runs[1:]:
                        r.text = ""
                    # Insert {{ para }} and endfor
                    p_para = OxmlElement('w:p')
                    if body_pPr:
                        p_para.append(copy.deepcopy(body_pPr))
                    r_para = OxmlElement('w:r')
                    if body_rPr:
                        r_para.append(copy.deepcopy(body_rPr))
                    t_el = OxmlElement('w:t')
                    t_el.set(qn('xml:space'), 'preserve')
                    t_el.text = '{{ para }}'
                    r_para.append(t_el)
                    p_para.append(r_para)
                    pj._p.addnext(p_para)
                    p_end = OxmlElement('w:p')
                    r_end = OxmlElement('w:r')
                    t_end = OxmlElement('w:t')
                    t_end.text = '{%p endfor %}'
                    r_end.append(t_end)
                    p_end.append(r_end)
                    p_para.addnext(p_end)
                    # Clear remaining abstract body paragraphs
                    for k in range(j + 1, min(j + 8, len(paras))):
                        pk = paras[k]
                        tk = (pk.text or '').strip()
                        sk = pk.style.name if pk.style else ''
                        if sk == 'Heading 1' or '关键词' in tk:
                            break
                        if tk and sk == 'Normal':
                            for r in pk.runs:
                                r.text = ""
                    break
            # Fix keywords
            for j in range(i + 1, min(i + 15, len(paras))):
                pj = paras[j]
                tj = (pj.text or '').strip()
                if '关键词' in tj:
                    if pj.runs:
                        pj.runs[0].text = "关键词：{{ keywords_zh }}"
                        for r in pj.runs[1:]:
                            r.text = ""
                    break
            break

    print("  Step 3: 中文摘要")

    # ========== Step 4: 英文摘要 → Jinja2 ==========
    paras = doc.paragraphs
    for i, p in enumerate(paras):
        s = p.style.name if p.style else ''
        t = (p.text or '').strip()
        if s == 'Heading 1' and 'ABSTRACT' in t.upper():
            for j in range(i + 1, min(i + 10, len(paras))):
                pj = paras[j]
                tj = (pj.text or '').strip()
                sj = pj.style.name if pj.style else ''
                if sj == 'Heading 1':
                    break
                if tj and 'KEY WORDS' not in tj.upper() and sj == 'Normal':
                    pj.runs[0].text = "{%p for para in abstract_en_list %}"
                    for r in pj.runs[1:]:
                        r.text = ""
                    p_para = OxmlElement('w:p')
                    if body_pPr:
                        p_para.append(copy.deepcopy(body_pPr))
                    r_para = OxmlElement('w:r')
                    if body_rPr:
                        r_para.append(copy.deepcopy(body_rPr))
                    t_el = OxmlElement('w:t')
                    t_el.set(qn('xml:space'), 'preserve')
                    t_el.text = '{{ para }}'
                    r_para.append(t_el)
                    p_para.append(r_para)
                    pj._p.addnext(p_para)
                    p_end = OxmlElement('w:p')
                    r_end = OxmlElement('w:r')
                    t_end = OxmlElement('w:t')
                    t_end.text = '{%p endfor %}'
                    r_end.append(t_end)
                    p_end.append(r_end)
                    p_para.addnext(p_end)
                    for k in range(j + 1, min(j + 8, len(paras))):
                        pk = paras[k]
                        tk = (pk.text or '').strip()
                        if 'KEY WORDS' in tk.upper() or pk.style.name == 'Heading 1':
                            break
                        if tk and pk.style.name == 'Normal':
                            for r in pk.runs:
                                r.text = ""
                    break
            for j in range(i + 1, min(i + 15, len(paras))):
                pj = paras[j]
                tj = (pj.text or '').strip()
                if 'KEY WORDS' in tj.upper():
                    if pj.runs:
                        pj.runs[0].text = "KEY WORDS: {{ keywords_en }}"
                        for r in pj.runs[1:]:
                            r.text = ""
                    break
            break

    print("  Step 4: 英文摘要")

    # ========== Step 5: 目录页 - 清空 ==========
    paras = doc.paragraphs
    for i, p in enumerate(paras):
        s = p.style.name if p.style else ''
        t = (p.text or '').strip()
        if s == 'Heading 1' and '目' in t and '录' in t:
            # Clear TOC entries after this
            for j in range(i + 1, min(i + 60, len(paras))):
                pj = paras[j]
                sj = pj.style.name if pj.style else ''
                if sj in ('Heading 1', 'Thesis Heading 1'):
                    break
                for r in pj.runs:
                    r.text = ""
            break

    print("  Step 5: 目录清空")

    # ========== Step 6: 正文 → Jinja2 循环 ==========
    paras = doc.paragraphs
    body_start = None
    body_end = None

    for i, p in enumerate(paras):
        s = p.style.name if p.style else ''
        t = (p.text or '').strip()
        if s == 'Thesis Heading 1' and body_start is None:
            body_start = i
        if s == 'Heading 1' and '参考文献' in t:
            body_end = i
            break

    if body_start is None or body_end is None:
        print("  ERROR: 找不到正文范围")
        return

    print(f"  正文范围: P{body_start} ~ P{body_end} ({body_end - body_start} 段)")

    # Delete body paragraphs, keep first 14 for Jinja2 loop
    # (no 三级标题, so loop is simpler: ch → sec → content)
    for i in range(body_end - 1, body_start + 13, -1):
        p = paras[i]
        pPr = p._p.pPr
        has_sect = pPr is not None and pPr.find(qn('w:sectPr')) is not None
        if not has_sect:
            p._p.getparent().remove(p._p)

    # Remove images and tables from remaining body paragraphs
    paras = doc.paragraphs
    for i in range(body_start, min(body_start + 14, len(paras))):
        p = paras[i]
        for drawing in p._p.findall('.//' + qn('w:drawing')):
            drawing.getparent().remove(drawing)

    # Remove all tables
    while len(doc.tables) > 0:
        tbl = doc.tables[-1]
        tbl._element.getparent().remove(tbl._element)

    print(f"  Step 6a: 删除正文和表格，剩余 {len(doc.paragraphs)} 段")

    # Set Jinja2 tags (no 三级标题, simpler loop)
    paras = doc.paragraphs
    tags = [
        (body_start + 0,  "{%p for ch in chapters %}"),
        (body_start + 1,  "{{ ch.title }}"),
        (body_start + 2,  "{%p for item in ch.content %}"),
        (body_start + 3,  "{{ item }}"),
        (body_start + 4,  "{%p endfor %}"),
        (body_start + 5,  "{%p for sec in ch.sections %}"),
        (body_start + 6,  "{{ sec.title }}"),
        (body_start + 7,  "{%p for item in sec.content %}"),
        (body_start + 8,  "{{ item }}"),
        (body_start + 9,  "{%p endfor %}"),
        (body_start + 10, "{%p for sub in sec.subsections %}"),
        (body_start + 11, "{{ sub.title }}"),
        (body_start + 12, "{%p for item in sub.content %}"),
        (body_start + 13, "{{ item }}"),
    ]
    # Need more paragraphs for endfor tags — insert them
    last_p = paras[body_start + 13]
    for tag_text in ["{%p endfor %}", "{%p endfor %}", "{%p endfor %}", "{%p endfor %}"]:
        p_new = OxmlElement('w:p')
        r_new = OxmlElement('w:r')
        t_new = OxmlElement('w:t')
        t_new.text = tag_text
        r_new.append(t_new)
        p_new.append(r_new)
        last_p._p.addnext(p_new)
        last_p = type('P', (), {'_p': p_new})()

    paras = doc.paragraphs
    for idx, text in tags:
        if idx >= len(paras):
            break
        p = paras[idx]
        if p.runs:
            p.runs[0].text = text
            for r in p.runs[1:]:
                r.text = ""
        else:
            p.add_run(text)

    # Apply correct styles
    def _apply_fmt(para, saved_pPr, saved_rPr):
        if saved_pPr is not None:
            old = para._p.pPr
            if old is not None:
                para._p.remove(old)
            para._p.insert(0, copy.deepcopy(saved_pPr))
        if saved_rPr is not None and para.runs:
            r = para.runs[0]._r
            old = r.find(qn('w:rPr'))
            if old is not None:
                r.remove(old)
            r.insert(0, copy.deepcopy(saved_rPr))

    _apply_fmt(paras[body_start + 1], ch_heading_pPr, ch_heading_rPr)
    # sec.title → Thesis Heading 2
    _apply_fmt(paras[body_start + 6], sec_heading_pPr, sec_heading_rPr)
    # sub.title reuses sec_heading style (no Thesis Heading 3 in this template)
    _apply_fmt(paras[body_start + 11], sec_heading_pPr, sec_heading_rPr)
    # body content paragraphs → Normal with indent
    for offset in [3, 8, 13]:
        _apply_fmt(paras[body_start + offset], body_pPr, body_rPr)
    # for/endfor tags should be Normal, not heading styles
    # P+5 ({%p for sec %}), P+9 ({%p endfor %}), P+10 ({%p for sub %}) might have heading style
    for offset in [0, 2, 4, 5, 7, 9, 10, 12]:
        p = paras[body_start + offset]
        if p.style and p.style.name in ('Thesis Heading 1', 'Thesis Heading 2'):
            _apply_fmt(p, body_pPr, body_rPr)

    print("  Step 6: 正文Jinja2循环")

    # ========== Step 7: 结论 → Jinja2 ==========
    paras = doc.paragraphs
    for i, p in enumerate(paras):
        s = p.style.name if p.style else ''
        t = (p.text or '').strip()
        if s == 'Heading 1' and '参考文献' in t:
            # 结论在参考文献之前，找 "结论" Heading 1 或 Thesis Heading 1
            # Actually 结论 is at P279 with style Thesis Heading 1
            break

    # Find 结论
    for i, p in enumerate(paras):
        s = p.style.name if p.style else ''
        t = (p.text or '').strip()
        if ('结论' in t or '结  论' in t) and s in ('Heading 1', 'Thesis Heading 1'):
            for j in range(i + 1, min(i + 10, len(paras))):
                pj = paras[j]
                sj = pj.style.name if pj.style else ''
                tj = (pj.text or '').strip()
                if sj == 'Heading 1':
                    break
                if tj and sj == 'Normal':
                    conc_pPr = copy.deepcopy(pj._p.pPr) if pj._p.pPr else None
                    conc_rPr = copy.deepcopy(pj.runs[0]._r.find(qn('w:rPr'))) if pj.runs else None
                    pj.runs[0].text = "{%p for para in conclusion_list %}"
                    for r in pj.runs[1:]:
                        r.text = ""
                    p_para = OxmlElement('w:p')
                    if conc_pPr:
                        p_para.append(copy.deepcopy(conc_pPr))
                    r_para = OxmlElement('w:r')
                    if conc_rPr:
                        r_para.append(copy.deepcopy(conc_rPr))
                    t_el = OxmlElement('w:t')
                    t_el.set(qn('xml:space'), 'preserve')
                    t_el.text = '{{ para }}'
                    r_para.append(t_el)
                    p_para.append(r_para)
                    pj._p.addnext(p_para)
                    p_end = OxmlElement('w:p')
                    r_end = OxmlElement('w:r')
                    t_end = OxmlElement('w:t')
                    t_end.text = '{%p endfor %}'
                    r_end.append(t_end)
                    p_end.append(r_end)
                    p_para.addnext(p_end)
                    # Clear remaining conclusion paragraphs
                    for k in range(j + 1, min(j + 10, len(paras))):
                        pk = paras[k]
                        sk = pk.style.name if pk.style else ''
                        if sk == 'Heading 1':
                            break
                        if (pk.text or '').strip():
                            for r in pk.runs:
                                r.text = ""
                    break
            break

    print("  Step 7: 结论")

    # ========== Step 8: 参考文献 → Jinja2 ==========
    paras = doc.paragraphs
    for i, p in enumerate(paras):
        s = p.style.name if p.style else ''
        t = (p.text or '').strip()
        if s == 'Heading 1' and '参考文献' in t:
            for j in range(i + 1, min(i + 20, len(paras))):
                pj = paras[j]
                tj = (pj.text or '').strip()
                sj = pj.style.name if pj.style else ''
                if sj == 'Heading 1':
                    break
                if tj and sj == 'Normal':
                    ref_pPr = copy.deepcopy(pj._p.pPr) if pj._p.pPr else None
                    ref_rPr = copy.deepcopy(pj.runs[0]._r.find(qn('w:rPr'))) if pj.runs else None
                    pj.runs[0].text = "{%p for ref in references %}"
                    for r in pj.runs[1:]:
                        r.text = ""
                    p_ref = OxmlElement('w:p')
                    if ref_pPr:
                        p_ref.append(copy.deepcopy(ref_pPr))
                    r_ref = OxmlElement('w:r')
                    if ref_rPr:
                        r_ref.append(copy.deepcopy(ref_rPr))
                    t_ref = OxmlElement('w:t')
                    t_ref.set(qn('xml:space'), 'preserve')
                    t_ref.text = '{{ ref }}'
                    r_ref.append(t_ref)
                    p_ref.append(r_ref)
                    pj._p.addnext(p_ref)
                    p_end = OxmlElement('w:p')
                    r_end = OxmlElement('w:r')
                    t_end = OxmlElement('w:t')
                    t_end.text = '{%p endfor %}'
                    r_end.append(t_end)
                    p_end.append(r_end)
                    p_ref.addnext(p_end)
                    for k in range(j + 1, min(j + 15, len(paras))):
                        pk = paras[k]
                        sk = pk.style.name if pk.style else ''
                        if sk == 'Heading 1':
                            break
                        if (pk.text or '').strip():
                            for r in pk.runs:
                                r.text = ""
                    break
            break

    print("  Step 8: 参考文献")

    # ========== Step 9: 致谢 → Jinja2 ==========
    paras = doc.paragraphs
    for i, p in enumerate(paras):
        s = p.style.name if p.style else ''
        t = (p.text or '').strip()
        if s == 'Heading 1' and '致' in t and '谢' in t:
            for j in range(i + 1, min(i + 8, len(paras))):
                pj = paras[j]
                tj = (pj.text or '').strip()
                sj = pj.style.name if pj.style else ''
                if tj and sj == 'Normal':
                    ack_pPr = copy.deepcopy(pj._p.pPr) if pj._p.pPr else None
                    ack_rPr = copy.deepcopy(pj.runs[0]._r.find(qn('w:rPr'))) if pj.runs else None
                    pj.runs[0].text = "{%p for para in acknowledgement_list %}"
                    for r in pj.runs[1:]:
                        r.text = ""
                    p_para = OxmlElement('w:p')
                    if ack_pPr:
                        p_para.append(copy.deepcopy(ack_pPr))
                    r_para = OxmlElement('w:r')
                    if ack_rPr:
                        r_para.append(copy.deepcopy(ack_rPr))
                    t_el = OxmlElement('w:t')
                    t_el.set(qn('xml:space'), 'preserve')
                    t_el.text = '{{ para }}'
                    r_para.append(t_el)
                    p_para.append(r_para)
                    pj._p.addnext(p_para)
                    p_end = OxmlElement('w:p')
                    r_end = OxmlElement('w:r')
                    t_end = OxmlElement('w:t')
                    t_end.text = '{%p endfor %}'
                    r_end.append(t_end)
                    p_end.append(r_end)
                    p_para.addnext(p_end)
                    for k in range(j + 1, min(j + 6, len(paras))):
                        pk = paras[k]
                        if (pk.text or '').strip():
                            for r in pk.runs:
                                r.text = ""
                    break
            break

    print("  Step 9: 致谢")

    # ========== Step 10: 清理空段落(仅摘要之后) ==========
    paras = doc.paragraphs
    removed = 0
    # Find first Heading 1 摘要
    clean_start = len(paras)
    for i, p in enumerate(paras):
        s = p.style.name if p.style else ''
        t = (p.text or '').strip()
        if s == 'Heading 1' and '摘' in t:
            clean_start = i
            break

    for i in range(len(paras) - 1, clean_start - 1, -1):
        p = paras[i]
        text = (p.text or "").strip()
        style = p.style.name if p.style else ""
        pPr = p._p.pPr
        has_sect = pPr is not None and pPr.find(qn('w:sectPr')) is not None
        if has_sect:
            continue
        if text:
            continue
        if style in ('Heading 1', 'Thesis Heading 1', 'Thesis Heading 2'):
            continue
        has_drawing = bool(p._p.findall('.//' + qn('w:drawing')))
        if not has_drawing:
            p._p.getparent().remove(p._p)
            removed += 1

    print(f"  Step 10: 删除 {removed} 个空段落")

    # ========== Save ==========
    doc.save(out_path)

    # Verify
    doc2 = Document(out_path)
    p_count = len(doc2.paragraphs)
    t_count = len(doc2.tables)
    print(f"\n结果: {p_count} 段落, {t_count} 表格")
    for i, p in enumerate(doc2.paragraphs):
        t = (p.text or "").strip()
        if t:
            print(f"  P{i:2d} [{p.style.name:25s}] {t[:80]}")

    full = "\n".join(p.text or "" for p in doc2.paragraphs)
    for tag in ["{%", "%}", "{{", "}}"]:
        count = full.count(tag)
        if count:
            print(f"  Jinja2 '{tag}': {count}")


def main():
    if len(sys.argv) < 2:
        print("用法: python -m templates.shjkyxy.make <原始论文.docx>")
        sys.exit(1)

    src = sys.argv[1]
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "template.docx")

    print(f"输入: {src}")
    print(f"输出: {out}")
    make(src, out)
    print("完成!")


if __name__ == "__main__":
    main()
