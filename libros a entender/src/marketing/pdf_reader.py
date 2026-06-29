from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader  # type: ignore


from src.marketing.constitution import assert_read_only_pdf


MAX_CHARS_LLM = 48_000


@dataclass
class PDFContent:
    path: Path
    num_paginas: int
    texto_completo: str
    texto_para_llm: str
    nombre_archivo: str

    @property
    def titulo_inferido(self) -> str:
        for linea in self.texto_completo.splitlines():
            limpia = linea.strip()
            if len(limpia) > 8:
                return limpia[:120]
        return self.nombre_archivo


def extract_pdf_content(pdf_path: Path) -> PDFContent:
    path = assert_read_only_pdf(pdf_path)

    reader = PdfReader(str(path))
    paginas: list[str] = []
    for page in reader.pages:
        paginas.append((page.extract_text() or "").strip())

    texto_completo = "\n\n".join(p for p in paginas if p)
    texto_para_llm = _recortar_para_llm(texto_completo, paginas)

    return PDFContent(
        path=path,
        num_paginas=len(reader.pages),
        texto_completo=texto_completo,
        texto_para_llm=texto_para_llm,
        nombre_archivo=path.name,
    )


def _recortar_para_llm(texto: str, paginas: list[str]) -> str:
    if len(texto) <= MAX_CHARS_LLM:
        return texto

    head_pages = min(12, len(paginas))
    tail_pages = min(4, max(0, len(paginas) - head_pages))
    head = "\n\n".join(paginas[:head_pages])
    tail = "\n\n".join(paginas[-tail_pages:]) if tail_pages else ""
    recorte = f"{head}\n\n[... contenido intermedio omitido ...]\n\n{tail}"
    return recorte[:MAX_CHARS_LLM]
