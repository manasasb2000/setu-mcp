"""Shared application objects: settings, logging, the FastMCP instance, and the
Sarvam client. Tool modules import from here and register themselves on `mcp`.

Kept separate from server.py to avoid circular imports between the transport
entrypoint and the tool modules.
"""

from __future__ import annotations

from .config import get_sarvam_settings, get_settings
from .logging import configure_logging, get_logger
from .sarvam_client import SarvamClient

settings = get_settings()
sarvam_settings = get_sarvam_settings()

configure_logging(settings.log_level)
log = get_logger("setu")

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover - dependency guard
    raise SystemExit(
        "The 'mcp' package is required. Install with: pip install -e '.[dev]'"
    ) from exc

# The shared MCP application. Tool modules decorate functions with @mcp.tool().
mcp = FastMCP(settings.server_name)

# The shared Sarvam client (mock or live per SETU_MODE).
client = SarvamClient(settings, sarvam_settings)
