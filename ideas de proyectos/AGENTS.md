# Ideas de proyectos — Evaluador

Evalúa ideas **antes** de abrir una rama nueva (libros a entender, proyectos/x, etc.).

## Comando

```bash
python evaluar.py ideas/cola-pedidos-whatsapp.json
python evaluar.py --texto "Mi idea..."
python evaluar.py listar
```

## Salida

```
evaluaciones/{slug}/
├── veredicto.json
└── informe.md   → PDF opcional vía libros a entender
```

## Roles

| Pieza | Rol |
|-------|-----|
| **Evaluador** (esta carpeta) | ¿Sirve? ¿Margen? ¿Escala? |
| **Yo (Cursor)** | Refino evaluación, diseño ramas, construyo si autorizas |
| **libros a entender** | Producción PDF + marketing (otra rama) |

## Gate construcción

Solo crear código en `proyectos/` si el usuario dice: `construye`, `armado`, `crea el proyecto`.

Reglas completas: [EVALUADOR.md](EVALUADOR.md)
