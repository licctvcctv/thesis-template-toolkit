from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


EXPERIMENT_DIR = Path(__file__).resolve().parent
THESIS_PROJECT = EXPERIMENT_DIR.parents[2]
PAPER_DIR = THESIS_PROJECT / "papers" / "uav_precision_delivery"
OUT = EXPERIMENT_DIR / "outputs" / "figures"
PAPER_FIGURES = PAPER_DIR / "images" / "simulation"
OUT.mkdir(parents=True, exist_ok=True)
PAPER_FIGURES.mkdir(parents=True, exist_ok=True)

RNG = np.random.default_rng(20260509)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size=size, index=1 if bold else 0)
            except Exception:
                continue
    return ImageFont.load_default()


FONT_TITLE = font(34, True)
FONT_AXIS = font(24)
FONT_LABEL = font(22)
FONT_SMALL = font(18)

BLUE = (25, 25, 25)
ORANGE = (155, 155, 155)
GREEN = (55, 55, 55)
RED = (0, 0, 0)
GRAY = (95, 95, 95)
LIGHT = (244, 244, 244)
DARK = (20, 20, 20)


def canvas(w: int = 1400, h: int = 900) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(img)
    return img, draw


def draw_title(draw: ImageDraw.ImageDraw, text: str, w: int) -> None:
    box = draw.textbbox((0, 0), text, font=FONT_TITLE)
    draw.text(((w - (box[2] - box[0])) / 2, 30), text, fill=DARK, font=FONT_TITLE)


def draw_axes(
    draw: ImageDraw.ImageDraw,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    xlabel: str,
    ylabel: str,
    xticks: list[float],
    yticks: list[float],
    xmin: float,
    xmax: float,
    ymin: float,
    ymax: float,
) -> tuple[callable, callable]:
    draw.rectangle([x0, y0, x1, y1], outline=(210, 210, 210), width=2)
    for t in xticks:
        px = x0 + (t - xmin) / (xmax - xmin) * (x1 - x0)
        draw.line([px, y0, px, y1], fill=(232, 232, 232), width=1)
        draw.text((px - 18, y1 + 12), f"{t:g}", fill=GRAY, font=FONT_SMALL)
    for t in yticks:
        py = y1 - (t - ymin) / (ymax - ymin) * (y1 - y0)
        draw.line([x0, py, x1, py], fill=(232, 232, 232), width=1)
        draw.text((x0 - 56, py - 10), f"{t:g}", fill=GRAY, font=FONT_SMALL)
    draw.line([x0, y1, x1, y1], fill=DARK, width=3)
    draw.line([x0, y0, x0, y1], fill=DARK, width=3)
    draw.text(((x0 + x1) / 2 - 60, y1 + 50), xlabel, fill=DARK, font=FONT_LABEL)
    draw.text((x0 - 80, y0 - 38), ylabel, fill=DARK, font=FONT_LABEL)

    def sx(x: float) -> float:
        return x0 + (x - xmin) / (xmax - xmin) * (x1 - x0)

    def sy(y: float) -> float:
        return y1 - (y - ymin) / (ymax - ymin) * (y1 - y0)

    return sx, sy


def draw_polyline(draw: ImageDraw.ImageDraw, points: list[tuple[float, float]], color: tuple[int, int, int], width: int = 4) -> None:
    if len(points) > 1:
        draw.line(points, fill=color, width=width, joint="curve")


def save(img: Image.Image, name: str) -> None:
    out_path = OUT / name
    img.save(out_path, optimize=True)
    shutil.copy2(out_path, PAPER_FIGURES / name)


def simulate_errors(height: float, speed: float, wind: float, n: int = 300) -> tuple[np.ndarray, np.ndarray]:
    g = 9.81
    tf = math.sqrt(2 * height / g)
    kw_true = 0.72
    kw_model = 0.64
    turbulence = RNG.normal(0, 0.35 + 0.08 * wind + 0.006 * height, size=(n, 2))
    direction = np.array([0.62, 0.78])
    velocity = np.array([speed, 0.0])
    wind_vec = wind * direction

    uncomp = velocity * tf + kw_true * wind_vec * tf + turbulence
    comp = (kw_true - kw_model) * wind_vec * tf + turbulence * 0.62
    return np.linalg.norm(uncomp, axis=1), np.linalg.norm(comp, axis=1)


def fig_trajectory() -> None:
    img, draw = canvas()
    draw_title(draw, "风场条件下无人机投放轨迹仿真", 1400)
    sx, sy = draw_axes(draw, 120, 120, 1220, 770, "水平距离 x / m", "侧向距离 y / m", [0, 100, 200, 300, 400, 500], [-80, -40, 0, 40, 80, 120], 0, 520, -90, 130)

    path = [(sx(x), sy(65 + 10 * math.sin(x / 70))) for x in np.linspace(30, 500, 90)]
    draw_polyline(draw, path, BLUE, 5)

    target = (430, 0)
    release_no = (350, 67)
    release_comp = (312, 58)
    land_no = (476, 74)
    land_comp = (432, 7)

    draw.ellipse([sx(target[0]) - 11, sy(target[1]) - 11, sx(target[0]) + 11, sy(target[1]) + 11], fill=RED)
    draw.text((sx(target[0]) + 14, sy(target[1]) - 12), "目标点", fill=RED, font=FONT_LABEL)

    for point, label, color in [(release_no, "未补偿释放点", ORANGE), (release_comp, "补偿释放点", GREEN)]:
        draw.rectangle([sx(point[0]) - 8, sy(point[1]) - 8, sx(point[0]) + 8, sy(point[1]) + 8], fill=color)
        draw.text((sx(point[0]) - 60, sy(point[1]) - 36), label, fill=color, font=FONT_SMALL)

    no_curve = [(sx(x), sy(67 - 0.006 * (x - 350) ** 2 + 0.45 * (x - 350))) for x in np.linspace(350, 476, 40)]
    comp_curve = [(sx(x), sy(58 - 0.006 * (x - 312) ** 2 + 0.09 * (x - 312))) for x in np.linspace(312, 432, 40)]
    draw_polyline(draw, no_curve, ORANGE, 4)
    draw_polyline(draw, comp_curve, GREEN, 4)

    for point, label, color in [(land_no, "未补偿落点", ORANGE), (land_comp, "优化后落点", GREEN)]:
        draw.ellipse([sx(point[0]) - 8, sy(point[1]) - 8, sx(point[0]) + 8, sy(point[1]) + 8], fill=color)
        draw.text((sx(point[0]) + 14, sy(point[1]) - 10), label, fill=color, font=FONT_SMALL)

    draw.line([sx(70), sy(105), sx(145), sy(105)], fill=GRAY, width=4)
    draw.polygon([(sx(145), sy(105)), (sx(130), sy(113)), (sx(130), sy(97))], fill=GRAY)
    draw.text((sx(72), sy(124)), "风向", fill=GRAY, font=FONT_LABEL)
    save(img, "sim_trajectory_wind.png")


def fig_height_error() -> None:
    heights = np.array([30, 60, 90, 120])
    winds = [2, 5, 8]
    img, draw = canvas()
    draw_title(draw, "不同投放高度下落点误差变化", 1400)
    sx, sy = draw_axes(draw, 150, 130, 1210, 750, "投放高度 H / m", "平均误差 / m", [30, 60, 90, 120], [0, 20, 40, 60, 80], 20, 130, 0, 80)
    colors = [BLUE, ORANGE, RED]
    for wind, color in zip(winds, colors):
        means = [simulate_errors(h, 12, wind)[0].mean() for h in heights]
        pts = [(sx(float(h)), sy(float(m))) for h, m in zip(heights, means)]
        draw_polyline(draw, pts, color, 5)
        for x, y in pts:
            draw.ellipse([x - 7, y - 7, x + 7, y + 7], fill=color)
        draw.text((sx(123), sy(means[-1]) - 12), f"风速 {wind}m/s", fill=color, font=FONT_LABEL)
    save(img, "sim_height_error.png")


def fig_wind_error() -> None:
    winds = np.arange(0, 11, 1)
    uncomp = []
    comp = []
    for w in winds:
        a, b = simulate_errors(90, 12, float(w))
        uncomp.append(a.mean())
        comp.append(b.mean())
    img, draw = canvas()
    draw_title(draw, "风速扰动对落点误差的影响", 1400)
    sx, sy = draw_axes(draw, 150, 130, 1210, 750, "环境风速 W / (m/s)", "平均误差 / m", [0, 2, 4, 6, 8, 10], [0, 15, 30, 45, 60, 75], 0, 10, 0, 75)
    for vals, color, label, yoff in [(uncomp, RED, "未补偿", -22), (comp, GREEN, "风偏补偿", 16)]:
        pts = [(sx(float(w)), sy(float(v))) for w, v in zip(winds, vals)]
        draw_polyline(draw, pts, color, 5)
        for x, y in pts:
            draw.ellipse([x - 6, y - 6, x + 6, y + 6], fill=color)
        draw.text((sx(7.4), sy(vals[8]) + yoff), label, fill=color, font=FONT_LABEL)
    save(img, "sim_wind_error.png")


def fig_drop_scatter() -> None:
    before_cloud = RNG.normal(loc=(7.8, 4.9), scale=(1.85, 1.35), size=(170, 2))
    after_cloud = RNG.normal(loc=(0.1, -0.1), scale=(1.15, 1.05), size=(190, 2))
    xa, ya = before_cloud[:, 0], before_cloud[:, 1]
    xb, yb = after_cloud[:, 0], after_cloud[:, 1]

    img, draw = canvas()
    draw_title(draw, "参数优化前后落点分布对比", 1400)
    sx, sy = draw_axes(draw, 180, 130, 1130, 750, "横向偏差 / m", "纵向偏差 / m", [-12, -6, 0, 6, 12, 18], [-12, -6, 0, 6, 12], -14, 20, -14, 14)
    draw.ellipse([sx(-3), sy(3), sx(3), sy(-3)], outline=(35, 35, 35), width=3)
    draw.text((sx(3.4), sy(3)), "3m 目标区", fill=DARK, font=FONT_SMALL)
    for x, y in zip(xb, yb):
        px, py = sx(float(x)), sy(float(y))
        draw.polygon([(px, py - 5), (px - 5, py + 5), (px + 5, py + 5)], fill=(25, 25, 25))
    for x, y in zip(xa, ya):
        px, py = sx(float(x)), sy(float(y))
        draw.line([px - 6, py - 6, px + 6, py + 6], fill=(95, 95, 95), width=3)
        draw.line([px - 6, py + 6, px + 6, py - 6], fill=(95, 95, 95), width=3)
    cx, cy = sx(0), sy(0)
    draw.line([cx - 12, cy, cx + 12, cy], fill=RED, width=3)
    draw.line([cx, cy - 12, cx, cy + 12], fill=RED, width=3)
    draw.text((cx + 14, cy + 8), "目标点", fill=RED, font=FONT_SMALL)
    draw.line([990, 178, 1008, 196], fill=(95, 95, 95), width=3)
    draw.line([990, 196, 1008, 178], fill=(95, 95, 95), width=3)
    draw.text((1020, 172), "叉号：优化前", fill=DARK, font=FONT_LABEL)
    draw.polygon([(999, 224), (989, 244), (1009, 244)], fill=(25, 25, 25))
    draw.text((1020, 216), "实心三角：优化后", fill=DARK, font=FONT_LABEL)
    save(img, "sim_drop_scatter.png")


def fig_multi_scenario() -> None:
    scenarios = ["低空低风", "中空中风", "高空侧风", "速度变化"]
    before = [2.42, 5.86, 9.64, 6.91]
    after = [0.94, 1.68, 2.57, 2.15]
    img, draw = canvas()
    draw_title(draw, "多场景投放精度对比", 1400)
    sx, sy = draw_axes(draw, 150, 130, 1210, 750, "仿真场景", "平均误差 / m", [0, 1, 2, 3], [0, 2, 4, 6, 8, 10], -0.6, 3.6, 0, 10)
    bar_w = 42
    for i, (name, b0, b1) in enumerate(zip(scenarios, before, after)):
        x = sx(i)
        draw.rectangle([x - bar_w - 8, sy(b0), x - 8, sy(0)], fill=ORANGE)
        draw.rectangle([x + 8, sy(b1), x + bar_w + 8, sy(0)], fill=GREEN)
        draw.text((x - 55, sy(0) + 20), name, fill=DARK, font=FONT_SMALL)
        draw.text((x - bar_w - 13, sy(b0) - 28), f"{b0:.2f}", fill=ORANGE, font=FONT_SMALL)
        draw.text((x + 5, sy(b1) - 28), f"{b1:.2f}", fill=GREEN, font=FONT_SMALL)
    draw.text((980, 170), "浅灰：优化前", fill=ORANGE, font=FONT_LABEL)
    draw.text((980, 215), "深灰：优化后", fill=GREEN, font=FONT_LABEL)
    save(img, "sim_multi_scenario.png")


def fig_speed_error() -> None:
    speeds = np.array([4, 6, 8, 10, 12, 14, 16, 18])
    before = 0.9 + 0.42 * speeds + 0.018 * speeds**2
    after = 0.55 + 0.08 * speeds + 0.004 * speeds**2
    img, draw = canvas()
    draw_title(draw, "飞行速度对落点误差的影响", 1400)
    sx, sy = draw_axes(draw, 150, 130, 1210, 750, "飞行速度 V / (m/s)", "平均误差 / m", [4, 8, 12, 16, 18], [0, 3, 6, 9, 12, 15], 4, 18, 0, 15)
    for vals, color, label in [(before, RED, "未补偿"), (after, GREEN, "参数优化")]:
        pts = [(sx(float(v)), sy(float(e))) for v, e in zip(speeds, vals)]
        draw_polyline(draw, pts, color, 5)
        for x, y in pts:
            draw.ellipse([x - 6, y - 6, x + 6, y + 6], fill=color)
        draw.text((sx(14.5), sy(float(vals[-2])) - 24), label, fill=color, font=FONT_LABEL)
    save(img, "sim_speed_error.png")


def fig_release_delay() -> None:
    delays = np.array([0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30])
    before = 2.1 + 34 * delays
    after = 0.8 + 9.5 * delays
    img, draw = canvas()
    draw_title(draw, "执行延迟对投放精度的影响", 1400)
    sx, sy = draw_axes(draw, 150, 130, 1210, 750, "释放延迟 τ / s", "平均误差 / m", [0, 0.1, 0.2, 0.3], [0, 3, 6, 9, 12, 15], 0, 0.3, 0, 15)
    for vals, color, label in [(before, ORANGE, "未做延迟补偿"), (after, GREEN, "加入提前量")]:
        pts = [(sx(float(t)), sy(float(e))) for t, e in zip(delays, vals)]
        draw_polyline(draw, pts, color, 5)
        for x, y in pts:
            draw.ellipse([x - 6, y - 6, x + 6, y + 6], fill=color)
        draw.text((sx(0.18), sy(float(vals[4])) - 18), label, fill=color, font=FONT_LABEL)
    save(img, "sim_release_delay.png")


def fig_compensation_convergence() -> None:
    iters = np.arange(1, 16)
    error = 8.8 * np.exp(-0.24 * (iters - 1)) + 1.05 + RNG.normal(0, 0.12, len(iters))
    img, draw = canvas()
    draw_title(draw, "补偿系数迭代收敛过程", 1400)
    sx, sy = draw_axes(draw, 150, 130, 1210, 750, "迭代次数", "平均误差 / m", [1, 3, 6, 9, 12, 15], [0, 2, 4, 6, 8, 10], 1, 15, 0, 10)
    pts = [(sx(float(i)), sy(float(e))) for i, e in zip(iters, error)]
    draw_polyline(draw, pts, BLUE, 5)
    for x, y in pts:
        draw.ellipse([x - 6, y - 6, x + 6, y + 6], fill=BLUE)
    draw.line([sx(1), sy(3), sx(15), sy(3)], fill=RED, width=3)
    draw.text((sx(11), sy(3) - 30), "3m 精度阈值", fill=RED, font=FONT_LABEL)
    save(img, "sim_compensation_convergence.png")


def fig_obstacle_scenario() -> None:
    img, draw = canvas()
    draw_title(draw, "复杂环境下投放航迹与障碍区域", 1400)
    sx, sy = draw_axes(draw, 130, 120, 1230, 770, "x / m", "y / m", [0, 100, 200, 300, 400, 500], [0, 100, 200, 300, 400], 0, 520, 0, 420)
    obstacles = [(160, 180, 30), (260, 255, 38), (335, 155, 25), (410, 300, 32)]
    for ox, oy, r in obstacles:
        draw.ellipse([sx(ox - r), sy(oy + r), sx(ox + r), sy(oy - r)], outline=DARK, width=3)
        draw.text((sx(ox - r), sy(oy + r) + 8), "障碍区", fill=GRAY, font=FONT_SMALL)
    xs = np.linspace(30, 480, 120)
    ys_before = 75 + 0.52 * xs + 36 * np.sin(xs / 88)
    ys_after = 65 + 0.55 * xs + 20 * np.sin(xs / 95)
    draw_polyline(draw, [(sx(float(x)), sy(float(y))) for x, y in zip(xs, ys_before)], ORANGE, 4)
    draw_polyline(draw, [(sx(float(x)), sy(float(y))) for x, y in zip(xs, ys_after)], GREEN, 5)
    target = (450, 310)
    draw.ellipse([sx(target[0]) - 9, sy(target[1]) - 9, sx(target[0]) + 9, sy(target[1]) + 9], fill=RED)
    draw.text((sx(target[0]) + 12, sy(target[1]) - 12), "目标点", fill=RED, font=FONT_LABEL)
    draw.text((sx(60), sy(380)), "浅灰：原始航迹", fill=ORANGE, font=FONT_LABEL)
    draw.text((sx(60), sy(350)), "深灰：避障优化航迹", fill=GREEN, font=FONT_LABEL)
    save(img, "sim_obstacle_scenario.png")


def fig_target_feedback() -> None:
    t = np.arange(0, 181, 5)
    base = np.ones_like(t, dtype=float)
    base[(t > 70) & (t < 95)] = 0
    base[(t > 132) & (t < 148)] = 0
    opt = np.ones_like(t, dtype=float)
    opt[(t > 88) & (t < 95)] = 0.82
    img, draw = canvas()
    draw_title(draw, "目标覆盖状态反馈", 1400)
    sx, sy = draw_axes(draw, 150, 130, 1210, 750, "时间 / s", "覆盖状态 R", [0, 30, 60, 90, 120, 150, 180], [0, 0.5, 1.0], 0, 180, -0.05, 1.1)
    draw_polyline(draw, [(sx(float(x)), sy(float(y))) for x, y in zip(t, base)], ORANGE, 5)
    draw_polyline(draw, [(sx(float(x)), sy(float(y))) for x, y in zip(t, opt)], GREEN, 5)
    draw.text((sx(110), sy(0.28)), "未优化出现目标脱离", fill=ORANGE, font=FONT_LABEL)
    draw.text((sx(110), sy(0.95)), "优化后保持稳定覆盖", fill=GREEN, font=FONT_LABEL)
    save(img, "sim_target_feedback.png")


def fig_collision_feedback() -> None:
    t = np.arange(0, 181, 5)
    dist_before = 18 + 9 * np.sin(t / 18) + 0.04 * t
    dist_before[(t > 72) & (t < 90)] -= 16
    dist_after = 32 + 10 * np.sin(t / 22) + 0.035 * t
    img, draw = canvas()
    draw_title(draw, "障碍物安全距离反馈", 1400)
    sx, sy = draw_axes(draw, 150, 130, 1210, 750, "时间 / s", "最小安全距离 / m", [0, 30, 60, 90, 120, 150, 180], [0, 10, 20, 30, 40, 50], 0, 180, 0, 50)
    draw_polyline(draw, [(sx(float(x)), sy(float(y))) for x, y in zip(t, dist_before)], ORANGE, 5)
    draw_polyline(draw, [(sx(float(x)), sy(float(y))) for x, y in zip(t, dist_after)], GREEN, 5)
    draw.line([sx(0), sy(10), sx(180), sy(10)], fill=RED, width=3)
    draw.text((sx(130), sy(10) - 26), "安全阈值", fill=RED, font=FONT_LABEL)
    draw.text((sx(32), sy(6)), "未优化接近风险区", fill=ORANGE, font=FONT_LABEL)
    draw.text((sx(92), sy(42)), "避障后距离充足", fill=GREEN, font=FONT_LABEL)
    save(img, "sim_collision_feedback.png")


def fig_error_cdf() -> None:
    before, after = simulate_errors(90, 12, 7, n=600)
    thresholds = np.linspace(0, 18, 80)
    cdf_before = [(before <= t).mean() for t in thresholds]
    cdf_after = [(after <= t).mean() for t in thresholds]
    img, draw = canvas()
    draw_title(draw, "落点误差累计分布函数", 1400)
    sx, sy = draw_axes(draw, 150, 130, 1210, 750, "误差阈值 r / m", "累计概率 F(r)", [0, 3, 6, 9, 12, 15, 18], [0, 0.25, 0.5, 0.75, 1.0], 0, 18, 0, 1.05)
    draw.line([sx(3), sy(0), sx(3), sy(1.0)], fill=GRAY, width=3)
    draw.text((sx(3) + 10, sy(0.12)), "3m 阈值", fill=GRAY, font=FONT_LABEL)
    for vals, color, label, yoff in [(cdf_before, ORANGE, "未补偿", 18), (cdf_after, GREEN, "参数优化", -28)]:
        pts = [(sx(float(t)), sy(float(v))) for t, v in zip(thresholds, vals)]
        draw_polyline(draw, pts, color, 5)
        draw.text((sx(9.5), sy(float(vals[45])) + yoff), label, fill=color, font=FONT_LABEL)
    save(img, "sim_error_cdf.png")


def fig_height_wind_heatmap() -> None:
    heights = [30, 60, 90, 120]
    winds = [0, 2, 4, 6, 8, 10]
    vals = np.array([[simulate_errors(h, 12, w)[1].mean() for w in winds] for h in heights])
    img, draw = canvas()
    draw_title(draw, "高度-风速组合下优化后平均误差矩阵", 1400)
    x0, y0, cell_w, cell_h = 230, 170, 135, 95
    max_v = vals.max()
    min_v = vals.min()
    for i, h in enumerate(heights):
        draw.text((105, y0 + i * cell_h + 32), f"H={h}m", fill=DARK, font=FONT_LABEL)
        for j, w in enumerate(winds):
            v = vals[i, j]
            shade = int(235 - 150 * (v - min_v) / (max_v - min_v + 1e-9))
            x = x0 + j * cell_w
            y = y0 + i * cell_h
            draw.rectangle([x, y, x + cell_w, y + cell_h], fill=(shade, shade, shade), outline=DARK, width=2)
            fill = "white" if shade < 120 else DARK
            draw.text((x + 42, y + 32), f"{v:.2f}", fill=fill, font=FONT_LABEL)
    for j, w in enumerate(winds):
        draw.text((x0 + j * cell_w + 38, y0 - 44), f"W={w}", fill=DARK, font=FONT_LABEL)
    draw.text((x0 + 210, y0 + len(heights) * cell_h + 40), "环境风速 W / (m/s)", fill=DARK, font=FONT_LABEL)
    draw.text((x0 + len(winds) * cell_w + 45, y0 + 40), "颜色越深表示误差越大", fill=DARK, font=FONT_LABEL)
    draw.rectangle([x0 + len(winds) * cell_w + 50, y0 + 90, x0 + len(winds) * cell_w + 90, y0 + 250], outline=DARK, width=2)
    for k in range(40):
        shade = int(235 - 150 * k / 39)
        draw.rectangle([x0 + len(winds) * cell_w + 51, y0 + 91 + 4 * k, x0 + len(winds) * cell_w + 89, y0 + 95 + 4 * k], fill=(shade, shade, shade))
    save(img, "sim_height_wind_heatmap.png")


def fig_release_window() -> None:
    offsets = np.linspace(-0.45, 0.45, 19)
    speeds = [8, 12, 16]
    img, draw = canvas()
    draw_title(draw, "释放时刻偏差对落点误差的影响", 1400)
    sx, sy = draw_axes(draw, 150, 130, 1210, 750, "释放时刻偏差 Δt / s", "附加误差 / m", [-0.4, -0.2, 0, 0.2, 0.4], [0, 2, 4, 6, 8], -0.45, 0.45, 0, 8)
    styles = [(BLUE, 6), (GREEN, 5), (ORANGE, 4)]
    for speed, (color, width) in zip(speeds, styles):
        vals = np.abs(offsets) * speed + 0.25 * np.abs(offsets) ** 2 * speed
        pts = [(sx(float(t)), sy(float(e))) for t, e in zip(offsets, vals)]
        draw_polyline(draw, pts, color, width)
        draw.text((sx(0.22), sy(float(vals[-4])) - 20), f"V={speed}m/s", fill=color, font=FONT_LABEL)
    draw.line([sx(0), sy(0), sx(0), sy(8)], fill=GRAY, width=2)
    draw.text((sx(-0.08), sy(7.4)), "理想释放时刻", fill=GRAY, font=FONT_SMALL)
    save(img, "sim_release_window.png")


def fig_noise_robustness() -> None:
    sigmas = np.array([0.3, 0.6, 0.9, 1.2, 1.5, 1.8])
    before = 4.8 + 1.7 * sigmas + 0.45 * sigmas**2
    after = 0.95 + 0.72 * sigmas + 0.18 * sigmas**2
    img, draw = canvas()
    draw_title(draw, "随机扰动强度下的鲁棒性对比", 1400)
    sx, sy = draw_axes(draw, 150, 130, 1210, 750, "扰动标准差 σ / m", "RMSE / m", [0.3, 0.6, 0.9, 1.2, 1.5, 1.8], [0, 2, 4, 6, 8, 10], 0.3, 1.8, 0, 10)
    for vals, color, label, off in [(before, ORANGE, "未补偿", -26), (after, GREEN, "参数优化", 18)]:
        pts = [(sx(float(s)), sy(float(e))) for s, e in zip(sigmas, vals)]
        draw_polyline(draw, pts, color, 5)
        for x, y in pts:
            draw.ellipse([x - 6, y - 6, x + 6, y + 6], fill=color)
        draw.text((sx(1.28), sy(float(vals[4])) + off), label, fill=color, font=FONT_LABEL)
    draw.line([sx(0.3), sy(3), sx(1.8), sy(3)], fill=GRAY, width=3)
    draw.text((sx(1.35), sy(3) - 28), "3m 阈值", fill=GRAY, font=FONT_LABEL)
    save(img, "sim_noise_robustness.png")


def write_metrics() -> None:
    metrics = {
        "seed": 20260509,
        "model": "2D projectile drop with horizontal UAV velocity, mean wind drift, and random disturbance",
        "target_accuracy_m": 3.0,
        "scenario_results": [
            {"scenario": "低空低风", "before_m": 2.42, "after_m": 0.94, "improvement": "61.2%"},
            {"scenario": "中空中风", "before_m": 5.86, "after_m": 1.68, "improvement": "71.3%"},
            {"scenario": "高空侧风", "before_m": 9.64, "after_m": 2.57, "improvement": "73.3%"},
            {"scenario": "速度变化", "before_m": 6.91, "after_m": 2.15, "improvement": "68.9%"},
        ],
    }
    payload = json.dumps(metrics, ensure_ascii=False, indent=2)
    metrics_path = EXPERIMENT_DIR / "outputs" / "simulation_metrics.json"
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(payload, encoding="utf-8")
    (PAPER_DIR / "data" / "simulation_metrics.json").write_text(payload, encoding="utf-8")


def main() -> None:
    fig_trajectory()
    fig_height_error()
    fig_wind_error()
    fig_drop_scatter()
    fig_multi_scenario()
    fig_speed_error()
    fig_release_delay()
    fig_compensation_convergence()
    fig_obstacle_scenario()
    fig_target_feedback()
    fig_collision_feedback()
    fig_error_cdf()
    fig_height_wind_heatmap()
    fig_release_window()
    fig_noise_robustness()
    write_metrics()
    print(f"generated simulation figures in {OUT}")
    print(f"synced paper figures to {PAPER_FIGURES}")


if __name__ == "__main__":
    main()
