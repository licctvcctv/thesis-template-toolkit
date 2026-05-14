"""GhostConv-based lightweight modules for YOLO."""

import torch
import torch.nn as nn

from ultralytics.nn.modules.conv import Conv, GhostConv, autopad


class GhostBottleneck(nn.Module):
    """Ghost Bottleneck block with residual connection."""

    def __init__(self, c1, c2, k=3, s=1):
        super().__init__()
        c_ = c2 // 2
        self.conv = nn.Sequential(
            GhostConv(c1, c_, 1, 1),
            nn.BatchNorm2d(c_) if s == 2 else nn.Identity(),
            nn.Conv2d(c_, c_, k, s, autopad(k), groups=c_, bias=False) if s == 2 else nn.Identity(),
            nn.BatchNorm2d(c_) if s == 2 else nn.Identity(),
            GhostConv(c_, c2, 1, 1, act=False),
        )
        self.shortcut = (
            nn.Sequential(
                nn.Conv2d(c1, c1, k, s, autopad(k), groups=c1, bias=False),
                nn.BatchNorm2d(c1),
                nn.Conv2d(c1, c2, 1, 1, bias=False),
                nn.BatchNorm2d(c2),
            )
            if s == 2 or c1 != c2
            else nn.Identity()
        )

    def forward(self, x):
        return self.conv(x) + self.shortcut(x)


class C2f_Ghost(nn.Module):
    """C2f module with GhostBottleneck — drop-in replacement for C2f in YOLO backbone."""

    def __init__(self, c1, c2, n=1, shortcut=False, g=1, e=0.5):
        super().__init__()
        self.c = int(c2 * e)
        self.cv1 = Conv(c1, 2 * self.c, 1, 1)
        self.cv2 = Conv((2 + n) * self.c, c2, 1)
        self.m = nn.ModuleList(GhostBottleneck(self.c, self.c) for _ in range(n))

    def forward(self, x):
        y = list(self.cv1(x).chunk(2, 1))
        y.extend(m(y[-1]) for m in self.m)
        return self.cv2(torch.cat(y, 1))
