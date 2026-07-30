import copy, importlib.util, json, tempfile, unittest
from datetime import datetime, timezone
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
        files = {"sources.lock": lock, "patches/series": b"one.patch\n", "patches/one.patch": b"patch\n", "config/mozconfig-pilot": b"moz\n", v.POLICY: b"policy\n"}
        for path, data in files.items():
            target = self.root / path; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(data)
        self.write_output()
        self.state = {"head": "d" * 40, "remote": v.REMOTE, "base": "e" * 40, "ancestor": True, "clean": v.text_sha(""), "sources": {"gecko": {"revision": self.gecko, "status_sha256": v.text_sha("")}, "comm": {"revision": self.comm, "status_sha256": v.text_sha("")}}}

    def tearDown(self): self.temp.cleanup()

    def write_output(self):
        for path, data in {"dist/mindy.exe": b"binary", "dist/application.ini": b"[App]\nName=Mindy\nVersion=0\n", "dist/mindy-config.json": json.dumps({"identity": v.IDENTITY, "version": "0"}).encode(), "verification/unit.txt": b"result=pass\n"}.items():
            target = self.artifacts / path; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(data)

    def receipt(self, classification="synthetic"):
        patch = self.root / "patches/one.patch"; binary = self.artifacts / "dist/mindy.exe"; ini = self.artifacts / "dist/application.ini"; config = self.artifacts / "dist/mindy-config.json"
        entries = [{"path": "one.patch", "sha256": v.sha(patch)}]
        output = self.artifacts / "verification/unit.txt"
        return {"schema_version": 1, "classification": classification, "git": {"commit": "d" * 40, "integration": {"remote": "origin", "url": v.REMOTE, "branch": "feat/mindy-desktop-mvp", "commit": "e" * 40}}, "source_pins": {"lock_path": "sources.lock", "clean_status": v.clean_records(self.state), "gecko": {"repository": "https://g", "revision": self.gecko}, "comm": {"repository": "https://c", "revision": self.comm}}, "patches": {"series_path": "patches/series", "canonical_sha256": v.canonical_series(entries), "entries": entries}, "build": {"mozconfig_path": "config/mozconfig-pilot", "mozconfig_sha256": v.sha(self.root / "config/mozconfig-pilot"), "command": ["mach", "build"], "environment": {"os": "Windows", "architecture": "x64", "mozconfig": "config/mozconfig-pilot"}}, "configuration": dict(v.IDENTITY), "artifact": {"path": "dist/mindy.exe", "sha256": v.sha(binary), "size": binary.stat().st_size, "timestamp": datetime.fromtimestamp(binary.stat().st_mtime, timezone.utc).isoformat().replace("+00:00", "Z"), "version": "0", "manifest": {"path": "dist/application.ini", "sha256": v.sha(ini)}, "configuration": {"path": "dist/mindy-config.json", "sha256": v.sha(config)}}, "service_policy": {"issue": 27, "path": v.POLICY, "sha256": v.sha(self.root / v.POLICY), "endpoints": []}, "verification": [{"command": ["python", "-m", "unittest"], "expected": "pass", "output": {"scope": "artifact", "path": "verification/unit.txt", "sha256": v.sha(output)}}], "unknowns": [{"status": "unknown", "code": "canonical-artifact", "detail": "No clean artifact exists."}], "limitations": [{"status": "pending", "code": "independent-review", "detail": "Synthetic fixture."}], "claims": sorted(v.CLAIMS), "approval": {"status": "pending-independent-review", "reviewer": None}}

    def check(self, receipt=None): return v.validate(receipt or self.receipt(), self.root, self.artifacts, self.state, accept_historical=True, fixture=True)

    def test_accepts_explicit_noncanonical_fixture_only(self): self.check()
    def test_canonical_requires_artifact_root_and_recomputes_output(self):
        receipt = self.receipt("canonical")
        with self.assertRaisesRegex(v.ReceiptError, "requires verified artifact root"): v.validate(receipt, self.root, state=self.state, fixture=True)
        self.check(receipt)
        (self.artifacts / "dist/mindy.exe").write_bytes(b"forged")
        with self.assertRaisesRegex(v.ReceiptError, "artifact hash"): self.check(receipt)
    def test_rejects_application_version_and_generated_identity_drift(self):
        receipt = self.receipt("canonical"); ini = self.artifacts / "dist/application.ini"
        ini.write_text("[App]\nName=Thunderbird\nVersion=0\n", encoding="utf-8"); receipt["artifact"]["manifest"]["sha256"] = v.sha(ini)
        with self.assertRaisesRegex(v.ReceiptError, "application version or generated identity"): self.check(receipt)
        self.write_output(); receipt = self.receipt("canonical"); receipt["configuration"]["app"] = "Thunderbird"
        with self.assertRaisesRegex(v.ReceiptError, "generated configuration identity"): self.check(receipt)
    def test_rejects_platform_traversal_links_and_resolved_escape(self):
        for value in ("../sources.lock", r"..\sources.lock", r"C:\sources.lock", r"\\server\share"):
            receipt = self.receipt(); receipt["source_pins"]["lock_path"] = value
            with self.assertRaisesRegex(v.ReceiptError, "unsafe path"): self.check(receipt)
        with patch.object(v, "linked", side_effect=lambda path: path.name == "sources.lock"):
            with self.assertRaisesRegex(v.ReceiptError, "linked path rejected"): v.safe_path(self.root, "sources.lock")
        outside = Path(self.temp.name) / "outside"
        with patch.object(Path, "resolve", side_effect=[self.root, outside]):
            with self.assertRaisesRegex(v.ReceiptError, "resolved path escapes root"): v.safe_path(self.root, "sources.lock")
    def test_rejects_linked_artifact_root_before_resolution(self):
        receipt = self.receipt("canonical"); linked_root = Path(self.temp.name) / "artifact-link"
        with patch.object(v, "linked", side_effect=lambda path: path == self.artifacts):
            with self.assertRaisesRegex(v.ReceiptError, "linked root rejected"): v.safe_path(self.artifacts, "dist/mindy.exe")
        try: linked_root.symlink_to(self.artifacts, target_is_directory=True)
        except OSError: return
        with self.assertRaisesRegex(v.ReceiptError, "linked root rejected"): v.validate(receipt, self.root, linked_root, self.state, fixture=True)
    def test_rejects_alternate_empty_or_noncanonical_patch_series(self):
        receipt = self.receipt(); receipt["patches"]["series_path"] = "patches/empty"
        with self.assertRaisesRegex(v.ReceiptError, "alternate patch series"): self.check(receipt)
        (self.root / "patches/series").write_bytes(b"")
        with self.assertRaisesRegex(v.ReceiptError, "patch series entries differ"): self.check()
        (self.root / "patches/series").write_bytes(b"one.patch\n"); (self.root / "patches/one.patch").write_bytes(b"patch\r\n")
        with self.assertRaisesRegex(v.ReceiptError, "noncanonical"): self.check()
    def test_rejects_remote_status_and_external_pin_mismatch(self):
        state = copy.deepcopy(self.state); state["remote"] = "https://example.invalid/mindy.git"
        with self.assertRaisesRegex(v.ReceiptError, "Git remote"): v.validate(self.receipt(), self.root, self.artifacts, state, accept_historical=True, fixture=True)
        receipt = self.receipt(); del receipt["source_pins"]["comm"]
        with self.assertRaisesRegex(v.ReceiptError, "source pins are incomplete"): self.check(receipt)
        receipt = self.receipt(); receipt["source_pins"]["clean_status"]["gecko"]["result"] = "dirty"
        with self.assertRaisesRegex(v.ReceiptError, "clean Git or source"): self.check(receipt)
        state = copy.deepcopy(self.state); state["ancestor"] = False
        with self.assertRaisesRegex(v.ReceiptError, "Git remote"): v.validate(self.receipt(), self.root, self.artifacts, state, accept_historical=True, fixture=True)
        state = copy.deepcopy(self.state); state["sources"]["gecko"]["revision"] = "c" * 40
        with self.assertRaisesRegex(v.ReceiptError, "external source pins"): v.validate(self.receipt(), self.root, self.artifacts, state, accept_historical=True, fixture=True)
    def test_accepts_explicit_provider_evidence_and_rejects_product_or_generic_urls(self):
        receipt = self.receipt(); receipt["service_policy"]["endpoints"] = [{"url": "https://oauth.example.test", "classification": "provider", "purpose": "user OAuth", "policy_evidence": f"{v.POLICY}#service-policy"}]
        self.check(receipt)
        receipt["service_policy"]["endpoints"][0]["url"] = "https://services.mozilla.com"
        with self.assertRaisesRegex(v.ReceiptError, "unowned or unclassified"): self.check(receipt)
        receipt = self.receipt(); receipt["service_policy"]["endpoints"] = [{"url": "https://mail.example.test"}]
        with self.assertRaisesRegex(v.ReceiptError, "unowned or unclassified"): self.check(receipt)
    def test_rejects_incomplete_verification_unknowns_claims_and_self_approval(self):
        receipt = self.receipt(); receipt["verification"][0]["command"] = []
        with self.assertRaisesRegex(v.ReceiptError, "verification records"): self.check(receipt)
        receipt = self.receipt(); receipt["verification"][0]["output"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(v.ReceiptError, "verification records"): self.check(receipt)
        receipt = self.receipt(); receipt["verification"][0]["output"]["path"] = "missing.txt"
        with self.assertRaisesRegex(v.ReceiptError, "missing evidence"): self.check(receipt)
        receipt = self.receipt(); receipt["verification"][0]["output"]["sha256"] = "f" * 64
        with self.assertRaisesRegex(v.ReceiptError, "output evidence"): self.check(receipt)
        receipt = self.receipt(); receipt["verification"][0]["expected"] = "unverified assertion"
        with self.assertRaisesRegex(v.ReceiptError, "verification records"): self.check(receipt)
        receipt = self.receipt(); receipt["unknowns"] = []
        with self.assertRaisesRegex(v.ReceiptError, "unknowns"): self.check(receipt)
        receipt = self.receipt(); receipt["limitations"][0]["detail"] = "all facts known"
        with self.assertRaisesRegex(v.ReceiptError, "unknowns or limitations"): self.check(receipt)
        receipt = self.receipt(); receipt["claims"].append("supported-release")
        with self.assertRaisesRegex(v.ReceiptError, "identity or claims"): self.check(receipt)
        receipt = self.receipt(); receipt["approval"]["status"] = "approved"
        with self.assertRaisesRegex(v.ReceiptError, "self-approval"): self.check(receipt)
    def test_historical_never_satisfies_canonical_acceptance(self):
        receipt = self.receipt("historical")
        with self.assertRaisesRegex(v.ReceiptError, "cannot satisfy canonical"): v.validate(receipt, self.root, self.artifacts, self.state, fixture=True)
        self.check(receipt)

if __name__ == "__main__": unittest.main()
