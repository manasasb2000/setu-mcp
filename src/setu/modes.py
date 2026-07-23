"""Live vs mock dispatch.

`SETU_MODE=mock` (the default) serves deterministic fixtures so CI, contributors,
and demos never burn Sarvam credits. `SETU_MODE=live` routes to the real Sarvam SDK.
"""

from __future__ import annotations

from .config import Mode


def is_mock(mode: Mode) -> bool:
    """True when the server should serve fixtures instead of calling Sarvam."""
    return mode == "mock"


def is_live(mode: Mode) -> bool:
    """True when the server should call the real Sarvam APIs."""
    return mode == "live"
