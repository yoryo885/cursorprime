# Evaluador de proyectos

Reglas que sigue el evaluador (código + cerebro en Cursor).

## Entrada

`ideas/{slug}.json` o texto libre con: problema, cliente, modelo de negocio, mercado.

## Salida

```
evaluaciones/{slug}/
├── veredicto.json
└── informe.md
```

## Veredicto

| Valor | Cuándo |
|-------|--------|
| `viable` | score ≥ 65, margen posible, escala razonable |
| `condicional` | score 40–64 o mucha incertidumbre |
| `descartar` | score < 40 o bloqueador crítico |

## Campos obligatorios en veredicto.json

- `veredicto`, `score` (0–100), `confidence` (0–1)
- `margen`: `{min, max, point, unidad}` — siempre rango, nunca un solo número
- `escala`: `{sirve: bool, nota}`
- `riesgos`: top 3
- `siguiente_paso`: una acción concreta
- `warnings`: incertidumbres

## Reglas

1. No inventar cifras de mercado — si no hay datos, `confidence` ≤ 0.5
2. Margen siempre en rango min/max
3. Evaluar antes de construir cualquier rama nueva
4. PDF opcional: pasar `informe.md` a libros a entender

## Comando

```bash
python evaluar.py ideas/mi-idea.json
python evaluar.py --texto "Descripción del problema..."
python evaluar.py --listar
```
