"""Smoke tests for the RAPHAEL-native scaffold."""

from raphael.core.intent_router import IntentRouter
from raphael.core.policy_engine import PolicyEngine
from raphael.voice.console import RaphaelConsole


def test_router_defaults_to_chat():
    routed = IntentRouter().route("what should I do next?")

    assert routed.route == "chat"
    assert routed.risk == "low"


def test_router_marks_research_workflow():
    routed = IntentRouter().route("research papers about local AI assistants")

    assert routed.route == "research"
    assert routed.risk == "medium"


def test_policy_requires_review_for_high_class():
    decision = PolicyEngine().evaluate("high")

    assert decision.approved is False
    assert decision.needs_review is True


def test_native_console_dry_run_routes_input(tmp_path):
    console = RaphaelConsole(dry_run=True)
    console.events.path = tmp_path / "events.jsonl"

    result = console.handle("remember this project decision")

    assert "route=memory" in result
    assert console.events.path.exists()
