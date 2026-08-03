# Sistema #4 — Wasap task (FAQ / citas / handoff)

Bot de WhatsApp **por tarea**, no ChatGPT genérico (política Meta 2026).  
**Estado:** esqueleto n8n (importar después).

## Embudo

```
Audit/Presencia → Cliente necesita atención 24/7 controlada
               → FAQ + agendar cita + pasar a humano
```

Upsell natural del #1/#2. Distinto del #3 (cola de pedidos): acá el foco es **FAQ + citas**, no tickets de cocina.

## Qué recibe el cliente

| Entregable | Descripción |
|------------|-------------|
| FAQ automático | Horario, precio, dirección, servicios |
| Citas | Pedir día/hora → confirmar / lista |
| Handoff | “Te paso con una persona” |
| Métricas (TODO) | % resuelto sin humano, primer respuesta |

## Apps

| Rol | App |
|-----|-----|
| Canal | WhatsApp Meta Cloud API |
| Orquestar | n8n |
| FAQ data | JSON por cliente / Notion |
| Agenda | Sheet / Cal.com (TODO) |
| Guardar | `clientes/{slug}/` |

## Paquetes

Ver `paquetes.json`: `faq` | `citas` | `full_task`.

## Workflows

| Archivo | Qué hace |
|---------|----------|
| `01-entrada-meta.json` | Webhook mensaje Meta → normaliza |
| `02-intent-router.json` | faq / cita / handoff / ignore |
| `03-responder-faq.json` | Contesta desde mapa FAQ |
| `04-agendar-cita.json` | Alta solicitud de cita |
| `05-handoff-humano.json` | Marca handoff + aviso |

## Relación

| Sistema | Rol |
|---------|-----|
| #1 Audit | Detecta mala atención |
| #2 Completo | Puede incluir este Wasap |
| #3 Cola | Pedidos/comida; este es FAQ+citas |
| `03-wasap-faq` genérico | Plantilla corta; este es el de negocio |
