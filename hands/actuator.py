"""PyAutoGUI-based desktop action executor for Sutra.

Processes JSON action plans and translates them into real mouse/keyboard
interactions using PyAutoGUI.  Supports click, type_text, hotkey, wait,
and template-matching lookups via on-screen image search.
"""

import logging
import time
import random
import sys
import os
from typing import List, Dict, Any, Optional, Tuple

import pyautogui
import pyperclip

# ---------------------------------------------------------------------------
# Project imports
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MOUSE_DURATION, TYPING_INTERVAL, ACTION_DELAY_MIN, ACTION_DELAY_MAX

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Safety configuration
# ---------------------------------------------------------------------------
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05


class Actuator:
    """Executes UI action plans using PyAutoGUI.

    Supported actions
    -----------------
    * **click** / **double_click** — mouse click at coordinates or template target.
    * **type_text** — type a string (ASCII via keyboard, Unicode via clipboard).
    * **hotkey** / **press_key** — press a keyboard shortcut.
    * **wait** — pause execution for a given duration.
    * **undo** — convenience alias for Ctrl+Z.

    Human-like random delays and smooth mouse movements are added
    automatically between steps.
    """

    ASSETS_DIR: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets"
    )

    def __init__(self) -> None:
        logger.info("Actuator initialized. FAILSAFE=True (move mouse to corner to abort)")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _human_delay(self) -> None:
        """Add a random human-like delay between actions."""
        delay = random.uniform(ACTION_DELAY_MIN, ACTION_DELAY_MAX)
        time.sleep(delay)

    def _find_on_screen(
        self, target: str, confidence: float = 0.8
    ) -> Optional[Tuple[int, int]]:
        """Find a UI element on screen using template matching.

        Looks for an image file in the assets directory matching *target*.
        Returns ``(x, y)`` centre coordinates or ``None`` if not found.
        """
        image_path = os.path.join(self.ASSETS_DIR, f"{target}.png")
        if not os.path.exists(image_path):
            logger.warning(f"Template image not found: {image_path}")
            return None

        try:
            location = pyautogui.locateCenterOnScreen(
                image_path, confidence=confidence
            )
            if location:
                logger.info(f"Found '{target}' at ({location.x}, {location.y})")
                return (location.x, location.y)
            else:
                logger.warning(f"Could not find '{target}' on screen")
                return None
        except Exception as e:
            logger.error(f"Screen search error: {e}")
            return None

    # ------------------------------------------------------------------
    # Action executors
    # ------------------------------------------------------------------

    def execute_click(self, step: Dict[str, Any]) -> bool:
        """Execute a click action.

        If *target* is a string, tries to find it via template matching.
        If *x* and *y* are provided, clicks at those coordinates.
        Falls back to clicking at the current cursor position.
        """
        x: Optional[int] = None
        y: Optional[int] = None

        if "x" in step and "y" in step:
            x, y = step["x"], step["y"]
        elif "target" in step:
            coords = self._find_on_screen(step["target"])
            if coords:
                x, y = coords
            else:
                logger.error(f"Cannot find click target: {step['target']}")
                return False
        else:
            # Click at current position
            pyautogui.click()
            return True

        duration = step.get("duration", MOUSE_DURATION)
        pyautogui.moveTo(x, y, duration=duration)

        clicks = step.get("clicks", 1)
        if clicks == 2:
            pyautogui.doubleClick()
        else:
            pyautogui.click(clicks=clicks)

        logger.info(f"Clicked at ({x}, {y}), clicks={clicks}")
        return True

    def execute_type_text(self, step: Dict[str, Any]) -> bool:
        """Type text with human-like speed.

        Uses the clipboard (Ctrl+V) for Unicode text (Hindi, emoji, etc.)
        and ``pyautogui.write`` for plain ASCII.
        """
        text: str = step.get("text", "")
        if not text:
            logger.warning("Empty text in type_text action")
            return False

        # Check if text is ASCII-only
        try:
            text.encode("ascii")
            is_ascii = True
        except UnicodeEncodeError:
            is_ascii = False

        if is_ascii:
            interval = step.get("interval", TYPING_INTERVAL)
            pyautogui.write(text, interval=interval)
        else:
            # Use clipboard for Unicode text
            pyperclip.copy(text)
            pyautogui.hotkey("ctrl", "v")

        display = f"'{text[:50]}...'" if len(text) > 50 else f"'{text}'"
        logger.info(f"Typed: {display}")
        return True

    def execute_hotkey(self, step: Dict[str, Any]) -> bool:
        """Press a keyboard shortcut.
        
        Handles both true simultaneous hotkeys (ctrl+b) and sequential
        ribbon key presses (alt+h then f then s — each pressed separately).
        Keys with 1 character that are NOT modifier keys are pressed sequentially.
        """
        keys: List[str] = step.get("keys", [])
        if not keys:
            logger.warning("No keys specified for hotkey action")
            return False

        MODIFIERS = {"ctrl", "alt", "shift", "win", "command", "option"}

        # If all keys are single chars AND none are modifiers → sequential press
        # e.g. ["f", "s"] from Alt+H ribbon navigation
        all_single = all(len(k) == 1 for k in keys)
        has_modifier = any(k.lower() in MODIFIERS for k in keys)

        if all_single and not has_modifier and len(keys) > 1:
            # Sequential key presses (ribbon shortcut keys)
            for k in keys:
                pyautogui.press(k)
                time.sleep(0.05)
            logger.info(f"Sequential keys: {' → '.join(keys)}")
        else:
            # True simultaneous hotkey
            pyautogui.hotkey(*keys)
            logger.info(f"Hotkey: {'+'.join(keys)}")
        return True

    def execute_wait(self, step: Dict[str, Any]) -> bool:
        """Wait for a specified duration in seconds."""
        seconds: float = step.get("seconds", 1.0)
        logger.info(f"Waiting {seconds}s...")
        time.sleep(seconds)
        return True

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def execute_step(self, step: Dict[str, Any]) -> bool:
        """Execute a single action step from a plan.

        Raises ``pyautogui.FailSafeException`` if the mouse is moved to a
        screen corner (abort mechanism).
        """
        action = step.get("action", "").lower()

        handlers: Dict[str, Any] = {
            "click": self.execute_click,
            "double_click": lambda s: self.execute_click({**s, "clicks": 2}),
            "type_text": self.execute_type_text,
            "hotkey": self.execute_hotkey,
            "press_key": self.execute_hotkey,  # alias
            "wait": self.execute_wait,
            "undo": lambda s: self.execute_hotkey({"keys": ["ctrl", "z"]}),
        }

        handler = handlers.get(action)
        if not handler:
            logger.error(f"Unknown action: {action}")
            return False

        try:
            return handler(step)
        except pyautogui.FailSafeException:
            logger.critical("FAILSAFE TRIGGERED! Mouse moved to corner. Aborting.")
            raise
        except Exception as e:
            logger.error(f"Action '{action}' failed: {e}")
            return False

    def execute_plan(self, steps: List[Dict[str, Any]]) -> bool:
        """Execute a complete action plan (list of step dicts).

        Returns ``True`` if every step succeeded, ``False`` if any step
        failed.  A ``FailSafeException`` is re-raised immediately.
        """
        if not steps:
            logger.warning("Empty action plan")
            return True

        logger.info(f"Executing plan with {len(steps)} steps...")

        for i, step in enumerate(steps):
            logger.info(f"Step {i+1}/{len(steps)}: {step.get('action', 'unknown')}")

            success = self.execute_step(step)
            if not success:
                logger.error(f"Step {i+1} failed: {step}")
                return False

            # Human-like delay between steps (skip after the last step or waits)
            if i < len(steps) - 1 and step.get("action") != "wait":
                self._human_delay()

        logger.info("Plan executed successfully!")
        return True


# -----------------------------------------------------------------------
# Standalone test
# -----------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    actuator = Actuator()

    # 1) Print screen size
    width, height = pyautogui.size()
    logger.info(f"Screen size: {width}x{height}")

    # 2) Quick test plan — open Notepad and type a greeting
    test_plan: List[Dict[str, Any]] = [
        {"action": "hotkey", "keys": ["win", "r"]},
        {"action": "wait", "seconds": 0.5},
        {"action": "type_text", "text": "notepad"},
        {"action": "hotkey", "keys": ["enter"]},
        {"action": "wait", "seconds": 1.0},
        {"action": "type_text", "text": "Hello from Sutra!"},
    ]

    logger.info("Running test plan: open Notepad and type greeting...")
    try:
        result = actuator.execute_plan(test_plan)
        logger.info(f"Test plan result: {'SUCCESS' if result else 'FAILED'}")
    except pyautogui.FailSafeException:
        logger.critical("Test aborted by fail-safe.")
