from common import (
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
)
from data import CAISSON, GENERAL, NORM_NOTES


def sparse_hatch(ms, x, y, w, h, step, layer="4_HATCH"):
    count = int((w + h) / step) + 1
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


def wave_pattern(ms, x, y, w, h, step, layer="3_WATER"):
    yy = y + step
    while yy < y + h:
        xx = x
        while xx < x + w - step:
            line(ms, (xx, yy), (xx + step * 0.50, yy + step * 0.18), layer=layer)
            line(ms, (xx + step * 0.50, yy + step * 0.18), (xx + step, yy), layer=layer)
            xx += step
        yy += step * 1.4


def draw_layer_tag(ms, x, y, code, label, s, layer="6_TEXT"):
    rect(ms, x, y - 3.8 * s, 12.0 * s, 7.6 * s, layer="0_FRAME")
    ctext(ms, code, x + 6.0 * s, y - 1.1 * s, 1.55 * s, layer=layer)
    text(ms, label, x + 15.0 * s, y - 2.0 * s, 1.55 * s, layer=layer)


def draw_joint(ms, x, y1, y2, scale):
    line(ms, (x - 0.8 * scale, y1), (x - 0.8 * scale, y2), layer="3_CENTERLINE")
    line(ms, (x + 0.8 * scale, y1), (x + 0.8 * scale, y2), layer="3_CENTERLINE")
    for k in range(5):
        yy = y1 + (y2 - y1) * (k + 0.5) / 5
        line(ms, (x - 1.8 * scale, yy - 1.2 * scale), (x + 1.8 * scale, yy + 1.2 * scale), layer="2_SECONDARY")


def draw_caisson_plan(ms, c):
    s = c["scale"]
    x0 = c["x_min"] + 65 * s
    y0 = c["y_min"] + 368 * s
    unit_l = m(CAISSON["unit_length_m"])
    width = m(CAISSON["unit_width_m"])
    count = CAISSON["unit_count"]
    length = unit_l * count

    rect(ms, x0 - 12 * s, y0 - 23 * s, length + 24 * s, width + 76 * s, layer="0_FRAME")
    rect(ms, x0 - 12 * s, y0 - 23 * s, length + 24 * s, 18 * s, layer="3_WATER")
    wave_pattern(ms, x0 - 10 * s, y0 - 20 * s, length + 20 * s, 12 * s, 8 * s)
    rect(ms, x0 - 12 * s, y0 + width + 14 * s, length + 24 * s, 28 * s, layer="2_SECONDARY")
    horizontal_pattern(ms, x0 - 12 * s, y0 + width + 14 * s, length + 24 * s, 28 * s, 6 * s)
    draw_layer_tag(ms, x0 + 6 * s, y0 + width + 37 * s, "P1", "后方陆域及引桥", s)
    draw_layer_tag(ms, x0 + 6 * s, y0 - 12 * s, "P2", "前沿水域及护舷", s, layer="3_WATER")
    draw_layer_tag(ms, x0 + length * 0.45, y0 + width * 0.50, "P3", "沉箱主体舱格", s)
    rect(ms, x0, y0, length, width, layer="1_MAIN")
    ctext(ms, "平面图：沉箱分段、舱格、变形缝及前沿设施", x0 + length / 2, y0 + width + 17 * s, 2.8 * s)
    text(ms, "前沿水侧", x0, y0 - 9 * s, 2.0 * s)
    text(ms, "后方陆侧", x0, y0 + width + 43 * s, 2.0 * s)

    for i in range(count):
        x = x0 + i * unit_l
        rect(ms, x, y0, unit_l, width, layer="1_MAIN")
        ctext(ms, f"C{i + 1:02d}", x + unit_l / 2, y0 + width + 5 * s, 1.8 * s)
        for k in range(1, CAISSON["chamber_cols"]):
            line(ms, (x + k * unit_l / CAISSON["chamber_cols"], y0), (x + k * unit_l / CAISSON["chamber_cols"], y0 + width), layer="2_SECONDARY")
        line(ms, (x, y0 + width / 2), (x + unit_l, y0 + width / 2), layer="2_SECONDARY")
        for lx in (x + unit_l * 0.18, x + unit_l * 0.82):
            for ly in (y0 + width * 0.20, y0 + width * 0.80):
                circle(ms, lx, ly, 280, layer="2_SECONDARY")
        sparse_hatch(ms, x + 1.0 * s, y0 + 1.0 * s, unit_l - 2.0 * s, width - 2.0 * s, 12.0 * s)
    for i in range(count + 1):
        x = x0 + i * unit_l
        line(ms, (x, y0 - m(1.6)), (x, y0 + width + m(1.6)), layer="3_CENTERLINE")
    rect(ms, x0, y0 - m(1.5), length, m(1.5), layer="2_SECONDARY")
    sparse_hatch(ms, x0, y0 - m(1.5), length, m(1.5), 9 * s)
    rect(ms, x0, y0 + width, length, m(3.0), layer="2_SECONDARY")
    horizontal_pattern(ms, x0, y0 + width, length, m(3.0), 4.5 * s)
    line(ms, (x0, y0 + width + m(1.5)), (x0 + length, y0 + width + m(1.5)), layer="2_SECONDARY")
    ctext(ms, "现浇胸墙及前沿护舷带", x0 + length / 2, y0 - 7 * s, 1.9 * s)

    for i in range(0, count, 2):
        x = x0 + i * unit_l + unit_l / 2
        circle(ms, x, y0 - m(2.3), 360, layer="2_SECONDARY")
        rect(ms, x - 800, y0 - m(1.5), 1600, 650, layer="2_SECONDARY")

    for tx in (x0 + m(40), x0 + m(220)):
        rect(ms, tx, y0 + width + m(3.0), m(12), m(32), layer="1_MAIN")
        ctext(ms, "引桥", tx + m(6), y0 + width + m(19), 1.8 * s)

    dim_h(ms, x0, x0 + length, y0, -14 * s)
    dim_v(ms, x0 + length, y0, y0 + width, 9 * s)
    ctext(ms, "13个标准沉箱连续布置，总长260m", x0 + length / 2, y0 - 18 * s, 2.0 * s)
    return x0, y0, length, width


def draw_caisson_elevation(ms, c, x0, length):
    s = c["scale"]
    datum = c["y_min"] + 193 * s
    unit_l = m(CAISSON["unit_length_m"])
    count = CAISSON["unit_count"]
    bottom = datum - m(14.0)
    top = datum + m(2.0)
    wall_top = datum + m(3.60)

    rect(ms, x0 - 12 * s, bottom - m(8.0), length + 24 * s, wall_top - bottom + m(14.0), layer="0_FRAME")
    line(ms, (x0, datum), (x0 + length, datum), layer="5_DIM")
    text(ms, "基准面0.00", x0 - 15 * s, datum - 1.5 * s, 1.7 * s)
    rect(ms, x0, bottom, length, top - bottom, layer="1_MAIN")
    sparse_hatch(ms, x0, bottom, length, top - bottom, 20.0 * s)
    rect(ms, x0, top, length, wall_top - top, layer="2_SECONDARY")
    sparse_hatch(ms, x0, top, length, wall_top - top, 13.0 * s)
    rect(ms, x0, bottom - m(2.0), length, m(2.0), layer="4_HATCH")
    sparse_hatch(ms, x0, bottom - m(2.0), length, m(2.0), 13.0 * s)
    rect(ms, x0, bottom - m(6.0), length, m(4.0), layer="4_HATCH")
    sparse_hatch(ms, x0, bottom - m(6.0), length, m(4.0), 15.0 * s)
    for i in range(count + 1):
        x = x0 + i * unit_l
        draw_joint(ms, x, bottom, wall_top, s)
        if i < count:
            ctext(ms, f"C{i + 1:02d}", x + unit_l / 2, wall_top + 4 * s, 1.6 * s)
            line(ms, (x + unit_l * 0.25, bottom), (x + unit_l * 0.25, top), layer="2_SECONDARY")
            line(ms, (x + unit_l * 0.50, bottom), (x + unit_l * 0.50, top), layer="2_SECONDARY")
            line(ms, (x + unit_l * 0.75, bottom), (x + unit_l * 0.75, top), layer="2_SECONDARY")
            line(ms, (x, bottom + (top - bottom) * 0.52), (x + unit_l, bottom + (top - bottom) * 0.52), layer="2_SECONDARY")
    for i in range(0, count, 2):
        x = x0 + i * unit_l + unit_l / 2
        rect(ms, x - 800, top - m(1.0), 1600, m(1.0), layer="2_SECONDARY")
    ctext(ms, "立面图：沉箱主体、胸墙、基床换填及分段缝", x0 + length / 2, wall_top + 11 * s, 2.8 * s)
    text(ms, "2.0m碎石整平基床", x0 + 8 * s, bottom - m(1.3), 1.65 * s)
    text(ms, "4.0m块石换填加固层（软土地基处理）", x0 + 8 * s, bottom - m(4.3), 1.65 * s)
    draw_layer_tag(ms, x0 + length + 8 * s, wall_top - 2 * s, "E1", "胸墙层", s)
    draw_layer_tag(ms, x0 + length + 8 * s, bottom + (top - bottom) * 0.55, "E2", "沉箱主体层", s)
    draw_layer_tag(ms, x0 + length + 8 * s, bottom - m(1.0), "E3", "碎石基床", s)
    draw_layer_tag(ms, x0 + length + 8 * s, bottom - m(4.2), "E4", "块石换填", s)
    text(ms, "前沿水侧", x0, wall_top + 6 * s, 1.9 * s)
    text(ms, "后方陆侧", x0 + length - 35 * s, wall_top + 6 * s, 1.9 * s)
    dim_h(ms, x0, x0 + length, bottom, -38 * s)
    dim_v(ms, x0 + length + 9 * s, bottom - m(6.0), wall_top, 9 * s)
    section_title(ms, "重力式沉箱码头立面图", x0 + length / 2, datum - 55 * s, 2.6 * s)


def draw_standard_unit_detail(ms, c):
    s = c["scale"]
    box_x = c["x_max"] - 178 * s
    box_y = c["y_min"] + 304 * s
    box_w = 158 * s
    box_h = 75 * s
    rect(ms, box_x, box_y, box_w, box_h, layer="0_FRAME")
    ctext(ms, "标准沉箱单元构造索引", box_x + box_w / 2, box_y + box_h - 8 * s, 2.1 * s)

    ux = box_x + 18 * s
    uy = box_y + 18 * s
    uw = 88 * s
    uh = 34 * s
    rect(ms, ux, uy, uw, uh, layer="1_MAIN")
    for k in range(1, 4):
        line(ms, (ux + uw * k / 4, uy), (ux + uw * k / 4, uy + uh), layer="2_SECONDARY")
    line(ms, (ux, uy + uh / 2), (ux + uw, uy + uh / 2), layer="2_SECONDARY")
    for k in range(4):
        ctext(ms, "填料舱", ux + uw * (k + 0.5) / 4, uy + uh * 0.73, 1.35 * s)
        ctext(ms, "空舱/检修", ux + uw * (k + 0.5) / 4, uy + uh * 0.25, 1.25 * s)
    dot_pattern(ms, ux + 3 * s, uy + 3 * s, uw - 6 * s, uh - 6 * s, 6 * s, 0.42 * s)
    rect(ms, ux, uy - 6 * s, uw, 4 * s, layer="2_SECONDARY")
    sparse_hatch(ms, ux, uy - 6 * s, uw, 4 * s, 7 * s)
    rect(ms, ux, uy + uh + 3 * s, uw, 5 * s, layer="2_SECONDARY")
    horizontal_pattern(ms, ux, uy + uh + 3 * s, uw, 5 * s, 2.4 * s)
    draw_layer_tag(ms, ux + uw + 9 * s, uy + uh + 5 * s, "D1", "胸墙", s)
    draw_layer_tag(ms, ux + uw + 9 * s, uy + uh * 0.55, "D2", "舱格", s)
    draw_layer_tag(ms, ux + uw + 9 * s, uy - 4 * s, "D3", "基床", s)
    text(ms, "单元长20m，宽12m；4列x2排舱格，分段缝处设止水。", box_x + 12 * s, box_y + 8 * s, 1.45 * s)


def draw_material_legend(ms, c):
    s = c["scale"]
    x = c["x_max"] - 178 * s
    y = c["y_min"] + 234 * s
    rect(ms, x, y, 158 * s, 55 * s, layer="0_FRAME")
    ctext(ms, "材料与构造分层图例", x + 79 * s, y + 48 * s, 2.0 * s)
    rows = [
        ("混凝土胸墙/沉箱壁", "sparse"),
        ("块石填料/舱格填充", "dot"),
        ("碎石整平基床", "dot"),
        ("块石换填加固层", "diag"),
    ]
    for idx, (label, kind) in enumerate(rows):
        yy = y + 36 * s - idx * 9 * s
        rect(ms, x + 10 * s, yy - 4 * s, 28 * s, 6 * s, layer="0_FRAME")
        if kind == "dot":
            dot_pattern(ms, x + 10 * s, yy - 4 * s, 28 * s, 6 * s, 3.2 * s, 0.32 * s)
        else:
            sparse_hatch(ms, x + 10 * s, yy - 4 * s, 28 * s, 6 * s, 4.5 * s)
        text(ms, label, x + 43 * s, yy - 3.0 * s, 1.45 * s)


def draw(doc):
    c = create_sheet(doc, 500, "重力式沉箱结构平面、立面图", "S-03")
    ms = c["ms"]
    s = c["scale"]
    x0, _, length, _ = draw_caisson_plan(ms, c)
    draw_caisson_elevation(ms, c, x0, length)
    draw_standard_unit_detail(ms, c)
    draw_material_legend(ms, c)

    table(ms, c["x_max"] - 178 * s, c["y_max"] - 70 * s, [45 * s, 48 * s, 68 * s], [
        ["项目", "参数", "表达重点"],
        ["沉箱数量", f"{CAISSON['unit_count']}个", "20m标准段连续布置"],
        ["单箱尺寸", "20m x 12m x 14m", "平面舱格与立面高度"],
        ["基础处理", "4m块石换填+2m碎石基床", "软土地基加固后计算"],
        ["上部结构", "现浇胸墙+前沿护舷带", "靠泊与系缆受力"],
        ["接缝", "变形缝+止水带", "沉箱分段构造"],
    ], 1.9 * s, title="沉箱方案构件表")

    notes(ms, c, [
        NORM_NOTES["caisson"],
        "本工程天然软土地基不宜直接采用重力式结构，图中按换填加固后布置沉箱方案，用于完整计算和方案比选。",
        f"沉箱总长按{CAISSON['unit_count']}个20m标准箱布置，与总平面{GENERAL['berth_length_m']:.0f}m泊位长度一致。",
        "本图作为两方案结构平立面图之一，后续S-04给出横断面、稳定构造和代表配筋。",
    ])
