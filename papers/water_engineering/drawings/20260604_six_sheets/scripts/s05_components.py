import math


def _poly(s, pts, layer="THICK"):
    s.poly(pts, True, layer)


def _hatch_polygon(s, pts, spacing=850):
    """Draw 45 degree section lines clipped to a simple polygon."""
    if len(pts) < 3:
        return
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    c_min = min(y - x for x, y in pts) - spacing
    c_max = max(y - x for x, y in pts) + spacing
    c = math.floor(c_min / spacing) * spacing
    edges = list(zip(pts, pts[1:] + pts[:1]))
    while c <= c_max:
        cuts = []
        for (x1, y1), (x2, y2) in edges:
            d1 = y1 - x1 - c
            d2 = y2 - x2 - c
            if abs(d1) < 1e-7 and abs(d2) < 1e-7:
                continue
            if (d1 <= 0 < d2) or (d2 <= 0 < d1):
                t = d1 / (d1 - d2)
                x = x1 + t * (x2 - x1)
                y = y1 + t * (y2 - y1)
                cuts.append((x + y, x, y))
        cuts.sort()
        for i in range(0, len(cuts) - 1, 2):
            _, x1, y1 = cuts[i]
            _, x2, y2 = cuts[i + 1]
            if (x2 - x1) ** 2 + (y2 - y1) ** 2 > 220 * 220:
                s.line(x1, y1, x2, y2, "HATCH")
        c += spacing


def _dim_h(s, x1, y, x2, label, above=False, text_h=360):
    offset = 1000 if above else -1000
    yy = y + offset
    s.line(x1, y, x1, yy, "DIM")
    s.line(x2, y, x2, yy, "DIM")
    s.line(x1, yy, x2, yy, "DIM")
    tick = 300
    s.line(x1, yy, x1 + tick, yy + (120 if above else -120), "DIM")
    s.line(x2, yy, x2 - tick, yy + (120 if above else -120), "DIM")
    s.text((x1 + x2) / 2, yy + (220 if above else 220), label, text_h, "DIM", "C")


def _dim_h_top_chain(s, y, breaks, labels, text_h=260):
    yy = y + 1050
    tick = 220
    for x in breaks:
        s.line(x, y, x, yy, "DIM")
        s.line(x, yy, x + tick, yy + 100, "DIM")
    for x1, x2 in zip(breaks, breaks[1:]):
        s.line(x1, yy, x2, yy, "DIM")
    for (x1, x2), label in zip(zip(breaks, breaks[1:]), labels):
        s.text((x1 + x2) / 2, yy + 260, label, text_h, "DIM", "C")


def _dim_h_top_two_small(s, y, x0, x1, x2):
    yy = y + 1050
    tick = 220
    for x in (x0, x1, x2):
        s.line(x, y, x, yy, "DIM")
        s.line(x, yy, x + tick, yy + 100, "DIM")
    s.line(x0, yy, x2, yy, "DIM")
    s.text((x0 + x1) / 2, yy + 260, "150", 260, "DIM", "C")
    s.line((x1 + x2) / 2, yy, x2 + 520, yy + 430, "DIM")
    s.text(x2 + 620, yy + 340, "50", 240, "DIM", "L")


def _dim_v_left(s, x, y1, y2, label, text_h=360):
    xx = x - 1100
    s.line(x, y1, xx, y1, "DIM")
    s.line(x, y2, xx, y2, "DIM")
    s.line(xx, y1, xx, y2, "DIM")
    tick = 280
    s.line(xx, y1, xx - tick, y1 + tick, "DIM")
    s.line(xx, y2, xx + tick, y2 - tick, "DIM")
    s.text(xx - 300, (y1 + y2) / 2, label, text_h, "DIM", "R", 90)


def _dim_v_right(s, x, y1, y2, label, text_h=360):
    xx = x + 1100
    s.line(x, y1, xx, y1, "DIM")
    s.line(x, y2, xx, y2, "DIM")
    s.line(xx, y1, xx, y2, "DIM")
    tick = 280
    s.line(xx, y1, xx + tick, y1 + tick, "DIM")
    s.line(xx, y2, xx - tick, y2 - tick, "DIM")
    s.text(xx + 300, (y1 + y2) / 2, label, text_h, "DIM", "L", 90)


def _dim_v_left_at(s, x_body, x_dim, y1, y2, label, text_h=360):
    s.line(x_body, y1, x_dim, y1, "DIM")
    s.line(x_body, y2, x_dim, y2, "DIM")
    s.line(x_dim, y1, x_dim, y2, "DIM")
    tick = 260
    s.line(x_dim, y1, x_dim - tick, y1 + tick, "DIM")
    s.line(x_dim, y2, x_dim + tick, y2 - tick, "DIM")
    s.text(x_dim - 260, (y1 + y2) / 2, label, text_h, "DIM", "R", 90)


def _scale_pts(origin, scale, pts):
    ox, oy = origin
    return [(ox + x * scale, oy + y * scale) for x, y in pts]


def draw_t_beam(s, origin=(22000, 34000), scale=5.0):
    ox, oy = origin
    k = scale
    pts = _scale_pts(origin, k, [
        (0, 0), (1800, 0), (1800, 800), (1350, 800),
        (1350, 2200), (450, 2200), (450, 800), (0, 800),
    ])
    _poly(s, pts)
    _hatch_polygon(s, _scale_pts(origin, k, [(0, 0), (1800, 0), (1800, 800), (0, 800)]), 800)
    _hatch_polygon(s, _scale_pts(origin, k, [(450, 800), (1350, 800), (1350, 2200), (450, 2200)]), 800)
    s.text(ox + 900 * k, oy - 1600, "横梁断面", 430, "TEXT", "C")
    _dim_h(s, ox, oy, ox + 1800 * k, "1800")
    _dim_h(s, ox, oy + 2200 * k, ox + 450 * k, "450", True)
    _dim_h(s, ox + 450 * k, oy + 2200 * k, ox + 1350 * k, "900", True)
    _dim_h(s, ox + 1350 * k, oy + 2200 * k, ox + 1800 * k, "450", True)
    _dim_v_left(s, ox, oy, oy + 800 * k, "800")
    _dim_v_left(s, ox, oy + 800 * k, oy + 2200 * k, "1400")


def draw_trapezoid_beam(s, origin=(50000, 34000), scale=6.0):
    ox, oy = origin
    k = scale
    pts = _scale_pts(origin, k, [
        (200, 0), (600, 0), (800, 1200), (0, 1200),
    ])
    _poly(s, pts)
    _hatch_polygon(s, pts, 800)
    s.text(ox + 400 * k, oy - 1600, "纵梁断面", 430, "TEXT", "C")
    _dim_h(s, ox, oy + 1200 * k, ox + 800 * k, "800", True)
    _dim_h(s, ox + 200 * k, oy, ox + 600 * k, "400")
    _dim_v_left(s, ox, oy, oy + 1200 * k, "1200")


def draw_berthing_component(s, origin=(40000, 9500), scale=4.2):
    ox, oy = origin
    k = scale
    # Reference-style berthing component: straight left datum, simple tapered body,
    # horizontal corbel and aligned dimension chain.
    body = _scale_pts(origin, k, [
        (0, 0), (250, 0), (400, 2450), (520, 2450),
        (520, 2750), (410, 2750), (220, 3800),
        (200, 3800), (200, 4000), (0, 4000),
    ])
    corbel = _scale_pts(origin, k, [
        (520, 2450), (1520, 2450), (1520, 2750), (520, 2750),
    ])
    top_recess = _scale_pts(origin, k, [
        (0, 3800), (200, 3800), (200, 4000), (0, 4000),
    ])

    _poly(s, body)
    _poly(s, corbel)
    s.line(ox + 150 * k, oy + 3800 * k, ox + 150 * k, oy + 4000 * k, "THIN")
    _hatch_polygon(s, body, 720)
    _hatch_polygon(s, corbel, 720)
    _hatch_polygon(s, top_recess, 720)

    s.text(ox + 650 * k, oy - 1700, "靠船构件断面", 430, "TEXT", "C")

    x_total = ox - 2500
    x_seg = ox - 1200
    _dim_v_left_at(s, ox, x_total, oy, oy + 4000 * k, "4000")
    _dim_v_left_at(s, ox, x_seg, oy, oy + 2450 * k, "2450")
    _dim_v_left_at(s, ox, x_seg, oy + 2450 * k, oy + 2750 * k, "300")
    _dim_v_left_at(s, ox, x_seg, oy + 2750 * k, oy + 3800 * k, "1050")
    _dim_v_left_at(s, ox, x_seg, oy + 3800 * k, oy + 4000 * k, "200")
    _dim_h(s, ox, oy, ox + 250 * k, "250")
    _dim_h(s, ox + 520 * k, oy + 2750 * k, ox + 1520 * k, "1000", True)
    _dim_h_top_two_small(s, oy + 4000 * k, ox, ox + 150 * k, ox + 200 * k)


def draw_s05_components(s):
    s.text(42050, 51500, "横梁、纵梁及靠船构件断面图（单位：mm）", 560, "TEXT", "C")
    draw_t_beam(s)
    draw_trapezoid_beam(s)
    draw_berthing_component(s)
    s.mtext(
        56500,
        28500,
        17000,
        "说明：\\P"
        "1. 本图按典型构件断面绘制，尺寸单位为mm。\\P"
        "2. 横梁按1800×2200控制，底部加宽段与桩帽、节点钢筋连接。\\P"
        "3. 纵梁按800×1200控制，底宽400，梁端搁置和湿接缝长度另按构造处理。\\P"
        "4. 靠船构件按前沿局部受力构件绘制，护舷、系船柱连接区应按构造加强。",
        380,
    )
