import math

from common import (
    arrow,
    circle,
    create_sheet,
    ctext,
    line,
    multiline,
    poly,
    rect,
    table,
    text,
)
from data import GENERAL, HYDRO, NORM_NOTES, SHIP


def _pt(canvas, px, py):
    s = canvas["scale"]
    return canvas["x_min"] + px * s, canvas["y_min"] + py * s


def _h(canvas, value_mm):
    return value_mm * canvas["scale"]


def _line(ms, canvas, p1, p2, layer="1_MAIN"):
    return line(ms, _pt(canvas, *p1), _pt(canvas, *p2), layer=layer)


def _poly(ms, canvas, points, layer="1_MAIN", closed=False):
    return poly(ms, [_pt(canvas, *p) for p in points], layer=layer, closed=closed)


def _rect(ms, canvas, px, py, w, h, layer="1_MAIN"):
    x, y = _pt(canvas, px, py)
    return rect(ms, x, y, _h(canvas, w), _h(canvas, h), layer=layer)


def _circle(ms, canvas, px, py, r, layer="1_MAIN"):
    x, y = _pt(canvas, px, py)
    return circle(ms, x, y, _h(canvas, r), layer=layer)


def _text(ms, canvas, value, px, py, h=2.2, layer="6_TEXT", align=None, rotation=0.0):
    x, y = _pt(canvas, px, py)
    return text(ms, value, x, y, _h(canvas, h), layer=layer, align=align, rotation=rotation)


def _ctext(ms, canvas, value, px, py, h=2.2, layer="6_TEXT"):
    x, y = _pt(canvas, px, py)
    return ctext(ms, value, x, y, _h(canvas, h), layer=layer)


def _multiline(ms, canvas, rows, px, py, h=2.0, leading=5.4, layer="6_TEXT", max_chars=34):
    x, y = _pt(canvas, px, py)
    return multiline(
        ms,
        rows,
        x,
        y,
        _h(canvas, h),
        leading=_h(canvas, leading),
        layer=layer,
        max_chars=max_chars,
    )


def _water_waves(ms, canvas, x1, x2, y_values):
    for idx, y in enumerate(y_values):
        pts = []
        step = 18.0
        x = x1
        phase = idx * 0.9
        while x <= x2:
            pts.append((x, y + math.sin((x - x1) / step * math.pi + phase) * 1.2))
            x += step / 2.0
        _poly(ms, canvas, pts, layer="3_WATER")


def _shore_ticks(ms, canvas, x1, x2, y):
    x = x1 + 7.0
    while x < x2:
        _line(ms, canvas, (x, y), (x - 4.5, y - 6.0), layer="4_HATCH")
        x += 18.0


def _double_arrow_h(ms, canvas, x1, x2, y, label, text_above=True):
    s = canvas["scale"]
    p1 = _pt(canvas, x1, y)
    p2 = _pt(canvas, x2, y)
    line(ms, p1, p2, layer="5_DIM")
    arrow(ms, _pt(canvas, x1 + 10, y), p1, _h(canvas, 2.2), layer="5_DIM")
    arrow(ms, _pt(canvas, x2 - 10, y), p2, _h(canvas, 2.2), layer="5_DIM")
    offset = 3.0 if text_above else -5.0
    ctext(ms, label, (p1[0] + p2[0]) / 2, p1[1] + offset * s, _h(canvas, 2.1), layer="6_TEXT")


def _double_arrow_v(ms, canvas, x, y1, y2, label):
    s = canvas["scale"]
    p1 = _pt(canvas, x, y1)
    p2 = _pt(canvas, x, y2)
    line(ms, p1, p2, layer="5_DIM")
    arrow(ms, _pt(canvas, x, y1 + 8), p1, _h(canvas, 2.2), layer="5_DIM")
    arrow(ms, _pt(canvas, x, y2 - 8), p2, _h(canvas, 2.2), layer="5_DIM")
    text(ms, label, p1[0] + 3.0 * s, (p1[1] + p2[1]) / 2 - 12.0 * s, _h(canvas, 2.0), rotation=math.pi / 2)


def _draw_building(ms, canvas, px, py, w, h, label):
    _rect(ms, canvas, px, py, w, h, layer="2_SECONDARY")
    _line(ms, canvas, (px, py), (px + w, py + h), layer="4_HATCH")
    _line(ms, canvas, (px, py + h), (px + w, py), layer="4_HATCH")
    _ctext(ms, canvas, label, px + w / 2, py + h / 2 - 1.0, h=1.85)


def _draw_road(ms, canvas, points, width=7.0):
    for p1, p2 in zip(points, points[1:]):
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = math.hypot(dx, dy)
        if length < 1:
            continue
        nx = -dy / length * width / 2
        ny = dx / length * width / 2
        _line(ms, canvas, (p1[0] + nx, p1[1] + ny), (p2[0] + nx, p2[1] + ny), layer="2_SECONDARY")
        _line(ms, canvas, (p1[0] - nx, p1[1] - ny), (p2[0] - nx, p2[1] - ny), layer="2_SECONDARY")
        _line(ms, canvas, p1, p2, layer="3_CENTERLINE")


def _draw_belt(ms, canvas, points, label=None):
    for p1, p2 in zip(points, points[1:]):
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = math.hypot(dx, dy)
        if length < 1:
            continue
        nx = -dy / length * 1.2
        ny = dx / length * 1.2
        _line(ms, canvas, (p1[0] + nx, p1[1] + ny), (p2[0] + nx, p2[1] + ny), layer="1_MAIN")
        _line(ms, canvas, (p1[0] - nx, p1[1] - ny), (p2[0] - nx, p2[1] - ny), layer="1_MAIN")
        _line(ms, canvas, p1, p2, layer="5_DIM")
    if label:
        _text(ms, canvas, label, points[-1][0] + 5, points[-1][1] + 1.5, h=2.0)


def _draw_transfer(ms, canvas, px, py, label):
    _rect(ms, canvas, px - 5.0, py - 5.0, 10.0, 10.0, layer="1_MAIN")
    _ctext(ms, canvas, label, px, py - 1.2, h=2.0)


def _draw_tag(ms, canvas, px, py, code, label, layer="6_TEXT"):
    _rect(ms, canvas, px, py - 4.0, 12.0, 8.0, layer="0_FRAME")
    _ctext(ms, canvas, code, px + 6.0, py - 1.2, h=1.65, layer=layer)
    _text(ms, canvas, label, px + 15.0, py - 2.1, h=1.65, layer=layer)


def _draw_coal_bay(ms, canvas, px, py, w, h, label):
    _rect(ms, canvas, px, py, w, h, layer="1_MAIN")
    ridge_y = py + h * 0.58
    _poly(
        ms,
        canvas,
        [
            (px + 3.0, py + 5.0),
            (px + w * 0.50, ridge_y + 5.0),
            (px + w - 3.0, py + 5.0),
            (px + w - 3.0, py + h - 5.0),
            (px + 3.0, py + h - 5.0),
        ],
        layer="4_HATCH",
        closed=True,
    )
    x = px + 8.0
    while x < px + w - 5.0:
        _line(ms, canvas, (x, py + 7.0), (x + 12.0, py + h - 7.0), layer="4_HATCH")
        x += 11.0
    _ctext(ms, canvas, label, px + w / 2, py + h / 2 - 1.0, h=1.8)


def _draw_scale_bar(ms, canvas, px, py):
    seg = 50.0
    _text(ms, canvas, "比例尺", px, py + 8, h=2.0)
    for idx in range(4):
        _rect(ms, canvas, px + 22 + idx * seg, py, seg, 5.0, layer="0_FRAME")
        if idx % 2 == 0:
            _line(ms, canvas, (px + 22 + idx * seg, py), (px + 22 + (idx + 1) * seg, py + 5.0), layer="4_HATCH")
            _line(ms, canvas, (px + 22 + idx * seg, py + 5.0), (px + 22 + (idx + 1) * seg, py), layer="4_HATCH")
    for idx, label in enumerate(["0", "75", "150", "225", "300m"]):
        _text(ms, canvas, label, px + 19 + idx * seg, py - 6.0, h=1.8)


def _draw_legend(ms, canvas, px, py):
    _rect(ms, canvas, px, py - 54, 154, 54, layer="0_FRAME")
    _ctext(ms, canvas, "图例", px + 77, py - 7, h=2.4)
    y = py - 17
    _line(ms, canvas, (px + 10, y), (px + 38, y), layer="1_MAIN")
    _text(ms, canvas, "码头、皮带机、主要构筑物", px + 44, y - 2, h=1.9)
    y -= 10
    _line(ms, canvas, (px + 10, y), (px + 38, y), layer="3_WATER")
    _text(ms, canvas, "水域边界、航道与港池控制线", px + 44, y - 2, h=1.9)
    y -= 10
    _line(ms, canvas, (px + 10, y + 2), (px + 38, y + 2), layer="2_SECONDARY")
    _line(ms, canvas, (px + 10, y - 2), (px + 38, y - 2), layer="2_SECONDARY")
    _text(ms, canvas, "陆域道路", px + 44, y - 2, h=1.9)
    y -= 10
    _rect(ms, canvas, px + 10, y - 3, 28, 6, layer="2_SECONDARY")
    _text(ms, canvas, "后方建筑、辅助生产区", px + 44, y - 2, h=1.9)


def _draw_key_table(ms, canvas):
    s = canvas["scale"]
    x, y = _pt(canvas, 54, 532)
    rows = [
        ["项目", "设计取值"],
        ["设计船型", f"{SHIP['dwt']}散货船 L={SHIP['length_m']:.0f}m B={SHIP['beam_m']:.1f}m"],
        ["泊位", f"煤码头1个泊位，泊位长度{GENERAL['berth_length_m']:.0f}m"],
        ["水域", f"回旋水域D={GENERAL['turning_diameter_m']:.0f}m，航道宽{GENERAL['channel_width_m']:.0f}m"],
        ["标高", f"码头面+{GENERAL['deck_elevation_m']:.2f}m，前沿底高程{HYDRO['front_depth_m']:.2f}m"],
        ["依据", "JTS 165-2025、JTS 167-2018及任务书"],
    ]
    table(ms, x, y, [46 * s, 125 * s], rows, 1.75 * s, row_h=6.4 * s, title="主要设计控制指标")


def _draw_norm_note(ms, canvas):
    _rect(ms, canvas, 54, 440, 258, 36, layer="0_FRAME")
    _text(ms, canvas, "规范依据", 60, 465, h=2.3)
    rows = [
        "总平面尺度按《海港总体设计规范》JTS 165-2025确定，结合5万DWT散货船、设计水位和港池水深布置。",
        "结构图后续分别表达高桩梁板式与重力式沉箱方案，按《码头结构设计规范》JTS 167-2018进行构造控制。",
    ]
    _multiline(ms, canvas, rows, 60, 457, h=1.85, leading=5.1, max_chars=40)


def draw(doc):
    canvas = create_sheet(doc, 1500, "总平面布置图", "G-01", plotted_scale="1:1500")
    ms = canvas["ms"]

    # Clear, readable planning bands: land above, water below, wharf/shoreline between.
    land = (42, 286, 708, 250)
    water = (42, 82, 708, 204)
    shore_y = 286.0
    _rect(ms, canvas, *land, layer="2_SECONDARY")
    _rect(ms, canvas, *water, layer="3_WATER")
    _ctext(ms, canvas, "港池水域", 675, 104, h=5.0, layer="3_WATER")
    _water_waves(ms, canvas, 55, 733, [108, 132, 156, 180, 204, 228, 252])

    # Shoreline and wharf.
    _line(ms, canvas, (42, shore_y), (750, shore_y), layer="0_FRAME")
    _shore_ticks(ms, canvas, 42, 750, shore_y)
    _ctext(ms, canvas, "岸线 / 码头前沿线", 184, shore_y + 8, h=2.4)

    wharf_len = GENERAL["berth_length_m"] * 1000 / canvas["scale"]
    wharf_w = 18_000 / canvas["scale"]
    wharf_x = 324.0
    wharf_y = shore_y
    _rect(ms, canvas, wharf_x, wharf_y, wharf_len, wharf_w, layer="1_MAIN")
    _line(ms, canvas, (wharf_x, wharf_y + 4.0), (wharf_x + wharf_len, wharf_y + 4.0), layer="2_SECONDARY")
    _line(ms, canvas, (wharf_x, wharf_y + 10.0), (wharf_x + wharf_len, wharf_y + 10.0), layer="2_SECONDARY")
    for i in range(9):
        x = wharf_x + 12 + i * (wharf_len - 24) / 8
        _rect(ms, canvas, x - 2, wharf_y - 4.5, 4, 4, layer="1_MAIN")
        _circle(ms, canvas, x, wharf_y + wharf_w + 4, 1.5, layer="2_SECONDARY")
    _ctext(ms, canvas, "装卸泊位 L=260m", wharf_x + wharf_len / 2, wharf_y + wharf_w + 11, h=2.4)
    _text(ms, canvas, "门机轨道", wharf_x + 12, wharf_y + 5.7, h=1.8)
    _double_arrow_h(ms, canvas, wharf_x, wharf_x + wharf_len, wharf_y + wharf_w + 22, "泊位长度 260m")

    # Berthing water, design ship, turning basin and channel.
    berth_x = wharf_x - 15
    berth_y = wharf_y - 48
    berth_w = wharf_len + 30
    berth_h = GENERAL["berthing_water_width_m"] * 1000 / canvas["scale"]
    _rect(ms, canvas, berth_x, berth_y, berth_w, berth_h, layer="3_WATER")
    _ctext(ms, canvas, "靠泊水域 宽40m  底高程-12.50m", berth_x + berth_w / 2, berth_y + berth_h + 6, h=2.2, layer="3_WATER")
    _draw_tag(ms, canvas, berth_x + berth_w + 18, berth_y + 10, "W1", "靠泊水域", layer="3_WATER")

    ship_len = SHIP["length_m"] * 1000 / canvas["scale"]
    ship_beam = SHIP["beam_m"] * 1000 / canvas["scale"]
    ship_x = wharf_x + (wharf_len - ship_len) / 2
    ship_y = berth_y + 7.0
    _draw_ship_like(ms, canvas, ship_x, ship_y, ship_len, ship_beam)
    _ctext(ms, canvas, "5万DWT散货船", ship_x + ship_len / 2, ship_y + ship_beam / 2 - 1, h=2.0)

    basin_cx, basin_cy = 407.0, 170.0
    basin_r = GENERAL["turning_diameter_m"] * 1000 / canvas["scale"] / 2.0
    _circle(ms, canvas, basin_cx, basin_cy, basin_r, layer="3_WATER")
    _line(ms, canvas, (basin_cx - basin_r, basin_cy), (basin_cx + basin_r, basin_cy), layer="3_CENTERLINE")
    _line(ms, canvas, (basin_cx, basin_cy - basin_r), (basin_cx, basin_cy + basin_r), layer="3_CENTERLINE")
    _ctext(ms, canvas, "回旋水域 D=270m", basin_cx, basin_cy + 8, h=2.5, layer="3_WATER")
    _double_arrow_h(ms, canvas, basin_cx - basin_r, basin_cx + basin_r, basin_cy - basin_r - 10, "270m")
    _draw_tag(ms, canvas, basin_cx - basin_r - 8, basin_cy + basin_r - 14, "W2", "回旋水域", layer="3_WATER")

    channel_w = GENERAL["channel_width_m"] * 1000 / canvas["scale"]
    ch_l = basin_cx - channel_w / 2.0
    ch_r = basin_cx + channel_w / 2.0
    _line(ms, canvas, (ch_l, 82), (ch_l, basin_cy), layer="3_WATER")
    _line(ms, canvas, (ch_r, 82), (ch_r, basin_cy), layer="3_WATER")
    _line(ms, canvas, (basin_cx, 82), (basin_cx, basin_cy), layer="3_CENTERLINE")
    _double_arrow_h(ms, canvas, ch_l, ch_r, 100, "航道宽98m", text_above=False)
    arrow(ms, _pt(canvas, basin_cx, 118), _pt(canvas, basin_cx, 88), _h(canvas, 3.5), layer="3_WATER")
    _ctext(ms, canvas, "进港航道", basin_cx + 51, 114, h=2.2, layer="3_WATER")
    _draw_tag(ms, canvas, ch_r + 12, 92, "W3", "进港航道", layer="3_WATER")

    # Land-side road hierarchy.
    _draw_road(ms, canvas, [(54, 330), (735, 330)], width=9.0)
    _draw_road(ms, canvas, [(292, 330), (292, 432), (55, 432)], width=8.0)
    _draw_road(ms, canvas, [(535, 330), (535, 462), (735, 462)], width=8.0)
    _text(ms, canvas, "陆域主干道", 596, 337, h=2.0)
    _text(ms, canvas, "场区道路", 68, 438, h=2.0)
    _draw_tag(ms, canvas, 78, 414, "L1", "辅助建筑层")
    _draw_tag(ms, canvas, 342, 438, "L2", "堆场装卸层")
    _draw_tag(ms, canvas, 562, 352, "L3", "道路排水层")

    # Auxiliary production zone on land, separated from stockyard.
    _rect(ms, canvas, 70, 344, 190, 78, layer="0_FRAME")
    _ctext(ms, canvas, "生产辅助区", 165, 413, h=2.8)
    _draw_building(ms, canvas, 88, 386, 46, 22, "综合楼")
    _draw_building(ms, canvas, 151, 388, 38, 18, "变电所")
    _draw_building(ms, canvas, 205, 387, 34, 18, "维修间")
    _draw_building(ms, canvas, 88, 356, 36, 17, "消防泵房")
    _draw_building(ms, canvas, 143, 356, 42, 17, "备品库")
    _draw_building(ms, canvas, 203, 356, 33, 17, "地磅")
    _rect(ms, canvas, 88, 376, 56, 8, layer="3_WATER")
    _ctext(ms, canvas, "沉淀池", 116, 378.5, h=1.65, layer="3_WATER")
    _text(ms, canvas, "大门", 58, 326, h=2.0)

    # Stockyard and handling system.
    yard_w = GENERAL["stockyard_length_m"] * 1000 / canvas["scale"]
    yard_h = GENERAL["stockyard_width_m"] * 1000 / canvas["scale"]
    yard_x, yard_y = 338.0, 368.0
    _rect(ms, canvas, yard_x - 13, yard_y - 13, yard_w + 26, yard_h + 26, layer="2_SECONDARY")
    _ctext(ms, canvas, "煤炭堆场及斗轮堆取料机作业区", yard_x + yard_w / 2, yard_y + yard_h + 17, h=2.5)
    _rect(ms, canvas, yard_x, yard_y, yard_w, yard_h, layer="1_MAIN")
    bay_gap = 4.0
    bay_w = (yard_w - 5 * bay_gap) / 4.0
    for idx in range(4):
        _draw_coal_bay(ms, canvas, yard_x + bay_gap + idx * (bay_w + bay_gap), yard_y + 7, bay_w, yard_h - 14, f"煤堆{idx + 1}")
    _line(ms, canvas, (yard_x + 7, yard_y + yard_h / 2), (yard_x + yard_w - 7, yard_y + yard_h / 2), layer="2_SECONDARY")
    _text(ms, canvas, "堆取料机轨道", yard_x + 20, yard_y + yard_h / 2 + 4, h=1.9)
    _double_arrow_h(ms, canvas, yard_x, yard_x + yard_w, yard_y - 15, "堆场长度 250m", text_above=False)
    _double_arrow_v(ms, canvas, yard_x + yard_w + 15, yard_y, yard_y + yard_h, "堆场宽100m")

    _draw_transfer(ms, canvas, 405, 315, "T1")
    _draw_transfer(ms, canvas, 405, 352, "T2")
    _draw_transfer(ms, canvas, 526, 419, "T3")
    _draw_belt(ms, canvas, [(405, 304), (405, 315), (405, 352), (382, 368), (382, 419), (526, 419), (604, 448)], "至电厂煤仓")
    arrow(ms, _pt(canvas, 563, 436), _pt(canvas, 604, 448), _h(canvas, 3.0), layer="1_MAIN")
    _text(ms, canvas, "卸船机-皮带机-堆场输送线", 424, 350, h=2.0)

    # Drainage and fire-water facilities remain compact and readable.
    _rect(ms, canvas, 548, 365, 92, 44, layer="3_WATER")
    _ctext(ms, canvas, "雨污分流及回用水池", 594, 390, h=2.0, layer="3_WATER")
    _line(ms, canvas, (548, 387), (640, 387), layer="3_WATER")
    _line(ms, canvas, (594, 365), (594, 409), layer="3_WATER")
    arrow(ms, _pt(canvas, 516, 372), _pt(canvas, 548, 382), _h(canvas, 2.5), layer="3_WATER")
    _text(ms, canvas, "场地排水", 510, 365, h=1.9, layer="3_WATER")

    # Clear labels and boundary marks.
    _ctext(ms, canvas, "水域", 128, 164, h=6.5, layer="3_WATER")
    _ctext(ms, canvas, "陆域", 704, 438, h=6.5)
    _text(ms, canvas, "后方陆域建筑与堆场均位于岸线以上，水域构筑物位于岸线以下。", 470, 306, h=2.0)

    _draw_key_table(ms, canvas)
    _draw_norm_note(ms, canvas)
    _draw_legend(ms, canvas, 574, 532)
    _draw_scale_bar(ms, canvas, 54, 66)


def _draw_ship_like(ms, canvas, x, y, length, beam):
    bow = length * 0.12
    stern = length * 0.10
    pts = [
        (x, y + beam / 2),
        (x + bow, y + beam),
        (x + length - stern, y + beam),
        (x + length, y + beam * 0.72),
        (x + length, y + beam * 0.28),
        (x + length - stern, y),
        (x + bow, y),
    ]
    _poly(ms, canvas, pts, layer="2_SECONDARY", closed=True)
    bay_w = length * 0.075
    gap = length * 0.032
    bx = x + bow + gap
    for _ in range(6):
        _rect(ms, canvas, bx, y + beam * 0.22, bay_w, beam * 0.56, layer="2_SECONDARY")
        _line(ms, canvas, (bx, y + beam * 0.22), (bx + bay_w, y + beam * 0.78), layer="4_HATCH")
        _line(ms, canvas, (bx, y + beam * 0.78), (bx + bay_w, y + beam * 0.22), layer="4_HATCH")
        bx += bay_w + gap
