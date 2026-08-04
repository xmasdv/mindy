import base64
import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT / "patches" / "0006-mindy-windows-exe-identity.patch"
FIXTURE = ROOT / "tools" / "tests" / "fixtures" / "0006-windows-app-preimage.json"
SERIES = (
    ("0002-mindy-mail-shell.patch", "3d7121e6b25d6eb09c8689197704240084a7b69628a494b657a5c556cd6ab578"),
    ("0003-mindy-visual-packages.patch", "88b9822425f41f2611f9d12f1fc031cd804edf3e87fac57143f800362f2bf49e"),
    ("0004-mindy-identity-namespace.patch", "98ff34214761441f557ebbe1247036d3f0da37f7ba7f9ecc8e5d213c4859f013"),
    ("0005-mindy-branding-package.patch", "d829b482041c149a1e30efbddc65d32c31ba9e79de6dd3b39a237ae6123cff3c"),
    ("0006-mindy-windows-exe-identity.patch", "940af9eae5ed67689284aa2cb486c1f38c784eba28670256ebe4d0330febfe08"),
    ("0007-mindy-service-policy-baseline.patch", "1d63509764cb021e48f857372ae405d8fce031a7724503a779935c36f959162d"),
)
TARGETS = ("comm/mail/app/module.ver", "comm/mail/app/thunderbird.exe.manifest")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def targets(patch):
    return tuple(line[6:] for line in patch.splitlines() if line.startswith("+++ b/"))


def validate(patch, names):
    require(b"\r" not in patch, "patch is not canonical LF")
    text = patch.decode("utf-8")
    added = "\n".join(line[1:] for line in text.splitlines() if line.startswith("+") and not line.startswith("+++"))
    require(tuple(names) == tuple(name for name, _ in SERIES), "patch series identity/order differs")
    require(targets(text) == TARGETS, "patch target scope differs")
    require("COPYRIGHT" not in text, "MPL copyright must remain untouched")
    for value in ("WIN32_MODULE_COMPANYNAME=Mindy Project", "WIN32_MODULE_TRADEMARKS=", "WIN32_MODULE_COMMENT=Mindy Mail and Calendar Client", 'name="Mindy.Application"', "<description>Mindy</description>"):
        require(value in added, f"Mindy identity differs: {value}")
    require(not any(value in added for value in ("Thunderbird", "Mozilla", "Corporation", "Publisher", "Trademark of", "Mindy is a Trademark")), "publisher or trademark claim differs")


def fixture_source(root):
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    lock = json.loads((ROOT / "sources.lock").read_text(encoding="utf-8"))
    require({key: fixture[key] for key in ("repository", "revision")} == {key: lock["comm"][key] for key in ("repository", "revision")}, "fixture source pin differs")
    for item in fixture["files"]:
        data = (FIXTURE.parent / item["fixture"]).read_bytes() if "fixture" in item else base64.b64decode(item["base64"])
        require(hashlib.sha256(data).hexdigest() == item["sha256"], f"fixture hash differs: {item['path']}")
        target = root / item["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return fixture


class WindowsExeIdentityTests(unittest.TestCase):
    def test_manifest_preimage_is_pinned_to_lf(self):
        attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8").splitlines()
        self.assertIn("tools/tests/fixtures/0006-thunderbird.exe.manifest-preimage text eol=lf", attributes)

    def test_canonical_series_patch_and_fixture_hashes_are_exact(self):
        names = tuple(line.split("#", 1)[0].strip() for line in (ROOT / "patches" / "series").read_text(encoding="utf-8").splitlines() if line.split("#", 1)[0].strip())
        validate(PATCH.read_bytes(), names)
        for name, digest in SERIES:
            with self.subTest(name=name):
                self.assertEqual(digest, hashlib.sha256((ROOT / "patches" / name).read_bytes()).hexdigest())
        with tempfile.TemporaryDirectory() as temporary:
            fixture_source(Path(temporary))

    def test_ordered_canonical_series_applies_to_pinned_preimage(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with zipfile.ZipFile(ROOT / "tools/tests/fixtures/0002-comm-preimage.zip") as archive:
                archive.extractall(root)
            for source, target in ((ROOT / "tools/tests/fixtures/0004-moz.configure-preimage", root / "comm/mail/moz.configure"), (ROOT / "tools/tests/fixtures/0005-confvars-preimage", root / "comm/mail/confvars.sh")):
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
            fixture_source(root)
            fixture_series = [name for name, _ in SERIES if name != "0007-mindy-service-policy-baseline.patch"]
            result = subprocess.run(["git", "apply", "--check", *(ROOT / "patches" / name for name in fixture_series)], cwd=root, text=True, capture_output=True)
            self.assertEqual(0, result.returncode, result.stderr)
            result = subprocess.run(["git", "apply", str(ROOT / "patches/0004-mindy-identity-namespace.patch")], cwd=root, text=True, capture_output=True)
            self.assertEqual(0, result.returncode, result.stderr)
            result = subprocess.run(["git", "apply", "--check", "--include=comm/mail/moz.configure", str(ROOT / "patches/0007-mindy-service-policy-baseline.patch")], cwd=root, text=True, capture_output=True)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_applied_identity_is_truthful_and_preserves_mpl_copyright(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture_source(root)
            result = subprocess.run(["git", "apply", str(PATCH)], cwd=root, text=True, capture_output=True)
            self.assertEqual(0, result.returncode, result.stderr)
            module = (root / TARGETS[0]).read_text(encoding="latin-1")
            manifest = (root / TARGETS[1]).read_text(encoding="utf-8")
        self.assertIn("WIN32_MODULE_COPYRIGHT=\u00a9Thunderbird and Mozilla Developers, according to the MPL", module)
        self.assertIn("WIN32_MODULE_COMPANYNAME=Mindy Project", module)
        self.assertIn("WIN32_MODULE_TRADEMARKS=\n", module)
        self.assertIn("WIN32_MODULE_COMMENT=Mindy Mail and Calendar Client", module)
        self.assertIn('name="Mindy.Application"', manifest)
        self.assertIn("<description>Mindy</description>", manifest)

    def test_historical_filename_is_only_the_pinned_esr140_build_wiring_boundary(self):
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual({
            "splash_rc": {"path": "comm/mail/app/splash.rc", "sha256": "914df1c50d0c01dc65c20801e77cb9fc88edc6ef7da7542158810a75fd822666", "line": '1 24 "thunderbird.exe.manifest"'},
            "moz_build": {"path": "comm/mail/app/moz.build", "sha256": "e05ad99668a7de170d846184dc4b49f2a4d157f026a9e397f7e3f778206c6cb3", "line": '    RCINCLUDE = "splash.rc"'},
        }, fixture["build_wiring"])
        self.assertNotIn("splash.rc", PATCH.read_text(encoding="utf-8"))

    def test_static_contract_rejects_mismatch_scope_claim_lf_and_series_drift(self):
        patch = PATCH.read_bytes()
        names = [name for name, _ in SERIES]
        cases = {
            "Mindy/Thunderbird mismatch": (patch.replace(b"<description>Mindy</description>", b"<description>Thunderbird</description>"), names),
            "wrong target": (patch.replace(b"comm/mail/app/module.ver", b"comm/mail/app/installer.ver"), names),
            "publisher claim": (patch.replace(b"Mindy Project", b"Mindy Project Publisher"), names),
            "trademark claim": (patch.replace(b"WIN32_MODULE_TRADEMARKS=\n", b"WIN32_MODULE_TRADEMARKS=Mindy is a Trademark\n"), names),
            "non-LF": (patch.replace(b"\n", b"\r\n"), names),
            "series drift": (patch, [*names, names[-1]]),
        }
        for name, (candidate, candidate_names) in cases.items():
            with self.subTest(name=name), self.assertRaises(ValueError):
                validate(candidate, candidate_names)


if __name__ == "__main__":
    unittest.main()
