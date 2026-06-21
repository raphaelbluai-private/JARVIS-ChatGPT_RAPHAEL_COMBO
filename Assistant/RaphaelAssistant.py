"""RAPHAEL repair wrapper.

This module keeps the legacy VirtualAssistant class intact while overriding the
broken paths that block the repair baseline. It is intentionally thin: once the
repair baseline is proven, these methods should be extracted into the
RAPHAEL-native architecture under a dedicated voice/core package.
"""

import os
import time
import uuid

import pygame

from Assistant.VirtualAssistant import VirtualAssistant
from Assistant.research_mode import ResearchAssistant
from Assistant.semantic_scholar.agent_tools import Document, llama_query_engine, load_workspace, readPDF


class RaphaelResearchAssistant(ResearchAssistant):
    """Repair-safe research assistant for the RAPHAEL baseline."""

    def boot_workspace(self, workspace):
        """Boot an existing workspace only when a concrete path is available."""
        if workspace is None:
            return None
        return super().boot_workspace(workspace)

    def load_pdf_to_pinecone(self, paths):
        """Load one or more PDF paths into the active query index.

        Legacy bug fixed:
        - The original implementation converted a string into a list, then raised
          an exception whenever the input was a list. This implementation accepts
          both a single path and a list/tuple of paths.
        """
        if isinstance(paths, str):
            paths = [paths]
        elif not isinstance(paths, (list, tuple)):
            raise TypeError("paths must be a PDF path string or a list/tuple of PDF paths")

        inserted = 0
        for path in paths:
            if not isinstance(path, str) or not path.lower().endswith(".pdf"):
                continue

            content = readPDF(path)
            doc = Document(text=content, doc_id=uuid.uuid4().hex)
            self.docs.append(doc)

            if self.Index is None:
                self.query_engine, self.Index = llama_query_engine(
                    self.docs,
                    pinecone_index_name=self.index_name,
                )
            else:
                self.Index.insert(document=doc)

            inserted += 1

        if inserted == 0:
            return "no PDF files were loaded"

        self.query_engine = self.Index.as_query_engine()
        return f"loaded {inserted} PDF file(s) into the RAPHAEL research workspace"


class RaphaelAssistant(VirtualAssistant):
    """RAPHAEL-branded baseline assistant.

    This class repairs the broken legacy behavior while preserving the working
    voice/transcription/memory mechanics for extraction.
    """

    assistant_name = "RAPHAEL"

    def use_tools(self, prompt, debug=VirtualAssistant.DEBUG):
        """Route tool use correctly in CHAT or RESEARCH mode.

        Legacy bug fixed:
        - The original code checked for self.MODE == "CAHT", which meant the
          chat-mode tool path was unreachable. This override uses "CHAT".
        """
        if debug:
            print(" -use RAPHAEL tools ")

        if self.MODE == "CHAT":
            from Assistant.Agents import generateReactAgent

            action_manager = generateReactAgent(self, k=1)
            return action_manager.run(input=prompt)

        if self.MODE == "RESEARCH":
            return self.ResearchAssistant.agent.run(input=prompt)

        return f"error: unsupported RAPHAEL mode {self.MODE}"

    def init_research_mode(self, workspace=None):
        """Initialize research mode with the repaired research assistant."""
        if workspace is None and "workspaces" in os.listdir(os.getcwd()):
            search_dir = os.path.join("workspaces")
            subdirs = os.listdir(search_dir)
            subdirs.sort(key=lambda fn: os.path.getmtime(os.path.join(search_dir, fn)))
            subdirs.reverse()
            for subd in subdirs:
                folder_path = os.path.join("workspaces", subd)
                if os.path.isdir(folder_path):
                    self.say("loading the last created RAPHAEL workspace", VoiceIdx="en", elevenlabs=True)
                    workspace = os.path.abspath(folder_path)
                    break

        self.play("Sci-Fi-UI.mp3", loop=True)
        self.MODE = "RESEARCH"
        self.ResearchAssistant = RaphaelResearchAssistant(
            current_conversation=self.current_conversation,
            index_name="paperquestioning",
            workspace=workspace,
        )
        pygame.mixer.stop()
