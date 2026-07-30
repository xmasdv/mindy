import hashlib
import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("bootstrap", ROOT / "tools" / "bootstrap-upstream.py")
bootstrap = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bootstrap)
OVERLAY = ROOT / "overlay" / "comm" / "mail" / "branding" / "mindy"
GENERATED = ROOT / "assets" / "brand-production" / "generated"
PATCH = ROOT / "patches" / "0005-mindy-branding-package.patch"
FIXTURE = ROOT / "tools" / "tests" / "fixtures" / "0005-confvars-preimage"


class MindyBrandingPackageTests(unittest.TestCase):
    def test_selector_series_and_pinned_raw_preimage_are_exact(self):
        bootstrap.verify_branding_selector()
        self.assertEqual("83f5be01463b190e6a6edc656125e4c8d6012ba3aa32986c6ca3b45461dbda63", hashlib.sha256(FIXTURE.read_bytes()).hexdigest())
        self.assertIn("0005-mindy-branding-package.patch", (ROOT / "patches" / "series").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "comm/mail/confvars.sh"
            target.parent.mkdir(parents=True)
            shutil.copyfile(FIXTURE, target)
            self.assertEqual(0, subprocess.run(["git", "apply", "--check", str(PATCH)], cwd=temporary).returncode)
        with tempfile.TemporaryDirectory() as temporary:
            wrong = Path(temporary) / "wrong.patch"
            wrong.write_text(PATCH.read_text(encoding="utf-8").replace("/mindy", "/nightly"), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "selector"):
                bootstrap.verify_branding_selector(wrong)

    def test_package_contract_has_only_canonical_compatible_content(self):
        bootstrap.verify_branding_overlay()
        texts = "\n".join(path.read_text(encoding="utf-8") for path in (OVERLAY / "configure.sh", OVERLAY / "pref/thunderbird-branding.js", *(OVERLAY / "locales/en-US").iterdir()))
        self.assertNotRegex(texts, r"Thunderbird|Daily")
        self.assertNotRegex(texts.replace("http://mozilla.org/MPL/2.0/", ""), r"https?://")
        self.assertEqual(['!define BrandFullNameInternal "Mindy"', '!define BrandFullName "Mindy"'], [line for line in (OVERLAY / "branding.nsi").read_text(encoding="utf-8").splitlines() if line.startswith("!define")])
        manifest = json.loads((GENERATED / "manifest.json").read_text(encoding="utf-8"))["derivatives"]
        self.assertTrue(set(bootstrap.PACKAGE_ASSETS) <= set(manifest))
        self.assertNotIn("msix/", "\n".join(bootstrap.files(OVERLAY)))

    def test_overlay_rejects_drift_untracked_files_and_nonempty_destinations(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); overlay, generated = root / "overlay", root / "generated"
            shutil.copytree(OVERLAY, overlay); shutil.copytree(GENERATED, generated)
            (overlay / "default16.png").write_bytes(b"drift")
            with self.assertRaisesRegex(ValueError, "asset differs"):
                bootstrap.verify_branding_overlay(overlay, generated)
            shutil.copyfile(GENERATED / "default16.png", overlay / "default16.png")
            (overlay / "TB-symbolic.svg").write_text("drift", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "asset differs"):
                bootstrap.verify_branding_overlay(overlay, generated)
            shutil.copyfile(GENERATED / "TB-symbolic.svg", overlay / "TB-symbolic.svg")
            (overlay / "TB-symbolic.svg").unlink()
            with self.assertRaisesRegex(ValueError, "files differ"):
                bootstrap.verify_branding_overlay(overlay, generated)
            shutil.copyfile(GENERATED / "TB-symbolic.svg", overlay / "TB-symbolic.svg")
            (overlay / "locales/en-US/brand.ftl").write_text("-brand-short-name = Thunderbird\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "locale or config"):
                bootstrap.verify_branding_overlay(overlay, generated)
            shutil.copyfile(OVERLAY / "locales/en-US/brand.ftl", overlay / "locales/en-US/brand.ftl")
            (generated / "untracked.png").write_bytes(b"untracked")
            with self.assertRaisesRegex(ValueError, "inventory"):
                bootstrap.verify_branding_overlay(overlay, generated)
            (generated / "untracked.png").unlink()
            (overlay / "jar.mn").unlink()
            with self.assertRaisesRegex(ValueError, "files differ"):
                bootstrap.verify_branding_overlay(overlay, generated)
            shutil.copyfile(OVERLAY / "jar.mn", overlay / "jar.mn")
            bootstrap.copy_branding_overlay(root / "clean", overlay, generated)
            self.assertEqual((generated / "default16.png").read_bytes(), (root / "clean/mail/branding/mindy/default16.png").read_bytes())
            destination = root / "comm/mail/branding/mindy"; destination.mkdir(parents=True)
            (destination / "occupied").write_text("no", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "nonempty"):
                bootstrap.copy_branding_overlay(root / "comm", overlay, generated)


if __name__ == "__main__":
    unittest.main()
