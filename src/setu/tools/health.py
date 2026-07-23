"""Health-check tool (milestone 1)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .. import __version__
from ..app import log, mcp, settings
from ..logging import new_request_id


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
    log.info("setu_ping", request_id=rid, message=message, mode=settings.mode)
    return PingResult(
        ok=True,
        server=settings.server_name,
        version=__version__,
        mode=settings.mode,
        echo=message,
        request_id=rid,
    )
