"""10 — Shotlist legible para grabar."""

from __future__ import annotations

from pathlib import Path


def run(input: dict) -> dict:
    hook = input.get("hook_elegido") or ""
    script = input.get("script") or {}
    interrupts = (input.get("pattern_interrupts") or {}).get("interrupts") or []
    textos = (input.get("onscreen_text") or {}).get("textos") or []
    cta = input.get("cta") or {}
    loop = input.get("loop") or {}
    audio = input.get("audio") or {}
    caption = input.get("caption_hashtags") or {}

    lines = [
        f"# Shotlist — {input.get('tema', 'TikTok')}",
        "",
        f"**Hook:** {hook}",
        f"**Mensaje central:** {script.get('mensaje_central', '')}",
        f"**Duración aprox:** {script.get('duracion_seg_aprox', '?')}s",
        f"**Audio:** {audio.get('tipo', '')} · ritmo {audio.get('ritmo', '')}",
        f"**CTA:** {cta.get('cta', '')}",
        f"**Loop:** {loop.get('loop', '')}",
        "",
        "## Escenas",
        "",
    ]

    bloques = script.get("bloques") or []
    # Escena 0 = hook
    lines.append("### 0:00–0:03 · HOOK")
    lines.append(f"- Decir: {hook}")
    lines.append("- Plano: zoom_in a cámara")
    t0 = next((x for x in textos if x.get("escena_id") == 0), None)
    if t0:
        lines.append(f"- Texto en pantalla: «{t0.get('texto')}»")
    lines.append("")

    t_cursor = 5
    for b in bloques:
        bid = b.get("id", 1)
        t_end = t_cursor + 7
        lines.append(f"### 0:{t_cursor:02d}–0:{t_end:02d} · PASO {bid}")
        lines.append(f"- Decir: {b.get('texto', '')}")
        txt = next((x for x in textos if x.get("escena_id") == bid), None)
        if txt:
            lines.append(f"- Texto en pantalla: «{txt.get('texto')}»")
        inter = [i for i in interrupts if i.get("t_inicio", 0) >= t_cursor - 1 and i.get("t_inicio", 0) < t_end]
        for i in inter[:2]:
            lines.append(f"- Corte: {i.get('tipo')} — {i.get('nota', '')}")
        lines.append("")
        t_cursor = t_end

    lines.append(f"### 0:{t_cursor:02d}–final · CTA + LOOP")
    lines.append(f"- Decir CTA: {cta.get('cta', '')}")
    lines.append(f"- Loop: {loop.get('loop', '')}")
    lines.append("- Plano: zoom_in + texto CTA")
    lines.append("")
    lines.append("## Caption")
    lines.append(caption.get("caption", ""))
    lines.append("")
    lines.append("## Hashtags")
    lines.append(" ".join(caption.get("hashtags") or []))
    lines.append("")
    lines.append("## Notas de edición")
    for i in interrupts:
        lines.append(
            f"- {i.get('t_inicio')}–{i.get('t_fin')}s: {i.get('tipo')} ({i.get('nota', '')})"
        )

    md = "\n".join(lines)
    out_path = input.get("_shotlist_path")
    if out_path:
        p = Path(out_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(md, encoding="utf-8")

    return {"shotlist_md": md, "shotlist_path": str(out_path or "")}
