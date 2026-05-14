# 基于Spark的豆瓣影视数据分析系统的设计与实现

本目录是南阳理工学院模板下的豆瓣影视数据分析系统论文材料目录，和此前混入的另一学校版本分开维护。论文题目统一为“基于Spark的豆瓣影视数据分析系统的设计与实现”。

## 目录结构

```text
douban-nylg/
├── build.py
├── 基于Spark的豆瓣影视数据分析系统的设计与实现_论文初稿.docx
├── content/
│   ├── meta.json
│   ├── chapters.json
│   ├── figures.json
│   ├── tables.json
│   ├── code_blocks.json
│   ├── references.json
│   └── toc_pages.json
├── data/
│   ├── douban_movies.xlsx
│   ├── experiment_results.json
│   └── experiment_results_improved.json
├── images/
│   ├── final_figures/
│   ├── imagegen/
│   ├── system_screenshots/
│   └── analysis_diagrams/
└── render_check/
    ├── page-*.png
    └── 基于Spark的豆瓣影视数据分析系统的设计与实现_论文初稿.pdf
```

## 构建说明

`build.py` 使用项目内的南阳理工模板：

```text
/Users/a136/vs/45425/thesis_project/templates/nylg/template.docx
```

执行下面命令可重新生成论文：

```bash
python3 /Users/a136/vs/45425/thesis_project/papers/douban-nylg/build.py
```

## 本次整理

- 将南阳理工豆瓣论文材料集中到当前项目的 `thesis_project/papers/douban-nylg/`。
- 保留旧的 `thesis_project/papers/douban/` 目录不动，避免继续混入另一篇豆瓣论文。
- 将论文内容从 `build.py` 迁移到 `content/*.json`，构建脚本只负责读取 JSON、套模板、插入图片/表格/代码块和生成 DOCX。
- 按教师意见补充系统用例分析、用例说明表、三大功能模块设计、系统流程设计、数据库概念结构与物理结构、测试用例表。
- 第五章按具体功能截图拆分为独立小节，统一为“文字介绍+截图+代码”的写法。
- 参考文献更新为 20 条，其中包含 5 条外文文献，并在正文中使用上标引用。
- 按教师意见删除 1.3 技术路线图，第二章不再放置图，只保留后文确实使用的技术概述。
- 新增第 4 章分析结果、推荐记录实体属性图，补齐五个实体的概念结构和物理表设计。
- 架构图、流程图、实体属性图和 E-R 图均来自 ImageGen，未使用 Python 生成或修改图片。
