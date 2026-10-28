# Integration with `microsoft/agent-governance-toolkit`

This prototype is a transparent, first-principles reference for the concepts that
the [Microsoft Agent Governance Toolkit](https://github.com/microsoft/agent-governance-toolkit)
(MIT-licensed, multi-language) productionises. The modules here are deliberately
shaped to mirror the toolkit's packages so you can reason about the controls in
plain Python and then swap in the production engine for enforcement at scale.

## Concept mapping

| This prototype (`agentgov`) | Toolkit package / capability |
| --- | --- |
| `identity.AgentIdentity` / `AgentRegistry` | `agent-governance-toolkit-core` — zero-trust identity, capability model, trust scoring |
| `policy.AdaptivePolicyEngine` | `agent-governance-toolkit-core` — policy engine (+ `cli` policy linting) |
| `gateway.GovernedActionGateway` | `agent-governance-toolkit-core` — MCP gateway / action mediation |
| `attestation.AuditLedger` | `agent-governance-toolkit-core` — audit / attestation |
| `breaker.CircuitBreaker` | `agent-governance-toolkit-sre` — circuit breakers, error budgets; `-runtime` termination control |
| exec/denylist checks in `policy`/`risk` | `agent-governance-toolkit-runtime` — privilege rings, command denylist, execution-plan validation |
| `owasp_agentic` catalogue | `agent-governance-toolkit-cli` — OWASP (Agentic Top 10) verification |

## Suggested integration path

1. **Keep the gateway seam.** `GovernedActionGateway.submit()` is the single choke
   point. In production, delegate steps 2–5 to the toolkit's policy engine and
   runtime while keeping this interface.
2. **Install the toolkit** (optional): `pip install agent-governance-toolkit[full]`
   (see `requirements.txt`). Replace the in-memory `AuditLedger` with the toolkit's
   audit sink and the `CircuitBreaker` with the SRE package's breakers.
3. **Run OWASP verification** via the toolkit CLI (`agt`) in CI alongside this
   repo's unit tests, so agentic threats are checked on every change.
4. **Contribution opportunity.** Porting this prototype's adaptive risk-tiered
   decision table as a reusable policy pattern is a natural first PR to the toolkit —
   and a visible, credibility-building open-source contribution.

> Verify package names and APIs against the toolkit's current README before wiring,
> as the project is young and evolving.
