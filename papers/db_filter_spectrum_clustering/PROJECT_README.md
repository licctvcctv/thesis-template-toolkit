# 基于数据库过滤的谱图聚类算法设计

## 论文身份

- 学校：深圳北理莫斯科大学
- 题目：基于数据库过滤的谱图聚类算法设计
- 英文题目：Design of a Mass Spectrum Clustering Algorithm Based on Database Filtering
- 学生：李天溧
- 输出文件：`基于数据库过滤的谱图聚类算法设计_论文初稿.docx`

## 项目结构

- 模板来源：`thesis_project/templates/smbu/source.docx`
- 论文内容：`content/meta.json`、`content/chapters.json`、`content/tables.json`、`content/figures.json`、`content/code_blocks.json`、`content/references.json`
- 实验代码：`thesis_project/experiments/db_filter_spectrum_clustering/run_experiment.py`
- 实验指标：`data/experiment_metrics.json`
- 论文图表：`images/experiments/`
- 结构检查：`../../artifacts/db_filter_spectrum_clustering_final_structure.txt`

## 复现命令

```bash
cd /Users/mac/Downloads/Users/a136/vs/45425/thesis_project
/Users/mac/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 experiments/db_filter_spectrum_clustering/run_experiment.py
cd papers/db_filter_spectrum_clustering
/Users/mac/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 build.py
```

说明：当前本机未安装 `soffice`，因此不能自动刷新并渲染 Word 目录。生成的 DOCX 已插入真实 TOC 域，打开后在 Word/WPS 中更新目录即可获得准确页码。
