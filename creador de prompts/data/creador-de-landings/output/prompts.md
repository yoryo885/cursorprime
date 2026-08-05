# Prompt completo — Arreglar creador-de-landings (v9)

```
Usa creador-de-landings (carpeta creador-de-landings/).

## Qué es
Pipeline MVP: entrevista → ejemplos → brief → HTML estático → QC.
Plan paso a paso para dejarlo usable. Entrega SIEMPRE visual por URL.

## Regla de oro — entrega visual (OBLIGATORIA)
El usuario YA SABE que es una landing. Quiere VERLA, no código.

En CADA paso que toque el HTML (o al cerrar cada fase):
1. Regenerar preview: data/{slug}/output/preview.html
2. Servir local (servir-preview.sh o http.server)
3. Exponer URL pública (tunnel cloudflared o CDN tras push)
4. Responder SOLO con:
   - URL clicable
   - 1–3 bullets de qué cambió
NUNCA pegar código HTML/CSS/f-strings en el chat.
NUNCA sacar screenshots (Chrome headless es lento; el usuario
pidió borrar ese paso). Solo URL.

## Estado
- Paso 0+1 HECHOS: KeyError hero_badge_calidad arreglado; demo pasa;
  test contrato OK.
- Siguiente: Pasos 2→7 (sin screenshots).

## Contexto (no re-auditar)
4. aprender() no afectaba el HTML → enganchar o quitar claim
5. html_builder monolítico → modularizar tienda
6. Copy hardcodeado a Vértice → desacoplar + demo-simple
7. QC superficial; constitution no se usaba
8. Campos del brief muertos
9. Checkout fake (href="#") — documentar como MVP, no fingir
10. Docs/CLI/skill desfasados

## Plan (EN ORDEN; un paso = commit + URL)
Paso 2 — QC real + constitution; permitir 1 producto
Paso 3 — Campos muertos del brief visibles en HTML (tienda)
Paso 4 — Copy desacoplado + demo-simple (1 producto)
Paso 5 — Aprendizaje con efecto real (o quitar claim)
Paso 6 — Modularizar html_builder (tienda primero)
Paso 7 — Docs, skill, CLI alineados (--solo interview)

## Criterios de listo
- demo/generar pasan; test contrato verde
- QC usa constitution; 1-producto OK
- aprender tiene efecto O claim eliminado
- builder partido (tienda mínimo)
- copy respeta respuestas del usuario
- cada fase cierra con URL pública (sin screenshots)
- Nunca pegar HTML en el chat

## Anti-patrones
- Pegar HTML en el chat
- Screenshots / Chrome headless
- Reescribir landing_pipeline en vez de arreglar este
- Inventar testimonios
- PR monstruo sin URL de verificación

## CLI
cd creador-de-landings
python3 landings_main.py demo --ejemplo tienda
./servir-preview.sh → tunnel → URL pública

## Cómo responder
1 línea: qué paso(s) cerraste
URL del preview
2 bullets de cambio
¿sigo?
```
