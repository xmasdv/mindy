#!/usr/bin/env python3
"""Validate the authority-backed Phase 1A/1B package and host patches."""

import hashlib, json, os, re, subprocess, sys, tempfile, zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SERIES = ("0002-mindy-mail-shell.patch", "0003-mindy-visual-packages.patch", "0004-mindy-visual-host-switch.patch")
PACKAGE_PATCH = EXPECTED_SERIES[1]
HOST_PATCH = EXPECTED_SERIES[2]
HOST_PATCH_SHA256 = "f88943bb920397924462c68646e92de511605e65bf6e7c8c1aa774530bf29256"
REQUIRED_EDGES = {("adapters", "contracts"), ("ui", "adapters"),
                  ("ui", "theme"), ("ui", "brand"), ("test", "ui")}
ALLOWED = {"comm/mail/moz.build", "comm/mail/mindy/moz.build",
           *{f"comm/mail/mindy/{root}/{name}" for root, names in {
               "contracts": ("moz.build", "VisualRegistry.sys.mjs"), "adapters": ("moz.build", "VisualAuthorityAdapter.sys.mjs"),
               "theme": ("moz.build", "ThemeOwnership.sys.mjs"), "brand": ("moz.build", "BrandOwnership.sys.mjs"),
               "ui": ("moz.build", "VisualPackage.sys.mjs"),
               "test": ("moz.build", "xpcshell.toml", "test_visual_package.js")}.items() for name in names}}
HOST_ALLOWED = {"comm/mail/base/content/about3Pane.xhtml", "comm/mail/base/content/about3Pane.js",
                "comm/mail/mindy/moz.build", "comm/mail/mindy/mindy.js",
                "comm/mail/mindy/contracts/moz.build", "comm/mail/mindy/contracts/VisualHost.sys.mjs",
                "comm/mail/test/browser/folder-display/browser.toml",
                "comm/mail/test/browser/folder-display/browser_mindyVisualHost.js"}
RAW_RESOURCE = "resource:///modules/mindy/"
STATIC_IMPORT = re.compile(r'import\s*\{\s*\w+\s*\}\s*from\s*"(resource:///modules/mindy/[^"\s]+)"\s*;')
TEST_IMPORT = re.compile(r'ChromeUtils\.importESModule\(\s*"resource:///modules/mindy/ui/VisualPackage\.sys\.mjs"\s*\)')
TOKEN = re.compile(r'"[^"\n]*"|[A-Za-z_$][\w$]*|\d+|[+{}()[\],.:;=]')
# Phase 1A grammar: exact manifests and frozen metadata exports; comments/whitespace are insignificant.
GRAMMAR = {
    "comm/mail/mindy/adapters/VisualAuthorityAdapter.sys.mjs": 'import { VisualRegistry } from "resource:///modules/mindy/contracts/VisualRegistry.sys.mjs"; export const VisualAuthority = Object.freeze({ registry: VisualRegistry, });',
    "comm/mail/mindy/theme/ThemeOwnership.sys.mjs": 'export const ThemeOwnership = Object.freeze({ layer: "theme", visualValues: false });',
    "comm/mail/mindy/brand/BrandOwnership.sys.mjs": 'export const BrandOwnership = Object.freeze({ layer: "brand", visualAssets: false });',
    "comm/mail/mindy/ui/VisualPackage.sys.mjs": 'import { VisualAuthority } from "resource:///modules/mindy/adapters/VisualAuthorityAdapter.sys.mjs"; import { BrandOwnership } from "resource:///modules/mindy/brand/BrandOwnership.sys.mjs"; import { ThemeOwnership } from "resource:///modules/mindy/theme/ThemeOwnership.sys.mjs"; export const VisualPackage = Object.freeze({ authority: VisualAuthority, brand: BrandOwnership, theme: ThemeOwnership, });',
    "comm/mail/moz.build": '"mindy",', "comm/mail/mindy/moz.build": 'DIRS += ["contracts", "adapters", "theme", "brand", "ui"] TEST_DIRS += ["test"]',
    **{f"comm/mail/mindy/{root}/moz.build": f'EXTRA_JS_MODULES.mindy.{root} += ["{name}"]' for root, name in {
        "contracts": "VisualRegistry.sys.mjs", "adapters": "VisualAuthorityAdapter.sys.mjs", "theme": "ThemeOwnership.sys.mjs",
        "brand": "BrandOwnership.sys.mjs", "ui": "VisualPackage.sys.mjs"}.items()},
    "comm/mail/mindy/test/moz.build": 'XPCSHELL_TESTS_MANIFESTS += ["xpcshell.toml"]',
    "comm/mail/mindy/test/xpcshell.toml": '[DEFAULT] ["test_visual_package.js"]',
}

class PackageError(ValueError):
    pass

def require(condition, message):
    if not condition:
        raise PackageError(message)

def safe_relative(raw):
    require(isinstance(raw, str) and raw, "path must be non-empty")
    relative = PurePosixPath(raw)
    require("\\" not in raw and not Path(raw).is_absolute() and not Path(raw).drive and
            not relative.is_absolute() and not relative.drive and ".." not in relative.parts,
            f"unsafe path: {raw}")
    return relative

def contained_target(raw, root=ROOT):
    relative = safe_relative(raw)
    cursor = Path(root).resolve()
    for part in relative.parts:
        cursor /= part
        require(not cursor.is_symlink() and not getattr(os.path, "isjunction", lambda _: False)(cursor), f"linked path rejected: {raw}")
    resolved = cursor.resolve(strict=False)
    require(Path(root).resolve() in (resolved, *resolved.parents), f"resolved path escapes repository: {raw}")
    return cursor

def safe_path(raw, root=ROOT): return contained_target(raw, root).resolve(strict=True)

def load(raw): return json.loads(safe_path(raw).read_text(encoding="utf-8"))

def series():
    names = tuple(line.split("#", 1)[0].strip() for line in
                  safe_path("patches/series").read_text().splitlines()
                  if line.split("#", 1)[0].strip())
    require(names == EXPECTED_SERIES, "patch series identity/order differs")
    return [safe_path(f"patches/{name}") for name in names]

def generated_registry():
    authority = load("contracts/visual/authority.json")
    families = load(authority["surface_inventory"]["schema_path"])["x-exact-families"]
    ids = [item for family in families.values() for item in family]
    require(len(ids) == len(set(ids)) == authority["surface_inventory"]["total"] == 80,
            "authority registry IDs differ")
    payload = {"authoritySha256": hashlib.sha256(
        safe_path("contracts/visual/authority.json").read_bytes()).hexdigest(),
        "schemaVersion": authority["schema_version"], "phase": authority["phase"]}
    body = json.dumps(payload, separators=(",", ":"))[:-1]
    return f'export const VisualRegistry = Object.freeze({body},"surfaceIds":Object.freeze({json.dumps(ids, separators=(",", ":"))})}});'

def module_tokens(text):
    code = re.sub(r"(?m)(^|\s)//.*$", r"\1", re.sub(r"/\*.*?\*/", " ", text, flags=re.S))
    tokens = TOKEN.findall(code)
    require("".join(tokens) == re.sub(r"\s+", "", code), "metadata module grammar rejected syntax")
    return tokens, code

def header_path(raw, prefix):
    require(raw == "/dev/null" or raw.startswith(prefix), f"patch header prefix differs: {raw}")
    return None if raw == "/dev/null" else safe_relative(raw[2:]).as_posix()

def added_files(patch=None, allowed=ALLOWED, with_removed=False):
    text = (patch or safe_path(f"patches/{PACKAGE_PATCH}")).read_text(encoding="utf-8")
    files, removed_content, deleted = {}, {}, set()
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
        collecting = False; content = []; removed_lines = []
        for line in lines:
            collecting = collecting or line.startswith("@@")
            if collecting and line.startswith("+") and not line.startswith("+++"):
                content.append(line[1:])
            if collecting and line.startswith("-") and not line.startswith("---"):
                removed_lines.append(line[1:])
        files[target] = "\n".join(content)
        removed_content[target] = "\n".join(removed_lines)
        if removed:
            deleted.add(target)
    require(set(files) == allowed and not deleted, "patch target scope differs")
    return (files, removed_content) if with_removed else files

def validate_packages(files):
    for path, expected in GRAMMAR.items():
        require(path in files and module_tokens(files[path])[0] == module_tokens(expected)[0], f"manifest/module grammar differs: {path}")
    modules = {path: text for path, text in files.items() if path.endswith((".mjs", ".js"))}
    edges = set()
    for path, text in modules.items():
        parts = PurePosixPath(path).parts; source = "test" if "test" in parts else parts[3]
        if source == "test":
            require(text.count(RAW_RESOURCE) == 1 and TEST_IMPORT.search(text),
                    "unclassified Mindy test resource")
            edges.add(("test", "ui")); continue
        actual, code = module_tokens(text)
        if source == "contracts":
            require(actual == module_tokens(generated_registry())[0], f"metadata module grammar differs: {path}")
        imports = STATIC_IMPORT.findall(code)
        require(text.count(RAW_RESOURCE) == len(imports), f"unclassified Mindy resource: {path}")
        edges.update((source, url.removeprefix(RAW_RESOURCE).split("/", 1)[0]) for url in imports)
    require(edges == REQUIRED_EDGES, f"package import edges differ: {sorted(edges)}")

def validate_host(patch=None, execute=True):
    files, removed = added_files(patch or safe_path(f"patches/{HOST_PATCH}"), HOST_ALLOWED, True)
    require(files["comm/mail/mindy/mindy.js"].strip() == 'pref("mindy.visual.enabled", false);', "host pref default differs")
    require(files["comm/mail/mindy/moz.build"].strip() == 'JS_PREFERENCE_FILES += ["mindy.js"]', "host pref registration differs")
    require(files["comm/mail/mindy/contracts/moz.build"].strip() ==
            'EXTRA_JS_MODULES.mindy.contracts += ["VisualHost.sys.mjs", "VisualRegistry.sys.mjs"]', "host module registration differs")
    host = files["comm/mail/base/content/about3Pane.js"]
    require(all(item in host for item in ('getBoolPref("mindy.visual.enabled", false)', 'initialize(window, "about3Pane"',
                                         'contracts/VisualHost.sys.mjs', 'reject(window, "startup-error")',
                                         '} finally {', 'mindyVisualHost?.cleanup(window)')) and
            host.count("hasDOMContentLoaded.resolve()") == 1,
            "host startup/cleanup wiring differs")
    require("data-mindy-shell" in removed["comm/mail/base/content/about3Pane.xhtml"] and
            "mindyMail.css" in removed["comm/mail/base/content/about3Pane.xhtml"] and
            "mindy" not in files["comm/mail/base/content/about3Pane.xhtml"], "inherited host restoration differs")
    module = files["comm/mail/mindy/contracts/VisualHost.sys.mjs"]
    require(not re.search(r"\b(?:Services|ChromeUtils|window|document)\b", module), "direct globals rejected")
    require(all(item in module for item in ('import { VisualRegistry }', 'registry === VisualRegistry', 'new Set(ids).size == 80',
                                           'registry.authoritySha256 == VisualRegistry.authoritySha256', 'inherited: status != "active"',
                                           'registry.schemaVersion == VisualRegistry.schemaVersion', 'registry.phase == VisualRegistry.phase',
                                           '"unknown-hook"', 'surfaceClaim: false', 'states.delete(host)')) and
            "surfaceClaim: true" not in module,
            "host diagnostic contract differs")
    browser = files["comm/mail/test/browser/folder-display/browser_mindyVisualHost.js"]
    require(all(item in browser for item in ("openHost(false)", "openHost(true)", "registryCount, 80", "unknown-hook", "windowClosed")),
            "browser smoke contract differs")
    require("browser_mindyVisualHost.js" in files["comm/mail/test/browser/folder-display/browser.toml"] and
            "browser_mindyMailShell.js" in removed["comm/mail/test/browser/folder-display/browser.toml"],
            "browser smoke registration differs")
    require(not any(path.endswith((".css", ".svg", ".png")) for path in files) and
            not re.search(r"#[0-9a-fA-F]{3,8}|\b\d+(?:px|rem|ms)\b", "\n".join(files.values())),
            "visual files/values rejected")
    if execute:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); registry_source = root / "VisualRegistry.mjs"; source = root / "VisualHost.mjs"
            registry_source.write_text(generated_registry(), encoding="utf-8")
            source.write_text(module.replace("resource:///modules/mindy/contracts/VisualRegistry.sys.mjs", "./VisualRegistry.mjs"), encoding="utf-8")
            startup = re.search(r'  try \{\n.*?  \} finally \{\n    hasDOMContentLoaded\.resolve\(\);\n  \}', host, re.S)
            require(startup is not None, "host executable startup block missing")
            runner = root / "HostStartup.mjs"
            runner.write_text(f'''export async function run(Services,ChromeUtils,window,console,hasDOMContentLoaded){{
let mindyVisualHost;\n{startup.group()}\nreturn mindyVisualHost;\n}}''', encoding="utf-8")
            script = f'''import {{ VisualHost }} from "{source.as_uri()}";
import {{ VisualRegistry }} from "{registry_source.as_uri()}";
import {{ run }} from "{runner.as_uri()}";
const pkg={{VisualPackage:{{authority:{{registry:VisualRegistry}}}}}};
async function start(pref=false,fail="",visualHost=VisualHost){{
 const window={{}}, resolved={{count:0}};
 const Services={{prefs:{{getBoolPref(){{if(pref==="throw")throw Error("pref");return pref;}}}}}};
 const ChromeUtils={{importESModule(url){{if(fail&&url.includes(fail))throw Error("missing");return url.includes("VisualHost")?{{VisualHost:visualHost}}:pkg;}}}};
 await run(Services,ChromeUtils,window,{{error(){{}}}},{{resolve(){{resolved.count++;}}}});
 if(resolved.count!==1)throw Error("resolve");return window;
}}
await start();for(const failure of ["pref","VisualHost","VisualPackage"])await start(failure==="pref"?"throw":true,failure);
const activeHost=await start(true);const active=VisualHost.inspect(activeHost);
if(active.status!=="active"||active.registryCount!==80||active.surfaceClaim)throw Error("on");
const throwing={{initialize(){{throw Error("init");}},reject(){{throw Error("diagnostic");}}}};await start(true,"",throwing);
const ids=[...VisualRegistry.surfaceIds];for(const registry of [
 {{...VisualRegistry,surfaceIds:Array(80).fill(ids[0])}},{{...VisualRegistry,authoritySha256:"wrong"}},
 {{...VisualRegistry,surfaceIds:ids.toReversed()}},{{...VisualRegistry,surfaceIds:ids.slice(1)}}]){{
 const state=VisualHost.initialize({{}},"about3Pane",registry);if(!state.inherited||state.status!=="rejected"||state.code!=="invalid-registry")throw Error("registry");
}}
if(VisualHost.initialize({{}},"unknown",VisualRegistry).code!=="unknown-hook")throw Error("unknown");
VisualHost.cleanup(activeHost);if(VisualHost.inspect(activeHost).status!=="disabled")throw Error("cleanup");'''
            result = subprocess.run(["node", "--input-type=module", "--eval", script], capture_output=True, text=True)
            require(result.returncode == 0, f"host executable contract failed: {result.stderr.strip()}")

def validate_pins(authority=None, sources=None):
    authority, sources = authority or load("contracts/visual/authority.json"), sources or load("sources.lock")
    behavior = authority["behavior_authority"]
    require((sources["gecko"]["revision"], sources["comm"]["revision"]) ==
            (behavior["gecko_revision"], behavior["comm_revision"]), "source pins differ")

def applicability():
    manifest = load("tools/tests/fixtures/0002-comm-preimage.json")
    require((manifest["repository"], manifest["revision"]) ==
            tuple(load("sources.lock")["comm"][key] for key in ("repository", "revision")), "fixture source pin differs")
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
        host_manifest = load("tools/tests/fixtures/0004-about3Pane-preimage.json")
        require((host_manifest["repository"], host_manifest["revision"]) ==
                tuple(load("sources.lock")["comm"][key] for key in ("repository", "revision")), "host preimage pin differs")
        require((host_manifest["kind"], host_manifest["source_path"], host_manifest["target_path"]) ==
                ("minimal_hunk_preimage", "mail/base/content/about3Pane.js", "comm/mail/base/content/about3Pane.js"), "host preimage scope differs")
        host_preimage = safe_path(f'tools/tests/fixtures/{host_manifest["fixture"]}')
        require(hashlib.sha256(host_preimage.read_bytes()).hexdigest() == host_manifest["sha256"], "host preimage differs")
        host_target = contained_target(host_manifest["target_path"], source)
        host_target.parent.mkdir(parents=True, exist_ok=True); host_target.write_bytes(host_preimage.read_bytes())
        for target in ALLOWED:
            contained_target(target, source)
        paths = series()
        for reverse, selected in ((False, paths), (True, reversed(paths)), (False, paths)):
            for path in selected:
                command = ["git", "apply", *(["--reverse"] if reverse else []), str(path)]
                result = subprocess.run(command, cwd=source, capture_output=True, text=True)
                require(result.returncode == 0, f"ordered fixture apply/reverse/reapply failed: {result.stderr.strip()}")
    return "PASS(exact pinned fixture, ordered 0002+0003+0004)"

def validate():
    paths, authority = series(), load("contracts/visual/authority.json")
    validate_pins(authority)
    expected_0002 = authority["implementation_evidence"][0]
    require(paths[0].name == Path(expected_0002["path"]).name and
            hashlib.sha256(paths[0].read_bytes()).hexdigest() == expected_0002["sha256"],
            "Phase 0 patch identity differs")
    validate_packages(added_files(paths[1]))
    require(hashlib.sha256(paths[2].read_bytes()).hexdigest() == HOST_PATCH_SHA256,
            "Phase 1B patch identity differs")
    validate_host(paths[2])

def main():
    try:
        validate()
        status = applicability()
    except (PackageError, KeyError, OSError, subprocess.SubprocessError) as error:
        print(f"Phase 1A/1B visual package validation failed: {error}", file=sys.stderr)
        return 1
    print("Phase 1A/1B visual packages valid: authority registry, default-off host, cleanup, pins, and patch order passed.")
    print(f"patch applicability: {status}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
