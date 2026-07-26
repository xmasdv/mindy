#!/usr/bin/env python3
"""Reproduce and verify Mindy's paired Thunderbird/Gecko checkout."""

import argparse
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "sources.lock"
PATCH_DIR = ROOT / "patches"
MOZCONFIG = (ROOT / "config" / "mozconfig-pilot").resolve()
HEX40 = re.compile(r"^[0-9a-f]{40}$")

def load_lock(path=LOCK_PATH):
    lock = json.loads(Path(path).read_text(encoding="utf-8"))
    if lock.get("schema") != 1:
        raise ValueError("sources.lock schema must be 1")
    for name in ("gecko", "comm"):
        source = lock.get(name, {})
        if not source.get("repository", "").startswith("https://hg.mozilla.org/"):
            raise ValueError(f"{name} repository must use Mozilla HTTPS")
        if not HEX40.fullmatch(source.get("revision", "")):
            raise ValueError(f"{name} revision must be a full 40-character hash")
    if lock.get("compatibility", {}).get("gecko_revision") != lock["gecko"]["revision"]:
        raise ValueError("compatibility Gecko revision differs from Gecko pin")
    if lock.get("layout") != {
        "gecko": "vendor/gecko",
        "comm": "vendor/gecko/comm",
    }:
        raise ValueError("checkout layout must be vendor/gecko with nested comm")
    return lock

def verify_gecko_rev(text, expected):
    values = dict(re.findall(r"^([A-Z_]+):\s*(\S+)\s*$", text, re.MULTILINE))
    if values.get("GECKO_HEAD_REPOSITORY") != expected["repository"]:
        raise ValueError("GECKO_HEAD_REPOSITORY does not match sources.lock")
    if values.get("GECKO_HEAD_REV") != expected["revision"]:
        raise ValueError("GECKO_HEAD_REV does not match sources.lock")

def read_series(text=None, patch_dir=PATCH_DIR):
    text = (patch_dir / "series").read_text(encoding="utf-8") if text is None else text
    patches, seen = [], set()
    for raw in text.splitlines():
        value = raw.split("#", 1)[0].strip()
        if not value:
            continue
        path = PurePosixPath(value)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"unsafe patch path: {value}")
        if value in seen:
            raise ValueError(f"duplicate patch path: {value}")
        resolved = (patch_dir / Path(*path.parts)).resolve()
        if patch_dir.resolve() not in resolved.parents or not resolved.is_file():
            raise ValueError(f"missing patch: {value}")
        seen.add(value)
        patches.append(resolved)
    return patches

def verify_contract():
    lock = load_lock()
    text = MOZCONFIG.read_text(encoding="utf-8")
    if "ac_add_options --enable-project=comm/mail" not in text:
        raise ValueError("mozconfig does not select comm/mail")
    if not MOZCONFIG.is_absolute():
        raise ValueError("MOZCONFIG path is not absolute")
    read_series()
    return lock

def run(command, cwd=None, env=None):
    print("+", subprocess.list2cmdline([str(part) for part in command]))
    subprocess.run(command, cwd=cwd, env=env, check=True)

def require_hg():
    executable = shutil.which("hg")
    if not executable:
        raise RuntimeError("Mercurial (hg) is required; install Mozilla build prerequisites")
    return executable

def paths(lock):
    return ROOT / lock["layout"]["gecko"], ROOT / lock["layout"]["comm"]

def _remove_read_only(function, path, error):
    if not isinstance(error, PermissionError):
        raise error
    os.chmod(path, stat.S_IWRITE)
    function(path)

def cleanup_created_clone(destination, vendor_root):
    destination = Path(destination)
    is_junction = getattr(destination, "is_junction", lambda: False)
    if destination.is_symlink() or is_junction():
        raise RuntimeError(f"unsafe clone cleanup target: {destination}")
    target = destination.resolve()
    vendor = Path(vendor_root).resolve()
    if target == vendor or vendor not in target.parents:
        raise RuntimeError(f"unsafe clone cleanup target: {destination}")
    if target.exists():
        shutil.rmtree(target, onexc=_remove_read_only)

def clone_with_fallback(hg, repository, destination, vendor_root):
    destination = Path(destination)
    if destination.exists():
        raise RuntimeError(f"refusing existing clone destination: {destination}")
    primary = [hg, "clone", "-U", repository, destination]
    fallback = [hg, "--config", "ui.clonebundles=false", *primary[1:]]
    for command in (primary, fallback):
        try:
            run(command)
            return
        except (OSError, subprocess.CalledProcessError):
            cleanup_created_clone(destination, vendor_root)
            if command is fallback:
                raise

def checkout(lock):
    hg = require_hg()
    gecko, comm = paths(lock)
    for source, destination in ((lock["gecko"], gecko), (lock["comm"], comm)):
        if destination.exists() and not (destination / ".hg").is_dir():
            raise RuntimeError(f"refusing non-Mercurial destination: {destination}")
        if not destination.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            clone_with_fallback(hg, source["repository"], destination, ROOT / "vendor")
        dirty = subprocess.check_output(
            [hg, "-R", destination, "status", "-mard"], text=True
        ).strip()
        if dirty:
            raise RuntimeError(f"refusing to overwrite changes in {destination}")
        run([hg, "-R", destination, "update", "--rev", source["revision"]])

def verify_checkout(lock):
    hg = require_hg()
    gecko, comm = paths(lock)
    for name, source, directory in (
        ("gecko", lock["gecko"], gecko),
        ("comm", lock["comm"], comm),
    ):
        if not (directory / ".hg").is_dir():
            raise RuntimeError(f"{name} checkout missing: {directory}")
        node = subprocess.check_output(
            [hg, "-R", directory, "log", "-r", ".", "-T", "{node}"], text=True
        ).strip()
        if node != source["revision"]:
            raise RuntimeError(f"{name} checkout is {node}, expected {source['revision']}")
    verify_gecko_rev((comm / ".gecko_rev.yml").read_text(encoding="utf-8"), lock["gecko"])

def apply_patches(lock):
    verify_checkout(lock)
    patch_files = read_series()
    if patch_files:
        git = shutil.which("git")
        if not git:
            raise RuntimeError("git is required to apply the ordered patch series")
        run([git, "apply", "--directory=vendor/gecko", "--check", *patch_files], cwd=ROOT)
        run([git, "apply", "--directory=vendor/gecko", *patch_files], cwd=ROOT)

def build_pilot(lock):
    if sys.platform != "win32":
        raise RuntimeError("the pilot build is supported only on Windows 11 x64")
    apply_patches(lock)
    gecko, _ = paths(lock)
    env = os.environ.copy()
    env["MOZCONFIG"] = str(MOZCONFIG)
    run([sys.executable, str(gecko / "mach"), "build"], cwd=gecko, env=env)

def main():
    parser = argparse.ArgumentParser()
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--contract-only", action="store_true", help=argparse.SUPPRESS)
    actions.add_argument("--checkout", action="store_true")
    actions.add_argument("--verify", action="store_true")
    actions.add_argument("--apply-patches", action="store_true")
    actions.add_argument("--build-pilot", action="store_true")
    args = parser.parse_args()
    try:
        lock = verify_contract()
        if args.checkout:
            checkout(lock)
            verify_checkout(lock)
        elif args.verify:
            verify_checkout(lock)
        elif args.apply_patches:
            apply_patches(lock)
        elif args.build_pilot:
            build_pilot(lock)
        print("upstream bootstrap: PASS")
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"upstream bootstrap: FAIL: {error}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
