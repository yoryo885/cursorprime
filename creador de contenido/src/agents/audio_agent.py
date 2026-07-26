"""AudioAgent — brief + TTS ElevenLabs (opcional) + mux voz/cama al video."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from src.config import ROOT, load_json, save_json
from src.paths_resolve import resolve_video_final
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
            # Reusa narracion.mp3 si ya existe y no forzamos regenerar
            reuse = bool(audio_cfg.get("reusar_voz", True)) and out_voz.exists() and out_voz.stat().st_size > 1000
            force = bool(audio_cfg.get("regenerar_voz") or lote.get("regenerar_voz"))
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
            elif reuse and not force:
                voz_path = out_voz
                brief["tts"] = {
                    "provider": "archivo",
                    "modo": "reusar",
                    "path": str(out_voz),
                    "nota": "Reutiliza copy/narracion.mp3 (pon regenerar_voz:true para forzar TTS)",
                }
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

        # 2) Resolver video final (portable Mac/cloud)
        videos_meta = load_json(ctx.paths.get("generated_videos"), {}) if ctx.paths.get("generated_videos") else {}
        videos_out = Path(ctx.paths["videos_out"])
        prefer = (
            audio_cfg.get("video_path")
            or audio_cfg.get("video")
            or lote.get("video_final")
            or ""
        )
        prefer_name = Path(str(prefer)).name if prefer else None
        final_path = resolve_video_final(videos_meta or {}, videos_out, ctx.slug, prefer_name=prefer_name)

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

        if audio_for_mux and final_path:
            out_mux = videos_out / f"{ctx.slug}_audio.mp4"
            ok, msg = mux_audio_bed(final_path, audio_for_mux, out_mux)
            if ok:
                muxed = str(out_mux)
                brief["mux"] = {
                    "ok": True,
                    "path": muxed,
                    "fuente": "voz" if voz_path and audio_for_mux == voz_path else "bed",
                    "video_fuente": str(final_path),
                }
                # Normaliza meta a rutas locales
                videos_meta = videos_meta or {}
                videos_meta["final"] = str(final_path)
                videos_meta["final_audio"] = muxed
                videos_meta.setdefault("videos", [])
                # quita entradas stale de final_audio
                videos_meta["videos"] = [
                    v
                    for v in videos_meta["videos"]
                    if v.get("tipo") != "final_audio"
                ]
                videos_meta["videos"].append(
                    {
                        "archivo": out_mux.name,
                        "path": muxed,
                        "modulo": "videos",
                        "modo": "audio_mux",
                        "tipo": "final_audio",
                    }
                )
                # reescribe paths de videos existentes si el archivo local existe por nombre
                fixed = []
                for v in videos_meta["videos"]:
                    vv = dict(v)
                    name = vv.get("archivo") or Path(str(vv.get("path") or "")).name
                    local = videos_out / name if name else None
                    if local and local.exists():
                        vv["path"] = str(local)
                        vv["archivo"] = name
                    elif vv.get("escena_id") is not None:
                        clip = videos_out / "clips" / name
                        if clip.exists():
                            vv["path"] = str(clip)
                    fixed.append(vv)
                videos_meta["videos"] = fixed
                save_json(ctx.paths["generated_videos"], videos_meta)
            else:
                warnings.append(f"mux audio: {msg}")
                brief["mux"] = {"ok": False, "error": msg}
        elif audio_for_mux and not final_path:
            warnings.append(
                "mux audio: no hay video local. Corre sin --desde, o: "
                f"--desde video  (busca {ctx.slug}.mp4 en videos/)"
            )
            brief["mux"] = {
                "ok": False,
                "error": "video no existe",
                "hint": "Regenera video o asegúrate de tener data/.../videos/{slug}.mp4",
            }
        else:
            brief["mux"] = {
                "ok": False,
                "nota": (
                    "Sin voz TTS ni bed_path — solo brief. "
                    "Pon MOCK_TTS=false + ELEVENLABS_API_KEY en ELEVENLABS_KEY.env"
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
            f"**Mux:** {brief.get('mux')}\n\n"
            f"**Atracción:**\n" + "\n".join(f"- {a}" for a in brief["atraccion"]) + "\n",
            encoding="utf-8",
        )
        notes = f"Audio brief ({tipo})"
        if voz_path:
            notes += f" · voz {voz_path.name}"
        if muxed:
            notes += f" · mux {Path(muxed).name}"
        # ok=True si hay voz aunque mux falle (el usuario ya tiene narracion.mp3)
        return AgentResult(ok=True, artifacts=[str(out), str(md)], notes=notes, warnings=warnings)
