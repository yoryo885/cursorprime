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

def synthesize(texto: str, out_mp3: Path, mock: bool | None = None) -> tuple[Path | None, str, str]:
    """
    Devuelve (path|None, modo, nota).
    modo: elevenlabs | mock | skip
    """
    use_mock = MOCK_TTS if mock is None else mock
    if use_mock:
        return None, "mock", "MOCK_TTS=true — no se llamó a ElevenLabs"
    if not tts_activo():
        return None, "skip", "TTS inactivo (falta ELEVENLABS_API_KEY o TTS_PROVIDER)"
    path = synthesize_elevenlabs(texto, out_mp3)
    return path, "elevenlabs", f"voz generada ({path.name})"
