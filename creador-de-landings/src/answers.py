"""Resuelve respuestas A/B/C/D → valores de brief."""

from __future__ import annotations

import re

from src.config import load_json, preguntas_path


def load_spec() -> dict:
    return load_json(preguntas_path(), {}) or {}


def parse_letras(texto: str, n: int) -> list[str]:
    """
    Acepta:
      - 'todo A' / 'todas A'
      - '1A 2B 3A ...'
      - 'A B C A ...' (una letra por pregunta en orden)
      - 'AAAAAAAAAAAAAA' (n letras seguidas)
    """
    t = (texto or "").strip()
    if not t:
        return []

    low = t.lower()
    if low.startswith("todo ") or low.startswith("todas "):
        letter = t.split()[-1].upper()
        if letter in "ABCD":
            return [letter] * n
        # 'todo auto' / 'recomendadas'
        if letter in ("AUTO", "RECOMENDADAS", "OK"):
            return ["*"] * n

    pairs = re.findall(r"(\d+)\s*([A-Da-d])", t)
    if pairs:
        out = [""] * n
        for num, let in pairs:
            i = int(num) - 1
            if 0 <= i < n:
                out[i] = let.upper()
        if all(out):
            return out

    letters = re.findall(r"[A-Da-d]", t)
    if len(letters) >= n:
        return [x.upper() for x in letters[:n]]
    if len(letters) == 1 and n > 1 and re.fullmatch(r"[A-Da-d\s]+", t.strip()):
        # una sola letra repetida implícita no — exigir n
        pass
    if letters and len(letters) == n:
        return [x.upper() for x in letters]
    return [x.upper() for x in letters] if letters else []


def resolver_respuestas(texto_usuario: str, extras: dict | None = None) -> dict:
    """Convierte letras del usuario en dict listo para respuestas.json."""
    spec = load_spec()
    preguntas = spec.get("preguntas") or []
    n = len(preguntas)
    letras = parse_letras(texto_usuario, n)
    extras = extras or {}

    # rellenar faltantes con recomendado
    out: dict = {"_fuente": "letras", "_raw": texto_usuario}
    for i, q in enumerate(preguntas):
        qid = q["id"]
        rec = (q.get("recomendado") or "A").upper()
        let = letras[i] if i < len(letras) and letras[i] else rec
        if let == "*":
            let = rec
        opts = q.get("opciones") or {}
        valor = opts.get(let) or opts.get(rec) or ""
        # limpiar ★ del texto
        valor = valor.replace(" ★", "").replace("★", "").strip()
        # overrides libres (opción D u otra)
        if let == "D" and extras.get(qid):
            valor = extras[qid]
        out[qid] = valor
        out[f"_{qid}_letra"] = let

    # normalizar campos que el pipeline espera
    estilo_map = {
        "tienda (colección tipo Filjós)": "tienda",
        "editorial (hero grande)": "editorial",
        "mockup (producto en tablet)": "mockup",
        "oferta (ads / cierre rápido)": "oferta",
    }
    if out.get("estilo") in estilo_map:
        out["estilo"] = estilo_map[out["estilo"]]
        out["estilo_preferido"] = out["estilo"]
        out["ejemplo_elegido"] = out["estilo"]

    tono = out.get("tono", "")
    if tono.startswith("auto"):
        out["tono"] = "editorial"

    clima = out.get("clima_color", "").lower().replace(" ★", "").strip()
    out["clima_color"] = clima

    pal = out.get("paleta", "")
    if pal.startswith("A") or "auto" in pal.lower():
        out["paleta"] = "A"
    elif pal.startswith("B"):
        out["paleta"] = "B"
    elif pal.startswith("C"):
        out["paleta"] = "C"

    if "filjos" in (out.get("referencia") or "").lower():
        out["referencia"] = "https://filjos.com/"

    return out
