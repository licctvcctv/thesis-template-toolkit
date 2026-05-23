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
    poly,
    rect,
    section_title,
    table,
    text,
    waterline,
)
from data import CAISSON, HYDRO, NORM_NOTES


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


def dot_pattern(ms, x, y, w, h, step, radius, layer="4_HATCH"):
    yy = y + step * 0.55
    row = 0
    while yy < y + h - radius:
        xx = x + step * (0.55 + 0.45 * (row % 2))
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
        yy += step * 1.25


def layer_tag(ms, x, y, code, label, s, layer="6_TEXT"):
    rect(ms, x, y - 3.5 * s, 11.0 * s, 7.0 * s, layer="0_FRAME")
    ctext(ms, code, x + 5.5 * s, y - 1.0 * s, 1.42 * s, layer=layer)
    text(ms, label, x + 13.0 * s, y - 2.0 * s, 1.42 * s, layer=layer)


def draw_main_section(ms, c):
    s = c["scale"]
    datum = c["y_min"] + 255 * s
    x = c["x_min"] + 150 * s
    width = m(CAISSON["unit_width_m"])
    height = m(CAISSON["unit_height_m"])
    bottom = datum - height
    top = datum
    wall_t = m(CAISSON["wall_thickness_m"])
    breast_top = datum + m(3.60)

    rect(ms, x - m(10), bottom - m(CAISSON["rubble_replacement_m"] + CAISSON["rubble_bed_m"]) - m(1), width + m(33), breast_top - bottom + m(CAISSON["rubble_replacement_m"] + CAISSON["rubble_bed_m"]) + m(8), layer="0_FRAME")
    rect(ms, x - m(5), bottom - m(CAISSON["rubble_replacement_m"] + CAISSON["rubble_bed_m"]), width + m(28), m(CAISSON["rubble_replacement_m"]), layer="4_HATCH")
    zigzag_pattern(ms, x - m(5), bottom - m(CAISSON["rubble_replacement_m"] + CAISSON["rubble_bed_m"]), width + m(28), m(CAISSON["rubble_replacement_m"]), 4.2 * s)
    rect(ms, x - m(3), bottom - m(CAISSON["rubble_bed_m"]), width + m(24), m(CAISSON["rubble_bed_m"]), layer="4_HATCH")
    dot_pattern(ms, x - m(3), bottom - m(CAISSON["rubble_bed_m"]), width + m(24), m(CAISSON["rubble_bed_m"]), 4.0 * s, 0.35 * s)
    rect(ms, x, bottom, width, height, layer="1_MAIN")
    dot_pattern(ms, x + wall_t, bottom + wall_t, width - 2 * wall_t, height / 2 - 1.6 * wall_t, 4.6 * s, 0.28 * s)
    dot_pattern(ms, x + wall_t, bottom + height / 2 + wall_t, width - 2 * wall_t, height / 2 - 1.6 * wall_t, 4.6 * s, 0.28 * s)
    for k in range(1, CAISSON["chamber_cols"]):
        wall_x = x + k * width / CAISSON["chamber_cols"] - wall_t / 2
        rect(ms, wall_x, bottom, wall_t, height, layer="1_MAIN")
        sparse_hatch_box(ms, wall_x, bottom, wall_t, height, 3.2 * s)
    rect(ms, x, bottom + height / 2 - wall_t / 2, width, wall_t, layer="1_MAIN")
    sparse_hatch_box(ms, x, bottom + height / 2 - wall_t / 2, width, wall_t, 3.2 * s)
    sparse_hatch_box(ms, x, bottom, wall_t, height, 3.2 * s)
    sparse_hatch_box(ms, x + width - wall_t, bottom, wall_t, height, 3.2 * s)
    for i in range(CAISSON["chamber_cols"]):
        ctext(ms, "块石填料", x + (i + 0.5) * width / CAISSON["chamber_cols"], bottom + height * 0.72, 1.25 * s)
        ctext(ms, "舱格", x + (i + 0.5) * width / CAISSON["chamber_cols"], bottom + height * 0.28, 1.25 * s)

    rect(ms, x - m(0.8), top, width + m(1.8), m(CAISSON["breast_wall_h_m"]), layer="1_MAIN")
    sparse_hatch_box(ms, x - m(0.8), top, width + m(1.8), m(CAISSON["breast_wall_h_m"]), 3.4 * s)
    rect(ms, x + width, top - m(0.3), m(10), m(1.3), layer="2_SECONDARY")
    poly(ms, [(x + width, bottom), (x + width + m(18), bottom), (x + width + m(18), breast_top), (x + width, breast_top)], layer="4_HATCH", closed=True)
    text(ms, "后方回填及卸荷平台", x + width + m(2), datum + m(1.8), 1.5 * s)
    horizontal_pattern(ms, x + width, bottom, m(18), breast_top - bottom, 5.8 * s)

    rect(ms, x - m(1.3), top - m(1.0), m(1.0), m(2.0), layer="2_SECONDARY")
    arrow(ms, (x - m(7), top - m(0.1)), (x - m(1.3), top - m(0.1)), 1.2 * s)
    text(ms, "护舷反力", x - m(8.5), top + m(0.7), 1.45 * s)
    arrow(ms, (x - m(6), datum + m(1.2)), (x, datum + m(1.2)), 1.2 * s)
    text(ms, "水压力", x - m(7.2), datum + m(2.0), 1.45 * s)
    arrow(ms, (x + width + m(14), datum + m(0.8)), (x + width, datum + m(0.8)), 1.2 * s)
    text(ms, "土压力", x + width + m(8), datum + m(1.6), 1.45 * s)

    waterline(ms, x - m(9), x + width + m(20), datum, HYDRO["design_high_m"], "设计高水位 +1.91m", s)
    waterline(ms, x - m(9), x + width + m(20), datum, HYDRO["design_low_m"], "设计低水位 +0.22m", s, layer="3_WATER")
    waterline(ms, x - m(9), x + width + m(20), datum, HYDRO["extreme_high_m"], "极端高水位 +3.56m", s)
    line(ms, (x - m(9), datum), (x + width + m(20), datum), layer="5_DIM")
    text(ms, "理论最低潮面0.00", x - m(8.8), datum - m(0.9), 1.35 * s)

    dim_h(ms, x, x + width, bottom, -9 * s)
    dim_v(ms, x - 8 * s, bottom - m(6), breast_top, -8 * s)
    section_title(ms, "B-B 沉箱横断面图", x + width / 2, breast_top + 8 * s, 2.6 * s)
    text(ms, "水侧", x - m(8.5), breast_top + m(2.5), 1.7 * s)
    text(ms, "陆侧", x + width + m(18), breast_top + m(2.5), 1.7 * s)
    text(ms, "结构分层：胸墙 / 沉箱舱格 / 碎石基床 / 块石换填", x + m(2), bottom - m(7.0), 1.45 * s)
    layer_tag(ms, x - m(8.6), top + m(1.4), "M1", "胸墙与护舷带", s)
    layer_tag(ms, x - m(8.6), bottom + height * 0.68, "M2", "沉箱舱格填料", s)
    layer_tag(ms, x - m(8.6), bottom - m(0.8), "M3", "碎石整平基床", s)
    layer_tag(ms, x - m(8.6), bottom - m(4.2), "M4", "块石换填加固", s)
    layer_tag(ms, x + width + m(3.5), bottom + height * 0.78, "M5", "后方回填卸荷", s)


def draw_rebar_and_stability(ms, c):
    s = c["scale"]
    x = c["x_max"] - 270 * s
    y = c["y_min"] + 365 * s

    rect(ms, x - 12 * s, y - 22 * s, 210 * s, 66 * s, layer="0_FRAME")
    ctext(ms, "代表构件配筋及稳定示意", x + 94 * s, y + 37 * s, 2.1 * s)

    rect(ms, x, y, 78 * s, 22 * s, layer="1_MAIN")
    sparse_hatch_box(ms, x, y, 78 * s, 22 * s, 4.5 * s)
    for i in range(11):
        line(ms, (x + 5 * s + i * 6.8 * s, y + 3 * s), (x + 5 * s + i * 6.8 * s, y + 19 * s), layer="2_SECONDARY")
        circle(ms, x + 5 * s + i * 6.8 * s, y + 18 * s, 0.65 * s, layer="1_MAIN")
    for j in range(4):
        line(ms, (x + 3 * s, y + 5 * s + j * 4 * s), (x + 75 * s, y + 5 * s + j * 4 * s), layer="2_SECONDARY")
    ctext(ms, "沉箱外壁配筋大样：竖筋Φ16@150，水平筋Φ12@200", x + 39 * s, y + 29 * s, 1.8 * s)

    x2 = x + 95 * s
    y2 = y - 4 * s
    rect(ms, x2, y2, 54 * s, 20 * s, layer="1_MAIN")
    sparse_hatch_box(ms, x2, y2, 54 * s, 20 * s, 4.0 * s)
    for i in range(8):
        circle(ms, x2 + 6 * s + i * 6 * s, y2 + 5 * s, 0.75 * s, layer="1_MAIN")
        circle(ms, x2 + 6 * s + i * 6 * s, y2 + 15 * s, 0.75 * s, layer="1_MAIN")
    ctext(ms, "胸墙配筋：主筋Φ22，箍筋Φ12@150", x2 + 27 * s, y2 - 8 * s, 1.75 * s)

    bx = x
    by = c["y_min"] + 238 * s
    rect(ms, bx, by, 130 * s, 56 * s, layer="0_FRAME")
    ctext(ms, "重力式稳定验算受力示意", bx + 65 * s, by + 48 * s, 2.0 * s)
    rect(ms, bx + 45 * s, by + 12 * s, 32 * s, 26 * s, layer="1_MAIN")
    arrow(ms, (bx + 61 * s, by + 45 * s), (bx + 61 * s, by + 38 * s), 1.8 * s, layer="5_DIM")
    text(ms, "G", bx + 63 * s, by + 41 * s, 1.8 * s)
    arrow(ms, (bx + 17 * s, by + 26 * s), (bx + 45 * s, by + 26 * s), 2.0 * s, layer="5_DIM")
    text(ms, "P水", bx + 18 * s, by + 30 * s, 1.6 * s)
    arrow(ms, (bx + 105 * s, by + 23 * s), (bx + 77 * s, by + 23 * s), 2.0 * s, layer="5_DIM")
    text(ms, "E土", bx + 99 * s, by + 27 * s, 1.6 * s)
    arrow(ms, (bx + 52 * s, by + 9 * s), (bx + 78 * s, by + 9 * s), 2.0 * s, layer="5_DIM")
    text(ms, "R=μG", bx + 58 * s, by + 5 * s, 1.6 * s)


def draw_material_legend(ms, c):
    s = c["scale"]
    x = c["x_max"] - 270 * s
    y = c["y_min"] + 304 * s
    rect(ms, x, y, 178 * s, 31 * s, layer="0_FRAME")
    ctext(ms, "材料分层图例", x + 89 * s, y + 25 * s, 1.9 * s)
    rows = [
        ("M1 混凝土胸墙/沉箱壁", "diag"),
        ("M2 舱格块石填料", "dot"),
        ("M3 碎石整平基床", "dot"),
        ("M4 块石换填加固", "zig"),
        ("M5 后方回填卸荷", "h"),
    ]
    for idx, (label, kind) in enumerate(rows):
        yy = y + 18 * s - idx * 4.2 * s
        rect(ms, x + 8 * s, yy - 1.8 * s, 18 * s, 2.8 * s, layer="0_FRAME")
        if kind == "dot":
            dot_pattern(ms, x + 8 * s, yy - 1.8 * s, 18 * s, 2.8 * s, 2.8 * s, 0.24 * s)
        elif kind == "zig":
            zigzag_pattern(ms, x + 8 * s, yy - 1.8 * s, 18 * s, 2.8 * s, 2.8 * s)
        elif kind == "h":
            horizontal_pattern(ms, x + 8 * s, yy - 1.8 * s, 18 * s, 2.8 * s, 1.25 * s)
        else:
            sparse_hatch_box(ms, x + 8 * s, yy - 1.8 * s, 18 * s, 2.8 * s, 2.8 * s)
        text(ms, label, x + 30 * s, yy - 1.4 * s, 1.25 * s)


def draw_detail_callout(ms, c):
    s = c["scale"]
    x = c["x_max"] - 94 * s
    y = c["y_min"] + 238 * s
    rect(ms, x, y, 74 * s, 56 * s, layer="0_FRAME")
    ctext(ms, "接缝止水与倒滤构造", x + 37 * s, y + 49 * s, 1.7 * s)
    rect(ms, x + 15 * s, y + 12 * s, 16 * s, 28 * s, layer="1_MAIN")
    rect(ms, x + 43 * s, y + 12 * s, 16 * s, 28 * s, layer="1_MAIN")
    line(ms, (x + 37 * s, y + 10 * s), (x + 37 * s, y + 42 * s), layer="3_CENTERLINE")
    for k in range(5):
        yy = y + 14 * s + k * 5 * s
        line(ms, (x + 33 * s, yy), (x + 41 * s, yy + 2 * s), layer="2_SECONDARY")
    rect(ms, x + 8 * s, y + 6 * s, 58 * s, 4 * s, layer="4_HATCH")
    dot_pattern(ms, x + 8 * s, y + 6 * s, 58 * s, 4 * s, 3.2 * s, 0.25 * s)
    text(ms, "变形缝", x + 28 * s, y + 43 * s, 1.25 * s)
    text(ms, "止水带", x + 42 * s, y + 31 * s, 1.25 * s)
    text(ms, "倒滤层", x + 42 * s, y + 7 * s, 1.25 * s)


def draw(doc):
    c = create_sheet(doc, 100, "重力式方案断面图、细部构造及代表构件配筋图", "S-04", plotted_scale="1:100 / 大样1:30")
    ms = c["ms"]
    s = c["scale"]
    draw_main_section(ms, c)
    draw_rebar_and_stability(ms, c)
    draw_material_legend(ms, c)
    draw_detail_callout(ms, c)

    table(ms, c["x_max"] - 278 * s, c["y_min"] + 178 * s, [42 * s, 52 * s, 88 * s], [
        ["验算项目", "计算条件", "表达重点"],
        ["抗滑稳定", "R=μG 与水平力组合", "换填基床提供摩阻，满足规范安全系数"],
        ["抗倾稳定", "合力偏心距控制", "自重、胸墙、回填共同形成稳定力矩"],
        ["基床承载", "4m换填+2m碎石基床", "天然软土需先处理后计算"],
        ["耐久构造", "海工混凝土、止水带", "沉箱接缝与钢筋保护层控制"],
    ], 1.65 * s, title="沉箱方案计算表达表")

    c["note_x"] = c["x_min"] + 12 * s
    c["note_y"] = c["y_max"] - 58 * s
    notes(ms, c, [
        NORM_NOTES["caisson"],
        "老师要求两种方案均计算：本图明确重力式方案并非直接坐落软土，而是按换填加固后进行稳定验算。",
        "论文计算章节应对应补充：抗滑、抗倾、基床承载、地基处理工程量和沉降控制说明。",
        "配筋大样表达外壁、胸墙等代表构件，施工图阶段需结合完整荷载组合复核。",
    ])
