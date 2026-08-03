import hashlib
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT / "patches" / "0004-mindy-identity-namespace.patch"
FIXTURE = ROOT / "tools/tests/fixtures/0004-moz.configure-preimage"
APP_ID = '{3550f703-e582-4d05-9a08-453d09bdfdc6}'
SOURCE_SHA256 = "509333fa615937375bf294f8f98918eb0768f07a3c696a142dd62a2392a6867d"
SERIES = (
    ("0002-mindy-mail-shell.patch", "3d7121e6b25d6eb09c8689197704240084a7b69628a494b657a5c556cd6ab578"),
    ("0003-mindy-visual-packages.patch", "88b9822425f41f2611f9d12f1fc031cd804edf3e87fac57143f800362f2bf49e"),
    ("0004-mindy-identity-namespace.patch", "98ff34214761441f557ebbe1247036d3f0da37f7ba7f9ecc8e5d213c4859f013"),
    ("0005-mindy-branding-package.patch", "d829b482041c149a1e30efbddc65d32c31ba9e79de6dd3b39a237ae6123cff3c"),
    ("0006-mindy-windows-exe-identity.patch", "940af9eae5ed67689284aa2cb486c1f38c784eba28670256ebe4d0330febfe08"),
    ("0007-mindy-service-policy-baseline.patch", "6ac09adb75ca0f1b711770a5d4948550d157cd8ca1ac28decf0c4ac02db611ea"),
)


class IdentityNamespaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bytes = PATCH.read_bytes()
        cls.patch = cls.bytes.decode("utf-8")
        cls.added = "\n".join(
            line[1:]
            for line in cls.patch.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        )

    def test_canonical_patch_bytes_order_and_pinned_preimage(self):
        self.assertNotIn(b"\r", self.bytes)
        self.assertEqual(SOURCE_SHA256, hashlib.sha256(FIXTURE.read_bytes()).hexdigest())
        series = (ROOT / "patches/series").read_bytes()
        self.assertNotIn(b"\r", series)
        names = tuple(
            line.split("#", 1)[0].strip()
            for line in series.decode("utf-8").splitlines()
            if line.split("#", 1)[0].strip()
        )
        self.assertEqual(tuple(name for name, _ in SERIES), names)
        for name, digest in SERIES:
            with self.subTest(name=name):
                self.assertEqual(digest, hashlib.sha256((ROOT / "patches" / name).read_bytes()).hexdigest())

    def test_patch_is_identity_only_and_keeps_the_temporary_guid_contract(self):
        targets = [line[6:] for line in self.patch.splitlines() if line.startswith("+++ b/")]
        self.assertEqual(["comm/mail/moz.configure"], targets)
        self.assertEqual(1, self.patch.count(APP_ID))
        self.assertFalse(any(APP_ID in line for line in self.patch.splitlines() if line.startswith(("+", "-"))))
        self.assertIn("TEMPORARY add-on compatibility exception", self.added)
        self.assertIn("approved release-policy revision", self.added)
        self.assertIn("does not establish a supported-release identity", self.added)

    def test_values_disable_updates_without_an_endpoint(self):
        values = (
            'imply_option("MOZ_APP_NAME", "mindy")',
            'imply_option("MOZ_APP_PROFILE", "Mindy")',
            'imply_option("MOZ_APP_BASENAME", "Mindy")',
            'imply_option("MOZ_APP_REMOTINGNAME", "mindy")',
            'imply_option("MOZ_APP_VENDOR", "Mindy Project")',
            'imply_option("--enable-update-channel", "mindy-dev")',
            'imply_option("--enable-updater", False)',
        )
        options = [line for line in self.added.splitlines() if line.startswith("imply_option(")]
        self.assertCountEqual(values, options)
        for value in values:
            with self.subTest(value=value):
                self.assertIn(value, self.added)
        self.assertIn('-set_config("MOZ_APPUPDATE_HOST", "aus.thunderbird.net")', self.patch)
        self.assertNotIn("set_config(", self.added)
        self.assertNotIn("http://", self.patch)
        self.assertNotIn("https://", self.patch)

    def test_patch_applies_to_the_exact_offline_preimage(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "comm/mail/moz.configure"
            target.parent.mkdir(parents=True)
            shutil.copyfile(FIXTURE, target)
            result = subprocess.run(
                ["git", "apply", "--check", str(PATCH)], cwd=root, text=True, capture_output=True
            )
        self.assertEqual(0, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()
