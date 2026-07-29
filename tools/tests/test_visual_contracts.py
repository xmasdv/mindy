import copy, importlib.util, subprocess, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
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


if __name__ == "__main__":
    unittest.main()
