#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path


CONNECTORS = [
    "因此", "此外", "与此同时", "同时", "结果表明", "这意味着", "可以看出",
    "需要注意的是", "从应用角度看", "具体而言", "换言之", "基于此",
    "另一方面", "由图", "从图", "可见", "表明", "提示", "说明",
]

TERM_PATTERNS = {
    "EEG": r"\bEEG\b",
    "fMRI": r"\bfMRI\b",
    "BOLD": r"\bBOLD\b",
    "ROI": r"\bROI\b",
    "SVM": r"\bSVM\b",
    "kNN": r"\bkNN\b",
    "RF": r"\bRF\b",
    "CSP": r"\bCSP\b",
    "TR": r"\bTR\b",
    "Mu": r"\bMu\b",
    "Beta": r"\bBeta\b",
    "block": r"\bblock\b",
    "Fusion_Derived": r"\bFusion_Derived\b",
    "EEG_Derived": r"\bEEG_Derived\b",
    "BOLD_Derived": r"\bBOLD_Derived\b",
    "EEG_Handcrafted": r"\bEEG_Handcrafted\b",
    "laterality": r"\blaterality\b",
    "融合": r"融合",
    "特征": r"特征",
    "网络": r"网络",
    "分类": r"分类",
    "聚类系数": r"聚类系数",
    "全局效率": r"全局效率",
    "节点强度": r"节点强度",
}

TEMPLATE_MARKERS = [
    "结果表明", "这意味着", "需要注意的是", "从应用角度看",
    "具体而言", "换言之", "基于此", "可以看出",
]


@dataclass
class SentenceHit:
    sid: str
    score: float
    text: str
    connectors: list[str]
    terms: list[str]
    flags: list[str]
    clause_count: int


def normalize_text(text: str) -> str:
    text = text.replace("\u3000", " ").replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s*([，。；：！？,.;:!?])\s*", r"\1", text)
    text = re.sub(r"([（(])\s+", r"\1", text)
    text = re.sub(r"\s+([）)])", r"\1", text)
    text = text.replace(" - ", "-")
    return text


def load_js_object(source: Path, filename: str) -> dict:
    if source.is_file() and source.suffix.lower() == ".zip":
        with zipfile.ZipFile(source) as zf:
            matches = [n for n in zf.namelist() if n.endswith(filename)]
            if not matches:
                raise FileNotFoundError(f"zip 内未找到 {filename}")
            raw = zf.read(matches[0]).decode("utf-8", errors="ignore")
    else:
        matches = list(source.rglob(filename))
        if not matches:
            raise FileNotFoundError(f"目录内未找到 {filename}")
        raw = matches[0].read_text(encoding="utf-8", errors="ignore")

    m = re.search(r"=\s*(\{.*\})\s*;?\s*$", raw, re.S)
    if not m:
        raise ValueError(f"无法解析 {filename} 中的 JSON")
    return json.loads(m.group(1))


def detect_terms(text: str) -> list[str]:
    hits = []
    for name, pattern in TERM_PATTERNS.items():
        if re.search(pattern, text, re.I):
            hits.append(name)
    return hits


def detect_flags(text: str, connectors: list[str], terms: list[str]) -> tuple[list[str], int]:
    clause_count = len([x for x in re.split(r"[，。；：,;:！？!?]", text) if x.strip()])
    flags = []
    if len(connectors) >= 2:
        flags.append("connector-chain")
    if len(terms) >= 4:
        flags.append("term-cluster")
    if "图" in text and any(k in text for k in ["表明", "提示", "说明", "显示"]):
        flags.append("figure-interpretation")
    if any(k in text for k in ["准确率", "精确率", "召回率", "F1"]) and any(k in text for k in ["SVM", "kNN", "RF", "随机森林"]):
        flags.append("metric-summary")
    if clause_count >= 4 or len(text) >= 120:
        flags.append("long-sentence")
    if any(k in text for k in TEMPLATE_MARKERS):
        flags.append("template-summary")
    return flags, clause_count


def collect_hits(data: dict, min_score: float) -> list[SentenceHit]:
    hits = []
    for sid, row in data.items():
        text = normalize_text(" ".join(row.get("sectionContentList", [])))
        score = float(row.get("overall", 0.0))
        if not text or score < min_score:
            continue
        connectors = [c for c in CONNECTORS if c in text]
        terms = detect_terms(text)
        flags, clause_count = detect_flags(text, connectors, terms)
        hits.append(SentenceHit(sid=sid, score=score, text=text, connectors=connectors, terms=terms, flags=flags, clause_count=clause_count))
    hits.sort(key=lambda x: (-x.score, -len(x.flags), x.sid))
    return hits


def build_markdown(source: Path, summary: dict, hits: list[SentenceHit], top: int) -> str:
    connector_counter = Counter()
    term_counter = Counter()
    flag_counter = Counter()
    for hit in hits:
        connector_counter.update(hit.connectors)
        term_counter.update(hit.terms)
        flag_counter.update(hit.flags)

    lines = []
    lines.append(f"# PaperPass AIGC 扫描结果")
    lines.append("")
    lines.append(f"- 来源: `{source}`")
    lines.append(f"- AIGC 分数: `{summary.get('score')}`")
    lines.append(f"- 总可疑占比: `{summary.get('totalSuspectedTextRatio')}%`")
    lines.append(f"- 中高风险占比: `{summary.get('highAndMiddleSuspectedTextRatio')}%`")
    lines.append(f"- 句子数(>=阈值): `{len(hits)}`")
    lines.append("")
    if connector_counter:
        lines.append("## 高频连接词")
        lines.append("")
        for key, val in connector_counter.most_common(12):
            lines.append(f"- `{key}`: {val}")
        lines.append("")
    if term_counter:
        lines.append("## 高频术语簇")
        lines.append("")
        for key, val in term_counter.most_common(15):
            lines.append(f"- `{key}`: {val}")
        lines.append("")
    if flag_counter:
        lines.append("## 风险句型")
        lines.append("")
        for key, val in flag_counter.most_common():
            lines.append(f"- `{key}`: {val}")
        lines.append("")
    lines.append("## 高风险句子")
    lines.append("")
    for hit in hits[:top]:
        lines.append(f"### ID {hit.sid} | score {hit.score:.2f}")
        lines.append("")
        lines.append(f"- 连接词: `{', '.join(hit.connectors) if hit.connectors else '-'}`")
        lines.append(f"- 术语: `{', '.join(hit.terms) if hit.terms else '-'}`")
        lines.append(f"- 标记: `{', '.join(hit.flags) if hit.flags else '-'}`")
        lines.append(f"- 分句数: `{hit.clause_count}`")
        lines.append("")
        lines.append(hit.text)
        lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="扫描 PaperPass AIGC 报告 zip，提取高风险句和关键词链")
    p.add_argument("source", help="PaperPass 报告 zip 或已解压目录")
    p.add_argument("--min-score", type=float, default=60.0, help="只输出不低于该分数的句子")
    p.add_argument("--rewrite-threshold", type=float, help="把该分数视为必改阈值；高于或等于该分数的句子都应改写")
    p.add_argument("--top", type=int, default=30, help="最多输出多少句")
    p.add_argument("--json", action="store_true", help="输出 JSON")
    p.add_argument("--out", help="把结果写入文件")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    source = Path(args.source).expanduser().resolve()
    if not source.exists():
        print(f"路径不存在: {source}", file=sys.stderr)
        return 2

    threshold = args.rewrite_threshold if args.rewrite_threshold is not None else args.min_score
    summary = load_js_object(source, "reduceaigcpagedata.js")
    data = load_js_object(source, "simplesentenceresult_ai.js")
    hits = collect_hits(data, threshold)

    if args.json:
        payload = {
            "source": str(source),
            "rewriteThreshold": threshold,
            "summary": summary,
            "hits": [asdict(x) for x in hits[: args.top]],
        }
        out = json.dumps(payload, ensure_ascii=False, indent=2)
    else:
        out = build_markdown(source, summary, hits, args.top)
        out = out.replace(
            f"- AIGC 分数: `{summary.get('score')}`",
            f"- AIGC 分数: `{summary.get('score')}`\n- 重写阈值: `{threshold}`\n- 必改句子数(>=阈值): `{len(hits)}`",
            1,
        )

    if args.out:
        Path(args.out).write_text(out, encoding="utf-8")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
