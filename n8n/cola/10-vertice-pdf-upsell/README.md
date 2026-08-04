# Sistema #5 — Vértice PDF + upsell dropship

**Sin API todavía** — solo esqueleto para ver el flujo.

## Flujo
```
Pedido PDF (Shopify mock) → n8n → brief de qué PDF / oferta upsell
                              → (después) Cursor genera PDF
                              → oferta accesorio dropship
```

## Qué hace n8n
1. Recibe pedido / pedido mock  
2. Elige **qué PDF** (catálogo / slug)  
3. Arma brief para Cursor  
4. Arma oferta upsell físico  
5. Log sí/no upsell  

## Apps (después)
Shopify · Cursor (PDF) · Dropship · Email/Wasap · Sheet
