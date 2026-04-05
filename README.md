# CricComment AI

AI-powered cricket commentary generation from uploaded match videos using computer vision, LLM-based commentary generation, text-to-speech, and final video composition.

## Project Structure

```text
cric/
├── backend/
│   ├── config.py
│   ├── main.py
│   ├── requirements.txt
│   ├── modules/
│   │   ├── commentary_generator.py
│   │   ├── context_engine.py
│   │   ├── event_detector.py
│   │   ├── shot_classifier.py
│   │   ├── tts_engine.py
│   │   ├── video_composer.py
│   │   └── video_processor.py
│   ├── routes/
│   │   └── api.py
│   └── venv/
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── src/
│   └── public/
├── data/
│   ├── frames/
│   └── videos/
├── outputs/
│   ├── audio/
│   └── videos/
└── run.sh
```

## Tech Stack

### Backend
- FastAPI
- Uvicorn
- OpenCV
- PyTorch
- Ultralytics
- gTTS
- OpenAI SDK
- python-dotenv

### Frontend
- React
- Vite

### Media
- ffmpeg

## Prerequisites

Install these before running the project:

- Python 3.10+
- Node.js 18+
- npm
- ffmpeg

### Install ffmpeg

#### macOS
```bash
brew install ffmpeg
```

#### Ubuntu / Debian
```bash
sudo apt update
sudo apt install -y ffmpeg
```

### Verify ffmpeg
```bash
ffmpeg -version
which ffmpeg
```

## Backend Setup

Go to the backend directory:

```bash
cd /Users/dineshsai/Documents/cric/backend
```

Create a virtual environment if needed:

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

Install backend dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Frontend Setup

Go to the frontend directory:

```bash
cd /Users/dineshsai/Documents/cric/frontend
```

Install frontend dependencies:

```bash
npm install
```

## Environment Variables

Create a file at `backend/.env`:

```env
OPENAI_API_KEY=
EXTRACT_FPS=2
MAX_FRAMES=60
DEFAULT_STYLE=professional
LLM_MODEL=gpt-4o
TTS_PROVIDER=gtts
TTS_VOICE=nova
```

### Notes
- `OPENAI_API_KEY` is optional if you use `gTTS`
- Default TTS provider is `gtts`
- Set `TTS_PROVIDER=openai` only if you have a valid OpenAI API key

## Quick Start

From the project root:

```bash
cd /Users/dineshsai/Documents/cric
chmod +x run.sh
./run.sh
```

If executable permission is missing:

```bash
cd /Users/dineshsai/Documents/cric
bash run.sh
```

This starts:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

## Manual Run Commands

### Start Backend

Open Terminal 1:

```bash
cd /Users/dineshsai/Documents/cric/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Start Frontend

Open Terminal 2:

```bash
cd /Users/dineshsai/Documents/cric/frontend
npm run dev
```

## Application URLs

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

## Frontend Commands

From `frontend/`:

### Start development server
```bash
npm run dev
```

### Build production bundle
```bash
npm run build
```

### Preview production build
```bash
npm run preview
```

## Backend Commands

From `backend/`:

### Install dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Run development server
```bash
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

Base URL:

```text
http://localhost:8000/api
```

### Health Check
```http
GET /api/health
```

Example:
```bash
curl http://localhost:8000/api/health
```

### Upload Video
```http
POST /api/upload-video
```

Example:
```bash
curl -X POST http://localhost:8000/api/upload-video \
  -F "file=@/absolute/path/to/video.mp4"
```

### Start Processing
```http
POST /api/process-video
```

Example:
```bash
curl -X POST http://localhost:8000/api/process-video \
  -F "job_id=YOUR_JOB_ID" \
  -F "style=professional" \
  -F "batsman=Virat Kohli" \
  -F "bowler=Jasprit Bumrah"
```

### Get Results
```http
GET /api/results/{job_id}
```

Example:
```bash
curl http://localhost:8000/api/results/YOUR_JOB_ID
```

### Get Generated Audio
```http
GET /api/audio/{filename}
```

Example:
```bash
curl -O http://localhost:8000/api/audio/YOUR_AUDIO_FILE.mp3
```

### Get Final Video
```http
GET /api/video/{filename}
```

Example:
```bash
curl -O http://localhost:8000/api/video/YOUR_VIDEO_FILE.mp4
```

## Typical Workflow

1. Start backend and frontend
2. Open the frontend in your browser
3. Upload a cricket video
4. Start processing
5. Wait for:
   - frame extraction
   - event detection
   - commentary generation
   - audio generation
   - final video composition
6. Play or download the final output

## Generated Files

### Uploaded videos
Stored in:

```text
data/videos/
```

### Extracted frames
Stored in:

```text
data/frames/
```

### Generated commentary audio
Stored in:

```text
outputs/audio/
```

### Final composed videos
Stored in:

```text
outputs/videos/
```

## Troubleshooting

### 1. Final video is not generated

Check whether `ffmpeg` is installed:

```bash
ffmpeg -version
which ffmpeg
```

Restart the app after installing `ffmpeg`:

```bash
cd /Users/dineshsai/Documents/cric
./run.sh
```

Check generated output folders:

```bash
ls -la /Users/dineshsai/Documents/cric/outputs/audio
ls -la /Users/dineshsai/Documents/cric/outputs/videos
```

If audio files exist but no final video exists, stop the app, restart it, and process the video again.

### 2. Backend does not start

Run:

```bash
cd /Users/dineshsai/Documents/cric/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

If dependencies are missing:

```bash
pip install -r requirements.txt
```

### 3. Frontend does not start

Run:

```bash
cd /Users/dineshsai/Documents/cric/frontend
npm install
npm run dev
```

### 4. OpenAI TTS is not working

Make sure `backend/.env` contains:

```env
OPENAI_API_KEY=your_key_here
TTS_PROVIDER=openai
TTS_VOICE=nova
```

If the key is missing or invalid, the app can fall back to `gTTS`.

### 5. Port already in use

Check which process is using the ports:

```bash
lsof -i :8000
lsof -i :5173
```

Kill the process if needed:

```bash
kill -9 PID
```

Replace `PID` with the actual process ID.

### 6. Clean generated files

Remove generated outputs:

```bash
rm -rf /Users/dineshsai/Documents/cric/data/frames/*
rm -rf /Users/dineshsai/Documents/cric/outputs/audio/*
rm -rf /Users/dineshsai/Documents/cric/outputs/videos/*
```

## Useful Command Summary

### Run full app
```bash
cd /Users/dineshsai/Documents/cric
./run.sh
```

### Run backend
```bash
cd /Users/dineshsai/Documents/cric/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Run frontend
```bash
cd /Users/dineshsai/Documents/cric/frontend
npm run dev
```

### Install backend deps
```bash
cd /Users/dineshsai/Documents/cric/backend
source venv/bin/activate
pip install -r requirements.txt
```

### Install frontend deps
```bash
cd /Users/dineshsai/Documents/cric/frontend
npm install
```

### Build frontend
```bash
cd /Users/dineshsai/Documents/cric/frontend
npm run build
```

### Check API health
```bash
curl http://localhost:8000/api/health
```

## Notes

- Job state is currently stored in memory
- Restarting the backend clears in-memory job tracking
- Generated files remain on disk inside `data/` and `outputs/`
- If you change environment variables or install ffmpeg after startup, restart the app

## License

Add your preferred license here.