"""Application configuration — loads from environment / .env file."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
VIDEO_DIR = DATA_DIR / "videos"
FRAME_DIR = DATA_DIR / "frames"
OUTPUT_DIR = BASE_DIR / "outputs"
AUDIO_DIR = OUTPUT_DIR / "audio"
MODEL_DIR = BASE_DIR / "models"

for d in [VIDEO_DIR, FRAME_DIR, AUDIO_DIR, MODEL_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── API Keys ───────────────────────────────────────────────────────────
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

# ── Video Processing ──────────────────────────────────────────────────
EXTRACT_FPS: int = int(os.getenv("EXTRACT_FPS", "2"))
MAX_FRAMES: int = int(os.getenv("MAX_FRAMES", "60"))

# ── Commentary ────────────────────────────────────────────────────────
DEFAULT_STYLE: str = os.getenv("DEFAULT_STYLE", "professional")
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")  # "ollama" or "openai"
LLM_MODEL: str = os.getenv("LLM_MODEL", "gemma:7b")
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_VISION_MODEL: str = os.getenv("OLLAMA_VISION_MODEL", "llava:latest")
TTS_PROVIDER: str = os.getenv("TTS_PROVIDER", "gtts")  # "gtts" or "openai"
TTS_VOICE: str = os.getenv("TTS_VOICE", "nova")

# ── Context Engine ────────────────────────────────────────────────────
CONTEXT_HISTORY_SIZE: int = 10
