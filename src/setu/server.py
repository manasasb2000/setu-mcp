"""Setu MCP server — transport entrypoint.

Imports the shared FastMCP app and the tool package (which registers every tool
via import side-effect), then runs the requested transport.

Milestone 2 registers: setu_ping, sarvam_transcribe, sarvam_speak.
Later milestones add the remaining Sarvam tools and streamable-HTTP transport.
"""

from __future__ import annotations

import argparse

from . import __version__, tools  # noqa: F401  (tools import registers the tools)
from .app import log, mcp, settings

# Re-exported for tests and external importers.
from .tools.health import PingResult, setu_ping  # noqa: E402,F401
from .tools.speak import SpeakResult, sarvam_speak  # noqa: E402,F401
from .tools.transcribe import TranscribeResult, sarvam_transcribe  # noqa: E402,F401


def main() -> None:
    """Console entrypoint. Milestone 2 supports the stdio transport."""
    parser = argparse.ArgumentParser(prog="setu", description="Setu MCP server")
    parser.add_argument(
        "--transport",
        choices=["stdio"],  # 'streamable-http' arrives in milestone 6
        default="stdio",
        help="MCP transport (stdio only for now).",
    )
    args = parser.parse_args()

    log.info("setu.start", transport=args.transport, mode=settings.mode, version=__version__)
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
