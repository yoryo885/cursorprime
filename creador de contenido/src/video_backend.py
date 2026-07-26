"""Backends de video: slideshow, animado mock (crossfade) y Kling real vía Kie.ai."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

MOCK_KLING = os.getenv("MOCK_KLING", "true").lower() in ("1", "true", "yes", "on")
KIE_API_KEY = os.getenv("KIE_API_KEY", "")
KIE_API_URL = os.getenv("KIE_API_URL", "https://api.kie.ai/api/v1/jobs/createTask")
KIE_RECORD_URL = os.getenv("KIE_RECORD_URL", "https://api.kie.ai/api/v1/jobs/recordInfo")
KIE_KLING_MODEL = os.getenv("KIE_KLING_MODEL", "kling-2.6/image-to-video")
KIE_DURATION = os.getenv("KIE_DURATION", "5")  # 5 | 10
KIE_POLL_SECONDS = float(os.getenv("KIE_POLL_SECONDS", "4"))
KIE_POLL_MAX = int(os.getenv("KIE_POLL_MAX", "45"))
CLOUDINARY_URL = os.getenv("CLOUDINARY_URL", "")  # cloudinary://key:secret@cloud


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
    """Simula Kling: crossfade entre frame inicio y fin (juntar imágenes con movimiento)."""
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


def _parse_cloudinary() -> tuple[str, str, str] | None:
    """cloudinary://api_key:api_secret@cloud_name"""
    raw = CLOUDINARY_URL.strip()
    if not raw.startswith("cloudinary://"):
        return None
    try:
        rest = raw[len("cloudinary://") :]
        creds, cloud = rest.split("@", 1)
        key, secret = creds.split(":", 1)
        return key, secret, cloud
    except ValueError:
        return None


def upload_public_url(image_path: Path) -> str:
    """Sube PNG a Cloudinary y devuelve URL pública HTTPS."""
    parsed = _parse_cloudinary()
    if not parsed:
        raise RuntimeError("CLOUDINARY_URL no configurada (cloudinary://key:secret@cloud)")
    api_key, api_secret, cloud = parsed
    boundary = "----CursorPrimeForm"
    data = image_path.read_bytes()
    parts = []
    for name, value in (("file", None), ("api_key", api_key), ("upload_preset", None)):
        pass
    # Signed upload with timestamp + signature would need hashlib; use unsigned if preset set
    upload_preset = os.getenv("CLOUDINARY_UPLOAD_PRESET", "")
    if upload_preset:
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{image_path.name}"\r\n'
            f"Content-Type: image/png\r\n\r\n"
        ).encode() + data + (
            f"\r\n--{boundary}\r\n"
            f'Content-Disposition: form-data; name="upload_preset"\r\n\r\n{upload_preset}\r\n'
            f"--{boundary}--\r\n"
        ).encode()
        url = f"https://api.cloudinary.com/v1_1/{cloud}/image/upload"
        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        secure = payload.get("secure_url") or payload.get("url")
        if not secure:
            raise RuntimeError(f"Cloudinary sin URL: {payload}")
        return secure

    # Signed basic upload
    import hashlib
    import time as _t

    timestamp = str(int(_t.time()))
    to_sign = f"timestamp={timestamp}{api_secret}"
    signature = hashlib.sha1(to_sign.encode()).hexdigest()
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{image_path.name}"\r\n'
        f"Content-Type: image/png\r\n\r\n"
    ).encode() + data + (
        f"\r\n--{boundary}\r\n"
        f'Content-Disposition: form-data; name="api_key"\r\n\r\n{api_key}\r\n'
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="timestamp"\r\n\r\n{timestamp}\r\n'
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="signature"\r\n\r\n{signature}\r\n'
        f"--{boundary}--\r\n"
    ).encode()
    url = f"https://api.cloudinary.com/v1_1/{cloud}/image/upload"
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    secure = payload.get("secure_url") or payload.get("url")
    if not secure:
        raise RuntimeError(f"Cloudinary sin URL: {payload}")
    return secure


def _kie_headers() -> dict:
    return {
        "Authorization": f"Bearer {KIE_API_KEY}",
        "Content-Type": "application/json",
    }


def _kie_create(image_url: str, prompt: str) -> str:
    body = {
        "model": KIE_KLING_MODEL,
        "input": {
            "prompt": (prompt or "Subtle cinematic motion")[:1000],
            "image_urls": [image_url],
            "sound": False,
            "duration": KIE_DURATION if KIE_DURATION in ("5", "10") else "5",
        },
    }
    req = urllib.request.Request(
        KIE_API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers=_kie_headers(),
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    task_id = (payload.get("data") or {}).get("taskId") or payload.get("taskId")
    if not task_id:
        raise RuntimeError(f"Kie createTask sin taskId: {payload}")
    return str(task_id)


def _kie_poll(task_id: str) -> str:
    """Devuelve URL del video cuando state=success."""
    for _ in range(KIE_POLL_MAX):
        url = f"{KIE_RECORD_URL}?{urllib.parse.urlencode({'taskId': task_id})}"
        req = urllib.request.Request(url, headers=_kie_headers(), method="GET")
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        data = payload.get("data") or {}
        state = data.get("state") or ""
        if state == "success":
            result_raw = data.get("resultJson") or "{}"
            result = json.loads(result_raw) if isinstance(result_raw, str) else result_raw
            urls = result.get("resultUrls") or []
            if not urls:
                raise RuntimeError(f"Kie success sin resultUrls: {result}")
            return urls[0]
        if state == "fail":
            raise RuntimeError(f"Kie fail: {data.get('failMsg') or data.get('failCode')}")
        time.sleep(KIE_POLL_SECONDS)
    raise RuntimeError(f"Kie timeout tras {KIE_POLL_MAX} polls (taskId={task_id})")


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=180) as resp:
        dest.write_bytes(resp.read())


def _kling_via_kie(start: Path, end: Path, prompt: str, out_clip: Path) -> tuple[bool, str]:
    """Image-to-video: sube frame inicio → Kling. end se usa solo como hint en prompt."""
    if not KIE_API_KEY:
        return False, "KIE_API_KEY no configurada"
    try:
        image_url = upload_public_url(start)
    except Exception as exc:
        return False, f"Upload público falló: {exc}"

    full_prompt = prompt or "Smooth subtle motion, professional, clean"
    if end and end.exists():
        full_prompt = f"{full_prompt}. Evolve toward a related end composition."

    try:
        task_id = _kie_create(image_url, full_prompt)
        video_url = _kie_poll(task_id)
        _download(video_url, out_clip)
        return True, f"kling:{task_id}"
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")[:200]
        return False, f"Kie HTTP {exc.code}: {detail}"
    except Exception as exc:
        return False, f"Kie error: {exc}"


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


def _ffprobe_duration_sec(path: Path) -> float:
    ffmpeg = _ffmpeg()
    if not ffmpeg or not path.exists():
        return 0.0
    ffprobe = Path(ffmpeg).with_name("ffprobe")
    bin_ = str(ffprobe) if ffprobe.exists() else "ffprobe"
    try:
        out = subprocess.check_output(
            [bin_, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            text=True,
        ).strip()
        return float(out)
    except Exception:
        return 0.0


def mux_audio_bed(video_path: Path, audio_path: Path, out_path: Path) -> tuple[bool, str]:
    """Junta video + voz/cama. La voz manda: si el video es más corto, congela el último frame."""
    ffmpeg = _ffmpeg()
    if not ffmpeg:
        return False, "ffmpeg no instalado"
    if not video_path.exists():
        return False, "video no existe"
    if not audio_path.exists():
        return False, "audio no existe"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    v_dur = _ffprobe_duration_sec(video_path)
    a_dur = _ffprobe_duration_sec(audio_path)
    # Narración no se loopea (evitar eco). Si el video es corto → tpad clone.
    if a_dur > 0.5 and v_dur > 0 and a_dur > v_dur + 0.08:
        pad = a_dur - v_dur
        cmd = [
            ffmpeg, "-y",
            "-i", str(video_path.resolve()),
            "-i", str(audio_path.resolve()),
            "-filter_complex",
            f"[0:v]tpad=stop_mode=clone:stop_duration={pad:.3f},format=yuv420p[v]",
            "-map", "[v]", "-map", "1:a:0",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac",
            "-t", f"{a_dur:.3f}",
            "-movflags", "+faststart",
            str(out_path),
        ]
    else:
        # Video ≥ audio (o duraciones desconocidas): corta al más corto sin loop de voz
        cmd = [
            ffmpeg, "-y",
            "-i", str(video_path.resolve()),
            "-i", str(audio_path.resolve()),
            "-c:v", "copy",
            "-c:a", "aac",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            "-movflags", "+faststart",
            str(out_path),
        ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return False, proc.stderr[:300]
    return True, out_path.name
