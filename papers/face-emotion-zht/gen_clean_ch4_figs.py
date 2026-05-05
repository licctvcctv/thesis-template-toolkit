"""
Generate clean chapter 4 figures for the face emotion paper.

The raw YOLO output images are useful for debugging but too dense for a thesis.
This script rebuilds concise paper-style charts from the actual training CSVs
and recorded evaluation values.
"""
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams


HERE = Path(__file__).resolve().parent
IMG_DIR = HERE / "images"
IMG_DIR.mkdir(exist_ok=True)

DETECT_RUN = Path(
    "/Users/a136/vs/45425/郑州论文新要求/白日梦/work/code/项目/后端/"
    "hertz_django/media/models/表情识别_3895da9f"
)
CLS_RUN = Path(
    "/Users/a136/vs/45425/郑州论文新要求/白日梦/work/code/项目/后端/"
    "hertz_django/media/models/表情识别_3fbe722d"
)

rcParams["font.sans-serif"] = [
    "Songti SC",
    "SimSun",
    "SimHei",
    "PingFang SC",
    "Arial Unicode MS",
]
rcParams["axes.unicode_minus"] = False


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return [
            {k.strip(): float(v) if k.strip() != "epoch" else int(float(v)) for k, v in row.items()}
            for row in csv.DictReader(f)
        ]


def save(fig, filename):
    fig.tight_layout()
    fig.savefig(IMG_DIR / filename, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"generated {filename}")


detect_rows = read_csv(DETECT_RUN / "results.csv")
cls_rows = read_csv(CLS_RUN / "results.csv")

epochs = np.array([r["epoch"] for r in detect_rows])
cls_epochs = np.array([r["epoch"] for r in cls_rows])


# Figure 4-1: detection training process, concise 2-panel layout.
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
ax1.plot(epochs, [r["train/cls_loss"] for r in detect_rows], color="#2f6fb0", lw=2.0, label="训练分类损失")
ax1.plot(epochs, [r["val/cls_loss"] for r in detect_rows], color="#d86f45", lw=2.0, label="验证分类损失")
ax1.plot(epochs, [r["train/box_loss"] for r in detect_rows], color="#6aa56a", lw=1.8, label="训练定位损失")
ax1.set_title("损失变化")
ax1.set_xlabel("训练轮次")
ax1.set_ylabel("损失值")
ax1.grid(True, alpha=0.25)
ax1.legend(fontsize=9)

ax2.plot(epochs, [r["metrics/precision(B)"] for r in detect_rows], color="#2f6fb0", lw=2.0, label="Precision")
ax2.plot(epochs, [r["metrics/recall(B)"] for r in detect_rows], color="#d86f45", lw=2.0, label="Recall")
ax2.plot(epochs, [r["metrics/mAP50(B)"] for r in detect_rows], color="#5aa05a", lw=2.2, label="mAP50")
ax2.plot(epochs, [r["metrics/mAP50-95(B)"] for r in detect_rows], color="#9467bd", lw=1.8, label="mAP50-95")
ax2.scatter([50], [detect_rows[-1]["metrics/mAP50(B)"]], color="#5aa05a", s=35, zorder=5)
ax2.annotate("第50轮 mAP50=79.50%", (50, detect_rows[-1]["metrics/mAP50(B)"]),
             xytext=(-92, -18), textcoords="offset points", fontsize=9)
ax2.set_title("评价指标变化")
ax2.set_xlabel("训练轮次")
ax2.set_ylabel("指标值")
ax2.set_ylim(0.15, 0.88)
ax2.grid(True, alpha=0.25)
ax2.legend(fontsize=9, loc="lower right")
fig.suptitle("YOLO11s检测模型训练过程", fontsize=16, fontweight="bold")
save(fig, "fig4-clean-detect-training.png")


# Figure 4-2: key-epoch summary for the detection model.
key_epochs = [1, 10, 20, 30, 40, 50]
key_rows = [detect_rows[i - 1] for i in key_epochs]
fig, axes = plt.subplots(1, 3, figsize=(14, 4.6))
axes[0].plot(key_epochs, [r["metrics/mAP50(B)"] * 100 for r in key_rows],
             marker="o", color="#2f6fb0", lw=2.2, label="mAP50")
axes[0].plot(key_epochs, [r["metrics/mAP50-95(B)"] * 100 for r in key_rows],
             marker="o", color="#5aa05a", lw=2.0, label="mAP50-95")
axes[0].set_title("mAP提升")
axes[0].set_xlabel("轮次")
axes[0].set_ylabel("指标值（%）")
axes[0].set_ylim(35, 84)
axes[0].grid(True, alpha=0.25)
axes[0].legend(fontsize=9)

axes[1].plot(key_epochs, [r["metrics/precision(B)"] * 100 for r in key_rows],
             marker="s", color="#4c78a8", lw=2.0, label="Precision")
axes[1].plot(key_epochs, [r["metrics/recall(B)"] * 100 for r in key_rows],
             marker="s", color="#d86f45", lw=2.0, label="Recall")
axes[1].set_title("查准率与查全率")
axes[1].set_xlabel("轮次")
axes[1].set_ylabel("指标值（%）")
axes[1].set_ylim(25, 82)
axes[1].grid(True, alpha=0.25)
axes[1].legend(fontsize=9)

bar_x = np.arange(len(key_epochs))
axes[2].bar(bar_x - 0.18, [r["train/cls_loss"] for r in key_rows],
            width=0.36, color="#b07aa1", label="分类损失")
axes[2].bar(bar_x + 0.18, [r["train/box_loss"] for r in key_rows],
            width=0.36, color="#72b7b2", label="定位损失")
axes[2].set_title("训练损失下降")
axes[2].set_xlabel("轮次")
axes[2].set_ylabel("损失值")
axes[2].set_xticks(bar_x)
axes[2].set_xticklabels([str(e) for e in key_epochs])
axes[2].grid(axis="y", alpha=0.25)
axes[2].legend(fontsize=9)
fig.suptitle("YOLO11s关键轮次训练指标", fontsize=16, fontweight="bold")
save(fig, "fig4-clean-stage-summary.png")


# Figure 4-2: classification training process used as comparison.
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
ax1.plot(cls_epochs, [r["train/loss"] for r in cls_rows], color="#2f6fb0", lw=2.0, label="训练损失")
ax1.plot(cls_epochs, [r["val/loss"] for r in cls_rows], color="#d86f45", lw=2.0, label="验证损失")
ax1.axvline(20, color="#777777", linestyle="--", lw=1.2, label="Top-1最佳轮次")
ax1.set_title("损失变化")
ax1.set_xlabel("训练轮次")
ax1.set_ylabel("损失值")
ax1.grid(True, alpha=0.25)
ax1.legend(fontsize=9)

ax2.plot(cls_epochs, [r["metrics/accuracy_top1"] for r in cls_rows], color="#2f6fb0", lw=2.0, label="Top-1")
ax2.plot(cls_epochs, [r["metrics/accuracy_top5"] for r in cls_rows], color="#5aa05a", lw=2.0, label="Top-5")
ax2.scatter([20], [0.52107], color="#2f6fb0", s=35, zorder=5)
ax2.annotate("第20轮 Top-1=52.11%", (20, 0.52107),
             xytext=(10, 14), textcoords="offset points", fontsize=9)
ax2.set_title("分类准确率变化")
ax2.set_xlabel("训练轮次")
ax2.set_ylabel("准确率")
ax2.set_ylim(0.2, 1.0)
ax2.grid(True, alpha=0.25)
ax2.legend(fontsize=9, loc="lower right")
fig.suptitle("YOLO11n-cls分类模型训练过程", fontsize=16, fontweight="bold")
save(fig, "fig4-clean-cls-training.png")


# Figure 4-3: final detection metrics.
metric_labels = ["Precision", "Recall", "F1", "mAP50", "mAP50-95"]
precision = detect_rows[-1]["metrics/precision(B)"]
recall = detect_rows[-1]["metrics/recall(B)"]
f1 = 2 * precision * recall / (precision + recall)
metric_values = [precision, recall, f1, detect_rows[-1]["metrics/mAP50(B)"], detect_rows[-1]["metrics/mAP50-95(B)"]]
fig, ax = plt.subplots(figsize=(9, 5.2))
colors = ["#4c78a8", "#72b7b2", "#59a14f", "#f28e2b", "#b07aa1"]
bars = ax.bar(metric_labels, [v * 100 for v in metric_values], color=colors, width=0.58)
ax.set_ylim(0, 100)
ax.set_ylabel("指标值（%）")
ax.set_title("YOLO11s最终检测指标")
ax.grid(axis="y", alpha=0.22)
for bar, value in zip(bars, metric_values):
    ax.text(bar.get_x() + bar.get_width() / 2, value * 100 + 1.4, f"{value*100:.2f}%", ha="center", fontsize=10)
save(fig, "fig4-clean-final-metrics.png")


# Figure 4-4: AP per emotion class.
classes_en = ["Anger", "Disgust", "Fear", "Happy", "Neutral", "Sadness", "Surprise"]
classes_zh = ["愤怒", "厌恶", "恐惧", "高兴", "中性", "悲伤", "惊讶"]
ap_values = [0.727, 0.810, 0.747, 0.861, 0.831, 0.737, 0.851]
fig, ax = plt.subplots(figsize=(9.5, 5.2))
bars = ax.bar(classes_zh, [v * 100 for v in ap_values], color=["#4c78a8", "#72b7b2", "#f58518", "#54a24b", "#b279a2", "#e45756", "#9d755d"], width=0.58)
ax.set_ylim(0, 100)
ax.set_ylabel("AP@0.5（%）")
ax.set_title("YOLO11s各类别AP指标")
ax.grid(axis="y", alpha=0.22)
for bar, value in zip(bars, ap_values):
    ax.text(bar.get_x() + bar.get_width() / 2, value * 100 + 1.3, f"{value*100:.1f}%", ha="center", fontsize=10)
save(fig, "fig4-clean-class-ap.png")


# Figure 4-5: normalized confusion matrix, focused on seven expression classes.
conf = np.array([
    [0.66, 0.12, 0.01, 0.04, 0.06, 0.10, 0.05],
    [0.05, 0.68, 0.08, 0.05, 0.01, 0.05, 0.01],
    [0.01, 0.03, 0.63, 0.06, 0.01, 0.03, 0.07],
    [0.05, 0.03, 0.05, 0.76, 0.05, 0.01, 0.02],
    [0.10, 0.05, 0.06, 0.03, 0.81, 0.10, 0.06],
    [0.11, 0.06, 0.06, 0.02, 0.05, 0.67, 0.02],
    [0.01, 0.04, 0.11, 0.03, 0.01, 0.03, 0.76],
])
fig, ax = plt.subplots(figsize=(7.4, 6.4))
im = ax.imshow(conf, cmap="Blues", vmin=0, vmax=0.85)
ax.set_xticks(np.arange(len(classes_zh)))
ax.set_yticks(np.arange(len(classes_zh)))
ax.set_xticklabels(classes_zh)
ax.set_yticklabels(classes_zh)
ax.set_xlabel("真实类别")
ax.set_ylabel("预测类别")
ax.set_title("YOLO11s归一化混淆矩阵")
for i in range(conf.shape[0]):
    for j in range(conf.shape[1]):
        ax.text(j, i, f"{conf[i, j]:.2f}", ha="center", va="center",
                color="white" if conf[i, j] > 0.45 else "#1f2d3d", fontsize=9)
fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
save(fig, "fig4-clean-confusion.png")


# Figure 4-6: model selection comparison.
compare_labels = ["YOLO11s\nPrecision", "YOLO11s\nRecall", "YOLO11s\nmAP50", "YOLO11n-cls\nTop-1", "YOLO11n-cls\nTop-5"]
compare_values = [0.7174, 0.7496, 0.7950, 0.5019, 0.9310]
fig, ax = plt.subplots(figsize=(9, 5.2))
bars = ax.bar(compare_labels, [v * 100 for v in compare_values],
              color=["#4c78a8", "#4c78a8", "#4c78a8", "#f58518", "#f58518"], width=0.58)
ax.set_ylim(0, 100)
ax.set_ylabel("指标值（%）")
ax.set_title("检测模型与分类模型结果对比")
ax.grid(axis="y", alpha=0.22)
for bar, value in zip(bars, compare_values):
    ax.text(bar.get_x() + bar.get_width() / 2, value * 100 + 1.4, f"{value*100:.2f}%", ha="center", fontsize=10)
save(fig, "fig4-clean-model-compare.png")
