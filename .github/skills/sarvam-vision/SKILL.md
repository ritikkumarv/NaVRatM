---
name: sarvam-vision
description: "Implement Sarvam Vision Document Intelligence API. Use when extracting text from PDFs or scanned documents, processing Indian language documents, converting tables to HTML/Markdown, integrating document intelligence jobs, uploading files for OCR, or handling multilingual document processing across 23 languages (22 Indian + English) with Sarvam AI."
argument-hint: "Feature to implement (e.g., 'extract text from Hindi PDF', 'convert table to markdown', 'process scanned document', 'document intelligence job pipeline')"
---

# Sarvam Vision — Document Intelligence

**Model**: Sarvam Vision (3B parameter multimodal VLM)  
**Auth**: `api-subscription-key: sk_xxx` header (required)  
**SDK**: `sarvamai` Python / JavaScript SDK (job-based async pipeline)

> Purpose-built for high-accuracy document intelligence across 23 languages (22 Indian + English). Extracts text, preserves layout, converts tables to HTML/Markdown.

## Capabilities

| Feature | Details |
|---------|---------|
| Text Extraction | PDFs, scanned documents; preserves layout and reading order |
| Table Conversion | Complex tables → HTML or Markdown; handles merged cells, multi-level headers, invisible borders |
| Languages | 23 languages native (22 Indian + English) |
| Output | HTML or Markdown (delivered in ZIP); JSON page-level data always included |

## Supported Input Formats

`PDF`, `PNG`, `JPG`, `ZIP` (flat archive of JPG/PNG pages)

## Output Formats

| Format | Description |
|--------|-------------|
| `md` | Markdown with structure preserved |
| `html` | HTML with tables and layout |
| JSON | Always included in output ZIP regardless of chosen format |

## Supported Languages

All 22 official Indian languages + English:

`hi-IN`, `bn-IN`, `ta-IN`, `te-IN`, `mr-IN`, `gu-IN`, `kn-IN`, `ml-IN`, `pa-IN`, `od-IN`, `as-IN`, `ur-IN`, `sa-IN`, `ne-IN`, `doi-IN`, `brx-IN`, `kok-IN`, `mai-IN`, `sd-IN`, `ks-IN`, `mni-IN`, `sat-IN`, `en-IN`

## Job Pipeline

Document Intelligence uses an **async job pipeline** — not a single HTTP call:

```
1. create_job()       → get job_id
2. upload_file()      → send document
3. start()            → begin processing
4. wait_until_complete() → poll for completion
5. get_page_metrics() → inspect results
6. download_output()  → save ZIP with results
```

## Implementation Patterns

### Python SDK (recommended)

```python
from sarvamai import SarvamAI

client = SarvamAI(api_subscription_key="YOUR_SARVAM_API_KEY")

# 1. Create job
job = client.document_intelligence.create_job(
    language="hi-IN",    # BCP-47 language code
    output_format="md",  # "md" or "html"
)
print(f"Job created: {job.job_id}")

# 2. Upload document
job.upload_file("document.pdf")

# 3. Start processing
job.start()

# 4. Wait for completion (polls internally)
status = job.wait_until_complete()
print(f"State: {status.job_state}")

# 5. Inspect metrics
metrics = job.get_page_metrics()
print(f"Page metrics: {metrics}")

# 6. Download result ZIP
job.download_output("./output.zip")
# ZIP contains: output.md (or .html) + page-level JSON
```

### Python — extract and read output in-memory

```python
import zipfile
import io

# After job.wait_until_complete()
zip_bytes = job.download_output_bytes()   # if SDK supports bytes variant
with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
    for name in zf.namelist():
        if name.endswith(".md"):
            text = zf.read(name).decode("utf-8")
            print(text)
        elif name.endswith(".json"):
            import json
            data = json.loads(zf.read(name))
```

### JavaScript SDK

```javascript
import { SarvamAIClient } from "sarvamai";

const client = new SarvamAIClient({ apiSubscriptionKey: "YOUR_SARVAM_API_KEY" });

const job = await client.documentIntelligence.createJob({
    language: "hi-IN",
    outputFormat: "md",
});

await job.uploadFile("document.pdf");
await job.start();

const status = await job.waitUntilComplete();
console.log(`State: ${status.job_state}`);

const metrics = job.getPageMetrics();
await job.downloadOutput("./output.zip");
```

### Error Handling

```python
from sarvamai import SarvamAI
import sarvamai.exceptions as err

try:
    job = client.document_intelligence.create_job(language="hi-IN", output_format="md")
    job.upload_file("document.pdf")
    job.start()
    status = job.wait_until_complete()

    if status.job_state != "completed":
        raise RuntimeError(f"Job failed with state: {status.job_state}")

    job.download_output("./output.zip")

except err.AuthenticationError:
    # Invalid api-subscription-key
    raise
except err.RateLimitError:
    # Quota exceeded — back off and retry
    raise
except Exception as e:
    print(f"Unexpected error: {e}")
    raise
```

## Job States

| State | Meaning |
|-------|---------|
| `created` | Job initialized, awaiting file upload |
| `uploaded` | File uploaded, not yet started |
| `processing` | Document being processed |
| `completed` | Output ready for download |
| `failed` | Processing error; check job details |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Calling `start()` before `upload_file()` | Always upload first, then start |
| Downloading output before `wait_until_complete()` | Wait for `completed` state |
| Passing unsupported `output_format` | Use `"md"` or `"html"` only |
| Expecting plain text response | Output is a ZIP file; extract contents |
| Using `/v1/chat/completions` for documents | Use the Document Intelligence job API instead |
| Assuming output ZIP has only one file | ZIP always includes JSON page data alongside md/html |
| Passing language code without region (`"hi"` not `"hi-IN"`) | Use full BCP-47 format: `"hi-IN"` |

## Use Case Patterns

### Scanned document OCR (any Indian language)
```python
job = client.document_intelligence.create_job(language="ta-IN", output_format="md")
job.upload_file("scanned_tamil_doc.jpg")
job.start()
job.wait_until_complete()
job.download_output("./tamil_output.zip")
```

### Multi-page PDF with tables (HTML output)
```python
job = client.document_intelligence.create_job(language="mr-IN", output_format="html")
job.upload_file("financial_report.pdf")
job.start()
job.wait_until_complete()
job.download_output("./report_output.zip")
# Unzip → output.html contains tables as proper <table> elements
```

### Batch documents via ZIP archive
```python
# ZIP must be a flat archive of JPG/PNG pages
job = client.document_intelligence.create_job(language="bn-IN", output_format="md")
job.upload_file("document_pages.zip")   # flat ZIP of page images
job.start()
job.wait_until_complete()
```

## Model Selection Guide

```
Need text/table extraction from documents or scanned images?
  → Sarvam Vision (Document Intelligence job API)

Need real-time chat or reasoning over document content?
  → Use sarvam-chat-completion with image_url after extracting with Vision

Need to translate extracted text?
  → Chain with sarvam-translate after extraction

Audio input?
  → Use sarvam-stt (not Vision)
```

## References

- [Sarvam Vision Model Overview](https://docs.sarvam.ai/api-reference-docs/models/sarvam-vision)
- [Document Intelligence API Reference](https://docs.sarvam.ai/api-reference-docs/document-intelligence)
- [Developer Guide / Overview](https://docs.sarvam.ai/api-reference-docs/api-guides-tutorials/document-intelligence/overview)
- [API Dashboard](https://dashboard.sarvam.ai)
