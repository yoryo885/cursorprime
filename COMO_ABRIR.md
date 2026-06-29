# Cómo abrir Cursor — cursorprime

## Regla de oro

**Un solo workspace:** abre siempre `cursorprime.code-workspace`.  
No abras cada proyecto por separado desde el home.

```
/Users/yoryo/cursorprime/cursorprime.code-workspace
```

---

## Estructura en disco

```
cursorprime/
├── creador de prompts/      ← prompts compartidos para todos
├── creador de contenido/    ← pipeline PNG · GIF · Video · PDF
├── libros a entender/       ← PDFs, resúmenes, maquetación
├── ideas de proyectos/      ← evaluación de ideas
└── linkedin-ghostwriter/    ← proyecto aparte (ver abajo)
```

### linkedin-ghostwriter

Proyecto **independiente**. Si trabajas solo en LinkedIn, ábrelo aparte:

```
/Users/yoryo/cursorprime/linkedin-ghostwriter
```

No forma parte del flujo de pipelines compartidos.

---

## Pasos para limpiar el sidebar de Agents

Si ves varios repos (`creador de imagenes 1`, `creador de prompts`, etc.) son **workspaces viejos abiertos en paralelo**.

1. `File → Close Folder` — repite hasta que no quede ninguno
2. `File → Open Workspace from File…`
3. Elige `cursorprime.code-workspace`
4. Usa **Explorer** (`⌘ + Shift + E`) para carpetas reales

---

## Agents vs Explorer

| Panel | Qué es | ¿Para qué? |
|-------|--------|------------|
| **Agents** | Chats con memoria de contexto | Iterar, mejorar, preguntar por módulo |
| **Explorer** (`⌘⇧E`) | Archivos del disco | Editar código, ver carpetas reales |

**No son lo mismo.** Un chat llamado `video` no abre la carpeta `videos/` — pero **sí puede ser el lugar correcto** para hablar de ese módulo.

---

## Chats por módulo — válido y útil

Tener un chat por pieza del proyecto **está bien** si te ayuda a:

- Enfocarte en mejorar solo GIF, solo video, etc.
- Retomar contexto sin mezclar conversaciones
- Ver mentalmente cómo está armado el pipeline

Ejemplo en **creador de contenido**:

| Chat (Agents) | Carpeta de código (Explorer) | Para qué |
|---------------|------------------------------|----------|
| `imagenes` | `creador de contenido/imagenes/` | Mejorar módulo PNG |
| `gifs` | `creador de contenido/gifs/` | Mejorar módulo GIF |
| `video` | `creador de contenido/videos/` | Mejorar módulo MP4 |
| `operador de pipeline` | `creador de contenido/src/` + `operador/` | Orquestador y flujo general |

Lo que **sí conviene** renombrar: el repo/chat raíz de `creador de imagenes 1` → **creador de contenido** (nombre alineado con la carpeta). Ver [cómo renombrar](#cómo-renombrar-en-cursor) abajo.

Lo que **no hace falta borrar**: los chats de módulo. Solo archívalos si ya no los usas.

---

## Cómo renombrar en Cursor

### Renombrar un chat (ej. `video`, `gifs`, `imagenes`)

1. En el sidebar **Agents**, pasa el mouse sobre el chat
2. Clic en los **tres puntos** `⋯` o **clic derecho** → **Rename**
3. Escribe el nombre nuevo y Enter

Alternativa: abre el chat y arriba, donde dice el título, haz **clic** para editarlo.

---

### Renombrar el repo `creador de imagenes 1` → `creador de contenido`

**No se puede renombrar con un botón.** Ese nombre es la carpeta que abriste hace tiempo (`~/creador de imagenes 1`, que ya no existe en disco).

Para que aparezca **creador de contenido**:

1. `File → Open Folder…`
2. Elige:
   ```
   /Users/yoryo/cursorprime/creador de contenido
   ```
3. En Agents verás una entrada nueva llamada **creador de contenido**

Tus chats viejos (`video`, `gifs`, etc.) **siguen bajo** `creador de imagenes 1` — Cursor no los mueve solos. Puedes:

| Opción | Qué pasa |
|--------|----------|
| **Seguir usando el bloque viejo** | Funciona igual; solo el nombre está desactualizado |
| **Crear chats nuevos** bajo `creador de contenido` | Empiezas limpio con el nombre correcto |
| **Abrir solo cursorprime** | Un workspace; chats agrupados bajo `cursorprime` |

Atajo recomendado si quieres todo junto:

```
File → Open Workspace from File…
→ /Users/yoryo/cursorprime/cursorprime.code-workspace
```

Los chats de módulo los creas o renombras tú dentro de **cursorprime** o **creador de contenido**.

---

## Nombre viejo → nombre actual

| Antes (chat o workspace) | Ahora (carpeta real) |
|--------------------------|----------------------|
| creador de imagenes 1 | `cursorprime/creador de contenido` |
| creador de imagenes | `cursorprime/creador de contenido` |

---

## Restaurar organización anterior

Si no te gusta este arreglo:

```bash
cp .backup-organizacion/cursorprime.code-workspace.bak cursorprime.code-workspace
cp .backup-organizacion/COMO_ABRIR.md.bak COMO_ABRIR.md
cp .backup-organizacion/README.md.bak README.md
cp .backup-organizacion/ESTRUCTURA.md.bak "creador de contenido/ESTRUCTURA.md"
```

Detalle completo: [.backup-organizacion/RESTAURAR.md](./.backup-organizacion/RESTAURAR.md)
