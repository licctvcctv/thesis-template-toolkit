#!/usr/bin/env python3
"""Generate deterministic waveform figures used by Chapter 6."""
from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties


ROOT = Path(__file__).resolve().parents[1]
IMG_DIR = ROOT / "images"
FONT_REG = "/System/Library/Fonts/STHeiti Light.ttc"
FONT_BOLD = "/System/Library/Fonts/STHeiti Medium.ttc"


def sine(freq: float, t_ms: list[float], amp_mv: float) -> list[float]:
    return [amp_mv * math.sin(2 * math.pi * freq * t / 1000) for t in t_ms]


def period_label(freq: float) -> str:
    return f"{1000 / freq:.3f} ms"


def build_switching_figure(path: Path):
    amp_mv = 320.0
    switch_ms = 1000 / 375
    duration_ms = switch_ms + 4 * (1000 / 900)
    steps = 1800
    t_ms = [duration_ms * i / steps for i in range(steps + 1)]
    phase_at_switch = 2 * math.pi * 375 * switch_ms / 1000
    y = []
    for t in t_ms:
        if t <= switch_ms:
            y.append(amp_mv * math.sin(2 * math.pi * 375 * t / 1000))
        else:
            y.append(amp_mv * math.sin(phase_at_switch + 2 * math.pi * 900 * (t - switch_ms) / 1000))

    font_reg = FontProperties(fname=FONT_REG)
    font_bold = FontProperties(fname=FONT_BOLD)
    fig, ax = plt.subplots(figsize=(9.9, 5.2), dpi=150)
    ax.axvspan(0, switch_ms, color="#f8e6f2", alpha=0.75, label="375Hz仿真段")
    ax.axvspan(switch_ms, duration_ms, color="#e8f2fb", alpha=0.75, label="900Hz仿真段")
    ax.plot(t_ms, y, color="#1f5aa6", linewidth=2.5, label="相位连续输出")
    ax.axvline(switch_ms, color="#222222", linestyle="--", linewidth=1.4)
    ax.text(
        switch_ms + 0.08,
        286,
        "频率切换点",
        fontproperties=font_reg,
        fontsize=10,
        color="#111111",
    )
    ax.text(
        switch_ms * 0.26,
        -300,
        "375Hz输出段",
        fontproperties=font_reg,
        fontsize=10,
        color="#7a1f59",
    )
    ax.text(
        switch_ms + (duration_ms - switch_ms) * 0.34,
        -300,
        "900Hz输出段",
        fontproperties=font_reg,
        fontsize=10,
        color="#1f5a88",
    )
    ax.set_title("375Hz至900Hz仿真切换输出波形", fontproperties=font_bold, fontsize=16, pad=12)
    ax.set_xlabel("时间 (ms)", fontproperties=font_reg, fontsize=11)
    ax.set_ylabel("电压 (mV)", fontproperties=font_reg, fontsize=11)
    ax.set_xlim(0, duration_ms)
    ax.set_ylim(-360, 360)
    ax.grid(True, linestyle="--", color="#c9c9c9", linewidth=0.8)
    ax.legend(prop=font_reg, loc="upper right", frameon=True)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontproperties(font_reg)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def build_overlay_figure(
    path: Path,
    title: str,
    freq_a: float,
    freq_b: float,
    label_a: str,
    label_b: str,
    duration_ms: float | None = None,
):
    duration_ms = duration_ms or 1000 / freq_a
    amp_mv = 320.0
    steps = 1200
    t_ms = [duration_ms * i / steps for i in range(steps + 1)]
    y_a = sine(freq_a, t_ms, amp_mv)
    y_b = sine(freq_b, t_ms, amp_mv)

    font_reg = FontProperties(fname=FONT_REG)
    font_bold = FontProperties(fname=FONT_BOLD)
    fig, ax = plt.subplots(figsize=(9.9, 5.9), dpi=150)
    ax.plot(t_ms, y_a, color="#e62f9a", linewidth=2.6, label=label_a)
    ax.plot(t_ms, y_b, color="#3d98d4", linewidth=2.0, linestyle="--", label=label_b)
    ax.set_title(title, fontproperties=font_bold, fontsize=16, pad=12)
    ax.set_xlabel("时间 (ms)", fontproperties=font_reg, fontsize=11)
    ax.set_ylabel("电压 (mV)", fontproperties=font_reg, fontsize=11)
    ax.set_xlim(0, duration_ms)
    ax.set_ylim(-350, 350)
    ax.grid(True, linestyle="--", color="#c9c9c9", linewidth=0.8)
    ax.legend(prop=font_reg, loc="upper right", frameon=True)
    ax.text(
        duration_ms * 0.05,
        292,
        f"375Hz周期: {period_label(freq_a)}",
        fontproperties=font_reg,
        fontsize=10,
        color="#111111",
    )
    ax.text(
        duration_ms * 0.05,
        252,
        f"900Hz周期: {period_label(freq_b)}",
        fontproperties=font_reg,
        fontsize=10,
        color="#111111",
    )
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontproperties(font_reg)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    build_switching_figure(IMG_DIR / "simulation_waveform_375_900.png")
    build_overlay_figure(
        IMG_DIR / "measured_waveform_375_900.png",
        "375Hz与900Hz实测频率对应仿真波形对比",
        375.039,
        900.151,
        "375.039 Hz",
        "900.151 Hz",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
