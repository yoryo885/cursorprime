"""HTML del embudo comercial: informe, propuesta, web y WhatsApp."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

BASE_CSS = """
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: system-ui, -apple-system, sans-serif;
    color: #1c1917; line-height: 1.6; background: #fafaf9;
  }
  .wrap { max-width: 720px; margin: 0 auto; padding: 2rem 1.25rem 3rem; }
  .wrap-wide { max-width: 960px; margin: 0 auto; padding: 2rem 1.25rem 3rem; }
  a { color: #0f766e; }
  .header {
    display: flex; justify-content: space-between; align-items: flex-start;
    gap: 1rem; border-bottom: 3px solid #0f766e; padding-bottom: 1rem; margin-bottom: 1.5rem;
  }
  .logo { height: 44px; width: auto; }
  .logo-text { font-weight: 700; color: #0f766e; font-size: 1rem; }
  .header-right { text-align: right; font-size: 0.8rem; color: #57534e; }
  .header-right a { text-decoration: none; font-weight: 600; }
  h1 { font-size: 1.5rem; color: #0f766e; margin-bottom: 0.5rem; }
  h2 { font-size: 1rem; text-transform: uppercase; letter-spacing: 0.05em;
       color: #0f766e; margin: 2rem 0 0.75rem; }
  h3 { font-size: 1.05rem; margin: 1.25rem 0 0.5rem; }
  p, li { font-size: 0.95rem; }
  .sub { color: #57534e; font-size: 0.9rem; margin-bottom: 1rem; }
  .badge {
    display: inline-block; background: #fef3c7; color: #92400e;
    padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.7rem;
  }
  .badge-demo { background: #e0e7ff; color: #3730a3; }
  .score-box {
    background: linear-gradient(135deg, #f0fdfa, #ecfdf5);
    border: 1px solid #99f6e4; border-radius: 16px; padding: 1.5rem;
    text-align: center; margin: 1.5rem 0;
  }
  .score { font-size: 3.5rem; font-weight: 800; color: #0f766e; line-height: 1; }
  .resumen { background: #fff; border: 1px solid #e7e5e4; padding: 1rem 1.25rem;
             border-radius: 8px; margin: 1rem 0; }
  table { width: 100%; border-collapse: collapse; font-size: 0.88rem; background: #fff; }
  th, td { padding: 0.6rem 0.5rem; border-bottom: 1px solid #e7e5e4; text-align: left; }
  th { color: #78716c; font-weight: 600; }
  .finding {
    padding: 0.85rem 1rem; margin-bottom: 0.5rem; border-radius: 8px;
    border-left: 4px solid #a8a29e; background: #fff; font-size: 0.92rem;
  }
  .critical { border-color: #dc2626; background: #fef2f2; }
  .high { border-color: #ea580c; background: #fff7ed; }
  .medium { border-color: #ca8a04; background: #fefce8; }
  .tag { font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
         color: #57534e; display: block; margin-bottom: 0.25rem; }
  .cta {
    background: #0f766e; color: #fff; padding: 1.25rem 1.5rem;
    border-radius: 12px; margin-top: 2rem; text-align: center;
  }
  .cta a, .btn {
    display: inline-block; margin-top: 0.75rem; background: #fff; color: #0f766e;
    padding: 0.6rem 1.25rem; border-radius: 8px; font-weight: 700;
    text-decoration: none; font-size: 0.95rem;
  }
  .btn-primary { background: #0f766e; color: #fff; margin-top: 0; }
  footer { margin-top: 2rem; font-size: 0.75rem; color: #a8a29e; text-align: center; }
  .nav-steps {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem; margin: 2rem 0;
  }
  .step-card {
    background: #fff; border: 1px solid #e7e5e4; border-radius: 12px;
    padding: 1.25rem; text-decoration: none; color: inherit;
    transition: box-shadow 0.15s, border-color 0.15s;
  }
  .step-card:hover { border-color: #0f766e; box-shadow: 0 4px 12px rgba(15,118,110,0.12); }
  .step-num {
    display: inline-block; background: #0f766e; color: #fff; width: 28px; height: 28px;
    border-radius: 50%; text-align: center; line-height: 28px; font-size: 0.85rem;
    font-weight: 700; margin-bottom: 0.5rem;
  }
  .step-card h3 { color: #0f766e; font-size: 1rem; margin: 0 0 0.35rem; }
  .step-card p { font-size: 0.85rem; color: #57534e; margin: 0; }
  .step-done { border-color: #99f6e4; background: #f0fdfa; }
  .plan-grid { display: grid; gap: 1rem; margin: 1rem 0; }
  @media (min-width: 640px) { .plan-grid { grid-template-columns: repeat(3, 1fr); } }
  .plan {
    background: #fff; border: 2px solid #e7e5e4; border-radius: 12px; padding: 1.25rem;
  }
  .plan.featured { border-color: #0f766e; position: relative; }
  .plan.featured::before {
    content: 'Recomendado'; position: absolute; top: -10px; left: 50%; transform: translateX(-50%);
    background: #0f766e; color: #fff; font-size: 0.65rem; font-weight: 700;
    padding: 0.15rem 0.6rem; border-radius: 4px; text-transform: uppercase;
  }
  .price { font-size: 1.5rem; font-weight: 800; color: #0f766e; margin: 0.5rem 0; }
  .plan ul { padding-left: 1.1rem; font-size: 0.85rem; }
  .plan li { margin-bottom: 0.35rem; }
  /* Landing clinica */
  .hero-landing {
    background: linear-gradient(135deg, #0f766e, #115e59); color: #fff;
    padding: 3rem 1.5rem; border-radius: 16px; text-align: center; margin-bottom: 2rem;
  }
  .hero-landing h1 { color: #fff; font-size: 1.75rem; margin-bottom: 0.5rem; }
  .hero-landing p { opacity: 0.92; margin-bottom: 1.25rem; }
  .hero-btns { display: flex; flex-wrap: wrap; gap: 0.75rem; justify-content: center; }
  .hero-btns a {
    background: #fff; color: #0f766e; padding: 0.65rem 1.25rem; border-radius: 8px;
    font-weight: 700; text-decoration: none; font-size: 0.9rem;
  }
  .hero-btns a.outline { background: transparent; border: 2px solid #fff; color: #fff; }
  .benefits { display: grid; gap: 1rem; margin: 1.5rem 0; }
  @media (min-width: 640px) { .benefits { grid-template-columns: repeat(3, 1fr); } }
  .benefit {
    background: #fff; border: 1px solid #e7e5e4; border-radius: 10px;
    padding: 1rem; text-align: center;
  }
  .benefit strong { display: block; color: #0f766e; margin-bottom: 0.25rem; }
  .faq-item { background: #fff; border: 1px solid #e7e5e4; border-radius: 8px;
              padding: 1rem; margin-bottom: 0.5rem; }
  .faq-item strong { color: #0f766e; }
  /* WhatsApp chat */
  .phone {
    max-width: 380px; margin: 2rem auto; background: #ece5dd;
    border-radius: 24px; overflow: hidden; box-shadow: 0 8px 32px rgba(0,0,0,0.15);
  }
  .phone-header {
    background: #075e54; color: #fff; padding: 1rem 1.25rem;
    display: flex; align-items: center; gap: 0.75rem;
  }
  .avatar {
    width: 40px; height: 40px; border-radius: 50%; background: #25d366;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 0.9rem;
  }
  .chat { padding: 1rem; min-height: 420px; display: flex; flex-direction: column; gap: 0.5rem; }
  .bubble {
    max-width: 85%; padding: 0.55rem 0.75rem; border-radius: 8px;
    font-size: 0.88rem; line-height: 1.45; box-shadow: 0 1px 1px rgba(0,0,0,0.08);
  }
  .bubble-in { background: #fff; align-self: flex-start; border-top-left-radius: 0; }
  .bubble-out { background: #dcf8c6; align-self: flex-end; border-top-right-radius: 0; }
  .bubble .time { font-size: 0.65rem; color: #78716c; text-align: right; margin-top: 0.25rem; }
  .demo-note {
    background: #fffbeb; border: 1px solid #fcd34d; border-radius: 8px;
    padding: 0.75rem 1rem; font-size: 0.85rem; margin-bottom: 1.5rem;
  }
"""


def _wa_link(numero: str, mensaje: str) -> str:
    n = "".join(c for c in numero if c.isdigit())
    return f"https://wa.me/{n}?text={quote(mensaje)}"


def _header_html(branding: dict, logo_rel: str = "logo.svg") -> str:
    nombre = branding.get("nombre", "Consultor")
    wa = branding.get("whatsapp", "")
    email = branding.get("email", "")
    wa_url = _wa_link(wa, branding.get("whatsapp_mensaje", "")) if wa else "#"
    email_link = f' · <a href="mailto:{email}">{email}</a>' if email else ""
    logo = f'<img src="{logo_rel}" alt="{nombre}" class="logo" />'
    return f"""
  <div class="header">
    {logo}
    <div class="header-right">
      <strong>{nombre}</strong><br>
      <a href="{wa_url}" target="_blank">WhatsApp</a>{email_link}
    </div>
  </div>"""


def generar_index_embudo(
    out_path: Path,
    cliente_nombre: str,
    branding: dict,
    pasos: list[dict],
) -> Path:
    cards = ""
    for p in pasos:
        done = " step-done" if p.get("listo") else ""
        cards += f"""
    <a class="step-card{done}" href="{p['href']}">
      <span class="step-num">{p['num']}</span>
      <h3>{p['titulo']}</h3>
      <p>{p['desc']}</p>
    </a>"""

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Embudo comercial — {cliente_nombre}</title>
  <style>{BASE_CSS}</style>
</head>
<body>
<div class="wrap-wide">
{_header_html(branding, "../paso-1-informe/logo.svg")}
  <h1>Embudo comercial — {cliente_nombre}</h1>
  <p class="sub">Primer cliente demo · 4 entregables en HTML · <span class="badge badge-demo">DEMO</span></p>

  <div class="resumen">
    Flujo completo: <strong>informe</strong> → <strong>propuesta</strong> → <strong>web</strong> → <strong>WhatsApp</strong>.
    Cada paso es un HTML independiente listo para mostrar al cliente o enviar por link.
  </div>

  <div class="nav-steps">{cards}
  </div>

  <div class="cta">
    <strong>¿Empezamos con un cliente real?</strong>
    <p>Paso 1: envía el informe. Cuando respondan, comparte la propuesta.</p>
    <a href="paso-1-informe/index.html">Ver informe (Paso 1)</a>
  </div>

  <footer>Presencia Local · Embudo demo · Confidencial</footer>
</div>
</body>
</html>"""
    out_path.write_text(html, encoding="utf-8")
    return out_path


def generar_propuesta_html(
    out_path: Path,
    branding: dict,
    cliente: dict,
    audit_score: int,
) -> Path:
    nombre = cliente.get("nombre", "Cliente")
    wa = branding.get("whatsapp", "")
    wa_url = _wa_link(wa, f"Hola, quiero el plan Crecimiento para {nombre}") if wa else "#"

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Propuesta comercial — {nombre}</title>
  <style>{BASE_CSS}</style>
</head>
<body>
<div class="wrap">
{_header_html(branding, "../paso-1-informe/logo.svg")}
  <h1>Propuesta de marketing digital</h1>
  <p class="sub"><strong>{nombre}</strong> · Basada en informe {audit_score}/100 · <span class="badge badge-demo">DEMO</span></p>

  <div class="resumen">
    {nombre} pierde consultas porque en Google no aparece un mensaje claro y la web no explica
    por qué elegirla. Esta propuesta cubre <strong>Google, web y contacto</strong> en 90 días.
  </div>

  <h2>Situación actual</h2>
  <table>
    <tr><th>Área</th><th>Nota</th><th>Estado</th></tr>
    <tr><td>Google y visibilidad</td><td>25/100</td><td>Urgente</td></tr>
    <tr><td>Contenido y mensaje</td><td>63/100</td><td>A mejorar</td></tr>
    <tr><td>Conversión (contacto)</td><td>61/100</td><td>A mejorar</td></tr>
    <tr><td>Meta 90 días</td><td colspan="2"><strong>70–75/100</strong> (estimado)</td></tr>
  </table>

  <h2>Qué incluye el trabajo</h2>
  <ul>
    <li><strong>Fase 1 (sem. 1–4):</strong> Google Maps, textos Google, botón WhatsApp visible</li>
    <li><strong>Fase 2 (sem. 5–8):</strong> «Por qué elegirnos», FAQ, fotos con descripción</li>
    <li><strong>Fase 3 (sem. 9–12):</strong> Seguimiento, ajustes e informe mensual</li>
  </ul>

  <h2>Planes de inversión</h2>
  <p class="sub">Precios en CLP · pago mensual · mínimo 3 meses</p>

  <div class="plan-grid">
    <div class="plan">
      <h3>Esencial</h3>
      <div class="price">$80.000<span style="font-size:0.9rem;font-weight:400">/mes</span></div>
      <ul>
        <li>Google Maps + textos clave</li>
        <li>Botón contacto visible</li>
        <li>1 reunión / mes</li>
      </ul>
    </div>
    <div class="plan featured">
      <h3>Crecimiento</h3>
      <div class="price">$120.000<span style="font-size:0.9rem;font-weight:400">/mes</span></div>
      <ul>
        <li>Todo Esencial +</li>
        <li>«Por qué elegirnos» + FAQ</li>
        <li>2 reuniones / mes</li>
      </ul>
    </div>
    <div class="plan">
      <h3>Acelerado</h3>
      <div class="price">$180.000<span style="font-size:0.9rem;font-weight:400">/mes</span></div>
      <ul>
        <li>Todo Crecimiento +</li>
        <li>2 contenidos / mes</li>
        <li>Prioridad y 4 touchpoints</li>
      </ul>
    </div>
  </div>

  <h2>Retorno estimado (conservador)</h2>
  <p>Con 3–8 consultas extra al mes, el plan Crecimiento ($120.000) puede equilibrarse en el mes 2–3.
  <em>No garantizamos resultados numéricos.</em></p>

  <div class="cta">
    <strong>¿Cuál plan te acomoda?</strong>
    <p>Escríbenos y agendamos 20 min sin compromiso.</p>
    <a href="{wa_url}" target="_blank">Elegir plan por WhatsApp</a>
  </div>

  <p style="margin-top:1.5rem;font-size:0.85rem;text-align:center">
    <a href="../index.html">← Volver al embudo</a> ·
    <a href="../paso-1-informe/index.html">Ver informe</a> ·
    <a href="../paso-3-web/index.html">Ver web propuesta</a>
  </p>
  <footer>Propuesta válida 30 días · Confidencial</footer>
</div>
</body>
</html>"""
    out_path.write_text(html, encoding="utf-8")
    return out_path


def generar_landing_html(out_path: Path, cliente: dict, branding: dict) -> Path:
    nombre = cliente.get("nombre", "Clínica").replace(" (FICTICIO)", "")
    ciudad = cliente.get("ciudad", "Santiago")
    wa = cliente.get("whatsapp", branding.get("whatsapp", ""))
    wa_url = _wa_link(wa, f"Hola, quiero agendar hora en {nombre}") if wa else "#"

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{nombre} | Salud y bienestar en {ciudad}</title>
  <meta name="description" content="{nombre} — consultas, estética y medicina preventiva. Agenda por WhatsApp. Av. Apoquindo 4500, Las Condes.">
  <style>{BASE_CSS}
    body {{ background: #fff; }}
    .wrap {{ max-width: 800px; }}
    .demo-banner {{
      background: #eff6ff; color: #1e40af; text-align: center; padding: 0.5rem;
      font-size: 0.8rem; font-weight: 600;
    }}
  </style>
</head>
<body>
<div class="demo-banner">Paso 3 — Web propuesta · DEMO · Generada tras cerrar plan de presencia digital</div>
<div class="wrap">
  <div class="hero-landing">
    <h1>Tu salud y bienestar, cerca de ti</h1>
    <p>{nombre} — consultas médicas, estética y chequeos preventivos en {ciudad}</p>
    <div class="hero-btns">
      <a href="{wa_url}" target="_blank">Agendar por WhatsApp</a>
      <a href="tel:+56223456789" class="outline">Llamar ahora</a>
    </div>
  </div>

  <h2>Por qué elegirnos</h2>
  <div class="benefits">
    <div class="benefit"><strong>+15 años</strong> atendiendo familias de la zona oriente</div>
    <div class="benefit"><strong>Equipo humano</strong> que explica sin apuros ni tecnicismos</div>
    <div class="benefit"><strong>Agenda flexible</strong> mañana, tarde y algunos sábados</div>
  </div>

  <h2>Servicios</h2>
  <ul>
    <li>Medicina general y chequeos preventivos</li>
    <li>Estética facial y corporal</li>
    <li>Nutrición y control de peso</li>
    <li>Exámenes y derivaciones coordinadas</li>
  </ul>

  <h2>Preguntas frecuentes</h2>
  <div class="faq-item"><strong>¿Tienen estacionamiento?</strong><br>Sí, estacionamiento visitas en el edificio (ficticio).</div>
  <div class="faq-item"><strong>¿Trabajan con Isapres?</strong><br>Sí — Fonasa e Isapres principales. Consulta tu cobertura por WhatsApp.</div>
  <div class="faq-item"><strong>¿Cómo agendo?</strong><br>WhatsApp, teléfono o formulario. Respondemos en horario hábil.</div>

  <h2>Ubicación</h2>
  <p>Av. Apoquindo 4500, Of. 802 — Las Condes, Santiago<br>
  Lun–Vie 8:30–19:00 · Sáb 9:00–13:00</p>
  <p>⭐ 4.7 en Google Maps · 120+ reseñas (demo)</p>

  <div class="cta">
    <strong>¿Listo para agendar?</strong>
    <p>Primera consulta orientativa sin compromiso.</p>
    <a href="{wa_url}" target="_blank">Escríbenos por WhatsApp</a>
  </div>

  <p style="margin-top:1.5rem;font-size:0.85rem;text-align:center">
    <a href="../index.html">← Volver al embudo</a> ·
    <a href="../paso-2-propuesta/index.html">Ver propuesta</a> ·
    <a href="../paso-4-whatsapp/index.html">Ver bot WhatsApp</a>
  </p>
  <footer>Web demo · {nombre} · Implementación real incluye dominio y hosting</footer>
</div>
</body>
</html>"""
    out_path.write_text(html, encoding="utf-8")
    return out_path


def generar_whatsapp_html(out_path: Path, cliente: dict, branding: dict) -> Path:
    nombre = cliente.get("nombre", "Clínica").replace(" (FICTICIO)", "")
    bot_name = nombre[:12]

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Bot WhatsApp — {nombre}</title>
  <style>{BASE_CSS}</style>
</head>
<body>
<div class="wrap">
  <h1>Bot WhatsApp — {nombre}</h1>
  <p class="sub">Paso 4 · Simulación de conversación · <span class="badge badge-demo">SIN API META</span></p>

  <div class="demo-note">
    <strong>Modo demo.</strong> Así respondería el bot cuando un paciente escribe por WhatsApp.
    En producción se conecta a la API de Meta Business.
  </div>

  <div class="phone">
    <div class="phone-header">
      <div class="avatar">CS</div>
      <div>
        <strong>{bot_name}</strong><br>
        <small>en línea</small>
      </div>
    </div>
    <div class="chat">
      <div class="bubble bubble-in">
        👋 Hola, soy el asistente de <strong>{nombre}</strong>.<br><br>
        ¿En qué te ayudo?<br>
        1️⃣ Agendar hora<br>
        2️⃣ Ver servicios y precios<br>
        3️⃣ Ubicación y horarios<br>
        4️⃣ Hablar con recepción
        <div class="time">10:02</div>
      </div>
      <div class="bubble bubble-out">
        Quiero agendar hora
        <div class="time">10:03 ✓✓</div>
      </div>
      <div class="bubble bubble-in">
        Perfecto 📅 ¿Qué servicio necesitas?<br><br>
        • Consulta medicina general — desde $35.000<br>
        • Control estético — desde $45.000<br>
        • Chequeo preventivo — desde $55.000<br><br>
        Responde con el número o nombre del servicio.
        <div class="time">10:03</div>
      </div>
      <div class="bubble bubble-out">
        Consulta medicina general
        <div class="time">10:04 ✓✓</div>
      </div>
      <div class="bubble bubble-in">
        ¿Qué día te acomoda?<br><br>
        • Martes 15 — 10:30 o 16:00<br>
        • Miércoles 16 — 11:00 o 17:30<br>
        • Jueves 17 — 09:30 o 15:00<br><br>
        Escribe día y hora (ej: martes 10:30)
        <div class="time">10:04</div>
      </div>
      <div class="bubble bubble-out">
        Martes 10:30
        <div class="time">10:05 ✓✓</div>
      </div>
      <div class="bubble bubble-in">
        ✅ <strong>Cita pre-reservada</strong><br><br>
        📋 Consulta medicina general<br>
        📅 Martes 15 · 10:30 hrs<br>
        📍 Av. Apoquindo 4500, Las Condes<br><br>
        ¿Confirmas? Responde <strong>SI</strong> o <strong>NO</strong>
        <div class="time">10:05</div>
      </div>
      <div class="bubble bubble-out">
        SI
        <div class="time">10:05 ✓✓</div>
      </div>
      <div class="bubble bubble-in">
        🎉 ¡Listo! Tu hora quedó agendada.<br><br>
        Te enviaremos un recordatorio 24 h antes.<br>
        Si necesitas cambiarla, escribe <strong>CAMBIAR</strong>.<br><br>
        ¡Te esperamos!
        <div class="time">10:05</div>
      </div>
    </div>
  </div>

  <h2>Qué hace este bot (plan Premium / add-on)</h2>
  <ul>
    <li>Responde 24/7 fuera de horario de recepción</li>
    <li>Agenda citas y confirma automáticamente</li>
    <li>Deriva casos complejos a un humano</li>
    <li>Reduce llamadas perdidas y mensajes sin responder</li>
  </ul>

  <div class="cta">
    <strong>¿Te interesa activarlo?</strong>
    <p>Se instala después de la web (Paso 3). Add-on desde $50.000/mes (demo).</p>
    <a href="../paso-2-propuesta/index.html">Ver planes</a>
  </div>

  <p style="margin-top:1.5rem;font-size:0.85rem;text-align:center">
    <a href="../index.html">← Volver al embudo</a> ·
    <a href="../paso-3-web/index.html">Ver web</a>
  </p>
  <footer>Simulación demo · {nombre}</footer>
</div>
</body>
</html>"""
    out_path.write_text(html, encoding="utf-8")
    return out_path
