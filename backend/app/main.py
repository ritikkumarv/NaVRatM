"""FastAPI application entry point — NaVRatM Beneficiary Intelligence."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import applications, documents, health, metrics, voice
from app.config import CORS_ORIGINS
from app.models.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    await init_db()
    yield


app = FastAPI(
    title="NaVRatM — Beneficiary Intelligence & Fraud Detection",
    description="AI-powered fraud detection for Indian welfare schemes, powered by Sarvam AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS + [
        "http://127.0.0.1:8080",
        "http://localhost:8080",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "null",  # file:// origin for local HTML
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router)
app.include_router(applications.router)
app.include_router(documents.router)
app.include_router(voice.router)
app.include_router(metrics.router)


@app.get("/")
async def root():
    return {
        "name": "NaVRatM",
        "tagline": "AI-Driven Beneficiary Intelligence & Fraud Detection",
        "version": "1.0.0",
        "docs": "/docs",
    }
