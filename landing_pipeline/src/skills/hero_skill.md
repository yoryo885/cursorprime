# Skill: Hero

## Regla
Título + bajada corta + botón. 3 segundos para decir qué hace el producto
y para quién. Nada de relleno ni frases genéricas tipo "Bienvenido a...".

## Obligatorio
- Título: máximo 8 palabras, beneficio concreto, no descripción de feature.
- Bajada: 1 frase, refuerza el título, no lo repite.
- Botón: verbo de acción + resultado. Nunca "Enviar" o "Click aquí".
- `tiene_imagen`: true solo si brief trae `imagen_hero` real (URL/path).
- Sin imagen real, el assemble fuerza hero_centrado (split prohibido).

## Ejemplo
"Lee lo esencial de un libro en 15 minutos" · [Descargar ahora]

## Output esperado (JSON)
{ "titulo": "", "bajada": "", "cta": "", "tiene_imagen": false, "imagen_hero": "" }
