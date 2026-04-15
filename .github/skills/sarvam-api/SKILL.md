---
name: sarvam-api
description: "Integrate Sarvam AI APIs for Indian language processing - STT, TTS, chat completions, translation, and document processing. Use when building Hindi/Indian language features or fixing Sarvam API calls."
argument-hint: "API endpoint or feature to implement (e.g., 'STT for Hindi', 'TTS endpoint', 'chat completion')"
---

# Sarvam AI API Integration

## Overview

Sarvam AI provides specialized APIs for Indian language processing. This skill covers correct endpoint usage, model selection, request/response formats, and async implementation patterns.

**Base URL**: `https://api.sarvam.ai`
**Authentication**: `api-subscription-key` header with API key

## Supported APIs

### 1. Chat Completions (LLM)
**Endpoint**: `POST /v1/chat/completions`
**Description**: OpenAI-compatible chat API supporting multilingual Indian language models

**Models**:
- `sarvam-105b` - Large reasoning model (quality over speed)
- `sarvam-m` - Medium model (24B, faster)

**Request**:
```json
{
  "model": "sarvam-m",
  "messages": [
    {"role": "user", "content": "Your prompt"}
  ],
  "temperature": 0.3,
  "max_tokens": 2048,
  "top_p": 0.95
}
```

**Response**:
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Response text"
      }
    }
  ]
}
```

### 2. Speech-to-Text (STT)
**Endpoint**: `POST /speech-to-text`
**Model**: `saaras:v3` (multilingual Indian language support)

**Request** (multipart/form-data):
```
- file: audio file (.wav, .mp3)
- model: "saaras:v3"
- language_code: "hi", "ta", "te", "ml", "kn", "en", etc.
```

**Response**:
```json
{
  "transcript": "कृपया आवेदन की स्थिति...",
  "language_code": "hi-IN",
  "confidence": 0.95,
  "language_detected": "hi"
}
```

### 3. Text-to-Speech (TTS)
**Endpoint**: `POST /text-to-speech`
**Model**: `bulbul:v3` (Indian language voices)

**Request**:
```json
{
  "inputs": ["Text to synthesize"],
  "target_language_code": "hi-IN",
  "speaker": "female",
  "model": "bulbul:v3"
}
```

**Available speakers**: male, female (language-dependent)

**Response**:
```json
{
  "audios": ["base64-encoded-audio"],
  "language_code": "hi-IN"
}
```

### 4. Translation
**Endpoint**: `POST /translate`
**Model**: `mayura:v2`

**Request**:
```json
{
  "input": "Text to translate",
  "source_language_code": "hi",
  "target_language_code": "en",
  "model": "mayura:v2",
  "enable_preprocessing": true
}
```

**Response**:
```json
{
  "translated_text": "Translated text",
  "source_language": "hi",
  "target_language": "en"
}
```

### 5. Document Extraction (Vision)
Use `/v1/chat/completions` with `image_url` in message content. Format image as data URI:
```json
{
  "type": "image_url",
  "image_url": {"url": "data:image/png;base64,<encoded-image>"}
}
```

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| 401 Unauthorized | Verify `SARVAM_API_KEY` in `/api-subscription-key` header |
| 400 Bad Request | Check `target_language_code` format (use locale codes: `hi-IN`, `ta-IN`) |
| Timeout (>30s) | Use 30-60s timeout for STT and image processing; 10-15s for LLM |
| Model not found | Use `sarvam-m` (default), `sarvam-105b` (quality), or check docs for latest |
| STT empty transcript | Verify audio format is `.wav` or `.mp3`; check language_code matches audio language |

## Implementation Patterns

### Async with httpx
Use `httpx.AsyncClient` for non-blocking I/O:

```python
import httpx

headers = {"api-subscription-key": SARVAM_API_KEY}

async with httpx.AsyncClient(timeout=30) as client:
    resp = await client.post(
        "https://api.sarvam.ai/v1/chat/completions",
        headers=headers,
        json={"model": "sarvam-m", "messages": [...]}
    )
    data = resp.json()
```

### Error Handling
```python
try:
    resp.raise_for_status()
    return resp.json()
except httpx.HTTPStatusError as e:
    log.error(f"API error {e.response.status_code}: {e.response.text}")
    # Provide fallback
except httpx.RequestError as e:
    log.error(f"Network error: {e}")
    # Retry or fallback
```

### Fallback Pattern
Implement mock responses when API key is unavailable (development mode):

```python
if not SARVAM_API_KEY:
    return mock_response()
```

## Language Codes

| Language | Code |
|----------|------|
| Hindi | `hi`, `hi-IN` |
| Tamil | `ta`, `ta-IN` |
| Telugu | `te`, `te-IN` |
| Kannada | `kn`, `kn-IN` |
| Malayalam | `ml`, `ml-IN` |
| English | `en`, `en-IN` |

## References

- [Official Docs](https://docs.sarvam.ai/)
- [API Reference](https://docs.sarvam.ai/api-reference-docs/overview)
- [Models](https://docs.sarvam.ai/api-reference-docs/getting-started/models)
- [Quickstart](https://docs.sarvam.ai/api-reference-docs/getting-started/quickstart)
