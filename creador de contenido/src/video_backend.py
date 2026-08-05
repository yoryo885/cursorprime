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


def _mock_clip_from_pair(start: Path, end: Path, out_clip: Path, duration: float = 4.0) -> tuple[bool, str]:
    """Motion de personaje corto: Ken Burns + crossfade (~duration segundos)."""
    ffmpeg = _ffmpeg()
    if not ffmpeg:
        return False, "ffmpeg no instalado"
    if not start.exists() or not end.exists():
        return False, f"frames faltantes: {start.name}, {end.name}"

    out_clip.parent.mkdir(parents=True, exist_ok=True)
    half = max(1.8, duration / 2)
    # frames totales por tramo (24 fps)
    d = max(36, int(half * 24))
    offset = max(0.3, half - 0.6)

    def ken(label_in: str, label_out: str, zoom_dir: str) -> str:
        # zoom_dir: "in" crece, "out" parte más cerca
        if zoom_dir == "in":
            z = "min(1.0+0.0018*on,1.12)"
        else:
            z = "max(1.12-0.0018*on,1.0)"
        return (
            f"[{label_in}]scale=1200:2133:force_original_aspect_ratio=increase,"
            f"crop=1200:2133,"
            f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={d}:s=1080x1920:fps=24,format=yuv420p[{label_out}];"
        )

    filt = (
        ken("0:v", "v0", "in")
        + ken("1:v", "v1", "out")
        + f"[v0][v1]xfade=transition=fade:duration=0.6:offset={offset},format=yuv420p[vout]"
    )
    cmd = [
        ffmpeg, "-y",
        "-loop", "1", "-i", str(start.resolve()),
        "-loop", "1", "-i", str(end.resolve()),
        "-filter_complex", filt,
        "-map", "[vout]",
        "-t", f"{duration:.2f}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "24",
        "-movflags", "+faststart",
        str(out_clip),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        cmd2 = [
            ffmpeg, "-y",
            "-loop", "1", "-t", str(half), "-i", str(start.resolve()),
            "-loop", "1", "-t", str(half), "-i", str(end.resolve()),
            "-filter_complex",
            (
                f"[0]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[a];"
                f"[1]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[b];"
                f"[a][b]xfade=transition=fade:duration=0.7:offset={offset},format=yuv420p"
            ),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            str(out_clip),
        ]
        proc2 = subprocess.run(cmd2, capture_output=True, text=True)
        if proc2.returncode != 0:
            return False, (proc.stderr or proc2.stderr)[:400]
    # sanity: no clips enormes
    try:
        import json as _json
        probe = subprocess.run(
            [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "json", str(out_clip),
            ],
            capture_output=True,
            text=True,
        )
        dur = float((_json.loads(probe.stdout).get("format") or {}).get("duration") or 0)
        if dur > duration * 3:
            # forzar recorte
            tmp = out_clip.with_suffix(".tmp.mp4")
            subprocess.run(
                [
                    ffmpeg, "-y", "-i", str(out_clip), "-t", f"{duration:.2f}",
                    "-c", "copy", str(tmp),
                ],
                capture_output=True,
            )
            if tmp.exists():
                tmp.replace(out_clip)
    except Exception:
        pass
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
