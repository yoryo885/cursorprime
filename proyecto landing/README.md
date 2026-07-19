# proyecto landing — Vértice Pro

**Carpeta única en cursorprime** con todo lo de la landing de venta (guías PDF).

Tienda: [verticepro.myshopify.com](https://verticepro.myshopify.com)

En el futuro: **`proyecto web/`** para sitio completo. Por ahora solo landing.

---

## Ubicación en cursorprime

```
cursorprime/
└── proyecto landing/          ← estás aquí
    ├── preview/               ← ver la landing (HTML)
    ├── shopify/               ← subir a Shopify (zip + theme código)
    ├── copy/                  ← textos para pegar
    ├── scripts/               ← regenerar desde pipeline
    └── README.md
```

Pipeline generador (cursorprime): `../sitio-pdf/`

---

## Archivos que necesitas

| Para qué | Dónde |
|----------|--------|
| **Ver la landing** | `preview/index.html` |
| **Subir a Shopify** | `shopify/vertice-pro-theme.zip` |
| **Guía Shopify** | `shopify/COMO-SUBIR-A-SHOPIFY.md` |
| **Textos home / producto** | `copy/copy-home.md`, `copy/copy-producto-pareto.md` |
| **Portada Pareto (foto)** | `preview/assets/portada-pareto.png` |
| **Código theme Liquid** | `shopify/theme/` |

---

## Ver en el navegador

**Lo más simple (Cursor):**

1. Abre `preview/versiones.html` en el editor
2. Clic derecho → **Open with Live Preview** / **Simple Browser: Show**
3. Elige la versión A–F desde el menú (no expiran, son archivos locales)

Landing actual: `preview/index.html` (mismo folder, mismos `assets/`).

```bash
open "proyecto landing/preview/versiones.html"
# o solo la actual:
open "proyecto landing/preview/index.html"
```

Servidor local (opcional):

```bash
cd preview && python3 -m http.server 8768
# http://localhost:8768/versiones.html
```

En Cursor: **Cmd+Shift+B** (task «Vértice Pro: abrir en Browser»).

---

## Subir a Shopify

1. Admin → **Tienda online** → **Temas**
2. **Agregar tema** → sube **`shopify/vertice-pro-theme.zip`**
3. **Publicar** → **Personalizar**

Detalle: `shopify/COMO-SUBIR-A-SHOPIFY.md`

**No pegues el HTML** — usa el zip.

---

## Regenerar diseño

```bash
bash "proyecto landing/scripts/sync-desde-pipeline.sh"
```

O desde `sitio-pdf/`:
```bash
python3 sitio_pdf_main.py generar --slug vertice-pro --producto pareto --mock --reset-checkpoint
```

---

## Cliente

Vértice Pro · carpeta cliente: `clientes/vertice-pro/CLIENTE.md`
