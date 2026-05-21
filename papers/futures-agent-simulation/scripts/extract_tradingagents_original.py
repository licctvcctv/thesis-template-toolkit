from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "references/foreign_literature/tradingagents_source/extracted"
OUT_JSON = ROOT / "content/foreign_original.json"
ASSET_OUT = ROOT / "references/foreign_literature/original_assets"


def strip_comments(text: str) -> str:
    cleaned = []
    for line in text.splitlines():
        if line.lstrip().startswith("%"):
            continue
        cleaned.append(re.sub(r"(?<!\\)%.*$", "", line))
    return "\n".join(cleaned)


def read_tex(rel_path: str) -> str:
    path = SOURCE / rel_path
    if not path.suffix:
        path = path.with_suffix(".tex")
    return strip_comments(path.read_text(encoding="utf-8", errors="ignore"))


def expand_inputs(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        rel = match.group(1)
        if not rel.endswith(".tex"):
            rel += ".tex"
        return "\n" + expand_inputs(read_tex(rel)) + "\n"

    previous = None
    while previous != text:
        previous = text
        text = re.sub(r"\\input\{([^}]+)\}", repl, text)
    return text


def find_braced(text: str, command: str, start: int = 0) -> tuple[str, int] | None:
    token = "\\" + command
    idx = text.find(token, start)
    if idx < 0:
        return None
    brace = text.find("{", idx + len(token))
    if brace < 0:
        return None
    depth = 0
    for pos in range(brace, len(text)):
        ch = text[pos]
        if ch == "{" and (pos == 0 or text[pos - 1] != "\\"):
            depth += 1
        elif ch == "}" and (pos == 0 or text[pos - 1] != "\\"):
            depth -= 1
            if depth == 0:
                return text[brace + 1:pos], pos + 1
    return None


def replace_simple_commands(text: str) -> str:
    text = re.sub(r"\\textcolor\{[^{}]*\}\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}", r"\1", text)
    for command in [
        "textbf",
        "textit",
        "emph",
        "texttt",
        "textsc",
        "normalfont",
        "small",
        "footnotesize",
        "url",
    ]:
        changed = True
        while changed:
            changed = False
            pattern = "\\" + command
            idx = text.find(pattern)
            while idx >= 0:
                found = find_braced(text, command, idx)
                if not found:
                    break
                inner, end = found
                text = text[:idx] + inner + text[end:]
                changed = True
                idx = text.find(pattern, idx + len(inner))
    return text


def latex_to_text(text: str) -> str:
    text = text.replace("\\model", "TradingAgents")
    text = text.replace("\\xspace", "")
    text = re.sub(r"\\verb(.)(.*?)\1", r"\2", text)
    text = re.sub(r"\\cite[p|t]?\{([^}]+)\}", lambda m: "[" + ", ".join(m.group(1).split(",")) + "]", text)
    text = re.sub(r"\\ref\{([^}]+)\}", lambda m: m.group(1), text)
    text = re.sub(r"\\label\{[^}]+\}", "", text)
    text = re.sub(r"\\footnote\{([^}]*)\}", r"（\1）", text)
    text = text.replace("``", '"').replace("''", '"')
    text = text.replace("\\\\", " ")
    text = text.replace("~", " ")
    text = text.replace("\\%", "%").replace("\\&", "&").replace("\\$", "$")
    text = text.replace("\\uparrow", "↑").replace("\\downarrow", "↓")
    text = text.replace("---", "—").replace("--", "–")
    text = re.sub(r"\\\(|\\\)", "", text)
    text = re.sub(r"\\\[|\\\]", "", text)
    text = replace_simple_commands(text)
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?", "", text)
    text = re.sub(r"\$\^\{?([^}$]+)\}?\$", r"\1", text)
    text = re.sub(r"\$([^$]+)\$", r"\1", text)
    text = text.replace("$", "")
    text = text.replace("{", "").replace("}", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def asset_name(src: str) -> str:
    return src.replace("/", "_").replace("\\", "_").replace(".", "_") + ".png"


def convert_asset(src: str) -> str | None:
    source_path = SOURCE / src
    if not source_path.suffix and source_path.exists():
        pass
    elif not source_path.exists():
        for ext in [".pdf", ".png", ".jpg", ".jpeg"]:
            if (SOURCE / (src + ext)).exists():
                source_path = SOURCE / (src + ext)
                break
    if not source_path.exists():
        return None

    ASSET_OUT.mkdir(parents=True, exist_ok=True)
    out_path = ASSET_OUT / asset_name(src)
    if source_path.suffix.lower() == ".png":
        shutil.copy2(source_path, out_path)
    elif source_path.suffix.lower() in {".jpg", ".jpeg"}:
        shutil.copy2(source_path, out_path.with_suffix(source_path.suffix.lower()))
        out_path = out_path.with_suffix(source_path.suffix.lower())
    elif source_path.suffix.lower() == ".pdf":
        stem = ASSET_OUT / out_path.stem
        subprocess.run(
            ["pdftoppm", "-png", "-singlefile", "-r", "180", str(source_path), str(stem)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        return None
    return str(out_path.relative_to(ROOT))


def extract_caption(block: str) -> str:
    found = find_braced(block, "caption")
    return latex_to_text(found[0]) if found else ""


def table_rows(block: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for raw in block.splitlines():
        line = raw.strip()
        if "&" not in line or line.startswith("\\"):
            continue
        line = re.sub(r"\\\\.*$", "", line)
        cells = [latex_to_text(cell.replace(r"\&", "&")) for cell in re.split(r"(?<!\\)&", line)]
        if len(cells) > 1:
            rows.append(cells)
    return rows


def equation_display(latex: str) -> str:
    if "\\text{CR}" in latex:
        return "CR = ((V(end) - V(start)) / V(start)) × 100%"
    if "\\text{AR}" in latex:
        return "AR = ((V(end) / V(start))^(1/N) - 1) × 100%"
    if "\\text{SR}" in latex:
        return "SR = (R̄ - Rf) / σ"
    if "\\text{MDD}" in latex:
        return "MDD = max t∈[0,T] ((Peak(t) - Trough(t)) / Peak(t)) × 100%"
    return latex_to_text(latex)


def process_text(text: str, items: list[dict]) -> None:
    heading_re = re.compile(r"\\(section|subsection|subsubsection)\*?\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}")
    pos = 0
    for match in heading_re.finditer(text):
        process_plain(text[pos:match.start()], items)
        level = {"section": 1, "subsection": 2, "subsubsection": 3}[match.group(1)]
        items.append({"type": "heading", "level": level, "text": latex_to_text(match.group(2))})
        pos = match.end()
    process_plain(text[pos:], items)


def process_plain(text: str, items: list[dict]) -> None:
    text = re.sub(r"\\(vskip|vspace|clearpage|newpage|onecolumn|beginsupplement).*", "", text)
    for paragraph in re.split(r"\n\s*\n", text):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        cleaned = latex_to_text(paragraph)
        if cleaned:
            items.append({"type": "paragraph", "text": cleaned})


def parse_items(text: str) -> list[dict]:
    items: list[dict] = []
    env_re = re.compile(
        r"\\begin\{(figure\*?|table\*?|equation|itemize|lstlisting|tcolorbox)\}.*?\\end\{\1\}",
        re.DOTALL,
    )
    pos = 0
    for match in env_re.finditer(text):
        process_text(text[pos:match.start()], items)
        env = match.group(1)
        block = match.group(0)
        if env.startswith("figure"):
            graphics = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", block)
            caption = extract_caption(block)
            for graphic in graphics:
                asset = convert_asset(graphic)
                items.append({
                    "type": "figure",
                    "src": asset,
                    "source": graphic,
                    "caption": caption,
                })
        elif env.startswith("table"):
            items.append({
                "type": "table",
                "caption": extract_caption(block),
                "rows": table_rows(block),
                "latex": block.strip(),
            })
        elif env == "equation":
            body = re.sub(r"\\begin\{equation\}|\\end\{equation\}", "", block).strip()
            items.append({"type": "equation", "latex": body, "text": equation_display(body)})
        elif env == "itemize":
            content = re.sub(r"\\begin\{itemize\}|\\end\{itemize\}", "", block)
            for item in re.split(r"\\item", content)[1:]:
                cleaned = latex_to_text(item)
                if cleaned:
                    items.append({"type": "list_item", "text": cleaned})
        elif env in {"lstlisting", "tcolorbox"}:
            title = ""
            title_matches = re.findall(r"(?:^|,)\s*title\s*=\s*([^,\]]+)", block, re.DOTALL)
            if title_matches:
                title = latex_to_text(title_matches[-1])
            code_match = re.search(r"\\begin\{lstlisting\}(.*?)\\end\{lstlisting\}", block, re.DOTALL)
            code = code_match.group(1).strip() if code_match else block
            items.append({"type": "code", "title": title, "text": code})
        pos = match.end()
    process_text(text[pos:], items)
    return items


def parse_references() -> list[dict]:
    bbl = read_tex("main.bbl")
    entries: list[dict] = [{"type": "heading", "level": 1, "text": "References"}]
    for chunk in re.split(r"\\bibitem(?:\[[^\]]+\])?\{[^}]+\}", bbl)[1:]:
        chunk = re.sub(r"\\newblock", " ", chunk)
        text = latex_to_text(chunk)
        if text:
            entries.append({"type": "reference", "text": text})
    return entries


def main() -> None:
    main_tex = read_tex("main.tex")
    title = latex_to_text(find_braced(main_tex, "title")[0]).replace("TradingAgents:", "TradingAgents:")
    author = "Yijia Xiao; Edward Sun; Di Luo; Wei Wang. 1 University of California, Los Angeles (UCLA); 2 Massachusetts Institute of Technology (MIT); 3 Tauric Research."
    abstract = latex_to_text(re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", main_tex, re.DOTALL).group(1))

    body_tex = "\n".join(
        [
            read_tex("sections/1.intro.tex"),
            read_tex("sections/2.related.tex"),
            read_tex("sections/3.methodology.tex"),
            read_tex("sections/4.expreiments.tex"),
            read_tex("sections/5.results.tex"),
            read_tex("sections/6.conclusion.tex"),
        ]
    )
    body_tex = expand_inputs(body_tex)
    appendix_tex = read_tex("sections/appendix.tex")
    appendix_start = appendix_tex.find("\\section{Supplementary Materials")
    if appendix_start >= 0:
        appendix_tex = appendix_tex[appendix_start:]
    appendix_tex = expand_inputs(appendix_tex)
    items = [
        {"type": "title", "text": title},
        {"type": "authors", "text": author},
        {"type": "heading", "level": 1, "text": "Abstract"},
        {"type": "paragraph", "text": abstract},
        *parse_items(body_tex),
        *parse_references(),
        *parse_items(appendix_tex),
    ]

    payload = {
        "meta": {
            "title": title,
            "authors": author,
            "source": "arXiv:2412.20138v7",
            "source_url": "https://arxiv.org/abs/2412.20138",
            "extraction_method": "arXiv LaTeX source parsed into structured JSON; PDF text used only as fallback material.",
        },
        "items": items,
        "stats": {
            "items": len(items),
            "figures": sum(1 for item in items if item["type"] == "figure"),
            "tables": sum(1 for item in items if item["type"] == "table"),
            "equations": sum(1 for item in items if item["type"] == "equation"),
            "code_blocks": sum(1 for item in items if item["type"] == "code"),
            "references": sum(1 for item in items if item["type"] == "reference"),
        },
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload["stats"], ensure_ascii=False, indent=2))
    print(OUT_JSON)


if __name__ == "__main__":
    main()
