import time
from pathlib import Path

import pythoncom
import pywintypes
import win32com.client


ROOT = Path(r"\\Mac\Home\Downloads\Users\a136\vs\45425\thesis_project")
BASE = ROOT / r"papers\water_engineering\drawings\20260604_six_sheets"
DWG_DIR = BASE / "output"
PDF_DIR = BASE / "preview_pdf"


def retry(fn, *args, **kwargs):
    last = None
    for _ in range(80):
        try:
            return fn(*args, **kwargs)
        except pywintypes.com_error as exc:
            last = exc
            pythoncom.PumpWaitingMessages()
            time.sleep(0.25)
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


def export_one(app, dwg):
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    pdf = PDF_DIR / (dwg.stem + ".pdf")
    docs = retry(lambda: app.Documents)
    doc = retry(docs.Open, str(dwg))
    try:
        layout = retry(lambda: doc.ActiveLayout)
        for device in ["AutoCAD PDF (High Quality Print).pc3", "DWG To PDF.pc3", "Microsoft Print to PDF"]:
            try:
                layout.ConfigName = device
                break
            except Exception:
                continue
        for media in [
            "ISO_full_bleed_A1_(841.00_x_594.00_MM)",
            "ISO_A1_(841.00_x_594.00_MM)",
            "ISO_expand_A1_(841.00_x_594.00_MM)",
            "ANSI_expand_D_(34.00_x_22.00_Inches)",
        ]:
            try:
                layout.CanonicalMediaName = media
                break
            except Exception:
                continue
        try:
            layout.PlotRotation = 1
            layout.PlotType = 1
            layout.CenterPlot = True
            layout.UseStandardScale = True
            layout.StandardScale = 0
            layout.StyleSheet = "monochrome.ctb"
            layout.PlotWithPlotStyles = True
        except Exception:
            pass
        retry(doc.Plot.PlotToFile, str(pdf))
    finally:
        retry(doc.Close, False)
    print(pdf)


def main():
    app = acad_app()
    for dwg in sorted(DWG_DIR.glob("*.dwg")):
        export_one(app, dwg)


if __name__ == "__main__":
    main()
