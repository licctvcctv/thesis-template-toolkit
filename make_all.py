"""
批量制作 3 篇论文模板。
封面/摘要: editor 精确替换 run.text
正文: body_maker 设置 Jinja2 循环（继承模板格式）
"""
import os
from editor import TemplateEditor
from scanner import scan_structure
from body_maker import setup_body_template

OUTPUT_DIR = "output"


def _common_abstract(ed, path):
    """通用摘要/关键词/致谢/参考文献替换"""
    from docx import Document
    doc = Document(path)
    paras = doc.paragraphs
    s = scan_structure(path)
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

    zh = s['parts'].get('abstract_zh', {}).get('start')
    en = s['parts'].get('abstract_en', {}).get('start')
    toc = s['parts'].get('toc', {}).get('start', 999)

    # 中文摘要
    if zh:
        upper = en or toc
        for i in range(zh + 1, upper):
            t = (paras[i].text or "").strip()
            if len(t) > 15 and "关键词" not in t:
                ed.replace_run(i, 0, "    {{ abstract_zh }}")
                for j in range(1, len(paras[i].runs)):
                    ed.replace_run(i, j, "")
                for k in range(i + 1, upper):
                    kt = (paras[k].text or "").strip()
                    if kt and "关键词" not in kt and len(kt) < 10:
                        ed.clear_para(k)
                break
        # 中文关键词
        for i in range(zh + 1, upper):
            text = paras[i].text or ""
            if "关键词：" in text or "关键词:" in text:
                after = False
                for j, r in enumerate(paras[i].runs):
                    if "：" in r.text or ":" in r.text:
                        after = True; continue
                    if after and r.text.strip():
                        ed.replace_run(i, j, "{{ keywords_zh }}")
                        for k in range(j+1, len(paras[i].runs)):
                            ed.replace_run(i, k, "")
                        break
                break

    # 英文摘要
    if en:
        upper2 = toc
        for i in range(en + 1, upper2):
            t = (paras[i].text or "").strip()
            if len(t) > 15 and "keyword" not in t.lower():
                ed.replace_run(i, 0, "    {{ abstract_en }}")
                for j in range(1, len(paras[i].runs)):
                    ed.replace_run(i, j, "")
                break
        for i in range(en + 1, upper2):
            text = paras[i].text or ""
            if "Keywords" in text or "Key words" in text:
                after = False
                for j, r in enumerate(paras[i].runs):
                    if "Keywords" in r.text or "Key words" in r.text:
                        after = True; continue
                    if after and r.text.strip():
                        ed.replace_run(i, j, "{{ keywords_en }}")
                        for k in range(j+1, len(paras[i].runs)):
                            ed.replace_run(i, k, "")
                        break
                break

    # 致谢
    ack = s['parts'].get('acknowledgement', {}).get('start')
    if ack:
        for i in range(ack + 1, min(ack + 5, len(paras))):
            if len((paras[i].text or "").strip()) > 10:
                ed.replace_run(i, 0, "    {{ acknowledgement }}")
                for j in range(1, len(paras[i].runs)):
                    ed.replace_run(i, j, "")
                break

    # 参考文献 → subdoc
    ref = s['parts'].get('references', {}).get('start')
    if ref:
        app = s['parts'].get('appendix', {}).get('start', len(paras))
        for i in range(ref + 1, min(ref + 5, len(paras))):
            t = (paras[i].text or "").strip()
            if t and len(t) > 5:
                ed.replace_run(i, 0, "{{p refs_subdoc }}")
                for j in range(1, len(paras[i].runs)):
                    ed.replace_run(i, j, "")
                for k in range(i + 1, min(app, len(paras))):
                    p = paras[k]
                    if p._p.find('.//w:sectPr', ns) is not None:
                        continue
                    for j2 in range(len(p.runs)):
                        ed.replace_run(k, j2, "")
                break


def make_A():
    """上海海洋大学"""
    path = "../副本上海海洋大学毕业论文（设计）模板.docx"
    out = f"{OUTPUT_DIR}/A_template.docx"
    # 先正文（用原始文件定位）
    setup_body_template(path, out)
    # 再封面/摘要
    ed = TemplateEditor(out)
    ed.replace_run(6, 3, "{{ title_zh }}")
    ed.replace_run(8, 4, "{{ title_en }}")
    ed.replace_run(10, 1, "学 院：{{ college }}")
    ed.replace_run(11, 0, "   班 级：{{ class_name }}")
    ed.replace_run(12, 0, "   姓 名：{{ name }}")
    ed.replace_run(13, 0, "   学 号：{{ student_id }}")
    ed.replace_run(14, 0, "指导教师：{{ advisor }}")
    ed.replace_run(16, 0, "{{ year }}年")
    ed.replace_run(16, 2, "{{ month }}月")
    _common_abstract(ed, out)
    ed.save(out)


def make_B():
    """陕西国际商贸学院"""
    path = "../附件2陕西国际商贸学院本科毕业论文（设计）撰写格式.docx"
    out = f"{OUTPUT_DIR}/B_template.docx"
    # 先正文
    setup_body_template(path, out)
    # 再封面/摘要
    ed = TemplateEditor(out)
    ed.replace_run(2, 0, "{{ 届 }}")
    ed.replace_run(6, 3, "{{ title_zh }}")
    ed.replace_run(10, 3, "{{ name }}")
    ed.clear_runs(10, [4])
    ed.replace_run(11, 1, "{{ student_id }}")
    ed.clear_runs(11, [2])
    ed.replace_run(12, 3, "{{ college }}")
    ed.clear_runs(12, [4])
    ed.replace_run(13, 3, "{{ major }}")
    ed.clear_runs(13, [4])
    ed.replace_run(14, 1, "{{ advisor_in }}  {{ advisor_in_title }}")
    ed.replace_run(15, 2, "{{ advisor_out }}")
    ed.replace_run(15, 3, "")
    ed.replace_run(15, 4, "{{ advisor_out_title }}")
    ed.replace_run(15, 5, "")
    ed.replace_run(21, 1, "{{ year }}")
    ed.replace_run(21, 2, "年{{ month }}月")
    ed.replace_run(25, 1, "{{ title_zh }}")
    ed.clear_runs(25, [2, 3])
    _common_abstract(ed, out)
    ed.save(out)


def make_C():
    """毕业设计模版2025"""
    path = "../副本附件5：毕业设计模版（2025.3.25）.docx"
    out = f"{OUTPUT_DIR}/C_template.docx"
    # 先设置正文循环（用原始文件扫描定位）
    setup_body_template(path, out)
    # 再在已设置循环的模板上做封面/摘要替换
    ed = TemplateEditor(out)
    ed.replace_run(19, 0, "{{ title_zh }}")
    ed.clear_runs(19, [1, 2, 3, 4])
    ed.replace_run(20, 0, "{{ title_en }}")
    ed.replace_run(10, 0,
        "我谨在此郑重声明：本人所写的毕业设计《{{ title_zh }}》均系本人独立完成，没有抄袭行为")
    _common_abstract(ed, out)
    ed.save(out)


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("A (上海海洋大学)...")
    make_A()
    print("B (陕西国际商贸学院)...")
    make_B()
    print("C (毕业设计模版2025)...")
    make_C()
    print(f"\n完成！模板在 {OUTPUT_DIR}/")
