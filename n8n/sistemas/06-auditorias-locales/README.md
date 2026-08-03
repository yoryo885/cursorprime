# Sistema #1 — Auditorías locales

Producto de entrada del embudo cursorprime.  
**Estado:** esqueleto (importar en n8n después). Login n8n pendiente a propósito.

## Embudo (cómo se vende)

```
Local (Maps) → Audit cobrado/piloto → Informe al cliente
                                      ↓ si quiere más
                         Plan Básico / Presencia / Completo
```

1. **Primero** se entrega el **análisis** (informe score + quick wins).
2. **Después**, si quiere el servicio, elige un **plan**.

## Qué recibe el cliente

| Momento | Entregable |
|---------|------------|
| Entrada | `MARKETING-AUDIT` (MD/HTML/PDF) + resumen accionable |
| Upsell | Trabajo del plan elegido (no solo más PDF) |

## Planes (upsell)

| Plan | Incluye (esqueleto) |
|------|---------------------|
| `basico` | Quick wins: CTA, WhatsApp visible, textos clave |
| `presencia` | Landing/web + Google Business Profile |
| `completo` | Presencia + Wasap task (citas/pedidos/FAQ) |

Definición máquina: `planes.json`.

## Apps del sistema

| Rol | App |
|-----|-----|
| Prospectar | Google Maps / Places |
| Analizar web | `marketing-audit` (Cursor + Claude) |
| Orquestar | n8n (estos workflows) |
| Contactar | WhatsApp |
| Guardar | `clientes/{slug}/` |
| PDF opcional | script vendor del audit |

## Workflows n8n (importar en orden)

| Archivo | Qué hace |
|---------|----------|
| `workflows/01-disparar-audit.json` | POST url+cliente → job audit + ack |
| `workflows/02-lead-interes-plan.json` | POST lead tras ver informe → elige plan |
| `workflows/03-seguimiento-wasap.json` | Esqueleto mensaje seguimiento WhatsApp |

## TODOs al insertar

- [ ] Credencial / HTTP al runner de `marketing_audit_main.py`
- [ ] Sheet o Notion de jobs (opcional)
- [ ] Plantillas Wasap reales
- [ ] Precios en `planes.json` (hoy placeholders)

## Comando pipeline (referencia, no n8n)

```bash
cd marketing-audit
python3 marketing_audit_main.py audit --url https://negocio.com --slug demo-local
```
