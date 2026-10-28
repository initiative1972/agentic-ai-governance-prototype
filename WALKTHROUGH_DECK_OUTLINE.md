# Agentic AI Governance Prototype — Walkthrough Deck Outline

A presentation-ready outline for walking an audience (interview panel, governance
forum, or meetup) through this project. Build the full deck in Gemini Notebook /
Google Slides from this skeleton.

- **Format per slide:** *On-slide* (what the audience sees) / *Notes* (what you say) / *Visual*.
- **Runtime:** ~12 min full version; a **7-slide interview cut** is marked ★.
- Everything below is grounded in the actual code and the verified demo run — no invented numbers.

---

## ★ Slide 1 — Title
- **On-slide:** *Agentic AI Governance Prototype* — "What is this agent allowed to do, how do we prove it, and how do we stop it?" · Henry Yan · Data & AI Governance.
- **Notes:** One line: a runnable runtime-governance layer for enterprise AI agents, built from first principles so the governance itself is reviewable.
- **Visual:** CollaborAgile banner; subtitle "built on the concepts in microsoft/agent-governance-toolkit".

## ★ Slide 2 — The problem agentic AI creates
- **On-slide:** Model assurance answers *"is the model fair/accurate?"*. Agents force a new question: they **take actions** — call tools, move money, read confidential data, spawn other agents. Three gaps: **authority, proof, control**.
- **Notes:** Fairness/accuracy (my eval harness) is necessary but not sufficient. The moment a model can act, risk shifts from *prediction* to *action*. That's a different control surface.
- **Visual:** Split diagram — "Model layer (harness)" vs "Agentic runtime (this project)".

## Slide 3 — Why it matters in regulated FS
- **On-slide:** OWASP **Top 10 for Agentic Applications (2026)**; NIST **AI RMF**; ISO/IEC **42001**; APRA **CPS 230 / CPS 234 / CPG 235**. Boards now ask for *agent* assurance, not just model assurance.
- **Notes:** These aren't academic — they map directly to operational-risk, info-security and data-risk obligations an AI governance function already owns.
- **Visual:** Four framework logos → one "Assurance Report" artefact.

## ★ Slide 4 — The idea: one governed action gateway
- **On-slide:** Every agent action passes through a single choke point (PDP + PEP): **Identify → Score → Decide → Attest → Contain → Report**.
- **Notes:** Rather than ten scattered controls, one seam. In production you keep this interface and delegate enforcement to the Microsoft toolkit.
- **Visual:** The pipeline diagram from `docs/architecture.md`.

## Slide 5 — (1) Zero-trust agent identity
- **On-slide:** Each agent = owner + least-privilege **capabilities** + data **clearance** + **trust tier** + attestation key. The registry *is* the AI inventory.
- **Notes:** Governance-by-default: nothing not explicitly granted is permitted. Two hard gates deny outright — ungranted capability, or data above clearance.
- **Visual:** `data/agents.json` snippet (orc-1 / kb-1 / pay-1 / util-1).

## ★ Slide 6 — (2+3) Risk scoring → adaptive decision
- **On-slide:** Inherent risk = **likelihood × impact** (1–25) → band → decision. Rigor **scales to risk**:
  - Low (≤4) → allow+log · Medium (5–9) → allow, approve if money/external/irreversible · High (10–14) → **step-up auth** · Critical (15–25) → **DENY + kill-switch**.
- **Notes:** The headline differentiator: *adaptive*. A low-risk read is logged; a $25k irreversible payout is denied. One fixed gate doesn't fit all.
- **Visual:** The 4-band decision table (colour-coded).

## Slide 7 — (4) Tamper-evident attested ledger
- **On-slide:** Every decision is **hash-chained** + **agent-signed (HMAC)**. `verify()` catches edits *and* reordering → non-repudiation.
- **Notes:** This is the evidence a 2nd-line reviewer trusts. In the demo: *Ledger integrity verified: True*; the tests prove tampering and reordering are detected.
- **Visual:** Chain diagram (record → prev_hash → record); green "verified" tick.

## Slide 8 — (5) Kill-switch & cascade halt
- **On-slide:** Critical action or ≥3 denials → **quarantine the agent**. ≥2 agents quarantined → **halt the system** (OWASP T08 cascading failures).
- **Notes:** Containment-first. The breaker turns a single rogue agent into a bounded incident instead of a spreading one.
- **Visual:** Circuit-breaker state → system HALT.

## ★ Slide 9 — Live demo: governance in motion
- **On-slide (verified run):**

  | Agent | Action | Band | Decision |
  | --- | --- | --- | --- |
  | kb-1 | read KB | Low | ALLOW_WITH_LOG |
  | orc-1 | reply to customer | Low | ALLOW_WITH_LOG |
  | pay-1 | refund $250 | High | STEP_UP_AUTH |
  | pay-1 | payout **$25k** | Critical | **DENY → kill-switch** |
  | util-1 | write confidential DB | High | **DENY** (no capability) |
  | util-1 | shell from web content | Medium | **DENY** |
  | util-1 | spawn 50 agents | — | **DENY → quarantined** |
  | util-1 | read KB | — | **HALT** (cascade) |
- **Notes:** Watch governance *move* — allow → step-up → deny → kill-switch → system halt — in one 8-action run. `python -m src.agentgov.run`.
- **Visual:** Terminal screenshot of the actual output.

## Slide 10 — The deliverable: assurance report
- **On-slide:** Auto-generated **Agentic AI Assurance Report** (NIST AI RMF: Govern/Map/Measure/Manage) with agent inventory, OWASP threat model, decision ledger, containment log, limitations, and a **sign-off block**. Status here: **REVIEW REQUIRED**.
- **Notes:** This is what a governance forum actually consumes — not code, an evidenced decision artefact with named accountability.
- **Visual:** `reports/agentic_assurance_report.md` thumbnail.

## ★ Slide 11 — Framework alignment
- **On-slide:** OWASP Agentic Top 10 → controls (T01 hijack, T02 tool misuse, T03 privilege abuse, T08 cascade, T10 rogue agents…). NIST RMF functions. APRA CPS 234 / CPS 230 / CPG 235 crosswalk.
- **Notes:** Each threat ships with controls and is auto-selected per action by capability/context. See `docs/owasp_agentic_alignment.md`.
- **Visual:** Compact OWASP-10 → control matrix.

## Slide 12 — How it fits the ecosystem
- **On-slide:** **Complements** my Responsible AI Eval Harness (model layer). **Mirrors** `microsoft/agent-governance-toolkit` packages (core/runtime/sre/cli) — swap in for production enforcement; adaptive policy table is a natural first PR.
- **Notes:** Two-layer story: model assurance + agentic runtime assurance. First-principles build → credible open-source contribution path.
- **Visual:** Two-box "Harness + Prototype" → "Toolkit (production)".

## ★ Slide 13 — Close
- **On-slide:** Pure-stdlib, runnable, tested (10/10 green). *From trusted data to governed AI — and governed agents.* Repo + contact.
- **Notes:** Transparent by design: every control is readable Python, so the governance can be reviewed. Invite questions.
- **Visual:** CollaborAgile sign-off banner.

---

## Appendix slides (optional, for deep-dive panels)
- **A1 — Threat → control catalogue** (`owasp_agentic.py` full table).
- **A2 — Risk model** (likelihood/impact factors, clamping, band thresholds).
- **A3 — Policy decision tree** (hard gates → band → gating conditions).
- **A4 — Ledger internals** (canonical JSON, genesis, HMAC attestation).
- **A5 — Test evidence** (`test_policy.py` / `test_attestation.py`, 10 passing).
- **A6 — Limitations & roadmap** (synthetic data; illustrative thresholds; production integration).

## Interview cut (≈5 min): slides 1, 2, 4, 6, 9, 11, 13 (the ★ set).
