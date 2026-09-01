from typing import Protocol, runtime_checkable
from dataclasses import dataclass
from datetime import datetime

@dataclass
class FactClaim:
    predicate: str
    category: str
    content: str
    confidence: float
    source_session: str
    timestamp: datetime = datetime.utcnow()

@runtime_checkable
class MemoryProtocol(Protocol):
    def ingest_fact(self, claim: FactClaim) -> int:
        ...
    def reinforce_fact(self, fact_id: int) -> None:
        ...
    def archive_fact(self, fact_id: int) -> None:
        ...