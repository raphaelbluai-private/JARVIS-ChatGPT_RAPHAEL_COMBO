"""Text-only RAPHAEL console.

Purpose:
- Exercise the RAPHAEL prompt loop without microphone, wake word, Whisper, PyAudio,
  pygame playback, IBM, ElevenLabs, or Coqui TTS.
- Provide a low-cost repair harness before the voice stack is tested.

Usage:

    python raphael_text_console.py --dry-run
    python raphael_text_console.py

Commands:

    /mode chat
    /mode research
    /history
    /clear
    /exit
"""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass, field
from typing import List, Dict

from dotenv import load_dotenv


SYSTEM_PROMPT = (
    "You are RAPHAEL, a local-first AI operator console. "
    "Answer clearly, preserve operational context, and avoid pretending to run tools "
    "that are not available in the text-only repair console."
)


@dataclass
class RaphaelTextSession:
    mode: str = "CHAT"
    dry_run: bool = False
    model: str = "gpt-3.5-turbo"
    history: List[Dict[str, str]] = field(default_factory=lambda: [
        {"role": "system", "content": SYSTEM_PROMPT}
    ])

    def route(self, prompt: str) -> str:
        normalized = prompt.strip().lower()

        if normalized in {"/exit", "exit", "quit", "/quit"}:
            return "__EXIT__"
        if normalized == "/history":
            return self.render_history()
        if normalized == "/clear":
            self.history = [{"role": "system", "content": SYSTEM_PROMPT}]
            return "RAPHAEL memory cleared for this text-only session."
        if normalized.startswith("/mode "):
            requested = normalized.split(maxsplit=1)[1].upper()
            if requested not in {"CHAT", "RESEARCH"}:
                return "Supported modes: CHAT, RESEARCH"
            self.mode = requested
            return f"RAPHAEL text console mode set to {self.mode}."

        self.history.append({"role": "user", "content": prompt})

        if self.dry_run:
            response = (
                f"[dry-run:{self.mode}] RAPHAEL received: {prompt}\n"
                "No microphone, TTS, API call, or tool execution was invoked."
            )
        else:
            response = self.ask_model(prompt)

        self.history.append({"role": "assistant", "content": response})
        return response

    def ask_model(self, prompt: str) -> str:
        """Call the legacy OpenAI SDK if available.

        This repo currently pins the old OpenAI SDK, so this method intentionally
        uses the legacy ChatCompletion path. During RAPHAEL extraction this should
        be migrated behind a provider adapter.
        """
        try:
            import openai
        except Exception as exc:
            return f"OpenAI SDK unavailable in this environment: {exc}"

        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            return "OPENAI_API_KEY is not set. Re-run with --dry-run or configure .env."

        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=self.history,
        )
        return response["choices"][0]["message"]["content"]

    def render_history(self) -> str:
        visible = [m for m in self.history if m["role"] != "system"]
        if not visible:
            return "No RAPHAEL text-console history yet."
        return "\n".join(f'{m["role"]}: {m["content"]}' for m in visible)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run RAPHAEL without mic/TTS dependencies.")
    parser.add_argument("--dry-run", action="store_true", help="Do not call OpenAI; echo routed prompts.")
    parser.add_argument("--model", default=os.getenv("RAPHAEL_TEXT_MODEL", "gpt-3.5-turbo"))
    args = parser.parse_args()

    load_dotenv()
    session = RaphaelTextSession(dry_run=args.dry_run, model=args.model)

    print("RAPHAEL text-only console online.")
    print("Type /exit to quit. Use --dry-run for no API calls.\n")

    while True:
        try:
            prompt = input("RAPHAEL> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nRAPHAEL text-only console offline.")
            return 0

        if not prompt:
            continue

        response = session.route(prompt)
        if response == "__EXIT__":
            print("RAPHAEL text-only console offline.")
            return 0
        print(f"\n{response}\n")


if __name__ == "__main__":
    raise SystemExit(main())
