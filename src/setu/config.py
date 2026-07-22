"""Configuration for Setu, via pydantic-settings.

Two settings groups, per the build brief:
  * SetuSettings   — server behaviour (mode, rate limits, log level).
  * SarvamSettings — Sarvam credentials + endpoint (used from milestone 2 onward).

All values come from environment variables (or a local .env). Nothing is hardcoded.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

Mode = Literal["mock", "live"]


class SetuSettings(BaseSettings):
    """Server-level configuration (prefix: SETU_)."""

    model_config = SettingsConfigDict(
        env_prefix="SETU_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mode: Mode = Field(
        default="mock",
        description="'mock' serves deterministic fixtures (no credits); 'live' calls Sarvam.",
    )
    server_name: str = Field(default="setu", description="Name advertised to MCP clients.")
    log_level: str = Field(default="INFO", description="structlog level (DEBUG/INFO/WARNING).")
    # Reserved for later milestones (token-bucket rate limiter).
    rate_limit_per_minute: int = Field(default=60, ge=1)


class SarvamSettings(BaseSettings):
    """Sarvam credentials + endpoint (no prefix; SARVAM_API_KEY is read by the SDK too)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    sarvam_api_key: str | None = Field(default=None, description="Sarvam API key (SARVAM_API_KEY).")
    sarvam_base_url: str = Field(default="https://api.sarvam.ai")
    request_timeout_s: float = Field(default=30.0, gt=0)


@lru_cache
def get_settings() -> SetuSettings:
    """Cached SetuSettings singleton."""
    return SetuSettings()


@lru_cache
def get_sarvam_settings() -> SarvamSettings:
    """Cached SarvamSettings singleton."""
    return SarvamSettings()
