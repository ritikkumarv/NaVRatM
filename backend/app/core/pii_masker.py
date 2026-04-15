"""PII masking — regex-based, applied at extraction time."""

from __future__ import annotations
import re


def mask_aadhaar(value: str | None) -> str | None:
    """9876 5432 1098 → XXXX-XXXX-1098"""
    if not value:
        return value
    digits = re.sub(r"\D", "", value)
    if len(digits) == 12:
        return f"XXXX-XXXX-{digits[-4:]}"
    return value


def mask_pan(value: str | None) -> str | None:
    """ABCRS1234K → XXXXX1234X"""
    if not value:
        return value
    v = value.strip().upper()
    if len(v) == 10:
        return f"XXXXX{v[5:9]}X"
    return value


def mask_bank_account(value: str | None) -> str | None:
    """50100012345678 → XXXXXXXXXX5678"""
    if not value:
        return value
    digits = re.sub(r"\D", "", value)
    if len(digits) >= 8:
        return "X" * (len(digits) - 4) + digits[-4:]
    return value


def mask_phone(value: str | None) -> str | None:
    """9876543210 → XXXXXX3210"""
    if not value:
        return value
    digits = re.sub(r"\D", "", value)
    if len(digits) == 10:
        return f"XXXXXX{digits[-4:]}"
    return value


def mask_fields(fields: dict) -> dict:
    """Apply masking to a dict of extracted fields. Returns a new dict."""
    masked = dict(fields)
    masked["aadhaar_number"] = mask_aadhaar(masked.get("aadhaar_number"))
    masked["pan_number"] = mask_pan(masked.get("pan_number"))
    masked["bank_account"] = mask_bank_account(masked.get("bank_account"))
    masked["phone"] = mask_phone(masked.get("phone"))
    return masked


def mask_text(text: str) -> str:
    """Mask PII patterns in free text."""
    # Aadhaar pattern: 4-4-4 digits
    text = re.sub(r"\b(\d{4})\s?(\d{4})\s?(\d{4})\b", r"XXXX XXXX \3", text)
    # Phone: 10 consecutive digits
    text = re.sub(r"\b(\d{6})(\d{4})\b", r"XXXXXX\2", text)
    # Bank account: long digit strings
    text = re.sub(r"\b(\d{6,}?)(\d{4})\b", lambda m: "X" * len(m.group(1)) + m.group(2), text)
    return text
