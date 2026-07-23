"""sarvam_speak — Bulbul v3 text-to-speech (milestone 2)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from ..app import client, log, mcp
from ..logging import new_request_id

# TTS target languages (Bulbul), verified against the API reference.
TTSLanguage = Literal[
    "hi-IN", "bn-IN", "en-IN", "gu-IN", "kn-IN", "ml-IN",
    "mr-IN", "od-IN", "pa-IN", "ta-IN", "te-IN",
]

# Max characters per REST call for bulbul:v3 (per the API reference).
_MAX_CHARS = 2500


class SpeakResult(BaseModel):
    """Typed output of sarvam_speak."""

    audio_base64: str = Field(description="Synthesised audio (WAV), base64-encoded.")
    format: str = Field(description="Audio container/format of the returned bytes.")
    speaker: str = Field(description="Speaker voice used.")
    model: str = Field(description="TTS model used.")
    chars: int = Field(description="Number of input characters synthesised.")
    latency_ms: float = Field(description="Wall-clock latency of the call.")
    request_id: str = Field(description="Correlation id for this call.")


@mcp.tool()
async def sarvam_speak(
    text: str,
    target_language_code: TTSLanguage = "hi-IN",
    speaker: str = "anushka",
    model: str = "bulbul:v3",
) -> SpeakResult:
    """Convert text to natural speech with Sarvam's Bulbul v3.

    Returns base64-encoded WAV audio. Supports code-mixed text (English + Indic).
    Note: bulbul:v3 speakers are case-sensitive and model-specific — pick a
    v3-compatible voice (e.g. `anushka`, `vidya`, `shubh`) for live calls.
    For numbers over 4 digits, comma-format them (e.g. '10,000') for correct
    pronunciation. Max 2500 characters per call.
    """
    if not text.strip():
        raise ValueError("text must be non-empty.")
    if len(text) > _MAX_CHARS:
        raise ValueError(f"text exceeds bulbul:v3 limit of {_MAX_CHARS} characters.")

    rid = new_request_id()
    log.info("sarvam_speak", request_id=rid, speaker=speaker, lang=target_language_code)

    result = await client.speak(
        text=text,
        target_language_code=target_language_code,
        speaker=speaker,
        model=model,
    )
    audios = result.get("audios") or [""]
    return SpeakResult(
        audio_base64=audios[0],
        format="wav",
        speaker=speaker,
        model=model,
        chars=len(text),
        latency_ms=result.get("latency_ms", 0.0),
        request_id=rid,
    )
