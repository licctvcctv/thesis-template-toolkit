#!/usr/bin/env python3
"""Generate thesis diagram PNGs (technical figures; screenshots 5-x are manual)."""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

OUT = Path(r'c:\Users\ygzn\Desktop\论文图表重绘')
OUT.mkdir(parents=True, exist_ok=True)


def save(fig, name):
    path = OUT / name
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('wrote', path)


def box(ax, x, y, w, h, text, fc='#E8F4FC', ec='#2563EB'):
    rect = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.02', fc=fc, ec=ec, lw=1.5)
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=9, wrap=True)


def arrow(ax, x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='->', mutation_scale=12, color='#334155'))


def fig2_1():
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis('off')
    box(ax, 0.5, 3.5, 2.2, 1, '历史行情\n(黄金/原油/大豆)')
    box(ax, 3.5, 3.5, 2.2, 1, '市场情景\n(36轮 regime/news)')
    box(ax, 6.5, 3.5, 2.8, 1, '四智能体\n保守/均衡/激进/审计')
    box(ax, 1, 1.5, 2.5, 1, 'LLM 决策\n+ Prompt 自进化')
    box(ax, 4, 1.5, 2.5, 1, '辩论场\n共识/异议')
    box(ax, 6.8, 1.5, 2.5, 1, '收益评分\n训练/测试分离')
    arrow(ax, 2.7, 4, 3.5, 4)
    arrow(ax, 5.7, 4, 6.5, 4)
    arrow(ax, 7.9, 3.5, 2.2, 2.5)
    arrow(ax, 3.4, 2, 4, 2)
    arrow(ax, 6.5, 2, 6.8, 2)
    ax.set_title('图2-1 多智能体期货 LLM 决策与自进化理论框架', fontsize=12, pad=12)
    save(fig, '图2-1-理论框架.png')


def fig3_1():
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 5)
    ax.axis('off')
    box(ax, 3.2, 4, 2.6, 0.8, '用户 / 实验者', fc='#FEF3C7')
    for i, (x, t) in enumerate([(0.3, '行情加载'), (2.3, '启动36轮'), (4.3, '查看决策'), (6.3, '策略评估'), (8.0, '运行日志')]):
        box(ax, x, 2.2, 1.6, 0.9, t)
        arrow(ax, 4.5, 4, x + 0.8, 3.1)
    box(ax, 2.5, 0.5, 4, 0.9, 'DeepSeek LLM + runs 录制 + WebSocket 实时推送')
    save(fig, '图3-1-用例示意.png')


def fig4_1():
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis('off')
    box(ax, 0.4, 2.5, 2.2, 1.4, 'frontend/\nAppShell · EventLog\nMarketStrategyPanel')
    box(ax, 3.2, 2.5, 2.4, 1.4, 'server/\nExpress · WebSocket\nllmClient · runRecorder')
    box(ax, 6.2, 2.5, 2.6, 1.4, 'adapter/\nsimulationEngine\ntradingRounds')
    box(ax, 3.5, 0.5, 3, 0.9, 'data/ + runs/预设运行版本')
    arrow(ax, 2.6, 3.2, 3.2, 3.2)
    arrow(ax, 5.6, 3.2, 6.2, 3.2)
    arrow(ax, 4.8, 2.5, 5, 1.4)
    ax.set_title('图4-1 系统体系结构', fontsize=12)
    save(fig, '图4-1-体系结构.png')


def fig4_4_sequence():
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis('off')
    steps = [
        '① 加载情景+本地价格',
        '② 三交易体 LLM 决策',
        '③ 汇总 peerDecisions',
        '④ 记忆审计官决策',
        '⑤ buildDebateRound',
        '⑥ buildLlmEvaluation',
        '⑦ WebSocket 广播',
    ]
    y = 6
    for i, s in enumerate(steps):
        box(ax, 1.5, y - i * 0.85, 7, 0.65, s, fc='#F0FDF4' if i % 2 else '#E8F4FC')
        if i < len(steps) - 1:
            arrow(ax, 5, y - i * 0.85, 5, y - (i + 1) * 0.85 + 0.65)
    ax.set_title('图4-4 单轮 LLM 仿真时序（36轮循环）', fontsize=12)
    save(fig, '图4-4-时序.png')


def fig4_6_evolution():
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis('off')
    nodes = ['自博弈\n四体并行', '收益评分', '失败归因', 'strategyPatchNotes', 'Prompt迭代\nv0→v1→v2', '测试段验证']
    x0 = 0.4
    for i, n in enumerate(nodes):
        box(ax, x0 + i * 1.55, 1.5, 1.35, 1.1, n, fc='#EDE9FE', ec='#7C3AED')
        if i < len(nodes) - 1:
            arrow(ax, x0 + (i + 1) * 1.55, 2.05, x0 + (i + 1) * 1.55 + 0.15, 2.05)
    ax.text(5, 0.5, '训练段 1–6 轮可进化；第4、7轮触发 prompt→promptv1→promptv2', ha='center', fontsize=9)
    ax.set_title('图4-6 自进化智能体学习闭环', fontsize=12)
    save(fig, '图4-6-自进化.png')


def fig4_5_decision():
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 5)
    ax.axis('off')
    box(ax, 3, 4, 3, 0.7, '市场输入 (价格/新闻/记忆)')
    for x, name in [(0.5, '保守型'), (2.5, '均衡型'), (4.5, '激进型')]:
        box(ax, x, 2.5, 1.6, 0.8, name)
        arrow(ax, 4.5, 4, x + 0.8, 3.3)
    box(ax, 6.5, 2.5, 2, 0.8, '记忆审计官\n(peerDecisions)')
    arrow(ax, 4.5, 4, 7.5, 3.3)
    box(ax, 3, 1, 3, 0.7, '辩论场 + 执行门控')
    arrow(ax, 1.3, 2.5, 3.5, 1.7)
    arrow(ax, 7.5, 2.5, 5.5, 1.7)
    save(fig, '图4-5-决策流程.png')


def fig4_7_eval():
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 4)
    ax.axis('off')
    box(ax, 0.5, 2.5, 1.8, 0.9, '动作+价格')
    box(ax, 2.8, 2.5, 1.8, 0.9, '单轮得分')
    box(ax, 5.1, 2.5, 1.8, 0.9, '累计/相对alpha')
    box(ax, 2.8, 0.8, 2.5, 0.9, '排名 1–4')
    arrow(ax, 2.3, 2.95, 2.8, 2.95)
    arrow(ax, 4.6, 2.95, 5.1, 2.95)
    arrow(ax, 6, 2.5, 4, 1.7)
    save(fig, '图4-7-评价闭环.png')


def fig4_2_function():
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 5)
    ax.axis('off')
    mods = ['数据管线', '情景引擎', 'LLM决策', '记忆审计', '辩论场', '策略评估', '运行展示']
    for i, m in enumerate(mods):
        box(ax, 0.3 + (i % 4) * 2.1, 3.2 - (i // 4) * 1.5, 1.9, 0.85, m)
    save(fig, '图4-2-功能结构.png')


def fig4_3_package():
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 4)
    ax.axis('off')
    for y, label in [(2.8, '<<frontend>>'), (1.6, '<<server>>'), (0.4, '<<adapter>>')]:
        box(ax, 1, y, 6, 0.9, label)
    save(fig, '图4-3-包图.png')


def fig4_8_er():
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 4)
    ax.axis('off')
    ents = ['智能体', '交易轮次', '决策记录', 'Prompt版本', '运行记录']
    for i, e in enumerate(ents):
        box(ax, 0.4 + i * 1.7, 1.5, 1.4, 0.8, e, fc='#FFF7ED')
    ax.text(4.5, 0.5, '1:N 关联：轮次—决策—评分—辩论—审计', ha='center', fontsize=9)
    save(fig, '图4-8-ER.png')


def fig4_9_data():
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 4)
    ax.axis('off')
    box(ax, 0.5, 2, 2, 1, 'commodities-\nhistorical.json')
    box(ax, 3, 2, 2, 1, 'tradingRounds\n(36)')
    box(ax, 5.5, 2, 2, 1, 'runs/rounds/*\njson 切片')
    arrow(ax, 2.5, 2.5, 3, 2.5)
    arrow(ax, 5, 2.5, 5.5, 2.5)
    save(fig, '图4-9-数据逻辑.png')


def fig4_10_deploy():
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.set_xlim(0, 7)
    ax.set_ylim(0, 4)
    ax.axis('off')
    box(ax, 0.5, 2, 2, 1, '浏览器\n:3102')
    box(ax, 3, 2, 2, 1, 'Node.js\n服务')
    box(ax, 5.5, 2, 1.5, 1, 'DeepSeek\nAPI')
    arrow(ax, 2.5, 2.5, 3, 2.5)
    arrow(ax, 5, 2.5, 5.5, 2.5)
    save(fig, '图4-10-部署.png')


def main():
    fig2_1()
    fig3_1()
    fig4_1()
    fig4_2_function()
    fig4_3_package()
    fig4_4_sequence()
    fig4_5_decision()
    fig4_6_evolution()
    fig4_7_eval()
    fig4_8_er()
    fig4_9_data()
    fig4_10_deploy()
    print('Done. Insert PNGs into Word for figures 2-1,3-1,4-1..4-10. Figures 5-1..5-3: see 论文截图清单.md')


if __name__ == '__main__':
    main()
