# Vértice Pro — Landing (Shopify)

**Carpeta única** con todo lo de la landing de venta de guías PDF.  
En el futuro: `proyectos/web/` para sitio completo; **por ahora solo landing**.

Tienda: [verticepro.myshopify.com](https://verticepro.myshopify.com)

---

## Dónde está cada cosa

| Qué necesitas | Archivo / carpeta |
|---------------|-------------------|
| **Ver la landing en el navegador** | `preview/index.html` (+ carpeta `preview/assets/`) |
| **Subir a Shopify** | `shopify/vertice-pro-theme.zip` |
| **Guía paso a paso Shopify** | `shopify/COMO-SUBIR-A-SHOPIFY.md` |
| **Textos para pegar en Shopify** | `copy/copy-home.md`, `copy/copy-producto-pareto.md` |
| **Portada real Pareto (PNG)** | `preview/assets/portada-pareto.png` |
| **Regenerar desde cursorprime** | `scripts/sync-desde-pipeline.sh` |

---

## Ver la landing en tu Mac

1. Abre la carpeta `preview/` en Finder.
2. Doble clic en **`index.html`**  
   (debe abrirse con `assets/` al lado; si no carga imágenes, sirve con un servidor local).

**En Cursor:** abre `preview/index.html` o usa el task «Vértice Pro: abrir en Browser».

**Servidor local rápido:**
```bash
cd preview && python3 -m http.server 8768
# Abre http://localhost:8768/index.html
```

---

## Subir a Shopify (resumen)

1. Admin Shopify → **Tienda online** → **Temas**
2. **Agregar tema** → **Subir ZIP** → elige **`shopify/vertice-pro-theme.zip`**
3. **Publicar** el tema «Vértice Pro PDF v2»
4. **Personalizar** → sección «Más vendidas» → tu colección con Pareto
5. App **Digital Downloads** + PDF del producto
6. Quitar contraseña de la tienda

Detalle: `shopify/COMO-SUBIR-A-SHOPIFY.md`

---

## Regenerar landing (cuando cambies diseño en cursorprime)

Desde la raíz del repo:
```bash
bash clientes/vertice-pro/proyectos/landing/scripts/sync-desde-pipeline.sh
```

O manualmente:
```bash
cd sitio-pdf
python3 sitio_pdf_main.py generar --slug vertice-pro --producto pareto --mock --reset-checkpoint
# Luego copia output → esta carpeta (o corre el script de arriba)
```

**Fuente del pipeline:** `sitio-pdf/` (no edites solo el zip a mano; regenera y sincroniza).

---

## Estructura

```
landing/
├── README.md              ← estás aquí
├── preview/
│   ├── index.html         ← landing HTML (vista previa)
│   └── assets/            ← portadas, mockups, PNG Pareto
├── shopify/
│   ├── vertice-pro-theme.zip
│   └── COMO-SUBIR-A-SHOPIFY.md
├── copy/
│   ├── copy-home.md
│   └── copy-producto-pareto.md
└── scripts/
    └── sync-desde-pipeline.sh
```

---

## Nota importante

**No pegues `index.html` dentro de Shopify.**  
Shopify usa el **ZIP del theme** (`shopify/vertice-pro-theme.zip`), que ya convierte el diseño en secciones editables.

---

## Próximo: carpeta `web/`

Cuando tengas sitio más allá de la landing de venta (blog, SEO, páginas extra), crearemos:

`clientes/vertice-pro/proyectos/web/`

Por ahora todo vive en **`landing/`**.
