"""Application configuration — loads from .env file."""

from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

# ── Sarvam AI ──
SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "")
SARVAM_BASE_URL: str = "https://api.sarvam.ai"

# Model IDs
SARVAM_LLM_MODEL: str = "sarvam-30b"            # primary LLM (64K ctx)
SARVAM_LLM_MODEL_HEAVY: str = "sarvam-105b"     # heavy reasoning (128K ctx)
SARVAM_STT_MODEL: str = "saarika:v2.5"          # STT default (12 langs)
SARVAM_STT_MODEL_ADV: str = "saaras:v3"         # STT advanced (23 langs, modes)
SARVAM_STT_TRANSLATE_MODEL: str = "saaras:v2.5"  # STT-translate → English
SARVAM_TTS_MODEL: str = "bulbul:v3"             # TTS (37 voices)
SARVAM_TRANSLATE_MODEL: str = "mayura:v1"        # text translate (11 langs)

# ── Database ──
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./navratm.db")

# ── CORS ──
CORS_ORIGINS: list[str] = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
]

# ── Risk band thresholds ──
RISK_BAND_LOW = (0, 24)
RISK_BAND_MEDIUM = (25, 49)
RISK_BAND_HIGH = (50, 74)
RISK_BAND_CRITICAL = (75, 100)


def risk_band_for_score(score: int) -> str:
    """Return risk band label for a given score."""
    if score <= RISK_BAND_LOW[1]:
        return "low"
    if score <= RISK_BAND_MEDIUM[1]:
        return "medium"
    if score <= RISK_BAND_HIGH[1]:
        return "high"
    return "critical"
