# cursorprime — Mapa para agentes

Workspace único. Guía de apertura: [COMO_ABRIR.md](./COMO_ABRIR.md)

## Proyecto → CLI → Skill

| Proyecto | Entrypoint | Skill | Inputs | Outputs |
|----------|------------|-------|--------|---------|
| creador de prompts | `python3 creador_prompts_main.py --slug {slug}` | `usa creador-de-prompts` | `data/{slug}/inputs/solicitud.json` | `data/{slug}/output/prompts.json` |
| creador de skills | `python3 creador_skills_main.py --slug {slug}` | `usa creador-de-skills` | `catalogo/{slug}.json` | `~/.cursor/skills/{nombre}/` |
| creador de contenido | `python3 creador_imagenes_main.py --slug {slug} --receta promo-guia` | `usa guion-a-video` | `data/{slug}/inputs/lote.json` (+ `guia` / receta) | `data/{slug}/videos/` · `copy/` · `output/` |
| redes (hooks/captions/thumb) | chat + pipeline PNG/video | `usa hooks-redes` / `captions-redes` / `thumbnail-social` | brief + guion | PNG + copy |
| **tiktok_pipeline** | `python3 tiktok_main.py --tema "..."` | `usa hooks-redes` (+ skills internas) | tema + nicho | `output/{slug}/shotlist.md` · `guion.json` · `qa_report.json` |
| buscar skill externa | `npx skills find {query}` | `usa find-skills` | keyword | propuesta install o catálogo |
| ideas de proyectos | `python3 evaluar.py ideas/{idea}.json` | `usa evaluar-idea` | `ideas/*.json` | `evaluaciones/{slug}/` |
| project lens | `python3 project_lens_main.py --slug {slug}` | `usa project-lens` | `ideas/*.json` o `data/{slug}/inputs/idea.json` | `data/{slug}/output/` |
| libros a entender | `python3 main.py` + `python3 kdp_main.py --slug {slug}` | `usa resumidor-kdp` | `libros/*.pdf` | `resumenes/{slug}/` + `kdp/` |
| PDF genérico | chat / pipeline | `usa pdf-resumidor` | PDF | JSON + markdown |
| linkedin-ghostwriter | `python3 generar_posts.py` | `usa copy-linkedin` | `ejecutivo_perfil.json` | `posts_generados/{nombre}_{mes}/` |
| nuevo pipeline Python | diseño → `construye` | `usa crear-pipeline` | brief YAML | `{proyecto}/` + CLI |
| gestión proyecto | docs → gate | `usa gestion-proyecto` | brief YAML/JSON | PROYECTO.md + plan |
| landing / lanzamiento | chat + prompts | `usa landing-lanzamiento` | brief producto | landing-brief.md |
| WhatsApp comercial | chat | `usa whatsapp-marketing` | negocio + objetivo | secuencia copy |
| audit marketing | chat + web | `usa audit-marketing` | URL + competidores | informe-audit.md |
| market audit (completo) | `python3 marketing_audit_main.py audit --url {url}` | `usa market-audit` | `brief.json` + URL | MARKETING-AUDIT.md + PDF |
| market proposal / funnel | chat | `market-proposal` / `market-funnel` | proyecto cliente | entregables/estrategia/ |
| **clientes / campañas** | chat + reglas proyecto | skills según `proyecto.mdc` | `clientes/{c}/proyectos/{slug}/` | `entregables/` |

## Ideas de videos — viabilidad

Registro: [ideas de proyectos/BACKLOG_VIABILIDAD.md](./ideas%20de%20proyectos/BACKLOG_VIABILIDAD.md) · JSON: `ideas/backlog-youtube-viabilidad.json`

## Flujos encadenados

```
Idea → evaluar-idea → (opcional) project-lens → gestion-proyecto → crear-pipeline → creador-de-prompts / creador de contenido
PDF libro → resumidor-kdp → KDP listing
PDF datos → pdf-resumidor → (opcional) project-lens / guion-a-video
Redes: hooks-redes → guion-a-video → thumbnail-social → captions-redes
Negocio → audit-marketing → landing-lanzamiento → (opcional) contenido redes
WhatsApp → whatsapp-marketing → evaluar-idea (si SaaS)
```

## Estado del ecosistema

Checklist actualizado (hecho / pendiente): [meta/ESTADO.md](./meta/ESTADO.md)

## Gate de construcción

En **ideas de proyectos**, no crear código en `proyectos/` ni ramas nuevas hasta que el usuario diga: `construye`, `armado` o `crea el proyecto`.

## Cola actual de skills

Ver [creador de skills/COLA_SKILLS.md](./creador%20de%20skills/COLA_SKILLS.md).

| # | Skill | Estado |
|---|-------|--------|
| 1 | guion-a-video | hecho |
| 2 | evaluar-idea | hecho |
| 3 | resumidor-kdp | hecho |
| 4 | copy-linkedin | hecho |
| 5 | crear-pipeline | hecho |
| 6 | hooks-redes | hecho |
| 7 | captions-redes | hecho |
| 8 | thumbnail-social | hecho |
| 9 | find-skills | hecho |
| 10 | gestion-proyecto | hecho |
| 11 | landing-lanzamiento | hecho |
| 12 | whatsapp-marketing | hecho |
| 13 | audit-marketing | hecho |

## Entorno

- APIs: revisar `.env` / `.env.example` en cada proyecto antes de correr pipelines de pago.
- Mock vs real: creador de contenido usa `MOCK_KLING` para video animado sin API.
