# eye_disease 项目工作目录

本目录按郑州工商学院信息工程学院毕业设计模板和参考论文组织，后续正文、图片、运行截图、输出稿都在同一项目内管理。

## 目录结构

```text
eye_disease/
├── meta.json                         # 论文封面、摘要、关键词、结论等基础信息
├── ch1.json ~ ch5.json               # 正文章节内容，按郑州参考论文目录维护
├── ch6.json                          # 备用总结内容，正式模板中结论独立处理
├── references.json                   # 参考文献
├── build.py                          # Word 拼接脚本
├── images/
│   ├── generated/                    # imagegen 生成的示意图、流程图、补充图
│   ├── model_results/                # 模型训练曲线、混淆矩阵、指标对比图
│   └── runtime_screenshots/          # 系统实际运行截图
├── materials/
│   ├── zhengzhou_template/           # 郑州毕业设计 Word 模板
│   ├── reference_paper/              # 杨孝刚参考论文
│   ├── opening_report/               # 肖锦天开题报告
│   └── zz_new_requirements/          # “郑州论文新要求”资料索引
├── runtime/
│   ├── candidate_systems/            # 候选可运行系统、代码来源说明
│   └── dataset/                      # 数据集来源、类别、样本量说明
├── notes/
│   ├── paper_directory.md            # 按参考论文整理的论文目录
│   ├── paper_directory.json          # 后续改写 JSON 时使用的章节骨架
│   └── project_structure.md          # 当前文件
├── outputs/                          # 后续生成的 Word 终稿、阶段稿
└── render_check/                     # Word 渲染检查页、版式 QA 输出
```

## 写作依据

- Word 模板以 `materials/zhengzhou_template/docxtpl_template.docx` 为准。
- 目录和正文写法参考 `materials/reference_paper/杨孝刚参考论文.docx`。
- 研究方向、学生信息和任务内容参考 `materials/opening_report/肖锦天开题报告.docx`。
- 新要求资料先在 `materials/zz_new_requirements/README.md` 中索引，后续需要时再提取具体修改点。

## 后续拼接规则

- 正文优先修改根目录下的 `meta.json`、`ch1.json` 至 `ch5.json`、`references.json`。
- 论文目录按 `notes/paper_directory.md` 的结构走，不额外发挥新的章节。
- 系统截图放入 `images/runtime_screenshots/`，模型指标图放入 `images/model_results/`，AI 生成补充图放入 `images/generated/`。
- 最终 Word 输出放入 `outputs/`，渲染检查结果放入 `render_check/`。
