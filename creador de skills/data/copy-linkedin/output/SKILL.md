---
name: copy-linkedin
description: >-
  Criterios de calidad para posts LinkedIn al estilo del ejecutivo en
  ejecutivo_perfil.json: tono profesional chileno, gancho, primera persona,
  pregunta final. Proyecto: LinkedIn Ghostwriter. Usar cuando el usuario pide
  post linkedin, copy linkedin, ghostwriter, posts del mes, usa copy-linkedin,
  o necesita copy superior al default del modelo.
---

# Copy LinkedIn

Skill de **capacidad** — capa extra de criterio (no workflow completo).

## Objetivo

Posts LinkedIn con la voz del ejecutivo definido en `ejecutivo_perfil.json`. Batch mensual con `generar_posts.py` o post único en chat aplicando los mismos criterios.

## Cuándo usar

Triggers: post linkedin, copy linkedin, ghostwriter, usa copy-linkedin, posts del mes.

**Workspace:** proyecto aparte → `~/cursorprime/linkedin-ghostwriter` (abrir carpeta o usar rutas absolutas).

## Modos

### Post único (chat)

1. Leer `ejecutivo_perfil.json` (o perfil que indique el usuario).
2. Confirmar tipo: historia personal, lección aprendida, opinión de industria, logro del equipo, reflexión de liderazgo, tendencia del sector, consejo práctico.
3. Redactar aplicando criterios abajo.
4. Auto-revisar (puntaje 1–10); reescribir si < 7.

### Batch mensual (CLI)

```bash
cd ~/cursorprime/linkedin-ghostwriter
# Editar ejecutivo_perfil.json (logros_recientes, cantidad_posts)
python3 generar_posts.py
```

Salida: `posts_generados/{nombre}_{YYYY-MM}/` — un `.txt` por post + `_TODOS_LOS_POSTS.txt`.

Pipeline interno: Planificador → Redactor → Revisor (3 agentes).

## Criterios de calidad

- **Perfil primero:** leer `ejecutivo_perfil.json` — `logros_recientes` dan autenticidad; no inventar datos.
- **Longitud:** 150–300 palabras (~800–1500 caracteres).
- **Emojis:** máximo 1–2; sin exceso.
- **Estructura:** gancho → historia o dato concreto → lección → pregunta final para engagement.
- **Voz:** primera persona; español profesional chileno, natural (no rígido ni corporativo vacío).
- **Valores y tono:** respetar `tono` y `valores` del perfil.
- **Prohibido:** mencionar que es un post de LinkedIn; solo entregar el texto listo para publicar.
- **QC:** ¿Suena humano? ¿Gancho en las primeras 2 líneas? ¿Aporta valor? ¿Termina con engagement? Objetivo ≥ 7/10.

## Tipos de post (calendario)

| Tipo | Enfoque |
|------|---------|
| historia personal | Anécdota concreta + lección |
| lección aprendida | Error o insight transformador |
| opinión de industria | Postura clara con fundamento |
| logro del equipo | Celebrar sin arrogancia |
| reflexión de liderazgo | Gestión de personas |
| tendencia del sector | Actualidad + visión |
| consejo práctico | Accionable en 3–5 puntos implícitos |

## Múltiples ejecutivos

Copiar `ejecutivo_perfil.json` con otro nombre y cambiar `ARCHIVO_PERFIL` en `generar_posts.py`.

## Proyecto

`~/cursorprime/linkedin-ghostwriter` · Guía: `INSTRUCCIONES.md`

## Iteración

Si el tono no encaja, pedir feedback y ajustar perfil o criterios en esta skill.
