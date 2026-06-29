# Ramas — libros a entender

Mapa de chats de Cursor y módulos del proyecto.

## Renombrar chats (sidebar)

Clic derecho en el chat → **Rename** → pegar nombre:

| Nombre actual (truncado) | Renombrar a | Qué hace |
|--------------------------|-------------|----------|
| CSS style changes for co… | **PDF · Portada CSS (1)** | Ajustes visuales portada Pareto en `html_renderer.py` |
| CSS style changes for co… | **PDF · Portada CSS (2)** | Más ajustes portada + orden DOM cover-meta/dot |
| Creación de pipeline par… | **Marketing · Amazon KDP** | Pipeline marketing: listing, bot Amazon, keywords |
| Sistema de agentes para… | **Core · Resumidor PDF** | Sistema base: PDF → temas → markdown → agentes |

## Módulos del proyecto (código)

| Rama | Carpeta / entrada | Función |
|------|-------------------|---------|
| **Core · Resumidor** | `main.py` | PDF libro → resúmenes .md |
| **PDF · Diseño** | `src/html_renderer.py`, `src/agents/pdf_design_agent.py` | HTML/CSS → PDF editorial |
| **PDF · Post-proceso** | `src/agents/pipeline.py` | Tablas, mapa, imágenes, QC |
| **Marketing · KDP** | `kdp_main.py`, `src/marketing/` | Vender en Amazon (copy, bot, learning) |
| **Planificador** | `plan.py` | Plan antes de ejecutar pipeline |

## Otras capas (fuera de esta carpeta)

| Rama | Carpeta | Función |
|------|---------|---------|
| **Evaluador** | `ideas de proyectos/` | ¿Sirve el proyecto? ¿Margen? |
| **Cerebro** | Cursor chat | Evalúa, conecta ramas, construye si autorizas |
