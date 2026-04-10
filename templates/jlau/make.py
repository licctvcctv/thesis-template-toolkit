"""
吉林农业大学本科生毕业论文模板制作。
用法: cd thesis_project && python -m templates.jlau.make <原始模板.docx>

模板特点:
- 封面在单元格表格(table[0])内，字段用下划线空格占位
- 有三种目录格式（农理工/毕设/经管社科），只保留农理工类
- 章标题用 Heading 1 + "第X章" 格式
- 正文小四号宋体，首行缩进两字符，行间距固定值20磅
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from body_maker import setup_body_template
from refs_maker import setup_refs_template
from docx import Document


def _replace_cover_field(cell_para, label, jinja_var):
    """替换封面表格内的字段：清空下划线空格 run，写入 Jinja2 变量"""
    runs = cell_para.runs
    found_label = False
    for r in runs:
        if label in r.text:
            found_label = True
        elif found_label and r.font.underline:
            # 第一个下划线 run 写变量，其余清空
            if jinja_var:
                r.text = jinja_var
                jinja_var = None  # 只写一次
            else:
                r.text = ""


def _clear_instruction_paras(doc, start, end):
    """清空指定范围内的格式说明段落（含"号""磅""宋体"等关键字）"""
    inst_keywords = ["号", "磅", "宋体", "黑体", "加粗", "行间距",
                     "罗马体", "居中", "居左", "缩进", "标点",
                     "标题", "参考模板", "可参考"]
    for i in range(start, min(end, len(doc.paragraphs))):
        text = (doc.paragraphs[i].text or "").strip()
        if any(kw in text for kw in inst_keywords):
            for r in doc.paragraphs[i].runs:
                r.text = ""


def _setup_jlau_body(doc_path):
    """手动设置正文循环。吉林农大模板只有 H1 + body 样本。"""
    from docx import Document
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from scanner import scan_structure, scan_body

    _NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

    doc = Document(doc_path)
    paras = doc.paragraphs
    s = scan_structure(doc)
    bs = s.get('body_start')
    be = s.get('body_end', len(paras))

    if not bs:
        print("  警告: 未找到正文区域")
        return

    body = scan_body(doc, bs, be)
    h1_idx = body['h1_samples'][0]['idx'] if body['h1_samples'] else None
    body_idx = body['body_samples'][0]['idx'] if body['body_samples'] else None

    if not h1_idx or not body_idx:
        print(f"  警告: 样本不足 h1={h1_idx} body={body_idx}")
        return

    keep = {h1_idx, body_idx}

    # 清空非样本段落
    _keep_kw = ['参考文献', '致谢', '致 谢', '致  谢', '附录', '附 录']
    for i in range(bs, be):
        if i in keep:
            continue
        p = paras[i]
        if p._p.find('.//w:sectPr', _NS) is not None:
            continue
        text = (p.text or "").strip()
        if any(kw in text for kw in _keep_kw):
            continue
        if p._p.find('.//w:numPr', _NS) is not None and len(text) > 5:
            continue
        for r in p.runs:
            r.text = ""

    # 删除正文区域的示例表格
    body_elem = doc.element.body
    tables_rm = []
    pc = 0
    for elem in body_elem:
        tag = elem.tag.split('}')[-1]
        if tag == 'p':
            pc += 1
        elif tag == 'tbl' and bs <= pc <= be:
            tables_rm.append(elem)
    for tbl in tables_rm:
        body_elem.remove(tbl)

    # 替换样本文本
    def _replace(para, text):
        if para.runs:
            para.runs[0].text = text
            for r in para.runs[1:]:
                r.text = ""

    paras[h1_idx].paragraph_format.page_break_before = True
    _replace(paras[h1_idx], "{{ ch.title }}")
    _replace(paras[body_idx], "{{ para }}")

    # 插入控制标签的辅助函数
    def _mk_para(text):
        p = OxmlElement('w:p')
        r = OxmlElement('w:r')
        t = OxmlElement('w:t')
        t.set(qn('xml:space'), 'preserve')
        t.text = text
        r.append(t)
        p.append(r)
        return p

    h1_p = paras[h1_idx]._p
    body_p = paras[body_idx]._p

    # 确保 body 在 h1 后面
    if body_p is not h1_p:
        h1_p.addnext(body_p)

    # 插入循环结构：
    # {%p for ch in chapters %}
    # {{ ch.title }}                    ← H1
    # {%p for sec in ch.sections %}
    # {{ sec.title }}                   ← 新建，复制 H1 格式但改小
    # {%p for para in sec.content %}
    # {{ para }}                        ← BODY
    # {%p endfor %}
    # {%p for sub in sec.subsections %}
    # {{ sub.title }}                   ← 新建
    # {%p for p2 in sub.content %}
    # {{ p2 }}                          ← 新建，复制 BODY 格式
    # {%p endfor %}
    # {%p endfor %}
    # {%p endfor %}
    # {%p endfor %}

    # 在 H1 前插入 for ch
    h1_p.addprevious(_mk_para("{%p for ch in chapters %}"))

    # 在 H1 后插入 sec 循环
    p_for_sec = _mk_para("{%p for sec in ch.sections %}")
    h1_p.addnext(p_for_sec)

    # sec.title - 复制 body_p 格式（因为没有 H2 样本）
    import copy
    sec_title_p = copy.deepcopy(body_p)
    for t_elem in sec_title_p.findall('.//w:t', _NS):
        t_elem.text = ""
    t_elems = sec_title_p.findall('.//w:t', _NS)
    if t_elems:
        t_elems[0].text = "{{ sec.title }}"
    p_for_sec.addnext(sec_title_p)

    # for para in sec.content
    p_for_para = _mk_para("{%p for para in sec.content %}")
    sec_title_p.addnext(p_for_para)

    # body_p ({{ para }}) 已经在正确位置，移到 for para 后面
    p_for_para.addnext(body_p)

    # endfor content
    p_endfor1 = _mk_para("{%p endfor %}")
    body_p.addnext(p_endfor1)

    # for sub in sec.subsections
    p_for_sub = _mk_para("{%p for sub in sec.subsections %}")
    p_endfor1.addnext(p_for_sub)

    # sub.title
    sub_title_p = copy.deepcopy(body_p)
    for t_elem in sub_title_p.findall('.//w:t', _NS):
        t_elem.text = ""
    t_elems = sub_title_p.findall('.//w:t', _NS)
    if t_elems:
        t_elems[0].text = "{{ sub.title }}"
    p_for_sub.addnext(sub_title_p)

    # for p2 in sub.content
    p_for_p2 = _mk_para("{%p for p2 in sub.content %}")
    sub_title_p.addnext(p_for_p2)

    # {{ p2 }}
    p2_p = copy.deepcopy(body_p)
    for t_elem in p2_p.findall('.//w:t', _NS):
        t_elem.text = ""
    t_elems = p2_p.findall('.//w:t', _NS)
    if t_elems:
        t_elems[0].text = "{{ p2 }}"
    p_for_p2.addnext(p2_p)

    # endfor sub.content
    p_endfor2 = _mk_para("{%p endfor %}")
    p2_p.addnext(p_endfor2)

    # endfor subsections
    p_endfor3 = _mk_para("{%p endfor %}")
    p_endfor2.addnext(p_endfor3)

    # endfor sections
    p_endfor4 = _mk_para("{%p endfor %}")
    p_endfor3.addnext(p_endfor4)

    # endfor chapters
    p_endfor5 = _mk_para("{%p endfor %}")
    p_endfor4.addnext(p_endfor5)

    doc.save(doc_path)
    print(f"  正文循环已设置: {doc_path}")


def make(src_path, out_path):
    out_dir = os.path.dirname(out_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    doc = Document(src_path)

    # ========== Step 1: 封面 ==========
    cover_cell = doc.tables[0].cell(0, 0)
    cps = cover_cell.paragraphs

    # cp[10]: 题目
    _replace_cover_field(cps[10], "目：", "{{ title_zh }}")
    # 清空题目第二行（cp[11] 可能是续行）
    for r in cps[11].runs:
        r.text = ""

    # cp[12]: 姓名 + 学号
    _replace_cover_field(cps[12], "名：", "{{ name }}")
    _replace_cover_field(cps[12], "号：", "{{ student_id }}")

    # cp[14]: 学院 + 专业
    _replace_cover_field(cps[14], "院", "{{ college }}")
    _replace_cover_field(cps[14], "业", "{{ major }}")

    # cp[16]: 指导教师 + 职称
    _replace_cover_field(cps[16], "教师：", "{{ advisor }}")
    _replace_cover_field(cps[16], "称：", "{{ advisor_title }}")

    # cp[23]: 日期
    if cps[23].runs:
        cps[23].runs[0].text = "{{ year }}年  {{ month }}月  {{ day }}日"
        for r in cps[23].runs[1:]:
            r.text = ""

    print("  Step 1: 封面")

    # ========== Step 2: 中文摘要 ==========
    # p[2]: 论文题目
    p2 = doc.paragraphs[2]
    if p2.runs:
        p2.runs[0].text = "{{ title_zh }}"
        for r in p2.runs[1:]:
            r.text = ""

    # p[4]: "摘  要" 标题 - 清掉格式说明
    p4 = doc.paragraphs[4]
    for r in p4.runs:
        if "号" in r.text or "黑体" in r.text:
            r.text = ""

    # p[6]: 摘要正文
    p6 = doc.paragraphs[6]
    if p6.runs:
        p6.runs[0].text = "{{ abstract_zh }}"
        for r in p6.runs[1:]:
            r.text = ""
    # 清空摘要格式说明段落 p[7]-p[13]
    for i in range(7, 14):
        for r in doc.paragraphs[i].runs:
            r.text = ""

    # p[14]: 关键词
    p14 = doc.paragraphs[14]
    if p14.runs:
        p14.runs[0].text = "关键词："
        if len(p14.runs) > 1:
            p14.runs[1].text = "{{ keywords_zh }}"
        for r in p14.runs[2:]:
            r.text = ""

    print("  Step 2: 中文摘要")

    # ========== Step 3: 英文摘要 ==========
    # p[17]: 英文题目
    p17 = doc.paragraphs[17]
    if p17.runs:
        p17.runs[0].text = "{{ title_en }}"
        for r in p17.runs[1:]:
            r.text = ""

    # p[19]: ABSTRACT 标题 - 清掉说明
    p19 = doc.paragraphs[19]
    for r in p19.runs:
        if "号" in r.text or "Roman" in r.text or "加粗" in r.text:
            r.text = ""

    # p[21]: 英文摘要正文
    p21 = doc.paragraphs[21]
    if p21.runs:
        p21.runs[0].text = "{{ abstract_en }}"
        for r in p21.runs[1:]:
            r.text = ""
    # 清空英文摘要说明 p[22]-p[24]
    for i in range(22, 25):
        for r in doc.paragraphs[i].runs:
            r.text = ""

    # p[25]: KEY WORDS
    p25 = doc.paragraphs[25]
    if p25.runs:
        p25.runs[0].text = "KEY WORDS: "
        if len(p25.runs) > 1:
            p25.runs[1].text = "{{ keywords_en }}"
        for r in p25.runs[2:]:
            r.text = ""

    print("  Step 3: 英文摘要")

    # ========== Step 4: 目录 - 只保留第一种（农理工），删除后两种 ==========
    # 第一种目录: p[29]-p[45]（保留，清掉标题里的说明文字）
    p29 = doc.paragraphs[29]
    for r in p29.runs:
        if "（" in r.text or "可参考" in r.text:
            r.text = ""

    # 第二种目录: p[49]-p[65]（毕业设计）-> 清空
    # 第三种目录: p[68]-p[84]（经管社科）-> 清空
    for i in range(46, 86):
        for r in doc.paragraphs[i].runs:
            r.text = ""

    print("  Step 4: 目录（保留农理工类）")

    # ========== Step 5: 正文区域格式说明清理 ==========
    # Heading 1 标题段落：删除格式说明 run，保留标题文字
    for i in [88, 99, 135, 143, 175, 213]:
        if i >= len(doc.paragraphs):
            continue
        p = doc.paragraphs[i]
        # 先拼出完整文本判断，再逐 run 清理
        full = p.text or ""
        for r in p.runs:
            t = r.text
            # 删掉独立的括号和格式说明 run
            if t.strip() in ("（", "）", "（正文）"):
                r.text = ""
            elif any(kw in t for kw in
                     ["号", "黑体", "加粗", "Roman", "Times"]):
                r.text = ""
            # "附录名称" → "附录"
            if "名称" in t:
                r.text = t.replace("名称", "")

    # 清空正文区域的格式说明段落（非标题非样本）
    heading_indices = {88, 99, 135, 143, 175, 213, 219}
    for i in range(89, 145):
        if i in heading_indices:
            continue
        p = doc.paragraphs[i]
        style = p.style.name if p.style else ""
        if style == "Heading 1":
            continue
        text = (p.text or "").strip()
        # 保留样本段落：表X-1、图X-1、(X-1) 等
        if text and ("表X" in text or "图X" in text or "（X-" in text
                     or "续表" in text):
            continue
        # 清掉说明文字段落
        if any(kw in text for kw in
               ["号", "磅", "宋体", "黑体", "加粗", "行间距",
                "居中", "居左", "缩进", "标点", "参考模板",
                "文献综述", "实验", "结论是对", "结论要严格",
                "展望或建议", "人文社", "最后一章"]):
            for r in p.runs:
                r.text = ""

    # 清空参考文献格式说明和示例 p[145]-p[172]，保留 p[150] 作为样本
    for i in range(145, 173):
        if i == 150:
            continue  # 保留第一条参考文献示例作为格式样本
        for r in doc.paragraphs[i].runs:
            r.text = ""

    # 清空附录/学术成果/致谢的说明段落
    for i in range(176, 225):
        if i >= len(doc.paragraphs) or i in heading_indices:
            continue
        text = (doc.paragraphs[i].text or "").strip()
        if any(kw in text for kw in
               ["号", "磅", "宋体", "黑体", "行间距", "致谢",
                "字数", "感谢"]):
            for r in doc.paragraphs[i].runs:
                r.text = ""

    print("  Step 5: 清理格式说明")

    # 保存中间结果
    doc.save(out_path)

    # ========== Step 6: 正文 Jinja2 循环 ==========
    # 吉林农大模板没有 H2/H3 样本，手动设置循环结构
    _setup_jlau_body(out_path)
    print("  Step 6: 正文循环")

    # ========== Step 7: 参考文献 + 致谢 ==========
    doc = Document(out_path)
    refs_done = False
    for i, p in enumerate(doc.paragraphs):
        text = (p.text or "").strip()
        if text == "参考文献" and i > 60 and not refs_done:
            # 找参考文献标题后第一个有 runs 的段落作为样本
            for j in range(i + 1, min(i + 20, len(doc.paragraphs))):
                pj = doc.paragraphs[j]
                if pj.runs:
                    # 用这个段落做参考文献模板
                    pj.runs[0].text = "{{ ref }}"
                    for r in pj.runs[1:]:
                        r.text = ""
                    # 在它前面插 for 循环
                    from editor import TemplateEditor
                    ed_p = pj._p
                    from docx.oxml import OxmlElement
                    from docx.oxml.ns import qn as _qn
                    for_p = OxmlElement('w:p')
                    for_r = OxmlElement('w:r')
                    for_t = OxmlElement('w:t')
                    for_t.set(_qn('xml:space'), 'preserve')
                    for_t.text = "{%p for ref in references %}"
                    for_r.append(for_t)
                    for_p.append(for_r)
                    ed_p.addprevious(for_p)
                    # 在它后面插 endfor
                    end_p = OxmlElement('w:p')
                    end_r = OxmlElement('w:r')
                    end_t = OxmlElement('w:t')
                    end_t.set(_qn('xml:space'), 'preserve')
                    end_t.text = "{%p endfor %}"
                    end_r.append(end_t)
                    end_p.append(end_r)
                    ed_p.addnext(end_p)
                    refs_done = True
                    break
            if not refs_done:
                # 没有非空段落，尝试 refs_maker
                setup_refs_template(doc, i)
                refs_done = True

        if text in ("致  谢", "致谢"):
            for j in range(i + 1, min(i + 5, len(doc.paragraphs))):
                pt = (doc.paragraphs[j].text or "").strip()
                if pt or doc.paragraphs[j].runs:
                    if doc.paragraphs[j].runs:
                        doc.paragraphs[j].runs[0].text = \
                            "    {{ acknowledgement }}"
                        for r in doc.paragraphs[j].runs[1:]:
                            r.text = ""
                    break
    doc.save(out_path)
    print("  Step 7: 参考文献/致谢")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python make.py <原始模板.docx> [输出路径]")
        sys.exit(1)
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "template.docx"
    print(f"制作模板: {src} -> {out}")
    make(src, out)
    print(f"完成: {out}")
