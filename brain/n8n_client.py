"""Brain module — multi-provider LLM planner with full Excel ribbon coverage.

Provider cascade (runtime-switchable via /config endpoint):
  groq    → Llama 3.3 70B  (free 14,400 req/day, ~1s latency)
  gemini  → Gemini 2.5 Flash (free tier)
  openai  → GPT-4o-mini (paid, most capable)
  custom  → Any OpenAI-compatible endpoint (Ollama, Together, Mistral, etc.)

Usage tracking: per-session token counts broadcast to frontend.
"""

import json
import logging
import re
import sys
import os
import threading
from datetime import datetime, date
from typing import Optional

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GEMINI_API_KEY, GROQ_API_KEY, OPENAI_API_KEY, LLM_PROVIDER, N8N_WEBHOOK_URL, N8N_TIMEOUT

logger = logging.getLogger(__name__)

# ─── Provider endpoints ──────────────────────────────────────────────────────
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
GROQ_URL   = "https://api.groq.com/openai/v1/chat/completions"
OPENAI_URL = "https://api.openai.com/v1/chat/completions"

# Free tier daily limits (approximate)
PROVIDER_LIMITS = {
    "groq":   {"daily_requests": 14400, "daily_tokens": 500000,  "rpm": 30},
    "gemini": {"daily_requests": 1500,  "daily_tokens": 1000000, "rpm": 15},
    "openai": {"daily_requests": 999999,"daily_tokens": 999999,  "rpm": 500},
    "custom": {"daily_requests": 999999,"daily_tokens": 999999,  "rpm": 999},
}

# ─── Usage tracker ────────────────────────────────────────────────────────────
class UsageTracker:
    """Tracks token and request usage per provider per day."""
    def __init__(self):
        self._lock = threading.Lock()
        self._data: dict = {}   # {provider: {date: {requests, tokens_in, tokens_out}}}

    def _today(self) -> str:
        return date.today().isoformat()

    def record(self, provider: str, tokens_in: int, tokens_out: int):
        with self._lock:
            today = self._today()
            if provider not in self._data:
                self._data[provider] = {}
            if today not in self._data[provider]:
                self._data[provider][today] = {"requests": 0, "tokens_in": 0, "tokens_out": 0}
            self._data[provider][today]["requests"] += 1
            self._data[provider][today]["tokens_in"] += tokens_in
            self._data[provider][today]["tokens_out"] += tokens_out

    def get_today(self, provider: str) -> dict:
        with self._lock:
            today = self._today()
            base = {"requests": 0, "tokens_in": 0, "tokens_out": 0}
            return self._data.get(provider, {}).get(today, base).copy()

    def get_usage_pct(self, provider: str) -> float:
        """Return usage as 0-100 percentage of daily request limit."""
        today = self.get_today(provider)
        limit = PROVIDER_LIMITS.get(provider, {}).get("daily_requests", 1)
        return min(100.0, round(today["requests"] / limit * 100, 1))

    def get_all_stats(self) -> dict:
        result = {}
        for provider in ["groq", "gemini", "openai", "custom"]:
            today = self.get_today(provider)
            limits = PROVIDER_LIMITS.get(provider, {})
            result[provider] = {
                **today,
                "daily_request_limit": limits.get("daily_requests", 0),
                "usage_pct": self.get_usage_pct(provider),
            }
        return result

usage = UsageTracker()

# ─── Runtime config (switchable without restart) ─────────────────────────────
class ProviderConfig:
    def __init__(self):
        self._lock = threading.Lock()
        self.provider: str = LLM_PROVIDER
        self.keys: dict = {
            "groq":   GROQ_API_KEY,
            "gemini": GEMINI_API_KEY,
            "openai": OPENAI_API_KEY,
            "custom": "",
        }
        self.custom_url:   str = ""
        self.custom_model: str = ""

    def set_provider(self, provider: str):
        with self._lock:
            self.provider = provider.lower()
        logger.info("Provider switched to: %s", self.provider)

    def set_key(self, provider: str, key: str):
        with self._lock:
            self.keys[provider.lower()] = key
        logger.info("API key updated for provider: %s", provider)

    def set_custom(self, url: str, model: str, key: str = ""):
        with self._lock:
            self.custom_url = url
            self.custom_model = model
            self.keys["custom"] = key
        logger.info("Custom provider set: %s / %s", url, model)

    def get(self) -> dict:
        with self._lock:
            return {
                "provider": self.provider,
                "custom_url": self.custom_url,
                "custom_model": self.custom_model,
                "keys_set": {k: bool(v) for k, v in self.keys.items()},
            }

provider_config = ProviderConfig()

# ─── System prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are Sutra, a precision AI agent that controls Microsoft Excel on Windows
using keyboard shortcuts. User speech is translated from Hindi/Marathi to English.

CRITICAL OUTPUT RULE: Return ONLY a JSON object. No markdown. No explanation. No code fences.

JSON FORMAT:
{
  "plan": "Short description of what you will do",
  "requires_confirmation": false,
  "steps": [
    {"action": "hotkey", "keys": ["ctrl", "b"]},
    {"action": "ribbon", "keys": ["h", "f", "s"]},
    {"action": "type_text", "text": "hello"},
    {"action": "press_key", "key": "enter"},
    {"action": "wait", "seconds": 0.4}
  ]
}

ACTION TYPES — use exactly these:
• hotkey      → simultaneous key press: {"action":"hotkey","keys":["ctrl","b"]}
• ribbon      → sequential ribbon key presses after Alt is already pressed: {"action":"ribbon","keys":["h","f","s"]}
  (ribbon presses keys one-by-one with 80ms gap — for Excel ribbon navigation)
• press_key   → single key press: {"action":"press_key","key":"enter"}
• type_text   → type text string: {"action":"type_text","text":"Arial"}
• wait        → pause: {"action":"wait","seconds":0.4}

═══════════════ EXCEL COMPLETE KEYBOARD MAP ═══════════════

▌HOME TAB (Alt+H prefix, then ribbon keys)
Bold              → hotkey ctrl+b
Italic            → hotkey ctrl+i
Underline         → hotkey ctrl+u
Strikethrough     → hotkey ctrl+5
Font size         → hotkey alt+h, wait 0.3, ribbon ["f","s"], wait 0.3, hotkey ctrl+a, type_text "14", press_key enter
Font family       → hotkey alt+h, wait 0.3, ribbon ["f","f"], wait 0.3, hotkey ctrl+a, type_text "Arial", press_key enter
Font color        → hotkey alt+h, wait 0.3, ribbon ["f","c"]   (applies last-used color)
Fill/bg color     → hotkey alt+h, wait 0.3, ribbon ["h"]       (applies last-used fill)
Clear formats     → hotkey alt+h, wait 0.3, ribbon ["e","f"]
Clear all         → hotkey alt+h, wait 0.3, ribbon ["e","a"]   (requires_confirmation)
Clear contents    → press_key delete

Align left        → hotkey ctrl+l
Align center      → hotkey ctrl+e
Align right       → hotkey alt+h, wait 0.3, ribbon ["a","r"]   (NOT ctrl+r — fills right)
Align top         → hotkey alt+h, wait 0.3, ribbon ["a","t"]
Align middle      → hotkey alt+h, wait 0.3, ribbon ["a","m"]
Align bottom      → hotkey alt+h, wait 0.3, ribbon ["a","b"]
Wrap text         → hotkey alt+h, wait 0.3, ribbon ["w"]
Merge & Center    → hotkey alt+h, wait 0.3, ribbon ["m","c"]   (requires_confirmation)
Merge cells only  → hotkey alt+h, wait 0.3, ribbon ["m","m"]   (requires_confirmation)
Unmerge           → hotkey alt+h, wait 0.3, ribbon ["m","u"]

Increase indent   → hotkey alt+h, wait 0.3, ribbon ["6"]
Decrease indent   → hotkey alt+h, wait 0.3, ribbon ["5"]
Text direction    → hotkey alt+h, wait 0.3, ribbon ["f","q"]

Number format General      → hotkey ctrl+shift+~
Number format Number(2dp)  → hotkey ctrl+shift+1
Number format Currency     → hotkey ctrl+shift+4
Number format Percentage   → hotkey ctrl+shift+5
Number format Date         → hotkey ctrl+shift+3
Number format Time         → hotkey ctrl+shift+2
Number format Scientific   → hotkey ctrl+shift+6
Format Cells dialog        → hotkey ctrl+1

Increase font size (+1pt)  → hotkey alt+h, wait 0.3, ribbon ["f","g"]
Decrease font size (-1pt)  → hotkey alt+h, wait 0.3, ribbon ["f","k"]

Borders all       → hotkey alt+h, wait 0.3, ribbon ["b","a"]
Borders outside   → hotkey alt+h, wait 0.3, ribbon ["b","s"]
Borders thick box → hotkey alt+h, wait 0.3, ribbon ["b","t"]
Borders bottom    → hotkey alt+h, wait 0.3, ribbon ["b","o"]
Borders top       → hotkey alt+h, wait 0.3, ribbon ["b","p"]
Borders none      → hotkey alt+h, wait 0.3, ribbon ["b","n"]

AutoFit col width → hotkey alt+h, wait 0.3, ribbon ["o","i"]
AutoFit row height→ hotkey alt+h, wait 0.3, ribbon ["o","a"]
Set col width     → hotkey alt+h, wait 0.3, ribbon ["o","w"], wait 0.4, type_text "20", press_key enter
Set row height    → hotkey alt+h, wait 0.3, ribbon ["o","h"], wait 0.4, type_text "30", press_key enter

AutoSum           → hotkey alt+=
Fill down         → hotkey ctrl+d
Fill right        → hotkey ctrl+r
Find              → hotkey ctrl+f
Replace           → hotkey ctrl+h
Sort ascending    → hotkey alt+a, wait 0.3, ribbon ["s","a"]
Sort descending   → hotkey alt+a, wait 0.3, ribbon ["s","d"]
Filter toggle     → hotkey ctrl+shift+l
Remove duplicates → hotkey alt+a, wait 0.3, ribbon ["m"]

▌INSERT TAB (Alt+N prefix)
Insert table      → hotkey ctrl+t
Insert chart      → hotkey alt+f1   (embedded) / press_key f11 (new sheet)
Insert PivotTable → hotkey alt+n, wait 0.3, ribbon ["v"]
Insert function   → hotkey shift+f3
Insert hyperlink  → hotkey ctrl+k
Insert comment    → hotkey shift+f2
Insert picture    → hotkey alt+n, wait 0.3, ribbon ["p","i"]
Insert shapes     → hotkey alt+n, wait 0.3, ribbon ["s","h"]
Insert sparkline  → hotkey alt+n, wait 0.3, ribbon ["s","n","l"]
Insert header/footer → hotkey alt+n, wait 0.3, ribbon ["h"]
Insert text box   → hotkey alt+n, wait 0.3, ribbon ["x"]
Insert WordArt    → hotkey alt+n, wait 0.3, ribbon ["w"]
New sheet         → hotkey shift+f11

▌PAGE LAYOUT TAB (Alt+P prefix)
Margins           → hotkey alt+p, wait 0.3, ribbon ["m"]
Orientation portrait  → hotkey alt+p, wait 0.3, ribbon ["o","r"]
Orientation landscape → hotkey alt+p, wait 0.3, ribbon ["o","l"]
Paper size        → hotkey alt+p, wait 0.3, ribbon ["s","z"]
Print area set    → hotkey alt+p, wait 0.3, ribbon ["r","s"]
Print area clear  → hotkey alt+p, wait 0.3, ribbon ["r","c"]
Page breaks       → hotkey alt+p, wait 0.3, ribbon ["b"]
Scale width       → hotkey alt+p, wait 0.3, ribbon ["s","w"]
Scale height      → hotkey alt+p, wait 0.3, ribbon ["s","t"]
Grid lines show   → hotkey alt+p, wait 0.3, ribbon ["v","g"]
Grid lines print  → hotkey alt+p, wait 0.3, ribbon ["i","g"]
Headings show     → hotkey alt+p, wait 0.3, ribbon ["v","h"]
Freeze panes      → hotkey alt+w, wait 0.3, ribbon ["f","f"]
Unfreeze panes    → hotkey alt+w, wait 0.3, ribbon ["f","f"]   (same toggle)
Split view        → hotkey alt+w, wait 0.3, ribbon ["s"]
Zoom to selection → hotkey alt+w, wait 0.3, ribbon ["g"]

▌FORMULAS TAB (Alt+M prefix)
Insert function   → hotkey shift+f3
AutoSum           → hotkey alt+=
Name manager      → hotkey ctrl+f3
Define name       → hotkey ctrl+shift+f3
Trace precedents  → hotkey alt+m, wait 0.3, ribbon ["p"]
Trace dependents  → hotkey alt+m, wait 0.3, ribbon ["d"]
Show formulas     → hotkey ctrl+`
Calculate now     → press_key f9
Calculate sheet   → hotkey shift+f9

▌DATA TAB (Alt+A prefix)
Sort A-Z          → hotkey alt+a, wait 0.3, ribbon ["s","a"]
Sort Z-A          → hotkey alt+a, wait 0.3, ribbon ["s","d"]
Filter            → hotkey ctrl+shift+l
Text to columns   → hotkey alt+a, wait 0.3, ribbon ["e"]
Remove duplicates → hotkey alt+a, wait 0.3, ribbon ["m"]
Data validation   → hotkey alt+a, wait 0.3, ribbon ["v","v"]
Group rows        → hotkey alt+shift+right
Ungroup rows      → hotkey alt+shift+left
Subtotal          → hotkey alt+a, wait 0.3, ribbon ["b"]
Flash fill        → hotkey ctrl+e
Refresh data      → hotkey ctrl+alt+f5

▌REVIEW TAB (Alt+R prefix)
Spell check       → press_key f7
Smart lookup      → hotkey alt+r, wait 0.3, ribbon ["r","l"]
Thesaurus         → hotkey shift+f7
Protect sheet     → hotkey alt+r, wait 0.3, ribbon ["p","s"]
Protect workbook  → hotkey alt+r, wait 0.3, ribbon ["p","w"]
Track changes     → hotkey alt+r, wait 0.3, ribbon ["g"]
New comment       → hotkey shift+f2
Delete comment    → hotkey alt+r, wait 0.3, ribbon ["d","d"]

▌VIEW TAB (Alt+W prefix)
Normal view       → hotkey alt+w, wait 0.3, ribbon ["l"]
Page Layout view  → hotkey alt+w, wait 0.3, ribbon ["p"]
Page Break view   → hotkey alt+w, wait 0.3, ribbon ["i"]
Freeze panes      → hotkey alt+w, wait 0.3, ribbon ["f","f"]
Split             → hotkey alt+w, wait 0.3, ribbon ["s"]
Hide/Show gridlines → hotkey alt+w, wait 0.3, ribbon ["v","g"]
Zoom in           → hotkey alt+w, wait 0.3, ribbon ["q"]
100% zoom         → hotkey alt+w, wait 0.3, ribbon ["j"]

▌NAVIGATION
Go to cell        → hotkey ctrl+g, wait 0.4, type_text "A1", press_key enter
Cell A1           → hotkey ctrl+home
Last cell         → hotkey ctrl+end
Next sheet        → hotkey ctrl+pagedown
Previous sheet    → hotkey ctrl+pageup
Select all        → hotkey ctrl+a
Select row        → hotkey shift+space
Select col        → hotkey ctrl+space
Extend selection  → hotkey shift+[arrow key]

▌ROWS & COLUMNS
Insert row        → hotkey shift+space, wait 0.2, hotkey ctrl+shift+=
Delete row        → hotkey shift+space, wait 0.2, hotkey ctrl+- (requires_confirmation)
Insert column     → hotkey ctrl+space, wait 0.2, hotkey ctrl+shift+=
Delete column     → hotkey ctrl+space, wait 0.2, hotkey ctrl+- (requires_confirmation)
Hide row          → hotkey ctrl+9
Unhide row        → hotkey ctrl+shift+9
Hide column       → hotkey ctrl+0
Unhide column     → hotkey ctrl+shift+0

▌EDITING
Edit cell         → press_key f2
Copy              → hotkey ctrl+c
Cut               → hotkey ctrl+x
Paste             → hotkey ctrl+v
Paste special     → hotkey ctrl+alt+v
Undo              → hotkey ctrl+z
Redo              → hotkey ctrl+y
Save              → hotkey ctrl+s
Save as           → press_key f12

═══════════════ RULES ═══════════════
1. ribbon action = sequential key presses after Alt has been pressed. ALWAYS use ribbon for Alt+letter+letter sequences.
2. NEVER use hotkey for more than 3 keys simultaneously (ctrl+shift+key is fine; ctrl+alt+shift+key is not).
3. ALWAYS add {"action":"wait","seconds":0.3} after ANY hotkey that opens a tab (alt+h, alt+n, alt+p etc.)
4. For font size/family: ALWAYS use ctrl+a to select all text in the input box before typing the value.
5. requires_confirmation=true for: delete row/col, merge cells, clear all, close without save, protect.
6. If unclear: return steps:[] and explain in plan what info you need.
7. Wrap text = ribbon ["w"] after alt+h. Merge = ribbon ["m","c"] after alt+h. These are NEVER ctrl shortcuts.

═══════════════ VERIFIED EXAMPLES ═══════════════

"wrap text" or "text wrap karo":
{"plan":"Wrap text in selected cell(s)","requires_confirmation":false,"steps":[
  {"action":"hotkey","keys":["alt","h"]},{"action":"wait","seconds":0.3},{"action":"ribbon","keys":["w"]}
]}

"merge and center" or "merge center karo":
{"plan":"Merge and center selected cells","requires_confirmation":true,"steps":[
  {"action":"hotkey","keys":["alt","h"]},{"action":"wait","seconds":0.3},{"action":"ribbon","keys":["m","c"]}
]}

"autofit column width" or "column width badao":
{"plan":"AutoFit column width to fit content","requires_confirmation":false,"steps":[
  {"action":"hotkey","keys":["alt","h"]},{"action":"wait","seconds":0.3},{"action":"ribbon","keys":["o","i"]}
]}

"increase column width to 25" or "column width 25 karo":
{"plan":"Set column width to 25","requires_confirmation":false,"steps":[
  {"action":"hotkey","keys":["alt","h"]},{"action":"wait","seconds":0.3},
  {"action":"ribbon","keys":["o","w"]},{"action":"wait","seconds":0.4},
  {"action":"type_text","text":"25"},{"action":"press_key","key":"enter"}
]}

"increase row height to 30":
{"plan":"Set row height to 30","requires_confirmation":false,"steps":[
  {"action":"hotkey","keys":["alt","h"]},{"action":"wait","seconds":0.3},
  {"action":"ribbon","keys":["o","h"]},{"action":"wait","seconds":0.4},
  {"action":"type_text","text":"30"},{"action":"press_key","key":"enter"}
]}

"font size 16 karo" or "increase font size to 16":
{"plan":"Set font size to 16","requires_confirmation":false,"steps":[
  {"action":"hotkey","keys":["alt","h"]},{"action":"wait","seconds":0.3},
  {"action":"ribbon","keys":["f","s"]},{"action":"wait","seconds":0.3},
  {"action":"hotkey","keys":["ctrl","a"]},{"action":"type_text","text":"16"},
  {"action":"press_key","key":"enter"}
]}

"bold and center" or "bold aur center karo":
{"plan":"Bold and center-align selected cell","requires_confirmation":false,"steps":[
  {"action":"hotkey","keys":["ctrl","b"]},{"action":"wait","seconds":0.2},
  {"action":"hotkey","keys":["ctrl","e"]}
]}

"all borders lagao":
{"plan":"Apply all borders to selected cells","requires_confirmation":false,"steps":[
  {"action":"hotkey","keys":["alt","h"]},{"action":"wait","seconds":0.3},
  {"action":"ribbon","keys":["b","a"]}
]}

"freeze first row" or "pehli row freeze karo":
{"plan":"Freeze the top row","requires_confirmation":false,"steps":[
  {"action":"hotkey","keys":["alt","w"]},{"action":"wait","seconds":0.3},
  {"action":"ribbon","keys":["f","r"]}
]}
"""

DEFAULT_ERROR_PLAN: dict = {
    "plan": "Sorry, I could not process that command.",
    "requires_confirmation": False,
    "steps": [],
}


class N8NClient:
    """Multi-provider LLM planner with live provider switching and usage tracking."""

    def __init__(self, webhook_url: Optional[str] = None) -> None:
        self.webhook_url: str = webhook_url or N8N_WEBHOOK_URL

    def send_command(self, user_text: str, context: str = "") -> dict:
        provider = provider_config.provider

        if provider == "groq":
            result = self._call_openai_compat(
                url=GROQ_URL,
                key=provider_config.keys.get("groq", ""),
                model="llama-3.3-70b-versatile",
                user_text=user_text,
                context=context,
                provider_name="groq",
                force_json=True,
            )
            if result: return result
            logger.warning("Groq failed, trying Gemini")

        if provider in ("gemini", "groq"):
            result = self._call_gemini(user_text, context)
            if result: return result
            logger.warning("Gemini failed, trying n8n")

        if provider == "openai":
            result = self._call_openai_compat(
                url=OPENAI_URL,
                key=provider_config.keys.get("openai", ""),
                model="gpt-4o-mini",
                user_text=user_text,
                context=context,
                provider_name="openai",
                force_json=True,
            )
            if result: return result

        if provider == "custom":
            result = self._call_openai_compat(
                url=provider_config.custom_url,
                key=provider_config.keys.get("custom", ""),
                model=provider_config.custom_model,
                user_text=user_text,
                context=context,
                provider_name="custom",
                force_json=False,
            )
            if result: return result

        return self._call_n8n(user_text, context)

    def health_check(self) -> bool:
        try:
            return requests.get("http://localhost:5678", timeout=5).status_code == 200
        except Exception:
            return False

    def _build_user_message(self, user_text: str, context: str) -> str:
        msg = ""
        if context:
            msg += f"[User preferences]\n{context}\n\n"
        msg += f"User command: {user_text}"
        return msg

    def _call_openai_compat(
        self, url: str, key: str, model: str,
        user_text: str, context: str, provider_name: str,
        force_json: bool = False,
    ) -> Optional[dict]:
        if not url or not key:
            logger.warning("%s: missing URL or key", provider_name)
            return None
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        payload: dict = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": self._build_user_message(user_text, context)},
            ],
            "temperature": 0.1,
            "max_tokens": 1024,
        }
        if force_json:
            payload["response_format"] = {"type": "json_object"}
        try:
            logger.info("Calling %s (%s) for: %s", provider_name, model, user_text)
            r = requests.post(url, headers=headers, json=payload, timeout=20)
            r.raise_for_status()
            data = r.json()
            raw = data["choices"][0]["message"]["content"]
            # Track usage
            usage_data = data.get("usage", {})
            usage.record(
                provider_name,
                usage_data.get("prompt_tokens", len(user_text) // 4),
                usage_data.get("completion_tokens", len(raw) // 4),
            )
            return self._parse_plan(raw)
        except requests.exceptions.HTTPError as e:
            logger.error("%s HTTP %s: %s", provider_name, e.response.status_code if e.response else "?", e)
        except Exception as e:
            logger.error("%s call failed: %s", provider_name, e)
        return None

    def _call_gemini(self, user_text: str, context: str) -> Optional[dict]:
        key = provider_config.keys.get("gemini", GEMINI_API_KEY)
        if not key:
            return None
        full_prompt = SYSTEM_PROMPT + "\n\n" + self._build_user_message(user_text, context)
        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 1024},
        }
        try:
            logger.info("Calling Gemini for: %s", user_text)
            r = requests.post(f"{GEMINI_URL}?key={key}", json=payload, timeout=20)
            r.raise_for_status()
            data = r.json()
            raw = data["candidates"][0]["content"]["parts"][0]["text"]
            # Gemini doesn't return token counts in same format; estimate
            meta = data.get("usageMetadata", {})
            usage.record("gemini",
                meta.get("promptTokenCount", len(user_text) // 4),
                meta.get("candidatesTokenCount", len(raw) // 4),
            )
            return self._parse_plan(raw)
        except requests.exceptions.HTTPError as e:
            logger.error("Gemini HTTP %s: %s", e.response.status_code if e.response else "?", e)
        except Exception as e:
            logger.error("Gemini call failed: %s", e)
        return None

    def _call_n8n(self, user_text: str, context: str) -> dict:
        payload = {"user_text": user_text, "context": context, "timestamp": datetime.now().isoformat()}
        try:
            r = requests.post(self.webhook_url, json=payload, timeout=N8N_TIMEOUT)
            r.raise_for_status()
            if not r.text.strip():
                return DEFAULT_ERROR_PLAN
            result = r.json()
            return {
                "plan": result.get("plan", "Executing..."),
                "requires_confirmation": result.get("requires_confirmation", False),
                "steps": result.get("steps", []),
            }
        except Exception as e:
            logger.error("n8n fallback failed: %s", e)
            return DEFAULT_ERROR_PLAN

    def _parse_plan(self, raw: str) -> Optional[dict]:
        try:
            cleaned = re.sub(r"```json\n?", "", raw).replace("```", "").strip()
            # Sometimes model wraps in outer object key
            parsed = json.loads(cleaned)
            plan = {
                "plan": parsed.get("plan", "Executing command..."),
                "requires_confirmation": bool(parsed.get("requires_confirmation", False)),
                "steps": parsed.get("steps", []) if isinstance(parsed.get("steps"), list) else [],
            }
            logger.info("Plan: %s (%d steps)", plan["plan"], len(plan["steps"]))
            return plan
        except (json.JSONDecodeError, KeyError) as e:
            logger.error("Parse failed: %s | raw: %.200s", e, raw)
            return None


# ── Standalone test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s — %(message)s")
    client = N8NClient()
    tests = [
        "wrap text karo",
        "merge and center",
        "autofit column width",
        "increase column width to 25",
        "set row height to 30",
        "font size 16 karo",
        "bold aur center align",
        "all borders lagao",
        "freeze top row",
    ]
    print(f"\nProvider: {provider_config.provider}\n" + "=" * 60)
    for cmd in tests:
        plan = client.send_command(cmd)
        print(f"\n{cmd!r}")
        print(f"  → {plan['plan']}")
        for s in plan["steps"]:
            print(f"     {s}")
