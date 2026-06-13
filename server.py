#!/usr/bin/env python3
"""
Sutra FastAPI Bridge Server
============================
Exposes the backend pipeline over:
  - WebSocket  ws://localhost:8000/ws      — real-time state events → frontend
  - POST       http://localhost:8000/start  — trigger a listen cycle
  - POST       http://localhost:8000/stop   — abort current cycle
  - POST       http://localhost:8000/undo   — send Ctrl+Z
  - GET        http://localhost:8000/status — current agent state (polling fallback)

Run with:
    python server.py
    (keep main.py for CLI-only use; this is the GUI-connected entrypoint)
"""

import asyncio
import json
import logging
import os
import sys
import threading
import time
from datetime import datetime
from typing import Optional

import pyautogui
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# ── project root on path ──────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from ears.vad_listener import VoiceListener
from ears.sarvam_stt import SarvamSTT
from brain.n8n_client import N8NClient
from hands.actuator import Actuator
from voice.tts_speaker import TTSSpeaker
from memory.mem0_manager import MemoryManager

# ── logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-20s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("sutra.server")
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(title="Sutra Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── global shared state ───────────────────────────────────────────────────────
class AgentState:
    def __init__(self):
        self.status: str = "idle"          # idle | listening | processing | executing
        self.command_count: int = 0
        self.last_hindi: str = ""
        self.last_english: str = ""
        self.last_plan: str = ""
        self.last_steps: list = []
        self.memories: list = []
        self.transcript: list = []         # list of {id, hindi, english, time, plan, steps}
        self._abort: bool = False
        self._lock = threading.Lock()

    def set_status(self, s: str):
        with self._lock:
            self.status = s
        asyncio.run_coroutine_threadsafe(broadcast_state(), loop)

    def abort(self):
        with self._lock:
            self._abort = True

    def clear_abort(self):
        with self._lock:
            self._abort = False

    def should_abort(self) -> bool:
        with self._lock:
            return self._abort

    def to_dict(self) -> dict:
        with self._lock:
            return {
                "type": "state",
                "status": self.status,
                "command_count": self.command_count,
                "last_hindi": self.last_hindi,
                "last_english": self.last_english,
                "last_plan": self.last_plan,
                "last_steps": self.last_steps,
                "memories": self.memories,
                "transcript": self.transcript[-50:],  # last 50 entries
            }


state = AgentState()
loop: asyncio.AbstractEventLoop = None
connected_clients: list[WebSocket] = []

# ── component singletons (initialized on startup) ─────────────────────────────
listener: Optional[VoiceListener] = None
stt: Optional[SarvamSTT] = None
brain: Optional[N8NClient] = None
actuator: Optional[Actuator] = None
speaker: Optional[TTSSpeaker] = None
memory: Optional[MemoryManager] = None
agent_thread: Optional[threading.Thread] = None


# ── WebSocket broadcast ───────────────────────────────────────────────────────
async def broadcast_state():
    """Push current state to all connected WebSocket clients."""
    if not connected_clients:
        return
    msg = json.dumps(state.to_dict())
    dead = []
    for ws in connected_clients:
        try:
            await ws.send_text(msg)
        except Exception:
            dead.append(ws)
    for ws in dead:
        connected_clients.remove(ws)


async def broadcast_event(event: dict):
    """Push a one-off event to all connected WebSocket clients."""
    if not connected_clients:
        return
    msg = json.dumps(event)
    dead = []
    for ws in connected_clients:
        try:
            await ws.send_text(msg)
        except Exception:
            dead.append(ws)
    for ws in dead:
        connected_clients.remove(ws)


def emit(event: dict):
    """Thread-safe wrapper to broadcast from a worker thread."""
    if loop and not loop.is_closed():
        asyncio.run_coroutine_threadsafe(broadcast_event(event), loop)


# ── agent worker (runs in a background thread) ────────────────────────────────
def run_listen_cycle():
    """
    One full pipeline cycle:
      listen → translate → plan → (confirm?) → execute → report
    Called in a daemon thread so FastAPI stays responsive.
    """
    global agent_thread

    if state.status != "idle":
        logger.info("Cycle already running, skipping.")
        return

    state.clear_abort()

    try:
        # ── Step 1: Listen ─────────────────────────────────────────────────
        state.set_status("listening")
        emit({"type": "status", "status": "listening"})
        logger.info("Waiting for speech...")

        try:
            audio = listener.record_until_silence()
        except Exception as e:
            logger.error("Recording failed: %s", e)
            emit({"type": "error", "message": f"Recording failed: {e}"})
            state.set_status("idle")
            return

        if state.should_abort():
            state.set_status("idle")
            return

        if not audio or len(audio) < 1000:
            emit({"type": "error", "message": "No audio captured"})
            state.set_status("idle")
            return

        # ── Step 2: Translate ──────────────────────────────────────────────
        state.set_status("processing")
        emit({"type": "status", "status": "processing"})
        logger.info("Translating...")

        english_text = stt.transcribe_and_translate(audio)
        if not english_text or not english_text.strip():
            emit({"type": "error", "message": "Empty transcription"})
            speaker.speak("I didn't catch anything. Please try again.")
            state.set_status("idle")
            return

        # We don't have the raw Hindi text from Sarvam (it translates directly)
        # so we display the english text in both fields for the transcript
        with state._lock:
            state.last_english = english_text
            state.last_hindi = english_text  # Sarvam translate mode returns English directly

        emit({"type": "transcript_partial", "english": english_text})
        logger.info("Heard: %s", english_text)

        if state.should_abort():
            state.set_status("idle")
            return

        # ── Step 3: Memory ─────────────────────────────────────────────────
        context = memory.get_context(english_text)
        memories = memory.get_all_memories()
        with state._lock:
            state.memories = memories

        # ── Step 4: Plan ───────────────────────────────────────────────────
        logger.info("Planning...")
        plan = brain.send_command(english_text, context)
        plan_text = plan.get("plan", "")
        steps = plan.get("steps", [])
        requires_confirmation = plan.get("requires_confirmation", False)

        with state._lock:
            state.last_plan = plan_text
            state.last_steps = steps

        emit({"type": "plan", "plan": plan_text, "steps": steps, "requires_confirmation": requires_confirmation})
        logger.info("Plan: %s (%d steps)", plan_text, len(steps))

        if not steps:
            emit({"type": "error", "message": f"No actions for: {english_text}"})
            speaker.speak(f"I understood, but I don't know how to do that yet.")
            state.set_status("idle")
            return

        if state.should_abort():
            state.set_status("idle")
            return

        # ── Step 5: Confirmation (destructive actions) ────────────────────
        if requires_confirmation:
            emit({"type": "confirm_required", "plan": plan_text})
            speaker.speak(f"I'm about to {plan_text}. Say yes or no.")

            # Listen for yes/no
            try:
                confirm_audio = listener.record_until_silence()
                confirm_text = stt.transcribe_and_translate(confirm_audio).lower()
                affirmative = ["yes", "yeah", "ok", "sure", "haan", "ha", "proceed", "do it"]
                confirmed = any(w in confirm_text for w in affirmative)
            except Exception:
                confirmed = False

            if not confirmed:
                emit({"type": "aborted", "reason": "User did not confirm"})
                speaker.speak("Okay, cancelled.")
                state.set_status("idle")
                return

        # ── Step 6: Execute ────────────────────────────────────────────────
        state.set_status("executing")
        emit({"type": "status", "status": "executing"})
        logger.info("Executing %d steps...", len(steps))

        try:
            success = actuator.execute_plan(steps)
        except pyautogui.FailSafeException:
            emit({"type": "error", "message": "Failsafe triggered! Move mouse away from corner."})
            state.set_status("idle")
            return
        except Exception as e:
            emit({"type": "error", "message": f"Execution error: {e}"})
            state.set_status("idle")
            return

        # ── Step 7: Report ─────────────────────────────────────────────────
        with state._lock:
            state.command_count += 1
            entry = {
                "id": int(time.time() * 1000),
                "hindi": state.last_hindi,
                "english": english_text,
                "plan": plan_text,
                "steps": steps,
                "success": success,
                "time": datetime.now().strftime("%H:%M:%S"),
            }
            state.transcript.append(entry)

        emit({"type": "transcript_entry", "entry": entry})

        if success:
            speaker.speak("Done!")
            emit({"type": "done", "plan": plan_text})
        else:
            speaker.speak("Some steps failed.")
            emit({"type": "error", "message": "Some steps failed"})

    except Exception as e:
        logger.exception("Unexpected error in cycle: %s", e)
        emit({"type": "error", "message": str(e)})

    finally:
        state.set_status("idle")
        emit({"type": "status", "status": "idle"})


# ── REST endpoints ─────────────────────────────────────────────────────────────
@app.get("/status")
def get_status():
    return state.to_dict()


@app.post("/start")
def start_listening():
    """Trigger one listen cycle (equivalent to pressing Ctrl+Space)."""
    global agent_thread
    if state.status != "idle":
        return {"ok": False, "message": "Already running"}

    agent_thread = threading.Thread(target=run_listen_cycle, daemon=True)
    agent_thread.start()
    return {"ok": True, "message": "Listening started"}


@app.post("/stop")
def stop_listening():
    """Abort the current cycle."""
    state.abort()
    speaker.stop()
    state.set_status("idle")
    return {"ok": True, "message": "Stopped"}


@app.post("/undo")
def undo_last():
    """Send Ctrl+Z immediately."""
    try:
        actuator.execute_plan([{"action": "hotkey", "keys": ["ctrl", "z"]}])
        emit({"type": "undo", "message": "Undo executed (Ctrl+Z)"})
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "message": str(e)}


# ── WebSocket endpoint ────────────────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connected_clients.append(ws)
    logger.info("Frontend connected. Total clients: %d", len(connected_clients))

    # Send current state immediately on connect
    await ws.send_text(json.dumps(state.to_dict()))

    try:
        while True:
            # Keep connection alive; frontend can also send commands over WS
            data = await ws.receive_text()
            msg = json.loads(data)
            cmd = msg.get("command")

            if cmd == "start":
                global agent_thread
                if state.status == "idle":
                    agent_thread = threading.Thread(target=run_listen_cycle, daemon=True)
                    agent_thread.start()
            elif cmd == "stop":
                state.abort()
                speaker.stop()
                state.set_status("idle")
            elif cmd == "undo":
                threading.Thread(
                    target=lambda: actuator.execute_plan([{"action": "hotkey", "keys": ["ctrl", "z"]}]),
                    daemon=True,
                ).start()
                emit({"type": "undo", "message": "Undo executed"})

    except WebSocketDisconnect:
        connected_clients.remove(ws)
        logger.info("Frontend disconnected. Total clients: %d", len(connected_clients))
    except Exception as e:
        logger.error("WebSocket error: %s", e)
        if ws in connected_clients:
            connected_clients.remove(ws)


# ── startup / shutdown ────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    global listener, stt, brain, actuator, speaker, memory, loop

    loop = asyncio.get_running_loop()
    logger.info("Initializing Sutra components...")

    try:
        listener = VoiceListener()
        logger.info("✅ VoiceListener ready")
    except Exception as e:
        logger.error("❌ VoiceListener failed: %s", e)

    stt = SarvamSTT()
    logger.info("✅ SarvamSTT ready")

    brain = N8NClient()
    logger.info("✅ N8NClient ready")

    actuator = Actuator()
    logger.info("✅ Actuator ready")

    speaker = TTSSpeaker()
    logger.info("✅ TTSSpeaker ready")

    memory = MemoryManager()
    logger.info("✅ MemoryManager ready")

    logger.info("🚀 Sutra server ready at http://localhost:8000")
    logger.info("   WebSocket: ws://localhost:8000/ws")
    logger.info("   Press Ctrl+C to stop")


@app.on_event("shutdown")
async def shutdown():
    if listener:
        listener.cleanup()
    logger.info("Sutra server stopped.")


# ── entrypoint ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="warning",
    )
