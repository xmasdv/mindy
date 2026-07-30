#!/usr/bin/env python3
"""Fail-closed validation for Mindy artifact provenance receipts."""
import argparse, hashlib, json, os, re, subprocess, sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
HEX, REV = re.compile(r"^[a-f0-9]{64}$"), re.compile(r"^[a-f0-9]{40}$")
IDENTITY = {"app", "product", "profile", "vendor", "channel", "branding", "updater", "lto"}
CLAIMS = {"clean-source", "no-owned-service-endpoints", "lto-disabled"}

class ReceiptError(ValueError): pass

def require(condition, message):
    if not condition: raise ReceiptError(message)

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def linked(path):
    return path.is_symlink() or getattr(os.path, "isjunction", lambda _: False)(path)

def safe_file(root, raw):
    require(isinstance(raw, str) and raw, "path is missing")
    value = PurePosixPath(raw)
    require(not value.is_absolute() and ".." not in value.parts and not Path(raw).drive, f"unsafe path: {raw}")
    path = Path(root)
    for part in value.parts:
        path /= part
        require(not linked(path), f"linked path rejected: {raw}")
    require(path.is_file(), f"missing evidence: {raw}")
    return path

def canonical_series(entries):
    return hashlib.sha256("".join(f"{item['path']}\0{item['sha256']}\n" for item in entries).encode()).hexdigest()

def repository_state(root):
    def git(*args): return subprocess.check_output(["git", *args], cwd=root, text=True).strip()
    return {"head": git("rev-parse", "HEAD"), "status": git("status", "--porcelain"), "base": git("rev-parse", "origin/feat/mindy-desktop-mvp")}

def validate(receipt, root=ROOT, artifact_root=None, state=None, accept_historical=False):
    required = {"schema_version", "classification", "git", "source_pins", "patches", "build", "configuration", "artifact", "service_policy", "verification", "limitations", "claims", "approval"}
    require(set(receipt) == required and receipt["schema_version"] == 1, "receipt schema is incomplete")
    classification = receipt["classification"]
    require(classification in {"canonical", "historical", "synthetic"}, "unsupported receipt classification")
    require(classification == "canonical" or accept_historical, "historical evidence cannot satisfy canonical acceptance")
    git = receipt["git"]; integration = git.get("integration", {})
    require(REV.fullmatch(git.get("commit", "")) and integration == {"remote": "origin", "branch": "feat/mindy-desktop-mvp", "commit": integration.get("commit")}, "Git integration identity is incomplete")
    require(REV.fullmatch(integration["commit"]), "integration base is incomplete")
    state = repository_state(root) if state is None else state
    require(state == {"head": git["commit"], "status": "", "base": integration["commit"]}, "Git commit, base, or clean source status differs")
    pins = receipt["source_pins"]; lock = json.loads(safe_file(root, pins.get("lock_path")).read_text(encoding="utf-8"))
    require(pins.get("clean_status") == {"repository": "clean", "gecko": "clean", "comm": "clean"}, "source status is dirty or incomplete")
    require(all(isinstance(pins.get(key), dict) and pins[key].get("repository", "").startswith("https://") and REV.fullmatch(pins[key].get("revision", "")) for key in ("gecko", "comm")), "source pins are incomplete")
    require({key: pins.get(key) for key in ("gecko", "comm")} == {key: lock.get(key) for key in ("gecko", "comm")}, "source pins differ from sources.lock")
    patches = receipt["patches"]; series = safe_file(root, patches.get("series_path"))
    require(b"\r" not in series.read_bytes(), "patch series is not canonical LF")
    names = [line.split("#", 1)[0].strip() for line in series.read_text(encoding="utf-8").splitlines()]; names = [name for name in names if name]
    entries = patches.get("entries")
    require(isinstance(entries, list) and names == [item.get("path") for item in entries], "patch series entries differ")
    for item in entries:
        path = safe_file(root, f"patches/{item.get('path', '')}"); data = path.read_bytes()
        require(path.suffix == ".patch" and b"\r" not in data and item.get("sha256") == sha(path), "patch bytes are noncanonical or mismatched")
    require(patches.get("canonical_sha256") == canonical_series(entries), "canonical patch series hash differs")
    build = receipt["build"]; mozconfig = safe_file(root, build.get("mozconfig_path"))
    require(build.get("mozconfig_sha256") == sha(mozconfig) and isinstance(build.get("command"), list) and build["command"] and all(isinstance(value, str) and value for value in build["command"]) and isinstance(build.get("environment"), dict) and all(build["environment"].values()), "build identity is incomplete")
    configuration = receipt["configuration"]
    require(set(configuration) == IDENTITY and all(isinstance(configuration[key], str) and configuration[key] for key in IDENTITY), "generated configuration identity is incomplete")
    require(configuration["lto"] == "disabled" and set(receipt["claims"]) == CLAIMS, "unsupported claims")
    policy = receipt["service_policy"]; policy_path = safe_file(root, policy.get("path"))
    require(policy.get("issue") == 27 and policy_path.as_posix().endswith("docs/MINDY-IDENTITY-AND-SERVICES.md") and policy.get("sha256") == sha(policy_path) and policy.get("endpoints") == [], "unowned service endpoints or policy evidence")
    artifact = receipt["artifact"]; manifest = artifact.get("manifest", {})
    require(HEX.fullmatch(artifact.get("sha256", "")) and isinstance(artifact.get("size"), int) and artifact["size"] >= 0 and all(isinstance(artifact.get(key), str) and artifact[key] for key in ("path", "timestamp", "version")) and HEX.fullmatch(manifest.get("sha256", "")), "artifact identity is incomplete")
    if artifact_root:
        binary, metadata = safe_file(artifact_root, artifact["path"]), safe_file(artifact_root, manifest.get("path"))
        require((sha(binary), binary.stat().st_size, sha(metadata)) == (artifact["sha256"], artifact["size"], manifest["sha256"]), "artifact hash, size, or manifest differs")
    checks = receipt["verification"]
    require(isinstance(checks, list) and checks and all(set(check) == {"command", "result", "output_sha256"} and check["result"] == "pass" and HEX.fullmatch(check["output_sha256"]) for check in checks), "verification results are incomplete")
    require(isinstance(receipt["limitations"], list) and receipt["limitations"] and receipt["approval"] == {"status": "pending-independent-review", "reviewer": None}, "receipt self-approval or limitations are invalid")

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("receipt"); parser.add_argument("--artifact-root"); parser.add_argument("--allow-historical", action="store_true")
    args = parser.parse_args()
    try:
        with open(args.receipt, encoding="utf-8") as stream: validate(json.load(stream), artifact_root=args.artifact_root, accept_historical=args.allow_historical)
    except (OSError, json.JSONDecodeError, ReceiptError, subprocess.CalledProcessError) as error:
        print(f"artifact receipt: FAIL: {error}", file=sys.stderr); return 1
    print("artifact receipt: PASS"); return 0

if __name__ == "__main__": raise SystemExit(main())
