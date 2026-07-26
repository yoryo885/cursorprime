"""Resuelve rutas de artefactos portables (cloud ↔ Mac)."""

from __future__ import annotations

from pathlib import Path

from src.config import ROOT


def resolve_existing(*candidates: Path | str | None) -> Path | None:
    for raw in candidates:
        if not raw:
            continue
        p = Path(raw)
        if p.exists() and p.is_file():
            return p
    return None


def resolve_video_final(videos_meta: dict, videos_out: Path, slug: str) -> Path | None:
    """
    Busca el MP4 final aunque generated_videos.json tenga rutas absolutas de otra máquina.
    Nunca devuelve un clip de videos/clips/.
    """
    videos_out = Path(videos_out)
    preferred: list[Path] = []

    # 1) Convención local más fiable
    preferred.append(videos_out / f"{slug}.mp4")
    preferred.append(ROOT / "data" / slug / "videos" / f"{slug}.mp4")

    # 2) Campo final / tipo final (por path y por nombre en carpeta videos/)
    raw_final = videos_meta.get("final")
    if raw_final:
        preferred.append(Path(str(raw_final)))
        preferred.append(videos_out / Path(str(raw_final)).name)

    for v in videos_meta.get("videos") or []:
        if v.get("tipo") != "final":
            continue
        if v.get("path"):
            preferred.append(Path(str(v["path"])))
        name = v.get("archivo") or Path(str(v.get("path") or "")).name
        if name and name.endswith(".mp4") and not name.endswith("_audio.mp4"):
            preferred.append(videos_out / name)

    # 3) Cualquier mp4 en videos/ (no clips, no _audio)
    if videos_out.exists():
        for p in sorted(videos_out.glob("*.mp4")):
            if p.name.endswith("_audio.mp4"):
                continue
            preferred.append(p)

    return resolve_existing(*preferred)


def resolve_artifact_path(raw_path: str, fallback_dirs: list[Path]) -> Path | None:
    """Si el path absoluto no existe, busca el mismo nombre en dirs locales."""
    p = Path(raw_path)
    if p.exists():
        return p
    name = p.name
    if not name:
        return None
    return resolve_existing(*(d / name for d in fallback_dirs))
