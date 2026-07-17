# Decisiones — Pipeline Sitio PDF (Vértice Pro)

Responde con letras (ej: `1A 2A 3B`) o confirma los defaults marcados con ★.

---

## 1. Salida del sitio

| Opción | Qué obtienes | Cuándo elegir |
|--------|--------------|---------------|
| **A ★ Shopify** | `theme.zip` + imágenes para subir al admin | Ya tienes `verticepro.myshopify.com` |
| **B** HTML solo | `preview.html` + assets (Vercel/Netlify) | Sin Shopify |
| **C** Ambos | Shopify + HTML espejo | Máxima flexibilidad |

**Default piloto:** A

---

## 2. Imágenes IA — proveedor

| Opción | Requisito | Calidad / velocidad |
|--------|-----------|---------------------|
| **A ★ OpenAI** | `OPENAI_API_KEY` en `.env` | Buena coherencia con prompt de marca |
| **B** Mock primero | Nada | Placeholders SVG; luego activas A |
| **C** Portada KDP existente | Solo reutilizar PNG de `libros a entender` | Sin hero nuevo; más rápido |

**Default piloto:** B → luego A cuando tengas key

---

## 3. Pack visual (qué generar)

Marca lo que quieres (mínimo recomendado ★):

- [ ] ★ **Hero** 1920×1080 — home principal
- [ ] ★ **Portada producto** — tarjeta del PDF (reusar Pareto si existe)
- [ ] ★ **Mockup móvil** — PDF en celular (prueba social)
- [ ] **Logo** Vértice Pro — símbolo + texto
- [ ] **3 iconos beneficios** — plan 10 semanas / tu rol / descarga
- [ ] **OG image** 1200×630 — compartir en redes
- [ ] **Favicon** 32×32

**Default piloto:** ★ hero + portada + mockup móvil

---

## 4. Estilo visual (marca)

| Opción | Descripción |
|--------|-------------|
| **A ★ Editorial profesional** | Azul marino `#1e3a5f`, blanco, acento `#2563eb`, tipografía serif en títulos |
| **B** Minimal tech | Negro/gris, sans-serif, estilo SaaS |
| **C** Cálido educativo | Verdes suaves, más “aula / salud” |

**Default piloto:** A

---

## 5. Copy — fuente

| Opción | Descripción |
|--------|-------------|
| **A ★ KDP existente** | Reutiliza `amazon_listing.txt` de Pareto |
| **B** Regenerar con agentes | Nuevo copy desde brief |
| **C** Tú escribes | Solo ensamblamos |

**Default piloto:** A

---

## 6. Producto piloto

| Opción | Slug |
|--------|------|
| **A ★** Pareto psicopedagogas | `pareto` |
| **B** Otro PDF | Indica título |

---

## 7. Precio mostrado en tienda

| Opción | Valor |
|--------|-------|
| **A** CLP | ej. $3.990 |
| **B ★** USD | $4.99 |
| **C** Ambos | Selector (más trabajo) |

---

## Lo que necesito de ti (checklist)

1. **Confirmar opciones** (1–7) o decir “defaults ★”
2. **¿Tienes `OPENAI_API_KEY`?** (sí/no → mock o real)
3. **¿Existe portada PNG de Pareto?** Ruta en tu Mac si no está en repo cloud
4. **Tagline oficial** — ¿“Aplicar en tu rol” va en hero o solo en footer?
5. **Email de contacto** para footer (opcional)

---

## Qué pasa después de tu respuesta

1. Completo `data/vertice-pro/inputs/marca.json`
2. Corro pipeline `--mock` → preview con estructura profesional
3. Si hay API key → segunda corrida con imágenes IA reales
4. Te paso enlace preview + zip Shopify
