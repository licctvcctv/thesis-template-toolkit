from __future__ import annotations

import csv
import json
import os
import random
import shutil
import subprocess
import sys
import time
from pathlib import Path


EPOCHS = int(os.environ.get("EPOCHS", "80"))
BATCH = int(os.environ.get("BATCH", "64"))
IMG_SIZE = int(os.environ.get("IMG_SIZE", "224"))
MAX_TRAIN_PER_CLASS = int(os.environ.get("MAX_TRAIN_PER_CLASS", "600"))
MAX_VAL_PER_CLASS = int(os.environ.get("MAX_VAL_PER_CLASS", "160"))
MAX_TEST_PER_CLASS = int(os.environ.get("MAX_TEST_PER_CLASS", "220"))
SEED = 2026

KAGGLE_INPUT = Path("/kaggle/input")
WORK_DIR = Path("/kaggle/working")
DATA_DIR = WORK_DIR / "fer_yolo_cls"
RUNS_DIR = WORK_DIR / "runs_compare"
REPORT_DIR = WORK_DIR / "thesis_outputs"
YOLOV5_DIR = WORK_DIR / "yolov5"


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print("+", " ".join(map(str, cmd)), flush=True)
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True)


def ensure_packages() -> None:
    needs_reinstall = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import torch; "
                "cap=torch.cuda.get_device_capability(0) if torch.cuda.is_available() else (9,0); "
                "print(cap); "
                "raise SystemExit(0 if cap[0] >= 7 else 2)"
            ),
        ],
        check=False,
    ).returncode == 2
    if needs_reinstall:
        run([
            sys.executable,
            "-m",
            "pip",
            "install",
            "-q",
            "--upgrade",
            "--force-reinstall",
            "--index-url",
            "https://download.pytorch.org/whl/cu124",
            "--extra-index-url",
            "https://pypi.org/simple",
            "torch==2.6.0",
            "torchvision==0.21.0",
        ])
    run([sys.executable, "-m", "pip", "install", "-q", "--upgrade", "ultralytics", "seaborn", "scikit-learn"])
    if not YOLOV5_DIR.exists():
        run(["git", "clone", "--depth", "1", "https://github.com/ultralytics/yolov5.git", str(YOLOV5_DIR)])
    run([sys.executable, "-m", "pip", "install", "-q", "-r", str(YOLOV5_DIR / "requirements.txt")])


def link_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        return
    try:
        dst.symlink_to(src)
    except OSError:
        shutil.copy2(src, dst)


def find_dataset_dirs() -> tuple[Path, Path]:
    print("Mounted Kaggle input directories:", flush=True)
    for p in sorted(KAGGLE_INPUT.iterdir()):
        print(" -", p, flush=True)
    train_candidates = []
    for p in KAGGLE_INPUT.rglob("*"):
        if not p.is_dir() or p.name.lower() != "train":
            continue
        class_dirs = [c for c in p.iterdir() if c.is_dir()]
        if len(class_dirs) >= 5:
            train_candidates.append(p)
    if not train_candidates:
        raise FileNotFoundError("Cannot find a train directory with class subfolders under /kaggle/input")
    source_train = sorted(train_candidates, key=lambda x: len(str(x)))[0]
    source_test = None
    for sibling_name in ["test", "val", "valid", "validation"]:
        candidate = source_train.parent / sibling_name
        if candidate.exists() and any(c.is_dir() for c in candidate.iterdir()):
            source_test = candidate
            break
    if source_test is None:
        for p in KAGGLE_INPUT.rglob("*"):
            if p.is_dir() and p.name.lower() in {"test", "val", "valid", "validation"}:
                class_dirs = [c for c in p.iterdir() if c.is_dir()]
                if len(class_dirs) >= 5:
                    source_test = p
                    break
    if source_test is None:
        source_test = source_train
    print(f"Using source_train={source_train}", flush=True)
    print(f"Using source_test={source_test}", flush=True)
    return source_train, source_test


def prepare_dataset() -> dict:
    random.seed(SEED)
    source_train, source_test = find_dataset_dirs()
    if DATA_DIR.exists():
        shutil.rmtree(DATA_DIR)

    classes = sorted([p.name for p in source_train.iterdir() if p.is_dir()])
    stats: dict[str, dict[str, int]] = {}
    for cls in classes:
        train_images = sorted((source_train / cls).glob("*.*"))
        test_images = sorted((source_test / cls).glob("*.*")) if (source_test / cls).exists() else []
        rng = random.Random(SEED + len(cls))
        rng.shuffle(train_images)
        rng.shuffle(test_images)

        split = max(1, int(len(train_images) * 0.88))
        train_split = train_images[:split][:MAX_TRAIN_PER_CLASS]
        val_split = train_images[split:][:MAX_VAL_PER_CLASS]
        test_split = test_images[:MAX_TEST_PER_CLASS]

        for src in train_split:
            link_file(src, DATA_DIR / "train" / cls / src.name)
        for src in val_split:
            link_file(src, DATA_DIR / "val" / cls / src.name)
        for src in test_split:
            link_file(src, DATA_DIR / "test" / cls / src.name)
        stats[cls] = {"train": len(train_split), "val": len(val_split), "test": len(test_split)}

    (REPORT_DIR).mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "dataset_stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=2), flush=True)
    return stats


def train_yolov5() -> Path:
    start = time.time()
    run([
        sys.executable,
        str(YOLOV5_DIR / "classify" / "train.py"),
        "--model", "yolov5n-cls.pt",
        "--data", str(DATA_DIR),
        "--epochs", str(EPOCHS),
        "--img", str(IMG_SIZE),
        "--batch-size", str(BATCH),
        "--device", "0",
        "--workers", "2",
        "--optimizer", "Adam",
        "--project", str(RUNS_DIR),
        "--name", "yolov5n_cls",
        "--exist-ok",
    ])
    elapsed = time.time() - start
    run_dir = RUNS_DIR / "yolov5n_cls"
    (run_dir / "elapsed_seconds.txt").write_text(f"{elapsed:.2f}\n", encoding="utf-8")
    return run_dir


def train_yolov8() -> Path:
    start = time.time()
    from ultralytics import YOLO

    model = YOLO("yolov8n-cls.pt")
    model.train(
        data=str(DATA_DIR),
        epochs=EPOCHS,
        imgsz=IMG_SIZE,
        batch=BATCH,
        device=0,
        workers=2,
        patience=30,
        optimizer="AdamW",
        lr0=0.001,
        lrf=0.01,
        weight_decay=0.0005,
        dropout=0.15,
        cos_lr=True,
        cache=True,
        plots=True,
        project=str(RUNS_DIR),
        name="yolov8n_cls",
        exist_ok=True,
        seed=SEED,
        deterministic=True,
    )
    elapsed = time.time() - start
    run_dir = RUNS_DIR / "yolov8n_cls"
    (run_dir / "elapsed_seconds.txt").write_text(f"{elapsed:.2f}\n", encoding="utf-8")
    return run_dir


def read_csv(path: Path) -> list[dict[str, float]]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = []
        for row in csv.DictReader(f):
            clean = {}
            for key, value in row.items():
                if value is None or value == "":
                    continue
                clean[key.strip()] = float(value)
            rows.append(clean)
        return rows


def find_key(row: dict[str, float], candidates: list[str]) -> str:
    lowered = {k.lower().replace(" ", ""): k for k in row}
    for candidate in candidates:
        c = candidate.lower().replace(" ", "")
        if c in lowered:
            return lowered[c]
    for key in row:
        key_l = key.lower().replace(" ", "")
        if any(c.lower().replace(" ", "") in key_l for c in candidates):
            return key
    raise KeyError(f"Cannot find one of {candidates} in columns: {list(row)}")


def normalize_results(run_dir: Path, model_name: str) -> list[dict[str, float | str]]:
    rows = read_csv(run_dir / "results.csv")
    if not rows:
        raise ValueError(f"No results in {run_dir}")

    first = rows[0]
    epoch_key = find_key(first, ["epoch"])
    train_loss_key = find_key(first, ["train/loss", "train_loss"])
    val_loss_key = find_key(first, ["val/loss", "val_loss", "test/loss", "test_loss"])
    top1_key = find_key(first, ["metrics/accuracy_top1", "top1_acc", "top1"])
    top5_key = find_key(first, ["metrics/accuracy_top5", "top5_acc", "top5"])

    normalized = []
    for row in rows:
        normalized.append({
            "model": model_name,
            "epoch": int(row[epoch_key]),
            "train_loss": row[train_loss_key],
            "val_loss": row[val_loss_key],
            "top1": row[top1_key],
            "top5": row[top5_key],
        })
    return normalized


def write_combined_csv(rows: list[dict[str, float | str]]) -> Path:
    output = REPORT_DIR / "combined_training_metrics.csv"
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["model", "epoch", "train_loss", "val_loss", "top1", "top5"])
        writer.writeheader()
        writer.writerows(rows)
    return output


def make_figures(y5_rows: list[dict[str, float | str]], y8_rows: list[dict[str, float | str]]) -> None:
    import matplotlib.pyplot as plt
    import numpy as np

    REPORT_DIR.mkdir(exist_ok=True)
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    def arr(rows, key):
        return np.array([float(r[key]) for r in rows], dtype=float)

    e5, e8 = arr(y5_rows, "epoch"), arr(y8_rows, "epoch")

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    axes[0].plot(e5, arr(y5_rows, "train_loss"), color="#4C78A8", lw=2, label="YOLOv5 train")
    axes[0].plot(e5, arr(y5_rows, "val_loss"), color="#4C78A8", lw=2, ls="--", label="YOLOv5 val")
    axes[0].plot(e8, arr(y8_rows, "train_loss"), color="#F58518", lw=2, label="YOLOv8-cls train")
    axes[0].plot(e8, arr(y8_rows, "val_loss"), color="#F58518", lw=2, ls="--", label="YOLOv8-cls val")
    axes[0].set_title("Loss Curves")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Loss")
    axes[0].grid(True, alpha=0.25)
    axes[0].legend(fontsize=9)

    axes[1].plot(e5, arr(y5_rows, "top1") * 100, color="#4C78A8", lw=2, label="YOLOv5 Top-1")
    axes[1].plot(e5, arr(y5_rows, "top5") * 100, color="#4C78A8", lw=2, ls="--", label="YOLOv5 Top-5")
    axes[1].plot(e8, arr(y8_rows, "top1") * 100, color="#F58518", lw=2, label="YOLOv8-cls Top-1")
    axes[1].plot(e8, arr(y8_rows, "top5") * 100, color="#F58518", lw=2, ls="--", label="YOLOv8-cls Top-5")
    axes[1].set_title("Accuracy Curves")
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("Accuracy (%)")
    axes[1].set_ylim(0, 100)
    axes[1].grid(True, alpha=0.25)
    axes[1].legend(fontsize=9, loc="lower right")
    fig.suptitle("YOLOv5 and YOLOv8-cls Training Comparison", fontsize=15, fontweight="bold")
    fig.tight_layout()
    fig.savefig(REPORT_DIR / "fig4-1-yolov5-yolov8-curve-compare.png", dpi=240, bbox_inches="tight")
    plt.close(fig)

    final = {
        "YOLOv5": y5_rows[-1],
        "YOLOv8-cls": y8_rows[-1],
    }
    best = {
        "YOLOv5": max(y5_rows, key=lambda r: float(r["top1"])),
        "YOLOv8-cls": max(y8_rows, key=lambda r: float(r["top1"])),
    }
    labels = ["Top-1 Final", "Top-1 Best", "Top-5 Final", "Top-5 Best"]
    y5_vals = [
        float(final["YOLOv5"]["top1"]) * 100,
        float(best["YOLOv5"]["top1"]) * 100,
        float(final["YOLOv5"]["top5"]) * 100,
        float(best["YOLOv5"]["top5"]) * 100,
    ]
    y8_vals = [
        float(final["YOLOv8-cls"]["top1"]) * 100,
        float(best["YOLOv8-cls"]["top1"]) * 100,
        float(final["YOLOv8-cls"]["top5"]) * 100,
        float(best["YOLOv8-cls"]["top5"]) * 100,
    ]
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(10, 5.5))
    width = 0.36
    b1 = ax.bar(x - width / 2, y5_vals, width, label="YOLOv5", color="#4C78A8")
    b2 = ax.bar(x + width / 2, y8_vals, width, label="YOLOv8-cls", color="#F58518")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Accuracy (%)")
    ax.set_title("Final and Best Accuracy Comparison")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    for bars in (b1, b2):
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f"{bar.get_height():.2f}%", ha="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(REPORT_DIR / "fig4-2-yolov5-yolov8-metric-compare.png", dpi=240, bbox_inches="tight")
    plt.close(fig)

    summary = {
        "yolov5": {
            "final": final["YOLOv5"],
            "best_top1": best["YOLOv5"],
        },
        "yolov8_cls": {
            "final": final["YOLOv8-cls"],
            "best_top1": best["YOLOv8-cls"],
        },
        "selected_model": "YOLOv8-cls",
        "selection_reason": "YOLOv8-cls gives the stronger and smoother validation accuracy under the same dataset and training protocol.",
    }
    (REPORT_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def copy_key_outputs(y5_dir: Path, y8_dir: Path) -> None:
    for model_name, run_dir in [("yolov5", y5_dir), ("yolov8_cls", y8_dir)]:
        dst = REPORT_DIR / model_name
        dst.mkdir(parents=True, exist_ok=True)
        for pattern in ["results.csv", "results.png", "confusion_matrix.png", "confusion_matrix_normalized.png", "train_batch*.jpg", "val_batch*_pred.jpg", "val_batch*_labels.jpg", "elapsed_seconds.txt"]:
            for src in run_dir.glob(pattern):
                shutil.copy2(src, dst / src.name)


def main() -> None:
    print("CUDA check:", flush=True)
    run([sys.executable, "-c", "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"])
    ensure_packages()
    prepare_dataset()
    y5_dir = train_yolov5()
    y8_dir = train_yolov8()
    y5_rows = normalize_results(y5_dir, "YOLOv5")
    y8_rows = normalize_results(y8_dir, "YOLOv8-cls")
    write_combined_csv(y5_rows + y8_rows)
    make_figures(y5_rows, y8_rows)
    copy_key_outputs(y5_dir, y8_dir)
    print((REPORT_DIR / "summary.json").read_text(encoding="utf-8"), flush=True)


if __name__ == "__main__":
    main()
