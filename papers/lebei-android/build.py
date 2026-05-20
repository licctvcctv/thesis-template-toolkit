"""
基于安卓的乐背单词APP的设计与实现论文组装器。

内容来源：
- content/meta.json
- content/chapters.json
- content/figures.json
- content/tables.json
- content/code_blocks.json
- content/references.json
- content/toc_pages.json（可选，渲染后二次校正目录页码）

用法:
  cd /Users/a136/vs/45425/thesis_project/papers/lebei-android
  python build.py
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from functools import lru_cache
from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from lxml import etree


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CONTENT = HERE / "content"
TEMPLATE = ROOT / "templates" / "bistu_2026" / "template.docx"
DEFAULT_OUTPUT = HERE / "论文_软工2102_2021011175_刘子安_基于安卓的乐背单词APP的设计与实现.docx"


def load_json(name: str, default=None):
    path = CONTENT / name
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def split_paras(value, count=4):
    if isinstance(value, list):
        parts = [str(x).strip() for x in value if str(x).strip()]
    else:
        parts = [p.strip() for p in str(value or "").splitlines() if p.strip()]
    parts = parts[:count]
    while len(parts) < count:
        parts.append("")
    return parts


def fmt_run(run, size=12, bold=None, east="宋体", ascii_font="Times New Roman"):
    run.font.size = Pt(size)
    run.font.name = ascii_font
    r_pr = run._element.get_or_add_rPr()
    r_fonts = r_pr.get_or_add_rFonts()
    r_fonts.set(qn("w:eastAsia"), east)
    r_fonts.set(qn("w:ascii"), ascii_font)
    r_fonts.set(qn("w:hAnsi"), ascii_font)
    if bold is not None:
        run.bold = bold


def replace_runs(paragraph, mapping):
    for run in paragraph.runs:
        text = run.text
        for key, value in mapping.items():
            text = text.replace(key, str(value))
        run.text = text


def replace_doc_placeholders(doc, mapping):
    for paragraph in doc.paragraphs:
        replace_runs(paragraph, mapping)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    replace_runs(paragraph, mapping)
    for section in doc.sections:
        for part in (section.header, section.footer):
            for paragraph in part.paragraphs:
                replace_runs(paragraph, mapping)


def set_paragraph_text(paragraph, text, size=12, bold=None, east="宋体"):
    paragraph.clear()
    if text:
        run = paragraph.add_run(str(text))
        fmt_run(run, size=size, bold=bold, east=east)
        return run
    return None


def delete_paragraph(paragraph):
    element = paragraph._p
    parent = element.getparent()
    if parent is not None:
        parent.remove(element)


def insert_paragraph_after(paragraph, text="", style=None):
    new_p = OxmlElement("w:p")
    paragraph._p.addnext(new_p)
    from docx.text.paragraph import Paragraph

    new_para = Paragraph(new_p, paragraph._parent)
    if style:
        try:
            new_para.style = style
        except Exception:
            pass
    if text:
        new_para.add_run(text)
    return new_para


def strip_heading_number(title: str) -> str:
    text = str(title).strip()
    text = re.sub(r"^第[一二三四五六七八九十0-9]+章\s*", "", text)
    text = re.sub(r"^\d+(?:\.\d+)*\s*", "", text)
    return text.strip() or str(title).strip()


def chinese_number(value: int) -> str:
    digits = "零一二三四五六七八九"
    if value <= 10:
        return "十" if value == 10 else digits[value]
    if value < 20:
        return "十" + digits[value % 10]
    tens, ones = divmod(value, 10)
    return digits[tens] + "十" + (digits[ones] if ones else "")


def chapter_title(title: str, index: int | None = None) -> str:
    raw = str(title).strip()
    match = re.match(r"^第([0-9一二三四五六七八九十]+)章\s*(.*)$", raw)
    if match:
        number, rest = match.groups()
        if number.isdigit():
            number = chinese_number(int(number))
        return f"第{number}章 {rest.strip()}".strip()
    if index is not None:
        return f"第{chinese_number(index)}章 {strip_heading_number(raw)}"
    return raw


def visible_heading_title(title: str, level: int) -> str:
    if level == 1:
        return chapter_title(title)
    return str(title).strip()


def add_heading(doc, title, level=1, page_break=False):
    style = {1: "Heading 1", 2: "Heading 2", 3: "Heading 3"}.get(level, "Heading 3")
    paragraph = doc.add_paragraph(style=style)
    paragraph.paragraph_format.page_break_before = bool(page_break)
    paragraph.paragraph_format.keep_with_next = True
    paragraph.paragraph_format.line_spacing = Pt(18)
    paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.space_after = Pt(6 if level == 1 else 0)
    text = visible_heading_title(title, level)
    if level == 1:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = paragraph.add_run(text)
        fmt_run(run, size=16, bold=True, east="黑体")
    elif level == 2:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        paragraph.paragraph_format.space_before = Pt(6)
        run = paragraph.add_run(text)
        fmt_run(run, size=12, bold=True, east="宋体")
    else:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        paragraph.paragraph_format.space_before = Pt(3)
        run = paragraph.add_run(text)
        fmt_run(run, size=10.5, bold=True, east="宋体")
    return paragraph


def add_body_text(doc, text):
    paragraph = doc.add_paragraph(style="Body Text")
    paragraph.paragraph_format.first_line_indent = Cm(0.74)
    paragraph.paragraph_format.line_spacing = Pt(18)
    paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.space_after = Pt(0)
    parts = re.split(r"(\[[0-9,，\-—]+\])", str(text))
    for part in parts:
        if not part:
            continue
        run = paragraph.add_run(part)
        fmt_run(run, size=10.5)
        if re.fullmatch(r"\[[0-9,，\-—]+\]", part):
            run.font.superscript = True
    return paragraph


def set_cell_border(cell, top=None, bottom=None, left=None, right=None):
    tc_pr = cell._tc.get_or_add_tcPr()
    old = tc_pr.first_child_found_in("w:tcBorders")
    if old is not None:
        tc_pr.remove(old)
    borders = OxmlElement("w:tcBorders")
    for edge, val in (("top", top), ("bottom", bottom), ("left", left), ("right", right)):
        if val is None:
            continue
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), val.get("val", "single"))
        el.set(qn("w:sz"), val.get("sz", "4"))
        el.set(qn("w:color"), val.get("color", "000000"))
        el.set(qn("w:space"), "0")
        borders.append(el)
    tc_pr.append(borders)


def set_cell_margins(cell, top=80, bottom=80, left=110, right=110):
    tc_pr = cell._tc.get_or_add_tcPr()
    old = tc_pr.first_child_found_in("w:tcMar")
    if old is not None:
        tc_pr.remove(old)
    margins = OxmlElement("w:tcMar")
    for edge, value in (("top", top), ("bottom", bottom), ("left", left), ("right", right)):
        node = OxmlElement(f"w:{edge}")
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")
        margins.append(node)
    tc_pr.append(margins)


def set_table_grid(table, widths_cm):
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    layout = tbl_pr.find(qn("w:tblLayout"))
    if layout is None:
        layout = OxmlElement("w:tblLayout")
        tbl_pr.append(layout)
    layout.set(qn("w:type"), "fixed")
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(int(sum(widths_cm) * 567)))
    tbl_w.set(qn("w:type"), "dxa")
    grid = tbl.tblGrid
    if grid is not None:
        tbl.remove(grid)
    grid = OxmlElement("w:tblGrid")
    for width in widths_cm:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(int(width * 567)))
        grid.append(col)
    tbl.insert(1, grid)


def set_row_cant_split(row):
    tr_pr = row._tr.get_or_add_trPr()
    if tr_pr.find(qn("w:cantSplit")) is None:
        tr_pr.append(OxmlElement("w:cantSplit"))


def set_row_repeat_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    if tr_pr.find(qn("w:tblHeader")) is None:
        tr_pr.append(OxmlElement("w:tblHeader"))


def add_table(doc, table_data):
    caption = table_data.get("caption", "")
    headers = table_data.get("headers", [])
    rows = table_data.get("rows", [])
    if not headers:
        return
    if table_data.get("page_break_before"):
        doc.add_page_break()
    if caption:
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.keep_with_next = True
        p_cap.paragraph_format.line_spacing = Pt(18)
        p_cap.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
        p_cap.paragraph_format.space_before = Pt(3)
        p_cap.paragraph_format.space_after = Pt(0)
        run = p_cap.add_run(caption)
        fmt_run(run, size=10.5, bold=True)

    widths = table_data.get("col_widths") or [13.5 / len(headers)] * len(headers)
    total = sum(widths)
    if total > 14.2:
        widths = [w * 14.2 / total for w in widths]
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    table.autofit = False
    set_table_grid(table, widths)
    thick = {"val": "single", "sz": "12", "color": "000000"}
    thin = {"val": "single", "sz": "4", "color": "000000"}
    none = {"val": "nil"}
    for r_idx, row in enumerate([headers] + rows):
        set_row_cant_split(table.rows[r_idx])
        if r_idx == 0:
            set_row_repeat_header(table.rows[r_idx])
        for c_idx, value in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_border(
                cell,
                top=thick if r_idx == 0 else none,
                bottom=thin if r_idx == 0 else (thick if r_idx == len(rows) else none),
                left=none,
                right=none,
            )
            paragraph = cell.paragraphs[0]
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx == 0 or len(str(value)) <= 12 else WD_ALIGN_PARAGRAPH.LEFT
            paragraph.paragraph_format.line_spacing = Pt(13.5)
            paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
            paragraph.paragraph_format.space_before = Pt(0)
            paragraph.paragraph_format.space_after = Pt(0)
            set_cell_margins(cell, top=45, bottom=45, left=80, right=80)
            set_paragraph_text(paragraph, value, size=9 if len(headers) >= 4 else 9.5, bold=(r_idx == 0))
    if table_data.get("page_break_after"):
        doc.add_page_break()
        return
    spacer = doc.add_paragraph()
    spacer.paragraph_format.line_spacing = Pt(6)
    spacer.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    spacer.paragraph_format.space_before = Pt(0)
    spacer.paragraph_format.space_after = Pt(0)


def add_image(doc, image_path, caption="", width_cm=12.0, page_break_before=False, page_break_after=False):
    path = Path(image_path)
    if not path.is_absolute():
        path = HERE / image_path
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.page_break_before = bool(page_break_before)
    p_img.paragraph_format.keep_with_next = True
    p_img.paragraph_format.space_before = Pt(0)
    p_img.paragraph_format.space_after = Pt(0)
    run = p_img.add_run()
    if path.exists():
        run.add_picture(str(path), width=Cm(width_cm))
    else:
        run.text = f"[图片缺失：{image_path}]"
        fmt_run(run, size=10.5)
    if caption:
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.keep_together = True
        p_cap.paragraph_format.line_spacing = Pt(18)
        p_cap.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
        p_cap.paragraph_format.space_before = Pt(0)
        p_cap.paragraph_format.space_after = Pt(3)
        run_cap = p_cap.add_run(caption)
        fmt_run(run_cap, size=9, bold=True)
    if page_break_after:
        doc.add_page_break()


def add_code(doc, code, caption=""):
    if caption:
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p_cap.add_run(caption)
        fmt_run(run, size=10.5, bold=True)
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.5)
    p.paragraph_format.line_spacing = Pt(12)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    for line in str(code).strip("\n").splitlines():
        run = p.add_run(line + "\n")
        fmt_run(run, size=8, east="宋体", ascii_font="Consolas")


@lru_cache(maxsize=64)
def latex_to_omml(latex: str) -> str:
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise RuntimeError("Pandoc is required to convert formula LaTeX to Word OMML")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        md_path = tmp_path / "formula.md"
        docx_path = tmp_path / "formula.docx"
        md_path.write_text(f"$$\n{latex}\n$$\n", encoding="utf-8")
        result = subprocess.run(
            [pandoc, "-f", "markdown+tex_math_dollars", str(md_path), "-o", str(docx_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Pandoc formula conversion failed: {result.stderr.strip()}")
        with zipfile.ZipFile(docx_path, "r") as zf:
            xml = zf.read("word/document.xml")
        root = etree.fromstring(xml)
        ns = {"m": "http://schemas.openxmlformats.org/officeDocument/2006/math"}
        nodes = root.xpath(".//m:oMath", namespaces=ns)
        if not nodes:
            raise RuntimeError(f"No OMML math element generated for formula: {latex}")
        return etree.tostring(nodes[0], encoding="unicode")


def add_formula(doc, formula):
    latex = formula.get("latex")
    number = formula.get("number", "")
    if not latex:
        raise ValueError(f"Formula block missing latex source: {formula.get('text', '')}")
    paragraph = doc.add_paragraph(style="Body Text")
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    paragraph.paragraph_format.first_line_indent = Cm(0)
    paragraph.paragraph_format.line_spacing = Pt(18)
    paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    paragraph.paragraph_format.space_before = Pt(3)
    paragraph.paragraph_format.space_after = Pt(3)
    paragraph.paragraph_format.tab_stops.add_tab_stop(Cm(7.2), WD_TAB_ALIGNMENT.CENTER)
    paragraph.paragraph_format.tab_stops.add_tab_stop(Cm(15.0), WD_TAB_ALIGNMENT.RIGHT)
    tab = paragraph.add_run("\t")
    fmt_run(tab, size=10.5)
    paragraph._p.append(parse_xml(latex_to_omml(str(latex))))
    number_run = paragraph.add_run(f"\t{number}" if number else "")
    fmt_run(number_run, size=10.5)


def build_blocks(doc, blocks):
    for block in blocks or []:
        if isinstance(block, str):
            add_body_text(doc, block)
        elif isinstance(block, dict):
            if block.get("type") == "formula":
                add_formula(doc, block)
            elif "text" in block:
                add_body_text(doc, block["text"])
            elif "table" in block:
                add_table(doc, block["table"])
            elif "figure" in block:
                fig = block["figure"]
                add_image(
                    doc,
                    fig["image"],
                    fig.get("caption", ""),
                    fig.get("width_cm", 12.0),
                    fig.get("page_break_before", False),
                    fig.get("page_break_after", False),
                )
            elif "image" in block:
                add_image(
                    doc,
                    block["image"],
                    block.get("caption", ""),
                    block.get("width_cm", 12.0),
                    block.get("page_break_before", False),
                    block.get("page_break_after", False),
                )
            elif "code" in block:
                add_code(doc, block["code"], block.get("caption", ""))


def build_body(doc, chapters, conclusion, acknowledgement, references):
    for ch_idx, chapter in enumerate(chapters):
        add_heading(doc, chapter["title"], level=1, page_break=(ch_idx > 0))
        build_blocks(doc, chapter.get("content", []))
        for section in chapter.get("sections", []):
            add_heading(doc, section["title"], level=2, page_break=section.get("page_break_before", False))
            build_blocks(doc, section.get("content", []))
            for subsection in section.get("subsections", []):
                add_heading(doc, subsection["title"], level=3, page_break=subsection.get("page_break_before", False))
                build_blocks(doc, subsection.get("content", []))

    if conclusion:
        p_conclusion = doc.add_paragraph(style="Heading 1")
        p_conclusion.paragraph_format.page_break_before = True
        p_conclusion.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p_conclusion.add_run("结论")
        fmt_run(run, size=16, bold=True, east="黑体")
        build_blocks(doc, [{"text": item} if isinstance(item, str) else item for item in conclusion])

    p_ack = doc.add_paragraph(style="致谢标题")
    p_ack.paragraph_format.page_break_before = True
    p_ack.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_paragraph_text(p_ack, "致谢", size=16, bold=True, east="黑体")
    for para in acknowledgement:
        add_body_text(doc, para)

    p_ref = doc.add_paragraph(style="参考文献标题")
    p_ref.paragraph_format.page_break_before = True
    p_ref.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_paragraph_text(p_ref, "参考文献", size=16, bold=True, east="黑体")
    for idx, ref in enumerate(references, 1):
        paragraph = doc.add_paragraph(style="参考文献条目")
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        paragraph.paragraph_format.first_line_indent = Cm(-0.74)
        paragraph.paragraph_format.left_indent = Cm(0.74)
        paragraph.paragraph_format.line_spacing = Pt(14)
        paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
        paragraph.paragraph_format.space_before = Pt(0)
        paragraph.paragraph_format.space_after = Pt(0)
        text = re.sub(r"^\[\d+\]\s*", "", str(ref).strip())
        run = paragraph.add_run(f"[{idx}] {text}")
        fmt_run(run, size=10.5)


def normalize_headers(doc, title: str):
    stale_tokens = ("{{ title_zh }}", "致谢", "老旧小区", "停车场收费")
    for section in doc.sections:
        for paragraph in section.header.paragraphs:
            text = paragraph.text.strip()
            if text and any(token in text for token in stale_tokens):
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                set_paragraph_text(paragraph, title, size=10.5)


def add_page_field(paragraph):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(begin)
    run._r.append(instr)
    run._r.append(separate)
    run._r.append(text)
    run._r.append(end)
    fmt_run(run, size=9)


def set_section_page_number_start(section, start=1):
    sect_pr = section._sectPr
    pg_num = sect_pr.find(qn("w:pgNumType"))
    if pg_num is None:
        pg_num = OxmlElement("w:pgNumType")
        sect_pr.append(pg_num)
    pg_num.set(qn("w:start"), str(start))
    pg_num.set(qn("w:fmt"), "decimal")


def add_body_page_footer(doc):
    if not doc.sections:
        return
    body_section = doc.sections[-1]
    body_section.footer_distance = Cm(1.75)
    set_section_page_number_start(body_section, 1)
    body_section.footer.is_linked_to_previous = False
    footer = body_section.footer
    for paragraph in list(footer.paragraphs)[1:]:
        delete_paragraph(paragraph)
    paragraph = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    paragraph.clear()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.line_spacing = Pt(12)
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.space_after = Pt(0)
    add_page_field(paragraph)


def iter_toc_entries(chapters, include_conclusion=True):
    yield ("摘要", "I", 1, "摘要")
    yield ("Abstract", "II", 1, "Abstract")
    for ch_idx, chapter in enumerate(chapters, 1):
        yield (chapter_title(chapter["title"], ch_idx), None, 1, chapter["title"])
        for sec_idx, section in enumerate(chapter.get("sections", []), 1):
            yield (f"{ch_idx}.{sec_idx} {strip_heading_number(section['title'])}", None, 2, section["title"])
            for sub_idx, subsection in enumerate(section.get("subsections", []), 1):
                yield (f"{ch_idx}.{sec_idx}.{sub_idx} {strip_heading_number(subsection['title'])}", None, 3, subsection["title"])
    if include_conclusion:
        yield ("结论", None, 1, "结论")
    yield ("致谢", None, 1, "致谢")
    yield ("参考文献", None, 1, "参考文献")


def default_toc_pages(chapters, include_conclusion=True):
    pages = {"摘要": "I", "Abstract": "II"}
    page = 1
    for entry, _, level, key in iter_toc_entries(chapters, include_conclusion):
        if key in pages:
            continue
        pages[key] = page
        if level == 1:
            page += 3
        elif level == 2:
            page += 1
    return pages


def add_toc_to_template(doc, chapters, toc_pages, include_conclusion=True):
    placeholder = None
    for paragraph in doc.paragraphs:
        if "{{ toc }}" in paragraph.text:
            placeholder = paragraph
            break
    if placeholder is None:
        return
    entries = list(iter_toc_entries(chapters, include_conclusion))
    first = True
    current = placeholder
    for title, fixed_page, level, key in entries:
        page = fixed_page if fixed_page is not None else toc_pages.get(key, toc_pages.get(title, 1))
        if first:
            paragraph = placeholder
            paragraph.clear()
            first = False
        else:
            paragraph = insert_paragraph_after(current, style=f"toc {min(level, 3)}")
        current = paragraph
        paragraph.paragraph_format.left_indent = Cm({1: 0, 2: 0.7, 3: 1.35}.get(level, 0))
        paragraph.paragraph_format.line_spacing = Pt(14)
        paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
        paragraph.paragraph_format.tab_stops.add_tab_stop(Cm(15.3), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        run = paragraph.add_run(f"{title}\t{page}")
        fmt_run(run, size=10.5, bold=(level == 1))


def remove_body_placeholder(doc):
    start = None
    for idx, paragraph in enumerate(doc.paragraphs):
        if "{{ body }}" in paragraph.text:
            start = idx
            break
    if start is None:
        return
    paragraphs = list(doc.paragraphs)
    for paragraph in reversed(paragraphs[start:]):
        delete_paragraph(paragraph)


def patch_update_fields(docx_path: Path):
    tmp = Path(str(docx_path) + ".tmp")
    with zipfile.ZipFile(docx_path, "r") as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename == "word/settings.xml":
                xml = data.decode("utf-8")
                if "w:updateFields" not in xml:
                    xml = xml.replace("</w:settings>", '<w:updateFields w:val="true"/></w:settings>')
                    data = xml.encode("utf-8")
            zout.writestr(info, data)
    tmp.replace(docx_path)


def collect_document_text(doc):
    parts = [p.text for p in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                parts.extend(p.text for p in cell.paragraphs)
    for section in doc.sections:
        for part in (section.header, section.footer):
            parts.extend(p.text for p in part.paragraphs)
    return "\n".join(parts)


def clear_cover_identity_when_blank(doc, meta):
    if str(meta.get("name", "")).strip() or str(meta.get("student_id", "")).strip():
        return
    for paragraph in doc.paragraphs:
        if "学生姓名：" not in paragraph.text:
            continue
        if paragraph.runs:
            paragraph.runs[0].text = "学生姓名：       "
            for run in paragraph.runs[1:]:
                run.text = ""
        break


def verify_output(docx_path: Path, title: str):
    doc = Document(str(docx_path))
    text = collect_document_text(doc)
    problems = []
    for token in ("{{", "}}", "__TABLE:", "__CODE:"):
        if token in text:
            problems.append(f"残留占位符 {token}")
    for old in ("老旧小区", "停车场收费", "期货", "多智能体", "鸿蒙", "HarmonyOS", "Harmony"):
        if old in text:
            problems.append(f"残留旧主题/不合规词：{old}")
    if title not in text:
        problems.append("未检测到目标论文题目")
    return problems


def iter_content_blocks(chapter):
    for block in chapter.get("content", []):
        yield block
    for section in chapter.get("sections", []):
        for block in section.get("content", []):
            yield block
        for subsection in section.get("subsections", []):
            for block in subsection.get("content", []):
                yield block


def validate_chapter_plan(chapters):
    problems = []
    if len(chapters) != 6:
        problems.append(f"论文正文应为6章，当前为{len(chapters)}章")
    for idx, chapter in enumerate(chapters[:3], 1):
        for block in iter_content_blocks(chapter):
            if isinstance(block, dict) and "table" in block:
                caption = block["table"].get("caption", "未命名表格")
                problems.append(f"第{idx}章不应出现表格：{caption}")
    return problems


def count_formula_blocks(chapters):
    count = 0
    for chapter in chapters:
        for block in iter_content_blocks(chapter):
            if isinstance(block, dict) and block.get("type") == "formula":
                count += 1
    return count


def count_docx_math_objects(docx_path: Path):
    ns = {"m": "http://schemas.openxmlformats.org/officeDocument/2006/math"}
    with zipfile.ZipFile(docx_path, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))
    return len(root.xpath(".//m:oMath", namespaces=ns))


def main():
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUTPUT
    if not TEMPLATE.exists():
        raise FileNotFoundError(f"template missing: {TEMPLATE}")

    meta = load_json("meta.json", {})
    chapters = load_json("chapters.json", [])
    conclusion = load_json("conclusion.json", [])
    acknowledgement = load_json("acknowledgement.json", [])
    references = load_json("references.json", [])
    outline_problems = validate_chapter_plan(chapters)
    if outline_problems:
        raise ValueError("章节结构校验失败：\n - " + "\n - ".join(outline_problems))
    formula_count = count_formula_blocks(chapters)

    include_conclusion = bool(conclusion)
    toc_pages = load_json("toc_pages.json", None) or default_toc_pages(chapters, include_conclusion)

    zh = split_paras(meta.get("abstract_zh"), 4)
    en = split_paras(meta.get("abstract_en"), 4)
    mapping = {f"{{{{ abstract_zh_{idx + 1} }}}}": para for idx, para in enumerate(zh)}
    mapping.update({f"{{{{ abstract_en_{idx + 1} }}}}": para for idx, para in enumerate(en)})
    for key, value in meta.items():
        if isinstance(value, (str, int, float)):
            mapping[f"{{{{ {key} }}}}"] = value
    mapping["老旧小区共享车位停车场收费系统设计"] = meta.get("title_zh", "")
    mapping["{{ toc }}"] = "{{ toc }}"
    mapping["{{ body }}"] = "{{ body }}"

    doc = Document(str(TEMPLATE))
    replace_doc_placeholders(doc, mapping)
    clear_cover_identity_when_blank(doc, meta)
    add_toc_to_template(doc, chapters, toc_pages, include_conclusion)
    remove_body_placeholder(doc)
    build_body(doc, chapters, conclusion, acknowledgement, references)
    normalize_headers(doc, meta.get("title_zh", ""))
    add_body_page_footer(doc)

    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output))
    patch_update_fields(output)
    rendered_formula_count = count_docx_math_objects(output)
    if rendered_formula_count != formula_count:
        raise ValueError(f"公式对象数量不一致：JSON={formula_count}，DOCX={rendered_formula_count}")
    problems = verify_output(output, meta.get("title_zh", ""))
    if problems:
        print("校验提醒:")
        for problem in problems:
            print(" -", problem)
    else:
        print("校验通过")
    print(f"完成: {output}")


if __name__ == "__main__":
    main()
