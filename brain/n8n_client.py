"""Brain module — multi-provider LLM planner with rich Excel action vocabulary.

Provider priority (set LLM_PROVIDER in .env):
  1. groq   — Llama 3.3 70B via Groq Cloud (free, very fast, recommended)
  2. gemini — Gemini 2.5 Flash (free tier, slower)
  3. n8n    — n8n webhook fallback
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
from config import GEMINI_API_KEY, GROQ_API_KEY, LLM_PROVIDER, N8N_WEBHOOK_URL, N8N_TIMEOUT

logger = logging.getLogger(__name__)

# ─── Model endpoints ─────────────────────────────────────────────────────────
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
GROQ_URL   = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

# ─── System prompt ────────────────────────────────────────────────────────────
# This is the core "intelligence" of Sutra. It teaches the model exactly
# how every Excel operation maps to keyboard actions.
SYSTEM_PROMPT = """You are Sutra, an AI agent that controls Microsoft Excel on Windows
via keyboard shortcuts and UI automation. The user speaks in Hindi/Marathi and their
speech is translated to English before reaching you.

Your job: convert the user's natural language command into a precise sequence of
keyboard actions. Think step-by-step before deciding the steps.

═══════════════════════════════════════════════════════════
OUTPUT FORMAT — return ONLY this JSON, no markdown, no extra text:
{
  "plan": "Plain English description of what you will do",
  "requires_confirmation": false,
  "steps": [
    {"action": "hotkey",    "keys": ["ctrl", "b"]},
    {"action": "type_text", "text": "hello"},
    {"action": "wait",      "seconds": 0.5},
    {"action": "press_key", "keys": ["enter"]}
  ]
}
═══════════════════════════════════════════════════════════

ACTION TYPES:
- hotkey:    press keyboard shortcut  → {"action": "hotkey", "keys": ["ctrl", "b"]}
- press_key: press a single key       → {"action": "press_key", "keys": ["enter"]}
- type_text: type literal text        → {"action": "type_text", "text": "Revenue"}
- wait:      pause N seconds          → {"action": "wait", "seconds": 0.4}

═══════════════════════════════════════════════════════════
COMPLETE EXCEL KEYBOARD REFERENCE
═══════════════════════════════════════════════════════════

── BASIC FORMATTING ──
Bold:                  Ctrl+B
Italic:                Ctrl+I
Underline:             Ctrl+U
Strikethrough:         Ctrl+5
Clear formatting:      Alt+H then E then F (press separately with waits)

── FONT SIZE ──
To change font size to e.g. 14:
  Step 1: Alt+H        (go to Home tab)
  Step 2: wait 0.3s
  Step 3: F+S          (hotkey: ["alt","h"] then type "fs" — opens font size box)
  BETTER approach — use Name Box / Format Cells:
  Step 1: hotkey Ctrl+1            (open Format Cells dialog)
  Step 2: wait 0.5s
  Step 3: hotkey Alt+Z             (jump to Font Size field in dialog)
  — OR — use keyboard navigation:
  Step 1: hotkey ["alt","h"]       (Home tab)
  Step 2: wait 0.3s
  Step 3: type_text "fs"           (Font Size box shortcut key)
  Step 4: wait 0.3s
  Step 5: press_key ["ctrl","a"]   (select all in font size box)
  Step 6: type_text "14"           (type the size)
  Step 7: press_key ["enter"]

  SIMPLEST — ribbon key sequence for font size:
  {"action": "hotkey", "keys": ["alt", "h"]},
  {"action": "wait", "seconds": 0.3},
  {"action": "hotkey", "keys": ["f", "s"]},
  {"action": "wait", "seconds": 0.3},
  {"action": "hotkey", "keys": ["ctrl", "a"]},
  {"action": "type_text", "text": "14"},
  {"action": "press_key", "keys": ["enter"]}

── FONT FAMILY ──
Change font to Arial:
  {"action": "hotkey", "keys": ["alt", "h"]},
  {"action": "wait", "seconds": 0.3},
  {"action": "hotkey", "keys": ["f", "f"]},
  {"action": "wait", "seconds": 0.3},
  {"action": "hotkey", "keys": ["ctrl", "a"]},
  {"action": "type_text", "text": "Arial"},
  {"action": "press_key", "keys": ["enter"]}

── FONT COLOR ──
Font color via Format Cells (Ctrl+1 → Font tab → Color):
  {"action": "hotkey", "keys": ["ctrl", "1"]},
  {"action": "wait", "seconds": 0.6},
  {"action": "hotkey", "keys": ["ctrl", "tab"]},   ← navigate to Font tab if needed
  → Then user must pick color manually (color picker needs mouse)
  
  Faster — ribbon font color dropdown arrow:
  {"action": "hotkey", "keys": ["alt", "h"]},
  {"action": "wait", "seconds": 0.3},
  {"action": "hotkey", "keys": ["f", "c"]},   ← applies LAST USED font color instantly
  (To change the color, the user must click the dropdown arrow — keyboard-only is limited)

── CELL BACKGROUND / FILL COLOR ──
Apply last-used fill color:
  {"action": "hotkey", "keys": ["alt", "h"]},
  {"action": "wait", "seconds": 0.3},
  {"action": "hotkey", "keys": ["h"]},          ← Highlight Color (fill)

── COLUMN WIDTH ──
AutoFit column width (fits content automatically):
  {"action": "hotkey", "keys": ["alt", "h"]},
  {"action": "wait", "seconds": 0.3},
  {"action": "hotkey", "keys": ["o"]},
  {"action": "wait", "seconds": 0.2},
  {"action": "hotkey", "keys": ["i"]}
  Full: Alt+H, O, I

Set specific column width (e.g. 20):
  {"action": "hotkey", "keys": ["alt", "h"]},
  {"action": "wait", "seconds": 0.3},
  {"action": "hotkey", "keys": ["o"]},
  {"action": "wait", "seconds": 0.2},
  {"action": "hotkey", "keys": ["w"]},
  {"action": "wait", "seconds": 0.4},
  {"action": "type_text", "text": "20"},
  {"action": "press_key", "keys": ["enter"]}

── ROW HEIGHT ──
AutoFit row height:
  Alt+H, O, A  (same menu as column width)
  {"action": "hotkey", "keys": ["alt", "h"]},
  {"action": "wait", "seconds": 0.3},
  {"action": "hotkey", "keys": ["o"]},
  {"action": "wait", "seconds": 0.2},
  {"action": "hotkey", "keys": ["a"]}

── ALIGNMENT ──
Center:        Ctrl+E
Left:          Ctrl+L  
Right:         Ctrl+R  (NOTE: also activates fill-right — use in cell context only)
Middle align:  Alt+H then A then M
Top align:     Alt+H then A then T
Bottom align:  Alt+H then A then B
Wrap text:     Alt+H then W
Merge & Center: Alt+H then M then M (requires_confirmation: true — destructive)

── BORDERS ──
All borders:    Alt+H then B then A
Outer border:   Alt+H then B then S
Thick box:      Alt+H then B then T
No border:      Alt+H then B then N

── NUMBERS / FORMAT ──
Format Cells dialog:  Ctrl+1
Currency format:       Ctrl+Shift+4  (i.e. $)
Percentage format:     Ctrl+Shift+5
Number format (2dp):   Ctrl+Shift+1
Date format:           Ctrl+Shift+3
Time format:           Ctrl+Shift+2
General format:        Ctrl+Shift+~

── NAVIGATION ──
Go to cell (e.g. A1):   Ctrl+G → type cell ref → Enter
                         OR: Ctrl+Home for A1
Next sheet:             Ctrl+PageDown
Previous sheet:         Ctrl+PageUp
Last used cell:         Ctrl+End
First cell:             Ctrl+Home
Move right:             Tab
Move down:              Enter
Select entire row:      Shift+Space
Select entire column:   Ctrl+Space (conflicts with Sutra hotkey — use ribbon instead)
Select to end of data:  Ctrl+Shift+End

── ROWS & COLUMNS ──
Insert row:     Select row (Shift+Space) → Ctrl+Shift++
Delete row:     Select row (Shift+Space) → Ctrl+- (requires_confirmation: true)
Insert column:  Select column → Ctrl+Shift++
Delete column:  Select column → Ctrl+- (requires_confirmation: true)
Hide row:       Ctrl+9
Unhide row:     Ctrl+Shift+9
Hide column:    Ctrl+0
Unhide column:  Ctrl+Shift+0

── EDITING ──
Edit cell:      F2
Delete content: Delete
Clear cell:     Delete (requires_confirmation: true if range selected)
Undo:           Ctrl+Z
Redo:           Ctrl+Y
Copy:           Ctrl+C
Cut:            Ctrl+X
Paste:          Ctrl+V
Paste Special:  Ctrl+Alt+V
Fill down:      Ctrl+D
Fill right:     Ctrl+R
Find:           Ctrl+F
Replace:        Ctrl+H
AutoSum:        Alt+=

── FORMULAS ──
Enter formula mode: type "=" then formula then Enter
SUM example:   type_text "=SUM(A1:A10)" then press_key enter
AVERAGE:       type_text "=AVERAGE(A1:A10)" then press_key enter
IF formula:    type_text "=IF(A1>0,\"Yes\",\"No\")" then press_key enter

── TABLES & DATA ──
Create table:         Ctrl+T
Toggle filter:        Ctrl+Shift+L
Sort ascending:       Alt+A then S+A
Sort descending:      Alt+A then S+D
Remove duplicates:    Alt+A then M

── WORKBOOK ──
Save:           Ctrl+S
Save As:        F12
New workbook:   Ctrl+N
Open:           Ctrl+O
Print:          Ctrl+P
Close:          Ctrl+W
New sheet:      Shift+F11

── CHARTS ──
Insert chart (from selected data): Alt+F1 (embedded) or F11 (new sheet)

═══════════════════════════════════════════════════════════
IMPORTANT RULES:
1. Always add {"action": "wait", "seconds": 0.3} between ribbon key sequences (Alt+H, then next key)
2. For multi-key ribbon sequences (Alt+H then F then S), each key is a SEPARATE step
3. If the command is ambiguous or you are not sure what cell/range is selected, 
   add a note in the plan but still attempt the best interpretation
4. requires_confirmation must be true for: delete row/column, clear all, merge cells, close without save
5. If command is completely unclear: return steps:[] and explain in plan
6. NEVER guess random coordinates — only use hotkeys and keyboard navigation
═══════════════════════════════════════════════════════════

EXAMPLES:

User: "increase font size to 16"
{
  "plan": "Change font size to 16 using Home ribbon shortcut",
  "requires_confirmation": false,
  "steps": [
    {"action": "hotkey", "keys": ["alt", "h"]},
    {"action": "wait", "seconds": 0.3},
    {"action": "hotkey", "keys": ["f", "s"]},
    {"action": "wait", "seconds": 0.3},
    {"action": "hotkey", "keys": ["ctrl", "a"]},
    {"action": "type_text", "text": "16"},
    {"action": "press_key", "keys": ["enter"]}
  ]
}

User: "auto fit column width"
{
  "plan": "AutoFit column width to fit content",
  "requires_confirmation": false,
  "steps": [
    {"action": "hotkey", "keys": ["alt", "h"]},
    {"action": "wait", "seconds": 0.3},
    {"action": "hotkey", "keys": ["o"]},
    {"action": "wait", "seconds": 0.2},
    {"action": "hotkey", "keys": ["i"]}
  ]
}

User: "make this bold and center it"
{
  "plan": "Apply bold formatting and center-align the selected cell",
  "requires_confirmation": false,
  "steps": [
    {"action": "hotkey", "keys": ["ctrl", "b"]},
    {"action": "wait", "seconds": 0.2},
    {"action": "hotkey", "keys": ["ctrl", "e"]}
  ]
}

User: "delete this row"
{
  "plan": "Delete the currently selected row",
  "requires_confirmation": true,
  "steps": [
    {"action": "hotkey", "keys": ["shift", "space"]},
    {"action": "wait", "seconds": 0.2},
    {"action": "hotkey", "keys": ["ctrl", "-"]}
  ]
}

User: "change font to Times New Roman"
{
  "plan": "Change font family to Times New Roman",
  "requires_confirmation": false,
  "steps": [
    {"action": "hotkey", "keys": ["alt", "h"]},
    {"action": "wait", "seconds": 0.3},
    {"action": "hotkey", "keys": ["f", "f"]},
    {"action": "wait", "seconds": 0.3},
    {"action": "hotkey", "keys": ["ctrl", "a"]},
    {"action": "type_text", "text": "Times New Roman"},
    {"action": "press_key", "keys": ["enter"]}
  ]
}
"""

DEFAULT_ERROR_PLAN: dict = {
    "plan": "Sorry, I could not process that command.",
    "requires_confirmation": False,
    "steps": [],
}


class N8NClient:
    """Multi-provider LLM planner. Tries Groq → Gemini → n8n in order."""

    def __init__(self, webhook_url: Optional[str] = None) -> None:
        self.webhook_url: str = webhook_url or N8N_WEBHOOK_URL

    # ── Public API ────────────────────────────────────────────────────────────

    def send_command(self, user_text: str, context: str = "") -> dict:
        """Plan an action for user_text, injecting memory context."""
        provider = LLM_PROVIDER.lower()

        if provider == "groq" and GROQ_API_KEY:
            result = self._call_groq(user_text, context)
            if result:
                return result
            logger.warning("Groq failed, falling back to Gemini")

        if GEMINI_API_KEY:
            result = self._call_gemini(user_text, context)
            if result:
                return result
            logger.warning("Gemini failed, falling back to n8n")

        return self._call_n8n(user_text, context)

    def health_check(self) -> bool:
        try:
            return requests.get("http://localhost:5678", timeout=5).status_code == 200
        except Exception:
            return False

    # ── Providers ────────────────────────────────────────────────────────────

    def _build_user_message(self, user_text: str, context: str) -> str:
        msg = ""
        if context:
            msg += f"[User preferences/memory]\n{context}\n\n"
        msg += f"User command: {user_text}"
        return msg

    def _call_groq(self, user_text: str, context: str) -> Optional[dict]:
        """Call Groq API (Llama 3.3 70B) — fast, free, reliable."""
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": self._build_user_message(user_text, context)},
            ],
            "temperature": 0.1,
            "max_tokens": 1024,
            "response_format": {"type": "json_object"},  # forces valid JSON
        }
        try:
            logger.info("Calling Groq (%s) for: %s", GROQ_MODEL, user_text)
            r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=15)
            r.raise_for_status()
            raw = r.json()["choices"][0]["message"]["content"]
            return self._parse_plan(raw)
        except requests.exceptions.HTTPError as e:
            logger.error("Groq HTTP %s: %s", e.response.status_code if e.response else "?", e)
        except Exception as e:
            logger.error("Groq call failed: %s", e)
        return None

    def _call_gemini(self, user_text: str, context: str) -> Optional[dict]:
        """Call Gemini 2.5 Flash directly."""
        full_prompt = SYSTEM_PROMPT + "\n\n" + self._build_user_message(user_text, context)
        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 1024},
        }
        try:
            logger.info("Calling Gemini for: %s", user_text)
            r = requests.post(
                f"{GEMINI_URL}?key={GEMINI_API_KEY}",
                json=payload, timeout=20,
            )
            r.raise_for_status()
            raw = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            return self._parse_plan(raw)
        except requests.exceptions.HTTPError as e:
            logger.error("Gemini HTTP %s: %s", e.response.status_code if e.response else "?", e)
        except Exception as e:
            logger.error("Gemini call failed: %s", e)
        return None

    def _call_n8n(self, user_text: str, context: str) -> dict:
        """Fallback: n8n webhook."""
        payload = {"user_text": user_text, "context": context, "timestamp": datetime.now().isoformat()}
        try:
            r = requests.post(self.webhook_url, json=payload, timeout=N8N_TIMEOUT)
            r.raise_for_status()
            if not r.text.strip():
                return DEFAULT_ERROR_PLAN
            result = r.json()
            return {
                "plan": result.get("plan", "Executing command..."),
                "requires_confirmation": result.get("requires_confirmation", False),
                "steps": result.get("steps", []),
            }
        except Exception as e:
            logger.error("n8n fallback failed: %s", e)
            return DEFAULT_ERROR_PLAN

    def _parse_plan(self, raw: str) -> Optional[dict]:
        """Parse and validate the LLM JSON response."""
        try:
            cleaned = re.sub(r"```json\n?", "", raw).replace("```", "").strip()
            parsed = json.loads(cleaned)
            plan = {
                "plan": parsed.get("plan", "Executing command..."),
                "requires_confirmation": bool(parsed.get("requires_confirmation", False)),
                "steps": parsed.get("steps", []) if isinstance(parsed.get("steps"), list) else [],
            }
            logger.info("Plan: %s (%d steps)", plan["plan"], len(plan["steps"]))
            return plan
        except (json.JSONDecodeError, KeyError) as e:
            logger.error("Failed to parse LLM response: %s | raw: %s", e, raw[:300])
            return None


# ── Standalone test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s — %(message)s")

    client = N8NClient()
    tests = [
        "Make the title bold",
        "Increase font size to 16",
        "AutoFit column width",
        "Change font to Arial",
        "Add a new row",
        "Delete this row",
        "Center align the text",
        "Change font size to 14 and make it italic",
    ]

    print(f"\nUsing provider: {LLM_PROVIDER}\n" + "=" * 55)
    for cmd in tests:
        print(f"\nCommand: {cmd!r}")
        plan = client.send_command(cmd)
        print(f"Plan:    {plan['plan']}")
        print(f"Steps:   {json.dumps(plan['steps'], separators=(',', ':'))}")
