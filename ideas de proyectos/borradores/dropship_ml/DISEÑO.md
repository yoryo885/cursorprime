# Diseño — Dropshipping parlantes Mercado Libre Chile

## Problema
Vendedor ML compra en Hogatodo y revende; necesita márgenes reales y sync stock.

## Modelo
SaaS semi-automático: scrape proveedor → margen ML → reporte → alertas

## Veredicto: **GO_CON_RESERVAS**

### MVP
- Collector con mock o scrape limitado
- Calculadora margen ML Chile
- Reporte JSON + resumen TXT

### Pipeline destino

1. **Cargar contexto** (`context`) → `ContextAgent`
2. **Recolectar datos proveedor** (`collect`) → `CollectorAgent`
3. **Calcular márgenes** (`margin`) → `MarginAgent`
4. **Generar reporte** (`report`) → `ReportAgent`
5. **QC final** (`qc`) → `QCAgent`

## Siguiente paso

Cuando estés conforme con este diseño, di en New Agent:

> **Construye el proyecto dropship_ml — está listo**

Hasta entonces **no** se creará nada en `proyectos/`.