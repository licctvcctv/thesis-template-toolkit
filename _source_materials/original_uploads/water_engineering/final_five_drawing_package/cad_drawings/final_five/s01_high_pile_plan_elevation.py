from common import (
    circle,
    create_sheet,
    ctext,
    dim_h,
    dim_v,
    line,
    m,
    multiline,
    notes,
    rect,
    section_title,
    table,
    text,
)
from data import GENERAL, HIGH_PILE, NORM_NOTES


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


def draw_plan(ms, canvas):
    s = canvas["scale"]
    x0 = canvas["x_min"] + 75 * s
    y0 = canvas["y_min"] + 365 * s
    length = m(GENERAL["structural_length_m"])
    width = m(HIGH_PILE["deck_width_m"])
    bent_count = HIGH_PILE["bent_count"]
    spacing = m(HIGH_PILE["bent_spacing_m"])

    rect(ms, x0 - 12 * s, y0 - 24 * s, length + 24 * s, width + 76 * s, layer="0_FRAME")
    rect(ms, x0, y0, length, width, layer="1_MAIN")
    ctext(ms, "平面图：排架、桩位、轨道、护舷及系船柱布置", x0 + length / 2, y0 + width + 17 * s, 2.8 * s)
    text(ms, "前沿水侧", x0, y0 - 9 * s, 2.0 * s)
    text(ms, "后方陆侧", x0, y0 + width + 43 * s, 2.0 * s)

    for i in range(7):
        y = y0 + width * i / 6
        line(ms, (x0, y), (x0 + length, y), layer="3_CENTERLINE")

    pile_rows = [m(v) for v in HIGH_PILE["pile_rows_m"]]
    for i in range(bent_count):
        x = x0 + i * spacing
        if x > x0 + length:
            continue
        line(ms, (x, y0 - m(2)), (x, y0 + width + m(2)), layer="3_CENTERLINE")
        rect(ms, x - 600, y0, 1200, width, layer="1_MAIN")
        ctext(ms, str(i + 1), x, y0 + width + 6 * s, 1.9 * s)
        for row_idx, py in enumerate(pile_rows):
            r = 400 if row_idx < 2 else 300
            circle(ms, x, y0 + py, r, layer="1_MAIN")
            line(ms, (x - r * 1.7, y0 + py), (x + r * 1.7, y0 + py), layer="3_CENTERLINE")
            line(ms, (x, y0 + py - r * 1.7), (x, y0 + py + r * 1.7), layer="3_CENTERLINE")

    rail_y1 = y0 + width / 2 - m(HIGH_PILE["track_gauge_m"]) / 2
    rail_y2 = y0 + width / 2 + m(HIGH_PILE["track_gauge_m"]) / 2
    for rail_y in (rail_y1, rail_y2):
        line(ms, (x0, rail_y - 100), (x0 + length, rail_y - 100), layer="1_MAIN")
        line(ms, (x0, rail_y + 100), (x0 + length, rail_y + 100), layer="1_MAIN")
        for i in range(0, bent_count, 2):
            x = x0 + i * spacing
            rect(ms, x - 350, rail_y - 230, 700, 460, layer="2_SECONDARY")
    ctext(ms, f"卸船机轨道，轨距{HIGH_PILE['track_gauge_m']}m", x0 + length * 0.72, rail_y2 + 4 * s, 2.0 * s)

    for i in range(0, bent_count, 2):
        x = x0 + i * spacing
        circle(ms, x, y0 + m(1.25), 360, layer="2_SECONDARY")
        circle(ms, x, y0 + m(1.25), 170, layer="2_SECONDARY")
    for i in range(bent_count):
        x = x0 + i * spacing
        rect(ms, x - 900, y0 - 850, 1800, 850, layer="2_SECONDARY")
    text(ms, "前沿DA-A橡胶护舷，间距约8m；隔排架设系船柱", x0, y0 - 4 * s, 2.0 * s)

    for x in (x0 + m(40), x0 + m(210)):
        rect(ms, x, y0 + width, m(12), m(34), layer="1_MAIN")
        ctext(ms, "引桥", x + m(6), y0 + width + m(17), 1.8 * s)

    ctext(ms, "结构长度250m，排架间距8m，三排桩支承", x0 + length / 2, y0 - 18 * s, 2.0 * s)
    dim_h(ms, x0, x0 + length, y0, -14 * s)
    dim_v(ms, x0 + length, y0, y0 + width, 9 * s)
    return x0, y0, length, width


def draw_elevation(ms, canvas, plan_x, plan_len):
    s = canvas["scale"]
    datum = canvas["y_min"] + 188 * s
    x0 = plan_x
    length = plan_len
    deck_top = datum + m(3.60)
    deck_bot = datum + m(2.20)
    mud = datum - m(12.50)
    pile_tip = datum - m(30.0)
    spacing = m(HIGH_PILE["bent_spacing_m"])

    rect(ms, x0 - 12 * s, pile_tip - 10 * s, length + 24 * s, deck_top - pile_tip + 35 * s, layer="0_FRAME")
    line(ms, (x0, datum), (x0 + length, datum), layer="5_DIM")
    text(ms, "基准面 0.00", x0 - 17 * s, datum - 1.5 * s, 1.7 * s)
    line(ms, (x0, mud), (x0 + length, mud), layer="3_WATER")
    text(ms, "前沿设计泥面/水深 -12.50m", x0 - 17 * s, mud - 1.5 * s, 1.7 * s)
    rect(ms, x0, deck_bot, length, deck_top - deck_bot, layer="1_MAIN")
    sparse_hatch_box(ms, x0, deck_bot, length, deck_top - deck_bot, 6.0 * s)
    ctext(ms, "立面图：上部梁板、排架、基桩入土及前沿设施", x0 + length / 2, deck_top + 11 * s, 2.8 * s)

    for i in range(HIGH_PILE["bent_count"]):
        x = x0 + i * spacing
        if x > x0 + length:
            continue
        rect(ms, x - 600, deck_bot - m(1.8), 1200, m(1.8), layer="1_MAIN")
        line(ms, (x, deck_bot - m(1.8)), (x, pile_tip), layer="1_MAIN")
        line(ms, (x - 420, deck_bot - m(1.8)), (x - 420, pile_tip), layer="1_MAIN")
        line(ms, (x + 420, deck_bot - m(1.8)), (x + 420, pile_tip), layer="1_MAIN")
        if i % 4 == 0:
            text(ms, f"{i + 1}", x - 1.5 * s, deck_top + 3 * s, 1.5 * s)
    rect(ms, x0, mud - m(0.8), length, m(0.8), layer="4_HATCH")
    sparse_hatch_box(ms, x0, mud - m(0.8), length, m(0.8), 8.0 * s)
    text(ms, "PHC桩穿透软弱淤泥层，桩端进入粗砾砂/强风化花岗岩持力层", x0 + 20 * s, pile_tip - 5 * s, 2.0 * s)
    text(ms, "前沿水侧", x0, deck_top + 6 * s, 1.9 * s)
    text(ms, "后方陆侧", x0 + length - 35 * s, deck_top + 6 * s, 1.9 * s)
    dim_h(ms, x0, x0 + length, deck_bot, -82 * s)
    dim_v(ms, x0 + length + 9 * s, mud, deck_top, 9 * s)
    section_title(ms, "高桩梁板式码头立面图", x0 + length / 2, datum - 52 * s, 2.6 * s)


def draw(doc):
    c = create_sheet(doc, 500, "高桩梁板式结构平面、立面图", "S-01")
    ms = c["ms"]
    s = c["scale"]
    plan_x, plan_y, plan_len, _ = draw_plan(ms, c)
    draw_elevation(ms, c, plan_x, plan_len)

    table(ms, c["x_max"] - 172 * s, c["y_max"] - 70 * s, [45 * s, 50 * s, 62 * s], [
        ["项目", "参数", "图中表达"],
        ["结构型式", "高桩梁板式", "平面+立面"],
        ["排架布置", "32榀，间距8.0m", "轴线编号1~32"],
        ["桩基", "前/中排PHC800，后排PHC600", "三排桩位"],
        ["上部结构", "横梁、纵梁、轨道梁、叠合面板", "梁板平台"],
        ["靠泊设施", "DA-A800H护舷、系船柱", "前沿布置"],
    ], 1.9 * s, title="高桩方案构件表")

    notes(ms, c, [
        NORM_NOTES["structure"],
        "本方案适用于表层厚软土场地，桩基将上部荷载传至深部粗砾砂及风化花岗岩持力层。",
        "平台主体按250m结构长度绘制，并与总平面260m泊位控制长度对应。",
        "本图作为两方案结构平立面图之一，后续S-02给出横断面、细部构造和代表构件配筋。",
    ])
