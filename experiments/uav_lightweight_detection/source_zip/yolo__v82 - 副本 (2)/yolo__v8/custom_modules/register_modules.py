"""Register custom modules into ultralytics framework.

C2f_Ghost needs a C2f-like alias so parse_model injects c1 and scales depth (n).
CBAM is a passthrough module — parse_model handles it in the else-branch
(c2 = ch[f]), so no alias is needed.
"""

import ultralytics.nn.modules as modules_ns
import ultralytics.nn.tasks as tasks_ns
from ultralytics.nn.modules import C2f

from .ghost_modules import C2f_Ghost, GhostBottleneck
from .attention import CBAM

_CUSTOM_MODULES = {
    "C2f_Ghost": C2f_Ghost,
    "GhostBottleneck": GhostBottleneck,
    "CBAM": CBAM,
}


# ---------------------------------------------------------------------------
# Alias metaclass: makes C2f_Ghost appear as C2f inside parse_model frozensets
# ---------------------------------------------------------------------------

class _C2fLikeMeta(type):
    """Spoof C2f identity so parse_model injects c1 and scales repeat count n."""

    def __hash__(cls):
        return hash(C2f)

    def __eq__(cls, other):
        return other is C2f or type.__eq__(cls, other)


class C2f_GhostAlias(C2f_Ghost, metaclass=_C2fLikeMeta):
    """C2f_Ghost registered with C2f-like identity for parse_model."""


_REGISTERED = {
    "C2f_Ghost": C2f_GhostAlias,
    "CBAM": CBAM,  # no alias needed — passthrough, uses else-branch in parse_model
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def register_custom_modules():
    """Register all custom modules into ultralytics.

    After this call, YAML configs may reference C2f_Ghost and CBAM.
    parse_model will handle C2f_Ghost identically to C2f (c1 injection +
    depth scaling) and CBAM as a simple passthrough module.
    """
    for name, cls in _CUSTOM_MODULES.items():
        setattr(modules_ns, name, cls)

    for name, cls in _REGISTERED.items():
        setattr(tasks_ns, name, cls)

    # Patch parse_model to keep registrations fresh across module reloads
    _orig = tasks_ns.parse_model

    def _patched(d, ch, verbose=True):
        for name, cls in _REGISTERED.items():
            setattr(tasks_ns, name, cls)
        return _orig(d, ch, verbose)

    if not getattr(tasks_ns, "_custom_modules_registered", False):
        tasks_ns.parse_model = _patched
        tasks_ns._custom_modules_registered = True

    # Verify
    failed = [n for n, c in _REGISTERED.items() if getattr(tasks_ns, n, None) is not c]
    if failed:
        raise RuntimeError(f"[custom_modules] Registration failed for: {failed}")

    print(f"[custom_modules] Registered: {list(_CUSTOM_MODULES.keys())}")
