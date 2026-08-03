# Sistema #2 — Presencia digital (locales)

Upsell después del audit (#1).  
**Estado:** esqueleto (importar en n8n después).

## Embudo

```
Audit (#1) → Cliente quiere arreglo → Presencia digital (#2)
                                      ↓
                         Setup web + GBP (+ Wasap si Completo)
```

El #1 entrega el **espejo** (informe).  
El #2 entrega el **arreglo** (presencia online andando).

## Qué recibe el cliente

| Entregable | Descripción |
|------------|-------------|
| Web / landing | Página publicada (URL viva) |
| Google Business | Perfil ordenado (GBP) |
| (Opcional) Wasap | Citas / pedidos / FAQ + handoff |
| Carpeta cliente | `clientes/{slug}/` con brief + entregables |

## Apps

| Rol | App |
|-----|-----|
| Landing | `creador-de-landings` / `landing_pipeline` |
| Deploy | Vercel / Netlify |
| GBP | Google Business Profile |
| Contacto | WhatsApp / Meta API |
| Orquestar | n8n (estos workflows) |
| Guardar | `clientes/{slug}/` |
| Entrada | `marketing-audit` (#1) |

## Paquetes

Ver `paquetes.json`:

| ID | Nombre |
|----|--------|
| `presencia` | Web + GBP |
| `completo` | Presencia + Wasap task |
| `mantenimiento` | Mes siguiente (opcional) |

## Workflows n8n

| Archivo | Qué hace |
|---------|----------|
| `workflows/01-alta-proyecto.json` | POST cliente + plan → crea job setup |
| `workflows/02-deploy-listo.json` | Marca web publicada + URL |
| `workflows/03-gbp-checklist.json` | Checklist GBP + estado |
| `workflows/04-entrega-cliente.json` | Mensaje de entrega / cierre |

## Relación con #1

- Requiere (o recomienda) `jobAudit` / informe previo.
- Planes `presencia` y `completo` del sistema `06-auditorias-locales` apuntan acá.

## TODOs al insertar

- [ ] Crear carpeta `clientes/{slug}/` automática
- [ ] Hook a `landings_main.py` / `landing_main.py`
- [ ] Deploy Vercel API o manual documentado
- [ ] Meta API para Wasap (solo plan completo)
