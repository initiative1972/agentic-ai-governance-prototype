# Framework Alignment — OWASP Agentic, NIST AI RMF, ISO 42001, APRA

This prototype is deliberately mapped to the frameworks an AI governance
function operates against, so it is a working demonstration of *how* agentic
governance obligations become repeatable, evidenced practice.

## OWASP Top 10 for Agentic Applications (2026)

Each threat ships with suggested controls (`owasp_agentic.py`) and is auto-selected
for an action from its capability and context. Verify identifiers against the
current OWASP GenAI Security Project publication before formal use.

| ID | Threat | How the prototype addresses it |
| --- | --- | --- |
| T01 | Agent Goal / Instruction Hijack | Risk score raises likelihood on suspected injection; external-facing actions escalate |
| T02 | Tool Misuse | Per-tool capability grants; tool actions raise risk and require authorisation |
| T03 | Identity & Privilege Abuse | Zero-trust identity; hard capability gate denies ungranted actions |
| T04 | Supply-Chain Vulnerabilities | Documented in threat model; controls flagged for third-party components |
| T05 | Unexpected Code Execution | Exec-type tool calls require explicit capability; denied by default |
| T06 | Memory & Context Poisoning | Memory-using actions flagged; provenance controls surfaced |
| T07 | Insecure Inter-Agent Communication | Spawn / A2A actions attract authentication & allow-list controls |
| T08 | Cascading Failures | Circuit breaker halts the system when 2+ agents are quarantined |
| T09 | Human-Agent Trust Exploitation | High-risk actions require human approval + step-up; approvals are rate-limited |
| T10 | Rogue / Unbounded Agents | Registry/attestation + kill-switch quarantine rogue or unbounded agents |

## NIST AI RMF (Govern / Map / Measure / Manage)
- **GOVERN** — agent registry/inventory, ownership, clearance, attested ledger, sign-off.
- **MAP** — capability-driven selection of applicable OWASP agentic threats.
- **MEASURE** — real-time risk scoring and per-action decisions against thresholds.
- **MANAGE** — kill-switch containment, coverage in the report, monitoring plan.

## ISO/IEC 42001 (AI management system)
Supports operational controls, risk assessment/treatment and performance
evaluation clauses: a documented risk method, a decision log (the ledger), an
assurance report, and periodic re-assessment.

## APRA alignment (financial services)
| Standard | How it maps |
| --- | --- |
| **CPS 234 (information security)** | Zero-trust identity, least privilege, attestation evidence control effectiveness |
| **CPS 230 (operational risk / resilience)** | Circuit breaker + cascade halt support operational tolerance; supply-chain threat (T04) maps to material service providers |
| **CPG 235 (data risk)** | Data-classification clearance gate ties agent actions back to data quality/provenance |
