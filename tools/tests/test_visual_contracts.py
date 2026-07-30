import copy, hashlib, importlib.util, json, subprocess, tempfile, unittest, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT / "patches" / "0002-mindy-mail-shell.patch"
FIXTURES = ROOT / "tools" / "tests" / "fixtures"
SPEC = importlib.util.spec_from_file_location("visual_contracts", ROOT / "tools" / "validate-visual-contracts.py")
v = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v)


class VisualContractAdversarialTests(unittest.TestCase):
    def setUp(self):
        self.rejected = v.load("contracts/visual/rejected-evidence.json")

    def accepted(self):
        return {"schema_version": 1, "classification": "accepted_baseline", "baseline_status": "accepted",
                "source_revisions": {"gecko": "a" * 40, "comm": "b" * 40}, "patch_series_sha256": "c" * 64,
                "artifact_sha256": "d" * 64, "fixture": "synthetic", "captured_at": "2026-07-28",
                "environment": {"os": "Windows", "scale": "100%", "app_zoom": "100%", "theme": "light", "locale": "en-US", "direction": "ltr"},
                "capture_actor": "capture", "review_actor": "review",
                "records": [{"name": "fresh", "path": "DESIGN.md", "sha256": v.digest(v.safe_path("DESIGN.md")), "state": "ready", "dimensions": "1x1"}]}

    def extract_0002_preimage(self, destination):
        manifest = json.loads((FIXTURES / "0002-comm-preimage.json").read_text())
        archive = FIXTURES / manifest["archive"]
        self.assertEqual(manifest["archive_sha256"], hashlib.sha256(archive.read_bytes()).hexdigest())
        source = v.load("sources.lock")["comm"]
        self.assertEqual((manifest["repository"], manifest["revision"]), (source["repository"], source["revision"]))
        with zipfile.ZipFile(archive) as bundle:
            self.assertEqual([item["path"] for item in manifest["files"]], bundle.namelist())
            for item in manifest["files"]:
                data = bundle.read(item["path"])
                self.assertEqual((item["size"], item["sha256"]), (len(data), hashlib.sha256(data).hexdigest()))
                target = destination / item["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)

    def test_rejects_traversal_and_absolute_paths(self):
        with self.assertRaisesRegex(v.ContractError, "unsafe path"):
            v.safe_path("../outside")
        with self.assertRaisesRegex(v.ContractError, "unsafe path"):
            v.safe_path(str(ROOT / "DESIGN.md"))

    def test_rejects_duplicate_registry_ids_and_invalid_combination(self):
        schema = v.load("contracts/visual/surface-registry.schema.json")
        counts = v.load("contracts/visual/authority.json")["surface_inventory"]["family_counts"]
        exact = v.validate_registry(schema, counts)
        instance = {"surfaces": [{"id": item, "owner": "mindy", "boundary": "owned", "adapter_contract": None} for item in exact]}
        instance["surfaces"][0].update(owner="native", boundary="owned")
        with self.assertRaisesRegex(v.ContractError, "invalid owner/boundary"):
            v.validate_registry(schema, counts, instance)
        schema["x-exact-families"]["SH"][1] = "SH-01"
        with self.assertRaises(v.ContractError):
            v.validate_registry(schema, counts)

    def test_rejects_empty_records_and_missing_provenance(self):
        manifest = self.accepted(); manifest["records"] = []
        with self.assertRaisesRegex(v.ContractError, "must not be empty"):
            v.validate_manifest(manifest, check_files=False)
        del manifest["source_revisions"]
        with self.assertRaisesRegex(v.ContractError, "provenance is incomplete"):
            v.validate_manifest(manifest, check_files=False)

    def test_rejects_same_actors_and_rejected_reuse(self):
        manifest = self.accepted(); manifest["review_actor"] = "capture"
        with self.assertRaisesRegex(v.ContractError, "independent actors"):
            v.validate(evidence=manifest)
        manifest = self.accepted(); manifest["records"][0] = copy.deepcopy(self.rejected["records"][0])
        with self.assertRaisesRegex(v.ContractError, "cannot be promoted"):
            v.validate(evidence=manifest)

    def test_top_level_rejects_approved_historical_authority(self):
        authority = v.load("contracts/visual/authority.json")
        authority["rejected_historical_evidence"]["approved_baseline"] = True
        with self.assertRaisesRegex(v.ContractError, "rejected evidence authority differs"):
            v.validate(authority=authority)

    def test_patch_bytes_are_lf_and_windows_input_cleans_to_the_same_blob(self):
        patches = sorted((ROOT / "patches").glob("*.patch"))
        self.assertTrue(patches)
        for patch in patches:
            self.assertNotIn(b"\r", patch.read_bytes(), patch.name)
            attribute = subprocess.check_output(["git", "check-attr", "eol", "--", str(patch)], cwd=ROOT, text=True)
            self.assertTrue(attribute.rstrip().endswith(": lf"), attribute)
        def clean_hash(data):
            return subprocess.run(
                ["git", "-c", "core.autocrlf=true", "hash-object", "--stdin", "--path=patches/example.patch"],
                cwd=ROOT, input=data, capture_output=True, check=True,
            ).stdout
        self.assertEqual(clean_hash(b"line one\nline two\n"), clean_hash(b"line one\r\nline two\r\n"))

    def test_validator_rejects_crlf_instead_of_normalizing_it(self):
        with tempfile.TemporaryDirectory() as temporary:
            patch = Path(temporary) / "corrupt.patch"
            patch.write_bytes(b"line one\r\nline two\r\n")
            with self.assertRaisesRegex(v.ContractError, "patch bytes must use LF"):
                v.patch_digest(patch)

    def test_master_authority_requires_canonical_lf_bytes(self):
        master = ROOT / "assets" / "brand-production" / "mindy-mark.svg"
        canonical = master.read_bytes()
        self.assertNotIn(b"\r", canonical)
        try:
            v.validate()
            for mutated in (canonical.replace(b"\n", b"\r\n"), canonical.replace(b"\n", b"\r\n", 1)):
                master.write_bytes(mutated)
                with self.assertRaisesRegex(v.ContractError, "authority hash mismatch"):
                    v.validate()
        finally:
            master.write_bytes(canonical)

    def test_checked_out_patch_hash_and_pinned_fixture_application(self):
        authority = v.load("contracts/visual/authority.json")["implementation_evidence"][0]
        patch_bytes = PATCH.read_bytes()
        self.assertEqual(authority["path"], PATCH.relative_to(ROOT).as_posix())
        self.assertEqual(authority["sha256"], hashlib.sha256(patch_bytes).hexdigest())
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)
            self.extract_0002_preimage(source)
            result = subprocess.run(["git", "apply", "--check", str(PATCH)], cwd=source, text=True, capture_output=True)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_pinned_fixture_rejects_context_and_patch_drift(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)
            self.extract_0002_preimage(source)
            page = source / "comm/mail/base/content/about3Pane.xhtml"
            original = page.read_bytes()
            page.write_bytes(original.replace(b'lightweightthemes="true"', b'lightweightthemes="false"', 1))
            context = subprocess.run(["git", "apply", "--check", str(PATCH)], cwd=source, capture_output=True)
            self.assertNotEqual(0, context.returncode)
            page.write_bytes(original)
            mutated = source / "mutated.patch"
            patch_bytes = PATCH.read_bytes()
            mutated.write_bytes(patch_bytes.replace(b' lightweightthemes="true">', b' lightweightthemes="other">', 1))
            self.assertNotEqual(v.load("contracts/visual/authority.json")["implementation_evidence"][0]["sha256"], hashlib.sha256(mutated.read_bytes()).hexdigest())
            patch = subprocess.run(["git", "apply", "--check", str(mutated)], cwd=source, capture_output=True)
            self.assertNotEqual(0, patch.returncode)


if __name__ == "__main__":
    unittest.main()
