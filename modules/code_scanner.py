import re
from typing import Dict, List

from modules.privacy_patterns import PRIVACY_PATTERNS
from modules.risk_engine import create_finding, calculate_policy_decision


CODE_ANTI_PATTERNS = [
    {
        "name": "PII in logs",
        "regex": re.compile(
            r"(logger|log|console\.log|print)\s*\(.*(email|ssn|dob|phone|account|customer|user).*",
            re.IGNORECASE,
        ),
        "severity": "High",
        "risk_area": "Logging control failure",
        "data_types": ["unknown_or_contextual"],
        "remediation": "Remove sensitive fields from logs or apply masking before log write.",
        "evidence_required": "Unit test showing sanitized logs and sample log output.",
    },
    {
        "name": "Raw LLM submission",
        "regex": re.compile(
            r"(openai|chatcompletion|responses\.create|llm|model)\b.*(customer|email|ssn|account|notes|prompt)",
            re.IGNORECASE,
        ),
        "severity": "High",
        "risk_area": "AI input privacy risk",
        "data_types": ["unknown_or_contextual"],
        "remediation": "Route prompts through the privacy scanner before model submission.",
        "evidence_required": "Architecture evidence showing scanner or redactor in the LLM request path.",
    },
    {
        "name": "Unbounded retention",
        "regex": re.compile(
            r"(store|save|insert|persist).*(customer|prompt|response|transcript|notes)",
            re.IGNORECASE,
        ),
        "severity": "Medium",
        "risk_area": "Retention control gap",
        "data_types": ["unknown_or_contextual"],
        "remediation": "Add retention metadata, deletion logic, or an approved retention rule.",
        "evidence_required": "Retention rule, deletion test, and owner approval.",
    },
]


def scan_code(code_text: str) -> List[Dict]:
    findings: List[Dict] = []

    if not code_text.strip():
        return findings

    lines = code_text.splitlines()

    for line_number, line in enumerate(lines, start=1):
        for pattern in PRIVACY_PATTERNS:
            if pattern.regex.search(line):
                findings.append(
                    create_finding(
                        source_module="Privacy Code Scanner",
                        title=f"{pattern.name} detected in code",
                        description=(
                            f"The code appears to reference or process {pattern.data_type}. "
                            "Review whether this data is required, masked, and protected."
                        ),
                        severity=pattern.severity,
                        risk_area=pattern.risk_area,
                        data_types=[pattern.data_type],
                        remediation=pattern.remediation,
                        evidence_required=pattern.evidence_required,
                        owner="Engineering",
                        policy_decision=calculate_policy_decision(
                            pattern.severity,
                            pattern.block_by_default,
                        ),
                        location=f"Line {line_number}",
                    )
                )

        for anti_pattern in CODE_ANTI_PATTERNS:
            if anti_pattern["regex"].search(line):
                findings.append(
                    create_finding(
                        source_module="Privacy Code Scanner",
                        title=anti_pattern["name"],
                        description=(
                            "A privacy anti-pattern was detected in the submitted code. "
                            "This should be reviewed before release."
                        ),
                        severity=anti_pattern["severity"],
                        risk_area=anti_pattern["risk_area"],
                        data_types=anti_pattern["data_types"],
                        remediation=anti_pattern["remediation"],
                        evidence_required=anti_pattern["evidence_required"],
                        owner="Engineering",
                        policy_decision=calculate_policy_decision(
                            anti_pattern["severity"],
                            False,
                        ),
                        location=f"Line {line_number}",
                    )
                )

    return findings