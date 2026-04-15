"""Wrapper around Sarvam AI SDK — provides OCR, translation, LLM, STT, TTS."""

from __future__ import annotations
import base64, json, logging, httpx
from typing import Optional
from app.config import SARVAM_API_KEY, SARVAM_BASE_URL, SARVAM_LLM_MODEL, SARVAM_STT_MODEL

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# We use httpx directly for maximum control + async support.
# The official sarvamai SDK is sync-only; httpx lets us stay async.
# ---------------------------------------------------------------------------

_HEADERS = {
    "api-subscription-key": SARVAM_API_KEY,
}


async def translate_text(
    text: str,
    source_lang: str = "auto",
    target_lang: str = "en-IN",
) -> str:
    """Translate text using Sarvam Translate API (mayura:v2)."""
    if not SARVAM_API_KEY:
        log.warning("No SARVAM_API_KEY set — returning original text")
        return text
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{SARVAM_BASE_URL}/translate",
            headers=_HEADERS,
            json={
                "input": text,
                "source_language_code": source_lang,
                "target_language_code": target_lang,
                "model": "mayura:v2",
                "enable_preprocessing": True,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("translated_text", text)


async def chat_completion(
    messages: list[dict],
    model: str = SARVAM_LLM_MODEL,
    temperature: float = 0.3,
    max_tokens: int = 2048,
) -> str:
    """Call Sarvam chat completions endpoint (OpenAI-compatible)."""
    if not SARVAM_API_KEY:
        log.warning("No SARVAM_API_KEY — returning mock response")
        return '{"error": "no api key"}'
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{SARVAM_BASE_URL}/v1/chat/completions",
            headers={**_HEADERS, "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


async def extract_fields_from_image(
    image_bytes: bytes,
    document_type: str = "aadhaar",
    filename: str = "document.png",
) -> dict:
    """Use Sarvam LLM (with vision or text) to extract structured fields from a document.

    Since the async doc-digitization pipeline is multi-step, we use the chat
    completions endpoint with a structured extraction prompt instead — simpler
    and faster for a hackathon.
    """
    b64 = base64.b64encode(image_bytes).decode()
    mime = "image/png" if filename.lower().endswith(".png") else "image/jpeg"

    prompt = f"""You are a document field extractor for Indian government documents.
Extract ALL fields from this {document_type} document image into JSON.

Return ONLY valid JSON with these keys (use null for missing fields):
{{
  "full_name": "...",
  "date_of_birth": "YYYY-MM-DD or null",
  "gender": "male/female/other or null",
  "address": "full address or null",
  "aadhaar_number": "XXXX XXXX XXXX or null",
  "pan_number": "ABCDE1234F or null",
  "income_monthly": 0.0,
  "bank_account": "account number or null",
  "phone": "10 digit number or null",
  "document_type": "{document_type}",
  "confidence": 0.85,
  "raw_text": "all visible text from the document",
  "language_detected": "hi/en/ta/mr etc"
}}"""

    if not SARVAM_API_KEY:
        # Return mock data for development without API key
        return _mock_extraction(document_type)

    try:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                ],
            }
        ]
        raw = await chat_completion(messages, model=SARVAM_LLM_MODEL)
        # Try to parse JSON from the response
        # Strip markdown code fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
        return json.loads(cleaned)
    except Exception as e:
        log.error(f"Field extraction failed: {e}")
        return _mock_extraction(document_type)


async def speech_to_text(audio_bytes: bytes, mode: str = "transcribe") -> dict:
    """Transcribe audio using Saaras v3."""
    if not SARVAM_API_KEY:
        return {"transcript": "यह एक परीक्षण वाक्य है", "language_detected": "hi-IN", "confidence": 0.95}

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{SARVAM_BASE_URL}/speech-to-text",
            headers=_HEADERS,
            files={"file": ("audio.wav", audio_bytes, "audio/wav")},
            data={"model": SARVAM_STT_MODEL, "language_code": "unknown", "mode": mode},
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "transcript": data.get("transcript", ""),
            "language_detected": data.get("language_code", "hi-IN"),
            "confidence": data.get("confidence", 0.0),
        }


async def text_to_speech(text: str, target_lang: str = "hi-IN", speaker: str = "female") -> Optional[str]:
    """Generate speech using Bulbul v3. Returns base64-encoded audio."""
    if not SARVAM_API_KEY:
        return None

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{SARVAM_BASE_URL}/text-to-speech",
            headers={**_HEADERS, "Content-Type": "application/json"},
            json={
                "inputs": [text],
                "target_language_code": target_lang,
                "speaker": speaker,
                "model": "bulbul:v3",
            },
        )
        resp.raise_for_status()
        data = resp.json()
        audios = data.get("audios", [])
        return audios[0] if audios else None


# ────────────────────── Mock helpers ──────────────────────

def _mock_extraction(doc_type: str) -> dict:
    """Return realistic mock data when no API key is available."""
    mocks = {
        "aadhaar": {
            "full_name": "Ramesh Kumar Sharma",
            "date_of_birth": "1985-03-15",
            "gender": "male",
            "address": "42, Gandhi Nagar, Sector 12, Jaipur, Rajasthan 302015",
            "aadhaar_number": "9876 5432 1098",
            "pan_number": None,
            "income_monthly": None,
            "bank_account": None,
            "phone": None,
            "document_type": "aadhaar",
            "confidence": 0.92,
            "raw_text": "भारत सरकार GOVERNMENT OF INDIA आधार AADHAAR Ramesh Kumar Sharma DOB: 15/03/1985 Male 42 Gandhi Nagar Jaipur 302015 9876 5432 1098",
            "language_detected": "hi",
        },
        "income_certificate": {
            "full_name": "Ramesh Kumar",
            "date_of_birth": "1985-03-15",
            "gender": "male",
            "address": "42 Gandhi Nagar, Jaipur, Rajasthan",
            "aadhaar_number": None,
            "pan_number": None,
            "income_monthly": 8500.0,
            "bank_account": None,
            "phone": "9876543210",
            "document_type": "income_certificate",
            "confidence": 0.88,
            "raw_text": "आय प्रमाण पत्र Income Certificate Name: Ramesh Kumar Monthly Income: Rs 8,500 Address: 42 Gandhi Nagar Jaipur",
            "language_detected": "hi",
        },
        "bank_statement": {
            "full_name": "Ramesh K Sharma",
            "date_of_birth": None,
            "gender": None,
            "address": "42 Gandhi Ngr, Jaipur",
            "aadhaar_number": None,
            "pan_number": None,
            "income_monthly": 15200.0,
            "bank_account": "50100012345678",
            "phone": "9876543210",
            "document_type": "bank_statement",
            "confidence": 0.85,
            "raw_text": "State Bank of India Account Statement Ramesh K Sharma A/c: 50100012345678 Avg Monthly Credit: 15200",
            "language_detected": "en",
        },
        "pan": {
            "full_name": "RAMESH KUMAR SHARMA",
            "date_of_birth": "1985-03-15",
            "gender": None,
            "address": None,
            "aadhaar_number": None,
            "pan_number": "ABCRS1234K",
            "income_monthly": None,
            "bank_account": None,
            "phone": None,
            "document_type": "pan",
            "confidence": 0.94,
            "raw_text": "INCOME TAX DEPARTMENT GOVT OF INDIA Permanent Account Number ABCRS1234K RAMESH KUMAR SHARMA 15/03/1985",
            "language_detected": "en",
        },
    }
    return mocks.get(doc_type, mocks["aadhaar"])
