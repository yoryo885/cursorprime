# Cómo publicar tu tienda Vértice Pro en Shopify

**No necesitas GitHub.** Tienes dos caminos; el **A** es el más fácil.

---

## Camino A — Usar Horizon (ya lo tienes) + copiar textos

1. En Shopify app → **Tienda online** → **Temas** → **Editar tema**.
2. Quita la contraseña: **Preferencias** → desactiva «Proteger tienda con contraseña».
3. En la home, edita sección por sección y pega los textos de `entregables/copy-home.md`.
4. **Productos** → **Añadir producto**:
   - Nombre: `Pareto para psicopedagogas en 10 semanas`
   - Marca: `Vértice Pro`
   - Precio: ej. $3.990 CLP o $4.99 USD
   - **Medios**: sube la portada del PDF
   - Descripción: copia de `entregables/copy-producto-pareto.md`
   - Abajo en **Tipo de producto** → marca **Digital** o instala app **Digital Downloads**
   - Sube el archivo PDF en la app de descargas
5. **Guardar** y **Vista previa**.

---

## Camino B — Subir tema custom (ZIP)

1. En tu Mac/PC, comprime la carpeta `theme/` en un `.zip` (solo el contenido dentro de `theme/`, no la carpeta padre).
2. Shopify → **Temas** → **Importar** → **Subir archivo zip**.
3. **Publicar** el tema «Vértice Pro PDF».
4. Crea el producto PDF como en el paso 4 del Camino A.

---

## ¿GitHub?

Solo si más adelante contratas a un desarrollador para cambiar código del tema. **Para vender PDFs no lo necesitas.**

---

## Archivos incluidos

| Archivo | Para qué |
|---------|----------|
| `entregables/preview.html` | Ver el diseño en el navegador antes de Shopify |
| `entregables/copy-home.md` | Textos de la home para pegar |
| `entregables/copy-producto-pareto.md` | Descripción del primer PDF |
| `theme/` | Tema Shopify listo para zip |
