"""Static smoke tests for the RAPHAEL repair baseline.

These tests intentionally avoid importing the heavy legacy audio stack. They only
check that the repair branch is wired to RAPHAEL and that the extraction-ready
files contain the expected safeguards.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_startup_uses_raphael_wrapper_and_identity():
    content = read("openai_api_chatbot.py")

    assert "from Assistant.RaphaelAssistant import RaphaelAssistant" in content
    assert "ASSISTANT_NAME = os.getenv('RAPHAEL_ASSISTANT_NAME', 'RAPHAEL')" in content
    assert "RAPHAEL_WAKE_KEYWORDS" in content
    assert "raphael = RaphaelAssistant(" in content


def test_prompt_routing_is_not_hardcoded_to_switch_mode():
    content = read("openai_api_chatbot.py")

    assert "flag = raphael.analyze_prompt(prompt)" in content
    assert "flag = '-1'" not in content


def test_raphael_wrapper_repairs_caht_tool_bug_functionally():
    content = read("Assistant/RaphaelAssistant.py")

    assert "class RaphaelAssistant(VirtualAssistant):" in content
    assert 'if self.MODE == "CHAT":' in content
    assert 'self.MODE == "CAHT"' not in content


def test_raphael_research_wrapper_accepts_pdf_lists():
    content = read("Assistant/RaphaelAssistant.py")

    assert "class RaphaelResearchAssistant(ResearchAssistant):" in content
    assert "def load_pdf_to_pinecone(self, paths):" in content
    assert "if isinstance(paths, str):" in content
    assert "elif not isinstance(paths, (list, tuple)):" in content
    assert "raise Exception" not in content.split("def load_pdf_to_pinecone", 1)[1].split("class RaphaelAssistant", 1)[0]


def test_text_console_has_dry_run_mode():
    content = read("raphael_text_console.py")

    assert "class RaphaelTextSession" in content
    assert "--dry-run" in content
    assert "No microphone, TTS, API call, or tool execution was invoked." in content


def test_repair_plan_exists():
    content = read("RAPHAEL_REPAIR_PLAN.md")

    assert "RAPHAEL Repair and Extraction Plan" in content
    assert "Voice Input" in content
    assert "Permission Gate" in content
