"""Real-time action risk scoring.

Each action an agent attempts is scored *in the moment* on likelihood x impact
(1-25), from first principles, so the policy engine can scale governance rigor
to the risk rather than applying a one-size gate.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from .identity import AgentIdentity, DATA_CLASS_ORDER


@dataclass
class ActionContext:
    """What an agent is trying to do, right now."""
    action_type: str
    description: str = ""
    required_capability: Optional[str] = None
    data_classification: str = "internal"
    external_facing: bool = False
    involves_pii: bool = False
    spends_money: float = 0.0
    irreversible: bool = False
    uses_memory: bool = False
    injection_suspected: bool = False
    target: str = ""


class RiskBand(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


@dataclass
class RiskScore:
    likelihood: int
    impact: int
    inherent: int
    band: RiskBand
    factors: List[str] = field(default_factory=list)


def _clamp(x: float) -> int:
    return max(1, min(5, int(round(x))))


def score_action(ctx: ActionContext, agent: AgentIdentity) -> RiskScore:
    factors: List[str] = []

    likelihood = 1.0
    if ctx.external_facing:
        likelihood += 1; factors.append("external-facing")
    if ctx.injection_suspected:
        likelihood += 2; factors.append("suspected prompt injection")
    if ctx.action_type in ("tool_call", "db_write", "payment", "spawn_agent"):
        likelihood += 1; factors.append(f"action={ctx.action_type}")
    if ctx.required_capability and not agent.has_capability(ctx.required_capability):
        likelihood += 1; factors.append("capability not granted")
    if agent.trust_tier <= 1:
        likelihood += 1; factors.append("low agent trust tier")

    impact = 1.0
    dc = DATA_CLASS_ORDER.get(ctx.data_classification, 1)
    if dc >= 2:
        impact += dc; factors.append(f"data={ctx.data_classification}")
    if ctx.involves_pii:
        impact += 1; factors.append("PII")
    if ctx.spends_money > 0:
        impact += 1 + (1 if ctx.spends_money >= 1000 else 0) + (1 if ctx.spends_money >= 10000 else 0)
        factors.append(f"spends ${ctx.spends_money:.0f}")
    if ctx.irreversible:
        impact += 1; factors.append("irreversible")

    likelihood_i, impact_i = _clamp(likelihood), _clamp(impact)
    inherent = likelihood_i * impact_i
    if inherent <= 4:
        band = RiskBand.LOW
    elif inherent <= 9:
        band = RiskBand.MEDIUM
    elif inherent <= 14:
        band = RiskBand.HIGH
    else:
        band = RiskBand.CRITICAL
    return RiskScore(likelihood_i, impact_i, inherent, band, factors)
