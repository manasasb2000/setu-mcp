"""Setu MCP server — milestone 1 skeleton.

Boots a FastMCP server over stdio and registers a single health-check tool
(`setu_ping`). The Sarvam tool surface (transcribe, speak, translate, chat,
transliterate, identify_language, parse_document) lands in later milestones;
this file is the transport + registration seam they plug into.
"""

from __future__ import annotations

import argparse

from pydantic import BaseModel, Field

from . import __version__
from .config import get_settings
from .logging import configure_logging, get_logger, new_request_id

_settings = get_settings()
configure_logging(_settings.log_level)
log = get_logger("setu.server")

# The shared FastMCP application. Later milestones register more @mcp.tool()s here.
try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover - dependency guard
    raise SystemExit(
        "The 'mcp' package is required. Install with: pip install -e '.[dev]'"
    ) from exc

mcp = FastMCP(_settings.server_name)


class PingResult(BaseModel):
    """Typed result of the health-check tool."""

    ok: bool = Field(description="Always true when the server is reachable.")
    server: str = Field(description="Server name advertised to the client.")
    version: str = Field(description="Setu package version.")
    mode: str = Field(description="Current dispatch mode: 'mock' or 'live'.")
    echo: str = Field(description="Echoes the caller's message.")
    request_id: str = Field(description="Correlation id for this call.")


@mcp.tool()
def setu_ping(message: str = "hello") -> PingResult:
    """Health check. Confirms Setu is reachable and reports server name, version, and mode.

    Use this to verify your MCP client is wired to Setu correctly.
    """
    rid = new_request_id()
    log.info("setu_ping", request_id=rid, message=message, mode=_settings.mode)
    return PingResult(
        ok=True,
        server=_settings.server_name,
        version=__version__,
        mode=_settings.mode,
        echo=message,
        request_id=rid,
    )


def main() -> None:
    """Console entrypoint. Milestone 1 supports the stdio transport."""
    parser = argparse.ArgumentParser(prog="setu", description="Setu MCP server")
    parser.add_argument(
        "--transport",
        choices=["stdio"],  # 'streamable-http' arrives in milestone 6
        default="stdio",
        help="MCP transport (milestone 1: stdio only).",
    )
    args = parser.parse_args()

    log.info(
        "setu.start",
        transport=args.transport,
        mode=_settings.mode,
        version=__version__,
    )
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
