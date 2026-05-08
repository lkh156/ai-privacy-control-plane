from datetime import datetime, timezone
from typing import Dict, List
import uuid


SEVERITY_SCORE = {
    "Low": 1,
    "Medium": 2,
    "High": 3,
    "Critical": 4,
}


CONTROL_MAPPINGS = {
    "PII exposure": ["Data minimization", "Access control", "Logging and monitoring"],
    "Regulated identifier exposure": ["Sensitive data handling", "Data loss prevention", "AI input governance"],
    "Logging control failure": ["Logging control", "Data minimization", "Secure SDLC"],
    "AI input privacy risk": ["AI governance", "Privacy-by-design", "DLP"],
    "Retention control gap": ["Retention management", "Data lifecycle governance", "Deletion controls"],
    "Sensitive data collection": ["Data minimization", "Purpose limitation", "Privacy review"],
}


def create_finding(
    source_module: str,
    title: str,
    description: str,
    severity: str,
    risk_area: str,
    data_types: List[str],
    remediation: str,
    evidence_required: str,
    owner: str = "Unassigned",
    status: str = "Open",
    policy_decision: str = "Review",
    location: str = "N/A",
) -> Dict:
    return {
        "finding_id": f"PRIV-{str(uuid.uuid4())[:8].upper()}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_module": source_module,
        "title": title,
        "description": description,
        "severity": severity,
        "severity_score": SEVERITY_SCORE.get(severity, 2),
        "risk_area": risk_area,
        "data_types": sorted(list(set(data_types))),
        "control_mapping": CONTROL_MAPPINGS.get(risk_area, ["Privacy review"]),
        "recommended_remediation": remediation,
        "evidence_required": evidence_required,
        "owner": owner,
        "status": status,
        "policy_decision": policy_decision,
        "location": location,
    }


def calculate_policy_decision(severity: str, block_by_default: bool = False) -> str:
    if block_by_default or severity == "Critical":
        return "Block"
    if severity == "High":
        return "Redact"
    if severity == "Medium":
        return "Warn"
    return "Allow"