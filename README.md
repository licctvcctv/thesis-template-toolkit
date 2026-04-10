# 论文模板自动化工具

将任意学校的毕业论文 Word 模板自动转换为可填充模板，然后用数据生成论文。

## 项目结构

```
thesis-template-toolkit/
├── scanner/              ← 通用：文档扫描器
├── editor.py             ← 通用：run 级文本替换
├── body_maker.py         ← 通用：正文 Jinja2 循环设置
├── refs_maker.py         ← 通用：参考文献循环设置
├── builder.py            ← 通用：内容构建器
├── generate.py           ← 通用：论文生成器
│
└── templates/            ← 各学校模板
    └── shou/             ← 上海海洋大学
        ├── make.py           制作模板的脚本
        ├── template.docx     制作好的模板（生成后）
        └── example_data.json 示例数据
```

## 使用流程

### 1. 制作模板（每个学校做一次）

```bash
cd templates/shou
python make.py ../../原始模板.docx template.docx
```

### 2. 生成论文（每次写论文时）

```bash
python generate.py templates/shou/template.docx data.json output.docx
```

## 添加新学校

1. 创建 `templates/<学校名>/` 目录
2. 用 scanner 扫描原始模板，确定封面字段位置
3. 写 `make.py`（约 50-80 行，只需指定封面 run 替换位置）
4. 运行 `make.py` 生成模板

正文循环、参考文献、致谢等由通用模块自动处理。

## 核心原则

- **只换文字不换格式** — 所有样式从原始模板继承
- **Jinja2 循环** — 正文/参考文献通过模板循环生成，不用 subdoc
- **渐进式扫描** — scanner 粗扫定位，细扫确认 run 位置
