# Cómo publicar Vértice Pro en Shopify

**Archivo listo:** `sitio-pdf/data/vertice-pro/output/vertice-pro-theme.zip`

---

## Paso 1 — Importar tema

1. Shopify Admin → **Tienda online** → **Temas**
2. **Importar tema** → sube `vertice-pro-theme.zip`
3. **Publicar** el tema «Vértice Pro PDF v2»

Incluye: carrusel hero, paleta crema/dorado, portadas SVG, carrito, colección, 404, búsqueda y páginas.

---

## Paso 2 — Quitar contraseña

**Preferencias** → desactiva «Proteger tienda con contraseña».

---

## Paso 3 — Crear producto PDF

**Productos** → **Añadir producto**:

| Campo | Valor |
|-------|--------|
| Nombre | Pareto para psicopedagogas en 10 semanas |
| Marca | Vértice Pro |
| Precio | $4.99 USD (o $3.990 CLP) |
| Imagen | Sube `portada-pareto.svg` o PNG |
| Descripción | Copia de `entregables/copy-producto-pareto.md` |
| Tipo | Digital |

Instala app **Digital Downloads** (o Shopify Files) y sube el PDF.

---

## Paso 4 — Colección

Crea colección **Todas las guías** y añade el producto. En el editor del tema, sección **Más vendidas** → elige esa colección.

---

## Paso 5 — Páginas legales (recomendado)

**Páginas** → crea Privacidad y Términos de descarga digital.

---

## Regenerar zip

```bash
cd sitio-pdf
python3 sitio_pdf_main.py generar --slug vertice-pro --producto pareto --mock --reset-checkpoint
```

Salida: `data/vertice-pro/output/vertice-pro-theme.zip`

---

## ¿GitHub?

No necesario para vender PDFs. Solo si contratas desarrollo del tema.
