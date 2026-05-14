#!/usr/bin/env python3
"""Generate supplemental theory figures for chapters 2 and 3."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
IMG_DIR = ROOT / "images"
FONT_REG = "/System/Library/Fonts/STHeiti Light.ttc"
FONT_BOLD = "/System/Library/Fonts/STHeiti Medium.ttc"


def fonts():
    return FontProperties(fname=FONT_REG), FontProperties(fname=FONT_BOLD)


def style_axis(ax, font):
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontproperties(font)


def triangle_wave(t, carrier_freq):
    phase = (t * carrier_freq) % 1.0
    return 4 * np.abs(phase - 0.5) - 1


def build_spwm_principle():
    reg, bold = fonts()
    t = np.linspace(0, 1, 2600)
    ref = 0.78 * np.sin(2 * np.pi * t)
    carrier = triangle_wave(t, 18)
    pwm = np.where(ref >= carrier, 1.0, 0.0)

    fig, axes = plt.subplots(2, 1, figsize=(10.2, 5.4), dpi=180, sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    axes[0].plot(t, ref, color="#d61f8c", linewidth=2.2, label="正弦参考波")
    axes[0].plot(t, carrier, color="#3f7fbf", linewidth=1.2, alpha=0.9, label="三角载波")
    axes[0].set_ylabel("归一化幅值", fontproperties=reg, fontsize=11)
    axes[0].set_title("SPWM调制机理示意图", fontproperties=bold, fontsize=16, pad=10)
    axes[0].grid(True, linestyle="--", color="#cfcfcf", linewidth=0.7)
    axes[0].legend(prop=reg, loc="upper right", frameon=True)
    axes[0].set_ylim(-1.15, 1.15)

    axes[1].step(t, pwm, where="post", color="#222222", linewidth=1.5, label="PWM脉冲序列")
    axes[1].fill_between(t, 0, pwm, step="post", color="#f4b183", alpha=0.55)
    axes[1].set_xlabel("归一化时间", fontproperties=reg, fontsize=11)
    axes[1].set_ylabel("开关状态", fontproperties=reg, fontsize=11)
    axes[1].set_yticks([0, 1])
    axes[1].grid(True, linestyle="--", color="#d8d8d8", linewidth=0.7)
    axes[1].legend(prop=reg, loc="upper right", frameon=True)
    style_axis(axes[0], reg)
    style_axis(axes[1], reg)
    fig.tight_layout()
    fig.savefig(IMG_DIR / "spwm_modulation_principle.png", bbox_inches="tight")
    plt.close(fig)


def add_box(ax, xy, text, width=1.75, height=0.72, fill="#f7fbff", edge="#4f81bd", bold=False):
    reg, bold_font = fonts()
    x, y = xy
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.035,rounding_size=0.035",
        linewidth=1.35,
        edgecolor=edge,
        facecolor=fill,
    )
    ax.add_patch(patch)
    ax.text(x + width / 2, y + height / 2, text, ha="center", va="center", fontproperties=bold_font if bold else reg, fontsize=10.5)
    return (x + width, y + height / 2), (x, y + height / 2)


def add_arrow(ax, start, end, label=None):
    reg, _ = fonts()
    arrow = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=14, linewidth=1.35, color="#333333")
    ax.add_patch(arrow)
    if label:
        x = (start[0] + end[0]) / 2
        y = (start[1] + end[1]) / 2 + 0.18
        ax.text(x, y, label, ha="center", va="bottom", fontproperties=reg, fontsize=9.5, color="#333333")


def build_control_chain():
    reg, bold = fonts()
    fig, ax = plt.subplots(figsize=(10.6, 4.6), dpi=180)
    ax.set_xlim(0, 10.8)
    ax.set_ylim(0, 4.2)
    ax.axis("off")
    ax.set_title("双频参数配置与输出链路图", fontproperties=bold, fontsize=16, pad=10)

    boxes = [
        ((0.35, 2.35), "频率选择\n375Hz/900Hz", "#f7fbff"),
        ((2.25, 2.35), "控制字计算\nM=round(f·2²⁸/fclk)", "#fff7eb"),
        ((4.25, 2.35), "STM32\nSPI写入", "#f7fbff"),
        ((6.05, 2.35), "AD9833\nDDS合成", "#eef7ee"),
        ((7.85, 2.35), "滤波/缓冲\n输出调理", "#f7fbff"),
        ((9.35, 2.35), "双频输出\n测试反馈", "#fff7eb"),
    ]
    anchors = []
    for xy, text, fill in boxes:
        anchors.append(add_box(ax, xy, text, width=1.35 if xy[0] > 9 else 1.55, fill=fill, bold=xy[0] in {0.35, 9.35}))

    for idx in range(len(anchors) - 1):
        add_arrow(ax, anchors[idx][0], anchors[idx + 1][1])

    add_box(ax, (2.55, 0.82), "参数表\nM375、M900", width=1.45, height=0.58, fill="#ffffff", edge="#9e9e9e")
    add_arrow(ax, (3.25, 1.4), (3.15, 2.35), "查表")
    add_box(ax, (6.05, 0.82), "相位累加\n波形查找表", width=1.55, height=0.58, fill="#ffffff", edge="#9e9e9e")
    add_arrow(ax, (6.82, 1.4), (6.82, 2.35), "内部转换")
    add_box(ax, (8.05, 0.82), "频率误差\n波形畸变", width=1.55, height=0.58, fill="#ffffff", edge="#9e9e9e")
    add_arrow(ax, (8.85, 2.35), (8.85, 1.4), "评价")

    ax.text(0.45, 0.25, "控制链路强调：目标频率先转化为DDS控制字，再通过SPI写入AD9833，最后由输出调理和测试反馈保证双频发射质量。", fontproperties=reg, fontsize=10.2, color="#333333")
    fig.tight_layout()
    fig.savefig(IMG_DIR / "dual_frequency_control_chain.png", bbox_inches="tight")
    plt.close(fig)


def main():
    build_spwm_principle()
    build_control_chain()


if __name__ == "__main__":
    main()
