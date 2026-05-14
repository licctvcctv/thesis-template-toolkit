"""生成论文级别的实验结果图表.

输出（全部到 results/figures/）：
  fig1_training_curves.png   — 三模型 mAP 训练曲线（主图）
  fig2_loss_curves.png       — 三模型 Loss 收敛曲线
  fig3_bar_metrics.png       — 最优指标分组柱状图
  fig4_ablation.png          — 消融实验分步效果图
  fig5_efficiency.png        — 参数量/GFLOPs vs mAP 效率权衡
  fig6_radar.png             — 雷达图多维度对比
  fig7_pr_curve.png          — 各模型 PR 曲线拼图（引用 ultralytics 输出）
  fig8_confusion.png         — 混淆矩阵拼图（归一化版）
"""

import shutil
import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib.gridspec import GridSpec

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR     = PROJECT_ROOT / "runs"
OUT_DIR      = PROJECT_ROOT / "results" / "figures"

# ── 字体 ─────────────────────────────────────────────────────────
def _setup_font():
    candidates = ["Microsoft YaHei", "SimHei", "STSong", "DejaVu Sans"]
    avail = {f.name for f in font_manager.fontManager.ttflist}
    for name in candidates:
        if name in avail:
            matplotlib.rcParams.update({
                "font.family":        name,
                "axes.unicode_minus": False,
                "font.size":          11,
            })
            return name
    matplotlib.rcParams["axes.unicode_minus"] = False
    return "DejaVu Sans"

FONT = _setup_font()

# ── 模型配置 ──────────────────────────────────────────────────────
MODELS = [
    {
        "key":    "yolov8s",
        "label":  "YOLOv8s（基准）",
        "short":  "YOLOv8s",
        "color":  "#2980b9",
        "ls":     "-",
        "marker": "o",
        "params": 11.13,
        "gflops": 28.4,
    },
    {
        "key":    "yolov8s-ghost",
        "label":  "YOLOv8s-Ghost（消融1）",
        "short":  "YOLOv8s-Ghost",
        "color":  "#27ae60",
        "ls":     "--",
        "marker": "^",
        "params": 9.27,
        "gflops": 23.2,
    },
    {
        "key":    "yolov8s-ghost-cbam",
        "label":  "YOLOv8s-Ghost-CBAM（消融2）",
        "short":  "Ghost-CBAM",
        "color":  "#e67e22",
        "ls":     "-.",
        "marker": "s",
        "params": 9.30,
        "gflops": 23.3,
    },
]


def load(key):
    p = RUNS_DIR / key / "train" / "results.csv"
    if not p.exists():
        return None
    df = pd.read_csv(p)
    df.columns = df.columns.str.strip()
    return df


def best(df, col="metrics/mAP50(B)"):
    idx = df[col].idxmax()
    return df.loc[idx]


def smooth(y, w=5):
    if len(y) < w:
        return np.array(y)
    k = np.ones(w) / w
    return np.convolve(y, k, mode="same")


def save(fig, name):
    p = OUT_DIR / name
    fig.savefig(p, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  √ {name}")


# ════════════════════════════════════════════════════════════════════
# Fig 1  mAP 训练收敛曲线（主图）
# ════════════════════════════════════════════════════════════════════
def fig1_training_curves(data):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("图1  各模型 mAP 训练收敛曲线对比", fontsize=14, fontweight="bold", y=1.02)

    for ax, col, title, ylbl in [
        (axes[0], "metrics/mAP50(B)",    "mAP@50",    "mAP@50"),
        (axes[1], "metrics/mAP50-95(B)", "mAP@50-95", "mAP@50-95"),
    ]:
        for m in MODELS:
            df = data.get(m["key"])
            if df is None:
                continue
            ep  = df["epoch"].values
            raw = df[col].values
            sm  = smooth(raw, w=5)
            bv  = raw.max()
            bi  = raw.argmax()

            ax.plot(ep, sm, color=m["color"], lw=2.2, ls=m["ls"],
                    label=f"{m['short']}  (best {bv:.4f})")
            ax.scatter(ep[bi], raw[bi], color=m["color"], s=90,
                       zorder=6, edgecolors="white", lw=1.5)
            ax.annotate(
                f"{bv:.4f}",
                xy=(ep[bi], raw[bi]),
                xytext=(8, 4), textcoords="offset points",
                fontsize=9, color=m["color"], fontweight="bold",
            )

        ax.set_title(title, fontsize=12, pad=8)
        ax.set_xlabel("Epoch", fontsize=11)
        ax.set_ylabel(ylbl, fontsize=11)
        ax.legend(fontsize=9, loc="lower right", framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle=":")
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.3f"))
        ax.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    save(fig, "fig1_training_curves.png")


# ════════════════════════════════════════════════════════════════════
# Fig 2  Loss 收敛曲线（3×2）
# ════════════════════════════════════════════════════════════════════
def fig2_loss_curves(data):
    loss_cfgs = [
        ("train/box_loss", "val/box_loss",  "Box Loss"),
        ("train/cls_loss", "val/cls_loss",  "Cls Loss"),
        ("train/dfl_loss", "val/dfl_loss",  "DFL Loss"),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(15, 8), sharex=False)
    fig.suptitle("图2  各模型训练集与验证集损失收敛曲线", fontsize=14, fontweight="bold", y=1.02)

    for col_i, (tc, vc, lname) in enumerate(loss_cfgs):
        for row_i, (src, split_name) in enumerate([(tc, "训练集"), (vc, "验证集")]):
            ax = axes[row_i, col_i]
            for m in MODELS:
                df = data.get(m["key"])
                if df is None or src not in df.columns:
                    continue
                ep  = df["epoch"].values
                sm  = smooth(df[src].values, w=7)
                ax.plot(ep, sm, color=m["color"], lw=2, ls=m["ls"],
                        label=m["short"])

            ax.set_title(f"{split_name} {lname}", fontsize=11, pad=6)
            ax.set_xlabel("Epoch", fontsize=9)
            ax.set_ylabel("Loss", fontsize=9)
            ax.grid(True, alpha=0.3, linestyle=":")
            ax.spines[["top", "right"]].set_visible(False)
            if col_i == 0 and row_i == 0:
                ax.legend(fontsize=8.5, loc="upper right", framealpha=0.9)

    plt.tight_layout()
    save(fig, "fig2_loss_curves.png")


# ════════════════════════════════════════════════════════════════════
# Fig 3  最优指标分组柱状图
# ════════════════════════════════════════════════════════════════════
def fig3_bar_metrics(data):
    metric_cfgs = [
        ("metrics/mAP50(B)",    "mAP@50"),
        ("metrics/mAP50-95(B)", "mAP@50-95"),
        ("metrics/precision(B)","Precision"),
        ("metrics/recall(B)",   "Recall"),
    ]

    vals = {m["key"]: {} for m in MODELS}
    for m in MODELS:
        df = data.get(m["key"])
        if df is not None:
            br = best(df)
            for col, _ in metric_cfgs:
                vals[m["key"]][col] = float(br[col])

    x     = np.arange(len(metric_cfgs))
    width = 0.25
    offsets = np.linspace(-(len(MODELS)-1)*width/2, (len(MODELS)-1)*width/2, len(MODELS))

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.suptitle("图3  各模型最优 Epoch 性能指标对比", fontsize=14, fontweight="bold", y=1.02)

    bars_all = []
    for i, (m, offset) in enumerate(zip(MODELS, offsets)):
        v = [vals[m["key"]].get(col, 0) for col, _ in metric_cfgs]
        bars = ax.bar(x + offset, v, width, color=m["color"],
                      label=m["short"], edgecolor="white", linewidth=0.6,
                      alpha=0.88)
        bars_all.append(bars)
        for bar, val in zip(bars, v):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.003,
                f"{val:.4f}",
                ha="center", va="bottom", fontsize=8, fontweight="bold",
                color=m["color"],
            )

    # 基准虚线
    baseline = MODELS[0]
    for xi, (col, _) in enumerate(metric_cfgs):
        bv = vals[baseline["key"]].get(col, 0)
        ax.plot([xi - 0.45, xi + 0.45], [bv, bv],
                color=baseline["color"], lw=1.2, ls=":", alpha=0.7)

    ax.set_xticks(x)
    ax.set_xticklabels([lbl for _, lbl in metric_cfgs], fontsize=11)
    ax.set_ylabel("指标值", fontsize=11)
    ax.set_ylim(0, 0.60)
    ax.legend(fontsize=10, loc="upper right", framealpha=0.9)
    ax.grid(axis="y", alpha=0.3, linestyle=":")
    ax.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    save(fig, "fig3_bar_metrics.png")


# ════════════════════════════════════════════════════════════════════
# Fig 4  消融实验逐步叠加效果图
# ════════════════════════════════════════════════════════════════════
def fig4_ablation(data):
    steps = [
        ("YOLOv8s\n基准",     "yolov8s",            "×", "×", "×"),
        ("+ Ghost\n轻量主干", "yolov8s-ghost",       "√", "×", "×"),
        ("+ CBAM\n注意力",   "yolov8s-ghost-cbam",  "√", "√", "×"),
        ("+ Wise-IoU\n自适应损失", None,             "√", "√", "√"),
    ]

    m50_vals  = []
    m95_vals  = []
    param_vals = [11.13, 9.27, 9.30, 9.30]
    gflop_vals = [28.4,  23.2, 23.3, 23.3]

    for _, key, *_ in steps:
        df = data.get(key) if key else None
        if df is not None:
            br = best(df)
            m50_vals.append(float(br["metrics/mAP50(B)"]))
            m95_vals.append(float(br["metrics/mAP50-95(B)"]))
        else:
            m50_vals.append(None)
            m95_vals.append(None)

    labels = [s[0] for s in steps]
    colors = ["#2980b9", "#27ae60", "#e67e22", "#c0392b"]
    x = np.arange(len(steps))

    fig = plt.figure(figsize=(15, 6))
    gs  = GridSpec(1, 3, figure=fig, wspace=0.38)
    ax1 = fig.add_subplot(gs[0, :2])
    ax2 = fig.add_subplot(gs[0, 2])

    fig.suptitle("图4  消融实验：各创新组件逐步叠加效果", fontsize=14, fontweight="bold", y=1.03)

    # 左图：mAP 折线
    valid_x   = [i for i, v in enumerate(m50_vals) if v is not None]
    valid_m50 = [v for v in m50_vals if v is not None]
    valid_m95 = [v for v in m95_vals if v is not None]

    ax1.plot(valid_x, valid_m50, "o-", color="#2c3e50", lw=2.5,
             markersize=8, label="mAP@50", zorder=5)
    ax1.plot(valid_x, valid_m95, "s--", color="#7f8c8d", lw=2,
             markersize=7, label="mAP@50-95", zorder=5)

    for i, (xi, v50, v95) in enumerate(zip(valid_x, valid_m50, valid_m95)):
        ax1.scatter(xi, v50, color=colors[xi], s=100, zorder=6, edgecolors="white", lw=2)
        ax1.annotate(f"{v50:.4f}", xy=(xi, v50), xytext=(0, 10),
                     textcoords="offset points", ha="center",
                     fontsize=9.5, fontweight="bold", color=colors[xi])
        ax1.annotate(f"{v95:.4f}", xy=(xi, v95), xytext=(0, -16),
                     textcoords="offset points", ha="center",
                     fontsize=8.5, color="#7f8c8d")

    # 训练中标注
    if m50_vals[-1] is None:
        ax1.annotate("（训练中）", xy=(len(steps)-1, valid_m50[-1]),
                     xytext=(0, 25), textcoords="offset points",
                     ha="center", fontsize=9, color="#c0392b",
                     arrowprops=dict(arrowstyle="->", color="#c0392b"))

    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=10.5)
    ax1.set_ylabel("mAP 指标值", fontsize=11)
    ax1.set_ylim(0.32, 0.46)
    ax1.legend(fontsize=10, loc="lower right")
    ax1.grid(True, alpha=0.3, linestyle=":")
    ax1.spines[["top", "right"]].set_visible(False)

    # 右图：参数量 & GFLOPs 对比
    w = 0.35
    xr = np.arange(len(steps))
    b1 = ax2.bar(xr - w/2, param_vals, w, label="参数量(M)", color="#3498db",
                 alpha=0.85, edgecolor="white")
    b2 = ax2.bar(xr + w/2, gflop_vals, w, label="GFLOPs", color="#e74c3c",
                 alpha=0.85, edgecolor="white")
    for bar, v in zip(b1, param_vals):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                 f"{v}", ha="center", fontsize=8.5, color="#3498db", fontweight="bold")
    for bar, v in zip(b2, gflop_vals):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                 f"{v}", ha="center", fontsize=8.5, color="#e74c3c", fontweight="bold")
    ax2.set_xticks(xr)
    ax2.set_xticklabels([s[0].split("\n")[0] for s in steps], fontsize=9, rotation=15)
    ax2.set_ylabel("参数量(M) / GFLOPs", fontsize=10)
    ax2.legend(fontsize=9)
    ax2.grid(axis="y", alpha=0.3, linestyle=":")
    ax2.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    save(fig, "fig4_ablation.png")


# ════════════════════════════════════════════════════════════════════
# Fig 5  效率权衡散点图
# ════════════════════════════════════════════════════════════════════
def fig5_efficiency(data):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("图5  精度 vs 计算效率权衡分析", fontsize=14, fontweight="bold", y=1.02)

    for ax, xcol, xlabel in [
        (axes[0], "params", "参数量 (M)"),
        (axes[1], "gflops", "GFLOPs"),
    ]:
        for m in MODELS:
            df = data.get(m["key"])
            if df is None:
                continue
            m50  = float(best(df)["metrics/mAP50(B)"])
            xval = m[xcol]
            mk   = "o" if m["key"] == "yolov8s" else ("^" if "ghost" == m["key"].split("-")[-1] else "s")
            ax.scatter(xval, m50, c=m["color"], s=250, marker=mk,
                       edgecolors="black", lw=1, zorder=5)
            ax.annotate(
                m["short"],
                xy=(xval, m50),
                xytext=(8, 4), textcoords="offset points",
                fontsize=9.5, color=m["color"], fontweight="bold",
            )

        ax.set_xlabel(xlabel, fontsize=11)
        ax.set_ylabel("mAP@50", fontsize=11)
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.3f"))
        ax.grid(True, alpha=0.3, linestyle=":")
        ax.spines[["top", "right"]].set_visible(False)

        # 右箭头注释
        ax.annotate("精度更高 →", xy=(0.98, 0.95), xycoords="axes fraction",
                    ha="right", fontsize=9, color="gray")
        ax.annotate("← 效率更高", xy=(0.02, 0.05), xycoords="axes fraction",
                    ha="left", fontsize=9, color="gray")

    plt.tight_layout()
    save(fig, "fig5_efficiency.png")


# ════════════════════════════════════════════════════════════════════
# Fig 6  雷达图
# ════════════════════════════════════════════════════════════════════
def fig6_radar(data):
    metrics_cfg = [
        ("metrics/mAP50(B)",    "mAP@50",    0.35, 0.42),
        ("metrics/mAP50-95(B)", "mAP@50-95", 0.20, 0.26),
        ("metrics/precision(B)","Precision",  0.44, 0.56),
        ("metrics/recall(B)",   "Recall",     0.35, 0.42),
    ]
    # 额外加轻量化维度（反向：参数越少分越高）
    radar_labels = [lbl for _, lbl, *_ in metrics_cfg] + ["轻量化"]

    N = len(radar_labels)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"polar": True})
    fig.suptitle("图6  各模型多维度性能雷达图", fontsize=14, fontweight="bold", y=1.02)

    max_params = 11.13

    for m in MODELS:
        df = data.get(m["key"])
        if df is None:
            continue
        br = best(df)
        vals = []
        for col, _, lo, hi in metrics_cfg:
            v = float(br[col])
            vals.append((v - lo) / (hi - lo + 1e-9))  # 归一化 0-1
        # 轻量化：参数越少越好（归一化）
        lightness = 1 - (m["params"] - 9.0) / (max_params - 9.0 + 1e-9)
        vals.append(lightness)

        vals_plot = vals + [vals[0]]
        ax.plot(angles, vals_plot, color=m["color"], lw=2.2, ls=m["ls"],
                label=m["short"])
        ax.fill(angles, vals_plot, color=m["color"], alpha=0.12)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(radar_labels, fontsize=11)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0.25", "0.50", "0.75", "1.00"], fontsize=8, color="gray")
    ax.grid(color="gray", alpha=0.3)
    ax.legend(fontsize=10, loc="upper right", bbox_to_anchor=(1.25, 1.1))

    plt.tight_layout()
    save(fig, "fig6_radar.png")


# ════════════════════════════════════════════════════════════════════
# Fig 7  PR 曲线拼图（直接引用 ultralytics 生成图）
# ════════════════════════════════════════════════════════════════════
def fig7_pr_curves():
    from PIL import Image
    titles = ["YOLOv8s（基准）", "YOLOv8s-Ghost（消融1）", "YOLOv8s-Ghost-CBAM（消融2）"]
    imgs   = []
    for m in MODELS:
        p = RUNS_DIR / m["key"] / "train" / "BoxPR_curve.png"
        if p.exists():
            imgs.append((titles[MODELS.index(m)], Image.open(p)))

    if not imgs:
        print("  ! fig7 跳过（PR 曲线文件未找到）")
        return

    n   = len(imgs)
    fig, axes = plt.subplots(1, n, figsize=(7 * n, 6))
    if n == 1:
        axes = [axes]
    fig.suptitle("图7  各模型 Precision-Recall 曲线对比", fontsize=14,
                 fontweight="bold", y=1.02)

    for ax, (title, img) in zip(axes, imgs):
        ax.imshow(np.array(img))
        ax.set_title(title, fontsize=11, pad=8)
        ax.axis("off")

    plt.tight_layout()
    save(fig, "fig7_pr_curves.png")


# ════════════════════════════════════════════════════════════════════
# Fig 8  混淆矩阵拼图
# ════════════════════════════════════════════════════════════════════
def fig8_confusion():
    from PIL import Image
    titles = ["YOLOv8s（基准）", "YOLOv8s-Ghost（消融1）", "YOLOv8s-Ghost-CBAM（消融2）"]
    imgs   = []
    for m in MODELS:
        p = RUNS_DIR / m["key"] / "train" / "confusion_matrix_normalized.png"
        if p.exists():
            imgs.append((titles[MODELS.index(m)], Image.open(p)))

    if not imgs:
        print("  ! fig8 跳过（混淆矩阵文件未找到）")
        return

    n   = len(imgs)
    fig, axes = plt.subplots(1, n, figsize=(7 * n, 7))
    if n == 1:
        axes = [axes]
    fig.suptitle("图8  各模型归一化混淆矩阵对比", fontsize=14,
                 fontweight="bold", y=1.02)

    for ax, (title, img) in zip(axes, imgs):
        ax.imshow(np.array(img))
        ax.set_title(title, fontsize=11, pad=8)
        ax.axis("off")

    plt.tight_layout()
    save(fig, "fig8_confusion.png")


# ════════════════════════════════════════════════════════════════════
# Main
# ════════════════════════════════════════════════════════════════════
def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"字体: {FONT}")
    print(f"输出目录: {OUT_DIR}\n")

    # 加载数据
    data = {}
    for m in MODELS:
        df = load(m["key"])
        if df is not None:
            data[m["key"]] = df
            br = best(df)
            print(f"  √ {m['short']:25s} epochs={len(df):3d}  "
                  f"best_ep={int(br['epoch']):3d}  "
                  f"mAP50={br['metrics/mAP50(B)']:.5f}  "
                  f"mAP50-95={br['metrics/mAP50-95(B)']:.5f}")
        else:
            print(f"  × {m['short']:25s} results.csv 未找到")

    if not data:
        print("\n[错误] 无数据，请先训练模型。")
        sys.exit(1)

    print("\n生成图表...")
    fig1_training_curves(data)
    fig2_loss_curves(data)
    fig3_bar_metrics(data)
    fig4_ablation(data)
    fig5_efficiency(data)
    fig6_radar(data)
    fig7_pr_curves()
    fig8_confusion()

    print(f"\n{'='*50}")
    print(f"完成！共 8 张图表，保存于：\n{OUT_DIR}")
    print("="*50)


if __name__ == "__main__":
    main()
