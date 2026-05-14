"""Wise-IoU: dynamic quality-aware bounding box regression loss.

Replaces the standard CIoU loss with a dynamically focused variant that
up-weights high-quality predictions (IoU > mean) and down-weights low-quality
ones, improving convergence on small/occluded objects in dense scenes.

Reference: inspired by WIoU (Zhang et al., 2023) — https://arxiv.org/abs/2301.10051

Usage:
    from custom_modules.wise_iou import WiseIoUTrainer
    model.train(data=..., trainer=WiseIoUTrainer)
"""

import torch
import torch.nn as nn

try:
    from ultralytics.models.yolo.detect import DetectionTrainer
except ImportError:
    from ultralytics.models.yolo.detect.train import DetectionTrainer

from ultralytics.utils.loss import BboxLoss, v8DetectionLoss
from ultralytics.utils.metrics import bbox_iou
from ultralytics.utils.tal import bbox2dist


class WiseIoUBboxLoss(BboxLoss):
    """BboxLoss with Wise-IoU dynamic focusing coefficient.

    β = clip(IoU / mean(IoU), 0.5, 2.0)

    High-quality matches (IoU >> mean) receive β > 1, amplifying their gradient
    and pushing the model to further refine already-decent predictions.
    Low-quality matches (IoU << mean) receive β < 1, suppressing gradient for
    hopeless detections and reducing noise from heavily occluded small targets.
    """

    def forward(
        self,
        pred_dist,
        pred_bboxes,
        anchor_points,
        target_bboxes,
        target_scores,
        target_scores_sum,
        fg_mask,
    ):
        weight = target_scores.sum(-1)[fg_mask].unsqueeze(-1)

        # CIoU base loss
        iou = bbox_iou(
            pred_bboxes[fg_mask], target_bboxes[fg_mask], xywh=False, CIoU=True
        )

        # Dynamic focusing: β adapts per-batch based on IoU quality distribution
        iou_d = iou.detach().clamp(min=0.0)
        n = iou_d.numel()
        iou_mean = iou_d.sum() / max(n, 1)
        beta = (iou_d / (iou_mean + 1e-6)).clamp(0.5, 2.0)

        loss_iou = ((1.0 - iou) * beta * weight).sum() / target_scores_sum

        # DFL loss (unchanged from parent)
        if self.use_dfl:
            target_ltrb = bbox2dist(anchor_points, target_bboxes, self.reg_max)
            loss_dfl = self._df_loss(pred_dist[fg_mask], target_ltrb[fg_mask]) * weight
            loss_dfl = loss_dfl.sum() / target_scores_sum
        else:
            loss_dfl = torch.tensor(0.0, device=pred_dist.device)

        return loss_iou, loss_dfl


class v8WiseIoUDetectionLoss(v8DetectionLoss):
    """v8DetectionLoss with WiseIoUBboxLoss replacing the standard BboxLoss."""

    def __init__(self, model, tal_topk=10):
        super().__init__(model, tal_topk)
        # Swap in the wise-iou bbox loss
        self.bbox_loss = WiseIoUBboxLoss(self.reg_max).to(self.device)


class WiseIoUTrainer(DetectionTrainer):
    """DetectionTrainer that uses Wise-IoU loss instead of standard CIoU."""

    def init_criterion(self):
        return v8WiseIoUDetectionLoss(self.model)
