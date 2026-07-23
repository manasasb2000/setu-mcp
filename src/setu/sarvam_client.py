"""Thin async wrapper over the Sarvam APIs.

One method per capability. Each measures wall-clock latency and returns a plain
dict that the tool layer maps into a typed Pydantic output.

Dispatch:
  * mock  -> deterministic fixtures (no network, no credits).
  * live  -> the official `sarvamai` async SDK.

Signatures verified against the Sarvam API reference:
  * STT  : client.speech_to_text.transcribe(file=, model="saaras:v3", mode=, language_code=)
           - "auto" maps to the API's "unknown" sentinel.
  * TTS  : client.text_to_speech.convert(text=, target_language_code=, model="bulbul:v3", speaker=)
           - response.audios is a list of base64 WAV strings.
Auth is the `api-subscription-key` header (the SDK sets this from the key).
"""

from __future__ import annotations

import base64
import io
import time
from typing import Any

from .config import SarvamSettings, SetuSettings
from .fixtures import transcribe_response, tts_response
from .logging import get_logger
from .modes import is_mock

log = get_logger("setu.sarvam_client")


class SarvamAuthError(RuntimeError):
    """Raised when live mode is requested without a SARVAM_API_KEY."""


class SarvamClient:
    """Async client that either serves fixtures (mock) or calls Sarvam (live)."""

    def __init__(self, setu: SetuSettings, sarvam: SarvamSettings) -> None:
        self._setu = setu
        self._sarvam = sarvam
        self._live_client: Any | None = None  # lazily constructed in live mode

    # ── internal ────────────────────────────────────────────────────────
    def _client(self) -> Any:
        """Build (once) the async sarvamai client for live mode."""
        if self._live_client is not None:
            return self._live_client
        if not self._sarvam.sarvam_api_key:
            raise SarvamAuthError(
                "SETU_MODE=live but SARVAM_API_KEY is not set. "
                "Add it to your environment or switch to SETU_MODE=mock."
            )
        try:
            from sarvamai import AsyncSarvamAI  # imported lazily; only needed live
        except ImportError as exc:  # pragma: no cover - depends on optional extra
            raise RuntimeError(
                "The 'sarvamai' package is required for live mode. "
                "Install it with: pip install 'setu-mcp[live]'"
            ) from exc
        self._live_client = AsyncSarvamAI(api_subscription_key=self._sarvam.sarvam_api_key)
        return self._live_client

    # ── speech-to-text ──────────────────────────────────────────────────
    async def transcribe(
        self,
        *,
        audio_base64: str | None,
        audio_url: str | None,
        language_code: str,
        mode: str,
        model: str,
    ) -> dict[str, Any]:
        """Saaras v3 speech-to-text. Returns transcript + detected language + latency."""
        # The API uses "unknown" (not "auto") for language auto-detection.
        api_language = "unknown" if language_code in {"auto", "unknown"} else language_code
        started = time.perf_counter()

        if is_mock(self._setu.mode):
            payload = transcribe_response(mode=mode, language_code=api_language)
        else:
            audio = await self._resolve_audio(audio_base64, audio_url)
            resp = await self._client().speech_to_text.transcribe(
                file=audio,
                model=model,
                mode=mode,
                language_code=api_language,
            )
            payload = _as_dict(resp)

        payload["latency_ms"] = round((time.perf_counter() - started) * 1000, 1)
        return payload

    # ── text-to-speech ──────────────────────────────────────────────────
    async def speak(
        self,
        *,
        text: str,
        target_language_code: str,
        speaker: str,
        model: str,
    ) -> dict[str, Any]:
        """Bulbul v3 text-to-speech. Returns base64 audio + latency."""
        started = time.perf_counter()

        if is_mock(self._setu.mode):
            payload = tts_response()
        else:
            resp = await self._client().text_to_speech.convert(
                text=text,
                target_language_code=target_language_code,
                model=model,
                speaker=speaker,
            )
            payload = _as_dict(resp)

        payload["latency_ms"] = round((time.perf_counter() - started) * 1000, 1)
        return payload

    # ── helpers ─────────────────────────────────────────────────────────
    async def _resolve_audio(self, audio_base64: str | None, audio_url: str | None) -> io.BytesIO:
        """Return a file-like object for the SDK from base64 or a URL (live mode)."""
        if audio_base64:
            buf = io.BytesIO(base64.b64decode(audio_base64))
            buf.name = "audio.wav"
            return buf
        if audio_url:
            import httpx  # part of the [live] extra

            async with httpx.AsyncClient(timeout=self._sarvam.request_timeout_s) as http:
                r = await http.get(audio_url)
                r.raise_for_status()
            buf = io.BytesIO(r.content)
            buf.name = "audio.wav"
            return buf
        raise ValueError("Provide either audio_base64 or audio_url.")


def _as_dict(resp: Any) -> dict[str, Any]:
    """Normalise an SDK response object into a plain dict."""
    for attr in ("model_dump", "dict"):
        fn = getattr(resp, attr, None)
        if callable(fn):
            return dict(fn())
    if isinstance(resp, dict):
        return dict(resp)
    # Fallback: pull public attributes.
    return {k: v for k, v in vars(resp).items() if not k.startswith("_")}
