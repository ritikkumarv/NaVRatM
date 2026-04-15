"""SQLAlchemy database models — SQLite backend."""

from __future__ import annotations
import uuid, json
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, Text, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.config import DATABASE_URL

Base = declarative_base()


def _uuid() -> str:
    return str(uuid.uuid4())[:8]


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ApplicationDB(Base):
    __tablename__ = "applications"

    id = Column(String, primary_key=True, default=_uuid)
    declared_json = Column(Text, default="{}")  # JSON blob of DeclaredValues
    status = Column(String, default="pending")
    risk_score = Column(Integer, nullable=True)
    risk_level = Column(String, nullable=True)
    risk_factors_json = Column(Text, default="[]")
    discrepancies_json = Column(Text, default="[]")
    explanation = Column(Text, nullable=True)
    decision_action = Column(String, nullable=True)
    decision_reason = Column(Text, nullable=True)
    decision_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)

    documents = relationship("DocumentDB", back_populates="application", cascade="all, delete-orphan")

    def set_declared(self, declared: dict):
        self.declared_json = json.dumps(declared)

    def get_declared(self) -> dict:
        return json.loads(self.declared_json) if self.declared_json else {}

    def set_discrepancies(self, discs: list[dict]):
        self.discrepancies_json = json.dumps(discs)

    def get_discrepancies(self) -> list[dict]:
        return json.loads(self.discrepancies_json) if self.discrepancies_json else []

    def set_risk_factors(self, factors: list[dict]):
        self.risk_factors_json = json.dumps(factors)

    def get_risk_factors(self) -> list[dict]:
        return json.loads(self.risk_factors_json) if self.risk_factors_json else []


class DocumentDB(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=_uuid)
    application_id = Column(String, ForeignKey("applications.id"), nullable=True)
    filename = Column(String, default="")
    document_type = Column(String, default="other")
    extracted_json = Column(Text, default="{}")  # JSON blob of ExtractedFields
    raw_ocr_text = Column(Text, default="")
    file_path = Column(String, default="")
    created_at = Column(DateTime, default=_now)

    application = relationship("ApplicationDB", back_populates="documents")

    def set_extracted(self, extracted: dict):
        self.extracted_json = json.dumps(extracted)

    def get_extracted(self) -> dict:
        return json.loads(self.extracted_json) if self.extracted_json else {}


class AuditLogDB(Base):
    __tablename__ = "audit_log"

    id = Column(String, primary_key=True, default=_uuid)
    application_id = Column(String, nullable=True)
    action = Column(String, default="")
    details = Column(Text, default="")
    officer_id = Column(String, default="")
    created_at = Column(DateTime, default=_now)


# ────────────────────── Engine setup ──────────────────────

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    """Dependency for FastAPI routes."""
    async with async_session() as session:
        yield session
