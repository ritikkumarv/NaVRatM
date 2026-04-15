"""
Death-registry connector (mock/synthetic).

Returns deceased-match flag, match confidence, registry date, and source state.

Trust: 0.90 — synthetic; civil registration data is authoritative but updates
can lag by weeks in rural areas.
"""

from __future__ import annotations
from typing import Any

from app.connectors import BaseConnector, ConnectorResult, SourceReliability

_TRUST = 0.90
_SOURCE = "death_registry"

_PROFILES: dict[str, dict[str, Any]] = {
    "clean": {
        "is_deceased_match": False,
        "match_confidence": 0.0,
        "registry_date": None,
        "source_state": None,
    },
    "fraud-ring": {
        "is_deceased_match": False,
        "match_confidence": 0.0,
        "registry_date": None,
        "source_state": None,
    },
    "income-mismatch": {
        "is_deceased_match": False,
        "match_confidence": 0.0,
        "registry_date": None,
        "source_state": None,
    },
    "deceased": {
        "is_deceased_match": True,
        "match_confidence": 0.92,
        "registry_date": "2025-09-18",
        "source_state": "Jharkhand",
    },
}


def _resolve(entity_id: str) -> dict[str, Any] | None:
    eid = entity_id.lower()
    for prefix in _PROFILES:
        if eid.startswith(prefix):
            return _PROFILES[prefix]
    return None


class DeathRegistryConnector(BaseConnector):
    name = _SOURCE

    async def fetch(self, entity_id: str, **kwargs: Any) -> ConnectorResult:
        profile = _resolve(entity_id)
        if profile is None:
            return self._empty()

        return ConnectorResult(
            source_name=self.name,
            data=profile,
            reliability=SourceReliability(
                source_name=self.name,
                source_trust_score=_TRUST,
                last_updated_at=self._now_iso(),
                access_mode="synthetic",
                evidence_uri="https://crsorgi.gov.in",
            ),
        )
