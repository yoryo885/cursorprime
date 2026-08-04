# Sistemas n8n — solo proyectos creados

En n8n viven **únicamente** los workflows de la capa **Proyectos creados** del centro de control.
Lo demás queda en `cola/` (ideas en cola — **no se importan ni se crean** en n8n).

## Proyectos creados → sistemas activos

| Proyecto (panel) | Carpeta n8n | Workflows |
|------------------|-------------|-----------|
| Marketing Audit | `sistemas/06-auditorias-locales` | Auditoría · … |
| Presencia web locales | `sistemas/07-presencia-digital` | Presencia · … |
| Bot WhatsApp pymes | `sistemas/09-wasap-task-faq-citas` | Wasap FAQ · … |
| Embudo comercial HTML | `sistemas/02-lead-landing` | Embudo · formulario landing |
| Libros / KDP | `sistemas/11-kdp-resumenes` | KDP · … |
| LinkedIn ghostwriter | `sistemas/12-linkedin-ghostwriter` | LinkedIn · … |
| Creador de contenido | `sistemas/13-creador-contenido` | Contenido · … |
| Videos TikTok | `sistemas/14-videos-tiktok` | TikTok · … |
| Capa clientes | — | Sin workflow n8n (carpeta `clientes/`) |

## Cola (no crear en n8n)

En `cola/`: ping, utilitarios, **Cola Wasap**, **Vértice PDF/upsell**, etc.
Vuelven a `sistemas/` solo cuando el panel los pase a proyectos creados y digas **construye**.

## Estado

- ✅ Sistemas de proyectos creados + **Videos TikTok** en `sistemas/`
- ✅ Instancia n8n alineada (~26 workflows)
- ⏸ Sin API real (mock / TODO)
