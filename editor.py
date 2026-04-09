"""
模板编辑器 - 执行 AI 决定的替换指令。

核心原则：只改 run.text，不碰任何格式属性。

用法（被 AI 调用）：
    from editor import TemplateEditor
    editor = TemplateEditor("原始模板.docx")
    editor.replace_run(para=10, run=3, text="{{ name }}")
    editor.clear_runs(para=10, runs=[4, 5])
    editor.insert_before(para=111, text="{%p for ch in chapters %}")
    editor.save("thesis_template.docx")
"""
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

_WML_NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}


class TemplateEditor:

    def __init__(self, doc_path):
        self.doc = Document(doc_path)
        self._log = []

    @property
    def paras(self):
        """Always return fresh paragraph list to avoid stale refs."""
        return self.doc.paragraphs

    def replace_run(self, para, run, text):
        """Only changes run.text — preserves all formatting."""
        try:
            self.paras[para].runs[run].text = text
            self._log.append(f"OK [{para}].run[{run}]")
        except IndexError as e:
            self._log.append(f"ERR [{para}].run[{run}]: {e}")

    def clear_runs(self, para, runs):
        for r in runs:
            self.replace_run(para, r, "")

    def clear_para(self, para):
        for r in self.paras[para].runs:
            r.text = ""
        self._log.append(f"OK [{para}] cleared")

    def insert_before(self, para, text):
        self.paras[para]._p.addprevious(self._make_para(text))
        self._log.append(f"OK insert before [{para}]")

    def insert_after(self, para, text):
        self.paras[para]._p.addnext(self._make_para(text))
        self._log.append(f"OK insert after [{para}]")

    def remove_sectPr(self, para):
        sect = self.paras[para]._p.find('.//w:sectPr', _WML_NS)
        if sect is not None:
            sect.getparent().remove(sect)
            self._log.append(f"OK [{para}] sectPr removed")

    def save(self, output_path):
        self.doc.save(output_path)
        self._log.append(f"saved: {output_path}")

    def get_log(self):
        return "\n".join(self._log)

    @staticmethod
    def _make_para(text):
        p = OxmlElement('w:p')
        r = OxmlElement('w:r')
        t = OxmlElement('w:t')
        t.set(qn('xml:space'), 'preserve')
        t.text = text
        r.append(t)
        p.append(r)
        return p
