"""Test suite for prepare_dataset.py data preprocessing pipeline.

Creates synthetic VisDrone-format data and verifies the conversion output
without requiring the real dataset to be downloaded.

Usage:
    python scripts/test_prepare_dataset.py
"""

import shutil
import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np

# Allow importing from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Patch dataset dir to use a temp directory for all tests
import scripts.prepare_dataset as prep

PASSED = 0
FAILED = 0


def ok(name):
    global PASSED
    PASSED += 1
    print(f"  [PASS] {name}")


def fail(name, reason):
    global FAILED
    FAILED += 1
    print(f"  [FAIL] {name}: {reason}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_image(path, w=640, h=480):
    """Write a solid-color JPEG image."""
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:] = (100, 150, 200)
    cv2.imwrite(str(path), img)


def make_annotation(path, lines):
    """Write a VisDrone annotation file."""
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def setup_split(tmp_dir, split, images, annotations):
    """
    Create a split directory with images and raw annotations.

    images      : {stem: (w, h)}
    annotations : {stem: [line, ...]}
    """
    img_dir = tmp_dir / split / "images"
    ann_dir = tmp_dir / split / "_annotations"
    img_dir.mkdir(parents=True)
    ann_dir.mkdir(parents=True)

    for stem, (w, h) in images.items():
        make_image(img_dir / f"{stem}.jpg", w, h)

    for stem, lines in annotations.items():
        make_annotation(ann_dir / f"{stem}.txt", lines)

    return img_dir, ann_dir


def run_convert(tmp_dir, split):
    """Temporarily redirect prepare_dataset's DATASET_DIR, run conversion."""
    original = prep.DATASET_DIR
    prep.DATASET_DIR = tmp_dir
    try:
        return prep.convert_visdrone_to_yolo(split)
    finally:
        prep.DATASET_DIR = original


def read_label(tmp_dir, split, stem):
    label_path = tmp_dir / split / "labels" / f"{stem}.txt"
    if not label_path.exists():
        return None
    text = label_path.read_text().strip()
    if not text:
        return []
    rows = []
    for line in text.splitlines():
        parts = line.split()
        rows.append((int(parts[0]), float(parts[1]), float(parts[2]),
                     float(parts[3]), float(parts[4])))
    return rows


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

def test_basic_conversion():
    """A valid annotation line should produce correct YOLO format."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        # 640x480 image, box at pixel (64, 96, 128, 192), category=1, score=1
        setup_split(tmp, "train",
                    images={"img0": (640, 480)},
                    annotations={"img0": ["64,96,128,192,1,1,0,0"]})
        run_convert(tmp, "train")
        rows = read_label(tmp, "train", "img0")

        if rows is None:
            fail("basic_conversion", "label file not created")
            return
        if len(rows) != 1:
            fail("basic_conversion", f"expected 1 row, got {len(rows)}")
            return

        cls, cx, cy, w, h = rows[0]
        # Expected: class 0 (category 1 -> 0)
        # cx = (64 + 128/2) / 640 = (64+64)/640 = 128/640 = 0.2
        # cy = (96 + 192/2) / 480 = (96+96)/480 = 192/480 = 0.4
        # nw = 128/640 = 0.2
        # nh = 192/480 = 0.4
        expected = (0, 0.2, 0.4, 0.2, 0.4)
        tol = 1e-4

        if cls != expected[0]:
            fail("basic_conversion", f"class={cls}, expected {expected[0]}")
            return
        for got, exp, name in zip((cx, cy, w, h), expected[1:], ("cx","cy","w","h")):
            if abs(got - exp) > tol:
                fail("basic_conversion", f"{name}={got:.6f}, expected {exp:.6f}")
                return
        ok("basic_conversion")


def test_category_mapping():
    """All 10 valid categories map to YOLO class 0-9."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        lines = [f"10,10,20,20,1,{cat},0,0" for cat in range(1, 11)]
        setup_split(tmp, "train",
                    images={"img1": (200, 200)},
                    annotations={"img1": lines})
        run_convert(tmp, "train")
        rows = read_label(tmp, "train", "img1")

        if rows is None or len(rows) != 10:
            fail("category_mapping", f"expected 10 rows, got {len(rows) if rows else 'None'}")
            return
        for i, (cls, *_) in enumerate(rows):
            if cls != i:
                fail("category_mapping", f"row {i}: class={cls}, expected {i}")
                return
        ok("category_mapping")


def test_skip_score_zero():
    """Lines with score==0 must be skipped."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        setup_split(tmp, "train",
                    images={"img2": (200, 200)},
                    annotations={"img2": [
                        "10,10,20,20,0,1,0,0",   # score=0 -> skip
                        "10,10,20,20,1,2,0,0",   # score=1 -> keep
                    ]})
        run_convert(tmp, "train")
        rows = read_label(tmp, "train", "img2")

        if rows is None or len(rows) != 1:
            fail("skip_score_zero", f"expected 1 row, got {len(rows) if rows else 'None'}")
            return
        if rows[0][0] != 1:  # category 2 -> class 1
            fail("skip_score_zero", f"wrong class kept: {rows[0][0]}")
            return
        ok("skip_score_zero")


def test_skip_ignored_categories():
    """Category 0 (ignored) and 11 (others) must be skipped."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        setup_split(tmp, "train",
                    images={"img3": (200, 200)},
                    annotations={"img3": [
                        "10,10,20,20,1,0,0,0",    # category 0 -> skip
                        "10,10,20,20,1,11,0,0",   # category 11 -> skip
                        "10,10,20,20,1,3,0,0",    # category 3 -> keep as class 2
                    ]})
        run_convert(tmp, "train")
        rows = read_label(tmp, "train", "img3")

        if rows is None or len(rows) != 1:
            fail("skip_ignored_categories", f"expected 1 row, got {len(rows) if rows else 'None'}")
            return
        if rows[0][0] != 2:
            fail("skip_ignored_categories", f"wrong class: {rows[0][0]}")
            return
        ok("skip_ignored_categories")


def test_clamp_out_of_bounds_box():
    """Boxes extending beyond image boundaries are clamped to [0,1]."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        # Box starts at -10,-10 with 300x300 on a 100x100 image
        setup_split(tmp, "train",
                    images={"img4": (100, 100)},
                    annotations={"img4": ["-10,-10,300,300,1,1,0,0"]})
        run_convert(tmp, "train")
        rows = read_label(tmp, "train", "img4")

        if rows is None or len(rows) != 1:
            fail("clamp_out_of_bounds", f"expected 1 row, got {len(rows) if rows else 'None'}")
            return
        cls, cx, cy, w, h = rows[0]
        if not (0.0 <= cx <= 1.0 and 0.0 <= cy <= 1.0 and
                0.0 <= w  <= 1.0 and 0.0 <= h  <= 1.0):
            fail("clamp_out_of_bounds", f"values out of [0,1]: cx={cx} cy={cy} w={w} h={h}")
            return
        ok("clamp_out_of_bounds")


def test_skip_zero_area_box():
    """Boxes that become zero-area after normalization are skipped."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        # width=0 -> nw=0 -> skip
        setup_split(tmp, "train",
                    images={"img5": (200, 200)},
                    annotations={"img5": ["10,10,0,0,1,1,0,0"]})
        run_convert(tmp, "train")
        rows = read_label(tmp, "train", "img5")

        if rows is None or len(rows) != 0:
            fail("skip_zero_area_box", f"expected 0 rows, got {len(rows) if rows else 'None'}")
            return
        ok("skip_zero_area_box")


def test_malformed_annotation_line_skipped():
    """Lines with non-integer fields must be skipped, not crash."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        setup_split(tmp, "train",
                    images={"img6": (200, 200)},
                    annotations={"img6": [
                        "bad,data,here,x,y,z,0,0",  # non-integer -> skip
                        "10,10,30,30,1,1,0,0",       # valid -> keep
                    ]})
        try:
            run_convert(tmp, "train")
            rows = read_label(tmp, "train", "img6")
            if rows is None or len(rows) != 1:
                fail("malformed_line_skipped", f"expected 1 row, got {len(rows) if rows else 'None'}")
            else:
                ok("malformed_line_skipped")
        except Exception as e:
            fail("malformed_line_skipped", f"raised exception: {e}")


def test_float_fields_in_annotation_skipped():
    """Lines with float values (e.g. '100.5') in int fields are skipped."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        setup_split(tmp, "train",
                    images={"img7": (200, 200)},
                    annotations={"img7": [
                        "100.5,200,50,30,1,3,0,0",  # float bbox_left -> skip
                        "10,10,30,30,1,2,0,0",       # valid -> keep
                    ]})
        try:
            run_convert(tmp, "train")
            rows = read_label(tmp, "train", "img7")
            if rows is None or len(rows) != 1:
                fail("float_fields_skipped", f"expected 1 row, got {len(rows) if rows else 'None'}")
            else:
                ok("float_fields_skipped")
        except Exception as e:
            fail("float_fields_skipped", f"raised exception: {e}")


def test_missing_image_skipped():
    """Annotation file with no matching image is skipped gracefully."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        ann_dir = tmp / "train" / "_annotations"
        ann_dir.mkdir(parents=True)
        (tmp / "train" / "images").mkdir(parents=True)
        make_annotation(ann_dir / "ghost.txt", ["10,10,20,20,1,1,0,0"])
        # No image named ghost.jpg

        try:
            n = run_convert(tmp, "train")
            ok("missing_image_skipped")
        except Exception as e:
            fail("missing_image_skipped", f"raised exception: {e}")


def test_empty_annotation_file():
    """An empty annotation file produces an empty label file without crashing."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        setup_split(tmp, "train",
                    images={"img8": (200, 200)},
                    annotations={"img8": []})
        run_convert(tmp, "train")
        rows = read_label(tmp, "train", "img8")

        if rows is None:
            fail("empty_annotation_file", "label file not created")
        elif len(rows) != 0:
            fail("empty_annotation_file", f"expected 0 rows, got {len(rows)}")
        else:
            ok("empty_annotation_file")


def test_multiple_images_all_converted():
    """All images in a split are converted, return count matches."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        images = {f"frame{i:03d}": (320, 240) for i in range(5)}
        annotations = {f"frame{i:03d}": ["10,10,40,40,1,1,0,0"] for i in range(5)}
        setup_split(tmp, "val", images=images, annotations=annotations)
        n = run_convert(tmp, "val")

        if n != 5:
            fail("multiple_images", f"expected 5 converted, got {n}")
        else:
            ok("multiple_images")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 55)
    print("Data Preprocessing Tests")
    print("=" * 55)

    print("\n[Annotation Conversion]")
    test_basic_conversion()
    test_category_mapping()
    test_skip_score_zero()
    test_skip_ignored_categories()
    test_clamp_out_of_bounds_box()
    test_skip_zero_area_box()

    print("\n[Robustness / Edge Cases]")
    test_malformed_annotation_line_skipped()
    test_float_fields_in_annotation_skipped()
    test_missing_image_skipped()
    test_empty_annotation_file()
    test_multiple_images_all_converted()

    print("\n" + "=" * 55)
    print(f"Results: {PASSED} passed, {FAILED} failed")
    print("=" * 55)

    sys.exit(0 if FAILED == 0 else 1)
