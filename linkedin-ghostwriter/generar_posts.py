#!/usr/bin/env python3
"""
Sistema de Ghostwriting LinkedIn para Ejecutivos Chilenos
Usa Claude Code instalado — sin costo adicional
"""

import json
import os
import subprocess
from datetime import datetime

# ─────────────────────────────────────────────
#  CONFIGURACION
# ─────────────────────────────────────────────
ARCHIVO_PERFIL = "ejecutivo_perfil.json"
CARPETA_POSTS  = "posts_generados"
CLAUDE_BIN     = "/Users/yoryo/.cursor/extensions/anthropic.claude-code-2.1.152-darwin-x64/resources/native-binary/claude"

# ─────────────────────────────────────────────
#  FUNCION BASE: llamar a Claude
# ─────────────────────────────────────────────
def llamar_claude(prompt: str) -> str:
    """Llama al Claude Code instalado con un prompt."""
    result = subprocess.run(
        [CLAUDE_BIN, "-p", prompt, "--output-format", "text"],
        capture_output=True,
        text=True,
        timeout=120
    )
    return result.stdout.strip()

# ─────────────────────────────────────────────
#  AGENTE 1: PLANIFICADOR
# ─────────────────────────────────────────────
def agente_planificador(perfil: dict) -> list:
    """Planifica los temas del mes según el perfil del ejecutivo."""

    prompt = f"""Eres un estratega de contenido LinkedIn para ejecutivos.

Crea un plan de {perfil['cantidad_posts']} posts para el mes para este ejecutivo:
- Cargo: {perfil['cargo']} en {perfil['industria']}
- Experto en: {', '.join(perfil['temas_experto'])}
- Logros recientes: {', '.join(perfil['logros_recientes'])}

Responde SOLO con un JSON válido, sin texto adicional, sin markdown:
[
  {{"tipo": "historia personal", "tema": "descripción específica"}},
  {{"tipo": "lección aprendida", "tema": "descripción específica"}}
]

Tipos disponibles: historia personal, lección aprendida, opinión de industria,
logro del equipo, reflexión de liderazgo, tendencia del sector, consejo práctico.

Usa los datos reales del ejecutivo. Sé específico, no genérico."""

    respuesta = llamar_claude(prompt)

    # Extraer JSON de la respuesta
    inicio = respuesta.find("[")
    fin = respuesta.rfind("]") + 1
    if inicio == -1 or fin == 0:
        raise ValueError(f"No se encontró JSON en la respuesta: {respuesta[:200]}")

    return json.loads(respuesta[inicio:fin])

# ─────────────────────────────────────────────
#  AGENTE 2: REDACTOR
# ─────────────────────────────────────────────
def agente_redactor(perfil: dict, tipo_post: str, tema: str) -> str:
    """Redacta el post con la voz del ejecutivo."""

    prompt = f"""Eres un ghostwriter experto en LinkedIn para ejecutivos chilenos.
Escribe un post tipo "{tipo_post}" sobre: {tema}

PERFIL DEL EJECUTIVO:
- Nombre: {perfil['nombre']}, {perfil['cargo']} en {perfil['empresa']}
- Industria: {perfil['industria']}, {perfil['anos_experiencia']} años de experiencia
- Tono: {perfil['tono']}
- Logros reales: {', '.join(perfil['logros_recientes'])}
- Valores: {', '.join(perfil['valores'])}

REGLAS:
1. Primera persona ("Hoy aprendí...", "En mis 20 años...")
2. Español profesional chileno — natural, no rígido
3. Máximo 1-2 emojis si aplica, no más
4. Estructura: gancho → historia/dato → lección → pregunta o reflexión
5. Entre 150-300 palabras
6. Que suene HUMANO y vivido, con detalles concretos
7. NO menciones que es un post de LinkedIn
8. Solo escribe el texto del post, nada más"""

    return llamar_claude(prompt)

# ─────────────────────────────────────────────
#  AGENTE 3: REVISOR
# ─────────────────────────────────────────────
def agente_revisor(post: str, perfil: dict) -> dict:
    """Evalúa y mejora el post si es necesario."""

    prompt = f"""Eres un editor senior de contenido LinkedIn. Evalúa este post:

---
{post}
---

Es para {perfil['nombre']}, {perfil['cargo']} en Chile. Tono esperado: {perfil['tono']}.

Responde SOLO con JSON válido, sin texto adicional:
{{"puntaje": 8, "aprobado": true, "mejora": null}}

- "puntaje": del 1 al 10
- "aprobado": true si puntaje >= 7
- "mejora": texto mejorado si puntaje < 7, sino null

Criterios: ¿Suena humano? ¿Tiene gancho? ¿Aporta valor? ¿Longitud correcta? ¿Termina con engagement?"""

    respuesta = llamar_claude(prompt)

    inicio = respuesta.find("{")
    fin = respuesta.rfind("}") + 1
    if inicio == -1 or fin == 0:
        return {"puntaje": 7, "aprobado": True, "mejora": None}

    try:
        return json.loads(respuesta[inicio:fin])
    except json.JSONDecodeError:
        return {"puntaje": 7, "aprobado": True, "mejora": None}

# ─────────────────────────────────────────────
#  SISTEMA PRINCIPAL
# ─────────────────────────────────────────────
def generar_posts_del_mes():
    print("\n" + "="*55)
    print("   SISTEMA GHOSTWRITING LINKEDIN - EJECUTIVOS CHILE")
    print("="*55)

    # Cargar perfil
    with open(ARCHIVO_PERFIL, "r", encoding="utf-8") as f:
        perfil = json.load(f)

    print(f"\n✓ Perfil: {perfil['nombre']} — {perfil['cargo']}")
    print(f"  Empresa: {perfil['empresa']} | {perfil['industria']}")
    print(f"  Generando {perfil['cantidad_posts']} posts...\n")

    # Crear carpeta de salida
    mes_actual = datetime.now().strftime("%Y-%m")
    nombre_limpio = perfil['nombre'].replace(' ', '_').lower()
    carpeta_salida = os.path.join(CARPETA_POSTS, f"{nombre_limpio}_{mes_actual}")
    os.makedirs(carpeta_salida, exist_ok=True)

    # AGENTE 1: Planificador
    print("📋 Agente 1 — Planificador: diseñando calendario...")
    plan = agente_planificador(perfil)
    print(f"   ✓ {len(plan)} temas definidos\n")

    posts_finales = []

    for i, item in enumerate(plan, 1):
        print(f"✍️  Post {i}/{len(plan)} — {item['tipo'].upper()}")
        print(f"   Tema: {item['tema']}")

        # AGENTE 2: Redactor
        print("   Redactando...", end=" ", flush=True)
        post_borrador = agente_redactor(perfil, item['tipo'], item['tema'])
        print("✓")

        # AGENTE 3: Revisor
        print("   Revisando...", end=" ", flush=True)
        revision = agente_revisor(post_borrador, perfil)
        puntaje = revision.get('puntaje', 7)

        if puntaje < 7 and revision.get('mejora'):
            post_final = revision['mejora']
            print(f"✓ mejorado ({puntaje}→ revisado)")
        else:
            post_final = post_borrador
            print(f"✓ puntaje {puntaje}/10")

        posts_finales.append({
            "numero": i,
            "tipo": item['tipo'],
            "tema": item['tema'],
            "post": post_final,
            "puntaje": puntaje
        })

        # Guardar post individual
        nombre_archivo = f"post_{i:02d}_{item['tipo'].replace(' ', '_')}.txt"
        ruta = os.path.join(carpeta_salida, nombre_archivo)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(f"POST #{i} | {item['tipo'].upper()} | Puntaje: {puntaje}/10\n")
            f.write(f"Tema: {item['tema']}\n")
            f.write("─" * 50 + "\n\n")
            f.write(post_final)
            f.write(f"\n\n─ Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")

        print()

    # Resumen completo
    resumen_path = os.path.join(carpeta_salida, "_TODOS_LOS_POSTS.txt")
    with open(resumen_path, "w", encoding="utf-8") as f:
        f.write(f"POSTS LINKEDIN — {perfil['nombre']}\n")
        f.write(f"Mes: {datetime.now().strftime('%B %Y').upper()}\n")
        f.write("=" * 55 + "\n\n")
        for p in posts_finales:
            f.write(f"{'='*55}\n")
            f.write(f"POST #{p['numero']} | {p['tipo'].upper()} | {p['puntaje']}/10\n")
            f.write(f"Tema: {p['tema']}\n")
            f.write("─" * 55 + "\n\n")
            f.write(p['post'])
            f.write("\n\n")

    promedio = sum(p['puntaje'] for p in posts_finales) / len(posts_finales)
    print("=" * 55)
    print(f"✅  {len(posts_finales)} posts generados — puntaje promedio {promedio:.1f}/10")
    print(f"📁  Carpeta: {carpeta_salida}/")
    print(f"📄  Resumen: _TODOS_LOS_POSTS.txt")
    print("=" * 55 + "\n")

if __name__ == "__main__":
    generar_posts_del_mes()
