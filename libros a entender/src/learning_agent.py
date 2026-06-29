"""
learning_agent.py — aprendizaje acumulativo entre libros.
"""
import json
from datetime import datetime
from pathlib import Path


class LearningSystem:
    def __init__(self, logs_dir: Path):
        self.path = logs_dir / "mejoras.json"
        logs_dir.mkdir(parents=True, exist_ok=True)

    def registrar(self, instruccion: str, libro: str, score_antes: float) -> None:
        mejoras = self._load()
        nueva = {
            "id": f"imp_{len(mejoras) + 1:03d}",
            "instruccion": instruccion,
            "libro_origen": libro,
            "score_antes": round(score_antes, 3),
            "score_despues": None,
            "activa": True,
            "fecha": datetime.now().isoformat(),
        }
        mejoras.append(nueva)
        self._save(mejoras)
        print(f"💡 Mejora registrada: [{nueva['id']}] {instruccion[:60]}...")

    def validar(self, score_actual: float) -> None:
        mejoras = self._load()
        for m in mejoras:
            if m["score_despues"] is None and m["activa"]:
                m["score_despues"] = round(score_actual, 3)
                delta = score_actual - m["score_antes"]
                if delta < -0.05:
                    m["activa"] = False
                    print(f"⚠️  Mejora '{m['id']}' desactivada (score bajó {delta:.2f})")
                else:
                    print(f"✅ Mejora '{m['id']}' validada (delta {delta:+.2f})")
        self._save(mejoras)

    def instrucciones_activas(self) -> list[str]:
        return [m["instruccion"] for m in self._load() if m["activa"]]

    def bloque_prompt(self) -> str:
        instrucciones = self.instrucciones_activas()
        if not instrucciones:
            return ""
        lineas = "\n".join(f"- {i}" for i in instrucciones)
        return f"\n\nMejoras aprendidas de libros anteriores (aplícalas):\n{lineas}\n"

    def registrar_error(self, tema: str, libro: str, motivo: str) -> None:
        errores_path = self.path.parent / "errores.json"
        errores = []
        if errores_path.exists():
            try:
                errores = json.loads(errores_path.read_text())
            except json.JSONDecodeError:
                errores = []
        errores.append({
            "tema": tema,
            "libro": libro,
            "motivo": motivo,
            "fecha": datetime.now().isoformat(),
        })
        errores_path.write_text(json.dumps(errores, ensure_ascii=False, indent=2))

    def _load(self) -> list:
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text())
            if isinstance(data, list):
                return data
            return []
        except json.JSONDecodeError:
            return []

    def _save(self, data: list) -> None:
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
