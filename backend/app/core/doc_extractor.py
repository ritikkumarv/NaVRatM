"""Document field extractor — routes images/text through Sarvam and normalises output."""

from __future__ import annotations

import json
import logging

from app.core import sarvam_client
from app.core.pii_masker import mask_fields
from app.models.schemas import DocumentType, ExtractedFields

log = logging.getLogger(__name__)

# ── Normalisation map (user-friendly string → enum) ──────────────────────

_DOC_TYPE_MAP: dict[str, DocumentType] = {
    "aadhaar": DocumentType.AADHAAR,
    "pan": DocumentType.PAN,
    "income_certificate": DocumentType.INCOME_CERT,
    "income_cert": DocumentType.INCOME_CERT,
    "income certificate": DocumentType.INCOME_CERT,
    "bank_statement": DocumentType.BANK_STMT,
    "bank_stmt": DocumentType.BANK_STMT,
    "bank statement": DocumentType.BANK_STMT,
    "birth_certificate": DocumentType.BIRTH_CERT,
    "birth certificate": DocumentType.BIRTH_CERT,
    "land_record": DocumentType.LAND_RECORD,
    "land record": DocumentType.LAND_RECORD,
    "voter_id": DocumentType.VOTER_ID,
    "voter id": DocumentType.VOTER_ID,
    "ration_card": DocumentType.RATION_CARD,
    "ration card": DocumentType.RATION_CARD,
}


def _normalise_doc_type(raw: str) -> DocumentType:
    """Convert a loose document type string to its enum value."""
    return _DOC_TYPE_MAP.get(raw.strip().lower(), DocumentType.OTHER)


# ── Public API ───────────────────────────────────────────────────────────


async def extract_from_image(
    image_bytes: bytes,
    document_type: str = "aadhaar",
    filename: str = "document.png",
    mask_pii: bool = True,
) -> ExtractedFields:
    """Extract structured fields from a document image.

    1. Calls ``sarvam_client.extract_document_fields()`` (vision LLM).
    2. Optionally masks PII via ``pii_masker.mask_fields()``.
    3. Returns a validated ``ExtractedFields`` with normalised document type.
    """
    try:
        raw: dict = await sarvam_client.extract_document_fields(
            image_bytes, document_type=document_type, filename=filename,
        )
    except Exception as exc:
        log.warning("Sarvam extraction unavailable (%s) — using mock fallback", exc)
        raw = _mock_extraction(document_type)

    if mask_pii:
        raw = mask_fields(raw)

    dt = _normalise_doc_type(raw.get("document_type", document_type))
    raw["document_type"] = dt.value

    return _safe_parse(raw, document_type)


async def extract_from_text(
    text: str,
    document_type: str = "other",
) -> ExtractedFields:
    """Extract fields from raw OCR/pasted text via Sarvam chat LLM."""
    prompt = (
        f"You are a document field extractor for Indian government documents.\n"
        f"Extract ALL fields from this {document_type} document text into JSON.\n\n"
        "Return ONLY valid JSON with these keys (use null for missing fields):\n"
        "{\n"
        '  "full_name": "...",\n'
        '  "dob": "YYYY-MM-DD or null",\n'
        '  "gender": "male/female/other or null",\n'
        '  "address": "full address or null",\n'
        '  "aadhaar_masked": "XXXX-XXXX-NNNN or null",\n'
        '  "pan_masked": "XXXXXNNNNX or null",\n'
        '  "income_monthly": 0.0,\n'
        '  "bank_account_masked": "XXXXXXXXXX1234 or null",\n'
        '  "phone_masked": "XXXXXX1234 or null",\n'
        f'  "document_type": "{document_type}",\n'
        '  "confidence": 0.85,\n'
        '  "raw_text": "...",\n'
        '  "language_detected": "hi-IN"\n'
        "}\n\n"
        f"Document text:\n{text}"
    )

    try:
        response = await sarvam_client.chat(
            messages=[{"role": "user", "content": prompt}],
        )
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
        data: dict = json.loads(cleaned)
    except Exception as exc:
        log.warning("Text extraction failed (%s) — returning minimal fields", exc)
        data = {"raw_text": text, "document_type": document_type, "confidence": 0.0}

    data = mask_fields(data)
    dt = _normalise_doc_type(data.get("document_type", document_type))
    data["document_type"] = dt.value

    return _safe_parse(data, document_type)


# ── Helpers ──────────────────────────────────────────────────────────────


def _safe_parse(raw: dict, fallback_type: str) -> ExtractedFields:
    """Parse a dict into ExtractedFields, falling back on errors."""
    try:
        return ExtractedFields(**raw)
    except Exception as exc:
        log.error("Failed to parse extracted fields: %s", exc)
        return ExtractedFields(
            raw_text=str(raw),
            document_type=_normalise_doc_type(fallback_type).value,
            confidence=0.0,
        )


def _mock_extraction(doc_type: str) -> dict:
    """Deterministic mock for offline dev — mirrors sarvam_client mocks."""
    mocks: dict[str, dict] = {
        "aadhaar": {
            "full_name": "Ramesh Kumar Sharma",
            "dob": "1985-03-15",
            "gender": "male",
            "address": "42, Gandhi Nagar, Sector 12, Jaipur, Rajasthan 302015",
            "aadhaar_masked": "XXXX-XXXX-1098",
            "pan_masked": None,
            "income_monthly": None,
            "bank_account_masked": None,
            "phone_masked": None,
            "document_type": "aadhaar",
            "confidence": 0.92,
            "raw_text": "GOVERNMENT OF INDIA AADHAAR Ramesh Kumar Sharma",
            "language_detected": "hi-IN",
        },
        "pan": {
            "full_name": "Ramesh Kumar Sharma",
            "dob": "1985-03-15",
            "gender": "male",
            "address": None,
            "aadhaar_masked": None,
            "pan_masked": "XXXXX1234X",
            "income_monthly": None,
            "bank_account_masked": None,
            "phone_masked": None,
            "document_type": "pan",
            "confidence": 0.88,
            "raw_text": "INCOME TAX DEPARTMENT PAN CARD",
            "language_detected": "en-IN",
        },
        "income_certificate": {
            "full_name": "Ramesh Kumar",
            "dob": "1985-03-15",
            "gender": "male",
            "address": "42 Gandhi Nagar, Jaipur, Rajasthan",
            "aadhaar_masked": None,
            "pan_masked": None,
            "income_monthly": 8500.0,
            "bank_account_masked": None,
            "phone_masked": None,
            "document_type": "income_certificate",
            "confidence": 0.85,
            "raw_text": "INCOME CERTIFICATE Ramesh Kumar",
            "language_detected": "hi-IN",
        },
    }
    return dict(mocks.get(doc_type, mocks["aadhaar"]))
