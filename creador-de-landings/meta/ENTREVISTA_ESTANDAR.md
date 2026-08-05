# Entrevista estándar (fija)

Fuente: `meta/preguntas.json` — **siempre las mismas**.

## Protocolo (agente)

Cada idea de tienda / landing → preguntar esto (1 mensaje):

1. Idea (frase + URL ref)
2. Marca
3. Qué vendes
4. Para quién
5. Promesa
6. ¿Catálogo varios productos?
7. CTA
8. Precio
9. Tono (editorial | cercano | directo)
10. Estilo (editorial | tienda | mockup | oferta | auto)
11. Clima color (cálido | frío | neutro | oscuro | auto)
12. Paleta (A | B | C | auto) ← el agente propone 3
13. Referencia visual (opcional)
14. Extra / no puede faltar (opcional)

Luego: guardar respuestas → generar HTML.

## CLI

```bash
python3 landings_main.py preguntas
python3 landings_main.py entrevista --slug mi-marca
```
