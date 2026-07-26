"""SubtitulosAgent — SRT de lo que dice la voz + burn-in en el video.

Skill: subtitulos-burn
1) Toma guion (beats) o texto de narración
2) Distribuye tiempos según duración de narracion.mp3 (o del video)
3) Escribe copy/subtitulos.srt
4) Genera videos/{slug}_subtitulado.mp4 (letras en pantalla)
"""

from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from src.config import load_json, save_json
from src.paths_resolve import resolve_video_final
from src.types import AgentResult, PipelineContext
from src.video_backend import _ffmpeg


def _ffprobe_duration(path: Path) -> float:
    ffmpeg = _ffmpeg()
    if not ffmpeg:
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


def _beats_from_guion(guion: str) -> list[str]:
    parts = [p.strip() for p in re.split(r"\n\s*\n", guion or "") if p.strip()]
    if len(parts) >= 2:
        return parts
    # frases
    frases = [f.strip() for f in re.split(r"(?<=[.!?])\s+", guion or "") if f.strip()]
    return frases or [guion.strip()]


def _srt_ts(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    ms = int(round(seconds * 1000))
    h, rem = divmod(ms, 3600_000)
    m, rem = divmod(rem, 60_000)
    s, milli = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{milli:03d}"


def _build_srt(beats: list[str], duration: float) -> str:
    weights = [max(len(b), 8) for b in beats]
    total_w = sum(weights) or 1
    # deja 0.15s de margen al final
    usable = max(duration - 0.15, 1.0)
    lines = []
    t = 0.0
    for i, (beat, w) in enumerate(zip(beats, weights), start=1):
        seg = usable * (w / total_w)
        start = t
        end = min(duration - 0.05, t + seg) if i < len(beats) else duration - 0.05
        if end <= start:
            end = start + 0.4
        text = re.sub(r"\s+", " ", beat).strip()
        # líneas cortas para móvil
        if len(text) > 42:
            mid = text.rfind(" ", 0, 42)
            if mid > 10:
                text = text[:mid] + "\n" + text[mid + 1 :]
        lines.append(f"{i}\n{_srt_ts(start)} --> {_srt_ts(end)}\n{text}\n")
        t = end
    return "\n".join(lines) + "\n"


def _burn_subtitles(video: Path, srt: Path, out: Path) -> tuple[bool, str]:
    ffmpeg = _ffmpeg()
    if not ffmpeg:
        return False, "ffmpeg no instalado"
    # escape path for subtitles filter (ffmpeg)
    srt_esc = str(srt.resolve()).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
    style = (
        "FontName=Arial,FontSize=16,PrimaryColour=&H00FFFFFF,OutlineColour=&H80000000,"
        "BorderStyle=3,Outline=2,Shadow=0,Alignment=2,MarginV=60"
    )
    vf = f"subtitles='{srt_esc}':force_style='{style}'"
    cmd = [
        ffmpeg, "-y", "-i", str(video.resolve()),
        "-vf", vf,
        "-c:a", "copy",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        str(out.resolve()),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        # fallback: drawtext simple por si falta libass
        return False, proc.stderr[-400:]
    return True, out.name


class SubtitulosAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        lote = load_json(ctx.paths["lote"], {}) or ctx.lote
        context = load_json(ctx.paths["context"], {})
        guion_meta = load_json(ctx.paths.get("guion"), {}) if ctx.paths.get("guion") else {}
        guion = str(lote.get("guion") or (guion_meta or {}).get("guion") or context.get("guion") or "")
        copy_dir = Path(ctx.paths["copy_dir"])
        copy_dir.mkdir(parents=True, exist_ok=True)
        videos_out = Path(ctx.paths["videos_out"])
        videos_out.mkdir(parents=True, exist_ok=True)

        narr = copy_dir / "narracion.mp3"
        videos_meta = load_json(ctx.paths.get("generated_videos"), {}) if ctx.paths.get("generated_videos") else {}
        prefer = (lote.get("audio") or {}).get("video_path") if isinstance(lote.get("audio"), dict) else None
        prefer = prefer or lote.get("video_final")
        # Preferir video con audio si existe
        audio_mp4 = videos_out / f"{ctx.slug}_audio.mp4"
        morph = videos_out / f"{ctx.slug}_morph.mp4"
        con_voz_alias = videos_out / "pareto_5_escenas_con_voz.mp4"
        video = None
        for cand in (audio_mp4, con_voz_alias, morph):
            if cand.exists():
                video = cand
                break
        if video is None:
            video = resolve_video_final(
                videos_meta or {},
                videos_out,
                ctx.slug,
                prefer_name=Path(str(prefer)).name if prefer else None,
            )
        if video is None or not video.exists():
            return AgentResult(ok=False, notes="Subtitulos: no hay video base para quemar letras")

        duration = _ffprobe_duration(narr) if narr.exists() else 0.0
        if duration < 1:
            duration = _ffprobe_duration(video)
        if duration < 1:
            duration = 8.0

        beats = _beats_from_guion(guion)
        if not beats:
            return AgentResult(ok=False, notes="Subtitulos: sin guion/texto")

        # Si el video es mucho más corto que la narración, acota beats al video
        vid_dur = _ffprobe_duration(video) or duration
        srt_dur = min(duration, vid_dur) if vid_dur > 0 else duration
        srt_text = _build_srt(beats, srt_dur)
        srt_path = copy_dir / "subtitulos.srt"
        srt_path.write_text(srt_text, encoding="utf-8")

        out_mp4 = videos_out / f"{ctx.slug}_subtitulado.mp4"
        ok, msg = _burn_subtitles(video, srt_path, out_mp4)
        warnings = []
        if not ok:
            # deja SRT igual; no tumba el lote
            warnings.append(f"burn-in falló (SRT listo): {msg}")
            out_mp4 = video

        payload = {
            "skill": "subtitulos-burn",
            "srt": str(srt_path),
            "video_in": str(video),
            "video_out": str(out_mp4),
            "beats": len(beats),
            "duration_srt": srt_dur,
            "duration_audio": duration,
            "duration_video": vid_dur,
            "burn_ok": ok,
            "generado_at": datetime.now(timezone.utc).isoformat(),
            "nota": "Letras = beats del guion sincronizados a la duración (aprox). Mejora futura: timestamps ElevenLabs.",
        }
        meta = Path(ctx.paths["meta"]) / "subtitulos.json"
        save_json(meta, payload)

        if ok and out_mp4.exists():
            gv = videos_meta or {}
            gv["final_subtitulado"] = str(out_mp4)
            gv.setdefault("videos", []).append(
                {
                    "archivo": out_mp4.name,
                    "path": str(out_mp4),
                    "modulo": "videos",
                    "modo": "subtitulos",
                    "tipo": "final_subtitulado",
                }
            )
            if ctx.paths.get("generated_videos"):
                save_json(ctx.paths["generated_videos"], gv)

        notes = f"Subtitulos {len(beats)} beats → {srt_path.name}"
        if ok:
            notes += f" · burn {out_mp4.name}"
        return AgentResult(
            ok=True,
            artifacts=[str(srt_path), str(meta)] + ([str(out_mp4)] if ok else []),
            notes=notes,
            warnings=warnings,
        )
