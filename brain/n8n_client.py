"""Brain module — calls Gemini directly with n8n as optional fallback.

Since n8n's Respond to Webhook node has a response-passthrough issue,
this module calls the Gemini API directly from Python. The n8n workflow
is kept as a reference but is bypassed for reliability.
"""

import json
import logging
import re
import sys
import os
from datetime import datetime
from typing import Optional

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GEMINI_API_KEY, N8N_WEBHOOK_URL, N8N_TIMEOUT

logger = logging.getLogger(__name__)

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

SYSTEM_PROMPT = """You are an AI desktop actuator for Microsoft Excel on Windows.
The user speaks in natural language (possibly translated from Hindi/Marathi).
Extract the FINAL intended action and break it down into a JSON object with this EXACT structure:
{
  "plan": "<human-readable description of what you will do>",
  "requires_confirmation": <true if destructive action like delete/clear/format-all, false otherwise>,
  "steps": [
    {"action": "<action_type>", ...params}
  ]
}

Allowed action types:
- "hotkey": {"action": "hotkey", "keys": ["ctrl", "b"]}
- "type_text": {"action": "type_text", "text": "hello"}
- "click": {"action": "click", "target": "element_name"}
- "wait": {"action": "wait", "seconds": 1}

Common Excel shortcuts:
- Bold: Ctrl+B       - Italic: Ctrl+I      - Underline: Ctrl+U
- Undo: Ctrl+Z       - Redo: Ctrl+Y        - Save: Ctrl+S
- Copy: Ctrl+C       - Paste: Ctrl+V       - Cut: Ctrl+X
- Select All: Ctrl+A - Find: Ctrl+F        - Replace: Ctrl+H
- Insert Row: Shift+Space then Ctrl+Shift++
- Delete Row: Shift+Space then Ctrl+-
- New Sheet: Shift+F11
- Format Cells: Ctrl+1
- AutoSum: Alt+=
- Toggle Filter: Ctrl+Shift+L
- Go to cell A1: Ctrl+Home
- Fill Down: Ctrl+D  - Fill Right: Ctrl+R
- Center align: Ctrl+E
- Wrap text: Alt+H then W
- Merge cells: Alt+H then M then M

If the user says "undo" or "go back": {"plan": "Undoing last action", "requires_confirmation": false, "steps": [{"action": "hotkey", "keys": ["ctrl", "z"]}]}
If destructive (delete/clear/overwrite), set requires_confirmation to true.

Return ONLY valid JSON. No markdown, no code fences, no explanation."""

DEFAULT_ERROR_PLAN: dict = {
    "plan": "Sorry, I could not process that command.",
    "requires_confirmation": False,
    "steps": [],
}


class N8NClient:
    """Calls Gemini directly for action planning. N8n webhook used as fallback."""

    def __init__(self, webhook_url: Optional[str] = None) -> None:
        self.webhook_url: str = webhook_url or N8N_WEBHOOK_URL

    def send_command(self, user_text: str, context: str = "") -> dict:
        """Send a user command to Gemini and get back an action plan.

        Tries Gemini directly first (reliable), falls back to n8n webhook.

        Args:
            user_text: Translated English text from STT.
            context: Optional memory context from Mem0.

        Returns:
            Dict with keys: plan, requires_confirmation, steps.
        """
        # Try direct Gemini call first
        result = self._call_gemini_direct(user_text, context)
        if result:
            return result

        # Fallback to n8n webhook
        logger.warning("Gemini direct call failed, trying n8n webhook...")
        return self._call_n8n(user_text, context)

    def _call_gemini_direct(self, user_text: str, context: str) -> Optional[dict]:
        """Call Gemini API directly."""
        prompt = SYSTEM_PROMPT
        if context:
            prompt += f"\n\nUser context/preferences: {context}"
        prompt += f"\n\nUser command: {user_text}"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 1024}
        }

        try:
            logger.info("Calling Gemini directly for: %s", user_text)
            r = requests.post(
                f"{GEMINI_URL}?key={GEMINI_API_KEY}",
                json=payload,
                timeout=20
            )
            r.raise_for_status()

            raw = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            logger.debug("Gemini raw output: %s", raw[:200])

            # Strip markdown fences if present
            cleaned = re.sub(r"```json\n?", "", raw).replace("```", "").strip()

            parsed = json.loads(cleaned)
            plan = {
                "plan": parsed.get("plan", "Executing command..."),
                "requires_confirmation": parsed.get("requires_confirmation", False),
                "steps": parsed.get("steps", []) if isinstance(parsed.get("steps"), list) else [],
            }
            logger.info("Gemini plan: %s (%d steps)", plan["plan"], len(plan["steps"]))
            return plan

        except requests.exceptions.HTTPError as e:
            logger.error("Gemini HTTP error %s: %s", e.response.status_code if e.response else "?", e)
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error("Failed to parse Gemini response: %s", e)
        except Exception as e:
            logger.error("Gemini direct call failed: %s", e)

        return None

    def _call_n8n(self, user_text: str, context: str) -> dict:
        """Fallback: call n8n webhook."""
        payload = {
            "user_text": user_text,
            "context": context,
            "timestamp": datetime.now().isoformat(),
        }
        try:
            r = requests.post(self.webhook_url, json=payload, timeout=N8N_TIMEOUT)
            r.raise_for_status()
            if not r.text.strip():
                logger.error("n8n returned empty response")
                return DEFAULT_ERROR_PLAN
            result = r.json()
            return {
                "plan": result.get("plan", "Executing command..."),
                "requires_confirmation": result.get("requires_confirmation", False),
                "steps": result.get("steps", []),
            }
        except Exception as e:
            logger.error("n8n fallback also failed: %s", e)
            return DEFAULT_ERROR_PLAN

    def health_check(self) -> bool:
        """Check if n8n is reachable."""
        try:
            return requests.get("http://localhost:5678", timeout=5).status_code == 200
        except Exception:
            return False


# ----------------------------------------------------------------------
# Standalone test
# ----------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    )

    client = N8NClient()

    print("=" * 50)
    print("n8n Health Check")
    print("=" * 50)
    print(f"  n8n reachable: {client.health_check()}")

    print("=" * 50)
    print("Sending Test Command")
    print("=" * 50)
    test_command = "Make the title bold in Excel"
    print(f"  Command: {test_command!r}\n")

    plan = client.send_command(test_command)
    print("Returned Action Plan:")
    print(json.dumps(plan, indent=2))
