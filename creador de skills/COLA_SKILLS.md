# Cola de skills — paso a paso

No crear todas de golpe. Una por sesión, probar, iterar.

## Estado

| # | Skill | Tipo | Proyecto | Estado |
|---|-------|------|----------|--------|
| 1 | guion-a-video | workflow | creador de contenido | **Hecho** ✓ |
| 2 | evaluar-idea | workflow | ideas de proyectos | **Hecho** ✓ |
| 3 | resumidor-kdp | workflow | libros a entender | **Hecho** ✓ |
| 4 | copy-linkedin | capacidad | linkedin-ghostwriter | **Hecho** ✓ |
| 5 | crear-pipeline | pipeline-python | general | **Hecho** ✓ |
| 6 | hooks-redes | capacidad | creador de contenido | **Hecho** ✓ |
| 7 | captions-redes | capacidad | creador de contenido | **Hecho** ✓ |
| 8 | thumbnail-social | workflow | creador de contenido | **Hecho** ✓ |
| 9 | find-skills | workflow | general | **Hecho** ✓ |
| 10 | gestion-proyecto | workflow | general | **Hecho** ✓ |
| 11 | landing-lanzamiento | workflow | general | **Hecho** ✓ |
| 12 | whatsapp-marketing | capacidad | ideas de proyectos | **Hecho** ✓ |
| 13 | audit-marketing | capacidad | ideas de proyectos | **Hecho** ✓ |

## Comandos

```bash
cd "/Users/yoryo/cursorprime/creador de skills"

# Paso 1
python3 creador_skills_main.py --slug guion-a-video --reset-checkpoint

# Paso 2 (cuando digas)
python3 creador_skills_main.py --slug evaluar-idea --reset-checkpoint

# ... etc
```

## Después de cada skill

1. Probar en chat: `usa nombre-skill`
2. Ajustar si falla → editar `catalogo/{slug}.json` y regenerar
3. Marcar `estado: hecho` en `meta/cola_skills.json`
