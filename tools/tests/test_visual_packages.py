import copy, importlib.util, os, tempfile, unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("visual_packages", ROOT / "tools" / "validate-visual-packages.py")
v = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v)

class VisualPackageAdversarialTests(unittest.TestCase):
    def setUp(self):
        self.files = v.added_files()

    def rejects(self, mutation, message):
        files = copy.deepcopy(self.files)
        mutation(files)
        with self.assertRaisesRegex(v.PackageError, message):
            v.validate_packages(files)

    def test_rejects_reverse_import_and_direct_ui_global(self):
        self.rejects(lambda f: f.__setitem__("comm/mail/mindy/theme/ThemeOwnership.sys.mjs",
            f["comm/mail/mindy/theme/ThemeOwnership.sys.mjs"] + '\nimport "resource:///modules/mindy/ui/VisualPackage.sys.mjs";'), "import edges differ")
        self.rejects(lambda f: f.__setitem__("comm/mail/mindy/ui/VisualPackage.sys.mjs",
            f["comm/mail/mindy/ui/VisualPackage.sys.mjs"] + "\nServices.io.offline;"), "Thunderbird globals")

    def test_rejects_dead_root_and_unregistered_hook(self):
        self.rejects(lambda f: f.__setitem__("comm/mail/mindy/ui/VisualPackage.sys.mjs",
            f["comm/mail/mindy/ui/VisualPackage.sys.mjs"].replace("/theme/ThemeOwnership.sys.mjs", "/brand/BrandOwnership.sys.mjs")), "import edges differ")
        self.rejects(lambda f: f.__setitem__("comm/mail/moz.build", ""), "registration hook")

    def test_rejects_registry_drift_and_duplicate(self):
        self.rejects(lambda f: f.__setitem__("comm/mail/mindy/contracts/VisualRegistry.sys.mjs",
            f["comm/mail/mindy/contracts/VisualRegistry.sys.mjs"].replace('"SH-02"', '"SH-01"')), "registry drift")

    def test_rejects_unsafe_and_linked_paths(self):
        with self.assertRaisesRegex(v.PackageError, "unsafe path"):
            v.safe_path("../outside")
        with self.assertRaisesRegex(v.PackageError, "unsafe path"):
            v.safe_path(str(ROOT / "patches" / v.PACKAGE_PATCH))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); outside = root.parent / "outside-phase1a"
            outside.mkdir(exist_ok=True)
            try:
                os.symlink(outside, root / "linked", target_is_directory=True)
            except OSError:
                self.skipTest("symlinks unavailable")
            with self.assertRaisesRegex(v.PackageError, "linked path"):
                v.safe_path("linked", root)
        patch = v.safe_path(f"patches/{v.PACKAGE_PATCH}").read_text().replace(
            " b/comm/mail/moz.build", " b/../../outside", 1)
        with tempfile.TemporaryDirectory() as temporary:
            bad = Path(temporary) / "bad.patch"; bad.write_text(patch)
            with self.assertRaisesRegex(v.PackageError, "unsafe path"):
                v.added_files(bad)

    def test_rejects_wrong_order_pin_and_missing_test_registration(self):
        with mock.patch.object(v, "EXPECTED_SERIES", tuple(reversed(v.EXPECTED_SERIES))):
            with self.assertRaisesRegex(v.PackageError, "identity/order"):
                v.series()
        sources = v.load("sources.lock"); sources["comm"]["revision"] = "0" * 40
        with self.assertRaisesRegex(v.PackageError, "source pins differ"):
            v.validate_pins(sources=sources)
        self.rejects(lambda f: f.__setitem__("comm/mail/mindy/test/moz.build", ""), "test root is unregistered")

if __name__ == "__main__":
    unittest.main()
