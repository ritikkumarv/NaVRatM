"""Voice routes — STT, TTS, and voice query loop."""

from __future__ import annotations

import logging

from fastapi import APIRouter, File, Form, UploadFile

from app.core import sarvam_client
from app.models.schemas import TranscriptionResponse, VoiceQueryResponse

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/voice", tags=["voice"])


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    language_code: str = Form("unknown"),
    model: str = Form("saarika:v2.5"),
):
    """Transcribe uploaded audio using Sarvam STT."""
    audio_bytes = await file.read()
    result = await sarvam_client.transcribe(
        audio_bytes, model=model, language_code=language_code
    )
    return TranscriptionResponse(
        transcript=result.get("transcript", ""),
        language_detected=result.get("language_code", "hi-IN"),
        confidence=result.get("language_probability", 0.0),
    )


@router.post("/query", response_model=VoiceQueryResponse)
async def voice_query(file: UploadFile = File(...)):
    """Full voice loop: audio → STT → LLM → translate → TTS → audio response."""
    audio_bytes = await file.read()

    # 1. Transcribe
    stt = await sarvam_client.transcribe(audio_bytes)
    transcript = stt.get("transcript", "")
    lang = stt.get("language_code", "hi-IN")

    # 2. Translate to English for LLM if not English
    query_en = transcript
    if not lang.startswith("en"):
        try:
            query_en = await sarvam_client.translate_text(transcript, lang, "en-IN")
        except Exception:
            query_en = transcript

    # 3. LLM reasoning
    prompt = (
        "You are a welfare fraud detection assistant. An officer has asked:\n"
        f"\"{query_en}\"\n\n"
        "Respond helpfully in 2-3 sentences."
    )
    try:
        response_text = await sarvam_client.chat(
            messages=[{"role": "user", "content": prompt}]
        )
    except Exception:
        response_text = "I could not process the query at this time."

    # 4. Translate response back
    response_translated = response_text
    if not lang.startswith("en"):
        try:
            response_translated = await sarvam_client.translate_text(
                response_text, "en-IN", lang
            )
        except Exception:
            response_translated = response_text

    # 5. TTS
    audio_b64 = None
    try:
        audio_b64 = await sarvam_client.tts(
            response_translated, target_language_code=lang
        )
    except Exception:
        pass

    return VoiceQueryResponse(
        transcript=transcript,
        language_detected=lang,
        response_text=response_translated,
        response_language=lang,
        audio_base64=audio_b64,
    )


@router.post("/synthesize")
async def synthesize_speech(
    text: str = Form(...),
    language: str = Form("hi-IN"),
    speaker: str = Form("shubh"),
):
    """Convert text to speech using Sarvam TTS."""
    audio_b64 = await sarvam_client.tts(
        text, target_language_code=language, speaker=speaker
    )
    return {"audio_base64": audio_b64, "language": language}
