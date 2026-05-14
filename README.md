# CricComment AI

AI-powered cricket commentary generator. Upload a cricket match video and get back a fully-voiced commentary video — powered by computer vision, Groq LLM, and neural text-to-speech.

```
Upload video → Extract frames → Detect events → Generate commentary → Synthesize voice → Output video
```

---

## How It Works

| Step | What Happens |
|------|-------------|
| 1. Upload | You upload a cricket video through the web UI |
| 2. Frame Extraction | OpenCV pulls frames at 2 fps (configurable) |
| 3. Event Detection | YOLOv8 classifies shots, boundaries, wickets |
| 4. Vision Analysis | Groq Vision (`llama-4-scout`) analyzes actual frame content |
| 5. Commentary | Groq LLM (`llama-3.3-70b`) generates ball-by-ball commentary in your chosen style |
| 6. Voice | edge-tts renders neural speech matched to the commentary style |
| 7. Compose | ffmpeg merges the commentary audio onto the original video |

---

## Project Structure

```
commentry/
├── backend/
│   ├── main.py                      # FastAPI app entry point
│   ├── config.py                    # Env config & directory setup
│   ├── requirements.txt
│   ├── .env.example                 # Template for environment variables
│   ├── modules/
│   │   ├── video_processor.py       # Frame extraction via OpenCV
│   │   ├── event_detector.py        # YOLOv8 object detection + event classification
│   │   ├── shot_classifier.py       # Cricket shot type classification
│   │   ├── commentary_generator.py  # Groq LLM + vision commentary prompts
│   │   ├── context_engine.py        # Match state, score, and history tracking
│   │   ├── tts_engine.py            # edge-tts / gTTS / OpenAI TTS
│   │   └── video_composer.py        # ffmpeg video + audio merge
│   └── routes/
│       └── api.py                   # All REST + WebSocket endpoints
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── components/
│   │       ├── VideoUpload.jsx
│   │       ├── StyleSelector.jsx
│   │       ├── ProcessingStatus.jsx
│   │       ├── CommentaryTimeline.jsx
│   │       └── AudioPlayer.jsx
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── data/
│   ├── videos/                      # Uploaded videos (git-ignored)
│   └── frames/                      # Extracted frames (git-ignored)
└── outputs/
    ├── audio/                       # Generated audio (git-ignored)
    └── videos/                      # Final videos (git-ignored)
```

---

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.10+ | [python.org](https://www.python.org) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org) |
| ffmpeg | any | see below |
| Groq API key | — | [console.groq.com](https://console.groq.com) |

### Install ffmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu / Debian:**
```bash
sudo apt update && sudo apt install -y ffmpeg
```

**Verify:**
```bash
ffmpeg -version
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/dinu2oo6/commentry.git
cd commentry
```

### 2. Backend setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Frontend setup

```bash
cd ../frontend
npm install
```

### 4. Environment variables

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

```env
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional — OpenAI TTS (premium voice quality)
OPENAI_API_KEY=your_openai_api_key_here

# Video processing
EXTRACT_FPS=2
MAX_FRAMES=60

# Commentary
DEFAULT_STYLE=professional
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
GROQ_VISION_MODEL=meta-llama/llama-4-scout-17b-16e-instruct

# Text-to-Speech: "gtts" (free fallback) or "openai" (premium)
TTS_PROVIDER=gtts
TTS_VOICE=nova
```

> Get a free Groq API key at [console.groq.com](https://console.groq.com). The free tier is generous enough for development and testing.

---

## Running the App

### Manual start — two terminals

**Terminal 1 — Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8002 |
| Interactive API Docs | http://localhost:8002/docs |

---

## All Commands Reference

### Backend

```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate           # macOS / Linux
venv\Scripts\activate              # Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run development server (port must match vite.config.js proxy → 8002)
uvicorn main:app --host 0.0.0.0 --port 8002 --reload

# Run without auto-reload
uvicorn main:app --host 0.0.0.0 --port 8002

# Deactivate virtual environment
deactivate
```

### Frontend

```bash
# Install dependencies
npm install

# Start development server  →  http://localhost:5173
npm run dev

# Build for production
npm run build

# Preview production build locally
npm run preview
```

### Utility

```bash
# Health check
curl http://localhost:8002/api/health

# Find and kill a process using a port (if port is already in use)
lsof -i :8002        # find PID
kill -9 <PID>

# Clean generated outputs
rm -rf data/frames/*
rm -rf outputs/audio/*
rm -rf outputs/videos/*
```

---

## API Reference

**Base URL:** `http://localhost:8002/api`

**Interactive docs:** `http://localhost:8002/docs`

---

### `GET /api/health`

Health check.

```bash
curl http://localhost:8002/api/health
```

```json
{ "status": "ok", "service": "CricComment AI" }
```

---

### `POST /api/upload-video`

Upload a video file. Returns a `job_id` used for all subsequent calls.

```bash
curl -X POST http://localhost:8002/api/upload-video \
  -F "file=@/path/to/match.mp4"
```

**Response:**
```json
{
  "job_id": "a1b2c3d4e5f6",
  "status": "uploaded",
  "filename": "match.mp4"
}
```

---

### `POST /api/process-video`

Start the full processing pipeline on an uploaded video.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `job_id` | string | required | ID returned from `/upload-video` |
| `style` | string | `professional` | Commentary style (see styles below) |
| `batsman` | string | `Batsman` | Batsman's name used in commentary |
| `bowler` | string | `Bowler` | Bowler's name used in commentary |

```bash
curl -X POST http://localhost:8002/api/process-video \
  -F "job_id=a1b2c3d4e5f6" \
  -F "style=professional" \
  -F "batsman=Virat Kohli" \
  -F "bowler=Jasprit Bumrah"
```

**Response:**
```json
{
  "job_id": "a1b2c3d4e5f6",
  "status": "processing"
}
```

---

### `GET /api/results/{job_id}`

Poll for processing status and results.

```bash
curl http://localhost:8002/api/results/a1b2c3d4e5f6
```

**Response (while processing):**
```json
{
  "job_id": "a1b2c3d4e5f6",
  "status": "processing",
  "step": "generating_commentary",
  "progress": 70,
  "results": null
}
```

**Response (completed):**
```json
{
  "job_id": "a1b2c3d4e5f6",
  "status": "completed",
  "step": "done",
  "progress": 100,
  "results": {
    "video_info": {
      "duration": 45.2,
      "fps": 30,
      "frames_extracted": 90
    },
    "events": [
      {
        "timestamp": 3.5,
        "event": "FOUR",
        "shot": "cover_drive",
        "confidence": 0.91,
        "commentary": "Beautiful cover drive by Virat Kohli! That races to the boundary!",
        "score": "24/1",
        "overs": "4.3"
      }
    ],
    "match_summary": { "total_runs": 87, "wickets": 2, "overs": "12.0" },
    "audio": {
      "full": { "filename": "a1b2c3d4e5f6_full_abc123.mp3", "provider": "edge-tts" },
      "segments": []
    },
    "final_video": { "filename": "a1b2c3d4e5f6_commentary.mp4" },
    "style": "professional"
  }
}
```

**Status values:**

| Status | Meaning |
|--------|---------|
| `uploaded` | Video received, not yet processing |
| `processing` | Pipeline is running |
| `completed` | All done, results are available |
| `error` | Pipeline failed — check the `error` field |

**Step values (in order):**

`extracting_frames` → `detecting_events` → `generating_commentary` → `generating_audio` → `composing_video` → `done`

---

### `GET /api/audio/{filename}`

Download or stream a generated audio file.

```bash
curl -O http://localhost:8002/api/audio/a1b2c3d4e5f6_full_abc123.mp3
```

---

### `GET /api/video/{filename}`

Download the final video with commentary audio merged in.

```bash
curl -O http://localhost:8002/api/video/a1b2c3d4e5f6_commentary.mp4
```

---

### `WS /api/stream/{job_id}`

WebSocket endpoint for real-time progress updates during processing.

```
ws://localhost:8002/api/stream/a1b2c3d4e5f6
```

**Message format (sent every ~1 second):**
```json
{
  "job_id": "a1b2c3d4e5f6",
  "status": "processing",
  "step": "generating_audio",
  "progress": 80
}
```

Connection closes automatically when status reaches `completed` or `error`.

---

## Commentary Styles

| Style | Description | Voice |
|-------|-------------|-------|
| `professional` | Harsha Bhogle style — measured, insightful, articulate | British male (Ryan Neural) |
| `hype` | IPL-style — maximum energy, capitals, crowd reactions | American male (Guy Neural) |
| `funny` | Casual with humor, memes, and pop culture references | Expressive casual (Tony Neural) |
| `analytical` | Stats-heavy — strike rates, wagon wheels, technique | British male (Ryan Neural) |

---

## Text-to-Speech Providers

The TTS engine tries providers in this order:

1. **edge-tts** (default, free) — Microsoft Azure neural voices, high quality, no API key needed
2. **gTTS** (fallback, free) — Google Translate TTS, basic quality
3. **OpenAI TTS** (premium) — requires `OPENAI_API_KEY`, uses `tts-1-hd` model with `nova` voice (or whichever `TTS_VOICE` is set)

Set `TTS_PROVIDER=openai` in `.env` to use OpenAI TTS.

---

## Event Types

The pipeline detects and generates commentary for these cricket events:

`DOT` · `SINGLE` · `DOUBLE` · `TRIPLE` · `FOUR` · `SIX` · `WICKET` · `WIDE` · `NO_BALL`

---

## Troubleshooting

### Commentary is generic / not using Groq

Check that `GROQ_API_KEY` is set in `backend/.env` and is valid:

```bash
# Test your key
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer $GROQ_API_KEY"
```

### Final video not generated

ffmpeg is required for video composition. Install it and restart the backend:

```bash
brew install ffmpeg        # macOS
sudo apt install ffmpeg    # Ubuntu
ffmpeg -version            # verify
```

### Backend won't start

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

### Frontend shows network errors

Make sure the backend is running on port **8002** — the Vite dev server proxies `/api` and `/static` to `localhost:8002`.

### Port already in use

```bash
lsof -i :8002    # find PID using the port
kill -9 <PID>

lsof -i :5173    # same for frontend
kill -9 <PID>
```

### edge-tts fails silently

edge-tts requires an internet connection (it calls Microsoft's Azure endpoint). If offline, it falls back to gTTS automatically.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI + Uvicorn |
| Computer Vision | OpenCV + YOLOv8 (Ultralytics) |
| Object Detection | PyTorch + TorchVision |
| LLM Commentary | Groq (`llama-3.3-70b-versatile`) |
| Vision Analysis | Groq Vision (`llama-4-scout-17b-16e-instruct`) |
| Text-to-Speech | edge-tts (neural) · gTTS (fallback) · OpenAI TTS (premium) |
| Video Composition | ffmpeg |
| Frontend | React 18 + Vite |

---

## License

MIT
