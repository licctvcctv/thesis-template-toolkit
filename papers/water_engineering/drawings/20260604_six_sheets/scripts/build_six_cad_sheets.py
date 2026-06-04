import math
import shutil
import time
from pathlib import Path

import pythoncom
import pywintypes
import win32com.client


ROOT = Path(r"\\Mac\Home\Downloads\Users\a136\vs\45425\thesis_project")
BASE = ROOT / r"papers\water_engineering\drawings\20260604_six_sheets"
SRC = BASE / "source"
OUT = BASE / "output"

TITLE = "汕尾电厂配套煤码头工程初步设计"
STUDENT = "潘欣"
CLASSNO = "2022级港口二班  3022001703"
TEACHER = "孙克俐"
DATE = "2026.06"


def retry(fn, *args, **kwargs):
    last = None
    for _ in range(60):
        try:
            return fn(*args, **kwargs)
        except pywintypes.com_error as exc:
            last = exc
            pythoncom.PumpWaitingMessages()
            time.sleep(0.2)
    raise last


def acad_app():
    pythoncom.CoInitialize()
    for progid in ("AutoCAD.Application.25.1", "AutoCAD.Application.25", "AutoCAD.Application"):
        try:
            app = win32com.client.Dispatch(progid)
            app.Visible = True
            return app
        except Exception:
            continue
    raise RuntimeError("AutoCAD COM unavailable")


def pt(x, y, z=0):
    return win32com.client.VARIANT(
        pythoncom.VT_ARRAY | pythoncom.VT_R8,
        (float(x), float(y), float(z)),
    )


def arr2(values):
    return win32com.client.VARIANT(
        pythoncom.VT_ARRAY | pythoncom.VT_R8,
        tuple(float(v) for v in values),
    )


class Sheet:
    W = 84100
    H = 59400

    def __init__(self, app, filename, sheet_no, name, scale="见图示"):
        self.app = app
        docs = retry(lambda: app.Documents)
        self.work_path = None
        template = SRC / "潘欣平面立面图1.dwg"
        if template.exists():
            self.work_path = OUT / f"__work_{filename}"
            OUT.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(template, self.work_path)
            self.doc = retry(docs.Open, str(self.work_path))
            for ent in list(self.doc.ModelSpace):
                try:
                    ent.Delete()
                except Exception:
                    pass
        else:
            try:
                self.doc = retry(docs.Add, "acadiso.dwt")
            except Exception:
                self.doc = retry(docs.Add)
        self.ms = self.doc.ModelSpace
        self.filename = filename
        self.sheet_no = sheet_no
        self.name = name
        self.scale = scale
        self.layers()
        self.frame()

    def layers(self):
        for name, color in [
            ("FRAME", 7),
            ("THICK", 7),
            ("THIN", 8),
            ("TEXT", 7),
            ("DIM", 7),
            ("HATCH", 9),
            ("CENTER", 4),
        ]:
            try:
                layer = self.doc.Layers.Add(name)
            except Exception:
                layer = self.doc.Layers.Item(name)
            layer.Color = color
        try:
            st = self.doc.TextStyles.Add("HZ")
        except Exception:
            st = self.doc.TextStyles.Item("HZ")
        for face in ("FangSong", "SimSun", "Microsoft YaHei"):
            try:
                st.SetFont(face, False, False, 134, 49)
                break
            except Exception:
                pass
        for font_file in (r"C:\Windows\Fonts\simfang.ttf", "simfang.ttf", r"C:\Windows\Fonts\simsun.ttc", "simsun.ttc"):
            try:
                st.FontFile = font_file
                break
            except Exception:
                pass
        try:
            self.doc.ActiveTextStyle = st
        except Exception:
            pass

    def line(self, x1, y1, x2, y2, layer="THIN"):
        e = retry(self.ms.AddLine, pt(x1, y1), pt(x2, y2))
        e.Layer = layer
        return e

    def rect(self, x, y, w, h, layer="THIN"):
        self.line(x, y, x + w, y, layer)
        self.line(x + w, y, x + w, y + h, layer)
        self.line(x + w, y + h, x, y + h, layer)
        self.line(x, y + h, x, y, layer)

    def poly(self, pts, closed=False, layer="THIN"):
        arr = []
        for x, y in pts:
            arr += [float(x), float(y)]
        e = retry(self.ms.AddLightWeightPolyline, arr2(arr))
        e.Closed = bool(closed)
        e.Layer = layer
        return e

    def circle(self, x, y, r, layer="THIN"):
        e = retry(self.ms.AddCircle, pt(x, y), float(r))
        e.Layer = layer
        return e

    def text(self, x, y, s, h=450, layer="TEXT", align="L", rot=0):
        e = retry(self.ms.AddText, s, pt(x, y), float(h))
        e.Layer = layer
        try:
            e.StyleName = "HZ"
        except Exception:
            pass
        e.Rotation = math.radians(rot)
        if align == "C":
            e.Alignment = 1
            e.TextAlignmentPoint = pt(x, y)
        elif align == "R":
            e.Alignment = 2
            e.TextAlignmentPoint = pt(x, y)
        return e

    def mtext(self, x, y, w, s, h=450, layer="TEXT"):
        e = retry(self.ms.AddMText, pt(x, y), float(w), s)
        e.Layer = layer
        e.Height = float(h)
        try:
            e.StyleName = "HZ"
        except Exception:
            pass
        return e

    def dimh(self, x1, y, x2, txt, off=1200):
        yy = y - off
        self.line(x1, y, x1, yy + 250, "DIM")
        self.line(x2, y, x2, yy + 250, "DIM")
        self.line(x1, yy, x2, yy, "DIM")
        self.line(x1, yy, x1 + 350, yy + 120, "DIM")
        self.line(x1, yy, x1 + 350, yy - 120, "DIM")
        self.line(x2, yy, x2 - 350, yy + 120, "DIM")
        self.line(x2, yy, x2 - 350, yy - 120, "DIM")
        self.text((x1 + x2) / 2, yy + 250, txt, 380, "DIM", "C")

    def dimv(self, x, y1, y2, txt, off=1200):
        xx = x + off
        self.line(x, y1, xx - 250, y1, "DIM")
        self.line(x, y2, xx - 250, y2, "DIM")
        self.line(xx, y1, xx, y2, "DIM")
        self.text(xx + 250, (y1 + y2) / 2, txt, 380, "DIM", "L", 90)

    def hatch_rubble(self, x, y, w, h):
        step = 1300
        for i in range(int(w // step) + 1):
            xx = x + i * step
            self.line(xx, y, xx - 900, y + h, "HATCH")
        for i in range(12):
            self.circle(x + 600 + i * 1600, y + h * 0.45 + (i % 3) * 350, 210, "HATCH")

    def hatch_diag_rect(self, x, y, w, h, spacing=900):
        for i in range(-int(h // spacing) - 2, int(w // spacing) + 3):
            x1 = x + i * spacing
            y1 = y
            x2 = x1 + h
            y2 = y + h
            # clip roughly to rectangle edges; enough for CAD-style section hatch.
            if x1 < x:
                y1 += x - x1
                x1 = x
            if x2 > x + w:
                y2 -= x2 - (x + w)
                x2 = x + w
            if y1 <= y + h and y2 >= y:
                self.line(x1, y1, x2, y2, "HATCH")

    def hatch_diag_poly_bbox(self, pts, spacing=900):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x, y, w, h = min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)
        # Use short interior hatch strokes. The outline carries the real shape.
        for i in range(-int(h // spacing) - 2, int(w // spacing) + 3):
            x1 = x + i * spacing
            y1 = y + 400
            x2 = x1 + h - 800
            y2 = y + h - 400
            if x1 < x:
                y1 += x - x1
                x1 = x
            if x2 > x + w:
                y2 -= x2 - (x + w)
                x2 = x + w
            if y1 <= y + h and y2 >= y:
                self.line(x1, y1, x2, y2, "HATCH")

    def hatch_diag_ring(self, cx, cy, r_outer, r_inner, spacing=650):
        inv = 1 / math.sqrt(2)
        c = -r_outer + spacing
        while c < r_outer:
            outer = math.sqrt(max(r_outer * r_outer - c * c, 0))
            cut = math.sqrt(max(r_inner * r_inner - c * c, 0)) if abs(c) < r_inner else 0
            segments = [(-outer, outer)] if cut <= 0 else [(-outer, -cut), (cut, outer)]
            for u1, u2 in segments:
                if u2 - u1 < 150:
                    continue
                x1 = cx + (u1 - c) * inv
                y1 = cy + (u1 + c) * inv
                x2 = cx + (u2 - c) * inv
                y2 = cy + (u2 + c) * inv
                self.line(x1, y1, x2, y2, "HATCH")
            c += spacing

    def frame(self):
        self.rect(0, 0, self.W, self.H, "FRAME")
        self.rect(1500, 1500, self.W - 3000, self.H - 3000, "FRAME")
        tbx, tby, tbw, tbh = 61000, 1500, 18500, 7600
        self.rect(tbx, tby, tbw, tbh, "FRAME")
        for yy in [tby + 1500, tby + 3000, tby + 4500, tby + 6000]:
            self.line(tbx, yy, tbx + tbw, yy, "FRAME")
        self.line(tbx + 5200, tby, tbx + 5200, tby + tbh, "FRAME")
        self.line(tbx + 11500, tby, tbx + 11500, tby + 4500, "FRAME")
        self.text(tbx + tbw / 2, tby + 6400, TITLE, 430, "TEXT", "C")
        self.text(tbx + 800, tby + 5000, "图名", 380)
        self.mtext(tbx + 5600, tby + 5650, 5400, self.name, 360)
        self.text(tbx + 800, tby + 3500, "比例", 380)
        self.text(tbx + 5600, tby + 3500, self.scale, 380)
        self.text(tbx + 12200, tby + 3500, "图号", 380)
        self.text(tbx + 15500, tby + 3500, f"{self.sheet_no}/6", 380)
        self.text(tbx + 800, tby + 2000, "设计", 380)
        self.text(tbx + 5600, tby + 2000, STUDENT, 380)
        self.text(tbx + 12200, tby + 2000, "日期", 380)
        self.text(tbx + 15500, tby + 2000, DATE, 380)
        self.text(tbx + 800, tby + 650, "指导教师", 360)
        self.text(tbx + 5600, tby + 650, TEACHER, 360)
        self.text(tbx + 12200, tby + 650, CLASSNO, 300)
        self.text(self.W / 2, 3450, self.name, 720, "TEXT", "C")
        self.line(self.W / 2 - 8200, 3200, self.W / 2 + 8200, 3200, "THICK")

    def save(self):
        out = OUT / self.filename
        out.parent.mkdir(parents=True, exist_ok=True)
        retry(self.doc.SaveAs, str(out))
        retry(self.doc.Close, False)
        if self.work_path and self.work_path != out:
            try:
                self.work_path.unlink()
            except Exception:
                pass
        return out


def replace_source_text(doc):
    repl = {
        "+4.50": "+3.60",
        "+4.00": "+3.56",
        "+3.50": "+1.91",
        "+2.20": "+0.80",
        "+2.00": "+0.50",
        "+1.50": "+0.22",
        "+1.00": "+0.22",
        "-4.0": "-12.50",
        "-35.0": "-28.40",
        "码头前沿高": "码头面高程",
        "码头前沿高程": "码头面高程",
        "平均水位": "平均水位",
        "高桩码头": "高桩梁板式码头",
        "课程名称": "工程名称",
        "汕尾电厂配套煤码头初步设计": TITLE,
        "2026.03": DATE,
        "2026.05": DATE,
        "1:100": "见图示",
    }
    for ent in doc.ModelSpace:
        try:
            obj = ent.ObjectName
        except Exception:
            continue
        if obj not in ("AcDbText", "AcDbMText"):
            continue
        try:
            s = ent.TextString
        except Exception:
            continue
        ns = s
        for a, b in repl.items():
            ns = ns.replace(a, b)
        if "图纸编号" not in ns and ns.strip() in ("2/6", "3/6"):
            # sheet number is handled by caller
            pass
        if ns != s:
            try:
                ent.TextString = ns
            except Exception:
                pass


def copy_modify_source(app, src_name, out_name, sheet_no, title):
    src = SRC / src_name
    dst = OUT / out_name
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    docs = retry(lambda: app.Documents)
    doc = retry(docs.Open, str(dst))
    replace_source_text(doc)
    for ent in doc.ModelSpace:
        try:
            if ent.ObjectName in ("AcDbText", "AcDbMText"):
                s = ent.TextString
                if "图纸编号" not in s:
                    if s.strip() in ("2/6", "3/6"):
                        ent.TextString = f"{sheet_no}/6"
                    if "高桩梁板式码头平面图" in s or "高桩梁板式码头断面图" in s:
                        ent.TextString = s.replace("高桩梁板式码头平面图、立面图", title).replace("高桩梁板式码头断面图", title)
        except Exception:
            pass
    retry(doc.SaveAs, str(dst))
    retry(doc.Close, False)
    return dst


def general_layout(app):
    s = Sheet(app, "G-01_煤码头总平面布置图.dwg", 1, "煤码头总平面布置图", "1:1000")
    ox, oy = 8500, 14000
    # shoreline and basin
    s.rect(ox, oy + 17500, 52000, 8000, "THIN")
    s.text(ox + 26000, oy + 24400, "后方陆域及煤炭堆场", 520, "TEXT", "C")
    # stockyard cells and service roads
    for i, name in enumerate(["煤堆场A", "煤堆场B", "预留堆场", "辅助区"]):
        x = ox + 2500 + i * 12000
        s.rect(x, oy + 18600, 9500, 4200, "THIN")
        s.text(x + 4750, oy + 20500, name, 360, "TEXT", "C")
        for k in range(1, 4):
            s.line(x + k * 2300, oy + 18600, x + k * 2300, oy + 22800, "HATCH")
    s.rect(ox + 3000, oy + 23200, 44500, 1200, "THIN")
    s.text(ox + 25000, oy + 23600, "后方检修道路及消防通道", 330, "TEXT", "C")
    s.rect(ox + 48500, oy + 18500, 4200, 4800, "THIN")
    s.text(ox + 50600, oy + 20500, "转运站", 360, "TEXT", "C")
    s.rect(ox + 2000, oy + 9000, 52000, 4500, "THICK")
    s.text(ox + 28000, oy + 10900, "码头平台 L=260m", 520, "TEXT", "C")
    s.rect(ox + 3000, oy + 14500, 48000, 1700, "THIN")
    s.text(ox + 27000, oy + 15050, "前沿作业带、卸船机轨道及皮带机廊道", 420, "TEXT", "C")
    # rail/berth equipment markers
    for i in range(6):
        x = ox + 6000 + i * 7600
        s.rect(x, oy + 11600, 2100, 1200, "THIN")
        s.text(x + 1050, oy + 11900, "卸船机", 280, "TEXT", "C")
    s.line(ox + 3500, oy + 12550, ox + 52000, oy + 12550, "CENTER")
    s.line(ox + 3500, oy + 10150, ox + 52000, oy + 10150, "CENTER")
    # berth water
    s.rect(ox + 2000, oy + 2500, 52000, 5200, "THIN")
    s.text(ox + 28000, oy + 4700, "停泊水域 B=65m，前沿设计水深 -12.50m", 420, "TEXT", "C")
    s.line(ox + 2000, oy + 1200, ox + 54000, oy + 1200, "CENTER")
    s.text(ox + 28000, oy + 200, "航道轴线及进港方向", 360, "TEXT", "C")
    for i in range(5):
        x = ox + 6000 + i * 9000
        s.line(x, oy + 1900, x + 1500, oy + 1200, "CENTER")
        s.line(x, oy + 500, x + 1500, oy + 1200, "CENTER")
    s.circle(ox + 60000, oy + 5200, 4200, "CENTER")
    s.text(ox + 60000, oy + 5200, "回旋水域 D=450m", 420, "TEXT", "C")
    # north arrow
    s.line(ox + 62000, oy + 21800, ox + 62000, oy + 25800, "THICK")
    s.poly([(ox + 62000, oy + 25800), (ox + 61100, oy + 24200), (ox + 62900, oy + 24200)], True, "THICK")
    s.text(ox + 62000, oy + 26300, "N", 520, "TEXT", "C")
    # handling flow arrows
    for x in [ox + 9000, ox + 18000, ox + 27000, ox + 36000]:
        s.line(x, oy + 13500, x + 2500, oy + 17500, "THIN")
        s.line(x + 2500, oy + 17500, x + 1850, oy + 16600, "THIN")
        s.line(x + 2500, oy + 17500, x + 1300, oy + 17350, "THIN")
    s.dimh(ox + 2000, oy + 9000, ox + 54000, "260m", 1500)
    s.dimh(ox + 2000, oy + 2500, ox + 54000, "停泊水域长260m", 900)
    # legend
    lx, ly = ox + 57000, oy + 9500
    s.rect(lx, ly, 13000, 5200, "THIN")
    s.text(lx + 6500, ly + 4500, "图例", 420, "TEXT", "C")
    s.rect(lx + 900, ly + 3150, 1600, 650, "THIN")
    s.text(lx + 3100, ly + 3230, "堆场及生产辅助区", 330)
    s.line(lx + 900, ly + 2400, lx + 2500, ly + 2400, "CENTER")
    s.text(lx + 3100, ly + 2280, "航道/轨道中心线", 330)
    s.rect(lx + 900, ly + 1250, 1600, 650, "THICK")
    s.text(lx + 3100, ly + 1330, "码头平台及泊位", 330)
    s.mtext(ox + 57000, oy + 17000, 14000, "说明：\\P1. 本图按5万吨级散货船靠泊条件布置。\\P2. 码头前沿布置卸船机轨道，后方设置皮带机廊道、转运站及堆场。\\P3. 水域包括停泊水域、回旋水域和进出港航道。", 420)
    return s.save()


def caisson_plan(app):
    s = Sheet(app, "S-03_沉箱方案平面立面图.dwg", 4, "重力式沉箱方案平面、立面图", "1:200")
    ox, oy = 8000, 30500
    # plan
    s.text(ox + 24000, oy + 17000, "沉箱平面布置", 560, "TEXT", "C")
    for i in range(12):
        x = ox + i * 3600
        s.rect(x, oy + 8000, 3400, 7600, "THICK")
        s.line(x + 1700, oy + 8000, x + 1700, oy + 15600, "THIN")
        s.line(x, oy + 11800, x + 3400, oy + 11800, "THIN")
    s.dimh(ox, oy + 8000, ox + 12 * 3600 - 200, "12×22m≈264m，泊位控制长度260m", 1600)
    s.dimh(ox, oy + 8000, ox + 3400, "22m", 900)
    s.text(ox + 22000, oy + 11900, "单节沉箱 22m×22m", 420, "TEXT", "C")
    # elevation
    ey = 10500
    s.text(ox + 24000, ey + 17000, "沉箱立面", 560, "TEXT", "C")
    s.line(ox - 2000, ey + 14500, ox + 46000, ey + 14500, "CENTER")
    s.text(ox - 2500, ey + 14600, "+3.60 码头面", 400, "TEXT", "R")
    s.line(ox - 2000, ey + 9200, ox + 46000, ey + 9200, "THIN")
    s.text(ox - 2500, ey + 9300, "-12.50 前沿泥面", 400, "TEXT", "R")
    for i in range(12):
        x = ox + i * 3600
        s.rect(x, ey + 9200, 3400, 5300, "THICK")
        s.line(x + 1700, ey + 9200, x + 1700, ey + 14500, "THIN")
    s.hatch_rubble(ox - 600, ey + 7600, 45000, 1200)
    s.text(ox + 21000, ey + 7800, "抛石基床及整平层", 420, "TEXT", "C")
    s.dimh(ox, ey + 9200, ox + 3400, "22m", 900)
    s.dimv(ox + 44600, ey + 9200, ey + 14500, "13m", 1600)
    return s.save()


def caisson_section(app):
    s = Sheet(app, "S-04_沉箱方案断面图.dwg", 5, "重力式沉箱方案断面图", "1:100")
    ox, oy = 18000, 11500
    # seabed and water/elevations
    s.line(ox - 10000, oy + 30000, ox + 42000, oy + 30000, "CENTER")
    s.text(ox - 10500, oy + 30100, "+3.60 码头面", 420, "TEXT", "R")
    s.line(ox - 10000, oy + 22500, ox + 42000, oy + 22500, "CENTER")
    s.text(ox - 10500, oy + 22600, "+1.91 设计高水位", 390, "TEXT", "R")
    s.line(ox - 10000, oy + 16000, ox + 42000, oy + 16000, "CENTER")
    s.text(ox - 10500, oy + 16100, "+0.22 设计低水位", 390, "TEXT", "R")
    s.line(ox - 10000, oy + 6500, ox + 42000, oy + 6500, "THIN")
    s.text(ox - 10500, oy + 6600, "-12.50 前沿泥面", 390, "TEXT", "R")
    # caisson and wharf
    s.rect(ox, oy + 6500, 22000, 23500, "THICK")
    s.rect(ox + 1200, oy + 8200, 19600, 18900, "THIN")
    for x in [ox + 7600, ox + 14400]:
        s.line(x, oy + 8200, x, oy + 27100, "THIN")
    s.line(ox + 1200, oy + 17650, ox + 20800, oy + 17650, "THIN")
    s.rect(ox - 1200, oy + 30000, 25500, 2500, "THICK")
    s.text(ox + 11000, oy + 30900, "现浇胸墙及面层", 420, "TEXT", "C")
    s.hatch_rubble(ox - 2500, oy + 4300, 27000, 1800)
    # backfill slope
    s.poly([(ox + 22000, oy + 6500), (ox + 39000, oy + 6500), (ox + 39000, oy + 30000), (ox + 24000, oy + 30000), (ox + 22000, oy + 6500)], False, "THIN")
    for i in range(11):
        s.line(ox + 24000 + i * 1300, oy + 7500, ox + 23200 + i * 1300, oy + 11800, "HATCH")
    s.text(ox + 30500, oy + 21000, "墙后回填开山石", 430, "TEXT", "C")
    s.text(ox + 11000, oy + 18200, "箱内回填块石", 420, "TEXT", "C")
    s.text(ox + 11000, oy + 10300, "沉箱仓格", 420, "TEXT", "C")
    s.dimh(ox, oy + 6500, ox + 22000, "22m", 1500)
    s.dimv(ox + 23500, oy + 6500, oy + 30000, "13m", 1500)
    s.mtext(ox + 43000, oy + 18500, 12000, "说明：\\P1. 单节沉箱平面尺寸22m×22m，高度约13m。\\P2. 箱内回填块石，墙后设置倒滤层及开山石回填。\\P3. 基床采用抛石基床并整平，稳定计算按可靠指标控制。", 420)
    return s.save()


def component_detail(app):
    s = Sheet(app, "S-05_典型构件尺寸图.dwg", 6, "典型构件尺寸图", "1:50")
    s.text(15000, 51500, "纵梁、横梁及靠船构件断面图（单位：mm）", 560, "TEXT", "L")

    # 1. Rail beam / longitudinal beam section, following the reference PDF style.
    x, y = 9000, 35000
    s.text(x + 4200, y + 11800, "轨道梁断面", 460, "TEXT", "C")
    s.rect(x, y, 8000, 12000, "THICK")
    # recessed rail groove, kept shallow to avoid inventing complicated rebar.
    s.rect(x + 2500, y + 4700, 3000, 4600, "THIN")
    s.hatch_diag_rect(x, y, 8000, 4700, 950)
    s.hatch_diag_rect(x, y + 9300, 8000, 2700, 950)
    s.hatch_diag_rect(x, y + 4700, 2500, 4600, 950)
    s.hatch_diag_rect(x + 5500, y + 4700, 2500, 4600, 950)
    s.text(x + 4000, y + 6000, "预留槽", 340, "TEXT", "C", 90)
    s.dimh(x, y + 12000, x + 8000, "800", 1200)
    s.dimv(x + 8300, y, y + 12000, "1200", 1200)
    s.dimh(x + 2500, y + 4700, x + 5500, "300", 900)
    s.dimv(x + 5600, y + 4700, y + 9300, "460", 900)

    # 2. General longitudinal beam.
    x2, y2 = 23500, 35000
    s.text(x2 + 4000, y2 + 11800, "一般纵梁断面", 460, "TEXT", "C")
    s.rect(x2, y2, 8000, 12000, "THICK")
    s.hatch_diag_rect(x2, y2, 8000, 12000, 950)
    s.dimh(x2, y2 + 12000, x2 + 8000, "800", 1200)
    s.dimv(x2 + 8300, y2, y2 + 12000, "1200", 1200)

    # 3. Inverted-T transverse beam, dimensions tied to thesis calculation b=1.8m, h=2.2m.
    x3, y3 = 39000, 33000
    s.text(x3 + 9000, y3 + 15000, "横梁断面", 460, "TEXT", "C")
    t_pts = [
        (x3, y3),
        (x3 + 18000, y3),
        (x3 + 18000, y3 + 6500),
        (x3 + 13000, y3 + 6500),
        (x3 + 13000, y3 + 22000),
        (x3 + 5000, y3 + 22000),
        (x3 + 5000, y3 + 6500),
        (x3, y3 + 6500),
    ]
    s.poly(t_pts, True, "THICK")
    s.hatch_diag_rect(x3, y3, 18000, 6500, 1100)
    s.hatch_diag_rect(x3 + 5000, y3 + 6500, 8000, 15500, 1100)
    s.dimh(x3, y3, x3 + 18000, "1800", 1200)
    s.dimh(x3 + 5000, y3 + 22000, x3 + 13000, "800", -1100)
    s.dimv(x3 + 18700, y3, y3 + 6500, "650", 1200)
    s.dimv(x3 + 20500, y3 + 6500, y3 + 22000, "1550", 1200)
    s.dimv(x3 + 22300, y3, y3 + 22000, "2200", 1200)

    # 4. Berthing component section, copied in spirit from the reference figure and adjusted for this wharf.
    bx, by = 10500, 10500
    s.text(bx + 6200, by + 21500, "靠船构件断面", 460, "TEXT", "C")
    kc_pts = [
        (bx + 1250, by),
        (bx + 2500, by),
        (bx + 4300, by + 12250),
        (bx + 10500, by + 12250),
        (bx + 10500, by + 13750),
        (bx + 5200, by + 13750),
        (bx + 4300, by + 19000),
        (bx + 5400, by + 19000),
        (bx + 5400, by + 20000),
        (bx + 4300, by + 20000),
        (bx + 4300, by + 19000),
        (bx + 3500, by + 19000),
        (bx + 2000, by + 12250),
    ]
    s.poly(kc_pts, True, "THICK")
    s.hatch_diag_rect(bx + 1700, by + 500, 1700, 11200, 850)
    s.hatch_diag_rect(bx + 3150, by + 12700, 1800, 6100, 850)
    s.hatch_diag_rect(bx + 5350, by + 12600, 4800, 1100, 850)
    s.rect(bx + 3000, by + 19000, 1400, 900, "THIN")
    s.text(bx + 3700, by + 19300, "护轮坎", 300, "TEXT", "C")
    s.text(bx + 7800, by + 12980, "靠船横撑", 330, "TEXT", "C")
    s.dimh(bx + 5200, by + 13750, bx + 10500, "1000", -900)
    s.dimh(bx + 1250, by, bx + 2500, "250", 1000)
    s.dimv(bx - 700, by, by + 20000, "4000", 1200)
    s.dimv(bx + 250, by, by + 12250, "2450", 900)
    s.dimv(bx + 250, by + 12250, by + 13750, "300", 900)
    s.dimv(bx + 250, by + 13750, by + 19000, "1050", 900)
    s.dimh(bx + 4300, by + 20000, bx + 5400, "200", -850)
    s.dimh(bx + 3500, by + 19000, bx + 4300, "150", -850)

    # 5. PHC pile section as an auxiliary detail.
    cx, cy = 51000, 15500
    s.text(cx, cy + 8200, "PHC管桩断面", 460, "TEXT", "C")
    s.circle(cx, cy, 4000, "THICK")
    s.circle(cx, cy, 2700, "THIN")
    s.hatch_diag_ring(cx, cy, 4000, 2700, 700)
    s.line(cx - 5000, cy, cx + 5000, cy, "CENTER")
    s.line(cx, cy - 5000, cx, cy + 5000, "CENTER")
    s.dimh(cx - 4000, cy + 4000, cx + 4000, "800", 1000)
    s.text(cx, cy - 5700, "壁厚约130", 360, "TEXT", "C")

    s.mtext(56500, 24500, 12500, "说明：\\P1. 图中尺寸单位为mm。\\P2. 纵梁按800×1200绘制，横梁按1800×2200控制。\\P3. 靠船构件按前沿局部受力构件绘制，护舷和系船柱连接区施工时应加强配筋。\\P4. PHC管桩按D800、壁厚约130绘制。", 380)
    return s.save()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    app = acad_app()
    made = []
    made.append(general_layout(app))
    made.append(copy_modify_source(app, "潘欣平面立面图1.dwg", "S-01_高桩梁板式码头平面立面图.dwg", 2, "高桩梁板式码头平面、立面图"))
    made.append(copy_modify_source(app, "潘欣高桩码头断面图1.dwg", "S-02_高桩梁板式码头断面图.dwg", 3, "高桩梁板式码头断面图"))
    made.append(caisson_plan(app))
    made.append(caisson_section(app))
    made.append(component_detail(app))
    for p in made:
        print(p)


if __name__ == "__main__":
    main()
