"""SQLAlchemy async models — SQLite + aiosqlite backend."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from app.config import DATABASE_URL

Base = declarative_base()


def _uuid() -> str:
    return str(uuid.uuid4())[:8]


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ApplicationDB(Base):
    __tablename__ = "applications"

    id = Column(String, primary_key=True, default=_uuid)
    declared_json = Column(Text, default="{}")
    status = Column(String, default="pending")
    risk_score = Column(Integer, nullable=True)
    risk_band = Column(String, nullable=True)
    risk_factors_json = Column(Text, default="[]")
    discrepancies_json = Column(Text, default="[]")
    anomalies_json = Column(Text, default="[]")
    network_flags_json = Column(Text, default="[]")
    explanation = Column(Text, nullable=True)
    decision_action = Column(String, nullable=True)
    decision_reason = Column(Text, nullable=True)
    decision_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)

    documents = relationship(
        "DocumentDB", back_populates="application", cascade="all, delete-orphan"
    )

    # ── JSON helpers ──

    def set_declared(self, data: dict) -> None:
        self.declared_json = json.dumps(data)

    def get_declared(self) -> dict:
        return json.loads(self.declared_json) if self.declared_json else {}

    def set_discrepancies(self, items: list[dict]) -> None:
        self.discrepancies_json = json.dumps(items)

    def get_discrepancies(self) -> list[dict]:
        return json.loads(self.discrepancies_json) if self.discrepancies_json else []

    def set_risk_factors(self, items: list[dict]) -> None:
        self.risk_factors_json = json.dumps(items)

    def get_risk_factors(self) -> list[dict]:
        return json.loads(self.risk_factors_json) if self.risk_factors_json else []

    def set_anomalies(self, items: list[dict]) -> None:
        self.anomalies_json = json.dumps(items)

    def get_anomalies(self) -> list[dict]:
        return json.loads(self.anomalies_json) if self.anomalies_json else []

    def set_network_flags(self, items: list[dict]) -> None:
        self.network_flags_json = json.dumps(items)

    def get_network_flags(self) -> list[dict]:
        return json.loads(self.network_flags_json) if self.network_flags_json else []


class DocumentDB(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=_uuid)
    application_id = Column(String, ForeignKey("applications.id"), nullable=True)
    filename = Column(String, default="")
    document_type = Column(String, default="other")
    extracted_json = Column(Text, default="{}")
    raw_ocr_text = Column(Text, default="")
    file_path = Column(String, default="")
    confidence = Column(Float, default=0.0)
    created_at = Column(DateTime, default=_now)

    application = relationship("ApplicationDB", back_populates="documents")

    def set_extracted(self, data: dict) -> None:
        self.extracted_json = json.dumps(data)

    def get_extracted(self) -> dict:
        return json.loads(self.extracted_json) if self.extracted_json else {}


class AuditLogDB(Base):
    __tablename__ = "audit_log"

    id = Column(String, primary_key=True, default=_uuid)
    application_id = Column(String, nullable=True)
    action = Column(String, default="")
    actor = Column(String, default="")
    details_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=_now)

    def set_details(self, data: dict) -> None:
        self.details_json = json.dumps(data)

    def get_details(self) -> dict:
        return json.loads(self.details_json) if self.details_json else {}


# ────────────────────── Engine setup ──────────────────────

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """Dependency for FastAPI routes."""
    async with async_session() as session:
        yield session
