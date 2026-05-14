"""TTS Engine — Neural TTS via edge-tts (default), with gTTS and OpenAI as fallbacks."""

import asyncio
import re
import uuid
from pathlib import Path
from typing import Optional

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from config import OPENAI_API_KEY, AUDIO_DIR, TTS_PROVIDER, TTS_VOICE

# Neural voices per commentary style — British commentator feel for professional
STYLE_VOICES = {
    "professional": "en-GB-RyanNeural",   # authoritative British male
    "hype":         "en-US-GuyNeural",    # energetic American male
    "funny":        "en-US-TonyNeural",   # expressive and casual
    "analytical":   "en-GB-RyanNeural",   # measured and clear
}

STYLE_RATES = {
    "professional": "+0%",
    "hype":         "+15%",
    "funny":        "+5%",
    "analytical":   "-5%",
}

STYLE_PITCH = {
    "professional": "+0Hz",
    "hype":         "+5Hz",
    "funny":        "+2Hz",
    "analytical":   "-2Hz",
}


def _clean_text_for_speech(text: str) -> str:
    """Format commentary text to sound more natural when spoken."""
    # Expand score notation: "45/2" → "45 for 2"
    text = re.sub(r'(\d+)/(\d+)', r'\1 for \2', text)
    # Expand over notation: "12.3" → "over 12, ball 3" isn't worth it; just read naturally
    # Remove markdown bold/italic
    text = re.sub(r'[*_`]', '', text)
    # Normalize ellipsis to natural pause phrasing
    text = text.replace('...', ', ')
    # Ensure sentence ends cleanly
    text = text.strip()
    if text and text[-1] not in '.!?':
        text += '.'
    return text


async def _edge_tts_async(text: str, output_path: Path, voice: str, rate: str, pitch: str):
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(str(output_path))


class TTSEngine:
    """Generate speech audio from commentary text."""

    def __init__(self, provider: str = TTS_PROVIDER, voice: str = TTS_VOICE, style: str = "professional"):
        self.provider = provider
        self.style    = style
        self.voice    = STYLE_VOICES.get(style, "en-GB-RyanNeural")
        self.client   = None

        if provider == "openai" and OPENAI_AVAILABLE and OPENAI_API_KEY:
            try:
                self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
            except Exception:
                self.provider = "edge-tts" if EDGE_TTS_AVAILABLE else "gtts"
        elif provider != "openai":
            self.provider = "edge-tts" if EDGE_TTS_AVAILABLE else "gtts"

    def set_style(self, style: str):
        self.style = style
        self.voice = STYLE_VOICES.get(style, "en-GB-RyanNeural")

    def synthesize(self, text: str, job_id: str, segment_id: Optional[int] = None) -> dict:
        """Generate audio from text. Returns file info."""
        if not text.strip():
            return {"error": "Empty text", "path": None}

        clean = _clean_text_for_speech(text)
        filename = f"{job_id}_{segment_id if segment_id is not None else 'full'}_{uuid.uuid4().hex[:6]}.mp3"
        output_path = AUDIO_DIR / filename

        if self.provider == "openai" and self.client:
            return self._openai_tts(clean, output_path)
        if EDGE_TTS_AVAILABLE:
            return self._edge_tts(clean, output_path)
        if GTTS_AVAILABLE:
            return self._gtts(clean, output_path)
        return {"error": "No TTS provider available", "path": None}

    def synthesize_full(self, commentary_items: list, job_id: str) -> dict:
        """Synthesise all commentary items into individual + combined audio."""
        results = []
        for i, item in enumerate(commentary_items):
            text = item.get("commentary", "")
            if text:
                result = self.synthesize(text, job_id, segment_id=i)
                result["timestamp"] = item.get("timestamp", 0)
                result["event"]     = item.get("event", "")
                results.append(result)

        # Natural join: pause between events
        full_text = "  ".join(
            _clean_text_for_speech(item.get("commentary", ""))
            for item in commentary_items
            if item.get("commentary")
        )
        full_result = self.synthesize(full_text, job_id, segment_id=None)

        return {
            "segments":       results,
            "full_audio":     full_result,
            "total_segments": len(results),
        }

    def _edge_tts(self, text: str, output_path: Path) -> dict:
        """Generate audio using Microsoft Edge neural TTS (free, high quality)."""
        try:
            voice = STYLE_VOICES.get(self.style, "en-GB-RyanNeural")
            rate  = STYLE_RATES.get(self.style, "+0%")
            pitch = STYLE_PITCH.get(self.style, "+0Hz")

            # asyncio.run works fine in a thread-pool executor (no existing event loop)
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        future = pool.submit(
                            asyncio.run,
                            _edge_tts_async(text, output_path, voice, rate, pitch)
                        )
                        future.result(timeout=60)
                else:
                    asyncio.run(_edge_tts_async(text, output_path, voice, rate, pitch))
            except RuntimeError:
                asyncio.run(_edge_tts_async(text, output_path, voice, rate, pitch))

            return {
                "path":       str(output_path),
                "filename":   output_path.name,
                "provider":   "edge-tts",
                "voice":      voice,
                "size_bytes": output_path.stat().st_size,
            }
        except Exception as e:
            if GTTS_AVAILABLE:
                return self._gtts(text, output_path)
            return {"error": str(e), "path": None}

    def _gtts(self, text: str, output_path: Path) -> dict:
        """Generate audio using Google TTS (free, fallback)."""
        try:
            tts = gTTS(text=text, lang="en", slow=False, tld="co.uk")
            tts.save(str(output_path))
            return {
                "path":       str(output_path),
                "filename":   output_path.name,
                "provider":   "gtts",
                "size_bytes": output_path.stat().st_size,
            }
        except Exception as e:
            return {"error": str(e), "path": None}

    def _openai_tts(self, text: str, output_path: Path) -> dict:
        """Generate audio using OpenAI TTS (premium quality)."""
        try:
            response = self.client.audio.speech.create(
                model="tts-1-hd",
                voice=self.voice,
                input=text,
            )
            response.stream_to_file(str(output_path))
            return {
                "path":       str(output_path),
                "filename":   output_path.name,
                "provider":   "openai",
                "voice":      self.voice,
                "size_bytes": output_path.stat().st_size,
            }
        except Exception as e:
            if EDGE_TTS_AVAILABLE:
                return self._edge_tts(text, output_path)
            if GTTS_AVAILABLE:
                return self._gtts(text, output_path)
            return {"error": str(e), "path": None}
