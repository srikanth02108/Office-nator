"""Stateful memory manager for Sutra.

Stores user preferences and command history locally in a JSON file.
Uses the LLM to extract facts from conversations and retrieve relevant
context — no OpenAI or cloud dependency required.

Storage: memory/sutra_memory.json (persists between sessions)
"""

import json
import logging
import os
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GEMINI_API_KEY, GROQ_API_KEY, LLM_PROVIDER

logger = logging.getLogger(__name__)

MEMORY_FILE = Path(__file__).parent / "sutra_memory.json"

GROQ_URL   = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"


def _call_llm(prompt: str, max_tokens: int = 256) -> Optional[str]:
    """Call the configured LLM to extract/retrieve memory facts."""
    try:
        if LLM_PROVIDER.lower() == "groq" and GROQ_API_KEY:
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0,
                "max_tokens": max_tokens,
            }
            r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=10)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()

        elif GEMINI_API_KEY:
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.0, "maxOutputTokens": max_tokens},
            }
            r = requests.post(f"{GEMINI_URL}?key={GEMINI_API_KEY}", json=payload, timeout=15)
            r.raise_for_status()
            return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

    except Exception as e:
        logger.warning("Memory LLM call failed: %s", e)
    return None


class MemoryManager:
    """Persistent local memory for user preferences and command history.

    Memories are stored as a list of fact strings in a local JSON file.
    The LLM is used to:
    1. Extract new facts from conversations (save_from_conversation)
    2. Retrieve relevant context for a given query (get_context)
    """

    def __init__(self) -> None:
        self._memories: List[dict] = []
        self._load()
        logger.info("MemoryManager loaded %d memories from %s", len(self._memories), MEMORY_FILE)

    # ── Persistence ──────────────────────────────────────────────────────────

    def _load(self) -> None:
        if MEMORY_FILE.exists():
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._memories = data.get("memories", [])
            except Exception as e:
                logger.warning("Could not load memory file: %s", e)
                self._memories = []

    def _save(self) -> None:
        try:
            MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump({"memories": self._memories, "updated": datetime.now().isoformat()}, f, indent=2)
        except Exception as e:
            logger.warning("Could not save memory file: %s", e)

    # ── Public API ────────────────────────────────────────────────────────────

    def get_context(self, user_text: str, user_id: str = "default") -> str:
        """Return relevant memory facts for the current command as a string."""
        if not self._memories:
            return ""

        # Simple keyword search first (fast, no LLM needed)
        facts = [m["fact"] for m in self._memories if m.get("user_id", "default") == user_id]
        if not facts:
            return ""

        # Score facts by keyword overlap with user_text
        query_words = set(user_text.lower().split())
        scored = []
        for fact in facts:
            fact_words = set(fact.lower().split())
            overlap = len(query_words & fact_words)
            scored.append((overlap, fact))

        # Return top 3 relevant facts (those with any overlap, plus general prefs)
        scored.sort(reverse=True)
        relevant = [f for score, f in scored if score > 0][:3]

        # Always include high-priority preferences (font, formatting preferences)
        pref_keywords = ["prefer", "always", "default", "use", "font", "color", "size"]
        for score, fact in scored:
            if any(kw in fact.lower() for kw in pref_keywords) and fact not in relevant:
                relevant.append(fact)
                if len(relevant) >= 5:
                    break

        if not relevant:
            return ""

        context = "User preferences and history:\n" + "\n".join(f"- {f}" for f in relevant[:5])
        logger.debug("Memory context: %s", context)
        return context

    def save_from_conversation(self, user_text: str, plan: str, user_id: str = "default") -> None:
        """Use LLM to extract memorable facts from a command + outcome pair."""
        prompt = f"""Extract any user preferences or habits worth remembering from this interaction.
Return a JSON array of short fact strings, or [] if nothing notable.
Only extract PREFERENCES (font choices, formatting habits, working style), not one-time actions.

User said: "{user_text}"
Action taken: "{plan}"

Examples of good facts:
- "User prefers Arial font"
- "User often uses bold headers"
- "User works in Hindi"

Return ONLY a JSON array like: ["fact 1", "fact 2"] or []"""

        result = _call_llm(prompt, max_tokens=150)
        if not result:
            return

        try:
            # Extract JSON array from response
            match = re.search(r"\[.*?\]", result, re.DOTALL)
            if not match:
                return
            facts = json.loads(match.group())
            if not isinstance(facts, list):
                return

            for fact in facts:
                if isinstance(fact, str) and fact.strip():
                    # Avoid duplicates
                    existing = [m["fact"] for m in self._memories]
                    if fact not in existing:
                        self._memories.append({
                            "fact": fact.strip(),
                            "user_id": user_id,
                            "created": datetime.now().isoformat(),
                            "source": f"command: {user_text[:50]}",
                        })
                        logger.info("Memory saved: %s", fact)

            if facts:
                self._save()

        except (json.JSONDecodeError, ValueError) as e:
            logger.debug("Memory extraction parse error: %s", e)

    def save_preference(self, text: str, user_id: str = "default") -> None:
        """Directly save a preference string."""
        existing = [m["fact"] for m in self._memories]
        if text not in existing:
            self._memories.append({
                "fact": text,
                "user_id": user_id,
                "created": datetime.now().isoformat(),
                "source": "explicit",
            })
            self._save()
            logger.info("Preference saved: %s", text)

    def get_all_memories(self, user_id: str = "default") -> List[str]:
        """Return all memory facts for display in the UI."""
        return [
            m["fact"] for m in self._memories
            if m.get("user_id", "default") == user_id
        ]

    def clear_memories(self, user_id: str = "default") -> None:
        """Clear all memories for a user."""
        self._memories = [m for m in self._memories if m.get("user_id") != user_id]
        self._save()
        logger.info("Cleared all memories for user: %s", user_id)

    def memory_count(self, user_id: str = "default") -> int:
        return sum(1 for m in self._memories if m.get("user_id", "default") == user_id)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s — %(message)s")

    mm = MemoryManager()
    print(f"Current memories: {mm.get_all_memories()}")

    mm.save_preference("User prefers Arial font size 12")
    mm.save_preference("User always uses bold for headers")
    mm.save_preference("User works primarily in Hindi")

    print(f"\nAfter saving preferences: {mm.get_all_memories()}")
    print(f"\nContext for 'make this bold': {mm.get_context('make this bold')}")
    print(f"Context for 'change font':    {mm.get_context('change font')}")

    mm.save_from_conversation("make the header bold", "Applied bold formatting to selected cell")
    print(f"\nAfter conversation save: {mm.get_all_memories()}")
