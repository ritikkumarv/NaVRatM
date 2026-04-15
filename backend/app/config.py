"""Application configuration — loads from .env file."""

import os
from dotenv import load_dotenv

load_dotenv()

SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "")
SARVAM_BASE_URL: str = "https://api.sarvam.ai"
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./navratm.db")
CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]

# Sarvam model IDs
SARVAM_LLM_MODEL: str = "sarvam-m"          # use sarvam-m (24B) for speed; swap to sarvam-105b for quality
SARVAM_LLM_MODEL_HEAVY: str = "sarvam-m"    # flagship reasoning model
SARVAM_STT_MODEL: str = "saaras:v3"
SARVAM_TTS_TARGET_LANG: str = "hi-IN"
