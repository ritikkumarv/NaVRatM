"""Async wrapper around Sarvam AI REST APIs.

Uses httpx for full async support. Every function has a mock fallback
when SARVAM_API_KEY is empty so the app runs offline during dev.
"""

from __future__ import annotations

import base64
import json
import logging

import httpx

from app.config import (
    SARVAM_API_KEY,
    SARVAM_BASE_URL,
    SARVAM_LLM_MODEL,
    SARVAM_STT_MODEL,
    SARVAM_STT_TRANSLATE_MODEL,
    SARVAM_TRANSLATE_MODEL,
    SARVAM_TTS_MODEL,
    SSL_VERIFY,
)

log = logging.getLogger(__name__)

_HEADERS: dict[str, str] = {"api-subscription-key": SARVAM_API_KEY}


def _client(**kwargs) -> httpx.AsyncClient:
    """Create an httpx async client with shared SSL and timeout settings."""
    kwargs.setdefault("timeout", 30)
    return httpx.AsyncClient(verify=SSL_VERIFY, **kwargs)


# ────────────────────── translate ──────────────────────


async def translate_text(
    text: str,
    source_lang: str = "auto",
    target_lang: str = "en-IN",
    model: str = SARVAM_TRANSLATE_MODEL,
) -> str:
    """Translate text via POST /translate (mayura:v1).

    Uses ``input`` field (not ``text``). BCP-47 language codes.
    """
    if not SARVAM_API_KEY:
        log.warning("No SARVAM_API_KEY — returning original text")
        return text

    async with _client(timeout=30) as client:
        resp = await client.post(
            f"{SARVAM_BASE_URL}/translate",
            headers=_HEADERS,
            json={
                "input": text,
                "source_language_code": source_lang,
                "target_language_code": target_lang,
                "model": model,
            },
        )
        resp.raise_for_status()
        return resp.json().get("translated_text", text)


# ────────────────────── chat completions ──────────────────────


async def chat(
    messages: list[dict],
    model: str = SARVAM_LLM_MODEL,
    temperature: float = 0.2,
    max_tokens: int = 2048,
) -> str:
    """Call POST /v1/chat/completions.

    Header: ``api-subscription-key`` (not Authorization Bearer).
    """
    if not SARVAM_API_KEY:
        log.warning("No SARVAM_API_KEY — returning mock chat response")
        return '{"mock": true, "message": "No API key configured"}'

    async with _client(timeout=60) as client:
        resp = await client.post(
            f"{SARVAM_BASE_URL}/v1/chat/completions",
            headers=_HEADERS,
            json={
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


# ────────────────────── speech-to-text ──────────────────────


async def transcribe(
    audio_bytes: bytes,
    model: str = SARVAM_STT_MODEL,
    language_code: str = "unknown",
    mode: str = "transcribe",
) -> dict:
    """Transcribe audio via POST /speech-to-text (multipart/form-data).

    Returns dict with keys: transcript, language_code, language_probability.
    """
    if not SARVAM_API_KEY:
        return {
            "transcript": "यह एक परीक्षण वाक्य है",
            "language_code": "hi-IN",
            "language_probability": 0.95,
        }

    async with _client(timeout=60) as client:
        data: dict[str, str] = {
            "model": model,
            "language_code": language_code,
        }
        # mode is only supported by saaras:v3
        if model == "saaras:v3" and mode:
            data["mode"] = mode
        resp = await client.post(
            f"{SARVAM_BASE_URL}/speech-to-text",
            headers=_HEADERS,
            files={"file": ("audio.wav", audio_bytes, "audio/wav")},
            data=data,
        )
        resp.raise_for_status()
        return resp.json()


# ────────────────────── speech-to-text-translate ──────────────────────


async def transcribe_translate(
    audio_bytes: bytes,
    model: str = SARVAM_STT_TRANSLATE_MODEL,
) -> dict:
    """Transcribe + translate to English via POST /speech-to-text-translate.

    Language is auto-detected. Output is always English.
    """
    if not SARVAM_API_KEY:
        return {
            "transcript": "This is a test sentence",
            "language_code": "hi-IN",
            "language_probability": 0.95,
        }

    async with _client(timeout=60) as client:
        resp = await client.post(
            f"{SARVAM_BASE_URL}/speech-to-text-translate",
            headers=_HEADERS,
            files={"file": ("audio.wav", audio_bytes, "audio/wav")},
            data={"model": model},
        )
        resp.raise_for_status()
        return resp.json()


# ────────────────────── text-to-speech ──────────────────────


async def tts(
    text: str,
    target_language_code: str = "hi-IN",
    speaker: str = "shubh",
    model: str = SARVAM_TTS_MODEL,
    pace: float = 1.0,
) -> str | None:
    """Generate speech via POST /text-to-speech.

    Field is ``text`` (singular string). Returns base64 audio decoded
    from ``audios[0]``.
    """
    if not SARVAM_API_KEY:
        return None

    async with _client(timeout=30) as client:
        resp = await client.post(
            f"{SARVAM_BASE_URL}/text-to-speech",
            headers=_HEADERS,
            json={
                "text": text,
                "target_language_code": target_language_code,
                "speaker": speaker,
                "model": model,
                "pace": pace,
            },
        )
        resp.raise_for_status()
        audios = resp.json().get("audios", [])
        return audios[0] if audios else None


# ────────────────────── document field extraction (via chat + vision) ──────────────────────


async def extract_document_fields(
    image_bytes: bytes,
    document_type: str = "aadhaar",
    filename: str = "document.png",
) -> dict:
    """Extract structured fields from a document image using chat() with vision prompt.

    Falls back to mock data when API key is absent.
    """
    if not SARVAM_API_KEY:
        return _mock_extraction(document_type)

    b64 = base64.b64encode(image_bytes).decode()
    mime = "image/png" if filename.lower().endswith(".png") else "image/jpeg"

    prompt = (
        f"You are a document field extractor for Indian government documents.\n"
        f"Extract ALL fields from this {document_type} document image into JSON.\n\n"
        "Return ONLY valid JSON with these keys (use null for missing fields):\n"
        "{\n"
        '  "full_name": "...",\n'
        '  "dob": "YYYY-MM-DD or null",\n'
        '  "gender": "male/female/other or null",\n'
        '  "address": "full address or null",\n'
        '  "aadhaar_masked": "XXXX-XXXX-NNNN or null",\n'
        '  "pan_masked": "XXXXXNNNNX or null",\n'
        '  "income_monthly": 0.0,\n'
        '  "bank_account_masked": "XXXXXXXXXX1234 or null",\n'
        '  "phone_masked": "XXXXXX1234 or null",\n'
        f'  "document_type": "{document_type}",\n'
        '  "confidence": 0.85,\n'
        '  "raw_text": "all visible text from the document",\n'
        '  "language_detected": "hi-IN"\n'
        "}"
    )

    try:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{b64}"},
                    },
                ],
            }
        ]
        raw = await chat(messages, model=SARVAM_LLM_MODEL)
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
        return json.loads(cleaned)
    except Exception as exc:
        log.error("Field extraction failed: %s", exc)
        return _mock_extraction(document_type)


# ────────────────────── mock helpers ──────────────────────


def _mock_extraction(doc_type: str) -> dict:
    """Realistic mock extraction for offline development."""
    mocks: dict[str, dict] = {
        "aadhaar": {
            "full_name": "Ramesh Kumar Sharma",
            "dob": "1985-03-15",
            "gender": "male",
            "address": "42, Gandhi Nagar, Sector 12, Jaipur, Rajasthan 302015",
            "aadhaar_masked": "XXXX-XXXX-1098",
            "pan_masked": None,
            "income_monthly": None,
            "bank_account_masked": None,
            "phone_masked": None,
            "document_type": "aadhaar",
            "confidence": 0.92,
            "raw_text": "GOVERNMENT OF INDIA AADHAAR Ramesh Kumar Sharma",
            "language_detected": "hi-IN",
        },
        "income_certificate": {
            "full_name": "Ramesh Kumar",
            "dob": "1985-03-15",
            "gender": "male",
            "address": "42 Gandhi Nagar, Jaipur, Rajasthan",
            "aadhaar_masked": None,
            "pan_masked": None,
            "income_monthly": 8500.0,
            "bank_account_masked": None,
            "phone_masked": "XXXXXX3210",
            "document_type": "income_certificate",
            "confidence": 0.88,
            "raw_text": "Income Certificate Name: Ramesh Kumar Monthly Income: Rs 8,500",
            "language_detected": "hi-IN",
        },
        "bank_statement": {
            "full_name": "Ramesh K Sharma",
            "dob": None,
            "gender": None,
            "address": "42 Gandhi Ngr, Jaipur",
            "aadhaar_masked": None,
            "pan_masked": None,
            "income_monthly": 15200.0,
            "bank_account_masked": "XXXXXXXXXX5678",
            "phone_masked": "XXXXXX3210",
            "document_type": "bank_statement",
            "confidence": 0.85,
            "raw_text": "State Bank of India Account Statement Ramesh K Sharma",
            "language_detected": "en-IN",
        },
        "pan": {
            "full_name": "RAMESH KUMAR SHARMA",
            "dob": "1985-03-15",
            "gender": None,
            "address": None,
            "aadhaar_masked": None,
            "pan_masked": "XXXXX1234X",
            "income_monthly": None,
            "bank_account_masked": None,
            "phone_masked": None,
            "document_type": "pan",
            "confidence": 0.94,
            "raw_text": "INCOME TAX DEPARTMENT PERMANENT ACCOUNT NUMBER",
            "language_detected": "en-IN",
        },
    }
    return mocks.get(doc_type, mocks["aadhaar"])
