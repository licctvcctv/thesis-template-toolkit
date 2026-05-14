"""Train YOLO models on VisDrone dataset.

Models:
  yolov8s              — baseline (standard YOLOv8s)
  yolov8s-ghost        — ablation 1: Ghost backbone only
  yolov8s-ghost-cbam   — ablation 2: Ghost backbone + CBAM attention
  yolov8s-improved     — full model: Ghost + CBAM + Wise-IoU loss

Usage:
  python train_ultralytics.py --model yolov8s
  python train_ultralytics.py --model yolov8s-ghost
  python train_ultralytics.py --model yolov8s-ghost-cbam
  python train_ultralytics.py --model yolov8s-improved
  python train_ultralytics.py --model all
"""

import argparse
import sys
from pathlib import Path

import torch
from ultralytics import YOLO

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_CFG     = PROJECT_ROOT / "configs" / "dataset" / "visdrone.yaml"
IMPROVED_DIR = PROJECT_ROOT / "configs" / "improved"
OUTPUT_DIR   = PROJECT_ROOT / "runs"

MODELS = {
    "yolov8s": {
        "source": "yolov8s.pt",
        "type": "pretrained",
        "epochs": 100,
    },
    "yolov8s-ghost": {
        "source": str(IMPROVED_DIR / "yolov8s-ghost.yaml"),
        "type": "custom",
        "pretrained_weights": "yolov8s.pt",
        "epochs": 100,
    },
    "yolov8s-ghost-cbam": {
        "source": str(IMPROVED_DIR / "yolov8s-ghost-cbam.yaml"),
        "type": "custom",
        "pretrained_weights": "yolov8s.pt",
        "epochs": 100,
    },
    "yolov8s-improved": {
        # Same architecture as ghost-cbam; Wise-IoU loss applied via custom trainer
        "source": str(IMPROVED_DIR / "yolov8s-ghost-cbam.yaml"),
        "type": "custom",
        "pretrained_weights": "yolov8s.pt",
        "epochs": 150,
        "use_wise_iou": True,
        "extra_args": {
            "optimizer": "AdamW",
            "lr0": 0.001,
            "copy_paste": 0.3,
        },
    },
}


def register_modules():
    sys.path.insert(0, str(PROJECT_ROOT))
    from custom_modules import register_custom_modules
    register_custom_modules()


def _transfer_pretrained(model, weights_path):
    """Transfer matching layers from a pretrained checkpoint."""
    try:
        pretrained = YOLO(weights_path)
        src = pretrained.model.state_dict()
        dst = model.model.state_dict()
        matched = sum(
            1 for k, v in src.items()
            if k in dst and dst[k].shape == v.shape and dst[k].dtype == v.dtype
        )
        model.model.load_state_dict(
            {k: src[k] if (k in src and dst[k].shape == src[k].shape) else dst[k]
             for k in dst},
            strict=False,
        )
        print(f"  Transferred {matched}/{len(dst)} pretrained layers from {weights_path}")
    except Exception as e:
        print(f"  Warning: pretrained transfer failed ({e}). Training from scratch.")


def train_model(model_name, resume=False):
    if model_name not in MODELS:
        print(f"Unknown model: {model_name}. Available: {list(MODELS.keys())}")
        return

    cfg     = MODELS[model_name]
    run_dir = OUTPUT_DIR / model_name

    print(f"\n{'='*60}\nTraining: {model_name}\n{'='*60}")

    if cfg["type"] == "custom":
        register_modules()

    model = YOLO(cfg["source"])

    if cfg["type"] == "custom" and "pretrained_weights" in cfg:
        _transfer_pretrained(model, cfg["pretrained_weights"])

    _device = 0 if torch.cuda.is_available() else "cpu"
    train_args = {
        "data":      str(DATA_CFG),
        "epochs":    cfg["epochs"],
        "imgsz":     640,
        "batch":     16,
        "project":   str(run_dir),
        "name":      "train",
        "exist_ok":  True,
        "pretrained": cfg["type"] == "pretrained",
        "mosaic":    1.0,
        "cache":     True,
        "workers":   4,
        "device":    _device,
        "verbose":   True,
    }
    train_args.update(cfg.get("extra_args", {}))

    if resume:
        train_args["resume"] = True

    # Wise-IoU: pass custom trainer class
    if cfg.get("use_wise_iou"):
        sys.path.insert(0, str(PROJECT_ROOT))
        from custom_modules.wise_iou import WiseIoUTrainer
        train_args["trainer"] = WiseIoUTrainer
        print("  Loss: Wise-IoU (dynamic quality-aware focusing)")

    print(f"  Source:  {cfg['source']}")
    print(f"  Data:    {DATA_CFG}")
    print(f"  Epochs:  {cfg['epochs']}")
    print(f"  Output:  {run_dir / 'train'}")

    results = model.train(**train_args)
    print(f"\nTraining complete for {model_name}!")
    return results


def main():
    parser = argparse.ArgumentParser(description="Train YOLO models on VisDrone")
    parser.add_argument(
        "--model",
        default="yolov8s",
        choices=list(MODELS.keys()) + ["all"],
        help="Model to train (default: yolov8s)",
    )
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    if args.model == "all":
        for name in MODELS:
            train_model(name, resume=args.resume)
    else:
        train_model(args.model, resume=args.resume)


if __name__ == "__main__":
    main()
