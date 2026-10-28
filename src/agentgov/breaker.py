"""Kill-switch / circuit breaker — containment and termination control.

Trips an agent on any critical action or after repeated high-risk/denied
actions, and trips the whole system when failures cascade across agents. Once
open, the gateway auto-halts further actions until a human resets it.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class BreakerState:
    tripped: bool = False
    reason: str = ""
    events: int = 0


class CircuitBreaker:
    def __init__(self, high_risk_limit: int = 3, cascade_limit: int = 2) -> None:
        self.high_risk_limit = high_risk_limit
        self.cascade_limit = cascade_limit
        self.agents: Dict[str, BreakerState] = {}
        self.system = BreakerState()
        self.log: List[str] = []

    def _st(self, agent_id: str) -> BreakerState:
        return self.agents.setdefault(agent_id, BreakerState())

    def is_open(self, agent_id: str) -> bool:
        return self.system.tripped or self._st(agent_id).tripped

    def record(self, agent_id: str, decision: str, band: str) -> None:
        st = self._st(agent_id)
        if band == "Critical" or decision == "DENY":
            st.events += 1
        if band == "Critical" and not st.tripped:
            st.tripped = True
            st.reason = "critical residual risk"
            self.log.append(f"KILL-SWITCH: agent {agent_id} quarantined (critical action blocked)")
        elif st.events >= self.high_risk_limit and not st.tripped:
            st.tripped = True
            st.reason = f">= {self.high_risk_limit} high-risk / denied actions"
            self.log.append(f"KILL-SWITCH: agent {agent_id} quarantined ({st.reason})")

        tripped = [a for a, s in self.agents.items() if s.tripped]
        if len(tripped) >= self.cascade_limit and not self.system.tripped:
            self.system.tripped = True
            self.system.reason = f"cascading failures ({len(tripped)} agents quarantined)"
            self.log.append("SYSTEM HALT: cascading failures across agents")

    def reset(self, agent_id: str, by: str = "human") -> None:
        self.agents[agent_id] = BreakerState()
        self.log.append(f"RESET: agent {agent_id} reinstated by {by}")
