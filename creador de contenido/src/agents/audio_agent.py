"""AudioAgent — brief de música/voz alineado al hook; mux opcional de cama."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from src.config import ROOT, load_json, save_json
from src.types import AgentResult, PipelineContext
from src.video_backend import mux_audio_bed


class AudioAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        lote = load_json(ctx.paths["lote"], {}) or ctx.lote
        context = load_json(ctx.paths["context"], {})
        hooks = load_json(ctx.paths.get("hooks"), {}) if ctx.paths.get("hooks") else {}
        hook = (hooks.get("elegido") or {}).get("texto") or lote.get("hook") or ""
        titulo = context.get("titulo") or lote.get("titulo") or ctx.slug
        audio_cfg = lote.get("audio") if isinstance(lote.get("audio"), dict) else {}

        # Brief que atrae: ritmo según hook (curiosidad → beat medio; lista → hits)
        tipo = audio_cfg.get("tipo") or "mix"
        if "3 " in hook.lower() or "pasos" in hook.lower():
            tipo = "lista_beats"
        brief = {
            "skill": "audio-redes",
            "titulo": titulo,
            "hook": hook,
            "tipo": tipo,
            "voz_off": audio_cfg.get("voz_off", True),
            "musica": {
                "estilo": audio_cfg.get("estilo")
                or "instrumental trendy, sin letra, volumen bajo bajo la voz",
                "bpm_sugerido": audio_cfg.get("bpm") or 100,
                "nota": "Buscar sonido trending del nicho o librería libre; no inventar archivo de pago",
            },
            "atraccion": [
                "Los primeros 3s del audio deben pegar con el hook visual",
                "Bajar música -12 dB cuando entra voz",
                "Loop limpio al final para rewatch",
            ],
            "generado_at": datetime.now(timezone.utc).isoformat(),
            "confidence": "medium",
        }

        warnings = []
        muxed = None
        bed = audio_cfg.get("bed_path") or audio_cfg.get("musica_path") or ""
        videos_meta = load_json(ctx.paths.get("generated_videos"), {}) if ctx.paths.get("generated_videos") else {}
        final = videos_meta.get("final")
        if not final:
            for v in videos_meta.get("videos") or []:
                if v.get("tipo") == "final" or v.get("archivo", "").endswith(".mp4"):
                    final = v.get("path")
                    break

        if bed and final:
            bed_path = Path(bed)
            if not bed_path.is_absolute():
                candidates = [ROOT / bed, ROOT.parent / bed, Path(bed)]
                bed_path = next((p for p in candidates if p.exists()), bed_path)
            out_mux = Path(ctx.paths["videos_out"]) / f"{ctx.slug}_audio.mp4"
            ok, msg = mux_audio_bed(Path(final), bed_path, out_mux)
            if ok:
                muxed = str(out_mux)
                brief["mux"] = {"ok": True, "path": muxed}
                # Actualizar meta videos
                videos_meta["final_audio"] = muxed
                videos_meta.setdefault("videos", []).append(
                    {
                        "archivo": out_mux.name,
                        "path": muxed,
                        "modulo": "videos",
                        "modo": "audio_mux",
                        "tipo": "final_audio",
                    }
                )
                save_json(ctx.paths["generated_videos"], videos_meta)
            else:
                warnings.append(f"mux audio: {msg}")
                brief["mux"] = {"ok": False, "error": msg}
        else:
            brief["mux"] = {
                "ok": False,
                "nota": "Sin bed_path en lote.audio — solo brief. Añade audio.bed_path para mux.",
            }

        out = ctx.paths["audio"]
        save_json(out, brief)
        md = Path(ctx.paths["copy_dir"]) / "audio.md"
        md.parent.mkdir(parents=True, exist_ok=True)
        md.write_text(
            f"# Audio — {titulo}\n\n"
            f"**Hook:** {hook}\n\n"
            f"**Tipo:** {tipo}\n\n"
            f"**Música:** {brief['musica']['estilo']} · ~{brief['musica']['bpm_sugerido']} BPM\n\n"
            f"**Atracción:**\n" + "\n".join(f"- {a}" for a in brief["atraccion"]) + "\n",
            encoding="utf-8",
        )
        notes = f"Audio brief ({tipo})" + (f" · mux {Path(muxed).name}" if muxed else "")
        return AgentResult(ok=True, artifacts=[str(out), str(md)], notes=notes, warnings=warnings)
