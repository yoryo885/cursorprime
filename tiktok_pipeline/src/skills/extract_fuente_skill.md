# Skill: Extract Fuente (solo lectura)

## Regla
Este pipeline es **aparte** de `libros a entender`. Nunca modifica el PDF ni el markdown fuente. Solo **lee** la salida y pesca ideas centrales para transformarlas en guion de video.

## Obligatorio
- Entrada: ruta a `.md` (preferido) o `.pdf` de un resumen ya generado.
- Extraer 3–7 ideas centrales (prioridad: sección «Ideas del PDF» / bullets citadas).
- No reescribir ni guardar sobre la fuente.
- Si no hay fuente, devolver ideas vacías y dejar que el resto del pipeline use solo `--tema`.

## Ejemplo
Fuente: resumen Pareto → ideas:
1. El 20% de causas produce el 80% de efectos
2. Separa lo vital de lo secundario
3. La proporción no es exacta (puede ser 10/90)

## Output esperado (JSON)
{
  "fuente_path": "",
  "titulo_fuente": "",
  "ideas_centrales": ["", "", ""],
  "extracto_corto": "",
  "modo": "solo_lectura",
  "confidence": "medium"
}
