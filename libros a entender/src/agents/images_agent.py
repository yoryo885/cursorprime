import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional

from src.agents.topic_translator import add_visual_suffix, translate_topics_for_search
from src.config import UNSPLASH_ACCESS_KEY
from src.llm import LLMClient
from src.models import TopicResult

UNSPLASH_SEARCH_URL = "https://api.unsplash.com/search/photos"
MIN_IMAGE_BYTES = 5000


class ImagesAgent:
    """Busca y descarga imágenes por tema usando Unsplash API."""

    def __init__(
        self,
        prompt_extra: Optional[list[str]] = None,
        llm: Optional[LLMClient] = None,
    ):
        self.prompt_extra = prompt_extra or []
        self.llm = llm
        self.access_key = UNSPLASH_ACCESS_KEY
        self._search_queries: dict[str, str] = {}

    def run(
        self,
        resultados: list[TopicResult],
        libro_nombre: str,
        output_dir: Path,
    ) -> dict[str, Path]:
        print("   🖼️  Agente Imágenes: buscando imágenes por tema (Unsplash)...")
        from src.output_paths import imagenes_dir

        img_dir = imagenes_dir(output_dir)
        img_dir.mkdir(parents=True, exist_ok=True)
        imagenes: dict[str, Path] = {}

        if not self.access_key:
            print("      ⚠️  UNSPLASH_ACCESS_KEY no configurada; sin imágenes.")
            return imagenes

        temas = [r.tema for r in resultados if not r.fallo]
        self._search_queries = translate_topics_for_search(temas, self.llm)

        for resultado in resultados:
            if resultado.fallo:
                continue

            slug = re.sub(r"[^\w-]", "_", resultado.tema.lower())[:40]
            existing = img_dir / f"{slug}.jpg"
            if existing.exists() and existing.stat().st_size > MIN_IMAGE_BYTES:
                imagenes[resultado.tema] = existing
                print(f"      ✓ Imagen en caché: '{resultado.tema}'")
                continue

            query_en = self._search_queries.get(resultado.tema, resultado.tema)
            query_visual = add_visual_suffix(query_en)
            print(f"      → Imagen: '{resultado.tema}' → '{query_visual}'...")
            try:
                path = self._buscar_y_descargar(resultado.tema, query_en, img_dir)
                if path:
                    imagenes[resultado.tema] = path
                else:
                    print(f"         · Sin imagen relevante para '{resultado.tema}'")
                time.sleep(1.0)
            except Exception as err:
                print(f"         ⚠️  Imagen falló: {err}")

        print(f"      ✓ {len(imagenes)} imágenes disponibles")
        return imagenes

    def _build_query(self, query_en: str) -> str:
        visual = add_visual_suffix(query_en)
        parts = [visual, *self.prompt_extra[:2]]
        return re.sub(r"\s+", " ", " ".join(parts)).strip()[:100]

    def _api_request(self, url: str) -> dict:
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Client-ID {self.access_key}",
                "Accept-Version": "v1",
            },
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read())

    def _buscar_y_descargar(
        self, tema: str, query_en: str, img_dir: Path
    ) -> Optional[Path]:
        query = self._build_query(query_en)
        params = urllib.parse.urlencode(
            {
                "query": query,
                "per_page": 5,
                "orientation": "landscape",
                "content_filter": "high",
            }
        )
        try:
            data = self._api_request(f"{UNSPLASH_SEARCH_URL}?{params}")
        except urllib.error.HTTPError as err:
            if err.code == 403:
                print("         ⚠️  Unsplash rechazó la clave (403)")
            elif err.code == 429:
                print("         ⚠️  Límite de Unsplash alcanzado (429)")
            return None

        results = data.get("results") or []
        if not results:
            return None

        photo = results[0]
        urls = photo.get("urls") or {}
        image_url = urls.get("full") or urls.get("regular")
        if not image_url:
            return None

        download_location = (photo.get("links") or {}).get("download_location")
        if download_location:
            try:
                self._api_request(download_location)
            except Exception:
                pass

        image_url = self._high_quality_url(image_url)
        slug = re.sub(r"[^\w-]", "_", tema.lower())[:40]
        dest = img_dir / f"{slug}.jpg"

        data_bytes = self._download_image(image_url)
        if not data_bytes or len(data_bytes) < MIN_IMAGE_BYTES:
            return None

        dest.write_bytes(data_bytes)
        return dest

    def _high_quality_url(self, url: str) -> str:
        sep = "&" if "?" in url else "?"
        return f"{url}{sep}w=1920&q=85&fm=jpg"

    def _download_image(self, url: str) -> Optional[bytes]:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "LibrosAgent/1.0 (Unsplash download)"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read()
        except Exception:
            return None
