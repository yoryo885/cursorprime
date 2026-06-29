# Backlog viabilidad — ideas de videos YouTube

Registro vivo. **No instalar packs externos** — skills propias en `~/.cursor/skills/`.

Fuente JSON: [ideas/backlog-youtube-viabilidad.json](./ideas/backlog-youtube-viabilidad.json)

## Leyenda

| Veredicto | Significado |
|-----------|-------------|
| **viable** | Encaja con cursorprime; skill creada o en uso |
| **condicional** | Skill cubre MVP; pipeline solo con demanda/cliente |
| **descartar** | Fuera de foco o redundante |
| **descartar_como_proyecto** | Ya cubierto por skills existentes |

## Resumen

| Idea | Veredicto | Skill |
|------|-----------|-------|
| Gestión proyectos reales (Ruben Loan) | ✅ viable | `gestion-proyecto` |
| Landing + lanzamiento | ⚠️ condicional | `landing-lanzamiento` |
| WhatsApp marketing PYME | ⚠️ condicional | `whatsapp-marketing` |
| Audit marketing e-commerce | ⚠️ condicional | `audit-marketing` |
| Webs agencia 10k€ | ❌ descartar | — |
| Swarm marketing Claude Code | ❌ ya cubierto | hooks, captions, copy-linkedin… |
| Pack 31 skills | ❌ descartar | `find-skills` para cherry-pick |
| Higgsfield Reels | ❌ descartar | `guion-a-video` + redes |

## Evaluar idea nueva

```bash
cd ~/cursorprime/ideas\ de\ proyectos
python3 evaluar.py ideas/backlog-youtube-viabilidad.json
# o copiar una idea a ideas/mi-idea.json y evaluar
```

## Gate construcción

Solo pipeline nuevo si veredicto **viable** + usuario dice `construye`.
