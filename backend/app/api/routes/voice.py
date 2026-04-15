"""Voice routes — STT, TTS, and voice query loop."""

from __future__ import annotations
import logging
from fastapi import APIRouter, UploadFile, File, Form
from app.models.schemas import TranscriptionResponse, VoiceQueryResponse
from app.core import sarvam_client
from app.config import SARVAM_LLM_MODEL

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/voice", tags=["voice"])


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(...), mode: str = Form("transcribe")):
    """Transcribe uploaded audio using Saaras v3 STT."""
    audio_bytes = await file.read()
    result = await sarvam_client.speech_to_text(audio_bytes, mode=mode)
    return TranscriptionResponse(
        transcript=result["transcript"],
        language_detected=result.get("language_detected", "hi-IN"),
        confidence=result.get("confidence", 0.0),
    )


@router.post("/query", response_model=VoiceQueryResponse)
async def voice_query(file: UploadFile = File(...)):
    """Full voice loop: audio → STT → LLM → translate → TTS → audio response."""
    audio_bytes = await file.read()

    # 1. Transcribe
    stt_result = await sarvam_client.speech_to_text(audio_bytes, mode="transcribe")
    transcript = stt_result["transcript"]
    lang = stt_result.get("language_detected", "hi-IN")

    # 2. Translate to English for LLM if not English
    query_en = transcript
    if not lang.startswith("en"):
        try:
            query_en = await sarvam_client.translate_text(transcript, lang, "en-IN")
        except Exception:
            query_en = transcript

    # 3. LLM reasoning
    prompt = f"""You are a welfare fraud detection assistant. An officer has asked:
"{query_en}"

Respond helpfully in 2-3 sentences. If they ask about a specific application, provide a brief summary.
If they ask a general question about fraud detection, answer concisely."""

    response_text = await sarvam_client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model=SARVAM_LLM_MODEL,
    )

    # 4. Translate response back to officer's language
    response_translated = response_text
    if not lang.startswith("en"):
        try:
            response_translated = await sarvam_client.translate_text(response_text, "en-IN", lang)
        except Exception:
            response_translated = response_text

    # 5. TTS
    audio_b64 = None
    try:
        audio_b64 = await sarvam_client.text_to_speech(response_translated, target_lang=lang)
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
async def synthesize_speech(text: str = Form(...), language: str = Form("hi-IN")):
    """Convert text to speech using Bulbul TTS."""
    audio_b64 = await sarvam_client.text_to_speech(text, target_lang=language)
    return {"audio_base64": audio_b64, "language": language}
