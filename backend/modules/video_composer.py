"""Video Composer — Merge commentary audio onto video with precise sync via ffmpeg."""

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from config import OUTPUT_DIR


class VideoComposer:
    """Merge TTS audio track onto the original video with frame-accurate sync."""

    def __init__(self):
        self.output_dir = OUTPUT_DIR / "videos"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _resolve_bin(self, name: str) -> str | None:
        candidates = [
            shutil.which(name),
            f"/opt/homebrew/bin/{name}",
            f"/usr/local/bin/{name}",
            f"/usr/bin/{name}",
        ]
        return next((c for c in candidates if c and Path(c).exists()), None)

    @property
    def ffmpeg(self) -> str | None:
        return self._resolve_bin("ffmpeg")

    @property
    def ffprobe(self) -> str | None:
        return self._resolve_bin("ffprobe")

    @property
    def available(self) -> bool:
        return self.ffmpeg is not None

    def _get_duration(self, path: str) -> float | None:
        """Return duration in seconds using ffprobe, or None on failure."""
        fp = self.ffprobe
        if not fp:
            return None
        try:
            result = subprocess.run(
                [fp, "-v", "quiet", "-print_format", "json", "-show_format", path],
                capture_output=True, text=True, timeout=15,
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return float(data["format"]["duration"])
        except Exception:
            pass
        return None

    def _trim_audio(self, audio_path: str, duration: float, ffmpeg: str) -> str:
        """Trim and fade-out audio so it fits the video exactly. Returns path to trimmed file."""
        audio_dur = self._get_duration(audio_path)
        if audio_dur is None or audio_dur <= duration:
            return audio_path  # No trim needed

        fade_start = max(0.0, duration - 2.5)
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        tmp.close()
        trimmed = tmp.name

        result = subprocess.run(
            [
                ffmpeg, "-y", "-i", audio_path,
                "-t", str(duration),
                "-af", f"afade=t=out:st={fade_start:.2f}:d=2.0",
                trimmed,
            ],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0 and Path(trimmed).stat().st_size > 0:
            return trimmed
        return audio_path  # Fall back to original if trim failed

    def compose(
        self,
        video_path: str,
        audio_path: str,
        job_id: str,
        keep_original_audio: bool = True,
        original_volume: float = 0.12,
    ) -> dict:
        """
        Merge commentary audio onto video with precise sync.

        Steps:
          1. Get video duration via ffprobe
          2. Trim/fade commentary audio to match video length
          3. Mix or replace original audio track
          4. Encode with AAC 192k + copy video stream
        """
        ffmpeg = self.ffmpeg
        if not ffmpeg:
            return {"error": "ffmpeg not installed", "path": None}

        for label, p in [("Video", video_path), ("Audio", audio_path)]:
            if not Path(p).exists():
                return {"error": f"{label} not found: {p}", "path": None}

        output_filename = f"{job_id}_commentary.mp4"
        output_path     = self.output_dir / output_filename

        # Get video duration for sync
        video_dur = self._get_duration(video_path)

        # Trim audio to video duration + gentle fade-out
        trimmed_audio = audio_path
        if video_dur:
            trimmed_audio = self._trim_audio(audio_path, video_dur, ffmpeg)

        try:
            if keep_original_audio:
                result = self._run_mix(ffmpeg, video_path, trimmed_audio, output_path, original_volume)
                if result["ok"]:
                    return self._success(output_path, output_filename, mixed=True)
                # Fall through to replace mode if mix fails
                mix_err = result["err"]
            else:
                mix_err = None

            result = self._run_replace(ffmpeg, video_path, trimmed_audio, output_path)
            if result["ok"]:
                resp = self._success(output_path, output_filename, mixed=False)
                if mix_err:
                    resp["warning"] = f"Mix failed, used replace mode: {mix_err}"
                return resp

            err = result["err"]
            if mix_err:
                err = f"mix: {mix_err} | replace: {err}"
            return {"error": f"ffmpeg failed: {err}", "path": None}

        except subprocess.TimeoutExpired:
            return {"error": "ffmpeg timed out (>120s)", "path": None}
        except Exception as e:
            return {"error": str(e), "path": None}
        finally:
            # Clean up temp trimmed file if it was created
            if trimmed_audio != audio_path:
                try:
                    Path(trimmed_audio).unlink(missing_ok=True)
                except Exception:
                    pass

    def _run_replace(self, ffmpeg, video_path, audio_path, output_path) -> dict:
        cmd = [
            ffmpeg, "-y",
            "-i", video_path,
            "-i", audio_path,
            "-map", "0:v",
            "-map", "1:a",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-af", "aresample=async=1",
            "-shortest",
            str(output_path),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        ok = r.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0
        return {"ok": ok, "err": (r.stderr or r.stdout or "")[-400:]}

    def _run_mix(self, ffmpeg, video_path, audio_path, output_path, vol) -> dict:
        cmd = [
            ffmpeg, "-y",
            "-i", video_path,
            "-i", audio_path,
            "-filter_complex",
            f"[0:a]volume={vol},aresample=async=1[orig];"
            f"[1:a]volume=1.0[comm];"
            f"[orig][comm]amix=inputs=2:duration=first:dropout_transition=3[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            str(output_path),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        ok = r.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0
        return {"ok": ok, "err": (r.stderr or r.stdout or "")[-400:]}

    def _success(self, output_path: Path, filename: str, mixed: bool) -> dict:
        size = output_path.stat().st_size
        return {
            "path":        str(output_path),
            "filename":    filename,
            "size_bytes":  size,
            "size_mb":     round(size / (1024 * 1024), 2),
            "mixed_audio": mixed,
        }
