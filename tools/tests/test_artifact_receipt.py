import copy, hashlib, importlib.util, json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("receipt", ROOT / "tools" / "validate-artifact-receipt.py")
v = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(v)

class ArtifactReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name) / "repo"; self.artifacts = Path(self.temp.name) / "artifacts"
        self.gecko, self.comm = "a" * 40, "b" * 40
        lock = json.dumps({"gecko": {"repository": "https://g", "revision": self.gecko}, "comm": {"repository": "https://c", "revision": self.comm}}).encode()
        for path, data in {"sources.lock": lock, "patches/series": b"one.patch\n", "patches/one.patch": b"patch\n", "config/mozconfig-pilot": b"moz\n", "docs/MINDY-IDENTITY-AND-SERVICES.md": b"policy\n"}.items():
            target = self.root / path; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(data)
        for path, data in {"dist/mindy.exe": b"binary", "dist/application.ini": b"manifest"}.items():
            target = self.artifacts / path; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(data)
        self.state = {"head": "d" * 40, "status": "", "base": "e" * 40}

    def tearDown(self): self.temp.cleanup()

    def receipt(self):
        patch = self.root / "patches/one.patch"; artifact = self.artifacts / "dist/mindy.exe"; manifest = self.artifacts / "dist/application.ini"
        entries = [{"path": "one.patch", "sha256": v.sha(patch)}]
        return {"schema_version": 1, "classification": "synthetic", "git": {"commit": "d" * 40, "integration": {"remote": "origin", "branch": "feat/mindy-desktop-mvp", "commit": "e" * 40}}, "source_pins": {"lock_path": "sources.lock", "clean_status": {"repository": "clean", "gecko": "clean", "comm": "clean"}, "gecko": {"repository": "https://g", "revision": self.gecko}, "comm": {"repository": "https://c", "revision": self.comm}}, "patches": {"series_path": "patches/series", "canonical_sha256": v.canonical_series(entries), "entries": entries}, "build": {"mozconfig_path": "config/mozconfig-pilot", "mozconfig_sha256": v.sha(self.root / "config/mozconfig-pilot"), "command": ["mach build"], "environment": {"os": "Windows", "architecture": "x64", "mozconfig": "config/mozconfig-pilot"}}, "configuration": {"app": "Mindy", "product": "Mindy", "profile": "mindy", "vendor": "Mindy Project", "channel": "dev", "branding": "mindy", "updater": "disabled", "lto": "disabled"}, "artifact": {"path": "dist/mindy.exe", "sha256": v.sha(artifact), "size": artifact.stat().st_size, "timestamp": "2026-07-30T00:00:00Z", "version": "0", "manifest": {"path": "dist/application.ini", "sha256": v.sha(manifest)}}, "service_policy": {"issue": 27, "path": "docs/MINDY-IDENTITY-AND-SERVICES.md", "sha256": v.sha(self.root / "docs/MINDY-IDENTITY-AND-SERVICES.md"), "endpoints": []}, "verification": [{"command": "python -m unittest", "result": "pass", "output_sha256": "f" * 64}], "limitations": ["synthetic fixture"], "claims": ["clean-source", "no-owned-service-endpoints", "lto-disabled"], "approval": {"status": "pending-independent-review", "reviewer": None}}

    def check(self, receipt=None, **kwargs): return v.validate(receipt or self.receipt(), self.root, self.artifacts, self.state, accept_historical=True, **kwargs)

    def test_accepts_explicitly_noncanonical_synthetic_shape(self): self.check()
    def test_rejects_unsafe_and_linked_evidence_paths(self):
        for value in ("../sources.lock", "C:/sources.lock"):
            receipt = self.receipt(); receipt["source_pins"]["lock_path"] = value
            with self.assertRaisesRegex(v.ReceiptError, "unsafe path"): self.check(receipt)
        with patch.object(v, "linked", return_value=True):
            with self.assertRaisesRegex(v.ReceiptError, "linked path rejected"): self.check()
    def test_rejects_dirty_or_mismatched_pins(self):
        dirty = dict(self.state, status=" M sources.lock")
        with self.assertRaisesRegex(v.ReceiptError, "clean source status differs"): v.validate(self.receipt(), self.root, self.artifacts, dirty, accept_historical=True)
        receipt = self.receipt(); del receipt["source_pins"]["comm"]
        with self.assertRaisesRegex(v.ReceiptError, "source pins are incomplete"): self.check(receipt)
        receipt = self.receipt(); receipt["source_pins"]["gecko"]["revision"] = "c" * 40
        with self.assertRaisesRegex(v.ReceiptError, "source pins differ"): self.check(receipt)
    def test_rejects_noncanonical_patch_bytes_and_identity_gaps(self):
        (self.root / "patches/one.patch").write_bytes(b"patch\r\n")
        with self.assertRaisesRegex(v.ReceiptError, "noncanonical"): self.check()
        (self.root / "patches/one.patch").write_bytes(b"patch\n")
        receipt = self.receipt(); del receipt["configuration"]["vendor"]
        with self.assertRaisesRegex(v.ReceiptError, "configuration identity"): self.check(receipt)
    def test_rejects_unowned_services_artifact_drift_claims_and_self_approval(self):
        receipt = self.receipt(); receipt["service_policy"]["endpoints"] = [{"owner": "Mozilla"}]
        with self.assertRaisesRegex(v.ReceiptError, "unowned service"): self.check(receipt)
        receipt = self.receipt(); receipt["artifact"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(v.ReceiptError, "artifact hash"): self.check(receipt)
        receipt = self.receipt(); receipt["claims"].append("signed-release")
        with self.assertRaisesRegex(v.ReceiptError, "unsupported claims"): self.check(receipt)
        receipt = self.receipt(); receipt["approval"]["status"] = "approved"
        with self.assertRaisesRegex(v.ReceiptError, "self-approval"): self.check(receipt)
    def test_historical_receipts_never_pass_canonical_acceptance(self):
        receipt = self.receipt(); receipt["classification"] = "historical"
        with self.assertRaisesRegex(v.ReceiptError, "cannot satisfy canonical"): v.validate(receipt, self.root, self.artifacts, self.state)
        self.check(receipt)

if __name__ == "__main__": unittest.main()
