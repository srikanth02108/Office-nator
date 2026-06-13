"""Sarvam AI Speech-to-Text client with Hindi/Marathi → English translation.

Sends WAV audio to the Sarvam ``/speech-to-text`` endpoint and returns
the translated English transcript.
"""

import io
import logging
import os
import sys

import requests

# ---------------------------------------------------------------------------
# Ensure the project root is importable so we can pull from the config module
# ---------------------------------------------------------------------------
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

try:
    from config import SARVAM_API_KEY, SARVAM_MODEL, SARVAM_STT_MODE
except ImportError:
    # Fallback defaults when config module is not yet available
    SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "")
    SARVAM_MODEL: str = "saaras:v3"
    SARVAM_STT_MODE: str = "translate"

logger = logging.getLogger(__name__)


class SarvamSTT:
    """Sarvam AI Speech-to-Text client with Hindi/Marathi → English translation.

    Example::

        stt = SarvamSTT()
        text = stt.transcribe_and_translate(wav_bytes)
        print(text)
    """

    API_URL: str = "https://api.sarvam.ai/speech-to-text"

    def __init__(self, api_key: str | None = None) -> None:
        """Initialise the STT client.

        Args:
            api_key: Sarvam subscription key.  Falls back to
                     ``config.SARVAM_API_KEY`` or the ``SARVAM_API_KEY``
                     environment variable.
        """
        self.api_key: str = api_key or SARVAM_API_KEY
        if not self.api_key:
            logger.warning(
                "No Sarvam API key provided.  Set SARVAM_API_KEY env var "
                "or pass it explicitly."
            )

    def transcribe_and_translate(self, audio_bytes: bytes) -> str:
        """Send audio to Sarvam AI and return the English translation.

        Args:
            audio_bytes: WAV audio data (16 kHz, 16-bit, mono).

        Returns:
            Translated English text, or an empty string on failure.
        """
        if not self.api_key:
            logger.error("Cannot call Sarvam API — no API key configured.")
            return ""

        headers: dict[str, str] = {
            "api-subscription-key": self.api_key,
        }

        files: dict[str, tuple[str, io.BytesIO, str]] = {
            "file": ("audio.wav", io.BytesIO(audio_bytes), "audio/wav"),
        }

        data: dict[str, str] = {
            "model": SARVAM_MODEL,
            "mode": SARVAM_STT_MODE,  # "translate" → Hindi/Marathi → English
        }

        try:
            response = requests.post(
                self.API_URL,
                headers=headers,
                files=files,
                data=data,
                timeout=15,
            )
            response.raise_for_status()
            result: dict = response.json()

            transcript: str = result.get("transcript", "")
            logger.info("Sarvam STT result: %s", transcript)
            return transcript

        except requests.exceptions.Timeout:
            logger.error("Sarvam API request timed out.")
            return ""
        except requests.exceptions.HTTPError as exc:
            logger.error(
                "Sarvam API HTTP error %s: %s",
                exc.response.status_code if exc.response is not None else "?",
                exc,
            )
            return ""
        except requests.exceptions.ConnectionError:
            logger.error("Could not connect to Sarvam API.")
            return ""
        except requests.exceptions.RequestException as exc:
            logger.error("Sarvam API request failed: %s", exc)
            return ""
        except (ValueError, KeyError) as exc:
            logger.error("Failed to parse Sarvam API response: %s", exc)
            return ""


# ═══════════════════════════════════════════════════════════════════════════
# Standalone test
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    stt = SarvamSTT()

    # Quick smoke test — if a WAV file path is supplied on the command line,
    # send it to Sarvam; otherwise just print usage instructions.
    if len(sys.argv) > 1:
        wav_path = sys.argv[1]
        if not os.path.isfile(wav_path):
            print(f"❌ File not found: {wav_path}")
            sys.exit(1)

        with open(wav_path, "rb") as f:
            wav_data = f.read()

        print(f"📤 Sending {len(wav_data)} bytes to Sarvam STT …")
        result = stt.transcribe_and_translate(wav_data)
        if result:
            print(f"📝 Translation: {result}")
        else:
            print("⚠️  No transcript returned (check logs above).")
    else:
        print(
            "Usage: python sarvam_stt.py <path_to_wav>\n"
            "\n"
            "Sends a WAV file (16 kHz, 16-bit, mono) to the Sarvam AI\n"
            "speech-to-text endpoint and prints the English translation.\n"
            "\n"
            "Make sure the SARVAM_API_KEY environment variable is set."
        )
