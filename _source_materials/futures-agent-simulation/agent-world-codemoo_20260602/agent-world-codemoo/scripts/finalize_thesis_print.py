#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Print-ready thesis: fix corruptions, remove meta/instruction text, embed figures."""

import re
import shutil
from pathlib import Path

from docx import Document
from docx.shared import Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph

DOCX = Path(r'c:\Users\ygzn\Desktop\论文过程稿5.27.docx')
BACKUP = Path(r'c:\Users\ygzn\Desktop\论文过程稿5.27.print-prep.bak.docx')
FIG_DIR = Path(r'c:\Users\ygzn\Desktop\论文图表重绘')

FIGURE_MAP = [
    ('图2-1', '图2-1-理论框架.png'),
    ('图3-1', '图3-1-用例示意.png'),
    ('图4-1', '图4-1-体系结构.png'),
    ('图4-2', '图4-2-功能结构.png'),
    ('图4-3', '图4-3-包图.png'),
    ('图4-4', '图4-4-时序.png'),
    ('图4-5', '图4-5-决策流程.png'),
    ('图4-6', '图4-6-自进化.png'),
    ('图4-7', '图4-7-评价闭环.png'),
    ('图4-8', '图4-8-ER.png'),
    ('图4-9', '图4-9-数据逻辑.png'),
    ('图4-10', '图4-10-部署.png'),
]

# Global text repairs (bad auto-replace artifacts)
TEXT_REPAIRS = [
    ('排名第二—判断—协商—行动—反思', '观察—判断—协商—行动—反思'),
    ('排名第二阶段读取', '观察阶段读取'),
    ('增强期货策略学习的可解释性', '增强期货策略学习的可解释性'),  # noop guard
    ('可排名第二性', '可解释性'),
    ('排名第一、排名第二或排名第四', '第一至第四相对排名'),
    ('如程?-', '如程序'),
    ('如?-', '如图'),
    ('?-1', '图4-1'),
    ('?-6', '图4-6'),
    ('?-7', '图4-7'),
    ('?-8', '图4-8'),
    ('?-9', '图4-9'),
    ('?-10', '图4-10'),
    ('?.1?', '（4.1）'),
    ('?.2?', '（4.2）'),
    ('（节选，与 server/llmClient.js buildMessages 一致）', ''),
    ('（节选）', ''),
    ('，与 server/llmClient.js buildMessages 一致', ''),
    ('（运行 ID：2026-06-01T13-38-51-040Z_b98e03，模型 deepseek-v4-flash）', ''),
    ('runs/预设运行版本 的 ', ''),
    ('不再使用采纳/淘汰标签，而以', '以'),
    ('需优化审计记忆权重与观望阈值。', ''),
    ('适合毕业设计演示。', ''),
    ('展示模块需要兼顾论文截图效果。桌面端截图应能够同时体现地图、行情和智能体状态；统计面板截图应能够突出预测结果和策略比较；移动端截图应证明窄屏下主要指标仍然可读。', ''),
]

DELETE_PARA_CONTAINS = [
    'constexpress=require',
    'constAGENT_PROFILES=Object.freeze',
    'functionscoreAgent',
    'functionrenderPredictionReport',
    'classLocalDataLoader{',
    'createSimulationEngine({ worldState',
    'buildLlmEvaluation() 读取',
    'AGENT_PROFILES 含 role',
]

# Keep program4 templates but drop duplicate ch2 program blocks (second copy)
def is_toc_or_preface_program(text: str, style_name: str) -> bool:
    """Remove program2 blocks that landed in TOC/preface region."""
    if not text.startswith('程序2-'):
        return False
    if style_name and 'toc' in style_name.lower():
        return True
    return False


PSEUDO_5 = {
    '程序5-1服务启动与状态广播关键代码': (
        '服务端通过 Express 提供 HTTP 与静态资源，WebSocket 广播仿真状态；'
        '核心入口创建 createSimulationEngine，将 worldState 增量推送至前端。'
    ),
    '程序5-2行情数据加载关键代码': (
        'LocalDataLoader 读取 commodities-historical.json，按日期查询黄金、原油、大豆价格；'
        'roundWithLocalPrices 将情景锚点价替换为本地真实月度价。'
    ),
    '程序5-3智能体画像与决策生成关键代码': (
        'AGENT_PROFILES 定义四类智能体画像；LLM 输出 commodity、action、confidence、reason；'
        '记忆审计官在 peerDecisions 审阅后独立决策；训练段可输出 strategyPatchNotes。'
    ),
    '程序5-4智能体收益评分关键代码': (
        'calculateTradeScore 根据相邻价格变化与动作方向计分；'
        'buildLlmEvaluation 汇总训练/测试得分、胜率、最大回撤及相对 alpha 排名。'
    ),
    '程序5-5统计面板渲染关键代码': (
        'MarketStrategyPanel 展示四名智能体相对排名、得分柱、收益曲线、动作分布与失败样本。'
    ),
    '程序5-6策略进化与失败样本修正关键代码': (
        '训练段累积 strategyPatchNotes，第 4、7 轮合并入 patchNotes 并触发 prompt 版本迭代；'
        '失败样本写入记忆教训，供下一轮 Prompt 检索。'
    ),
}

SECTION_42_5 = (
    '运行展示模块采用 AppShell 分页：总览、智能体、市场行情、工作站、策略评估与运行日志。'
    '策略评估页展示四智能体相对排名与训练/测试得分；运行日志按轮展示决策、辩论与执行记录。'
)


def apply_repairs(text: str) -> str:
    t = text
    for old, new in TEXT_REPAIRS:
        t = t.replace(old, new)
    return t


def remove_paragraph(p):
    p._element.getparent().remove(p._element)


def paragraph_has_image(p) -> bool:
    return bool(p._element.xpath('.//pic:pic'))


def embed_figure_after_caption(doc: Document):
    for p in list(doc.paragraphs):
        cap = p.text.strip().replace(' ', '')
        for key, fname in FIGURE_MAP:
            key_compact = key.replace(' ', '')
            if key_compact not in cap or not cap.startswith(key_compact[:4]):
                continue
            img = FIG_DIR / fname
            if not img.exists():
                continue
            # already embedded in this or next paragraph
            if paragraph_has_image(p):
                break
            nxt_el = p._element.getnext()
            if nxt_el is not None:
                nxt_p = Paragraph(nxt_el, p._parent)
                if paragraph_has_image(nxt_p):
                    break
                if not nxt_p.text.strip():
                    target = nxt_p
                else:
                    new_p = OxmlElement('w:p')
                    p._p.addnext(new_p)
                    target = Paragraph(new_p, p._parent)
            else:
                new_p = OxmlElement('w:p')
                p._p.addnext(new_p)
                target = Paragraph(new_p, p._parent)
            run = target.add_run()
            run.add_picture(str(img), width=Cm(14.0))
            target.alignment = WD_ALIGN_PARAGRAPH.CENTER
            break


def process(doc: Document):
    # Pass 1: delete junk paragraphs
    for idx, p in enumerate(list(doc.paragraphs)):
        t = p.text.strip()
        if not t:
            continue
        if any(k in t for k in DELETE_PARA_CONTAINS):
            remove_paragraph(p)
            continue
        if is_duplicate_ch2_program(idx, t):
            # remove program2 title + following template body until next heading
            remove_paragraph(p)

    # Pass 2: replace program5 blocks & section 4.2.5
    for p in list(doc.paragraphs):
        t = p.text.strip()
        if t in PSEUDO_5:
            nxt = p._element.getnext()
            if nxt is not None:
                nxt_p = Paragraph(nxt, p._parent)
                if nxt_p.text.strip() and 'const' in nxt_p.text.replace(' ', ''):
                    remove_paragraph(nxt_p)
            p.text = PSEUDO_5[t]
            for r in p.runs:
                r.font.name = 'Times New Roman'
            continue
        if t.startswith('运行展示模块包括地图可视化'):
            p.text = SECTION_42_5

    # Pass 3: program2 labels -> clean captions (keep one set in ch2 body only)
    seen_p2 = set()
    for p in list(doc.paragraphs):
        t = p.text.strip()
        if t.startswith('程序2-'):
            if t in seen_p2:
                remove_paragraph(p)
                continue
            seen_p2.add(t)
            p.text = t.replace('（节选）', '').replace('buildMessages 一致', '').strip()

    # Pass 4: repair all text
    for p in doc.paragraphs:
        if p.text:
            p.text = apply_repairs(p.text)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    if p.text:
                        p.text = apply_repairs(p.text)

    # §6.1 cleaner wording
    for p in doc.paragraphs:
        if p.text.startswith('本次评估基于'):
            p.text = (
                '本次评估基于 36 轮完整 LLM 仿真实验。训练段为第 1–6 轮（2016-02-11 至 2018-05-09），'
                '测试段为第 7–36 轮（2018-05-09 至 2026-01-12），共形成 144 条智能体决策记录。'
                '评分依据模型真实决策与下一期历史价格变化累计计算，并做四智能体相对 alpha 校正。'
            )

    embed_figure_after_caption(doc)


def main():
    if not DOCX.exists():
        raise SystemExit(f'Missing {DOCX}')
    shutil.copy2(DOCX, BACKUP)
    doc = Document(str(DOCX))
    process(doc)
    doc.save(str(DOCX))
    n_png = len(list(FIG_DIR.glob('*.png'))) if FIG_DIR.exists() else 0
    print(f'Saved: {DOCX}')
    print(f'Backup: {BACKUP}')
    print(f'Embedded figures from {FIG_DIR} ({n_png} files)')


if __name__ == '__main__':
    main()
