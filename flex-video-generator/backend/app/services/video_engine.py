"""
FFmpeg-based video rendering engine.
Handles clip assembly, audio sync, and caption overlay.
"""

import subprocess
import logging
import shutil
from pathlib import Path
from typing import Optional
import uuid

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class VideoEngine:
    """Service for video processing and rendering."""

    def __init__(self, temp_dir: Optional[str] = None):
        """Initialize video engine with temp directory."""
        self.temp_dir = Path(temp_dir or settings.temp_path)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def _get_video_duration_ms(self, file_path: str) -> int:
        """Get video duration in milliseconds using ffprobe."""
        try:
            cmd = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            duration_sec = float(result.stdout.strip())
            return int(duration_sec * 1000)
        except Exception as e:
            logger.error(f"Error getting video duration: {e}")
            return 0

    def _get_video_info(self, file_path: str) -> dict:
        """Get video metadata using ffprobe."""
        try:
            cmd = [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height,r_frame_rate,duration",
                "-of", "json",
                file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            import json
            data = json.loads(result.stdout)
            stream = data.get("streams", [{}])[0]

            # Parse frame rate
            fps_str = stream.get("r_frame_rate", "30/1")
            if "/" in fps_str:
                num, den = fps_str.split("/")
                fps = int(num) / int(den) if int(den) != 0 else 30
            else:
                fps = float(fps_str)

            return {
                "width": stream.get("width", 1080),
                "height": stream.get("height", 1920),
                "fps": fps,
                "duration_ms": self._get_video_duration_ms(file_path)
            }
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return {"width": 1080, "height": 1920, "fps": 30, "duration_ms": 0}

    async def render_video(
        self,
        clip_sequence: list[dict],
        audio_path: str,
        caption: str,
        output_path: str,
        resolution: tuple = (1080, 1920),
        fps: int = 30
    ) -> str:
        """
        Render final video with:
        - Clips assembled in sequence
        - Audio track overlaid
        - Caption text burned in (optional)

        Returns: Path to rendered video
        """
        width, height = resolution
        job_id = str(uuid.uuid4())[:8]
        job_temp = self.temp_dir / job_id
        job_temp.mkdir(parents=True, exist_ok=True)

        try:
            # Step 1: Process each clip to exact duration and resolution
            processed_clips = []

            for i, segment in enumerate(clip_sequence):
                clip_path = segment["clip_path"]
                start_ms = segment.get("clip_start_ms", 0)
                duration_ms = segment["end_ms"] - segment["start_ms"]

                processed_path = job_temp / f"clip_{i}.mp4"

                cmd = [
                    "ffmpeg", "-y",
                    "-ss", str(start_ms / 1000),
                    "-i", clip_path,
                    "-t", str(duration_ms / 1000),
                    "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1",
                    "-r", str(fps),
                    "-an",  # Remove audio from clips
                    "-c:v", "libx264",
                    "-preset", "fast",
                    "-pix_fmt", "yuv420p",
                    str(processed_path)
                ]

                logger.info(f"Processing clip {i}: {clip_path}")
                subprocess.run(cmd, check=True, capture_output=True)
                processed_clips.append(processed_path)

            # Step 2: Create concat file for FFmpeg
            concat_file = job_temp / "concat.txt"
            with open(concat_file, "w") as f:
                for clip in processed_clips:
                    f.write(f"file '{clip}'\n")

            # Step 3: Concatenate all clips
            concat_output = job_temp / "concat_output.mp4"
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_file),
                "-c", "copy",
                str(concat_output)
            ]
            logger.info("Concatenating clips")
            subprocess.run(cmd, check=True, capture_output=True)

            # Step 4: Add audio
            with_audio = job_temp / "with_audio.mp4"
            cmd = [
                "ffmpeg", "-y",
                "-i", str(concat_output),
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                str(with_audio)
            ]
            logger.info("Adding audio")
            subprocess.run(cmd, check=True, capture_output=True)

            # Step 5: Add caption overlay (if caption provided)
            if caption and caption.strip():
                # Escape special characters for FFmpeg drawtext
                escaped_caption = self._escape_ffmpeg_text(caption)

                # Caption styling
                drawtext_filter = (
                    f"drawtext=text='{escaped_caption}':"
                    f"fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                    f"fontsize=42:"
                    f"fontcolor=white:"
                    f"borderw=3:"
                    f"bordercolor=black:"
                    f"x=(w-text_w)/2:"
                    f"y=h-th-200:"
                    f"line_spacing=10"
                )

                cmd = [
                    "ffmpeg", "-y",
                    "-i", str(with_audio),
                    "-vf", drawtext_filter,
                    "-c:a", "copy",
                    output_path
                ]
                logger.info("Adding caption overlay")
                subprocess.run(cmd, check=True, capture_output=True)
            else:
                # No caption, just copy
                shutil.copy(with_audio, output_path)

            logger.info(f"Video rendered successfully: {output_path}")
            return output_path

        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
            raise RuntimeError(f"Video rendering failed: {e}")
        finally:
            # Cleanup temp files
            try:
                shutil.rmtree(job_temp)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp files: {e}")

    def _escape_ffmpeg_text(self, text: str) -> str:
        """Escape special characters for FFmpeg drawtext filter."""
        # Replace special characters
        text = text.replace("\\", "\\\\")
        text = text.replace("'", "'\\''")
        text = text.replace(":", "\\:")
        text = text.replace("[", "\\[")
        text = text.replace("]", "\\]")
        text = text.replace("%", "\\%")
        return text

    async def generate_thumbnail(
        self,
        video_path: str,
        output_path: str,
        timestamp_sec: float = 0.5
    ) -> str:
        """Extract thumbnail from video."""
        try:
            cmd = [
                "ffmpeg", "-y",
                "-ss", str(timestamp_sec),
                "-i", video_path,
                "-vframes", "1",
                "-q:v", "2",
                output_path
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error generating thumbnail: {e}")
            raise RuntimeError(f"Thumbnail generation failed: {e}")

    async def extract_audio_waveform(
        self,
        audio_path: str,
        output_path: str,
        width: int = 1800,
        height: int = 140
    ) -> str:
        """Generate waveform image from audio file."""
        try:
            cmd = [
                "ffmpeg", "-y",
                "-i", audio_path,
                "-filter_complex",
                f"showwavespic=s={width}x{height}:colors=#3182ce",
                "-frames:v", "1",
                output_path
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error generating waveform: {e}")
            raise RuntimeError(f"Waveform generation failed: {e}")

    async def get_audio_duration_ms(self, audio_path: str) -> int:
        """Get audio duration in milliseconds."""
        return self._get_video_duration_ms(audio_path)
