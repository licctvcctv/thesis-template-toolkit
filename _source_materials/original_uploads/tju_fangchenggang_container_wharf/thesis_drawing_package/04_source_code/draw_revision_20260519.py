import importlib.util
import math
import os
import sys
import time
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from cad import AcadSession, com_call


OUT_DIR = os.path.join(ROOT, "revision_2026_05_19", "output_five_plus")


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CaissonReferenceFallback:
    def monochrome_layers(self, d):
        for name in ["STRUCTURE", "CAISSON", "FOUNDATION", "BACKFILL", "HATCH", "TEXT", "DIM", "LEVEL", "CENTER"]:
            d.layer(name, 7 if name not in ["DIM", "HATCH", "CENTER"] else 8)

    def draw_main_section(self, d):
        x0, y0 = 90, 340
        d.text("沉箱标准断面", x0, y0 + 760, 30, "TEXT")
        d.polyline([(x0, y0), (x0 + 1080, y0), (x0 + 1080, y0 + 520), (x0 + 930, y0 + 650), (x0 + 150, y0 + 650), (x0, y0 + 520)], "CAISSON", True)
        for x in [230, 370, 510, 650, 790, 930]:
            d.line(x0 + x, y0 + 40, x0 + x, y0 + 610, "STRUCTURE")
        for y in [155, 285, 415]:
            d.line(x0 + 55, y0 + y, x0 + 1025, y0 + y, "STRUCTURE")
        d.rect(x0 - 60, y0 - 85, 1200, 70, "FOUNDATION")
        diag_hatch(d, x0 - 60, y0 - 85, 1200, 70, 18)
        level(d, x0 + 1130, x0 + 1280, y0 + 650, "+5.50", 20)
        level(d, x0 + 1130, x0 + 1280, y0 + 0, "-8.00", 20)
        dim_h(d, x0, x0 + 1080, y0, y0 - 145, "29.95m")
        dim_v(d, x0, y0, y0 + 650, x0 - 145, "13.50m")
        leader(d, x0 + 960, y0 + 555, x0 + 1320, y0 + 610, "现浇胸墙及护轮坎", 20)
        leader(d, x0 + 520, y0 + 275, x0 + 1320, y0 + 410, "沉箱舱格，外墙0.35m，内隔墙0.20m", 18)

    def draw_aa_plan(self, d):
        x0, y0 = 1470, 345
        d.text("A-A 平面舱格布置", x0, y0 + 760, 30, "TEXT")
        d.rect(x0, y0, 570, 650, "CAISSON")
        for x in [95, 190, 285, 380, 475]:
            d.line(x0 + x, y0, x0 + x, y0 + 650, "STRUCTURE")
        for y in [130, 260, 390, 520]:
            d.line(x0, y0 + y, x0 + 570, y0 + y, "STRUCTURE")
        for x in [120, 285, 450]:
            for y in [165, 325, 485]:
                d.circle(x0 + x, y0 + y, 18, "CENTER")
        dim_h(d, x0, x0 + 570, y0, y0 - 105, "12.50m")
        dim_v(d, x0, y0, y0 + 650, x0 - 105, "29.95m")
        d.text("预留孔/吊点及舱格示意", x0 + 120, y0 - 170, 18, "TEXT")


caisson_ref_path = os.path.join(ROOT, "caisson_only_reference_exact", "draw_caisson_exact.py")
caisson_ref = load_module("caisson_ref", caisson_ref_path) if os.path.exists(caisson_ref_path) else CaissonReferenceFallback()


def setup_layers(d):
    for name, color in [
        ("BORDER", 7),
        ("STRUCTURE", 7),
        ("CAISSON", 7),
        ("CYLINDER", 7),
        ("FOUNDATION", 8),
        ("BACKFILL", 8),
        ("HATCH", 8),
        ("TEXT", 7),
        ("NOTE", 7),
        ("DIM", 2),
        ("LEVEL", 7),
        ("CUT", 7),
        ("CENTER", 8),
        ("WATER", 8),
        ("ROAD", 8),
        ("RAIL", 7),
        ("LAND", 8),
        ("EQUIPMENT", 7),
        ("PROCESS", 2),
    ]:
        d.layer(name, color)


def dots(d, x, y, w, h, dx=55, dy=45, r=2.4, layer="HATCH"):
    yy = y + dy * 0.5
    while yy < y + h:
        xx = x + dx * 0.5
        while xx < x + w:
            d.circle(xx, yy, r, layer)
            xx += dx
        yy += dy


def fine_dots(d, x, y, w, h, dx=0.45, dy=0.36, r=0.025, layer="HATCH"):
    yy = y + dy * 0.5
    while yy < y + h:
        xx = x + dx * 0.5
        while xx < x + w:
            d.circle(xx, yy, r, layer)
            xx += dx
        yy += dy


def diag_hatch(d, x, y, w, h, spacing=24, layer="HATCH", angle=45):
    xmin, xmax = x, x + w
    ymin, ymax = y, y + h
    if angle >= 0:
        c = xmin - ymax
        end = xmax - ymin
        while c <= end:
            pts = []
            yy = xmin - c
            if ymin <= yy <= ymax:
                pts.append((xmin, yy))
            yy = xmax - c
            if ymin <= yy <= ymax:
                pts.append((xmax, yy))
            xx = ymin + c
            if xmin <= xx <= xmax:
                pts.append((xx, ymin))
            xx = ymax + c
            if xmin <= xx <= xmax:
                pts.append((xx, ymax))
            if len(pts) >= 2:
                d.line(pts[0][0], pts[0][1], pts[1][0], pts[1][1], layer)
            c += spacing
    else:
        c = xmin + ymin
        end = xmax + ymax
        while c <= end:
            pts = []
            yy = c - xmin
            if ymin <= yy <= ymax:
                pts.append((xmin, yy))
            yy = c - xmax
            if ymin <= yy <= ymax:
                pts.append((xmax, yy))
            xx = c - ymin
            if xmin <= xx <= xmax:
                pts.append((xx, ymin))
            xx = c - ymax
            if xmin <= xx <= xmax:
                pts.append((xx, ymax))
            if len(pts) >= 2:
                d.line(pts[0][0], pts[0][1], pts[1][0], pts[1][1], layer)
            c += spacing


def clipped_hatch_m(d, x, y, w, h, spacing=0.18, layer="HATCH"):
    diag_hatch(d, x, y, w, h, spacing, layer)


def slope_ticks(d, x1, y1, x2, y2, spacing=65, tick=26, layer="HATCH"):
    dx = x2 - x1
    dy = y2 - y1
    length = (dx * dx + dy * dy) ** 0.5
    if length <= 0:
        return
    ux, uy = dx / length, dy / length
    nx, ny = -uy, ux
    t = spacing
    while t < length:
        x = x1 + ux * t
        y = y1 + uy * t
        d.line(x, y, x + nx * tick, y + ny * tick, layer)
        t += spacing


def dim_h(d, x1, x2, y_line, y_dim, text):
    d.dim_rotated((x1, y_line, 0), (x2, y_line, 0), ((x1 + x2) / 2, y_dim, 0), 0, text)


def dim_v(d, x_line, y1, y2, x_dim, text):
    d.dim_rotated((x_line, y1, 0), (x_line, y2, 0), (x_dim, (y1 + y2) / 2, 0), math.pi / 2, text)


def level(d, x1, x2, y, text, h=22):
    d.line(x1, y, x2, y, "LEVEL")
    d.text(f"▽{text}", x2 + h * 0.7, y + h * 0.22, h, "TEXT")


def leader(d, x1, y1, x2, y2, text, h=22):
    d.leader(x1, y1, x2, y2, text, h, "TEXT")


def draw_container_slots(d, x, y, w, h, rows=2, cols=6):
    d.rect(x, y, w, h, "CENTER")
    gap_x = w / cols
    gap_y = h / rows
    for i in range(1, cols):
        d.line(x + gap_x * i, y, x + gap_x * i, y + h, "CENTER")
    for j in range(1, rows):
        d.line(x, y + gap_y * j, x + w, y + gap_y * j, "CENTER")


def draw_rail(d, x1, y, x2, label):
    d.line(x1, y - 1.2, x2, y - 1.2, "RAIL")
    d.line(x1, y + 1.2, x2, y + 1.2, "RAIL")
    x = x1
    while x <= x2:
        d.line(x, y - 2.8, x, y + 2.8, "RAIL")
        x += 12
    d.text(label, x1 + 8, y + 5, 4.2, "TEXT")


def north_arrow(d, x, y, size=38):
    d.north_arrow(x, y, size, "TEXT")


def draw_simple_legend(d, x, y, text_h=3.0):
    rows = [
        ("岸桥/装卸设备", "EQUIPMENT"),
        ("港内道路", "ROAD"),
        ("铁路装卸线", "RAIL"),
        ("箱区/堆场", "CENTER"),
        ("装卸工艺流线", "PROCESS"),
        ("水域/航道", "WATER"),
    ]
    d.rect(x, y - 50, 84, 50, "BORDER")
    d.text("图例", x + 3, y - 7, text_h * 1.2, "TEXT")
    yy = y - 14
    for label, layer in rows:
        if layer == "PROCESS":
            d.arrow(x + 5, yy - 1, x + 20, yy - 1, layer, 2.6)
        elif layer == "RAIL":
            d.line(x + 5, yy - 2, x + 20, yy - 2, layer)
            d.line(x + 5, yy + 1, x + 20, yy + 1, layer)
        else:
            d.rect(x + 5, yy - 4, 15, 5, layer)
        d.text(label, x + 25, yy - 4, text_h, "TEXT")
        yy -= 6


def draw_ship_outline(d, cx, cy, length=230, beam=36):
    bow = length * 0.12
    pts = [
        (cx - length / 2 + bow, cy - beam / 2),
        (cx + length / 2 - bow, cy - beam / 2),
        (cx + length / 2, cy),
        (cx + length / 2 - bow, cy + beam / 2),
        (cx - length / 2 + bow, cy + beam / 2),
        (cx - length / 2, cy),
    ]
    d.polyline(pts, "WATER", True)
    d.text("3万吨级集装箱船靠泊示意", cx - 58, cy - 4, 3.5, "TEXT")


def enforce_min_text_height(d, min_height):
    for index in range(d.count_entities()):
        try:
            ent = d.ms.Item(index)
            name = str(ent.ObjectName)
            if name in ("AcDbText", "AcDbMText") and float(ent.Height) < min_height:
                ent.Height = float(min_height)
        except Exception:
            pass


class OffsetDrawing:
    def __init__(self, drawing, dx=0, dy=0):
        self._drawing = drawing
        self.dx = dx
        self.dy = dy

    def __getattr__(self, name):
        return getattr(self._drawing, name)

    def _xy(self, x, y):
        return x + self.dx, y + self.dy

    def _point(self, p):
        return (p[0] + self.dx, p[1] + self.dy, p[2]) if len(p) > 2 else (p[0] + self.dx, p[1] + self.dy)

    def line(self, x1, y1, x2, y2, *args, **kwargs):
        return self._drawing.line(x1 + self.dx, y1 + self.dy, x2 + self.dx, y2 + self.dy, *args, **kwargs)

    def rect(self, x, y, w, h, *args, **kwargs):
        return self._drawing.rect(x + self.dx, y + self.dy, w, h, *args, **kwargs)

    def circle(self, x, y, radius, *args, **kwargs):
        return self._drawing.circle(x + self.dx, y + self.dy, radius, *args, **kwargs)

    def polyline(self, coords, *args, **kwargs):
        return self._drawing.polyline([(x + self.dx, y + self.dy) for x, y in coords], *args, **kwargs)

    def text(self, value, x, y, height, *args, **kwargs):
        return self._drawing.text(value, x + self.dx, y + self.dy, height, *args, **kwargs)

    def mtext(self, value, x, y, width, height, *args, **kwargs):
        return self._drawing.mtext(value, x + self.dx, y + self.dy, width, height, *args, **kwargs)

    def dim_rotated(self, p1, p2, loc, *args, **kwargs):
        return self._drawing.dim_rotated(self._point(p1), self._point(p2), self._point(loc), *args, **kwargs)

    def dim_aligned(self, p1, p2, loc, *args, **kwargs):
        return self._drawing.dim_aligned(self._point(p1), self._point(p2), self._point(loc), *args, **kwargs)

    def dim_diameter(self, p1, p2, *args, **kwargs):
        return self._drawing.dim_diameter(self._point(p1), self._point(p2), *args, **kwargs)

    def leader(self, x1, y1, x2, y2, *args, **kwargs):
        return self._drawing.leader(x1 + self.dx, y1 + self.dy, x2 + self.dx, y2 + self.dy, *args, **kwargs)

    def arrow(self, x1, y1, x2, y2, *args, **kwargs):
        return self._drawing.arrow(x1 + self.dx, y1 + self.dy, x2 + self.dx, y2 + self.dy, *args, **kwargs)


def draw_a1_sheet(d, title, drawing_no, scale, x, y, w, designer="褚喆", checker="褚喆"):
    """Draw an A1 landscape sheet frame in model space."""
    h = w * 594.0 / 841.0
    margin = w * 0.028
    inner_x = x + margin
    inner_y = y + margin
    inner_w = w - 2 * margin
    inner_h = h - 2 * margin
    line_h = h * 0.012
    title_h = h * 0.023
    small_h = h * 0.009
    table_w = w * 0.285
    table_h = h * 0.068
    table_x = inner_x + inner_w - table_w
    table_y = inner_y

    d.rect(x, y, w, h, "BORDER")
    d.rect(inner_x, inner_y, inner_w, inner_h, "BORDER")

    title_y = inner_y + table_h + h * 0.018
    d.text(title, x + w * 0.39, title_y, title_h, "TEXT")
    d.line(x + w * 0.35, title_y - title_h * 0.35, x + w * 0.66, title_y - title_h * 0.35, "BORDER")

    d.rect(table_x, table_y, table_w, table_h, "BORDER")
    d.line(table_x + table_w * 0.68, table_y, table_x + table_w * 0.68, table_y + table_h, "BORDER")
    d.line(table_x, table_y + table_h * 0.36, table_x + table_w, table_y + table_h * 0.36, "BORDER")
    d.line(table_x, table_y + table_h * 0.68, table_x + table_w, table_y + table_h * 0.68, "BORDER")
    d.line(table_x + table_w * 0.34, table_y, table_x + table_w * 0.34, table_y + table_h * 0.36, "BORDER")

    title_cell_h = small_h * (1.05 if len(title) > 16 else 1.35)
    d.text(title, table_x + table_w * 0.05, table_y + table_h * 0.50, title_cell_h, "TEXT")
    d.text(f"比例  {scale}", table_x + table_w * 0.72, table_y + table_h * 0.73, small_h, "TEXT")
    d.text(f"图号  {drawing_no}", table_x + table_w * 0.72, table_y + table_h * 0.46, small_h, "TEXT")
    d.text("制图", table_x + table_w * 0.05, table_y + table_h * 0.16, small_h, "TEXT")
    d.text(designer, table_x + table_w * 0.23, table_y + table_h * 0.16, small_h, "TEXT")
    d.text("审核", table_x + table_w * 0.39, table_y + table_h * 0.16, small_h, "TEXT")
    d.text(checker, table_x + table_w * 0.56, table_y + table_h * 0.16, small_h, "TEXT")
    d.text("港口一班", table_x + table_w * 0.72, table_y + table_h * 0.16, small_h * 0.95, "TEXT")


def draw_general_layout_revised(acad):
    d = acad.new_drawing(dimtxt=5.0, precision=1)
    setup_layers(d)
    berth_l = 300.0
    depth = 850.0
    d.coordinate_grid(0, 0, berth_l, depth, 100, 100, 2.8)
    north_arrow(d, 372, 780, 52)
    d.rect(0, 0, berth_l, depth, "LAND")
    d.rect(-6, -6, berth_l + 12, depth + 12, "BORDER")
    d.text("港区封闭围网", 305, 705, 3.0, "TEXT", rotation=90)
    d.line(0, 0, berth_l, 0, "STRUCTURE")
    d.text("码头前沿线 L=300m", 92, 8, 4.5, "TEXT")

    # Water area.
    d.rect(-120, -90, 540, 90, "WATER")
    draw_ship_outline(d, 150, -32, 225, 34)
    d.line(0, -65, 300, -65, "WATER")
    d.text("停泊水域 B=65m", 95, -42, 4.0, "TEXT")
    pts = []
    for i in range(144):
        a = 2 * math.pi * i / 144
        pts.append((150 + 250 * math.cos(a), -325 + 200 * math.sin(a)))
    d.polyline(pts, "WATER", True)
    d.text("回旋水域 500m x 400m", 60, -325, 4.2, "TEXT")
    d.line(-170, -555, 470, -555, "CENTER", "CENTER")
    d.line(-170, -630, 470, -630, "WATER")
    d.line(-170, -480, 470, -480, "WATER")
    d.text("航道有效宽150m", 96, -548, 4.2, "TEXT")

    # Quayside apron and process lane.
    d.rect(0, 0, 300, 85, "ROAD")
    d.line(0, 18, 300, 18, "RAIL")
    d.line(0, 32, 300, 32, "RAIL")
    d.text("岸桥海侧轨", 6, 20, 2.4, "TEXT")
    d.text("岸桥陆侧轨", 6, 34, 2.4, "TEXT")
    for x in range(20, 290, 24):
        d.line(x, 58, x + 14, 58, "ROAD")
    d.text("前沿作业带：岸桥轨道+集卡循环道+舱盖板临时区", 20, 50, 3.8, "TEXT")
    for x in [38, 112, 188, 262]:
        d.rect(x - 10, -7, 20, 18, "EQUIPMENT")
        d.text("QC", x - 5, 14, 3.2, "TEXT")
        d.arrow(x, 42, x + 26, 42, "PROCESS", 5.0)

    # Internal road system separated from rail.
    d.rect(0, 85, 24, 740, "ROAD")
    d.rect(276, 85, 24, 740, "ROAD")
    d.rect(0, 825, 300, 25, "ROAD")
    for y in [85, 315, 545, 645]:
        d.rect(0, y, 300, 15, "ROAD")
    d.text("港内主干道25m（公路集卡）", 184, 835, 3.6, "TEXT")
    d.text("港内次干道15m（箱区间道路）", 175, 552, 3.4, "TEXT")
    for y in [101, 331, 561, 661, 841]:
        d.arrow(40, y, 82, y, "PROCESS", 3.2)
        d.arrow(260, y, 218, y, "PROCESS", 3.2)

    # Yard blocks, expanded and closer to a real terminal: vertical blocks + inter-block lanes.
    block_xs = [35, 75, 115, 155, 195, 235]
    for idx, x in enumerate(block_xs, 1):
        draw_container_slots(d, x, 115, 28, 180, 6, 2)
        draw_container_slots(d, x, 335, 28, 180, 6, 2)
        d.line(x - 1.5, 115, x - 1.5, 295, "RAIL")
        d.line(x + 29.5, 115, x + 29.5, 295, "RAIL")
        d.line(x - 1.5, 335, x - 1.5, 515, "RAIL")
        d.line(x + 29.5, 335, x + 29.5, 515, "RAIL")
        d.text(f"重箱{idx}", x + 1.8, 205, 3.0, "TEXT", rotation=90)
        d.text(f"空箱{idx}", x + 1.8, 425, 3.0, "TEXT", rotation=90)
        d.text("RMG", x + 4, 298, 2.4, "TEXT")
    d.rect(35, 575, 76, 45, "STRUCTURE")
    d.text("冷藏箱区", 47, 594, 3.8, "TEXT")
    for x in range(42, 105, 14):
        d.rect(x, 578, 6, 6, "EQUIPMENT")
    d.rect(126, 575, 72, 45, "STRUCTURE")
    d.text("查验/海关", 137, 594, 3.8, "TEXT")
    d.rect(213, 575, 52, 45, "STRUCTURE")
    d.text("危品箱区", 220, 594, 3.2, "TEXT")
    d.rect(35, 625, 230, 12, "ROAD")
    d.text("消防/检修通道", 125, 629, 2.8, "TEXT")

    # Rail loading zone at rear, physically separated from roads.
    d.rect(25, 665, 250, 88, "STRUCTURE")
    d.text("铁路装卸区（位于堆场后方，和港内道路分区）", 42, 742, 4.0, "TEXT")
    draw_rail(d, 38, 705, 262, "铁路装卸线")
    draw_rail(d, 38, 682, 262, "铁路到发线")
    d.rect(35, 715, 220, 22, "EQUIPMENT")
    d.text("轨道吊/RMG换装带", 91, 722, 3.4, "TEXT")
    for x in range(48, 252, 24):
        d.rect(x, 718, 16, 6, "CENTER")

    # Gate, buffer, auxiliary zone.
    d.rect(25, 770, 120, 46, "ROAD")
    d.text("进港闸口6车道", 46, 791, 3.7, "TEXT")
    for i in range(6):
        d.line(37 + i * 16, 772, 37 + i * 16, 814, "BORDER")
    d.rect(158, 770, 56, 46, "STRUCTURE")
    d.text("缓冲停车区", 165, 792, 3.4, "TEXT")
    d.rect(226, 770, 49, 46, "STRUCTURE")
    d.text("生产辅助", 234, 792, 3.2, "TEXT")
    d.rect(226, 724, 49, 34, "STRUCTURE")
    d.text("机修/备件", 234, 740, 3.0, "TEXT")
    d.rect(158, 724, 56, 34, "STRUCTURE")
    d.text("管理用房", 167, 740, 3.0, "TEXT")
    d.arrow(95, 825, 95, 760, "PROCESS", 5)
    d.arrow(275, 620, 275, 95, "PROCESS", 5)
    d.arrow(24, 95, 24, 620, "PROCESS", 5)
    d.text("装卸工艺流线：岸桥 -> 集卡/AGV -> 堆场 -> 闸口/铁路", -115, 875, 4.0, "TEXT")
    draw_simple_legend(d, 338, 725, 3.0)

    # Dimensions and legend.
    dim_h(d, 0, 300, 0, -105, "300m")
    dim_v(d, 300, 0, 850, 335, "850m")
    dim_v(d, 0, -65, 0, -32, "65m")
    d.table(
        -120,
        830,
        [45, 85],
        18,
        [
            ["项目", "布置说明"],
            ["水域", "停泊65m，回旋500x400m，航道150m"],
            ["堆场", "重箱/空箱垂直岸线布置，箱区间设次干道"],
            ["道路", "港内主干道25m，次干道15m，环形组织"],
            ["铁路", "后方独立铁路装卸区，设到发线和装卸线"],
            ["工艺", "岸桥+集卡/AGV+场桥/RMG，公铁分流"],
            ["设备", "4台岸桥、12条RMG箱区轨道、铁路换装RMG"],
        ],
        3.0,
    )
    d.table(
        318,
        150,
        [42, 56],
        16,
        [
            ["道路分级", "宽度/功能"],
            ["主干道", "25m，环形集卡主通道"],
            ["次干道", "15m，箱区横向连接"],
            ["支路", "箱区端部作业通道"],
            ["铁路通道", "堆场后方独立布置"],
        ],
        2.8,
    )
    enforce_min_text_height(d, 4.0)
    draw_a1_sheet(d, "集装箱码头总平面布置图", "G-01", "1:2000", -900, -760, 2350)
    path = os.path.join(OUT_DIR, "G-01_general_layout_revised_rail_road.dwg")
    count = d.save(path)
    d.close()
    return path, count


def draw_caisson_plan_elevation_revised(acad):
    d = acad.new_drawing(dimtxt=1.8, precision=2)
    setup_layers(d)
    # Plan view.
    d.text("平面图", 0, 31, 2.4, "TEXT")
    for i in range(10):
        x = i * 30.0 + 0.025
        d.rect(x, 0, 29.95, 12.5, "CAISSON")
        d.text(f"C{i+1:02d}", x + 12.3, 5.55, 1.4, "TEXT")
        # Internal cells: 3 columns x 3 bands plus wall strips.
        for yy in [4.2, 8.3]:
            d.line(x + 0.35, yy, x + 29.6, yy, "CAISSON")
        for xx in [x + 7.5, x + 15.0, x + 22.5]:
            d.line(xx, 0.35, xx, 12.15, "CAISSON")
        d.rect(x, 12.5, 29.95, 1.1, "STRUCTURE")
        for fx in [x + 7.5, x + 22.5]:
            d.rect(fx - 0.45, -1.45, 0.9, 1.45, "EQUIPMENT")
            d.text("F", fx - 0.25, -2.65, 0.9, "TEXT")
        bx = x + 15.0
        d.circle(bx, 3.0, 0.8, "EQUIPMENT")
        d.text("B", bx - 0.28, 4.15, 0.9, "TEXT")
    for x in range(0, 301, 30):
        d.line(x, -4.5, x, 18.5, "CUT", "DASHED")
        d.text(f"K0+{x:03d}", x + 0.7, -6.0, 1.0, "TEXT")
    d.text("现浇C40胸墙平面范围 B=12.50m", 104, 15.0, 1.35, "TEXT")
    d.text("护舷2组/箱，系船柱1个/分段", 98, -3.0, 1.1, "TEXT")
    dim_h(d, 0, 300, 0, -12, "300.00m")
    dim_h(d, 0, 30, 0, -8, "30.00m")
    dim_v(d, 300, 0, 12.5, 315, "12.50m")

    # Elevation view.
    base_y = -45
    d.text("立面图", 0, base_y + 20, 2.4, "TEXT")
    d.rect(0, base_y, 300, 13.5, "CAISSON")
    for x in range(0, 301, 30):
        d.line(x, base_y, x, base_y + 15.5, "CUT", "DASHED")
    d.rect(0, base_y + 13.5, 300, 2.0, "STRUCTURE")
    for x in range(15, 300, 30):
        d.circle(x, base_y + 17.2, 0.65, "EQUIPMENT")
    level(d, -34, -8, base_y + 15.5, "+5.50", 1.15)
    level(d, -34, -8, base_y + 13.5, "+3.50", 1.15)
    level(d, -34, -8, base_y, "-10.00", 1.15)
    level(d, -34, -8, base_y - 3.0, "-13.00基床底", 1.15)
    d.rect(0, base_y - 3.0, 300, 3.0, "FOUNDATION")
    clipped_hatch_m(d, 0, base_y - 3.0, 300, 3.0, 0.55)
    dim_v(d, 305, base_y, base_y + 13.5, 320, "13.50m")
    dim_h(d, 0, 300, base_y, base_y - 7, "300.00m")

    # Key plan and check table to make the sheet less empty.
    d.table(
        0,
        base_y - 18,
        [42, 52, 78],
        5,
        [
            ["项目", "设计值", "说明"],
            ["沉箱数量", "10座", "每30m一段"],
            ["单座尺寸", "29.95x12.50x13.50m", "C45预制"],
            ["舱格", "3列x多格", "外墙0.35m，内隔墙0.20m"],
            ["胸墙", "高2.0m，顶+5.50m", "C40现浇，设剪力槽"],
            ["附属设施", "护舷20组，系船柱10个", "沿前沿均布"],
        ],
        1.1,
    )
    d.text("注：本图为沉箱方案结构平立面布置，断面、节点与配筋详见S-02。", 0, base_y - 54, 1.2, "NOTE")
    enforce_min_text_height(d, 1.25)
    draw_a1_sheet(d, "沉箱结构平面及立面图", "S-01", "1:500", -58, -188, 425)
    try:
        com_call(d.doc.Application.ZoomExtents)
    except Exception:
        pass
    path = os.path.join(OUT_DIR, "S-01_caisson_plan_elevation_revised.dwg")
    count = d.save(path)
    d.close()
    return path, count


def draw_caisson_small_details(d, x0, y0):
    d.text("细部构造", x0, y0 + 315, 28, "TEXT")
    # Joint.
    d.text("1 变形缝", x0, y0 + 270, 20, "TEXT")
    d.rect(x0, y0 + 120, 115, 130, "CAISSON")
    d.rect(x0 + 128, y0 + 120, 115, 130, "CAISSON")
    diag_hatch(d, x0, y0 + 120, 115, 130, 12)
    diag_hatch(d, x0 + 128, y0 + 120, 115, 130, 12)
    d.rect(x0 + 115, y0 + 120, 13, 130, "CUT")
    d.text("20mm沥青麻絮", x0 + 65, y0 + 262, 16, "TEXT")
    # Fender.
    fx = x0 + 330
    d.text("2 护舷安装", fx, y0 + 270, 20, "TEXT")
    d.rect(fx + 90, y0 + 115, 32, 145, "STRUCTURE")
    d.rect(fx + 20, y0 + 160, 70, 58, "EQUIPMENT")
    d.circle(fx + 105, y0 + 172, 5, "EQUIPMENT")
    d.circle(fx + 105, y0 + 205, 5, "EQUIPMENT")
    d.text("鼓型橡胶护舷", fx + 145, y0 + 210, 16, "TEXT")
    d.text("预埋锚栓", fx + 145, y0 + 170, 16, "TEXT")
    # Bedding/filter.
    bx = x0 + 660
    d.text("3 基床及倒滤层", bx, y0 + 270, 20, "TEXT")
    d.rect(bx, y0 + 105, 250, 45, "FOUNDATION")
    diag_hatch(d, bx, y0 + 105, 250, 45, 10)
    dots(d, bx + 270, y0 + 105, 125, 150, 18, 16, 1.5)
    d.text("10~100kg块石基床", bx + 20, y0 + 82, 15, "TEXT")
    d.text("二片石0.3m+碎石0.2m+土工布", bx + 250, y0 + 262, 15, "TEXT")


def draw_caisson_rebar(d, x0, y0):
    d.text("代表构件配筋", x0, y0 + 300, 28, "TEXT")
    d.text("4 沉箱前壁配筋", x0, y0 + 255, 20, "TEXT")
    d.rect(x0, y0 + 30, 120, 210, "CAISSON")
    diag_hatch(d, x0, y0 + 30, 120, 210, 11)
    for x in range(18, 112, 18):
        d.line(x0 + x, y0 + 42, x0 + x, y0 + 226, "STRUCTURE")
    for y in range(55, 225, 22):
        d.line(x0 + 12, y0 + y, x0 + 108, y0 + y, "STRUCTURE")
    d.text("竖向主筋 HRB400 C18@150", x0 + 145, y0 + 200, 15, "TEXT")
    d.text("水平分布筋 HRB400 C14@200", x0 + 145, y0 + 170, 15, "TEXT")
    d.text("保护层 50mm", x0 + 145, y0 + 140, 15, "TEXT")

    bx = x0 + 520
    d.text("5 底板配筋", bx, y0 + 255, 20, "TEXT")
    d.rect(bx, y0 + 115, 260, 65, "CAISSON")
    diag_hatch(d, bx, y0 + 115, 260, 65, 11)
    for x in range(20, 250, 22):
        d.line(bx + x, y0 + 122, bx + x, y0 + 174, "STRUCTURE")
    for y in [128, 146, 164]:
        d.line(bx + 12, y0 + y, bx + 248, y0 + y, "STRUCTURE")
    d.text("底板厚0.50m，双层双向 HRB400 C18@150", bx, y0 + 82, 15, "TEXT")

    cx = x0 + 920
    d.text("6 胸墙配筋", cx, y0 + 255, 20, "TEXT")
    d.polyline([(cx, y0 + 55), (cx + 270, y0 + 55), (cx + 270, y0 + 165), (cx + 35, y0 + 165), (cx + 35, y0 + 195), (cx, y0 + 195)], "STRUCTURE", True)
    diag_hatch(d, cx, y0 + 55, 270, 110, 11)
    for x in range(20, 260, 24):
        d.line(cx + x, y0 + 66, cx + x, y0 + 154, "STRUCTURE")
    for y in [75, 100, 125, 150]:
        d.line(cx + 12, y0 + y, cx + 258, y0 + y, "STRUCTURE")
    d.text("胸墙C40，顶面+5.50m", cx + 295, y0 + 155, 15, "TEXT")
    d.text("主筋 HRB400 C20@150", cx + 295, y0 + 125, 15, "TEXT")
    d.text("箍筋/分布筋 HRB400 C12@200", cx + 295, y0 + 95, 15, "TEXT")


def draw_caisson_combined(acad):
    d = acad.new_drawing(dimtxt=22, precision=0)
    caisson_ref.monochrome_layers(d)
    setup_layers(d)
    ref_d = OffsetDrawing(d, dx=180, dy=0)
    caisson_ref.draw_main_section(ref_d)
    caisson_ref.draw_aa_plan(ref_d)
    draw_caisson_small_details(d, 180, -515)
    draw_caisson_rebar(d, 180, -900)
    d.table(
        3420,
        -70,
        [185, 430],
        54,
        [
            ["沉箱方案参数", "取值"],
            ["码头长度/分段", "300m / 10段"],
            ["单座沉箱", "29.95m x 12.50m x 13.50m"],
            ["结构材料", "沉箱C45，胸墙C40"],
            ["墙厚", "外墙0.35m，内隔墙0.20m"],
            ["附属设施", "1500kN系船柱1个/段，护舷2组/箱"],
        ],
        17,
    )
    d.table(
        3420,
        -470,
        [185, 430],
        50,
        [
            ["施工顺序", "控制要点"],
            ["1 基槽开挖", "开挖至持力层并整平"],
            ["2 基床抛石", "分层抛填、夯实、整平"],
            ["3 沉箱安装", "定位、压载、坐床复测"],
            ["4 回填/倒滤", "分层回填，接缝处加厚倒滤"],
            ["5 胸墙及面层", "现浇、养护、安装附属设施"],
        ],
        16,
    )
    d.text("说明：本图按原沉箱示意图复刻断面，并将细部构造和代表构件配筋合并在同一张图纸内。", 180, -1015, 18, "TEXT")
    enforce_min_text_height(d, 16)
    draw_a1_sheet(d, "沉箱结构断面、细部构造及代表配筋图", "S-02", "1:100/1:50", 0, -1420, 4700)
    try:
        com_call(d.doc.Application.ZoomExtents)
    except Exception:
        pass
    path = os.path.join(OUT_DIR, "S-02_caisson_section_detail_rebar_combined.dwg")
    count = d.save(path)
    d.close()
    return path, count


def draw_cylinder_section_core(d, x0=530, y0=60):
    outer_d = 1200
    wall = 35
    height = 1550
    top_y = y0 + height
    chest_h = 150
    chest_top = top_y + chest_h

    # Rubble bed and foundation.
    d.polyline([(x0 - 330, y0 - 200), (x0 + outer_d + 260, y0 - 200), (x0 + outer_d + 260, y0), (x0 - 20, y0), (x0 - 330, y0 - 80)], "FOUNDATION", True)
    diag_hatch(d, x0 - 330, y0 - 200, outer_d + 590, 200, 40)
    d.text("10~100kg块石基床", x0 + 300, y0 - 258, 26, "TEXT")
    slope_ticks(d, x0 - 330, y0 - 80, x0 - 20, y0, 60)
    for cx in [x0 - 230, x0 - 145, x0 + outer_d + 95, x0 + outer_d + 170]:
        d.circle(cx, y0 - 90, 23, "FOUNDATION")

    # Cylinder section: drawn as rectangular cut of the circular shell.
    d.rect(x0, y0, outer_d, height, "CYLINDER")
    d.rect(x0 + wall, y0 + wall, outer_d - 2 * wall, height - wall, "CYLINDER")
    diag_hatch(d, x0, y0, outer_d, wall, 18)
    diag_hatch(d, x0, y0, wall, height, 18)
    diag_hatch(d, x0 + outer_d - wall, y0, wall, height, 18)
    dots(d, x0 + 80, y0 + 80, outer_d - 160, height - 150, 70, 60, 2.4)
    d.text("筒内回填开山土石", x0 + 410, y0 + 820, 28, "TEXT")
    d.text("大圆筒 C45", x0 + 420, y0 + 600, 28, "TEXT")

    # Top chest wall and pavement, following the reference outline.
    d.polyline([
        (x0 - 250, top_y),
        (x0 + outer_d + 250, top_y),
        (x0 + outer_d + 250, chest_top),
        (x0 - 250, chest_top),
    ], "STRUCTURE", True)
    diag_hatch(d, x0 - 250, top_y, outer_d + 500, chest_h, 28)
    d.rect(x0 + 90, top_y, 170, -60, "STRUCTURE")
    d.text("现浇C40胸墙", x0 + 250, top_y + 68, 26, "TEXT")
    d.text("电缆槽", x0 + 135, top_y + 20, 20, "TEXT")
    d.line(x0 - 250, chest_top, x0 + outer_d + 1520, chest_top, "STRUCTURE")
    d.text("地面/堆场面", x0 + outer_d + 820, chest_top + 18, 24, "TEXT")

    # Rear backfill and filter.
    bx = x0 + outer_d
    d.polyline([(bx, y0), (bx + 850, y0 + 320), (bx + 960, chest_top), (bx, chest_top)], "BACKFILL", True)
    dots(d, bx + 55, y0 + 80, 760, height + 80, 75, 64, 2.2)
    d.text("回填", bx + 385, y0 + 760, 28, "TEXT", rotation=90)
    d.polyline([(bx, y0 + 110), (bx + 150, y0 + 170), (bx + 150, top_y - 120), (bx, top_y - 80)], "FOUNDATION", False)
    d.text("倒滤层", bx + 185, y0 + 790, 22, "TEXT", rotation=78)
    d.line(bx + 450, y0 - 240, bx + 930, chest_top - 310, "FOUNDATION")
    slope_ticks(d, bx + 450, y0 - 240, bx + 930, chest_top - 310, 75)
    d.text("1:1.5", bx + 750, y0 + 490, 26, "TEXT", rotation=56)

    # Water levels and project elevations.
    level(d, x0 - 540, x0 - 300, chest_top, "+5.50")
    level(d, x0 - 540, x0 - 300, top_y, "+4.00")
    level(d, x0 - 540, x0 - 300, top_y - 173, "设计高水位 +2.27")
    level(d, x0 - 540, x0 - 300, top_y - 350, "设计低水位 +0.50")
    level(d, x0 - 540, x0 - 300, y0, "-11.50")
    level(d, x0 - 540, x0 - 300, y0 - 150, "-13.00")

    # Dimensions.
    dim_h(d, x0, x0 + outer_d, y0, y0 - 105, "1200")
    dim_h(d, x0 - 200, x0, y0, y0 - 105, "200")
    dim_h(d, x0 + outer_d, x0 + outer_d + 200, y0, y0 - 105, "200")
    dim_h(d, x0 - 330, x0 + outer_d + 270, y0 - 200, y0 - 335, "1600")
    dim_v(d, x0, y0, top_y, x0 - 170, "1550")
    dim_v(d, x0, top_y, chest_top, x0 - 105, "150")
    dim_h(d, x0, x0 + wall, top_y + 18, top_y + 80, "35")
    dim_h(d, x0 + outer_d - wall, x0 + outer_d, top_y + 18, top_y + 80, "35")
    leader(d, bx + 2, y0 + 820, bx + 230, y0 + 980, "圆筒壁厚0.35m", 22)
    leader(d, bx + 120, y0 + 260, bx + 315, y0 + 350, "二片石0.3m+碎石0.2m", 20)


def draw_cylinder_details_and_rebar(d, x0, y0):
    d.text("细部构造及配筋", x0, y0 + 1180, 30, "TEXT")
    # Top joint/cable.
    d.text("1 胸墙及电缆槽", x0, y0 + 1125, 22, "TEXT")
    d.polyline([(x0, y0 + 960), (x0 + 360, y0 + 960), (x0 + 360, y0 + 1075), (x0 + 35, y0 + 1075), (x0 + 35, y0 + 1110), (x0, y0 + 1110)], "STRUCTURE", True)
    diag_hatch(d, x0, y0 + 960, 360, 115, 12)
    d.rect(x0 + 80, y0 + 1040, 60, 40, "EQUIPMENT")
    d.text("0.60x0.40m电缆槽", x0 + 165, y0 + 1048, 16, "TEXT")
    d.text("剪力槽0.30m", x0 + 165, y0 + 995, 16, "TEXT")

    # Joint.
    d.text("2 分段缝", x0 + 480, y0 + 1125, 22, "TEXT")
    d.rect(x0 + 480, y0 + 960, 115, 140, "CYLINDER")
    d.rect(x0 + 610, y0 + 960, 115, 140, "CYLINDER")
    diag_hatch(d, x0 + 480, y0 + 960, 115, 140, 12)
    diag_hatch(d, x0 + 610, y0 + 960, 115, 140, 12)
    d.rect(x0 + 595, y0 + 960, 15, 140, "CUT")
    d.text("20mm沥青麻絮", x0 + 535, y0 + 1112, 16, "TEXT")

    # Filter and bedding.
    d.text("3 倒滤层/基床", x0, y0 + 850, 22, "TEXT")
    d.rect(x0, y0 + 650, 310, 65, "FOUNDATION")
    diag_hatch(d, x0, y0 + 650, 310, 65, 12)
    dots(d, x0 + 335, y0 + 650, 125, 205, 20, 18, 1.7)
    d.text("10~100kg块石基床", x0 + 35, y0 + 620, 16, "TEXT")
    d.text("倒滤层+土工布", x0 + 318, y0 + 870, 16, "TEXT")

    # Fender.
    d.text("4 护舷锚固", x0 + 560, y0 + 850, 22, "TEXT")
    d.rect(x0 + 630, y0 + 655, 34, 185, "STRUCTURE")
    d.rect(x0 + 558, y0 + 715, 72, 62, "EQUIPMENT")
    d.circle(x0 + 648, y0 + 728, 5, "EQUIPMENT")
    d.circle(x0 + 648, y0 + 762, 5, "EQUIPMENT")
    d.text("鼓型橡胶护舷", x0 + 692, y0 + 765, 16, "TEXT")
    d.text("预埋锚栓", x0 + 692, y0 + 728, 16, "TEXT")

    # Rebar ring plan.
    d.text("5 圆筒壁配筋", x0, y0 + 520, 22, "TEXT")
    cx, cy = x0 + 150, y0 + 310
    d.circle(cx, cy, 138, "CYLINDER")
    d.circle(cx, cy, 122, "CYLINDER")
    for a in range(0, 360, 15):
        r1, r2 = 122, 138
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        d.line(cx + r1 * ca, cy + r1 * sa, cx + r2 * ca, cy + r2 * sa, "STRUCTURE")
    for r in [126, 132]:
        d.circle(cx, cy, r, "STRUCTURE")
    d.text("环向筋 HRB400 C18@150", x0 + 330, y0 + 410, 16, "TEXT")
    d.text("竖向筋 HRB400 C20@150", x0 + 330, y0 + 375, 16, "TEXT")
    d.text("壁厚0.35m，保护层50mm", x0 + 330, y0 + 340, 16, "TEXT")

    # Chest wall rebar.
    d.text("6 胸墙配筋", x0 + 560, y0 + 520, 22, "TEXT")
    d.rect(x0 + 560, y0 + 220, 300, 145, "STRUCTURE")
    diag_hatch(d, x0 + 560, y0 + 220, 300, 145, 12)
    for xx in range(20, 290, 24):
        d.line(x0 + 560 + xx, y0 + 235, x0 + 560 + xx, y0 + 350, "STRUCTURE")
    for yy in [25, 55, 85, 115]:
        d.line(x0 + 575, y0 + 220 + yy, x0 + 845, y0 + 220 + yy, "STRUCTURE")
    d.text("主筋 HRB400 C20@150", x0 + 560, y0 + 185, 16, "TEXT")
    d.text("箍筋 HRB400 C12@200", x0 + 560, y0 + 150, 16, "TEXT")


def draw_large_cylinder_combined(acad):
    d = acad.new_drawing(dimtxt=22, precision=0)
    setup_layers(d)
    draw_cylinder_section_core(d, 600, 45)
    draw_cylinder_details_and_rebar(d, 2500, 360)
    d.table(
        2500,
        265,
        [110, 175],
        42,
        [
            ["大圆筒方案参数", "取值"],
            ["码头长度/分段", "300m / 10段"],
            ["圆筒布置", "20个，2个/分段，中心距15.0m"],
            ["圆筒尺寸", "外径12.0m，壁厚0.35m，高15.5m"],
            ["标高控制", "筒顶+4.00m，筒底-11.50m"],
            ["基础", "10~100kg块石基床，厚2.0m"],
            ["附属设施", "胸墙、电缆槽、护舷、系船柱"],
        ],
        16,
    )
    d.table(
        2500,
        -80,
        [110, 175],
        38,
        [
            ["施工安装要求", "控制内容"],
            ["预制吊运", "控制吊点、裂缝、外观质量"],
            ["圆筒坐床", "复核中心线、标高和垂直度"],
            ["筒内回填", "分层回填，避免偏压"],
            ["胸墙浇筑", "分段缝20mm，剪力槽嵌固"],
        ],
        15,
    )
    d.text("说明：按方案比选数据绘制，圆筒外径12.0m、壁厚0.35m、高15.5m；每30m分段设2个圆筒。", 80, -420, 20, "TEXT")
    d.text("单位：cm；配筋为代表构件示意，最终直径与间距应按内力计算复核。", 80, -465, 20, "TEXT")
    enforce_min_text_height(d, 16)
    draw_a1_sheet(d, "大圆筒结构断面、细部构造及代表配筋图", "C-02", "1:100/1:50", 0, -900, 4550)
    try:
        com_call(d.doc.Application.ZoomExtents)
    except Exception:
        pass
    path = os.path.join(OUT_DIR, "C-02_large_cylinder_section_detail_rebar.dwg")
    count = d.save(path)
    d.close()
    return path, count


def draw_large_cylinder_plan(acad):
    d = acad.new_drawing(dimtxt=1.8, precision=2)
    setup_layers(d)
    length = 300.0
    diameter = 12.0
    wall = 0.35
    center_y = 6.25
    d.text("平面图", -8, 33, 2.2, "TEXT")
    d.rect(0, 0, length, 12.5, "STRUCTURE")
    d.text("现浇C40胸墙平面范围 B=12.50m", 90, 13.6, 1.5, "TEXT")
    d.line(0, 0, length, 0, "STRUCTURE")
    d.text("码头前沿线", 114, -3.5, 1.5, "TEXT")
    for i in range(20):
        cx = 7.5 + 15.0 * i
        d.circle(cx, center_y, diameter / 2, "CYLINDER")
        d.circle(cx, center_y, diameter / 2 - wall, "CYLINDER")
        d.line(cx, 0.25, cx, 12.25, "CENTER", "CENTER")
        d.text(f"Y{i+1:02d}", cx - 1.3, center_y - 0.45, 0.9, "TEXT")
        if i % 2 == 0:
            d.circle(cx + 7.5, 3.0, 0.75, "EQUIPMENT")
            d.text("B", cx + 7.25, 4.1, 0.8, "TEXT")
        for fx in [cx - 3.75, cx + 3.75]:
            d.rect(fx - 0.35, -1.2, 0.7, 1.2, "EQUIPMENT")
    for x in range(0, 301, 30):
        d.line(x, -4.5, x, 18.5, "CUT", "DASHED")
        d.text(f"K0+{x:03d}", x + 0.6, -6.3, 1.0, "TEXT")
    d.line(0, 14.2, 300, 14.2, "BACKFILL")
    d.text("后方倒滤层及回填区", 112, 15.5, 1.3, "TEXT")
    d.text("分段缝20mm，段间独立变形", 182, 18.6, 1.1, "TEXT")
    d.text("护舷沿前沿布置，系船柱每分段1个", 96, -2.0, 1.1, "TEXT")
    dim_h(d, 0, 300, 0, -12, "300.00m")
    dim_h(d, 0, 30, 0, -8, "30.00m")
    dim_h(d, 0, 15, 18, 22, "15.00m")
    dim_v(d, 300, 0, 12.5, 315, "12.50m")
    d.dim_diameter((7.5 + diameter / 2, center_y, 0), (7.5 - diameter / 2, center_y, 0), 2.0, "%%c12.00m")

    # Elevation view below the plan, so this sheet satisfies the plan/elevation requirement.
    elev_y = -44
    d.text("立面图", 0, elev_y + 22, 2.2, "TEXT")
    d.rect(0, elev_y, 300, 15.5, "CYLINDER")
    for x in range(0, 301, 15):
        d.line(x, elev_y, x, elev_y + 15.5, "CENTER", "CENTER")
    for x in range(0, 301, 30):
        d.line(x, elev_y, x, elev_y + 17.0, "CUT", "DASHED")
    d.rect(0, elev_y + 15.5, 300, 1.5, "STRUCTURE")
    d.rect(0, elev_y - 2.0, 300, 2.0, "FOUNDATION")
    clipped_hatch_m(d, 0, elev_y - 2.0, 300, 2.0, 0.55)
    for x in range(7, 300, 15):
        d.line(x - 3, elev_y + 1.0, x + 3, elev_y + 1.0, "CENTER")
        d.line(x, elev_y + 1.0, x, elev_y + 14.5, "CENTER")
    level(d, -34, -8, elev_y + 17.0, "+5.50", 1.15)
    level(d, -34, -8, elev_y + 15.5, "+4.00", 1.15)
    level(d, -34, -8, elev_y, "-11.50", 1.15)
    level(d, -34, -8, elev_y - 2.0, "-13.00", 1.15)
    dim_v(d, 305, elev_y, elev_y + 15.5, 320, "15.50m")
    dim_h(d, 0, 300, elev_y, elev_y - 7, "300.00m")

    d.table(
        0,
        -72,
        [36, 54, 72],
        5,
        [
            ["项目", "设计值", "说明"],
            ["码头长度", "300m", "10个分段"],
            ["大圆筒", "20个", "2个/分段"],
            ["圆筒外径", "12.0m", "中心距15.0m"],
            ["壁厚/高度", "0.35m/15.5m", "C45预制"],
            ["附属设施", "护舷2组/段，系船柱1个/段", "与胸墙锚固"],
        ],
        1.15,
    )
    enforce_min_text_height(d, 1.25)
    draw_a1_sheet(d, "大圆筒结构平面及立面图", "C-01", "1:500", -58, -188, 425)
    try:
        com_call(d.doc.Application.ZoomExtents)
    except Exception:
        pass
    path = os.path.join(OUT_DIR, "C-01_large_cylinder_plan.dwg")
    count = d.save(path)
    d.close()
    return path, count


def process_box(d, x, y, w, h, title, subtitle=None, layer="STRUCTURE"):
    d.rect(x, y, w, h, layer)
    d.text(title, x + w * 0.08, y + h * 0.58, h * 0.22, "TEXT")
    if subtitle:
        d.text(subtitle, x + w * 0.08, y + h * 0.25, h * 0.16, "TEXT")


def draw_handling_process_sheet(acad):
    d = acad.new_drawing(dimtxt=3.0, precision=1)
    setup_layers(d)
    d.text("装卸工艺流程与设备配置图", 0, 150, 6.0, "TEXT")
    lanes = [
        ("船舶/水域", 120),
        ("码头前沿", 90),
        ("水平运输", 60),
        ("堆场作业", 30),
        ("集疏运出口", 0),
    ]
    for label, y in lanes:
        d.line(-10, y - 6, 280, y - 6, "CENTER", "DASHED")
        d.text(label, -38, y + 1, 3.3, "TEXT")

    process_box(d, 0, 112, 45, 18, "集装箱船", "3万吨级", "WATER")
    process_box(d, 58, 112, 45, 18, "岸桥QC", "4台", "EQUIPMENT")
    process_box(d, 116, 112, 50, 18, "拆装锁站", "前沿作业带", "STRUCTURE")
    process_box(d, 178, 112, 56, 18, "集卡/AGV", "水平运输", "ROAD")
    process_box(d, 0, 48, 50, 20, "重箱堆场", "RMG作业", "CENTER")
    process_box(d, 62, 48, 50, 20, "空箱堆场", "空箱堆高", "CENTER")
    process_box(d, 124, 48, 50, 20, "冷藏/危品", "专用箱区", "CENTER")
    process_box(d, 188, 48, 58, 20, "查验区", "海关/检疫", "STRUCTURE")
    process_box(d, 0, -8, 62, 20, "公路闸口", "6车道+缓冲", "ROAD")
    process_box(d, 82, -8, 70, 20, "铁路装卸线", "到发线+装卸线", "RAIL")
    process_box(d, 172, -8, 62, 20, "生产辅助区", "机修/备件/管理", "STRUCTURE")

    for x1, y1, x2, y2 in [
        (45, 121, 58, 121),
        (103, 121, 116, 121),
        (166, 121, 178, 121),
        (206, 112, 25, 68),
        (206, 112, 87, 68),
        (206, 112, 149, 68),
        (206, 112, 217, 68),
        (25, 48, 32, 12),
        (87, 48, 117, 12),
        (149, 48, 117, 12),
        (217, 48, 117, 12),
    ]:
        d.arrow(x1, y1, x2, y2, "PROCESS", 3.2)

    d.text("进口流向", 238, 104, 3.0, "TEXT")
    d.arrow(238, 101, 260, 101, "PROCESS", 4)
    d.text("出口流向反向组织，空重箱分区调度", 0, 23, 3.0, "TEXT")
    d.text("公铁分流：公路闸口与铁路装卸区在堆场后方分区布置，减少交叉干扰。", 0, -26, 3.0, "TEXT")

    d.table(
        0,
        -45,
        [45, 48, 92],
        8,
        [
            ["设备/设施", "数量或规模", "布置说明"],
            ["岸桥QC", "4台", "沿300m泊位前沿布置"],
            ["RMG/场桥", "重箱、空箱及铁路换装区配置", "服务垂直岸线箱区"],
            ["集卡/AGV车道", "主干道25m，次干道15m", "环形组织，避免前沿拥堵"],
            ["闸口", "6车道", "后方布置并设缓冲停车区"],
            ["铁路", "到发线1条、装卸线1条", "后方独立装卸区"],
        ],
        2.2,
    )
    d.title_block("装卸工艺流程与设备配置图", "P-01", "示意", 0, -120, 205, 24, 2.8)
    try:
        com_call(d.doc.Application.ZoomExtents)
    except Exception:
        pass
    path = os.path.join(OUT_DIR, "P-01_handling_process_equipment.dwg")
    count = d.save(path)
    d.close()
    return path, count


def draw_quantity_schedule_sheet(acad):
    d = acad.new_drawing(dimtxt=3.2, precision=2)
    setup_layers(d)
    d.text("主要工程量与设计检查表", 0, 190, 6.0, "TEXT")

    caisson_count = 10
    cyl_count = 20
    cyl_d = 12.0
    cyl_t = 0.35
    cyl_h = 15.5
    cyl_inner = cyl_d - 2 * cyl_t
    cyl_shell = math.pi / 4 * (cyl_d * cyl_d - cyl_inner * cyl_inner) * cyl_h
    cyl_shell_total = cyl_shell * cyl_count
    bed_volume = 300.0 * 16.0 * 2.0
    chest_volume = 300.0 * 12.5 * 1.5
    caisson_bed_volume = 300.0 * 16.0 * 2.0
    caisson_chest_volume = 300.0 * 12.5 * 2.0

    d.table(
        0,
        170,
        [58, 58, 58, 90],
        10,
        [
            ["沉箱方案", "数量/尺寸", "材料", "说明"],
            ["沉箱", "10座；29.95x12.50x13.50m", "C45预制", "3列舱格，外墙0.35m，内隔墙0.20m"],
            ["胸墙", f"约{caisson_chest_volume:.0f}m3", "C40现浇", "高2.0m，宽12.5m"],
            ["基床", f"约{caisson_bed_volume:.0f}m3", "10~100kg块石", "厚2.0m，底宽16.0m"],
            ["护舷/系船柱", "20组/10个", "橡胶/铸钢", "护舷2组/箱，1500kN系船柱1个/段"],
            ["倒滤层", "通长布置", "二片石+碎石+土工布", "接缝处加厚至0.8m"],
        ],
        2.5,
    )
    d.table(
        0,
        96,
        [58, 58, 58, 90],
        10,
        [
            ["大圆筒方案", "数量/尺寸", "材料", "说明"],
            ["大圆筒", f"20个；单个壳体约{cyl_shell:.0f}m3", "C45预制", f"壳体混凝土合计约{cyl_shell_total:.0f}m3"],
            ["胸墙", f"约{chest_volume:.0f}m3", "C40现浇", "高1.5m，宽12.5m"],
            ["基床", f"约{bed_volume:.0f}m3", "10~100kg块石", "厚2.0m，底宽16.0m"],
            ["护舷/系船柱", "20组/10个", "橡胶/铸钢", "护舷2组/段，系船柱1个/段"],
            ["倒滤层", "通长布置", "二片石+碎石+土工布", "圆筒接缝处重点加厚"],
        ],
        2.5,
    )
    d.table(
        0,
        22,
        [70, 88, 106],
        9,
        [
            ["自检项目", "检查结果", "后续注意"],
            ["结构类型", "沉箱图与大圆筒图已分开表达", "方案比选时分别引用"],
            ["图纸组织", "沉箱断面/细部/配筋合并；大圆筒同样合并", "符合本次修改意见"],
            ["总平面", "铁路装卸区与港内道路分区标注", "后续可结合真实港区再细化"],
            ["文字乱码", "采用CN-SIMSUN样式，截图未见紫色乱码", "异机打开需确认字体"],
            ["标注拥挤", "主图与表格分区，标题栏下移", "打印前建议A1或A2幅面检查"],
            ["造价", "本表只列工程量，不列造价", "按老师要求暂不写造价"],
        ],
        2.3,
    )
    d.text("注：本表为毕业设计阶段工程量估算和图纸自检清单，用于提高工作量表达；正式造价需另按定额和单价计算。", 0, -48, 3.0, "NOTE")
    d.title_block("主要工程量与设计检查表", "Q-01", "表格", 0, -90, 230, 24, 2.8)
    try:
        com_call(d.doc.Application.ZoomExtents)
    except Exception:
        pass
    path = os.path.join(OUT_DIR, "Q-01_quantity_and_check_schedule.dwg")
    count = d.save(path)
    d.close()
    return path, count


def make_zip(paths):
    zip_path = os.path.join(OUT_DIR, "revision_2026_05_19_five_drawings_plus.zip")
    if os.path.exists(zip_path):
        os.remove(zip_path)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in paths:
            zf.write(path, arcname=os.path.basename(path))
    return zip_path


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    outputs = []
    for func in [
        draw_general_layout_revised,
        draw_caisson_plan_elevation_revised,
        draw_caisson_combined,
        draw_large_cylinder_plan,
        draw_large_cylinder_combined,
    ]:
        acad = AcadSession()
        path, count = func(acad)
        outputs.append((path, count))
        time.sleep(0.5)
    zip_path = make_zip([p for p, _ in outputs])
    print("DONE")
    for path, count in outputs:
        print(f"{path} | ModelSpace entities: {count}")
    print(f"ZIP: {zip_path}")


if __name__ == "__main__":
    main()
