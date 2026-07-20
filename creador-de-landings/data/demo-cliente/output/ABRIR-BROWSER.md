# Arreglar preview en Cursor (ERR_CONNECTION_REFUSED)

## Causa
El HTML está bien. Falla el **puerto**: Cursor no está reenviando `8777` a tu navegador.

## Arreglo (30 segundos)

### 1. Servidor (en la terminal del workspace)
```bash
cd creador-de-landings
bash servir-preview.sh
```
O: `Ctrl/Cmd+Shift+B` → task **Landings: abrir preview en Browser**

### 2. Reenviar el puerto
1. Panel **Ports** (abajo en Cursor)
2. **Forward a Port** → escribe `8777`
3. Clic en la URL / **Open in Browser**

### 3. Abrir
http://localhost:8777/preview.html

Si sigue fallando: cierra Simple Browser, vuelve a Forward `8777`, y abre de nuevo.
