import streamlit as st
import pandas as pd

from modules.code_scanner import scan_code
from modules.prompt_scanner import redact_prompt, overall_prompt_decision
from modules.demo_data import get_demo_findings

st.set_page_config(
    page_title="AI Privacy Control Plane MVP",
    page_icon="🔐",
    layout="wide",
)


st.title("🔐 AI Privacy Control Plane MVP")

st.write(
    "This MVP detects privacy risk in code and LLM prompts, "
    "normalizes findings into a unified risk model, and supports remediation tracking."
)


if "findings" not in st.session_state:
    st.session_state.findings = []
st.sidebar.title("Demo Controls")

if st.sidebar.button("Load Demo Scenario"):
    st.session_state.findings = get_demo_findings()
    st.sidebar.success("Demo scenario loaded.")

if st.sidebar.button("Clear Findings"):
    st.session_state.findings = []
    st.sidebar.warning("Findings cleared.")

def findings_dataframe(findings):
    if not findings:
        return pd.DataFrame()

    df = pd.DataFrame(findings)

    visible_columns = [
        "finding_id",
        "source_module",
        "title",
        "severity",
        "risk_area",
        "data_types",
        "policy_decision",
        "owner",
        "status",
        "location",
        "recommended_remediation",
        "evidence_required",
    ]

    return df[[column for column in visible_columns if column in df.columns]]


st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select view",
    [
        "Dashboard",
        "Privacy Code Scanner",
        "LLM Prompt Scanner",
        "Remediation Queue",
        "Architecture / Roadmap",
        "Export Findings",
    ],
)


if page == "Dashboard":
    st.subheader("Executive Risk Dashboard")

    findings = st.session_state.findings

    total_findings = len(findings)
    critical_findings = sum(1 for f in findings if f["severity"] == "Critical")
    high_findings = sum(1 for f in findings if f["severity"] == "High")
    open_findings = sum(1 for f in findings if f["status"] == "Open")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Findings", total_findings)
    col2.metric("Critical", critical_findings)
    col3.metric("High", high_findings)
    col4.metric("Open", open_findings)

    if findings:
        df = findings_dataframe(findings)

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("### Findings by Severity")
            severity_counts = df["severity"].value_counts().reset_index()
            severity_counts.columns = ["severity", "count"]
            st.bar_chart(severity_counts, x="severity", y="count")

        with chart_col2:
            st.markdown("### Findings by Source Module")
            source_counts = df["source_module"].value_counts().reset_index()
            source_counts.columns = ["source_module", "count"]
            st.bar_chart(source_counts, x="source_module", y="count")

        st.markdown("### Unified Privacy Findings")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No findings yet. Run the Privacy Code Scanner to generate findings.")


if page == "Privacy Code Scanner":
    st.subheader("Privacy Code Scanner")

    st.write(
        "Paste code or a pull request diff below. "
        "The scanner will detect privacy anti-patterns and create standardized findings."
    )

    sample_code = """

    
import logging

logger = logging.getLogger(__name__)

def create_support_case(user):
    logger.info(f"Creating support case for {user.email} with SSN {user.ssn}")
    payload = {
        "email": user.email,
        "dob": user.dob,
        "account_number": user.account_number
    }
    save_customer_transcript(payload)
    return payload
"""

    code_text = st.text_area(
        "Code or PR diff",
        value=sample_code,
        height=320,
    )

    if st.button("Scan Code", type="primary"):
        new_findings = scan_code(code_text)
        st.session_state.findings.extend(new_findings)

        st.success(f"Scan complete. {len(new_findings)} finding(s) generated.")

        if new_findings:
            st.dataframe(
                findings_dataframe(new_findings),
                use_container_width=True,
                hide_index=True,
            )
if page == "LLM Prompt Scanner":
    st.subheader("LLM Prompt Privacy Scanner")

    st.write(
        "Paste an LLM prompt or retrieval context below. "
        "The scanner will detect sensitive data, redact it, and generate privacy findings."
    )

    sample_prompt = (
        "Summarize this customer complaint. Customer email is jane.doe@example.com, "
        "phone is (480) 555-1212, SSN is 123-45-6789, "
        "and account_number is 99887766. "
        "The customer says they are disputing a transaction."
    )

    prompt_text = st.text_area(
        "LLM prompt or context",
        value=sample_prompt,
        height=260,
    )

    if st.button("Scan Prompt", type="primary"):
        redacted_prompt, new_findings = redact_prompt(prompt_text)
        decision = overall_prompt_decision(new_findings)

        st.session_state.findings.extend(new_findings)

        if decision == "Block":
            st.error("Policy Decision: BLOCK")
        elif decision == "Redact":
            st.warning("Policy Decision: REDACT")
        elif decision == "Warn":
            st.warning("Policy Decision: WARN")
        else:
            st.success("Policy Decision: ALLOW")

        st.markdown("### Redacted Prompt")
        st.code(redacted_prompt, language="text")

        st.markdown("### Generated Privacy Findings")

        if new_findings:
            st.dataframe(
                findings_dataframe(new_findings),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No sensitive data detected.")
if page == "Remediation Queue":
    st.subheader("Remediation Queue")

    st.write(
        "This view converts privacy findings into accountable remediation work. "
        "It shows the owner, policy decision, recommended remediation, and evidence needed for closure."
    )

    findings = st.session_state.findings

    if not findings:
        st.info("No findings yet. Run the Privacy Code Scanner or LLM Prompt Scanner first.")
    else:
        df = findings_dataframe(findings)

        queue_columns = [
            "finding_id",
            "severity",
            "policy_decision",
            "owner",
            "status",
            "title",
            "recommended_remediation",
            "evidence_required",
        ]

        remediation_df = df[[column for column in queue_columns if column in df.columns]]

        st.markdown("### Open Remediation Items")
        st.dataframe(
            remediation_df,
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("### Operating Model Summary")

        col1, col2, col3 = st.columns(3)

        engineering_items = sum(
            1 for finding in findings if finding.get("owner") == "Engineering"
        )

        ai_privacy_items = sum(
            1 for finding in findings if finding.get("owner") == "AI Product / Privacy"
        )

        blocked_items = sum(
            1 for finding in findings if finding.get("policy_decision") == "Block"
        )

        col1.metric("Engineering-Owned Items", engineering_items)
        col2.metric("AI / Privacy-Owned Items", ai_privacy_items)
        col3.metric("Blocked Policy Decisions", blocked_items)

        st.markdown("### Product and Operating Readout")

        st.info(
            "This queue supports cross-functional execution by translating privacy findings "
            "into owner-aligned remediation work, evidence requirements, and policy decisions."
        )

if page == "Architecture / Roadmap":
    st.subheader("Architecture / Roadmap")

    st.write(
        "This view explains the control plane architecture, current MVP scope, "
        "and the phased roadmap for scaling the tool into an enterprise privacy engineering platform."
    )

    st.markdown("### Current MVP Architecture")

    st.code(
        """
Privacy Code Scanner ┐
                     ├── Standard Finding Model ── Executive Dashboard ── Remediation Queue
LLM Prompt Scanner   ┘
        """,
        language="text",
    )

    st.markdown("### Target Platform Architecture")

    st.code(
        """
GitHub / PR Diffs       ┐
LLM Gateway             ├── Privacy Signal Modules ── Policy Engine ── Unified Risk Model
SOC Reports             │                                      │
Vendor Reviews          │                                      ├── Executive Dashboard
Data Flow Mapper        ┘                                      ├── Remediation Queue
                                                                └── Evidence Repository
        """,
        language="text",
    )

    st.markdown("### Phase Roadmap")

    roadmap_data = [
        {
            "Phase": "Phase 1",
            "Capability": "GitHub PR Integration",
            "Business Outcome": "Scan privacy risk before code is merged.",
        },
        {
            "Phase": "Phase 2",
            "Capability": "SOC Report Extractor",
            "Business Outcome": "Extract CUECs, exceptions, and physical/environmental controls.",
        },
        {
            "Phase": "Phase 3",
            "Capability": "Jira Integration",
            "Business Outcome": "Convert privacy findings into accountable remediation tickets.",
        },
        {
            "Phase": "Phase 4",
            "Capability": "Data Flow Mapper",
            "Business Outcome": "Map systems, data types, AI usage, vendors, and retention rules.",
        },
        {
            "Phase": "Phase 5",
            "Capability": "Evidence Repository",
            "Business Outcome": "Support privacy reviews, audits, and customer assurance requests.",
        },
        {
            "Phase": "Phase 6",
            "Capability": "Executive Reporting",
            "Business Outcome": "Track risk reduction, aging, SLAs, repeat findings, and control maturity.",
        },
    ]

    roadmap_df = pd.DataFrame(roadmap_data)

    st.dataframe(
        roadmap_df,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Product and Operating Model")

    st.info(
        "The MVP is intentionally narrow, but the architecture is modular. "
        "The core strategy is to normalize privacy signals from code, prompts, vendors, SOC reports, "
        "and data flows into one operating model for risk prioritization, ownership, remediation, and evidence."
    )

if page == "Export Findings":
    st.subheader("Export Findings")

    st.write(
        "This page supports auditability by allowing privacy findings to be exported "
        "for remediation tracking, evidence review, or stakeholder reporting."
    )

    findings = st.session_state.findings

    if not findings:
        st.info("No findings available to export. Load the demo scenario or run a scanner first.")
    else:
        df = findings_dataframe(findings)

        st.markdown("### Export Preview")
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

        csv_data = df.to_csv(index=False)

        st.download_button(
            label="Download Findings as CSV",
            data=csv_data,
            file_name="privacy_findings_export.csv",
            mime="text/csv",
        )    