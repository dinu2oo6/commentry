"""Video Composer — Merge generated commentary audio onto original video using ffmpeg."""

import shutil
import subprocess
from pathlib import Path

from config import OUTPUT_DIR


class VideoComposer:
    """Merge TTS audio track onto the original video to produce final output."""

    def __init__(self):
        self.ffmpeg = self._resolve_ffmpeg()
        self.output_dir = OUTPUT_DIR / "videos"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _resolve_ffmpeg(self) -> str | None:
        """Resolve ffmpeg path dynamically, including common macOS locations."""
        candidates = [
            shutil.which("ffmpeg"),
            "/opt/homebrew/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            "/usr/bin/ffmpeg",
        ]

        for candidate in candidates:
            if candidate and Path(candidate).exists():
                return candidate
        return None

    @property
    def available(self) -> bool:
        return self._resolve_ffmpeg() is not None

    def compose(
        self,
        video_path: str,
        audio_path: str,
        job_id: str,
        keep_original_audio: bool = False,
        original_volume: float = 0.15,
    ) -> dict:
        """
        Merge audio onto video.

        Args:
            video_path: Path to the original video.
            audio_path: Path to the commentary MP3.
            job_id: Job identifier.
            keep_original_audio: Mix original audio at lower volume.
            original_volume: Volume of original audio when mixing (0-1).

        Returns:
            Dict with output path and metadata.
        """
        ffmpeg = self._resolve_ffmpeg()
        self.ffmpeg = ffmpeg

        if not ffmpeg:
            return {"error": "ffmpeg not installed or not found in PATH", "path": None}

        if not Path(video_path).exists():
            return {"error": f"Video not found: {video_path}", "path": None}
        if not Path(audio_path).exists():
            return {"error": f"Audio not found: {audio_path}", "path": None}

        output_filename = f"{job_id}_commentary.mp4"
        output_path = self.output_dir / output_filename

        try:

            def _build_replace_cmd() -> list[str]:
                return [
                    ffmpeg,
                    "-y",
                    "-i",
                    video_path,
                    "-i",
                    audio_path,
                    "-map",
                    "0:v",
                    "-map",
                    "1:a",
                    "-c:v",
                    "copy",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "192k",
                    "-shortest",
                    str(output_path),
                ]

            def _build_mix_cmd() -> list[str]:
                return [
                    ffmpeg,
                    "-y",
                    "-i",
                    video_path,
                    "-i",
                    audio_path,
                    "-filter_complex",
                    f"[0:a]volume={original_volume}[orig];"
                    f"[1:a]volume=1.0[comm];"
                    f"[orig][comm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
                    "-map",
                    "0:v",
                    "-map",
                    "[aout]",
                    "-c:v",
                    "copy",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "192k",
                    "-shortest",
                    str(output_path),
                ]

            mix_error = None
            if keep_original_audio:
                result = subprocess.run(
                    _build_mix_cmd(),
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                if result.returncode == 0 and output_path.exists():
                    size = output_path.stat().st_size
                    return {
                        "path": str(output_path),
                        "filename": output_filename,
                        "size_bytes": size,
                        "size_mb": round(size / (1024 * 1024), 2),
                        "mixed_audio": True,
                    }
                mix_error = (result.stderr or result.stdout or "")[-300:]

            result = subprocess.run(
                _build_replace_cmd(),
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode != 0 or not output_path.exists():
                error_msg = (
                    f"ffmpeg failed: {(result.stderr or result.stdout or '')[-300:]}"
                )
                if mix_error:
                    error_msg = f"mix failed: {mix_error} | replace failed: {(result.stderr or result.stdout or '')[-300:]}"
                return {
                    "error": error_msg,
                    "path": None,
                }

            size = output_path.stat().st_size
            response = {
                "path": str(output_path),
                "filename": output_filename,
                "size_bytes": size,
                "size_mb": round(size / (1024 * 1024), 2),
                "mixed_audio": False,
            }
            if mix_error:
                response["warning"] = (
                    f"Original-audio mix failed, fell back to commentary-only track: {mix_error}"
                )
            return response

        except subprocess.TimeoutExpired:
            return {"error": "ffmpeg timed out (>120s)", "path": None}
        except Exception as e:
            return {"error": str(e), "path": None}
