# CricComment AI

AI-powered cricket commentary generator. Upload a cricket match video and get back a fully-voiced commentary video — powered by computer vision, Ollama (local LLM), and text-to-speech.

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
| 4. Commentary | Ollama (`gemma:7b`) writes professional ball-by-ball commentary |
| 5. Vision | Ollama (`llava:latest`) analyzes frames for visual context |
| 6. Voice | gTTS converts text to speech |
| 7. Compose | ffmpeg merges the original video with audio |

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
│   │   ├── commentary_generator.py  # Ollama commentary prompts
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
| Ollama | latest | [ollama.com](https://ollama.com) |

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

### Install Ollama

**macOS / Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**macOS (Homebrew):**
```bash
brew install ollama
```

**Verify:**
```bash
ollama --version
```

### Pull required Ollama models

```bash
# Text commentary model
ollama pull gemma:7b

# Vision model (for frame analysis)
ollama pull llava:latest
```

**Start the Ollama server** (runs in the background):
```bash
ollama serve
```

Ollama listens on `http://localhost:11434` by default.

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

EXTRACT_FPS=2             # Frames per second to extract
MAX_FRAMES=60             # Max frames per video
DEFAULT_STYLE=professional

# Ollama settings (local LLM — no API key needed)
LLM_PROVIDER=ollama
LLM_MODEL=gemma:7b
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_VISION_MODEL=llava:latest

# Text-to-Speech
TTS_PROVIDER=gtts         # "gtts" (free) or "openai" (needs OPENAI_API_KEY)
TTS_VOICE=nova            # Only used when TTS_PROVIDER=openai
```

> **Note:** No API keys are required when using Ollama. Just make sure `ollama serve` is running and the models are pulled before starting the backend.

---

## Running the App

### 0. Start Ollama (required first)

```bash
ollama serve
```

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
Ollama    →  http://localhost:11434
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

### Ollama

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama server
ollama serve

# Pull the text model
ollama pull gemma:7b

# Pull the vision model
ollama pull llava:latest

# List downloaded models
ollama list

# Remove a model
ollama rm gemma:7b

# Run a model interactively (test it)
ollama run gemma:7b

# Check Ollama API health
curl http://localhost:11434/api/tags

# Generate text via Ollama API directly
curl http://localhost:11434/api/generate \
  -d '{"model": "gemma:7b", "prompt": "Hello, world!", "stream": false}'
```

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

1. Start Ollama: `ollama serve`
2. Open `http://localhost:5173` in your browser
3. Upload a cricket video clip
4. Enter player names (optional) and choose commentary style
5. Click **Process**
6. Watch the real-time progress bar
7. Download or play the final commentary video

---

## Troubleshooting

### Commentary generation fails
Make sure Ollama is running and the models are downloaded:
```bash
ollama serve
ollama pull gemma:7b
ollama pull llava:latest

# Verify Ollama is reachable
curl http://localhost:11434/api/tags
```

### Ollama connection refused
If you see `Connection refused` on port `11434`, start the Ollama server:
```bash
ollama serve
```

### Model not found error
Pull the missing model:
```bash
ollama pull gemma:7b
ollama pull llava:latest
```

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

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI + Uvicorn |
| Computer Vision | OpenCV + YOLOv8 (Ultralytics) |
| AI Commentary | Ollama (`gemma:7b`) |
| Vision Analysis | Ollama (`llava:latest`) |
| Text-to-Speech | gTTS (free) |
| Video Composition | ffmpeg |
| Frontend | React 18 + Vite |
| Deep Learning | PyTorch + TorchVision |

---

## License

MIT License — see [LICENSE](LICENSE) for details.
