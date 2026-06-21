"""Minimal RAPHAEL event log scaffold."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json


@dataclass(frozen=True)
class EventRecord:
    input_text: str
    route: str
    risk: str
    decision: str
    reason: str
    timestamp: str


class EventLog:
    def __init__(self, path: str = "raphael_event_log.jsonl") -> None:
        self.path = Path(path)

    def record(self, input_text: str, route: str, risk: str, decision: str, reason: str) -> EventRecord:
        event = EventRecord(
            input_text=input_text,
            route=route,
            risk=risk,
            decision=decision,
            reason=reason,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(event)) + "\n")
        return event
