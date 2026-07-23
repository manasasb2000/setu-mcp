"""Deterministic fixtures for mock mode.

These mirror the *shape* of real Sarvam responses (verified against the API
reference), so tools return identical schemas whether SETU_MODE is mock or live.
No network, no credits.
"""

from __future__ import annotations

from typing import Any

# A tiny valid base64-encoded WAV header (silent) — enough to prove the audio
# round-trips through the tool without shipping a large binary. Matches the
# example in the Sarvam text-to-speech reference.
MOCK_WAV_BASE64 = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAIA+AAACABAAZGF0YQAAAAA="


def transcribe_response(mode: str, language_code: str) -> dict[str, Any]:
    """Fixture mirroring Sarvam's SpeechToTextResponse (saaras:v3)."""
    # A code-mixed (Hinglish) utterance, in the requested output mode.
    by_mode = {
        "transcribe": "मेरा EMI कितना बचा है और अगली due date क्या है?",
        "codemix": "मेरा EMI कितना बचा है, aur next due date kya hai?",
        "translate": "How much of my EMI is left, and what is the next due date?",
        "translit": "mera EMI kitna bacha hai, aur next due date kya hai?",
        "verbatim": "मेरा ई एम आई कितना बचा है और अगली ड्यू डेट क्या है",
    }
    detected = "hi-IN" if language_code in {"unknown", "auto"} else language_code
    return {
        "request_id": "mock-stt-0001",
        "transcript": by_mode.get(mode, by_mode["transcribe"]),
        "language_code": detected,
        "language_probability": 0.94,
        "timestamps": None,
        "diarized_transcript": None,
    }


def tts_response() -> dict[str, Any]:
    """Fixture mirroring Sarvam's TextToSpeechResponse (bulbul:v3)."""
    return {
        "request_id": "mock-tts-0001",
        "audios": [MOCK_WAV_BASE64],
    }
