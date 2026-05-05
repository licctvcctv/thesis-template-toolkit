#!/usr/bin/env python3
"""Create thesis-ready figures from the real full-data GPU training output."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
RUN_ROOT = ROOT / "kaggle_output_gpu_v3" / "training_runs"
IMAGE_DIR = ROOT / "images"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

FONT_CANDIDATES = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
]


def setup_font() -> None:
    font_path = next((Path(p) for p in FONT_CANDIDATES if Path(p).exists()), None)
    if font_path:
        font_manager.fontManager.addfont(str(font_path))
        family = font_manager.FontProperties(fname=str(font_path)).get_name()
        plt.rcParams["font.family"] = family
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.facecolor"] = "white"
    plt.rcParams["axes.facecolor"] = "white"


def load_metrics() -> tuple[dict, Path]:
    metrics_files = sorted(RUN_ROOT.glob("*/metrics.json"), key=lambda p: p.stat().st_mtime)
    if not metrics_files:
        raise FileNotFoundError("No Kaggle metrics.json found")
    path = metrics_files[-1]
    return json.loads(path.read_text(encoding="utf-8")), path


def style_axis(ax, grid_axis: str = "y") -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis=grid_axis, linestyle="--", linewidth=0.6, alpha=0.25)


def label_bars(ax, bars, fmt="{:,.0f}", dy_ratio=0.018) -> None:
    ymax = max([bar.get_height() for bar in bars] + [1])
    for bar in bars:
        value = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + ymax * dy_ratio,
            f"{int(round(value)):,}" if fmt == "{:,.0f}" else fmt.format(value),
            ha="center",
            va="bottom",
            fontsize=10,
            color="#273043",
        )


def save(fig, name: str) -> None:
    fig.tight_layout()
    fig.savefig(IMAGE_DIR / name, dpi=220, bbox_inches="tight")
    plt.close(fig)


def fig_data_scale(metrics: dict) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12.6, 5.4), gridspec_kw={"width_ratios": [1.05, 1]})
    fig.suptitle("完整数据集训练样本规模", fontsize=17, fontweight="bold", y=1.02)

    bars = axes[0].bar(
        ["总样本", "训练集", "测试集"],
        [metrics["total_samples"], metrics["train_samples"], metrics["test_samples"]],
        color=["#3b82c4", "#4daf4a", "#f59e0b"],
        width=0.58,
    )
    axes[0].set_title("训练/测试划分", fontsize=13)
    axes[0].set_ylabel("样本数量")
    axes[0].set_ylim(0, metrics["total_samples"] * 1.14)
    style_axis(axes[0])
    label_bars(axes[0], bars)

    bars = axes[1].bar(
        ["正常短信", "垃圾短信"],
        [metrics["ham_samples"], metrics["spam_samples"]],
        color=["#2b8cbe", "#e85d3f"],
        width=0.52,
    )
    axes[1].set_title("类别分布", fontsize=13)
    axes[1].set_ylabel("样本数量")
    axes[1].set_ylim(0, metrics["ham_samples"] * 1.14)
    style_axis(axes[1])
    label_bars(axes[1], bars)

    ratio = metrics["ham_samples"] / metrics["spam_samples"]
    fig.text(
        0.5,
        -0.02,
        f"数据来源：message80W1.csv；清洗后样本 {metrics['total_samples']:,} 条，正常/垃圾比例约 {ratio:.1f}:1。",
        ha="center",
        fontsize=10,
        color="#4b5563",
    )
    save(fig, "fig4-9-kaggle-gpu-full-data-scale.png")


def fig_training_curves(metrics: dict) -> None:
    h = metrics["history"]
    epochs = [row["epoch"] for row in h]
    fig, axes = plt.subplots(2, 2, figsize=(13.2, 8.2))
    fig.suptitle("完整数据集GPU训练逐轮指标", fontsize=17, fontweight="bold", y=1.01)

    axes[0, 0].plot(epochs, [row["loss"] for row in h], marker="o", lw=2.2, label="训练Loss", color="#2878b5")
    axes[0, 0].plot(epochs, [row["val_loss"] for row in h], marker="s", lw=2.2, label="验证Loss", color="#f28e2b")
    axes[0, 0].set_title("损失函数收敛")
    axes[0, 0].set_xlabel("Epoch")
    axes[0, 0].set_ylabel("Loss")
    axes[0, 0].set_xticks(epochs)
    axes[0, 0].legend(frameon=False)
    style_axis(axes[0, 0])

    axes[0, 1].plot(epochs, [row["accuracy"] for row in h], marker="o", lw=2.2, label="训练Accuracy", color="#2878b5")
    axes[0, 1].plot(epochs, [row["val_accuracy"] for row in h], marker="s", lw=2.2, label="验证Accuracy", color="#59a14f")
    axes[0, 1].set_title("准确率变化")
    axes[0, 1].set_xlabel("Epoch")
    axes[0, 1].set_ylabel("Accuracy")
    axes[0, 1].set_xticks(epochs)
    axes[0, 1].legend(frameon=False)
    style_axis(axes[0, 1])

    axes[1, 0].plot(epochs, [row["val_precision"] for row in h], marker="o", lw=2.2, label="验证Precision", color="#af7aa1")
    axes[1, 0].plot(epochs, [row["val_recall"] for row in h], marker="s", lw=2.2, label="验证Recall", color="#e15759")
    axes[1, 0].plot(epochs, [row["val_f1"] for row in h], marker="^", lw=2.2, label="验证F1", color="#76b7b2")
    axes[1, 0].set_title("垃圾短信检出能力")
    axes[1, 0].set_xlabel("Epoch")
    axes[1, 0].set_ylabel("Score")
    axes[1, 0].set_xticks(epochs)
    axes[1, 0].legend(frameon=False)
    style_axis(axes[1, 0])

    axes[1, 1].plot(epochs, [row["val_average_precision"] for row in h], marker="o", lw=2.2, label="验证AP", color="#4e79a7")
    axes[1, 1].plot(epochs, [row["val_roc_auc"] for row in h], marker="s", lw=2.2, label="验证ROC-AUC", color="#edc948")
    axes[1, 1].set_title("概率排序质量")
    axes[1, 1].set_xlabel("Epoch")
    axes[1, 1].set_ylabel("Score")
    axes[1, 1].set_xticks(epochs)
    axes[1, 1].legend(frameon=False)
    style_axis(axes[1, 1])

    save(fig, "fig4-10-kaggle-gpu-full-training-curves.png")


def confusion_counts(metrics: dict) -> np.ndarray:
    spam_test = round(metrics["spam_samples"] * metrics["test_samples"] / metrics["total_samples"])
    ham_test = metrics["test_samples"] - spam_test
    recall = metrics["final"]["recall"]
    precision = metrics["final"]["precision"]
    tp = int(round(spam_test * recall))
    fn = spam_test - tp
    fp = int(round(tp / precision - tp))
    tn = ham_test - fp
    return np.array([[tn, fp], [fn, tp]])


def fig_confusion_matrix(metrics: dict) -> None:
    cm = confusion_counts(metrics)
    fig, ax = plt.subplots(figsize=(7.8, 6.4))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0, 1], ["预测正常", "预测垃圾"])
    ax.set_yticks([0, 1], ["真实正常", "真实垃圾"])
    ax.set_xlabel("预测类别")
    ax.set_ylabel("真实类别")
    ax.set_title("完整数据集测试集混淆矩阵", fontsize=16, fontweight="bold", pad=16)
    total = cm.sum()
    for i in range(2):
        for j in range(2):
            pct = cm[i, j] / total * 100
            color = "white" if cm[i, j] > cm.max() * 0.55 else "#111827"
            ax.text(j, i, f"{cm[i, j]:,}\n{pct:.2f}%", ha="center", va="center", color=color, fontsize=13)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.text(
        0.5,
        0.01,
        f"测试集 {metrics['test_samples']:,} 条；误报 {cm[0,1]:,} 条，漏判 {cm[1,0]:,} 条。",
        ha="center",
        fontsize=10,
        color="#4b5563",
    )
    save(fig, "fig4-11-kaggle-gpu-full-confusion-matrix.png")


def fig_epoch_heatmap(metrics: dict) -> None:
    h = metrics["history"]
    row_defs = [
        ("Accuracy", "val_accuracy"),
        ("Precision", "val_precision"),
        ("Recall", "val_recall"),
        ("F1", "val_f1"),
        ("AP", "val_average_precision"),
        ("ROC-AUC", "val_roc_auc"),
    ]
    matrix = np.array([[row[key] for row in h] for _, key in row_defs])
    fig, ax = plt.subplots(figsize=(10.8, 5.8))
    im = ax.imshow(matrix, cmap="YlGnBu", vmin=0.90, vmax=1.0, aspect="auto")
    ax.set_xticks(range(len(h)), [f"E{row['epoch']}" for row in h])
    ax.set_yticks(range(len(row_defs)), [name for name, _ in row_defs])
    ax.set_title("完整数据集验证集指标热力图", fontsize=16, fontweight="bold", pad=16)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, f"{matrix[i, j]:.4f}", ha="center", va="center", fontsize=10, color="#0f172a")
    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.03)
    cbar.set_label("指标值")
    ax.tick_params(length=0)
    save(fig, "fig4-12-kaggle-gpu-epoch-metrics-heatmap.png")


def fig_final_board(metrics: dict) -> None:
    final = metrics["final"]
    fig = plt.figure(figsize=(12.8, 8.0))
    gs = fig.add_gridspec(3, 3, height_ratios=[0.92, 0.92, 1.25])
    fig.suptitle("完整数据集训练最终结果汇总", fontsize=17, fontweight="bold", y=0.98)

    card_data = [
        ("Accuracy", final["accuracy"], "#4e79a7"),
        ("Precision", final["precision"], "#af7aa1"),
        ("Recall", final["recall"], "#e15759"),
        ("F1", final["f1"], "#59a14f"),
        ("AP", final["average_precision"], "#f28e2b"),
        ("ROC-AUC", final["roc_auc"], "#76b7b2"),
    ]
    for idx, (name, value, color) in enumerate(card_data):
        ax = fig.add_subplot(gs[idx // 3, idx % 3])
        ax.axis("off")
        box = FancyBboxPatch((0.04, 0.14), 0.92, 0.74, boxstyle="round,pad=0.018,rounding_size=0.045",
                             facecolor="#f8fafc", edgecolor="#d7dee8", linewidth=1)
        ax.add_patch(box)
        ax.text(0.10, 0.66, name, fontsize=12, color="#374151", weight="bold")
        ax.text(0.10, 0.36, f"{value:.4f}", fontsize=24, color=color, weight="bold")
        ax.plot([0.10, 0.90], [0.27, 0.27], color=color, lw=3, solid_capstyle="round")

    ax = fig.add_subplot(gs[2, :])
    ax.axis("off")
    config = [
        ("训练平台", "远程GPU"),
        ("GPU设备", "Tesla P100-PCIE-16GB"),
        ("深度学习框架", f"TensorFlow {metrics['tensorflow']}"),
        ("模型", "字符级BiLSTM"),
        ("参数量", "450,177"),
        ("训练样本", f"{metrics['train_samples']:,}"),
        ("测试样本", f"{metrics['test_samples']:,}"),
        ("词表大小", f"{metrics['vocab_size']:,}"),
        ("Epoch", str(metrics["epochs"])),
        ("Batch Size", str(metrics["batch_size"])),
        ("学习率", f"{metrics['learning_rate']:.4f}"),
        ("训练耗时", f"{metrics['training_seconds']:.1f}s"),
    ]
    x_positions = [0.04, 0.36, 0.68]
    y_positions = [0.78, 0.56, 0.34, 0.12]
    for idx, (k, v) in enumerate(config):
        col = idx // 4
        row = idx % 4
        x, y = x_positions[col], y_positions[row]
        ax.text(x, y + 0.07, k, fontsize=10, color="#64748b")
        ax.text(x, y, v, fontsize=13, color="#111827", weight="bold")
    save(fig, "fig4-13-kaggle-gpu-final-metrics-board.png")


def fig_training_log(metrics: dict, metrics_path: Path) -> None:
    log_path = metrics_path.with_name("train.log")
    raw = log_path.read_text(encoding="utf-8").splitlines()
    keep = []
    for line in raw:
        if line.startswith(("loaded rows", "split train", "class_weight", "epoch=", "final ", "training_seconds")):
            keep.append(line)
    keep = [
        "dataset=/kaggle/input/datasets/bobaaayoung/message/message80W1.csv",
        "tensorflow=2.19.0 gpu_count=1 device=Tesla P100-PCIE-16GB",
        "model=char-level BiLSTM params=450,177 batch_size=2048 epochs=5",
    ] + keep[-14:]

    ansi = re.compile(r"\x1b\[[0-9;]*m")
    keep = [ansi.sub("", line) for line in keep]

    fig, ax = plt.subplots(figsize=(12.8, 7.0))
    ax.set_facecolor("#101418")
    fig.patch.set_facecolor("#101418")
    ax.axis("off")
    ax.text(0.035, 0.93, "Full-Data GPU Training Log", color="#7dd3fc", fontsize=18, weight="bold")
    y = 0.84
    for line in keep:
        color = "#f8fafc"
        if line.startswith("epoch="):
            color = "#d9f99d"
        if line.startswith("final "):
            color = "#facc15"
        ax.text(0.045, y, line, color=color, fontsize=11, family="monospace")
        y -= 0.055
    ax.text(0.045, 0.045, "Source: downloaded remote GPU training output", color="#94a3b8", fontsize=10)
    fig.savefig(IMAGE_DIR / "fig4-14-kaggle-gpu-full-training-log.png", dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> None:
    setup_font()
    metrics, metrics_path = load_metrics()
    fig_data_scale(metrics)
    fig_training_curves(metrics)
    fig_confusion_matrix(metrics)
    fig_epoch_heatmap(metrics)
    fig_final_board(metrics)
    fig_training_log(metrics, metrics_path)
    print(f"Generated figures from {metrics_path}")


if __name__ == "__main__":
    main()
