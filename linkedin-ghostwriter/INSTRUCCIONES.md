# Sistema Ghostwriting LinkedIn 🚀

## Cómo usar (3 pasos)

### 1. Edita el perfil del ejecutivo
Abre `ejecutivo_perfil.json` y cambia los datos:
- nombre, cargo, empresa
- industria, años de experiencia
- temas en los que es experto
- logros recientes (MUY IMPORTANTE — da autenticidad)
- cantidad_posts (cuántos posts quieres al mes)

### 2. Ejecuta el sistema
```bash
cd /Users/yoryo/cursorprime/linkedin-ghostwriter
python3 generar_posts.py
```

### 3. Revisa los posts
Los posts quedan en la carpeta `posts_generados/nombre_mes/`
- Un archivo .txt por post
- Un `_RESUMEN_DEL_MES.txt` con todos juntos

---

## Cómo funciona por dentro

El sistema usa **3 agentes de IA** en secuencia:

```
AGENTE 1 (Planificador)
→ Analiza el perfil y crea 8 temas del mes

AGENTE 2 (Redactor)  
→ Escribe cada post con la voz del ejecutivo

AGENTE 3 (Revisor)
→ Califica del 1-10 y mejora si es necesario
```

---

## Para múltiples ejecutivos
Copia el archivo `ejecutivo_perfil.json` con otro nombre
y al ejecutar, cambia la línea:
```python
ARCHIVO_PERFIL = "ejecutivo_perfil.json"
```
por el nombre del nuevo archivo.

---

## Tiempo estimado
~3-5 minutos para generar 8 posts completos
