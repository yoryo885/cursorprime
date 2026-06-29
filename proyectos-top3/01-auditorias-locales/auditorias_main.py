#!/usr/bin/env python3
"""Orquestador audit local — usa marketing-audit + clientes/."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

CURSORPRIME = ROOT.parent.parent
MARKETING = CURSORPRIME / "marketing-audit"
CLIENTES = CURSORPRIME / "clientes"


def run_demo():
    brief = ROOT / "data" / "clinica-sol" / "inputs" / "brief.json"
    slug = "demo-clinica-sol"
    cmd = [
        sys.executable,
        str(MARKETING / "marketing_audit_main.py"),
        "audit",
        "--brief",
        str(brief),
        "--slug",
        slug,
        "--cliente",
        "clinica-sol",
        "--proyecto",
        "audit-inicial",
    ]
    print("→ marketing-audit (cliente ficticio clinica-sol)\n")
    r = subprocess.run(cmd, cwd=MARKETING)
    if r.returncode == 0:
        print(f"\n📁 Entregables: clientes/clinica-sol/proyectos/audit-inicial/entregables/")
    return r.returncode


def run_embudo():
    from embudo import run_embudo as _run

    return _run()


def main():
    p = argparse.ArgumentParser(description="Auditorías locales — demo y embudo HTML")
    p.add_argument("cmd", choices=["demo", "audit", "embudo"])
    args = p.parse_args()
    if args.cmd == "demo":
        sys.exit(run_demo())
    if args.cmd == "embudo":
        sys.exit(run_embudo())
    print("Usa: python3 auditorias_main.py demo | embudo")


if __name__ == "__main__":
    main()
