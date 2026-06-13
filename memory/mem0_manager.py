"""Stubbed memory manager for user preference storage.

Mem0 integration is planned for a future iteration. Currently provides
a no-op interface so the rest of Sutra can call memory methods without
errors.
"""

import logging
from typing import List

logger = logging.getLogger(__name__)


class MemoryManager:
    """Stubbed memory manager. Mem0 integration planned for future.

    Currently returns empty context for all queries.
    """

    def __init__(self) -> None:
        """Initialize the (stubbed) memory manager."""
        logger.info("MemoryManager initialized (stubbed — no Mem0)")
        self._memories: dict[str, list[str]] = {}  # Simple dict for basic key-value storage

    def get_context(self, user_text: str, user_id: str = "default") -> str:
        """Search for relevant context based on the user's text.

        Args:
            user_text: The current user utterance to find context for.
            user_id: Identifier for the user.

        Returns:
            Relevant context string. Currently always returns empty string.
        """
        return ""

    def save_preference(self, text: str, user_id: str = "default") -> None:
        """Save a user preference.

        Args:
            text: The preference text to store.
            user_id: Identifier for the user.
        """
        logger.info(f"[STUB] Would save preference: {text}")

    def get_all_memories(self, user_id: str = "default") -> List[str]:
        """Get all stored memories for a user.

        Args:
            user_id: Identifier for the user.

        Returns:
            List of memory strings. Currently always returns empty list.
        """
        return []


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    )

    mm = MemoryManager()

    # Test get_context
    ctx = mm.get_context("open Chrome")
    logger.info(f"Context for 'open Chrome': '{ctx}' (expected empty)")

    # Test save_preference
    mm.save_preference("I prefer dark mode")

    # Test get_all_memories
    memories = mm.get_all_memories()
    logger.info(f"All memories: {memories} (expected [])")

    logger.info("MemoryManager stub test complete.")
