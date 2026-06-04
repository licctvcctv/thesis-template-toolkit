from __future__ import annotations

import math
import os
import shutil
import subprocess
import textwrap
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "water_engineering"
OUT = ROOT / "outputs" / os.environ.get("CODEX_THREAD_ID", "manual-20260601") / "presentations" / "shanwei-coal-wharf-image-ppt"
SLIDES = OUT / "slides"
OUTPUT = OUT / "output"
W, H = 1920, 1080

COLORS = {
    "ink": "#172033",
    "muted": "#5c667a",
    "line": "#1f2937",
    "accent": "#0f6f66",
    "accent2": "#a05413",
    "pale": "#eef5f4",
    "grid": "#e7ecef",
    "light": "#f8fafb",
}


def font_path(name: str) -> str:
    try:
        got = subprocess.check_output(["fc-match", "-v", name], text=True)
        for line in got.splitlines():
            line = line.strip()
            if line.startswith("file:"):
                p = line.split('"', 2)[1]
                if Path(p).exists():
                    return p
    except Exception:
        pass
    candidates = [
        f"/System/Library/Fonts/{name}.ttc",
        f"/System/Library/Fonts/{name}.ttf",
        f"/System/Library/Fonts/Supplemental/{name}.ttc",
        f"/System/Library/Fonts/Supplemental/{name}.ttf",
        f"/Library/Fonts/{name}.ttc",
        f"/Library/Fonts/{name}.ttf",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
    ]
    for p in candidates:
        if Path(p).exists():
            return p
    return "/System/Library/Fonts/PingFang.ttc"


FONT_REG = "/System/Library/Fonts/Hiragino Sans GB.ttc"
FONT_HEI = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_SONG = "/System/Library/Fonts/Supplemental/Songti.ttc"


def f(size: int, bold: bool = False, song: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_HEI if bold else (FONT_SONG if song else FONT_REG), size)


def text_bbox(draw: ImageDraw.ImageDraw, xy, text: str, font: ImageFont.FreeTypeFont):
    return draw.textbbox(xy, text, font=font)


def wrap_text(text: str, max_chars: int) -> list[str]:
    out: list[str] = []
    for para in text.split("\n"):
        if not para:
            out.append("")
            continue
        line = ""
        for ch in para:
            if len(line) >= max_chars:
                out.append(line)
                line = ch
            else:
                line += ch
        if line:
            out.append(line)
    return out


def fit_image(path: Path, box: tuple[int, int, int, int], contain=True, bg="white", crop_white=True) -> Image.Image:
    img = Image.open(path).convert("RGB")
    if crop_white:
        bg_img = Image.new("RGB", img.size, "white")
        diff = ImageChops.difference(img, bg_img) if False else None
        gray = ImageOps.grayscale(ImageChops_dif(img))
        bbox = gray.point(lambda p: 255 if p > 18 else 0).getbbox()
        if bbox:
            pad = 25
            bbox = (max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(img.width, bbox[2] + pad), min(img.height, bbox[3] + pad))
            img = img.crop(bbox)
    bw, bh = box[2] - box[0], box[3] - box[1]
    if contain:
        img.thumbnail((bw, bh), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (bw, bh), bg)
        canvas.paste(img, ((bw - img.width) // 2, (bh - img.height) // 2))
        return canvas
    return ImageOps.fit(img, (bw, bh), Image.Resampling.LANCZOS, centering=(0.5, 0.5))


def ImageChops_dif(img: Image.Image) -> Image.Image:
    from PIL import ImageChops
    return ImageChops.difference(img, Image.new("RGB", img.size, "white"))


def base_slide(title: str, kicker: str | None = None, page: int | None = None) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    for x in range(0, W, 48):
        d.line((x, 0, x, H), fill=COLORS["grid"], width=1)
    for y in range(0, H, 48):
        d.line((0, y, W, y), fill=COLORS["grid"], width=1)
    d.rectangle((50, 42, W - 50, H - 42), outline="#4b5563", width=2)
    d.rectangle((70, 62, W - 70, H - 62), outline="#c9d0d6", width=1)
    d.rectangle((70, 62, W - 70, 150), fill="white", outline="#c9d0d6", width=1)
    d.text((95, 84), title, fill=COLORS["ink"], font=f(42, bold=True))
    if kicker:
        d.text((95, 132), kicker, fill=COLORS["muted"], font=f(20))
    if page is not None:
        d.text((W - 170, 96), f"{page:02d}/20", fill=COLORS["muted"], font=f(24))
    return img, d


def footer(d: ImageDraw.ImageDraw, label="汕尾电厂配套煤码头工程初步设计"):
    d.line((95, H - 88, W - 95, H - 88), fill="#c9d0d6", width=1)
    d.text((95, H - 70), label, fill="#6b7280", font=f(18))


def bullet_list(d, x, y, items, size=29, gap=14, max_chars=34, color=None):
    color = color or COLORS["ink"]
    yy = y
    for item in items:
        lines = wrap_text(item, max_chars)
        d.ellipse((x, yy + 12, x + 8, yy + 20), fill=COLORS["accent"])
        for i, line in enumerate(lines):
            d.text((x + 26, yy + i * (size + 8)), line, fill=color, font=f(size))
        yy += len(lines) * (size + 8) + gap
    return yy


def info_table(d, x, y, w, row_h, headers, rows, col_fracs=None, size=24):
    col_fracs = col_fracs or [1 / len(headers)] * len(headers)
    xs = [x]
    for frac in col_fracs:
        xs.append(xs[-1] + int(w * frac))
    xs[-1] = x + w
    d.rectangle((x, y, x + w, y + row_h), fill=COLORS["pale"], outline=COLORS["line"], width=2)
    for i, h in enumerate(headers):
        d.text((xs[i] + 14, y + 14), h, fill=COLORS["ink"], font=f(size, bold=True))
    yy = y + row_h
    for r, row in enumerate(rows):
        d.rectangle((x, yy, x + w, yy + row_h), fill="white" if r % 2 == 0 else "#fbfcfd", outline="#9aa4af", width=1)
        for i, cell in enumerate(row):
            d.text((xs[i] + 14, yy + 13), str(cell), fill=COLORS["ink"], font=f(size))
        yy += row_h
    for xx in xs:
        d.line((xx, y, xx, yy), fill="#9aa4af", width=1)
    d.rectangle((x, y, x + w, yy), outline=COLORS["line"], width=2)
    return yy


def calc_box(d, x, y, w, title, formulas, result=None):
    d.rectangle((x, y, x + w, y + 210), fill="white", outline="#334155", width=2)
    d.rectangle((x, y, x + w, y + 44), fill="#f1f5f6", outline="#334155", width=2)
    d.text((x + 18, y + 10), title, fill=COLORS["ink"], font=f(24, bold=True))
    yy = y + 64
    for line in formulas:
        d.text((x + 24, yy), line, fill=COLORS["ink"], font=f(24, song=True))
        yy += 42
    if result:
        d.text((x + 24, y + 166), result, fill=COLORS["accent"], font=f(24, bold=True))


def draw_simple_plan(d, x, y, w, h):
    d.rectangle((x, y, x + w, y + h), outline=COLORS["line"], width=3)
    water = (x + 35, y + int(h * 0.12), x + w - 35, y + int(h * 0.38))
    berth = (x + 80, y + int(h * 0.43), x + w - 80, y + int(h * 0.54))
    land = (x + 35, y + int(h * 0.59), x + w - 35, y + h - 45)
    d.rectangle(water, fill="#eef7fb", outline="#64748b", width=1)
    for i in range(8):
        yy = water[1] + 20 + i * 18
        d.arc((water[0] + 20, yy, water[0] + 100, yy + 28), 0, 180, fill="#77a9bd", width=1)
    d.rectangle(berth, fill="#eef5f4", outline=COLORS["line"], width=2)
    d.text((berth[0] + 18, berth[1] + 15), "泊位长度 260 m", font=f(24, bold=True), fill=COLORS["ink"])
    d.rectangle(land, fill="#f9fafb", outline="#64748b", width=2)
    lh = max(34, int((land[3] - land[1]) * 0.18))
    labels = [
        ("卸船机轨道带", land[0] + 40, land[1] + 25, land[2] - 40, land[1] + 25 + lh),
        ("封闭皮带机廊道", land[0] + 40, land[1] + 55 + lh, land[2] - 210, land[1] + 55 + 2 * lh),
        ("转运站 / 除尘设施", land[2] - 190, land[1] + 45 + lh, land[2] - 40, land[1] + 45 + 2 * lh + 22),
        ("检修道路与消防通道", land[0] + 40, land[3] - lh - 25, land[2] - 40, land[3] - 25),
    ]
    for label, x1, y1, x2, y2 in labels:
        d.rectangle((x1, y1, x2, y2), outline=COLORS["accent"], width=2)
        d.text((x1 + 12, y1 + 12), label, font=f(21), fill=COLORS["ink"])


def draw_caisson_section(d, x, y, w, h):
    # textbook-style schematic, intentionally without construction title block
    sea_x = x + 100
    d.line((x + 30, y + 110, x + w - 30, y + 110), fill="#64748b", width=2)
    d.text((x + 35, y + 82), "设计高水位 +4.27", font=f(18), fill="#334155")
    d.polygon([(x + 55, y + h - 95), (x + w - 70, y + h - 95), (x + w - 140, y + h - 40), (x + 110, y + h - 40)], outline="#475569", fill="#f8fafc")
    for i in range(28):
        px = x + 90 + i * 28
        py = y + h - 88 + (i % 5) * 8
        d.ellipse((px, py, px + 16, py + 10), outline="#475569", width=1)
    cx1, cy1 = x + int(w * 0.28), y + int(h * 0.34)
    cx2, cy2 = x + int(w * 0.66), y + h - int(h * 0.18)
    d.rectangle((cx1, cy1, cx2, cy2), outline=COLORS["line"], width=4)
    d.rectangle((cx1 + 26, cy1 + 28, cx2 - 26, cy2 - 26), outline=COLORS["line"], width=2)
    d.line((cx1 + int((cx2-cx1) * 0.38), cy1 + 28, cx1 + int((cx2-cx1) * 0.38), cy2 - 26), fill=COLORS["line"], width=2)
    d.line((cx1 + int((cx2-cx1) * 0.70), cy1 + 28, cx1 + int((cx2-cx1) * 0.70), cy2 - 26), fill=COLORS["line"], width=2)
    d.line((cx1 + 26, cy1 + 155, cx2 - 26, cy1 + 155), fill=COLORS["line"], width=2)
    d.rectangle((cx1 - 20, cy1 - 58, cx2 + 35, cy1), outline=COLORS["line"], width=4)
    d.rectangle((cx2 + 25, cy1 + 28, x + w - 70, cy2), fill="#f2eee8", outline="#9a7b51", width=1)
    d.text((cx1 + 95, cy1 + 70), "沉箱仓格", font=f(22), fill=COLORS["ink"])
    d.text((cx1 - 5, cy1 - 45), "胸墙", font=f(20), fill=COLORS["ink"])
    d.text((cx2 + 55, cy1 + 120), "后方回填", font=f(20), fill=COLORS["ink"])
    d.text((cx1 + 120, cy2 + 12), "抛石基床", font=f(20), fill=COLORS["ink"])
    d.line((cx1, cy2 + 40, cx2, cy2 + 40), fill="#334155", width=1)
    d.text((cx1 + 110, cy2 + 48), "单节长度 22 m", font=f(18), fill="#334155")


def draw_bar_chart(d, x, y, w, h, values, labels):
    maxv = max(values)
    axis_y = y + h - 70
    d.line((x + 70, y + 40, x + 70, axis_y), fill=COLORS["line"], width=2)
    d.line((x + 70, axis_y, x + w - 40, axis_y), fill=COLORS["line"], width=2)
    bar_w = 180
    gap = 190
    for i, (v, lab) in enumerate(zip(values, labels)):
        bh = int((h - 150) * v / maxv)
        bx = x + 150 + i * (bar_w + gap)
        d.rectangle((bx, axis_y - bh, bx + bar_w, axis_y), fill=COLORS["accent"] if i == 0 else "#8b5e34", outline=COLORS["line"], width=2)
        d.text((bx + 20, axis_y - bh - 42), f"{v:.0f} 万元", font=f(26, bold=True), fill=COLORS["ink"])
        for j, line in enumerate(wrap_text(lab, 8)):
            d.text((bx + 12, axis_y + 18 + j * 28), line, font=f(21), fill=COLORS["ink"])
    d.text((x + 80, y + 12), "初步总造价对比", font=f(25, bold=True), fill=COLORS["ink"])


def add_image_panel(img, path, box, title=None, contain=True):
    d = ImageDraw.Draw(img)
    x1, y1, x2, y2 = box
    d.rectangle((x1, y1, x2, y2), fill="white", outline="#94a3b8", width=2)
    if title:
        d.rectangle((x1, y1, x2, y1 + 42), fill="#f1f5f6", outline="#94a3b8", width=1)
        d.text((x1 + 14, y1 + 9), title, font=f(22, bold=True), fill=COLORS["ink"])
        ibox = (x1 + 12, y1 + 52, x2 - 12, y2 - 12)
    else:
        ibox = (x1 + 12, y1 + 12, x2 - 12, y2 - 12)
    panel = fit_image(Path(path), ibox, contain=contain, crop_white=True)
    img.paste(panel, (ibox[0], ibox[1]))


def slide_01():
    img, d = base_slide("", None, 1)
    d.rectangle((90, 94, W - 90, H - 94), outline="#111827", width=3)
    d.rectangle((116, 120, W - 116, H - 120), outline="#cbd5df", width=1)
    d.text((155, 215), "汕尾电厂配套煤码头工程初步设计", font=f(60, bold=True), fill=COLORS["ink"])
    d.text((158, 300), "毕业设计答辩汇报", font=f(36), fill=COLORS["accent"])
    d.line((155, 360, 1080, 360), fill="#111827", width=2)
    rows = [("专业", "港口航道与海岸工程"), ("设计船型", "5万吨级散货船"), ("泊位长度", "260 m"), ("推荐结构", "高桩梁板式码头")]
    info_table(d, 158, 435, 690, 58, ["项目", "内容"], rows, [0.32, 0.68], size=24)
    draw_simple_plan(d, 1000, 410, 700, 420)
    d.text((158, 875), "学生：潘欣    指导教师：孙克俐    2026年5月", font=f(25), fill=COLORS["muted"])
    return img


def build_slides():
    paths = []
    img_dir = PAPER / "images"
    slides = []

    slides.append(slide_01())

    img, d = base_slide("一、工程任务与设计依据", "初步设计范围、规范依据和成果组成", 2)
    bullet_list(d, 120, 205, [
        "工程对象为汕尾电厂配套5万吨级煤码头，承担燃料煤接卸、转运和短期储备。",
        "设计内容包括总平面、装卸工艺、结构方案、结构计算、工程量概预算和方案比选。",
        "主要依据海港总体设计、港口工程荷载、桩基、混凝土结构、环保和概预算相关规范。",
        "结构方案采用高桩梁板式与重力式沉箱两种型式进行同口径比较。"
    ], max_chars=31)
    add_image_panel(img, img_dir / "fig1-1-technical-route.png", (1030, 220, 1780, 770), "设计技术路线")
    footer(d); slides.append(img)

    img, d = base_slide("二、工程条件与基础参数", "水位、气象、地质和设计船型", 3)
    rows = [
        ("设计船型", "5万吨级散货船", "船长225 m，型宽32.2 m"),
        ("泊位长度", "260 m", "两端各取17.5 m富裕量"),
        ("前沿水深", "12.50 m", "满足满载靠泊和富裕深度"),
        ("码头面高程", "+3.60 m", "兼顾潮位、浪溅和作业要求"),
        ("地基条件", "软弱覆盖层较厚", "高桩方案适应性较好"),
    ]
    info_table(d, 120, 210, 980, 62, ["项目", "取值", "说明"], rows, [0.22, 0.23, 0.55], size=23)
    add_image_panel(img, img_dir / "user_provided/fig2-1-wind-rose.jpeg", (1190, 210, 1705, 780), "风玫瑰图")
    footer(d); slides.append(img)

    img, d = base_slide("三、泊位尺度计算", "按5万吨级散货船靠泊条件确定", 4)
    calc_box(d, 120, 205, 760, "泊位长度", [
        "L_b = L + 2d",
        "L_b = 225 + 2×17.5 = 260 m",
    ], "取泊位长度 L_b = 260 m")
    calc_box(d, 120, 460, 760, "前沿设计水深", [
        "D = T + Z_1 + Z_2 + Z_3",
        "D ≈ 11.20 + 0.70 + 0.30 + 0.30 = 12.50 m",
    ], "取前沿设计水深 12.50 m")
    rows = [("泊位长度", "260 m", "满足靠泊、系缆、检修"), ("停泊水域", "按船宽与安全间距控制", "靠泊作业水域"), ("回旋水域", "直径约450 m", "满足调头要求"), ("码头面高程", "+3.60 m", "满足作业与防浪要求")]
    info_table(d, 1000, 245, 760, 66, ["尺度", "计算取值", "控制理由"], rows, [0.25, 0.32, 0.43], size=22)
    footer(d); slides.append(img)

    img, d = base_slide("四、总平面布置", "顺岸式单泊位与后方输送系统衔接", 5)
    add_image_panel(img, img_dir / "user_provided/G-01_general_layout.png", (100, 185, 1125, 875), "总平面布置图", contain=True)
    bullet_list(d, 1190, 230, [
        "泊位采用顺岸式布置，前沿线与输送廊道平行。",
        "卸船机轨道、前沿漏斗、皮带机廊道和转运站沿煤流方向组织。",
        "检修道路和消防通道与生产区域分开布置，减少作业干扰。",
        "两种结构方案采用相同泊位尺度和装卸工艺边界。"
    ], size=28, max_chars=19)
    footer(d); slides.append(img)

    img, d = base_slide("五、水域与陆域控制", "靠离泊、回旋、疏浚和维护条件", 6)
    draw_simple_plan(d, 120, 210, 820, 575)
    rows = [
        ("靠泊岸线", "260 m", "满足5万吨级散货船靠泊"),
        ("前沿水深", "12.50 m", "兼顾吃水和富裕深度"),
        ("回旋尺度", "约450 m", "满足拖轮协助调头"),
        ("陆域控制", "廊道、转运站、检修道", "保证煤流顺直"),
    ]
    info_table(d, 1020, 235, 760, 70, ["控制项", "取值", "说明"], rows, [0.25, 0.28, 0.47], size=23)
    footer(d); slides.append(img)

    img, d = base_slide("六、装卸工艺流程", "卸船、转运、除尘和入厂输送", 7)
    add_image_panel(img, img_dir / "imagegen/fig4-1-coal-handling-environmental-control.png", (120, 195, 1780, 645), "煤码头卸船、输送及环保控制流程")
    rows = [("卸船设备", "桥式抓斗卸船机或连续卸船机", "控制前沿轨道荷载"), ("水平转运", "带式输送机+转运站", "减少煤流转折"), ("环保控制", "封闭廊道、喷淋、除尘器", "控制粉尘和含煤污水"), ("运行目标", "连续接卸、稳定供煤", "满足电厂燃料需求")]
    info_table(d, 180, 700, 1500, 58, ["环节", "布置", "设计控制"], rows, [0.2, 0.42, 0.38], size=22)
    footer(d); slides.append(img)

    img, d = base_slide("七、设备能力与堆场容量", "设备能力与煤炭周转能力匹配", 8)
    calc_box(d, 120, 205, 800, "设备年通过能力", ["Q_y = N·t·P·η", "Q_y = 280×18×1000×0.72 = 362.9万t"], "设备能力满足年接卸需求")
    calc_box(d, 120, 465, 800, "堆场容量", ["A = Q_s /(h·ρ·φ)", "A ≈ 180000 /(6.0×0.85×0.80) ≈ 4.4万m²"], "堆场面积按约4.4万m²控制")
    rows = [("卸船机", "1台", "额定效率约1000 t/h"), ("带式输送机", "连续布置", "与卸船能力匹配"), ("堆场容量", "18万t", "满足短期储备"), ("堆场面积", "约4.4万m²", "含通道和环保设施")]
    info_table(d, 1030, 250, 720, 65, ["项目", "取值", "说明"], rows, [0.26, 0.28, 0.46], size=22)
    footer(d); slides.append(img)

    img, d = base_slide("八、平台功能分区与荷载", "荷载按功能带进入结构计算", 9)
    rows = [("靠船带", "船舶撞击、护舷反力", "靠船构件、前排桩"), ("轨道带", "卸船机轮压", "轨道梁、横梁"), ("廊道带", "皮带机、支座反力", "纵梁、支承梁"), ("检修带", "车辆、临时堆载", "面板和梁格")]
    info_table(d, 120, 220, 860, 72, ["功能带", "主要作用", "结构控制"], rows, [0.24, 0.39, 0.37], size=23)
    calc_box(d, 1080, 250, 620, "轨道带等效荷载", ["q_e = G_e /(n·A_w)", "q_e = 3200 /(8×5.0) = 80 kN/m²"], "轨道梁按轮压包络验算")
    draw_simple_plan(d, 1060, 520, 650, 320)
    footer(d); slides.append(img)

    img, d = base_slide("九、结构方案选型", "高桩梁板式与重力式沉箱同条件比较", 10)
    rows = [("传力方式", "梁板—桩基—持力层", "自重—基床—地基"), ("地基适应", "适应软弱覆盖层", "需地基加固和基床整平"), ("施工特点", "打桩、预制安装、现浇节点", "沉箱预制、浮运、安装、回填"), ("主要风险", "桩顶位移、节点质量", "沉降、基床质量、浮运窗口")]
    info_table(d, 120, 220, 930, 74, ["比较项", "高桩梁板式", "重力式沉箱"], rows, [0.22, 0.39, 0.39], size=22)
    draw_caisson_section(d, 1120, 235, 620, 465)
    d.text((1150, 740), "备选方案按可靠度、基底应力和浮运稳定验算", font=f(24), fill=COLORS["muted"])
    footer(d); slides.append(img)

    img, d = base_slide("十、高桩梁板式结构组成", "PHC管桩、桩帽、横梁、纵梁和面板", 11)
    add_image_panel(img, img_dir / "detail/fig5-1-phc-pile-cap-detail.png", (110, 185, 900, 835), "PHC管桩与桩帽构造")
    bullet_list(d, 980, 235, [
        "PHC管桩采用直径约800 mm管桩，穿越软弱土层后进入较好持力层。",
        "标准单元纵向长度取27 m，桩距按9 m控制。",
        "桩帽、横梁、纵梁和面板形成梁桩体系，设备荷载落在受力明确位置。",
        "前沿靠船构件、护舷和系船柱基础与横梁节点加强连接。"
    ], size=28, max_chars=22)
    footer(d); slides.append(img)

    img, d = base_slide("十一、梁板与靠船构件细部", "横梁、纵梁、轨道梁和前沿节点", 12)
    add_image_panel(img, img_dir / "detail/fig5-2-beam-slab-node-detail.png", (95, 185, 930, 815), "横梁、纵梁及轨道梁断面")
    add_image_panel(img, img_dir / "detail/fig5-3-berthing-component-detail.png", (990, 185, 1785, 815), "靠船构件、护舷及系船柱基础")
    d.text((150, 860), "横梁1800×2200，纵梁800×1200，面板厚度350，尺寸单位为mm。", font=f(25), fill=COLORS["ink"])
    footer(d); slides.append(img)

    img, d = base_slide("十二、沉箱方案计算边界", "沉箱、胸墙、基床、倒滤层和回填", 13)
    draw_caisson_section(d, 130, 210, 850, 600)
    rows = [("沉箱", "宽22 m，高13 m，单节长22 m", "提供主体自重和岸壁刚度"), ("胸墙", "现浇钢筋混凝土", "承受系缆、靠船及面层荷载"), ("基床", "抛石基床并整平", "控制承载力和沉降"), ("回填", "倒滤层+后方回填", "控制土压力与排水")]
    info_table(d, 1060, 245, 700, 70, ["构造", "取值", "作用"], rows, [0.22, 0.42, 0.36], size=21)
    footer(d); slides.append(img)

    img, d = base_slide("十三、结构计算荷载组合", "永久作用、可变作用和施工阶段作用", 14)
    rows = [("结构自重", "面板、梁、桩帽", "沉箱、胸墙、填料"), ("设备荷载", "轨道梁、横梁、桩列", "胸墙、基底应力"), ("船舶作用", "靠船构件、前排桩", "胸墙和整体稳定"), ("土压力", "后方连接段", "回填侧压力控制"), ("施工作用", "吊装、临时堆载", "浮运、安装、回填")]
    info_table(d, 135, 210, 1080, 68, ["荷载类型", "高桩梁板式控制部位", "沉箱式控制部位"], rows, [0.24, 0.38, 0.38], size=22)
    bullet_list(d, 1290, 245, ["正常使用组合控制裂缝、位移和轨道线形。", "承载能力组合控制梁板强度、桩基承载和整体稳定。", "施工阶段组合控制沉箱浮运、基床临时稳定和梁板吊装。"], size=27, max_chars=16)
    footer(d); slides.append(img)

    img, d = base_slide("十四、高桩梁板式：面板与梁格计算", "列公式、代入数值并形成结果表", 15)
    calc_box(d, 115, 195, 760, "面板均布荷载", ["g_s = γ_c h_s = 25×0.35 = 8.75 kN/m²", "q = q_g+q_p+q_e = 10.75+60+12"], "q = 82.75 kN/m²")
    calc_box(d, 115, 455, 760, "面板跨中弯矩", ["M = ql²/8", "M = 25×3.0²/8 = 28.13 kN·m"], "按板跨控制配筋")
    rows = [("面板自重", "8.75 kN/m²", "由板厚0.35 m确定"), ("计算均布荷载", "82.75 kN/m²", "含堆载和设备等效荷载"), ("面板弯矩", "28.13 kN·m", "普通板跨控制"), ("横梁控制弯矩", "按轨道轮压组合", "轨道带控制截面")]
    info_table(d, 965, 235, 820, 70, ["项目", "计算结果", "控制说明"], rows, [0.28, 0.32, 0.40], size=22)
    footer(d); slides.append(img)

    img, d = base_slide("十五、高桩梁板式：PHC桩承载计算", "竖向承载、水平作用和桩顶位移", 16)
    calc_box(d, 115, 205, 790, "单桩竖向反力", ["N = (G+Q)/n", "N = (5400+3600)/12 = 750 kN"], "小于单桩承载设计值")
    calc_box(d, 115, 465, 790, "水平力分配", ["H_p = H/n_f", "H_p = 900/6 = 150 kN"], "前排桩与靠船节点共同控制")
    rows = [("单桩竖向反力", "750 kN", "满足承载要求"), ("水平分配力", "150 kN", "前排桩控制"), ("桩顶位移", "按水平作用验算", "满足初步设计控制"), ("控制部位", "轨道梁、桩帽节点", "需加强配筋")]
    info_table(d, 1005, 245, 760, 68, ["计算项", "结果", "结论"], rows, [0.28, 0.27, 0.45], size=22)
    footer(d); slides.append(img)

    img, d = base_slide("十六、沉箱方案：可靠度与稳定验算", "按可靠指标替代单纯安全系数表述", 17)
    calc_box(d, 115, 190, 820, "有效竖向力", ["W = G_c+G_f+G_s-U", "W = 66250+87300+28600-17150"], "W = 165000 kN")
    calc_box(d, 115, 450, 820, "可靠指标", ["β = (R-S)/√(σ_R²+σ_S²)", "抗滑、抗倾、基底应力分别计算"], "指标满足初步验算要求")
    rows = [("抗滑可靠指标", "β_s ≈ 3.10", "满足"), ("抗倾可靠指标", "β_o ≈ 3.35", "满足"), ("基底应力", "e < B/6", "偏心距满足"), ("浮运稳定", "GM > 0", "浮态满足")]
    info_table(d, 1000, 235, 760, 72, ["项目", "计算结果", "结论"], rows, [0.32, 0.32, 0.36], size=22)
    footer(d); slides.append(img)

    img, d = base_slide("十七、工程量与概预算", "按主体、基床、回填、附属分项比较", 18)
    draw_bar_chart(d, 130, 220, 760, 500, [6500, 12200], ["高桩梁板式", "重力式沉箱"])
    rows = [("高桩梁板式", "约6500万元", "费用集中在PHC桩、梁板、钢筋和打桩措施"), ("重力式沉箱", "约12200万元", "费用集中在沉箱、基床、地基处理和回填"), ("费用差额", "约5700万元", "沉箱方案投资明显增加"), ("费用差率", "约87.7%", "同功能口径比较")]
    info_table(d, 950, 245, 830, 70, ["方案", "造价", "主要费用来源"], rows, [0.24, 0.23, 0.53], size=21)
    footer(d); slides.append(img)

    img, d = base_slide("十八、方案比选与推荐", "安全、地基、施工、运营和投资综合判断", 19)
    rows = [("结构安全", "梁板与桩基传力明确", "经加固后可满足稳定"), ("地基适应", "适应软弱覆盖层", "地基处理规模较大"), ("施工组织", "工艺成熟，节点可控", "预制、浮运、安装约束强"), ("运营维护", "局部维修较方便", "整体刚度大但修复复杂"), ("工程投资", "约6500万元", "约12200万元")]
    info_table(d, 130, 210, 1150, 66, ["指标", "高桩梁板式", "重力式沉箱"], rows, [0.22, 0.39, 0.39], size=21)
    d.rectangle((1350, 290, 1725, 560), fill="#eef5f4", outline=COLORS["accent"], width=3)
    d.text((1415, 350), "推荐方案", font=f(32, bold=True), fill=COLORS["accent"])
    d.text((1390, 420), "高桩梁板式码头", font=f(38, bold=True), fill=COLORS["ink"])
    d.text((1380, 515), "软基适应性、施工风险和投资控制更优", font=f(22), fill=COLORS["muted"])
    footer(d); slides.append(img)

    img, d = base_slide("十九、设计结论", "主要成果和后续复核重点", 20)
    bullet_list(d, 130, 220, [
        "完成5万吨级煤码头初步设计，泊位长度260 m，前沿设计水深12.50 m，码头面高程+3.60 m。",
        "装卸工艺采用卸船机、前沿漏斗、带式输送机、转运站和除尘系统组成连续接卸流程。",
        "高桩梁板式与重力式沉箱两种方案均完成构造说明、结构计算和概预算比较。",
        "推荐采用高桩梁板式码头结构，重点控制桩基承载、轨道梁内力、桩帽节点和耐久性构造。",
        "施工图阶段应结合详勘和设备厂家资料复核轮压、轨距、锚固件、配筋和节点细部。"
    ], size=30, max_chars=41)
    d.rectangle((1230, 280, 1710, 690), outline="#475569", width=2)
    d.text((1280, 350), "核心结论", font=f(38, bold=True), fill=COLORS["ink"])
    d.text((1278, 430), "结构安全可控", font=f(32), fill=COLORS["accent"])
    d.text((1278, 485), "软基适应性好", font=f(32), fill=COLORS["accent"])
    d.text((1278, 540), "工程投资较低", font=f(32), fill=COLORS["accent"])
    d.text((1278, 595), "施工组织成熟", font=f(32), fill=COLORS["accent"])
    footer(d); slides.append(img)

    SLIDES.mkdir(parents=True, exist_ok=True)
    for i, s in enumerate(slides, 1):
        p = SLIDES / f"slide_{i:02d}.png"
        s.save(p, quality=95)
        paths.append(p)
    return paths


def rels_xml(target: str, type_: str, rid: str) -> str:
    return f'<Relationship Id="{rid}" Type="{type_}" Target="{target}"/>'


def write_image_only_pptx(slide_paths: list[Path], pptx_path: Path):
    pptx_path.parent.mkdir(parents=True, exist_ok=True)
    cx, cy = 12192000, 6858000
    with zipfile.ZipFile(pptx_path, "w", zipfile.ZIP_DEFLATED) as z:
        overrides = [
            '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>',
            '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>',
            '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>',
            '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>',
        ]
        for i in range(1, len(slide_paths) + 1):
            overrides.append(f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>')
        content = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Default Extension="png" ContentType="image/png"/>'
            + "".join(overrides) + "</Types>"
        )
        z.writestr("[Content_Types].xml", content)
        z.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + rels_xml("ppt/presentation.xml", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument", "rId1") + "</Relationships>")
        sld_ids = "".join(f'<p:sldId id="{256+i}" r:id="rId{i+1}"/>' for i in range(1, len(slide_paths) + 1))
        pres = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>
<p:sldIdLst>{sld_ids}</p:sldIdLst>
<p:sldSz cx="{cx}" cy="{cy}" type="wide"/><p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>'''
        z.writestr("ppt/presentation.xml", pres)
        rels = [rels_xml("slideMasters/slideMaster1.xml", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster", "rId1")]
        for i in range(1, len(slide_paths) + 1):
            rels.append(rels_xml(f"slides/slide{i}.xml", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide", f"rId{i+1}"))
        z.writestr("ppt/_rels/presentation.xml.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + "".join(rels) + "</Relationships>")
        z.writestr("ppt/theme/theme1.xml", '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="ImageOnly"><a:themeElements><a:clrScheme name="Office"><a:dk1><a:sysClr val="windowText" lastClr="000000"/></a:dk1><a:lt1><a:sysClr val="window" lastClr="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="1F2937"/></a:dk2><a:lt2><a:srgbClr val="F8FAFC"/></a:lt2><a:accent1><a:srgbClr val="0F6F66"/></a:accent1><a:accent2><a:srgbClr val="A05413"/></a:accent2><a:accent3><a:srgbClr val="64748B"/></a:accent3><a:accent4><a:srgbClr val="94A3B8"/></a:accent4><a:accent5><a:srgbClr val="334155"/></a:accent5><a:accent6><a:srgbClr val="0F172A"/></a:accent6><a:hlink><a:srgbClr val="0563C1"/></a:hlink><a:folHlink><a:srgbClr val="954F72"/></a:folHlink></a:clrScheme><a:fontScheme name="Office"><a:majorFont><a:latin typeface="Arial"/><a:ea typeface="PingFang SC"/><a:cs typeface="Arial"/></a:majorFont><a:minorFont><a:latin typeface="Arial"/><a:ea typeface="PingFang SC"/><a:cs typeface="Arial"/></a:minorFont></a:fontScheme><a:fmtScheme name="Office"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:gradFill rotWithShape="1"/><a:gradFill rotWithShape="1"/></a:fillStyleLst><a:lnStyleLst><a:ln w="6350" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:prstDash val="solid"/></a:ln><a:ln w="12700" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:prstDash val="solid"/></a:ln><a:ln w="19050" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:prstDash val="solid"/></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle/><a:effectStyle/><a:effectStyle/></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme></a:themeElements><a:objectDefaults/><a:extraClrSchemeLst/></a:theme>''')
        master = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill><a:effectLst/></p:bgPr></p:bg><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMap accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" bg1="lt1" bg2="lt2" folHlink="folHlink" hlink="hlink" tx1="dk1" tx2="dk2"/><p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>'''
        z.writestr("ppt/slideMasters/slideMaster1.xml", master)
        z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + rels_xml("../slideLayouts/slideLayout1.xml", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout", "rId1") + rels_xml("../theme/theme1.xml", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme", "rId2") + "</Relationships>")
        layout = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1"><p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>'''
        z.writestr("ppt/slideLayouts/slideLayout1.xml", layout)
        z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + rels_xml("../slideMasters/slideMaster1.xml", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster", "rId1") + "</Relationships>")

        for i, p in enumerate(slide_paths, 1):
            z.write(p, f"ppt/media/image{i}.png")
            slide = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
<p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
<p:pic><p:nvPicPr><p:cNvPr id="2" name="slide_{i:02d}.png"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr><p:blipFill><a:blip r:embed="rId1"/><a:stretch><a:fillRect/></a:stretch></p:blipFill><p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>
</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'''
            z.writestr(f"ppt/slides/slide{i}.xml", slide)
            z.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + rels_xml(f"../media/image{i}.png", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image", "rId1") + "</Relationships>")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    slide_paths = build_slides()
    pptx = OUTPUT / "汕尾电厂配套煤码头工程初步设计_答辩PPT_图片版.pptx"
    write_image_only_pptx(slide_paths, pptx)
    print(pptx)
    print(f"slides={len(slide_paths)}")


if __name__ == "__main__":
    main()
