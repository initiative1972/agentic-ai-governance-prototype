"""Tamper-evident, agent-attested action ledger.

Every governed action is appended to a hash-chained ledger. Each record carries
the previous record's hash (chain integrity) and an HMAC attestation signed with
the acting agent's key (attribution / non-repudiation). `verify()` detects any
tampering or reordering.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass
from typing import List, Optional

from .identity import AgentRegistry


def _canon(d: dict) -> str:
    return json.dumps(d, sort_keys=True, separators=(",", ":"), default=str)


@dataclass
class LedgerRecord:
    seq: int
    ts: float
    agent_id: str
    action: str
    decision: str
    inherent: int
    band: str
    prev_hash: str
    attestation: str = ""
    record_hash: str = ""


class AuditLedger:
    GENESIS = "0" * 64

    def __init__(self, registry: Optional[AgentRegistry] = None) -> None:
        self.registry = registry
        self.records: List[LedgerRecord] = []

    @staticmethod
    def _body(rec: LedgerRecord) -> str:
        return _canon({k: v for k, v in asdict(rec).items()
                       if k not in ("attestation", "record_hash")})

    def append(self, agent_id: str, action: str, decision: str,
               inherent: int, band: str) -> LedgerRecord:
        prev = self.records[-1].record_hash if self.records else self.GENESIS
        rec = LedgerRecord(seq=len(self.records), ts=time.time(), agent_id=agent_id,
                           action=action, decision=decision, inherent=inherent,
                           band=band, prev_hash=prev)
        body = self._body(rec)
        if self.registry:
            try:
                rec.attestation = self.registry.get(agent_id).sign(body)
            except KeyError:
                rec.attestation = "UNREGISTERED"
        rec.record_hash = hashlib.sha256((body + rec.attestation).encode()).hexdigest()
        self.records.append(rec)
        return rec

    def verify(self) -> bool:
        prev = self.GENESIS
        for rec in self.records:
            if rec.prev_hash != prev:
                return False
            expected = hashlib.sha256((self._body(rec) + rec.attestation).encode()).hexdigest()
            if rec.record_hash != expected:
                return False
            prev = rec.record_hash
        return True
