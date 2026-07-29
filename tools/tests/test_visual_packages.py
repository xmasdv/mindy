import copy, importlib.util, os, tempfile, unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("visual_packages", ROOT / "tools" / "validate-visual-packages.py")
v = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v)

class VisualPackageAdversarialTests(unittest.TestCase):
    def rejects(self, mutation, message):
        files = copy.deepcopy(v.added_files())
        mutation(files)
        with self.assertRaisesRegex(v.PackageError, message):
            v.validate_packages(files)

    def test_rejects_reverse_import_and_direct_ui_global(self):
        self.rejects(lambda f: f.__setitem__("comm/mail/mindy/theme/ThemeOwnership.sys.mjs",
            f["comm/mail/mindy/theme/ThemeOwnership.sys.mjs"] + '\nimport "resource:///modules/mindy/ui/VisualPackage.sys.mjs";'), "import edges differ")
        self.rejects(lambda f: f.__setitem__("comm/mail/mindy/ui/VisualPackage.sys.mjs",
            f["comm/mail/mindy/ui/VisualPackage.sys.mjs"] + "\nServices.io.offline;"), "Thunderbird globals")
        self.rejects(lambda f: f.__setitem__("comm/mail/mindy/theme/ThemeOwnership.sys.mjs",
            f["comm/mail/mindy/theme/ThemeOwnership.sys.mjs"] + '\nimport("resource:///modules/mindy/ui/VisualPackage.sys.mjs");'), "import edges differ")

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
            "+++ b/comm/mail/moz.build", "+++ b/../../outside", 1)
        with tempfile.TemporaryDirectory() as temporary:
            bad = Path(temporary) / "bad.patch"; bad.write_text(patch)
            with self.assertRaisesRegex(v.PackageError, "unsafe path"):
                v.added_files(bad)

    def test_rejects_deletion_only_high_churn_and_visual_css(self):
        base = v.safe_path(f"patches/{v.PACKAGE_PATCH}").read_text()
        mutations = [
            "diff --git a/comm/mail/base/content/about3Pane.xhtml b/comm/mail/base/content/about3Pane.xhtml\ndeleted file mode 100644\n--- a/comm/mail/base/content/about3Pane.xhtml\n+++ /dev/null\n@@ -1 +0,0 @@\n-old\n",
            "diff --git a/comm/mail/mindy/ui/colors.css b/comm/mail/mindy/ui/colors.css\nnew file mode 100644\n--- /dev/null\n+++ b/comm/mail/mindy/ui/colors.css\n@@ -0,0 +1 @@\n+body { color: #fff; }\n"]
        for mutation in mutations:
            with self.subTest(mutation=mutation.splitlines()[0]), tempfile.TemporaryDirectory() as temporary:
                patch = Path(temporary) / "mutated.patch"; patch.write_text(base + mutation)
                with self.assertRaisesRegex(v.PackageError, "target scope differs"):
                    v.added_files(patch)

    def test_rejects_wrong_order_pin_and_missing_test_registration(self):
        with mock.patch.object(v, "EXPECTED_SERIES", tuple(reversed(v.EXPECTED_SERIES))):
            with self.assertRaisesRegex(v.PackageError, "identity/order"):
                v.series()
        sources = v.load("sources.lock"); sources["comm"]["revision"] = "0" * 40
        with self.assertRaisesRegex(v.PackageError, "source pins differ"):
            v.validate_pins(sources=sources)
        self.rejects(lambda f: f.__setitem__("comm/mail/mindy/test/moz.build", ""), "test root is unregistered")

    def test_ordered_series_applies_to_exact_pinned_fixture(self):
        self.assertEqual("PASS(exact pinned fixture, ordered 0002+0003)", v.applicability())
