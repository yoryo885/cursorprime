# Estructura — Creador de Contenido

## Abrir el proyecto

Abre el workspace raíz (no esta subcarpeta sola):

```
/Users/yoryo/cursorprime/cursorprime.code-workspace
```

Luego en Explorer (`⌘⇧E`): `cursorprime → creador de contenido`.

## Carpetas

```
creador de contenido/
├── imagenes/      ← módulo PNG
├── gifs/          ← módulo GIF
├── videos/        ← módulo MP4
├── pdf/           ← módulo PDF
├── operador/      ← documentación del pipeline
├── src/           ← core + pipeline.py
└── data/{slug}/   ← salidas por lote
    ├── imagenes/
    ├── gifs/
    ├── videos/
    └── output/
```

## Chats en Cursor (Agents)

Puedes tener **un chat por módulo** — es una forma válida de trabajar:

```
creador de contenido          ← chat/repo raíz (nombre del proyecto)
├── imagenes                  ← chat → carpeta imagenes/
├── gifs                      ← chat → carpeta gifs/
├── video                     ← chat → carpeta videos/
└── operador de pipeline      ← chat → src/ + operador/
```

Cada chat guarda el hilo de mejoras de ese módulo. Para **editar archivos**, usa Explorer (`⌘⇧E`); para **iterar con el agente**, el chat del módulo.

## Prompts compartidos

Usa `../creador de prompts` para generar prompts antes de correr un lote.
