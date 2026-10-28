"""End-to-end demo: profile a multi-agent system -> govern a run -> report.

Run from the repository root:

    python -m src.agentgov.run

It builds a synthetic enterprise multi-agent system (a customer-service
orchestrator, a KB retriever, a privileged payments agent, and an
under-trusted utility agent), submits a sequence of actions through the governed
gateway, and writes an Agentic AI Assurance Report to ``reports/``. The run is
designed to show every decision type — allow, step-up, deny, and a kill-switch
trip that cascades to a system halt.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from .assurance import render_assurance_report
from .gateway import GovernedActionGateway
from .identity import AgentIdentity, AgentRegistry, TrustTier
from .owasp_agentic import threats_for_action
from .risk import ActionContext


def build_system() -> AgentRegistry:
    reg = AgentRegistry()
    reg.register(AgentIdentity("orc-1", "Orchestrator", "AI Platform Team",
        "customer-service orchestrator",
        capabilities=["read_kb", "call_tool:handoff", "send_external"],
        clearance="internal", trust_tier=TrustTier.STANDARD))
    reg.register(AgentIdentity("kb-1", "KB Retriever", "AI Platform Team", "retrieval agent",
        capabilities=["read_kb"], clearance="internal", trust_tier=TrustTier.LIMITED))
    reg.register(AgentIdentity("pay-1", "Payments Agent", "Payments Eng", "payment execution agent",
        capabilities=["call_tool:payments", "pay"], clearance="confidential",
        trust_tier=TrustTier.PRIVILEGED))
    reg.register(AgentIdentity("util-1", "Utility Agent", "Unassigned", "general utility agent",
        capabilities=["read_kb"], clearance="internal", trust_tier=TrustTier.UNTRUSTED))
    return reg


def scenario() -> List[Tuple[str, ActionContext]]:
    return [
        ("kb-1", ActionContext("kb_read", "retrieve KB article",
            required_capability="read_kb", data_classification="internal", uses_memory=True)),
        ("orc-1", ActionContext("send_external", "reply to customer",
            required_capability="send_external", data_classification="internal", external_facing=True)),
        ("pay-1", ActionContext("payment", "refund $250 to customer",
            required_capability="pay", data_classification="confidential",
            involves_pii=True, spends_money=250, irreversible=True)),
        ("pay-1", ActionContext("payment", "payout $25,000 to third party",
            required_capability="pay", data_classification="confidential",
            spends_money=25000, irreversible=True, external_facing=True)),
        ("util-1", ActionContext("db_write", "update customer record",
            required_capability="write_db", data_classification="confidential")),
        ("util-1", ActionContext("tool_call", "run shell command from web content",
            required_capability="call_tool:exec", data_classification="internal",
            external_facing=True, injection_suspected=True)),
        ("util-1", ActionContext("spawn_agent", "spawn 50 sub-agents",
            required_capability="spawn_agent", data_classification="internal")),
        ("util-1", ActionContext("kb_read", "retrieve KB article",
            required_capability="read_kb", data_classification="internal")),
    ]


def run(out_dir: str = "reports") -> None:
    reg = build_system()
    gw = GovernedActionGateway(reg)
    applicable = set()

    print("\nAgentic AI Governance Prototype - governed action decisions\n")
    for agent_id, ctx in scenario():
        res = gw.submit(agent_id, ctx)
        applicable.update(threats_for_action(ctx.action_type, ctx.required_capability,
                                              ctx.external_facing, ctx.uses_memory))
        band = res.outcome.risk.band.value if res.outcome.risk else "n/a"
        print(f"[{agent_id:6s}] {ctx.action_type:12s} band={band:9s} -> {res.outcome.decision.value}")

    report = render_assurance_report(reg, gw.ledger, gw.breaker, sorted(applicable))
    out = Path(out_dir)
    out.mkdir(exist_ok=True)
    report_path = out / "agentic_assurance_report.md"
    report_path.write_text(report, encoding="utf-8")

    print(f"\nLedger integrity verified: {gw.ledger.verify()}")
    print(f"Report written to: {report_path.resolve()}\n")


if __name__ == "__main__":
    run()
