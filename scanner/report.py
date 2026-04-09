"""
扫描报告生成 - 将扫描结果格式化为 AI 可读的文本报告。
AI 看到报告后决定替换方案，调用 editor 执行。
"""


def generate_report(structure, paragraphs=None):
    """
    生成结构化文本报告。

    参数:
        structure: scan_structure() 的返回值
        paragraphs: scan_paragraphs() 的返回值（可选）

    返回: 格式化的报告字符串
    """
    lines = []
    lines.append("=" * 60)
    lines.append("论文模板扫描报告")
    lines.append("=" * 60)

    # 基本信息
    lines.append(f"\n总段落数: {structure['total_paragraphs']}")
    lines.append(f"总表格数: {structure['total_tables']}")
    lines.append(f"总分节数: {structure['total_sections']}")

    # 样式统计
    lines.append(f"\n使用的样式:")
    for name, count in structure['styles_used'].items():
        lines.append(f"  {name}: {count}次")

    # 文档分区
    lines.append(f"\n文档分区:")
    for name, info in structure['parts'].items():
        lines.append(
            f"  {name}: Para[{info['start']}] "
            f"'{info['text']}'")
    if 'body_start' in structure:
        lines.append(
            f"  body_start: Para[{structure['body_start']}]")
    if 'body_end' in structure:
        lines.append(
            f"  body_end: Para[{structure['body_end']}]")

    # 段落详情（如果提供）
    if paragraphs:
        lines.append(f"\n段落详情 ({len(paragraphs)}个):")
        for p in paragraphs:
            flags = []
            if p.get("has_sectPr"):
                flags.append("SECT")
            if p.get("has_numPr"):
                flags.append("NUM")
            flag_str = (
                f" [{','.join(flags)}]" if flags else "")
            lines.append(
                f"  [{p['idx']}]{flag_str} "
                f"'{p['text'][:60]}'")

            if "runs" in p:
                for r in p["runs"]:
                    fmt = []
                    if r["font"]:
                        fmt.append(f"font={r['font']}")
                    if r["size"]:
                        fmt.append(f"sz={r['size']}")
                    if r["bold"]:
                        fmt.append("B")
                    if r["underline"]:
                        fmt.append("U")
                    fmt_str = (
                        ', '.join(fmt) if fmt else "default")
                    lines.append(
                        f"    run[{r['idx']}]: "
                        f"'{r['text'][:40]}' "
                        f"({fmt_str})")

    return "\n".join(lines)
