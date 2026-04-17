---
name: paperpass-aigc-rewrite
description: Use when the user provides a PaperPass AIGC zip report, asks to lower AIGC score, wants all sentences above a score threshold rewritten, or needs thesis text reduced in AI-like sentence patterns without becoming colloquial.
---

# PaperPass AIGC Rewrite

Use this skill when the user gives a PaperPass AIGC report zip, wants the remaining risky sentences extracted, or wants thesis text rewritten to reduce AIGC-like patterns while keeping an academic register.

## Workflow

1. Determine the rewrite threshold.
   - If the user gives an explicit score such as `大于 60 分`, treat that threshold as mandatory.
   - Otherwise use a conservative default threshold of `55`.
   - **Every sentence at or above the threshold must be rewritten.** Do not stop after only the top 5-10 hits.

2. Run the scanner on the zip report.

```bash
python .codex/skills/paperpass-aigc-rewrite/scripts/scan_paperpass_aigc.py /path/to/report.zip --top 30 --min-score 60
```

Optional:

```bash
python .codex/skills/paperpass-aigc-rewrite/scripts/scan_paperpass_aigc.py /path/to/report.zip --json
python .codex/skills/paperpass-aigc-rewrite/scripts/scan_paperpass_aigc.py /path/to/report.zip --rewrite-threshold 55
python .codex/skills/paperpass-aigc-rewrite/scripts/scan_paperpass_aigc.py /path/to/report.zip --out /tmp/aigc-scan.md
```

3. Read the output in this order:
   - rewrite threshold and mandatory rewrite count
   - overall score and suspected ratio
   - top flagged sentences
   - connector summary
   - risky technical-term clusters

4. Prioritize edits in this order:
   - figure explanation sentences
   - result summary sentences
   - modality comparison paragraphs
   - limitation / outlook paragraphs
   - generic theoretical paragraphs with dense term chains

5. Apply rewrite rules from [references/rewrite-playbook.md](references/rewrite-playbook.md).

6. If the thesis is source-driven, edit source files first instead of rendered `docx`.
   - For this project, prefer chapter `json` files over the generated `output.docx`.

7. After edits, regenerate the rendered `docx` and verify against the current report.
   - Source files may be clean while the rendered document still preserves risky paragraph joins.
   - Check the rendered `docx` text, not only the source `json`.

8. After the next PaperPass report arrives, continue only on the remaining sentences at or above the threshold.

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
- Keep the text in academic written Chinese. Do not paraphrase into spoken language.
- Do not use chatty fillers such as `做下来 / 比较好 / 没问题 / 基本上 / 其实 / 这种`.
- Every sentence at or above the rewrite threshold is mandatory work, not optional cleanup.
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
