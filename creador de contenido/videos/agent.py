"""Módulo video — slideshow o animado (frame A + B → clip por escena)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from src.config import load_json, save_json, slug_clips
from src.types import AgentResult, PipelineContext
from src.video_backend import animate_pair, concat_clips, slideshow_from_pngs


class VideosModule:
    slug_modulo = "videos"

    def _pendiente(self, ctx: PipelineContext, videos_dir: Path, msg: str) -> AgentResult:
        placeholder = videos_dir / f"{ctx.slug}_pendiente.txt"
        placeholder.write_text(msg + "\n", encoding="utf-8")
        out = ctx.paths["generated_videos"]
        save_json(out, {"videos": [{"archivo": placeholder.name, "path": str(placeholder), "mock": True}], "count": 0, "pendiente": True})
        return AgentResult(ok=True, artifacts=[str(out)], notes="Video pendiente", warnings=[msg])

    def _modo_slideshow(self, ctx: PipelineContext, context: dict, imgs: list, videos_dir: Path) -> AgentResult:
        cfg = context.get("video") or {}
        fps = int(cfg.get("fps") or 2)
        png_paths = [Path(i["path"]) for i in imgs if Path(i["path"]).exists()]
        out_mp4 = videos_dir / f"{ctx.slug}.mp4"
        ok, msg = slideshow_from_pngs(png_paths, out_mp4, fps=fps)
        if not ok:
            return self._pendiente(ctx, videos_dir, msg)
        item = {
            "archivo": out_mp4.name,
            "path": str(out_mp4),
            "modulo": "videos",
            "modo": "slideshow",
            "fps": fps,
            "generado_at": datetime.now(timezone.utc).isoformat(),
        }
        out = ctx.paths["generated_videos"]
        save_json(out, {"videos": [item], "count": 1, "modo": "slideshow"})
        return AgentResult(ok=True, artifacts=[str(out_mp4)], notes=f"Slideshow: {out_mp4.name}")

    def _modo_animado(self, ctx: PipelineContext, context: dict, imgs: list) -> AgentResult:
        escenas = load_json(ctx.paths["escenas"], {}).get("escenas", [])
        if not escenas:
            return AgentResult(ok=False, notes="Modo animado sin escenas.json")

        by_escena: dict[int, dict[str, Path]] = {}
        for img in imgs:
            eid = img.get("escena_id")
            if eid is None:
                continue
            by_escena.setdefault(eid, {})
            tf = img.get("tipo_frame")
            if tf in ("inicio", "fin"):
                by_escena[eid][tf] = Path(img["path"])

        clips_dir = slug_clips(ctx.slug)
        clips_dir.mkdir(parents=True, exist_ok=True)
        videos_dir = ctx.paths["videos_out"]
        videos_dir.mkdir(parents=True, exist_ok=True)
        warnings = []
        clips = []
        items = []

        for esc in escenas:
            eid = esc["id"]
            pair = by_escena.get(eid, {})
            start = pair.get("inicio")
            end = pair.get("fin")
            if not start or not end or not start.exists() or not end.exists():
                return AgentResult(ok=False, notes=f"Escena {eid}: faltan frames inicio/fin")

            clip_path = clips_dir / esc.get("archivo_clip", f"{eid:02d}.mp4")
            ok, msg, fue_mock = animate_pair(start, end, esc.get("animation_prompt", ""), clip_path)
            if not ok:
                return AgentResult(ok=False, notes=f"Escena {eid}: {msg}")
            if fue_mock:
                warnings.append(f"escena {eid}: motion mock/fallback ({msg})")
            else:
                warnings.append(f"escena {eid}: kling real ({msg})")
            clips.append(clip_path)
            items.append(
                {
                    "escena_id": eid,
                    "archivo": clip_path.name,
                    "path": str(clip_path),
                    "modulo": "videos",
                    "modo": "animado",
                    "mock_kling": fue_mock,
                }
            )

        final = videos_dir / f"{ctx.slug}.mp4"
        ok, msg = concat_clips(clips, final)
        if not ok:
            return self._pendiente(ctx, videos_dir, msg)

        items.append(
            {
                "archivo": final.name,
                "path": str(final),
                "modulo": "videos",
                "modo": "animado",
                "tipo": "final",
                "escenas": len(clips),
                "generado_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        out = ctx.paths["generated_videos"]
        save_json(out, {"videos": items, "count": len(clips), "modo": "animado", "final": str(final)})
        return AgentResult(
            ok=True,
            artifacts=[str(final)],
            notes=f"Animado: {len(clips)} clips → {final.name}",
            warnings=warnings,
        )

    def run(self, ctx: PipelineContext) -> AgentResult:
        context = load_json(ctx.paths["context"], {})
        imgs = load_json(ctx.paths["generated_imagenes"], {}).get("imagenes", [])
        video_modo = (context.get("video") or {}).get("modo", "slideshow")
        videos_dir = ctx.paths["videos_out"]
        videos_dir.mkdir(parents=True, exist_ok=True)

        if not imgs:
            return AgentResult(ok=False, notes="Video requiere PNG — módulo imagenes vacío")

        if video_modo == "animado":
            return self._modo_animado(ctx, context, imgs)
        return self._modo_slideshow(ctx, context, imgs, videos_dir)
