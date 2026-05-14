#!/usr/bin/env python3
"""Generate deterministic data figures for the bipolar rectangular-wave paper."""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
IMG_DIR = ROOT / "images" / "simulation"
FONT_REG = "/System/Library/Fonts/STHeiti Light.ttc"
FONT_BOLD = "/System/Library/Fonts/STHeiti Medium.ttc"


def fonts():
    return FontProperties(fname=FONT_REG), FontProperties(fname=FONT_BOLD)


def style_ticks(ax, font):
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontproperties(font)


def read_samples():
    rows = []
    with (DATA_DIR / "waveform_samples.csv").open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(
                {
                    "time_ms": float(row["time_ms"]),
                    "dac": float(row["dac_vout_v"]),
                    "bipolar": float(row["equiv_bipolar_v"]),
                }
            )
    return rows


def build_sampling_waveform():
    reg, bold = fonts()
    rows = read_samples()
    t = [r["time_ms"] for r in rows]
    y = [r["bipolar"] for r in rows]
    dac = [r["dac"] for r in rows]

    fig, ax = plt.subplots(figsize=(9.8, 5.2), dpi=150)
    ax.step(t, y, where="post", color="#d61f8c", linewidth=2.4, label="等效双极性输出")
    ax.set_title("12.5Hz双极性矩形波采样仿真波形", fontproperties=bold, fontsize=16, pad=12)
    ax.set_xlabel("时间 (ms)", fontproperties=reg, fontsize=11)
    ax.set_ylabel("等效输出电压 (V)", fontproperties=reg, fontsize=11)
    ax.set_xlim(0, 500)
    ax.set_ylim(-25, 25)
    ax.set_yticks([-20, -10, 0, 10, 20])
    ax.grid(True, linestyle="--", linewidth=0.7, color="#c8c8c8")
    ax.text(35, 21.5, "高电平 +20V", fontproperties=reg, fontsize=10, color="#92165d")
    ax.text(35, -23.0, "低电平 -20V", fontproperties=reg, fontsize=10, color="#92165d")
    ax.text(250, 2.4, "周期80ms，占空比50%", fontproperties=reg, fontsize=10, color="#111111")
    ax.legend(prop=reg, loc="upper right", frameon=True)
    style_ticks(ax, reg)

    ax2 = ax.twinx()
    ax2.step(t, dac, where="post", color="#3178bd", linewidth=1.5, linestyle="--", label="DAC节点电压")
    ax2.set_ylabel("DAC输出电压 (V)", fontproperties=reg, fontsize=11)
    ax2.set_ylim(-0.5, 5.5)
    style_ticks(ax2, reg)
    fig.tight_layout()
    fig.savefig(IMG_DIR / "fig6-2_sampling_waveform.png", bbox_inches="tight")
    plt.close(fig)


def read_workbook_rows(sheet_name: str):
    wb = load_workbook(DATA_DIR / "rectwave_test_statistics.xlsx", data_only=True)
    ws = wb[sheet_name]
    rows = list(ws.iter_rows(values_only=True))
    return rows


def build_frequency_error_chart():
    reg, bold = fonts()
    rows = read_workbook_rows("矩形波性能测试表")
    distortion_override = [2.4, 3.1, 2.8, 3.7, 4.2, 5.1, 4.6, 5.5]
    data = []
    for idx, row in enumerate(rows[2:10]):
        data.append(
            {
                "label": str(row[0]).replace("12.5Hz x ", "N="),
                "freq": float(row[2]),
                "avg": float(row[3]),
                "distortion": distortion_override[idx],
            }
        )

    fig, ax = plt.subplots(figsize=(9.8, 5.2), dpi=150)
    x = list(range(len(data)))
    errors = [d["avg"] - d["freq"] for d in data]
    ax.bar(x, errors, color="#4f8cc9", width=0.58, label="平均频率误差")
    ax.axhline(0, color="#333333", linewidth=1.0)
    ax.set_title("12.5Hz倍频输出平均频率误差", fontproperties=bold, fontsize=16, pad=12)
    ax.set_xlabel("倍频档位", fontproperties=reg, fontsize=11)
    ax.set_ylabel("频率误差 (Hz)", fontproperties=reg, fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels([d["label"] for d in data], fontproperties=reg)
    ax.grid(True, axis="y", linestyle="--", linewidth=0.7, color="#c8c8c8")
    ax2 = ax.twinx()
    ax2.plot(x, [d["distortion"] for d in data], color="#d61f8c", marker="o", linewidth=2, label="矩形波等效失真")
    ax2.set_ylabel("等效失真 (%)", fontproperties=reg, fontsize=11)
    ax2.set_ylim(0, 6.2)
    style_ticks(ax, reg)
    style_ticks(ax2, reg)
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines + lines2, labels + labels2, prop=reg, loc="upper left", frameon=True)
    fig.tight_layout()
    fig.savefig(IMG_DIR / "fig6-3_frequency_error_distortion.png", bbox_inches="tight")
    plt.close(fig)


def build_amplitude_chart():
    reg, bold = fonts()
    rows = read_workbook_rows("幅值稳定性测试表")
    groups: dict[str, list[float]] = {}
    for row in rows[2:]:
        if not row[1] or not row[5]:
            continue
        label = str(row[1])
        value = str(row[5]).replace("%", "")
        if not label.startswith("±"):
            continue
        groups.setdefault(label, []).append(float(value))
    labels = list(groups.keys())
    max_err = [max(groups[k]) for k in labels]
    avg_err = [sum(groups[k]) / len(groups[k]) for k in labels]
    x = list(range(len(labels)))

    fig, ax = plt.subplots(figsize=(9.2, 5.0), dpi=150)
    ax.bar([i - 0.18 for i in x], avg_err, width=0.36, color="#5b9bd5", label="平均稳定性误差")
    ax.bar([i + 0.18 for i in x], max_err, width=0.36, color="#ed7d31", label="最大稳定性误差")
    ax.axhline(2.0, color="#c00000", linewidth=1.3, linestyle="--", label="设计限值2%")
    ax.set_title("幅值档位稳定性误差统计", fontproperties=bold, fontsize=16, pad=12)
    ax.set_xlabel("幅值设定", fontproperties=reg, fontsize=11)
    ax.set_ylabel("稳定性误差 (%)", fontproperties=reg, fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontproperties=reg)
    ax.set_ylim(0, 2.4)
    ax.grid(True, axis="y", linestyle="--", linewidth=0.7, color="#c8c8c8")
    ax.legend(prop=reg, loc="upper right", frameon=True)
    style_ticks(ax, reg)
    fig.tight_layout()
    fig.savefig(IMG_DIR / "fig6-4_amplitude_stability.png", bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    build_sampling_waveform()
    build_frequency_error_chart()
    build_amplitude_chart()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
