"""Tests for the adaptive policy engine and governed gateway."""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agentgov.identity import AgentIdentity, AgentRegistry, TrustTier
from src.agentgov.risk import ActionContext
from src.agentgov.policy import AdaptivePolicyEngine, Decision
from src.agentgov.gateway import GovernedActionGateway


class TestPolicy(unittest.TestCase):
    def setUp(self):
        self.engine = AdaptivePolicyEngine()
        self.priv = AgentIdentity("pay", "Pay", "Eng", "payments",
                                  capabilities=["pay"], clearance="confidential",
                                  trust_tier=TrustTier.PRIVILEGED)
        self.weak = AgentIdentity("util", "Util", "None", "utility",
                                  capabilities=["read_kb"], clearance="internal",
                                  trust_tier=TrustTier.UNTRUSTED)

    def test_low_risk_allows(self):
        ctx = ActionContext("kb_read", required_capability="read_kb",
                            data_classification="internal")
        out = self.engine.evaluate(self.weak, ctx)
        self.assertEqual(out.decision, Decision.ALLOW_WITH_LOG)

    def test_missing_capability_denied(self):
        ctx = ActionContext("db_write", required_capability="write_db",
                            data_classification="internal")
        out = self.engine.evaluate(self.weak, ctx)
        self.assertEqual(out.decision, Decision.DENY)

    def test_clearance_gate_denied(self):
        ctx = ActionContext("kb_read", required_capability="read_kb",
                            data_classification="restricted")
        out = self.engine.evaluate(self.weak, ctx)
        self.assertEqual(out.decision, Decision.DENY)

    def test_critical_money_denied_even_for_privileged(self):
        ctx = ActionContext("payment", required_capability="pay",
                            data_classification="confidential",
                            spends_money=25000, irreversible=True, external_facing=True)
        out = self.engine.evaluate(self.priv, ctx)
        self.assertEqual(out.decision, Decision.DENY)

    def test_high_risk_steps_up(self):
        ctx = ActionContext("payment", required_capability="pay",
                            data_classification="confidential",
                            involves_pii=True, spends_money=250, irreversible=True)
        out = self.engine.evaluate(self.priv, ctx)
        self.assertEqual(out.decision, Decision.STEP_UP_AUTH)

    def test_breaker_halts_after_trip(self):
        reg = AgentRegistry()
        reg.register(self.weak)
        gw = GovernedActionGateway(reg)
        # three denials quarantine the agent
        for _ in range(3):
            gw.submit("util", ActionContext("db_write", required_capability="write_db",
                                            data_classification="internal"))
        res = gw.submit("util", ActionContext("kb_read", required_capability="read_kb",
                                             data_classification="internal"))
        self.assertEqual(res.outcome.decision, Decision.HALT)


if __name__ == "__main__":
    unittest.main()
