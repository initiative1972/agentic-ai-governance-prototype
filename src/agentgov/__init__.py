"""Agentic AI Governance Prototype (`agentgov`).

A lightweight, first-principles, *runtime* governance layer for enterprise AI
agents: zero-trust agent identity, an adaptive risk-tiered policy engine, a
tamper-evident attested action ledger, and a kill-switch / circuit breaker —
producing an Agentic AI Assurance Report structured on the NIST AI RMF and
mapped to the OWASP Top 10 for Agentic Applications.

Built as a transparent reference implementation of the concepts that
`microsoft/agent-governance-toolkit` productionises, and designed to complement
the Responsible AI Evaluation Harness (which governs model fairness/accuracy).
"""
from .identity import AgentIdentity, AgentRegistry, TrustTier
from .risk import ActionContext, RiskScore, RiskBand, score_action
from .policy import AdaptivePolicyEngine, Decision, PolicyOutcome
from .attestation import AuditLedger, LedgerRecord
from .breaker import CircuitBreaker
from .gateway import GovernedActionGateway, GatewayResult
from .owasp_agentic import AGENTIC_TOP_10, threats_for_action

__version__ = "0.1.0"
__all__ = [
    "AgentIdentity", "AgentRegistry", "TrustTier",
    "ActionContext", "RiskScore", "RiskBand", "score_action",
    "AdaptivePolicyEngine", "Decision", "PolicyOutcome",
    "AuditLedger", "LedgerRecord", "CircuitBreaker",
    "GovernedActionGateway", "GatewayResult",
    "AGENTIC_TOP_10", "threats_for_action",
]
