# 无人机精准投放技术论文项目

本目录用于生成四川大学电子信息学院本科毕业论文《无人机精准投放技术》。

## 输入材料

- 学校模板：`../../templates/scu_eie_2026/source.docx`
- 案例论文：`data/case_paper.pdf`
- 开题报告：`data/proposal.docx`
- 沟通记录：`data/source_chat.txt`
- 原始上传材料归档：`../../_source_materials/original_uploads/`
- 仿真实验代码：`../../experiments/uav_precision_delivery/simulation/`

## 目录边界

- `content/`：论文正文、图表、参考文献、目录页码等 JSON 源。
- `data/`：论文写作需要引用的规范化输入材料和仿真指标副本。
- `images/imagegen/`：论文使用的结构图、流程图等非运行证明类图片。
- `images/simulation/`：论文使用的仿真图片，由外层实验脚本同步生成。
- `scripts/`：只保留论文装配/目录页码等文档维护脚本，不放仿真或预测实验代码。
- `../../artifacts/uav_precision_delivery/render_check_latest/`：最后一次交付前渲染检查结果。

## 生成方式

1. 生成 Python 仿真图：

   ```bash
   cd ../../
   python experiments/uav_precision_delivery/simulation/generate_simulation_figures.py
   ```

2. 构建论文 DOCX：

   ```bash
   cd papers/uav_precision_delivery
   python build.py
   ```

3. 渲染检查：

   ```bash
   env TMPDIR=/private/tmp python /Users/a136/.codex/plugins/cache/openai-primary-runtime/documents/26.506.11943/skills/documents/render_docx.py 无人机精准投放技术-游忠锦.docx --output_dir ../../artifacts/uav_precision_delivery/render_check_latest --emit_pdf
   ```

## 内容源

正文、图表、参考文献均以 `content/*.json` 为源，`build.py` 只负责装配模板、插入图片/表格、生成目录与参考文献。后续修改论文内容时，优先修改 JSON 和图片资源，不直接手工改最终 DOCX。

## 图片来源规则

- `images/imagegen/`：结构图、流程图等非运行证明类论文图，由 ImageGen 生成。
- `images/simulation/`：仿真实验图，由 Python 脚本生成。
- `images/system_screenshots/`：真实系统运行截图；本阶段没有实际硬件/系统运行截图，因此不伪造。
