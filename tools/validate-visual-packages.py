#!/usr/bin/env python3
"""Generate and validate the authority-backed Phase 1A package patch."""

import hashlib, json, os, re, shutil, subprocess, sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SERIES = ("0002-mindy-mail-shell.patch", "0003-mindy-visual-packages.patch")
PACKAGE_PATCH = EXPECTED_SERIES[1]
ROOTS = ("contracts", "adapters", "ui", "theme", "brand", "test")
REQUIRED_EDGES = {("adapters", "contracts"), ("ui", "adapters"),
                  ("ui", "theme"), ("ui", "brand"), ("test", "ui")}
IMPORT = re.compile(r'(?:from\s+|import\s+|importESModule\(\s*)["\']resource:///modules/mindy/([^/]+)/')
GLOBALS = re.compile(r"\b(?:ChromeUtils|Services|MailServices|Cc|Ci|Cr)\b")

class PackageError(ValueError):
    pass

def require(condition, message):
    if not condition:
        raise PackageError(message)

def safe_relative(raw):
    require(isinstance(raw, str) and raw, "path must be non-empty")
    relative = PurePosixPath(raw)
    native = Path(raw)
    require("\\" not in raw and not native.is_absolute() and not native.drive and
            not relative.is_absolute() and not relative.drive and ".." not in relative.parts,
            f"unsafe path: {raw}")
    return relative

def safe_path(raw, root=ROOT):
    relative = safe_relative(raw)
    cursor = Path(root).resolve()
    for part in relative.parts:
        cursor /= part
        require(not cursor.is_symlink() and
                not getattr(os.path, "isjunction", lambda _: False)(cursor),
                f"linked path rejected: {raw}")
    resolved = cursor.resolve(strict=True)
    require(Path(root).resolve() in resolved.parents, f"resolved path escapes repository: {raw}")
    return resolved

def load(raw):
    return json.loads(safe_path(raw).read_text(encoding="utf-8"))

def series():
    names = tuple(line.split("#", 1)[0].strip() for line in
                  safe_path("patches/series").read_text().splitlines()
                  if line.split("#", 1)[0].strip())
    require(names == EXPECTED_SERIES, "patch series identity/order differs")
    return [safe_path(f"patches/{name}") for name in names]

def generated_registry():
    authority = load("contracts/visual/authority.json")
    schema = load(authority["surface_inventory"]["schema_path"])
    ids = [item for family in schema["x-exact-families"].values() for item in family]
    require(len(ids) == len(set(ids)) == authority["surface_inventory"]["total"] == 80,
            "authority registry IDs differ")
    payload = {"authoritySha256": hashlib.sha256(
        safe_path("contracts/visual/authority.json").read_bytes()).hexdigest(),
        "schemaVersion": authority["schema_version"], "phase": authority["phase"]}
    prefix = "export const VisualRegistry = Object.freeze("
    body = json.dumps(payload, separators=(",", ":"))[:-1]
    return f'{prefix}{body},"surfaceIds":Object.freeze({json.dumps(ids, separators=(",", ":"))})}});'

def added_files(patch=None):
    text = (patch or safe_path(f"patches/{PACKAGE_PATCH}")).read_text(encoding="utf-8")
    files, current, collecting = {}, None, False
    for line in text.splitlines():
        if line.startswith("diff --git "):
            current, collecting = line.split(" b/", 1)[1], False
            safe_relative(current)
            require(current.startswith("comm/mail/"), f"patch target outside Thunderbird mail: {current}")
            files.setdefault(current, [])
        elif line.startswith("@@"):
            collecting = True
        elif collecting and line.startswith("+") and not line.startswith("+++"):
            files[current].append(line[1:])
    return {path: "\n".join(lines) for path, lines in files.items()}

def layer(path):
    parts = PurePosixPath(path).parts
    return "test" if "test" in parts else parts[3]

def validate_packages(files):
    require(set(ROOTS) <= {layer(path) for path in files
                           if path.startswith("comm/mail/mindy/") and len(PurePosixPath(path).parts) > 4},
            "package root missing")
    hook = files.get("comm/mail/moz.build", "")
    require(hook == '    "mindy",', "package registration hook differs")
    top = files.get("comm/mail/mindy/moz.build", "")
    require('DIRS += ["contracts", "adapters", "theme", "brand", "ui"]' in top and
            'TEST_DIRS += ["test"]' in top, "package roots are unregistered")
    modules = {path: text for path, text in files.items() if path.endswith((".mjs", ".js"))}
    edges = set()
    for path, text in modules.items():
        source = layer(path)
        require(text.strip() and "{}" not in text, f"empty package module: {path}")
        require(f'EXTRA_JS_MODULES.mindy.{source}' in files.get(
            f"comm/mail/mindy/{source}/moz.build", "") or source == "test",
            f"unregistered package module: {path}")
        edges.update((source, target) for target in IMPORT.findall(text))
        if source == "ui":
            require(not GLOBALS.search(text), "owned UI imports Thunderbird globals")
    require(edges == REQUIRED_EDGES, f"package import edges differ: {sorted(edges)}")
    require('XPCSHELL_TESTS_MANIFESTS += ["xpcshell.toml"]' in
            files.get("comm/mail/mindy/test/moz.build", ""), "test root is unregistered")
    registry = files.get("comm/mail/mindy/contracts/VisualRegistry.sys.mjs", "")
    require(registry == generated_registry(), "runtime registry drift/duplication detected")

def validate_pins(authority=None, sources=None):
    authority = authority or load("contracts/visual/authority.json")
    sources = sources or load("sources.lock")
    behavior = authority["behavior_authority"]
    require((sources["gecko"]["revision"], sources["comm"]["revision"]) ==
            (behavior["gecko_revision"], behavior["comm_revision"]), "source pins differ")

def applicability():
    source = Path(os.environ.get("MINDY_GECKO_SOURCE", ROOT / "vendor" / "gecko"))
    if not source.is_dir():
        return "UNAVAILABLE(source checkout missing)"
    hg = shutil.which("hg")
    if not hg:
        return "UNAVAILABLE(Mercurial missing; pins unverified)"
    lock = load("sources.lock")
    for name, directory in (("gecko", source), ("comm", source / "comm")):
        node = subprocess.check_output([hg, "-R", directory, "log", "-r", ".", "-T", "{node}"], text=True).strip()
        require(node == lock[name]["revision"], f"{name} checkout pin differs")
        require(not subprocess.check_output([hg, "-R", directory, "status", "-mard"], text=True).strip(),
                f"{name} checkout is not clean")
    command = ["git", "apply", "--check", *series()]
    subprocess.run(command, cwd=source, check=True, capture_output=True, text=True)
    return "PASS(verified clean pinned checkout)"

def validate():
    paths = series()
    authority = load("contracts/visual/authority.json")
    validate_pins(authority)
    expected_0002 = authority["implementation_evidence"][0]
    require(paths[0].name == Path(expected_0002["path"]).name and
            hashlib.sha256(paths[0].read_bytes()).hexdigest() == expected_0002["sha256"],
            "Phase 0 patch identity differs")
    validate_packages(added_files(paths[1]))

def main():
    try:
        validate()
        status = applicability()
    except (PackageError, KeyError, OSError, subprocess.SubprocessError) as error:
        print(f"Phase 1A visual package validation failed: {error}", file=sys.stderr)
        return 1
    print("Phase 1A visual packages valid: authority registry, causal imports, roots, hook, pins, and patch order passed.")
    print(f"patch applicability: {status}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
