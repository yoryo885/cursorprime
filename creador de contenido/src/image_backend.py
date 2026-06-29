"""Backend visual compartido (mock MVP; IA real pendiente V1)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def _fonts():
    try:
        large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
        small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
    except OSError:
        large = ImageFont.load_default()
        small = large
    return large, small


def generate_placeholder(
    output_path: Path,
    titulo: str,
    tema: str,
    palette: list[str],
    frame: int = 1,
    frames_total: int = 1,
    size: tuple[int, int] = (1024, 1024),
) -> Path:
    bg = palette[2] if len(palette) > 2 else "#f5f5f5"
    accent = palette[1] if len(palette) > 1 else "#16a085"
    dark = palette[0] if palette else "#1a1a2e"

    img = Image.new("RGB", size, bg)
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, size[0] - 40, size[1] - 40], outline=accent, width=4)
    offset = frame * 12
    draw.rectangle([40 + offset, 120, size[0] - 40 - offset, size[1] - 140], outline=dark, width=2)

    font_l, font_s = _fonts()
    draw.text((80, 80), titulo[:40], fill=dark, font=font_l)
    draw.text((80, 200), tema, fill=accent, font=font_s)
    if frames_total > 1:
        draw.text((80, 260), f"frame {frame}/{frames_total}", fill=dark, font=font_s)
    draw.text((80, size[1] - 100), "creador de contenido · mock", fill=accent, font=font_s)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, format="PNG")
    return output_path
