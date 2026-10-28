"""Adaptive, risk-tiered policy decision point (PDP).

Governance rigor scales with the real-time risk of each action:
Low -> allow with log; Medium -> approval if money/external/irreversible;
High -> human approval + step-up auth; Critical -> deny and arm the kill-switch.
Hard identity gates (capability / data-classification) deny outright
(governance-by-default: nothing not explicitly permitted is allowed).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from .identity import AgentIdentity, TrustTier
from .risk import ActionContext, RiskBand, RiskScore, score_action
from .owasp_agentic import threats_for_action


class Decision(str, Enum):
    ALLOW_WITH_LOG = "ALLOW_WITH_LOG"
    REQUIRE_HUMAN_APPROVAL = "REQUIRE_HUMAN_APPROVAL"
    STEP_UP_AUTH = "STEP_UP_AUTH"
    DENY = "DENY"
    HALT = "HALT"


@dataclass
class PolicyOutcome:
    decision: Decision
    risk: Optional[RiskScore]
    reasons: List[str] = field(default_factory=list)
    owasp: List[str] = field(default_factory=list)
    required_controls: List[str] = field(default_factory=list)


class AdaptivePolicyEngine:
    def __init__(self, money_approval_threshold: float = 1000.0) -> None:
        self.money_approval_threshold = money_approval_threshold

    def evaluate(self, agent: AgentIdentity, ctx: ActionContext) -> PolicyOutcome:
        risk = score_action(ctx, agent)
        owasp = threats_for_action(ctx.action_type, ctx.required_capability,
                                   ctx.external_facing, ctx.uses_memory)

        # --- hard identity / privilege gates (OWASP T03) ---
        if ctx.required_capability and not agent.has_capability(ctx.required_capability):
            return PolicyOutcome(Decision.DENY, risk,
                                 [f"agent lacks capability '{ctx.required_capability}' (privilege abuse)"],
                                 owasp, ["least-privilege enforcement", "per-action authorisation"])
        if not agent.can_access(ctx.data_classification):
            return PolicyOutcome(Decision.DENY, risk,
                                 [f"agent not cleared for '{ctx.data_classification}' data"],
                                 owasp, ["data-classification access control"])

        # --- adaptive rigor by risk band ---
        gated = ctx.spends_money > 0 or ctx.irreversible or ctx.external_facing

        if risk.band == RiskBand.CRITICAL:
            return PolicyOutcome(Decision.DENY, risk, ["critical residual risk"],
                                 owasp, ["halt & human review", "arm kill-switch"])

        if risk.band == RiskBand.HIGH:
            return PolicyOutcome(Decision.STEP_UP_AUTH, risk,
                                 ["high risk requires human approval + step-up authentication"],
                                 owasp, ["human-in-the-loop approval", "step-up authentication", "action attestation"])

        if risk.band == RiskBand.MEDIUM:
            if gated or ctx.spends_money >= self.money_approval_threshold:
                return PolicyOutcome(Decision.REQUIRE_HUMAN_APPROVAL, risk,
                                     ["medium risk with money/external/irreversible -> approval"],
                                     owasp, ["human-in-the-loop approval", "action attestation"])
            if agent.trust_tier >= TrustTier.PRIVILEGED:
                return PolicyOutcome(Decision.ALLOW_WITH_LOG, risk,
                                     ["privileged agent, medium non-gated risk -> allow with log"],
                                     owasp, ["audit log"])
            return PolicyOutcome(Decision.ALLOW_WITH_LOG, risk,
                                 ["medium risk -> allow with log + monitoring"],
                                 owasp, ["audit log", "post-hoc review sample"])

        # LOW
        return PolicyOutcome(Decision.ALLOW_WITH_LOG, risk, ["low risk -> allow with log"],
                             owasp, ["audit log"])
