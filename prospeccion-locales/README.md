# Prospección locales — Paso 0 Presencia digital

Busca negocios por rubro + ciudad y puntúa si necesitan Presencia digital.

## Uso

```bash
# Demo sin API
python3 prospeccion_main.py buscar --rubro dentista --ciudad Providencia --mock

# Real (requiere GOOGLE_PLACES_API_KEY en .env)
export GOOGLE_PLACES_API_KEY=...
python3 prospeccion_main.py buscar --rubro dentista --ciudad Providencia --limit 15
```

## Salida

`data/{slug}/output/leads.json` + `leads.md`

## Score ≥ 50 = viable

Señales: sin web, solo red social, pocas reseñas, rating bajo.

## Límites

- **Mock:** demo interna
- **Places API:** candidatos públicos, no clientes cerrados
- **Tú** contactas por WhatsApp (Paso 1 informe)
