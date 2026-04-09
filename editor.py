"""
模板编辑器 - 执行 AI 决定的替换指令。

核心原则：只改 run.text，不碰任何格式属性。

用法（被 AI 调用）：
    from editor import TemplateEditor
    editor = TemplateEditor("原始模板.docx")

    # AI 决定的替换指令
    editor.replace_run(para=10, run=3, text="{{ name }}")
    editor.clear_runs(para=10, runs=[4, 5])
    editor.clear_para(para=39)

    # 插入 Jinja2 控制段落（用于循环）
    editor.insert_before(para=111, text="{%p for ch in chapters %}")

    editor.save("thesis_template.docx")
"""
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


class TemplateEditor:
    """模板编辑器 - 精确执行替换指令"""

    def __init__(self, doc_path):
        self.doc = Document(doc_path)
        self.paras = self.doc.paragraphs
        self._log = []

    def replace_run(self, para, run, text):
        """替换指定 run 的文本（保留格式）"""
        try:
            self.paras[para].runs[run].text = text
            self._log.append(f"OK [{para}].run[{run}] → '{text[:30]}'")
        except (IndexError, Exception) as e:
            self._log.append(f"ERR [{para}].run[{run}]: {e}")

    def clear_runs(self, para, runs):
        """清空指定 run 列表的文本"""
        for r in runs:
            self.replace_run(para, r, "")

    def clear_para(self, para):
        """清空段落所有 run 文本（保留段落结构）"""
        try:
            for r in self.paras[para].runs:
                r.text = ""
            self._log.append(f"OK [{para}] 段落已清空")
        except Exception as e:
            self._log.append(f"ERR [{para}]: {e}")

    def insert_before(self, para, text):
        """在指定段落前插入新段落"""
        new_p = self._make_para(text)
        self.paras[para]._p.addprevious(new_p)
        self._log.append(f"OK 在[{para}]前插入 '{text[:30]}'")

    def insert_after(self, para, text):
        """在指定段落后插入新段落"""
        new_p = self._make_para(text)
        self.paras[para]._p.addnext(new_p)
        self._log.append(f"OK 在[{para}]后插入 '{text[:30]}'")

    def remove_sectPr(self, para):
        """移除段落中的分节符（解决 LibreOffice 渲染问题）"""
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        sect = self.paras[para]._p.find('.//w:sectPr', ns)
        if sect is not None:
            sect.getparent().remove(sect)
            self._log.append(f"OK [{para}] sectPr 已移除")
        else:
            self._log.append(f"SKIP [{para}] 无 sectPr")

    def save(self, output_path):
        """保存模板"""
        self.doc.save(output_path)
        self._log.append(f"保存: {output_path}")

    def get_log(self):
        """获取操作日志"""
        return "\n".join(self._log)

    @staticmethod
    def _make_para(text):
        """创建一个简单段落元素"""
        p = OxmlElement('w:p')
        r = OxmlElement('w:r')
        t = OxmlElement('w:t')
        t.set(qn('xml:space'), 'preserve')
        t.text = text
        r.append(t)
        p.append(r)
        return p
