from __future__ import annotations

import subprocess
from pathlib import Path
from xml.sax.saxutils import escape


PAPER_DIR = Path(__file__).resolve().parents[1]
OUT = PAPER_DIR / "images" / "diagrams"


def svg_start(width: int, height: int) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<defs>",
        '<marker id="arrow" viewBox="0 0 14 10" refX="10" refY="5" markerWidth="14" markerHeight="10" orient="auto" markerUnits="strokeWidth">',
        '<path d="M 0 0 L 14 5 L 0 10 Z" fill="#323232" stroke="#323232" stroke-width="1"/>',
        "</marker>",
        "</defs>",
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff"/>',
    ]


def rect(x: int, y: int, w: int, h: int, fill: str = "#ffffff", stroke: str = "#212930", sw: float = 2.0) -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def round_rect(x: int, y: int, w: int, h: int, fill: str = "#ffffff", stroke: str = "#212930", sw: float = 2.0, rx: int = 10) -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def diamond(cx: int, cy: int, w: int, h: int, fill: str = "#ffffff") -> str:
    pts = f"{cx},{cy-h//2} {cx+w//2},{cy} {cx},{cy+h//2} {cx-w//2},{cy}"
    return f'<polygon points="{pts}" fill="{fill}" stroke="#212930" stroke-width="2"/>'


def ellipse(cx: int, cy: int, rx: int, ry: int, fill: str = "#ffffff", sw: float = 2.0) -> str:
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="#212930" stroke-width="{sw}"/>'


def cylinder(x: int, y: int, w: int, h: int, fill: str = "#ffffff") -> str:
    return (
        f'<path d="M{x},{y+18} C{x},{y-6} {x+w},{y-6} {x+w},{y+18} '
        f'L{x+w},{y+h-18} C{x+w},{y+h+6} {x},{y+h+6} {x},{y+h-18} Z" '
        f'fill="{fill}" stroke="#212930" stroke-width="2"/>'
        f'<ellipse cx="{x+w/2}" cy="{y+18}" rx="{w/2}" ry="18" fill="{fill}" stroke="#212930" stroke-width="2"/>'
    )


def text_center(x: int, y: int, w: int, h: int, text: str, size: int = 24, bold: bool = True) -> str:
    weight = "700" if bold else "400"
    return (
        f'<text x="{x + w / 2}" y="{y + h / 2 + size * 0.36}" text-anchor="middle" '
        f'font-family="Microsoft YaHei, SimHei, Arial" font-size="{size}" font-weight="{weight}" fill="#323232">'
        f"{escape(text)}</text>"
    )


def multiline_center(x: int, y: int, w: int, h: int, lines: list[str], size: int = 22, bold: bool = False) -> str:
    weight = "700" if bold else "400"
    line_h = size * 1.32
    start = y + h / 2 - (len(lines) - 1) * line_h / 2 + size * 0.36
    chunks = [
        f'<text x="{x+w/2}" y="{start}" text-anchor="middle" '
        f'font-family="Microsoft YaHei, SimSun, Arial" font-size="{size}" font-weight="{weight}" fill="#323232">'
    ]
    for idx, line in enumerate(lines):
        dy = 0 if idx == 0 else line_h
        chunks.append(f'<tspan x="{x+w/2}" dy="{dy}">{escape(line)}</tspan>')
    chunks.append("</text>")
    return "".join(chunks)


def label(x: int, y: int, text: str, size: int = 18, bold: bool = False, anchor: str = "start") -> str:
    weight = "700" if bold else "400"
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Microsoft YaHei, SimSun, Arial" '
        f'font-size="{size}" font-weight="{weight}" fill="#323232">{escape(text)}</text>'
    )


def text(cx: int, cy: int, value: str, size: int = 20, bold: bool = False, anchor: str = "middle") -> str:
    weight = "700" if bold else "400"
    return (
        f'<text x="{cx}" y="{cy + size * 0.36}" text-anchor="{anchor}" '
        f'font-family="Microsoft YaHei, SimSun, Arial" font-size="{size}" font-weight="{weight}" fill="#323232">'
        f"{escape(value)}</text>"
    )


def vertical_text(x: int, y: int, w: int, h: int, text: str, size: int = 23) -> str:
    tokens: list[str] = []
    i = 0
    while i < len(text):
        if text.startswith("AI", i):
            tokens.append("AI")
            i += 2
        elif text.startswith("API", i):
            tokens.extend(["A", "P", "I"])
            i += 3
        elif text.startswith("JWT", i):
            tokens.extend(["J", "W", "T"])
            i += 3
        else:
            tokens.append(text[i])
            i += 1
    line_h = size * 1.18
    start_y = y + (h - line_h * len(tokens)) / 2 + size * 0.75
    cx = x + w / 2
    chunks = [
        f'<text x="{cx}" y="{start_y}" text-anchor="middle" font-family="Microsoft YaHei, SimHei, Arial" '
        f'font-size="{size}" font-weight="700" fill="#323232">'
    ]
    for idx, token in enumerate(tokens):
        chunks.append(f'<tspan x="{cx}" dy="{0 if idx == 0 else line_h}">{escape(token)}</tspan>')
    chunks.append("</text>")
    return "".join(chunks)


def line(x1: int, y1: int, x2: int, y2: int, arrow: bool = False, dashed: bool = False, sw: float = 2.0) -> str:
    marker = ' marker-end="url(#arrow)"' if arrow else ""
    dash = ' stroke-dasharray="10,6"' if dashed else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#323232" stroke-width="{sw}" fill="none"{dash}{marker}/>'


def polyline(points: list[tuple[int, int]], arrow: bool = False, dashed: bool = False, sw: float = 2.0) -> str:
    pts = " ".join(f"{x},{y}" for x, y in points)
    marker = ' marker-end="url(#arrow)"' if arrow else ""
    dash = ' stroke-dasharray="10,6"' if dashed else ""
    return f'<polyline points="{pts}" stroke="#323232" stroke-width="{sw}" fill="none"{dash}{marker}/>'


def save_svg(name: str, parts: list[str], width: int, height: int) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{name}.svg"
    path.write_text("\n".join(svg_start(width, height) + parts + ["</svg>"]), encoding="utf-8")
    return path


def render_svg(svg: Path, out_width: int = 2500) -> Path:
    png = svg.with_suffix(".png")
    subprocess.run(["rsvg-convert", "-w", str(out_width), "-o", str(png), str(svg)], check=True)
    return png


def module_architecture() -> Path:
    width, height = 2500, 739
    parts: list[str] = []
    top = (850, 30, 800, 72)
    app = (360, 196, 410, 70)
    admin = (1035, 196, 410, 70)
    server = (1720, 196, 410, 70)
    parts += [rect(*top), text_center(*top, "基于Android的英语词汇复习系统", 28)]
    for box, text in ((app, "Android App端"), (admin, "Web管理端"), (server, "Spring Boot服务端")):
        parts += [rect(*box), text_center(*box, text, 28)]
    parts.append(line(top[0] + top[2] // 2, top[1] + top[3], top[0] + top[2] // 2, 148))
    for box in (app, admin, server):
        parts.append(polyline([(top[0] + top[2] // 2, 148), (box[0] + box[2] // 2, 148), (box[0] + box[2] // 2, box[1] - 7)], arrow=True))

    module_groups = [
        (60, ["登录注册模块", "资料完善模块", "词库导入模块", "每日计划模块", "单词学习模块", "AI例句模块", "拼写挑战模块", "统计排行模块"]),
        (945, ["管理员登录", "排行榜查看", "个人中心", "Token存储", "路由守卫"]),
        (1610, ["认证鉴权模块", "用户资料模块", "计划同步模块", "学习统计模块", "AI生成模块", "排行榜接口", "后台接口", "数据持久化"]),
    ]
    y, box_w, box_h = 350, 64, 340
    for x0, labels in module_groups:
        xs = [x0 + i * 88 for i in range(len(labels))]
        parts.append(line(xs[0] + box_w // 2, 306, xs[-1] + box_w // 2, 306))
        for x, text in zip(xs, labels):
            parts.append(polyline([(x + box_w // 2, 306), (x + box_w // 2, y - 8)], arrow=True))
            parts += [rect(x, y, box_w, box_h), vertical_text(x, y, box_w, box_h, text)]
    return render_svg(save_svg("fig2_1_module_architecture", parts, width, height))


def system_architecture() -> Path:
    width, height = 1800, 980
    parts: list[str] = []
    parts += [rect(650, 35, 500, 64), text_center(650, 35, 500, 64, "系统总体架构", 28)]
    parts += [round_rect(70, 175, 360, 130), multiline_center(70, 175, 360, 130, ["Android App", "原生页面 / Room / OkHttp"], 24, True)]
    parts += [round_rect(70, 520, 360, 115), multiline_center(70, 520, 360, 115, ["Vue管理端", "登录 / 排行榜 / 个人中心"], 22, True)]
    parts += [round_rect(630, 170, 500, 110), multiline_center(630, 170, 500, 110, ["REST接口层", "App接口 / 后台接口"], 23, True)]
    parts += [round_rect(630, 330, 500, 110), multiline_center(630, 330, 500, 110, ["安全控制层", "JWT鉴权过滤器"], 23, True)]
    parts += [round_rect(630, 490, 500, 110), multiline_center(630, 490, 500, 110, ["业务服务层", "用户服务 / AI服务"], 23, True)]
    parts += [round_rect(630, 650, 500, 110), multiline_center(630, 650, 500, 110, ["数据访问层", "JPA仓库 / Room DAO"], 23, True)]
    parts += [cylinder(1360, 175, 300, 145), multiline_center(1360, 175, 300, 145, ["MySQL", "users表"], 23, True)]
    parts += [cylinder(1360, 430, 300, 145), multiline_center(1360, 430, 300, 145, ["本地Room", "词库与每日计划"], 23, True)]
    parts += [round_rect(1340, 690, 340, 120), multiline_center(1340, 690, 340, 120, ["百度千帆", "例句与短文生成"], 23, True)]
    parts.append(polyline([(430, 240), (630, 225)], arrow=True))
    parts.append(polyline([(430, 575), (630, 225)], arrow=True))
    parts.append(polyline([(880, 280), (880, 330)], arrow=True))
    parts.append(polyline([(880, 440), (880, 490)], arrow=True))
    parts.append(polyline([(880, 600), (880, 650)], arrow=True))
    parts.append(polyline([(1130, 705), (1360, 250)], arrow=True))
    parts.append(polyline([(430, 265), (1360, 500)], arrow=True, dashed=True))
    parts.append(polyline([(1130, 545), (1340, 750)], arrow=True, dashed=True))
    parts += [label(485, 220, "HTTPS/JSON", 18), label(1160, 230, "JPA访问", 18), label(1165, 505, "离线学习数据", 18), label(1162, 725, "AI请求", 18)]
    return render_svg(save_svg("fig4_1_system_architecture", parts, width, height), 2200)


def login_flow() -> Path:
    width, height = 1050, 1250
    parts: list[str] = []
    parts += [round_rect(450, 35, 150, 54, "#ffffff"), text_center(450, 35, 150, 54, "开始", 20)]
    steps = [
        ("打开App登录页", "process"),
        ("已有账号？", "decision"),
        ("输入用户名与密码", "process"),
        ("提交登录接口", "process"),
        ("注册并返回Token", "process"),
        ("资料是否完整？", "decision"),
        ("进入资料完善页", "process"),
        ("选择年龄、水平、词库", "process"),
        ("进入主界面", "process"),
        ("结束", "end"),
    ]
    y = 130
    last_mid = (525, 89)
    coords: list[tuple[int, int, int, int, str]] = []
    for text, kind in steps:
        if kind == "decision":
            parts += [diamond(525, y + 45, 260, 90), text_center(395, y, 260, 90, text, 20)]
            coords.append((395, y, 260, 90, kind))
        else:
            w, h = (310, 62)
            x = 370
            parts += [round_rect(x, y, w, h), text_center(x, y, w, h, text, 20)]
            coords.append((x, y, w, h, kind))
        parts.append(line(last_mid[0], last_mid[1], 525, y - 5, arrow=True))
        last_mid = (525, y + (90 if kind == "decision" else 62))
        y += 120 if kind != "decision" else 140
    parts.append(polyline([(655, 295), (850, 295), (850, 490), (680, 490)], arrow=True))
    parts += [label(710, 282, "否", 20, True), label(535, 402, "是", 20, True)]
    parts.append(polyline([(655, 775), (850, 775), (850, 1035), (680, 1035)], arrow=True))
    parts += [label(710, 762, "是", 20, True), label(535, 900, "否", 20, True)]
    return render_svg(save_svg("fig4_2_login_profile_flow", parts, width, height), 1500)


def daily_learning_flow() -> Path:
    width, height = 1500, 1160
    parts: list[str] = []
    boxes = [
        (585, 35, 330, 62, "开始学习页"),
        (585, 145, 330, 70, "读取本地资料与Token"),
        (585, 265, 330, 70, "导入/补全本地词库"),
        (585, 385, 330, 70, "查询今日计划"),
        (585, 505, 330, 70, "抽取新词与到期复习词"),
        (585, 625, 330, 70, "展示单词卡片"),
        (180, 760, 330, 70, "生成AI例句/短文"),
        (585, 760, 330, 70, "用户选择简单/困难"),
        (990, 760, 330, 70, "拼写复习挑战"),
        (585, 900, 330, 70, "更新Room学习进度"),
        (585, 1020, 330, 70, "同步服务端统计"),
    ]
    for x, y, w, h, text in boxes:
        parts += [round_rect(x, y, w, h), text_center(x, y, w, h, text, 21)]
    for i in range(5):
        x, y, w, h, _ = boxes[i]
        nx, ny, _, _, _ = boxes[i + 1]
        parts.append(line(x + w // 2, y + h, nx + w // 2, ny - 6, arrow=True))
    parts.append(polyline([(750, 695), (345, 695), (345, 754)], arrow=True))
    parts.append(line(750, 695, 750, 754, arrow=True))
    parts.append(polyline([(750, 695), (1155, 695), (1155, 754)], arrow=True))
    parts.append(polyline([(345, 830), (345, 935), (585, 935)], arrow=True))
    parts.append(line(750, 830, 750, 894, arrow=True))
    parts.append(polyline([(1155, 830), (1155, 935), (915, 935)], arrow=True))
    parts.append(line(750, 970, 750, 1014, arrow=True))
    return render_svg(save_svg("fig4_3_daily_learning_flow", parts, width, height), 1900)


def use_case_diagram() -> Path:
    width, height = 1700, 1050
    parts: list[str] = []
    parts += [rect(405, 70, 890, 835), label(430, 118, "乐背英语词汇复习系统", 26, True)]
    parts += [ellipse(170, 210, 34, 34), line(170, 244, 170, 330), line(125, 278, 215, 278), line(170, 330, 130, 405), line(170, 330, 210, 405)]
    parts += [text(170, 455, "App用户", 22, True)]
    parts += [ellipse(1530, 260, 34, 34), line(1530, 294, 1530, 380), line(1485, 328, 1575, 328), line(1530, 380, 1490, 455), line(1530, 380, 1570, 455)]
    parts += [text(1530, 505, "管理员", 22, True)]
    app_cases = [
        (660, 165, "注册/登录"),
        (995, 165, "完善资料"),
        (660, 305, "设置学习计划"),
        (995, 305, "导入本地词库"),
        (660, 445, "单词学习"),
        (995, 445, "AI例句与短文"),
        (660, 585, "拼写挑战"),
        (995, 585, "统计与排行"),
    ]
    admin_cases = [
        (995, 735, "后台登录"),
        (660, 735, "查看排行榜"),
        (830, 845, "查看个人信息"),
    ]
    for cx, cy, name in app_cases + admin_cases:
        parts += [ellipse(cx, cy, 135, 42), text(cx, cy, name, 21)]
    for cx, cy, _ in app_cases:
        parts.append(line(220, 300, cx - 135, cy, dashed=True))
    for cx, cy, _ in admin_cases:
        parts.append(line(1480, 360, cx + 135, cy, dashed=True))
    parts += [label(470, 945, "说明：App用户以移动端学习流程为主，管理员通过Web端查看统计结果。", 22)]
    return render_svg(save_svg("fig3_1_use_case", parts, width, height), 2100)


def requirement_structure() -> Path:
    width, height = 1600, 980
    parts: list[str] = []
    root = (540, 45, 520, 64)
    parts += [rect(*root), text_center(*root, "系统功能需求结构", 27)]
    columns = [
        (70, "账号与资料", ["注册登录", "Token保存", "资料完善", "多账号隔离"]),
        (420, "学习计划", ["词库选择", "每日新词", "到期复习", "计划稳定生成"]),
        (770, "学习复习", ["单词卡片", "简单/困难", "复习权重", "拼写挑战"]),
        (1120, "统计与管理", ["本地统计", "服务端同步", "排行榜", "后台查看"]),
    ]
    for x, title, items in columns:
        head = (x, 190, 300, 62)
        parts += [rect(*head, fill="#f3f5f7"), text_center(*head, title, 23)]
        parts.append(polyline([(800, 109), (800, 145), (x + 150, 145), (x + 150, 184)], arrow=True))
        for idx, item in enumerate(items):
            y = 320 + idx * 118
            parts += [round_rect(x + 25, y, 250, 58), text_center(x + 25, y, 250, 58, item, 20, False)]
            if idx == 0:
                parts.append(line(x + 150, 252, x + 150, y - 6, arrow=True))
            else:
                parts.append(line(x + 150, y - 60, x + 150, y - 6, arrow=True))
    parts += [rect(260, 835, 1080, 60), text_center(260, 835, 1080, 60, "非功能需求：安全鉴权、离线可用、异常提示、模块可维护、接口响应稳定", 22, False)]
    return render_svg(save_svg("fig3_2_requirement_structure", parts, width, height), 2000)


def database_model() -> Path:
    width, height = 1800, 1180
    parts: list[str] = []

    def entity(cx: int, cy: int, name: str, w: int = 210, h: int = 78) -> tuple[int, int, int, int]:
        x, y = cx - w // 2, cy - h // 2
        parts.extend([rect(x, y, w, h, fill="#ffffff"), text_center(x, y, w, h, name, 24)])
        return x, y, w, h

    def attr(cx: int, cy: int, target: tuple[int, int], name: str, rx: int = 96) -> None:
        parts.append(line(target[0], target[1], cx, cy, sw=1.6))
        parts.extend([ellipse(cx, cy, rx, 34), text(cx, cy, name, 18)])

    user = entity(280, 500, "用户")
    word = entity(1500, 500, "单词")
    plan = entity(880, 205, "每日计划")
    plan_word = entity(880, 800, "计划单词")

    attr(120, 190, (280, 461), "用户ID")
    attr(350, 160, (280, 461), "用户名")
    attr(105, 340, (190, 500), "密码摘要")
    attr(130, 655, (190, 500), "角色")
    attr(330, 840, (280, 539), "学习水平")
    attr(540, 740, (385, 500), "当前词库")
    attr(520, 360, (385, 500), "积分/今日学习")

    attr(720, 80, (775, 205), "计划ID")
    attr(915, 80, (880, 166), "日期")
    attr(1085, 115, (985, 205), "词库ID")
    attr(1120, 280, (985, 205), "目标数量")
    attr(690, 300, (775, 205), "AI短文")

    attr(680, 640, (775, 800), "明细ID")
    attr(620, 840, (775, 800), "排序")
    attr(715, 1020, (775, 800), "AI例句")
    attr(1015, 1020, (985, 800), "完成状态")

    attr(1320, 190, (1500, 461), "单词ID")
    attr(1540, 160, (1500, 461), "英文单词")
    attr(1685, 340, (1605, 500), "音标")
    attr(1680, 645, (1605, 500), "中文释义")
    attr(1500, 840, (1500, 539), "熟悉度")
    attr(1280, 735, (1395, 500), "下次复习")
    attr(1270, 360, (1395, 500), "词库/难度")

    parts += [diamond(570, 500, 170, 85), text(570, 500, "配置", 22, True)]
    parts += [line(385, 500, 485, 500), line(655, 500, 775, 242)]
    parts += [label(430, 480, "1", 20, True), label(700, 360, "N", 20, True)]
    parts += [diamond(880, 500, 190, 88), text(880, 500, "包含", 22, True)]
    parts += [line(880, 244, 880, 456), line(880, 544, 880, 761)]
    parts += [label(900, 330, "1", 20, True), label(900, 690, "N", 20, True)]
    parts += [diamond(1190, 800, 180, 88), text(1190, 800, "对应", 22, True)]
    parts += [line(985, 800, 1100, 800), line(1280, 800, 1440, 539)]
    parts += [label(1030, 780, "N", 20, True), label(1350, 650, "1", 20, True)]
    parts += [label(80, 1080, "注：用户实体位于服务端MySQL，单词、每日计划和计划单词位于Android本地Room；“配置”为账号计划与本地计划生成之间的逻辑关系。", 22)]
    return render_svg(save_svg("fig4_4_database_model", parts, width, height), 2300)


def ai_sequence() -> Path:
    width, height = 1700, 980
    parts: list[str] = []
    actors = [
        (165, "学习页"),
        (505, "LebeiApi"),
        (845, "AI控制器"),
        (1185, "AI服务"),
        (1525, "千帆接口"),
    ]
    for x, title in actors:
        parts += [rect(x - 110, 65, 220, 58, fill="#f3f5f7"), text_center(x - 110, 65, 220, 58, title, 22)]
        parts.append(line(x, 123, x, 895, dashed=True, sw=1.6))
    messages = [
        (165, 505, 185, "点击查看AI例句/生成短文"),
        (505, 845, 285, "POST /api/app/ai/example"),
        (845, 1185, 385, "校验Token并取用户资料"),
        (1185, 1525, 485, "构造提示词并调用模型"),
        (1525, 1185, 590, "返回生成文本"),
        (1185, 845, 690, "格式化英文与中文解释"),
        (845, 505, 790, "返回JSON响应"),
        (505, 165, 875, "展示并写入本地Room"),
    ]
    for x1, x2, y, msg in messages:
        parts.append(line(x1, y, x2, y, arrow=True))
        parts.append(label(min(x1, x2) + 18, y - 12, msg, 18))
    return render_svg(save_svg("fig4_5_ai_sequence", parts, width, height), 2100)


def stats_flow() -> Path:
    width, height = 1700, 980
    parts: list[str] = []
    nodes = [
        (90, 155, 330, 92, ["学习行为", "简单/困难、拼写答题"]),
        (90, 435, 330, 92, ["本地Room统计", "已学、掌握、复习次数"]),
        (625, 285, 360, 100, ["Spring Boot统计接口", "study-word / learned-words"]),
        (1200, 155, 330, 92, ["MySQL users表", "积分、今日学习、掌握词"]),
        (1200, 435, 330, 92, ["排行榜接口", "按积分和已学数排序"]),
        (625, 660, 360, 100, ["App与后台展示", "排行榜/统计页/管理端"]),
    ]
    for x, y, w, h, lines_ in nodes:
        parts += [round_rect(x, y, w, h), multiline_center(x, y, w, h, lines_, 22, True)]
    parts.append(line(255, 247, 255, 429, arrow=True))
    parts.append(polyline([(420, 480), (625, 335)], arrow=True))
    parts.append(polyline([(255, 247), (625, 335)], arrow=True))
    parts.append(polyline([(985, 335), (1200, 200)], arrow=True))
    parts.append(line(1365, 247, 1365, 429, arrow=True))
    parts.append(polyline([(1200, 480), (985, 710)], arrow=True))
    parts.append(polyline([(625, 710), (420, 480)], arrow=True, dashed=True))
    parts += [label(430, 300, "同步统计", 19, True), label(1060, 190, "写入/更新", 19, True), label(1070, 590, "查询排行", 19, True), label(410, 640, "统计页读取", 19, True)]
    return render_svg(save_svg("fig4_6_stats_leaderboard_flow", parts, width, height), 2100)


def jwt_auth_flow() -> Path:
    width, height = 1500, 930
    parts: list[str] = []
    boxes = [
        (560, 45, 380, 58, "携带 Bearer Token 请求"),
        (560, 165, 380, 64, "JwtAuthenticationFilter"),
        (560, 285, 380, 64, "解析 token 与用户角色"),
        (560, 405, 380, 64, "写入 SecurityContext"),
        (165, 555, 330, 64, "访问 /api/app/**"),
        (585, 555, 330, 64, "访问 /api/admin/**"),
        (1005, 555, 330, 64, "认证失败或角色不符"),
        (165, 725, 330, 64, "APP_USER 放行"),
        (585, 725, 330, 64, "ADMIN 放行"),
        (1005, 725, 330, 64, "返回 401/403"),
    ]
    for x, y, w, h, title in boxes:
        parts += [round_rect(x, y, w, h), text_center(x, y, w, h, title, 21, True)]
    for i in range(3):
        x, y, w, h, _ = boxes[i]
        nx, ny, _, _, _ = boxes[i + 1]
        parts.append(line(x + w // 2, y + h, nx + w // 2, ny - 6, arrow=True))
    parts.append(polyline([(750, 469), (330, 469), (330, 549)], arrow=True))
    parts.append(polyline([(750, 469), (750, 549)], arrow=True))
    parts.append(polyline([(750, 469), (1170, 469), (1170, 549)], arrow=True))
    parts.append(line(330, 619, 330, 719, arrow=True))
    parts.append(line(750, 619, 750, 719, arrow=True))
    parts.append(line(1170, 619, 1170, 719, arrow=True))
    parts += [label(360, 505, "App接口", 19, True), label(775, 505, "后台接口", 19, True), label(1195, 505, "异常分支", 19, True)]
    return render_svg(save_svg("fig4_7_jwt_auth_flow", parts, width, height), 1900)


def room_data_flow() -> Path:
    width, height = 1650, 980
    parts: list[str] = []
    nodes = [
        (80, 110, 310, 76, "assets CSV词库"),
        (80, 350, 310, 76, "DataProvider导入"),
        (520, 350, 310, 76, "word_table"),
        (520, 595, 310, 76, "DailyWordPicker"),
        (960, 595, 310, 76, "daily_plan"),
        (960, 350, 310, 76, "daily_plan_word"),
        (520, 110, 310, 76, "WordReviewPolicy"),
        (960, 110, 310, 76, "学习页/拼写挑战"),
        (1330, 350, 240, 76, "统计同步"),
    ]
    for x, y, w, h, title in nodes:
        fill = "#f3f5f7" if "table" in title or "daily" in title else "#ffffff"
        parts += [round_rect(x, y, w, h, fill=fill), text_center(x, y, w, h, title, 21, True)]
    parts.append(line(235, 186, 235, 344, arrow=True))
    parts.append(line(390, 388, 514, 388, arrow=True))
    parts.append(line(675, 426, 675, 589, arrow=True))
    parts.append(line(830, 633, 954, 633, arrow=True))
    parts.append(line(1115, 595, 1115, 432, arrow=True))
    parts.append(polyline([(960, 148), (830, 148), (830, 388)], arrow=True))
    parts.append(line(675, 186, 675, 344, arrow=True))
    parts.append(polyline([(1270, 388), (1330, 388)], arrow=True))
    parts.append(polyline([(1115, 186), (1115, 344)], arrow=True))
    parts += [label(270, 280, "首次/增量写入", 18), label(710, 525, "按日期与词库抽取", 18), label(1140, 525, "生成计划明细", 18), label(1160, 255, "学习动作更新", 18)]
    parts += [rect(95, 815, 1460, 58), text_center(95, 815, 1460, 58, "本地数据流重点：词库导入、计划生成、学习权重更新和统计同步相互独立，但通过 Room 表保持状态连续。", 21, False)]
    return render_svg(save_svg("fig4_8_room_data_flow", parts, width, height), 2100)


def test_flow() -> Path:
    width, height = 1300, 820
    parts: list[str] = []
    xs = [85, 345, 605, 865]
    labels = ["单元测试", "接口测试", "功能测试", "兼容性检查"]
    details = [
        ["策略算法", "拼写匹配", "Markdown渲染"],
        ["认证接口", "资料接口", "AI接口"],
        ["登录注册", "学习计划", "排行榜"],
        ["Android 8+", "网络异常", "TTS可用性"],
    ]
    for x, title, ds in zip(xs, labels, details):
        parts += [rect(x, 120, 220, 70, "#f3f5f7"), text_center(x, 120, 220, 70, title, 22)]
        for idx, d in enumerate(ds):
            yy = 240 + idx * 92
            parts += [round_rect(x, yy, 220, 56), text_center(x, yy, 220, 56, d, 19, False)]
            if idx == 0:
                parts.append(line(x + 110, 190, x + 110, yy - 6, arrow=True))
            else:
                parts.append(line(x + 110, yy - 36, x + 110, yy - 6, arrow=True))
    parts += [round_rect(1085, 300, 160, 90), text_center(1085, 300, 160, 90, "测试结论", 22)]
    for x in xs:
        parts.append(polyline([(x + 110, 520), (1165, 520), (1165, 394)], arrow=True))
    return render_svg(save_svg("fig6_1_test_flow", parts, width, height), 1700)


def main() -> None:
    generated = [
        module_architecture(),
        use_case_diagram(),
        requirement_structure(),
        system_architecture(),
        login_flow(),
        daily_learning_flow(),
        database_model(),
        ai_sequence(),
        stats_flow(),
        jwt_auth_flow(),
        room_data_flow(),
        test_flow(),
    ]
    for path in generated:
        print(path)


if __name__ == "__main__":
    main()
