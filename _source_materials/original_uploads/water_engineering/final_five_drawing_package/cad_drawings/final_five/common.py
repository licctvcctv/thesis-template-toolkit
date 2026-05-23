import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cad_core.drawing_utils import (  # noqa: E402
    add_circle,
    add_dim_aligned,
    add_dim_rotated,
    add_line,
    add_polyline,
    add_rect,
    add_text,
    retry_com,
)
from cad_core.layers import setup_layers  # noqa: E402
from data import ADVISOR, DESIGN_STAGE, DESIGNER, PROJECT_NAME  # noqa: E402


def m(value):
    return float(value) * 1000.0


def line(ms, p1, p2, layer="1_MAIN"):
    return add_line(ms, p1, p2, layer=layer)


def poly(ms, points, layer="1_MAIN", closed=False):
    return add_polyline(ms, points, layer=layer, closed=closed)


def rect(ms, x, y, w, h, layer="1_MAIN", hatch=None, hatch_scale=1.0):
    return add_rect(ms, (x, y), (x + w, y + h), layer=layer, fill_hatch=hatch, hatch_scale=hatch_scale)


def circle(ms, x, y, r, layer="1_MAIN"):
    return add_circle(ms, (x, y), r, layer=layer)


def text(ms, value, x, y, h, layer="6_TEXT", align=None, rotation=0.0):
    return add_text(ms, value, (x, y), h, layer=layer, alignment=align, rotation=rotation)


def ctext(ms, value, x, y, h, layer="6_TEXT"):
    return text(ms, value, x, y, h, layer=layer, align=1)


def wrap(value, max_chars):
    value = str(value)
    rows = []
    buf = ""
    for char in value:
        buf += char
        if len(buf) >= max_chars or char in "。；;":
            rows.append(buf.strip())
            buf = ""
    if buf.strip():
        rows.append(buf.strip())
    return rows or [""]


def multiline(ms, rows, x, y, h, leading=None, layer="6_TEXT", max_chars=None):
    if isinstance(rows, str):
        rows = [rows]
    expanded = []
    for item in rows:
        expanded.extend(wrap(item, max_chars) if max_chars else [item])
    leading = leading or h * 1.5
    for idx, row in enumerate(expanded):
        text(ms, row, x, y - idx * leading, h, layer=layer)
    return len(expanded)


def table(ms, x, y_top, col_widths, rows, h, row_h=None, title=None):
    row_h = row_h or h * 3.0
    if title:
        ctext(ms, title, x + sum(col_widths) / 2, y_top + h * 2.0, h * 1.15)
    y = y_top
    for r_idx, row in enumerate(rows):
        wrapped = []
        max_lines = 1
        for c_idx, cell in enumerate(row):
            max_chars = max(4, int(col_widths[c_idx] / max(h * 0.74, 1)))
            rows2 = wrap(cell, max_chars)
            wrapped.append(rows2)
            max_lines = max(max_lines, len(rows2))
        rh = max(row_h, h * (1.5 + 1.25 * max_lines))
        x0 = x
        for c_idx, rows2 in enumerate(wrapped):
            rect(ms, x0, y - rh, col_widths[c_idx], rh, layer="0_FRAME")
            if r_idx == 0:
                ctext(ms, " / ".join(rows2), x0 + col_widths[c_idx] / 2, y - rh / 2 - h * 0.30, h)
            else:
                multiline(ms, rows2, x0 + h * 0.65, y - h * 1.25, h * 0.88, leading=h * 1.15)
            x0 += col_widths[c_idx]
        y -= rh
    return y


def set_doc_vars(doc, scale):
    values = {
        "INSUNITS": 4,
        "LUNITS": 2,
        "LUPREC": 0,
        "DIMSCALE": scale,
        "DIMTXT": 2.6 * scale,
        "DIMASZ": 2.0 * scale,
        "DIMEXE": 0.8 * scale,
        "DIMEXO": 0.8 * scale,
    }
    for name, val in values.items():
        try:
            doc.SetVariable(name, val)
        except Exception:
            pass


def dim_h(ms, x1, x2, y, offset, layer="5_DIM"):
    return add_dim_rotated(ms, (x1, y), (x2, y), ((x1 + x2) / 2, y + offset), 0.0, layer=layer)


def dim_v(ms, x, y1, y2, offset, layer="5_DIM"):
    return add_dim_rotated(ms, (x, y1), (x, y2), (x + offset, (y1 + y2) / 2), math.pi / 2, layer=layer)


def dim_a(ms, p1, p2, p_dim, layer="5_DIM"):
    return add_dim_aligned(ms, p1, p2, p_dim, layer=layer)


def arrow(ms, p1, p2, size, layer="5_DIM"):
    line(ms, p1, p2, layer=layer)
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = math.hypot(dx, dy)
    if length <= 1:
        return
    ux, uy = dx / length, dy / length
    nx, ny = -uy, ux
    back = (p2[0] - ux * size, p2[1] - uy * size)
    line(ms, p2, (back[0] + nx * size * 0.45, back[1] + ny * size * 0.45), layer=layer)
    line(ms, p2, (back[0] - nx * size * 0.45, back[1] - ny * size * 0.45), layer=layer)


def create_sheet(doc, scale, title, sheet_no, plotted_scale=None):
    setup_layers(doc)
    set_doc_vars(doc, scale)
    ms = retry_com("ModelSpace", lambda: doc.ModelSpace, attempts=80, delay=0.2)

    w = 841.0 * scale
    h = 594.0 * scale
    x_min = 25.0 * scale
    y_min = 10.0 * scale
    x_max = 831.0 * scale
    y_max = 584.0 * scale

    rect(ms, 0, 0, w, h, layer="0_FRAME")
    rect(ms, x_min, y_min, x_max - x_min, y_max - y_min, layer="0_FRAME")

    tb_w = 205.0 * scale
    tb_h = 48.0 * scale
    tb_x = x_max - tb_w
    tb_y = y_min
    rect(ms, tb_x, tb_y, tb_w, tb_h, layer="0_FRAME")
    for i in range(1, 6):
        line(ms, (tb_x, tb_y + i * 8.0 * scale), (tb_x + tb_w, tb_y + i * 8.0 * scale), layer="0_FRAME")
    for xoff in (25.0, 123.0, 157.0):
        line(ms, (tb_x + xoff * scale, tb_y), (tb_x + xoff * scale, tb_y + tb_h), layer="0_FRAME")

    title_rows = [
        ("项目", PROJECT_NAME, "编号", sheet_no),
        ("图名", title, "比例", plotted_scale or f"1:{scale}"),
        ("阶段", DESIGN_STAGE, "日期", "2026.05"),
        ("设计", DESIGNER, "指导", ADVISOR),
        ("图幅", "A1 横向", "单位", "mm/m"),
        ("说明", "按任务书及现行港工规范绘制", "版本", "五图重绘"),
    ]
    for idx, row in enumerate(title_rows):
        yy = tb_y + (5 - idx) * 8.0 * scale + 2.1 * scale
        text(ms, row[0], tb_x + 2.0 * scale, yy, 2.0 * scale)
        text(ms, row[1], tb_x + 27.0 * scale, yy, 2.15 * scale)
        text(ms, row[2], tb_x + 126.0 * scale, yy, 2.0 * scale)
        text(ms, row[3], tb_x + 160.0 * scale, yy, 2.15 * scale)

    ctext(ms, title, (x_min + x_max) / 2, y_min + 24.0 * scale, 4.4 * scale)
    line(ms, (x_min + 210.0 * scale, y_min + 20.0 * scale), (x_max - 210.0 * scale, y_min + 20.0 * scale), layer="0_FRAME")

    nx = x_max - 30.0 * scale
    ny = y_max - 42.0 * scale
    arrow(ms, (nx, ny - 16.0 * scale), (nx, ny + 16.0 * scale), 3.5 * scale, layer="5_DIM")
    ctext(ms, "N", nx, ny + 20.0 * scale, 3.2 * scale)

    return {
        "ms": ms,
        "scale": scale,
        "x_min": x_min,
        "x_max": x_max,
        "y_min": y_min,
        "y_max": y_max,
        "title_block": (tb_x, tb_y, tb_w, tb_h),
        "note_x": x_min + 8.0 * scale,
        "note_y": y_min + 82.0 * scale,
    }


def notes(ms, canvas, rows, title="设计说明"):
    s = canvas["scale"]
    x = canvas["note_x"]
    y = canvas["note_y"]
    text(ms, f"{title}：", x, y, 2.8 * s)
    note_rows = [f"{idx + 1}. {row}" for idx, row in enumerate(rows)]
    multiline(ms, note_rows, x, y - 7.0 * s, 2.1 * s, leading=6.0 * s, max_chars=54)


def draw_ship(ms, x, y, length, beam, layer="2_SECONDARY"):
    bow = length * 0.12
    stern = length * 0.10
    pts = [
        (x, y + beam / 2),
        (x + bow, y + beam),
        (x + length - stern, y + beam),
        (x + length, y + beam * 0.74),
        (x + length, y + beam * 0.26),
        (x + length - stern, y),
        (x + bow, y),
    ]
    poly(ms, pts, layer=layer, closed=True)
    hatch_w = length * 0.085
    gap = length * 0.035
    hx = x + bow + gap
    for _ in range(5):
        rect(ms, hx, y + beam * 0.22, hatch_w, beam * 0.56, layer=layer)
        line(ms, (hx, y + beam * 0.22), (hx + hatch_w, y + beam * 0.78), layer=layer)
        line(ms, (hx, y + beam * 0.78), (hx + hatch_w, y + beam * 0.22), layer=layer)
        hx += hatch_w + gap


def waterline(ms, x1, x2, datum_y, level_m, label, scale, layer="3_WATER_LEVEL"):
    y = datum_y + m(level_m)
    line(ms, (x1, y), (x2, y), layer=layer)
    text(ms, label, x1 + 1.0 * scale, y + 1.0 * scale, 1.5 * scale)


def soil_profile(ms, x, y_top, width, layers, vscale=1.0, text_h=800):
    y = y_top
    hatches = ["ANSI31", "ANSI32", "ANSI37", "DOLMIT", "GRAVEL", "ANSI38"]
    for idx, (name, thick_m, desc) in enumerate(layers):
        h = m(thick_m) * vscale
        rect(ms, x, y - h, width, h, layer="4_HATCH", hatch=hatches[idx % len(hatches)], hatch_scale=18.0)
        text(ms, name, x + text_h * 1.2, y - h / 2 + text_h * 0.5, text_h)
        text(ms, desc, x + width * 0.52, y - h / 2 + text_h * 0.5, text_h * 0.78)
        y -= h
    return y


def section_title(ms, label, x, y, h):
    ctext(ms, label, x, y, h)
    line(ms, (x - 15 * h, y - 1.0 * h), (x + 15 * h, y - 1.0 * h), layer="0_FRAME")
