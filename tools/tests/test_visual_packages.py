import copy, importlib.util, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("visual_packages", ROOT / "tools" / "validate-visual-packages.py")
v = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(v)

class VisualPackageAdversarialTests(unittest.TestCase):
    def setUp(self):
        self.contract = v.load()
        self.patch = (ROOT / self.contract["upstream"]["patch"]).read_text(encoding="utf-8")

    def test_complete_contract_passes(self):
        v.validate(self.contract, self.patch)

    def test_reverse_dependency_fails(self):
        contract = copy.deepcopy(self.contract)
        contract["layers"][0]["dependencies"] = ["ui"]
        with self.assertRaisesRegex(v.PackageError, "reverse dependency"):
            v.validate(contract, self.patch)

    def test_surface_claim_and_unregistered_target_fail(self):
        contract = copy.deepcopy(self.contract)
        contract["surface_registry"]["claims"] = ["SH-01"]
        with self.assertRaisesRegex(v.PackageError, "without claims"):
            v.validate(contract, self.patch)
        patch = self.patch + "\ndiff --git a/comm/mail/unknown b/comm/mail/unknown\n+++ b/comm/mail/unknown\n+hook\n"
        with self.assertRaisesRegex(v.PackageError, "unapproved path"):
            v.validate(self.contract, patch)

    def test_visual_literal_and_ui_global_fail(self):
        patch = self.patch.replace("claims: Object.freeze([])", "claims: Object.freeze([]), color: '#fff'")
        with self.assertRaisesRegex(v.PackageError, "visual"):
            v.validate(self.contract, patch)
        patch = self.patch.replace("return Object.freeze({ mode", "Services.prefs; return Object.freeze({ mode")
        with self.assertRaisesRegex(v.PackageError, "Thunderbird globals"):
            v.validate(self.contract, patch)

    def test_switch_defaults_and_modes_are_fail_closed(self):
        for old in ('pref("mindy.visual.enabled", false);', 'getBoolPref(PREF, false)', 'mode: "registry-only"'):
            with self.subTest(old=old), self.assertRaisesRegex(v.PackageError, "feature switch"):
                v.validate(self.contract, self.patch.replace(old, old.replace("false", "true").replace("registry-only", "visual")))

if __name__ == "__main__":
    unittest.main()
