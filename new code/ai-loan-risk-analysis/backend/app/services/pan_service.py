import re


PAN_PATTERN = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")


def verify_pan(pan: str) -> dict:
    return {
        "pan": pan,
        "pan_verified": bool(PAN_PATTERN.fullmatch(pan)),
    }
