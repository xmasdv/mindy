#!/usr/bin/env python3
"""Focused verification entry point for Mindy MVP work units."""

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "area",
        choices=("bootstrap", "mail", "ai", "app-update", "ai-update", "validation"),
    )
    area = parser.parse_args().area
    if area != "bootstrap":
        print(f"{area} verification is not implemented yet", file=sys.stderr)
        return 2
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "bootstrap-upstream.py"), "--contract-only"],
        cwd=ROOT,
    )
    if result.returncode:
        return result.returncode
    print("bootstrap contract: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
