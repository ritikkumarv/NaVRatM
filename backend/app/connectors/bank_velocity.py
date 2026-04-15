"""
Bank-account velocity-signals connector (mock/synthetic).

Returns beneficiary-mapping count, average monthly credits,
unusual-pattern flag, and last transaction date.

Privacy: Account numbers are never included.
Trust: 0.85 — synthetic.
"""

from __future__ import annotations
from typing import Any

from app.connectors import BaseConnector, ConnectorResult, SourceReliability

_TRUST = 0.85
_SOURCE = "bank_velocity"

_PROFILES: dict[str, dict[str, Any]] = {
    "clean": {
        "mapped_beneficiary_count": 1,
        "avg_monthly_credits": 20000,
        "unusual_pattern_flag": False,
        "last_transaction_date": "2026-04-10",
    },
    "fraud-ring": {
        # Shared bank account mapped to many beneficiaries — key fraud signal
        "mapped_beneficiary_count": 14,
        "avg_monthly_credits": 185000,
        "unusual_pattern_flag": True,
        "last_transaction_date": "2026-04-14",
    },
    "income-mismatch": {
        "mapped_beneficiary_count": 1,
        "avg_monthly_credits": 95000,
        "unusual_pattern_flag": False,
        "last_transaction_date": "2026-04-12",
    },
    "deceased": {
        "mapped_beneficiary_count": 1,
        "avg_monthly_credits": 8500,
        "unusual_pattern_flag": True,     # credits after reported death
        "last_transaction_date": "2026-03-28",
    },
}


def _resolve(entity_id: str) -> dict[str, Any] | None:
    eid = entity_id.lower()
    for prefix in _PROFILES:
        if eid.startswith(prefix):
            return _PROFILES[prefix]
    return None


class BankVelocityConnector(BaseConnector):
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
                evidence_uri="https://npci.org.in",
            ),
        )
