"""Pipeline: brief → landing wireframe markdown."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import load_json, save_json, slug_dir, CLIENTES


def run_demo(slug: str = "ferreteria-central") -> bool:
    brief = load_json(slug_dir(slug) / "inputs" / "brief.json", {})
    nombre = brief.get("negocio", slug)
    out = slug_dir(slug) / "output"
    out.mkdir(parents=True, exist_ok=True)

    md = f"""# Landing — {nombre}

*Wireframe demo — {datetime.now(timezone.utc).strftime('%Y-%m-%d')}*

## Hero
- **Headline:** {brief.get('headline', 'Tu ferretería de confianza en el barrio')}
- **Sub:** {brief.get('subheadline', 'Herramientas, materiales y asesoría')}
- **CTA:** WhatsApp / Llamar / Cómo llegar

## Beneficios (3)
1. {brief.get('beneficios', ['Stock local', 'Precios justos', 'Asesoría'])[0]}
2. {brief.get('beneficios', ['', 'Precios justos', ''])[1]}
3. {brief.get('beneficios', ['', '', 'Asesoría'])[2]}

## Prueba social
- "Más de 15 años en el barrio" (ficticio)
- Google Maps ⭐ 4.6

## Contacto
- Dirección: {brief.get('direccion', 'Av. Demo 123, Santiago')}
- WhatsApp: {brief.get('whatsapp', '+56 9 XXXX XXXX')}

## SEO básico
- Title: {nombre} | Ferretería Santiago
- Meta: Materiales y herramientas — envío local

---
*Generado por presencia_main.py demo — reemplazar con HTML real*
"""
    path = out / "landing-wireframe.md"
    path.write_text(md, encoding="utf-8")
    save_json(out / "manifest.json", {"slug": slug, "negocio": nombre, "mock": True})

    dest = CLIENTES / "ferreteria-central" / "proyectos" / "web-inicial" / "entregables" / "copy"
    dest.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copy2(path, dest / "landing-wireframe.md")

    print(f"  ✓ Wireframe: {path}")
    print(f"  ✓ Cliente: {dest}")
    return True
