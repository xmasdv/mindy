#!/usr/bin/env python3
"""Fail-closed validation for Mindy artifact provenance receipts."""
import argparse, configparser, hashlib, json, os, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
HEX, REV = re.compile(r"^[a-f0-9]{64}$"), re.compile(r"^[a-f0-9]{40}$")
IDENTITY = {"app": "Mindy", "product": "Mindy", "profile": "mindy", "remoting": "mindy", "vendor": "Mindy Project", "channel": "development", "branding": "mindy", "updater": "disabled", "lto": "disabled"}
CLAIMS = {"clean-source", "no-owned-service-endpoints", "lto-disabled"}
POLICY = "docs/MINDY-IDENTITY-AND-SERVICES.md"
REMOTE = "https://github.com/xmasdv/mindy.git"

class ReceiptError(ValueError): pass

def require(condition, message):
    if not condition: raise ReceiptError(message)

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def text_sha(value): return hashlib.sha256(value.encode()).hexdigest()
def linked(path): return path.is_symlink() or getattr(os.path, "isjunction", lambda _: False)(path)

def safe_path(root, raw, required=True):
    require(isinstance(raw, str) and raw, "path is missing")
    require(not raw.startswith(("/", "\\")) and not re.match(r"^[A-Za-z]:", raw), f"unsafe path: {raw}")
    parts = re.split(r"[\\/]", raw)
    require(all(part not in ("", ".", "..") for part in parts), f"unsafe path: {raw}")
    base = Path(root)
    require(not linked(base), f"linked root rejected: {root}")
    base = base.resolve(strict=True)
    require(not linked(base), f"linked root rejected: {root}")
    path = base
    for part in parts:
        path /= part
        require(not linked(path), f"linked path rejected: {raw}")
    resolved = path.resolve(strict=False)
    require(resolved == base or base in resolved.parents, f"resolved path escapes root: {raw}")
    require(not required or resolved.is_file(), f"missing evidence: {raw}")
    return resolved

def canonical_series(entries):
    return text_sha("".join(f"{item['path']}\0{item['sha256']}\n" for item in entries))

def command(*args, cwd):
    return subprocess.check_output(args, cwd=cwd, text=True).strip()

def repository_state(root):
    def hg(path):
        status = command("hg", "-R", str(path), "status", "-mard", cwd=root)
        return {"revision": command("hg", "-R", str(path), "log", "-r", ".", "-T", "{node}", cwd=root), "status_sha256": text_sha(status)}
    head = command("git", "rev-parse", "HEAD", cwd=root)
    base = command("git", "rev-parse", "origin/feat/mindy-desktop-mvp", cwd=root)
    ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", base, head], cwd=root).returncode == 0
    status = command("git", "status", "--porcelain", cwd=root)
    return {"head": head, "remote": command("git", "remote", "get-url", "origin", cwd=root), "base": base, "ancestor": ancestor, "clean": text_sha(status), "sources": {"gecko": hg(root / "vendor/gecko"), "comm": hg(root / "vendor/gecko/comm")}}

def clean_records(state):
    return {"repository": {"command": "git status --porcelain", "result": "clean", "output_sha256": state["clean"]}, **{name: {"command": "hg status -mard", "result": "clean", "output_sha256": item["status_sha256"]} for name, item in state["sources"].items()}}

def evidence_records(records, repository, artifact):
    require(isinstance(records, list) and records, "verification records are incomplete")
    for record in records:
        output = record.get("output", {})
        require(set(record) == {"command", "expected", "output"} and isinstance(record["command"], list) and record["command"] and all(isinstance(value, str) and value.strip() for value in record["command"]) and record["expected"] in {"pass", "fail", "unavailable"} and set(output) == {"scope", "path", "sha256"} and output["scope"] in {"repository", "artifact"} and HEX.fullmatch(output["sha256"]) and output["sha256"] != "0" * 64, "verification records are incomplete")
        root = repository if output["scope"] == "repository" else artifact
        require(root is not None and sha(safe_path(root, output["path"])) == output["sha256"], "verification output evidence differs")

def status_records(records):
    require(isinstance(records, list) and records and all(set(item) == {"status", "code", "detail"} and item["status"] in {"pending", "unknown", "deferred", "not_applicable"} and re.fullmatch(r"[a-z][a-z0-9-]{2,63}", item["code"]) and item["detail"].strip().lower() not in {"none", "all facts known"} for item in records), "unknowns or limitations are invalid")
    return any(item["status"] in {"pending", "unknown"} for item in records)

def validate(receipt, root=ROOT, artifact_root=None, state=None, accept_historical=False, fixture=False):
    required = {"schema_version", "classification", "git", "source_pins", "patches", "build", "configuration", "artifact", "service_policy", "verification", "unknowns", "limitations", "claims", "approval"}
    require(set(receipt) == required and receipt["schema_version"] == 1, "receipt schema is incomplete")
    classification = receipt["classification"]
    require(classification in {"canonical", "historical", "synthetic"}, "unsupported receipt classification")
    require(classification == "canonical" or accept_historical, "historical evidence cannot satisfy canonical acceptance")
    require(classification != "canonical" or artifact_root, "canonical receipt requires verified artifact root")
    require(state is None or fixture, "fixture state requires explicit test mode")
    git, integration = receipt["git"], receipt["git"].get("integration", {})
    expected_integration = {"remote": "origin", "url": REMOTE, "branch": "feat/mindy-desktop-mvp", "commit": integration.get("commit")}
    require(REV.fullmatch(git.get("commit", "")) and integration == expected_integration and REV.fullmatch(integration["commit"]), "Git integration identity is incomplete")
    pins = receipt["source_pins"]; lock = json.loads(safe_path(root, pins.get("lock_path")).read_text(encoding="utf-8"))
    require(all(isinstance(pins.get(name), dict) and pins[name].get("repository", "").startswith("https://") and REV.fullmatch(pins[name].get("revision", "")) for name in ("gecko", "comm")), "source pins are incomplete")
    require({name: pins.get(name) for name in ("gecko", "comm")} == {name: lock.get(name) for name in ("gecko", "comm")}, "source pins differ from sources.lock")
    if state is None: state = repository_state(root)
    require(state["head"] == git["commit"] and state["remote"] == REMOTE and state["base"] == integration["commit"] and state["ancestor"], "Git remote, commit, or base ancestry differs")
    require(pins.get("clean_status") == clean_records(state), "clean Git or source status evidence differs")
    require(all(state["sources"][name]["revision"] == pins[name]["revision"] for name in ("gecko", "comm")), "external source pins differ")
    patches = receipt["patches"]
    require(patches.get("series_path") == "patches/series", "alternate patch series rejected")
    series = safe_path(root, "patches/series"); data = series.read_bytes()
    require(b"\r" not in data, "patch series is not canonical LF")
    names = [line.split("#", 1)[0].strip() for line in data.decode("utf-8").splitlines()]; names = [name for name in names if name]
    entries = patches.get("entries")
    require(names and isinstance(entries, list) and names == [item.get("path") for item in entries], "patch series entries differ")
    for item in entries:
        path = safe_path(root, f"patches/{item.get('path', '')}")
        require(path.suffix == ".patch" and b"\r" not in path.read_bytes() and item.get("sha256") == sha(path), "patch bytes are noncanonical or mismatched")
    require(patches.get("canonical_sha256") == canonical_series(entries), "canonical patch series hash differs")
    build = receipt["build"]; mozconfig = safe_path(root, build.get("mozconfig_path"))
    require(build.get("mozconfig_path") == "config/mozconfig-pilot" and build.get("mozconfig_sha256") == sha(mozconfig) and isinstance(build.get("command"), list) and all(isinstance(value, str) and value.strip() for value in build["command"]) and isinstance(build.get("environment"), dict) and all(isinstance(value, str) and value.strip() for value in build["environment"].values()), "build identity is incomplete")
    require(receipt["configuration"] == IDENTITY and set(receipt["claims"]) == CLAIMS, "generated configuration identity or claims differ")
    policy = receipt["service_policy"]; policy_path = safe_path(root, policy.get("path"))
    require(policy.get("issue") == 27 and policy.get("path") == POLICY and policy.get("sha256") == sha(policy_path), "service policy evidence differs")
    require(isinstance(policy.get("endpoints"), list), "unowned or unclassified service endpoint")
    for endpoint in policy["endpoints"]:
        parsed = urlsplit(endpoint.get("url", "")); host = parsed.hostname or ""
        require(set(endpoint) == {"url", "classification", "purpose", "policy_evidence"} and parsed.scheme and host and endpoint["classification"] in {"provider", "user_initiated", "account_configuration"} and endpoint["purpose"].strip() and endpoint["policy_evidence"] == f"{POLICY}#service-policy" and not any(name in host.lower() for name in ("mindy", "mozilla", "thunderbird")), "unowned or unclassified service endpoint")
    artifact, manifest = receipt["artifact"], receipt["artifact"].get("manifest", {})
    require(HEX.fullmatch(artifact.get("sha256", "")) and isinstance(artifact.get("size"), int) and artifact["size"] >= 0 and all(isinstance(artifact.get(key), str) and artifact[key] for key in ("path", "timestamp", "version")) and set(manifest) == {"path", "sha256"} and set(artifact.get("configuration", {})) == {"path", "sha256"}, "artifact identity is incomplete")
    output_root = artifact_root or root
    binary = safe_path(output_root, artifact["path"], required=bool(artifact_root)); ini = safe_path(output_root, manifest["path"], required=bool(artifact_root)); config = safe_path(output_root, artifact["configuration"]["path"], required=bool(artifact_root))
    if classification == "canonical":
        parser = configparser.ConfigParser(); parser.read(ini, encoding="utf-8")
        generated = json.loads(config.read_text(encoding="utf-8"))
        timestamp = datetime.fromtimestamp(binary.stat().st_mtime, timezone.utc).isoformat().replace("+00:00", "Z")
        require((sha(binary), binary.stat().st_size, sha(ini), sha(config), timestamp) == (artifact["sha256"], artifact["size"], manifest["sha256"], artifact["configuration"]["sha256"], artifact["timestamp"]), "artifact hash, size, manifest, configuration, or timestamp differs")
        require(parser["App"].get("Name") == IDENTITY["app"] and parser["App"].get("Version") == artifact["version"] and generated == {"identity": IDENTITY, "version": artifact["version"]}, "application version or generated identity differs")
    evidence_records(receipt["verification"], root, artifact_root)
    require(status_records(receipt["unknowns"]) and status_records(receipt["limitations"]) and receipt["approval"] == {"status": "pending-independent-review", "reviewer": None}, "receipt self-approval, unknowns, or limitations are invalid")

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("receipt"); parser.add_argument("--artifact-root"); parser.add_argument("--allow-historical", action="store_true")
    args = parser.parse_args()
    try:
        with open(args.receipt, encoding="utf-8") as stream: validate(json.load(stream), artifact_root=args.artifact_root, accept_historical=args.allow_historical)
    except (OSError, KeyError, TypeError, configparser.Error, json.JSONDecodeError, ReceiptError, subprocess.CalledProcessError) as error:
        print(f"artifact receipt: FAIL: {error}", file=sys.stderr); return 1
    print("artifact receipt: PASS"); return 0

if __name__ == "__main__": raise SystemExit(main())
