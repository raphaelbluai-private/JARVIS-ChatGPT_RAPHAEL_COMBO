"""RAPHAEL-native text console scaffold."""

from __future__ import annotations

from raphael.core.intent_router import IntentRouter
from raphael.core.policy_engine import PolicyEngine
from raphael.core.event_log import EventLog


class RaphaelConsole:
    def __init__(self, dry_run: bool = True) -> None:
        self.dry_run = dry_run
        self.router = IntentRouter()
        self.policy = PolicyEngine()
        self.events = EventLog()

    def handle(self, text: str) -> str:
        routed = self.router.route(text)
        decision = self.policy.evaluate(routed.risk)
        self.events.record(
            input_text=text,
            route=routed.route,
            risk=routed.risk,
            decision="approved" if decision.approved else "review",
            reason=decision.reason,
        )

        if decision.needs_review:
            return f"RAPHAEL review required: {decision.reason}"

        if self.dry_run:
            return f"[dry-run] route={routed.route}; risk={routed.risk}; reason={routed.reason}"

        return "RAPHAEL native console scaffold is ready for provider integration."
