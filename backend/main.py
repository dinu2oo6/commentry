"""CricComment AI — FastAPI Backend Application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import AUDIO_DIR
from routes.api import router as api_router

app = FastAPI(
    title="CricComment AI",
    description="AI-powered cricket commentary system",
    version="1.0.0",
)

# ── CORS ──────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files (generated audio) ───────────────────────────────────
app.mount("/static/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")

# ── Routes ────────────────────────────────────────────────────────────
app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "name": "CricComment AI",
        "version": "1.0.0",
        "description": "AI-powered cricket commentary system",
        "endpoints": {
            "health": "/api/health",
            "upload": "POST /api/upload-video",
            "process": "POST /api/process-video",
            "results": "GET /api/results/{job_id}",
            "audio": "GET /api/audio/{filename}",
            "stream": "WS /api/stream/{job_id}",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
