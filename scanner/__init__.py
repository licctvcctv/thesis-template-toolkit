"""
论文模板扫描器 - 分析 Word 文档结构，输出结构化信息供 AI 决策。

不直接修改文件，只负责"看"和"报告"。
"""
from .structure import scan_structure
from .paragraphs import scan_paragraphs
from .report import generate_report

__all__ = ['scan_structure', 'scan_paragraphs', 'generate_report']
