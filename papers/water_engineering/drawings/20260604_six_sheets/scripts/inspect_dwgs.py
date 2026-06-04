import json
import time
from pathlib import Path

import pythoncom
import pywintypes
import win32com.client


ROOT = Path(r"\\Mac\Home\Downloads\Users\a136\vs\45425\thesis_project")
SOURCE_DIR = ROOT / r"papers\water_engineering\drawings\20260604_six_sheets\source"
OUTPUT_DIR = ROOT / r"papers\water_engineering\drawings\20260604_six_sheets\output"
DWGS = list(SOURCE_DIR.glob("*.dwg")) + list(OUTPUT_DIR.glob("*.dwg"))
OUT = ROOT / r"papers\water_engineering\drawings\20260604_six_sheets\dwg_inspection.json"


def retry(fn, *args, **kwargs):
    last = None
    for _ in range(40):
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


def point_tuple(v):
    try:
        return [float(v[0]), float(v[1]), float(v[2])]
    except Exception:
        return None


def inspect_one(app, path):
    docs = retry(lambda: app.Documents)
    doc = retry(docs.Open, str(path))
    retry(app.ActiveDocument.SetVariable, "FILEDIA", 0)
    texts = []
    counts = {}
    minp = maxp = None
    try:
        minv, maxv = doc.GetVariable("EXTMIN"), doc.GetVariable("EXTMAX")
        minp, maxp = point_tuple(minv), point_tuple(maxv)
    except Exception:
        pass
    for ent in doc.ModelSpace:
        try:
            obj = ent.ObjectName
        except Exception:
            continue
        counts[obj] = counts.get(obj, 0) + 1
        if obj in ("AcDbText", "AcDbMText"):
            try:
                text = ent.TextString
            except Exception:
                text = ""
            try:
                ins = point_tuple(ent.InsertionPoint)
            except Exception:
                ins = None
            if text.strip():
                texts.append({"object": obj, "text": text, "point": ins})
    retry(doc.Close, False)
    return {"path": str(path), "extmin": minp, "extmax": maxp, "counts": counts, "texts": texts}


def main():
    app = acad_app()
    data = [inspect_one(app, p) for p in DWGS]
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(OUT))
    for item in data:
        print(Path(item["path"]).name, "texts", len(item["texts"]), "counts", item["counts"])


if __name__ == "__main__":
    main()
