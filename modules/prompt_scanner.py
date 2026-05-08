from typing import Dict, List, Tuple

from modules.privacy_patterns import PRIVACY_PATTERNS
from modules.risk_engine import create_finding, calculate_policy_decision


def redact_prompt(prompt_text: str) -> Tuple[str, List[Dict]]:
    findings: List[Dict] = []
    redacted_text = prompt_text

    if not prompt_text.strip():
        return redacted_text, findings

    for pattern in PRIVACY_PATTERNS:
        matches = list(pattern.regex.finditer(prompt_text))

        if not matches:
            continue

        redacted_text = pattern.regex.sub(
            f"[REDACTED_{pattern.data_type.upper()}]",
            redacted_text,
        )

        findings.append(
            create_finding(
                source_module="LLM Prompt Privacy Scanner",
                title=f"{pattern.name} detected in LLM prompt",
                description=(
                    f"The prompt contains {pattern.data_type}. "
                    "Review whether this data should be blocked, redacted, or allowed under policy."
                ),
                severity=pattern.severity,
                risk_area=pattern.risk_area,
                data_types=[pattern.data_type],
                remediation=pattern.remediation,
                evidence_required=pattern.evidence_required,
                owner="AI Product / Privacy",
                policy_decision=calculate_policy_decision(
                    pattern.severity,
                    pattern.block_by_default,
                ),
                location="Prompt body",
            )
        )

    return redacted_text, findings


def overall_prompt_decision(findings: List[Dict]) -> str:
    decisions = [finding.get("policy_decision") for finding in findings]

    if "Block" in decisions:
        return "Block"

    if "Redact" in decisions:
        return "Redact"

    if "Warn" in decisions:
        return "Warn"

    return "Allow"