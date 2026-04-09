# 论文模板自动化工具 (Thesis Template Skill)

将任意学校的毕业论文 Word 模板自动转换为 docxtpl 可填充模板。

## 核心理念

**只换文字，不碰格式。** 所有样式从原始模板继承，零硬编码。

## 架构

```
原始论文模板 .docx
      ↓
scanner/         ← 扫描器（只看，不改）
  structure.py   - 识别文档分区（封面/摘要/正文/致谢等）
  paragraphs.py  - 提取段落和 run 级详细信息
  report.py      - 生成 AI 可读的扫描报告
      ↓
AI 决策           ← AI 看扫描报告，决定哪些 run 要替换成什么
      ↓
editor.py        ← 编辑器（只改 run.text，不碰格式）
      ↓
docxtpl 模板 .docx
      ↓
builder.py       ← 内容构建器（章节/参考文献/表格/图片）
generate.py      ← 填充数据，生成最终论文
```

## 使用流程

### 1. 扫描模板
```python
from scanner import scan_structure, scan_paragraphs, generate_report

# 扫描整体结构
structure = scan_structure("学校论文模板.docx")

# 扫描特定区域的段落详情
paras = scan_paragraphs("学校论文模板.docx", start=0, end=30, detail=True)

# 生成报告（给 AI 看）
report = generate_report(structure, paras)
print(report)
```

### 2. AI 决策后，执行替换
```python
from editor import TemplateEditor

editor = TemplateEditor("学校论文模板.docx")

# 封面字段
editor.replace_run(para=10, run=3, text="{{ name }}")
editor.replace_run(para=11, run=1, text="{{ student_id }}")

# 摘要
editor.replace_run(para=39, run=0, text="    {{ abstract_zh }}")
editor.clear_runs(para=39, runs=[1, 2, 3, 4])

# 正文区域：保留样本段落格式，插入 Jinja2 循环
editor.insert_before(para=111, text="{%p for ch in chapters %}")
editor.replace_run(para=111, run=3, text="{{ ch.title }}")
# ...

editor.save("thesis_template.docx")
```

### 3. 填充数据生成论文
```python
from docxtpl import DocxTemplate

doc = DocxTemplate("thesis_template.docx")
context = {
    "name": "张三",
    "abstract_zh": "本文研究了...",
    "chapters": [...],
}
doc.render(context)
doc.save("我的毕业论文.docx")
```

## 文件说明

| 文件 | 用途 | 行数 |
|------|------|------|
| scanner/__init__.py | 扫描器入口 | ~10 |
| scanner/structure.py | 文档分区识别 | ~100 |
| scanner/paragraphs.py | 段落/run 级扫描 | ~120 |
| scanner/report.py | 报告生成 | ~80 |
| editor.py | 模板编辑器（只改文字） | ~90 |
| builder.py | 内容构建器 | ~200 |
| generate.py | 论文生成入口 | ~50 |

## 设计原则

1. **只换文字不换格式** - editor 只修改 run.text
2. **AI 驱动决策** - scanner 提供信息，AI 决定改什么
3. **模板继承优先** - 正文用 Jinja2 循环，格式从模板继承
4. **通用性** - 不针对特定学校，适配 99% 的论文模板
