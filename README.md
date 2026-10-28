# agentic-ai-governance-prototype
A lightweight, auditable **runtime governance layer for enterprise AI agents** —
zero-trust agent identity, an **adaptive risk-tiered policy engine**, a
**tamper-evident attested action ledger**, and a **kill-switch / circuit
breaker** — that produces the **Agentic AI Assurance Report** a governance forum
reviews before (and while) autonomous agents are allowed to act.

> Portfolio piece for data & AI governance in regulated (banking / financial
> services) environments. Every control is implemented from first principles so
> the governance itself is transparent and reviewable. It is a reference
> implementation of the concepts productionised by
> [`microsoft/agent-governance-toolkit`](https://github.com/microsoft/agent-governance-toolkit),
> and it complements the **Responsible AI Evaluation Harness** (model
> fairness/accuracy) by covering the *agentic runtime* instead.

---

## Why this exists

Model-level assurance answers *"is this model fair, accurate and fit?"*. It does
**not** answer the question agentic AI forces: *"this thing can take actions —
call tools, move money, spawn other agents, read confidential data — so **what is
it allowed to do, how do we prove each action was authorised, and how do we stop
it?**"*

This prototype operationalises that as a single **governed action gateway**:

1. **Identify** every agent (owner, least-privilege capabilities, data clearance, trust tier).
2. **Score** each action's risk in real time (likelihood x impact).
3. **Decide** with rigor that scales to the risk — allow / approve / step-up / deny.
4. **Attest** every decision to a hash-chained, agent-signed ledger (non-repudiation).
5. **Contain** with a kill-switch that quarantines a rogue agent and halts cascades.
6. **Report** it all as a NIST-AI-RMF-structured assurance report with sign-off.

It maps to the **OWASP Top 10 for Agentic Applications**, the **NIST AI RMF**,
**ISO/IEC 42001**, and **APRA CPS 230 / CPS 234 / CPG 235** — see
[`docs/owasp_agentic_alignment.md`](docs/owasp_agentic_alignment.md).

---

## What's inside

```
agentic-ai-governance-prototype/
├── src/agentgov/
│   ├── identity.py         # zero-trust agent identity + registry (the AI inventory)
│   ├── owasp_agentic.py    # OWASP Top 10 for Agentic Applications + control catalogue
│   ├── risk.py             # real-time action risk scoring (likelihood x impact -> band)
│   ├── policy.py           # AdaptivePolicyEngine: risk-tiered decision point (PDP)
│   ├── attestation.py      # hash-chained, agent-attested action ledger (tamper-evident)
│   ├── breaker.py          # kill-switch / circuit breaker (termination & containment)
│   ├── gateway.py          # GovernedActionGateway: the single PDP+PEP choke point
│   ├── assurance.py        # Agentic AI Assurance Report (NIST AI RMF)
│   └── run.py              # end-to-end multi-agent scenario -> ledger + report
├── data/                   # sample agent profiles + policy thresholds (swap in your own)
├── docs/                   # architecture, OWASP/NIST/APRA alignment, toolkit integration
├── templates/              # assurance report template
├── reports/                # generated artefacts land here
├── tests/                  # test_policy.py, test_attestation.py
├── requirements.txt
└── LICENSE
```

---

## Quickstart

Requires **Python 3.10+**. No third-party dependencies — pure standard library.

```bash
# run the end-to-end demo (writes reports/agentic_assurance_report.md)
python -m src.agentgov.run

# run the tests
python -m unittest discover -s tests -v
```

The demo governs a synthetic multi-agent system and deliberately exercises every
decision path:

| Agent | Action | Risk band | Decision |
| --- | --- | --- | --- |
| `kb-1` | read a KB article | Low | ALLOW_WITH_LOG |
| `orc-1` | reply to a customer | Low | ALLOW_WITH_LOG |
| `pay-1` | refund $250 (irreversible, PII) | High | STEP_UP_AUTH |
| `pay-1` | payout **$25,000** external | Critical | **DENY → kill-switch** |
| `util-1` | write a confidential DB record (no capability) | — | **DENY** (privilege abuse) |
| `util-1` | run shell command from web content | — | **DENY** |
| `util-1` | spawn 50 sub-agents | — | **DENY → agent quarantined** |
| `util-1` | read a KB article | — | **HALT** (system halted — cascade) |

The run shows governance **move** from allow, through step-up and deny, to a
kill-switch trip that cascades into a **system halt** — then proves the ledger is
tamper-evident.

---

## The adaptive policy (plain English)

Governance rigor **scales to the real-time risk** of each action — not a single
fixed gate:

| Risk band (inherent = likelihood x impact) | Default decision |
| --- | --- |
| **Low** (≤ 4) | Allow with log |
| **Medium** (5–9) | Allow with log — *approval* if it spends money / is external / irreversible |
| **High** (10–14) | Human approval **+ step-up authentication** + attestation |
| **Critical** (15–25) | **Deny** and arm the kill-switch |

Two **hard gates** deny outright regardless of band (governance-by-default):
an action needing a **capability the agent wasn't granted**, or touching a
**data classification above its clearance**.

---

## How it relates to `microsoft/agent-governance-toolkit`

This prototype mirrors the toolkit's building blocks so you can reason about them
transparently and later swap in the production engine. See
[`docs/toolkit_integration.md`](docs/toolkit_integration.md) for the mapping
(policy engine, capability model, zero-trust identity, audit, circuit breakers,
OWASP verification).

---

## Important notes

- The agents, policies and scenario are **synthetic** — they exist to exercise
  the workflow. Swap in your own via `data/agents.json` and `data/policies.json`.
- Risk weights, thresholds and control effectiveness are **illustrative** and
  must be agreed with Risk & Compliance per use case.
- The gateway is a **decision point that informs a human governance forum**, not
  a silent autonomous enforcer. Wire it to the toolkit for production enforcement.
- OWASP Agentic identifiers reflect the **2026** list — verify against the current
  OWASP GenAI Security Project publication.

## License

MIT — see [`LICENSE`](LICENSE).
