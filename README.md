# CricComment AI

AI-powered cricket commentary generator. Upload a cricket match video and get back a fully-voiced commentary video — powered by computer vision, GPT-4o, and text-to-speech.

```
Upload video → Extract frames → Detect events → Generate commentary → Synthesize voice → Output video
```

---

## How It Works

| Step | What Happens |
|------|-------------|
| 1. Upload | You upload a cricket video through the web UI |
| 2. Frame Extraction | OpenCV pulls frames at 2 fps (configurable) |
| 3. Event Detection | YOLOv8 detects shots, boundaries, wickets |
| 4. Commentary | GPT-4o writes professional ball-by-ball commentary |
| 5. Voice | gTTS (or OpenAI TTS) converts text to speech |
| 6. Compose | ffmpeg merges the original video with audio |

---

## Project Structure

```
commentry/
├── backend/
│   ├── main.py                   # FastAPI app entry point
│   ├── config.py                 # Env config & directory setup
│   ├── requirements.txt
│   ├── modules/
│   │   ├── video_processor.py    # Frame extraction via OpenCV
│   │   ├── event_detector.py     # YOLOv8-based shot detection
│   │   ├── shot_classifier.py    # Shot type classification
│   │   ├── commentary_generator.py  # GPT-4o commentary prompts
│   │   ├── context_engine.py     # Match context & history
│   │   ├── tts_engine.py         # gTTS / OpenAI TTS
│   │   └── video_composer.py     # ffmpeg video + audio merge
│   └── routes/
│       └── api.py                # All REST + WebSocket routes
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── components/
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── data/
│   ├── videos/                   # Uploaded videos (git-ignored)
│   └── frames/                   # Extracted frames (git-ignored)
├── outputs/
│   ├── audio/                    # Generated audio (git-ignored)
│   └── videos/                   # Final videos (git-ignored)
└── run.sh                        # One-command startup script
```

---

## Prerequisites

Make sure these are installed before running the project.

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.10+ | [python.org](https://www.python.org) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org) |
| ffmpeg | any | see below |

### Install ffmpeg

**macOS (Homebrew):**
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

Create `backend/.env`:

```bash
cp backend/.env.example backend/.env   # if example exists, or create manually
```

```env
# backend/.env

OPENAI_API_KEY=           # Optional — only needed for OpenAI TTS or GPT-4o
EXTRACT_FPS=2             # Frames per second to extract
MAX_FRAMES=60             # Max frames per video
DEFAULT_STYLE=professional
LLM_MODEL=gpt-4o
TTS_PROVIDER=gtts         # "gtts" (free) or "openai" (needs key)
TTS_VOICE=nova            # Only used when TTS_PROVIDER=openai
```

> **Note:** `OPENAI_API_KEY` is required for GPT-4o commentary generation. Without it the backend will error during processing. Set `TTS_PROVIDER=gtts` to use free TTS even when you have an OpenAI key.

---

## Running the App

### One-command start (recommended)

From the project root:

```bash
chmod +x run.sh
./run.sh
```

This starts both servers simultaneously:

```
Frontend  →  http://localhost:5173
Backend   →  http://localhost:8000
API Docs  →  http://localhost:8000/docs
```

Press `Ctrl+C` to stop both.

---

### Manual start (two terminals)

**Terminal 1 — Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

---

## All Commands Reference

### Backend

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate           # macOS / Linux
venv\Scripts\activate              # Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run development server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Run without auto-reload (production-like)
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
# Install dependencies
npm install

# Start development server (http://localhost:5173)
npm run dev

# Build for production
npm run build

# Preview production build locally
npm run preview
```

### Utility

```bash
# Health check
curl http://localhost:8000/api/health

# Kill process on a port (if port already in use)
lsof -i :8000        # find PID
kill -9 <PID>

# Clean generated outputs
rm -rf data/frames/*
rm -rf outputs/audio/*
rm -rf outputs/videos/*
```

---

## API Reference

Base URL: `http://localhost:8000/api`

Interactive docs: `http://localhost:8000/docs`

### Health Check
```http
GET /api/health
```
```bash
curl http://localhost:8000/api/health
```

### Upload Video
```http
POST /api/upload-video
Content-Type: multipart/form-data
```
```bash
curl -X POST http://localhost:8000/api/upload-video \
  -F "file=@/path/to/match.mp4"
# Returns: { "job_id": "abc123..." }
```

### Start Processing
```http
POST /api/process-video
Content-Type: multipart/form-data
```
```bash
curl -X POST http://localhost:8000/api/process-video \
  -F "job_id=abc123" \
  -F "style=professional" \
  -F "batsman=Virat Kohli" \
  -F "bowler=Jasprit Bumrah"
```

### Get Results
```http
GET /api/results/{job_id}
```
```bash
curl http://localhost:8000/api/results/abc123
```

### Download Audio
```http
GET /api/audio/{filename}
```
```bash
curl -O http://localhost:8000/api/audio/abc123_full.mp3
```

### Download Final Video
```http
GET /api/video/{filename}
```
```bash
curl -O http://localhost:8000/api/video/abc123_commentary.mp4
```

### Real-time Progress (WebSocket)
```
WS /api/stream/{job_id}
```
Connect to receive live status updates while the video processes.

---

## Typical Workflow

1. Open `http://localhost:5173` in your browser
2. Upload a cricket video clip
3. Enter player names (optional) and choose commentary style
4. Click **Process**
5. Watch the real-time progress bar
6. Download or play the final commentary video

---

## Troubleshooting

### Final video is missing
ffmpeg is required for video composition. Install it, then restart the app.
```bash
brew install ffmpeg        # macOS
sudo apt install ffmpeg    # Ubuntu
```

### Backend won't start
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend won't start
```bash
cd frontend
npm install
npm run dev
```

### Port already in use
```bash
lsof -i :8000    # or :5173
kill -9 <PID>
```

### OpenAI TTS not working
Ensure `backend/.env` has:
```env
OPENAI_API_KEY=sk-...
TTS_PROVIDER=openai
TTS_VOICE=nova
```

### Commentary generation fails
`GPT-4o` requires a valid `OPENAI_API_KEY`. Check the key is set and has credits.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI + Uvicorn |
| Computer Vision | OpenCV + YOLOv8 (Ultralytics) |
| AI Commentary | OpenAI GPT-4o |
| Text-to-Speech | gTTS (free) / OpenAI TTS |
| Video Composition | ffmpeg |
| Frontend | React 18 + Vite |
| Deep Learning | PyTorch + TorchVision |

---

## License

MIT License — see [LICENSE](LICENSE) for details.
