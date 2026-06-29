import re


def tema_slug(tema: str, max_len: int = 40) -> str:
    return re.sub(r"[^\w-]", "_", tema.lower())[:max_len]
