"""Generate comparison tables and charts from evaluation_results.csv.

Outputs (all in results/):
  comparison_table.md     — ablation table + per-class AP
  bar_*.png               — bar charts for each metric
  scatter_tradeoff.png    — mAP vs Params / GFLOPs trade-off
  small_object_ap.png     — per-class AP50 for small-object categories

Usage:
  python compare_results.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from tabulate import tabulate

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR  = PROJECT_ROOT / "results"
CSV_PATH     = RESULTS_DIR  / "evaluation_results.csv"

# Color palette: baseline=blue, ablation1=teal, ablation2=orange, full=red
_PALETTE = {
    "YOLOv8s":            "#3498db",
    "YOLOv8s-Ghost":      "#1abc9c",
    "YOLOv8s-Ghost-CBAM": "#f39c12",
    "YOLOv8s-Improved":   "#e74c3c",
}

def _color(name):
    return _PALETTE.get(name, "#95a5a6")


def load_results():
    if not CSV_PATH.exists():
        print(f"Results file not found: {CSV_PATH}")
        print("Run evaluate_all.py first.")
        return None
    return pd.read_csv(CSV_PATH)


# ---------------------------------------------------------------------------
# Markdown table
# ---------------------------------------------------------------------------

def generate_markdown_table(df):
    summary_cols = ["model", "Params(M)", "GFLOPs", "mAP50", "mAP50-95", "FPS"]
    exist_cols   = [c for c in summary_cols if c in df.columns]

    md_path = RESULTS_DIR / "comparison_table.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# 模型对比实验结果\n\n")

        # --- Overall table ---
        f.write("## 整体性能对比（VisDrone2019-DET 测试集）\n\n")
        f.write(tabulate(df[exist_cols], headers="keys", tablefmt="pipe", showindex=False))
        f.write("\n\n")

        # --- Ablation table ---
        f.write("## 消融实验（各创新点贡献）\n\n")
        ablation_rows = []
        components = {
            "YOLOv8s":            ("—",  "—",    "—"),
            "YOLOv8s-Ghost":      ("✅", "—",    "—"),
            "YOLOv8s-Ghost-CBAM": ("✅", "✅",   "—"),
            "YOLOv8s-Improved":   ("✅", "✅",   "✅"),
        }
        for _, row in df.iterrows():
            name = row["model"]
            ghost, cbam, wiou = components.get(name, ("?", "?", "?"))
            ablation_rows.append({
                "模型": name,
                "Ghost轻量化": ghost,
                "CBAM注意力": cbam,
                "Wise-IoU损失": wiou,
                "Params(M)": row.get("Params(M)", "—"),
                "mAP50": row.get("mAP50", "—"),
                "mAP50-95": row.get("mAP50-95", "—"),
            })
        f.write(tabulate(ablation_rows, headers="keys", tablefmt="pipe", showindex=False))
        f.write("\n\n")

        # --- Improvement vs baseline ---
        baseline = df[df["model"] == "YOLOv8s"]
        improved = df[df["model"] != "YOLOv8s"]
        if not baseline.empty and not improved.empty:
            b50   = float(baseline["mAP50"].iloc[0])
            b5095 = float(baseline["mAP50-95"].iloc[0])
            f.write("## 相对基准改进量\n\n")
            delta_rows = []
            for _, row in improved.iterrows():
                delta_rows.append({
                    "模型": row["model"],
                    "ΔmAP50":    f"{row['mAP50']  - b50:+.4f}",
                    "ΔmAP50-95": f"{row['mAP50-95'] - b5095:+.4f}",
                    "ΔParams(M)": f"{row['Params(M)'] - float(baseline['Params(M)'].iloc[0]):+.2f}",
                })
            f.write(tabulate(delta_rows, headers="keys", tablefmt="pipe", showindex=False))
            f.write("\n\n")

        # --- Per-class AP50 ---
        small_cols = [c for c in df.columns if c.startswith("AP50_")]
        if small_cols:
            f.write("## 各类别 AP@50\n\n")
            class_df = df[["model"] + small_cols].copy()
            class_df.columns = [c.replace("AP50_", "") for c in class_df.columns]
            f.write(tabulate(class_df, headers="keys", tablefmt="pipe", showindex=False))
            f.write("\n")

    print(f"Markdown table saved to {md_path}")


# ---------------------------------------------------------------------------
# Bar charts
# ---------------------------------------------------------------------------

def plot_bar_charts(df):
    sns.set_theme(style="whitegrid")
    metrics = {
        "mAP50":     "mAP@50",
        "mAP50-95":  "mAP@50-95",
        "Params(M)": "Parameters (M)",
        "GFLOPs":    "GFLOPs",
        "FPS":       "FPS (batch=1)",
    }
    colors = [_color(n) for n in df["model"]]

    for col, label in metrics.items():
        if col not in df.columns:
            continue
        plot_df = df[pd.to_numeric(df[col], errors="coerce").notna()].copy()
        pcol    = [_color(n) for n in plot_df["model"]]

        fig, ax = plt.subplots(figsize=(9, 5))
        bars = ax.bar(plot_df["model"], plot_df[col], color=pcol,
                      edgecolor="white", linewidth=0.5)
        for bar, val in zip(bars, plot_df[col]):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.005 * plot_df[col].max(),
                f"{val:.2f}" if isinstance(val, float) else str(val),
                ha="center", va="bottom", fontsize=9, fontweight="bold",
            )
        ax.set_ylabel(label, fontsize=12)
        ax.set_title(f"模型对比：{label}", fontsize=13, fontweight="bold")
        plt.xticks(rotation=20, ha="right")
        plt.tight_layout()
        fig_path = RESULTS_DIR / f"bar_{col.replace('(','').replace(')','')}.png"
        fig.savefig(fig_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"  Saved: {fig_path.name}")


# ---------------------------------------------------------------------------
# Scatter: accuracy vs efficiency
# ---------------------------------------------------------------------------

def plot_scatter_tradeoff(df):
    if "mAP50-95" not in df.columns:
        return
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, xcol, xlabel in zip(axes, ["Params(M)", "GFLOPs"], ["Parameters (M)", "GFLOPs"]):
        if xcol not in df.columns:
            continue
        plot_df = df[
            pd.to_numeric(df[xcol],      errors="coerce").notna() &
            pd.to_numeric(df["mAP50-95"], errors="coerce").notna()
        ].copy()
        for _, row in plot_df.iterrows():
            name = row["model"]
            c    = _color(name)
            mk   = "*" if "Improved" in name else ("D" if "CBAM" in name else ("^" if "Ghost" in name else "o"))
            sz   = 200 if mk == "*" else 120
            ax.scatter(row[xcol], row["mAP50-95"],
                       c=c, marker=mk, s=sz, edgecolors="black", linewidth=0.5, zorder=5)
            ax.annotate(name, (row[xcol], row["mAP50-95"]),
                        textcoords="offset points", xytext=(5, 5), fontsize=8)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel("mAP@50-95", fontsize=12)
        ax.set_title(f"精度 vs {xlabel} 权衡", fontsize=12, fontweight="bold")
        ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fig_path = RESULTS_DIR / "scatter_tradeoff.png"
    fig.savefig(fig_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {fig_path.name}")


# ---------------------------------------------------------------------------
# Small object per-class AP bar chart
# ---------------------------------------------------------------------------

def plot_small_object_ap(df):
    small_cols = ["AP50_pedestrian", "AP50_people", "AP50_bicycle", "AP50_motor"]
    exist = [c for c in small_cols if c in df.columns]
    if not exist:
        print("  No per-class AP data.")
        return

    labels = [c.replace("AP50_", "") for c in exist]
    x      = range(len(df))
    width  = 0.18
    colors = [_color(n) for n in df["model"]]

    fig, ax = plt.subplots(figsize=(11, 5))
    for i, (col, lbl) in enumerate(zip(exist, labels)):
        offsets = [(j + (i - len(exist)/2 + 0.5) * width) for j in x]
        ax.bar(offsets, df[col], width, label=lbl,
               color=[plt.cm.Set2(i / len(exist))] * len(df),
               edgecolor="white", linewidth=0.5)

    ax.set_xticks(list(x))
    ax.set_xticklabels(df["model"], rotation=20, ha="right")
    ax.set_ylabel("AP@50", fontsize=12)
    ax.set_title("小目标类别 AP@50 对比", fontsize=13, fontweight="bold")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    fig_path = RESULTS_DIR / "small_object_ap.png"
    fig.savefig(fig_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {fig_path.name}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Generating Comparison Results")
    print("=" * 60)

    df = load_results()
    if df is None:
        return

    print(f"\nLoaded {len(df)} model(s) from {CSV_PATH.name}")

    print("\n--- Markdown Table ---")
    generate_markdown_table(df)

    print("\n--- Bar Charts ---")
    plot_bar_charts(df)

    print("\n--- Scatter Trade-off ---")
    plot_scatter_tradeoff(df)

    print("\n--- Small Object AP ---")
    plot_small_object_ap(df)

    print(f"\nAll outputs saved to {RESULTS_DIR}/")


if __name__ == "__main__":
    main()
