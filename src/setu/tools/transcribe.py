"""sarvam_transcribe — Saaras v3 speech-to-text (milestone 2)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from ..app import client, log, mcp
from ..logging import new_request_id

# Saaras v3 output modes (verified against the API reference).
TranscribeMode = Literal["transcribe", "translate", "verbatim", "translit", "codemix"]

# BCP-47 codes Saaras v3 accepts; "auto" is mapped to the API's "unknown" sentinel.
LanguageCode = Literal[
    "auto", "hi-IN", "bn-IN", "kn-IN", "ml-IN", "mr-IN", "od-IN", "pa-IN",
    "ta-IN", "te-IN", "en-IN", "gu-IN", "as-IN", "ur-IN", "ne-IN",
]


class TranscribeResult(BaseModel):
    """Typed output of sarvam_transcribe."""

    text: str = Field(description="The transcribed text.")
    language: str | None = Field(description="Detected BCP-47 language code.")
    confidence: float | None = Field(description="Language-detection probability (0-1).")
    mode: str = Field(description="Output mode used.")
    model: str = Field(description="STT model used.")
    latency_ms: float = Field(description="Wall-clock latency of the call.")
    request_id: str = Field(description="Correlation id for this call.")


@mcp.tool()
async def sarvam_transcribe(
    audio_base64: str | None = None,
    audio_url: str | None = None,
    language_code: LanguageCode = "auto",
    mode: TranscribeMode = "codemix",
    model: str = "saaras:v3",
) -> TranscribeResult:
    """Transcribe speech to text with Sarvam's Saaras v3.

    Provide exactly one of `audio_base64` or `audio_url`. `mode` selects the output
    style — `codemix` keeps English words in Latin and Indic words in native script,
    ideal for Hinglish. `language_code='auto'` lets Saaras detect the language.
    """
    if not audio_base64 and not audio_url:
        raise ValueError("Provide either audio_base64 or audio_url.")

    rid = new_request_id()
    log.info("sarvam_transcribe", request_id=rid, mode=mode, language_code=language_code)

    result = await client.transcribe(
        audio_base64=audio_base64,
        audio_url=audio_url,
        language_code=language_code,
        mode=mode,
        model=model,
    )
    return TranscribeResult(
        text=result.get("transcript", ""),
        language=result.get("language_code"),
        confidence=result.get("language_probability"),
        mode=mode,
        model=model,
        latency_ms=result.get("latency_ms", 0.0),
        request_id=rid,
    )
