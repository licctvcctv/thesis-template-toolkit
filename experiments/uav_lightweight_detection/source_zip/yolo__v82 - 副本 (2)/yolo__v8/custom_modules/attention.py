"""CBAM: Convolutional Block Attention Module.

Applies sequential channel and spatial attention to adaptively recalibrate
feature responses. Acts as a drop-in passthrough module (same input/output
channels and spatial dimensions).

Reference: Woo et al., ECCV 2018 — https://arxiv.org/abs/1807.06521
"""

import torch
import torch.nn as nn


class ChannelAttention(nn.Module):
    """Channel attention via global avg-pool + max-pool → shared MLP → sigmoid."""

    def __init__(self, channels, reduction=16):
        super().__init__()
        mid = max(channels // reduction, 1)
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.max_pool = nn.AdaptiveMaxPool2d(1)
        self.mlp = nn.Sequential(
            nn.Conv2d(channels, mid, 1, bias=False),
            nn.ReLU(inplace=True),
            nn.Conv2d(mid, channels, 1, bias=False),
        )
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        avg = self.mlp(self.avg_pool(x))
        mx = self.mlp(self.max_pool(x))
        return x * self.sigmoid(avg + mx)


class SpatialAttention(nn.Module):
    """Spatial attention via channel-wise avg + max → conv → sigmoid."""

    def __init__(self, kernel_size=7):
        super().__init__()
        self.conv = nn.Conv2d(2, 1, kernel_size, padding=kernel_size // 2, bias=False)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        avg = x.mean(dim=1, keepdim=True)
        mx = x.max(dim=1, keepdim=True).values
        attn = torch.cat([avg, mx], dim=1)
        return x * self.sigmoid(self.conv(attn))


class CBAM(nn.Module):
    """CBAM: channel attention followed by spatial attention.

    Usage in YAML:  [-1, 1, CBAM, [<channels>]]
    The module is channel/spatial passthrough — input shape equals output shape.
    """

    def __init__(self, channels, reduction=16, kernel_size=7):
        super().__init__()
        self.ca = ChannelAttention(channels, reduction)
        self.sa = SpatialAttention(kernel_size)

    def forward(self, x):
        return self.sa(self.ca(x))
