# Radar de mejoras — emprendimientos cursorprime

**Fecha:** 2026-07-19  
**Skill:** `lluvia-de-ideas` · **Análisis live:** `analisis-de-proyectos/data/mejoras-emprendimientos-2026/`  
**Perspectiva:** qué acelera progreso real (ingreso + producción), no features cosméticas.

---

## 1. Mapa de lo que ya tienen

| Emprendimiento / sistema | Estado hoy | Cuello de botella |
|--------------------------|------------|-------------------|
| **Presencia digital 360** (audit → propuesta → web → WA) | Demos HTML (clínica-sol, ferretería, empanadas) | Ningún cliente real pagando; falta deploy + GBP |
| **Audit marketing** | Pipeline 5 agentes listo | Sin URL live + outreach sistematizado |
| **Wasap PYMEs** | Simulación mock | Sin Meta API / webhook / piloto |
| **Prospección Maps** | Idea (no construido) | Sin leads entrando al embudo |
| **Creador de contenido** | PNG/GIF/video mock | Kling real + empaquetado post-investigación |
| **Libros / KDP** | Skills listos | Sin PDF concreto publicado |
| **LinkedIn ghostwriter** | Generador de posts | Sin mes publicado + voice profile |
| **cursorprime (meta)** | Router + skills + cola | Mucha capacidad, poca monetización cerrada |

**Lectura profesional:** el stack está sobrado en *capacidad* y flojo en *cierre*. El progreso no viene de más skills; viene de **un embudo que cobra**.

---

## 2. Qué está moviendo el mercado (fuentes 2026)

### WhatsApp / CRM / agentes

| Fuente | Insight accionable |
|--------|-------------------|
| [WhatsApp AI Agent Guide 2026](https://agentic-whatsup.com/en/blog/whatsapp-ai-agent) | API oficial + human handoff + métricas (containment, CSAT) desde día 1 |
| [Conversational Marketing Playbook 2026](https://www.digitalapplied.com/blog/whatsapp-business-conversational-marketing-playbook-2026) | Meta restringe bots “ChatGPT genéricos”; ganan bots **por tarea** (pedidos, citas, FAQ) |
| [WhatsApp Business PYMES LATAM](https://faststrat.ai/whatsapp-business-pymes-latam-guia-2026/) | En LATAM WhatsApp es el canal; la IA debe armar calendario + medición alrededor |
| [WACRM open source](https://wacrm.tech/) + [tutorial Andy Cruz](https://youtu.be/ef69Z36ai9M) + [Coolify+n8n+Groq](https://www.youtube.com/watch?v=rJe0ccJu2eQ) | Self-host + Meta API + IA externa (n8n) es el patrón dominante open source |
| [n8n + Meta API free](https://github.com/YousefAutomates/whatsapp-api-free-n8n-automation) | Ruta rápida a piloto sin reinventar CRM |

### Audit local / SEO / agencia multi-cliente

| Fuente | Insight accionable |
|--------|-------------------|
| [Local SEO Automation Claude Code](https://ccforseo.com/blog/local-seo-automation-claude-code) | GBP + NAP + schema LocalBusiness + map pack = audit v2 vendible |
| [Manage 20 SEO clients Claude](https://ccforseo.com/blog/manage-20-seo-clients-claude-code) | Estructura `clients/{slug}/` + reportes en paralelo (ya la tienen a medias) |
| [GEO + IA LATAM](https://www.themarkethink.com/mkt-digital/5-agencias-geo-ia-latam/) | Nueva capa de oferta: aparecer en ChatGPT/Perplexity, no solo Google |
| [Marketing IA LATAM PYMES](https://faststrat.ai/marketing-ia-latam-tendencias-2026/) | Vender “departamento marketing virtual”, no “uso ChatGPT” |

### Contenido / KDP / LinkedIn

| Fuente | Insight accionable |
|--------|-------------------|
| [Faceless YouTube 2026](https://kompozy.io/ai-content/faceless-youtube) + [YT: new faceless](https://www.youtube.com/watch?v=hOUYIASWLhs) | Híbrido humano+IA; nichos tutoriales; AdSense solo no basta |
| [KDP honest AI 2026](https://ailearningguides.com/how-to-publish-a-book-with-ai-on-amazon-kdp-2026/) | Nichos estrechos + disclose AI; masa de libros genéricos muerta |
| [LinkedIn ghostwriting 2026](https://windmillgrowth.com/blogseo/state-of-linkedin-ghostwriting-2026) | Voice profile + pipeline (comentarios→DM); AI slop pierde engagement |

---

## 3. Mejoras priorizadas (impacto × esfuerzo)

Ordenadas por **aumento de progreso** (cash + aprendizaje de mercado).

### P0 — Cerrar el embudo (máximo ROI)

1. **Prospección → 10 audits → 3 propuestas → 1 cobro**  
   - Construir o MVP-manual el paso 0 (`prospeccion-maps-bot` / Places API).  
   - Checklist ya lo pide: “1 cliente paga” en auditorías.  
   - Sin esto, el resto del ecosistema es inventario.

2. **Audit v2: GBP + NAP + schema LocalBusiness**  
   - Extender `marketing-audit` con señales Google Business (categorías, fotos, reviews, Q&A).  
   - Diferenciador vs audit genérico web; ticket más fácil de justificar en clínicas/locales.

3. **Wasap: piloto task-scoped (no agente genérico)**  
   - Producto: bot de **pedidos / citas / FAQ** con handoff humano.  
   - Stack recomendado: Meta Cloud API + n8n (IA) ± WACRM (inbox).  
   - Plan B Evolution solo documentado; no venderlo como default.

### P1 — Profesionalizar entrega

4. **Deploy real de presencia digital**  
   - Vercel/Netlify + subdominio propio → luego dominio cliente.  
   - GBP post-deploy (ya en checklist).  
   - Métrica: 1 setup cobrado.

5. **GEO lite en informe de audit**  
   - Sección “¿te encuentran ChatGPT/Perplexity?” + recomendaciones de citabilidad.  
   - Bajo esfuerzo, narrativa innovadora LATAM 2026.

6. **Métricas operativas WhatsApp**  
   - En demos y propuestas: first-response time, % resuelto sin humano, opt-in.  
   - Convierte “tenemos bot” en “medimos negocio”.

### P2 — Sistemas internos que multiplican

7. **Encadenar investigación → contenido**  
   - Tras `analisis-de-proyectos`, auto-lote en `creador de contenido` (3 PNG + hook).  
   - Ya hay idea en cola lluvia; implementarla reduce fricción de validación.

8. **LinkedIn: voice profile + 1 mes publicado**  
   - Extender `ejecutivo_perfil.json` → ledger de voz; posts con anécdotas/números.  
   - Objetivo: inbound a Presencia digital, no vanity metrics.

9. **KDP: 1 título estrecho validado, no radar infinito**  
   - Elegir 1 nicho profesional LATAM → resumen → listing → publish.  
   - Radar semanal solo después del primer ingreso.

### P3 — Innovación (después de cobrar)

10. **WACRM white-label como upsell** (post-piloto Meta)  
11. **Agentes n8n + RAG** sobre menú/servicios del cliente (patrón Evolution+Gemini, pero preferible Meta)  
12. **Panel centro de control** → dashboard de embudo (leads → audits → $$$)

---

## 4. Matriz: sistema → mejora → por qué acelera

| Sistema | Mejora concreta | Por qué acelera progreso |
|---------|-----------------|--------------------------|
| `01-auditorias-locales` | GBP + GEO en PDF | Informe más vendible; menos “¿y esto para qué?” |
| `02-wasap-pymes` | Meta API + bot por tarea + n8n | Sale de mock; upsell natural del audit |
| `03-presencia-digital` | Deploy + GBP | Entregable vivo = prueba social |
| `marketing-audit` | Places API / NAP check | Escala multi-cliente (patrón agencias SEO) |
| `clientes/*` | Regla: todo trabajo deja metricas.json | Operación tipo agencia, no hobby |
| `creador de contenido` | Auto-pack post-análisis | Validación visual sin chat nuevo |
| `lluvia-de-ideas` | Aprobar solo ideas P0–P1 | Evita cola basura (hoy 18 pendientes genéricas) |
| `linkedin-ghostwriter` | Voice + pipeline DM | Canal B2B de captación |
| `libros a entender` | 1 KDP real | Ingreso pasivo secundario; prueba pipeline |

---

## 5. Plan de progreso (secuencia profesional)

```
Semana A: 10 locales → 5 audits (plantilla si falla script) → 3 outreach
Semana B: 1 propuesta cobrada OR 1 piloto gratis a cambio de caso
Semana C: Deploy web + GBP del piloto
Semana D: Bot WhatsApp task-scoped (Meta) + métricas
Semana E: Case study → LinkedIn + YouTube corto → siguiente lote
```

**Regla de oro:** no abrir skill/pipeline nuevo hasta tener **1 peso cobrado** o **1 caso publicado**.

---

## 6. Qué NO hacer (ruido vs progreso)

- Montar WACRM “para todos” sin cliente que lo pida  
- Agente WhatsApp genérico estilo ChatGPT (riesgo política Meta 2026)  
- Más skills en cola sin producto cobrado  
- Radar KDP semanal sin primer libro  
- Evolution API como oferta principal (ban risk)

---

## 7. Artefactos generados en esta corrida

| Artefacto | Ruta |
|-----------|------|
| Análisis live (14 fuentes) | `analisis-de-proyectos/data/mejoras-emprendimientos-2026/output/analisis.md` |
| Ideas lluvia (cola) | `lluvia-de-ideas/data/lluvia_mejoras-emprendimientos-2026/output/` |
| Este radar | `meta/radar-mejoras-emprendimientos-2026.md` |
| Prompt activo (refinado) | `creador de prompts/data/mejoras-emprendimientos-sistemas/output/prompts.md` |

---

## 8. Decisión pedida

Para seguir, elige **una** línea P0:

1. `arma prospección + 5 audits`  
2. `extiende audit con GBP/GEO`  
3. `lleva wasap a Meta API piloto`  

Sin esa elección, el progreso se diluye en mejoras paralelas.
