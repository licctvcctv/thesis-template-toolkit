# 基于多智能体的期货交易模拟系统论文工程

## 主要产物

- 最终 Word 初稿：`基于多智能体的期货交易模拟系统设计与实现_论文初稿.docx`
- 附录 Word：`附录_基于自进化LLM的期货市场多智能体决策模拟系统.docx`
- 正文渲染校验目录：`render_check/prompt_metrics_ack_update/`
- 学校论文模板：`../../templates/bistu_2026/template.docx`
- 内容源文件：`content/meta.json`、`content/chapters.json`、`content/conclusion.json`、`content/acknowledgement.json`、`content/references.json`
- 组装脚本：`build.py`
- 附录内容源文件：`content/appendix.json`、`content/foreign_original.json`
- 附录组装脚本：`build_appendix_template_replace.py`

## 图片材料

- 概念图：`images/imagegen/fig3-1_system_architecture.png`
- 概念图：`images/imagegen/fig3-2_function_structure.png`
- 概念图：`images/imagegen/fig3-3_strategy_evolution_flow.png`
- 系统用例图：`images/imagegen/fig3-1_system_use_case.png`
- 第二章理论图：`images/imagegen/fig2-1_multi_agent_futures_negotiation_framework.png`
- 第四章算法图：`images/imagegen/fig2-2_self_evolving_agent_learning_flow.png`
- 真实运行截图：`images/system_screenshots/fig4-1_home_runtime.png`
- 真实运行截图：`images/system_screenshots/fig4-2_statistics_runtime.png`
- 真实运行截图：`images/system_screenshots/fig4-3_mobile_runtime.png`

## 附录材料

- 附录模板和用户原始材料：`../../_source_materials/futures-agent-simulation/appendix_inputs/`
- 外文文献 PDF：`references/foreign_literature/tradingagents_2412.20138.pdf`
- 外文文献 LaTeX 源：`references/foreign_literature/tradingagents_source/`
- 外文原文图像资产：`references/foreign_literature/original_assets/`
- 译文插图资产：`references/foreign_literature/figures/`
- 外文原文结构化结果：`content/foreign_original.json`

## 重新生成论文

```bash
cd /Users/a136/vs/45425/thesis_project/papers/futures-agent-simulation
python3 build.py
```

## 重新生成附录

```bash
cd /Users/a136/vs/45425/thesis_project/papers/futures-agent-simulation
python3 scripts/extract_tradingagents_original.py
python3 build_appendix_template_replace.py
```

## 重新运行系统测试

```bash
cd /Users/a136/vs/45425/thesis_project/papers/futures-agent-simulation/data/agent-world-codemoo
npm test
```

## 校验记录

- Word 组装脚本输出：校验通过，公式对象数量校验通过。
- 文档残留检查：占位符、旧题目和不合规词均为 0。
- 项目测试：本次修改未改动系统源码；如需复验可在系统目录执行 `npm test`。
- Word 渲染：已输出 `render_check/prompt_metrics_ack_update` 下 46 页 PNG 供版式检查；第二章目录已压缩为理论概览，工程技术细节移动至第四章、第六章和第七章，自进化智能体算法集中放在第四章 4.2.3 节展开。
- 个人信息检查：学生姓名、学号和导师姓名均未填写，最终文件名不包含姓名或学号。
- 图表检查：图3-1 已替换为 ImageGen 黑白用例图，仅保留“用户”一个参与者；第4章已补充 LLM 各功能模块提示词模板，第6章已补充评价指标与计算公式，第7章已扩写总结、进化机制、不足和展望，目录页码已同步。
- 致谢检查：已补充开题答辩老师关于真实期货 K 线与历史数据模拟方案的建议，未补写具体姓名。
- 附录检查：附件1直接复制开题报告原 DOCX 段落，保留签字意见区格式；附件4根据 TradingAgents 的 arXiv LaTeX 源生成 Word 原文，不使用整页 OCR 图片；附录文件名不包含姓名和学号。
