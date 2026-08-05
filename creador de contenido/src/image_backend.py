"""Backend visual compartido (ilustración personaje; IA real pendiente V1)."""

from __future__ import annotations

import hashlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter


# Vertical nativo para Telegram / Reels
DEFAULT_SIZE = (1080, 1920)


def _fonts(size_l: int = 44, size_s: int = 28):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    large = small = None
    for path in candidates:
        try:
            large = ImageFont.truetype(path, size_l)
            small = ImageFont.truetype(path, size_s)
            break
        except OSError:
            continue
    if large is None:
        large = ImageFont.load_default()
        small = large
    return large, small


def _hex(c: str, default: str) -> str:
    if isinstance(c, str) and c.startswith("#") and len(c) in (4, 7):
        return c
    return default


def _gradient(size: tuple[int, int], top: str, bottom: str) -> Image.Image:
    w, h = size
    img = Image.new("RGB", size, top)
    draw = ImageDraw.Draw(img)
    tr, tg, tb = tuple(int(top[i : i + 2], 16) for i in (1, 3, 5))
    br, bg, bb = tuple(int(bottom[i : i + 2], 16) for i in (1, 3, 5))
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(tr + (br - tr) * t)
        g = int(tg + (bg - tg) * t)
        b = int(tb + (bb - tb) * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return img


def _draw_person(
    draw: ImageDraw.ImageDraw,
    cx: int,
    base_y: int,
    *,
    scale: float = 1.0,
    skin: str = "#e8b896",
    hair: str = "#3b2a1a",
    shirt: str = "#f4efe6",
    apron: str | None = "#0e6b5c",
    smile: bool = False,
    hold_phone: bool = True,
    phone_happy: bool = False,
    arm_raise: bool = False,
) -> None:
    """Personaje cartoon con proporciones legibles (cabeza, torso, piernas)."""
    s = scale
    dark = "#1b2a38"

    head_r = int(78 * s)
    head_y = base_y - int(520 * s)
    # cabeza
    draw.ellipse(
        [cx - head_r, head_y - head_r, cx + head_r, head_y + head_r],
        fill=skin,
        outline=dark,
        width=3,
    )
    # pelo
    draw.ellipse(
        [cx - int(70 * s), head_y - head_r - int(10 * s), cx + int(70 * s), head_y - int(20 * s)],
        fill=hair,
    )
    # ojos
    ey = head_y - int(8 * s)
    er = int(10 * s)
    draw.ellipse([cx - int(28 * s) - er, ey - er, cx - int(28 * s) + er, ey + er], fill=dark)
    draw.ellipse([cx + int(28 * s) - er, ey - er, cx + int(28 * s) + er, ey + er], fill=dark)
    # mejillas
    draw.ellipse(
        [cx - int(48 * s), head_y + int(18 * s), cx - int(28 * s), head_y + int(34 * s)],
        fill="#f0a090",
    )
    draw.ellipse(
        [cx + int(28 * s), head_y + int(18 * s), cx + int(48 * s), head_y + int(34 * s)],
        fill="#f0a090",
    )
    # boca
    if smile:
        draw.arc(
            [cx - int(28 * s), head_y + int(20 * s), cx + int(28 * s), head_y + int(55 * s)],
            20,
            160,
            fill=dark,
            width=4,
        )
    else:
        draw.arc(
            [cx - int(22 * s), head_y + int(35 * s), cx + int(22 * s), head_y + int(55 * s)],
            200,
            340,
            fill=dark,
            width=4,
        )

    # cuello
    draw.rectangle(
        [cx - int(18 * s), head_y + head_r - 4, cx + int(18 * s), head_y + head_r + int(30 * s)],
        fill=skin,
    )
    # torso
    top = head_y + head_r + int(20 * s)
    bot = base_y - int(160 * s)
    draw.rounded_rectangle(
        [cx - int(95 * s), top, cx + int(95 * s), bot],
        radius=int(28 * s),
        fill=shirt,
        outline=dark,
        width=3,
    )
    if apron:
        draw.polygon(
            [
                (cx - int(70 * s), top + int(30 * s)),
                (cx + int(70 * s), top + int(30 * s)),
                (cx + int(85 * s), bot),
                (cx - int(85 * s), bot),
            ],
            fill=apron,
            outline=dark,
        )
        # bolsillo
        draw.rounded_rectangle(
            [cx - int(28 * s), bot - int(90 * s), cx + int(28 * s), bot - int(40 * s)],
            radius=8,
            outline="#ffffff",
            width=3,
        )

    # brazos
    arm_y1 = top + int(40 * s)
    if arm_raise:
        draw.line(
            [(cx - int(95 * s), arm_y1), (cx - int(160 * s), arm_y1 - int(120 * s))],
            fill=skin,
            width=int(28 * s),
        )
        draw.ellipse(
            [
                cx - int(175 * s),
                arm_y1 - int(145 * s),
                cx - int(145 * s),
                arm_y1 - int(115 * s),
            ],
            fill=skin,
            outline=dark,
            width=2,
        )
    else:
        draw.line(
            [(cx - int(95 * s), arm_y1), (cx - int(130 * s), arm_y1 + int(140 * s))],
            fill=skin,
            width=int(28 * s),
        )
        draw.ellipse(
            [
                cx - int(145 * s),
                arm_y1 + int(125 * s),
                cx - int(115 * s),
                arm_y1 + int(155 * s),
            ],
            fill=skin,
            outline=dark,
            width=2,
        )

    # brazo derecho + celular
    if hold_phone:
        ph_x = cx + int(110 * s)
        ph_y = arm_y1 + (int(20 * s) if not phone_happy else int(-10 * s))
        draw.line([(cx + int(95 * s), arm_y1), (ph_x, ph_y + int(40 * s))], fill=skin, width=int(28 * s))
        draw.rounded_rectangle(
            [ph_x - int(10 * s), ph_y, ph_x + int(70 * s), ph_y + int(130 * s)],
            radius=12,
            fill="#1f2a33",
            outline=dark,
            width=2,
        )
        screen = "#25D366" if phone_happy else "#ff8a80"
        draw.rounded_rectangle(
            [ph_x, ph_y + int(16 * s), ph_x + int(58 * s), ph_y + int(112 * s)],
            radius=6,
            fill=screen,
        )
        if not phone_happy:
            # burbujas de mensajes
            for i, ox in enumerate((-55, -70, -50)):
                by = ph_y + int(10 * s) + i * int(38 * s)
                draw.rounded_rectangle(
                    [ph_x + int(ox * s), by, ph_x + int((ox + 40) * s), by + int(28 * s)],
                    radius=10,
                    fill="#ffffff",
                    outline="#25D366",
                    width=2,
                )
    else:
        draw.line(
            [(cx + int(95 * s), arm_y1), (cx + int(130 * s), arm_y1 + int(140 * s))],
            fill=skin,
            width=int(28 * s),
        )

    # piernas + zapatos
    hip = bot
    foot = base_y - int(20 * s)
    draw.line([(cx - int(35 * s), hip), (cx - int(45 * s), foot)], fill="#2c3e50", width=int(26 * s))
    draw.line([(cx + int(35 * s), hip), (cx + int(45 * s), foot)], fill="#2c3e50", width=int(26 * s))
    draw.ellipse(
        [cx - int(70 * s), foot - int(15 * s), cx - int(20 * s), foot + int(20 * s)],
        fill=dark,
    )
    draw.ellipse(
        [cx + int(20 * s), foot - int(15 * s), cx + int(70 * s), foot + int(20 * s)],
        fill=dark,
    )


def _draw_guide(
    draw: ImageDraw.ImageDraw,
    cx: int,
    base_y: int,
    *,
    scale: float = 0.9,
    accent: str = "#2a6fdb",
) -> None:
    """Personaje guía (mascota / asistente) claramente distinto."""
    s = scale
    dark = "#1b2a38"
    skin = "#ffe0c2"
    head_r = int(70 * s)
    head_y = base_y - int(480 * s)

    # cuerpo cápsula
    draw.rounded_rectangle(
        [cx - int(80 * s), head_y + int(50 * s), cx + int(80 * s), base_y - int(40 * s)],
        radius=int(40 * s),
        fill=accent,
        outline=dark,
        width=3,
    )
    # cabeza
    draw.ellipse(
        [cx - head_r, head_y - head_r, cx + head_r, head_y + head_r],
        fill=skin,
        outline=dark,
        width=3,
    )
    # antena
    draw.line([(cx, head_y - head_r), (cx, head_y - head_r - int(40 * s))], fill=dark, width=4)
    draw.ellipse(
        [cx - int(12 * s), head_y - head_r - int(55 * s), cx + int(12 * s), head_y - head_r - int(30 * s)],
        fill="#ffd166",
        outline=dark,
        width=2,
    )
    # ojos grandes amables
    draw.ellipse(
        [cx - int(32 * s), head_y - int(15 * s), cx - int(8 * s), head_y + int(15 * s)],
        fill="#ffffff",
        outline=dark,
        width=2,
    )
    draw.ellipse(
        [cx + int(8 * s), head_y - int(15 * s), cx + int(32 * s), head_y + int(15 * s)],
        fill="#ffffff",
        outline=dark,
        width=2,
    )
    draw.ellipse(
        [cx - int(24 * s), head_y - int(5 * s), cx - int(14 * s), head_y + int(8 * s)],
        fill=dark,
    )
    draw.ellipse(
        [cx + int(16 * s), head_y - int(5 * s), cx + int(26 * s), head_y + int(8 * s)],
        fill=dark,
    )
    draw.arc(
        [cx - int(22 * s), head_y + int(15 * s), cx + int(22 * s), head_y + int(45 * s)],
        20,
        160,
        fill=dark,
        width=4,
    )
    # brazo señalando
    draw.line(
        [(cx - int(80 * s), head_y + int(120 * s)), (cx - int(160 * s), head_y + int(160 * s))],
        fill=skin,
        width=int(22 * s),
    )
    draw.ellipse(
        [
            cx - int(175 * s),
            head_y + int(145 * s),
            cx - int(145 * s),
            head_y + int(175 * s),
        ],
        fill=skin,
        outline=dark,
        width=2,
    )


def generate_placeholder(
    output_path: Path,
    titulo: str,
    tema: str,
    palette: list[str],
    frame: int = 1,
    frames_total: int = 1,
    size: tuple[int, int] = DEFAULT_SIZE,
    force_character: bool = False,
) -> Path:
    """Sistema: animado/personaje → figura; si no, card legacy (slideshow)."""
    t = f"{titulo} {tema}".lower()
    wants_character = force_character or any(
        k in t
        for k in (
            "personaje",
            "emprendedor",
            "delantal",
            "celular",
            "whatsapp",
            "cliente",
            "guía",
            "guia",
            "bot",
            "hombre",
            "mujer",
            "inicio",
            "fin",
        )
    )
    if wants_character or frames_total > 1:
        return generate_character_frame(
            output_path, titulo, tema, palette, frame=frame, frames_total=frames_total, size=size
        )

    bg = _hex(palette[2] if len(palette) > 2 else "", "#f5f5f5")
    accent = _hex(palette[1] if len(palette) > 1 else "", "#16a085")
    dark = _hex(palette[0] if palette else "", "#1a1a2e")

    img = Image.new("RGB", size, bg)
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, size[0] - 40, size[1] - 40], outline=accent, width=4)
    font_l, font_s = _fonts()
    draw.text((80, 80), titulo[:40], fill=dark, font=font_l)
    draw.text((80, 200), tema[:80], fill=accent, font=font_s)
    draw.text((80, size[1] - 100), "creador de contenido · mock", fill=accent, font=font_s)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, format="PNG")
    return output_path


def generate_character_frame(
    output_path: Path,
    titulo: str,
    tema: str,
    palette: list[str],
    frame: int = 1,
    frames_total: int = 1,
    size: tuple[int, int] = DEFAULT_SIZE,
) -> Path:
    """Escena vertical con personaje emprendedor (+ guía). Pensado para Telegram."""
    w, h = size
    accent = _hex(palette[1] if len(palette) > 1 else "", "#0e6b5c")
    dark = _hex(palette[0] if palette else "", "#1b2a38")
    apron = accent if accent.startswith("#") else "#0e6b5c"

    hsh = int(hashlib.md5(tema.encode()).hexdigest()[:6], 16)
    smile = frame >= 2 or any(k in tema.lower() for k in ("sonr", "feliz", "resuelto", "orden"))
    guide = any(k in tema.lower() for k in ("guía", "guia", "bot", "personaje", "amable", "muestra"))
    # frame 2 de cada escena también puede mostrar guía
    show_guide = guide or (frame == 2 and "celular" not in tema.lower())

    img = _gradient(size, "#dff3ff", "#fff6e8")
    draw = ImageDraw.Draw(img)

    # ambientación local (mostrador)
    draw.rectangle([0, int(h * 0.72), w, h], fill="#d9c4a5")
    draw.rectangle([int(w * 0.08), int(h * 0.68), int(w * 0.92), int(h * 0.72)], fill="#a67c52")
    # ventana
    draw.rounded_rectangle(
        [int(w * 0.12), int(h * 0.12), int(w * 0.88), int(h * 0.38)],
        radius=24,
        fill="#b8e0f0",
        outline="#7eb6c9",
        width=6,
    )
    # plantas
    for px in (int(w * 0.18), int(w * 0.82)):
        draw.ellipse([px - 40, int(h * 0.58), px + 40, int(h * 0.68)], fill="#3d8b6e")
        draw.rectangle([px - 12, int(h * 0.66), px + 12, int(h * 0.72)], fill="#8b5a2b")

    base_y = int(h * 0.88)
    if show_guide:
        _draw_person(
            draw,
            int(w * 0.34) + (hsh % 20) - 10,
            base_y,
            scale=1.05,
            apron=apron,
            smile=smile,
            hold_phone=True,
            phone_happy=smile,
            arm_raise=False,
        )
        _draw_guide(draw, int(w * 0.72), base_y, scale=0.95, accent="#2a6fdb")
    else:
        _draw_person(
            draw,
            int(w * 0.50) + (hsh % 30) - 15,
            base_y,
            scale=1.15,
            apron=apron,
            smile=smile,
            hold_phone=True,
            phone_happy=smile,
            arm_raise=smile,
        )

    # caption corta de escena (no card mock) — wrap a 2 líneas
    font_l, font_s = _fonts(36, 26)
    caption = (tema.split("·")[0].strip() if tema else titulo or "").strip()
    words = caption.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if len(trial) <= 34:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
        if len(lines) >= 2:
            break
    if cur and len(lines) < 2:
        lines.append(cur)
    band_y = int(h * 0.05)
    band_h = 56 + 44 * max(1, len(lines))
    draw.rounded_rectangle(
        [40, band_y, w - 40, band_y + band_h],
        radius=20,
        fill=dark,
    )
    for i, line in enumerate(lines[:2]):
        draw.text((64, band_y + 22 + i * 44), line, fill="#ffffff", font=font_l)

    img = img.filter(ImageFilter.SMOOTH)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, format="PNG")
    return output_path
