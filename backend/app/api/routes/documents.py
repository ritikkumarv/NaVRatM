"""Document upload & OCR routes."""

from __future__ import annotations
import uuid, logging
from fastapi import APIRouter, UploadFile, File, Form
from app.models.schemas import DocumentUploadResponse, DocumentType
from app.core.doc_extractor import extract_from_image

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form("aadhaar"),
):
    """Upload a document image and extract structured fields via Sarvam OCR/LLM."""
    image_bytes = await file.read()
    doc_id = f"DOC-{str(uuid.uuid4())[:6].upper()}"

    extracted = await extract_from_image(
        image_bytes,
        document_type=document_type,
        filename=file.filename or "document.png",
    )

    return DocumentUploadResponse(
        id=doc_id,
        filename=file.filename or "unknown",
        document_type=extracted.document_type,
        extracted_fields=extracted,
        raw_ocr_text=extracted.raw_text,
        status="processed",
    )
