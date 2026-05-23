import os
import pathlib
import sys
import time

import pythoncom
import pywintypes
import win32com.client

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
PROJECT_ROOT = ROOT.parent
for item in (str(HERE), str(ROOT)):
    if item not in sys.path:
        sys.path.insert(0, item)

import g01_general_layout  # noqa: E402
import s01_high_pile_plan_elevation  # noqa: E402
import s02_high_pile_section_detail  # noqa: E402
import s03_caisson_plan_elevation  # noqa: E402
import s04_caisson_section_detail  # noqa: E402


SHEETS = [
    ("G-01_general_layout.dwg", "G-01", g01_general_layout.draw),
    ("S-01_high_pile_plan_elevation.dwg", "S-01", s01_high_pile_plan_elevation.draw),
    ("S-02_high_pile_section_detail_rebar.dwg", "S-02", s02_high_pile_section_detail.draw),
    ("S-03_caisson_plan_elevation.dwg", "S-03", s03_caisson_plan_elevation.draw),
    ("S-04_caisson_section_detail_rebar.dwg", "S-04", s04_caisson_section_detail.draw),
]


def retry(label, func, attempts=160, delay=0.25):
    last = None
    for _ in range(attempts):
        try:
            return func()
        except Exception as exc:
            last = exc
            pythoncom.PumpWaitingMessages()
            time.sleep(delay)
    raise RuntimeError(f"{label} failed after retries: {last}")


def get_acad():
    errors = []
    factories = (
        lambda: win32com.client.gencache.EnsureDispatch("AutoCAD.Application.25.1"),
        lambda: win32com.client.GetActiveObject("AutoCAD.Application.25.1"),
        lambda: win32com.client.GetActiveObject("AutoCAD.Application.25"),
        lambda: win32com.client.Dispatch("AutoCAD.Application.25.1"),
        lambda: win32com.client.Dispatch("AutoCAD.Application.25"),
        lambda: win32com.client.Dispatch("AutoCAD.Application"),
    )
    for factory in factories:
        try:
            app = factory()
            app.Visible = True
            return app
        except Exception as exc:
            errors.append(repr(exc))
            time.sleep(0.5)
    raise RuntimeError("Unable to attach/start AutoCAD COM: " + " | ".join(errors))


def new_document(app):
    docs = retry("Documents", lambda: app.Documents, attempts=240, delay=0.5)
    for factory in (lambda: docs.Add("acadiso.dwt"), lambda: docs.Add(), lambda: app.ActiveDocument):
        try:
            doc = retry("Document", factory, attempts=240, delay=0.5)
            retry("ModelSpace", lambda: doc.ModelSpace, attempts=240, delay=0.5)
            return doc
        except Exception:
            time.sleep(0.5)
    raise RuntimeError("Unable to create AutoCAD document")


def close_docs_under(app, marker):
    try:
        docs = app.Documents
        for idx in range(docs.Count - 1, -1, -1):
            try:
                doc = docs.Item(idx)
                if marker.lower() in str(doc.FullName).lower():
                    doc.Close(False)
            except Exception:
                pass
    except Exception:
        pass


def entity_count(doc):
    ms = retry("ModelSpace", lambda: doc.ModelSpace)
    return retry("ModelSpace.Count", lambda: ms.Count)


def run_sheet(app, output_dir, filename, draw_func):
    doc = new_document(app)
    print(f"Drawing {filename} ...", flush=True)
    draw_func(doc)
    count = entity_count(doc)
    path = os.path.join(str(output_dir), filename)
    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception:
            pass
    retry("SaveAs", lambda: doc.SaveAs(path), attempts=240, delay=0.5)
    retry("Close", lambda: doc.Close(False), attempts=120, delay=0.25)
    print(f"Saved {filename}: {count} entities", flush=True)
    return filename, count


def main():
    pythoncom.CoInitialize()
    output_dir = HERE / "output_dwgs"
    output_dir.mkdir(parents=True, exist_ok=True)
    selected = {arg.lower() for arg in sys.argv[1:]}
    run_list = []
    for filename, sheet_no, func in SHEETS:
        if selected and filename.lower() not in selected and sheet_no.lower() not in selected:
            continue
        run_list.append((filename, func))
    if not run_list:
        raise RuntimeError(f"No sheets matched arguments: {sorted(selected)}")

    app = get_acad()
    close_docs_under(app, str(output_dir))
    results = []
    for filename, func in run_list:
        try:
            results.append(run_sheet(app, output_dir, filename, func))
        except pywintypes.com_error as exc:
            print(f"COM error while drawing {filename}: {exc}", flush=True)
            raise
    print("ALL FINAL FIVE DRAWINGS GENERATED")
    for filename, count in results:
        print(f"{filename}\t{count}", flush=True)


if __name__ == "__main__":
    main()
