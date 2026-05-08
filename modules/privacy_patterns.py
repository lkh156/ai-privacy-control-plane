import re
from dataclasses import dataclass
from typing import Pattern


@dataclass(frozen=True)
class PrivacyPattern:
    name: str
    data_type: str
    regex: Pattern
    severity: str
    risk_area: str
    block_by_default: bool
    remediation: str
    evidence_required: str


PRIVACY_PATTERNS = [
    PrivacyPattern(
        name="Email Address",
        data_type="email",
        regex=re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        severity="Medium",
        risk_area="PII exposure",
        block_by_default=False,
        remediation="Mask or tokenize email addresses before logging, analytics, or LLM processing.",
        evidence_required="Sanitized output sample and unit test showing email masking.",
    ),
    PrivacyPattern(
        name="US Phone Number",
        data_type="phone_number",
        regex=re.compile(r"(\+?1[-.\s]?)?(\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}"),
        severity="Medium",
        risk_area="PII exposure",
        block_by_default=False,
        remediation="Mask phone numbers unless the business purpose requires full visibility.",
        evidence_required="Sanitized output sample and test evidence.",
    ),
    PrivacyPattern(
        name="Social Security Number",
        data_type="ssn",
        regex=re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        severity="Critical",
        risk_area="Regulated identifier exposure",
        block_by_default=True,
        remediation="Block SSNs from external model calls and tokenize or remove from logs.",
        evidence_required="Policy decision log, redaction test, and blocked transmission evidence.",
    ),
    PrivacyPattern(
        name="Date of Birth Field",
        data_type="date_of_birth",
        regex=re.compile(r"\b(dob|date_of_birth|birth_date|birthdate)\b", re.IGNORECASE),
        severity="High",
        risk_area="Sensitive data collection",
        block_by_default=False,
        remediation="Confirm full date of birth is required. Use age band or age verification flag when possible.",
        evidence_required="Data minimization rationale and product requirement approval.",
    ),
    PrivacyPattern(
        name="Account Number Field",
        data_type="account_number",
        regex=re.compile(r"\b(account_number|acct_num|acct_no|routing_number)\b", re.IGNORECASE),
        severity="High",
        risk_area="Regulated identifier exposure",
        block_by_default=True,
        remediation="Mask financial identifiers and restrict processing to approved systems.",
        evidence_required="Masking test and approved data-flow documentation.",
    ),
]