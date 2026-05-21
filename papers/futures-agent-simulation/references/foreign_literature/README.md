# 外文文献材料说明

本目录只保留附录最终使用的外文文献材料。

- `tradingagents_2412.20138.pdf`：外文原文 PDF。
- `tradingagents_source/`：arXiv e-print 和解包后的 LaTeX 源文件，用于结构化提取正文、参考文献、表格、公式和图。
- `original_assets/`：由 LaTeX 源文件中的图形资源转换得到的原文插图，用于附件4。
- `figures/`：译文部分选用的 TradingAgents 插图，用于附件3。

生成流程：

```bash
python3 scripts/extract_tradingagents_original.py
python3 build_appendix_template_replace.py
```

旧的 PDF 整页截图、OCR 中间文本和未采用的候选论文不放在论文目录内。
