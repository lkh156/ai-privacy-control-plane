# AI Privacy Control Plane MVP Demo Script

## 30-Second Overview

This is an AI Privacy Control Plane MVP. It demonstrates how privacy risk can be detected in code and LLM prompts, normalized into a unified risk model, routed into a remediation queue, and exported for evidence or stakeholder review.

The goal is to show how privacy obligations can be translated into operational workflows across product, engineering, privacy, security, legal, and audit.

## Demo Step 1: Load Demo Scenario

Click **Load Demo Scenario** in the sidebar.

Talking point:

> I included a demo scenario so the risk dashboard can immediately show a realistic privacy operating model. The findings represent common AI and product privacy issues, including PII in logs, regulated identifiers in prompts, retention gaps, and overcollection.

## Demo Step 2: Executive Dashboard

Open **Dashboard**.

Show:

- Total findings
- Critical findings
- High findings
- Open findings
- Findings by severity
- Findings by source module
- Unified privacy findings table

Talking point:

> The dashboard provides an executive risk view. It is not just reporting raw scanner output. Each finding is normalized with severity, owner, status, policy decision, remediation guidance, and evidence required for closure.

## Demo Step 3: Privacy Code Scanner

Open **Privacy Code Scanner** and click **Scan Code**.

Talking point:

> This module simulates scanning application code or a pull request diff. It detects privacy anti-patterns such as PII in logs, references to date of birth, account numbers, and retention concerns.

Explain the value:

> The goal is to move privacy review earlier in the SDLC, before risky code is merged or deployed.

## Demo Step 4: LLM Prompt Scanner

Open **LLM Prompt Scanner** and click **Scan Prompt**.

Show:

- Policy decision
- Redacted prompt
- Generated findings

Talking point:

> This module simulates a privacy gateway for LLM workflows. It detects sensitive data in prompts or retrieval context, redacts the prompt, and produces policy decisions such as Allow, Warn, Redact, or Block.

Explain the value:

> This is especially relevant for AI products where sensitive data can move into model prompts, RAG context, logs, or outputs.

## Demo Step 5: Remediation Queue

Open **Remediation Queue**.

Show:

- Finding ID
- Severity
- Policy decision
- Owner
- Status
- Recommended remediation
- Evidence required

Talking point:

> This is where the tool becomes an operating model rather than just a scanner. Findings are translated into accountable remediation work, with ownership and evidence expectations.

## Demo Step 6: Architecture / Roadmap

Open **Architecture / Roadmap**.

Talking point:

> The MVP is intentionally narrow, but the architecture is modular. Additional modules could include GitHub PR scanning, SOC report extraction, vendor risk scoring, data-flow mapping, Jira integration, and an evidence repository.

## Demo Step 7: Export Findings

Open **Export Findings** and show the CSV export button.

Talking point:

> Exportability supports auditability, remediation tracking, and stakeholder reporting. In a production version, this would connect to Jira, GRC tooling, or an evidence repository.

## Closing Narrative

This MVP shows a practical privacy engineering workflow:

1. Detect risk
2. Normalize findings
3. Assign ownership
4. Prioritize remediation
5. Track evidence
6. Report progress
7. Scale into enterprise integrations

The broader platform vision is a modular AI privacy control plane that turns privacy requirements into measurable product and engineering workflows.