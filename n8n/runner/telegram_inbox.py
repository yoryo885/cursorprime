#!/usr/bin/env python3
"""
Telegram inbox — órdenes desde @mi_asistente_yoryo_bot → runner → respuesta.

Solo acepta el chat_id configurado (seguridad).
"""
from __future__ import annotations

import json
import os
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
N8N_ROOT = ROOT.parent
DATA = ROOT / "data"
OFFSET_FILE = DATA / "telegram_offset.txt"
LOG = DATA / "telegram_inbox.log"
CONFIG = ROOT / "config.json"
RUNNER = os.environ.get("RUNNER_URL", "http://127.0.0.1:8780")


def load_dotenv() -> None:
    env_path = N8N_ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


load_dotenv()
DATA.mkdir(parents=True, exist_ok=True)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
ALLOWED_CHAT = str(
    os.environ.get("TELEGRAM_CHAT_ID")
    or (json.loads(CONFIG.read_text()).get("telegram") or {}).get("chat_id")
    or ""
).strip()


def log(msg: str) -> None:
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {msg}\n"
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line)
    print(line, end="", flush=True)


def tg_api(method: str, payload: dict | None = None, timeout: int = 35) -> dict:
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"} if data else {},
        method="POST" if data else "GET",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def reply(chat_id: int | str, text: str) -> None:
    tg_api(
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": text[:4000],
            "disable_web_page_preview": True,
        },
    )


def runner_job(action: str, payload: dict) -> dict:
    body = json.dumps({"action": action, "payload": payload}).encode()
    req = urllib.request.Request(
        f"{RUNNER}/job",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def runner_get(path: str) -> dict:
    with urllib.request.urlopen(f"{RUNNER}{path}", timeout=15) as resp:
        return json.loads(resp.read().decode())


HELP = """Comandos cursorprime:

• ayuda — esta lista
• ping / status — ¿está vivo?
• leads — últimos leads
• audit NOMBRE [| ciudad]
• tiktok TEMA [| slug]
• correr — demo del sistema completo (lead + audit + tiktok)

Ejemplos:
correr
audit Clínica Sol | Providencia
tiktok 3 errores en Google

Todo es borrador. Si no te gusta, pedí el cambio en Cursor."""


def handle_text(text: str) -> str:
    raw = (text or "").strip()
    if not raw:
        return HELP
    low = raw.lower().strip()

    if low in ("/start", "start", "hola", "hi"):
        return "✅ Inbox activo.\nEscribí ayuda para ver comandos."

    if low in ("ayuda", "help", "/help", "?"):
        return HELP

    if low in ("ping", "/ping"):
        r = runner_job("ping", {})
        return f"pong · runner ok={r.get('ok')}"

    if low in ("status", "health", "/status"):
        h = runner_get("/health")
        return (
            f"Runner: ok={h.get('ok')}\n"
            f"Leads: {h.get('leads')} · Jobs: {h.get('jobs')}\n"
            f"Actions: {', '.join(h.get('actions') or [])}"
        )

    if low in ("leads", "/leads"):
        data = runner_get("/leads")
        rows = data.get("leads") or []
        if not rows:
            return "Sin leads todavía."
        lines = ["Últimos leads:"]
        for L in rows[-8:]:
            lines.append(
                f"• {L.get('nombre') or '—'} | {L.get('email') or '—'} | {L.get('intencion')}"
            )
        return "\n".join(lines)

    if low.startswith("audit ") or low.startswith("/audit "):
        rest = raw.split(" ", 1)[1].strip()
        negocio, _, ciudad = [x.strip() for x in (rest + "|").split("|", 1)]
        ciudad = ciudad.strip()
        slug = (
            "audit-"
            + "".join(c if c.isalnum() else "-" for c in negocio.lower()).strip("-")[:40]
        )
        r = runner_job(
            "pipeline.audit_demo",
            {"negocio": negocio, "ciudad": ciudad, "slug": slug},
        )
        brief = r.get("brief") or {}
        return (
            f"✅ Audit encolado\n"
            f"Negocio: {brief.get('negocio')}\n"
            f"Ciudad: {brief.get('ciudad') or '—'}\n"
            f"Slug: {brief.get('slug')}\n"
            f"Borrador listo para revisar."
        )

    if low.startswith("tiktok ") or low.startswith("/tiktok "):
        rest = raw.split(" ", 1)[1].strip()
        if "|" in rest:
            tema, slug = [x.strip() for x in rest.split("|", 1)]
        else:
            tema, slug = rest, ""
        payload = {"tema": tema}
        if slug:
            payload["slug"] = slug
        r = runner_job("pipeline.tiktok_brief", payload)
        b = r.get("brief") or {}
        return (
            f"✅ TikTok brief\n"
            f"Tema: {b.get('tema')}\n"
            f"Slug: {b.get('slug')}\n"
            f"Modo: {(b.get('video') or {}).get('modo')}\n"
            f"Revisá y pedí cambios si hace falta."
        )

    if low in ("correr", "correr todo", "sistema", "full", "/correr", "demo"):
        # Demo sistema completo: lead + audit + tiktok brief
        lead = runner_job(
            "lead.append",
            {
                "lead": {
                    "nombre": "Demo Telegram",
                    "email": "demo-telegram@cursorprime.local",
                    "mensaje": "Quiero audit + presencia",
                    "marca": "Demo Local",
                    "origen": "telegram-correr",
                }
            },
        )
        audit = runner_job(
            "pipeline.audit_demo",
            {
                "negocio": "Demo Local",
                "ciudad": "Providencia",
                "slug": "audit-demo-telegram",
            },
        )
        tt = runner_job(
            "pipeline.tiktok_brief",
            {
                "tema": "3 errores de locales en Google Maps",
                "slug": "tt-demo-telegram",
                "nicho": "negocios locales",
            },
        )
        return (
            "✅ Sistema completo (demo) disparado desde Telegram\n\n"
            f"1) Lead: {((lead.get('lead') or {}).get('id'))}\n"
            f"2) Audit: {((audit.get('brief') or {}).get('slug'))}\n"
            f"3) TikTok: {((tt.get('brief') or {}).get('slug'))}\n\n"
            "Son borradores. Revisá y pedí cambios si hace falta."
        )

    return "No entendí.\nEscribí: ayuda"


def get_offset() -> int:
    if OFFSET_FILE.exists():
        try:
            return int(OFFSET_FILE.read_text().strip() or "0")
        except ValueError:
            return 0
    return 0


def set_offset(n: int) -> None:
    OFFSET_FILE.write_text(str(n), encoding="utf-8")


def main() -> None:
    if not TOKEN:
        raise SystemExit("Falta TELEGRAM_BOT_TOKEN")
    if not ALLOWED_CHAT:
        raise SystemExit("Falta TELEGRAM_CHAT_ID")
    log(f"inbox listening · allowed_chat={ALLOWED_CHAT}")
    # aviso de arranque
    try:
        reply(ALLOWED_CHAT, "🟢 Inbox Telegram ON\nMandá: ayuda")
    except Exception as e:
        log(f"boot notify fail: {e}")

    offset = get_offset()
    while True:
        try:
            data = tg_api(
                "getUpdates",
                {"timeout": 25, "offset": offset, "allowed_updates": ["message"]},
                timeout=35,
            )
            for upd in data.get("result") or []:
                offset = max(offset, int(upd["update_id"]) + 1)
                set_offset(offset)
                msg = upd.get("message") or {}
                chat = msg.get("chat") or {}
                chat_id = str(chat.get("id") or "")
                text = msg.get("text") or ""
                if chat_id != ALLOWED_CHAT:
                    log(f"ignore chat {chat_id}")
                    continue
                if not text:
                    continue
                log(f"cmd from {chat_id}: {text[:120]}")
                try:
                    out = handle_text(text)
                except Exception as e:
                    log(f"handler err: {e}\n{traceback.format_exc()}")
                    out = f"Error: {e}"
                reply(chat_id, out)
        except urllib.error.HTTPError as e:
            log(f"http {e.code}: {e.read()[:200]}")
            time.sleep(3)
        except Exception as e:
            log(f"loop err: {e}")
            time.sleep(3)


if __name__ == "__main__":
    main()
