"""structlog setup: JSON logs with a correlation/request id on every line.

IMPORTANT: over the stdio transport, stdout carries the MCP protocol, so all logs
MUST go to stderr — otherwise they corrupt the JSON-RPC stream. We bind structlog
to a stderr logger here.
"""

from __future__ import annotations

import logging
import sys
import uuid

import structlog


def configure_logging(level: str = "INFO") -> None:
    """Configure structlog to emit JSON to stderr."""
    log_level = getattr(logging, level.upper(), logging.INFO)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a bound structlog logger."""
    return structlog.get_logger(name)


def new_request_id() -> str:
    """Short correlation id for a single tool invocation."""
    return uuid.uuid4().hex[:12]
