"""
Enrichment connector layer — base interface, result types, and registry.

Provides a unified async adapter pattern for all external data sources
used in fraud risk scoring. Each connector returns a ConnectorResult with
reliability metadata so downstream scoring can weight evidence appropriately.

Privacy note: No raw PII should ever appear in ConnectorResult.data —
all identifiers must be masked before inclusion.
"""

from __future__ import annotations

import abc
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

log = logging.getLogger(__name__)


# ────────────────────── Data contracts ──────────────────────
# Field names are identical to Sprint 1 schemas so these local
# dataclasses can be swapped to Pydantic imports later.

@dataclass
class SourceReliability:
    """Metadata about the trustworthiness/freshness of a connector result."""
    source_name: str
    source_trust_score: float          # 0.0 – 1.0
    last_updated_at: str               # ISO-8601
    access_mode: str                   # live | batch | cached | synthetic
    evidence_uri: str = ""             # optional link to authoritative source


@dataclass
class ConnectorResult:
    """Normalised output from any enrichment connector."""
    source_name: str
    data: dict[str, Any]
    reliability: SourceReliability


def _empty_result(source_name: str, trust: float = 0.1) -> ConnectorResult:
    """Return a graceful-degradation result when entity is not found."""
    return ConnectorResult(
        source_name=source_name,
        data={},
        reliability=SourceReliability(
            source_name=source_name,
            source_trust_score=trust,
            last_updated_at=datetime.now(timezone.utc).isoformat(),
            access_mode="synthetic",
            evidence_uri="",
        ),
    )


# ────────────────────── Abstract base ──────────────────────

class BaseConnector(abc.ABC):
    """All enrichment source adapters extend this."""

    name: str = "base"

    @abc.abstractmethod
    async def fetch(self, entity_id: str, **kwargs: Any) -> ConnectorResult:
        """Fetch enrichment data for *entity_id*.

        Must never raise on missing entities — return an empty
        ConnectorResult with a low trust score instead.
        """

    # convenience ----------------------------------------------------------
    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _empty(self, trust: float = 0.1) -> ConnectorResult:
        return _empty_result(self.name, trust)


# ────────────────────── Registry ──────────────────────

class ConnectorRegistry:
    """Thread-safe registry for named connectors."""

    def __init__(self) -> None:
        self._connectors: dict[str, BaseConnector] = {}

    def register(self, connector: BaseConnector) -> None:
        self._connectors[connector.name] = connector
        log.info("Registered connector: %s", connector.name)

    def get(self, name: str) -> BaseConnector | None:
        return self._connectors.get(name)

    def all(self) -> dict[str, BaseConnector]:
        return dict(self._connectors)

    def names(self) -> list[str]:
        return list(self._connectors.keys())


# Singleton registry used across the application
registry = ConnectorRegistry()


def _auto_register() -> None:
    """Import all built-in connectors so they self-register."""
    # Lazy imports to avoid circular deps
    from app.connectors.aadhaar import AadhaarConnector
    from app.connectors.pan_income import PanIncomeConnector
    from app.connectors.ration_pds import RationPDSConnector
    from app.connectors.voter import VoterConnector
    from app.connectors.blacklist import BlacklistConnector
    from app.connectors.police import PoliceConnector
    from app.connectors.bank_velocity import BankVelocityConnector
    from app.connectors.death_registry import DeathRegistryConnector
    from app.connectors.scheme_history import SchemeHistoryConnector

    for cls in (
        AadhaarConnector,
        PanIncomeConnector,
        RationPDSConnector,
        VoterConnector,
        BlacklistConnector,
        PoliceConnector,
        BankVelocityConnector,
        DeathRegistryConnector,
        SchemeHistoryConnector,
    ):
        registry.register(cls())


def boot_connectors() -> ConnectorRegistry:
    """Call once at app startup to populate the registry."""
    if not registry.names():
        _auto_register()
    return registry
