---
name: sarvam-chat-completion
description: "Implement Sarvam AI chat completions API (POST /v1/chat/completions). Use when integrating sarvam-105b, sarvam-30b, or sarvam-m LLM models, building chat interfaces, adding tool calling/function calling, enabling streaming responses, wiki grounding, or fixing chat completion request/response handling with Sarvam API."
argument-hint: "Feature to implement (e.g., 'basic chat', 'streaming', 'tool calling', 'multilingual chat')"
---

# Sarvam Chat Completion API

**Endpoint**: `POST https://api.sarvam.ai/v1/chat/completions`
**Auth**: `Authorization: Bearer <token>` OR `api-subscription-key: sk_xxx` header

## Models

| Model | Context | Use Case |
|-------|---------|----------|
| `sarvam-30b` | 64K tokens | Recommended for new integrations |
| `sarvam-105b` | 128K tokens | Best quality, reasoning-heavy tasks |
| `sarvam-m` | — | Legacy 24B; migrate to sarvam-30b |

## Request Structure

```json
{
  "model": "sarvam-30b",
  "messages": [
    { "role": "system", "content": "You are a helpful assistant." },
    { "role": "user", "content": "Your question here" }
  ],
  "temperature": 0.2,
  "max_tokens": 2048,
  "top_p": 1,
  "stream": false,
  "n": 1
}
```

### Required Fields
 `messages` — Array of message objects (see [Message Roles](#message-roles))
 `model` — One of `sarvam-30b`, `sarvam-105b`, `sarvam-m`

### Optional Fields

| Field | Default | Notes |
|-------|---------|-------|
| `temperature` | `0.2` | 0–2; lower = more deterministic. Don't combine with `top_p`. |
| `top_p` | `1` | Nucleus sampling. Don't combine with `temperature`. |
| `max_tokens` | `2048` | Max tokens to generate |
| `stream` | `false` | SSE streaming |
| `n` | `1` | Completions per request; keep `1` to control costs |
| `reasoning_effort` | `medium` | `low`/`medium`/`high` or null to disable |
| `stop` | — | String or array of up to 4 stop sequences |
| `seed` | — | Beta: attempt deterministic output |
| `frequency_penalty` | `0` | -2.0 to 2.0; reduces repetition |
| `presence_penalty` | `0` | -2.0 to 2.0; encourages new topics |
| `wiki_grounding` | `false` | Ground response in Wikipedia facts |
| `tools` | — | List of function/tool definitions |
| `tool_choice` | — | `"none"` / `"auto"` / `"required"` / named tool |

## Message Roles

```python
# user
{"role": "user", "content": "Hello!"}

# system
{"role": "system", "content": "You are a helpful assistant."}

# assistant (with optional tool_calls)
{"role": "assistant", "content": "Sure, calling a tool...", "tool_calls": [...]}

# tool (response to a tool call)
{"role": "tool", "content": "<json result>", "tool_call_id": "<id from assistant>"}
```

## Response Structure

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1713200000,
  "model": "sarvam-30b",
  "choices": [
    {
      "index": 0,
      "finish_reason": "stop",
      "message": {
        "role": "assistant",
        "content": "Response text here",
        "reasoning_content": null,
        "tool_calls": null
      }
    }
  ],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 50,
    "total_tokens": 70
  }
}
```

**`finish_reason` values**: `stop` | `length` | `tool_calls` | `content_filter` | `function_call`

Extract content: `response["choices"][0]["message"]["content"]`

## Implementation Patterns

### Python (httpx async — recommended)

```python
import httpx
import os

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

async def chat(messages: list[dict], model: str = "sarvam-30b") -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.sarvam.ai/v1/chat/completions",
            headers={"api-subscription-key": SARVAM_API_KEY},
            json={"model": model, "messages": messages, "temperature": 0.2},
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
```

### Python SDK

```python
from sarvamai import SarvamAI, ChatCompletionRequestMessage_User

client = SarvamAI()  # reads SARVAM_API_KEY env var

response = client.chat.completions(
    messages=[ChatCompletionRequestMessage_User(content="Hello!")],
    model="sarvam-30b",
)
```

### Streaming (SSE)

```python
async with httpx.AsyncClient(timeout=60) as client:
    async with client.stream(
        "POST",
        "https://api.sarvam.ai/v1/chat/completions",
        headers={"api-subscription-key": SARVAM_API_KEY},
        json={"model": "sarvam-30b", "messages": messages, "stream": True},
    ) as resp:
        async for line in resp.aiter_lines():
            if line.startswith("data: ") and line != "data: [DONE]":
                chunk = json.loads(line[6:])
                delta = chunk["choices"][0].get("delta", {})
                if content := delta.get("content"):
                    yield content
```

### Tool Calling

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"}
                },
                "required": ["city"]
            }
        }
    }
]

resp = await client.post(
    "https://api.sarvam.ai/v1/chat/completions",
    headers={"api-subscription-key": SARVAM_API_KEY},
    json={
        "model": "sarvam-30b",
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto",
    },
)
data = resp.json()
choice = data["choices"][0]

if choice["finish_reason"] == "tool_calls":
    tool_call = choice["message"]["tool_calls"][0]
    fn_name = tool_call["function"]["name"]
    fn_args = json.loads(tool_call["function"]["arguments"])
    # execute fn_name(**fn_args), then append tool result message
```

### Error Handling

```python
try:
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]
except httpx.HTTPStatusError as e:
    status = e.response.status_code
    error = e.response.json().get("error", {})
    code = error.get("code")           # e.g. "rate_limit_exceeded_error"
    message = error.get("message")
    request_id = error.get("request_id")
    raise
```

## Error Codes

| HTTP | Code | Action |
|------|------|--------|
| 400 | `invalid_request_error` | Fix request body/params |
| 403 | `invalid_api_key_error` / `authentication_error` | Check `SARVAM_API_KEY` |
| 422 | `unprocessable_entity_error` | Fix message format/types |
| 429 | `rate_limit_exceeded_error` / `insufficient_quota_error` | Backoff, check quota |
| 500 | `internal_server_error` | Retry with exponential backoff |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using `sarvam-m` for new integrations | Prefer `sarvam-30b` or `sarvam-105b` |
| Setting both `temperature` and `top_p` | Use only one |
| Not handling `tool_calls` finish_reason | Check `finish_reason` before reading `content` |
| Timeout on large outputs | Use 30–60s timeout; enable `stream: true` for UX |
| `content` is null when tool called | `content` may be null when `tool_calls` is present |
| Using `Authorization` header with raw key | Use `api-subscription-key` for `sk_xxx` keys |

## Reasoning

When `reasoning_effort` is set, the response includes a `reasoning_content` field alongside `content`:

```python
reasoning = choice["message"].get("reasoning_content")  # chain-of-thought
answer = choice["message"]["content"]
```

Set `reasoning_effort: null` to disable reasoning and reduce latency/cost.

## References

- [Sarvam Chat Completions Docs](https://docs.sarvam.ai/api-reference-docs/chat/chat-completions)
- [Authentication Guide](https://docs.sarvam.ai/api-reference-docs/authentication)
- [Models Overview](https://docs.sarvam.ai/api-reference-docs/getting-started/models)
