# Prompt completo — Pipeline de Landings (v7)

```
Usa landing-pipeline (carpeta landing_pipeline/).

## Qué es
Sistema tipo pipeline en Python (patrón Libros a Entender):
agentes en src/agents/, cada uno con una sola responsabilidad,
orquestados en secuencia, inputs/outputs en JSON.
Recibe datos de un negocio/producto y genera copy + diseño de
una landing completa, sección por sección, usando skills (.md).

## Regla de oro
Cada agente NO improvisa el estilo. Antes de generar, carga su
skill en src/skills/ y lo inyecta en el system prompt.
El LLM NUNCA ensambla HTML completo (causa de duplicaciones).
- LLM → solo copy (02–10) + tokens/layout (11a)
- HTML → 100% Python determinístico con Jinja2 (11b_assemble)

## NUEVO: agente de referencia visual (00_referencia.py)
Antes de 01_brief, el pipeline carga una lista curada a mano de
URLs de landings reales bien armadas (empieza con
https://filjos.com/) y extrae SOLO patrones estructurales — nunca
copia texto ni diseño literal. Devuelve referencia.json:
{
  "trust_badge_posicion": "arriba del todo, antes del hero",
  "hero_visual": "imagen real de producto, nunca texto duplicado",
  "testimonio_formato": "quote corto + nombre + ciudad entre paréntesis",
  "cta_por_bloque": "un único CTA claro por bloque, no botones compitiendo",
  "fuente": ["https://filjos.com/"]
}
referencia.json se pasa como contexto extra a 02_hero.py y a
11a_design_tokens.py, junto con brief.json y su skill. No reemplaza
ningún skill, los complementa. La lista de URLs es curada a mano
(vos la editás en src/config/referencias.json), nunca scraping
automático de "sitios similares".

## Fix del bug real: hero split con texto duplicado
En la última corrida, layout=hero_split generó una tarjeta con el
mismo título+bajada que el hero grande de abajo (duplicado DENTRO
de la misma sección, no detectado por section_counts porque es un
solo <section data-section="hero">).
Causa: hero_split reserva un panel visual para imagen de producto;
sin imagen real, el LLM rellenó ese panel repitiendo el copy.
Fix:
- 02_hero.py devuelve también "tiene_imagen": true|false
  (true solo si brief.json trae "imagen_hero" real).
- 11b_assemble.py fuerza hero_centrado si tiene_imagen=false,
  SIN pasar por el LLM ni por tokens.json["layout"]["hero"] — la
  variante split queda excluida por código si no hay imagen, no por
  instrucción de prompt.
- El panel visual de hero_split.html, cuando sí hay imagen, jamás
  recibe titulo/bajada como contenido — solo <img>.

## Estructura
landing_pipeline/
├── landing_main.py
├── src/
│   ├── agents/
│   │   ├── 00_referencia.py       # NUEVO: patrones de URLs reales
│   │   ├── 01_brief.py
│   │   ├── 02_hero.py … 10_footer.py
│   │   ├── 11a_design_tokens.py   # tokens + layout (sin HTML)
│   │   ├── 11b_assemble.py        # Jinja2, SIN LLM
│   │   ├── 12_qa.py
│   │   └── 13_visual_qa.py        # Playwright screenshots
│   ├── config/
│   │   └── referencias.json       # NUEVO: lista curada de URLs
│   ├── templates/                 # variantes Jinja2
│   ├── skills/                    # reglas por sección
│   ├── sections.py                # SECTION_ORDER + variantes
│   ├── pipeline.py
│   ├── llm_client.py
│   └── text_utils.py              # sanitize_prepend, naming
├── output/{slug}/
│   ├── brief.json, copy.json, tokens.json, referencia.json
│   ├── landing.html, qa_report.json
│   └── screenshots/mobile.png, desktop.png
└── logs/mejoras.json

## Flujo
0. 00_referencia → referencia.json (patrones de URLs curadas)
1. 01_brief → brief.json (nombre_producto, propuesta_valor, precio…)
2. 02_hero → 10_footer → acumulan copy.json (leen su skill + referencia.json)
3. 11a_design_tokens → tokens.json (colores + layout de lista cerrada)
4. 11b_assemble → landing.html (SECTION_ORDER una sola vez;
   hero_split solo si copy.hero.tiene_imagen=true)
5. 12_qa → qa_report.json (score, bugs_v2, section_counts, duplicado_intra_seccion)
6. 13_visual_qa → screenshots + overlap real (si no hay Playwright, skip)

SECTION_ORDER =
["hero","social_proof","problem","benefits","testimonials",
 "pricing","faq","cta_final","footer"]

## Variantes de layout (lista cerrada — el LLM solo elige nombres)
- hero: centrado | split (split excluido por código si no hay imagen real)
- benefits: tarjetas | lista_numerada
- pricing: una_columna | comparativa
Default si falta: centrado / tarjetas / una_columna.

## Bugs prevenidos por diseño
1. Copy duplicado ("desde desde") → sanitize_prepend
2. Overlap secciones → flujo normal, sin absolute/fixed de contenido,
   sin animaciones scroll-reveal (opacity:0 + translateY)
3. Acento inconsistente → un solo --accent; todos los .btn lo usan
4. Naming interno filtrado → solo nombre_producto / propuesta_valor
5. Testimonios silenciados → omitida:true + omisiones en qa_report
6. Hero/FAQ duplicados entre secciones → 11b renderiza cada
   data-section exactamente 1 vez (0 si omitida legítimamente)
7. NUEVO — Hero duplicado dentro de la misma sección (tarjeta split
   repitiendo el título) → hero_split requiere imagen real; sin ella,
   cae a hero_centrado por código, nunca por elección del LLM

## Conversión (v5+)
- Social proof: dato verificable; no inventar estrellas/clientes
- Precio: línea garantia bajo el CTA
- FAQ: pregunta de riesgo/garantía obligatoria
- CTA primario ≥ 3 (hero + mid beneficios + precio/cta final)
- NUEVO: patrones de referencia.json (badge de confianza arriba del
  todo si hay dato real; testimonio "Nombre (Ciudad)")

## Skills (formato fijo)
# Skill: {Sección}
## Regla
## Obligatorio
## Ejemplo
## Output esperado (JSON)

Skills: hero, social_proof, problem, benefits, testimonials,
pricing, faq, cta, footer, design, qa_checklist.

## Contrato técnico
- Cada agente: def run(input: dict) -> dict
- 11b_assemble NO importa llm_client
- 00_referencia NO hace scraping libre: solo lee src/config/referencias.json
- Reintento: --retry-from {agente} / --solo {agente}
- Sin API key → MOCK; con ANTHROPIC_API_KEY → Claude
- Mostrar resultado SIEMPRE visual (URL pública o screenshots),
  NUNCA pegar código HTML en el chat

## CLI
cd landing_pipeline
python3 landing_main.py run --demo
python3 landing_main.py run --input meta/ejemplo-negocio.json --slug mi-marca
python3 landing_main.py run --slug vertice-pro --retry-from 07_pricing
python3 landing_main.py run --slug vertice-pro --retry-from 02_hero  # para forzar fix del hero split

## Demo actual
Slug: vertice-pro
Layout: hero=centrado (forzado por falta de imagen real — antes era
split y ahí estaba el bug de la tarjeta duplicada), benefits=lista_numerada,
pricing=comparativa
Outputs: output/vertice-pro/landing.html + screenshots/
Pedile al agente que confirme en qa_report.json que
duplicado_intra_seccion.hero = false antes de darlo por bueno.
```
