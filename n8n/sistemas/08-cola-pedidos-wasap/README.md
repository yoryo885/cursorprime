# Sistema #3 — Cola de pedidos WhatsApp (locales)

Negocios con local físico: pedidos/consultas por teléfono se pierden en hora pico.  
**Estado:** esqueleto n8n (importar después).

## Embudo

```
Local sobrecargado → Alta cola Wasap → Pedidos en fila ordenada
                                    → Estado / horarios por bot
```

Puede venderse solo (SaaS/setup) o como upsell del #2 Completo.

## Qué recibe el cliente

| Entregable | Descripción |
|------------|-------------|
| Número / flujo Wasap | Pedidos entran por WhatsApp |
| Cola ordenada | Ticket #, estado (nuevo → prep → listo) |
| Avisos | “Tu pedido está listo” (esqueleto) |
| Panel simple | Lista de pedidos del día (TODO Sheet/Notion) |

## Apps

| Rol | App |
|-----|-----|
| Canal | WhatsApp / Meta Cloud API |
| Orquestar | n8n |
| Cola | Sheet / Notion / DB (TODO) |
| Guardar | `clientes/{slug}/` |

## Paquetes

Ver `paquetes.json`: `setup` | `mensual` | `pico` (temporada).

## Workflows

| Archivo | Qué hace |
|---------|----------|
| `01-nuevo-pedido.json` | Webhook pedido → asigna ticket |
| `02-cambiar-estado.json` | nuevo/preparando/listo/entregado |
| `03-avisar-cliente.json` | Mensaje estado al cliente |
| `04-alta-negocio.json` | Onboarding del local |

## Relación

- #1 Audit detecta caos de atención  
- #2 Completo puede incluir Wasap  
- #3 = producto enfocado en **cola de pedidos**
