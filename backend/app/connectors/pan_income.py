"""
PAN / Income-tax connector (mock/synthetic).

Returns AIS-like income summary, declared vs assessed income, credit score
indicator, employer information, and tax-filing status.

Privacy: PAN numbers are masked (first 5 + last 1 visible only).
"""

from __future__ import annotations
from typing import Any

from app.connectors import BaseConnector, ConnectorResult, SourceReliability

_TRUST = 0.90
_SOURCE = "pan_income_tax"

_PROFILES: dict[str, dict[str, Any]] = {
    "clean": {
        "assessed_annual_income": 240000,
        "declared_annual_income": 240000,
        "income_sources": [
            {"type": "agriculture", "amount": 240000},
        ],
        "credit_score_band": "no_history",
        "employer_name": None,
        "tax_filing_status": "non_taxable",
    },
    "fraud-ring": {
        "assessed_annual_income": 780000,
        "declared_annual_income": 180000,
        "income_sources": [
            {"type": "salary", "amount": 480000},
            {"type": "business", "amount": 300000},
        ],
        "credit_score_band": "good",            # 700-750
        "employer_name": "XXXXX Enterprises",    # masked
        "tax_filing_status": "filed_regular",
    },
    "income-mismatch": {
        "assessed_annual_income": 960000,
        "declared_annual_income": 180000,
        "income_sources": [
            {"type": "salary", "amount": 600000},
            {"type": "rental", "amount": 360000},
        ],
        "credit_score_band": "excellent",        # 750+
        "employer_name": "XXXXX Ltd.",
        "tax_filing_status": "filed_regular",
    },
    "deceased": {
        "assessed_annual_income": 120000,
        "declared_annual_income": 120000,
        "income_sources": [
            {"type": "pension", "amount": 120000},
        ],
        "credit_score_band": "no_history",
        "employer_name": None,
        "tax_filing_status": "non_taxable",
    },
}


def _resolve(entity_id: str) -> dict[str, Any] | None:
    eid = entity_id.lower()
    for prefix in _PROFILES:
        if eid.startswith(prefix):
            return _PROFILES[prefix]
    return None


class PanIncomeConnector(BaseConnector):
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
                evidence_uri="https://incometax.gov.in",
            ),
        )
