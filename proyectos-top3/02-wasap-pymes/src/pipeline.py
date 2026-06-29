"""Pipeline mock: catálogo → conversación → cola pedidos."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import load_json, save_json, slug_dir, CLIENTES


def run_demo(slug: str = "don-pedro") -> bool:
    base = slug_dir(slug)
    brief = load_json(base / "inputs" / "brief.json", {})
    menu = brief.get("menu") or []

    # Simular conversación
    conv = {
        "at": datetime.now(timezone.utc).isoformat(),
        "cliente_ficticio": brief.get("negocio"),
        "mensajes": [
            {"de": "cliente", "texto": "Hola, qué empanadas tienen?"},
            {"de": "bot", "texto": _menu_text(menu)},
            {"de": "cliente", "texto": "Quiero 2 pino y 1 napolitana"},
            {"de": "bot", "texto": "Pedido registrado #1001. Total $8.500. ¿Confirmas? (SI/NO)"},
            {"de": "cliente", "texto": "SI"},
            {"de": "bot", "texto": "✅ Listo! Te avisamos cuando esté. ~25 min."},
        ],
    }

    pedido = {
        "id": "1001",
        "items": [{"sku": "pino", "qty": 2}, {"sku": "napolitana", "qty": 1}],
        "total_clp": 8500,
        "estado": "en_cola",
        "cliente_telefono": "+56900000000 (ficticio)",
    }

    meta = base / "meta"
    out = base / "output"
    meta.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)

    save_json(meta / "conversacion.json", conv)
    save_json(meta / "cola_pedidos.json", {"pedidos": [pedido], "mock": True})
    save_json(out / "manifest.json", {"slug": slug, "pedidos": 1, "mock": True})

    sim = out / "simulacion_whatsapp.md"
    lines = [f"# Simulación WhatsApp — {brief.get('negocio')}\n", "**MODO DEMO** — sin API Meta\n"]
    for m in conv["mensajes"]:
        lines.append(f"**{m['de']}:** {m['texto']}\n")
    sim.write_text("\n".join(lines), encoding="utf-8")

    # Bridge clientes
    import shutil

    dest = CLIENTES / "empanadas-don-pedro" / "proyectos" / "bot-pedidos" / "entregables" / "operacion"
    dest.mkdir(parents=True, exist_ok=True)
    save_json(dest / "cola_pedidos.json", load_json(meta / "cola_pedidos.json"))
    shutil.copy2(sim, dest / "simulacion_whatsapp.md")

    print(f"  ✓ Conversación: {sim}")
    print(f"  ✓ Cola: {meta / 'cola_pedidos.json'}")
    print(f"  ✓ Cliente: {dest}")
    return True


def _menu_text(menu: list) -> str:
    lines = ["📋 Menú:"]
    for item in menu:
        lines.append(f"• {item['nombre']} — ${item['precio_clp']:,}")
    lines.append("\nEscribe cantidad x producto (ej: 2x pino)")
    return "\n".join(lines)
