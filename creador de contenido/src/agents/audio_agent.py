"""AudioAgent — brief + TTS ElevenLabs (opcional) + mux voz/cama al video."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from src.config import ROOT, load_json, save_json
from src.tts_elevenlabs import synthesize, tts_activo
from src.types import AgentResult, PipelineContext
from src.video_backend import mux_audio_bed


def _texto_narracion(lote: dict, context: dict, guion_meta: dict, hook: str) -> str:
    """Prioriza guion completo; si no, hook + ideas."""
    if lote.get("audio") and isinstance(lote["audio"], dict) and lote["audio"].get("texto"):
        return str(lote["audio"]["texto"]).strip()
    guion = (
        lote.get("guion")
        or guion_meta.get("guion")
        or context.get("guion")
        or ""
    )
    if guion:
        return str(guion).strip()
    partes = [hook] if hook else []
    ideas = guion_meta.get("ideas") or context.get("temas") or []
    partes.extend(str(x) for x in ideas[:5])
    return "\n\n".join(p for p in partes if p).strip()


class AudioAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        lote = load_json(ctx.paths["lote"], {}) or ctx.lote
        context = load_json(ctx.paths["context"], {})
        hooks = load_json(ctx.paths.get("hooks"), {}) if ctx.paths.get("hooks") else {}
        guion_meta = load_json(ctx.paths.get("guion"), {}) if ctx.paths.get("guion") else {}
        hook = (hooks.get("elegido") or {}).get("texto") or lote.get("hook") or ""
        titulo = context.get("titulo") or lote.get("titulo") or ctx.slug
        audio_cfg = lote.get("audio") if isinstance(lote.get("audio"), dict) else {}

        tipo = audio_cfg.get("tipo") or "mix"
        if "3 " in hook.lower() or "pasos" in hook.lower():
            tipo = "lista_beats"

        narracion = _texto_narracion(lote, context, guion_meta or {}, hook)
        voz_off = bool(audio_cfg.get("voz_off", True))

        brief = {
            "skill": "audio-redes",
            "titulo": titulo,
            "hook": hook,
            "tipo": tipo,
            "voz_off": voz_off,
            "tts": {"provider": "elevenlabs", "activo": tts_activo(), "modo": None},
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

        warnings: list[str] = []
        muxed = None
        voz_path: Path | None = None

        # 1) TTS ElevenLabs (si MOCK_TTS=false + key)
        copy_dir = Path(ctx.paths["copy_dir"])
        copy_dir.mkdir(parents=True, exist_ok=True)
        if voz_off and narracion:
            out_voz = copy_dir / "narracion.mp3"
            # Permite override: audio.voz_path ya generado
            preset = audio_cfg.get("voz_path") or ""
            if preset:
                p = Path(preset)
                if not p.is_absolute():
                    p = next(
                        (c for c in (ROOT / preset, ROOT.parent / preset, p) if c.exists()),
                        p,
                    )
                if p.exists():
                    voz_path = p
                    brief["tts"] = {"provider": "archivo", "modo": "voz_path", "path": str(p)}
            else:
                try:
                    path, modo, nota = synthesize(narracion, out_voz)
                    brief["tts"] = {
                        "provider": "elevenlabs",
                        "modo": modo,
                        "nota": nota,
                        "chars": len(narracion),
                    }
                    if path:
                        voz_path = path
                        brief["tts"]["path"] = str(path)
                    elif modo == "mock":
                        warnings.append(nota)
                except Exception as exc:
                    warnings.append(f"TTS: {exc}")
                    brief["tts"] = {"provider": "elevenlabs", "modo": "error", "error": str(exc)[:200]}

        # 2) Resolver video final
        videos_meta = load_json(ctx.paths.get("generated_videos"), {}) if ctx.paths.get("generated_videos") else {}
        final = videos_meta.get("final")
        if not final:
            for v in videos_meta.get("videos") or []:
                if v.get("tipo") == "final" or str(v.get("archivo", "")).endswith(".mp4"):
                    final = v.get("path")
                    break

        bed = audio_cfg.get("bed_path") or audio_cfg.get("musica_path") or ""
        audio_for_mux: Path | None = None
        if voz_path and voz_path.exists():
            audio_for_mux = voz_path
        elif bed:
            bed_path = Path(bed)
            if not bed_path.is_absolute():
                bed_path = next(
                    (p for p in (ROOT / bed, ROOT.parent / bed, bed_path) if p.exists()),
                    bed_path,
                )
            if bed_path.exists():
                audio_for_mux = bed_path

        if audio_for_mux and final:
            out_mux = Path(ctx.paths["videos_out"]) / f"{ctx.slug}_audio.mp4"
            ok, msg = mux_audio_bed(Path(final), audio_for_mux, out_mux)
            if ok:
                muxed = str(out_mux)
                brief["mux"] = {
                    "ok": True,
                    "path": muxed,
                    "fuente": "voz" if voz_path and audio_for_mux == voz_path else "bed",
                }
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
                "nota": (
                    "Sin voz TTS ni bed_path — solo brief. "
                    "Pon MOCK_TTS=false + ELEVENLABS_API_KEY, o audio.voz_path / audio.bed_path."
                ),
            }

        out = ctx.paths["audio"]
        save_json(out, brief)
        md = copy_dir / "audio.md"
        tts_line = brief.get("tts") or {}
        md.write_text(
            f"# Audio — {titulo}\n\n"
            f"**Hook:** {hook}\n\n"
            f"**Tipo:** {tipo}\n\n"
            f"**TTS:** {tts_line.get('modo') or '—'} · {tts_line.get('nota') or tts_line.get('path') or ''}\n\n"
            f"**Música:** {brief['musica']['estilo']} · ~{brief['musica']['bpm_sugerido']} BPM\n\n"
            f"**Atracción:**\n" + "\n".join(f"- {a}" for a in brief["atraccion"]) + "\n",
            encoding="utf-8",
        )
        notes = f"Audio brief ({tipo})"
        if voz_path:
            notes += f" · voz {voz_path.name}"
        if muxed:
            notes += f" · mux {Path(muxed).name}"
        return AgentResult(ok=True, artifacts=[str(out), str(md)], notes=notes, warnings=warnings)
