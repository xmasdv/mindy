#!/usr/bin/env python3
"""Validate Phase 0 visual authority contracts using only the standard library."""

from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts" / "visual"


def load(path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(condition, message, errors):
    if not condition:
        errors.append(message)


def main():
    errors = []
    json_paths = [
        CONTRACTS / "authority.json", CONTRACTS / "surface-registry.schema.json",
        CONTRACTS / "adapter-contract.template.json", CONTRACTS / "screenshot-manifest.schema.json",
        CONTRACTS / "rejected-evidence.json", ROOT / "sources.lock",
    ]
    documents = {}
    for path in json_paths:
        try:
            documents[path.name] = load(path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"cannot parse {path.relative_to(ROOT)}: {exc}")
    if errors:
        return report(errors)

    authority = documents["authority.json"]
    required_classes = {"visual_authority", "behavior_authority", "implementation_evidence", "rejected_historical_evidence", "external_native_unknowns"}
    check(required_classes <= authority.keys(), "authority manifest is missing an evidence class", errors)
    for record in authority["visual_authority"] + authority["implementation_evidence"]:
        path = ROOT / record["path"]
        check(path.is_file(), f"missing authoritative path: {record['path']}", errors)
        if path.is_file():
            check(digest(path) == record["sha256"], f"hash mismatch: {record['path']}", errors)
    behavior = authority["behavior_authority"]
    source_path = ROOT / behavior["path"]
    check(source_path.is_file() and digest(source_path) == behavior["sha256"], "sources.lock hash mismatch", errors)
    sources = documents["sources.lock"]
    check(sources["gecko"]["revision"] == behavior["gecko_revision"], "Gecko source pin mismatch", errors)
    check(sources["comm"]["revision"] == behavior["comm_revision"], "comm source pin mismatch", errors)

    inventory = authority["surface_inventory"]
    check((ROOT / inventory["schema_path"]).is_file(), "surface registry schema path is missing", errors)
    ids = re.findall(r"^\| ([A-Z]{2}-\d{2}) \|", (ROOT / inventory["audit_path"]).read_text(encoding="utf-8"), re.MULTILINE)
    counts = Counter(item.split("-")[0] for item in ids)
    check(len(ids) == inventory["total"] == 80, f"expected 80 audit IDs, found {len(ids)}", errors)
    check(len(ids) == len(set(ids)), "audit IDs are not unique", errors)
    check(dict(counts) == inventory["family_counts"], f"family counts differ: {dict(counts)}", errors)
    for family, count in inventory["family_counts"].items():
        actual = sorted(int(item[3:]) for item in ids if item.startswith(f"{family}-"))
        check(actual == list(range(1, count + 1)), f"{family} IDs are not sequential", errors)
    schema = documents["surface-registry.schema.json"]
    check(schema["x-family-counts"] == inventory["family_counts"], "surface schema family counts differ", errors)

    template = documents["adapter-contract.template.json"]
    for field in ("contract_id", "surface_ids", "normalized_state", "commands", "events", "security_invariants", "fixtures"):
        check(field in template, f"adapter template missing {field}", errors)
    rejected = documents["rejected-evidence.json"]
    check((ROOT / authority["rejected_historical_evidence"]["manifest"]).is_file(), "rejected evidence manifest path is missing", errors)
    unknown_log = authority["external_native_unknowns"]["log"].split("#", 1)[0]
    check((ROOT / unknown_log).is_file(), "external/native unknown log path is missing", errors)
    check(rejected["classification"] == "rejected_historical_evidence", "historical evidence classification changed", errors)
    check(rejected["baseline_status"] == "rejected", "historical evidence must remain rejected", errors)
    check(authority["rejected_historical_evidence"]["approved_baseline"] is False, "historical evidence cannot be a baseline", errors)
    expected_states = {"first-run", "account-free-confirmation", "account-free-print-boundary", "privacy-provider-residue", "account-free-shell", "about", "narrow-keyboard-focus", "restored-wide"}
    check({item["state"] for item in rejected["records"]} == expected_states, "rejected screenshot state matrix differs", errors)
    for record in rejected["records"]:
        path = ROOT / record["path"]
        check(path.is_file(), f"missing rejected evidence: {record['path']}", errors)
        if path.is_file():
            check(digest(path) == record["sha256"], f"rejected evidence hash mismatch: {record['path']}", errors)

    authored = "\n".join(path.read_text(encoding="utf-8") for path in CONTRACTS.glob("*.json"))
    authored += (ROOT / "docs" / "VISUAL-PHASE-0-POLICY.md").read_text(encoding="utf-8")
    prohibited = [r"\bpixel[- ]perfect\b", r"\b(?:upstream|mozilla) updates? (?:are|is) harmless\b", r"\ball provider (?:flows|content) (?:is|are) (?:accepted|supported)\b"]
    for pattern in prohibited:
        check(not re.search(pattern, authored, re.IGNORECASE), f"prohibited guarantee language: {pattern}", errors)
    return report(errors)


def report(errors):
    if errors:
        print("Phase 0 visual contract validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Phase 0 visual contracts valid: authority hashes, source pins, 80 sequential IDs, schemas, rejected evidence, and language gates passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
