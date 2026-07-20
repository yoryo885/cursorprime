# Abrir preview (arreglo ERR_CONNECTION_REFUSED)

## Usa este puerto (recomendado)
Cursor ya suele tener **8768** abierto:

**http://localhost:8768/preview.html**

## Si 8777 falla
`8777` a veces no se reenvía → `ERR_CONNECTION_REFUSED`.
No es un error del HTML; es el port forward.

## Ports
1. Panel **Ports**
2. Debe aparecer **8768** (y/o 8777)
3. Clic → Open in Browser
