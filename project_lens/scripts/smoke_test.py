#!/usr/bin/env python3
"""Smoke test — ejecutar: python3 scripts/smoke_test.py"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
main = ROOT / "project_lens_main.py"

def run(args):
    r = subprocess.run([sys.executable, str(main), *args], cwd=ROOT, capture_output=True, text=True)
    print(r.stdout)
    if r.stderr:
        print(r.stderr, file=sys.stderr)
    return r.returncode

if __name__ == "__main__":
    code = run(["--slug", "demo-idea", "--modo", "mvp"])
    resumen = ROOT / "data" / "demo-idea" / "output" / "resumen.md"
    if code != 0:
        sys.exit(code)
    if not resumen.exists():
        print("FAIL: no resumen.md")
        sys.exit(1)
    print("OK:", resumen.read_text()[:200])
