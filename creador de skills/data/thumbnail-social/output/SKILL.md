---
name: thumbnail-social
description: >-
  Thumbnail on-brand para YouTube (16:9) o Reels/Shorts (9:16): brief visual,
  prompt imagen y pipeline PNG en creador de contenido. Usar cuando el usuario
  pide thumbnail, miniatura, portada video, carátula youtube, usa
  thumbnail-social, o miniatura en su estilo.
---

# Thumbnail Social

Skill de **workflow** para Creador de Contenido.

## Cuándo usar

Triggers: thumbnail, miniatura, portada video, carátula youtube, usa thumbnail-social.

**No usar Higgsfield/Facelock** — pipeline local cursorprime (PNG vía `creador_imagenes_main.py`).

## Proceso

Brief → prompt imagen → PNG en `data/{slug}/imagenes/`.

## Pasos

1. **Confirmar**: plataforma (16:9 YouTube / 9:16 Reels), título corto (≤5 palabras en imagen), referencia de estilo (`meta/estilos_animacion.json` o imagen de referencia).
2. **Prompt imagen**: alto contraste, rostro o objeto grande, texto bold legible en móvil, fondo simple.
3. **Opcional prompts pack**:
   ```bash
   cd ~/cursorprime/creador\ de\ prompts
   python3 creador_prompts_main.py --slug {slug}-thumb --tipo imagen
   ```
4. **Generar PNG**:
   ```bash
   cd ~/cursorprime/creador\ de\ contenido
   # Armar data/{slug}/inputs/lote.json con salidas: ["png"] y temas del thumbnail
   python3 creador_imagenes_main.py --slug {slug} --modo png
   ```
5. **Entregar**: `data/{slug}/imagenes/*.png` + 1 variante A/B si pidió test.

## Reglas

- Máx. **5 palabras** en el thumbnail — legible en preview móvil.
- **Alto contraste** — evitar fondos recargados.
- **Consistencia de marca** — mismos colores/fuentes que videos anteriores del slug.
- Probar **1 variante** antes de lote.
- Ruta base: `~/cursorprime/creador de contenido`

## Encadenar

```
hooks-redes → guion-a-video → thumbnail-social → captions-redes
```

## Proyecto

Carpeta: `../creador de contenido` · Módulo: `imagenes/`

## Iteración

Si el PNG no lee bien en móvil, simplificar texto y subir contraste.
