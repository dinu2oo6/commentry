"""TTS Engine — Text-to-speech using gTTS (free) or OpenAI TTS (premium)."""

import uuid
from pathlib import Path
from typing import Optional

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


class TTSEngine:
    """Generate speech audio from commentary text."""

    def __init__(self, provider: str = TTS_PROVIDER, voice: str = TTS_VOICE):
        self.provider = provider
        self.voice = voice
        self.client = None
        if provider == "openai" and OPENAI_AVAILABLE and OPENAI_API_KEY:
            try:
                self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
            except Exception:
                self.provider = "gtts"

    def synthesize(self, text: str, job_id: str, segment_id: Optional[int] = None) -> dict:
        """Generate audio from text. Returns file info."""
        if not text.strip():
            return {"error": "Empty text", "path": None}

        filename = f"{job_id}_{segment_id or 'full'}_{uuid.uuid4().hex[:6]}.mp3"
        output_path = AUDIO_DIR / filename

        if self.provider == "openai" and self.client:
            return self._openai_tts(text, output_path)
        elif GTTS_AVAILABLE:
            return self._gtts(text, output_path)
        else:
            return {"error": "No TTS provider available", "path": None}

    def synthesize_full(self, commentary_items: list, job_id: str) -> dict:
        """Synthesize all commentary items into individual + combined audio."""
        results = []
        for i, item in enumerate(commentary_items):
            text = item.get("commentary", "")
            if text:
                result = self.synthesize(text, job_id, segment_id=i)
                result["timestamp"] = item.get("timestamp", 0)
                result["event"] = item.get("event", "")
                results.append(result)

        # Combine all commentary text for full audio
        full_text = " ... ".join(
            item.get("commentary", "") for item in commentary_items if item.get("commentary")
        )
        full_result = self.synthesize(full_text, job_id, segment_id=None)

        return {
            "segments": results,
            "full_audio": full_result,
            "total_segments": len(results),
        }

    def _gtts(self, text: str, output_path: Path) -> dict:
        """Generate audio using Google TTS (free)."""
        try:
            tts = gTTS(text=text, lang="en", slow=False)
            tts.save(str(output_path))
            return {
                "path": str(output_path),
                "filename": output_path.name,
                "provider": "gtts",
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
                "path": str(output_path),
                "filename": output_path.name,
                "provider": "openai",
                "voice": self.voice,
                "size_bytes": output_path.stat().st_size,
            }
        except Exception as e:
            # Fallback to gTTS
            if GTTS_AVAILABLE:
                return self._gtts(text, output_path)
            return {"error": str(e), "path": None}
