#!/usr/bin/env python3
"""
cursorprime runner — puente n8n → pipelines / logs locales.

POST http://127.0.0.1:8780/job
{
  "action": "lead.append" | "ping" | "job.enqueue" | "pipeline.audit_demo" | "pipeline.tiktok_brief",
  "payload": { ... }
}
"""
from __future__ import annotations

import json
import os
import subprocess
import threading
import traceback
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
CURSORPRIME = ROOT.parent.parent
N8N_ROOT = ROOT.parent
DATA = ROOT / "data"
JOBS = ROOT / "jobs"
LEADS = DATA / "leads.jsonl"
LOG = DATA / "runner.log"
CONFIG = ROOT / "config.json"
PORT = int(os.environ.get("RUNNER_PORT", "8780"))

DATA.mkdir(parents=True, exist_ok=True)
JOBS.mkdir(parents=True, exist_ok=True)


def _load_dotenv() -> None:
    env_path = N8N_ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_dotenv()


def load_config() -> dict:
    if CONFIG.exists():
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    return {}


def _tg_creds() -> tuple[str, str, str, dict]:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    cfg = load_config().get("telegram") or {}
    username = cfg.get("username_at") or cfg.get("username") or "@yoryo321"
    if not chat_id and cfg.get("chat_id"):
        chat_id = str(cfg["chat_id"])
    pending = {
        "ok": False,
        "pending": True,
        "to": username,
        "error": "falta TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID",
        "hint": "Creá el bot con @BotFather, /start al bot, bash scripts/telegram-setup.sh",
    }
    return token, chat_id, username, pending


def telegram_send(text: str) -> dict:
    """Envía mensaje al chat configurado. Sin token/chat_id → pending."""
    token, chat_id, username, pending = _tg_creds()
    if not token or not chat_id:
        return pending
    import urllib.request

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    body = json.dumps(
        {"chat_id": chat_id, "text": text[:4000], "disable_web_page_preview": True}
    ).encode()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode())
    return {"ok": bool(data.get("ok")), "to": username, "chat_id": chat_id, "telegram": data}


def telegram_send_video(path: Path, caption: str = "") -> dict:
    """Sube un MP4 al chat de Telegram."""
    token, chat_id, username, pending = _tg_creds()
    if not token or not chat_id:
        return pending
    if not path.exists():
        return {"ok": False, "error": f"no existe {path}", "to": username}
    import urllib.request

    boundary = "----cpRunnerVideo"
    raw = path.read_bytes()
    parts = []

    def field(name: str, value: str) -> bytes:
        return (
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n"
            f"{value}\r\n"
        ).encode()

    parts.append(field("chat_id", chat_id))
    if caption:
        parts.append(field("caption", caption[:1024]))
    parts.append(
        (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="video"; filename="{path.name}"\r\n'
            f"Content-Type: video/mp4\r\n\r\n"
        ).encode()
        + raw
        + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode())
    body = b"".join(parts)
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendVideo",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode())
    return {
        "ok": bool(data.get("ok")),
        "to": username,
        "chat_id": chat_id,
        "file": str(path),
        "bytes": len(raw),
        "telegram": {"ok": data.get("ok"), "description": data.get("description")},
    }


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(msg: str) -> None:
    line = f"{now()} {msg}\n"
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line)
    print(line, end="", flush=True)


def append_jsonl(path: Path, obj: dict) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def handle_lead_append(payload: dict) -> dict:
    lead = payload.get("lead") or payload
    row = {
        "id": lead.get("leadId") or f"L-{uuid.uuid4().hex[:10]}",
        "nombre": lead.get("nombre") or "",
        "email": lead.get("email") or "",
        "mensaje": lead.get("mensaje") or "",
        "marca": lead.get("marca") or "",
        "origen": lead.get("origen") or "embudo",
        "intencion": lead.get("intencion") or _guess_intent(lead),
        "at": lead.get("at") or now(),
        "status": "nuevo",
    }
    append_jsonl(LEADS, row)
    # también cola de seguimiento
    job = {
        "jobId": f"J-{uuid.uuid4().hex[:10]}",
        "type": "seguimiento_lead",
        "lead": row,
        "todo_humano": "Revisar lead y responder (Wasap/email) — 20% DG/Marketing",
        "at": now(),
    }
    (JOBS / f"{job['jobId']}.json").write_text(
        json.dumps(job, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    tg = telegram_send(
        f"🆕 Lead nuevo\n"
        f"{row['nombre']} · {row['email']}\n"
        f"Intención: {row['intencion']}\n"
        f"{row['mensaje'][:300]}"
    )
    return {"ok": True, "action": "lead.append", "lead": row, "job": job, "telegram": tg}


def _guess_intent(lead: dict) -> str:
    text = f"{lead.get('mensaje','')} {lead.get('marca','')}".lower()
    if any(k in text for k in ("wasap", "whatsapp", "cita", "bot")):
        return "wasap"
    if any(k in text for k in ("web", "landing", "presencia", "seo")):
        return "presencia"
    if any(k in text for k in ("audit", "informe", "marketing")):
        return "audit"
    return "embudo"


def handle_enqueue(payload: dict) -> dict:
    job = {
        "jobId": f"J-{uuid.uuid4().hex[:10]}",
        "type": payload.get("type") or "generic",
        "payload": payload,
        "status": "queued",
        "at": now(),
    }
    (JOBS / f"{job['jobId']}.json").write_text(
        json.dumps(job, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {"ok": True, "action": "job.enqueue", "job": job}


def handle_tiktok_brief(payload: dict) -> dict:
    slug = (payload.get("slug") or f"tt-{uuid.uuid4().hex[:8]}").strip()
    tema = (payload.get("tema") or payload.get("hook") or "").strip()
    out_dir = CURSORPRIME / "creador de contenido" / "data" / slug / "inputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    brief = {
        "slug": slug,
        "plataforma": "tiktok",
        "formato": "9:16",
        "tema": tema,
        "nicho": payload.get("nicho") or "general",
        "video": {"modo": payload.get("modo") or "slideshow", "fps": 2},
        "status": "brief_listo",
        "at": now(),
        "nota": "Borrador automático. Revisar antes de publicar (ciclo feedback).",
    }
    path = out_dir / "tiktok-brief.json"
    path.write_text(json.dumps(brief, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    job = handle_enqueue({"type": "tiktok_brief", "slug": slug, "path": str(path)})
    tg = telegram_send(
        f"🎬 TikTok brief listo\n"
        f"slug: {slug}\n"
        f"tema: {tema or '—'}\n"
        f"Revisá el borrador y pedime cambios si hace falta."
    )
    return {
        "ok": True,
        "action": "pipeline.tiktok_brief",
        "brief": brief,
        "path": str(path),
        "job": job["job"],
        "telegram": tg,
    }


def handle_telegram_notify(payload: dict) -> dict:
    text = str(payload.get("text") or payload.get("mensaje") or "").strip()
    if not text:
        return {"ok": False, "error": "falta text"}
    result = telegram_send(text)
    return {"ok": result.get("ok", False), "action": "telegram.notify", **result}


def handle_contenido_video(payload: dict) -> dict:
    """Corre creador de contenido (slideshow) y manda el MP4 a Telegram."""
    slug = (payload.get("slug") or f"tg-vid-{uuid.uuid4().hex[:8]}").strip()
    temas = payload.get("temas")
    if isinstance(temas, str):
        temas = [t.strip() for t in temas.split(",") if t.strip()]
    if not temas:
        tema = (payload.get("tema") or payload.get("titulo") or "Contenido demo").strip()
        temas = [tema, "WhatsApp", "Clientes"]
    titulo = (payload.get("titulo") or temas[0]).strip()
    # Por defecto animado CON personaje (no slideshow de cards)
    modo_video = (payload.get("modo") or "animado").strip()
    content_root = CURSORPRIME / "creador de contenido"
    lote_dir = content_root / "data" / slug / "inputs"
    lote_dir.mkdir(parents=True, exist_ok=True)
    guion = (payload.get("guion") or "").strip()
    if not guion:
        guion = (
            f"Un emprendedor con delantal mira el celular: {titulo}.\n\n"
            f"Aparece un personaje guía amable que le muestra la solución.\n\n"
            f"El emprendedor sonríe: ahora puede atender el local tranquilo."
        )
    lote = {
        "titulo": titulo,
        "salidas": ["png", "video"],
        "estilo": payload.get("estilo") or "papel-sketch",
        "temas": temas[:5],
        "video": {
            "modo": modo_video,
            "fps": int(payload.get("fps") or 2),
            "limit_escenas": int(payload.get("limit_escenas") or 2),
        },
        "guion": guion,
        "personaje": {
            "descripcion": payload.get("personaje")
            or "Emprendedor joven con delantal + personaje guía ilustrado"
        },
        "notas": "Generado por runner → Telegram (modo personaje)",
    }
    (lote_dir / "lote.json").write_text(
        json.dumps(lote, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    env = os.environ.copy()
    env.setdefault("MOCK_KLING", "true")
    cmd = [
        "python3",
        "creador_imagenes_main.py",
        "--slug",
        slug,
        "--modo",
        "video",
    ]
    proc = subprocess.run(
        cmd,
        cwd=str(content_root),
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )
    mp4 = content_root / "data" / slug / "videos" / f"{slug}.mp4"
    if proc.returncode != 0 or not mp4.exists():
        return {
            "ok": False,
            "action": "pipeline.contenido_video",
            "slug": slug,
            "error": "pipeline_fallo",
            "stdout": (proc.stdout or "")[-800:],
            "stderr": (proc.stderr or "")[-800:],
            "mp4": str(mp4),
        }
    tg = telegram_send_video(
        mp4,
        caption=(
            f"🎬 Creador de contenido\n"
            f"slug: {slug}\n"
            f"tema: {titulo}\n"
            f"modo: {modo_video}\n\n"
            f"Borrador — si no te gusta, pedí cambios."
        ),
    )
    return {
        "ok": True,
        "action": "pipeline.contenido_video",
        "slug": slug,
        "mp4": str(mp4),
        "telegram": tg,
        "lote": lote,
    }


def handle_audit_demo(payload: dict) -> dict:
    """Dispara audit en modo mock/demo si el CLI lo permite; si no, encola."""
    slug = (payload.get("slug") or f"audit-{uuid.uuid4().hex[:8]}").strip()
    cmd = [
        "python3",
        "marketing_audit_main.py",
        "--help",
    ]
    # Preferimos encolar + dejar instrucción clara; demo real puede ser pesada.
    job_path = JOBS / f"audit-{slug}.json"
    job = {
        "jobId": f"J-audit-{slug}",
        "type": "audit",
        "slug": slug,
        "status": "queued_ready",
        "cmd_sugerido": f"cd marketing-audit && python3 marketing_audit_main.py --slug {slug}",
        "payload": payload,
        "at": now(),
        "nota": "Borrador. DG/Marketing aprueba antes de enviar al cliente.",
    }
    job_path.write_text(json.dumps(job, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Intento liviano: escribir brief de audit
    brief_dir = CURSORPRIME / "marketing-audit" / "data" / slug / "inputs"
    brief_dir.mkdir(parents=True, exist_ok=True)
    brief = {
        "slug": slug,
        "negocio": payload.get("negocio") or payload.get("nombre") or slug,
        "ciudad": payload.get("ciudad") or "",
        "origen": "n8n-runner",
        "at": now(),
    }
    (brief_dir / "brief.json").write_text(
        json.dumps(brief, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {"ok": True, "action": "pipeline.audit_demo", "job": job, "brief": brief}


ACTIONS = {
    "ping": lambda p: {"ok": True, "action": "ping", "at": now(), "service": "cursorprime-runner"},
    "lead.append": handle_lead_append,
    "job.enqueue": handle_enqueue,
    "pipeline.tiktok_brief": handle_tiktok_brief,
    "pipeline.audit_demo": handle_audit_demo,
    "pipeline.contenido_video": handle_contenido_video,
    "telegram.notify": handle_telegram_notify,
}


class Handler(BaseHTTPRequestHandler):
    def _json(self, code: int, obj: dict) -> None:
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/health"):
            leads = 0
            if LEADS.exists():
                leads = sum(1 for _ in LEADS.open(encoding="utf-8") if _.strip())
            return self._json(
                200,
                {
                    "ok": True,
                    "service": "cursorprime-runner",
                    "at": now(),
                    "leads": leads,
                    "jobs": len(list(JOBS.glob("*.json"))),
                    "actions": list(ACTIONS.keys()),
                },
            )
        if path == "/leads":
            rows = []
            if LEADS.exists():
                for line in LEADS.read_text(encoding="utf-8").splitlines():
                    if line.strip():
                        rows.append(json.loads(line))
            return self._json(200, {"ok": True, "leads": rows[-50:]})
        return self._json(404, {"ok": False, "error": "not_found"})

    def do_POST(self):
        path = urlparse(self.path).path
        if path not in ("/job", "/v1/job"):
            return self._json(404, {"ok": False, "error": "use POST /job"})
        try:
            n = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(n).decode("utf-8") or "{}")
        except Exception as e:
            return self._json(400, {"ok": False, "error": f"json_invalido: {e}"})
        action = (body.get("action") or "").strip()
        payload = body.get("payload") if isinstance(body.get("payload"), dict) else body
        fn = ACTIONS.get(action)
        if not fn:
            return self._json(
                400,
                {"ok": False, "error": "action_desconocida", "actions": list(ACTIONS.keys())},
            )
        try:
            result = fn(payload)
            log(f"OK {action} {json.dumps(result, ensure_ascii=False)[:200]}")
            return self._json(200, result)
        except Exception as e:
            log(f"ERR {action} {e}\n{traceback.format_exc()}")
            return self._json(500, {"ok": False, "error": str(e), "action": action})

    def log_message(self, fmt, *args):
        return


def main():
    log(f"runner listening on :{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
