# Prompt — Pipeline landings v4

```
Usa landing-pipeline.

Arquitectura:
- LLM: copy (02–10) + tokens (11a). NUNCA HTML completo.
- HTML: 11b_assemble + Jinja2 templates, SECTION_ORDER una vez.
- Mostrar resultado VISUAL (URL/screenshots), no pegar código HTML.

Bugs prevenidos: desde-desde, overlap, acento único, naming, testimonios omitida, secciones duplicadas.

CLI: python3 landing_main.py run --demo
```
