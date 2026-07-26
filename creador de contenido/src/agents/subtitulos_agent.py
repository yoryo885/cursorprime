"""SubtitulosAgent — letras de lo que dice la voz, limpio y al ritmo.

Skill: subtitulos-burn
1) Toma guion (texto narrado)
2) Parte en palabras/chunks y reparte tiempos según narracion.mp3
3) Escribe copy/subtitulos.ass (+ .srt de respaldo)
4) Quema en videos/{slug}_subtitulado.mp4

UX (obligatorio):
- Solo las palabras (sin caja negra, sin sombra negra)
- Aparecen con la voz y desaparecen (fad in/out por chunk)
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


def _texto_plano(guion: str) -> str:
    text = re.sub(r"\s+", " ", (guion or "").strip())
    # quita etiquetas tipo "La idea central:" si vienen truncadas con …
    return text


def _words(guion: str) -> list[str]:
    text = _texto_plano(guion)
    # tokens: palabras y números con %
    toks = re.findall(
        r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+(?:[./][A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+)?%?|[…]",
        text,
    )
    # filtra puntos suspensivos sueltos
    return [t for t in toks if t and t != "…"]


def _chunk_words(words: list[str], max_words: int = 3, max_chars: int = 28) -> list[str]:
    """Agrupa 1–3 palabras para lectura móvil (aparecen/desaparecen con la voz)."""
    chunks: list[str] = []
    buf: list[str] = []
    for w in words:
        trial = (" ".join(buf + [w])).strip()
        if buf and (len(buf) >= max_words or len(trial) > max_chars):
            chunks.append(" ".join(buf))
            buf = [w]
        else:
            buf.append(w)
    if buf:
        chunks.append(" ".join(buf))
    return chunks or [" "]


def _ass_ts(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    cs = int(round(seconds * 100))
    h, rem = divmod(cs, 3600_00)
    m, rem = divmod(rem, 60_00)
    s, c = divmod(rem, 100)
    return f"{h}:{m:02d}:{s:02d}.{c:02d}"


def _srt_ts(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    ms = int(round(seconds * 1000))
    h, rem = divmod(ms, 3600_000)
    m, rem = divmod(rem, 60_000)
    s, milli = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{milli:03d}"


def _timed_chunks(chunks: list[str], duration: float) -> list[tuple[float, float, str]]:
    weights = [max(len(c), 4) for c in chunks]
    total_w = sum(weights) or 1
    usable = max(duration - 0.12, 1.0)
    gap = 0.04  # hueco para que “desaparezcan” antes del siguiente
    out: list[tuple[float, float, str]] = []
    t = 0.05
    for i, (chunk, w) in enumerate(zip(chunks, weights)):
        seg = usable * (w / total_w)
        start = t
        end = start + max(seg - gap, 0.18)
        if i == len(chunks) - 1:
            end = min(duration - 0.05, max(end, start + 0.2))
        else:
            end = min(end, duration - 0.08)
        if end <= start:
            end = start + 0.2
        out.append((start, end, chunk))
        t = end + gap
    return out


def _build_ass(chunks_timed: list[tuple[float, float, str]]) -> str:
    # Sin caja (BorderStyle=1), sin sombra, outline mínimo solo para legibilidad
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Word,Arial,64,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,2,40,40,140,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header.rstrip()]
    for start, end, text in chunks_timed:
        # fad in/out suave; solo el texto
        safe = text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")
        fad_in = 80
        fad_out = 90
        dur_ms = int((end - start) * 1000)
        if dur_ms < 280:
            fad_in = 40
            fad_out = 40
        lines.append(
            f"Dialogue: 0,{_ass_ts(start)},{_ass_ts(end)},Word,,0,0,0,,{{\\fad({fad_in},{fad_out})}}{safe}"
        )
    return "\n".join(lines) + "\n"


def _build_srt(chunks_timed: list[tuple[float, float, str]]) -> str:
    lines = []
    for i, (start, end, text) in enumerate(chunks_timed, start=1):
        lines.append(f"{i}\n{_srt_ts(start)} --> {_srt_ts(end)}\n{text}\n")
    return "\n".join(lines) + "\n"


def _burn_ass(video: Path, ass: Path, out: Path) -> tuple[bool, str]:
    ffmpeg = _ffmpeg()
    if not ffmpeg:
        return False, "ffmpeg no instalado"
    ass_esc = str(ass.resolve()).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
    # force_style refuerza: sin sombra, sin caja opaca
    style = (
        "FontName=Arial,FontSize=22,PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00000000,BackColour=&H00000000,"
        "BorderStyle=1,Outline=0,Shadow=0,Alignment=2,MarginV=70,Bold=1"
    )
    # Preferir filtro ass (respeta Style del archivo + fad)
    for vf_try in (
        f"ass='{ass_esc}'",
        f"subtitles='{ass_esc}':force_style='{style}'",
    ):
        cmd = [
            ffmpeg, "-y", "-i", str(video.resolve()),
            "-vf", vf_try,
            "-c:a", "copy",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
            "-movflags", "+faststart",
            str(out.resolve()),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode == 0:
            return True, out.name
        last_err = proc.stderr[-400:]
    return False, last_err


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

        words = _words(guion)
        if not words:
            return AgentResult(ok=False, notes="Subtitulos: sin guion/texto")

        chunks = _chunk_words(words, max_words=3, max_chars=28)
        # Usar duración de audio (voz) para timing; el video ya debería igualarla
        vid_dur = _ffprobe_duration(video) or duration
        srt_dur = duration if duration >= 1 else vid_dur
        timed = _timed_chunks(chunks, srt_dur)

        ass_path = copy_dir / "subtitulos.ass"
        srt_path = copy_dir / "subtitulos.srt"
        ass_path.write_text(_build_ass(timed), encoding="utf-8")
        srt_path.write_text(_build_srt(timed), encoding="utf-8")

        out_mp4 = videos_out / f"{ctx.slug}_subtitulado.mp4"
        ok, msg = _burn_ass(video, ass_path, out_mp4)
        warnings = []
        if not ok:
            warnings.append(f"burn-in falló (ASS/SRT listos): {msg}")
            out_mp4 = video

        payload = {
            "skill": "subtitulos-burn",
            "modo": "palabras_con_voz",
            "ass": str(ass_path),
            "srt": str(srt_path),
            "video_in": str(video),
            "video_out": str(out_mp4),
            "chunks": len(timed),
            "words": len(words),
            "duration_srt": srt_dur,
            "duration_audio": duration,
            "duration_video": vid_dur,
            "estilo": {
                "caja_negra": False,
                "sombra": False,
                "fad": True,
                "solo_palabras": True,
            },
            "burn_ok": ok,
            "generado_at": datetime.now(timezone.utc).isoformat(),
            "nota": "Chunks 1–3 palabras sincronizados a narracion.mp3; sin caja/sombra negra.",
        }
        meta = Path(ctx.paths["meta"]) / "subtitulos.json"
        save_json(meta, payload)

        if ok and out_mp4.exists():
            # Entregable canónico en la carpeta videos/ del slug
            canonical = videos_out / f"{ctx.slug}.mp4"
            try:
                data = out_mp4.read_bytes()
                canonical.write_bytes(data)
            except Exception as exc:
                warnings.append(f"copia canónica {canonical.name}: {exc}")
                data = None
            # Aliases que el operador suele abrir en Finder
            if data is not None:
                for alias_name in (
                    "pareto_5_escenas_animado.mp4",
                    "pareto_5_escenas_con_voz.mp4",
                    "pareto_final.mp4",
                    "00_VER_ESTE_pareto.mp4",
                ):
                    if "pareto" in ctx.slug or alias_name.startswith("00_"):
                        try:
                            (videos_out / alias_name).write_bytes(data)
                        except Exception as exc:
                            warnings.append(f"alias {alias_name}: {exc}")
            # También en output/ (junto a resumen/manifest)
            out_dir = Path(ctx.paths["output"])
            out_dir.mkdir(parents=True, exist_ok=True)
            out_copy = out_dir / f"{ctx.slug}.mp4"
            try:
                if data is not None:
                    out_copy.write_bytes(data)
                else:
                    out_copy.write_bytes(out_mp4.read_bytes())
            except Exception as exc:
                warnings.append(f"copia output: {exc}")

            gv = videos_meta or {}
            gv["final"] = str(canonical if canonical.exists() else out_mp4)
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
            if canonical.exists():
                gv.setdefault("videos", []).append(
                    {
                        "archivo": canonical.name,
                        "path": str(canonical),
                        "modulo": "videos",
                        "modo": "subtitulos",
                        "tipo": "final",
                    }
                )
            if ctx.paths.get("generated_videos"):
                save_json(ctx.paths["generated_videos"], gv)

            # lote apunta al archivo que el usuario espera abrir
            lote_u = load_json(ctx.paths["lote"], {}) or lote
            lote_u = {**lote_u, "video_final": canonical.name if canonical.exists() else out_mp4.name}
            save_json(ctx.paths["lote"], lote_u)
            ctx.lote = lote_u

        notes = f"Subtitulos {len(timed)} chunks ({len(words)} palabras) → {ass_path.name}"
        if ok:
            notes += f" · burn {out_mp4.name}"
            can = videos_out / f"{ctx.slug}.mp4"
            if can.exists():
                notes += f" · final {can.name}"
        return AgentResult(
            ok=True,
            artifacts=[str(ass_path), str(srt_path), str(meta)]
            + ([str(out_mp4)] if ok else [])
            + ([str(videos_out / f"{ctx.slug}.mp4")] if ok and (videos_out / f"{ctx.slug}.mp4").exists() else []),
            notes=notes,
            warnings=warnings,
        )
