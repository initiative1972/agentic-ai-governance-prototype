"""Zero-trust agent identity and registry.

Every agent has an explicit identity: an owner, a role, a *least-privilege*
capability grant, a data-classification clearance, and a trust tier. Each agent
is issued a secret key used to *attest* (HMAC-sign) the actions attributed to it
in the audit ledger — the basis for non-repudiation.
"""
from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Dict, List


class TrustTier(IntEnum):
    """Privilege ring. Higher tiers earn more autonomy — never on money/irreversible actions."""
    UNTRUSTED = 0
    LIMITED = 1
    STANDARD = 2
    PRIVILEGED = 3


# Ordered sensitivity so clearance can be compared to the data an action touches.
DATA_CLASS_ORDER = {"public": 0, "internal": 1, "confidential": 2, "restricted": 3}


@dataclass
class AgentIdentity:
    agent_id: str
    name: str
    owner: str
    role: str
    capabilities: List[str] = field(default_factory=list)   # least-privilege grants
    clearance: str = "internal"                             # max data classification allowed
    trust_tier: TrustTier = TrustTier.STANDARD
    human_oversight: bool = True
    _key: bytes = field(default=b"", repr=False)

    def can_access(self, data_classification: str) -> bool:
        return DATA_CLASS_ORDER.get(data_classification, 3) <= DATA_CLASS_ORDER.get(self.clearance, 0)

    def has_capability(self, capability: str) -> bool:
        return capability in self.capabilities

    def sign(self, message: str) -> str:
        """HMAC-SHA256 attestation over a canonical message (non-repudiation)."""
        return hmac.new(self._key, message.encode(), hashlib.sha256).hexdigest()


class AgentRegistry:
    """The AI inventory: the set of agents allowed to exist and act."""

    def __init__(self) -> None:
        self._agents: Dict[str, AgentIdentity] = {}

    def register(self, agent: AgentIdentity) -> AgentIdentity:
        if agent.agent_id in self._agents:
            raise ValueError(f"agent {agent.agent_id} already registered")
        if not agent._key:
            agent._key = secrets.token_bytes(32)
        self._agents[agent.agent_id] = agent
        return agent

    def get(self, agent_id: str) -> AgentIdentity:
        if agent_id not in self._agents:
            raise KeyError(f"unknown agent {agent_id}")
        return self._agents[agent_id]

    def all(self) -> List[AgentIdentity]:
        return list(self._agents.values())
