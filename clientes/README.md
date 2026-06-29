# Clientes — espacio de trabajo con memoria

Capa opcional sobre cursorprime. Cada **cliente** tiene tono, marca y reglas; cada **proyecto** define qué pipelines correr y dónde guardar entregables.

## Por qué existe (y qué no cubre el router global)

`router.py` en la raíz resuelve **intención → skill** según palabras en tu mensaje. No sabe:

- en qué cliente estás trabajando
- qué tono o prohibiciones aplicar
- qué `slug` usar en los pipelines
- en qué orden encadenar estratega → copy → visual
- dónde copiar los entregables finales

Eso lo resuelven las **reglas de enrutamiento por proyecto** en `.cursor/rules/` dentro de cada carpeta de cliente y proyecto.

```
Mensaje del usuario
       ↓
router.py (global)     → skill genérico: copy-linkedin, guion-a-video…
       +
reglas del proyecto    → slug, tono, orden, entregables, prohibiciones
       ↓
Pipeline con contexto correcto
```

## Estructura

```
clientes/
├── _plantilla/              ← copiar para cada cliente nuevo
│   ├── CLIENTE.md
│   ├── perfil.json
│   ├── .cursor/rules/
│   ├── templates/
│   └── proyectos/_ejemplo/
└── {nombre-cliente}/
    └── proyectos/{slug}/
        ├── brief.json
        ├── CONTEXTO.md
        ├── .cursor/rules/proyecto.mdc   ← enrutamiento de ESTE proyecto
        └── entregables/
```

## Crear un cliente nuevo

```bash
cd ~/cursorprime/clientes
cp -r _plantilla mi-cliente
# Renombrar proyectos/_ejemplo → proyectos/mi-campana-q2
# Editar CLIENTE.md, perfil.json, brief.json, CONTEXTO.md
# Ajustar .cursor/rules/proyecto.mdc con slug y objetivos reales
```

## Usar en Cursor

1. Abre `cursorprime.code-workspace` (como siempre).
2. Crea un chat titulado `{cliente} · {proyecto}`.
3. Referencia la carpeta del proyecto: `@clientes/mi-cliente/proyectos/mi-campana-q2/`
4. Pide el trabajo en lenguaje natural — el agente lee reglas globales + cliente + proyecto.

## Flujo típico (equipo de marketing)

| Paso | Rol | Skill / pipeline | Salida |
|------|-----|------------------|--------|
| 1 | Estratega | `audit-marketing` o `analisis-de-proyectos` | brief ampliado en `CONTEXTO.md` |
| 2 | Copy | `copy-linkedin`, `captions-redes`, `landing-lanzamiento` | markdown en `entregables/copy/` |
| 3 | Visual | `hooks-redes` → `creador de contenido` | PNG/GIF en pipeline + copia a `entregables/` |
| 4 | QC | revisión humana | aprobar antes de publicar |

Los slugs de pipeline deben coincidir con `brief.json` → campo `pipeline_slug`.

## Enlace con pipelines existentes

Los pipelines siguen en sus carpetas (`creador de contenido/data/{slug}/`, etc.). La carpeta `entregables/` es el **punto de reunión** del cliente — copia o documenta ahí lo generado.
