---
name: sarvam-stt
description: "Implement Sarvam AI Speech-to-Text (STT) transcription API (POST /speech-to-text). Use when transcribing Indian language audio, integrating saarika:v2.5 or saaras:v3 models, handling multilingual transcription, enabling translate/verbatim/translit/codemix modes, uploading audio files, or fixing STT request/response handling with Sarvam API."
argument-hint: "Feature to implement (e.g., 'transcribe Hindi audio', 'translate speech to English', 'codemix mode', 'PCM audio support')"
---

# Sarvam Speech-to-Text API

**Endpoint**: `POST https://api.sarvam.ai/speech-to-text`  
**Content-Type**: `multipart/form-data`  
**Auth**: `api-subscription-key: sk_xxx` header (required)

> **REST vs Batch**: This skill covers the REST API (audio < 30s, immediate response). For longer files or diarization (speaker identification), use the [Batch API](https://docs.sarvam.ai/api-reference-docs/api-guides-tutorials/speech-to-text/batch-api).

## Models

| Model | Default | Languages | Modes |
|-------|---------|-----------|-------|
| `saarika:v2.5` | Yes | 12 (see below) | transcribe only |
| `saaras:v3` | — | 23 (all) | transcribe, translate, verbatim, translit, codemix |

## Request Fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `file` | binary | **Yes** | Audio file (see [Supported Formats](#supported-audio-formats)) |
| `model` | string | No | `saarika:v2.5` (default) or `saaras:v3` |
| `language_code` | string | No | BCP-47 code; optional for `saarika:v2.5`, use `unknown` for auto-detect |
| `mode` | string | No | Only for `saaras:v3`; default `transcribe` |
| `input_audio_codec` | string | No | **Required only for PCM files** (`pcm_s16le`, `pcm_l16`, `pcm_raw`) |

## Modes (saaras:v3 only)

Given audio: *"मेरा फोन नंबर है 9840950950"*

| Mode | Output | Use Case |
|------|--------|----------|
| `transcribe` | `मेरा फोन नंबर है 9840950950` | Standard transcription with number normalization |
| `translate` | `My phone number is 9840950950` | Speech → English text |
| `verbatim` | `मेरा फोन नंबर है नौ आठ चार zero नौ पांच zero नौ पांच zero` | Word-for-word, no normalization |
| `translit` | `mera phone number hai 9840950950` | Romanization / Latin script |
| `codemix` | `मेरा phone number है 9840950950` | Indic script + English words in English |

## Language Codes

**saarika:v2.5** (12): `unknown`, `hi-IN`, `bn-IN`, `kn-IN`, `ml-IN`, `mr-IN`, `od-IN`, `pa-IN`, `ta-IN`, `te-IN`, `en-IN`, `gu-IN`

**saaras:v3 additional** (11 more): `as-IN`, `ur-IN`, `ne-IN`, `kok-IN`, `ks-IN`, `sd-IN`, `sa-IN`, `sat-IN`, `mni-IN`, `brx-IN`, `mai-IN`, `doi-IN`

Use `unknown` or omit `language_code` for automatic language detection.

## Supported Audio Formats

Auto-detected: WAV, MP3, AAC, AIFF, OGG, OPUS, FLAC, MP4/M4A, AMR, WMA, WebM  
**Manual codec required**: `pcm_s16le`, `pcm_l16`, `pcm_raw` (16kHz only)

- Best results at **16kHz sample rate**
- Multi-channel audio is merged to mono automatically
- REST API: audio **under 30 seconds**

## Response Structure

```json
{
  "request_id": "20240415_abc123",
  "transcript": "मेरा फोन नंबर है 9840950950",
  "language_code": "hi-IN",
  "language_probability": 0.97,
  "timestamps": null,
  "diarized_transcript": null
}
```

- `language_probability`: confidence float (0.0–1.0); only populated when `language_code` was `unknown` or omitted
- `timestamps`: word-level timestamps (Batch API only)
- `diarized_transcript`: speaker-separated entries (Batch API only)

Extract transcript: `response["transcript"]`

## Implementation Patterns

### Python (httpx async — recommended)

```python
import httpx
import os

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

async def transcribe(
    audio_path: str,
    language_code: str = "unknown",
    model: str = "saarika:v2.5",
    mode: str | None = None,
) -> dict:
    async with httpx.AsyncClient(timeout=60) as client:
        with open(audio_path, "rb") as f:
            files = {"file": (os.path.basename(audio_path), f, "audio/wav")}
            data = {"model": model, "language_code": language_code}
            if mode:
                data["mode"] = mode
            resp = await client.post(
                "https://api.sarvam.ai/speech-to-text",
                headers={"api-subscription-key": SARVAM_API_KEY},
                files=files,
                data=data,
            )
        resp.raise_for_status()
        return resp.json()

# Usage
result = await transcribe("audio.wav", language_code="hi-IN")
print(result["transcript"])
```

### Python — PCM audio (must set codec)

```python
files = {"file": ("audio.pcm", open("audio.pcm", "rb"), "audio/pcm")}
data = {
    "model": "saarika:v2.5",
    "language_code": "hi-IN",
    "input_audio_codec": "pcm_s16le",   # REQUIRED for PCM
}
```

### Python — saaras:v3 with translate mode

```python
files = {"file": ("speech.mp3", open("speech.mp3", "rb"), "audio/mpeg")}
data = {
    "model": "saaras:v3",
    "mode": "translate",          # speech → English
    "language_code": "hi-IN",
}
```

### Python SDK

```python
from sarvamai import SarvamAI

client = SarvamAI(api_subscription_key="YOUR_API_KEY_HERE")

response = client.speech_to_text.transcribe(file=open("audio.wav", "rb"))
print(response.transcript)
```

### Error Handling

```python
try:
    resp.raise_for_status()
    return resp.json()
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
| Using `mode` with `saarika:v2.5` | `mode` is only supported by `saaras:v3` |
| Wrong `language_code` format | Use BCP-47 with region: `hi-IN` not `hi` |
| Expecting `language_probability` when code provided | It's only set when `language_code` is `unknown` or omitted |
| Short timeout (< 30s) | Use 60s timeout; audio processing takes time |
| Sending `Content-Type: application/json` | Must be `multipart/form-data`; let httpx set the boundary automatically |

## Model Selection Guide

```
Need speaker identification (diarization)?
  → Batch API (out of scope for REST)

Audio in one of the 12 core Indian languages?
  → saarika:v2.5 (faster, default)

Need translate/translit/codemix/verbatim output?
  → saaras:v3 with appropriate mode

Language in extended set (Urdu, Assamese, Sanskrit, etc.)?
  → saaras:v3
```

## References

- [STT API Reference](https://docs.sarvam.ai/api-reference-docs/speech-to-text/transcribe)
- [Batch API Guide](https://docs.sarvam.ai/api-reference-docs/api-guides-tutorials/speech-to-text/batch-api)
- [Pricing](https://docs.sarvam.ai/api-reference-docs/getting-started/pricing)
- [Authentication](https://docs.sarvam.ai/api-reference-docs/authentication)
