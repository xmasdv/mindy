#!/usr/bin/env python3
"""Validate the inert Phase 1 package and upstream-drift boundary."""
import importlib.util, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "contracts" / "visual" / "package-isolation.json"
EXPECTED_LAYERS = ["contracts", "adapters", "ui", "theme", "brand", "test"]
EXPECTED_TARGETS = {
    "comm/mail/moz.build", "comm/mail/app/profile/all-thunderbird.js",
    "comm/mail/base/content/about3Pane.js", "comm/mindy/moz.build",
    "comm/mindy/contracts/SurfaceRegistry.sys.mjs",
    "comm/mindy/adapters/FeatureSwitch.sys.mjs",
    "comm/mindy/ui/VisualBootstrap.sys.mjs", "comm/mindy/theme/package.json",
    "comm/mindy/brand/package.json", "comm/mindy/test/moz.build",
    "comm/mindy/test/xpcshell.ini", "comm/mindy/test/test_visual_bootstrap.js",
}
FORBIDDEN = re.compile(r"#[0-9a-f]{3,8}\b|\brgba?\(|\b\d+(?:px|rem|em)\b|local.?ai|mindy.*(?:identity|installer)", re.I)

class PackageError(ValueError):
    pass

def require(condition, message):
    if not condition:
        raise PackageError(message)

def load(path=CONTRACT_PATH):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def added_targets(patch):
    return set(re.findall(r"^\+\+\+ b/(.+)$", patch, re.MULTILINE))

def added_content(patch):
    return "\n".join(line[1:] for line in patch.splitlines() if line.startswith("+") and not line.startswith("+++"))

def validate(contract=None, patch=None):
    contract = load() if contract is None else contract
    patch_path = ROOT / contract["upstream"]["patch"]
    patch = patch_path.read_text(encoding="utf-8") if patch is None else patch
    require(contract.get("phase") == 1, "contract must describe Phase 1")
    layers = contract.get("layers", [])
    names = [layer.get("name") for layer in layers]
    require(names == EXPECTED_LAYERS, "package layer order differs")
    for index, layer in enumerate(layers):
        require(layer.get("path") == f"comm/mindy/{layer['name']}/", f"package path differs: {layer['name']}")
        allowed = set(names[:index]) if layer["name"] != "test" else set(names[:-1])
        require(set(layer.get("dependencies", [])) <= allowed, f"reverse dependency: {layer['name']}")
    registry = contract.get("surface_registry", {})
    require(registry == {"authority": "contracts/visual/surface-registry.schema.json", "claims": []}, "Phase 1 registry must load authority without claims")
    schema = json.loads((ROOT / registry["authority"]).read_text(encoding="utf-8"))
    require(schema.get("x-validator") == "tools/validate-visual-contracts.py", "registry authority is not Phase 0")
    hook, switch = contract.get("hook", {}), contract.get("feature_switch", {})
    require(hook.get("id") == "about3Pane" and hook.get("host") == "comm/mail/base/content/about3Pane.js", "hook is unregistered")
    require(switch == {"preference": "mindy.visual.enabled", "default": False, "off": "inherited", "on": "registry-only"}, "feature switch contract differs")
    require(added_targets(patch) == EXPECTED_TARGETS, "patch target drift or unapproved path")
    added = added_content(patch)
    require(not FORBIDDEN.search(added), "visual, identity, installer, or local-AI literal found")
    host_patch = re.search(r"diff --git a/comm/mail/base/content/about3Pane.js.+?(?=diff --git|\Z)", patch, re.S)
    require(host_patch and host_patch.group().count('initializeMindyVisual("about3Pane")') == 1, "hook registration differs")
    require(added.count('pref("mindy.visual.enabled", false);') == 1, "feature switch must default off")
    require('getBoolPref(PREF, false)' in added and 'mode: "inherited"' in added and 'mode: "registry-only"' in added, "feature switch behavior differs")
    require("claims: Object.freeze([])" in added and "SURFACE_REGISTRY_AUTHORITY" in added, "empty authority-backed registry differs")
    require("Services." not in re.search(r"diff --git a/comm/mindy/ui/.+?(?=diff --git|\Z)", patch, re.S).group(), "UI accesses Thunderbird globals")
    series = [line.split("#", 1)[0].strip() for line in (ROOT / "patches" / "series").read_text().splitlines() if line.split("#", 1)[0].strip()]
    require(series[-1] == patch_path.name and series.count(patch_path.name) == 1, "Phase 1 patch registration differs")
    bootstrap = (ROOT / "tools" / "bootstrap-upstream.py").read_text(encoding="utf-8")
    require('"apply", "--directory=vendor/gecko", "--check"' in bootstrap, "strict patch applicability gate missing")
    authority = json.loads((ROOT / "contracts" / "visual" / "authority.json").read_text())
    pins = json.loads((ROOT / contract["upstream"]["pins"]).read_text())
    behavior = authority["behavior_authority"]
    require((pins["gecko"]["revision"], pins["comm"]["revision"]) == (behavior["gecko_revision"], behavior["comm_revision"]), "source pins drifted from Phase 0")

def main():
    try:
        spec = importlib.util.spec_from_file_location("phase0", ROOT / "tools" / "validate-visual-contracts.py")
        phase0 = importlib.util.module_from_spec(spec); spec.loader.exec_module(phase0); phase0.validate()
        validate()
    except (PackageError, KeyError, TypeError, json.JSONDecodeError, OSError, ValueError) as error:
        print(f"Phase 1 visual package validation failed: {error}")
        return 1
    print("Phase 1 visual packages valid: authority, layers, hooks, switch, pins, patch gate, and inert registry passed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
