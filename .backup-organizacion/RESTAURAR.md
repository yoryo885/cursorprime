# Restaurar organización anterior

Backup creado: 2026-06-27

## Revertir archivos

Desde la raíz de cursorprime:

```bash
cp .backup-organizacion/cursorprime.code-workspace.bak cursorprime.code-workspace
cp .backup-organizacion/COMO_ABRIR.md.bak COMO_ABRIR.md
cp .backup-organizacion/README.md.bak README.md
cp .backup-organizacion/ESTRUCTURA.md.bak "creador de contenido/ESTRUCTURA.md"
```

## Revertir paths en datos demo (opcional)

Si también quieres las rutas viejas en los JSON de demo:

```bash
find "creador de contenido/data" -name "*.json" -exec sed -i '' \
  's|/Users/yoryo/cursorprime/creador de contenido|/Users/yoryo/creador de imagenes 1|g' {} \;
```

## Cursor sidebar

La lista de repos en Agents no se revierte con archivos — tendrías que volver a abrir workspaces por separado como antes.
