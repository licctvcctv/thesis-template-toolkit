"""Evaluate all trained models and collect metrics for comparison.

Metrics: mAP50, mAP50-95, Params(M), GFLOPs, FPS, per-class AP50.
Outputs: results/evaluation_results.csv

Usage:
  python evaluate_all.py
"""

import time
from pathlib import Path

import pandas as pd
import torch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_CFG     = PROJECT_ROOT / "configs" / "dataset" / "visdrone.yaml"
RUNS_DIR     = PROJECT_ROOT / "runs"
RESULTS_DIR  = PROJECT_ROOT / "results"

CLASS_NAMES = [
    "pedestrian", "people", "bicycle", "car", "van",
    "truck", "tricycle", "awning-tricycle", "bus", "motor",
]

# Models to evaluate: (display_name, weights_path, needs_custom_modules)
MODELS_TO_EVAL = [
    ("YOLOv8s",            RUNS_DIR / "yolov8s"            / "train/weights/best.pt", False),
    ("YOLOv8s-Ghost",      RUNS_DIR / "yolov8s-ghost"      / "train/weights/best.pt", True),
    ("YOLOv8s-Ghost-CBAM", RUNS_DIR / "yolov8s-ghost-cbam" / "train/weights/best.pt", True),
    ("YOLOv8s-Improved",   RUNS_DIR / "yolov8s-improved"   / "train/weights/best.pt", True),
]


def get_model_info(model):
    from thop import profile
    device = next(model.model.parameters()).device
    dummy  = torch.randn(1, 3, 640, 640).to(device)
    try:
        flops, params = profile(model.model, inputs=(dummy,), verbose=False)
        return params / 1e6, flops / 1e9
    except Exception:
        return sum(p.numel() for p in model.model.parameters()) / 1e6, None


def measure_fps(model, imgsz=640, warmup=10, runs=100):
    device = next(model.model.parameters()).device
    dummy  = torch.randn(1, 3, imgsz, imgsz).to(device)
    for _ in range(warmup):
        model.model(dummy)
    if device.type == "cuda":
        torch.cuda.synchronize()
    t0 = time.perf_counter()
    for _ in range(runs):
        model.model(dummy)
    if device.type == "cuda":
        torch.cuda.synchronize()
    return runs / (time.perf_counter() - t0)


def evaluate_model(display_name, weights_path, needs_custom):
    import sys
    from ultralytics import YOLO

    weights = Path(weights_path)
    if not weights.exists():
        print(f"  SKIPPED — weights not found: {weights}")
        return None

    if needs_custom:
        sys.path.insert(0, str(PROJECT_ROOT))
        from custom_modules import register_custom_modules
        register_custom_modules()

    print(f"  Loading {display_name} ...")
    model = YOLO(str(weights))

    results = model.val(
        data=str(DATA_CFG),
        imgsz=640,
        batch=1,
        split="test",
        verbose=False,
    )

    params_m, gflops = get_model_info(model)
    fps = measure_fps(model)

    row = {
        "model":      display_name,
        "mAP50":      round(results.box.map50, 4),
        "mAP50-95":   round(results.box.map,   4),
        "Params(M)":  round(params_m, 2),
        "GFLOPs":     round(gflops, 2) if gflops is not None else "N/A",
        "FPS":        round(fps, 1),
    }

    if hasattr(results.box, "ap50"):
        ap50 = results.box.ap50
        if len(ap50) == len(CLASS_NAMES):
            for i, name in enumerate(CLASS_NAMES):
                row[f"AP50_{name}"] = round(float(ap50[i]), 4)

    return row


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    all_rows = []
    for display_name, weights_path, needs_custom in MODELS_TO_EVAL:
        print(f"\n{'='*50}\nEvaluating: {display_name}\n{'='*50}")
        row = evaluate_model(display_name, weights_path, needs_custom)
        if row:
            all_rows.append(row)
            print(f"  mAP50={row['mAP50']}  mAP50-95={row['mAP50-95']}  "
                  f"Params={row['Params(M)']}M  GFLOPs={row['GFLOPs']}  FPS={row['FPS']}")

    if not all_rows:
        print("\nNo models evaluated. Train models first:")
        print("  python scripts/train_ultralytics.py --model all")
        return

    df = pd.DataFrame(all_rows)
    csv_path = RESULTS_DIR / "evaluation_results.csv"
    df.to_csv(csv_path, index=False)

    print(f"\n\n{'='*70}")
    print("EVALUATION SUMMARY")
    print("="*70)
    cols = ["model", "Params(M)", "GFLOPs", "mAP50", "mAP50-95", "FPS"]
    print(df[[c for c in cols if c in df.columns]].to_string(index=False))
    print(f"\nSaved to {csv_path}")


if __name__ == "__main__":
    main()
