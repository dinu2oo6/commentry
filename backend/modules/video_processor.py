"""Video Processing — Extract frames from video at configurable FPS using OpenCV."""

import base64
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple
from config import EXTRACT_FPS, MAX_FRAMES, FRAME_DIR


class VideoProcessor:
    """Extracts frames from cricket match videos."""

    def __init__(self, fps: int = EXTRACT_FPS, max_frames: int = MAX_FRAMES):
        self.fps = fps
        self.max_frames = max_frames

    def extract_frames(self, video_path: str, job_id: str) -> dict:
        """
        Extract frames at configured FPS.
        Returns metadata + list of base64-encoded JPEG frames.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        video_fps = cap.get(cv2.CAP_PROP_FPS) or 30
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / video_fps if video_fps else 0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Calculate frame sampling interval
        sample_interval = max(1, int(video_fps / self.fps))
        frame_dir = FRAME_DIR / job_id
        frame_dir.mkdir(parents=True, exist_ok=True)

        frames: List[dict] = []
        frame_idx = 0
        extracted = 0

        while cap.isOpened() and extracted < self.max_frames:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % sample_interval == 0:
                # Resize for efficiency (max 768px wide)
                if frame.shape[1] > 768:
                    scale = 768 / frame.shape[1]
                    frame = cv2.resize(frame, None, fx=scale, fy=scale)

                # Encode to JPEG
                _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                b64 = base64.b64encode(buffer).decode("utf-8")

                timestamp = frame_idx / video_fps
                frame_path = frame_dir / f"frame_{extracted:04d}.jpg"
                cv2.imwrite(str(frame_path), frame)

                frames.append({
                    "index": extracted,
                    "timestamp": round(timestamp, 2),
                    "base64": b64,
                    "path": str(frame_path),
                })
                extracted += 1

            frame_idx += 1

        cap.release()

        return {
            "job_id": job_id,
            "video_path": video_path,
            "duration": round(duration, 2),
            "original_fps": round(video_fps, 2),
            "width": width,
            "height": height,
            "total_original_frames": total_frames,
            "extracted_frames": len(frames),
            "frames": frames,
        }

    def get_frames_for_llm(self, frames_data: dict, every_n: int = 5) -> List[str]:
        """Return subset of base64 frames for LLM vision input."""
        all_frames = frames_data.get("frames", [])
        return [f["base64"] for f in all_frames[::every_n]]
