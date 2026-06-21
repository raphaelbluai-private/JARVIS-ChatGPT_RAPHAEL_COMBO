# RAPHAEL Repair and Extraction Plan

## Branch

`repair/raphael-baseline-v0.1`

## Purpose

This branch repairs the existing JARVIS-ChatGPT prototype only far enough to prove the usable mechanics, then prepares the reusable pieces for a RAPHAEL-native voice console.

The target is not to preserve JARVIS as the product. The target is to extract the useful voice, transcription, response, memory, and research mechanisms into RAPHAEL.

## Required identity change

RAPHAEL replaces JARVIS as the operating identity.

### Wake/input sequence

Primary wake keyword:

```text
raphael
```

Configurable environment variable:

```text
RAPHAEL_WAKE_KEYWORDS=raphael
RAPHAEL_ASSISTANT_NAME=RAPHAEL
```

Important implementation note: Picovoice Porcupine may require a custom keyword file for non-built-in wake words. If Porcupine cannot initialize the RAPHAEL keyword, the repaired baseline must fall back to passive speech recognition instead of crashing.

## Phase 1: Repair baseline

Goal: prove the current repo can run end-to-end before extraction.

Required repairs:

1. Replace JARVIS startup identity with RAPHAEL.
2. Replace default wake/input keyword with `raphael`.
3. Restore prompt routing by using `analyze_prompt(prompt)` instead of hardcoded `flag = '-1'`.
4. Fix the `CAHT` typo in `Assistant/VirtualAssistant.py` so chat-mode tools can run.
5. Fix research PDF list handling in `Assistant/research_mode.py`.
6. Add a text-only test harness so the assistant brain can be tested without microphone, PyAudio, Porcupine, or TTS.
7. Document remaining fragile dependencies.

## Phase 2: Extract reusable modules

Keep:

- wake-word / passive listener
- recorder
- Whisper transcription
- speaker/TTS wrapper
- saved chat memory concept
- local search concept
- research workspace concept

Rewrite or remove:

- old LangChain agent routing
- hardcoded JARVIS branding
- brittle autonomous tool execution
- IBM Watson as a required dependency
- ElevenLabs as a required dependency
- old OpenAI SDK usage
- fragile research PDF pipeline
- oversized dependency stack

## Phase 3: Compile into RAPHAEL

Target architecture:

```text
Voice Input
  -> Transcription
  -> RAPHAEL Intent Router
  -> Permission Gate
  -> Tool Execution
  -> Audit Log
  -> Spoken/Text Response
```

Suggested structure:

```text
RAPHAEL/
  core/
    intent_router.py
    policy_engine.py
    memory_engine.py
    audit_logger.py
    tool_registry.py

  voice/
    wake_word.py
    recorder.py
    transcriber.py
    speaker.py

  tools/
    local_files.py
    github.py
    research.py
    repo_runner.py
    document_builder.py
    property_analysis.py

  memory/
    conversations/
    projects/
    decisions/
    embeddings/

  config/
    permissions.yaml
    profiles.yaml
    env.example
```

## First completed change

`openai_api_chatbot.py` has been updated to:

- instantiate `raphael` instead of `jarvis` at runtime;
- use `RAPHAEL` as the assistant identity;
- default wake keyword to `raphael`;
- support `RAPHAEL_WAKE_KEYWORDS` and `RAPHAEL_ASSISTANT_NAME` environment variables;
- fall back from Porcupine to passive listening if a custom RAPHAEL wake word is not supported;
- restore prompt routing with `raphael.analyze_prompt(prompt)`.

## Next changes to apply

1. Fix `Assistant/VirtualAssistant.py`:

```python
if self.MODE == "CAHT":
```

to:

```python
if self.MODE == "CHAT":
```

2. Fix `Assistant/research_mode.py` list handling in `load_pdf_to_pinecone`.

3. Add `raphael_text_console.py` for text-only test mode.

4. Add smoke tests for startup, prompt routing, chat response, sleep flow, and saved chat search.
