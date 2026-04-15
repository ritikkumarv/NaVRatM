"""FastAPI application entry point — NaVRatM Beneficiary Intelligence."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import CORS_ORIGINS
from app.api.routes import health, applications, documents, voice

app = FastAPI(
    title="NaVRatM — Beneficiary Intelligence & Fraud Detection",
    description="AI-powered fraud detection assistant for Indian welfare schemes, powered by Sarvam AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router)
app.include_router(applications.router)
app.include_router(documents.router)
app.include_router(voice.router)


@app.get("/")
async def root():
    return {
        "name": "NaVRatM",
        "tagline": "AI-Driven Beneficiary Intelligence & Fraud Detection",
        "version": "1.0.0",
        "docs": "/docs",
    }
