"""Importing this package registers every Setu tool on the shared FastMCP app."""

from __future__ import annotations

from . import health, speak, transcribe  # noqa: F401  (import side-effect: registration)

__all__ = ["health", "speak", "transcribe"]
