"""MorphAgent — anima escenas A→B (morph fluido) y concatena el video base.

Prioridad de frames:
1) refs/escenas/{id}_a.png + _b.png (pack visual validado)
2) imagenes/*-inicio.png + *-fin.png del PNG agent
"""

from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

from src.config import ROOT, load_json, save_json, slug_dir
from src.types import AgentResult, PipelineContext
from src.video_backend import _ffmpeg, concat_clips


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


def _pad_clip_to_duration(clip: Path, target_s: float, out: Path) -> tuple[bool, str]:
    """Congela el último frame hasta alcanzar target_s (voz manda la duración)."""
    ffmpeg = _ffmpeg()
    if not ffmpeg:
        return False, "ffmpeg no instalado"
    cur = _ffprobe_duration(clip)
    if cur <= 0:
        return False, "clip sin duración"
    if target_s <= cur + 0.05:
        out.write_bytes(clip.read_bytes())
        return True, out.name
    pad = target_s - cur
    cmd = [
        ffmpeg, "-y", "-i", str(clip),
        "-vf", f"tpad=stop_mode=clone:stop_duration={pad:.3f},format=yuv420p",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "veryfast",
        "-t", f"{target_s:.3f}",
        "-an", "-movflags", "+faststart", str(out),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return False, proc.stderr[-300:]
    return True, out.name


def _slug_num(name: str) -> str | None:
    m = re.match(r"^(\d+)_", name)
    return m.group(1) if m else None


def _pairs_from_refs(refs_dir: Path) -> list[tuple[Path, Path, str]]:
    if not refs_dir.exists():
        return []
    a_files = sorted(refs_dir.glob("*_a.png"))
    pairs = []
    for a in a_files:
        stem = a.name[: -len("_a.png")]
        b = refs_dir / f"{stem}_b.png"
        if b.exists():
            pairs.append((a, b, stem))
    return pairs


def _pairs_from_imagenes(img_dir: Path) -> list[tuple[Path, Path, str]]:
    if not img_dir.exists():
        return []
    inicios = sorted(img_dir.glob("*-inicio.png"))
    pairs = []
    for a in inicios:
        b = Path(str(a).replace("-inicio.png", "-fin.png"))
        if b.exists():
            pairs.append((a, b, a.stem.replace("-inicio", "")))
    return pairs


def _morph_clip(a: Path, b: Path, out: Path, fps: int = 24, hold: int = 8, xfade: int = 16) -> tuple[bool, str]:
    """Morph A→B con blend ease (misma técnica que el demo que gustó)."""
    ffmpeg = _ffmpeg()
    if not ffmpeg:
        return False, "ffmpeg no instalado"
    size = (1080, 1080)
    tmp = out.parent / f"_morph_tmp_{out.stem}"
    if tmp.exists():
        for old in tmp.glob("*"):
            old.unlink()
        tmp.rmdir()
    tmp.mkdir(parents=True, exist_ok=True)

    im_a = Image.open(a).convert("RGB").resize(size, Image.Resampling.LANCZOS)
    im_b = Image.open(b).convert("RGB").resize(size, Image.Resampling.LANCZOS)
    n = 0

    def save(im: Image.Image) -> None:
        nonlocal n
        im.save(tmp / f"f{n:04d}.jpg", quality=90)
        n += 1

    for _ in range(hold):
        save(im_a)
    for t in range(xfade):
        u = t / max(xfade - 1, 1)
        e = 3 * u * u - 2 * u * u * u
        save(Image.blend(im_a, im_b, e))
    for _ in range(hold):
        save(im_b)

    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg, "-y", "-framerate", str(fps), "-i", str(tmp / "f%04d.jpg"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "veryfast",
        "-movflags", "+faststart", str(out),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    for f in tmp.glob("*"):
        f.unlink()
    tmp.rmdir()
    if proc.returncode != 0:
        return False, proc.stderr[-300:]
    return True, out.name


class MorphAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        lote = load_json(ctx.paths["lote"], {}) or ctx.lote
        videos_out = Path(ctx.paths["videos_out"])
        videos_out.mkdir(parents=True, exist_ok=True)
        clips_dir = videos_out / "clips_morph"
        clips_dir.mkdir(parents=True, exist_ok=True)

        refs = slug_dir(ctx.slug) / "refs" / "escenas"
        imgs = Path(ctx.paths["imagenes_out"])
        pairs = _pairs_from_refs(refs)
        fuente = "refs/escenas"
        if not pairs:
            pairs = _pairs_from_imagenes(imgs)
            fuente = "imagenes"
        if not pairs:
            return AgentResult(
                ok=False,
                notes="Morph: sin pares A/B (pon refs/escenas/*_a.png|*_b.png o corre png animado)",
            )

        morph_cfg = lote.get("morph") if isinstance(lote.get("morph"), dict) else {}
        hold = int(morph_cfg.get("hold_frames") or 10)
        xfade = int(morph_cfg.get("xfade_frames") or 20)
        fps = int(morph_cfg.get("fps") or 24)

        # Sync: morph corto + freeze por escena hasta cubrir narracion.mp3
        narr = Path(ctx.paths["copy_dir"]) / "narracion.mp3"
        audio_dur = _ffprobe_duration(narr)
        sync_audio = morph_cfg.get("sync_audio", True)
        per_scene_target = (
            audio_dur / len(pairs) if sync_audio and audio_dur >= 1.0 and pairs else 0.0
        )

        clip_paths: list[Path] = []
        items = []
        warnings = []
        for i, (a, b, stem) in enumerate(pairs, start=1):
            raw_clip = clips_dir / f"{i:02d}-{stem}_raw.mp4"
            out_clip = clips_dir / f"{i:02d}-{stem}.mp4"
            ok, msg = _morph_clip(a, b, raw_clip, fps=fps, hold=hold, xfade=xfade)
            if not ok:
                return AgentResult(ok=False, notes=f"Morph escena {i}: {msg}")
            if per_scene_target > 0:
                ok, msg = _pad_clip_to_duration(raw_clip, per_scene_target, out_clip)
                if not ok:
                    return AgentResult(ok=False, notes=f"Morph pad escena {i}: {msg}")
                try:
                    raw_clip.unlink(missing_ok=True)
                except Exception:
                    pass
            else:
                out_clip.write_bytes(raw_clip.read_bytes())
                try:
                    raw_clip.unlink(missing_ok=True)
                except Exception:
                    pass
            clip_paths.append(out_clip)
            items.append(
                {
                    "escena": i,
                    "stem": stem,
                    "archivo": out_clip.name,
                    "path": str(out_clip),
                    "a": str(a),
                    "b": str(b),
                    "duracion_objetivo_s": round(per_scene_target, 3) if per_scene_target else None,
                }
            )

        final = videos_out / f"{ctx.slug}_morph.mp4"
        # también alias estable para audio/subtitulos
        alias = videos_out / "pareto_5_escenas_animado.mp4" if "pareto" in ctx.slug else videos_out / f"{ctx.slug}_escenas.mp4"
        ok, msg = concat_clips(clip_paths, final)
        if not ok:
            return AgentResult(ok=False, notes=f"Morph concat: {msg}")
        # copia alias
        try:
            alias.write_bytes(final.read_bytes())
        except Exception as exc:
            warnings.append(f"alias: {exc}")

        expected_dur = audio_dur if per_scene_target else len(pairs) * (2 * hold + xfade) / max(fps, 1)
        payload = {
            "skill": "morph-escenas",
            "fuente_frames": fuente,
            "count": len(items),
            "clips": items,
            "final": str(final),
            "alias": str(alias) if alias.exists() else None,
            "hold_frames": hold,
            "xfade_frames": xfade,
            "fps": fps,
            "audio_dur_target": audio_dur or None,
            "duration_esperada_s": round(expected_dur, 3),
            "sync_audio": bool(sync_audio and audio_dur >= 1.0),
            "pad_mode": "tpad_freeze" if per_scene_target else None,
            "generado_at": datetime.now(timezone.utc).isoformat(),
        }
        out_meta = Path(ctx.paths["meta"]) / "morph.json"
        save_json(out_meta, payload)

        # Actualiza generated_videos para Audio/Subtitulos/QC
        gv_path = ctx.paths.get("generated_videos")
        gv = load_json(gv_path, {}) if gv_path else {}
        gv = gv or {}
        gv["final"] = str(final)
        gv["morph_final"] = str(final)
        gv["modo"] = "morph"
        videos = [v for v in (gv.get("videos") or []) if v.get("tipo") not in {"final", "morph_final"}]
        videos.append(
            {
                "archivo": final.name,
                "path": str(final),
                "modulo": "videos",
                "modo": "morph",
                "tipo": "final",
                "escenas": len(items),
                "generado_at": payload["generado_at"],
            }
        )
        gv["videos"] = videos
        gv["count"] = len(items)
        if gv_path:
            save_json(gv_path, gv)

        # lote apunta al video visual correcto
        lote_u = {
            **lote,
            "video_final": final.name,
            "audio": {**(lote.get("audio") if isinstance(lote.get("audio"), dict) else {}), "video_path": final.name},
        }
        save_json(ctx.paths["lote"], lote_u)
        ctx.lote = lote_u

        return AgentResult(
            ok=True,
            artifacts=[str(final), str(out_meta)],
            notes=f"Morph {len(items)} escenas ({fuente}) → {final.name}",
            warnings=warnings,
        )
