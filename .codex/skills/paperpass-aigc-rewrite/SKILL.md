---
name: paperpass-aigc-rewrite
description: Scan PaperPass AIGC report zip files, extract flagged AI-like sentences and risky keyword chains, and rewrite thesis text with safer sentence shapes while preserving facts, metrics, and technical terminology. Use when the user provides a PaperPass AIGC zip report, asks to lower AIGC score, or wants rewrite rules for high-risk academic sentences.
---

# PaperPass AIGC Rewrite

Use this skill when the user gives a PaperPass AIGC report zip, wants the remaining risky sentences extracted, or wants thesis text rewritten to reduce AIGC-like patterns without becoming colloquial.

## Workflow

1. Run the scanner on the zip report.

```bash
python .codex/skills/paperpass-aigc-rewrite/scripts/scan_paperpass_aigc.py /path/to/report.zip --top 30 --min-score 60
```

Optional:

```bash
python .codex/skills/paperpass-aigc-rewrite/scripts/scan_paperpass_aigc.py /path/to/report.zip --json
python .codex/skills/paperpass-aigc-rewrite/scripts/scan_paperpass_aigc.py /path/to/report.zip --out /tmp/aigc-scan.md
```

2. Read the output in this order:
   - overall score and suspected ratio
   - top flagged sentences
   - connector summary
   - risky technical-term clusters

3. Prioritize edits in this order:
   - figure explanation sentences
   - result summary sentences
   - modality comparison paragraphs
   - limitation / outlook paragraphs
   - generic theoretical paragraphs with dense term chains

4. Apply rewrite rules from [references/rewrite-playbook.md](references/rewrite-playbook.md).

5. If the thesis is source-driven, edit source files first instead of rendered `docx`.
   - For this project, prefer chapter `json` files over the generated `output.docx`.

6. After edits, rerun the scanner on the next PaperPass report and continue only on the remaining high-score sentences.

## What The Scanner Detects

The scanner extracts:

- overall PaperPass AIGC score
- high-score sentences from `simplesentenceresult_ai.js`
- connector chains such as `因此 / 结果表明 / 这意味着 / 具体而言`
- technical-term clusters such as `EEG / fMRI / BOLD / ROI / SVM / 融合 / 指标`
- risky sentence shapes:
  - `figure-interpretation`
  - `metric-summary`
  - `connector-chain`
  - `term-cluster`
  - `template-summary`
  - `long-sentence`

## Rewrite Guardrails

- Keep numbers, metrics, dataset facts, and model names intact unless the source itself is wrong.
- Do not paraphrase into spoken language.
- Do not add generic filler to “wash” the sentence.
- Split dense sentences before replacing words.
- Replace explicit summary connectors before touching terminology.
- Expand only with local, concrete detail:
  - sample size
  - block length
  - channels / ROI
  - validation setup
  - metric meaning

## When To Read More

- Read [references/rewrite-playbook.md](references/rewrite-playbook.md) before rewriting.
- Read the scanner script only if you need to patch detection rules or add more risky markers.
