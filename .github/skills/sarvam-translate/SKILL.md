---
name: sarvam-translate
description: "Implement Sarvam AI text translation API (POST /translate). Use when translating text between Indian languages, integrating mayura:v1 or sarvam-translate:v1 models, auto-detecting source language, applying formal/colloquial/code-mixed translation modes, romanizing output script, using native numerals, or fixing translation request/response handling with Sarvam API."
argument-hint: "Feature to implement (e.g., 'translate Hindi to English', 'auto-detect language', 'formal mode', 'native numerals output')"
---

# Sarvam Text Translation API

**Endpoint**: `POST https://api.sarvam.ai/translate`  
**Content-Type**: `application/json`  
**Auth**: `api-subscription-key: sk_xxx` header (required)

> Translates text from one language to another while preserving meaning. Example: `मैं ऑफिस जा रहा हूँ` → `I am going to the office`

## Models

| Model | Languages | Char Limit | Modes | Auto-detect | Transliteration |
|-------|-----------|------------|-------|-------------|-----------------|
| `mayura:v1` | 11 core | 1000 | formal, classic-colloquial, modern-colloquial, code-mixed | Yes (`auto`) | Yes |
| `sarvam-translate:v1` | 22 (all scheduled) | 2000 | formal only | No | No |

## Required Fields

| Field | Type | Notes |
|-------|------|-------|
| `input` | string | Text to translate |
| `source_language_code` | string | BCP-47 source language or `auto` (mayura:v1 only) |
| `target_language_code` | string | BCP-47 target language |

## Optional Fields

| Field | Default | mayura:v1 | sarvam-translate:v1 | Notes |
|-------|---------|-----------|----------------------|-------|
| `model` | — | `mayura:v1` | `sarvam-translate:v1` | Specify explicitly |
| `mode` | `formal` | all 4 modes | `formal` only | Translation tone/style |
| `speaker_gender` | — | `Male` / `Female` | `Male` / `Female` | Improves gendered translations |
| `output_script` | `null` | `roman`, `fully-native`, `spoken-form-in-native` | ❌ not supported | Transliteration of output |
| `numerals_format` | `international` | `international`, `native` | `international`, `native` | Number script format |

## Language Codes

**mayura:v1** (11 languages + `auto`):  
`auto`, `bn-IN`, `en-IN`, `gu-IN`, `hi-IN`, `kn-IN`, `ml-IN`, `mr-IN`, `od-IN`, `pa-IN`, `ta-IN`, `te-IN`

**sarvam-translate:v1** extends with 12 more:  
`as-IN`, `brx-IN`, `doi-IN`, `kok-IN`, `ks-IN`, `mai-IN`, `mni-IN`, `ne-IN`, `sa-IN`, `sat-IN`, `sd-IN`, `ur-IN`

## Translation Modes (mayura:v1 only)

| Mode | Description | Example (Hindi → English) |
|------|-------------|---------------------------|
| `formal` | Standard, professional (default) | "I am going to the office." |
| `modern-colloquial` | Casual contemporary speech | "I'm heading to the office." |
| `classic-colloquial` | Traditional informal speech | "I am going to my office." |
| `code-mixed` | English words in Indic context | "मैं office जा रहा हूँ" |

## Output Script (mayura:v1 only)

Given: `Your EMI of Rs. 3000 is pending.` → Hindi translation

| `output_script` | Output |
|-----------------|--------|
| `null` (default) | `आपका Rs. 3000 का EMI pending है` |
| `roman` | `aapka Rs. 3000 ka EMI pending hai` |
| `fully-native` | Native script, formal style |
| `spoken-form-in-native` | Native script, spoken style |

## Numerals Format

| `numerals_format` | Example |
|-------------------|---------|
| `international` (default) | `मेरा phone number है: 9840950950` |
| `native` | `मेरा phone number है: ९८४०९५०९५०` |

## Response Structure

```json
{
  "request_id": "20240415_abc123",
  "translated_text": "I am going to the office",
  "source_language_code": "hi-IN"
}
```

- `translated_text` — Translated output in the target language
- `source_language_code` — Detected or provided source language (useful when `auto` was used)

Extract result: `response["translated_text"]`

## Implementation Patterns

### Python (httpx async — recommended)

```python
import httpx
import os

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

async def translate(
    text: str,
    source_lang: str,
    target_lang: str,
    model: str = "mayura:v1",
    mode: str = "formal",
    speaker_gender: str | None = None,
) -> dict:
    payload = {
        "input": text,
        "source_language_code": source_lang,
        "target_language_code": target_lang,
        "model": model,
        "mode": mode,
    }
    if speaker_gender:
        payload["speaker_gender"] = speaker_gender

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.sarvam.ai/translate",
            headers={"api-subscription-key": SARVAM_API_KEY},
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()

# Usage
result = await translate("मैं ऑफिस जा रहा हूँ", "hi-IN", "en-IN")
print(result["translated_text"])      # "I am going to the office"
print(result["source_language_code"]) # "hi-IN"
```

### Python — auto-detect source language (mayura:v1 only)

```python
result = await translate(
    text="मैं ऑफिस जा रहा हूँ",
    source_lang="auto",          # auto-detect
    target_lang="en-IN",
    model="mayura:v1",
)
print(result["source_language_code"])  # detected: "hi-IN"
```

### Python — extended languages with sarvam-translate:v1

```python
result = await translate(
    text="আমি অফিস যাচ্ছি",      # Assamese
    source_lang="as-IN",
    target_lang="hi-IN",
    model="sarvam-translate:v1",  # required for extended languages
    mode="formal",                # only formal is supported
)
```

### Python — romanized output with native numerals

```python
payload = {
    "input": "Your EMI of Rs. 3000 is pending.",
    "source_language_code": "en-IN",
    "target_language_code": "hi-IN",
    "model": "mayura:v1",
    "mode": "modern-colloquial",
    "output_script": "roman",
    "numerals_format": "native",
}
```

### Python SDK

```python
from sarvamai import SarvamAI

client = SarvamAI(api_subscription_key="YOUR_API_KEY_HERE")

response = client.text.translate(
    input="मैं ऑफिस जा रहा हूँ",
    source_language_code="hi-IN",
    target_language_code="en-IN",
)
print(response.translated_text)
```

### Error Handling

```python
try:
    resp.raise_for_status()
    return resp.json()["translated_text"]
except httpx.HTTPStatusError as e:
    error = e.response.json().get("error", {})
    code = error.get("code")        # e.g. "invalid_request_error"
    request_id = error.get("request_id")
    raise
```

## Error Codes

| HTTP | Code | Action |
|------|------|--------|
| 400 | `invalid_request_error` | Check input text, language codes, mode compatibility |
| 403 | `invalid_api_key_error` / `authentication_error` | Check `SARVAM_API_KEY` |
| 422 | `unprocessable_entity_error` | Fix field types or unsupported param combinations |
| 429 | `rate_limit_exceeded_error` / `insufficient_quota_error` | Backoff, check quota |
| 500 | `internal_server_error` | Retry with exponential backoff |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using `auto` with `sarvam-translate:v1` | `auto` is only supported by `mayura:v1` |
| Using non-formal `mode` with `sarvam-translate:v1` | Only `formal` mode is supported by that model |
| Using `output_script` with `sarvam-translate:v1` | Transliteration only works with `mayura:v1` |
| Using extended language (e.g. `ur-IN`) with `mayura:v1` | Switch to `sarvam-translate:v1` |
| Text > 1000 chars with `mayura:v1` | Use `sarvam-translate:v1` (2000 char limit) or split text |
| Omitting `speaker_gender` for gendered languages | Provide `Male`/`Female` for better accuracy in Hindi etc. |
| Expecting `source_language_code` to be optional | All three core fields are required |

## Model Selection Guide

```
Need auto language detection?
  → mayura:v1 with source_language_code: "auto"

Need colloquial/code-mixed/roman output?
  → mayura:v1

Need Urdu, Sanskrit, Assamese, or other scheduled languages?
  → sarvam-translate:v1

Text longer than 1000 characters?
  → sarvam-translate:v1 (2000 char limit)

Standard formal translation between core 11 languages?
  → Either model; mayura:v1 default
```

## References

- [Translate API Reference](https://docs.sarvam.ai/api-reference-docs/text/translate-text)
- [Translate API Tutorial Notebook](https://github.com/sarvamai/sarvam-ai-cookbook/blob/main/notebooks/translate/Translate_API_Tutorial.ipynb)
- [Pricing](https://docs.sarvam.ai/api-reference-docs/getting-started/pricing)
- [Authentication](https://docs.sarvam.ai/api-reference-docs/authentication)
