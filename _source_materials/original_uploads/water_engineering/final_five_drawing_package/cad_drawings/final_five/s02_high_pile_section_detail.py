import math

from common import (
    arrow,
    circle,
    create_sheet,
    ctext,
    dim_h,
    dim_v,
    line,
    m,
    notes,
    rect,
    section_title,
    table,
    text,
    waterline,
)
from data import HIGH_PILE, HYDRO, NORM_NOTES, SOIL_LAYERS


def sparse_hatch_box(ms, x, y, w, h, step, layer="4_HATCH"):
    count = int((w + h) / step) + 2
    for i in range(count):
        x1 = x + i * step
        y1 = y
        x2 = x1 - h
        y2 = y + h
        if x1 > x + w:
            extra = x1 - (x + w)
            x1 = x + w
            y1 = y + extra
        if x2 < x:
            y2 -= x - x2
            x2 = x
        if y1 <= y + h and y2 >= y:
            line(ms, (x1, y1), (x2, y2), layer=layer)


def horizontal_pattern(ms, x, y, w, h, step, layer="4_HATCH"):
    yy = y + step
    while yy < y + h:
        line(ms, (x, yy), (x + w, yy), layer=layer)
        yy += step


def vertical_pattern(ms, x, y, w, h, step, layer="4_HATCH"):
    xx = x + step
    while xx < x + w:
        line(ms, (xx, y), (xx, y + h), layer=layer)
        xx += step


def dot_pattern(ms, x, y, w, h, step, radius, layer="4_HATCH"):
    yy = y + step * 0.6
    row = 0
    while yy < y + h - radius:
        xx = x + step * (0.6 + 0.5 * (row % 2))
        while xx < x + w - radius:
            circle(ms, xx, yy, radius, layer=layer)
            xx += step
        yy += step
        row += 1


def zigzag_pattern(ms, x, y, w, h, step, layer="4_HATCH"):
    yy = y + step
    while yy < y + h:
        xx = x
        while xx < x + w - step:
            line(ms, (xx, yy), (xx + step * 0.5, yy + step * 0.28), layer=layer)
            line(ms, (xx + step * 0.5, yy + step * 0.28), (xx + step, yy), layer=layer)
            xx += step
        yy += step * 1.35


def soil_pattern(ms, x, y, w, h, idx, text_h):
    if idx == 0:
        horizontal_pattern(ms, x, y, w, h, text_h * 2.6)
    elif idx == 1:
        sparse_hatch_box(ms, x, y, w, h, text_h * 4.8)
    elif idx == 2:
        horizontal_pattern(ms, x, y, w, h, text_h * 2.2)
        sparse_hatch_box(ms, x, y, w, h, text_h * 6.0)
    elif idx == 3:
        horizontal_pattern(ms, x, y, w, h, text_h * 3.4)
        vertical_pattern(ms, x, y, w, h, text_h * 7.0)
    elif idx == 4:
        dot_pattern(ms, x, y, w, h, text_h * 4.6, text_h * 0.28)
    else:
        zigzag_pattern(ms, x, y, w, h, text_h * 4.8)


def light_soil_profile(ms, x, y_top, width, layers, vscale=1.0, text_h=800):
    y = y_top
    for idx, (name, thick_m, desc) in enumerate(layers):
        h = m(thick_m) * vscale
        rect(ms, x, y - h, width, h, layer="0_FRAME")
        soil_pattern(ms, x, y - h, width, h, idx, text_h)
        text(ms, f"{idx + 1}", x - text_h * 2.8, y - h / 2 + text_h * 0.4, text_h * 0.9)
        line(ms, (x - text_h * 1.2, y), (x, y), layer="5_DIM")
        line(ms, (x - text_h * 1.2, y - h), (x, y - h), layer="5_DIM")
        text(ms, name, x + text_h * 1.2, y - h / 2 + text_h * 0.4, text_h)
        text(ms, desc, x + width * 0.50, y - h / 2 + text_h * 0.4, text_h * 0.72)
        y -= h
    text(ms, "地层编号", x - text_h * 4.2, y_top + text_h * 1.3, text_h * 0.78)
    return y


def draw_main_section(ms, c):
    s = c["scale"]
    datum = c["y_min"] + 375 * s
    x_front = c["x_min"] + 145 * s
    width = m(HIGH_PILE["deck_width_m"])
    x_back = x_front + width
    deck_top = datum + m(3.60)
    deck_bot = datum + m(2.20)
    mud = datum + m(HYDRO["front_depth_m"])
    pile_tip = datum - m(32.0)

    rect(ms, x_front - m(12), pile_tip - m(2), m(48), deck_top - pile_tip + m(9), layer="0_FRAME")
    light_soil_profile(ms, x_front - m(10), mud, m(43), SOIL_LAYERS, vscale=0.72, text_h=1.4 * s)
    rect(ms, x_front, deck_bot, width, deck_top - deck_bot, layer="1_MAIN")
    sparse_hatch_box(ms, x_front, deck_bot, width, deck_top - deck_bot, 3.8 * s)
    rect(ms, x_front - m(1.3), deck_bot - m(2.6), m(1.3), m(4.0), layer="1_MAIN")
    sparse_hatch_box(ms, x_front - m(1.3), deck_bot - m(2.6), m(1.3), m(4.0), 2.8 * s)
    rect(ms, x_back, deck_bot, m(7.0), m(1.0), layer="2_SECONDARY")
    text(ms, "后方搭板及堆场连接段", x_back + m(0.8), deck_top + m(0.5), 1.5 * s)

    row_x = [x_front + m(2.0), x_front + m(10.0), x_front + m(18.0)]
    for idx, px in enumerate(row_x):
        r = 400 if idx < 2 else 300
        rect(ms, px - r, deck_bot - m(2.0), 2 * r, m(2.0), layer="1_MAIN")
        line(ms, (px - r, deck_bot - m(2.0)), (px - r, pile_tip), layer="1_MAIN")
        line(ms, (px + r, deck_bot - m(2.0)), (px + r, pile_tip), layer="1_MAIN")
        circle(ms, px, pile_tip, r, layer="1_MAIN")
        text(ms, "PHC800" if idx < 2 else "PHC600", px - 4 * s, pile_tip - 4 * s, 1.35 * s)
    rect(ms, x_front, deck_bot - m(1.8), width, m(1.8), layer="1_MAIN")
    sparse_hatch_box(ms, x_front, deck_bot - m(1.8), width, m(1.8), 3.5 * s)
    text(ms, HIGH_PILE["beam_size"], x_front + m(1.0), deck_bot - m(1.1), 1.45 * s)

    rect(ms, x_front - m(1.5), deck_bot - m(1.0), m(1.1), m(2.0), layer="2_SECONDARY")
    arrow(ms, (x_front - m(7), deck_bot - m(0.2)), (x_front - m(1.5), deck_bot - m(0.2)), 1.2 * s)
    text(ms, "DA-A橡胶护舷", x_front - m(7.5), deck_bot + m(0.6), 1.45 * s)

    waterline(ms, x_front - m(10), x_back + m(14), datum, HYDRO["design_high_m"], "设计高水位 +1.91m", s)
    waterline(ms, x_front - m(10), x_back + m(14), datum, HYDRO["design_low_m"], "设计低水位 +0.22m", s, layer="3_WATER")
    waterline(ms, x_front - m(10), x_back + m(14), datum, HYDRO["extreme_high_m"], "极端高水位 +3.56m", s)
    line(ms, (x_front - m(10), datum), (x_back + m(14), datum), layer="5_DIM")
    text(ms, "理论最低潮面 0.00", x_front - m(9.5), datum - m(0.9), 1.35 * s)

    dim_h(ms, x_front, x_back, deck_bot, -8 * s)
    dim_v(ms, x_back + 7 * s, mud, deck_top, 8 * s)
    section_title(ms, "A-A 横断面图", x_front + width / 2, deck_top + 8 * s, 2.6 * s)
    text(ms, "水侧", x_front - m(8.5), deck_top + m(2.4), 1.7 * s)
    text(ms, "陆侧", x_back + m(8.0), deck_top + m(2.4), 1.7 * s)
    return datum, x_front, x_back, deck_top, mud


def draw_rebar_details(ms, c):
    s = c["scale"]
    x = c["x_max"] - 285 * s
    y = c["y_min"] + 360 * s

    rect(ms, x - 12 * s, y - 86 * s, 210 * s, 132 * s, layer="0_FRAME")
    ctext(ms, "代表构件配筋大样", x + 93 * s, y + 38 * s, 2.1 * s)

    rect(ms, x, y, 78 * s, 24 * s, layer="1_MAIN")
    sparse_hatch_box(ms, x, y, 78 * s, 24 * s, 4.5 * s)
    for i in range(10):
        circle(ms, x + 7 * s + i * 7 * s, y + 6 * s, 0.85 * s, layer="1_MAIN")
        circle(ms, x + 7 * s + i * 7 * s, y + 18 * s, 0.85 * s, layer="1_MAIN")
    for i in range(7):
        rect(ms, x + 5 * s + i * 10 * s, y + 3 * s, 5 * s, 18 * s, layer="2_SECONDARY")
    ctext(ms, "横梁配筋大样：上/下主筋8Φ25，箍筋Φ12@150", x + 39 * s, y + 31 * s, 1.9 * s)

    x2 = x
    y2 = y - 55 * s
    rect(ms, x2, y2, 58 * s, 18 * s, layer="1_MAIN")
    sparse_hatch_box(ms, x2, y2, 58 * s, 18 * s, 4.0 * s)
    for i in range(8):
        circle(ms, x2 + 5 * s + i * 6.5 * s, y2 + 5 * s, 0.75 * s, layer="1_MAIN")
        circle(ms, x2 + 5 * s + i * 6.5 * s, y2 + 13 * s, 0.75 * s, layer="1_MAIN")
    ctext(ms, "叠合面板配筋：Φ14@150双向，保护层50mm", x2 + 29 * s, y2 + 25 * s, 1.8 * s)

    x3 = x + 95 * s
    y3 = y - 5 * s
    circle(ms, x3 + 18 * s, y3, 17 * s, layer="1_MAIN")
    circle(ms, x3 + 18 * s, y3, 10 * s, layer="2_SECONDARY")
    for i in range(8):
        px = x3 + 18 * s + 13 * s * math.cos(i * 0.785398)
        py = y3 + 13 * s * math.sin(i * 0.785398)
        circle(ms, px, py, 0.7 * s, layer="1_MAIN")
    ctext(ms, "PHC管桩桩头连接：灌芯C40，锚筋8Φ22", x3 + 18 * s, y3 - 24 * s, 1.75 * s)


def draw(doc):
    c = create_sheet(doc, 100, "高桩方案断面图、细部构造及代表构件配筋图", "S-02", plotted_scale="1:100 / 大样1:30")
    ms = c["ms"]
    s = c["scale"]
    draw_main_section(ms, c)
    draw_rebar_details(ms, c)

    table(ms, c["x_max"] - 278 * s, c["y_min"] + 230 * s, [42 * s, 54 * s, 82 * s], [
        ["构造部位", "主要参数", "设计说明"],
        ["码头面", "+3.60m", "满足极端高水位及作业安全要求"],
        ["桩基", "PHC800/PHC600", "穿透软土并进入持力层"],
        ["横梁", "1.2m x 1.8m", "承担排架横向受力"],
        ["护舷", HIGH_PILE["fender"], "抵抗船舶靠泊能量"],
        ["钢筋保护层", "50~70mm", "海洋环境耐久性控制"],
    ], 1.65 * s, title="断面与构造控制表")

    c["note_x"] = c["x_min"] + 12 * s
    c["note_y"] = c["y_max"] - 58 * s
    notes(ms, c, [
        NORM_NOTES["pile"],
        "本图补齐高桩方案横断面、水位、地质分层、桩入土、护舷、后方搭板及代表构件配筋。",
        "论文计算章节应对应补充：桩基竖向承载力、水平力、排架内力、横梁与面板配筋计算。",
        "构件配筋为毕业设计初步表达，施工图阶段需结合完整内力包络复核。",
    ])
