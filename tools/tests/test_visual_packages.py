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

    def test_rejects_fail_closed_package_grammar(self):
        theme = "comm/mail/mindy/theme/ThemeOwnership.sys.mjs"
        ui = "comm/mail/mindy/ui/VisualPackage.sys.mjs"
        suffixes = [
            '\nimport { VisualPackage } from "resource:///modules/mindy/ui/VisualPackage.sys.mjs";', '\nimport("resource:///modules/mindy/ui/VisualPackage.sys.mjs");',
            '\nimport(`resource:///modules/mindy/ui/VisualPackage.sys.mjs`);', '\nconst layer = "ui"; import(`resource:///modules/mindy/${layer}/VisualPackage.sys.mjs`);',
            '\nconst raw = "resource:///modules/mindy/ui/VisualPackage.sys.mjs";', "\ndoThing();", '\nexport const metadata = "extra";',
            *(f'\nexport const {name} = "{value}";' for name, value in (("spacing", "8px"), ("dimension", "12px"), ("radius", "4px"), ("font", "Inter"), ("motion", "120ms"), ("color", "#fff")))]
        for suffix in suffixes:
            self.rejects(lambda files, value=suffix: files.__setitem__(theme, files[theme] + value), "grammar|unclassified")
        self.rejects(lambda files: files.__setitem__(ui, files[ui] + "\nServices.io.offline;"), "grammar")
        self.rejects(lambda files: files.__setitem__("comm/mail/mindy/contracts/VisualRegistry.sys.mjs",
            files["comm/mail/mindy/contracts/VisualRegistry.sys.mjs"].replace('"SH-02"', '"SH-01"')), "grammar differs")
        files = v.added_files()
        files[theme] = "/* ownership */\n" + files[theme] + " // metadata"
        files["comm/mail/mindy/moz.build"] = "/* roots */\n" + files["comm/mail/mindy/moz.build"] + " // exact"
        v.validate_packages(files)
        manifests = [("comm/mail/mindy/moz.build", '\nDIRS += ["tokens"]'), ("comm/mail/mindy/theme/moz.build", '\nEXTRA_JS_MODULES.mindy.theme += ["Other.sys.mjs"]'),
            ("comm/mail/mindy/test/xpcshell.toml", '\n["missing.js"]'), ("comm/mail/mindy/moz.build", '\nTEST_DIRS += ["test"]'),
            ("comm/mail/mindy/moz.build", "\nUNKNOWN = true"), ("comm/mail/moz.build", None), ("comm/mail/mindy/test/moz.build", None)]
        for path, suffix in manifests:
            self.rejects(lambda data, key=path, value=suffix: data.__setitem__(key, "" if value is None else data[key] + value), "manifest/module grammar")
        self.rejects(lambda data: data.__setitem__(ui, data[ui].replace("/theme/ThemeOwnership.sys.mjs", "/brand/BrandOwnership.sys.mjs")), "grammar differs")
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

    def test_rejects_wrong_order_and_pin(self):
        with mock.patch.object(v, "EXPECTED_SERIES", tuple(reversed(v.EXPECTED_SERIES))):
            with self.assertRaisesRegex(v.PackageError, "identity/order"):
                v.series()
        sources = v.load("sources.lock"); sources["comm"]["revision"] = "0" * 40
        with self.assertRaisesRegex(v.PackageError, "source pins differ"):
            v.validate_pins(sources=sources)

    def test_ordered_series_applies_to_exact_pinned_fixture(self):
        self.assertEqual("PASS(exact pinned fixture, ordered 0002+0003)", v.applicability())
