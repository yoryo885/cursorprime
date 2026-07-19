# Catálogo Vértice Pro — cómo ordenar la landing

## Regla de oro: dos capas, no mezclar

| Capa | Qué muestra | Ejemplo |
|------|-------------|---------|
| **1. Serie (libros famosos)** | El libro fuente | Pareto · Hábitos atómicos · Kahneman |
| **2. Guías (productos)** | Libro × Rol | Pareto para psicopedagogas · Hábitos para abogados |

El visitante entiende: *«Estos son los libros que adaptamos»* → *«Esta es la versión para mi oficio»*.

---

## En la landing (HTML / Shopify)

```
HERO
  Carrusel → solo LIBROS de la serie (3–5 max)
  Caption  → nombre del libro + «Aplica en tu rol»

SECCIÓN «Guías para tu rol»
  Filtros  → Psicopedagogas | Abogados | Soldadores | Docentes | …
  Grid     → productos filtrados (libro × rol)

SECCIÓN «Más vendidas» (opcional)
  2–4 destacados reales de Shopify
```

---

## Modelo de datos (`marca.json`)

```json
"serie_libros": [
  { "slug": "pareto", "titulo": "El principio de Pareto", "autor": "Antoine Delers" }
],
"roles": [
  { "slug": "psicopedagogas", "nombre": "Psicopedagogas" }
],
"catalogo_guias": [
  {
    "slug": "pareto-psicopedagogas",
    "libro": "pareto",
    "rol": "psicopedagogas",
    "titulo": "Pareto para psicopedagogas en 10 semanas",
    "disponible": true
  }
]
```

**SKU / producto Shopify** = una fila de `catalogo_guias`.  
**Colecciones Shopify** (futuro): por rol (`/collections/psicopedagogas`) o por libro (`/collections/pareto`).

---

## Convención de nombres

```
{título libro corto} para {rol} en 10 semanas
```

Ejemplos:
- Pareto para psicopedagogas en 10 semanas
- Hábitos atómicos para abogados en 10 semanas
- Pareto para soldadores en 10 semanas

---

## Evitar colapso de información

1. **Carrusel:** máximo 5 libros; sin roles.
2. **Filtro por rol:** un rol activo a la vez; grid max 6 visibles.
3. **Próximamente:** guías no disponibles con opacidad, sin mezclar con disponibles arriba.
4. **No repetir** el carrusel en el grid.

---

## Escalar (muchas guías)

| Guías totales | Recomendación |
|---------------|---------------|
| &lt; 12 | Filtro por rol en la home |
| 12–40 | Home por rol + página colección por rol |
| 40+ | Matriz libro×rol en página aparte; home solo destacados |
