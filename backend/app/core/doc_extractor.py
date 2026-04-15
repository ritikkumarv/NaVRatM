"""Document field extractor — parses Sarvam OCR/LLM output into structured fields."""

from __future__ import annotations
import logging
from app.core import sarvam_client
from app.core.pii_masker import mask_fields
from app.models.schemas import ExtractedFields, DocumentType

log = logging.getLogger(__name__)

# Map user-friendly names to enum
_DOC_TYPE_MAP = {
    "aadhaar": DocumentType.AADHAAR,
    "pan": DocumentType.PAN,
    "income_certificate": DocumentType.INCOME_CERT,
    "income_cert": DocumentType.INCOME_CERT,
    "bank_statement": DocumentType.BANK_STMT,
    "bank_stmt": DocumentType.BANK_STMT,
    "birth_certificate": DocumentType.BIRTH_CERT,
    "land_record": DocumentType.LAND_RECORD,
}


async def extract_from_image(
    image_bytes: bytes,
    document_type: str = "aadhaar",
    filename: str = "document.png",
    mask_pii: bool = True,
) -> ExtractedFields:
    """Extract structured fields from a document image.

    1. Sends image to Sarvam LLM for field extraction.
    2. Optionally masks PII in the result.
    3. Returns a validated ExtractedFields object.
    """
    raw = await sarvam_client.extract_fields_from_image(image_bytes, document_type, filename)

    # Mask PII before storing/displaying
    if mask_pii:
        raw = mask_fields(raw)

    # Normalise document_type
    dt = _DOC_TYPE_MAP.get(raw.get("document_type", "other"), DocumentType.OTHER)
    raw["document_type"] = dt.value

    try:
        return ExtractedFields(**raw)
    except Exception as e:
        log.error(f"Failed to parse extracted fields: {e}")
        return ExtractedFields(
            raw_text=str(raw),
            document_type=_DOC_TYPE_MAP.get(document_type, DocumentType.OTHER).value,
            confidence=0.0,
        )


async def extract_from_text(
    text: str,
    document_type: str = "other",
) -> ExtractedFields:
    """Extract fields from raw OCR text using LLM reasoning."""
    prompt = f"""Extract structured fields from this {document_type} document text.
Return ONLY valid JSON with keys: full_name, date_of_birth (YYYY-MM-DD), gender, address,
aadhaar_number, pan_number, income_monthly (float), bank_account, phone, document_type, confidence (0-1), language_detected.

Document text:
{text}"""

    try:
        response = await sarvam_client.chat_completion(
            messages=[{"role": "user", "content": prompt}]
        )
        import json
        data = json.loads(response)
        data = mask_fields(data)
        return ExtractedFields(**data)
    except Exception as e:
        log.error(f"Text extraction failed: {e}")
        return ExtractedFields(raw_text=text, document_type=document_type, confidence=0.0)
