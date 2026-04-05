"""API Routes — REST + WebSocket endpoints for CricComment AI."""

import asyncio
import os
import sys
import uuid
from pathlib import Path
from typing import Dict

from fastapi import APIRouter, File, Form, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import AUDIO_DIR, OUTPUT_DIR, VIDEO_DIR
from modules.commentary_generator import CommentaryGenerator
from modules.context_engine import ContextEngine
from modules.event_detector import EventDetector
from modules.shot_classifier import ShotClassifier
from modules.tts_engine import TTSEngine
from modules.video_composer import VideoComposer
from modules.video_processor import VideoProcessor

router = APIRouter(prefix="/api")

# ── In-memory job store ───────────────────────────────────────────────
jobs: Dict[str, dict] = {}

# ── Module instances ──────────────────────────────────────────────────
video_processor = VideoProcessor()
event_detector = EventDetector()
shot_classifier = ShotClassifier()
commentary_generator = CommentaryGenerator()
tts_engine = TTSEngine()
video_composer = VideoComposer()


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "CricComment AI"}


@router.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    """Upload a video file for processing."""
    job_id = uuid.uuid4().hex[:12]
    ext = Path(file.filename or "video.mp4").suffix or ".mp4"
    video_path = VIDEO_DIR / f"{job_id}{ext}"

    content = await file.read()
    with open(video_path, "wb") as f:
        f.write(content)

    jobs[job_id] = {
        "id": job_id,
        "status": "uploaded",
        "video_path": str(video_path),
        "filename": file.filename,
        "size_bytes": len(content),
        "progress": 0,
        "step": "uploaded",
        "results": None,
    }

    return {"job_id": job_id, "status": "uploaded", "filename": file.filename}


@router.post("/process-video")
async def process_video(
    job_id: str = Form(...),
    style: str = Form("professional"),
    batsman: str = Form("Batsman"),
    bowler: str = Form("Bowler"),
):
    """Start the full processing pipeline for an uploaded video."""
    if job_id not in jobs:
        return JSONResponse(status_code=404, content={"error": "Job not found"})

    job = jobs[job_id]
    if job["status"] == "processing":
        return {"job_id": job_id, "status": "already_processing"}

    # Run pipeline in background
    asyncio.create_task(_run_pipeline(job_id, style, batsman, bowler))

    return {"job_id": job_id, "status": "processing"}


async def _run_pipeline(job_id: str, style: str, batsman: str, bowler: str):
    """Execute the full pipeline asynchronously."""
    job = jobs[job_id]
    try:
        # 1. Frame extraction
        job["status"] = "processing"
        job["step"] = "extracting_frames"
        job["progress"] = 10

        loop = asyncio.get_event_loop()
        frames_data = await loop.run_in_executor(
            None, video_processor.extract_frames, job["video_path"], job_id
        )
        job["progress"] = 30

        # 2. Event detection
        job["step"] = "detecting_events"
        events = await loop.run_in_executor(
            None, event_detector.analyze_sequence, frames_data
        )
        job["progress"] = 50

        # 3. Context + Commentary
        job["step"] = "generating_commentary"
        commentary_generator.set_style(style)
        context_engine = ContextEngine()
        context_engine.set_players(batsman, bowler)

        commentary_items = await loop.run_in_executor(
            None, commentary_generator.generate_batch, events, context_engine
        )
        job["progress"] = 70

        # 4. TTS
        job["step"] = "generating_audio"
        tts_result = await loop.run_in_executor(
            None, tts_engine.synthesize_full, commentary_items, job_id
        )
        job["progress"] = 80

        # 5. Compose final video (audio + video merge)
        composed_video = {}
        full_audio = tts_result.get("full_audio", {})
        audio_path = full_audio.get("path")
        if audio_path and video_composer.available:
            job["step"] = "composing_video"
            composed_video = await loop.run_in_executor(
                None,
                video_composer.compose,
                job["video_path"],
                audio_path,
                job_id,
                True,  # keep_original_audio
                0.15,  # original_volume
            )
        elif not audio_path:
            composed_video = {
                "error": full_audio.get("error", "Commentary audio was not generated"),
                "path": None,
            }
        else:
            composed_video = {
                "error": "Video composition skipped because ffmpeg is not available on the backend",
                "path": None,
            }
        job["progress"] = 95

        # 6. Done
        job["status"] = "completed"
        job["step"] = "done"
        job["progress"] = 100
        job["results"] = {
            "video_info": {
                "duration": frames_data.get("duration"),
                "fps": frames_data.get("original_fps"),
                "frames_extracted": frames_data.get("extracted_frames"),
            },
            "events": [
                {
                    "timestamp": e.get("timestamp"),
                    "event": e.get("event"),
                    "shot": e.get("shot"),
                    "confidence": e.get("confidence"),
                    "commentary": e.get("commentary"),
                    "score": e.get("score"),
                    "overs": e.get("overs"),
                    "run_rate": e.get("run_rate"),
                }
                for e in commentary_items
            ],
            "match_summary": context_engine.get_match_summary(),
            "audio": {
                "full": tts_result.get("full_audio", {}),
                "segments": tts_result.get("segments", []),
            },
            "final_video": composed_video,
            "style": style,
        }

    except Exception as e:
        job["status"] = "error"
        job["step"] = "failed"
        job["error"] = str(e)


@router.get("/results/{job_id}")
async def get_results(job_id: str):
    """Poll for processing results."""
    if job_id not in jobs:
        return JSONResponse(status_code=404, content={"error": "Job not found"})

    job = jobs[job_id]
    return {
        "job_id": job_id,
        "status": job["status"],
        "step": job["step"],
        "progress": job["progress"],
        "results": job.get("results"),
        "error": job.get("error"),
    }


@router.get("/audio/{filename}")
async def serve_audio(filename: str):
    """Serve generated audio files."""
    filepath = AUDIO_DIR / filename
    if not filepath.exists():
        return JSONResponse(status_code=404, content={"error": "Audio file not found"})
    return FileResponse(str(filepath), media_type="audio/mpeg", filename=filename)


@router.get("/video/{filename}")
async def serve_video(filename: str):
    """Serve the final composed video with commentary audio."""
    filepath = OUTPUT_DIR / "videos" / filename
    if not filepath.exists():
        return JSONResponse(status_code=404, content={"error": "Video file not found"})
    return FileResponse(str(filepath), media_type="video/mp4", filename=filename)


@router.websocket("/stream/{job_id}")
async def stream_progress(websocket: WebSocket, job_id: str):
    """WebSocket for real-time progress updates."""
    await websocket.accept()
    try:
        while True:
            if job_id not in jobs:
                await websocket.send_json({"error": "Job not found"})
                break

            job = jobs[job_id]
            await websocket.send_json(
                {
                    "job_id": job_id,
                    "status": job["status"],
                    "step": job["step"],
                    "progress": job["progress"],
                }
            )

            if job["status"] in ("completed", "error"):
                break

            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
