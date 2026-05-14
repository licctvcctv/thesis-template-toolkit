from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "images"
FONT_REGULAR = "/System/Library/Fonts/STHeiti Light.ttc"
FONT_BOLD = "/System/Library/Fonts/STHeiti Medium.ttc"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size=size)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for ch in text:
        trial = current + ch
        if text_size(draw, trial, fnt)[0] <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return lines


def centered_text(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    fnt: ImageFont.FreeTypeFont,
    *,
    fill: str = "black",
    max_width_pad: int = 24,
    line_gap: int = 8,
) -> None:
    x1, y1, x2, y2 = box
    lines = []
    for raw in text.split("\n"):
        lines.extend(wrap_text(draw, raw, fnt, max(20, x2 - x1 - max_width_pad)))
    heights = [text_size(draw, line, fnt)[1] for line in lines]
    total_h = sum(heights) + line_gap * max(0, len(lines) - 1)
    y = y1 + (y2 - y1 - total_h) / 2
    for line, h in zip(lines, heights):
        w, _ = text_size(draw, line, fnt)
        draw.text((x1 + (x2 - x1 - w) / 2, y), line, font=fnt, fill=fill)
        y += h + line_gap


def canvas(width: int, height: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (width, height), "white")
    return img, ImageDraw.Draw(img)


def save(img: Image.Image, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / name, "PNG", dpi=(300, 300))


def line(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], width: int = 4) -> None:
    draw.line([start, end], fill="black", width=width)


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], width: int = 4) -> None:
    draw.line([start, end], fill="black", width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    length = 18
    spread = math.radians(24)
    p1 = (end[0] - length * math.cos(angle - spread), end[1] - length * math.sin(angle - spread))
    p2 = (end[0] - length * math.cos(angle + spread), end[1] - length * math.sin(angle + spread))
    draw.polygon([end, p1, p2], fill="black")


def rect(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, fnt=None, width: int = 4) -> None:
    draw.rectangle(box, outline="black", width=width)
    centered_text(draw, box, text, fnt or font(34))


def ellipse(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, fnt=None, width: int = 4) -> None:
    draw.ellipse(box, outline="black", width=width)
    centered_text(draw, box, text, fnt or font(34))


def diamond(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, fnt=None, width: int = 4) -> None:
    x1, y1, x2, y2 = box
    pts = [(int((x1 + x2) / 2), y1), (x2, int((y1 + y2) / 2)), (int((x1 + x2) / 2), y2), (x1, int((y1 + y2) / 2))]
    draw.line(pts + [pts[0]], fill="black", width=width)
    centered_text(draw, box, text, fnt or font(30), max_width_pad=70)


def stick_actor(draw: ImageDraw.ImageDraw, x: int, y: int, label: str) -> tuple[int, int]:
    draw.ellipse((x - 30, y, x + 30, y + 60), outline="black", width=4)
    line(draw, (x, y + 60), (x, y + 185), 4)
    line(draw, (x - 80, y + 100), (x + 80, y + 100), 4)
    line(draw, (x, y + 185), (x - 70, y + 285), 4)
    line(draw, (x, y + 185), (x + 70, y + 285), 4)
    centered_text(draw, (x - 120, y + 300, x + 120, y + 360), label, font(34, True))
    return x, y + 100


def draw_usecase_oval(draw: ImageDraw.ImageDraw, center: tuple[int, int], text: str, w: int = 330, h: int = 92) -> tuple[int, int, int, int]:
    x, y = center
    box = (x - w // 2, y - h // 2, x + w // 2, y + h // 2)
    ellipse(draw, box, text, font(32), 4)
    return box


def connect_actor_to_box(draw: ImageDraw.ImageDraw, actor_pt: tuple[int, int], box: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = box
    target = (x1, int((y1 + y2) / 2)) if actor_pt[0] < x1 else (x2, int((y1 + y2) / 2))
    line(draw, actor_pt, target, 3)


def user_use_case() -> None:
    img, draw = canvas(1600, 1000)
    draw.rectangle((300, 80, 1330, 860), outline="black", width=4)
    centered_text(draw, (560, 90, 1070, 150), "用户端预约与药品用例图", font(42, True))
    actor = stick_actor(draw, 150, 300, "用户")
    centers = [
        (560, 230, "注册登录"),
        (560, 350, "浏览公告"),
        (560, 470, "浏览医师科室"),
        (560, 590, "预约挂号"),
        (560, 710, "查看预约结果"),
        (1030, 290, "浏览药品"),
        (1030, 430, "药品下单"),
        (1030, 570, "个人信息维护"),
    ]
    boxes = [draw_usecase_oval(draw, (x, y), text) for x, y, text in centers]
    for box in boxes:
        connect_actor_to_box(draw, actor, box)
    save(img, "fig3_3_user_use_case_imagegen_bw.png")


def doctor_admin_use_case() -> None:
    img, draw = canvas(1700, 1000)
    draw.rectangle((300, 80, 1390, 860), outline="black", width=4)
    centered_text(draw, (560, 90, 1150, 150), "医师端与后台维护用例图", font(42, True))
    doctor = stick_actor(draw, 140, 210, "医师")
    admin = stick_actor(draw, 1560, 255, "后台维护端")
    doctor_boxes = [
        draw_usecase_oval(draw, (660, 240), "查看个人信息"),
        draw_usecase_oval(draw, (660, 380), "查看预约记录"),
        draw_usecase_oval(draw, (660, 520), "处理预约状态"),
    ]
    admin_boxes = [
        draw_usecase_oval(draw, (1060, 230), "维护用户信息"),
        draw_usecase_oval(draw, (1060, 350), "维护医师科室"),
        draw_usecase_oval(draw, (1060, 470), "管理挂号记录"),
        draw_usecase_oval(draw, (1060, 590), "管理药品订单"),
        draw_usecase_oval(draw, (1060, 710), "发布公告信息"),
    ]
    for box in doctor_boxes:
        connect_actor_to_box(draw, doctor, box)
    for box in admin_boxes:
        connect_actor_to_box(draw, admin, box)
    save(img, "fig3_4_doctor_admin_use_case_imagegen_bw.png")


def sequence_positions(count: int) -> list[int]:
    presets = {
        5: [170, 550, 950, 1350, 1730],
        6: [170, 470, 800, 1120, 1450, 1730],
    }
    if count in presets:
        return presets[count]
    if count <= 1:
        return [950]
    left, right = 170, 1730
    step = (right - left) / (count - 1)
    return [int(left + i * step) for i in range(count)]


def draw_sequence_diagram(
    title: str,
    labels: list[str],
    messages: list[tuple[int, int, int, str]],
    filename: str,
) -> None:
    img, draw = canvas(1900, 1120)
    centered_text(draw, (0, 30, 1900, 95), title, font(44, True))
    xs = sequence_positions(len(labels))
    top, bottom = 160, 1030
    for x, label in zip(xs, labels):
        rect(draw, (x - 105, top - 55, x + 105, top + 10), label, font(28), 3)
        draw.line([(x, top + 10), (x, bottom)], fill="black", width=3)
        for y in range(top + 25, bottom, 28):
            draw.line([(x, y), (x, y + 12)], fill="white", width=4)
    for a, b, y, text in messages:
        start = (xs[a], y)
        end = (xs[b], y)
        arrow(draw, start, end, 3)
        mid_x = (start[0] + end[0]) // 2
        label_box = (mid_x - 160, y - 45, mid_x + 160, y - 8)
        centered_text(draw, label_box, text, font(24))
    save(img, filename)


def sequence_diagrams() -> None:
    draw_sequence_diagram(
        "预约挂号业务时序图",
        ["用户", "前台页面", "预约控制器", "预约服务", "MySQL数据库", "医师端"],
        [
            (0, 1, 235, "选择科室与医师"),
            (1, 2, 315, "提交预约申请"),
            (2, 3, 395, "校验用户、医师和时间"),
            (3, 4, 475, "查询医师与号源状态"),
            (4, 3, 555, "返回可预约结果"),
            (3, 4, 635, "保存预约挂号记录"),
            (4, 3, 715, "返回预约编号"),
            (3, 2, 795, "返回处理结果"),
            (2, 1, 875, "提示预约成功"),
            (5, 4, 955, "查询个人预约列表"),
            (4, 5, 1020, "返回预约记录"),
        ],
        "fig3_5_appointment_sequence_imagegen_bw_v2.png",
    )
    draw_sequence_diagram(
        "医师端预约处理时序图",
        ["医师", "医师端页面", "预约控制器", "预约服务", "MySQL数据库"],
        [
            (0, 1, 240, "登录并进入预约管理"),
            (1, 2, 320, "查询预约列表"),
            (2, 3, 400, "按医师编号筛选"),
            (3, 4, 480, "读取预约记录"),
            (4, 3, 560, "返回预约列表"),
            (3, 1, 640, "展示预约列表"),
            (0, 1, 720, "更新预约状态"),
            (1, 2, 800, "保存处理结果"),
            (2, 3, 880, "更新预约状态"),
            (3, 4, 960, "写入状态变更"),
            (4, 3, 1020, "返回更新结果"),
            (3, 1, 1070, "返回处理成功"),
        ],
        "fig3_6_doctor_appointment_sequence_imagegen_bw.png",
    )
    draw_sequence_diagram(
        "药品订单生成时序图",
        ["用户", "药品详情页", "订单控制器", "订单服务", "MySQL数据库"],
        [
            (0, 1, 235, "浏览药品信息"),
            (1, 2, 315, "提交下单请求"),
            (2, 3, 395, "校验用户与库存"),
            (3, 4, 475, "查询库存与用户信息"),
            (4, 3, 555, "返回可下单结果"),
            (3, 4, 635, "保存订单记录并扣减库存"),
            (4, 3, 715, "返回订单编号"),
            (3, 1, 795, "返回下单成功"),
            (1, 0, 875, "提示订单成功"),
        ],
        "fig3_7_medicine_order_sequence_imagegen_bw.png",
    )


def db_logical_structure() -> None:
    img, draw = canvas(1900, 1160)
    centered_text(draw, (0, 30, 1900, 95), "数据库逻辑结构总体图", font(44, True))

    def table_box(x: int, y: int, title: str, rows: list[str]) -> tuple[int, int, int, int]:
        w, row_h = 370, 44
        h = 74 + row_h * len(rows)
        draw.rectangle((x, y, x + w, y + h), outline="black", width=4)
        draw.rectangle((x, y, x + w, y + 64), outline="black", width=4)
        centered_text(draw, (x, y + 8, x + w, y + 58), title, font(28, True), max_width_pad=10)
        for i, row in enumerate(rows):
            yy = y + 64 + i * row_h
            draw.line([(x, yy), (x + w, yy)], fill="black", width=2)
            centered_text(draw, (x + 10, yy + 5, x + w - 10, yy + row_h - 3), row, font(24), max_width_pad=12)
        return (x, y, x + w, y + h)

    user = table_box(100, 160, "user 用户表", ["id PK", "username", "real_name", "phone"])
    dept = table_box(760, 150, "department 科室表", ["id PK", "department_name", "description"])
    doctor = table_box(760, 470, "doctor 医师表", ["id PK", "department_id FK", "doctor_name", "title", "register_fee"])
    appoint = table_box(1260, 380, "appointment 挂号表", ["id PK", "user_id FK", "doctor_id FK", "appointment_time", "status"])
    med = table_box(100, 700, "medicine 药品表", ["id PK", "medicine_name", "price", "stock"])
    order = table_box(560, 790, "medicine_order 订单表", ["id PK", "user_id FK", "medicine_id FK", "order_time", "status"])
    news = table_box(1260, 780, "news 公告表", ["id PK", "title", "content", "publish_time"])

    def right_mid(box):
        return box[2], (box[1] + box[3]) // 2

    def left_mid(box):
        return box[0], (box[1] + box[3]) // 2

    def bottom_mid(box):
        return (box[0] + box[2]) // 2, box[3]

    def top_mid(box):
        return (box[0] + box[2]) // 2, box[1]

    arrow(draw, right_mid(user), left_mid(appoint), 3)
    centered_text(draw, (700, 255, 820, 305), "1:N", font(24, True))
    arrow(draw, right_mid(doctor), left_mid(appoint), 3)
    centered_text(draw, (1080, 500, 1180, 550), "1:N", font(24, True))
    arrow(draw, bottom_mid(dept), top_mid(doctor), 3)
    centered_text(draw, (865, 365, 965, 410), "1:N", font(24, True))
    arrow(draw, right_mid(user), left_mid(order), 3)
    centered_text(draw, (455, 650, 545, 700), "1:N", font(24, True))
    arrow(draw, right_mid(med), left_mid(order), 3)
    centered_text(draw, (455, 850, 545, 900), "1:N", font(24, True))
    save(img, "fig4_11_database_logical_structure_imagegen_bw.png")


def flowchart(name: str, title: str, steps: list[tuple[str, str]], filename: str) -> None:
    img, draw = canvas(1100, 1700)
    centered_text(draw, (0, 30, 1100, 95), title, font(42, True))
    x = 550
    y = 145
    prev_bottom: tuple[int, int] | None = None
    for shape, text in steps:
        if shape == "start":
            box = (x - 150, y, x + 150, y + 80)
            ellipse(draw, box, text, font(30), 4)
            y += 135
        elif shape == "process":
            box = (x - 230, y, x + 230, y + 90)
            rect(draw, box, text, font(30), 4)
            y += 145
        elif shape == "decision":
            box = (x - 230, y - 20, x + 230, y + 130)
            diamond(draw, box, text, font(28), 4)
            y += 195
        elif shape == "end":
            box = (x - 150, y, x + 150, y + 80)
            ellipse(draw, box, text, font(30), 4)
            y += 130
        else:
            raise ValueError(shape)
        top = ((box[0] + box[2]) // 2, box[1])
        if prev_bottom is not None:
            arrow(draw, prev_bottom, top, 4)
        prev_bottom = ((box[0] + box[2]) // 2, box[3])
    save(img, filename)


def flowcharts() -> None:
    flowchart(
        "appointment",
        "预约挂号处理流程图",
        [
            ("start", "开始"),
            ("process", "浏览科室与医师"),
            ("process", "选择预约时间"),
            ("process", "提交预约信息"),
            ("decision", "信息是否完整"),
            ("process", "校验医师号源"),
            ("decision", "时间是否可约"),
            ("process", "生成预约记录"),
            ("process", "返回预约结果"),
            ("end", "结束"),
        ],
        "fig5_15_appointment_flowchart_imagegen_bw.png",
    )
    flowchart(
        "doctor",
        "医师端预约处理流程图",
        [
            ("start", "开始"),
            ("process", "医师登录系统"),
            ("process", "进入预约管理"),
            ("process", "查询本人预约列表"),
            ("decision", "是否需要处理"),
            ("process", "更新预约状态"),
            ("process", "保存处理结果"),
            ("process", "用户查看结果"),
            ("end", "结束"),
        ],
        "fig5_16_doctor_appointment_flowchart_imagegen_bw.png",
    )
    flowchart(
        "medicine",
        "药品订单生成流程图",
        [
            ("start", "开始"),
            ("process", "浏览药品信息"),
            ("process", "进入药品详情"),
            ("process", "提交订单请求"),
            ("decision", "库存是否满足"),
            ("process", "生成订单记录"),
            ("process", "保存订单状态"),
            ("process", "返回下单结果"),
            ("end", "结束"),
        ],
        "fig5_17_medicine_order_flowchart_imagegen_bw.png",
    )


def main() -> None:
    user_use_case()
    doctor_admin_use_case()
    sequence_diagrams()
    db_logical_structure()
    flowcharts()


if __name__ == "__main__":
    main()
