import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

from src.config import NAPKIN_API_BASE, NAPKIN_API_KEY

NAPKIN_STYLE_CORPORATE = "CSQQ4VB1DGPPTVVEDXHPGWKFDNJJTSKCC5T0"
POLL_START_SECS = 2.0
POLL_MAX_SECS = 30.0
POLL_MAX_ATTEMPTS = 40


class NapkinClient:
    """Cliente mínimo para la API de Napkin AI."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or NAPKIN_API_KEY
        self.base_url = NAPKIN_API_BASE.rstrip("/")

    def generate_visual(
        self,
        content: str,
        output_path: Path,
        *,
        visual_query: str = "mindmap",
        context_before: str = "",
        context_after: str = "",
        language: str = "es-ES",
        style_id: str = NAPKIN_STYLE_CORPORATE,
        width: int = 1920,
    ) -> Path:
        if not self.api_key:
            raise ValueError(
                "Se requiere NAPKIN_API_KEY. Agrégala al archivo .env."
            )

        payload = {
            "format": "png",
            "content": content,
            "visual_query": visual_query,
            "language": language,
            "style_id": style_id,
            "number_of_visuals": 1,
            "width": width,
        }
        if context_before:
            payload["context_before"] = context_before
        if context_after:
            payload["context_after"] = context_after

        created = self._request("POST", "/v1/visual", payload)
        request_id = created.get("id")
        if not request_id:
            raise RuntimeError("Napkin no devolvió id de solicitud")

        status_data = self._poll_until_done(request_id)
        files = status_data.get("generated_files") or []
        if not files:
            raise RuntimeError("Napkin completó sin archivos generados")

        file_info = files[0]
        download_url = file_info.get("url")
        file_id = file_info.get("id")
        if not download_url and file_id:
            download_url = f"{self.base_url}/v1/visual/{request_id}/file/{file_id}"

        if not download_url:
            raise RuntimeError("Napkin no devolvió URL de descarga")

        data = self._download_file(download_url)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(data)
        return output_path

    def _poll_until_done(self, request_id: str) -> dict:
        delay = POLL_START_SECS
        for attempt in range(POLL_MAX_ATTEMPTS):
            data = self._request("GET", f"/v1/visual/{request_id}/status")
            status = data.get("status", "pending")
            if status == "completed":
                return data
            if status == "failed":
                if attempt < 2:
                    time.sleep(5)
                    continue
                raise RuntimeError(f"Napkin falló la generación (request {request_id})")

            time.sleep(delay)
            delay = min(delay * 1.5, POLL_MAX_SECS)

        raise TimeoutError(
            f"Napkin no completó a tiempo (request {request_id})"
        )

    def _headers(self, *, json_body: bool = False) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "User-Agent": "LibrosAgent/1.0 (compatible; NapkinAPI/1.0)",
        }
        if json_body:
            headers["Content-Type"] = "application/json"
        return headers

    def _request(self, method: str, path: str, payload: Optional[dict] = None) -> dict:
        url = f"{self.base_url}{path}"
        body = None
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=body,
            headers=self._headers(json_body=payload is not None),
            method=method,
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as err:
            detail = err.read().decode("utf-8", errors="replace")[:300]
            raise RuntimeError(
                f"Napkin HTTP {err.code}: {detail}"
            ) from err

    def _download_file(self, url: str) -> bytes:
        req = urllib.request.Request(
            url,
            headers={
                **self._headers(),
                "Accept": "*/*",
            },
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.read()
