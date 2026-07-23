"""Milestone 2 tests — transcribe + speak in mock mode, and tool registration."""

from __future__ import annotations

import asyncio
import base64
import os

import pytest

from setu.fixtures import MOCK_WAV_BASE64
from setu.server import (
    SpeakResult,
    TranscribeResult,
    mcp,
    sarvam_speak,
    sarvam_transcribe,
)


def test_all_tools_registered() -> None:
    names = {t.name for t in asyncio.run(mcp.list_tools())}
    assert {"setu_ping", "sarvam_transcribe", "sarvam_speak"} <= names


# ── transcribe ──────────────────────────────────────────────────────────
async def test_transcribe_codemix_mock() -> None:
    res = await sarvam_transcribe(audio_base64=MOCK_WAV_BASE64, mode="codemix")
    assert isinstance(res, TranscribeResult)
    # codemix keeps English tokens in Latin and Indic tokens in native script
    assert "EMI" in res.text and "है" in res.text
    assert res.language == "hi-IN"
    assert 0.0 <= (res.confidence or 0) <= 1.0
    assert res.model == "saaras:v3"
    assert res.latency_ms >= 0


async def test_transcribe_translate_mode_mock() -> None:
    res = await sarvam_transcribe(audio_url="https://example.com/a.wav", mode="translate")
    assert res.text.startswith("How much")  # translated to English


async def test_transcribe_requires_audio() -> None:
    with pytest.raises(ValueError):
        await sarvam_transcribe()


# ── speak ───────────────────────────────────────────────────────────────
async def test_speak_mock_returns_valid_base64() -> None:
    res = await sarvam_speak(text="आपका EMI ₹4,250 है।", target_language_code="hi-IN")
    assert isinstance(res, SpeakResult)
    assert res.audio_base64 == MOCK_WAV_BASE64
    # decodes to a RIFF/WAVE header
    raw = base64.b64decode(res.audio_base64)
    assert raw[:4] == b"RIFF" and raw[8:12] == b"WAVE"
    assert res.model == "bulbul:v3"
    assert res.chars == len("आपका EMI ₹4,250 है।")


async def test_speak_rejects_empty_and_overlong() -> None:
    with pytest.raises(ValueError):
        await sarvam_speak(text="   ")
    with pytest.raises(ValueError):
        await sarvam_speak(text="क" * 2501)


# ── live smoke test (skipped unless a real key is present) ───────────────
@pytest.mark.skipif(
    os.getenv("SETU_MODE") != "live" or not os.getenv("SARVAM_API_KEY"),
    reason="live smoke test needs SETU_MODE=live and SARVAM_API_KEY",
)
async def test_live_speak_smoke() -> None:  # pragma: no cover - only runs with a key
    res = await sarvam_speak(text="Namaste", target_language_code="hi-IN", speaker="anushka")
    assert res.audio_base64
