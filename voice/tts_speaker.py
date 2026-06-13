"""Edge-TTS based text-to-speech with streaming audio playback.

Uses Microsoft Edge's neural TTS voices for high-quality speech synthesis.
Supports streaming playback (starts speaking before full audio is generated)
and barge-in interruption.
"""

import asyncio
import logging
import threading
import sys
import os

import pyaudio
import edge_tts

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TTS_VOICE_EN, TTS_VOICE_HI, TTS_RATE

logger = logging.getLogger(__name__)


class TTSSpeaker:
    """Text-to-speech using Microsoft Edge TTS.

    Supports streaming playback (starts speaking before full audio is generated)
    and can be interrupted (barge-in support).
    """

    def __init__(self, voice: str = None):
        """Initialize TTSSpeaker.

        Args:
            voice: Default voice to use. Falls back to TTS_VOICE_EN from config.
        """
        self.voice: str = voice or TTS_VOICE_EN
        self._is_speaking: bool = False
        self._stop_flag: bool = False

    @property
    def is_speaking(self) -> bool:
        """Whether the speaker is currently producing audio."""
        return self._is_speaking

    def stop(self) -> None:
        """Interrupt current speech (barge-in)."""
        if self._is_speaking:
            self._stop_flag = True
            logger.info("TTS interrupted (barge-in)")

    async def _speak_async(self, text: str, voice: str = None) -> None:
        """Internal async method for streaming TTS.

        Opens a PyAudio output stream and writes audio chunks as they arrive
        from the edge-tts service, enabling low-latency playback.

        Args:
            text: The text to synthesise.
            voice: Optional voice override.
        """
        voice = voice or self.voice
        self._is_speaking = True
        self._stop_flag = False

        p = pyaudio.PyAudio()
        stream = None

        try:
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=TTS_RATE,
                output=True,
            )

            communicate = edge_tts.Communicate(text, voice)

            async for chunk in communicate.stream():
                if self._stop_flag:
                    logger.info("Speech stopped by barge-in")
                    break
                if chunk["type"] == "audio":
                    stream.write(chunk["data"])

        except Exception as e:
            logger.error(f"TTS error: {e}")

        finally:
            if stream:
                stream.stop_stream()
                stream.close()
            p.terminate()
            self._is_speaking = False
            self._stop_flag = False

    def speak(self, text: str, voice: str = None) -> None:
        """Speak text aloud (blocking). Streams audio for low latency.

        Args:
            text: Text to speak.
            voice: Optional voice override (e.g., 'hi-IN-SwaraNeural' for Hindi).
        """
        if not text:
            return

        if len(text) > 80:
            logger.info(f"Speaking: '{text[:80]}...'")
        else:
            logger.info(f"Speaking: '{text}'")

        # Run async speak in an event loop
        try:
            loop = asyncio.get_running_loop()
            # Already inside a running loop — spin up a thread with its own loop
            thread = threading.Thread(
                target=lambda: asyncio.run(self._speak_async(text, voice))
            )
            thread.start()
            thread.join()
        except RuntimeError:
            # No running loop — safe to use asyncio.run()
            asyncio.run(self._speak_async(text, voice))

    def speak_async_fire_and_forget(self, text: str, voice: str = None) -> threading.Thread:
        """Speak in background thread (non-blocking).

        Args:
            text: Text to speak.
            voice: Optional voice override.

        Returns:
            The daemon thread running the speech.
        """
        thread = threading.Thread(
            target=self.speak,
            args=(text, voice),
            daemon=True,
        )
        thread.start()
        return thread


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    )

    speaker = TTSSpeaker()

    # English greeting
    logger.info("Testing English TTS...")
    speaker.speak(
        "Hello! I am Sutra, your voice-controlled desktop assistant. Ready to help!"
    )

    # Hindi greeting
    logger.info("Testing Hindi TTS...")
    speaker.speak("नमस्ते! मैं सूत्र हूँ", voice=TTS_VOICE_HI)

    logger.info("TTS test complete.")
