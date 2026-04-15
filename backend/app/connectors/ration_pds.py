"""
Ration / PDS state-level connector (mock/synthetic).

Returns ration card type, family members listed, monthly entitlement,
last collection date, and active status.

Privacy: Card numbers are masked.
Trust: 0.75 — state-level data is often stale or inconsistently digitised.
"""

from __future__ import annotations
from typing import Any

from app.connectors import BaseConnector, ConnectorResult, SourceReliability

_TRUST = 0.75
_SOURCE = "ration_pds"

_PROFILES: dict[str, dict[str, Any]] = {
    "clean": {
        "card_type": "BPL",
        "card_number_masked": "XXXX-XXXX-4821",
        "family_members": [
            {"name_masked": "R***a Devi", "relation": "self", "age": 38},
            {"name_masked": "S***m Kumar", "relation": "spouse", "age": 42},
            {"name_masked": "A***a Kumari", "relation": "daughter", "age": 14},
        ],
        "monthly_entitlement_kg": 15.0,
        "last_collection_date": "2026-03-15",
        "active_status": True,
    },
    "fraud-ring": {
        "card_type": "AAY",
        "card_number_masked": "XXXX-XXXX-7713",
        "family_members": [
            {"name_masked": "M***d Ali", "relation": "self", "age": 45},
            {"name_masked": "F***a Begum", "relation": "spouse", "age": 40},
            {"name_masked": "I***n Ali", "relation": "son", "age": 22},
            {"name_masked": "S***a Begum", "relation": "daughter", "age": 18},
            {"name_masked": "A***d Ali", "relation": "son", "age": 16},
        ],
        "monthly_entitlement_kg": 35.0,
        "last_collection_date": "2026-04-01",
        "active_status": True,
    },
    "income-mismatch": {
        "card_type": "BPL",
        "card_number_masked": "XXXX-XXXX-5504",
        "family_members": [
            {"name_masked": "V***h Sharma", "relation": "self", "age": 35},
            {"name_masked": "P***a Sharma", "relation": "spouse", "age": 32},
        ],
        "monthly_entitlement_kg": 10.0,
        "last_collection_date": "2026-02-20",
        "active_status": True,
    },
    "deceased": {
        "card_type": "BPL",
        "card_number_masked": "XXXX-XXXX-2290",
        "family_members": [
            {"name_masked": "L***i Prasad", "relation": "self", "age": 72},
        ],
        "monthly_entitlement_kg": 5.0,
        "last_collection_date": "2025-11-10",
        "active_status": True,  # still active — stale data
    },
}


def _resolve(entity_id: str) -> dict[str, Any] | None:
    eid = entity_id.lower()
    for prefix in _PROFILES:
        if eid.startswith(prefix):
            return _PROFILES[prefix]
    return None


class RationPDSConnector(BaseConnector):
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
                evidence_uri="https://nfsa.gov.in",
            ),
        )
