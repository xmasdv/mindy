#!/usr/bin/env python3
"""Generate and validate the authority-backed Phase 1A package patch."""

import hashlib, json, os, re, subprocess, sys, tempfile, zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SERIES = ("0002-mindy-mail-shell.patch", "0003-mindy-visual-packages.patch")
PACKAGE_PATCH = EXPECTED_SERIES[1]
ROOTS = ("contracts", "adapters", "ui", "theme", "brand", "test")
REQUIRED_EDGES = {("adapters", "contracts"), ("ui", "adapters"),
                  ("ui", "theme"), ("ui", "brand"), ("test", "ui")}
ALLOWED = {"comm/mail/moz.build", "comm/mail/mindy/moz.build",
           *{f"comm/mail/mindy/{root}/{name}" for root, names in {
               "contracts": ("moz.build", "VisualRegistry.sys.mjs"),
               "adapters": ("moz.build", "VisualAuthorityAdapter.sys.mjs"),
               "theme": ("moz.build", "ThemeOwnership.sys.mjs"),
               "brand": ("moz.build", "BrandOwnership.sys.mjs"),
               "ui": ("moz.build", "VisualPackage.sys.mjs"),
               "test": ("moz.build", "xpcshell.toml", "test_visual_package.js")}.items() for name in names}}
RESOURCE = re.compile(r'["\']resource:///modules/mindy/([^/]+)/[^"\']+["\']')
IMPORT = re.compile(r'(?:from\s+|import\s*(?:\(\s*)?|ChromeUtils\.importESModule\(\s*)["\']resource:///modules/mindy/([^/]+)/')
GLOBALS = re.compile(r"\b(?:ChromeUtils|Services|MailServices|Cc|Ci|Cr)\b")
VISUAL = re.compile(r"#[0-9a-f]{3,8}\b|\brgba?\(|\b(?:color|background|font|margin|padding)\s*:", re.I)

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

def contained_target(raw, root=ROOT):
    relative = safe_relative(raw)
    cursor = Path(root).resolve()
    for part in relative.parts:
        cursor /= part
        require(not cursor.is_symlink() and
                not getattr(os.path, "isjunction", lambda _: False)(cursor),
                f"linked path rejected: {raw}")
    resolved = cursor.resolve(strict=False)
    require(Path(root).resolve() in (resolved, *resolved.parents), f"resolved path escapes repository: {raw}")
    return cursor

def safe_path(raw, root=ROOT):
    return contained_target(raw, root).resolve(strict=True)

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
    body = json.dumps(payload, separators=(",", ":"))[:-1]
    return f'export const VisualRegistry = Object.freeze({body},"surfaceIds":Object.freeze({json.dumps(ids, separators=(",", ":"))})}});'

def header_path(raw, prefix):
    if raw == "/dev/null":
        return None
    require(raw.startswith(prefix), f"patch header prefix differs: {raw}")
    return safe_relative(raw[2:]).as_posix()

def added_files(patch=None):
    text = (patch or safe_path(f"patches/{PACKAGE_PATCH}")).read_text(encoding="utf-8")
    files, deleted = {}, set()
    for block in re.split(r"(?=^diff --git )", text, flags=re.M)[1:]:
        lines = block.splitlines()
        match = re.fullmatch(r"diff --git a/(\S+) b/(\S+)", lines[0])
        require(match is not None, "malformed diff header")
        left, right = (safe_relative(item).as_posix() for item in match.groups())
        require(left == right, "diff paths differ")
        old_headers, new_headers = ([line[4:] for line in lines if line.startswith(prefix)]
                                    for prefix in ("--- ", "+++ "))
        require(len(old_headers) == len(new_headers) == 1, "patch file headers differ")
        old, new = header_path(old_headers[0], "a/"), header_path(new_headers[0], "b/")
        require((old is None or old == left) and (new is None or new == right), "effective patch paths differ")
        added, removed = old is None, new is None
        require(not (added and removed) and added == ("new file mode 100644" in lines)
                and removed == ("deleted file mode 100644" in lines), "invalid add/delete headers")
        target = left if removed else right
        require(target.startswith("comm/mail/") and target not in files, f"invalid/duplicate patch target: {target}")
        collecting = False; content = []
        for line in lines:
            collecting = collecting or line.startswith("@@")
            if collecting and line.startswith("+") and not line.startswith("+++"):
                content.append(line[1:])
        files[target] = "\n".join(content)
        if removed:
            deleted.add(target)
    require(set(files) == ALLOWED and not deleted, "Phase 1A patch target scope differs")
    return files

def layer(path):
    parts = PurePosixPath(path).parts; return "test" if "test" in parts else parts[3]

def validate_packages(files):
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
        imports, references = IMPORT.findall(text), RESOURCE.findall(text)
        require(imports == references and all(target in ROOTS for target in imports),
                f"unclassified Mindy resource reference: {path}")
        edges.update((source, target) for target in imports)
        if source == "ui":
            require(not GLOBALS.search(text), "owned UI imports Thunderbird globals")
    require(edges == REQUIRED_EDGES, f"package import edges differ: {sorted(edges)}")
    require('XPCSHELL_TESTS_MANIFESTS += ["xpcshell.toml"]' in
            files.get("comm/mail/mindy/test/moz.build", ""), "test root is unregistered")
    registry = files.get("comm/mail/mindy/contracts/VisualRegistry.sys.mjs", "")
    require(registry == generated_registry(), "runtime registry drift/duplication detected")
    require(not VISUAL.search("\n".join(files.values())), "Phase 2 visual value/file detected")

def validate_pins(authority=None, sources=None):
    authority = authority or load("contracts/visual/authority.json")
    sources = sources or load("sources.lock")
    behavior = authority["behavior_authority"]
    require((sources["gecko"]["revision"], sources["comm"]["revision"]) ==
            (behavior["gecko_revision"], behavior["comm_revision"]), "source pins differ")

def applicability():
    manifest = load("tools/tests/fixtures/0002-comm-preimage.json")
    lock = load("sources.lock")["comm"]
    require((manifest["repository"], manifest["revision"]) ==
            (lock["repository"], lock["revision"]), "fixture source pin differs")
    archive = safe_path(f'tools/tests/fixtures/{manifest["archive"]}')
    require(hashlib.sha256(archive.read_bytes()).hexdigest() == manifest["archive_sha256"],
            "fixture archive hash differs")
    with tempfile.TemporaryDirectory() as temporary, zipfile.ZipFile(archive) as bundle:
        source = Path(temporary); expected = [item["path"] for item in manifest["files"]]
        require(bundle.namelist() == expected, "fixture archive members differ")
        for item in manifest["files"]:
            data = bundle.read(item["path"])
            require((len(data), hashlib.sha256(data).hexdigest()) ==
                    (item["size"], item["sha256"]), f'fixture file differs: {item["path"]}')
            target = contained_target(item["path"], source)
            target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(data)
        for target in ALLOWED:
            contained_target(target, source)
        result = subprocess.run(["git", "apply", "--check", *series()], cwd=source,
                                capture_output=True, text=True)
        require(result.returncode == 0, f"ordered fixture applicability failed: {result.stderr.strip()}")
    return "PASS(exact pinned fixture, ordered 0002+0003)"

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
