#!/usr/bin/env python3
"""CLI — Bot WhatsApp pymes (demo mock)."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.pipeline import run_demo  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["demo"])
    args = p.parse_args()
    ok = run_demo()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
