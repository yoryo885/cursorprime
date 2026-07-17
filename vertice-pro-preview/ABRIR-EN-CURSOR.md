# Ver la tienda en Cursor

1. **Puerto 8768** — el servidor ya corre en background (carrusel incluido).
2. Abre el panel **Ports / Puertos** (abajo en Cursor) → busca **Vértice Pro — Preview tienda**.
3. Clic en **Open in Browser** o en el globo 🌐.

URL directa:

```
http://localhost:8768/preview.html
```

Si no hay servidor:

- `Cmd/Ctrl+Shift+P` → **Tasks: Run Task** → **Vértice Pro: servir preview**
- O terminal:
  ```bash
  cd sitio-pdf/data/vertice-pro/output && python3 -m http.server 8768
  ```

Simple Browser manual: `Cmd/Ctrl+Shift+P` → **Simple Browser: Show** → pegar la URL de arriba.
