"""Download and convert VisDrone2019-DET dataset to YOLO format.

VisDrone annotation format (per line):
    bbox_left, bbox_top, bbox_width, bbox_height, score, category, truncation, occlusion

Conversion rules:
    - Skip objects with score == 0
    - Skip category 0 (ignored) and 11 (others)
    - Map category 1-10 to class 0-9
    - Convert bbox to YOLO normalized xywh center format
"""

import os
import sys
import shutil
import time
from pathlib import Path

import cv2

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _resolve_dataset_dir() -> Path:
    """Resolve the dataset directory the same way Ultralytics does.

    Ultralytics resolves the ``path`` field in a dataset yaml as:
        Path(settings["datasets_dir"]) / yaml_path

    This function reads that setting so ``prepare_dataset.py`` always saves
    data to the exact location Ultralytics will look for it.
    """
    # "VisDrone" mirrors the `path:` field in configs/dataset/visdrone.yaml.
    # Ultralytics resolves it as: DATASETS_DIR / "VisDrone"
    yaml_path = Path("VisDrone")
    try:
        from ultralytics.utils import DATASETS_DIR  # type: ignore
        resolved = (Path(DATASETS_DIR) / yaml_path).resolve()
        print(f"[prepare_dataset] Dataset directory (from ultralytics settings): {resolved}")
        return resolved
    except Exception:
        fallback = (PROJECT_ROOT / "datasets" / "VisDrone").resolve()
        print(f"[prepare_dataset] Dataset directory (fallback): {fallback}")
        return fallback


DATASET_DIR = _resolve_dataset_dir()

# VisDrone download URLs (Google Drive)
SPLITS = {
    "train": {
        "images": "https://drive.google.com/uc?id=1a2oHjcEcwXP8oUF95qiwrqzACb2YlUhn",
        "annotations": "https://drive.google.com/uc?id=1bxK5zgLn0_L8x276eKkuYA_FzwCIjb59",
    },
    "val": {
        "images": "https://drive.google.com/uc?id=1PFkRpW7IQOZpFnsDqH0GFcCAOQGm62Il",
        "annotations": "https://drive.google.com/uc?id=1B1RoKIJm2cBMovdPnMkIdiNPk4Kjl9Ms",
    },
    "test": {
        "images": "https://drive.google.com/uc?id=1PFkRpW7IQOZpFnsDqH0GFcCAOQGm62Il",
        "annotations": "https://drive.google.com/uc?id=1B1RoKIJm2cBMovdPnMkIdiNPk4Kjl9Ms",
    },
}

MAX_RETRIES = 3

# VisDrone category mapping: category_id -> yolo_class_id
# Category 0 = ignored, 1-10 = valid classes, 11 = others (skip)
CATEGORY_MAP = {i: i - 1 for i in range(1, 11)}  # {1:0, 2:1, ..., 10:9}


def download_visdrone_auto():
    """Download VisDrone dataset using ultralytics built-in downloader (preferred)."""
    print("Attempting to download VisDrone via ultralytics built-in...")
    try:
        from ultralytics.data.utils import check_det_dataset
        # ultralytics has a built-in VisDrone.yaml that handles download
        check_det_dataset("VisDrone.yaml")
        print("Download via ultralytics successful!")
        return True
    except Exception as e:
        print(f"Ultralytics auto-download failed: {e}")
        return False


def download_visdrone_gdown():
    """Download VisDrone dataset using gdown from Google Drive."""
    import gdown
    import zipfile

    tmp_dir = DATASET_DIR / "_tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    for split_name, urls in SPLITS.items():
        print(f"\n--- Downloading {split_name} split ---")
        split_dir = DATASET_DIR / split_name
        if (split_dir / "images").exists() and len(list((split_dir / "images").iterdir())) > 0:
            print(f"  {split_name} already exists, skipping download.")
            continue

        for data_type, url in urls.items():
            zip_path = tmp_dir / f"{split_name}_{data_type}.zip"
            if not zip_path.exists():
                print(f"  Downloading {data_type}...")
                for attempt in range(MAX_RETRIES):
                    try:
                        gdown.download(url, str(zip_path), quiet=False)
                        break
                    except Exception as e:
                        print(f"  Download attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
                        if attempt < MAX_RETRIES - 1:
                            time.sleep(2 ** attempt)
                        else:
                            raise
                if not zipfile.is_zipfile(zip_path):
                    raise RuntimeError(f"Downloaded file is not a valid zip: {zip_path}")

            print(f"  Extracting {data_type}...")
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(str(tmp_dir))

    # Organize extracted files into expected structure
    print("\nOrganizing files...")
    _organize_extracted(tmp_dir)

    # Cleanup
    shutil.rmtree(tmp_dir, ignore_errors=True)
    print("Temporary files cleaned up.")


def _organize_extracted(tmp_dir):
    """Move extracted VisDrone files into the expected directory structure."""
    # VisDrone extracts into folders like VisDrone2019-DET-train/
    for split in ["train", "val", "test"]:
        img_dst = DATASET_DIR / split / "images"
        img_dst.mkdir(parents=True, exist_ok=True)

        # Find the extracted image directory
        possible_dirs = [
            tmp_dir / f"VisDrone2019-DET-{split}" / "images",
            tmp_dir / f"VisDrone2019-DET-{split}",
        ]
        for src_dir in possible_dirs:
            if src_dir.exists():
                for f in src_dir.glob("*.jpg"):
                    shutil.copy2(f, img_dst / f.name)
                for f in src_dir.glob("*.png"):
                    shutil.copy2(f, img_dst / f.name)
                break

        # Find and store raw annotations temporarily for conversion
        ann_dst = DATASET_DIR / split / "_annotations"
        ann_dst.mkdir(parents=True, exist_ok=True)
        possible_ann_dirs = [
            tmp_dir / f"VisDrone2019-DET-{split}" / "annotations",
        ]
        for src_dir in possible_ann_dirs:
            if src_dir.exists():
                for f in src_dir.glob("*.txt"):
                    shutil.copy2(f, ann_dst / f.name)
                break


def convert_visdrone_to_yolo(split):
    """Convert VisDrone annotations to YOLO format for a given split.

    Args:
        split: One of 'train', 'val', 'test'.
    """
    # Support both manual-download layout ({split}/images) and
    # the ultralytics layout (images/{split}); annotations always
    # come from the manual path since ultralytics already converts them.
    img_dir = DATASET_DIR / split / "images"
    ann_dir = DATASET_DIR / split / "_annotations"
    label_dir = DATASET_DIR / split / "labels"
    label_dir.mkdir(parents=True, exist_ok=True)


    if not ann_dir.exists():
        print(f"  No annotations found for {split}, skipping conversion.")
        return 0

    ann_files = sorted(ann_dir.glob("*.txt"))
    converted = 0
    skipped = 0

    for ann_file in ann_files:
        # Find corresponding image to get dimensions
        img_name = ann_file.stem
        img_path = None
        for ext in [".jpg", ".jpeg", ".png"]:
            candidate = img_dir / (img_name + ext)
            if candidate.exists():
                img_path = candidate
                break

        if img_path is None:
            skipped += 1
            continue

        img = cv2.imread(str(img_path))
        if img is None:
            skipped += 1
            continue

        img_h, img_w = img.shape[:2]
        yolo_lines = []

        with open(ann_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(",")
                if len(parts) < 8:
                    continue

                try:
                    bbox_left = int(parts[0].strip())
                    bbox_top  = int(parts[1].strip())
                    bbox_w    = int(parts[2].strip())
                    bbox_h    = int(parts[3].strip())
                    score     = int(parts[4].strip())
                    category  = int(parts[5].strip())
                except ValueError:
                    skipped += 1
                    continue

                # Skip: score == 0, category 0 (ignored), category 11 (others)
                if score == 0 or category not in CATEGORY_MAP:
                    continue

                class_id = CATEGORY_MAP[category]

                # Convert to YOLO format: normalized center_x, center_y, width, height
                cx = (bbox_left + bbox_w / 2.0) / img_w
                cy = (bbox_top + bbox_h / 2.0) / img_h
                nw = bbox_w / img_w
                nh = bbox_h / img_h

                # Clamp to [0, 1]
                cx = max(0.0, min(1.0, cx))
                cy = max(0.0, min(1.0, cy))
                nw = max(0.0, min(1.0, nw))
                nh = max(0.0, min(1.0, nh))

                # Skip zero-area boxes
                if nw <= 0 or nh <= 0:
                    continue

                yolo_lines.append(f"{class_id} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}")

        # Write YOLO label file
        label_path = label_dir / (img_name + ".txt")
        with open(label_path, "w") as f:
            f.write("\n".join(yolo_lines))
        converted += 1

    # Cleanup raw annotations
    shutil.rmtree(ann_dir, ignore_errors=True)

    return converted


def _split_dirs(split: str):
    """Return (img_dir, label_dir) for a split, supporting both layouts.

    Ultralytics built-in download layout:  DATASET_DIR/images/{split}/
    Manual gdown layout:                   DATASET_DIR/{split}/images/
    """
    # Ultralytics layout (preferred)
    ul_img = DATASET_DIR / "images" / split
    ul_lbl = DATASET_DIR / "labels" / split
    if ul_img.exists():
        return ul_img, ul_lbl

    # Manual layout fallback
    return DATASET_DIR / split / "images", DATASET_DIR / split / "labels"


def verify_dataset():
    """Print dataset statistics and verify a few samples."""
    print("\n=== Dataset Verification ===")
    for split in ["train", "val", "test"]:
        img_dir, label_dir = _split_dirs(split)
        if not img_dir.exists():
            print(f"  {split}: NOT FOUND")
            continue

        n_images = len(list(img_dir.glob("*.*")))
        n_labels = len(list(label_dir.glob("*.txt"))) if label_dir.exists() else 0
        print(f"  {split}: {n_images} images, {n_labels} labels")

        # Show sample label
        if label_dir.exists():
            sample = next(label_dir.iterdir(), None)
            if sample:
                with open(sample) as f:
                    lines = f.readlines()
                print(f"    Sample ({sample.name}): {len(lines)} objects")
                if lines:
                    print(f"    First line: {lines[0].strip()}")


def main():
    print("=" * 60)
    print("VisDrone2019-DET Dataset Preparation")
    print("=" * 60)

    DATASET_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Download
    # Ultralytics built-in download already produces YOLO-format labels,
    # so skip our custom conversion step when it succeeds.
    auto_ok = download_visdrone_auto()
    if not auto_ok:
        print("\nFalling back to gdown download...")
        download_visdrone_gdown()

        # Step 2: Convert raw annotations → YOLO format (gdown path only)
        print("\n--- Converting annotations to YOLO format ---")
        for split in ["train", "val", "test"]:
            n = convert_visdrone_to_yolo(split)
            print(f"  {split}: converted {n} annotations")
    else:
        print("\n--- Skipping conversion: ultralytics download already provides YOLO labels ---")

    # Step 3: Verify
    verify_dataset()

    print("\nDataset preparation complete!")
    print(f"Dataset location: {DATASET_DIR}")


if __name__ == "__main__":
    main()
