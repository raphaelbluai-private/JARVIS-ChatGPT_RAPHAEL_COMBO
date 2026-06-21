# RAPHAEL Extraction Architecture

This document defines the extraction target after the repaired baseline proves the useful mechanics.

## Extraction principle

Do not move the full legacy JARVIS codebase into RAPHAEL.

Extract only reusable capabilities:

1. wake/input activation;
2. audio recording;
3. speech-to-text transcription;
4. text command loop;
5. answer generation provider adapter;
6. speech output adapter;
7. project memory persistence;
8. search/retrieval;
9. research workspace orchestration.

## Proposed package layout

```text
raphael/
  __init__.py

  core/
    __init__.py
    intent_router.py
    policy_engine.py
    audit_logger.py
    tool_registry.py
    runtime.py

  voice/
    __init__.py
    wake_word.py
    recorder.py
    transcriber.py
    speaker.py
    console.py

  memory/
    __init__.py
    conversation_store.py
    project_store.py
    retrieval.py

  research/
    __init__.py
    workspace.py
    paper_search.py
    document_index.py

  providers/
    __init__.py
    openai_provider.py
    local_llm_provider.py
    tts_provider.py

  tools/
    __init__.py
    local_files.py
    github.py
    repo_runner.py
    document_builder.py
    property_analysis.py

  config/
    permissions.yaml
    profiles.yaml
    env.example
```

## Runtime flow

```text
Input Channel
  -> Transcriber or Text Console
  -> Intent Router
  -> Policy Engine
  -> Tool Registry
  -> Memory / Provider / Tool Execution
  -> Audit Logger
  -> Speaker or Text Output
```

## Permission levels

### Low risk

- answer a question
- summarize saved memory
- save a note
- read a user-approved local file

### Medium risk

- write a local file
- run a local repo command
- create a draft document
- query connected/private data

### High risk

- delete files
- push GitHub commits
- send messages/emails
- spend money
- sign or submit documents
- change production infrastructure

High-risk commands must require explicit approval.

## First extraction target

The first RAPHAEL-native module should be the text console because it removes the heavy audio stack from the first validation cycle.

Target:

```text
raphael/voice/console.py
raphael/core/intent_router.py
raphael/core/audit_logger.py
```

Once that works, migrate:

```text
Assistant/RaphaelAssistant.py -> raphael/voice/runtime.py
raphael_text_console.py -> raphael/voice/console.py
```

## Validation gates

Before merging into RAPHAEL-native architecture:

1. text console starts in dry-run mode;
2. command routing supports CHAT and RESEARCH;
3. audit log records command input and selected route;
4. permission engine blocks high-risk actions by default;
5. voice mode can be disabled without breaking text mode;
6. tests do not require microphone, GPU, PyAudio, pygame, IBM, ElevenLabs, or OpenAI keys.
