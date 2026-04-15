---
name: sarvam-api
description: "Integrate Sarvam AI APIs for Indian language processing - STT, TTS, chat completions, translation, and document processing. Use when building Hindi/Indian language features or fixing Sarvam API calls."
argument-hint: "API endpoint or feature to implement (e.g., 'STT for Hindi', 'TTS endpoint', 'chat completion')"
---

# Sarvam AI API — Router

**Base URL**: `https://api.sarvam.ai`  
**Auth**: `api-subscription-key: sk_xxx` header on every request

This is a routing skill. Load the focused skill for the specific API you need.

## API → Skill Map

| What you need | Endpoint | Load this skill |
|---------------|----------|-----------------|
| LLM chat, tool calling, streaming, reasoning | `POST /v1/chat/completions` | `sarvam-chat-completion` |
| Transcribe Indian language audio | `POST /speech-to-text` | `sarvam-stt` |
| Transcribe + translate speech to English | `POST /speech-to-text-translate` | `sarvam-stt-translate` |
| Convert text to audio (TTS) | `POST /text-to-speech` | `sarvam-tts` |
| Translate text between Indian languages | `POST /translate` | `sarvam-translate` |
| Extract text/tables from PDFs or scanned docs | Document Intelligence job API | `sarvam-vision` |

## Quick Decision Guide

```
Audio input?
  Transcribe in original language  → sarvam-stt
  Get English output directly      → sarvam-stt-translate

Text input?
  Generate / reason / chat         → sarvam-chat-completion
  Translate to another language    → sarvam-translate
  Convert to spoken audio          → sarvam-tts

Document / image input?
  Extract text or tables from PDF  → sarvam-vision
```

## Common Across All APIs

- **Header**: `api-subscription-key: <your-key>` (not `Authorization: Bearer`)
- **Env var**: `SARVAM_API_KEY`
- **Language format**: Always use full BCP-47 codes — `hi-IN`, not `hi`
- **HTTP client**: Use `httpx.AsyncClient(timeout=30)` for async Python
- **SDK**: `sarvamai` package for Python and JavaScript

## References

- [Official Docs](https://docs.sarvam.ai/)
- [API Reference](https://docs.sarvam.ai/api-reference-docs/overview)
- [Models](https://docs.sarvam.ai/api-reference-docs/getting-started/models)
- [Authentication](https://docs.sarvam.ai/api-reference-docs/authentication)
- [Pricing](https://docs.sarvam.ai/api-reference-docs/getting-started/pricing)
