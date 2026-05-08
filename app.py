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
        "AI Privacy Assessment",
        "Privacy Review Workflow",
        "Executive Privacy Metrics",
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

if page == "AI Privacy Assessment":
    st.subheader("AI Privacy Assessment")

    st.write(
        "This assessment simulates the intake and privacy review process for an AI-enabled feature. "
        "It translates product context, data types, model usage, and findings into a privacy risk recommendation."
    )

    st.markdown("### AI Use Case Intake")

    col1, col2 = st.columns(2)

    with col1:
        use_case_name = st.text_input(
            "AI Use Case Name",
            value="Customer Support AI Summarization",
        )

        business_owner = st.text_input(
            "Business Owner",
            value="Customer Experience Product Team",
        )

        ai_workflow = st.selectbox(
            "AI Workflow Type",
            [
                "Customer support summarization",
                "Internal knowledge assistant",
                "Code generation assistant",
                "Document review assistant",
                "Customer-facing chatbot",
                "Other",
            ],
        )

    with col2:
        model_context = st.selectbox(
            "Model Context",
            [
                "Internal enterprise LLM",
                "External third-party LLM",
                "Fine-tuned model",
                "RAG-enabled workflow",
                "Hybrid model architecture",
            ],
        )

        user_population = st.selectbox(
            "User Population",
            [
                "Internal employees",
                "Customer support agents",
                "External customers",
                "Developers",
                "Legal / Compliance users",
            ],
        )

        jurisdiction_scope = st.multiselect(
            "Jurisdiction / Regulatory Scope",
            [
                "United States",
                "California",
                "Texas",
                "Financial services",
                "Children / minors",
                "Healthcare / PHI-like data",
                "International users",
            ],
            default=["United States", "Financial services"],
        )

    st.markdown("### Data Types Involved")

    data_types = st.multiselect(
        "Select data types processed by this AI use case",
        [
            "Email address",
            "Phone number",
            "Customer ID",
            "Account number",
            "Date of birth",
            "Social Security Number",
            "Payment card data",
            "Customer support notes",
            "Authentication secrets",
            "Employee data",
            "Confidential business data",
        ],
        default=["Email address", "Account number", "Customer support notes"],
    )

    st.markdown("### Privacy Controls")

    controls = st.multiselect(
        "Select controls currently implemented",
        [
            "Prompt redaction",
            "Output filtering",
            "Data minimization review",
            "Retention rule defined",
            "Access control review",
            "Logging review",
            "Vendor review completed",
            "Human-in-the-loop review",
            "Evidence package created",
            "Risk acceptance documented",
        ],
        default=["Prompt redaction", "Access control review"],
    )

    st.markdown("### Assessment Result")

    high_risk_data = {
        "Social Security Number",
        "Payment card data",
        "Account number",
        "Date of birth",
        "Authentication secrets",
        "Customer support notes",
    }

    required_controls = {
        "Prompt redaction",
        "Data minimization review",
        "Retention rule defined",
        "Logging review",
        "Evidence package created",
    }

    high_risk_count = len(high_risk_data.intersection(set(data_types)))
    missing_controls = sorted(list(required_controls.difference(set(controls))))

    if high_risk_count >= 3 and missing_controls:
        assessment_rating = "High"
        recommendation = "Conditional Approval"
        rationale = (
            "The use case processes multiple sensitive data types and has unresolved control gaps. "
            "Privacy remediation and evidence completion should occur before production launch."
        )
    elif high_risk_count >= 2:
        assessment_rating = "Medium"
        recommendation = "Conditional Approval"
        rationale = (
            "The use case includes sensitive data and should proceed only with documented controls, "
            "clear ownership, and completed evidence requirements."
        )
    elif high_risk_count == 1:
        assessment_rating = "Medium"
        recommendation = "Proceed with Privacy Review"
        rationale = (
            "The use case includes at least one sensitive data type. "
            "Targeted review is required before approval."
        )
    else:
        assessment_rating = "Low"
        recommendation = "Proceed"
        rationale = (
            "No high-risk data types were selected. Continue standard privacy-by-design review."
        )

    metric_col1, metric_col2, metric_col3 = st.columns(3)

    metric_col1.metric("Privacy Risk Rating", assessment_rating)
    metric_col2.metric("Approval Recommendation", recommendation)
    metric_col3.metric("Missing Required Controls", len(missing_controls))

    st.markdown("### Assessment Rationale")
    st.info(rationale)

    st.markdown("### Required Follow-Up Actions")

    if missing_controls:
        for control in missing_controls:
            st.warning(f"Missing control: {control}")
    else:
        st.success("All required baseline controls are present.")

    st.markdown("### Stakeholder Ownership")

    ownership_data = [
        {
            "Stakeholder": "Product",
            "Responsibility": "Define use case, business purpose, user impact, and product requirements.",
        },
        {
            "Stakeholder": "Engineering",
            "Responsibility": "Implement redaction, logging controls, access controls, and retention logic.",
        },
        {
            "Stakeholder": "Privacy / Legal",
            "Responsibility": "Review data minimization, notice, consent, retention, and risk acceptance.",
        },
        {
            "Stakeholder": "Security",
            "Responsibility": "Validate secure handling, secrets management, and model interaction controls.",
        },
        {
            "Stakeholder": "Audit / Compliance",
            "Responsibility": "Validate evidence, control mapping, remediation closure, and governance reporting.",
        },
    ]

    ownership_df = pd.DataFrame(ownership_data)

    st.dataframe(
        ownership_df,
        use_container_width=True,
        hide_index=True,
    )        
if page == "Privacy Review Workflow":
    st.subheader("Privacy Review Workflow")

    st.write(
        "This workflow shows how an AI-enabled feature moves through privacy review, "
        "from intake through remediation, evidence collection, and approval."
    )

    workflow_data = [
        {
            "Stage": "1. Intake",
            "Objective": "Capture AI use case, business purpose, owner, user population, and model context.",
            "Primary Owner": "Product",
            "Exit Criteria": "Use case submitted with business purpose and accountable owner.",
        },
        {
            "Stage": "2. Data Classification",
            "Objective": "Identify PII, sensitive identifiers, customer notes, financial data, and confidential data.",
            "Primary Owner": "Privacy / Data Governance",
            "Exit Criteria": "Data types classified and mapped to processing purpose.",
        },
        {
            "Stage": "3. Technical Scanning",
            "Objective": "Scan code, prompts, and retrieval context for privacy risk.",
            "Primary Owner": "Engineering",
            "Exit Criteria": "Code and prompt findings generated and risk-rated.",
        },
        {
            "Stage": "4. Risk Triage",
            "Objective": "Prioritize findings by severity, policy decision, data sensitivity, and exposure pathway.",
            "Primary Owner": "Privacy TPM",
            "Exit Criteria": "Findings assigned to owners with remediation expectations.",
        },
        {
            "Stage": "5. Remediation",
            "Objective": "Implement redaction, minimization, logging controls, retention rules, and access restrictions.",
            "Primary Owner": "Engineering / Product",
            "Exit Criteria": "High-risk findings remediated or formally risk accepted.",
        },
        {
            "Stage": "6. Evidence Collection",
            "Objective": "Collect tests, screenshots, approvals, policy decisions, and data-flow documentation.",
            "Primary Owner": "Audit / Compliance",
            "Exit Criteria": "Evidence package is complete and linked to findings.",
        },
        {
            "Stage": "7. Privacy Decision",
            "Objective": "Approve, conditionally approve, block, or escalate the AI use case.",
            "Primary Owner": "Privacy / Legal",
            "Exit Criteria": "Final decision documented with residual risk rationale.",
        },
    ]

    workflow_df = pd.DataFrame(workflow_data)

    st.markdown("### End-to-End Workflow")
    st.dataframe(
        workflow_df,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Privacy Decision Model")

    decision_data = [
        {
            "Decision": "Approved",
            "Criteria": "No Critical or High findings remain open, required controls are implemented, and evidence is complete.",
        },
        {
            "Decision": "Conditional Approval",
            "Criteria": "Medium or limited High findings remain, owners are assigned, mitigation dates are documented, and risk is accepted.",
        },
        {
            "Decision": "Blocked",
            "Criteria": "Critical findings, blocked data types, missing required controls, or unresolved regulated identifier exposure remain.",
        },
        {
            "Decision": "Escalate",
            "Criteria": "Residual risk requires executive, legal, security, or compliance leadership review.",
        },
    ]

    decision_df = pd.DataFrame(decision_data)

    st.dataframe(
        decision_df,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Workflow KPIs")

    findings = st.session_state.findings

    total_findings = len(findings)
    critical_findings = sum(1 for finding in findings if finding.get("severity") == "Critical")
    high_findings = sum(1 for finding in findings if finding.get("severity") == "High")
    blocked_decisions = sum(1 for finding in findings if finding.get("policy_decision") == "Block")

    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

    kpi_col1.metric("Total Findings", total_findings)
    kpi_col2.metric("Critical Findings", critical_findings)
    kpi_col3.metric("High Findings", high_findings)
    kpi_col4.metric("Blocked Decisions", blocked_decisions)

    st.markdown("### Operating Model Narrative")

    st.info(
        "This workflow positions privacy review as a repeatable product and engineering operating model. "
        "The goal is to standardize intake, data classification, technical scanning, remediation ownership, "
        "evidence collection, and final privacy decisioning across AI use cases."
    )
if page == "Executive Privacy Metrics":
    st.subheader("Executive Privacy Metrics")

    st.write(
        "This view translates privacy review activity into program-level metrics for leadership, "
        "privacy governance, compliance reporting, and cross-functional execution."
    )

    findings = st.session_state.findings

    total_findings = len(findings)
    critical_findings = sum(1 for finding in findings if finding.get("severity") == "Critical")
    high_findings = sum(1 for finding in findings if finding.get("severity") == "High")
    medium_findings = sum(1 for finding in findings if finding.get("severity") == "Medium")
    blocked_decisions = sum(1 for finding in findings if finding.get("policy_decision") == "Block")
    redaction_decisions = sum(1 for finding in findings if finding.get("policy_decision") == "Redact")
    open_findings = sum(1 for finding in findings if finding.get("status") == "Open")

    if total_findings == 0:
        evidence_completion_rate = 0
        critical_high_rate = 0
    else:
        remediated_findings = sum(
            1 for finding in findings if finding.get("status") == "Remediated"
        )
        evidence_completion_rate = round((remediated_findings / total_findings) * 100, 1)
        critical_high_rate = round(
            ((critical_findings + high_findings) / total_findings) * 100,
            1,
        )

    st.markdown("### Program Health Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Findings", total_findings)
    col2.metric("Critical + High Risk Rate", f"{critical_high_rate}%")
    col3.metric("Blocked Decisions", blocked_decisions)
    col4.metric("Evidence Completion", f"{evidence_completion_rate}%")

    st.markdown("### Risk Distribution")

    risk_data = [
        {"Risk Level": "Critical", "Count": critical_findings},
        {"Risk Level": "High", "Count": high_findings},
        {"Risk Level": "Medium", "Count": medium_findings},
    ]

    risk_df = pd.DataFrame(risk_data)

    st.bar_chart(
        risk_df,
        x="Risk Level",
        y="Count",
    )

    st.markdown("### Policy Decision Distribution")

    decision_data = [
        {"Policy Decision": "Block", "Count": blocked_decisions},
        {"Policy Decision": "Redact", "Count": redaction_decisions},
        {"Policy Decision": "Open Findings", "Count": open_findings},
    ]

    decision_df = pd.DataFrame(decision_data)

    st.bar_chart(
        decision_df,
        x="Policy Decision",
        y="Count",
    )

    st.markdown("### Executive Readout")

    if total_findings == 0:
        st.info(
            "No findings are currently loaded. Load the demo scenario or run the scanners "
            "to populate executive privacy metrics."
        )
    elif critical_findings > 0 or blocked_decisions > 0:
        st.error(
            "Executive status: Attention required. The current privacy review population includes "
            "Critical findings or Block policy decisions. These items should be remediated, risk accepted, "
            "or escalated before approval."
        )
    elif high_findings > 0:
        st.warning(
            "Executive status: Conditional approval posture. High findings remain open and should be "
            "assigned to accountable owners with remediation timelines and evidence expectations."
        )
    else:
        st.success(
            "Executive status: Privacy review appears on track. Continue monitoring evidence completion, "
            "repeat findings, and residual risk."
        )

    st.markdown("### Leadership Questions This View Answers")

    leadership_questions = [
        {
            "Question": "Where is the highest privacy risk concentrated?",
            "Metric / Signal": "Critical and High findings by source module and risk area.",
        },
        {
            "Question": "Which AI use cases are blocked or conditionally approved?",
            "Metric / Signal": "Policy decision distribution and blocked decision count.",
        },
        {
            "Question": "Are teams closing privacy issues with defensible evidence?",
            "Metric / Signal": "Evidence completion rate and remediation status.",
        },
        {
            "Question": "Which stakeholders own the current remediation burden?",
            "Metric / Signal": "Owner-aligned findings in the remediation queue.",
        },
        {
            "Question": "Is privacy review operating as a repeatable governance workflow?",
            "Metric / Signal": "Workflow KPIs, standardized findings, and repeatable decision model.",
        },
    ]

    leadership_df = pd.DataFrame(leadership_questions)

    st.dataframe(
        leadership_df,
        use_container_width=True,
        hide_index=True,
    )