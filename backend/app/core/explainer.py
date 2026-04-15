"""Explainer agent — generates plain-language risk explanations using Sarvam LLM."""

from __future__ import annotations
import json, logging
from app.core import sarvam_client
from app.models.schemas import CanonicalRiskProfile, Discrepancy
from app.config import SARVAM_LLM_MODEL_HEAVY

log = logging.getLogger(__name__)


async def explain_risk(
    discrepancies: list[Discrepancy],
    risk_profile: CanonicalRiskProfile,
    lang: str = "en",
) -> str:
    """Generate a plain-language explanation of the risk assessment."""
    discs_summary = []
    for d in discrepancies:
        discs_summary.append({
            "field": d.field,
            "declared": d.declared_value,
            "found": d.extracted_value,
            "source": d.source_document,
            "severity": d.severity.value,
            "details": d.details,
        })

    factors_summary = []
    for f in risk_profile.factors:
        factors_summary.append({
            "rule": f.factor_name,
            "points": f.points,
            "description": f.description,
        })

    prompt = f"""You are a fraud detection assistant for Indian government welfare schemes.
An application has been analysed and received a risk score of {risk_profile.risk_score}/100 ({risk_profile.risk_band.value} risk).

Discrepancies found:
{json.dumps(discs_summary, indent=2)}

Risk factors:
{json.dumps(factors_summary, indent=2)}

Recommended action: {risk_profile.recommended_action}

Write a clear, professional summary for a government officer. Structure it as:

## Summary
One paragraph overview of the application risk.

## Key Findings
Bullet points of each discrepancy with specific values and sources.

## Recommendation
Clear action recommendation with justification.

Rules:
- Be factual and cite specific document sources
- Use simple language suitable for a government officer
- Do NOT include any raw PII (Aadhaar numbers, bank accounts, phone numbers)
- Keep it concise — max 200 words"""

    try:
        explanation = await sarvam_client.chat(
            messages=[{"role": "user", "content": prompt}],
            model=SARVAM_LLM_MODEL_HEAVY,
        )
    except Exception as e:
        log.error(f"LLM explanation failed: {e}")
        explanation = _fallback_explanation(discrepancies, risk_profile)

    if lang and lang not in ("en", "en-IN"):
        try:
            lang_code = lang if "-" in lang else f"{lang}-IN"
            explanation = await sarvam_client.translate_text(explanation, "en-IN", lang_code)
        except Exception as e:
            log.warning(f"Translation to {lang} failed: {e}")

    return explanation


def _fallback_explanation(discrepancies: list[Discrepancy], risk_profile: CanonicalRiskProfile) -> str:
    """Generate a basic explanation without LLM when API is unavailable."""
    lines = [
        f"## Risk Assessment Summary",
        f"",
        f"**Risk Score: {risk_profile.risk_score}/100 ({risk_profile.risk_band.value.upper()})**",
        f"",
        f"### Key Findings",
    ]
    for d in discrepancies:
        icon = "🔴" if d.severity.value == "high" else "🟡" if d.severity.value == "medium" else "🟢"
        lines.append(f"- {icon} **{d.field.replace('_', ' ').title()}**: {d.details}")

    lines.append(f"")
    lines.append(f"### Recommendation")
    lines.append(f"**{risk_profile.recommended_action.replace('_', ' ').title()}** — "
                 f"{'Significant discrepancies detected requiring manual review.' if risk_profile.risk_score > 50 else 'Minor issues detected but within acceptable limits.'}")

    return "\n".join(lines)
