"""Tests for the tamper-evident attested action ledger."""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agentgov.identity import AgentIdentity, AgentRegistry, TrustTier
from src.agentgov.attestation import AuditLedger


class TestAttestation(unittest.TestCase):
    def setUp(self):
        self.reg = AgentRegistry()
        self.reg.register(AgentIdentity("a1", "A1", "Owner", "role",
                                        capabilities=["read_kb"], trust_tier=TrustTier.STANDARD))
        self.ledger = AuditLedger(self.reg)
        self.ledger.append("a1", "kb_read", "ALLOW_WITH_LOG", 2, "Low")
        self.ledger.append("a1", "payment", "DENY", 20, "Critical")

    def test_chain_verifies(self):
        self.assertTrue(self.ledger.verify())

    def test_detects_tampering(self):
        # mutate a committed record without recomputing hashes
        self.ledger.records[0].decision = "HALT"
        self.assertFalse(self.ledger.verify())

    def test_detects_reorder(self):
        self.ledger.records[0], self.ledger.records[1] = (
            self.ledger.records[1], self.ledger.records[0])
        self.assertFalse(self.ledger.verify())

    def test_records_are_attested(self):
        self.assertTrue(all(r.attestation and r.attestation != "UNREGISTERED"
                            for r in self.ledger.records))


if __name__ == "__main__":
    unittest.main()
