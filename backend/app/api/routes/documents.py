"""Document upload & OCR routes."""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, File, Form, UploadFile

from app.core import sarvam_client
from app.core.pii_masker import mask_fields
from app.models.schemas import DocumentType, DocumentUploadResponse, ExtractedFields

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/documents", tags=["documents"])

_DOC_TYPE_MAP: dict[str, DocumentType] = {
    "aadhaar": DocumentType.AADHAAR,
    "pan": DocumentType.PAN,
    "income_certificate": DocumentType.INCOME_CERT,
    "income_cert": DocumentType.INCOME_CERT,
    "bank_statement": DocumentType.BANK_STMT,
    "bank_stmt": DocumentType.BANK_STMT,
    "birth_certificate": DocumentType.BIRTH_CERT,
    "land_record": DocumentType.LAND_RECORD,
    "voter_id": DocumentType.VOTER_ID,
    "ration_card": DocumentType.RATION_CARD,
}


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form("aadhaar"),
):
    """Upload a document image and extract structured fields via Sarvam OCR/LLM."""
    image_bytes = await file.read()
    doc_id = f"DOC-{str(uuid.uuid4())[:6].upper()}"

    raw = await sarvam_client.extract_document_fields(
        image_bytes,
        document_type=document_type,
        filename=file.filename or "document.png",
    )

    # Mask PII
    masked = mask_fields(raw)

    dt = _DOC_TYPE_MAP.get(masked.get("document_type", "other"), DocumentType.OTHER)
    masked["document_type"] = dt.value

    try:
        extracted = ExtractedFields(**masked)
    except Exception:
        extracted = ExtractedFields(document_type=dt, raw_text=str(masked))

    return DocumentUploadResponse(
        id=doc_id,
        filename=file.filename or "unknown",
        document_type=dt,
        extracted_fields=extracted,
        raw_ocr_text=extracted.raw_text,
        status="processed",
    )
