import re


AADHAAR_PATTERN = re.compile(r"^[0-9]{12}$")


def verify_aadhaar(aadhaar: str) -> dict:
    return {
        "aadhaar": aadhaar,
        "aadhaar_verified": bool(AADHAAR_PATTERN.fullmatch(aadhaar)),
    }
