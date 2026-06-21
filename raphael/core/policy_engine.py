"""Minimal RAPHAEL policy engine scaffold."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyDecision:
    approved: bool
    needs_review: bool
    reason: str


class PolicyEngine:
    def evaluate(self, risk: str) -> PolicyDecision:
        normalized = risk.strip().lower()

        if normalized == "high":
            return PolicyDecision(
                approved=False,
                needs_review=True,
                reason="manual review is required for this action class",
            )
        if normalized in {"low", "medium"}:
            return PolicyDecision(
                approved=True,
                needs_review=False,
                reason=f"{normalized} action class passed baseline policy",
            )
        return PolicyDecision(
            approved=False,
            needs_review=True,
            reason=f"unknown action class: {risk}",
        )
