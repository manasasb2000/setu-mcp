"""Milestone 1 smoke tests: the server imports, registers the tool, and it runs."""

from __future__ import annotations

import asyncio

from setu import __version__
from setu.server import PingResult, mcp, setu_ping


def test_ping_returns_typed_result() -> None:
    result = setu_ping("ping")
    assert isinstance(result, PingResult)
    assert result.ok is True
    assert result.echo == "ping"
    assert result.version == __version__
    assert result.mode in {"mock", "live"}
    assert len(result.request_id) == 12


def test_tool_is_registered() -> None:
    tools = asyncio.run(mcp.list_tools())
    names = {t.name for t in tools}
    assert "setu_ping" in names


def test_default_mode_is_mock() -> None:
    # With no env overrides, Setu must default to mock so nothing burns credits.
    assert setu_ping().mode == "mock"
