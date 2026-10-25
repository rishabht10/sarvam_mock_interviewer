"""Thin wrappers around the Sarvam APIs. If a call fails, the error text names the bad field; check docs.sarvam.ai."""
import base64
import os
import re

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SARVAM_API_KEY", "")
STT_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v3")
LLM_MODEL = os.getenv("SARVAM_LLM_MODEL", "sarvam-105b-conversations")
TTS_MODEL = os.getenv("SARVAM_TTS_MODEL", "bulbul:v3")
TTS_SPEAKER = os.getenv("SARVAM_TTS_SPEAKER", "tanya")

BASE = "https://api.sarvam.ai"
HEADERS = {"api-subscription-key": API_KEY}


class SarvamError(Exception):
    pass


def _check(r: requests.Response, what: str) -> dict:
    if not r.ok:
        raise SarvamError(f"{what} failed ({r.status_code}): {r.text}")
    return r.json()


def stt(audio_bytes: bytes) -> tuple[str, str]:
    """Speech to text. Returns (transcript, language_code)."""
    r = requests.post(
        f"{BASE}/speech-to-text",
        headers=HEADERS,
        files={"file": ("audio.wav", audio_bytes, "audio/wav")},
        data={"model": STT_MODEL},
        timeout=90,
    )
    j = _check(r, "Speech-to-text")
    return j.get("transcript", ""), j.get("language_code") or "en-IN"


def chat(system: str, user: str, temperature: float = 0.5) -> str:
    """Single LLM call. Strips <think> blocks some reasoning models emit."""
    r = requests.post(
        f"{BASE}/v1/chat/completions",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
        },
        timeout=90,
    )
    j = _check(r, "LLM")
    text = j["choices"][0]["message"]["content"]
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def tts(text: str, lang: str = "en-IN") -> bytes:
    """Text to speech. Returns WAV bytes."""
    r = requests.post(
        f"{BASE}/text-to-speech",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={
            "text": text[:1500],
            "target_language_code": lang,
            "speaker": TTS_SPEAKER,
            "model": TTS_MODEL,
        },
        timeout=90,
    )
    j = _check(r, "Text-to-speech")
    return base64.b64decode(j["audios"][0])
