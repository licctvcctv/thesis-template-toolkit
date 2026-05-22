import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DETAIL_ROOT = os.path.join(ROOT, "port_drawings_detailed")
if DETAIL_ROOT not in sys.path:
    sys.path.insert(0, DETAIL_ROOT)

from common.cad import AcadSession, com_call


OUT_DIR = os.path.join(ROOT, "caisson_only_reference_exact", "output")


def monochrome_layers(d):
    # The reference is a black-and-white textbook drawing. Keep AutoCAD layer
    # colors subdued so the generated DWG does not look like an unrelated CAD
    # schematic with colored construction layers.
    for name, color in [
        ("STRUCTURE", 7),
        ("CAISSON", 7),
        ("FOUNDATION", 8),
        ("BACKFILL", 8),
        ("HATCH", 8),
        ("TEXT", 7),
        ("DIM", 2),
        ("LEVEL", 7),
        ("CUT", 7),
        ("CENTER", 8),
    ]:
        d.layer(name, color)


def dots(d, x, y, w, h, dx=55, dy=45):
    yy = y + dy * 0.5
    while yy < y + h:
        xx = x + dx * 0.5
        while xx < x + w:
            d.circle(xx, yy, 2.2, "HATCH")
            xx += dx
        yy += dy


def concrete(d, x, y, w, h, spacing=24):
    diag_hatch(d, x, y, w, h, spacing, 45)


def diag_hatch(d, x, y, w, h, spacing=24, angle=45):
    # Clipped diagonal hatching. The previous generic hatch filled across
    # adjacent objects and made the drawing look nothing like the reference.
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
                d.line(pts[0][0], pts[0][1], pts[1][0], pts[1][1], "HATCH")
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
                d.line(pts[0][0], pts[0][1], pts[1][0], pts[1][1], "HATCH")
            c += spacing


def slope_ticks(d, x1, y1, x2, y2, spacing=55):
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
        d.line(x, y, x + nx * 22, y + ny * 22, "HATCH")
        t += spacing


def dim_h(d, x1, x2, y_line, y_dim, text):
    d.dim_rotated((x1, y_line, 0), (x2, y_line, 0), ((x1 + x2) / 2, y_dim, 0), 0, text)


def dim_v(d, x_line, y1, y2, x_dim, text):
    d.dim_rotated((x_line, y1, 0), (x_line, y2, 0), (x_dim, (y1 + y2) / 2, 0), 1.57079632679, text)


def level(d, x1, x2, y, text, tx=None):
    d.line(x1, y, x2, y, "LEVEL")
    d.text(f"▽{text}", tx if tx is not None else x2 + 18, y + 8, 22, "TEXT")


def leader(d, x1, y1, x2, y2, text, height=22, rotation=0):
    d.line(x1, y1, x2, y2, "TEXT")
    d.text(text, x2 + 8, y2 + 6, height, "TEXT", rotation=rotation)


def draw_main_section(d):
    # Coordinates are in cm, arranged to match the provided caisson reference photo.
    x0, y0 = 500, 120
    outer_w, outer_h = 1100, 1200
    left_wall, right_wall, bottom_wall, top_wall = 85, 85, 85, 95
    mid_wall = 45
    top_y = y0 + outer_h

    # Foundation and seabed line.
    d.line(210, y0 - 35, 1845, y0 - 35, "FOUNDATION")
    slope_ticks(d, 210, y0 - 35, 1845, y0 - 35, 70)
    d.text("抛石基床", 1520, y0 - 130, 24, "TEXT")
    d.text("单位:cm", 1735, y0 - 190, 22, "TEXT")
    d.text("图 2-3  沉箱码头", 1165, y0 - 190, 24, "TEXT")

    # Toe stones matching the reference dots/circles.
    for cx, cy, r in [
        (360, y0 + 18, 20), (405, y0 + 38, 18), (450, y0 + 15, 16),
        (1628, y0 + 22, 20), (1675, y0 + 45, 17), (1718, y0 + 18, 16),
    ]:
        d.circle(cx, cy, r, "FOUNDATION")

    # Caisson body: hatch only concrete walls, not the whole interior.
    d.rect(x0, y0, outer_w, outer_h, "CAISSON")
    d.rect(x0 + left_wall, y0 + bottom_wall, outer_w - left_wall - right_wall, outer_h - bottom_wall - top_wall, "CAISSON")
    # Concrete wall strips.
    concrete(d, x0, y0, outer_w, bottom_wall, 24)
    concrete(d, x0, top_y - top_wall, outer_w, top_wall, 24)
    concrete(d, x0, y0, left_wall, outer_h, 24)
    concrete(d, x0 + outer_w - right_wall, y0, right_wall, outer_h, 24)
    d.rect(x0 + outer_w / 2 - mid_wall / 2, y0 + bottom_wall, mid_wall, outer_h - bottom_wall - top_wall, "CAISSON")
    concrete(d, x0 + outer_w / 2 - mid_wall / 2, y0 + bottom_wall, mid_wall, outer_h - bottom_wall - top_wall, 22)
    d.rect(x0 + left_wall, y0 + outer_h / 2 - mid_wall / 2, outer_w - left_wall - right_wall, mid_wall, "CAISSON")
    concrete(d, x0 + left_wall, y0 + outer_h / 2 - mid_wall / 2, outer_w - left_wall - right_wall, mid_wall, 22)

    # Chamber fill with dots, leaving wall hatch visible.
    dots(d, x0 + left_wall + 18, y0 + bottom_wall + 18, outer_w - left_wall - right_wall - 36, outer_h - bottom_wall - top_wall - 36, 48, 40)

    # Upper chamber openings, placed like the reference.
    d.rect(x0 + 205, y0 + 705, 330, 285, "CAISSON")
    d.rect(x0 + 655, y0 + 705, 330, 285, "CAISSON")

    # Back fill area to the right.
    bx = x0 + outer_w
    d.polyline([(bx, y0), (bx + 555, y0 + 170), (bx + 760, top_y), (bx, top_y)], "BACKFILL", True)
    dots(d, bx + 35, y0 + 70, 620, outer_h - 95, 55, 45)
    d.text("回", bx + 315, y0 + 550, 26, "TEXT", rotation=90)
    d.text("填", bx + 315, y0 + 495, 26, "TEXT", rotation=90)
    d.text("砂", bx + 315, y0 + 435, 26, "TEXT", rotation=90)
    d.line(bx, y0, bx + 230, y0 - 215, "FOUNDATION")
    slope_ticks(d, bx, y0, bx + 230, y0 - 215, 55)

    # Chest wall and small top cap, closer to the reference proportions.
    d.rect(x0 - 85, y0, 85, outer_h + 55, "STRUCTURE")
    concrete(d, x0 - 85, y0, 85, outer_h + 55, 22)
    d.polyline([
        (x0 - 85, top_y + 55),
        (x0 + 315, top_y + 55),
        (x0 + 315, top_y + 250),
        (x0 + 165, top_y + 250),
        (x0 + 165, top_y + 315),
        (x0 - 85, top_y + 315),
    ], "STRUCTURE", True)
    concrete(d, x0 - 85, top_y + 55, 400, 260, 28)
    d.text("胸墙", x0 - 190, top_y + 140, 24, "TEXT", rotation=90)
    d.text("纵隔墙", x0 + 498, top_y + 22, 22, "TEXT", rotation=90)
    d.text("箱臂", bx + 70, y0 + 490, 24, "TEXT", rotation=90)
    d.text("箱底", bx + 35, y0 + 120, 24, "TEXT", rotation=90)

    # Water levels and elevations as in the photo.
    level(d, x0 - 475, x0 - 255, top_y + 250, "+4.00")
    level(d, x0 - 410, x0 - 180, top_y + 72, "设计高水位 +2.27")
    level(d, x0 - 410, x0 - 180, top_y - 105, "设计低水位 +0.50")
    level(d, x0 - 260, x0 - 80, y0 + 150, "-10.50")
    level(d, x0 - 260, x0 - 80, y0, "-12.00")

    # Dimensions placed to match the reference, not an invented layout.
    dim_h(d, x0, x0 + outer_w, y0, y0 - 115, "1100")
    dim_h(d, x0 - 200, x0, y0, y0 - 115, "200")
    dim_h(d, x0 + outer_w, x0 + outer_w + 200, y0, y0 - 115, "200")
    dim_v(d, x0 - 8, y0, top_y, x0 - 200, "1200")
    dim_h(d, x0 + 165, x0 + 315, top_y + 315, top_y + 390, "150")
    dim_h(d, x0 - 85, x0 + 165, top_y + 315, top_y + 390, "250")
    dim_h(d, x0 - 85, x0 + 230, top_y + 250, top_y + 455, "315")
    dim_v(d, x0 + left_wall + 18, y0 + bottom_wall, y0 + bottom_wall + 290, x0 + 140, "290")
    dim_h(d, x0 + left_wall, x0 + left_wall + 427.5, y0 + 520, y0 + 450, "427.5")
    dim_v(d, x0 + 350, top_y - 95, top_y, x0 + 290, "95")
    dim_v(d, x0 + 350, top_y - 95 - 237.5, top_y - 95, x0 + 290, "237.5")
    dim_v(d, x0 + 350, top_y - 95 - 237.5 - 95, top_y - 95 - 237.5, x0 + 290, "95")

    # A-A cut line and marks.
    d.text("A", x0 + 80, top_y - 165, 28, "TEXT")
    d.text("A", bx + 70, y0 + 275, 28, "TEXT")
    d.line(x0 + 100, top_y - 175, bx + 70, y0 + 300, "CUT", "DASHED")

    # Leaders.
    leader(d, bx - 12, y0 + 640, bx + 220, y0 + 785, "箱臂", 22, 0)
    leader(d, bx - 20, y0 + 85, bx + 210, y0 + 230, "箱底", 22, 0)


def draw_aa_plan(d):
    # Right A-A plan from the same reference photo.
    px, py = 2130, 265
    s = 0.72
    outer_l, outer_w = 1245 * s, 1100 * s
    wall = 85 * s
    mid_w = 85 * s
    d.text("A-A", px + 350, py - 95, 22, "TEXT")
    d.rect(px, py, outer_l, outer_w, "CAISSON")
    d.rect(px + wall, py + wall, outer_l - 2 * wall, outer_w - 2 * wall, "CAISSON")
    concrete(d, px, py, outer_l, wall, 24)
    concrete(d, px, py + outer_w - wall, outer_l, wall, 24)
    concrete(d, px, py, wall, outer_w, 24)
    concrete(d, px + outer_l - wall, py, wall, outer_w, 24)

    # 3 columns x 2 rows, visually matching the photo.
    col_w = 367 * s
    x1 = px + wall + col_w
    x2 = x1 + mid_w + col_w
    d.rect(x1, py + wall, mid_w, outer_w - 2 * wall, "CAISSON")
    d.rect(x2, py + wall, mid_w, outer_w - 2 * wall, "CAISSON")
    d.rect(px + wall, py + outer_w / 2 - mid_w / 2, outer_l - 2 * wall, mid_w, "CAISSON")
    concrete(d, x1, py + wall, mid_w, outer_w - 2 * wall, 22)
    concrete(d, x2, py + wall, mid_w, outer_w - 2 * wall, 22)
    concrete(d, px + wall, py + outer_w / 2 - mid_w / 2, outer_l - 2 * wall, mid_w, 22)
    for cx in [px + wall + col_w / 2, px + wall + col_w + mid_w + col_w / 2, px + outer_l - wall - col_w / 2]:
        d.line(cx - 30, py + wall, cx - 30, py + outer_w - wall, "CENTER")
        d.line(cx + 30, py + wall, cx + 30, py + outer_w - wall, "CENTER")

    # Dimensions exactly near the plan.
    dim_h(d, px, px + outer_l, py, py - 90, "1245")
    dim_v(d, px, py, py + outer_w, px - 110, "1100")
    dim_v(d, px + wall, py + wall, py + outer_w - wall, px - 50, "930")
    d.dim_rotated((px + wall, py + 570 * s, 0), (px + wall + 367 * s, py + 570 * s, 0), (px + wall + 183.5 * s, py + 505 * s, 0), 0, "367")
    d.dim_rotated((px + wall + 452 * s, py + 570 * s, 0), (px + wall + 879.5 * s, py + 570 * s, 0), (px + wall + 665.75 * s, py + 505 * s, 0), 0, "427.5")
    d.dim_rotated((px, py + outer_w, 0), (px + wall, py + outer_w, 0), (px + 42.5 * s, py + outer_w + 54, 0), 0, "85")
    d.dim_rotated((px + outer_l - wall, py + outer_w, 0), (px + outer_l, py + outer_w, 0), (px + outer_l - 42.5 * s, py + outer_w + 54, 0), 0, "85")


def draw_sheet():
    os.makedirs(OUT_DIR, exist_ok=True)
    acad = AcadSession()
    d = acad.new_drawing(dimtxt=22, precision=0)
    monochrome_layers(d)
    draw_main_section(d)
    draw_aa_plan(d)
    try:
        com_call(d.doc.Application.ZoomExtents)
    except Exception:
        pass
    path = os.path.join(OUT_DIR, "S-02_caisson_section_AA_plan_reference_exact_v4.dwg")
    count = d.save(path)
    d.close()
    zip_path = os.path.join(OUT_DIR, "caisson_reference_exact_only.zip")
    if os.path.exists(zip_path):
        os.remove(zip_path)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(path, arcname=os.path.basename(path))
    return path, zip_path, count


def main():
    path, zip_path, count = draw_sheet()
    print("DONE")
    print(f"{path} | ModelSpace entities: {count}")
    print(f"ZIP: {zip_path}")


if __name__ == "__main__":
    main()
