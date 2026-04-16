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


def mask_email(value: str | None) -> str | None:
    """user@domain.com → u***@domain.com"""
    if not value:
        return value
    match = re.match(r"^([^@])([^@]*)@(.+)$", value.strip())
    if match:
        return f"{match.group(1)}***@{match.group(3)}"
    return value


def mask_name(value: str | None) -> str | None:
    """Rajesh Kumar → R*** K***"""
    if not value:
        return value
    parts = value.strip().split()
    masked_parts = []
    for part in parts:
        if len(part) > 1:
            masked_parts.append(f"{part[0]}***")
        else:
            masked_parts.append(part)
    return " ".join(masked_parts)


def mask_fields(fields: dict) -> dict:
    """Apply masking to a dict of extracted fields.  Returns a new dict."""
    masked = dict(fields)
    masked["aadhaar_masked"] = mask_aadhaar(masked.pop("aadhaar_number", None) or masked.get("aadhaar_masked"))
    masked["pan_masked"] = mask_pan(masked.pop("pan_number", None) or masked.get("pan_masked"))
    masked["bank_account_masked"] = mask_bank_account(masked.pop("bank_account", None) or masked.get("bank_account_masked"))
    masked["phone_masked"] = mask_phone(masked.pop("phone", None) or masked.get("phone_masked"))
    if "email" in masked:
        masked["email"] = mask_email(masked["email"])
    return masked


def mask_text(text: str) -> str:
    """Mask PII patterns in free text."""
    # Email addresses: user@domain.com → u***@domain.com
    text = re.sub(
        r"\b([a-zA-Z0-9])([a-zA-Z0-9._%+-]*)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b",
        lambda m: f"{m.group(1)}***@{m.group(3)}",
        text,
    )
    # PAN pattern: 5 letters + 4 digits + 1 letter
    text = re.sub(
        r"\b[A-Z]{5}\d{4}[A-Z]\b",
        lambda m: f"XXXXX{m.group()[5:9]}X",
        text,
    )
    # Aadhaar pattern: 4-4-4 digits
    text = re.sub(r"\b(\d{4})\s?(\d{4})\s?(\d{4})\b", r"XXXX XXXX \3", text)
    # Phone: 10 consecutive digits
    text = re.sub(r"\b(\d{6})(\d{4})\b", r"XXXXXX\2", text)
    # Bank account: long digit strings
    text = re.sub(
        r"\b(\d{6,}?)(\d{4})\b",
        lambda m: "X" * len(m.group(1)) + m.group(2),
        text,
    )
    return text
