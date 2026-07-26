"""Backend visual: placeholder mock o API real (OpenAI / Replicate) con fallback."""

from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from src.config import MOCK_GENERATE

IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "openai").lower()  # openai | replicate
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "dall-e-3")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
REPLICATE_IMAGE_MODEL = os.getenv(
    "REPLICATE_IMAGE_MODEL",
    "black-forest-labs/flux-schnell",
)


def _fonts():
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        try:
            large = ImageFont.truetype(path, 48)
            small = ImageFont.truetype(path, 28)
            return large, small
        except OSError:
            continue
    large = ImageFont.load_default()
    return large, large


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
    draw.text((80, 200), tema[:80], fill=accent, font=font_s)
    if frames_total > 1:
        draw.text((80, 260), f"frame {frame}/{frames_total}", fill=dark, font=font_s)
    draw.text((80, size[1] - 100), "creador de contenido · mock", fill=accent, font=font_s)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, format="PNG")
    return output_path


def _openai_image(prompt: str, output_path: Path, size: str = "1024x1024") -> None:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY no configurada")
    body = {
        "model": OPENAI_IMAGE_MODEL,
        "prompt": prompt[:3900],
        "n": 1,
        "size": size,
        "response_format": "b64_json",
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    b64 = payload["data"][0]["b64_json"]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(base64.b64decode(b64))


def _replicate_image(prompt: str, output_path: Path) -> None:
    """Flux schnell vía Replicate predictions API (sync wait)."""
    if not REPLICATE_API_TOKEN:
        raise RuntimeError("REPLICATE_API_TOKEN no configurada")
    create_body = {
        "input": {"prompt": prompt[:2000], "num_outputs": 1},
    }
    # Prefer model versionless deployments endpoint when model has /
    url = f"https://api.replicate.com/v1/models/{REPLICATE_IMAGE_MODEL}/predictions"
    req = urllib.request.Request(
        url,
        data=json.dumps(create_body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {REPLICATE_API_TOKEN}",
            "Content-Type": "application/json",
            "Prefer": "wait",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")[:300]
        raise RuntimeError(f"Replicate HTTP {exc.code}: {detail}") from exc

    out = payload.get("output")
    if isinstance(out, list) and out:
        image_url = out[0]
    elif isinstance(out, str):
        image_url = out
    else:
        raise RuntimeError(f"Replicate sin output: {payload.get('status')}")

    with urllib.request.urlopen(image_url, timeout=120) as img_resp:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(img_resp.read())


def generate_image(
    output_path: Path,
    *,
    prompt: str,
    titulo: str,
    tema: str,
    palette: list[str] | None = None,
    frame: int = 1,
    frames_total: int = 1,
    mock: bool | None = None,
) -> tuple[Path, bool, str]:
    """
    Genera PNG. Retorna (path, fue_mock, nota).
    Si mock=False y falla la API → placeholder + warning (no tumba el lote).
    """
    use_mock = MOCK_GENERATE if mock is None else mock
    palette = palette or ["#1a1a2e", "#16a085", "#f5f5f5"]

    if use_mock:
        generate_placeholder(output_path, titulo, tema, palette, frame, frames_total)
        return output_path, True, "mock_placeholder"

    try:
        if IMAGE_PROVIDER == "replicate":
            _replicate_image(prompt, output_path)
            return output_path, False, "replicate"
        _openai_image(prompt, output_path)
        return output_path, False, "openai"
    except Exception as exc:
        generate_placeholder(output_path, titulo, tema, palette, frame, frames_total)
        return output_path, True, f"fallback_placeholder: {exc}"[:200]
