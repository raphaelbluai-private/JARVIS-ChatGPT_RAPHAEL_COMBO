"""Minimal RAPHAEL intent router scaffold.

This is intentionally simple for the repair branch. The extraction branch should
replace heuristic routing with a tested router and policy-backed command schema.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RoutedIntent:
    route: str
    risk: str
    reason: str


class IntentRouter:
    def route(self, text: str) -> RoutedIntent:
        normalized = text.strip().lower()

        if not normalized:
            return RoutedIntent(route="noop", risk="low", reason="empty input")
        if any(term in normalized for term in ["delete", "send email", "push commit", "spend", "sign"]):
            return RoutedIntent(route="approval_required", risk="high", reason="high-risk action keyword detected")
        if any(term in normalized for term in ["research", "paper", "study", "semantic scholar"]):
            return RoutedIntent(route="research", risk="medium", reason="research workflow keyword detected")
        if any(term in normalized for term in ["save", "remember", "note"]):
            return RoutedIntent(route="memory", risk="low", reason="memory workflow keyword detected")

        return RoutedIntent(route="chat", risk="low", reason="default conversational route")
