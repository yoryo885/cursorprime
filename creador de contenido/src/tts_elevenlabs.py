"""TTS ElevenLabs — genera narración mp3 desde texto."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

ELEVEN_API = os.getenv("ELEVENLABS_API_URL", "https://api.elevenlabs.io/v1")
ELEVEN_KEY = os.getenv("ELEVENLABS_API_KEY", "").strip().strip('"').strip("'")
ELEVEN_VOICE = os.getenv("ELEVENLABS_VOICE_ID", "").strip().strip('"').strip("'")
ELEVEN_MODEL = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2").strip()
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "elevenlabs").strip().lower()
MOCK_TTS = os.getenv("MOCK_TTS", "true").lower() in ("1", "true", "yes", "on")

# Voces por defecto (evita /v1/voices que exige permiso user_read)
_DEFAULT_VOICES = [
    "EXAVITQu4vr4xnSDxMaL",  # Bella — suele funcionar en plan free vía API
    "JBFqnCBsd6RMkjVDRZzb",  # George
    "21m00Tcm4TlvDq8ikWAM",  # Rachel (a veces requiere plan de pago)
]


def tts_activo() -> bool:
    if MOCK_TTS:
        return False
    if TTS_PROVIDER != "elevenlabs":
        return False
    return bool(ELEVEN_KEY)


def _voice_candidates() -> list[str]:
    if ELEVEN_VOICE:
        return [ELEVEN_VOICE]
    return list(_DEFAULT_VOICES)


def _tts_once(texto: str, voice_id: str, out_mp3: Path) -> Path:
    url = f"{ELEVEN_API}/text-to-speech/{voice_id}"
    payload = {
        "text": texto,
        "model_id": ELEVEN_MODEL or "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.45, "similarity_boost": 0.75},
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "xi-api-key": ELEVEN_KEY,
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    out_mp3.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(req, timeout=120) as resp:
        out_mp3.write_bytes(resp.read())
    if not out_mp3.exists() or out_mp3.stat().st_size < 100:
        raise RuntimeError("ElevenLabs devolvió audio vacío")
    return out_mp3


def synthesize_elevenlabs(texto: str, out_mp3: Path) -> Path:
    """Genera MP3 con ElevenLabs. Lanza si falla."""
    if not ELEVEN_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY vacía")
    text = " ".join(str(texto).split()).strip()
    if not text:
        raise RuntimeError("texto vacío para TTS")
    if len(text) > 4500:
        text = text[:4500]

    errors: list[str] = []
    for voice_id in _voice_candidates():
        try:
            return _tts_once(text, voice_id, out_mp3)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")[:200]
            if exc.code == 401:
                errors.append(f"{voice_id}: 401 key inválida o sin permiso TTS")
            elif exc.code == 402:
                errors.append(f"{voice_id}: 402 voz de librería requiere plan de pago")
            else:
                errors.append(f"{voice_id}: HTTP {exc.code} {detail}")
        except Exception as exc:
            errors.append(f"{voice_id}: {exc}")
    raise RuntimeError(
        "ElevenLabs falló con todas las voces. "
        "Pon ELEVENLABS_VOICE_ID= de una voz de TU cuenta (VoiceLab). "
        + " | ".join(errors[:3])
    )

def _synthesize_edge(texto: str, out_mp3: Path) -> Path:
    """Fallback local/remoto sin cuota ElevenLabs (edge-tts)."""
    import asyncio
    try:
        import edge_tts
    except ImportError as exc:
        raise RuntimeError("Instala edge-tts para fallback TTS") from exc
    text = " ".join(str(texto).split()).strip()
    voice = os.getenv("EDGE_TTS_VOICE", "es-MX-DaliaNeural").strip() or "es-MX-DaliaNeural"
    rate = os.getenv("EDGE_TTS_RATE", "-5%").strip() or "-5%"

    async def _run() -> None:
        communicate = edge_tts.Communicate(text, voice=voice, rate=rate)
        await communicate.save(str(out_mp3))

    asyncio.run(_run())
    if not out_mp3.exists() or out_mp3.stat().st_size < 100:
        raise RuntimeError("edge-tts devolvió audio vacío")
    return out_mp3


def synthesize(texto: str, out_mp3: Path, mock: bool | None = None) -> tuple[Path | None, str, str]:
    """
    Devuelve (path|None, modo, nota).
    modo: elevenlabs | edge-tts | mock | skip
    """
    use_mock = MOCK_TTS if mock is None else mock
    if use_mock:
        return None, "mock", "MOCK_TTS=true — no se llamó a ElevenLabs"
    if not tts_activo():
        # sin ElevenLabs: intentar edge-tts
        try:
            path = _synthesize_edge(texto, out_mp3)
            return path, "edge-tts", f"voz edge-tts ({path.name})"
        except Exception as exc:
            return None, "skip", f"TTS inactivo y edge-tts falló: {exc}"
    try:
        path = synthesize_elevenlabs(texto, out_mp3)
        return path, "elevenlabs", f"voz generada ({path.name})"
    except Exception as exc:
        # key sin permiso TTS → fallback
        try:
            path = _synthesize_edge(texto, out_mp3)
            return path, "edge-tts", f"fallback edge-tts tras ElevenLabs: {exc}"
        except Exception as exc2:
            raise RuntimeError(f"ElevenLabs y edge-tts fallaron: {exc} | {exc2}") from exc2
