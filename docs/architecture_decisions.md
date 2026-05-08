# Architecture and Product Decisions

## Purpose

This document explains the key architecture, product, and tradeoff decisions behind the AI Privacy Control Plane MVP.

The goal of the MVP is not to build a production-grade enterprise platform. The goal is to demonstrate a repeatable operating model for AI privacy review, risk detection, remediation ownership, control mapping, and evidence readiness.

## Decision 1: Build a Narrow Vertical Slice First

### Decision

The MVP focuses on a narrow but complete workflow:

```text
AI use case intake → data classification → code/prompt scanning → findings → control mapping → remediation queue → executive metrics → export
```

### Rationale

A narrow vertical slice is more valuable than many incomplete modules. It demonstrates the end-to-end operating model from detection through decisioning and evidence.

### Tradeoff

The MVP does not include full enterprise integrations yet, such as GitHub PR automation, Jira tickets, SOC report parsing, or centralized authentication.

### Future Direction

Add integrations after the core finding model and workflow logic are stable.

## Decision 2: Use a Standard Finding Model

### Decision

All scanner outputs and demo findings are normalized into a consistent finding model with:

- Finding ID
- Source module
- Severity
- Risk area
- Data types
- Policy decision
- Owner
- Status
- Remediation guidance
- Evidence required
- Control mapping

### Rationale

A standard finding model makes the platform extensible. New modules can be added without redesigning the dashboard, remediation queue, metrics, or export workflow.

### Tradeoff

The current model is simplified and does not yet include aging, SLA tracking, related systems, business unit, or jurisdiction-specific risk metadata.

### Future Direction

Add fields for system owner, business unit, risk acceptance, SLA due date, jurisdiction, vendor, and evidence links.

## Decision 3: Use Streamlit for the MVP

### Decision

The MVP uses Streamlit to build and deploy a working product quickly.

### Rationale

Streamlit is well suited for rapid prototyping, dashboards, and interactive data workflows. It allowed the project to move from concept to deployed demo quickly.

### Tradeoff

Streamlit is not the final architecture for a production enterprise platform. A production version would likely use a dedicated frontend, backend API, database, authentication layer, and integration services.

### Future Direction

Move toward a modular architecture with:

- React or Next.js frontend
- FastAPI backend
- PostgreSQL database
- Authentication and role-based access control
- GitHub, Jira, and GRC integrations
- Evidence repository

## Decision 4: Start with Rule-Based Detection

### Decision

The MVP uses rule-based detection for sensitive data patterns and privacy anti-patterns.

### Rationale

Rule-based detection is explainable, fast, and easy to tune. For privacy/compliance workflows, explainability is important because reviewers need to understand why a finding was generated.

### Tradeoff

Rule-based detection can produce false positives and false negatives. It does not fully understand context, intent, or business purpose.

### Future Direction

Add layered detection:

1. Regex and deterministic rules
2. Configurable policy rules
3. Context-aware classification
4. Optional LLM-assisted explanation and remediation suggestions
5. Human review and approval workflow

## Decision 5: Avoid Storing Raw Sensitive Data

### Decision

The MVP focuses on classification and findings rather than retaining raw sensitive values.

### Rationale

Privacy tooling should avoid creating a new privacy risk repository. Findings should capture enough context to remediate the issue without unnecessarily storing sensitive data.

### Tradeoff

Some debugging and validation use cases may need representative examples, but those should be masked, tokenized, or stored with strict access controls.

### Future Direction

A production platform should store only metadata by default and require elevated access or explicit approval for sensitive evidence artifacts.

## Decision 6: Treat Evidence as a First-Class Workflow

### Decision

Every finding includes evidence required for closure.

### Rationale

Privacy review is not complete when a finding is identified. It is complete when the risk is remediated, accepted, or escalated with defensible evidence.

### Tradeoff

The MVP does not yet support direct evidence uploads, links, approvals, or validation workflows.

### Future Direction

Add an evidence repository that supports:

- Evidence upload
- Evidence owner
- Approval status
- Validation notes
- Audit trail
- Expiration and revalidation dates

## Decision 7: Separate Detection from Governance

### Decision

The app separates scanner modules from governance views.

Scanner modules detect risk. Governance views translate risk into control mapping, workflow status, remediation ownership, and executive reporting.

### Rationale

This separation makes the platform extensible and prevents it from becoming just another scanner. The strategic value is in connecting detection to action and evidence.

### Tradeoff

The MVP currently simulates parts of the governance workflow rather than integrating with enterprise systems of record.

### Future Direction

Integrate with Jira, GitHub, GRC platforms, data catalogs, vendor risk tools, and evidence repositories.

## Decision 8: Build for Privacy TPM and AI Governance Use Cases

### Decision

The MVP is positioned around AI privacy assessment, privacy review workflow, control mapping, remediation, and executive privacy metrics.

### Rationale

This aligns the project with AI privacy, compliance, governance, and risk management workflows. It avoids over-positioning the tool as a release management platform.

### Tradeoff

The current version does not attempt to solve broader release train management or deployment orchestration.

### Future Direction

Support pre-launch privacy readiness as part of product governance, while keeping privacy and AI governance as the primary use case.

## Summary

The central design decision is to build a modular AI privacy control plane that connects:

```text
Detection → Risk model → Control mapping → Remediation → Evidence → Executive visibility
```

The MVP is intentionally narrow, but the architecture supports expansion into enterprise-scale AI privacy governance.