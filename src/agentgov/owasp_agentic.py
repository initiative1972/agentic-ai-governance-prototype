"""OWASP Top 10 for Agentic Applications (2026) — control-annotated catalogue.

Ships the agentic threat list and auto-selects the threats applicable to a
given action from its capability and context. Verify the identifiers and titles
against the current OWASP GenAI Security Project publication before formal use.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class AgenticThreat:
    id: str
    title: str
    description: str
    controls: tuple


AGENTIC_TOP_10: Dict[str, AgenticThreat] = {
    "T01": AgenticThreat("T01", "Agent Goal / Instruction Hijack",
        "Manipulating an agent's goal or instructions (e.g. prompt injection) to redirect its behaviour.",
        ("input provenance & isolation", "instruction/plan validation", "out-of-band goal confirmation")),
    "T02": AgenticThreat("T02", "Tool Misuse",
        "Agent invokes tools in unintended or unsafe ways.",
        ("per-tool capability grants", "argument validation", "dry-run / sandbox")),
    "T03": AgenticThreat("T03", "Identity & Privilege Abuse",
        "Agent acts beyond its authorised identity or permissions.",
        ("zero-trust identity", "least-privilege rings", "per-action authorisation")),
    "T04": AgenticThreat("T04", "Supply-Chain Vulnerabilities",
        "Compromise via third-party models, tools or components.",
        ("component provenance", "version pinning", "vendor due diligence")),
    "T05": AgenticThreat("T05", "Unexpected Code Execution",
        "Agent executes attacker-influenced code or commands.",
        ("command denylist", "execution sandbox", "no raw shell/eval")),
    "T06": AgenticThreat("T06", "Memory & Context Poisoning",
        "Corrupting agent memory or RAG context to alter future actions.",
        ("source vetting", "memory integrity checks", "context provenance")),
    "T07": AgenticThreat("T07", "Insecure Inter-Agent Communication",
        "Spoofing or abuse of agent-to-agent / MCP protocols.",
        ("authenticated A2A/MCP", "message signing", "allow-listed peers")),
    "T08": AgenticThreat("T08", "Cascading Failures",
        "One agent's failure or compromise propagates across the system.",
        ("circuit breakers", "blast-radius limits", "isolation")),
    "T09": AgenticThreat("T09", "Human-Agent Trust Exploitation",
        "Over-trust of agent output by humans; overwhelming the human-in-the-loop.",
        ("confidence/uncertainty surfacing", "rate-limited approvals", "clear provenance to users")),
    "T10": AgenticThreat("T10", "Rogue / Unbounded Agents",
        "Agents operating outside policy, self-spawning, or consuming without bound.",
        ("inventory & attestation", "kill-switch / termination", "quotas & budgets")),
}

# Which threats a capability tends to attract.
CAPABILITY_THREATS = {
    "call_tool": ["T02", "T05"],
    "spawn_agent": ["T10", "T07"],
    "write_db": ["T03", "T05"],
    "send_external": ["T01", "T09"],
    "read_kb": ["T06"],
    "pay": ["T02", "T03"],
}


def threats_for_action(action_type: str, capability: Optional[str],
                       external_facing: bool, uses_memory: bool) -> List[str]:
    """Select applicable OWASP agentic threats from an action's shape."""
    ids = {"T01"}  # goal hijack applies to every LLM-driven agent
    if capability:
        for cap, ts in CAPABILITY_THREATS.items():
            if capability.startswith(cap):
                ids.update(ts)
    if external_facing:
        ids.update(["T01", "T09"])
    if uses_memory:
        ids.add("T06")
    return sorted(ids)
