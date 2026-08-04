"""Backend visual compartido (mock ilustrado; IA real pendiente V1)."""

from __future__ import annotations

import hashlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def _fonts():
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    large = small = None
    for path in candidates:
        try:
            large = ImageFont.truetype(path, 36)
            small = ImageFont.truetype(path, 22)
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


def generate_placeholder(
    output_path: Path,
    titulo: str,
    tema: str,
    palette: list[str],
    frame: int = 1,
    frames_total: int = 1,
    size: tuple[int, int] = (1024, 1024),
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
    offset = frame * 12
    draw.rectangle([40 + offset, 120, size[0] - 40 - offset, size[1] - 140], outline=dark, width=2)

    font_l, font_s = _fonts()
    draw.text((80, 80), titulo[:40], fill=dark, font=font_l)
    draw.text((80, 200), tema[:80], fill=accent, font=font_s)
    if frames_total > 1:
        draw.text((80, 260), f"frame {frame}/{frames_total}", fill=dark, font=font_s)
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
    size: tuple[int, int] = (1024, 1024),
) -> Path:
    """Ilustración simple con personaje visible (emprendedor / guía)."""
    skin = "#e8b896"
    hair = "#3b2a1a"
    apron = _hex(palette[1] if len(palette) > 1 else "", "#c45c26")
    shirt = "#f4efe6"
    bg = _hex(palette[2] if len(palette) > 2 else "", "#f3ebe0")
    accent = _hex(palette[1] if len(palette) > 1 else "", "#0e6b5c")
    dark = _hex(palette[0] if palette else "", "#1b2a38")
    phone = "#1f2a33"

    # Variación por frame (inicio vs fin) y hash del tema
    h = int(hashlib.md5(tema.encode()).hexdigest()[:6], 16)
    shift = 40 if frame == 1 else 0
    smile = frame >= 2 or "sonr" in tema.lower() or "feliz" in tema.lower()
    guide = any(k in tema.lower() for k in ("guía", "guia", "bot", "personaje guía", "amable"))

    img = Image.new("RGB", size, bg)
    draw = ImageDraw.Draw(img)

    # suelo / mesa
    draw.ellipse([120, 720, 900, 980], fill="#e2d3c0")

    cx = 420 + (h % 40) - shift
    # cuerpo
    draw.ellipse([cx - 70, 280, cx + 70, 420], fill=skin)  # cabeza
    draw.ellipse([cx - 55, 270, cx + 55, 330], fill=hair)  # pelo
    # ojos
    draw.ellipse([cx - 28, 330, cx - 12, 346], fill=dark)
    draw.ellipse([cx + 12, 330, cx + 28, 346], fill=dark)
    # boca
    if smile:
        draw.arc([cx - 22, 355, cx + 22, 390], 20, 160, fill=dark, width=4)
    else:
        draw.line([cx - 18, 375, cx + 18, 375], fill=dark, width=4)

    # torso + delantal
    draw.rectangle([cx - 90, 420, cx + 90, 700], fill=shirt)
    draw.polygon(
        [(cx - 70, 450), (cx + 70, 450), (cx + 80, 700), (cx - 80, 700)],
        fill=apron,
    )
    # brazos
    draw.rectangle([cx - 130, 460, cx - 90, 620], fill=skin)
    draw.rectangle([cx + 90, 460, cx + 130, 580], fill=skin)

    # celular
    px, py = cx + 95, 500 + (0 if frame == 1 else -30)
    draw.rounded_rectangle([px, py, px + 70, py + 120], radius=10, fill=phone)
    draw.rectangle([px + 8, py + 18, px + 62, py + 100], fill="#7ddea8" if smile else "#f0a090")
    # burbujas wasap
    if not smile:
        draw.ellipse([px - 40, py - 10, px - 5, py + 25], fill="#ffffff", outline=accent, width=2)
        draw.ellipse([px - 55, py + 30, px - 15, py + 65], fill="#ffffff", outline=accent, width=2)

    # personaje guía (segundo) en escenas de guía o frame 2
    if guide or frame == 2:
        gx = 720
        draw.ellipse([gx - 55, 300, gx + 55, 410], fill="#f0c4a8")
        draw.ellipse([gx - 45, 290, gx + 45, 345], fill="#2c3e50")
        draw.ellipse([gx - 20, 345, gx - 8, 357], fill=dark)
        draw.ellipse([gx + 8, 345, gx + 20, 357], fill=dark)
        draw.arc([gx - 18, 365, gx + 18, 395], 20, 160, fill=dark, width=3)
        draw.rectangle([gx - 70, 410, gx + 70, 680], fill=accent)
        # mano señalando
        draw.polygon([(gx - 70, 520), (cx + 100, 540), (gx - 70, 560)], fill="#f0c4a8")

    # Título mínimo — el foco es el personaje, no la card
    font_l, font_s = _fonts()
    draw.rectangle([0, 0, size[0], 72], fill=dark)
    draw.text((28, 22), (titulo or "Personaje")[:40], fill="#ffffff", font=font_l)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, format="PNG")
    return output_path
