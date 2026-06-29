"""Backends de video: slideshow (ffmpeg concat) y animado (Kling/mock)."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

MOCK_KLING = os.getenv("MOCK_KLING", "true").lower() in ("1", "true", "yes")
KIE_API_KEY = os.getenv("KIE_API_KEY", "")
KIE_API_URL = os.getenv(
    "KIE_API_URL",
    "https://api.kie.ai/api/v1/jobs/createTask",
)


def _ffmpeg() -> str | None:
    return shutil.which("ffmpeg")


def slideshow_from_pngs(png_paths: list[Path], out_mp4: Path, fps: int = 2) -> tuple[bool, str]:
    ffmpeg = _ffmpeg()
    if not ffmpeg:
        return False, "ffmpeg no instalado (brew install ffmpeg)"
    if not png_paths:
        return False, "sin PNG para slideshow"

    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    list_file = out_mp4.parent / "_concat_slideshow.txt"
    list_file.write_text(
        "\n".join(f"file '{p.resolve()}'\nduration {1/fps}" for p in png_paths),
        encoding="utf-8",
    )
    cmd = [
        ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-vf", f"fps={fps},format=yuv420p", "-c:v", "libx264", str(out_mp4),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    list_file.unlink(missing_ok=True)
    if proc.returncode != 0:
        return False, proc.stderr[:300]
    return True, out_mp4.name


def _mock_clip_from_pair(start: Path, end: Path, out_clip: Path, duration: float = 3.0) -> tuple[bool, str]:
    """Simula Kling: crossfade entre frame inicio y fin."""
    ffmpeg = _ffmpeg()
    if not ffmpeg:
        return False, "ffmpeg no instalado"
    if not start.exists() or not end.exists():
        return False, f"frames faltantes: {start.name}, {end.name}"

    out_clip.parent.mkdir(parents=True, exist_ok=True)
    half = duration / 2
    offset = max(0.1, half - 0.5)
    cmd = [
        ffmpeg, "-y",
        "-loop", "1", "-t", str(half), "-i", str(start.resolve()),
        "-loop", "1", "-t", str(half), "-i", str(end.resolve()),
        "-filter_complex",
        f"[0][1]xfade=transition=fade:duration=0.8:offset={offset},format=yuv420p",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out_clip),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return False, proc.stderr[:300]
    return True, out_clip.name


def _kling_via_kie(start: Path, end: Path, prompt: str, out_clip: Path) -> tuple[bool, str]:
    if not KIE_API_KEY:
        return False, "KIE_API_KEY no configurada — usa MOCK_KLING=true"
    # Kie requiere URLs públicas; sin Cloudinary usamos mock como fallback documentado
    return False, "Kie/Kling requiere URLs públicas (Cloudinary) — pendiente V1; usando mock"


def animate_pair(
    start: Path,
    end: Path,
    prompt: str,
    out_clip: Path,
    mock: bool | None = None,
) -> tuple[bool, str, bool]:
    """Retorna (ok, mensaje, fue_mock)."""
    use_mock = MOCK_KLING if mock is None else mock
    if use_mock:
        ok, msg = _mock_clip_from_pair(start, end, out_clip)
        return ok, msg, True
    ok, msg = _kling_via_kie(start, end, prompt, out_clip)
    if ok:
        return True, msg, False
    ok2, msg2 = _mock_clip_from_pair(start, end, out_clip)
    return ok2, f"{msg} → fallback mock: {msg2}", True


def concat_clips(clips: list[Path], out_mp4: Path) -> tuple[bool, str]:
    ffmpeg = _ffmpeg()
    if not ffmpeg:
        return False, "ffmpeg no instalado"
    if not clips:
        return False, "sin clips"
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    list_file = out_mp4.parent / "_concat_clips.txt"
    list_file.write_text("\n".join(f"file '{c.resolve()}'" for c in clips), encoding="utf-8")
    cmd = [
        ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-c", "copy", str(out_mp4),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    list_file.unlink(missing_ok=True)
    if proc.returncode != 0:
        return False, proc.stderr[:300]
    return True, out_mp4.name
