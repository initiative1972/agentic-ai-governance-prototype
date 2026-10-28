"""Governed action gateway — the single policy decision + enforcement point.

Every agent action passes through `submit()`: the breaker is checked, the action
is risk-scored, the policy engine decides, the decision is attested to the
ledger, and the breaker is updated. This is the choke point that makes agent
self-service safe and enterprise agentic delivery auditable.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .attestation import AuditLedger
from .breaker import CircuitBreaker
from .identity import AgentRegistry
from .policy import AdaptivePolicyEngine, Decision, PolicyOutcome
from .risk import ActionContext


@dataclass
class GatewayResult:
    agent_id: str
    action: str
    outcome: PolicyOutcome


class GovernedActionGateway:
    def __init__(self, registry: AgentRegistry,
                 engine: Optional[AdaptivePolicyEngine] = None,
                 ledger: Optional[AuditLedger] = None,
                 breaker: Optional[CircuitBreaker] = None) -> None:
        self.registry = registry
        self.engine = engine or AdaptivePolicyEngine()
        self.ledger = ledger or AuditLedger(registry)
        self.breaker = breaker or CircuitBreaker()

    def submit(self, agent_id: str, ctx: ActionContext) -> GatewayResult:
        agent = self.registry.get(agent_id)

        if self.breaker.is_open(agent_id):
            out = PolicyOutcome(Decision.HALT, None,
                                ["circuit breaker open (agent/system quarantined)"],
                                [], ["await human reset"])
            self.ledger.append(agent_id, ctx.action_type, out.decision.value, 0, "n/a")
            return GatewayResult(agent_id, ctx.action_type, out)

        out = self.engine.evaluate(agent, ctx)
        band = out.risk.band.value if out.risk else "n/a"
        inherent = out.risk.inherent if out.risk else 0
        self.ledger.append(agent_id, ctx.action_type, out.decision.value, inherent, band)
        self.breaker.record(agent_id, out.decision.value, band)
        return GatewayResult(agent_id, ctx.action_type, out)
