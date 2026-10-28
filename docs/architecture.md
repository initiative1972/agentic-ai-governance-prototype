# Architecture

The prototype is a single **governed action gateway** that every agent action
must pass through — a Policy Decision Point (PDP) and Policy Enforcement Point
(PEP) with an attested audit trail and a kill-switch.

```
                        +-----------------------------+
   agent action  --->   |   GovernedActionGateway     |
   (ActionContext)      |                             |
                        |  1. CircuitBreaker.is_open? |---- open ---> HALT (logged)
                        |  2. score_action (risk.py)  |
                        |  3. AdaptivePolicyEngine     |---> Decision
                        |  4. AuditLedger.append       |   (ALLOW / STEP_UP /
                        |     (hash-chain + attest)    |    APPROVE / DENY / HALT)
                        |  5. CircuitBreaker.record    |
                        +-----------------------------+
                                     |
                                     v
                        AuditLedger  +  CircuitBreaker
                                     |
                                     v
                     assurance.render_assurance_report  (NIST AI RMF)
```

## Components

| Module | Role | NIST AI RMF |
| --- | --- | --- |
| `identity.py` | Zero-trust agent identity, least-privilege capabilities, data clearance, trust tier, attestation key; the registry is the AI inventory | GOVERN |
| `owasp_agentic.py` | OWASP Top 10 for Agentic Applications catalogue; selects applicable threats by capability/context | MAP |
| `risk.py` | Real-time likelihood x impact scoring -> risk band | MEASURE |
| `policy.py` | Adaptive risk-tiered decision point; hard identity/data gates | MEASURE / MANAGE |
| `attestation.py` | Hash-chained, agent-signed, tamper-evident action ledger | GOVERN / MEASURE |
| `breaker.py` | Kill-switch / circuit breaker; agent quarantine + system halt | MANAGE |
| `gateway.py` | The single PDP+PEP choke point tying it together | GOVERN |
| `assurance.py` | Governance-ready assurance report with decision + sign-off | all four |

## Design principles

- **Governance by default** — nothing not explicitly permitted is allowed; teams
  request exceptions, not the reverse.
- **Rigor scales to risk** — a low-risk read is logged; a $25k irreversible payout
  is denied. One gate does not fit all.
- **Attribution & non-repudiation** — every action is signed by the acting agent
  and chained, so the record is tamper-evident and attributable.
- **Containment first** — a critical action or a rogue agent trips a kill-switch
  before damage spreads; cascades halt the system.
- **Transparent first principles** — every control is readable Python, so the
  governance itself can be reviewed (a responsible-AI expectation).
