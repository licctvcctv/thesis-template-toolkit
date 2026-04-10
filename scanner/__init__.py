"""
论文模板扫描器 - 渐进式分析，供 AI 决策。

粗扫: scan_structure() → 文档分区概览
细扫: scan_paragraphs() → 特定区域的 run 级详情
正文: scan_body() → 找格式样本（标题/表格/图片）
报告: generate_report() → AI 可读的文本报告
"""
from .structure import scan_structure
from .paragraphs import scan_paragraphs, scan_para_runs
from .body import scan_body
from .report import generate_report

__all__ = [
    'scan_structure', 'scan_paragraphs', 'scan_para_runs',
    'scan_body', 'generate_report',
]
