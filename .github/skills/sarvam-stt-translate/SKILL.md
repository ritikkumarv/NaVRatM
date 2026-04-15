---
name: sarvam-stt-translate
description: "Implement Sarvam AI Speech-to-Text-Translate API (POST /speech-to-text-translate). Use when transcribing and translating Indian language audio directly to English, integrating saaras:v2.5, auto-detecting spoken language, handling PCM audio, or fixing STT-translate request/response handling with Sarvam API."
argument-hint: "Feature to implement (e.g., 'translate Hindi audio to English', 'auto-detect language and translate', 'PCM audio translate')"
---

# Sarvam Speech-to-Text-Translate API

**Endpoint**: `POST https://api.sarvam.ai/speech-to-text-translate`  
**Content-Type**: `multipart/form-data`  
**Auth**: `api-subscription-key: sk_xxx` header (required)

> **One-step pipeline**: This API auto-detects the spoken Indic language, transcribes the audio, and returns English text — all in a single call. Output is always English regardless of source language.

> **REST vs Batch**: REST API handles audio < 30s with immediate response. For longer files or diarization (speaker identification), use the [Batch API](https://docs.sarvam.ai/api-reference-docs/api-guides-tutorials/speech-to-text/batch-api).

## Model

| Model | Default | Description |
|-------|---------|-------------|
| `saaras:v2.5` | Yes | Translates any spoken Indic language → English text |

Only one model is currently available. The `model` field can be omitted.

## Request Fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `file` | binary | **Yes** | Audio file (see [Supported Formats](#supported-audio-formats)) |
| `model` | string | No | `saaras:v2.5` (only option, can omit) |
| `prompt` | string | No | Conversation context hint to boost accuracy (experimental) |
| `input_audio_codec` | string | No | **Required only for PCM files** (`pcm_s16le`, `pcm_l16`, `pcm_raw`) |

> **Note on `prompt`**: The system is experimental and does not yet match LLM-level prompt following. Use sparingly.

## Supported Audio Formats

Auto-detected: WAV, MP3, AAC, AIFF, OGG, OPUS, FLAC, MP4/M4A, AMR, WMA, WebM  
**Manual codec required**: `pcm_s16le`, `pcm_l16`, `pcm_raw` (16kHz only)

- Best results at **16kHz sample rate**
- Multi-channel audio is merged to mono automatically
- REST API: audio **under 30 seconds**

## Supported Source Languages

`hi-IN`, `bn-IN`, `kn-IN`, `ml-IN`, `mr-IN`, `od-IN`, `pa-IN`, `ta-IN`, `te-IN`, `gu-IN`, `en-IN`, `as-IN`, `ur-IN`, `ne-IN`, `kok-IN`, `ks-IN`, `sd-IN`, `sa-IN`, `sat-IN`, `mni-IN`, `brx-IN`, `mai-IN`, `doi-IN`

Language detection is **automatic** — no `language_code` input is needed. The detected language is returned in the response.

## Response Structure

```json
{
  "request_id": "20240415_abc123",
  "transcript": "My phone number is 9840950950",
  "language_code": "hi-IN",
  "language_probability": 0.97,
  "diarized_transcript": null
}
```

- `transcript` — Always English text (translated output)
- `language_code` — Detected BCP-47 source language; `null` if not detected
- `language_probability` — Confidence float (0.0–1.0) for the detected language
- `diarized_transcript` — Speaker-separated entries (Batch API only, always `null` in REST)

Extract result: `response["transcript"]`

## Implementation Patterns

### Python (httpx async — recommended)

```python
import httpx
import os

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

async def translate_speech(audio_path: str, prompt: str | None = None) -> dict:
    async with httpx.AsyncClient(timeout=60) as client:
        with open(audio_path, "rb") as f:
            files = {"file": (os.path.basename(audio_path), f, "audio/wav")}
            data = {"model": "saaras:v2.5"}
            if prompt:
                data["prompt"] = prompt
            resp = await client.post(
                "https://api.sarvam.ai/speech-to-text-translate",
                headers={"api-subscription-key": SARVAM_API_KEY},
                files=files,
                data=data,
            )
        resp.raise_for_status()
        return resp.json()

# Usage
result = await translate_speech("hindi_audio.wav")
print(result["transcript"])        # English translation
print(result["language_code"])     # e.g. "hi-IN"
print(result["language_probability"])  # e.g. 0.97
```

### Python — PCM audio (must set codec)

```python
files = {"file": ("audio.pcm", open("audio.pcm", "rb"), "audio/pcm")}
data = {
    "model": "saaras:v2.5",
    "input_audio_codec": "pcm_s16le",   # REQUIRED for PCM
}
```

### Python SDK

```python
from sarvamai import SarvamAI

client = SarvamAI(api_subscription_key="YOUR_API_KEY_HERE")

response = client.speech_to_text.translate(file=open("audio.wav", "rb"))
print(response.transcript)       # English output
print(response.language_code)    # detected source language
```

### Error Handling

```python
try:
    resp.raise_for_status()
    result = resp.json()
    return result["transcript"]
except httpx.HTTPStatusError as e:
    error = e.response.json().get("error", {})
    code = error.get("code")        # e.g. "rate_limit_exceeded_error"
    request_id = error.get("request_id")
    raise
```

## Error Codes

| HTTP | Code | Action |
|------|------|--------|
| 400 | `invalid_request_error` | Check file format, codec, or field values |
| 403 | `invalid_api_key_error` / `authentication_error` | Check `SARVAM_API_KEY` |
| 422 | `unprocessable_entity_error` | Fix multipart form fields/types |
| 429 | `rate_limit_exceeded_error` / `insufficient_quota_error` | Backoff, check quota |
| 500 | `internal_server_error` | Retry with exponential backoff |
| 503 | *(service overloaded)* | Retry after delay |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Audio > 30s in REST API | Use Batch API for longer files |
| PCM file with no `input_audio_codec` | Always pass `input_audio_codec` for PCM formats |
| PCM not at 16kHz | Re-sample PCM to 16kHz before sending |
| Expecting native-language output | This API always outputs **English**; use `/speech-to-text` for native transcription |
| Passing `language_code` in request | Not a supported field; language is auto-detected only |
| Short timeout (< 30s) | Use 60s timeout for audio processing |
| Sending `Content-Type: application/json` | Must be `multipart/form-data`; let httpx set boundary automatically |
| Over-relying on `prompt` for accuracy | Prompt support is experimental; don't depend on it for production |

## API vs sarvam-stt Comparison

| Feature | `/speech-to-text` | `/speech-to-text-translate` |
|---------|-------------------|------------------------------|
| Output language | Same as input | Always **English** |
| Language input | Optional `language_code` | Auto-detected only |
| Multiple modes | Yes (saaras:v3) | No (translate only) |
| Prompt support | No | Yes (experimental) |
| Use case | Native transcription | Direct speech → English pipeline |

## References

- [STT-Translate API Reference](https://docs.sarvam.ai/api-reference-docs/speech-to-text-translate/translate)
- [Batch API Guide](https://docs.sarvam.ai/api-reference-docs/api-guides-tutorials/speech-to-text/batch-api)
- [Pricing](https://docs.sarvam.ai/api-reference-docs/getting-started/pricing)
- [Authentication](https://docs.sarvam.ai/api-reference-docs/authentication)
