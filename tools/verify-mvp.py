#!/usr/bin/env python3
"""Focused verification entry point for Mindy MVP work units."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def verify_mail():
    environment = os.environ.copy()
    environment["MINDY_MAIL_VERIFY_CHILD"] = "1"
    tests = subprocess.run(
        [sys.executable, "-m", "unittest", "overlay.tests.test_mail_shell", "-v"],
        cwd=ROOT,
        env=environment,
    )
    if tests.returncode:
        return tests.returncode
    patch = ROOT / "patches" / "0002-mindy-mail-shell.patch"
    checkout = ROOT / "vendor" / "gecko"
    applied = subprocess.run(["git", "apply", "--check", str(patch)], cwd=checkout)
    if applied.returncode:
        applied = subprocess.run(
            ["git", "apply", "--reverse", "--check", str(patch)], cwd=checkout
        )
        if applied.returncode:
            return applied.returncode
    receipt = json.loads(
        (ROOT / "overlay" / "upstream-test-receipt.json").read_text()
    )
    print("mail contract: PASS")
    print(f"upstream runtime: {receipt['runtimeStatus'].upper()}")
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "area",
        choices=("bootstrap", "mail", "visual-packages", "ai", "app-update", "ai-update", "validation"),
    )
    area = parser.parse_args().area
    if area == "mail":
        return verify_mail()
    if area == "visual-packages":
        return subprocess.run([sys.executable, str(ROOT / "tools" / "validate-visual-packages.py")], cwd=ROOT).returncode
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
