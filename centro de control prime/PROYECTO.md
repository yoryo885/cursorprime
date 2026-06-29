# Centro de control prime

Panel de **solo lectura** que escanea el ecosistema cursorprime y muestra inventario, estadísticas y estado del flujo fábrica.

## Qué hace

- Lee JSON y manifests de: `analisis-de-proyectos`, `lluvia-de-ideas`, `ideas de proyectos`, `creador de contenido`, `creador de prompts`, `creador de skills`, skills en `~/.cursor/skills/`
- Genera:
  - `meta/inventario.json` — datos completos
  - `output/panel.html` — **HUD interactivo** (gráficos Chart.js, anillos SVG, pestañas)
  - `output/dashboard.canvas.tsx` — Canvas en Cursor

## Comandos

```bash
cd "centro de control prime"
python3 panel_main.py refresh   # escanear y regenerar
python3 panel_main.py resumen   # último resumen en consola
```

## No hace

- No modifica otros proyectos
- No es landing de venta
- No requiere servidor ni coste ($0 local)

## Flujo en el ecosistema

```
analisis → lluvia/cola → ideas/evaluar → contenido
                ↑
         centro de control (lee todo)
```
