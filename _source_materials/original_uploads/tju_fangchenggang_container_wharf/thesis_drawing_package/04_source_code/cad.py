import math
import os
import time

import pythoncom
import pywintypes
import win32com.client


RPC_E_CALL_REJECTED = -2147418111
RPC_E_SERVERCALL_RETRYLATER = -2147417846
RPC_E_SERVERFAULT = -2147417851


def com_call(func, *args, retries=90, delay=0.12):
    last_error = None
    for _ in range(retries):
        try:
            return func(*args)
        except pywintypes.com_error as exc:
            last_error = exc
            hresult = getattr(exc, "hresult", None)
            if hresult is None and exc.args:
                hresult = exc.args[0]
            if (
                hresult in (RPC_E_CALL_REJECTED, RPC_E_SERVERCALL_RETRYLATER, RPC_E_SERVERFAULT)
                or "Call was rejected by callee" in str(exc)
                or "被呼叫方拒绝接收呼叫" in str(exc)
            ):
                pythoncom.PumpWaitingMessages()
                time.sleep(delay)
                continue
            raise
    raise last_error


def point(x, y, z=0.0):
    return win32com.client.VARIANT(
        pythoncom.VT_ARRAY | pythoncom.VT_R8,
        (float(x), float(y), float(z)),
    )


def lw_points(coords):
    data = []
    for item in coords:
        data.extend([float(item[0]), float(item[1])])
    return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, tuple(data))


class AcadSession:
    def __init__(self):
        pythoncom.CoInitialize()
        self.app = None
        for factory in [
            lambda: win32com.client.gencache.EnsureDispatch("AutoCAD.Application.25.1"),
            lambda: win32com.client.GetActiveObject("AutoCAD.Application.25.1"),
            lambda: win32com.client.GetActiveObject("AutoCAD.Application.25"),
            lambda: win32com.client.Dispatch("AutoCAD.Application.25.1"),
            lambda: win32com.client.Dispatch("AutoCAD.Application.25"),
            lambda: win32com.client.GetActiveObject("AutoCAD.Application"),
            lambda: win32com.client.Dispatch("AutoCAD.Application"),
        ]:
            try:
                self.app = factory()
                com_call(lambda: setattr(self.app, "Visible", True), retries=120, delay=0.25)
                break
            except Exception:
                self.app = None
                time.sleep(0.5)
        if self.app is None:
            raise RuntimeError("Unable to start or attach to AutoCAD.Application")

    def new_drawing(self, dimtxt=2.5, dimasz=None, precision=2):
        last_error = None
        for _ in range(90):
            try:
                docs = com_call(lambda: self.app.Documents, retries=10, delay=0.2)
                try:
                    com_call(lambda: docs.Add("acadiso.dwt"), retries=10, delay=0.2)
                except Exception:
                    com_call(lambda: docs.Add(), retries=10, delay=0.2)
                break
            except (pywintypes.com_error, AttributeError) as exc:
                last_error = exc
                pythoncom.PumpWaitingMessages()
                time.sleep(0.25)
        else:
            raise last_error
        time.sleep(0.35)
        doc = com_call(lambda: self.app.ActiveDocument, retries=120, delay=0.2)
        drawing = Drawing(doc)
        drawing.configure(dimtxt=dimtxt, dimasz=dimasz or dimtxt * 0.8, precision=precision)
        return drawing


class Drawing:
    def __init__(self, doc):
        self.doc = doc
        self.ms = doc.ModelSpace

    def configure(self, dimtxt=2.5, dimasz=2.0, precision=2):
        for name, value in [
            ("INSUNITS", 6),  # meters
            ("LUNITS", 2),
            ("LUPREC", precision),
            ("DIMDEC", precision),
            ("DIMTXT", float(dimtxt)),
            ("DIMASZ", float(dimasz)),
            ("DIMEXO", float(dimtxt) * 0.35),
            ("DIMEXE", float(dimtxt) * 0.45),
            ("DIMGAP", float(dimtxt) * 0.25),
            ("DIMSCALE", 1.0),
        ]:
            try:
                com_call(self.doc.SetVariable, name, value)
            except Exception:
                pass
        for name in ["CENTER", "DASHED", "HIDDEN", "PHANTOM"]:
            try:
                com_call(self.doc.Linetypes.Load, name, "acad.lin")
            except Exception:
                pass
        self._setup_text_style()
        self._setup_layers()

    def _setup_text_style(self):
        try:
            style = com_call(self.doc.TextStyles.Item, "CN-SIMSUN")
        except Exception:
            style = com_call(self.doc.TextStyles.Add, "CN-SIMSUN")
        for setter in [
            lambda: style.SetFont("SimSun", False, False, 0, 134),
            lambda: style.SetFont("宋体", False, False, 0, 134),
            lambda: setattr(style, "FontFile", r"C:\Windows\Fonts\simsun.ttc"),
            lambda: setattr(style, "FontFile", r"C:\Windows\Fonts\simhei.ttf"),
            lambda: setattr(style, "FontFile", "simsun.ttc"),
        ]:
            try:
                setter()
                break
            except Exception:
                pass
        try:
            self.doc.ActiveTextStyle = style
        except Exception:
            pass

    def _setup_layers(self):
        layer_defs = {
            "BORDER": 7,
            "TEXT": 7,
            "NOTE": 7,
            "DIM": 2,
            "CENTER": 3,
            "CONTROL": 8,
            "LAND": 3,
            "WATER": 4,
            "DREDGE": 151,
            "ROAD": 8,
            "YARD": 2,
            "BUILDING": 30,
            "RAIL": 1,
            "EQUIPMENT": 140,
            "STRUCTURE": 1,
            "CAISSON": 5,
            "FOUNDATION": 32,
            "BACKFILL": 94,
            "LEVEL": 4,
            "HATCH": 9,
            "CUT": 1,
            "WARNING": 1,
        }
        for name, color in layer_defs.items():
            self.layer(name, color)

    def layer(self, name, color):
        try:
            layer = com_call(self.doc.Layers.Item, name)
        except Exception:
            layer = com_call(self.doc.Layers.Add, name)
        try:
            layer.Color = int(color)
        except Exception:
            pass
        return layer

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        com_call(self.doc.SaveAs, os.path.abspath(path))
        try:
            com_call(self.doc.Regen, 1)
        except Exception:
            pass
        return self.count_entities()

    def close(self):
        try:
            com_call(self.doc.Close, False)
        except Exception:
            pass

    def count_entities(self):
        last = None
        for _ in range(60):
            try:
                return int(self.ms.Count)
            except pywintypes.com_error as exc:
                last = exc
                pythoncom.PumpWaitingMessages()
                time.sleep(0.1)
        raise last

    def set_layer(self, ent, layer):
        try:
            ent.Layer = layer
        except Exception:
            pass
        return ent

    def set_linetype(self, ent, linetype):
        if not linetype:
            return ent
        try:
            ent.Linetype = linetype
        except Exception:
            pass
        return ent

    def line(self, x1, y1, x2, y2, layer="STRUCTURE", linetype=None):
        ent = com_call(self.ms.AddLine, point(x1, y1), point(x2, y2))
        self.set_layer(ent, layer)
        return self.set_linetype(ent, linetype)

    def polyline(self, coords, layer="STRUCTURE", closed=False, linetype=None):
        pts = list(coords)
        if closed and pts and pts[0] != pts[-1]:
            pts.append(pts[0])
        ent = com_call(self.ms.AddLightWeightPolyline, lw_points(pts))
        try:
            ent.Closed = bool(closed)
        except Exception:
            pass
        self.set_layer(ent, layer)
        return self.set_linetype(ent, linetype)

    def rect(self, x, y, w, h, layer="STRUCTURE", linetype=None):
        return self.polyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], layer, True, linetype)

    def circle(self, x, y, radius, layer="STRUCTURE"):
        ent = com_call(self.ms.AddCircle, point(x, y), float(radius))
        return self.set_layer(ent, layer)

    def text(self, value, x, y, height, layer="TEXT", rotation=0.0):
        ent = com_call(self.ms.AddText, str(value), point(x, y), float(height))
        self.set_layer(ent, layer)
        try:
            ent.StyleName = "CN-SIMSUN"
        except Exception:
            pass
        try:
            ent.Rotation = math.radians(rotation)
        except Exception:
            pass
        return ent

    def mtext(self, value, x, y, width, height, layer="TEXT"):
        ent = com_call(self.ms.AddMText, point(x, y), float(width), str(value))
        self.set_layer(ent, layer)
        try:
            ent.Height = float(height)
        except Exception:
            pass
        try:
            ent.StyleName = "CN-SIMSUN"
        except Exception:
            pass
        return ent

    def dim_rotated(self, p1, p2, loc, rotation=0.0, text=None):
        ent = com_call(self.ms.AddDimRotated, point(*p1), point(*p2), point(*loc), float(rotation))
        self.set_layer(ent, "DIM")
        if text is not None:
            try:
                ent.TextOverride = str(text)
            except Exception:
                pass
        return ent

    def dim_aligned(self, p1, p2, loc, text=None):
        ent = com_call(self.ms.AddDimAligned, point(*p1), point(*p2), point(*loc))
        self.set_layer(ent, "DIM")
        if text is not None:
            try:
                ent.TextOverride = str(text)
            except Exception:
                pass
        return ent

    def dim_diameter(self, p1, p2, leader_length=1.0, text=None):
        ent = com_call(self.ms.AddDimDiametric, point(*p1), point(*p2), float(leader_length))
        self.set_layer(ent, "DIM")
        if text is not None:
            try:
                ent.TextOverride = str(text)
            except Exception:
                pass
        return ent

    def leader(self, x1, y1, x2, y2, label, height, layer="TEXT"):
        self.line(x1, y1, x2, y2, layer)
        ang = math.atan2(y2 - y1, x2 - x1)
        size = height * 0.7
        p1 = (x1, y1)
        p2 = (x1 + size * math.cos(ang + 2.6), y1 + size * math.sin(ang + 2.6))
        p3 = (x1 + size * math.cos(ang - 2.6), y1 + size * math.sin(ang - 2.6))
        self.polyline([p1, p2, p3], layer, True)
        self.text(label, x2 + height * 0.4, y2 + height * 0.15, height, layer)

    def arrow(self, x1, y1, x2, y2, layer="TEXT", size=1.0):
        self.line(x1, y1, x2, y2, layer)
        ang = math.atan2(y2 - y1, x2 - x1)
        p1 = (x2, y2)
        p2 = (x2 - size * math.cos(ang - 0.45), y2 - size * math.sin(ang - 0.45))
        p3 = (x2 - size * math.cos(ang + 0.45), y2 - size * math.sin(ang + 0.45))
        self.polyline([p1, p2, p3], layer, True)

    def title_block(self, title, drawing_no, scale, x, y, w, h, text_h):
        self.rect(x, y, w, h, "BORDER")
        self.line(x, y + h * 0.58, x + w, y + h * 0.58, "BORDER")
        self.line(x + w * 0.56, y, x + w * 0.56, y + h, "BORDER")
        self.line(x + w * 0.76, y, x + w * 0.76, y + h * 0.58, "BORDER")
        self.text("项目：防城港9号泊位3万吨级集装箱进口码头", x + text_h, y + h * 0.66, text_h, "TEXT")
        self.text(f"图名：{title}", x + text_h, y + h * 0.25, text_h * 1.12, "TEXT")
        self.text(f"比例：{scale}", x + w * 0.58, y + h * 0.28, text_h, "TEXT")
        self.text(f"图号：{drawing_no}", x + w * 0.78, y + h * 0.28, text_h, "TEXT")

    def table(self, x, y, col_widths, row_height, rows, text_h, layer="TEXT"):
        total_w = sum(col_widths)
        total_h = row_height * len(rows)
        self.rect(x, y - total_h, total_w, total_h, "BORDER")
        running = x
        for width in col_widths[:-1]:
            running += width
            self.line(running, y, running, y - total_h, "BORDER")
        for idx in range(1, len(rows)):
            yy = y - row_height * idx
            self.line(x, yy, x + total_w, yy, "BORDER")
        for r, row in enumerate(rows):
            yy = y - row_height * r - row_height * 0.62
            xx = x
            for c, cell in enumerate(row):
                self.text(cell, xx + text_h * 0.35, yy, text_h, layer)
                xx += col_widths[c]

    def north_arrow(self, x, y, size, layer="TEXT"):
        self.arrow(x, y, x, y + size, layer, size * 0.18)
        self.text("N", x - size * 0.13, y + size * 1.05, size * 0.18, layer)
        self.circle(x, y + size * 0.45, size * 0.32, layer)

    def coordinate_grid(self, x0, y0, x1, y1, step, label_step, text_h):
        x = x0
        while x <= x1 + 1e-6:
            self.line(x, y0, x, y1, "CONTROL", "DASHED")
            if abs((x - x0) % label_step) < 1e-6:
                self.text(f"X={x:g}", x + text_h * 0.3, y0 - text_h * 2.0, text_h, "CONTROL")
            x += step
        y = y0
        while y <= y1 + 1e-6:
            self.line(x0, y, x1, y, "CONTROL", "DASHED")
            if abs((y - y0) % label_step) < 1e-6:
                self.text(f"Y={y:g}", x0 - text_h * 5.6, y + text_h * 0.25, text_h, "CONTROL")
            y += step

    def rect_hatch_lines(self, x, y, w, h, spacing, layer="HATCH", angle=45):
        if angle == 0:
            yy = y + spacing
            while yy < y + h:
                self.line(x, yy, x + w, yy, layer)
                yy += spacing
            return
        # Lightweight diagonal fill for rectangular areas.
        slope = 1 if angle > 0 else -1
        start = -h
        while start < w:
            x_a = x + max(start, 0)
            y_a = y + max(-start, 0)
            x_b = x + min(start + h, w)
            y_b = y + min(h, h + start) if start < 0 else y + h
            if slope < 0:
                y_a = y + h - (y_a - y)
                y_b = y + h - (y_b - y)
            self.line(x_a, y_a, x_b, y_b, layer)
            start += spacing


def output_path(root, drawing_dir, filename):
    output_name = os.environ.get("PORT_DRAWINGS_OUTPUT_NAME", "output")
    return os.path.join(root, output_name, drawing_dir, filename)
