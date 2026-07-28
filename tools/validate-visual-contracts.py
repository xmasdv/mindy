#!/usr/bin/env python3
"""Validate the exact Phase 0 contract subset; this is not a JSON Schema engine."""
from collections import Counter
import hashlib, json, os, re, struct, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts" / "visual"
HASH, REVISION = re.compile(r"^[a-f0-9]{64}$"), re.compile(r"^[a-f0-9]{40}$")
REQUIRED_VISUAL = {"DESIGN.md", "docs/VISUAL-AUDIT.md", "docs/VISUAL-OWNERSHIP.md", "docs/VISUAL-RECONSTRUCTION-PLAN.md", "assets/design-concepts/mindy-inbox-mockup-v2-navy-teal.png", "assets/brand-production/mindy-mark.svg"}
OWNER_RULES = {"mindy": ["owned", "adapter"], "thunderbird": ["adapter"], "shared": ["adapter"], "native": ["inherited-native"], "provider": ["inherited-external"]}

class ContractError(ValueError):
    pass

def require(condition, message):
    if not condition:
        raise ContractError(message)

def safe_path(raw):
    require(isinstance(raw, str) and raw, "path must be non-empty")
    relative = Path(raw)
    require(not relative.is_absolute() and not relative.drive and ".." not in relative.parts, f"unsafe path: {raw}")
    cursor = ROOT
    for part in relative.parts:
        cursor /= part
        require(not cursor.is_symlink() and not getattr(os.path, "isjunction", lambda _: False)(cursor), f"linked path rejected: {raw}")
    resolved = cursor.resolve(strict=True)
    require(resolved == ROOT or ROOT in resolved.parents, f"resolved path escapes repository: {raw}")
    return resolved

def load(raw):
    with safe_path(raw).open(encoding="utf-8") as stream:
        return json.load(stream)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def validate_registry(schema, counts, instance=None):
    families = schema["x-exact-families"]
    require(set(families) == set(counts), "registry families differ from authority")
    exact = []
    for family, count in counts.items():
        expected = [f"{family}-{number:02}" for number in range(1, count + 1)]
        require(families[family] == expected, f"registry sequence differs for {family}")
        exact.extend(expected)
    require(len(exact) == len(set(exact)) == 80, "registry must contain 80 unique IDs")
    require(schema["x-valid-owner-boundaries"] == OWNER_RULES, "registry owner/boundary rules differ")
    if instance is None:
        return exact
    surfaces = instance.get("surfaces")
    require(isinstance(surfaces, list) and len(surfaces) == 80, "registry instance requires 80 surfaces")
    require([item.get("id") for item in surfaces] == exact, "registry instance IDs must match the exact ordered set")
    for item in surfaces:
        owner, boundary, adapter = item.get("owner"), item.get("boundary"), item.get("adapter_contract")
        require(owner in OWNER_RULES and boundary in OWNER_RULES[owner], f"invalid owner/boundary for {item.get('id')}")
        require((boundary == "adapter") == (isinstance(adapter, str) and bool(adapter)), f"invalid adapter binding for {item.get('id')}")
    return exact

def rejected_references(manifest):
    return ({item["path"] for item in manifest["records"]}, {item["sha256"] for item in manifest["records"]})

def validate_manifest(manifest, check_files=True):
    required = {"schema_version", "classification", "baseline_status", "source_revisions", "patch_series_sha256", "artifact_sha256", "fixture", "environment", "captured_at", "capture_actor", "review_actor", "records"}
    require(required <= manifest.keys(), "manifest provenance is incomplete")
    revisions = manifest["source_revisions"]
    require({"gecko", "comm"} <= revisions.keys() and all(REVISION.fullmatch(revisions[key]) for key in ("gecko", "comm")), "source revisions are incomplete")
    environment = manifest["environment"]
    environment_keys = ("os", "scale", "app_zoom", "theme", "locale", "direction")
    require(all(str(environment.get(key, "")).strip() for key in environment_keys), "environment provenance is incomplete")
    require(all(str(manifest[key]).strip() for key in ("fixture", "captured_at", "capture_actor")), "capture provenance is incomplete")
    records = manifest["records"]
    require(isinstance(records, list) and records, "manifest records must not be empty")
    require(len({item.get("name") for item in records}) == len(records), "manifest record names must be unique")
    for item in records:
        require(all(str(item.get(key, "")).strip() for key in ("name", "path", "sha256", "state", "dimensions")) and HASH.fullmatch(item["sha256"]), "malformed manifest record")
        path = safe_path(item["path"])
        if check_files:
            require(digest(path) == item["sha256"], f"evidence hash mismatch: {item['path']}")
            if path.suffix.lower() == ".png":
                width, height = struct.unpack(">II", path.read_bytes()[16:24])
                require(item["dimensions"] == f"{width}x{height}", f"evidence dimensions differ: {item['path']}")
    classification = manifest["classification"]
    statuses = {"candidate_runtime_evidence": "pending-independent-approval", "accepted_baseline": "accepted", "rejected_historical_evidence": "rejected"}
    require(statuses.get(classification) == manifest["baseline_status"], "classification and baseline status differ")
    if classification in ("candidate_runtime_evidence", "accepted_baseline"):
        require(HASH.fullmatch(manifest["patch_series_sha256"] or "") and HASH.fullmatch(manifest["artifact_sha256"] or ""), "candidate hashes are incomplete")
        require(not any(str(value).startswith("unknown") for value in environment.values()), "candidate environment contains unknown provenance")
    if classification == "accepted_baseline":
        require(str(manifest["review_actor"] or "").strip() and manifest["review_actor"] != manifest["capture_actor"], "accepted baseline requires independent actors")
        paths, hashes = rejected_references(load("contracts/visual/rejected-evidence.json"))
        require(not any(item["path"] in paths or item["sha256"] in hashes for item in records), "rejected evidence cannot be promoted or reused")
    if classification == "rejected_historical_evidence":
        require(manifest.get("redacted") is True and str(manifest.get("reason", "")).strip() and manifest["review_actor"] is None, "rejected evidence classification is incomplete")

def validate_adapter(template):
    version, compatibility = template.get("contract_version"), template.get("compatibility", {})
    require(compatibility.get("minimum_upstream_contract") <= version <= compatibility.get("maximum_upstream_contract"), "adapter versioning is incomplete")
    state = template.get("normalized_state", {})
    require(set(state.get("status", {}).get("enum", [])) == {"loading", "ready", "empty", "error", "unavailable"}, "adapter statuses are incomplete")
    require(state.get("data", {}).get("nullable") is True and set(state["data"]["null_when"]) == {"loading", "empty", "error", "unavailable"} and state.get("error", {}).get("nullable") is True, "adapter null/loading/error semantics are incomplete")
    shapes = {"inputs": {"name", "schema", "required", "nullable"}, "commands": {"name", "payload_schema", "result_schema", "enabled_when", "disabled_result", "errors"}, "events": {"name", "payload_schema", "delivery"}, "capabilities": {"name", "type", "absent_behavior"}, "fixtures": {"id", "seed", "initial_status", "expected_events", "real_credentials", "real_personal_data"}}
    for group, fields in shapes.items():
        entries = template.get(group)
        require(isinstance(entries, list) and entries and all(fields <= entry.keys() for entry in entries), f"adapter {group} shape is incomplete")
    require(all(item["enabled_when"] and item["disabled_result"] == "reject" for item in template["commands"]), "adapter command enablement is incomplete")
    require(all(not item["real_credentials"] and not item["real_personal_data"] for item in template["fixtures"]), "adapter fixtures must be synthetic")

def validate(authority=None, evidence=None):
    authority = load("contracts/visual/authority.json") if authority is None else authority
    sources = load("sources.lock")
    visual = authority["visual_authority"]
    require({item["path"] for item in visual} == REQUIRED_VISUAL, "visual authority paths differ from the required set")
    for item in visual + authority["implementation_evidence"]:
        require(digest(safe_path(item["path"])) == item["sha256"], f"authority hash mismatch: {item['path']}")
    implementation = authority["implementation_evidence"]
    require({item["path"] for item in implementation} == {"patches/0002-mindy-mail-shell.patch"} and not implementation[0]["authority"], "implementation evidence paths differ")
    behavior = authority["behavior_authority"]
    require(behavior["path"] == "sources.lock" and digest(safe_path(behavior["path"])) == behavior["sha256"], "behavior authority differs")
    require(sources["gecko"]["revision"] == behavior["gecko_revision"] and sources["comm"]["revision"] == behavior["comm_revision"], "source pins differ")
    inventory = authority["surface_inventory"]
    exact = validate_registry(load(inventory["schema_path"]), inventory["family_counts"])
    audit = re.findall(r"^\| ([A-Z]{2}-\d{2}) \|", safe_path(inventory["audit_path"]).read_text(encoding="utf-8"), re.MULTILINE)
    require(audit == exact and Counter(item[:2] for item in audit) == Counter(inventory["family_counts"]), "audit and exact registry differ")
    screenshot_schema = load("contracts/visual/screenshot-manifest.schema.json")
    require(screenshot_schema["properties"]["records"]["minItems"] == 1 and screenshot_schema["x-independent-actors"] and screenshot_schema["x-rejected-promotion"] is False, "screenshot schema invariants differ")
    rejected = authority["rejected_historical_evidence"]
    require(rejected == {"manifest": "contracts/visual/rejected-evidence.json", "classification": "rejected_historical_evidence", "approved_baseline": False}, "rejected evidence authority differs")
    validate_manifest(load(rejected["manifest"]))
    if evidence is not None:
        validate_manifest(evidence)
    validate_adapter(load("contracts/visual/adapter-contract.template.json"))
    unknown_path, unknown_anchor = authority["external_native_unknowns"]["log"].split("#", 1)
    policy = safe_path(unknown_path).read_text(encoding="utf-8")
    require(unknown_anchor == "provider-native-and-accessibility-unknowns" and "## Provider, native, and accessibility unknowns" in policy, "unknown-log link differs")
    authored = "\n".join(path.read_text(encoding="utf-8") for path in CONTRACTS.glob("*.json")) + policy
    require(not re.search(r"pixel[- ]perfect|(?:upstream|mozilla) updates? (?:are|is) harmless|all provider (?:flows|content) (?:is|are) (?:accepted|supported)", authored, re.IGNORECASE), "prohibited guarantee language found")

def main():
    try:
        validate()
    except (ContractError, KeyError, TypeError, json.JSONDecodeError, OSError) as error:
        print(f"Phase 0 visual contract validation failed: {error}")
        return 1
    print("Phase 0 visual contracts valid: explicit schema subset, safe paths, exact 80-ID registry, adapter shapes, authority, and rejected evidence passed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
