"""Cross-verification engine — compares extracted fields against declared values."""

from __future__ import annotations
import logging
from rapidfuzz import fuzz
from app.models.schemas import Discrepancy, Severity, ExtractedFields, DeclaredValues

log = logging.getLogger(__name__)

# Thresholds — tuned for demo sensitivity
NAME_MATCH_THRESHOLD = 85       # fuzzy ratio below this → flag
ADDRESS_MATCH_THRESHOLD = 50
INCOME_DEVIATION_THRESHOLD = 0.3  # 30% deviation → flag


def _fuzzy_score(a: str, b: str) -> float:
    """Normalised fuzzy match score 0-100."""
    if not a or not b:
        return 100.0  # can't compare if missing
    return fuzz.token_sort_ratio(a.lower().strip(), b.lower().strip())


def _normalise_name(name: str) -> str:
    """Basic normalisation for Indian names."""
    import re
    name = name.strip().lower()
    name = re.sub(r"\s+", " ", name)
    # Remove common prefixes
    for prefix in ["shri", "smt", "mr", "mrs", "ms", "dr"]:
        name = re.sub(rf"^{prefix}\.?\s*", "", name)
    return name.strip()


def verify_name(declared: str, extracted: str, source: str) -> Discrepancy | None:
    """Check name consistency using fuzzy matching."""
    if not declared or not extracted:
        return None
    score = _fuzzy_score(_normalise_name(declared), _normalise_name(extracted))
    if score >= NAME_MATCH_THRESHOLD:
        return None
    severity = Severity.HIGH if score < 50 else Severity.MEDIUM
    return Discrepancy(
        field="full_name",
        declared_value=declared,
        extracted_value=extracted,
        source_document=source,
        severity=severity,
        match_score=score / 100.0,
        details=f"Name fuzzy match score: {score:.0f}% (threshold: {NAME_MATCH_THRESHOLD}%)"
    )


def verify_dob(declared: str, extracted: str, source: str) -> Discrepancy | None:
    """Check date of birth consistency."""
    if not declared or not extracted:
        return None
    # Normalise dates: handle DD/MM/YYYY, YYYY-MM-DD, etc.
    import re
    def _norm(d: str) -> str:
        d = d.strip()
        m = re.match(r"(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})", d)
        if m:
            return f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"
        return d
    d1, d2 = _norm(declared), _norm(extracted)
    if d1 == d2:
        return None
    return Discrepancy(
        field="date_of_birth",
        declared_value=declared,
        extracted_value=extracted,
        source_document=source,
        severity=Severity.HIGH,
        match_score=0.0,
        details=f"DOB mismatch: declared '{declared}' vs extracted '{extracted}' from {source}"
    )


def verify_income(declared: float, extracted: float, source: str) -> Discrepancy | None:
    """Check income consistency — flag if deviation > threshold."""
    if declared <= 0 or extracted <= 0:
        return None
    deviation = abs(declared - extracted) / max(declared, extracted)
    if deviation <= INCOME_DEVIATION_THRESHOLD:
        return None
    severity = Severity.HIGH if deviation > 0.8 else Severity.MEDIUM
    return Discrepancy(
        field="income_monthly",
        declared_value=f"₹{declared:,.0f}",
        extracted_value=f"₹{extracted:,.0f}",
        source_document=source,
        severity=severity,
        match_score=1.0 - deviation,
        details=f"Income deviation: {deviation*100:.0f}% ({source} shows ₹{extracted:,.0f} vs declared ₹{declared:,.0f})"
    )


def verify_address(declared: str, extracted: str, source: str) -> Discrepancy | None:
    """Check address similarity with tolerant fuzzy matching."""
    if not declared or not extracted:
        return None
    score = _fuzzy_score(declared, extracted)
    if score >= ADDRESS_MATCH_THRESHOLD:
        return None
    return Discrepancy(
        field="address",
        declared_value=declared,
        extracted_value=extracted,
        source_document=source,
        severity=Severity.MEDIUM,
        match_score=score / 100.0,
        details=f"Address fuzzy match: {score:.0f}% (threshold: {ADDRESS_MATCH_THRESHOLD}%)"
    )


def verify_gender(declared: str, extracted: str, source: str) -> Discrepancy | None:
    """Check gender consistency."""
    if not declared or not extracted:
        return None
    d, e = declared.strip().lower(), extracted.strip().lower()
    if d == e or d[0] == e[0]:  # 'm' == 'male', 'f' == 'female'
        return None
    return Discrepancy(
        field="gender",
        declared_value=declared,
        extracted_value=extracted,
        source_document=source,
        severity=Severity.HIGH,
        match_score=0.0,
        details=f"Gender mismatch: '{declared}' vs '{extracted}'"
    )


def verify_phone(declared: str, extracted: str, source: str) -> Discrepancy | None:
    """Check phone number consistency."""
    if not declared or not extracted:
        return None
    import re
    d = re.sub(r"\D", "", declared)
    e = re.sub(r"\D", "", extracted)
    if d == e or d[-4:] == e[-4:]:  # last 4 digits match (masked comparison)
        return None
    return Discrepancy(
        field="phone",
        declared_value=declared,
        extracted_value=extracted,
        source_document=source,
        severity=Severity.LOW,
        match_score=0.0,
        details=f"Phone number mismatch"
    )


def cross_verify(
    declared: DeclaredValues,
    extracted_docs: list[tuple[str, ExtractedFields]],
) -> list[Discrepancy]:
    """Run all verification checks across declared values and extracted document fields.

    Args:
        declared: The applicant's self-declared values.
        extracted_docs: List of (doc_source_name, ExtractedFields) tuples.

    Returns:
        List of discovered discrepancies.
    """
    discrepancies: list[Discrepancy] = []

    for source, fields in extracted_docs:
        # Name check
        if d := verify_name(declared.full_name, fields.full_name, source):
            discrepancies.append(d)

        # DOB check
        if d := verify_dob(declared.date_of_birth, fields.date_of_birth, source):
            discrepancies.append(d)

        # Income check
        if d := verify_income(declared.income_monthly, fields.income_monthly or 0, source):
            discrepancies.append(d)

        # Address check
        if d := verify_address(declared.address, fields.address, source):
            discrepancies.append(d)

        # Gender check
        if d := verify_gender(declared.gender, fields.gender, source):
            discrepancies.append(d)

        # Phone check
        if d := verify_phone(declared.phone, fields.phone, source):
            discrepancies.append(d)

    # Cross-doc checks: compare fields between documents
    if len(extracted_docs) >= 2:
        for i in range(len(extracted_docs)):
            for j in range(i + 1, len(extracted_docs)):
                src_i, fields_i = extracted_docs[i]
                src_j, fields_j = extracted_docs[j]
                # DOB across docs
                if d := verify_dob(fields_i.date_of_birth, fields_j.date_of_birth, f"{src_i} vs {src_j}"):
                    d.details = f"DOB inconsistency between documents: {src_i} and {src_j}"
                    discrepancies.append(d)
                # Name across docs
                if d := verify_name(fields_i.full_name, fields_j.full_name, f"{src_i} vs {src_j}"):
                    d.details = f"Name inconsistency between documents: {src_i} and {src_j}"
                    discrepancies.append(d)

    return discrepancies
