# Creador de Skills

Genera **SKILL.md** para Cursor e instala en `~/.cursor/skills/`.

## Comando

```bash
cd "/Users/yoryo/cursorprime/creador de skills"
python3 creador_skills_main.py --slug guion-a-video --reset-checkpoint
```

Desde catálogo (sin copiar a data/):
```bash
python3 creador_skills_main.py --slug evaluar-idea
```

## Cola paso a paso

Ver `COLA_SKILLS.md` y `meta/cola_skills.json`.

| # | Skill | Comando |
|---|-------|---------|
| 1 | guion-a-video | `--slug guion-a-video` |
| 2 | evaluar-idea | `--slug evaluar-idea` |
| 3 | resumidor-kdp | `--slug resumidor-kdp` |
| 4 | copy-linkedin | `--slug copy-linkedin` |
| 5 | crear-pipeline | `--slug crear-pipeline` |

## Entrada solicitud.json

```json
{
  "nombre": "mi-skill",
  "tipo": "workflow",
  "proyecto_destino": "creador-de-contenido",
  "triggers": ["palabra clave"],
  "proceso": "Qué hace...",
  "pasos": ["Paso 1", "Paso 2"],
  "reglas": ["Regla 1"]
}
```

## Invocar en chat

`usa creador-de-skills`
