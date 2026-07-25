# Prompt completo — Arreglar creador-de-landings (v8)

```
Usa creador-de-landings (carpeta creador-de-landings/).

## Qué es
Pipeline MVP: entrevista → ejemplos → brief → HTML estático → QC.
Hoy está roto y con deuda estructural. Este prompt es el plan
paso a paso para dejarlo usable, con entrega SIEMPRE visual.

## Regla de oro — entrega visual (OBLIGATORIA)
El usuario YA SABE que es una landing. No quiere ver código HTML
en el chat. Quiere VER la página.

En CADA paso que toque el HTML (o al cerrar cada fase):
1. Regenerar preview: data/{slug}/output/preview.html
2. Servir local (servir-preview.sh o http.server)
3. Exponer URL pública (tunnel cloudflared o CDN tras push)
4. Capturar desktop + mobile (Playwright o chrome headless)
5. Responder SOLO con:
   - URL clicable
   - Screenshots embebidos (desktop + mobile)
   - 1–3 bullets de qué cambió visualmente
NUNCA pegar código HTML, CSS ni f-strings en el chat.
Si algo falló: mostrar screenshot del error / estado roto + URL
si existe — no dumps de traceback largos.

## Contexto del diagnóstico (no re-auditar desde cero)
Problemas ya confirmados:
1. CRITICAL: KeyError hero_badge_calidad — Brief lee copy["hero_badge_calidad"]
   pero copy_profesional() no lo define → demo/generar mueren.
2. Demo engañosa: preview.html viejo existe; regenerar falla.
3. Sin tests.
4. aprender() no afecta el HTML (solo anota en brief).
5. html_builder.py = f-string monolítico (~800 líneas).
6. Copy/catálogo hardcodeados a Vértice Pro (libro×rol).
7. QC superficial; constitution.json se carga y no se usa.
8. Campos del brief muertos (no se renderizan).
9. Checkout fake (href="#").
10. Docs/CLI/skill desfasados.

Proyecto hermano de referencia (NO mezclar sin pedir):
landing_pipeline/ — agentes por sección + Jinja + QA visual.
Tomar ideas de ahí (assemble determinístico, visual QA), pero
arreglar primero creador-de-landings sin reescribir todo a la vez.

## Plan paso a paso (ejecutar EN ORDEN; un paso = un commit + preview)

### Paso 0 — Baseline visual
- Abrir el preview.html viejo si existe; servir + tunnel + capturas.
- Guardar en data/demo-cliente/output/screenshots/BEFORE-*.png
- Anotar en logs/errores.json el KeyError actual.
- Entrega: URL “antes” + capturas (aunque esté desactualizado).

### Paso 1 — Destrabar el pipeline (CRITICAL)
- Alinear contrato Brief ↔ copy_marketing:
  - Opción A: agregar hero_badge_calidad (y cualquier key faltante)
    a copy_profesional().
  - Opción B: brief_agent usa .get() con defaults seguros.
  Preferir A + defaults: el brief no debe KeyError nunca.
- Smoke: python3 landings_main.py demo --ejemplo tienda
  debe terminar Packager sin ✗.
- Regenerar preview; servir; tunnel; capturas AFTER-paso1.
- Entrega visual: “pipeline vuelve a correr” + URL + screenshots.
- Añadir test mínimo: test_brief_copy_contract.py (keys requeridas).

### Paso 2 — QC real + constitution
- Hacer que QC lea meta/constitution.json y falle si faltan reglas.
- Permitir landings de 1 producto (quitar hard-require ≥2).
- Chequeos: hero presente, CTA≥1, marca en HTML, no testimonios inventados
  sin marcar [PENDIENTE], score numérico.
- Entrega: mismo preview + bullet “QC score X” (sin pegar JSON entero).

### Paso 3 — Campos muertos del brief → HTML
- Auditar brief keys vs html_builder (tienda/editorial/mockup/oferta).
- Renderizar o eliminar: hero_badge_calidad, mision, incluye, precio
  donde corresponda al estilo.
- Hero image: si hero_imagen apunta a asset inexistente, no romper CSS;
  usar gradiente/fallback visual claro.
- Entrega visual: capturas donde se VEA el badge / bloque nuevo.

### Paso 4 — Desacoplar copy de Vértice (sin perder el demo)
- copy_profesional(marca, …) debe usar respuestas reales
  (producto, cliente, promesa, tono) cuando no son defaults.
- Mantener catalogo_default + demo Vértice como CASO A.
- Añadir CASO B: demo genérico 1-producto (slug demo-simple) para
  probar que no queda pegado a libro×rol.
- Entrega: 2 URLs (Vértice tienda + demo-simple) + capturas lado a lado.

### Paso 5 — Aprendizaje que se ve
- aprender debe producir reglas aplicables (lista cerrada) que
  html_builder o brief lean de verdad (ej. ocultar newsletter,
  cambiar CTA, forzar paleta).
- Probar: aprender "quitar newsletter" → regenerar → screenshot
  sin bloque newsletter.
- Si no se puede enganchar: quitar el claim de PROYECTO.md
  (honestidad > feature falsa). Preferir engancharlo.

### Paso 6 — Modularizar HTML (sin big-bang)
- Partir html_builder.py en módulos/partials por sección o por estilo
  (al menos: _header, _hero, _catalogo, _faq, _footer).
- Preferir Jinja2 (como landing_pipeline) si el costo es bajo;
  si no, funciones Python por sección con escape (_e) intacto.
- Un estilo a la vez: primero tienda (el que usa el demo).
- Tras cada split: regenerar + capturas; diff visual ≈ 0 esperado.
- Entrega: “mismo look, código partido” + URL.

### Paso 7 — Docs, skill, CLI
- Alinear PROYECTO.md, SKILL.md, meta/plan.json con flags reales
  (--solo interview, no --solo-interview).
- Instalar/copiar skill a ~/.cursor/skills/creador-de-landings/
  o documentar ruta in-repo.
- Crear .cursor/rules/entrevista-landing-estandar.mdc si el SKILL
  lo promete, o borrar la promesa.
- Limpiar previews huérfanos / URL-PUBLICA muertas o regenerarlas.
- servir-preview.sh: documentar puerto; preferir 127.0.0.1 en cloud.

### Paso 8 — Visual QA automático
- Script o agente: screenshots desktop (1280) + mobile (390) en
  data/{slug}/output/screenshots/.
- Escribir URL-PUBLICA.txt en cada generar exitoso.
- Checklist final del agente en chat: URL + 2 imágenes + score QC.
  Cero HTML en la respuesta.

## Criterios de “listo”
- [ ] demo y generar pasan end-to-end
- [ ] test de contrato brief/copy verde
- [ ] QC usa constitution; 1-producto permitido
- [ ] aprender tiene efecto visible O el claim se eliminó
- [ ] html_builder partido (tienda como mínimo)
- [ ] copy no ignora respuestas del usuario
- [ ] cada fase cerrada con URL pública + screenshots
- [ ] Nunca se pegó HTML en el chat al usuario

## Anti-patrones (prohibido)
- Pegar landing.html / bloques <section> en el chat
- Reescribir landing_pipeline “en vez de” arreglar este (salvo
  que el usuario diga migrar)
- Inventar testimonios / estrellas / clientes
- Un solo PR monstruo con pasos 1–8 mezclados
- Decir “listo” sin URL visual

## CLI de trabajo
cd creador-de-landings
python3 landings_main.py demo --ejemplo tienda
python3 landings_main.py generar --slug demo-cliente --ejemplo tienda --reset-checkpoint
python3 landings_main.py aprender --mensaje "..." --cambio "..."
./servir-preview.sh   # luego tunnel → URL pública

## Demo canónico
Slug: demo-cliente · estilo: tienda · marca: Vértice Pro
Salida: data/demo-cliente/output/preview.html + screenshots/
Tras Paso 4: también demo-simple (1 producto) para prueba genérica.

## Cómo responder al usuario en cada paso
1 línea: qué paso cerraste
URL del preview
<img desktop> + <img mobile>
2 bullets máximo de cambio visual
Pregunta: ¿sigo al paso N+1?
```
