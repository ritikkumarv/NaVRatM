---
name: sarvam-tts
description: "Implement Sarvam AI Text-to-Speech API (POST /text-to-speech). Use when converting text to audio, integrating bulbul:v3 or bulbul:v2 models, selecting Indian language voices, decoding base64 audio output, controlling pace/pitch/temperature, or fixing TTS request/response handling with Sarvam API."
argument-hint: "Feature to implement (e.g., 'Hindi TTS with female voice', 'save audio to file', 'streaming TTS', 'codemix text to speech')"
---

# Sarvam Text-to-Speech API

**Endpoint**: `POST https://api.sarvam.ai/text-to-speech`  
**Content-Type**: `application/json`  
**Auth**: `api-subscription-key: sk_xxx` header (required)

> **Output is base64**: The response contains base64-encoded WAV audio strings. You must decode them before saving or streaming.

## Models

| Model | Voices | Char Limit | Controls | Notes |
|-------|--------|------------|----------|-------|
| `bulbul:v3` | 37+ | 2500 | pace, temperature | Recommended; pitch/loudness NOT supported |
| `bulbul:v2` | 7 | 1500 | pace, pitch, loudness | Legacy; preprocessing available |

Default model if omitted: `bulbul:v3` behavior applies when `speaker` defaults are used.

## Required Fields

| Field | Type | Notes |
|-------|------|-------|
| `text` | string | Text to synthesize |
| `target_language_code` | string | BCP-47 output language |

## Optional Fields

| Field | Default | bulbul:v3 | bulbul:v2 | Notes |
|-------|---------|-----------|-----------|-------|
| `model` | — | `bulbul:v3` | `bulbul:v2` | Specify explicitly |
| `speaker` | `shubh` / `anushka` | 37 voices | 7 voices | Case-sensitive, lowercase |
| `pace` | `1.0` | 0.5–2.0 | 0.3–3.0 | Speech speed |
| `temperature` | `0.6` | 0.01–2.0 | ❌ not supported | Expressiveness |
| `pitch` | `0.0` | ❌ not supported | -0.75–0.75 | Voice pitch |
| `loudness` | `1.0` | ❌ not supported | 0.3–3.0 | Volume |
| `speech_sample_rate` | `24000` | 8000–48000 Hz | 8000–24000 Hz | Higher rates REST-only |
| `output_audio_codec` | — | mp3, wav, opus, flac, aac, linear16, mulaw, alaw | same | Output format |
| `enable_preprocessing` | `false` | ❌ auto-enabled | opt-in | Normalizes numbers/dates |
| `dict_id` | — | custom dict ID | ❌ not supported | Pronunciation dictionary |
| `enable_cached_responses` | `false` | ❌ beta v1/v2 only | beta | Cache identical requests |

## Target Language Codes

`hi-IN`, `bn-IN`, `gu-IN`, `kn-IN`, `ml-IN`, `mr-IN`, `od-IN`, `pa-IN`, `ta-IN`, `te-IN`, `en-IN`

## Voices

**bulbul:v3** (37 voices, default: `shubh`):  
`shubh`, `aditya`, `ritu`, `priya`, `neha`, `rahul`, `pooja`, `rohan`, `simran`, `kavya`, `amit`, `dev`, `ishita`, `shreya`, `ratan`, `varun`, `manan`, `sumit`, `roopa`, `kabir`, `aayan`, `ashutosh`, `advait`, `anand`, `tanya`, `tarun`, `sunny`, `mani`, `gokul`, `vijay`, `shruti`, `suhani`, `mohit`, `kavitha`, `rehan`, `soham`, `rupali`

**bulbul:v2** (7 voices, default: `anushka`):  
Female: `anushka`, `manisha`, `vidya`, `arya`  
Male: `abhilash`, `karun`, `hitesh`

> Speaker names are **case-sensitive** and must be **lowercase** (e.g., `ritu` not `Ritu`).  
> Speaker must be compatible with selected model — mixing causes errors.

## Response Structure

```json
{
  "request_id": "20240415_abc123",
  "audios": ["UklGRiQ...base64encodedWAV..."]
}
```

- `audios` — Array of base64-encoded WAV strings (one per input text)
- Decode each string to bytes before writing to file or streaming

## Implementation Patterns

### Python (httpx async — recommended)

```python
import base64
import httpx
import os

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

async def text_to_speech(
    text: str,
    language_code: str,
    speaker: str = "shubh",
    model: str = "bulbul:v3",
    pace: float = 1.0,
    output_path: str | None = None,
) -> bytes:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.sarvam.ai/text-to-speech",
            headers={"api-subscription-key": SARVAM_API_KEY},
            json={
                "text": text,
                "target_language_code": language_code,
                "speaker": speaker,
                "model": model,
                "pace": pace,
            },
        )
        resp.raise_for_status()
        audio_b64 = resp.json()["audios"][0]
        audio_bytes = base64.b64decode(audio_b64)

    if output_path:
        with open(output_path, "wb") as f:
            f.write(audio_bytes)

    return audio_bytes

# Usage
audio = await text_to_speech("नमस्ते दुनिया", "hi-IN", speaker="ritu")
```

### Python — bulbul:v2 with pitch/loudness

```python
resp = await client.post(
    "https://api.sarvam.ai/text-to-speech",
    headers={"api-subscription-key": SARVAM_API_KEY},
    json={
        "text": "Hello from Sarvam",
        "target_language_code": "en-IN",
        "model": "bulbul:v2",
        "speaker": "anushka",        # bulbul:v2 voice
        "pitch": 0.2,                # bulbul:v2 only
        "loudness": 1.2,             # bulbul:v2 only
        "pace": 1.0,
        "enable_preprocessing": True,
    },
)
```

### Python — custom sample rate and codec

```python
json={
    "text": "Your text here",
    "target_language_code": "hi-IN",
    "model": "bulbul:v3",
    "speaker": "shubh",
    "speech_sample_rate": "16000",   # string, not int
    "output_audio_codec": "mp3",
}
```

### Python SDK

```python
from sarvamai import SarvamAI

client = SarvamAI(api_subscription_key="YOUR_API_KEY_HERE")

response = client.text_to_speech.convert(
    text="Hello, welcome to Sarvam.",
    target_language_code="en-IN",
)

import base64
audio_bytes = base64.b64decode(response.audios[0])
with open("output.wav", "wb") as f:
    f.write(audio_bytes)
```

### Decode and Return as FastAPI Response

```python
from fastapi.responses import Response
import base64

audio_b64 = resp.json()["audios"][0]
audio_bytes = base64.b64decode(audio_b64)
return Response(content=audio_bytes, media_type="audio/wav")
```

### Error Handling

```python
try:
    resp.raise_for_status()
    return base64.b64decode(resp.json()["audios"][0])
except httpx.HTTPStatusError as e:
    error = e.response.json().get("error", {})
    code = error.get("code")        # e.g. "invalid_request_error"
    request_id = error.get("request_id")
    raise
```

## Error Codes

| HTTP | Code | Action |
|------|------|--------|
| 400 | `invalid_request_error` | Check text length, language code, speaker name |
| 403 | `invalid_api_key_error` / `authentication_error` | Check `SARVAM_API_KEY` |
| 422 | `unprocessable_entity_error` | Fix field types or unsupported param combinations |
| 429 | `rate_limit_exceeded_error` / `insufficient_quota_error` | Backoff, check quota |
| 500 | `internal_server_error` | Retry with exponential backoff |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using `pitch`/`loudness` with `bulbul:v3` | These params are only for `bulbul:v2` |
| Using `temperature` with `bulbul:v2` | `temperature` is only for `bulbul:v3` |
| Using a `bulbul:v2` speaker (e.g. `anushka`) with `bulbul:v3` | Match speaker to model |
| Capitalizing speaker name (`Ritu`) | Speaker names must be lowercase (`ritu`) |
| Text > 2500 chars (v3) or > 1500 chars (v2) | Split text into chunks |
| Using `speech_sample_rate` as integer | Pass as string: `"16000"` not `16000` |
| Forgetting to base64-decode the audio | `audios[0]` is base64; always decode before use |
| Numbers > 4 digits without commas | Use `"10,000"` not `"10000"` for correct pronunciation |
| `enable_preprocessing: true` on `bulbul:v3` | Not supported; preprocessing is automatic |

## Model Selection Guide

```
Need 30+ voices or temperature control?
  → bulbul:v3 (recommended default)

Need pitch or loudness control?
  → bulbul:v2

Need response caching (beta)?
  → bulbul:v2 with enable_cached_responses: true

Need custom pronunciation dictionary?
  → bulbul:v3 with dict_id
```

## Text Formatting Tips

- Numbers > 4 digits: use commas → `"10,000"` not `"10000"`
- Code-mixed text is supported (English + Indic in same string)
- `bulbul:v3` auto-normalizes numbers and dates (preprocessing always on)
- `bulbul:v2` requires `enable_preprocessing: true` for normalization

## References

- [TTS API Reference](https://docs.sarvam.ai/api-reference-docs/text-to-speech/convert)
- [Pronunciation Dictionary API](https://docs.sarvam.ai/api-reference-docs/pronunciation-dictionary/create)
- [Pricing](https://docs.sarvam.ai/api-reference-docs/getting-started/pricing)
- [Authentication](https://docs.sarvam.ai/api-reference-docs/authentication)
