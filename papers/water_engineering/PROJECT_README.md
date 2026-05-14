# 汕尾电厂配套煤码头工程初步设计模板工程

## 文件

- 原始材料：`thesis_project/_source_materials/original_uploads/water_engineering/`
- 结构报告：`thesis_project/_source_materials/diagnostics/water_engineering/`
- Word 模板：`thesis_project/templates/water_engineering/template.docx`
- 内容 JSON：`thesis_project/papers/water_engineering/content/`
- 构建脚本：`thesis_project/papers/water_engineering/build.py`
- 成品：`thesis_project/papers/water_engineering/汕尾电厂配套煤码头工程初步设计_毕业设计说明书.docx`

## 生成

```bash
/Users/a136/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 thesis_project/papers/water_engineering/scripts/make_template.py
/Users/a136/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 thesis_project/papers/water_engineering/build.py
```

当前工程以 `2026本科毕业设计.docx` 为学校格式母版，任务书和开题报告为身份与设计条件来源，正文从 `content/chapters.json` 生成，参考文献从 `content/references.json` 生成。
