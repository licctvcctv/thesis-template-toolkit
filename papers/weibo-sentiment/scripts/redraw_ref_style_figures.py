from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import FancyArrowPatch, Rectangle


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "images"
FONT = FontProperties(fname="/System/Library/Fonts/STHeiti Medium.ttc")


def ax0(figsize):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, text, fs=13.5, fill="#FFFFFF", lw=1.2):
    ax.add_patch(Rectangle((x, y), w, h, linewidth=lw, edgecolor="black", facecolor=fill))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontproperties=FONT, fontsize=fs, color="black")


def label(ax, x, y, text, fs=12):
    ax.text(x, y, text, ha="center", va="center", fontproperties=FONT, fontsize=fs, color="black")


def arrow(ax, x1, y1, x2, y2):
    ax.add_patch(
        FancyArrowPatch(
            (x1, y1),
            (x2, y2),
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=1.1,
            color="black",
            connectionstyle="arc3,rad=0",
        )
    )


def save(fig, name):
    fig.savefig(OUT / name, dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def system_architecture():
    fig, ax = ax0((12.5, 6.8))
    label(ax, 17, 92, "数据采集层", 12)
    label(ax, 51, 92, "数据处理层", 12)
    label(ax, 84, 92, "应用展示层", 12)

    box(ax, 6, 66, 20, 12, "微博热搜 / 评论采集", 13)
    box(ax, 6, 46, 20, 12, "代理池 / 反爬策略", 13)
    box(ax, 6, 26, 20, 12, "MySQL原始库 / JSON", 13)

    box(ax, 36, 72, 28, 10, "ODS贴源层", 14)
    box(ax, 36, 57, 28, 10, "DWD明细层", 14)
    box(ax, 36, 42, 28, 10, "DWS汇总层", 14)
    box(ax, 36, 27, 28, 10, "ADS应用层", 14)
    box(ax, 31, 10, 18, 9, "Hive SQL", 12.5, fill="#F2F2F2")
    box(ax, 51, 10, 18, 9, "PySpark分析", 12.5, fill="#F2F2F2")

    box(ax, 74, 63, 20, 12, "Superset可视化大屏", 13)
    box(ax, 74, 43, 20, 12, "Matplotlib分析图表", 13)
    box(ax, 74, 23, 20, 12, "情感分类 / 趋势预测", 13)

    arrow(ax, 16, 66, 16, 58)
    arrow(ax, 16, 46, 16, 38)
    arrow(ax, 26, 32, 36, 32)
    arrow(ax, 50, 72, 50, 67)
    arrow(ax, 50, 57, 50, 52)
    arrow(ax, 50, 42, 50, 37)
    arrow(ax, 64, 62, 74, 69)
    arrow(ax, 64, 47, 74, 49)
    arrow(ax, 64, 32, 74, 29)

    save(fig, "11_system_architecture.png")


def etl_flow():
    fig, ax = ax0((8.8, 10.6))
    box(ax, 20, 86, 60, 10, "微博热搜与评论采集", 15)
    box(ax, 20, 71, 60, 10, "ODS贴源层：原始快照 / 话题表 / 评论表", 14)
    box(ax, 20, 56, 60, 10, "DWD明细层：清洗 / 分词 / 标注 / 规范化", 14)
    box(ax, 20, 41, 60, 10, "DWS汇总层：热度 / 情感 / 分类 / 活跃度聚合", 14)
    box(ax, 20, 26, 60, 10, "ADS应用层：16项指标 / 健康评分 / 预警指数", 14)
    box(ax, 20, 11, 60, 10, "可视化与模型消费：Superset / Matplotlib / 趋势预测", 13.5)
    for y1, y2 in [(86, 81), (71, 66), (56, 51), (41, 36), (26, 21)]:
        arrow(ax, 50, y1, 50, y2)
    save(fig, "12_etl_flow.png")


def indicator_map():
    fig, ax = ax0((12, 7.6))
    box(ax, 38, 82, 24, 9, "微博舆情指标体系", 14.5)
    box(ax, 4, 56, 24, 11, "情感分布分析域\n正向率 / 演变趋势 / 分类交叉", 12)
    box(ax, 38, 56, 24, 11, "话题热度分析域\n平均热度 / Top10 / 高频关键词", 12)
    box(ax, 72, 56, 24, 11, "舆情风险监控域\n预警指数 / 波动率 / 传播深度", 12)
    box(ax, 18, 26, 26, 11, "综合评价域\n互动活跃 / 存活中位数 / 分类分布", 12)
    box(ax, 56, 26, 26, 11, "复合融合域\n健康评分 / P/N比值 / 情感波动率", 12)
    for x, y in [(16, 67), (50, 67), (84, 67), (31, 37), (69, 37)]:
        arrow(ax, 50, 78, x, y)
    save(fig, "16_indicator_system_map.png")


def model_pipeline():
    fig, ax = ax0((13.2, 7.8))
    box(ax, 3, 68, 13, 10, "评论数据", 14)
    box(ax, 20, 68, 15, 10, "数据清洗", 14)
    box(ax, 39, 68, 15, 10, "特征构建", 14)
    box(ax, 58, 68, 15, 10, "模型训练", 14)
    box(ax, 77, 68, 15, 10, "性能评估", 14)
    box(ax, 34, 49, 25, 8.5, "词典自动标注 + TF-IDF", 12.5, fill="#F2F2F2")
    box(ax, 56, 49, 19, 8.5, "NB / LR / SVM / RF", 12.5, fill="#F2F2F2")
    box(ax, 56, 35, 19, 8.5, "多项式回归 7日预测", 12.5, fill="#F2F2F2")
    box(ax, 79, 49, 14, 8.5, "Acc / F1", 12.5, fill="#F2F2F2")
    box(ax, 73, 16, 22, 8.5, "Superset / Matplotlib", 12.5)

    arrow(ax, 16, 73, 20, 73)
    arrow(ax, 35, 73, 39, 73)
    arrow(ax, 54, 73, 58, 73)
    arrow(ax, 73, 73, 77, 73)
    arrow(ax, 46.5, 68, 46.5, 57.5)
    arrow(ax, 65.5, 68, 65.5, 57.5)
    arrow(ax, 65.5, 49, 65.5, 43.5)
    arrow(ax, 86, 68, 86, 57.5)
    arrow(ax, 86, 49, 86, 24.5)
    arrow(ax, 65.5, 35, 84, 24.5)

    save(fig, "13_model_pipeline.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    system_architecture()
    etl_flow()
    indicator_map()
    model_pipeline()


if __name__ == "__main__":
    main()
